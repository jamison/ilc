from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRELOCK = ROOT / "docs/specs/ilc_cdl_097_type_definition_node_authority_prelock_1527p_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
OBL_REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1523p_1530p_sequence_lock_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
AGENTS = ROOT / "AGENTS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1527p_adr0035_cdl_deliberation_prelock_walkthrough.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_prelock_records_all_output_tokens_and_non_ratification_boundary() -> None:
    text = read(PRELOCK)

    assert "cdl_097_prelock_committed_phase_1527p" in text
    assert "cdl_097_scope_constants_locked_phase_1527p" in text
    assert "public_path_still_blocked_phase_1527p" in text
    assert "CDL-097 is not ratified by this phase. Ratification requires exact `GO Phase 1528p`." in text
    assert "No CDL register mutation" not in text  # The doc phrases this as CDL register mutation in the non-authorization floor.
    assert "CDL register mutation" in text


def test_prelock_locks_all_scope_constants() -> None:
    text = read(PRELOCK)

    for constant in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"):
        assert constant in text

    assert 'Route (a) is locked: `content_type="type_definition"`' in text
    assert "Phase 1525p definition-node candidate record shape is adopted" in text
    assert "Phase 1525p stable verifier error-token table is adopted" in text
    assert "`attribution_policy: non_attributable` is locked as a hard rule" in text
    assert "Phase 1528p ratifies schema authority only" in text
    assert "Type-level dispute procedure is deferred to a later CDL annex" in text
    assert "parse support only and is not authority-bearing while the guard remains set" in text


def test_cdl_register_preserves_prelock_boundary_after_later_ratification() -> None:
    cdl = read(CDL_REGISTER)

    assert "| CDL-097 |" in cdl
    assert "cdl_097_type_definition_node_authority_opened_phase_1526p" in cdl
    if "ratification_token: cdl_097_ratified_phase_1528p" in cdl:
        assert "prelock_token: cdl_097_prelock_committed_phase_1527p" in cdl
        assert "scope_token: cdl_097_scope_constants_locked_phase_1527p" in cdl
        assert "| ratified |" in cdl
    else:
        assert "| open |" in cdl
        assert "cdl_097_prelock_committed_phase_1527p" not in cdl
        assert "cdl_097_scope_constants_locked_phase_1527p" not in cdl


def test_frontier_documents_record_phase_1527p_and_obl025_open() -> None:
    obl = read(OBL_REGISTER)
    sequence = read(SEQUENCE_LOCK)
    planning = read(PLANNING_INDEX)
    status = read(STATUS)
    agents = read(AGENTS)
    walkthrough = read(WALKTHROUGH)

    for text in (obl, sequence, planning, status, agents, walkthrough):
        assert "cdl_097_prelock_committed_phase_1527p" in text
        assert "cdl_097_scope_constants_locked_phase_1527p" in text
        assert "public_path_still_blocked_phase_1527p" in text

    assert "| 1527p | CDL deliberation and prelock | NON-SENSITIVE | COMPLETE |" in sequence
    assert "Phase 1527p" in status
    assert "OBL-025 remains open" in status
    assert "Phase 1528p remains SENSITIVE" in status or "Phase 1528p - ADR-0035 CDL-097 Ratification" in status
    assert "phase_1527p: complete_cdl097_deliberation_prelock" in agents
    assert (
        "Phase 1528p is the next phase and is SENSITIVE" in planning
        or "Phase 1529p is the next phase and is NON-SENSITIVE" in planning
        or "Phase 1530p is next and requires exact `GO Phase 1530p`" in planning
    )
    assert "⬅ CURRENT" in planning


def test_walkthrough_contains_required_phase_controls() -> None:
    text = read(WALKTHROUGH)

    assert "Claim Verification" in text
    assert "Discovery Summary" in text
    assert "Scope Constant Resolution" in text
    assert "No CDL register mutation" in text
    assert "graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_097_type_definition_node_authority_prelock_1527p_v0.1.md -> governance/cdl-097-prelock" in text
