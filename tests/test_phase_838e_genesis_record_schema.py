"""Phase 838e — CDL-069 genesis record schema tests.

Covers:
  - derive_blinding_factor
  - compute_identity_seed_commitment
  - compute_recovery_commitment
  - compute_personhood_commitment
  - RecoverySpecType enum and encode_recovery_spec
  - GenesisRecord dataclass: validate(), to_canonical_bytes(), from_identity_seed()
  - RecoveryTransaction dataclass: validate_against_record(), to_canonical_bytes()
  - Validation helpers (_require_commitment, _require_hex)
  - Version and dependency tokens
"""
from __future__ import annotations

import hashlib
import json

import pytest

from ilc_core.identity.genesis_record_schema import (
    GENESIS_RECORD_SCHEMA_VERSION,
    CDL_069_DEPENDENCY,
    GenesisRecord,
    GenesisRecordError,
    RecoverySpecType,
    RecoveryTransaction,
    compute_identity_seed_commitment,
    compute_personhood_commitment,
    compute_recovery_commitment,
    derive_blinding_factor,
    encode_recovery_spec,
)

_SEED_32 = bytes(range(32))
_SEED_32_B = bytes(range(1, 33))
_FAKE_MLDSA_PK = "ab" * 1664  # 3328 hex chars


# ---------------------------------------------------------------------------
# Version and dependency tokens
# ---------------------------------------------------------------------------

def test_schema_version_token() -> None:
    assert GENESIS_RECORD_SCHEMA_VERSION == "genesis_record_schema_838e.v0.1"


def test_cdl_069_dependency_token() -> None:
    assert CDL_069_DEPENDENCY == "cdl_069_opens_phase_838"


# ---------------------------------------------------------------------------
# derive_blinding_factor
# ---------------------------------------------------------------------------

def test_blinding_factor_returns_bytes() -> None:
    bf = derive_blinding_factor(_SEED_32)
    assert isinstance(bf, bytes)
    assert len(bf) == 48  # SHA-384 = 48 bytes


def test_blinding_factor_known_vector() -> None:
    seed = b"\x00" * 32
    expected = hashlib.sha384(b"ilc-recovery-blind-v1:" + seed).digest()
    assert derive_blinding_factor(seed) == expected


def test_blinding_factor_is_deterministic() -> None:
    assert derive_blinding_factor(_SEED_32) == derive_blinding_factor(_SEED_32)


def test_blinding_factor_differs_for_different_seeds() -> None:
    assert derive_blinding_factor(_SEED_32) != derive_blinding_factor(_SEED_32_B)


def test_blinding_factor_rejects_non_bytes() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        derive_blinding_factor("not bytes")  # type: ignore[arg-type]
    assert "cdl_069_genesis_invalid_identity_seed" in exc.value.token


def test_blinding_factor_rejects_wrong_length() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        derive_blinding_factor(b"\x00" * 16)
    assert "cdl_069_genesis_invalid_identity_seed" in exc.value.token


def test_blinding_factor_rejects_empty() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        derive_blinding_factor(b"")
    assert "cdl_069_genesis_invalid_identity_seed" in exc.value.token


# ---------------------------------------------------------------------------
# compute_identity_seed_commitment
# ---------------------------------------------------------------------------

def test_identity_seed_commitment_returns_96_hex() -> None:
    result = compute_identity_seed_commitment(_SEED_32)
    assert isinstance(result, str)
    assert len(result) == 96
    assert all(c in "0123456789abcdef" for c in result)


def test_identity_seed_commitment_known_vector() -> None:
    seed = b"\x00" * 32
    expected = hashlib.sha384(seed).hexdigest()
    assert compute_identity_seed_commitment(seed) == expected


def test_identity_seed_commitment_is_deterministic() -> None:
    assert compute_identity_seed_commitment(_SEED_32) == compute_identity_seed_commitment(_SEED_32)


def test_identity_seed_commitment_differs_for_different_seeds() -> None:
    assert compute_identity_seed_commitment(_SEED_32) != compute_identity_seed_commitment(_SEED_32_B)


def test_identity_seed_commitment_rejects_non_bytes() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        compute_identity_seed_commitment("oops")  # type: ignore[arg-type]
    assert "cdl_069_genesis_invalid_identity_seed" in exc.value.token


