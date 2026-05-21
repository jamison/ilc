"""Phase 1423 private soft-RC rehearsal criteria tests."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md"


def _spec_text() -> str:
    assert SPEC.exists()
    return SPEC.read_text(encoding="utf-8")


def test_required_phase_tokens_present() -> None:
    text = _spec_text()

    for token in (
        "private_soft_rc_rehearsal_entry_criteria_defined_phase_1423",
        "three_machine_seven_agent_topology_spec_defined_phase_1423",
        "rehearsal_not_activated_phase_1423",
        "no_live_llm_calls_in_rehearsal_spec_phase_1423",
    ):
        assert token in text


def test_six_required_sections_present() -> None:
    text = _spec_text()

    for heading in (
        "## 1. Entry Criteria",
        "## 2. Topology",
        "## 3. Agent Identity Initialization",
        "## 4. Test Dataset Selection",
        "## 5. Wipe And Reset Rights",
        "## 6. Scripted-Agent Behavioral Specification",
    ):
        assert heading in text


def test_three_machine_seven_agent_topology_is_explicit() -> None:
    text = _spec_text()

    for role in (
        "M1",
        "M2",
        "M3",
        "Genesis agent",
        "Reviewer-1",
        "Reviewer-2",
        "Validator-A1",
        "Validator-A2",
        "Validator-B1",
        "Validator-B2",
    ):
        assert role in text


def test_identity_init_constraints_reference_adr_and_cdl_boundaries() -> None:
    text = _spec_text()

    assert "ADR-0038 birth attestation semantics are required" in text
    assert "ADR-0041 permissionless INIT semantics are required" in text
    assert "CDL-042 flat namespace law" in text
    assert "No secret seed" in text
    assert "stdout" in text


def test_dataset_and_no_copyrighted_verbatim_constraints() -> None:
    text = _spec_text()

    assert "at least 10 knowledge nodes" in text
    assert "at least 3 taxonomy classes" in text
    assert "at most 5 theorems" in text
    assert "No copyrighted verbatim content" in text


def test_no_live_llm_or_activation_authorized() -> None:
    text = _spec_text()

    assert "No live LLM calls" in text
    assert "No external model API calls" in text
    assert "No economic settlement" in text
    assert "No production ECU distribution" in text
    assert "does not provision VPS machines" in text
    assert "patch `jury_activation_gate.py`" in text
