from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PHASE_1387A_PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1387a_g8_accepted_adr_cdl_coverage_public_economics_firewall.md"
)
PHASE_1388_PROMPT = (
    ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1388_g8_cdl_048_activation_counsel_clearance.md"
)
PHASE_1389_PROMPT = (
    ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1389_g8_public_claimability_activation_gate.md"
)
WINDOW_PLAN = ROOT / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)


REQUIRED_1387A_TOKENS = (
    "accepted_adr_cdl_runtime_coverage_matrix_phase_1387a",
    "public_economics_requires_public_node_admission_verified_phase_1387a",
    "private_visibility_excluded_from_public_economics_phase_1387a",
    "no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1387a_prompt_is_schema_valid_and_carries_gap_closure_tokens() -> None:
    assert validate(PHASE_1387A_PROMPT) == []
    prompt = read(PHASE_1387A_PROMPT)

    for token in REQUIRED_1387A_TOKENS:
        assert token in prompt

    assert "public ECU" in prompt
    assert "public reputation" in prompt
    assert "public settlement" in prompt
    assert "public claimability" in prompt
    assert "private or semi-private" in prompt
    assert "operator-local advisory scoring only" in prompt
    assert "not protocol ECU" in prompt
    assert "private or semi-private ECU generation" in prompt
    assert "gap_blocks_public_rc" in prompt


def test_window_plans_route_public_only_economics_gap_to_phase_1387a() -> None:
    for plan_path in (WINDOW_PLAN, FORWARD_PLAN):
        plan = read(plan_path)
        assert "1387a" in plan
        assert "Accepted ADR/CDL coverage" in plan
        assert "public-economics admission firewall" in plan
        assert "operator-local advisory scoring" in plan
        assert "public_economics_requires_public_node_admission_verified_phase_1387a" in plan
        assert "no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a" in plan


def test_activation_and_public_claimability_gates_fail_closed_without_1387a() -> None:
    phase_1388 = read(PHASE_1388_PROMPT)
    phase_1389 = read(PHASE_1389_PROMPT)

    for token in REQUIRED_1387A_TOKENS:
        assert token in phase_1388
        assert token in phase_1389

    assert "Phase 1387a PASS must be confirmed before executing" in phase_1388
    assert "Phase 1387a did not prove accepted ADR/CDL coverage" in phase_1389
    assert "result=public_claimability_activated" in phase_1389


def test_1387a_and_1388_separate_prerequisites_from_output_tokens() -> None:
    phase_1387a = read(PHASE_1387A_PROMPT)
    phase_1388 = read(PHASE_1388_PROMPT)

    assert "Output tokens that must not already exist before this phase executes" in phase_1387a
    assert "Output tokens that must not already exist before this phase executes" in phase_1388

    phase_1387a_prerequisites = phase_1387a.split(
        "Output tokens that must not already exist before this phase executes", 1
    )[0]
    for token in REQUIRED_1387A_TOKENS:
        assert token not in phase_1387a_prerequisites

    phase_1388_prerequisites = phase_1388.split(
        "Output tokens that must not already exist before this phase executes", 1
    )[0]
    assert "cdl_048_activated_phase_1388" not in phase_1388_prerequisites
    assert "counsel_clearance_public_verifier_api_phase_1388" not in phase_1388_prerequisites
    assert "first_live_value_path_activation_phase_1388" not in phase_1388_prerequisites