def test_identity_seed_commitment_rejects_wrong_length() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        compute_identity_seed_commitment(b"\x00" * 31)
    assert "cdl_069_genesis_invalid_identity_seed" in exc.value.token


# ---------------------------------------------------------------------------
# compute_recovery_commitment
# ---------------------------------------------------------------------------

def test_recovery_commitment_known_vector() -> None:
    spec_bytes = b"test-recovery-spec"
    blind = b"\xab" * 48
    expected = hashlib.sha384(spec_bytes + blind).hexdigest()
    assert compute_recovery_commitment(spec_bytes, blind) == expected


def test_recovery_commitment_is_deterministic() -> None:
    bf = derive_blinding_factor(_SEED_32)
    spec = b"spec-data"
    assert compute_recovery_commitment(spec, bf) == compute_recovery_commitment(spec, bf)


def test_recovery_commitment_returns_96_hex() -> None:
    bf = derive_blinding_factor(_SEED_32)
    result = compute_recovery_commitment(b"spec", bf)
    assert len(result) == 96
    assert all(c in "0123456789abcdef" for c in result)


def test_recovery_commitment_differs_for_different_specs() -> None:
    bf = derive_blinding_factor(_SEED_32)
    assert compute_recovery_commitment(b"spec-a", bf) != compute_recovery_commitment(b"spec-b", bf)


# ---------------------------------------------------------------------------
# compute_personhood_commitment
# ---------------------------------------------------------------------------

def test_personhood_commitment_known_vector() -> None:
    proof = b"personhood-proof-data"
    blind = b"\xcd" * 48
    expected = hashlib.sha384(proof + blind).hexdigest()
    assert compute_personhood_commitment(proof, blind) == expected


def test_personhood_commitment_returns_96_hex() -> None:
    bf = derive_blinding_factor(_SEED_32)
    result = compute_personhood_commitment(b"proof", bf)
    assert len(result) == 96
    assert all(c in "0123456789abcdef" for c in result)


# ---------------------------------------------------------------------------
# RecoverySpecType and encode_recovery_spec
# ---------------------------------------------------------------------------

def test_recovery_spec_type_enum_values() -> None:
    assert RecoverySpecType.SINGLE_KEY_MLDSA.value == "single_key_mldsa"
    assert RecoverySpecType.SINGLE_KEY_SPHINCS.value == "single_key_sphincs"
    assert RecoverySpecType.SHAMIR_SPHINCS.value == "shamir_sphincs"
    assert RecoverySpecType.QUORUM_VALIDATOR.value == "quorum_validator"
    assert RecoverySpecType.THRESHOLD_MULTIPARTY.value == "threshold_multiparty"
    assert RecoverySpecType.HSM_ATTESTATION.value == "hsm_attestation"
    assert RecoverySpecType.PERSONHOOD_BIOMETRIC.value == "personhood_biometric"


def test_encode_recovery_spec_returns_bytes() -> None:
    result = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_MLDSA, pk_hex="ab" * 1664)
    assert isinstance(result, bytes)


def test_encode_recovery_spec_is_valid_json() -> None:
    result = encode_recovery_spec(RecoverySpecType.HSM_ATTESTATION, hsm_id="hsm-001")
    payload = json.loads(result.decode())
    assert payload["type"] == "hsm_attestation"
    assert payload["hsm_id"] == "hsm-001"


def test_encode_recovery_spec_canonical_sort_keys() -> None:
    # Keys must be sorted for canonical encoding
    result = encode_recovery_spec(
        RecoverySpecType.SHAMIR_SPHINCS,
        pk_hex="aa" * 32,
        threshold=2,
        total_shares=3,
    )
    payload = json.loads(result.decode())
    keys = list(payload.keys())
    assert keys == sorted(keys)


def test_encode_recovery_spec_no_spaces() -> None:
    result = encode_recovery_spec(RecoverySpecType.QUORUM_VALIDATOR, threshold=3, delay_epochs=10)
    assert b" " not in result


def test_encode_recovery_spec_deterministic() -> None:
    a = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="cc" * 32)
    b = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="cc" * 32)
    assert a == b


