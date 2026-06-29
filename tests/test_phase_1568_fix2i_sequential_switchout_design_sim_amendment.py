from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMENDMENT = ROOT / "docs/adr/ADR_0040_amendment_01_sequential_switchout_v0.1.md"
SIM = ROOT / "docs/specs/ilc_phase_1568_fix2i_sequential_switchout_sim_v0.1.md"
ADM_ADDENDUM = (
    ROOT / "docs/specs/ilc_adm_003_sequential_switchout_addendum_1568_fix2i_v0.1.md"
)
JURY_RUNTIME = ROOT / "ilc_core/epistemic/jury_assignment_runtime.py"
STATUS = ROOT / "docs/phases/STATUS.md"


def test_amendment_exists_and_is_draft_not_ratified():
    text = AMENDMENT.read_text()
    assert "DRAFT" in text
    assert "not ratified" in text.lower()
    assert "requires human GO and CDL authority before implementation" in text


def test_five_prompt_questions_resolved():
    text = AMENDMENT.read_text()
    for heading in [
        "Switch-Out Non-Response",
        "Switch-Out Time Window",
        "Switch-Out Pool Source",
        "Random Slot Removal Seed",
        "Economic Treatment",
    ]:
        assert heading in text
    assert "No open design question from the Fix2i prompt remains unresolved" in text
    assert "minimum lane-specific eligible-pool size or sparse-pool merge rule" in text


def test_economic_treatment_is_explicitly_deferred():
    text = AMENDMENT.read_text()
    assert "discarded_reviewer_economic_treatment: requires_cdl_authority" in text
    assert "switchout_accuracy_bonus_treatment: requires_cdl_authority" in text
    assert "switchout_base_fee_treatment: requires_cdl_authority" in text
    assert "does not define reviewer payment" in text


def test_runtime_substrate_boundary_is_non_authorized():
    text = AMENDMENT.read_text()
    assert "same_cxl_pool_operator_not_independent_for_substrate_purposes" in text
    assert "substrate_custody_settlement_effect_requires_cdl_authority" in text
    assert "not active runtime checks" in text


def test_adm_addendum_keeps_additive_model_canonical_until_ratified():
    text = ADM_ADDENDUM.read_text()
    assert "not canonical ADM replacement" in text
    assert "does not modify ADM-003 constants" in text
    assert "The additive ADM-003 model remains canon" in text
    assert "does not" in text
    assert "authorize ECU or ILC settlement" in text


def test_sim_records_fix2j_post_rc_label():
    text = SIM.read_text()
    assert "Chosen label: `fix2j_post_rc`" in text
    assert "activation matrix template does not require blind-jury" in text


def test_production_assignment_guard_is_phase_1429_authorized_state():
    runtime_text = JURY_RUNTIME.read_text()
    status_text = STATUS.read_text()
    assert "production_assignment_activated_phase_1429" in runtime_text
    assert "PRODUCTION_ASSIGNMENT_NOT_ACTIVATED: bool = False" in runtime_text
    assert "production_assignment_activated_phase_1429" in status_text
    assert "production_assignment_not_activated_flag_flipped_phase_1429" in status_text
    assert "public_rc_not_activated_phase_1429" in status_text
