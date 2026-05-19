from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

HANDOFF = REPO / "docs/specs/ilc_window_1369_1390_handoff_1390_v0.1.md"
WALKTHROUGH = REPO / "docs/phases/phase_1390_window_1369_1390_closure_handoff_walkthrough.md"
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING_INDEX = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
WINDOW_GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"
ROADMAP = REPO / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PHASE_1389_RERUN = REPO / "docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md"
WALKTHROUGH_1387A = (
    REPO / "docs/phases/phase_1387a_accepted_adr_cdl_coverage_public_economics_firewall_walkthrough.md"
)
WALKTHROUGH_1387B = REPO / "docs/phases/phase_1387b_sim_genesis_compile_02_walkthrough.md"


REQUIRED_TOKENS = (
    "window_1369_1390_closed_phase_1390.v0.1",
    "window_1369_1390_closure_verdict_recorded_phase_1390",
    "mempalace_refresh_disposition_recorded_phase_1390",
    "window_1391_not_open_phase_1390",
    "go_window_1391_required_next",
)

REQUIRED_SECTIONS = (
    "## 1. Window identity and closure basis",
    "## 2. Inputs and closure inheritance",
    "## 3. Closure verdict summary",
    "## 4. Carry-forward items and residual blockers",
    "## 5. Next-window entry criteria and routing",
    "## 6. MemPalace refresh disposition",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_handoff_schema_sections_and_tokens() -> None:
    text = _read(HANDOFF)
    for section in REQUIRED_SECTIONS:
        assert section in text
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "Status: handoff artifact" in text
    assert "Classification: closure and carry-forward handoff" in text


def test_handoff_records_phase_1389_verdict_verbatim() -> None:
    text = _read(HANDOFF)
    rerun = _read(PHASE_1389_RERUN)
    assert "result=public_claimability_activated" in text
    assert "phase_1389_public_claimability_result=result=public_claimability_activated" in text
    assert "result=public_claimability_activated" in rerun


def test_handoff_records_mempalace_required_disposition() -> None:
    text = _read(HANDOFF)
    assert "- `Disposition:` `required`" in text
    assert "- `Active working set impacted:` `yes`" in text
    assert "bash tools/mempalace/build_active_working_set.sh" in text


def test_handoff_records_support_lane_walkthrough_gaps() -> None:
    text = _read(HANDOFF) + "\n" + _read(WALKTHROUGH)
    for phase in ("1387c", "1387f", "1387g", "1387h", "1387i", "1387j"):
        assert phase in text
    assert "incomplete - no walkthrough file found" in text


def test_planning_surfaces_record_window_closed() -> None:
    combined = "\n".join(
        _read(path)
        for path in (STATUS, PLANNING_INDEX, SEQUENCE_LOCK, WINDOW_GROUPING, ROADMAP)
    )
    for token in REQUIRED_TOKENS:
        assert token in combined
    assert "Window 1369-1390 is CLOSED" in combined
    assert "Window 1391+ requires explicit" in combined


def test_metadata_drift_fixed_for_1387a_and_1387b() -> None:
    assert "PENDING_HASH_BACKFILL" not in _read(WALKTHROUGH_1387A)
    assert "**Commit:** 290f5a70" in _read(WALKTHROUGH_1387A)
    assert "**Status:** complete" in _read(WALKTHROUGH_1387B)


def test_phase_1390_walkthrough_has_no_ellipsis() -> None:
    assert "..." not in _read(WALKTHROUGH)
