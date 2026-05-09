from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
OLD_CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.50.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1282_context_capsule_v5_51_frontier_refresh_walkthrough.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "context_capsule_v5_51_frontier_refresh_phase_1282.v0.1",
    "capsule_v5_51_supersedes_v5_50",
    "cdl087_ratification_reflected_in_capsule_phase_1282",
    "window_1273_1280_closure_reflected_in_capsule_phase_1282",
    "public_rc_remains_blocked_after_phase_1282",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1282_capsule_required_tokens_are_published() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)
    status = read(STATUS)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in capsule
        assert token in planning
        assert token in status
        assert token in walkthrough


def test_phase_1282_capsule_supersedes_v5_50_in_session_canon() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)
    old_capsule = read(OLD_CAPSULE)

    assert f"**Supersedes:** `{OLD_CAPSULE}`" in capsule
    assert "| **Capsule v5.51** ⬅ CURRENT |" in planning
    assert "| **Context Capsule v5.51** ⬅ CURRENT |" in planning
    assert "| **Capsule v5.50** (superseded) |" in planning
    assert "| **Context Capsule v5.50** (superseded) |" in planning
    assert "| **Capsule v5.50** ⬅ CURRENT |" not in planning
    assert "| **Context Capsule v5.50** ⬅ CURRENT |" not in planning
    assert "OPEN / PRELOCKED / NOT RATIFIED" in old_capsule
    assert "OPEN / PRELOCKED / NOT RATIFIED" not in capsule


def test_phase_1282_reflects_cdl087_ratification_without_public_activation() -> None:
    capsule = read(CAPSULE)
    cdl_register = read(CDL_REGISTER)

    assert "| CDL-087 |" in cdl_register
    assert "| ratified |" in cdl_register
    assert "public_fetch_serving_status: not_enabled" in cdl_register
    assert "public_sidecar_projection_status: blocked_pending_separate_authorization" in cdl_register
    assert "cdl087_ratified_phase_1278_fix1" in capsule
    assert "cdl087_register_mutated_phase_1278_fix1" in capsule
    assert "cdl087_public_fetch_serving_not_enabled_phase_1278_fix1" in capsule
    assert "cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1" in capsule
    assert "no_cdl088_opening_phase_1278_fix1" in capsule
    assert "CDL-088 remains unopened" in capsule


def test_phase_1282_window_frontier_and_sensitive_stop_are_explicit() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)
    status = read(STATUS)

    assert "Window 1273-1280 is closed with a pass verdict" in capsule
    assert "Window 1281-1288 open through Phase 1284" in capsule
    assert "Window 1281-1288 is OPEN through Phase 1284" in planning
    assert "## Phase 1282" in status
    assert "## Phase 1283" in status
    assert "requires explicit `GO Phase 1285`" in capsule
    assert "Phase 1285 is sensitive and requires explicit `GO Phase 1285`" in planning


def test_phase_1282_public_rc_release_and_signing_remain_blocked() -> None:
    capsule = read(CAPSULE)

    for phrase in (
        "Public RC remains blocked after Phase 1284",
        "final public claimability API/verifier authority",
        "public sidecar/projection serving authorization",
        "Source allowlist export execution",
        "release artifacts, release keys, release envelopes",
        "Genesis Atlas mutation/regeneration/signing and v0.2 signing authorization",
        "ECU minting, ILC settlement, and withdrawal runtime activation",
        "Phase 1283 is a sensitive public claimability authority preflight only",
    ):
        assert phrase in capsule


def test_phase_1282_genesis_and_h_ip_frontier_are_current() -> None:
    capsule = read(CAPSULE)

    assert "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c" in capsule
    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in capsule
    assert "v0.2 remains unsigned" in capsule
    assert "Genesis Atlas v0.2 signing remains deferred until the Atlas-G tail" in capsule
    assert "h_series_020_plus_registered_phase_1280_fix1" in capsule
    assert "ip_lane_001_plus_registered_phase_1280_fix1" in capsule
    assert "PUBLIC_RC_EXCLUDE: internal_ip_publication_planning_not_public_rc_launch_surface" in capsule


def test_phase_1282_walkthrough_records_discovery_and_graph_delta() -> None:
    walkthrough = read(WALKTHROUGH)

    for phrase in (
        "§0a Known-token audit",
        "§0b Concept-discovery search",
        "§0c Contradiction and non-claim search",
        "§0d Source expansion and newly discovered tokens",
        "Stale v5.50 corrections",
        "Non-authorization boundary",
    ):
        assert phrase in walkthrough

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1282_context_capsule_v5_51_frontier_refresh.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1282_context_capsule_v5_51_frontier_refresh_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in read(STATUS)


def test_phase_1282_does_not_mutate_cdl_register_status_beyond_existing_cdl087_ratification() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)

    assert "Phase 1282 Fix1 does not" in planning
    assert "mutate the CDL register" in planning
    assert "CDL mutation" in capsule
    assert "CDL-088 opening" in capsule
