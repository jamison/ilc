from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RATIFICATION = ROOT / "docs/specs/ilc_cdl_096_ratification_evidence_1553p_v0.1.md"
OPENING = ROOT / "docs/specs/ilc_cdl_096_opening_1551p_v0.1.md"
PRELOCK = ROOT / "docs/specs/ilc_cdl_096_prelock_1552p_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
AGENTS = ROOT / "AGENTS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1553p_cdl096_ratification_walkthrough.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cdl_row(number: str) -> str:
    register = read(CDL_REGISTER)
    return next(line for line in register.splitlines() if line.startswith(f"| {number} |"))


def test_ratification_artifact_records_option_a_tokens_and_scope() -> None:
    text = read(RATIFICATION)

    assert "cdl_096_ratified_phase_1553p" in text
    assert "cdl_096_scope_ratified_phase_1553p" in text
    assert "cdl_096_runtime_activation_not_authorized_phase_1553p" in text
    assert "public_path_remains_blocked_phase_1553p" in text
    assert "Option A - combined Werner flow-governor authority plus CDL-095 global-tier jury finality" in text
    assert "cdl_096_scope_selection_option_a_phase_1551p" in text
    assert "cdl_096_prelock_committed_phase_1552p" in text


def test_cdl096_register_row_is_ratified_and_prelock_status_replaced() -> None:
    row = cdl_row("CDL-096")

    assert "| ratified |" in row
    assert "opening_token: cdl_096_opened_phase_1551p" in row
    assert "scope_selection_token: cdl_096_scope_selection_option_a_phase_1551p" in row
    assert "prelock_status: cdl_096_prelock_committed_phase_1552p" in row
    assert "prelock_status: pending_phase_1552p" not in row
    assert "ratification_status: ratified_phase_1553p" in row
    assert "ratification_token: cdl_096_ratified_phase_1553p" in row
    assert "scope_token: cdl_096_scope_ratified_phase_1553p" in row
    assert "evidence_document: docs/specs/ilc_cdl_096_ratification_evidence_1553p_v0.1.md" in row


def test_cdl096_ratification_preserves_runtime_and_public_boundaries() -> None:
    row = cdl_row("CDL-096")
    text = read(RATIFICATION)

    for token in (
        "werner_flow_governor_runtime_status: not_authorized",
        "werner_value_path_status: not_ecu_not_ilc_not_claimability",
        "global_tier_activation_status: not_authorized",
        "rust_p2p_bridge_status: RUST_P2P_BRIDGE_NOT_ACTIVATED=True",
        "jury_finality_evaluator_status: JURY_FINALITY_EVALUATOR_NOT_PRODUCTION=True",
        "runtime_activation_status: not_authorized",
        "public_path_status: blocked",
    ):
        assert token in row

    assert "RUST_P2P_BRIDGE_NOT_ACTIVATED = True" in text
    assert "JURY_FINALITY_EVALUATOR_NOT_PRODUCTION = True" in text
    assert "No runtime module was activated" in read(WALKTHROUGH)


def test_cdl095_not_amended_and_cdl098_unconsumed() -> None:
    cdl095 = cdl_row("CDL-095")
    cdl096 = cdl_row("CDL-096")

    assert "global_tier_activation_status: deferred_to_cdl_096" in cdl095
    assert "cdl_095_amendment_status: not_required_for_option_a" in cdl096
    assert "cdl_098_status: unconsumed" in cdl096
    assert "CDL-095 is not amended" in read(RATIFICATION)


def test_ratification_evidence_preserves_werner_and_global_tier_constants() -> None:
    text = read(RATIFICATION)

    for token in (
        'topology_pressure_model = "werner_v1"',
        "Tier B topology pressure only",
        "smoothed pressure greater than or equal to `100`",
        "`K = 2`, `N = 3`, `beta_floor = 0.5`, `pulse_floor = 0.5`",
        "dimensionless flow-control priority, not ECU or ILC",
        "Directed edge observations | 12",
        "Success rate | `1.000000`",
        "Tier B smoothed pressure sequence | `479.875000`, `739.312500`, `848.656250`",
        "Panel size | 21 reviewers",
        "Participation floor | 15 of 21 reviewers",
        "Compensation basis | `3 * CDL-091 base review fee`",
    ):
        assert token in text


def test_frontier_docs_advance_to_phase_1554_without_public_activation() -> None:
    combined = "\n".join(
        read(path)
        for path in (SEQUENCE_LOCK, PLANNING_INDEX, STATUS, AGENTS, WALKTHROUGH, OPENING, PRELOCK)
    )

    assert "cdl_096_ratified_phase_1553p" in combined
    assert "cdl_096_scope_ratified_phase_1553p" in combined
    assert "cdl_096_runtime_activation_not_authorized_phase_1553p" in combined
    assert "public_path_remains_blocked_phase_1553p" in combined
    assert "next_phase: phase_1554p_block5_coherence_capsule" in combined
    assert "Phase 1554p is next and NON-SENSITIVE" in combined
    assert "no_cdl_096_runtime_activation" in read(AGENTS)
    assert "no_cdl_096_open" not in read(AGENTS)
