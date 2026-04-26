"""Phase 838c — CDL-069 epoch endorsement runtime tests."""
from __future__ import annotations

import hashlib
import json
import pytest

from ilc_core.identity.epoch_endorsement_runtime import (
    EPOCH_ENDORSEMENT_RUNTIME_VERSION,
    CDL_069_DEPENDENCY,
    PROTOCOL_VERSION,
    MAX_ENDORSEMENT_WINDOW_EPOCHS_DEFAULT,
    EndorsementError,
    EpochEndorsementPacket,
    EpochCloseAttestation,
    EndorsementCache,
    derive_liveness_assertion,
    derive_epoch_nonce,
    compute_ecu_commitment,
    verify_ecu_commitment,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

_AGENT_ID = "a" * 96          # 96-char hex
_AGENT_ID_2 = "b" * 96
_EPOCH = 1000
_SEQ = 1
_EPH_PK = "c" * 96            # 96-char BLS12-381 G1 pk (48 bytes = 96 hex chars)
_EPH_PK_2 = "d" * 96          # 96-char BLS12-381 G1 pk
_STATE_ROOT = "bafybeiabc123"
_ID_SEED_COMMIT = "e" * 96    # 96-char identity_seed_commitment


def _liveness(agent_id: str = _AGENT_ID, epoch_id: int = _EPOCH) -> str:
    return derive_liveness_assertion(agent_id, epoch_id)


def _make_packet(
    *,
    agent_id: str = _AGENT_ID,
    epoch_id: int = _EPOCH,
    seq: int = _SEQ,
    eph_pk: str = _EPH_PK,
    valid_epochs: int = 1,
    supersedes_epoch_id: int | None = None,
    state_root: str = _STATE_ROOT,
) -> EpochEndorsementPacket:
    return EpochEndorsementPacket(
        protocol_version=PROTOCOL_VERSION,
        agent_id=agent_id,
        epoch_id=epoch_id,
        sequence_number=seq,
        ephemeral_signing_pk=eph_pk,
        valid_epochs=valid_epochs,
        liveness_assertion=_liveness(agent_id, epoch_id),
        agent_state_root=state_root,
        supersedes_epoch_id=supersedes_epoch_id,
    )


# ---------------------------------------------------------------------------
# Module tokens
# ---------------------------------------------------------------------------

def test_runtime_version_token() -> None:
    assert EPOCH_ENDORSEMENT_RUNTIME_VERSION == "epoch_endorsement_runtime_838c.v0.1"


def test_cdl_069_dependency_token() -> None:
    assert CDL_069_DEPENDENCY == "cdl_069_opens_phase_838"


def test_module_presence_token() -> None:
    import ilc_core.identity.epoch_endorsement_runtime as m
    assert "epoch_endorsement_runtime_838c_present" in m.__doc__


# ---------------------------------------------------------------------------
# liveness_assertion derivation (finding I2)
# ---------------------------------------------------------------------------

def test_liveness_assertion_is_deterministic() -> None:
    a = derive_liveness_assertion(_AGENT_ID, _EPOCH)
    b = derive_liveness_assertion(_AGENT_ID, _EPOCH)
    assert a == b


def test_liveness_assertion_is_64_hex_chars() -> None:
    la = derive_liveness_assertion(_AGENT_ID, _EPOCH)
    assert len(la) == 64
    assert all(c in "0123456789abcdef" for c in la)


def test_liveness_assertion_differs_by_epoch() -> None:
    a = derive_liveness_assertion(_AGENT_ID, 1000)
    b = derive_liveness_assertion(_AGENT_ID, 1001)
    assert a != b


def test_liveness_assertion_differs_by_agent() -> None:
    a = derive_liveness_assertion(_AGENT_ID, _EPOCH)
    b = derive_liveness_assertion(_AGENT_ID_2, _EPOCH)
    assert a != b


# ---------------------------------------------------------------------------
# ECU commitment nonce (finding C2)
# ---------------------------------------------------------------------------

def test_epoch_nonce_is_deterministic() -> None:
    n1 = derive_epoch_nonce(_ID_SEED_COMMIT, _EPOCH)
    n2 = derive_epoch_nonce(_ID_SEED_COMMIT, _EPOCH)
    assert n1 == n2


def test_epoch_nonce_differs_by_epoch() -> None:
    n1 = derive_epoch_nonce(_ID_SEED_COMMIT, 1000)
    n2 = derive_epoch_nonce(_ID_SEED_COMMIT, 1001)
    assert n1 != n2


def test_ecu_commitment_is_deterministic() -> None:
    c1 = compute_ecu_commitment("50", _ID_SEED_COMMIT, _EPOCH)
    c2 = compute_ecu_commitment("50", _ID_SEED_COMMIT, _EPOCH)
    assert c1 == c2


def test_ecu_commitment_differs_from_naive_hash() -> None:
    """Commitment must not be sha256(amount) — nonce is required."""
    naive = hashlib.sha256(b"50").hexdigest()
    with_nonce = compute_ecu_commitment("50", _ID_SEED_COMMIT, _EPOCH)
    assert with_nonce != naive


def test_ecu_commitment_differs_by_amount() -> None:
    c50 = compute_ecu_commitment("50", _ID_SEED_COMMIT, _EPOCH)
    c51 = compute_ecu_commitment("51", _ID_SEED_COMMIT, _EPOCH)
    assert c50 != c51


def test_ecu_commitment_differs_by_epoch() -> None:
    c1 = compute_ecu_commitment("50", _ID_SEED_COMMIT, 1000)
    c2 = compute_ecu_commitment("50", _ID_SEED_COMMIT, 1001)
    assert c1 != c2


def test_verify_ecu_commitment_correct() -> None:
    c = compute_ecu_commitment("100", _ID_SEED_COMMIT, _EPOCH)
    assert verify_ecu_commitment(c, "100", _ID_SEED_COMMIT, _EPOCH)


def test_verify_ecu_commitment_wrong_amount() -> None:
    c = compute_ecu_commitment("100", _ID_SEED_COMMIT, _EPOCH)
    assert not verify_ecu_commitment(c, "101", _ID_SEED_COMMIT, _EPOCH)


def test_verify_ecu_commitment_wrong_epoch() -> None:
    c = compute_ecu_commitment("100", _ID_SEED_COMMIT, _EPOCH)
    assert not verify_ecu_commitment(c, "100", _ID_SEED_COMMIT, _EPOCH + 1)


# ---------------------------------------------------------------------------
# EpochEndorsementPacket validation
# ---------------------------------------------------------------------------

def test_valid_packet_passes_validation() -> None:
    _make_packet().validate()  # must not raise


def test_wrong_protocol_version_rejected() -> None:
    p = _make_packet()
    p.protocol_version = 99
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_unknown_protocol_version" in exc.value.token


def test_short_agent_id_rejected() -> None:
    # Construct directly — _make_packet calls derive_liveness_assertion which also validates agent_id
    p = EpochEndorsementPacket(
        protocol_version=PROTOCOL_VERSION,
        agent_id="a" * 64,  # too short
        epoch_id=_EPOCH,
        sequence_number=_SEQ,
        ephemeral_signing_pk=_EPH_PK,
        valid_epochs=1,
        liveness_assertion="0" * 64,  # placeholder — validate() fails before liveness check
        agent_state_root=_STATE_ROOT,
    )
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_invalid_agent_id" in exc.value.token


def test_non_hex_agent_id_rejected() -> None:
    p = _make_packet()
    p.agent_id = "g" * 96
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_agent_id_not_hex" in exc.value.token


def test_negative_epoch_id_rejected() -> None:
    with pytest.raises(EndorsementError) as exc:
        _make_packet(epoch_id=-1)
    assert "cdl_069_endorsement_invalid_epoch_id" in exc.value.token


def test_negative_sequence_number_rejected() -> None:
    p = _make_packet(seq=-1)
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_invalid_sequence_number" in exc.value.token


def test_valid_epochs_zero_rejected() -> None:
    p = _make_packet(valid_epochs=0)
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_invalid_valid_epochs" in exc.value.token


def test_valid_epochs_exceeds_max_rejected() -> None:
    p = _make_packet(valid_epochs=MAX_ENDORSEMENT_WINDOW_EPOCHS_DEFAULT + 1)
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_invalid_valid_epochs" in exc.value.token


def test_valid_epochs_at_max_passes() -> None:
    _make_packet(valid_epochs=MAX_ENDORSEMENT_WINDOW_EPOCHS_DEFAULT).validate()


def test_wrong_liveness_assertion_rejected() -> None:
    p = _make_packet()
    p.liveness_assertion = "0" * 64  # wrong value
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_liveness_mismatch" in exc.value.token


def test_empty_state_root_rejected() -> None:
    p = _make_packet(state_root="")
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_missing_agent_state_root" in exc.value.token


def test_supersedes_epoch_id_negative_rejected() -> None:
    p = _make_packet(supersedes_epoch_id=-1)
    with pytest.raises(EndorsementError) as exc:
        p.validate()
    assert "cdl_069_endorsement_invalid_supersedes_epoch_id" in exc.value.token


def test_supersedes_epoch_id_none_passes() -> None:
    _make_packet(supersedes_epoch_id=None).validate()


def test_supersedes_epoch_id_valid_passes() -> None:
    _make_packet(supersedes_epoch_id=_EPOCH - 1).validate()


# ---------------------------------------------------------------------------
# Packet window logic
# ---------------------------------------------------------------------------

def test_is_active_at_start_epoch() -> None:
    p = _make_packet(epoch_id=100, valid_epochs=10)
    assert p.is_active_at(100)


def test_is_active_at_last_epoch_in_window() -> None:
    p = _make_packet(epoch_id=100, valid_epochs=10)
    assert p.is_active_at(109)


def test_is_not_active_at_epoch_after_window() -> None:
    p = _make_packet(epoch_id=100, valid_epochs=10)
    assert not p.is_active_at(110)


def test_is_not_active_before_start_epoch() -> None:
    p = _make_packet(epoch_id=100, valid_epochs=10)
    assert not p.is_active_at(99)


# ---------------------------------------------------------------------------
# Signing payload
# ---------------------------------------------------------------------------

def test_signing_payload_is_deterministic() -> None:
    p = _make_packet()
    assert p.to_signing_payload() == p.to_signing_payload()


def test_signing_payload_is_valid_json() -> None:
    p = _make_packet()
    payload = json.loads(p.to_signing_payload())
    assert payload["agent_id"] == _AGENT_ID
    assert payload["epoch_id"] == _EPOCH


def test_signing_payload_excludes_mldsa_signature() -> None:
    p = _make_packet()
    p.mldsa_signature = b"\x01\x02\x03"
    payload = json.loads(p.to_signing_payload())
    assert "mldsa_signature" not in payload


def test_signing_payload_includes_supersedes_when_present() -> None:
    p = _make_packet(supersedes_epoch_id=999)
    payload = json.loads(p.to_signing_payload())
    assert payload["supersedes_epoch_id"] == 999


def test_signing_payload_excludes_supersedes_when_none() -> None:
    p = _make_packet(supersedes_epoch_id=None)
    payload = json.loads(p.to_signing_payload())
    assert "supersedes_epoch_id" not in payload


# ---------------------------------------------------------------------------
# EpochCloseAttestation validation
# ---------------------------------------------------------------------------

def _make_attest(
    *,
    epoch_id: int = _EPOCH,
    agent_id: str = _AGENT_ID,
    sent: str = "0" * 64,
    received: str = "0" * 64,
    rep_delta: int = 0,
) -> EpochCloseAttestation:
    return EpochCloseAttestation(
        epoch_id=epoch_id,
        agent_id=agent_id,
        actions_root="bafyabc",
        ecu_sent_commitment=sent,
        ecu_received_commitment=received,
        reputation_delta=rep_delta,
    )


def test_valid_attestation_passes() -> None:
    _make_attest().validate()


def test_short_ecu_commitment_rejected() -> None:
    a = _make_attest(sent="abc")
    with pytest.raises(EndorsementError) as exc:
        a.validate()
    assert "cdl_069_attest_invalid_ecu_sent_commitment" in exc.value.token


def test_non_integer_reputation_delta_rejected() -> None:
    a = _make_attest()
    a.reputation_delta = "five"  # type: ignore[assignment]
    with pytest.raises(EndorsementError) as exc:
        a.validate()
    assert "cdl_069_attest_invalid_reputation_delta" in exc.value.token


def test_negative_reputation_delta_passes() -> None:
    _make_attest(rep_delta=-10).validate()


# ---------------------------------------------------------------------------
# EndorsementCache — acceptance rules (finding I3: sequence ordering)
# ---------------------------------------------------------------------------

def test_cache_accepts_valid_packet() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet())
    assert len(cache) == 1


