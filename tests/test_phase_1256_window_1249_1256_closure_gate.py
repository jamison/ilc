from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


HANDOFF = "docs/specs/ilc_window_1249_1256_handoff_1256_v0.1.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1256_window_1249_1256_closure_gate_walkthrough.md"


REQUIRED_TOKENS = [
    "window_1249_1256_closed_phase_1256",
    "window_1249_1256_closure_gate_verdict=pass",
    "phase_1256_window_1249_1256_closure_complete",
    "phase_1250_fix1_gap_audit_routes_reconciled_phase_1256",
    "window_1257_plus_sequence_lock_required_before_next_phase_assignment",
]


def test_phase_1256_required_tokens_are_published() -> None:
    handoff = read(HANDOFF)
    status = read(STATUS)
    planning = read(PLANNING)
    walkthrough = read(WALKTHROUGH)

    for token in REQUIRED_TOKENS:
        assert token in handoff
        assert token in status
        assert token in planning
        assert token in walkthrough


def test_handoff_follows_closure_schema_and_mempalace_disposition() -> None:
    handoff = read(HANDOFF)
    required_sections = [
        "## 1. Window identity and closure basis",
        "## 2. Inputs and closure inheritance",
        "## 3. Closure verdict summary",
        "## 4. Carry-forward items and residual blockers",
        "## 5. Next-window entry criteria and routing",
        "## 6. MemPalace refresh disposition",
    ]
    positions = [handoff.index(section) for section in required_sections]
    assert positions == sorted(positions)

    assert "Status: handoff artifact" in handoff
    assert "Classification: closure and carry-forward handoff" in handoff
    assert "Disposition: required" in handoff
    assert "Active working set impacted: yes" in handoff
    assert "docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json" in handoff
    assert "bash tools/mempalace/build_active_working_set.sh" in handoff


def test_all_phase_1250_fix1_routes_are_reconciled() -> None:
    handoff = read(HANDOFF)
    expected_dispositions = {
        "RCGAP-1250-FIX1-001": "closed_phase_1251",
        "RCGAP-1250-FIX1-002": "closed_phase_1254_no_bulk_history_rewrite",
        "RCGAP-1250-FIX1-003": "closed_phase_1252",
        "RCGAP-1250-FIX1-004": "closed_phase_1253_classified_no_runtime_change",
        "RCGAP-1250-FIX1-005": "carried_forward_rust_m5_public_p2p",
        "RCGAP-1250-FIX1-006": "closed_phase_1252_boundary_public_claimability_deferred",
        "RCGAP-1250-FIX1-007": "carried_forward_cdl_087_sensitive_ratification",
        "RCGAP-1250-FIX1-008": "carried_forward_transport_principal_public_p2p",
        "RCGAP-1250-FIX1-009": "carried_forward_v0_2_signing_authorization",
        "RCGAP-1250-FIX1-010": "superseded_by_current_cdl_086_ratification",
    }

    for finding_id, disposition in expected_dispositions.items():
        assert finding_id in handoff
        assert disposition in handoff


def test_public_rc_non_authorization_boundary_is_preserved() -> None:
    handoff = read(HANDOFF)
    roadmap = read(ROADMAP)
    planning = read(PLANNING)
    status = read(STATUS)

    required_non_claims = [
        "public RC claim",
        "public repository publication",
        "public P2P exposure",
        "public sidecar/projection serving",
        "public claimability activation",
        "CDL-087 ratification",
        "release-key generation",
        "v0.2 signing",
    ]
    for non_claim in required_non_claims:
        assert non_claim in handoff

    assert "Public RC remains blocked" in planning
    assert "public_rc_remains_blocked_after_phase_1256" in roadmap
    assert "Window 1257+ sequence lock is required before assigning further phase numbers" in status


def test_planning_index_points_to_phase_1256_handoff_as_current_frontier() -> None:
    planning = read(PLANNING)
    assert "Window 1249-1256 CLOSED / PASS through Phase 1256" in planning
    assert HANDOFF in planning
    assert "Window 1257+ sequence lock required before next phase assignment" in planning
    assert "Exact-token `rg` is only a schema/completion check" in planning
