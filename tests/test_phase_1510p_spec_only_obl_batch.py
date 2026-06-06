from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1510p_g9_spec_only_obl_batch.md"
SHARD_SPEC = ROOT / "docs/specs/ilc_shard_tier_panel_selection_spec_1510p_v0.1.md"
SECTOR_SPEC = ROOT / "docs/specs/ilc_sector_ab_economy_distinction_spec_1510p_v0.1.md"
STATUS_SPEC = ROOT / "docs/specs/ilc_status_formula_semantics_1510p_v0.1.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1510p_spec_only_obl_batch_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"

TOKENS = [
    "obl_008_shard_tier_panel_selection_spec_committed_phase_1510p",
    "obl_011_sector_ab_economy_distinction_spec_committed_phase_1510p",
    "obl_016_status_formula_semantics_clarified_phase_1510p",
    "no_shard_tier_activation_phase_1510p",
    "no_sector_b_payout_activation_phase_1510p",
    "no_status_runtime_change_phase_1510p",
]


def _row_for(obligation_id: str) -> str:
    for line in REGISTER.read_text().splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def test_phase_1510p_specs_record_required_tokens_and_boundaries() -> None:
    texts = {
        "prompt": PROMPT.read_text(),
        "shard": SHARD_SPEC.read_text(),
        "sector": SECTOR_SPEC.read_text(),
        "status": STATUS_SPEC.read_text(),
        "register": REGISTER.read_text(),
        "sequence_lock": SEQUENCE_LOCK.read_text(),
        "walkthrough": WALKTHROUGH.read_text(),
        "status_log": STATUS.read_text(),
        "planning_index": PLANNING_INDEX.read_text(),
        "agents": AGENTS.read_text(),
    }

    for token in TOKENS:
        assert any(token in text for text in texts.values()), token
        assert token in texts["register"], token
        assert token in texts["walkthrough"], token
        assert token in texts["status_log"], token

    assert "Phase 1511p" in texts["status_log"]
    assert texts["planning_index"].count("⬅ CURRENT") == 1


def test_shard_tier_spec_preserves_cdl095_non_activation_boundary() -> None:
    text = SHARD_SPEC.read_text()
    assert "JURY_SHARD_INTERIM_FALLBACK_SELECTION_STATUS = \"deferred_to_shard_activation_gate\"" in text
    assert "largest cluster slots must be less than or equal to 4" in text
    assert "no_shard_tier_activation_phase_1510p" in text
    assert "does not re-open CDL-095" in text
    assert "does not assign new CDL-096 global-tier constants" in text


def test_sector_ab_spec_keeps_subjective_market_out_of_objective_issuance() -> None:
    text = SECTOR_SPEC.read_text()
    assert "Sector A" in text
    assert "Sector B" in text
    assert "unknown_or_mixed_without_refutation_surface -> Sector B / no Sector A issuance" in text
    assert "ADR-0023 remains an accepted scoped architecture, not a live Sector B payout authorization" in text
    assert "no_sector_b_payout_activation_phase_1510p" in text


def test_status_formula_spec_is_semantic_not_runtime_authority() -> None:
    text = STATUS_SPEC.read_text()
    assert "status_signal = bounded_deployment_velocity_factor * bounded_quality_factor" in text
    assert "A weighted sum is rejected as the default interpretation" in text
    assert "not raw spend velocity and not wall-clock speed" in text
    assert "Phase 1510p does not add deployment velocity" in text
    assert "no_status_runtime_change_phase_1510p" in text


def test_register_closes_only_phase_1510p_obligations_and_cdl_register_unchanged() -> None:
    for obligation_id in ("OBL-008", "OBL-011", "OBL-016"):
        row = _row_for(obligation_id)
        assert "| closed |" in row
        assert "1510p" in row

    for obligation_id in ("OBL-012", "OBL-015", "OBL-017", "OBL-018", "OBL-019"):
        assert "| open |" in _row_for(obligation_id)

    cdl_register = CDL_REGISTER.read_text()
    assert "| CDL-095 |" in cdl_register
    assert "| CDL-096 |" not in cdl_register
    assert "obl_008_shard_tier_panel_selection_spec_committed_phase_1510p" not in cdl_register
