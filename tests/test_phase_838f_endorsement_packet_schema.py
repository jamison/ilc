"""Phase 838f — CDL-069 endorsement packet schema tests.

Covers:
  - derive_liveness_assertion known vector + error cases
  - verify_liveness_assertion
  - EndorsementPacket.validate() — required fields, constraints, liveness mismatch
  - EndorsementPacket.is_active_at() — window logic
  - EndorsementPacket.to_signing_payload() — canonical JSON, sorted keys, optional fields
  - EndorsementPacket.build() — auto-derives liveness_assertion
  - check_endorsement_window
  - build_cose_tbs_bytes
  - Version and dependency tokens
"""
from __future__ import annotations

import hashlib
import json

import pytest

from ilc_core.identity.endorsement_packet_schema import (
    CURRENT_PROTOCOL_VERSION,
    ENDORSEMENT_PACKET_SCHEMA_VERSION,
    MAX_ENDORSEMENT_WINDOW_EPOCHS,
    CDL_069_DEPENDENCY,
    COSE_ALG_MLDSA65_CANDIDATE,
    EndorsementPacket,
    EndorsementPacketSchemaError,
    build_cose_tbs_bytes,
    check_endorsement_window,
    derive_liveness_assertion,
    verify_liveness_assertion,
)

_AGENT_ID = "a0" * 48          # 96 hex chars
_EPHEMERAL_PK = "b1" * 48      # 96 hex chars (BLS G1)
_MLDSA_PK = "cd" * 1664        # 3328 hex chars
_CID = "bafy2bzaceab3wcn"


# ---------------------------------------------------------------------------
# Version and dependency tokens
# ---------------------------------------------------------------------------

def test_schema_version_token() -> None:
    assert ENDORSEMENT_PACKET_SCHEMA_VERSION == "endorsement_packet_schema_838f.v0.1"


def test_cdl_069_dependency_token() -> None:
    assert CDL_069_DEPENDENCY == "cdl_069_opens_phase_838"


def test_current_protocol_version_is_1() -> None:
    assert CURRENT_PROTOCOL_VERSION == 1


def test_max_endorsement_window_epochs() -> None:
    assert MAX_ENDORSEMENT_WINDOW_EPOCHS == 1440


# ---------------------------------------------------------------------------
# derive_liveness_assertion
# ---------------------------------------------------------------------------

def test_liveness_assertion_returns_64_hex() -> None:
    result = derive_liveness_assertion(_AGENT_ID, 100)
    assert isinstance(result, str)
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_liveness_assertion_known_vector() -> None:
    agent_id = "a0" * 48
    epoch_id = 42
    domain = b"ilc-liveness-v1:"
    expected = hashlib.sha256(
        domain + agent_id.encode() + epoch_id.to_bytes(8, "big")
    ).hexdigest()
    assert derive_liveness_assertion(agent_id, epoch_id) == expected


def test_liveness_assertion_is_deterministic() -> None:
    assert derive_liveness_assertion(_AGENT_ID, 100) == derive_liveness_assertion(_AGENT_ID, 100)


def test_liveness_assertion_differs_for_different_epochs() -> None:
    assert derive_liveness_assertion(_AGENT_ID, 100) != derive_liveness_assertion(_AGENT_ID, 101)


def test_liveness_assertion_differs_for_different_agent_ids() -> None:
    agent_b = "b0" * 48
    assert derive_liveness_assertion(_AGENT_ID, 100) != derive_liveness_assertion(agent_b, 100)


def test_liveness_assertion_rejects_wrong_length_agent_id() -> None:
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        derive_liveness_assertion("ab" * 47, 100)  # 94 chars
    assert "cdl_069_endorsement_invalid_agent_id_for_liveness" in exc.value.token


def test_liveness_assertion_rejects_non_string_agent_id() -> None:
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        derive_liveness_assertion(12345, 100)  # type: ignore[arg-type]
    assert "cdl_069_endorsement_invalid_agent_id_for_liveness" in exc.value.token


def test_liveness_assertion_rejects_negative_epoch_id() -> None:
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        derive_liveness_assertion(_AGENT_ID, -1)
    assert "cdl_069_endorsement_invalid_epoch_id_for_liveness" in exc.value.token