def test_cache_accepts_higher_sequence_number() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(seq=1))
    cache.accept_packet(_make_packet(seq=2))
    assert cache.get_packet(_AGENT_ID, _EPOCH).sequence_number == 2


def test_cache_rejects_lower_sequence_number() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(seq=5))
    with pytest.raises(EndorsementError) as exc:
        cache.accept_packet(_make_packet(seq=3))
    assert "cdl_069_endorsement_stale_sequence_number" in exc.value.token


def test_cache_rejects_duplicate_sequence_number() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(seq=1))
    with pytest.raises(EndorsementError) as exc:
        cache.accept_packet(_make_packet(seq=1))
    assert "cdl_069_endorsement_duplicate_sequence_number" in exc.value.token


def test_cache_returns_none_for_unknown_agent() -> None:
    cache = EndorsementCache()
    assert cache.get_packet(_AGENT_ID, _EPOCH) is None


def test_cache_returns_none_after_window_expires() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=5))
    assert cache.get_packet(_AGENT_ID, 105) is None


def test_cache_returns_packet_within_window() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=10))
    assert cache.get_packet(_AGENT_ID, 109) is not None


# ---------------------------------------------------------------------------
# EndorsementCache — ephemeral key validation (findings C3, I1)
# ---------------------------------------------------------------------------