def test_encode_recovery_spec_threshold_multiparty() -> None:
    result = encode_recovery_spec(
        RecoverySpecType.THRESHOLD_MULTIPARTY,
        threshold=2,
        pk_hexes=["aa" * 32, "bb" * 32],
    )
    payload = json.loads(result.decode())
    assert payload["type"] == "threshold_multiparty"
    assert payload["threshold"] == 2
    assert len(payload["pk_hexes"]) == 2


# ---------------------------------------------------------------------------
# GenesisRecord — from_identity_seed
# ---------------------------------------------------------------------------

def _make_record(seed: bytes = _SEED_32) -> GenesisRecord:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    return GenesisRecord.from_identity_seed(
        identity_seed=seed,
        canonical_root_pk_hex=_FAKE_MLDSA_PK,
        recovery_spec_bytes=spec_bytes,
    )


def test_genesis_record_from_identity_seed_fields_present() -> None:
    rec = _make_record()
    assert len(rec.identity_seed_commitment) == 96
    assert len(rec.canonical_root_pk) == 3328
    assert len(rec.recovery_commitment) == 96
    assert rec.personhood_commitment is None


def test_genesis_record_from_identity_seed_with_personhood() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(
        identity_seed=_SEED_32,
        canonical_root_pk_hex=_FAKE_MLDSA_PK,
        recovery_spec_bytes=spec_bytes,
        personhood_proof_bytes=b"biometric-proof-data",
    )
    assert rec.personhood_commitment is not None
    assert len(rec.personhood_commitment) == 96


def test_genesis_record_from_identity_seed_is_deterministic() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec1 = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    rec2 = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    assert rec1.identity_seed_commitment == rec2.identity_seed_commitment
    assert rec1.recovery_commitment == rec2.recovery_commitment


def test_genesis_record_identity_seed_commitment_matches_standalone() -> None:
    rec = _make_record()
    expected = compute_identity_seed_commitment(_SEED_32)
    assert rec.identity_seed_commitment == expected


def test_genesis_record_recovery_commitment_matches_standalone() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    bf = derive_blinding_factor(_SEED_32)
    expected = compute_recovery_commitment(spec_bytes, bf)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    assert rec.recovery_commitment == expected


def test_genesis_record_different_seeds_produce_different_commitments() -> None:
    rec_a = _make_record(_SEED_32)
    rec_b = _make_record(_SEED_32_B)
    assert rec_a.identity_seed_commitment != rec_b.identity_seed_commitment
    assert rec_a.recovery_commitment != rec_b.recovery_commitment


# ---------------------------------------------------------------------------
# GenesisRecord — validate()
# ---------------------------------------------------------------------------

def test_genesis_record_validate_passes_for_valid_record() -> None:
    rec = _make_record()
    rec.validate()  # must not raise


def test_genesis_record_validate_passes_with_personhood() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes, b"proof")
    rec.validate()


def test_genesis_record_validate_rejects_bad_identity_commitment() -> None:
    rec = _make_record()
    rec.identity_seed_commitment = "short"
    with pytest.raises(GenesisRecordError) as exc:
        rec.validate()
    assert "cdl_069_genesis_invalid_identity_seed_commitment" in exc.value.token


def test_genesis_record_validate_rejects_uppercase_commitment() -> None:
    rec = _make_record()
    rec.identity_seed_commitment = "A" * 96
    with pytest.raises(GenesisRecordError) as exc:
        rec.validate()
    assert "cdl_069_genesis_invalid_identity_seed_commitment" in exc.value.token


def test_genesis_record_validate_rejects_bad_pk_length() -> None:
    rec = _make_record()
    rec.canonical_root_pk = "ab" * 100  # wrong length
    with pytest.raises(GenesisRecordError) as exc:
        rec.validate()
    assert "cdl_069_genesis_invalid_canonical_root_pk" in exc.value.token


def test_genesis_record_validate_rejects_uppercase_pk() -> None:
    rec = _make_record()
    rec.canonical_root_pk = "AB" * 1664  # uppercase
    with pytest.raises(GenesisRecordError) as exc:
        rec.validate()
    assert "cdl_069_genesis_invalid_canonical_root_pk" in exc.value.token


def test_genesis_record_validate_rejects_bad_recovery_commitment() -> None:
    rec = _make_record()
    rec.recovery_commitment = "zz" * 48  # non-hex
    with pytest.raises(GenesisRecordError) as exc:
        rec.validate()
    assert "cdl_069_genesis_invalid_recovery_commitment" in exc.value.token


