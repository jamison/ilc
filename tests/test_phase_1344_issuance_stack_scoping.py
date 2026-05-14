from __future__ import annotations

from pathlib import Path


SPEC = Path("docs/specs/ilc_issuance_stack_scoping_window_1343_1368_v0.1.md")
PROMPT = Path("docs/antigravity_tasks/antigravity_prompt__phase_1344_g8_issuance_stack_scoping.md")
FORWARD_PLAN = Path("docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md")
STATUS = Path("docs/phases/STATUS.md")
INDEX = Path("docs/PLANNING_INDEX.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1344_scoping_tokens_and_non_authorization_are_recorded() -> None:
    text = _read(SPEC)
    for token in (
        "issuance_stack_scoping_phase_1344.v0.1",
        "cdl_053_vehicle_collision_resolved_or_rerouted_phase_1344",
        "cdl_025_model_b_ratification_evidence_bound_phase_1344",
        "cdl_026_cmax_25920000_bound_phase_1344",
        "cdl_027_halving_h48_monthly_bound_phase_1344",
        "phase_1345_emission_engine_next",
        "issuance_stack_no_implementation_phase_1344",
        "production_minting_not_authorized_phase_1344",
        "public_rc_remains_blocked_after_phase_1344",
    ):
        assert token in text
    assert "does not authorize production issuance implementation" in text
    assert "does not authorize production minting" in text


def test_phase_1344_maps_all_required_cdl_surfaces() -> None:
    text = _read(SPEC)
    for cdl in (
        "CDL-025",
        "CDL-026",
        "CDL-027",
        "CDL-028",
        "CDL-029",
        "CDL-030",
        "CDL-031",
        "CDL-047",
        "CDL-054",
        "CDL-083",
    ):
        assert cdl in text
    assert "New `ilc_core/epoch/epoch_emission_runtime.py` quote engine" in text
    assert "1352 is the first integration gate" in text


def test_phase_1344_records_cdl_053_reroute_and_phase_1366_standard() -> None:
    text = _read(SPEC)
    assert "blocking_authority_vehicle_must_not_be_cdl_053_phase_1344" in text
    assert "blocking_authority_vehicle_selection_deferred_to_phase_1362_phase_1344" in text
    assert "Phase 1366 may record `soft_rc_eligible=true` only if all of these are true" in text
    assert "block rather than emit" in text


def test_prompt_and_frontier_docs_reflect_phase_1344_completion() -> None:
    assert "issuance_stack_scoping_phase_1344.v0.1" in _read(PROMPT)
    forward = _read(FORWARD_PLAN)
    assert "blocking_authority_vehicle_must_not_be_cdl_053_phase_1344" in forward
    assert "phase_1345_emission_engine_next" in forward
    status = _read(STATUS)
    index = _read(INDEX)
    assert "## Phase 1344" in status
    assert "phase_1345_emission_engine_next" in status
    assert "Phase 1345 - CDL-025/026/027 epoch emission runtime" in status
    assert "Phase 1344 issuance stack scoping" in index