def test_ephemeral_key_valid_in_window() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=10, eph_pk=_EPH_PK))
    assert cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 100)
    assert cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 109)


def test_ephemeral_key_invalid_after_window() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=5, eph_pk=_EPH_PK))
    assert not cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 105)


def test_superseded_ephemeral_key_rejected_at_supersede_epoch(
) -> None:
    """Finding C3: old key rejected at supersedes_epoch_id even before new packet propagates."""
    cache = EndorsementCache()
    # First packet with EPH_PK
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=10, eph_pk=_EPH_PK, seq=1))
    # Override packet supersedes EPH_PK from epoch 105
    override = _make_packet(
        epoch_id=105,
        valid_epochs=10,
        eph_pk=_EPH_PK_2,
        seq=2,
        supersedes_epoch_id=105,
    )
    cache.accept_packet(override)
    # Old key rejected at and after supersede epoch
    assert not cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 105)
    assert not cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 106)
    # New key is valid
    assert cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK_2, 105)


def test_wrong_ephemeral_key_rejected() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(eph_pk=_EPH_PK))
    assert not cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK_2, _EPOCH)


# ---------------------------------------------------------------------------
# EndorsementCache — recovery freeze (finding I4)
# ---------------------------------------------------------------------------

def test_freeze_clamped_to_current_epoch() -> None:
    """freeze_from_epoch < current_epoch must be silently clamped forward."""
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=50, eph_pk=_EPH_PK))
    effective = cache.apply_recovery_freeze(
        _AGENT_ID,
        old_canonical_root_pk="old_pk",
        freeze_from_epoch=50,   # past epoch
        current_epoch=120,
    )
    assert effective == 120  # clamped to current


