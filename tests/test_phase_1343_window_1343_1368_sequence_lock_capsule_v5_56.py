from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1343_g8_window_1343_1368_sequence_lock_capsule_v5_56.md"
)
SEQUENCE_LOCK = "docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.56.md"
OLD_CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.55.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = (
    "docs/phases/"
    "phase_1343_window_1343_1368_sequence_lock_capsule_v5_56_walkthrough.md"
)
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
FORWARD_PLAN = (
    "docs/specs/"
    "ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
CDL = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
EPOCH_WITNESS = "ilc_core/epoch/epoch_boundary_witness_runtime.py"

REQUIRED_TOKENS = (
    "window_1343_1368_sequence_lock_committed",
    "window_1343_1368_sequence_lock_verdict=pass",
    "context_capsule_v5_56_window_1343_sequence_lock_phase_1343.v0.1",
    "capsule_v5_56_supersedes_v5_55",
    "phase_1344_issuance_stack_scoping_next",
    "window_1343_1368_no_public_activation_or_value_path_authority",
    "soft_rc_gate_routed_phase_1366",
    "public_rc_remains_blocked_after_phase_1343",
    "cdl_053_vehicle_collision_recorded_phase_1343",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1343_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(PROMPT)
        assert token in read(SEQUENCE_LOCK)
        assert token in read(CAPSULE)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1343_opens_window_only_through_1343() -> None:
    lock = read(SEQUENCE_LOCK)
    capsule = read(CAPSULE)
    planning = read(PLANNING)

    assert "Window 1343-1368 is CLOSED through Phase 1368" in lock
    assert "Window 1343-1368 is OPEN through Phase 1343" in capsule
    assert "Window 1343-1368" in planning
    assert "Phase 1368 closes the window" in lock
    assert "Phase 1344" in capsule
    assert "Phase 1344 was not executed" in read(WALKTHROUGH)

    for phase in range(1343, 1369):
        assert f"| {phase} |" in lock


def test_phase_1343_capsule_supersedes_v5_55_in_session_canon() -> None:
    capsule = read(CAPSULE)
    planning = read(PLANNING)

    assert f"**Supersedes:** `{OLD_CAPSULE}`" in capsule
    assert "| **Capsule v5.56** (superseded) |" in planning
    assert "| **Context Capsule v5.56** (superseded) |" in planning
    assert "| **Capsule v5.55** (superseded) |" in planning
    assert "| **Context Capsule v5.55** (superseded) |" in planning
    assert "| **Capsule v5.55** <- CURRENT |" not in planning
    assert "| **Capsule v5.57** |" in planning


def test_phase_1343_records_cdl_053_collision_without_opening_it() -> None:
    lock = read(SEQUENCE_LOCK)
    capsule = read(CAPSULE)
    status = read(STATUS)
    cdl = read(CDL)

    assert "CDL-053 has no register row" in lock
    assert "older canon reserves CDL-053 for Werner-credit architecture" in lock
    assert "Phase 1344 must resolve" in capsule
    assert "cdl_053_vehicle_collision_recorded_phase_1343" in status
    assert "| CDL-053 |" not in cdl


def test_phase_1343_records_mysticeti_source_checked_status() -> None:
    lock = read(SEQUENCE_LOCK)
    capsule = read(CAPSULE)

    for phrase in (
        "M-series M-001 through M-022 is complete",
        "`ilc_consensus/` contains the Rust DAG-BFT crate",
        "M-009 4-validator testnet config exists",
        "testnet-only",
        "HIGH-002 is fixed in current code",
        "older M-series handoff text still carries historical limitation context",
        "SEC-004 validator-set epoch binding exists in Rust fast path",
        "production integration remains future work",
    ):
        assert phrase in lock

    for phrase in (
        "M-series and `ilc_consensus/` exist",
        "production `ilc_core/` bridge remains future work",
        "No privacy claim is authorized",
    ):
        assert phrase in capsule


def test_phase_1343_preserves_blocking_authority_deferred_state() -> None:
    witness = read(EPOCH_WITNESS)
    lock = read(SEQUENCE_LOCK)

    assert "BLOCKING_AUTHORITY_DEFERRED" in witness
    assert "`BLOCKING_AUTHORITY_DEFERRED=False`" in lock
    assert "CDL-057 activation" in lock
    assert "executed after explicit `GO Phase 1364` and CDL mutation authority" in lock


def test_phase_1343_preserves_non_authorization_boundary() -> None:
    lock = read(SEQUENCE_LOCK)
    capsule = read(CAPSULE)

    for phrase in (
        "production-minted ILC",
        "ECU minting",
        "ILC settlement",
        "wallet-facing withdrawal request",
        "public claimability/API activation",
        "public P2P",
        "non-loopback bind",
        "Mysticeti production deployment",
        "live ECU transfer submission to `ilc_consensus/`",
        "soft-RC eligibility",
        "sender-privacy claim",
        "CDL mutation",
        "CDL-053 opening",
        "CDL-088 opening",
        "identity artifact creation",
        "counsel approval",
    ):
        assert phrase in lock
        assert phrase in capsule


def test_phase_1343_updates_forward_plan_and_roadmap_frontier() -> None:
    forward = read(FORWARD_PLAN)
    roadmap = read(ROADMAP)

    for phrase in (
        "window_1343_1368_sequence_lock_committed",
        "context_capsule_v5_56_window_1343_sequence_lock_phase_1343.v0.1",
        "cdl_053_vehicle_collision_recorded_phase_1343",
    ):
        assert phrase in forward
        assert phrase in roadmap

    assert "Phase 1344 is the next planned phase" in forward
    assert "Window 1343-1368 is CLOSED through Phase 1368" in roadmap


def test_phase_1343_walkthrough_records_discovery_and_graph_delta() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for phrase in (
        "Section 0a Known-token audit",
        "Section 0b Concept-discovery search",
        "Section 0c Contradiction and non-claim search",
        "Section 0d Source expansion",
        "MemPalace",
        "CDL-053 vehicle collision",
    ):
        assert phrase in walkthrough

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.56.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1343_window_1343_1368_sequence_lock_capsule_v5_56.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1343_window_1343_1368_sequence_lock_capsule_v5_56_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status
