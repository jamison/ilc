from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from ilc_core.economics.productive_ecu_expansion_bounty_runtime import (
    PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED,
)
from ilc_core.epoch.ejected_stake_distribution_production_path import (
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
)
from ilc_core.epoch.epoch_emission_production_path import (
    PRODUCTION_EMISSION_NOT_ACTIVATED,
)
from ilc_core.epoch.treasury_validator_reward_production_path import (
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
)
from ilc_core.ledger.conversion_candidate_runtime import (
    CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED,
)
from ilc_core.validator.validator_admission_ejection_production_path import (
    VALIDATOR_ADMISSION_NOT_ACTIVATED,
)


DOMAIN_SEPARATOR = "ilc-genesis-public-rc-signing-envelope-v0.5"
SPEC_PATH = Path(
    "docs/specs/ilc_genesis_v05_public_rc_signing_ceremony_spec_1575c_fix1_v0.1.md"
)
ENVELOPE_PATH = Path("out/genesis_public_rc_signing_envelope_v0.5.json")
SIGNATURE_PAYLOAD_PATH = Path(
    "out/genesis_public_rc_signing_envelope_v0.5.signature_payload.bin"
)
SIGNING_REQUEST_PATH = Path(
    "out/genesis_public_rc_signing_envelope_v0.5.signing_request.json"
)
SIGNATURE_HEX_PATH = Path(
    "out/genesis_public_rc_signing_envelope_v0.5.signature.hex"
)
SIGNATURE_RECORD_PATH = Path(
    "out/genesis_public_rc_signing_envelope_v0.5.signature.json"
)
VERIFICATION_RECORD_PATH = Path(
    "out/genesis_public_rc_signing_envelope_v0.5.verification.json"
)
STATUS_PATH = Path("docs/phases/STATUS.md")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _load_envelope() -> dict[str, object]:
    return json.loads(ENVELOPE_PATH.read_text())


def test_spec_file_exists_and_records_narrow_v05_scope_boundary() -> None:
    text = SPEC_PATH.read_text()
    assert "Genesis v0.5 Public-RC Signing Ceremony Spec" in text
    assert "public-RC signing envelope" in text
    assert "not** mean the full post-RC behavioral Genesis v0.5" in text
    assert DOMAIN_SEPARATOR in text


def test_unsigned_payload_exists_and_has_no_signature_or_private_material_fields() -> None:
    payload = _load_envelope()
    assert payload["artifact_kind"] == "genesis_public_rc_signing_envelope"
    assert payload["artifact_version"] == "v0.5"
    assert payload["scope_boundary"] == (
        "public_rc_signing_envelope_v0_5_not_behavioral_genesis_v0_5"
    )
    forbidden_keys = {
        "signature",
        "signatures",
        "signature_hex",
        "mnemonic",
        "seed_phrase",
        "shamir_share",
        "private_key",
        "private_key_hex",
    }
    assert forbidden_keys.isdisjoint(payload)


def test_canonical_byte_serialization_is_file_exact_and_deterministic() -> None:
    payload = _load_envelope()
    canonical = _canonical_bytes(payload)
    assert ENVELOPE_PATH.read_bytes() == canonical
    assert _canonical_bytes(json.loads(canonical.decode("utf-8"))) == canonical


def test_domain_separator_and_signature_payload_hashes_match_recomputation() -> None:
    envelope_bytes = ENVELOPE_PATH.read_bytes()
    signature_payload = SIGNATURE_PAYLOAD_PATH.read_bytes()
    assert signature_payload == DOMAIN_SEPARATOR.encode("utf-8") + envelope_bytes

    signing_request = json.loads(SIGNING_REQUEST_PATH.read_text())
    assert signing_request["domain_separator"] == DOMAIN_SEPARATOR
    assert signing_request["unsigned_payload_sha256"] == hashlib.sha256(
        envelope_bytes
    ).hexdigest()
    assert signing_request["signature_payload_sha256"] == hashlib.sha256(
        signature_payload
    ).hexdigest()


def test_current_state_has_verified_v05_signature_but_no_public_rc_success() -> None:
    status = STATUS_PATH.read_text()
    assert "genesis_v05_public_rc_envelope_unsigned_payload_committed_phase_1575c_fix1" in status
    assert "genesis_v05_public_rc_envelope_signed_phase_1575c_fix1" in status
    assert "genesis_v05_public_rc_envelope_signature_verified_phase_1575c_fix1" in status
    assert "atlas_slice_manifest_v05_signed_phase_1575c_fix1" in status
    assert "phase_1575c_v05_signing_tokens_accepted_by_gate_phase_1575c_fix1" in status
    assert "public_rc_gate_001_authorized" not in status
    assert "public_rc_live_phase_1575c" not in status
    assert "public_repository_push_authorized_phase_1575c" not in status


