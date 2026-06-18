from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHERENCE = ROOT / "docs/specs/ilc_window_1546p_coherence_1554p_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.69p_private_block5.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1546p_1555p_sequence_lock_v0.1.md"
OBL_REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
AGENTS = ROOT / "AGENTS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1554p_block5_coherence_capsule_walkthrough.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def table_row(path: Path, key: str) -> str:
    return next(line for line in read(path).splitlines() if line.startswith(f"| {key} |"))


def test_coherence_report_records_block5_tokens_and_phase_state() -> None:
    text = read(COHERENCE)

    for token in (
        "block5_coherence_complete_phase_1554p",
        "context_capsule_block5_committed_phase_1554p",
        "block6_private_rehearsal_required_next_phase_1554p",
        "public_path_remains_blocked_phase_1554p",
    ):
        assert token in text

    assert "| 1554p | COMPLETE | Block 5 coherence report and private capsule v5.69p |" in text
    assert "| 1555p | PENDING | SENSITIVE window closure gate requiring exact `GO Phase 1555p` |" in text
    assert "Phase 1554p does not authorize either Block 6 execution or Phase 1448b publication." in text


def test_obligation_sweep_confirms_closures_without_new_closure_claims() -> None:
    coherence = read(COHERENCE)
    register = read(OBL_REGISTER)

    for obl, token in (
        ("OBL-023", "obl_023_closed_phase_1547p"),
        ("OBL-024", "obl_024_closed_phase_1548p"),
        ("OBL-028", "obl_028_closed_phase_1549p"),
        ("OBL-029", "obl_029_closed_phase_1550p"),
    ):
        row = table_row(OBL_REGISTER, obl)
        assert "| closed |" in row
        assert token in row
        assert token in coherence

    assert "OBL-023, OBL-024, OBL-028, and OBL-029 were closed by their owning phases" in coherence
    assert "| OBL-030 |" in register
    assert "| OBL-030 |" in coherence
    assert "| open |" in table_row(OBL_REGISTER, "OBL-030")


def test_cdl_sweep_records_cdl096_ratified_and_runtime_boundaries() -> None:
    coherence = read(COHERENCE)
    cdl096 = table_row(CDL_REGISTER, "CDL-096")
    cdl095 = table_row(CDL_REGISTER, "CDL-095")

    assert "| ratified |" in cdl096
    assert "cdl_096_ratified_phase_1553p" in cdl096
    assert "scope_token: cdl_096_scope_ratified_phase_1553p" in cdl096
    assert "werner_value_path_status: not_ecu_not_ilc_not_claimability" in cdl096
    assert "werner_flow_governor_runtime_status: not_authorized" in cdl096
    assert "global_tier_activation_status: not_authorized" in cdl096
    assert "runtime_activation_status: not_authorized" in cdl096
    assert "public_path_status: blocked" in cdl096

    assert "global_tier_activation_status: deferred_to_cdl_096" in cdl095
    assert "CDL-098 |" not in read(CDL_REGISTER)
    assert "CDL-098 | Unconsumed" in coherence


def test_capsule_supersedes_v568_and_routes_to_phase_1555p() -> None:
    text = read(CAPSULE)

    assert "context_capsule_block5_committed_phase_1554p" in text
    assert "block5_coherence_complete_phase_1554p" in text
    assert "Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.68p_private_block4b.md`" in text
    assert "| 1554p | COMPLETE | Block 5 coherence checkpoint and capsule v5.69p |" in text
    assert "| 1555p | PENDING | SENSITIVE closure gate requiring exact human GO |" in text
    assert "Block 6 | Required next after closure" in text
    assert "GLOBAL_TIER_JURY_NOT_ACTIVATED" in text


def test_frontier_docs_advance_to_phase_1555_without_public_activation() -> None:
    combined = "\n".join(
        read(path)
        for path in (SEQUENCE_LOCK, PLANNING_INDEX, STATUS, AGENTS, WALKTHROUGH, COHERENCE, CAPSULE)
    )

    for token in (
        "block5_coherence_complete_phase_1554p",
        "context_capsule_block5_committed_phase_1554p",
        "block6_private_rehearsal_required_next_phase_1554p",
        "public_path_remains_blocked_phase_1554p",
    ):
        assert token in combined

    assert "Phase 1555p is next" in combined or "## Phase 1555p" in combined or "phase_1555p" in combined
    assert "GO Phase 1555p" in combined or "Phase 1555p" in combined
    assert "phase_1555p_sensitive_window_closure_gate" in read(AGENTS) or "phase_1555p" in read(AGENTS)
    assert "no_public_rc" in read(AGENTS)
    assert "No window closure" in read(WALKTHROUGH)
    assert "No public RC" in read(WALKTHROUGH)
