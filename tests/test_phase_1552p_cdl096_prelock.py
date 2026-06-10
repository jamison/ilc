from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRELOCK = ROOT / "docs/specs/ilc_cdl_096_prelock_1552p_v0.1.md"
OPENING = ROOT / "docs/specs/ilc_cdl_096_opening_1551p_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
AGENTS = ROOT / "AGENTS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1552p_cdl096_prelock_walkthrough.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_prelock_records_required_tokens_and_non_ratification_boundary() -> None:
    text = read(PRELOCK)

    assert "cdl_096_prelock_committed_phase_1552p" in text
    assert "cdl_096_scope_constants_locked_phase_1552p" in text
    assert "cdl_096_runtime_activation_not_authorized_phase_1552p" in text
    assert "public_path_remains_blocked_phase_1552p" in text
    assert "CDL-096 is not ratified by this phase" in text
    assert "Ratification requires exact `GO Phase 1553p`" in text
    assert "CDL register mutation" in text


def test_prelock_locks_werner_constants_from_live_capture_and_sim_fetch() -> None:
    text = read(PRELOCK)

    for token in (
        "topology_pressure_model = \"werner_v1\"",
        "Tier B topology pressure only",
        "K = 2",
        "N = 3",
        "beta_floor = 0.5",
        "pulse_floor = 0.5",
        "RUST_P2P_BRIDGE_NOT_ACTIVATED = True",
    ):
        assert token in text

    assert "Directed edge observations | 12" in text
    assert "Success rate | `1.000000`" in text
    assert "Routed effective Tier A+B failure rate | `0.000000`" in text
    assert "Routed holder hit rate | `1.000000`" in text
    assert "Tier B smoothed pressure sequence | `479.875000`, `739.312500`, `848.656250`" in text
    assert "The output is dimensionless flow-control priority, not ECU or ILC" in text


def test_prelock_locks_global_tier_constants_without_activation() -> None:
    text = read(PRELOCK)

    assert "Global-tier review is limited to cross-shard disputes" in text
    assert "panel size is 21 reviewers" in text
    assert "15 of 21 reviewers" in text
    assert "Approval threshold remains exact 2/3 integer arithmetic" in text
    assert "3 * CDL-091 base review fee" in text
    assert "JURY_FINALITY_EVALUATOR_NOT_PRODUCTION = True" in text
    assert "GLOBAL_TIER_JURY_NOT_ACTIVATED = True" in text
    assert "Production selection is deferred" in text


def test_cdl_register_remains_open_and_unmutated_by_prelock() -> None:
    cdl = read(CDL_REGISTER)
    cdl096_row = next(line for line in cdl.splitlines() if line.startswith("| CDL-096 |"))

    assert "| open |" in cdl096_row
    assert "opening_token: cdl_096_opened_phase_1551p" in cdl096_row
    assert "prelock_status: pending_phase_1552p" in cdl096_row
    assert "ratification_status: not_ratified" in cdl096_row
    assert "cdl_096_prelock_committed_phase_1552p" not in cdl096_row
    assert "cdl_096_scope_constants_locked_phase_1552p" not in cdl096_row


def test_frontier_docs_advance_to_sensitive_phase_1553() -> None:
    combined = "\n".join(
        read(path)
        for path in (SEQUENCE_LOCK, PLANNING_INDEX, STATUS, AGENTS, WALKTHROUGH, OPENING)
    )

    assert "cdl_096_opened_phase_1551p" in combined
    assert "cdl_096_prelock_committed_phase_1552p" in combined
    assert "cdl_096_scope_constants_locked_phase_1552p" in combined
    assert "cdl_096_runtime_activation_not_authorized_phase_1552p" in combined
    assert "public_path_remains_blocked_phase_1552p" in combined
    assert "next_phase: phase_1553p_sensitive_cdl096_ratification" in combined
    assert "Phase 1553p is the next phase and is SENSITIVE" in combined
    assert "CDL-096 is open and prelocked but not ratified" in combined
