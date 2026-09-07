# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT
    / "docs/specs/ilc_genesis_validator_provenance_binding_record_GAP_GENESIS_VALIDATOR_PROVENANCE_BINDING_00_v0.1.json"
)
PUBKEY_RECORD = ROOT / "docs/genesis/genesis_agent1_pubkey_record_838a.txt"
GENESIS_JSON = ROOT / "config/public_rc_validators/genesis.json"
ASSERTIONS_MANIFEST = (
    ROOT
    / "docs/specs/ilc_validator_endpoint_assertions_manifest_GAP_VPS_VALIDATOR_REPROVISION_00_v0.1.json"
)
EXPECTED_ASSERTIONS_SHA256 = (
    "427b1593908f9179037e5bce33645e38c4e4d39eafc2e74ef3bd802ef0b96c5e"
)
EXPECTED_TOKENS = {
    "genesis_validator_provenance_binding_record_committed_GAP_GENESIS_VALIDATOR_PROVENANCE_BINDING_00",
    "genesis_validator_provenance_binding_signed_by_genesis_GAP_GENESIS_VALIDATOR_PROVENANCE_BINDING_00",
    "all_4_validators_bound_GAP_GENESIS_VALIDATOR_PROVENANCE_BINDING_00",
    "dev_invite_provenance_gap_closed_GAP_GENESIS_VALIDATOR_PROVENANCE_BINDING_00",
    "genesis_validator_provenance_binding_complete_GAP_GENESIS_VALIDATOR_PROVENANCE_BINDING_00",
}


def _record() -> dict[str, object]:
    if not RECORD_PATH.exists():
        pytest.skip("Genesis validator provenance binding record not produced yet")
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def _genesis_validators() -> dict[str, dict[str, object]]:
    data = json.loads(GENESIS_JSON.read_text(encoding="utf-8"))
    return {str(v["agent_id"]): v for v in data["validators"]}


def _assertion_index() -> dict[str, dict[str, object]]:
    data = json.loads(ASSERTIONS_MANIFEST.read_text(encoding="utf-8"))
    return {str(v["validator_agent_id"]): v for v in data["assertion_index"]}


def _signed_payload(record: dict[str, object]) -> bytes:
    payload = {
        key: value
        for key, value in record.items()
        if key not in {"binding_sig_hex", "phase_tokens"}
    }
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _pq_sign_path() -> Path | None:
    for candidate in (
        ROOT / "ilc_consensus/target/release/pq_sign",
        ROOT / "ilc_consensus/target/debug/pq_sign",
    ):
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


def test_binding_record_exists() -> None:
    if not RECORD_PATH.exists():
        pytest.skip("Genesis validator provenance binding record not produced yet")
    assert RECORD_PATH.exists()


def test_binding_record_required_fields() -> None:
    record = _record()
    expected = {
        "assertions_manifest_path",
        "assertions_manifest_sha256",
        "binding_sig_hex",
        "binding_sig_scheme",
        "binding_signed_date",
        "bound_validators",
        "genesis_agent_cid",
        "issued_at_epoch",
        "network_id",
        "phase",
        "phase_tokens",
        "provenance_gap_closed",
        "reprovision_receipt_path",
        "revocation_policy",
        "role",
        "scope",
        "validator_count",
    }
    assert set(record) == expected
    for key in expected - {"bound_validators", "issued_at_epoch", "phase_tokens", "validator_count"}:
        assert isinstance(record[key], str)
        assert record[key]


def test_binding_validator_count_is_4() -> None:
    record = _record()
    assert record["validator_count"] == 4
    assert len(record["bound_validators"]) == 4


def test_bound_validator_agent_ids_match_genesis_json() -> None:
    record = _record()
    genesis_ids = set(_genesis_validators())
    bound_ids = {str(v["validator_agent_id"]) for v in record["bound_validators"]}
    assert bound_ids == genesis_ids


def test_bound_validator_agent_ids_are_bls_g1_format() -> None:
    for validator in _record()["bound_validators"]:
        assert re.fullmatch(r"[0-9a-f]{96}", str(validator["validator_agent_id"]))


def test_assertions_manifest_sha256_matches_known_value() -> None:
    assert _record()["assertions_manifest_sha256"] == EXPECTED_ASSERTIONS_SHA256


def test_assertion_content_sha256_values_match_manifest() -> None:
    manifest = _assertion_index()
    for validator in _record()["bound_validators"]:
        agent_id = str(validator["validator_agent_id"])
        assert agent_id in manifest
        assert (
            validator["assertion_content_sha256"]
            == manifest[agent_id]["assertion_content_sha256"]
        )


def test_bound_validator_host_and_grpc_port_match_genesis_json() -> None:
    genesis = _genesis_validators()
    for validator in _record()["bound_validators"]:
        source = genesis[str(validator["validator_agent_id"])]
        assert validator["host"] == source["host"]
        assert validator["grpc_port"] == source["port"]


def test_network_id_is_public_rc() -> None:
    assert _record()["network_id"] == "public-rc"


def test_issued_at_epoch_is_0() -> None:
    assert _record()["issued_at_epoch"] == 0


def test_binding_sig_scheme_is_mldsa() -> None:
    assert _record()["binding_sig_scheme"] == "mldsa"


def test_binding_sig_hex_excluded_from_signed_payload() -> None:
    record = _record()
    payload = _signed_payload(record).decode("ascii")
    assert str(record["binding_sig_hex"]) not in payload


def test_binding_sig_mldsa_verifies_against_genesis_838a_pubkey() -> None:
    pq_sign = _pq_sign_path()
    if pq_sign is None:
        pytest.skip("pq_sign verifier not available")
    record = _record()
    payload = _signed_payload(record)
    with tempfile.NamedTemporaryFile(prefix="ilc_validator_provenance_binding_", suffix=".json") as tmp:
        tmp.write(payload)
        tmp.flush()
        result = subprocess.run(
            [
                str(pq_sign),
                "verify",
                "--input-file",
                tmp.name,
                "--pubkey-record",
                str(PUBKEY_RECORD),
                "--signature-hex",
                str(record["binding_sig_hex"]),
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    assert result.returncode == 0, result.stderr
    assert "signature_verified" in result.stdout


def test_no_private_key_material_in_record() -> None:
    forbidden = [
        "private_key",
        "secret_key",
        "sk_hex",
        "mldsa_sk",
        "sphincs_sk",
        "seed",
        "mnemonic",
    ]
    content = json.dumps(_record()).lower()
    for term in forbidden:
        assert term not in content


def test_phase_tokens_present() -> None:
    assert set(_record()["phase_tokens"]) == EXPECTED_TOKENS


def test_genesis_agent_cid_matches_known_value() -> None:
    assert _record()["genesis_agent_cid"] == GENESIS_AGENT1_AGENT_ID


def test_no_runtime_constant_added() -> None:
    result = subprocess.run(
        ["grep", "-r", "GENESIS_VALIDATOR_PROVENANCE_BINDING", "ilc_core/"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 1
    assert result.stdout == ""
