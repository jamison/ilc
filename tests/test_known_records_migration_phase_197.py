from __future__ import annotations

import json
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.protocol.ilc_cluster_a_ingest import (
    apply_governance_record,
    canonical_governance_payload_bytes,
    canonical_governance_record_digest,
)
from ilc_core.protocol.known_records_migration import (
    migrate_known_records_payload_hash_to_record_digest,
)


def _make_signed_record(gov_record_id: str, proposal_id: str, key_id: str, signer) -> dict:
    record = {
        "protocol_version": "v0.1",
        "gov_record_id": gov_record_id,
        "proposal_id": proposal_id,
        "state": "proposed",
        "timestamp": "2026-02-16T00:00:00Z",
        "payload": {"param": "value"},
        "signatures": [],
    }
    payload_bytes = canonical_governance_payload_bytes(record)
    signature_hex = signer.sign(payload_bytes).hex()
    record["signatures"].append(
        {
            "key_id": key_id,
            "sig_alg": "ed25519",
            "signature": signature_hex,
            "signed_at": "2026-02-16T00:00:00Z",
        }
    )
    return record


def test_phase_197_migration_function_migrates_payload_mode_to_record_digest() -> None:
    records = {
        "a" * 64: {
            "gov_record_id": "a" * 64,
            "proposal_id": "b" * 64,
            "state": "proposed",
            "timestamp": "2026-02-16T00:00:00Z",
            "payload": {"k": 1},
            "signatures": [],
        },
        "c" * 64: {
            "gov_record_id": "c" * 64,
            "proposal_id": "d" * 64,
            "state": "proposed",
            "timestamp": "2026-02-16T00:00:00Z",
            "payload": {"k": 2},
            "signatures": [],
        },
    }

    policy_state = {
        "proposals": {},
        "known_records": {
            "a" * 64: "payload_hash_old_a",
            "c" * 64: "payload_hash_old_c",
        },
        "known_records_hash_mode": "payload_hash_v0",
    }

    result = migrate_known_records_payload_hash_to_record_digest(policy_state, records)
    assert result["ok"] is True
    data = result["data"] or {}
    migrated = data["policy_state_migrated"]
    assert migrated["known_records_hash_mode"] == "record_digest_v1"
    assert migrated["known_records"]["a" * 64] == canonical_governance_record_digest(records["a" * 64])
    assert migrated["known_records"]["c" * 64] == canonical_governance_record_digest(records["c" * 64])


def test_phase_197_migration_function_fails_when_record_missing() -> None:
    policy_state = {
        "proposals": {},
        "known_records": {"a" * 64: "payload_hash_old_a"},
        "known_records_hash_mode": "payload_hash_v0",
    }

    result = migrate_known_records_payload_hash_to_record_digest(policy_state, records_input={})
    assert result["ok"] is False
    assert f"context_violation:migration_missing_record:{'a' * 64}" in result["errors"]


def test_phase_197_cli_migration_writes_output(tmp_path: Path) -> None:
    policy_state_path = tmp_path / "policy_state.json"
    records_path = tmp_path / "records.json"
    out_path = tmp_path / "migrated.json"

    records = {
        "a" * 64: {
            "gov_record_id": "a" * 64,
            "proposal_id": "b" * 64,
            "state": "proposed",
            "timestamp": "2026-02-16T00:00:00Z",
            "payload": {"k": 1},
            "signatures": [],
        }
    }
    policy_state = {
        "proposals": {},
        "known_records": {"a" * 64: "legacy_payload_hash"},
        "known_records_hash_mode": "payload_hash_v0",
    }

    policy_state_path.write_text(json.dumps(policy_state), encoding="utf-8")
    records_path.write_text(json.dumps(records), encoding="utf-8")

    result = subprocess.run(
        [
            "python3",
            "tools/migrate_known_records_hash_mode.py",
            "--policy-state",
            str(policy_state_path),
            "--records",
            str(records_path),
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "migration_ok" in result.stdout
    migrated = json.loads(out_path.read_text(encoding="utf-8"))
    assert migrated["known_records_hash_mode"] == "record_digest_v1"


def test_phase_197_apply_governance_record_emits_default_mode_telemetry() -> None:
    signer = ed25519.Ed25519PrivateKey.generate()
    pub = signer.public_key().public_bytes_raw()

    keyring = {"key_a": pub}
    policy_state = {"proposals": {}, "known_records": {}}
    record = _make_signed_record("a" * 64, "b" * 64, "key_a", signer)

    result = apply_governance_record(
        record,
        current_policy_state=policy_state,
        governance_keyring=keyring,
    )

    assert result["ok"] is True
    assert "known_records_hash_mode_defaulted_to_record_digest_v1" in result["warnings"]
    telemetry = (result.get("data") or {}).get("telemetry") or {}
    assert telemetry.get("known_records_hash_mode_defaulted_to_record_digest_v1") == 1


def test_phase_197_apply_governance_record_emits_fail_closed_telemetry_detail() -> None:
    signer = ed25519.Ed25519PrivateKey.generate()
    pub = signer.public_key().public_bytes_raw()

    keyring = {"key_a": pub}
    policy_state = {
        "proposals": {},
        "known_records": {"a" * 64: "f" * 64},
    }
    record = _make_signed_record("a" * 64, "b" * 64, "key_a", signer)

    result = apply_governance_record(
        record,
        current_policy_state=policy_state,
        governance_keyring=keyring,
    )

    assert result["ok"] is False
    assert "context_violation:known_records_hash_mode_required" in result["errors"]
    details = result.get("error_details") or []
    assert any(d.get("telemetry_counter") == "known_records_hash_mode_required_rejects" for d in details)