def test_freeze_uses_freeze_epoch_when_future() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=50, eph_pk=_EPH_PK))
    effective = cache.apply_recovery_freeze(
        _AGENT_ID,
        old_canonical_root_pk="old_pk",
        freeze_from_epoch=130,
        current_epoch=120,
    )
    assert effective == 130  # freeze_from_epoch > current


def test_frozen_key_rejected_after_freeze_epoch() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=50, eph_pk=_EPH_PK))
    cache.apply_recovery_freeze(
        _AGENT_ID,
        old_canonical_root_pk="old_pk",
        freeze_from_epoch=110,
        current_epoch=105,
    )
    # Before freeze epoch — still valid
    assert cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 109)
    # At and after freeze epoch — rejected
    assert not cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 110)
    assert not cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 120)


# ---------------------------------------------------------------------------
# EndorsementCache — eviction
# ---------------------------------------------------------------------------

def test_evict_expired_removes_stale_entries() -> None:
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(
        agent_id=_AGENT_ID, epoch_id=100, valid_epochs=5, seq=1,
    ))
    cache.accept_packet(_make_packet(
        agent_id=_AGENT_ID_2, epoch_id=100, valid_epochs=20, seq=1,
    ))
    evicted = cache.evict_expired(current_epoch=106)
    assert evicted == 1
    assert len(cache) == 1
    assert cache.get_packet(_AGENT_ID_2, 106) is not None


