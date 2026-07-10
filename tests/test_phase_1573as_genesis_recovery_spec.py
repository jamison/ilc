"""Phase 1573as Genesis recovery transaction boundary tests.

All fixtures are fake. No real Genesis Plate, Shamir, root, SPHINCS, ML-DSA,
or identity-seed material appears in this test file.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ilc_core.identity.genesis_record_schema import (
    GenesisRecord,
    GenesisRecordError,
    RecoverySpecType,
    RecoveryTransaction,
    encode_recovery_spec,
)

GENESIS_ROOT_SUCCESSION_DOMAIN = b"ilc-genesis-root-succession-v1:"
SPEC_PATH = Path("docs/specs/ilc_genesis_recovery_transaction_spec_1573as_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")

_SEED = bytes(range(32))
_OLD_PK = "ab" * 1664
_NEW_PK = "cd" * 1664
_OTHER_PK = "ef" * 1664


def _record_and_tx(freeze_from_epoch: int | None = None) -> tuple[GenesisRecord, RecoveryTransaction]:
    recovery_spec = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    record = GenesisRecord.from_identity_seed(
        identity_seed=_SEED,
        canonical_root_pk_hex=_OLD_PK,
        recovery_spec_bytes=recovery_spec,
    )
    tx = RecoveryTransaction(
        old_canonical_root_pk=_OLD_PK,
        new_canonical_root_pk=_NEW_PK,
        identity_seed_commitment=record.identity_seed_commitment,
        recovery_spec=recovery_spec,
        authorization=b"fake-signature-not-verified-in-1573as",
        freeze_from_epoch=freeze_from_epoch,
    )
    return record, tx


def _signature_payload(tx: RecoveryTransaction) -> bytes:
    return GENESIS_ROOT_SUCCESSION_DOMAIN + tx.to_canonical_bytes()


def test_canonical_tx_bytes_are_deterministic() -> None:
    _, tx = _record_and_tx(freeze_from_epoch=123)

    assert tx.to_canonical_bytes() == tx.to_canonical_bytes()
    assert json.loads(tx.to_canonical_bytes()) == {
        "freeze_from_epoch": 123,
        "identity_seed_commitment": tx.identity_seed_commitment,
        "new_canonical_root_pk": _NEW_PK,
        "old_canonical_root_pk": _OLD_PK,
    }


def test_freeze_from_epoch_is_clamped_up() -> None:
    record, tx = _record_and_tx(freeze_from_epoch=1)

    assert tx.validate_against_record(record, _SEED, current_epoch=100) == 100


def test_freeze_from_epoch_above_current_is_kept() -> None:
    record, tx = _record_and_tx(freeze_from_epoch=200)

    assert tx.validate_against_record(record, _SEED, current_epoch=100) == 200


def test_freeze_from_epoch_float_rejected() -> None:
    record, tx = _record_and_tx()
    tx.freeze_from_epoch = 100.5  # type: ignore[assignment]

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=100)
    assert exc.value.token == "cdl_069_recovery_invalid_epoch"


def test_freeze_from_epoch_bool_rejected() -> None:
    record, tx = _record_and_tx()
    tx.freeze_from_epoch = True  # type: ignore[assignment]

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=100)
    assert exc.value.token == "cdl_069_recovery_invalid_epoch"


def test_current_epoch_float_rejected() -> None:
    record, tx = _record_and_tx(freeze_from_epoch=200)

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=100.5)  # type: ignore[arg-type]
    assert exc.value.token == "cdl_069_recovery_invalid_epoch"


def test_negative_epoch_rejected() -> None:
    record, tx = _record_and_tx(freeze_from_epoch=-1)

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=100)
    assert exc.value.token == "cdl_069_recovery_invalid_epoch"


def test_recovery_spec_canonical_json_encoding() -> None:
    encoded = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 16)

    assert not encoded.startswith(b"single_key_sphincs:")
    assert json.loads(encoded) == {"pk_hex": "aa" * 16, "type": "single_key_sphincs"}
    assert encoded == b'{"pk_hex":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","type":"single_key_sphincs"}'


def test_shamir_sphincs_recovery_spec_encodes_threshold() -> None:
    encoded = encode_recovery_spec(
        RecoverySpecType.SHAMIR_SPHINCS,
        pk_hex="bb" * 16,
        threshold=2,
        total_shares=3,
    )

    assert json.loads(encoded) == {
        "pk_hex": "bb" * 16,
        "threshold": 2,
        "total_shares": 3,
        "type": "shamir_sphincs",
    }


def test_domain_separator_present_in_signature_payload() -> None:
    _, tx = _record_and_tx(freeze_from_epoch=123)

    payload = _signature_payload(tx)
    assert payload.startswith(GENESIS_ROOT_SUCCESSION_DOMAIN)
    assert hashlib.sha384(payload).digest() == hashlib.sha384(
        GENESIS_ROOT_SUCCESSION_DOMAIN + tx.to_canonical_bytes()
    ).digest()


def test_old_pk_mismatch_raises() -> None:
    record, tx = _record_and_tx()
    tx.old_canonical_root_pk = _OTHER_PK

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=100)
    assert exc.value.token == "cdl_069_recovery_old_pk_mismatch"


def test_commitment_mismatch_raises() -> None:
    record, tx = _record_and_tx()
    tx.recovery_spec = b"wrong-spec"

    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(record, _SEED, current_epoch=100)
    assert exc.value.token == "cdl_069_recovery_commitment_mismatch"


def test_phase_spec_records_non_operational_authorization_boundary() -> None:
    text = SPEC_PATH.read_text()

    assert "`authorization` is only a\nplaceholder field" in text
    assert "two-factor Genesis recovery model" in text
    assert "legacy byte-prefix" in text
    assert "canonical JSON" in text
    assert "No recovery transaction can retroactively invalidate" in text


def test_phase_status_tokens_present() -> None:
    text = STATUS_PATH.read_text()

    assert "genesis_recovery_transaction_boundary_spec_committed_phase_1573as" in text
    assert "genesis_recovery_two_factor_plate1_plate3_selected_phase_1573as" in text
    assert "genesis_recovery_spec_encoding_mismatch_resolved_phase_1573as" in text
    assert "public_path_remains_blocked_phase_1573as" in text
