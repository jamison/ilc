from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1303_window_1303_1316_sequence_lock_walkthrough.md"
CDL = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1303_1316_sequence_lock_committed",
    "window_1303_1316_sequence_lock_verdict=pass",
    "phase_1304_context_capsule_v5_53_refresh_next",
    "window_1303_1316_no_public_rc_or_public_activation",
    "rust_public_p2p_substrate_gate_required_before_phase_1313_activation_candidate",
    "human_question_escalation_required_for_uncertain_authority",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1303_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SEQUENCE_LOCK)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1303_locks_all_window_phases_and_stops_after_1303() -> None:
    lock = read(SEQUENCE_LOCK)

    for phase in range(1303, 1317):
        assert f"| {phase} |" in lock

    assert "Phase 1304 is the next planned phase" in lock
    assert "NON-SENSITIVE docs/canon refresh after Phase 1303" in lock
    assert "not executed by this lock" in lock
    assert "execution stops after Phase 1303" in lock


def test_phase_1303_consumes_guidance_without_turning_plans_into_authority() -> None:
    lock = read(SEQUENCE_LOCK)
    guidance = read(GUIDANCE)
    planning = read(PLANNING)

    assert "window_1303_1316_candidate_phase_grouping_consumed_by_phase_1303_sequence_lock" in guidance
    assert SEQUENCE_LOCK in planning
    assert GUIDANCE in planning
    assert "opens Window 1303-1316 through Phase 1303 only" in planning
    assert "Window 1303-1316 is CLOSED / PASS" in planning
    assert "This is a sequence lock only" in lock


def test_phase_1303_preserves_phase_1313_readiness_only_boundary() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Phase 1313 is locked as readiness-only",
        "Public fetch/P2P readiness candidate, default off with no activation",
        "no public P2P, public fetch serving, listener, or public transport claim",
        "separate Rust public-P2P substrate ADR/integration gate",
    ):
        assert phrase in lock


def test_phase_1303_preserves_helper_stripping_as_planning_not_execution() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Phase 1308 is the first explicit `PUBLIC_RC_EXCLUDE` helper disposition",
        "replace_before_export",
        "strip_from_export",
        "defer_public_rc",
        "Phase 1308 must not execute source export",
        "helper promotion",
        "marker removal",
        "helper stripping",
        "Phase 1319",
        "Phase 1333",
    ):
        assert phrase in lock


def test_phase_1303_preserves_public_rc_non_authorization() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "public RC claim",
        "public claimability API activation",
        "public verifier service activation",
        "public P2P exposure",
        "public fetch serving",
        "public sidecar/projection serving",
        "source allowlist export execution",
        "release-key generation",
        "release envelope production",
        "Genesis Atlas mutation/regeneration/signing",
        "v0.2 signing",
        "CDL-088 opening",
        "wallet-facing withdrawal requests",
        "wallet-facing transfer requests",
        "wallet-facing spend requests",
        "ECU minting",
        "ILC settlement",
        "public confidential messaging",
        "public confidential coordination serving",
    ):
        assert phrase in lock


def test_phase_1303_discovery_and_human_escalation_are_recorded() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Known-token audit",
        "Concept-discovery search",
        "Contradiction and non-claim search",
        "Source expansion",
        "Exact-token `rg` remains only a schema and completion check",
        "token components, synonyms",
        "must stop and prompt the human reviewer",
        "default_to_no_authorization_when_canon_is_ambiguous",
    ):
        assert phrase in lock


def test_phase_1303_does_not_open_cdl_088_or_signing_authority() -> None:
    cdl = read(CDL)
    lock = read(SEQUENCE_LOCK)

    assert "| CDL-088 |" not in cdl
    assert "CDL-088 is not opened" in lock
    assert "CDL mutation" in lock
    assert "v0.2 signing" in lock
    assert "Genesis Atlas signing" in lock


def test_phase_1303_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_phase_1303_1316_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_window_1303_1316_candidate_phase_grouping_v0.1.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1303_window_1303_1316_sequence_lock.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1303_window_1303_1316_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in lock
        assert graph_delta in walkthrough
