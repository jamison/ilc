from pathlib import Path


PLAN = Path("docs/specs/ilc_tier3_runtime_linkage_implementation_plan_1195_v0.1.md")
ROADMAP = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
STATUS = Path("docs/phases/STATUS.md")
WALKTHROUGH = Path("docs/phases/phase_1195_tier3_runtime_linkage_scoping_walkthrough.md")


def test_tier3_plan_exists_and_has_token() -> None:
    content = PLAN.read_text(encoding="utf-8")
    assert "tier3_runtime_linkage_scope_committed_phase_1195" in content
    assert "scope committed" in content


def test_tier3_plan_references_adr_0020_and_node_families() -> None:
    content = PLAN.read_text(encoding="utf-8")
    assert "ADR-0020" in content
    assert "`schema:*`" in content
    assert "`runtime:*`" in content


def test_tier3_plan_records_no_runtime_mutation() -> None:
    content = PLAN.read_text(encoding="utf-8")
    assert "No such token is introduced in Phase 1195" in content
    assert "mutate `ilc_core/`" in content
    assert "mutate signed Genesis v0.1" in content


def test_roadmap_and_planning_index_record_tier3_scope() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Tier-3 runtime linkage scope committed" in roadmap
    assert "tier3_runtime_linkage_scope_committed_phase_1195" in roadmap
    assert "Window 1191-1199 is IN PROGRESS through Phase 1195" in planning
    assert "tier3_runtime_linkage_scope_committed_phase_1195" in planning


def test_status_and_walkthrough_mark_phase_1195_complete() -> None:
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    assert "## Phase 1195" in status
    assert "tier3_runtime_linkage_scope_committed_phase_1195" in status
    assert "**Status:** complete" in walkthrough
    assert "tier3_runtime_linkage_scope_committed_phase_1195" in walkthrough
