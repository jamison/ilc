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
    / "docs/specs/ilc_genesis_public_submit_ingress_key_delegation_record_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_KEY_DELEGATION_00_v0.1.json"
)
INVITE_RECORD_PATH = (
    ROOT
    / "docs/specs/ilc_genesis_invite_issuer_delegation_record_GAP_GENESIS_INVITE_ISSUER_00_v0.1.json"
)
VALIDATOR_REGISTRY_PATH = ROOT / "config/public_rc_validators/genesis.json"
GENESIS_PUBKEY_RECORD_PATH = ROOT / "docs/genesis/genesis_agent1_pubkey_record_838a.txt"
PQ_SIGN = ROOT / "ilc_consensus/target/release/pq_sign"

EXPECTED_TOKENS = [
    "public_submit_ingress_key_delegation_schema_committed_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_KEY_DELEGATION_00",
    "public_submit_ingress_key_delegation_record_signed_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_KEY_DELEGATION_00",
    "public_submit_ingress_key_not_capsule_key_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_KEY_DELEGATION_00",
    "public_submit_ingress_key_not_invite_issuer_key_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_KEY_DELEGATION_00",
    "public_submit_ingress_key_not_validator_agentid_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_KEY_DELEGATION_00",
    "public_submit_ingress_key_delegation_complete_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_KEY_DELEGATION_00",
]


def _record() -> dict:
    return json.loads(RECORD_PATH.read_text())


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


def test_delegation_record_exists():
    assert RECORD_PATH.exists()


def test_delegation_record_required_fields():
    record = _record()
    required = {
        "public_submit_ingress_pk_hex",
        "role",
        "network_id",
        "epoch_scope",
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


def test_public_key_is_bls_g1_format():
    assert re.fullmatch(r"[0-9a-f]{96}", _record()["public_submit_ingress_pk_hex"])


def test_public_key_matches_genesis_settlement_constant():
    assert _record()["public_submit_ingress_pk_hex"] == GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX


def test_key_not_capsule_key():
    assert _record()["public_submit_ingress_pk_hex"] != GENESIS_CAPSULE_SIGNING_PK_HEX


def test_key_not_invite_issuer_key():
    invite_record = json.loads(INVITE_RECORD_PATH.read_text())
    assert _record()["public_submit_ingress_pk_hex"] != invite_record["invite_issuer_pk_hex"]


def test_key_not_validator_agentid():
    validators = json.loads(VALIDATOR_REGISTRY_PATH.read_text())["validators"]
    validator_ids = {validator["agent_id"] for validator in validators}
    assert _record()["public_submit_ingress_pk_hex"] not in validator_ids


def test_key_not_genesis_agent1_id():
    assert _record()["public_submit_ingress_pk_hex"] != GENESIS_AGENT1_AGENT_ID


def test_delegation_sig_excluded_from_signed_payload():
    record = _record()
    signed_payload = _signed_payload(record).decode("ascii")
    assert record["delegation_sig_hex"] not in signed_payload
    assert "phase_tokens" not in signed_payload


def test_delegation_sig_mldsa_verifies_against_838a(tmp_path):
    record = _record()
    payload_path = tmp_path / "delegation_payload.json"
    payload_path.write_bytes(_signed_payload(record))
    result = subprocess.run(
        [
            str(PQ_SIGN),
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
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "signature_verified"


def test_no_private_key_material_in_record():
    serialized = RECORD_PATH.read_text().lower()
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


def test_constant_in_all_exports():
    source = (ROOT / "ilc_core/epoch/genesis_settlement_destination.py").read_text()
    assert '"GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX"' in source
