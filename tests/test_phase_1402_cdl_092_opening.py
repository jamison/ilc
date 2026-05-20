"""Regression tests for Phase 1402 CDL-092 CapProof opening."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OPENING_DOC = REPO_ROOT / "docs/specs/ilc_cdl_092_capproof_opening_1402_v0.1.md"
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
J005_DOC = REPO_ROOT / "docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md"
ADR_0038 = REPO_ROOT / "docs/adr/ADR_0038_Agent_Birth_Attestation.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_row(cdl_id: str) -> str:
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith(f"| {cdl_id} |"):
            return line
    raise AssertionError(f"{cdl_id} row not found")


def test_opening_doc_present_with_required_tokens() -> None:
    text = _read(OPENING_DOC)

    assert "cdl_092_capproof_opened_phase_1402" in text
    assert "cdl_092_not_ratified_phase_1402" in text
    assert "cdl_092_deliberation_questions_recorded_phase_1402" in text


def test_opening_doc_records_j005_and_adr0038_anchors() -> None:
    text = _read(OPENING_DOC)

    assert "capproof_no_direct_ilc_reward_boundary_confirmed" in text
    assert "awp_iih_depends_on_capproof_infrastructure_confirmed" in text
    assert "activation_ladder_shadow_to_production_defined_phase_j005" in text
    assert "adr_0038_agent_birth_attestation_genesis_rooted" in text


def test_j005_source_boundary_still_records_no_direct_ilc_reward() -> None:
    text = _read(J005_DOC)

    assert "capproof_no_direct_ilc_reward_boundary_confirmed" in text
    assert "It never directly affects" in text
    assert "ILC reward allocation" in text


def test_adr0038_source_anchor_present() -> None:
    text = _read(ADR_0038)

    assert "adr_0038_agent_birth_attestation_genesis_rooted" in text
    assert "signed Genesis/Atlas lineage anchor" in text


def test_opening_doc_records_all_deliberation_questions() -> None:
    text = _read(OPENING_DOC)

    for question_id in ("Q1", "Q2", "Q3", "Q4"):
        assert f"| {question_id} |" in text

    assert "content-address input" in text
    assert "Capability Vector signing chain" in text
    assert "+/-15% ECU pricing band application rule" in text
    assert "all ECU-earning work types" in text


def test_cdl_091_ratified_prerequisite() -> None:
    row = _cdl_row("CDL-091")

    assert "| ratified |" in row
    assert "ratification_token: cdl_091_ratified_phase_1400" in row


def test_cdl_092_register_row_open_after_c2() -> None:
    row = _cdl_row("CDL-092")

    assert "| open |" in row
    assert "opened_phase: 1402" in row
    assert "opening_token: cdl_092_capproof_opened_phase_1402" in row
    assert "historical_non_ratification_token: cdl_092_not_ratified_phase_1402" in row
    assert "deliberation_questions_token: cdl_092_deliberation_questions_recorded_phase_1402" in row
    assert "ratification_status: not_ratified_pending_phase_1405" in row


def test_cdl_092_not_prematurely_ratified() -> None:
    row = _cdl_row("CDL-092")

    assert "| ratified |" not in row
    assert "ratified_phase: 1405" not in row
    assert "capproof_pricing_activation_status: not_authorized" in row