def test_signature_and_verification_records_exist_and_match_payload_hashes() -> None:
    assert SIGNATURE_HEX_PATH.exists()
    assert SIGNATURE_RECORD_PATH.exists()
    assert VERIFICATION_RECORD_PATH.exists()
    signature_record = json.loads(SIGNATURE_RECORD_PATH.read_text())
    verification_record = json.loads(VERIFICATION_RECORD_PATH.read_text())
    assert signature_record["operator_signature_produced"] is True
    assert signature_record["secret_material_handled_by_codex"] is False
    assert verification_record["verification_result"] == "signature_verified"
    assert verification_record["secret_material_handled_by_codex"] is False
    assert signature_record["signature_payload_sha256"] == hashlib.sha256(
        SIGNATURE_PAYLOAD_PATH.read_bytes()
    ).hexdigest()
    assert verification_record["signature_payload_sha256"] == signature_record[
        "signature_payload_sha256"
    ]


def test_phase_1575c_gate_prompt_consumes_verified_v05_signing_path() -> None:
    prompt = Path(
        "docs/antigravity_tasks/antigravity_prompt__phase_1575c_g10_block6_public_rc_gate_001.md"
    ).read_text()
    assert "Genesis v0.5 Signing Envelope" in prompt
    assert "genesis_v05_public_rc_envelope_signed_phase_1575c_fix1" in prompt
    assert "genesis_v05_public_rc_envelope_signature_verified_phase_1575c_fix1" in prompt
    assert "phase_1575c_v05_signing_tokens_accepted_by_gate_phase_1575c_fix1" in prompt
    assert "genesis_v04_signed_phase_1575c" not in prompt
    assert "atlas_slice_manifest_signed_phase_1575c" not in prompt


def test_existing_production_verifier_binary_remains_reproducible() -> None:
    signature_hex = Path("out/genesis_signing_root_envelope_v0.1.sig").read_text().strip()
    result = subprocess.run(
        [
            "ilc_consensus/target/debug/pq_sign",
            "verify",
            "--input-file",
            "out/genesis_signing_root_envelope_v0.1.json",
            "--signature-hex",
            signature_hex,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "signature_verified"


def test_dev_test_atlas_signing_profile_is_not_accepted_as_production() -> None:
    source = Path("ilc_core/cli/atlas_lmdb_cli.py").read_text()
    assert "ed25519_cose_sign1_dev_test_only" in source
    assert '"genesis_signing": False' in source
    assert '"ml_dsa_manifest_signing": False' in source
    assert '"public_rc_activation": False' in source


def test_pq_sign_disables_terminal_echo_for_seed_entry() -> None:
    source = Path("ilc_consensus/src/pq_sign_main.rs").read_text()
    assert "TerminalEchoGuard::disable()" in source
    assert 'run_stty(&["-echo"])' in source
    assert 'run_stty(&["echo"])' in source
    assert "input.zeroize();" in source


def test_pq_sign_reports_wrong_mnemonic_word_count_before_hex_parse() -> None:
    source = Path("ilc_consensus/src/pq_sign_main.rs").read_text()
    assert "let word_count = input.split_whitespace().count();" in source
    assert "mnemonic_word_count_must_be_24_got_{word_count}" in source
    assert "input.chars().any(|ch| ch.is_ascii_alphabetic())" in source


def test_full_behavioral_v05_non_claims_are_present() -> None:
    payload = _load_envelope()
    non_claims = payload["non_claims"]
    assert isinstance(non_claims, dict)
    assert non_claims["no_behavioral_genesis_v05_ceremony"] is True
    assert non_claims["no_public_rc_activation"] is True
    assert non_claims["no_public_repository_push"] is True
    assert non_claims["no_runtime_guard_clearance"] is True
    assert non_claims["no_ecu_minting"] is True
    assert non_claims["no_ilc_settlement"] is True
    assert non_claims["no_epoch_transition"] is True


def test_all_six_economic_not_activated_guards_remain_true() -> None:
    guards = {
        "CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED": CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED,
        "EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED": EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
        "PRODUCTION_EMISSION_NOT_ACTIVATED": PRODUCTION_EMISSION_NOT_ACTIVATED,
        "PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED": PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED,
        "TREASURY_DISTRIBUTION_NOT_ACTIVATED": TREASURY_DISTRIBUTION_NOT_ACTIVATED,
        "VALIDATOR_ADMISSION_NOT_ACTIVATED": VALIDATOR_ADMISSION_NOT_ACTIVATED,
    }
    assert set(guards) == {
        "CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED",
        "EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED",
        "PRODUCTION_EMISSION_NOT_ACTIVATED",
        "PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED",
        "TREASURY_DISTRIBUTION_NOT_ACTIVATED",
        "VALIDATOR_ADMISSION_NOT_ACTIVATED",
    }
    assert all(value is True for value in guards.values())