def test_liveness_assertion_rejects_non_int_epoch_id() -> None:
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        derive_liveness_assertion(_AGENT_ID, "100")  # type: ignore[arg-type]
    assert "cdl_069_endorsement_invalid_epoch_id_for_liveness" in exc.value.token


# ---------------------------------------------------------------------------
# verify_liveness_assertion
# ---------------------------------------------------------------------------

def test_verify_liveness_assertion_correct() -> None:
    la = derive_liveness_assertion(_AGENT_ID, 100)
    assert verify_liveness_assertion(la, _AGENT_ID, 100)


def test_verify_liveness_assertion_wrong_epoch() -> None:
    la = derive_liveness_assertion(_AGENT_ID, 100)
    assert not verify_liveness_assertion(la, _AGENT_ID, 101)


def test_verify_liveness_assertion_wrong_agent_id() -> None:
    la = derive_liveness_assertion(_AGENT_ID, 100)
    assert not verify_liveness_assertion(la, "ff" * 48, 100)


def test_verify_liveness_assertion_wrong_length_returns_false() -> None:
    assert not verify_liveness_assertion("ab" * 16, _AGENT_ID, 100)


# ---------------------------------------------------------------------------
# EndorsementPacket.build() — convenience constructor
# ---------------------------------------------------------------------------

def _make_packet(
    epoch_id: int = 100,
    sequence_number: int = 1,
    valid_epochs: int = 1,
    agent_id: str = _AGENT_ID,
    ephemeral_pk: str = _EPHEMERAL_PK,
    **kwargs: object,
) -> EndorsementPacket:
    return EndorsementPacket.build(
        agent_id=agent_id,
        epoch_id=epoch_id,
        sequence_number=sequence_number,
        ephemeral_signing_pk=ephemeral_pk,
        valid_epochs=valid_epochs,
        agent_state_root=_CID,
        **kwargs,
    )


def test_build_auto_derives_liveness() -> None:
    pkt = _make_packet()
    expected = derive_liveness_assertion(_AGENT_ID, 100)
    assert pkt.liveness_assertion == expected


def test_build_sets_protocol_version_to_1() -> None:
    pkt = _make_packet()
    assert pkt.protocol_version == CURRENT_PROTOCOL_VERSION


def test_build_passes_validate() -> None:
    pkt = _make_packet()
    pkt.validate()  # must not raise


def test_build_with_optional_supersedes() -> None:
    pkt = _make_packet(supersedes_epoch_id=90)
    pkt.validate()
    assert pkt.supersedes_epoch_id == 90


def test_build_with_canonical_root_pk() -> None:
    pkt = _make_packet(canonical_root_pk=_MLDSA_PK)
    pkt.validate()
    assert pkt.canonical_root_pk == _MLDSA_PK


# ---------------------------------------------------------------------------
# EndorsementPacket.validate() — required field errors
# ---------------------------------------------------------------------------

def test_validate_rejects_wrong_protocol_version() -> None:
    pkt = _make_packet()
    pkt.protocol_version = 2
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_protocol_version" in exc.value.token


def test_validate_rejects_bad_agent_id_length() -> None:
    pkt = _make_packet()
    pkt.agent_id = "ab" * 47  # 94 chars
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_agent_id" in exc.value.token


def test_validate_rejects_uppercase_agent_id() -> None:
    pkt = _make_packet()
    pkt.agent_id = "A0" * 48
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_agent_id" in exc.value.token


def test_validate_rejects_negative_epoch_id() -> None:
    pkt = EndorsementPacket(
        protocol_version=1,
        agent_id=_AGENT_ID,
        epoch_id=-1,
        sequence_number=1,
        ephemeral_signing_pk=_EPHEMERAL_PK,
        valid_epochs=1,
        liveness_assertion="a" * 64,
        agent_state_root=_CID,
    )
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_epoch_id" in exc.value.token


def test_validate_rejects_negative_sequence_number() -> None:
    pkt = _make_packet()
    pkt.sequence_number = -1
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_sequence_number" in exc.value.token


def test_validate_rejects_bad_ephemeral_pk_length() -> None:
    pkt = _make_packet()
    pkt.ephemeral_signing_pk = "ab" * 47  # 94 chars
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_ephemeral_signing_pk" in exc.value.token


