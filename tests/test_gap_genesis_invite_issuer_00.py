# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_CAPSULE_SIGNING_PK_HEX,
)


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT
    / "docs/specs/ilc_genesis_invite_issuer_delegation_record_GAP_GENESIS_INVITE_ISSUER_00_v0.1.json"
)
PUBKEY_RECORD = ROOT / "docs/genesis/genesis_agent1_pubkey_record_838a.txt"
VALIDATORS_PATH = ROOT / "config/public_rc_validators/genesis.json"
EXPECTED_TOKENS = {
    "genesis_invite_issuer_key_generated_GAP_GENESIS_INVITE_ISSUER_00",
    "genesis_invite_issuer_delegation_record_committed_GAP_GENESIS_INVITE_ISSUER_00",
    "genesis_invite_issuer_delegation_signed_by_genesis_GAP_GENESIS_INVITE_ISSUER_00",
    "invite_issuer_pk_not_capsule_key_GAP_GENESIS_INVITE_ISSUER_00",
    "invite_issuer_pk_not_validator_hot_key_GAP_GENESIS_INVITE_ISSUER_00",
    "genesis_invite_issuer_delegation_complete_GAP_GENESIS_INVITE_ISSUER_00",
}


def _record() -> dict[str, object]:
    if not RECORD_PATH.exists():
        pytest.skip("Genesis invite issuer delegation record not produced yet")
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def _signed_payload(record: dict[str, object]) -> bytes:
    payload = {
        key: value
        for key, value in record.items()
        if key not in {"delegation_sig_hex", "phase_tokens"}
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


def test_delegation_record_exists() -> None:
    if not RECORD_PATH.exists():
        pytest.skip("Genesis invite issuer delegation record not produced yet")
    assert RECORD_PATH.exists()


def test_delegation_record_required_fields() -> None:
    record = _record()
    expected = {
        "bls_sign_dst",
        "delegation_sig_hex",
        "delegation_sig_scheme",
        "delegation_signed_date",
        "epoch_scope",
        "genesis_agent_cid",
        "invite_issuer_pk_hex",
        "issuance_limits",
        "network_id",
        "phase",
        "phase_tokens",
        "relay_store_request_dst",
        "revocation_policy",
        "role",
        "shortcode_authority_scope",
    }
    assert set(record) == expected
    for key in expected - {"issuance_limits", "phase_tokens"}:
        assert isinstance(record[key], str)
        assert record[key]


def test_invite_issuer_pk_not_capsule_key() -> None:
    assert _record()["invite_issuer_pk_hex"] != GENESIS_CAPSULE_SIGNING_PK_HEX


def test_invite_issuer_pk_not_validator_agentid() -> None:
    record = _record()
    validators = json.loads(VALIDATORS_PATH.read_text(encoding="utf-8"))
    validator_ids = {validator["agent_id"] for validator in validators["validators"]}
    assert record["invite_issuer_pk_hex"] not in validator_ids


def test_invite_issuer_pk_is_bls_g1_format() -> None:
    assert re.fullmatch(r"[0-9a-f]{96}", str(_record()["invite_issuer_pk_hex"]))


def test_delegation_sig_scheme_is_mldsa() -> None:
    assert _record()["delegation_sig_scheme"] == "mldsa"


def test_delegation_sig_hex_excluded_from_signed_payload() -> None:
    record = _record()
    payload = _signed_payload(record).decode("ascii")
    assert str(record["delegation_sig_hex"]) not in payload


def test_delegation_sig_mldsa_verifies_against_genesis_838a_pubkey() -> None:
    pq_sign = _pq_sign_path()
    if pq_sign is None:
        pytest.skip("pq_sign verifier not available")
    record = _record()
    payload = _signed_payload(record)
    with tempfile.NamedTemporaryFile(prefix="ilc_invite_issuer_delegation_", suffix=".json") as tmp:
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
                str(record["delegation_sig_hex"]),
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


def test_network_id_is_public_rc() -> None:
    assert _record()["network_id"] == "public-rc"


def test_issuance_limits_are_machine_checkable() -> None:
    limits = _record()["issuance_limits"]
    assert isinstance(limits, dict)
    assert limits["max_batch_size"] is None or isinstance(limits["max_batch_size"], int)
    assert limits["max_total_batches"] is None or isinstance(limits["max_total_batches"], int)
    assert isinstance(limits.get("limit_authority_status"), str)
    assert limits["limit_authority_status"]
    assert "<TBD>" not in json.dumps(limits)


def test_phase_tokens_present() -> None:
    assert set(_record()["phase_tokens"]) == EXPECTED_TOKENS


def test_genesis_agent_cid_matches_known_value() -> None:
    assert _record()["genesis_agent_cid"] == GENESIS_AGENT1_AGENT_ID


def test_no_runtime_constant_added() -> None:
    result = subprocess.run(
        ["grep", "-r", "GENESIS_INVITE_ISSUER_PK_HEX", "ilc_core/"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 1
    assert result.stdout == ""
