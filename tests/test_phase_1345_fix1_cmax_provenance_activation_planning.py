from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
FIX1_SPEC = ROOT / "docs/specs/ilc_phase_1345_fix1_cmax_provenance_activation_planning_v0.1.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
PHASE_1368_PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1368_g8_window_1343_1368_closure_handoff.md"
)


def test_cdl_register_records_cmax_without_stale_not_ratified_wording() -> None:
    text = CDL_REGISTER.read_text()

    assert "| CDL-025 |" in text
    assert "| fee-funded tail / Model B |" in text
    assert "fee-funded tail / Model B (planning recommendation" not in text

    assert "C_max = 25,920,000 ILC" in text
    assert "Platonic Year × 1,000" in text
    assert 'C_MAX_ILC = Decimal("25920000")' in text


def test_cdl_027_separates_issuance_epoch_from_validation_epoch() -> None:
    text = CDL_REGISTER.read_text()

    assert "discrete halving period H=48, monthly issuance epochs" in text
    assert "validation epoch duration remains a separate temporal architecture parameter" in text
    assert "1 minute validation epoch per CDL-027" not in text


def test_fix1_spec_records_provenance_and_non_authorization_floor() -> None:
    text = FIX1_SPEC.read_text()

    required_tokens = [
        "phase_1345_fix1_cmax_provenance_activation_planning.v0.1",
        "cmax_25920000_platonic_year_times_1000_confirmed_phase_1345_fix1",
        "cdl_025_current_candidate_stale_text_repaired_phase_1345_fix1",
        "cdl_026_cmax_numeric_binding_register_repaired_phase_1345_fix1",
        "cdl_027_schedule_register_repaired_phase_1345_fix1",
        "phase_1368_production_minting_activation_or_defer_prompt_hardened_phase_1345_fix1",
        "production_minting_activation_requires_phase_1366_soft_rc_true_and_phase_1367_clean_pass",
        "public_rc_remains_blocked_after_phase_1345_fix1",
    ]
    for token in required_tokens:
        assert token in text

    assert "25,920 years multiplied by 1,000" in text
    assert "This Fix1 does not authorize production minting" in text


def test_phase_1368_prompt_has_required_discovery_sections_and_activation_tokens() -> None:
    text = PHASE_1368_PROMPT.read_text()

    for heading in [
        "### §0a — Known-token audit",
        "### §0b — Concept-discovery search",
        "### §0c — Contradiction and non-claim search",
        "### §0d — Source expansion and newly discovered tokens",
    ]:
        assert heading in text

    assert "No ellipses in walkthrough." in text
    assert "production_minting_activated_phase_1368" in text
    assert "production_minting_activation_deferred_phase_1368" in text
    assert "phase_1366_blockers_addressed_or_clean_pass_phase_1367" in text
    assert "must implement the private soft-RC production minting gate" in text


def test_forward_plan_routes_activation_to_phase_1368() -> None:
    text = FORWARD_PLAN.read_text()

    assert "Phase 1345 Fix1 addendum" in text
    assert "Phase 1368 is the" in text
    assert "concrete production-minting activation-or-defer point" in text
    assert "production_minting_activated_phase_1368" in text
    assert "production_minting_activation_deferred_phase_1368" in text
    assert "Phase 1368 records production minting activation without both" in text
