from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs/specs/ilc_window_1343_1368_handoff_1368_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1368_window_1343_1368_closure_handoff_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
EPOCH_EMISSION_RUNTIME = ROOT / "ilc_core/epoch/epoch_emission_runtime.py"


REQUIRED_TOKENS = (
    "window_1343_1368_closed_phase_1368.v0.1",
    "window_1343_1368_closure_verdict_recorded_phase_1368",
    "soft_rc_eligible_final_status_recorded_phase_1368",
    "window_1369_1390_entry_criteria_recorded_phase_1368",
    "window_1369_not_open_phase_1368",
    "go_phase_1369_required_next",
    "production_minting_activation_deferred_phase_1368",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1368_handoff_schema_sections_are_ordered() -> None:
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


def test_phase_1368_required_tokens_are_recorded_on_closure_surfaces() -> None:
    for path in (HANDOFF, WALKTHROUGH, STATUS, INDEX, SEQUENCE_LOCK, FORWARD_PLAN, ROADMAP):
        text = _read(path)
        for token in REQUIRED_TOKENS:
            assert token in text, f"{path} missing {token}"


def test_phase_1368_records_deferred_minting_only_on_handoff_surfaces() -> None:
    forbidden = "production_minting_activated_phase_1368"
    for path in (HANDOFF, WALKTHROUGH, STATUS, INDEX, SEQUENCE_LOCK, ROADMAP):
        text = _read(path)
        assert "production_minting_activation_deferred_phase_1368" in text
        assert forbidden not in text, f"{path} must not record activated minting token"


def test_phase_1368_preserves_phase_1366_false_verdict_and_window_1369_boundary() -> None:
    text = _read(HANDOFF)

    assert (
        "soft_rc_eligible=false_with_blockers: "
        "[phase_1366_treasury_epoch_budget_binding_unverified]"
    ) in text
    assert "Phase 1367 fixed the named blocker but did not re-run the full gate" in text
    assert "Window 1369 is NOT open. It opens only via explicit `GO Phase 1369`." in text
    assert "CDL-088 is not opened by this phase." in text


def test_phase_1368_handoff_contains_required_tables() -> None:
    text = _read(HANDOFF)

    assert "| Phase | Topic | Status | Commit hash |" in text
    assert "| Item | Originating phase | Window 1369 obligation | Blocks Phase 1369 (yes/no) |" in text
    assert "| Entry item | Required action before or inside Window 1369-1390 |" in text
    assert "Disposition: required" in text
    assert "Active working set impacted: yes" in text
    assert (
        "Working-set descriptor: "
        "`docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`"
    ) in text
    assert (
        "Manifest: "
        "`docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json`"
    ) in text


def test_phase_1368_walkthrough_contains_prompt_required_sections() -> None:
    text = _read(WALKTHROUGH)

    for heading in (
        "## Purpose",
        "## Delivery Summary",
        "## Phase Inventory",
        "## Soft RC Final Status",
        "## Carry-Forward",
        "## Window 1369-1390 Entry Criteria",
        "## PLANNING_INDEX Updates",
        "## No Ellipses",
    ):
        assert heading in text
    assert "| Deliverable | Path | Gate result |" in text
    assert "| Phase | Topic | Status | Commit hash |" in text
    assert (
        "soft_rc_eligible=false_with_blockers: "
        "[phase_1366_treasury_epoch_budget_binding_unverified]"
    ) in text


def test_phase_1368_does_not_open_epoch_emission_runtime_gate() -> None:
    runtime = _read(EPOCH_EMISSION_RUNTIME)

    assert 'PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN = "production_minting_not_activated_phase_1345"' in runtime
    assert 'production_minting_activated=False' in runtime
    assert "production_minting_activation_not_implemented_phase_1345" in runtime
    assert "production_minting_activation_deferred_phase_1368" not in runtime


def test_phase_1368_walkthrough_has_no_ellipses() -> None:
    text = _read(WALKTHROUGH)

    assert "..." not in text
    assert "\u2026" not in text
