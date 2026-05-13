from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.55.md"
OLD_CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.54.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1331_context_capsule_v5_55_release_candidate_freeze_walkthrough.md"
CDL = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "context_capsule_v5_55_release_candidate_freeze_phase_1331.v0.1",
    "capsule_v5_55_supersedes_v5_54",
    "window_1330_1342_sequence_lock_reflected_in_capsule_phase_1331",
    "final_rc_blocker_map_refreshed_phase_1331",
    "phase_1332_final_deterministic_code_security_audit_next",
    "public_rc_remains_blocked_after_phase_1331",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1331_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(CAPSULE)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1331_capsule_supersedes_v5_54_in_session_canon() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)

    assert f"**Supersedes:** `{OLD_CAPSULE}`" in capsule
    assert "| **Capsule v5.55** ⬅ CURRENT |" in planning
    assert "| **Context Capsule v5.55** ⬅ CURRENT |" in planning
    assert "| **Capsule v5.54** (superseded) |" in planning
    assert "| **Context Capsule v5.54** (superseded) |" in planning
    assert "| **Capsule v5.54** ⬅ CURRENT |" not in planning
    assert "| **Context Capsule v5.54** ⬅ CURRENT |" not in planning


def test_phase_1331_reflects_window_1330_1342_and_sensitive_next() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1330-1342 is OPEN through Phase 1331" in capsule
    assert "Window 1330-1342 is OPEN through Phase 1331" in planning
    assert "docs/specs/ilc_phase_1330_1342_sequence_lock_v0.1.md" in capsule
    assert "window_1330_1342_sequence_lock_committed" in capsule
    assert "window_1330_1342_sequence_lock_verdict=pass" in capsule
    assert "Phase 1331 records this capsule freeze only. It does not execute Phase 1332" in capsule
    assert "Phase 1332 is the next planned phase and is sensitive" in capsule
    assert "## Phase 1331" in status
    assert "Phase 1332 - Final deterministic code/security audit" in status


def test_phase_1331_final_rc_blocker_map_is_current() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "Source allowlist export",
        "Clean materialized public tree",
        "Release artifacts",
        "Release keys/envelopes",
        "Signing and v0.2 signing",
        "Public claimability/API",
        "Public P2P/fetch/sidecar path",
        "Public confidential coordination",
        "Wallet/ECU/ILC value path",
        "ATLAS-G-007",
        "ATLAS-G-008",
        "ATLAS-G-009",
        "ATLAS-G-010",
        "Identity bootstrap",
        "Counsel/publication",
    ):
        assert phrase in capsule


def test_phase_1331_preserves_identity_bootstrap_guard() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "identity_seed_commitment = sha384(\"ilc-seed-commit-v1:\" || identity_seed)",
        "Phase 1331 Fix1 repaired the runtime CDL-069 commitment formula",
        "Public bootstrap must also preserve the Genesis-rooted identity invariant",
        "Private graph content must not become identity-seed entropy or recovery material",
        "dummy Agent Birth artifact",
    ):
        assert phrase in capsule


def test_phase_1331_preserves_non_authorization_boundary() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "source allowlist export execution",
        "release artifact production",
        "release-key generation",
        "release envelope production",
        "release signing material generation",
        "signature production",
        "public claimability/API activation",
        "public P2P",
        "public fetch serving",
        "public sidecar/projection serving",
        "non-loopback bind",
        "peer discovery",
        "public confidential coordination serving",
        "Genesis Atlas mutation",
        "v0.2 signing",
        "CDL mutation",
        "CDL-088 opening",
        "identity artifact creation",
        "identity-seed generation",
        "wallet-facing withdrawal request",
        "ECU minting",
        "ILC settlement",
        "counsel approval",
    ):
        assert phrase in capsule


def test_phase_1331_walkthrough_records_discovery_and_graph_delta() -> None:
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
        "MemPalace returned stale historical capsule/planning hits only",
    ):
        assert phrase in walkthrough

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.55.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1331_context_capsule_v5_55_release_candidate_freeze.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1331_context_capsule_v5_55_release_candidate_freeze_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status


def test_phase_1331_does_not_mutate_cdl_or_close_public_rc() -> None:
    capsule = read(CAPSULE)
    cdl = read(CDL)

    assert "CDL-088 remains unopened" in capsule
    assert "| CDL-088 |" not in cdl
    assert "public_rc_remains_blocked_after_phase_1331" in capsule
    assert "Phase 1331 records this capsule freeze only. It does not execute Phase 1332" in capsule
