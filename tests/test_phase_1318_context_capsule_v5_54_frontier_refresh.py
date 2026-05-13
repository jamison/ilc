from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.54.md"
OLD_CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1318_context_capsule_v5_54_frontier_refresh_walkthrough.md"
CDL = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "context_capsule_v5_54_frontier_refresh_phase_1318.v0.1",
    "capsule_v5_54_supersedes_v5_53",
    "window_1317_1329_sequence_lock_reflected_in_capsule_phase_1318",
    "release_dry_run_blocker_map_refreshed_phase_1318",
    "phase_1319_deterministic_source_allowlist_export_rehearsal_next",
    "public_rc_remains_blocked_after_phase_1318",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1318_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(CAPSULE)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1318_capsule_supersedes_v5_53_in_session_canon() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)

    assert f"**Supersedes:** `{OLD_CAPSULE}`" in capsule
    assert "| **Capsule v5.54** \u2b05 CURRENT |" in planning
    assert "| **Context Capsule v5.54** \u2b05 CURRENT |" in planning
    assert "| **Capsule v5.53** (superseded) |" in planning
    assert "| **Context Capsule v5.53** (superseded) |" in planning
    assert "| **Capsule v5.53** \u2b05 CURRENT |" not in planning
    assert "| **Context Capsule v5.53** \u2b05 CURRENT |" not in planning


def test_phase_1318_reflects_phase_1317_lock_and_next_sensitive_phase() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1317-1329 is OPEN through Phase 1324 Fix2" in capsule
    assert "Window 1317-1329 is OPEN through Phase 1324 Fix2" in planning
    assert "docs/specs/ilc_phase_1317_1329_sequence_lock_v0.1.md" in capsule
    assert "window_1317_1329_sequence_lock_committed" in capsule
    assert "window_1317_1329_sequence_lock_verdict=pass" in capsule
    assert "Phase 1325 - CCSS-002 capability/membership boundary" in capsule
    assert "Phase 1325 is sensitive and requires explicit `GO Phase 1325`" in capsule
    assert "## Phase 1318" in status
    assert "Phase 1325 - CCSS-002 capability/membership boundary" in status


def test_phase_1318_release_dry_run_blocker_map_is_current() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "1319 source materialization rehearsal",
        "zero exported `PUBLIC_RC_EXCLUDE` markers",
        "stripped-helper imports",
        "1320 release artifact manifest rehearsal",
        "1321 release key/envelope procedure rehearsal",
        "1322 three-machine/seven-agent private deployment rehearsal",
        "1323 OpenClaw/NemoClaw claimable profile dry run",
        "1324 CCSS-001 private/gated shard contract",
        "1325 CCSS-002 capability/membership boundary",
        "1326 CCSS-003 sealed sender local delivery boundary",
        "1327 CCSS-004 gossip/jitter/cover tests",
        "1328 CCSS-005 private OpenClaw/NemoClaw droplet dry run",
        "1329 closure gate",
    ):
        assert phrase in capsule


def test_phase_1318_cross_cutting_public_rc_blockers_remain_open() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "legacy public-labeled FastAPI routes",
        "public claimability verifier/API serving authority",
        "replay/nullifier and duplicate-claim registry policy",
        "`PUBLIC_RC_EXCLUDE` helper replacement",
        "Rust public-P2P substrate ADR/integration gate",
        "TransportPrincipal public-path activation authority",
        "public sidecar/projection serving authority",
        "source allowlist export execution",
        "clean materialized public tree production",
        "release artifact production",
        "release-key generation",
        "release envelopes",
        "Genesis Atlas mutation/regeneration/signing",
        "v0.2 signing authorization",
        "wallet-facing withdrawal",
        "ECU minting activation",
        "ILC settlement activation",
        "public confidential messaging",
    ):
        assert phrase in capsule


def test_phase_1318_preserves_atlas_g_ccss_split_and_stale_reference_note() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "ccss_tail_routed_without_atlas_g_compression_phase_1317",
        "atlas_g_tail_carried_forward_not_hidden_inside_ccss_phase_1317_1329",
        "not substitutes for ATLAS-G-007 through ATLAS-G-010",
        "No current Window 1317-1329 control document still points to the obsolete",
        "Window 1289-1296",
        "References to Phase 1302 are historical",
    ):
        assert phrase in capsule


def test_phase_1318_preserves_non_authorization_boundary() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "public RC claim",
        "public claimability API activation",
        "public verifier service activation",
        "public P2P exposure",
        "public fetch serving",
        "public sidecar/projection serving",
        "source allowlist export execution",
        "release artifact production",
        "release-key generation",
        "release envelope production",
        "release signing material generation",
        "helper promotion",
        "marker removal",
        "helper stripping",
        "Genesis Atlas mutation",
        "v0.2 signing",
        "CDL-088 opening",
        "wallet-facing withdrawal request",
        "wallet-facing transfer request",
        "wallet-facing spend request",
        "ECU minting",
        "ILC settlement",
        "public confidential messaging",
        "public confidential coordination serving",
        "production `commit.epoch` emission",
    ):
        assert phrase in capsule


def test_phase_1318_walkthrough_records_discovery_and_graph_delta() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for phrase in (
        "Section 0a Known-token audit",
        "Section 0b Concept-discovery search",
        "Section 0c Contradiction and non-claim search",
        "Section 0d Source expansion",
        "Capsule Supersession Notes",
        "Blocker Map Delta",
        "Known Stale References",
        "Non-Authorization Boundary",
    ):
        assert phrase in walkthrough

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.54.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1318_context_capsule_v5_54_frontier_refresh.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1318_context_capsule_v5_54_frontier_refresh_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status


def test_phase_1318_does_not_mutate_cdl_or_close_public_rc() -> None:
    capsule = read(CAPSULE)
    cdl = read(CDL)

    assert "| CDL-088 |" not in cdl
    assert "CDL-088 opening" in capsule
    assert "public_rc_remains_blocked_after_phase_1318" in capsule
    assert "does not execute Phase 1319" in capsule
