from pathlib import Path


SCOPE = Path("docs/specs/ilc_persistent_rate_limiter_scope_1196_v0.1.md")
ROADMAP = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
STATUS = Path("docs/phases/STATUS.md")
WALKTHROUGH = Path("docs/phases/phase_1196_persistent_rate_limiter_scoping_walkthrough.md")


def test_persistent_rate_limiter_scope_exists_and_has_token() -> None:
    content = SCOPE.read_text(encoding="utf-8")
    assert "persistent_rate_limiter_scope_committed_phase_1196" in content
    assert "scope committed" in content


def test_scope_identifies_existing_cdl_077_surface() -> None:
    content = SCOPE.read_text(encoding="utf-8")
    assert "CDL-077" in content
    assert "WANT-HAVE" in content
    assert "WANT-BLOCK" in content
    assert "WANT_BLOCK_RATE_LIMIT_PER_MINUTE = 10" in content
    assert "FetchRateLimiter" in content


def test_scope_records_persistence_guardrails() -> None:
    content = SCOPE.read_text(encoding="utf-8")
    assert "Do not use wall clock as protocol source of truth" in content
    assert "Do not persist raw requester IDs" in content
    assert "Do not accumulate unbounded requester buckets" in content
    assert "sort_keys=True" in content
    assert "allow_nan=False" in content


def test_roadmap_and_planning_index_record_rate_limiter_scope() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Persistent rate limiter scope committed" in roadmap
    assert "persistent_rate_limiter_scope_committed_phase_1196" in roadmap
    assert "Window 1191-1199 is IN PROGRESS through Phase 1196" in planning
    assert "persistent_rate_limiter_scope_committed_phase_1196" in planning


def test_status_and_walkthrough_mark_phase_1196_complete() -> None:
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    assert "## Phase 1196" in status
    assert "persistent_rate_limiter_scope_committed_phase_1196" in status
    assert "**Status:** complete" in walkthrough
    assert "persistent_rate_limiter_scope_committed_phase_1196" in walkthrough