def test_genesis_record_validate_rejects_bad_personhood_commitment() -> None:
    rec = _make_record()
    rec.personhood_commitment = "x" * 50  # wrong length
    with pytest.raises(GenesisRecordError) as exc:
        rec.validate()
    assert "cdl_069_genesis_invalid_personhood_commitment" in exc.value.token


# ---------------------------------------------------------------------------
# GenesisRecord — to_canonical_bytes()
# ---------------------------------------------------------------------------

def test_genesis_record_to_canonical_bytes_is_valid_json() -> None:
    rec = _make_record()
    payload = json.loads(rec.to_canonical_bytes().decode())
    assert "identity_seed_commitment" in payload
    assert "canonical_root_pk" in payload
    assert "recovery_commitment" in payload
    assert "personhood_commitment" not in payload  # None → omitted


def test_genesis_record_to_canonical_bytes_includes_personhood_when_set() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes, b"proof")
    payload = json.loads(rec.to_canonical_bytes().decode())
    assert "personhood_commitment" in payload


def test_genesis_record_to_canonical_bytes_has_sorted_keys() -> None:
    rec = _make_record()
    payload = json.loads(rec.to_canonical_bytes().decode())
    keys = list(payload.keys())
    assert keys == sorted(keys)


def test_genesis_record_to_canonical_bytes_no_spaces() -> None:
    rec = _make_record()
    assert b" " not in rec.to_canonical_bytes()


# ---------------------------------------------------------------------------
# RecoveryTransaction — validate_against_record()
# ---------------------------------------------------------------------------

def _make_recovery_tx(
    genesis_record: GenesisRecord,
    recovery_spec_bytes: bytes,
    new_pk: str | None = None,
) -> RecoveryTransaction:
    return RecoveryTransaction(
        old_canonical_root_pk=genesis_record.canonical_root_pk,
        new_canonical_root_pk=new_pk or ("cd" * 1664),
        identity_seed_commitment=genesis_record.identity_seed_commitment,
        recovery_spec=recovery_spec_bytes,
        authorization=b"mock-authorization",
    )


def test_recovery_transaction_validate_passes() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    epoch = tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert epoch == 100  # no freeze_from_epoch set → returns current_epoch


def test_recovery_transaction_freeze_clamping_future() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    tx.freeze_from_epoch = 200
    epoch = tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert epoch == 200  # future freeze accepted


def test_recovery_transaction_freeze_clamping_past() -> None:
    """freeze_from_epoch in the past is clamped to current_epoch (no retroactive invalidation)."""
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    tx.freeze_from_epoch = 50
    epoch = tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert epoch == 100  # clamped: max(100, 50) = 100


def test_recovery_transaction_identity_seed_mismatch_rejected() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    tx.identity_seed_commitment = "00" * 48  # wrong commitment
    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert "cdl_069_recovery_identity_seed_commitment_mismatch" in exc.value.token


def test_recovery_transaction_wrong_recovery_spec_rejected() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    tx.recovery_spec = b"wrong-spec"  # different pre-image
    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert "cdl_069_recovery_commitment_mismatch" in exc.value.token


def test_recovery_transaction_wrong_seed_rejected() -> None:
    """Blinding factor derived from wrong seed → commitment mismatch."""
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(rec, _SEED_32_B, current_epoch=100)  # wrong seed
    assert "cdl_069_recovery_commitment_mismatch" in exc.value.token


def test_recovery_transaction_invalid_new_pk_rejected() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes, new_pk="tooshort")
    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert "cdl_069_recovery_invalid_new_pk" in exc.value.token


# ---------------------------------------------------------------------------
# RecoveryTransaction — to_canonical_bytes()
# ---------------------------------------------------------------------------

def test_recovery_transaction_to_canonical_bytes_is_valid_json() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    payload = json.loads(tx.to_canonical_bytes().decode())
    assert "old_canonical_root_pk" in payload
    assert "new_canonical_root_pk" in payload
    assert "identity_seed_commitment" in payload
    assert "freeze_from_epoch" not in payload  # None → omitted


def test_recovery_transaction_to_canonical_bytes_includes_freeze_when_set() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    tx.freeze_from_epoch = 500
    payload = json.loads(tx.to_canonical_bytes().decode())
    assert payload["freeze_from_epoch"] == 500


