from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"
OLD_GUIDANCE = "docs/specs/ilc_window_1289_1296_candidate_phase_grouping_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1289_window_1289_1302_sequence_lock_walkthrough.md"

REQUIRED_TOKENS = (
    "window_1289_1302_sequence_lock_committed",
    "window_1289_1302_sequence_lock_verdict=pass",
    "phase_1290_context_capsule_v5_52_refresh_next",
    "window_1289_1302_no_public_rc_or_public_activation",
    "human_question_escalation_required_for_uncertain_authority",
    "window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1289_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SEQUENCE_LOCK)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1289_expands_prior_candidate_window() -> None:
    lock = read(SEQUENCE_LOCK)
    guidance = read(GUIDANCE)
    old_guidance = read(OLD_GUIDANCE)

    assert "1289-1302" in lock
    assert "1289-1302" in guidance
    assert "window_1289_1296_candidate_phase_grouping_recorded_after_phase_1288_fix1" in old_guidance
    assert "window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289" in lock
    assert "This document is superseded by Phase 1289" in old_guidance


def test_phase_1289_locked_order_is_complete_and_stops_before_sensitive_1291() -> None:
    lock = read(SEQUENCE_LOCK)

    for phase in range(1289, 1303):
        assert f"| {phase} |" in lock

    assert "Phase 1290 is non-sensitive" in lock
    assert "Phase 1291 is sensitive" in lock
    assert "execution must stop after Phase 1290" in lock


def test_phase_1289_preserves_public_rc_non_authorization() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "public claimability API activation",
        "public P2P",
        "public fetch serving",
        "public sidecar/projection serving",
        "source allowlist export execution",
        "release-key generation",
        "release envelope production",
        "Genesis Atlas mutation/regeneration/signing",
        "v0.2 signing",
        "CDL-088 opening",
        "ECU minting",
        "ILC settlement",
    ):
        assert phrase in lock


def test_phase_1289_discovery_and_human_escalation_are_recorded() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Known-token audit",
        "Concept-discovery search",
        "Contradiction and non-claim search",
        "Source expansion",
        "Exact-token `rg` remains only a schema/completion check",
        "token components, synonyms",
        "must stop and prompt the human reviewer",
        "default_to_no_authorization_when_canon_is_ambiguous",
    ):
        assert phrase in lock


def test_phase_1289_frontier_updates_planning_and_status() -> None:
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1289-1302 is OPEN through Phase 1289" in planning
    assert SEQUENCE_LOCK in planning
    assert GUIDANCE in planning
    assert "## Phase 1289" in status
    assert "Phase 1290 - Context Capsule v5.52 frontier refresh" in status
    assert "Phase 1291 - Public claimability verifier contract preflight" in status


def test_phase_1289_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_window_1289_1296_candidate_phase_grouping_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/phase_1289_window_1289_1302_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1289_window_1289_1302_sequence_lock.py -> validation",
        "graph_delta=support_tests_changed:tests/test_window_1289_1302_prompt_drafts.py -> validation/frontier",
    ):
        assert graph_delta in lock
        assert graph_delta in walkthrough
