from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs/specs/ilc_window_1399_1428_handoff_1428_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1428_window_closure_gate_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1399_1428_sequence_lock_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1428_g8_window_closure_gate.md"
GATE_SOURCE = ROOT / "ilc_core/epistemic/jury_activation_gate.py"
SOFT_RC = ROOT / "docs/specs/ilc_soft_rc_gate_rerun_1426_v0.1.md"
J008_PASS = ROOT / "docs/specs/ilc_production_jury_activation_gate_pass_1427_v0.1.md"


REQUIRED_TOKENS = (
    "window_1399_1428_closed_phase_1428",
    "window_1399_1428_closure_verdict_recorded_phase_1428",
    "window_1429_not_open_phase_1428",
    "go_window_1429_required_next",
    "mempalace_refresh_disposition_recorded_phase_1428",
)

PRE_CLOSURE_WALKTHROUGHS = (
    "phase_1399_cdl_091_jury_incentive_economics_prelock_walkthrough.md",
    "phase_1400_cdl_091_jury_incentive_economics_ratification_walkthrough.md",
    "phase_1401_cdl_091_jury_incentive_runtime_stub_walkthrough.md",
    "phase_1402_cdl_092_capproof_opening_walkthrough.md",
    "phase_1403_cdl_092_capproof_deliberation_walkthrough.md",
    "phase_1404_cdl_092_capproof_prelock_walkthrough.md",
    "phase_1405_cdl_092_capproof_ratification_walkthrough.md",
    "phase_1406_cdl_093_maintenance_lottery_pool_opening_walkthrough.md",
    "phase_1407_cdl_093_maintenance_lottery_pool_deliberation_prelock_walkthrough.md",
    "phase_1408_cdl_093_maintenance_lottery_pool_ratification_walkthrough.md",
    "phase_1409_cdl_093_maintenance_lottery_runtime_stub_walkthrough.md",
    "phase_1410_vrf_proof_verifier_adr_walkthrough.md",
    "phase_1411_vrf_proof_verifier_implementation_walkthrough.md",
    "phase_1412_vrf_jury_assignment_integration_walkthrough.md",
    "phase_1413_vrf_integration_tests_security_review_walkthrough.md",
    "phase_1414_review_lane_wiring_adr_walkthrough.md",
    "phase_1415_review_lane_admission_runtime_walkthrough.md",
    "phase_1416_review_lane_dedup_payment_stub_walkthrough.md",
    "phase_1417_review_lane_integration_tests_walkthrough.md",
    "phase_1418_anti_capture_diversity_design_walkthrough.md",
    "phase_1419_anti_capture_diversity_verification_walkthrough.md",
    "phase_1420_copyright_counsel_disposition_walkthrough.md",
    "phase_1421_window_coherence_and_capsule_walkthrough.md",
    "phase_1422_launch_readiness_manifest_schema_walkthrough.md",
    "phase_1423_private_soft_rc_rehearsal_criteria_walkthrough.md",
    "phase_1424_public_rc_activation_certificate_design_walkthrough.md",
    "phase_1425_pre_gate_verification_walkthrough.md",
    "phase_1426_soft_rc_gate_rerun_walkthrough.md",
    "phase_1427_j008_gate_rerun_walkthrough.md",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1428_handoff_schema_sections_are_ordered() -> None:
    text = _read(HANDOFF)
    headings = [
        "## 1. Window identity and closure basis",
        "## 2. Inputs and closure inheritance",
        "## 3. Closure verdict summary",
        "## 4. Carry-forward items and residual blockers",
        "## 5. Next-window entry criteria and routing",
        "## 6. MemPalace refresh disposition",
    ]

    positions = [text.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_phase_1428_required_tokens_are_recorded_on_closure_surfaces() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS, INDEX, SEQUENCE_LOCK):
        text = _read(path)
        for token in REQUIRED_TOKENS:
            assert token in text, f"{path} missing {token}"


def test_phase_1428_pre_closure_walkthrough_inventory_is_complete() -> None:
    assert len(PRE_CLOSURE_WALKTHROUGHS) == 29
    for name in PRE_CLOSURE_WALKTHROUGHS:
        assert (ROOT / "docs/phases" / name).exists(), name

    text = _read(HANDOFF)
    assert "| 1428 | Window closure gate | complete by this artifact |" in text
    assert "docs/phases/phase_1428_window_closure_gate_walkthrough.md" in text


def test_phase_1428_records_gate_and_soft_rc_inputs() -> None:
    handoff = _read(HANDOFF)
    gate = _read(GATE_SOURCE)
    soft_rc = _read(SOFT_RC)
    j008 = _read(J008_PASS)

    assert "soft_rc_eligible=true_phase_1426" in soft_rc
    assert "production_jury_activation_gate_pass_phase_1427" in j008
    assert "all_10_conditions_met_phase_1427" in j008
    assert "PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED: bool = False" in gate
    assert "window_1399_1428_closure_verdict=closed_pass_with_carry_forward" in handoff


def test_phase_1428_handoff_records_mem_palace_refresh_required() -> None:
    text = _read(HANDOFF)

    assert "Disposition:` `required" in text
    assert "Active working set impacted:` `yes" in text
    assert "bash tools/mempalace/build_active_working_set.sh" in text
    assert "MemPalace remains advisory retrieval only." in text


def test_phase_1428_preserves_window_1429_boundary() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS, INDEX, SEQUENCE_LOCK):
        text = _read(path)
        assert "window_1429_not_open_phase_1428" in text
        assert "go_window_1429_required_next" in text

    handoff = _read(HANDOFF)
    assert "The Window 1429-1458 draft is an active sequence lock" in handoff
    assert "It is a draft forward plan only." in handoff
    assert "Requires explicit human `GO Window 1429`" in handoff


def test_phase_1428_prompt_hardened_to_30_locked_entries() -> None:
    prompt = _read(PROMPT)

    assert "30 locked phase-table" in prompt
    assert "29 pre-closure phases" in prompt
    assert "all_28_phases" not in prompt


def test_phase_1428_non_authorizations_are_explicit() -> None:
    text = _read(HANDOFF)

    for phrase in (
        "It does not open Window 1429",
        "Public RC is published",
        "The activation certificate is signed",
        "Epoch 0->1 has occurred",
        "Public serving is live",
    ):
        assert phrase in text


def test_phase_1428_walkthrough_has_no_ellipses() -> None:
    text = _read(WALKTHROUGH)

    assert "..." not in text
    assert "\u2026" not in text