def test_validate_rejects_valid_epochs_zero() -> None:
    pkt = _make_packet(valid_epochs=1)
    pkt.valid_epochs = 0
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_valid_epochs" in exc.value.token


def test_validate_rejects_valid_epochs_above_max() -> None:
    pkt = _make_packet(valid_epochs=MAX_ENDORSEMENT_WINDOW_EPOCHS + 1)
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_valid_epochs" in exc.value.token


def test_validate_accepts_valid_epochs_at_max() -> None:
    pkt = _make_packet(valid_epochs=MAX_ENDORSEMENT_WINDOW_EPOCHS)
    pkt.validate()  # must not raise


def test_validate_rejects_bad_liveness_assertion_length() -> None:
    pkt = _make_packet()
    pkt.liveness_assertion = "ab" * 16  # 32 chars, not 64
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_liveness_assertion" in exc.value.token


def test_validate_rejects_liveness_assertion_mismatch() -> None:
    """Wrong liveness assertion (right length, wrong value)."""
    pkt = _make_packet()
    pkt.liveness_assertion = "cc" * 32  # correct length but wrong hash
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_liveness_assertion_mismatch" in exc.value.token


def test_validate_rejects_empty_agent_state_root() -> None:
    pkt = _make_packet()
    pkt.agent_state_root = ""
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_agent_state_root" in exc.value.token


def test_validate_rejects_non_string_agent_state_root() -> None:
    pkt = _make_packet()
    pkt.agent_state_root = 12345  # type: ignore[assignment]
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_agent_state_root" in exc.value.token


def test_validate_rejects_bad_supersedes_epoch_id() -> None:
    pkt = _make_packet(supersedes_epoch_id=10)
    pkt.supersedes_epoch_id = -5
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_supersedes_epoch_id" in exc.value.token


def test_validate_rejects_bad_canonical_root_pk() -> None:
    pkt = _make_packet(canonical_root_pk=_MLDSA_PK)
    pkt.canonical_root_pk = "ab" * 100  # wrong length
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_canonical_root_pk" in exc.value.token


# ---------------------------------------------------------------------------
# EndorsementPacket.is_active_at()
# ---------------------------------------------------------------------------

def test_is_active_at_first_epoch() -> None:
    pkt = _make_packet(epoch_id=100, valid_epochs=5)
    assert pkt.is_active_at(100)


def test_is_active_at_last_epoch() -> None:
    pkt = _make_packet(epoch_id=100, valid_epochs=5)
    assert pkt.is_active_at(104)


def test_is_active_at_just_expired() -> None:
    pkt = _make_packet(epoch_id=100, valid_epochs=5)
    assert not pkt.is_active_at(105)  # epoch_id + valid_epochs


def test_is_active_at_before_epoch_id() -> None:
    pkt = _make_packet(epoch_id=100, valid_epochs=5)
    assert not pkt.is_active_at(99)


def test_is_active_at_single_epoch_window() -> None:
    pkt = _make_packet(epoch_id=100, valid_epochs=1)
    assert pkt.is_active_at(100)
    assert not pkt.is_active_at(101)


def test_is_active_at_max_window() -> None:
    pkt = _make_packet(epoch_id=0, valid_epochs=MAX_ENDORSEMENT_WINDOW_EPOCHS)
    assert pkt.is_active_at(0)
    assert pkt.is_active_at(MAX_ENDORSEMENT_WINDOW_EPOCHS - 1)
    assert not pkt.is_active_at(MAX_ENDORSEMENT_WINDOW_EPOCHS)


# ---------------------------------------------------------------------------
# EndorsementPacket.to_signing_payload()
# ---------------------------------------------------------------------------

def test_to_signing_payload_is_valid_json() -> None:
    pkt = _make_packet()
    payload = json.loads(pkt.to_signing_payload().decode())
    for field in (
        "protocol_version", "agent_id", "epoch_id", "sequence_number",
        "ephemeral_signing_pk", "valid_epochs", "liveness_assertion",
        "agent_state_root",
    ):
        assert field in payload


def test_to_signing_payload_sorted_keys() -> None:
    pkt = _make_packet()
    payload = json.loads(pkt.to_signing_payload().decode())
    keys = list(payload.keys())
    assert keys == sorted(keys)


