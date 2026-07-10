"""Phase 1573at fake-key Genesis recovery vector tests.

All key material is deterministic test fixture material. No real Genesis Plate,
Shamir, root, SPHINCS, ML-DSA, or identity-seed material is read or used.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ilc_core.identity.genesis_record_schema import (
    GenesisRecord,
    GenesisRecordError,
    RecoverySpecType,
    RecoveryTransaction,
    compute_recovery_commitment,
    derive_blinding_factor,
    encode_recovery_spec,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CARGO = Path.home() / ".cargo" / "bin" / "cargo"
MANIFEST = REPO_ROOT / "ilc_consensus" / "Cargo.toml"
VECTOR_BIN = REPO_ROOT / "ilc_consensus" / "target" / "debug" / "genesis_recovery_fake_vector"
VECTOR_DOC = REPO_ROOT / "docs" / "specs" / "ilc_genesis_recovery_fake_key_test_vectors_1573at_v0.1.md"
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"
DOMAIN_HEX = "696c632d67656e657369732d726f6f742d73756363657373696f6e2d76313a"

_SEED = bytes(range(32))
_SEED_B = bytes(range(1, 33))
_OLD_PK = "ab" * 1664
_NEW_PK = "cd" * 1664


@pytest.fixture(scope="session")
def vector() -> dict[str, Any]:
    subprocess.run(
        [str(CARGO), "build", "--manifest-path", str(MANIFEST), "--bin", "genesis_recovery_fake_vector"],
        check=True,
        cwd=REPO_ROOT,
    )
    result = subprocess.run(
        [str(VECTOR_BIN), "--vector"],
        check=True,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def _verify(vector: dict[str, Any], *, signature_hex: str | None = None, pk_hex: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(VECTOR_BIN),
            "--verify",
            "--pk-hex",
            pk_hex or vector["fake_sphincs_pk_hex"],
            "--message-hex",
            vector["signature_message_sha384_hex"],
            "--signature-hex",
            signature_hex or vector["fake_signature_hex"],
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def _record_and_tx(
    *,
    seed: bytes = _SEED,
    recovery_spec: bytes | None = None,
    new_pk: str = _NEW_PK,
    freeze_from_epoch: int | None = None,
) -> tuple[GenesisRecord, RecoveryTransaction]:
    spec = recovery_spec or encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    record = GenesisRecord.from_identity_seed(seed, _OLD_PK, spec)
    tx = RecoveryTransaction(
        old_canonical_root_pk=_OLD_PK,
        new_canonical_root_pk=new_pk,
        identity_seed_commitment=record.identity_seed_commitment,
        recovery_spec=spec,
        authorization=b"fake-authorization-tested-by-rust-helper",
        freeze_from_epoch=freeze_from_epoch,
    )
    return record, tx


def test_correct_recovery_sig_accepted(vector: dict[str, Any]) -> None:
    result = _verify(vector)

    assert result.returncode == 0
    assert result.stdout.strip() == "PASS"
    assert vector["verify_ok"] is True


def test_wrong_sig_rejected(vector: dict[str, Any]) -> None:
    wrong_sig = "00" + vector["fake_signature_hex"][2:]

    result = _verify(vector, signature_hex=wrong_sig)

    assert result.returncode != 0
    assert "signature verification failed" in result.stderr


def test_wrong_old_root_pk_rejected() -> None:
    record, tx = _record_and_tx()
    tx.old_canonical_root_pk = "ef" * 1664

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=500)
    assert exc.value.token == "cdl_069_recovery_old_pk_mismatch"


def test_malformed_new_root_pk_rejected() -> None:
    record, tx = _record_and_tx(new_pk="bad")

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=500)
    assert exc.value.token == "cdl_069_recovery_invalid_new_pk"


def test_wrong_identity_seed_commitment_mismatch() -> None:
    record, tx = _record_and_tx()
    tx.identity_seed_commitment = "00" * 48

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=500)
    assert exc.value.token == "cdl_069_recovery_identity_seed_commitment_mismatch"


def test_wrong_recovery_spec_commitment_mismatch() -> None:
    record, tx = _record_and_tx()
    tx.recovery_spec = b"wrong-spec"

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=500)
    assert exc.value.token == "cdl_069_recovery_commitment_mismatch"


def test_canonical_tx_bytes_deterministic(vector: dict[str, Any]) -> None:
    first = bytes.fromhex(vector["canonical_tx_hex"])
    second = bytes.fromhex(vector["canonical_tx_hex"])

    assert first == second
    assert json.loads(first) == json.loads(vector["canonical_tx_json"])


def test_freeze_epoch_clamped_at_current() -> None:
    record, tx = _record_and_tx(freeze_from_epoch=1)

    assert tx.validate_against_record(record, _SEED, current_epoch=500) == 500


def test_freeze_epoch_above_current_preserved() -> None:
    record, tx = _record_and_tx(freeze_from_epoch=1000)

    assert tx.validate_against_record(record, _SEED, current_epoch=500) == 1000


def test_recovery_spec_commitment_opens_under_correct_encoding() -> None:
    blind = derive_blinding_factor(_SEED)
    canonical = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    legacy = b"single_key_sphincs:" + bytes.fromhex("aa" * 32)

    assert compute_recovery_commitment(canonical, blind) != compute_recovery_commitment(legacy, blind)
    assert canonical.startswith(b'{"pk_hex"')
    assert legacy.startswith(b"single_key_sphincs:")


def test_two_factor_identity_seed_mismatch_fails() -> None:
    record, tx = _record_and_tx()

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED_B, current_epoch=500)
    assert exc.value.token == "cdl_069_recovery_commitment_mismatch"


def test_domain_separator_in_sig_payload(vector: dict[str, Any]) -> None:
    assert vector["domain_separator_hex"] == DOMAIN_HEX
    assert vector["signature_payload_hex"].startswith(DOMAIN_HEX)
    assert vector["signature_message_sha384_hex"] == (
        "bb215d1ffe99f7e5ed98d1d406eb6bb63e77649f8bd5add87b709ddebd6797d"
        "95ecfddfa011cf06b9513d5668cbb2a74"
    )


def test_vector_doc_records_fake_material_and_lengths(vector: dict[str, Any]) -> None:
    text = VECTOR_DOC.read_text()

    assert "fake/non-Genesis" in text
    assert vector["fake_sphincs_pk_hex"] in text
    assert "fake_signature_hex_length: 15712" in text
    assert "signature_message_sha384_hex: bb215d1ffe99f7e5ed98d1d406eb6bb63e77649f8bd5add87b709ddebd6797d95ecfddfa011cf06b9513d5668cbb2a74" in text


def test_phase_status_tokens_present() -> None:
    text = STATUS_PATH.read_text()

    assert "genesis_recovery_fake_key_vectors_committed_phase_1573at" in text
    assert "genesis_recovery_sphincs_sig_verify_path_proven_fake_keys_phase_1573at" in text
    assert "public_path_remains_blocked_phase_1573at" in text
