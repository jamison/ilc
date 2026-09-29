import json
import re
import subprocess
from pathlib import Path

from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_CAPSULE_SIGNING_PK_HEX,
    GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX,
)


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT
    / "docs/specs/ilc_genesis_capsule_signing_key_delegation_record_GAP_GENESIS_CAPSULE_SIGNING_KEY_DELEGATION_00_v0.1.json"
)
INVITE_RECORD_PATH = (
    ROOT
    / "docs/specs/ilc_genesis_invite_issuer_delegation_record_GAP_GENESIS_INVITE_ISSUER_00_v0.1.json"
)
VALIDATOR_REGISTRY_PATH = ROOT / "config/public_rc_validators/genesis.json"
GENESIS_PUBKEY_RECORD_PATH = ROOT / "docs/genesis/genesis_agent1_pubkey_record_838a.txt"
PQ_SIGN_CANDIDATES = [
    ROOT / "ilc_consensus/target/release/pq_sign",
    ROOT / "ilc_consensus/target/debug/pq_sign",
]

EXPECTED_TOKENS = [
    "capsule_signing_key_delegation_schema_committed_GAP_GENESIS_CAPSULE_SIGNING_KEY_DELEGATION_00",
    "capsule_signing_key_delegation_record_signed_GAP_GENESIS_CAPSULE_SIGNING_KEY_DELEGATION_00",
    "capsule_key_not_submit_ingress_key_GAP_GENESIS_CAPSULE_SIGNING_KEY_DELEGATION_00",
    "capsule_key_not_invite_issuer_key_GAP_GENESIS_CAPSULE_SIGNING_KEY_DELEGATION_00",
    "capsule_key_not_validator_agentid_GAP_GENESIS_CAPSULE_SIGNING_KEY_DELEGATION_00",
    "capsule_signing_key_delegation_complete_GAP_GENESIS_CAPSULE_SIGNING_KEY_DELEGATION_00",
]


def _record() -> dict:
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def _signed_payload(record: dict) -> bytes:
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


def _pq_sign() -> Path:
    for candidate in PQ_SIGN_CANDIDATES:
        if candidate.exists():
            return candidate
    raise AssertionError("delegation_signature_verifier_missing_pq_sign_binary")


def test_delegation_record_exists():
    assert RECORD_PATH.exists()


def test_delegation_record_required_fields():
    record = _record()
    required = {
        "capsule_signing_pk_hex",
        "role",
        "purpose",
        "network_scope",
        "revocation_policy",
        "genesis_agent_cid",
        "delegation_sig_hex",
        "delegation_sig_scheme",
        "delegation_signed_date",
        "phase",
        "phase_tokens",
    }
    assert required <= set(record)
    assert all(record[field] not in ("", None) for field in required)


def test_capsule_key_is_bls_g1_format():
    assert re.fullmatch(r"[0-9a-f]{96}", _record()["capsule_signing_pk_hex"])


def test_capsule_key_matches_genesis_settlement_constant():
    assert _record()["capsule_signing_pk_hex"] == GENESIS_CAPSULE_SIGNING_PK_HEX


def test_capsule_key_not_submit_ingress_key():
    assert _record()["capsule_signing_pk_hex"] != GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX


def test_capsule_key_not_invite_issuer_key():
    invite_record = json.loads(INVITE_RECORD_PATH.read_text(encoding="utf-8"))
    assert _record()["capsule_signing_pk_hex"] != invite_record["invite_issuer_pk_hex"]


def test_capsule_key_not_validator_agentid():
    validators = json.loads(VALIDATOR_REGISTRY_PATH.read_text(encoding="utf-8"))["validators"]
    validator_ids = {validator["agent_id"] for validator in validators}
    assert _record()["capsule_signing_pk_hex"] not in validator_ids


def test_capsule_key_not_genesis_agent1_id():
    assert _record()["capsule_signing_pk_hex"] != GENESIS_AGENT1_AGENT_ID


def test_delegation_sig_excluded_from_signed_payload():
    record = _record()
    signed_payload = _signed_payload(record).decode("ascii")
    assert record["delegation_sig_hex"] not in signed_payload
    assert "phase_tokens" not in signed_payload


def test_delegation_sig_mldsa_verifies_against_838a(tmp_path):
    record = _record()
    payload_path = tmp_path / "capsule_delegation_payload.json"
    payload_path.write_bytes(_signed_payload(record))
    result = subprocess.run(
        [
            str(_pq_sign()),
            "verify",
            "--input-file",
            str(payload_path),
            "--pubkey-record",
            str(GENESIS_PUBKEY_RECORD_PATH),
            "--signature-hex",
            record["delegation_sig_hex"],
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "signature_verified"


def test_no_private_key_material_in_record():
    serialized = RECORD_PATH.read_text(encoding="utf-8").lower()
    forbidden_terms = {
        "private_key",
        "secret_key",
        "sk_hex",
        "mldsa_sk",
        "sphincs_sk",
        "seed",
        "mnemonic",
    }
    assert not any(term in serialized for term in forbidden_terms)


def test_genesis_agent_cid_matches_constant():
    assert _record()["genesis_agent_cid"] == GENESIS_AGENT1_AGENT_ID


def test_phase_tokens_present():
    assert _record()["phase_tokens"] == EXPECTED_TOKENS


def test_role_is_capsule_only():
    assert _record()["role"] == "genesis_delegate_capsule_signing_v1"


def test_purpose_and_scope_are_capsule_only():
    record = _record()
    assert record["purpose"] == "relay_bootstrap_capsule_signing"
    assert record["network_scope"] == "all_relay_bootstrap_networks"
    assert record["role"] != "genesis_delegate_public_submit_ingress_v1"


def test_delegation_signature_shape():
    assert re.fullmatch(r"[0-9a-f]+", _record()["delegation_sig_hex"])
    assert len(_record()["delegation_sig_hex"]) > 1000
