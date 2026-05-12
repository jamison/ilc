from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
OLD_CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1304_context_capsule_v5_53_frontier_refresh_walkthrough.md"
CDL = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "context_capsule_v5_53_frontier_refresh_phase_1304.v0.1",
    "capsule_v5_53_supersedes_v5_52",
    "window_1303_1316_sequence_lock_reflected_in_capsule_phase_1304",
    "public_rc_blocker_map_refreshed_phase_1304",
    "phase_1305_offline_claimability_receipt_verifier_sidecar_next",
    "public_rc_remains_blocked_after_phase_1304",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1304_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(CAPSULE)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1304_capsule_supersedes_v5_52_in_session_canon() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)

    assert f"**Supersedes:** `{OLD_CAPSULE}`" in capsule
    assert "| **Capsule v5.53** ⬅ CURRENT |" in planning
    assert "| **Context Capsule v5.53** ⬅ CURRENT |" in planning
    assert "| **Capsule v5.52** (superseded) |" in planning
    assert "| **Context Capsule v5.52** (superseded) |" in planning
    assert "| **Capsule v5.52** ⬅ CURRENT |" not in planning
    assert "| **Context Capsule v5.52** ⬅ CURRENT |" not in planning


def test_phase_1304_reflects_window_1303_1316_and_sensitive_stop() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Phase 1304 records this capsule refresh and does not execute Phase 1305" in capsule
    assert "Window 1303-1316 is CLOSED / PASS" in capsule
    assert "Window 1303-1316 is CLOSED / PASS" in planning
    assert "docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md" in capsule
    assert "docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md" in capsule
    assert "window_1303_1316_sequence_lock_committed" in capsule
    assert "window_1303_1316_sequence_lock_verdict=pass" in capsule
    assert "Phase 1305 is complete after explicit `GO Phase 1305`" in capsule
    assert "## Phase 1304" in status
    assert "Phase 1305 - Offline/local claimability and receipt verifier sidecar/library" in status


def test_phase_1304_public_rc_blocker_map_is_current() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "legacy public-labeled FastAPI routes",
        "public claimability verifier/API serving authority",
        "PUBLIC_RC_EXCLUDE helper replacement and dry-run export proof",
        "privacy filter implementation/review",
        "replay/nullifier and duplicate-claim registry policy",
        "TransportPrincipal public-path activation authority",
        "Rust public-P2P substrate ADR/integration gate",
        "public sidecar/projection serving authority",
        "Counsel/license/CLA/trademark/IP/publication clearance",
        "source allowlist export execution",
        "clean materialized public tree production",
        "release artifact production",
        "release-key generation",
        "release envelope production",
        "Genesis Atlas mutation/regeneration/signing",
        "v0.2 signing authorization",
        "CDL-088 opening",
        "wallet-facing action activation",
        "ECU minting",
        "ILC settlement",
    ):
        assert phrase in capsule


def test_phase_1304_preserves_non_authorization_boundary() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "public claimability API activation",
        "public verifier service",
        "public P2P",
        "public fetch serving",
        "public sidecar/projection serving",
        "source allowlist export execution",
        "public release artifact production",
        "release artifact manifest instance production",
        "release-key generation",
        "release envelope production",
        "wallet-facing withdrawal request",
        "wallet-facing transfer request",
        "wallet-facing spend request",
        "CDL mutation",
        "CDL-088 opening",
        "Genesis Atlas mutation/regeneration",
        "v0.2 signing",
        "IP filing",
        "paper publication",
        "production `commit.epoch` emission",
    ):
        assert phrase in capsule


def test_phase_1304_records_sidecar_and_rust_gate_routing() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "OpenClaw, NemoClaw, DigitalOcean droplets",
        "hosts or consumers, not protocol substrates",
        "Offline claimability and receipt verifier sidecar",
        "Sidecar registry and deterministic manifest",
        "Truth primitive submission sidecar boundary",
        "TransportPrincipal admission sidecar substrate",
        "Local graph/memory projection sidecar",
        "Confidential coordination local preview profile",
        "confidential_coordination_sidecar_suite_not_public_rc_blocker_by_default",
        "rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate",
        "readiness-only/default-off",
    ):
        assert phrase in capsule


def test_phase_1304_walkthrough_records_discovery_and_graph_delta() -> None:
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
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.53.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1304_context_capsule_v5_53_frontier_refresh.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1304_context_capsule_v5_53_frontier_refresh_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status


def test_phase_1304_does_not_mutate_cdl_or_close_public_rc() -> None:
    capsule = read(CAPSULE)
    cdl = read(CDL)

    assert "CDL-088 remains unopened" in capsule
    assert "Phase 1308 does not mutate the" in capsule
    assert "CDL register" in capsule
    assert "Phase 1304 records this capsule refresh and does not execute Phase 1305" in capsule
    assert "| CDL-088 |" not in cdl
    assert "public_rc_remains_blocked_after_phase_1304" in capsule
