# SPDX-License-Identifier: AGPL-3.0-only
"""Artifact and runtime-boundary tests for GAP-HARNESS-SIDECAR-03."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.value_action.ilc_transfer_intent import (
    ActionType,
    AgentActionEnvelope,
    ILCTransferIntent,
    validate_envelope,
)


ROOT = Path(__file__).resolve().parents[1]
CDL = ROOT / "docs/cdl/cdl_111_generalized_agent_action_envelope_v0.1.md"
SPEC = (
    ROOT
    / "docs/specs/ilc_generalized_agent_action_envelope_spec_GAP_HARNESS_SIDECAR_03_v0.1.md"
)
DECISION_LOG = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"

AGENT_A = "a" * 96
AGENT_B = "b" * 96


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cdl_111_opening_document_exists_with_required_sections() -> None:
    text = _read(CDL)
    for heading in (
        "## Scope",
        "## Current State",
        "## Governance Framework",
        "## Dispatch Semantics",
        "## Ordered Next-Action-Type Queue",
        "## Non-Claims",
    ):
        assert heading in text
    assert "Status: opened" in text


def test_cdl_111_non_claims_are_explicitly_non_activating() -> None:
    text = _read(CDL)
    for required in (
        "does NOT activate any new `AgentActionEnvelope` action type",
        "Ratify CDL-111",
        "Modify `ilc_core/value_action/ilc_transfer_intent.py`",
        "Add `ECU_TRANSFER`, `GRAPH_SUBMIT`, `ATTRIBUTION_BATCH`, or",
        "Authorize public graph mutation",
        "Authorize generalized ECU money transfer",
        "Authorize external withdrawal",
        "Authorize public RC",
    ):
        assert required in text


def test_companion_spec_defines_dispatch_and_guard_contract() -> None:
    text = _read(SPEC)
    assert 'ValueError("unknown_envelope_action_type:<type>")' in text
    for guard in (
        "GRAPH_SUBMIT_ENVELOPE_DISPATCH_NOT_ACTIVATED",
        "ECU_TRANSFER_ENVELOPE_DISPATCH_NOT_ACTIVATED",
        "ATTRIBUTION_BATCH_ENVELOPE_DISPATCH_NOT_ACTIVATED",
        "TASK_COMMISSION_ENVELOPE_DISPATCH_NOT_ACTIVATED",
    ):
        assert guard in text
    assert "sort_keys=True" in text
    assert "allow_nan=False" in text
    assert "no floats for economic values" in text


def test_current_runtime_action_type_remains_ilc_transfer_only() -> None:
    assert [item.value for item in ActionType] == ["ILC_TRANSFER"]
    assert not hasattr(ActionType, "ECU_TRANSFER")
    assert not hasattr(ActionType, "GRAPH_SUBMIT")


def test_current_runtime_rejects_unknown_action_without_side_effects() -> None:
    env = AgentActionEnvelope(
        action_type="GRAPH_SUBMIT",  # type: ignore[arg-type]
        sender_agent_id=AGENT_A,
        recipient_agent_id=AGENT_B,
        amount_ilc=Decimal("1"),
        nonce="nonce-1",
        epoch=0,
    )
    with pytest.raises(ValueError, match="invalid_envelope_action_type"):
        validate_envelope(env)


def test_current_ilc_transfer_factory_still_produces_valid_envelope() -> None:
    env = ILCTransferIntent.create(
        sender_agent_id=AGENT_A,
        recipient_agent_id=AGENT_B,
        amount_ilc=Decimal("1.000001"),
        nonce="nonce-2",
        epoch=1,
        graph_context_anchor="graph-context-1",
    )
    validate_envelope(env)
    assert env.action_type is ActionType.ILC_TRANSFER


def test_decision_log_records_cdl_111_as_open_not_ratified() -> None:
    text = _read(DECISION_LOG)
    assert "| CDL-110 |" in text
    assert "| CDL-111 |" in text
    cdl_111_line = next(line for line in text.splitlines() if line.startswith("| CDL-111 |"))
    assert "| opened |" in cdl_111_line
    assert "generalized_agent_action_envelope_cdl_opened_GAP_HARNESS_SIDECAR_03" in cdl_111_line
    assert "| ratified |" not in cdl_111_line


def test_status_token_is_recorded() -> None:
    assert (
        "generalized_agent_action_envelope_cdl_opened_GAP_HARNESS_SIDECAR_03"
        in _read(STATUS)
    )
