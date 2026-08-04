# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.value_action.ilc_transfer_intent import (
    ILC_TRANSFER_ENABLED,
    ILC_TRANSFER_INTENT_VERSION,
    MAX_GRAPH_CONTEXT_ANCHOR_CHARS,
    MAX_NONCE_CHARS,
    ActionType,
    AgentActionEnvelope,
    ILCTransferIntent,
    validate_envelope,
)

SENDER_AGENT_ID = "a" * 96
RECIPIENT_AGENT_ID = "b" * 96
MODULE_PATH = Path("ilc_core/value_action/ilc_transfer_intent.py")


def _create(**overrides: object) -> AgentActionEnvelope:
    fields = {
        "sender_agent_id": SENDER_AGENT_ID,
        "recipient_agent_id": RECIPIENT_AGENT_ID,
        "amount_ilc": Decimal("12.5"),
        "nonce": "agent-a:1",
        "epoch": 0,
        "memo": "bounded public-RC transfer intent",
    }
    fields.update(overrides)
    return ILCTransferIntent.create(**fields)


def test_happy_path_create_envelope() -> None:
    env = _create(graph_context_anchor="graph:work-root-001")

    assert env.action_type is ActionType.ILC_TRANSFER
    assert env.sender_agent_id == SENDER_AGENT_ID
    assert env.recipient_agent_id == RECIPIENT_AGENT_ID
    assert env.amount_ilc == Decimal("12.5")
    assert env.nonce == "agent-a:1"
    assert env.epoch == 0
    assert env.graph_context_anchor == "graph:work-root-001"
    assert env.cose_signature is None
    assert ILC_TRANSFER_INTENT_VERSION == "ilc_transfer_intent_01.v0.1"


def test_self_transfer_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_self_transfer"):
        _create(recipient_agent_id=SENDER_AGENT_ID)


def test_non_finite_decimal_nan_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        _create(amount_ilc=Decimal("NaN"))


def test_non_finite_decimal_inf_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        _create(amount_ilc=Decimal("Infinity"))


def test_negative_amount_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_amount_not_positive"):
        _create(amount_ilc=Decimal("-1"))


def test_zero_amount_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_amount_not_positive"):
        _create(amount_ilc=Decimal("0"))


def test_float_amount_rejected() -> None:
    with pytest.raises(TypeError, match="invalid_envelope_amount_not_decimal"):
        _create(amount_ilc=1.0)


def test_memo_too_long_rejected() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_memo_too_long"):
        _create(memo="x" * 257)


@pytest.mark.parametrize("nonce", ["", " padded", "padded "])
def test_empty_or_noncanonical_nonce_rejected(nonce: str) -> None:
    with pytest.raises(ValueError, match="invalid_envelope_empty_nonce"):
        _create(nonce=nonce)


def test_epoch_must_be_non_negative_int_not_bool() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_epoch"):
        _create(epoch=-1)
    with pytest.raises(ValueError, match="invalid_envelope_epoch"):
        _create(epoch=True)


def test_agent_ids_must_be_96_lowercase_hex() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_sender_agent_id"):
        _create(sender_agent_id="A" * 96)
    with pytest.raises(ValueError, match="invalid_envelope_recipient_agent_id"):
        _create(recipient_agent_id="b" * 95)


def test_graph_context_anchor_if_present_is_canonical_non_empty_string() -> None:
    with pytest.raises(ValueError, match="invalid_envelope_graph_context_anchor"):
        _create(graph_context_anchor="")
    with pytest.raises(ValueError, match="invalid_envelope_graph_context_anchor"):
        _create(graph_context_anchor=" graph:root")


def test_validate_rejects_invalid_signature_field() -> None:
    env = AgentActionEnvelope(
        action_type=ActionType.ILC_TRANSFER,
        sender_agent_id=SENDER_AGENT_ID,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        amount_ilc=Decimal("1"),
        nonce="agent-a:2",
        epoch=0,
        cose_signature=b"",
    )
    with pytest.raises(ValueError, match="invalid_envelope_cose_signature"):
        validate_envelope(env)


def test_nonce_too_long_rejected() -> None:
    """Nonce exceeding MAX_NONCE_CHARS must be rejected before COSE payload construction."""
    with pytest.raises(ValueError, match="invalid_envelope_nonce_too_long"):
        _create(nonce="x" * (MAX_NONCE_CHARS + 1))


def test_nonce_at_max_length_accepted() -> None:
    validate_envelope(_create(nonce="a" * MAX_NONCE_CHARS))


def test_graph_context_anchor_too_long_rejected() -> None:
    """Anchor exceeding MAX_GRAPH_CONTEXT_ANCHOR_CHARS must be rejected before signing."""
    with pytest.raises(ValueError, match="invalid_envelope_graph_context_anchor_too_long"):
        _create(graph_context_anchor="g" * (MAX_GRAPH_CONTEXT_ANCHOR_CHARS + 1))


def test_graph_context_anchor_at_max_length_accepted() -> None:
    validate_envelope(_create(graph_context_anchor="g" * MAX_GRAPH_CONTEXT_ANCHOR_CHARS))


def test_amount_exceeding_u64_ceiling_rejected_for_non_genesis_agent() -> None:
    """The u64 micro-ILC ceiling must apply to all agents, not only Genesis.

    Without this check, an envelope with amount_ilc = 1e30 passes validate_envelope
    and enters the COSE signing path before any overflow guard fires.
    """
    _U64_MAX = 18_446_744_073_709_551_615
    micro_ilc_factor = 1_000_000
    # Smallest Decimal that exceeds u64 when scaled to micro-ILC.
    one_over = Decimal(_U64_MAX + 1) / Decimal(micro_ilc_factor)
    with pytest.raises(ValueError, match="amount_micro_ilc_exceeds_u64_max"):
        _create(amount_ilc=one_over)


def test_amount_at_u64_ceiling_accepted() -> None:
    _U64_MAX = 18_446_744_073_709_551_615
    micro_ilc_factor = 1_000_000
    at_cap = Decimal(_U64_MAX) / Decimal(micro_ilc_factor)
    validate_envelope(_create(amount_ilc=at_cap))


def test_ilc_transfer_enabled_is_true_after_rc08_gate() -> None:
    assert ILC_TRANSFER_ENABLED is True


def test_schema_module_has_no_signing_or_consensus_imports() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "ilc_consensus" not in source
    assert "cose_sign1" not in source
    assert "signing" not in source.lower()