def test_recovery_transaction_to_canonical_bytes_sorted_keys() -> None:
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = _make_recovery_tx(rec, spec_bytes)
    tx.freeze_from_epoch = 100
    payload = json.loads(tx.to_canonical_bytes().decode())
    keys = list(payload.keys())
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# Blinding factor domain separation: commitment ≠ identity_seed_commitment
# ---------------------------------------------------------------------------

def test_blinding_factor_domain_separates_from_identity_commitment() -> None:
    """The blinded commitment must differ from the plain identity_seed_commitment."""
    seed = b"\x42" * 32
    plain_commit = compute_identity_seed_commitment(seed)
    bf = derive_blinding_factor(seed)
    spec = b"any-spec"
    recovery_commit = compute_recovery_commitment(spec, bf)
    # Commitments derived from the same seed must be distinct due to domain separation
    assert plain_commit != recovery_commit


# ---------------------------------------------------------------------------
# F7: old_canonical_root_pk must match genesis record in validate_against_record
# ---------------------------------------------------------------------------

def test_recovery_transaction_old_pk_mismatch_rejected() -> None:
    """validate_against_record must reject if old_canonical_root_pk ≠ genesis canonical_root_pk."""
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = RecoveryTransaction(
        old_canonical_root_pk="ef" * 1664,  # wrong — not the key in the genesis record
        new_canonical_root_pk="cd" * 1664,
        identity_seed_commitment=rec.identity_seed_commitment,
        recovery_spec=spec_bytes,
        authorization=b"mock",
    )
    with pytest.raises(GenesisRecordError) as exc:
        tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert "cdl_069_recovery_old_pk_mismatch" in exc.value.token


def test_recovery_transaction_old_pk_matches_passes() -> None:
    """validate_against_record passes when old_canonical_root_pk matches genesis record."""
    spec_bytes = encode_recovery_spec(RecoverySpecType.SINGLE_KEY_SPHINCS, pk_hex="aa" * 32)
    rec = GenesisRecord.from_identity_seed(_SEED_32, _FAKE_MLDSA_PK, spec_bytes)
    tx = RecoveryTransaction(
        old_canonical_root_pk=_FAKE_MLDSA_PK,  # correct match
        new_canonical_root_pk="cd" * 1664,
        identity_seed_commitment=rec.identity_seed_commitment,
        recovery_spec=spec_bytes,
        authorization=b"mock",
    )
    epoch = tx.validate_against_record(rec, _SEED_32, current_epoch=100)
    assert epoch == 100


# ---------------------------------------------------------------------------
# F8: compute_recovery_commitment / compute_personhood_commitment type checks
# ---------------------------------------------------------------------------

def test_recovery_commitment_rejects_non_bytes_spec() -> None:
    bf = derive_blinding_factor(_SEED_32)
    with pytest.raises(GenesisRecordError) as exc:
        compute_recovery_commitment("not bytes", bf)  # type: ignore[arg-type]
    assert "cdl_069_genesis_invalid_recovery_spec" in exc.value.token


def test_recovery_commitment_rejects_non_bytes_blinding_factor() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        compute_recovery_commitment(b"spec", "not bytes")  # type: ignore[arg-type]
    assert "cdl_069_genesis_invalid_blinding_factor" in exc.value.token


def test_recovery_commitment_rejects_wrong_length_blinding_factor() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        compute_recovery_commitment(b"spec", b"\x00" * 32)  # 32 bytes, not 48
    assert "cdl_069_genesis_invalid_blinding_factor" in exc.value.token


def test_personhood_commitment_rejects_non_bytes_proof() -> None:
    bf = derive_blinding_factor(_SEED_32)
    with pytest.raises(GenesisRecordError) as exc:
        compute_personhood_commitment("not bytes", bf)  # type: ignore[arg-type]
    assert "cdl_069_genesis_invalid_personhood_proof" in exc.value.token


def test_personhood_commitment_rejects_wrong_length_blinding_factor() -> None:
    with pytest.raises(GenesisRecordError) as exc:
        compute_personhood_commitment(b"proof", b"\x00" * 16)  # wrong length
    assert "cdl_069_genesis_invalid_blinding_factor" in exc.value.token