def test_to_signing_payload_no_spaces() -> None:
    pkt = _make_packet()
    assert b" " not in pkt.to_signing_payload()


def test_to_signing_payload_omits_none_optional_fields() -> None:
    pkt = _make_packet()
    payload = json.loads(pkt.to_signing_payload().decode())
    for optional in ("supersedes_epoch_id", "canonical_root_pk", "capability_declaration",
                     "stake_position", "next_epoch_intent"):
        assert optional not in payload


def test_to_signing_payload_includes_supersedes_when_set() -> None:
    pkt = _make_packet(supersedes_epoch_id=90)
    payload = json.loads(pkt.to_signing_payload().decode())
    assert payload["supersedes_epoch_id"] == 90


def test_to_signing_payload_includes_canonical_root_pk_when_set() -> None:
    pkt = _make_packet(canonical_root_pk=_MLDSA_PK)
    payload = json.loads(pkt.to_signing_payload().decode())
    assert payload["canonical_root_pk"] == _MLDSA_PK


def test_to_signing_payload_includes_capability_declaration() -> None:
    pkt = _make_packet(capability_declaration="compute-v1")
    payload = json.loads(pkt.to_signing_payload().decode())
    assert payload["capability_declaration"] == "compute-v1"


def test_to_signing_payload_is_deterministic() -> None:
    pkt = _make_packet()
    assert pkt.to_signing_payload() == pkt.to_signing_payload()


# ---------------------------------------------------------------------------
# check_endorsement_window
# ---------------------------------------------------------------------------

def test_check_endorsement_window_active() -> None:
    pkt = _make_packet(epoch_id=100, valid_epochs=10)
    assert check_endorsement_window(pkt, 105)


def test_check_endorsement_window_expired() -> None:
    pkt = _make_packet(epoch_id=100, valid_epochs=5)
    assert not check_endorsement_window(pkt, 105)


# ---------------------------------------------------------------------------
# build_cose_tbs_bytes
# ---------------------------------------------------------------------------

def test_build_cose_tbs_bytes_includes_domain_tag() -> None:
    pkt = _make_packet()
    payload = pkt.to_signing_payload()
    tbs = build_cose_tbs_bytes(payload)
    assert tbs.startswith(b"ILC-EndorsementPacket-v1:")


def test_build_cose_tbs_bytes_includes_payload() -> None:
    pkt = _make_packet()
    payload = pkt.to_signing_payload()
    tbs = build_cose_tbs_bytes(payload)
    assert payload in tbs


def test_build_cose_tbs_bytes_is_deterministic() -> None:
    pkt = _make_packet()
    payload = pkt.to_signing_payload()
    assert build_cose_tbs_bytes(payload) == build_cose_tbs_bytes(payload)


def test_build_cose_tbs_bytes_differs_with_external_aad() -> None:
    pkt = _make_packet()
    payload = pkt.to_signing_payload()
    assert build_cose_tbs_bytes(payload, b"aad-data") != build_cose_tbs_bytes(payload, b"")


def test_cose_alg_candidate_is_defined() -> None:
    assert isinstance(COSE_ALG_MLDSA65_CANDIDATE, int)


# ---------------------------------------------------------------------------
# Sequence number ordering invariant
# ---------------------------------------------------------------------------

def test_sequence_number_zero_is_valid() -> None:
    """sequence_number=0 is valid (first packet ever issued by an agent)."""
    pkt = _make_packet(sequence_number=0)
    pkt.validate()


def test_sequence_number_max_u64_is_valid() -> None:
    pkt = _make_packet(sequence_number=2**64 - 1)
    pkt.validate()


def test_sequence_number_above_u64_rejected() -> None:
    pkt = _make_packet(sequence_number=2**64)
    with pytest.raises(EndorsementPacketSchemaError) as exc:
        pkt.validate()
    assert "cdl_069_endorsement_invalid_sequence_number" in exc.value.token


# ---------------------------------------------------------------------------
# epoch_id=0 (genesis epoch) is valid
# ---------------------------------------------------------------------------

def test_epoch_id_zero_is_valid() -> None:
    pkt = _make_packet(epoch_id=0)
    pkt.validate()
