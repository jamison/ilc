from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1330_1342_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1330_window_1330_1342_sequence_lock_walkthrough.md"
CDL = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1330_1342_sequence_lock_committed",
    "window_1330_1342_sequence_lock_verdict=pass",
    "phase_1331_context_capsule_v5_55_release_candidate_freeze_next",
    "window_1330_1342_no_publication_signing_or_public_activation",
    "final_rc_signing_gate_sequence_locked_phase_1330",
    "human_question_escalation_required_for_uncertain_authority",
    "public_rc_remains_blocked_after_phase_1330",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1330_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SEQUENCE_LOCK)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1330_locks_all_window_phases_and_stops_after_1330() -> None:
    lock = read(SEQUENCE_LOCK)

    for phase in range(1330, 1343):
        assert f"| {phase} |" in lock

    assert "Phase 1331 is the next planned phase" in lock
    assert "NON-SENSITIVE docs/canon capsule freeze after Phase 1330" in lock
    assert "not executed by this lock" in lock
    assert "Execution stops after Phase 1330" in lock
    assert "Phases 1332 through 1342 remain SENSITIVE" in lock


def test_phase_1330_consumes_guidance_without_turning_plans_into_authority() -> None:
    lock = read(SEQUENCE_LOCK)
    guidance = read(GUIDANCE)
    planning = read(PLANNING)

    assert "window_1330_1342_candidate_grouping_consumed_by_phase_1330_sequence_lock" in guidance
    assert SEQUENCE_LOCK in planning
    assert GUIDANCE in planning
    assert "opens Window 1330-1342 through Phase 1330 only" in planning
    assert "Sequence-lock phase only" in lock


def test_phase_1330_preserves_high_authority_phrases() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "GO Phase 1335: authorize release key/envelope generation",
        "GO Phase 1340: authorize v0.2 signing ceremony",
        "GO Phase 1341: authorize public RC publication/claim",
        "Ordinary queue position",
    ):
        assert phrase in lock


def test_phase_1330_preserves_atlas_g_tail_routing() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "ATLAS-G-007 unsigned v0.2+ candidate regeneration",
        "ATLAS-G-008 Genesis/ILC/ECU/hypergraph non-excisability review packet",
        "ATLAS-G-009 signing root envelope prep, no signing",
        "ATLAS-G-010 v0.2 signing ceremony if explicitly authorized",
        "CCSS evidence cannot substitute",
        "ATLAS-G-009 prep alone must not produce a signature",
        "Phase 1341 must not claim signed Genesis/Atlas v0.2 unless Phase 1340 records a valid",
    ):
        assert phrase in lock


def test_phase_1330_stop_conditions_are_recorded() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Phase 1329 handoff is missing",
        "competing or superseding Window 1330+ sequence lock",
        "Publication, source export",
        "Identity bootstrap",
        "Counsel/IP/CLA/trademark/publication clearance",
        "Public serving",
        "Atlas-G tail work is omitted",
        "No stop condition was triggered during Phase 1330",
    ):
        assert phrase in lock


def test_phase_1330_preserves_public_rc_non_authorization() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "public RC claim",
        "source allowlist export execution",
        "clean materialized public tree production",
        "release artifact production",
        "release-key generation",
        "release envelope production",
        "release signing material generation",
        "signature production",
        "public claimability/API activation",
        "public verifier service",
        "public P2P",
        "public fetch serving",
        "public sidecar/projection serving",
        "non-loopback bind",
        "peer discovery",
        "Genesis Atlas mutation",
        "ATLAS-G-007",
        "v0.2 signing",
        "CDL-088 opening",
        "identity artifact creation",
        "wallet-facing withdrawal request",
        "ECU minting",
        "ILC settlement",
        "public confidential messaging",
        "public confidential coordination serving",
    ):
        assert phrase in lock


def test_phase_1330_identity_bootstrap_guard_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "identity_seed_commitment = sha384(\"ilc-seed-commit-v1:\" || identity_seed)",
        "sha384(identity_seed)",
        "dummy Agent Birth artifact creation",
        "Public bootstrap must also preserve the Genesis-rooted identity invariant",
        "Private graph content must not become identity-seed entropy or recovery material",
    ):
        assert phrase in lock


def test_phase_1330_discovery_and_human_escalation_are_recorded() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Known-token audit",
        "Concept-discovery search",
        "Contradiction and non-claim search",
        "Source expansion",
        "MemPalace tier_b planning query returned historical and stale planning hits only",
        "Exact-token `rg` remains only a schema and completion check",
        "token components, synonyms",
        "must stop and prompt the human reviewer",
        "default_to_no_authorization_when_canon_is_ambiguous",
    ):
        assert phrase in lock


def test_phase_1330_does_not_open_cdl_088_or_signing_authority() -> None:
    cdl = read(CDL)
    lock = read(SEQUENCE_LOCK)

    assert "| CDL-088 |" not in cdl
    assert "CDL-088 is not opened" in lock
    assert "CDL mutation" in lock
    assert "v0.2 signing" in lock
    assert "Genesis Atlas signing" in lock


def test_phase_1330_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_phase_1330_1342_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1330_window_1330_1342_sequence_lock.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1330_window_1330_1342_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in lock
        assert graph_delta in walkthrough