def test_evict_expired_also_cleans_frozen_entries() -> None:
    """evict_expired must clean _frozen to prevent unbounded memory growth."""
    cache = EndorsementCache()
    cache.accept_packet(_make_packet(epoch_id=100, valid_epochs=5, seq=1))
    cache.apply_recovery_freeze(_AGENT_ID, "old_pk", freeze_from_epoch=110, current_epoch=100)
    assert _AGENT_ID in cache._frozen
    # Evict at epoch 106 (window epoch_id=100, valid_epochs=5 → expires at 105)
    cache.evict_expired(current_epoch=106)
    assert len(cache) == 0
    assert _AGENT_ID not in cache._frozen  # regression: was leaking before fix


def test_bool_rejected_as_protocol_version() -> None:
    """bool is a subclass of int in Python — must not pass protocol_version checks."""
    pkt = _make_packet()
    pkt.protocol_version = True  # True == 1, but is bool
    with pytest.raises(EndorsementError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_unknown_protocol_version" in exc.value.token


def test_bool_rejected_as_epoch_id() -> None:
    """bool True would serialize as JSON true, not 1."""
    pkt = EpochEndorsementPacket(
        protocol_version=PROTOCOL_VERSION,
        agent_id=_AGENT_ID,
        epoch_id=True,  # bool
        sequence_number=_SEQ,
        ephemeral_signing_pk=_EPH_PK,
        valid_epochs=1,
        liveness_assertion=_liveness(),
        agent_state_root=_STATE_ROOT,
    )
    with pytest.raises(EndorsementError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_epoch_id" in exc.value.token


def test_bool_rejected_as_valid_epochs() -> None:
    pkt = _make_packet()
    pkt.valid_epochs = True  # True == 1, is bool
    with pytest.raises(EndorsementError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_valid_epochs" in exc.value.token


def test_ecu_commitment_non_hex_rejected() -> None:
    """EpochCloseAttestation must reject commitments with non-hex characters."""
    attest = EpochCloseAttestation(
        epoch_id=100,
        agent_id=_AGENT_ID,
        actions_root="bafy123",
        ecu_sent_commitment="Z" * 64,  # correct length but not hex
        ecu_received_commitment="a" * 64,
        reputation_delta=0,
    )
    with pytest.raises(EndorsementError) as exc:
        attest.validate()
    assert "cdl_069_attest_ecu_sent_commitment_not_hex" in exc.value.token


def test_ecu_received_commitment_non_hex_rejected() -> None:
    attest = EpochCloseAttestation(
        epoch_id=100,
        agent_id=_AGENT_ID,
        actions_root="bafy123",
        ecu_sent_commitment="a" * 64,
        ecu_received_commitment="Q" * 64,  # correct length but not hex
        reputation_delta=0,
    )
    with pytest.raises(EndorsementError) as exc:
        attest.validate()
    assert "cdl_069_attest_ecu_received_commitment_not_hex" in exc.value.token


def test_superseded_key_valid_before_supersedes_epoch() -> None:
    """Old ephemeral key must remain valid for epochs strictly before supersedes_epoch_id."""
    cache = EndorsementCache()
    pkt1 = _make_packet(epoch_id=100, valid_epochs=20, seq=1, eph_pk=_EPH_PK)
    cache.accept_packet(pkt1)
    pkt2 = _make_packet(epoch_id=102, valid_epochs=20, seq=2, eph_pk=_EPH_PK_2,
                        supersedes_epoch_id=105)
    cache.accept_packet(pkt2)
    # Old key should still be valid at epoch 103 (< 105)
    assert cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 103) is True


def test_superseded_key_invalid_at_supersedes_epoch() -> None:
    """Old ephemeral key must be rejected at and after supersedes_epoch_id."""
    cache = EndorsementCache()
    pkt1 = _make_packet(epoch_id=100, valid_epochs=20, seq=1, eph_pk=_EPH_PK)
    cache.accept_packet(pkt1)
    pkt2 = _make_packet(epoch_id=102, valid_epochs=20, seq=2, eph_pk=_EPH_PK_2,
                        supersedes_epoch_id=105)
    cache.accept_packet(pkt2)
    # Old key must be rejected at epoch 105 (>= supersedes_epoch_id)
    assert cache.is_ephemeral_key_valid(_AGENT_ID, _EPH_PK, 105) is False


def test_derive_epoch_nonce_rejects_negative_epoch() -> None:
    """derive_epoch_nonce must raise, not OverflowError, on negative epoch_id."""
    with pytest.raises(EndorsementError) as exc:
        derive_epoch_nonce(_ID_SEED_COMMIT, -1)
    assert "cdl_069_epoch_nonce_invalid_epoch_id" in exc.value.token


def test_derive_epoch_nonce_rejects_invalid_commitment() -> None:
    with pytest.raises(EndorsementError) as exc:
        derive_epoch_nonce("tooshort", 100)
    assert "cdl_069_epoch_nonce_invalid_commitment" in exc.value.token


def test_compute_ecu_commitment_rejects_empty_total() -> None:
    with pytest.raises(EndorsementError) as exc:
        compute_ecu_commitment("", _ID_SEED_COMMIT, 100)
    assert "cdl_069_ecu_commit_invalid_total" in exc.value.token


# ---------------------------------------------------------------------------
# F1: ephemeral_signing_pk validation (was entirely missing)
# ---------------------------------------------------------------------------

def test_ephemeral_signing_pk_wrong_length_rejected() -> None:
    """ephemeral_signing_pk must be exactly 96 hex chars (BLS12-381 G1, 48 bytes)."""
    pkt = _make_packet()
    pkt.ephemeral_signing_pk = "c" * 64  # 64 chars — correct old fixture, wrong for BLS G1
    with pytest.raises(EndorsementError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_ephemeral_signing_pk" in exc.value.token


def test_ephemeral_signing_pk_empty_rejected() -> None:
    pkt = _make_packet()
    pkt.ephemeral_signing_pk = ""
    with pytest.raises(EndorsementError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_ephemeral_signing_pk" in exc.value.token


def test_ephemeral_signing_pk_non_hex_rejected() -> None:
    pkt = _make_packet()
    pkt.ephemeral_signing_pk = "G" * 96  # uppercase non-hex
    with pytest.raises(EndorsementError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_ephemeral_signing_pk_not_hex" in exc.value.token


def test_ephemeral_signing_pk_non_string_rejected() -> None:
    pkt = _make_packet()
    pkt.ephemeral_signing_pk = 12345  # type: ignore[assignment]
    with pytest.raises(EndorsementError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_ephemeral_signing_pk" in exc.value.token


# ---------------------------------------------------------------------------
# F2: EpochCloseAttestation.agent_id hex chars check (was length-only)
# ---------------------------------------------------------------------------

def test_attestation_agent_id_non_hex_rejected() -> None:
    """agent_id with correct length but non-hex characters must be rejected."""
    attest = _make_attest(agent_id="g" * 96)
    with pytest.raises(EndorsementError) as exc:
        attest.validate()
    assert "cdl_069_attest_agent_id_not_hex" in exc.value.token


# ---------------------------------------------------------------------------
# F3: EpochCloseAttestation bool guards on epoch_id and reputation_delta
# ---------------------------------------------------------------------------

def test_attestation_bool_rejected_as_epoch_id() -> None:
    """bool is a subclass of int — must not pass epoch_id validation."""
    attest = EpochCloseAttestation(
        epoch_id=True,  # type: ignore[arg-type]
        agent_id=_AGENT_ID, actions_root="bafy123",
        ecu_sent_commitment="a" * 64, ecu_received_commitment="b" * 64,
        reputation_delta=0,
    )
    with pytest.raises(EndorsementError) as exc:
        attest.validate()
    assert "cdl_069_attest_invalid_epoch_id" in exc.value.token


def test_attestation_bool_rejected_as_reputation_delta() -> None:
    """bool True/False must not be accepted as reputation_delta (serializes as JSON true/false)."""
    attest = _make_attest()
    attest.reputation_delta = True  # type: ignore[assignment]
    with pytest.raises(EndorsementError) as exc:
        attest.validate()
    assert "cdl_069_attest_invalid_reputation_delta" in exc.value.token


# ---------------------------------------------------------------------------
# F4: derive_liveness_assertion agent_id validation + bool epoch_id guard
# ---------------------------------------------------------------------------

def test_derive_liveness_assertion_rejects_short_agent_id() -> None:
    with pytest.raises(EndorsementError) as exc:
        derive_liveness_assertion("a" * 64, 100)  # 64 chars, not 96
    assert "cdl_069_endorsement_invalid_agent_id_for_liveness" in exc.value.token


def test_derive_liveness_assertion_rejects_non_string_agent_id() -> None:
    with pytest.raises(EndorsementError) as exc:
        derive_liveness_assertion(12345, 100)  # type: ignore[arg-type]
    assert "cdl_069_endorsement_invalid_agent_id_for_liveness" in exc.value.token


def test_derive_liveness_assertion_rejects_bool_epoch_id() -> None:
    """bool True == 1 but must not be accepted as epoch_id."""
    with pytest.raises(EndorsementError) as exc:
        derive_liveness_assertion(_AGENT_ID, True)  # type: ignore[arg-type]
    assert "cdl_069_endorsement_invalid_epoch_id" in exc.value.token


# ---------------------------------------------------------------------------
# F6: verify_ecu_commitment returns False on bad input, never raises
# ---------------------------------------------------------------------------

def test_verify_ecu_commitment_returns_false_on_empty_total() -> None:
    """verify_ecu_commitment is a predicate — must return False, not raise."""
    result = verify_ecu_commitment("a" * 64, "", _ID_SEED_COMMIT, 100)
    assert result is False


def test_verify_ecu_commitment_returns_false_on_invalid_commitment_input() -> None:
    result = verify_ecu_commitment("a" * 64, "50", "tooshort", 100)
    assert result is False
