from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
OLD_CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1290_context_capsule_v5_52_frontier_refresh_walkthrough.md"
PROMPT = "docs/antigravity_tasks/antigravity_prompt__phase_1290_g8_context_capsule_v5_52_frontier_refresh.md"

REQUIRED_TOKENS = (
    "context_capsule_v5_52_frontier_refresh_phase_1290.v0.1",
    "capsule_v5_52_supersedes_v5_51",
    "window_1289_1302_sequence_lock_reflected_in_capsule_phase_1290",
    "public_rc_blocker_map_refreshed_phase_1290",
    "public_rc_remains_blocked_after_phase_1290",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1290_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(CAPSULE)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1290_capsule_supersedes_v5_51_in_session_canon() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)

    assert f"**Supersedes:** `{OLD_CAPSULE}`" in capsule
    assert "| **Capsule v5.52** ⬅ CURRENT |" in planning
    assert "| **Context Capsule v5.52** ⬅ CURRENT |" in planning
    assert "| **Capsule v5.51** (superseded) |" in planning
    assert "| **Context Capsule v5.51** (superseded) |" in planning
    assert "| **Capsule v5.51** ⬅ CURRENT |" not in planning
    assert "| **Context Capsule v5.51** ⬅ CURRENT |" not in planning


def test_phase_1290_reflects_active_window_and_sensitive_stop() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1289-1302 is open through Phase 1290" in capsule
    assert "Window 1289-1302 is OPEN through Phase 1290" in planning
    assert "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md" in capsule
    assert "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in capsule
    assert "window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289" in capsule
    assert "Phase 1291 is sensitive" in planning
    assert "requires explicit `GO Phase 1291`" in capsule
    assert "## Phase 1290" in status
    assert "Phase 1291 - Public claimability verifier contract preflight" in status


def test_phase_1290_prompt_was_repointed_to_active_lock() -> None:
    prompt = read(PROMPT)

    assert "Window 1289-1302 sequence lock" in prompt
    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "window_1289_1302_sequence_lock_reflected_in_capsule_phase_1290" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt
    assert "window_1289_1296_sequence_lock_reflected_in_capsule_phase_1290" not in prompt


def test_phase_1290_public_rc_blocker_map_is_current() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "Final public claimability verifier/API authority",
        "Actual TransportPrincipal public-path activation authority",
        "Actual public sidecar/projection serving authority",
        "Counsel/license/CLA/trademark/IP/publication clearance",
        "Source allowlist export execution",
        "Release artifact production",
        "release-key generation",
        "release envelope production",
        "Genesis Atlas mutation/regeneration/signing",
        "v0.2 signing authorization",
        "CDL-088 opening",
        "Wallet withdrawal/transfer/spend semantics",
        "ECU minting",
        "ILC settlement",
    ):
        assert phrase in capsule


def test_phase_1290_preserves_non_authorization_boundary() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "public claimability API activation",
        "public verifier service",
        "public P2P",
        "public fetch serving",
        "public sidecar/projection serving",
        "source allowlist export execution",
        "public release artifact production",
        "release-key generation",
        "release envelope production",
        "wallet withdrawal",
        "wallet transfer",
        "wallet spend",
        "CDL mutation",
        "CDL-088 opening",
        "Genesis Atlas mutation/regeneration",
        "v0.2 signing",
        "IP filing",
        "paper publication",
        "production `commit.epoch` emission",
    ):
        assert phrase in capsule


def test_phase_1290_walkthrough_records_discovery_and_graph_delta() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for phrase in (
        "Section 0a Known-token audit",
        "Section 0b Concept-discovery search",
        "Section 0c Contradiction and non-claim search",
        "Section 0d Source expansion",
        "Capsule Supersession Notes",
        "Blocker Map Delta",
        "Non-Authorization Boundary",
    ):
        assert phrase in walkthrough

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier",
        "graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1290_g8_context_capsule_v5_52_frontier_refresh.md -> planning/prompts",
        "graph_delta=support_tests_added:tests/test_phase_1290_context_capsule_v5_52_frontier_refresh.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1290_context_capsule_v5_52_frontier_refresh_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status


def test_phase_1290_does_not_mutate_cdl_or_close_public_rc() -> None:
    capsule = read(CAPSULE)

    assert "Phase 1290 does not mutate the CDL register" in capsule
    assert "CDL-088 remains unopened" in capsule
    assert "Phase 1290 does not close any of those blockers" in capsule
    assert "public_rc_remains_blocked_after_phase_1290" in capsule
