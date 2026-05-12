from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SEQUENCE_LOCK = "docs/specs/ilc_phase_1317_1329_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1317_1329_candidate_phase_grouping_v0.1.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
WALKTHROUGH = "docs/phases/phase_1317_window_1317_1329_sequence_lock_walkthrough.md"
CDL = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "window_1317_1329_sequence_lock_committed",
    "window_1317_1329_sequence_lock_verdict=pass",
    "phase_1318_context_capsule_v5_54_refresh_next",
    "window_1317_1329_no_publication_signing_or_public_activation",
    "release_dry_run_private_only_sequence_locked_phase_1317",
    "ccss_tail_routed_without_atlas_g_compression_phase_1317",
    "human_question_escalation_required_for_uncertain_authority",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1317_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SEQUENCE_LOCK)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1317_locks_all_window_phases_and_stops_after_1317() -> None:
    lock = read(SEQUENCE_LOCK)

    for phase in range(1317, 1330):
        assert f"| {phase} |" in lock

    assert "Phase 1318 is the next planned phase" in lock
    assert "NON-SENSITIVE docs/canon refresh after Phase 1317" in lock
    assert "not executed by this lock" in lock
    assert "execution stops after Phase 1317" in lock


def test_phase_1317_consumes_guidance_without_turning_plans_into_authority() -> None:
    lock = read(SEQUENCE_LOCK)
    guidance = read(GUIDANCE)
    planning = read(PLANNING)

    assert "window_1317_1329_candidate_phase_grouping_consumed_by_phase_1317_sequence_lock" in guidance
    assert SEQUENCE_LOCK in planning
    assert GUIDANCE in planning
    assert "opens Window 1317-1329 through Phase 1317 only" in planning
    assert "This is a sequence-lock phase only" in lock


def test_phase_1317_preserves_release_dry_run_non_authorization() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Phase 1319 is locked as deterministic source allowlist export rehearsal only",
        "not source allowlist export execution",
        "zero exported `PUBLIC_RC_EXCLUDE` markers",
        "zero stripped-helper imports",
        "not source allowlist export execution, public source publication, package publication",
        "release manifest and signing procedure rehearsals only",
        "must not produce public release artifacts, release keys, release envelopes",
    ):
        assert phrase in lock


def test_phase_1317_preserves_ccss_and_atlas_g_split() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "ccss_tail_routed_without_atlas_g_compression_phase_1317",
        "Phases 1324-1328 are private/local Confidential Coordination Sidecar Suite",
        "not substitutes for ATLAS-G-007",
        "ATLAS-G-010",
        "Atlas-G tail work remains required before signing",
        "OpenClaw and NemoClaw remain harness/deployment targets",
        "They are not protocol substrates",
    ):
        assert phrase in lock


def test_phase_1317_stop_conditions_are_recorded() -> None:
    lock = read(SEQUENCE_LOCK)

    for phrase in (
        "Capsule v5.53 is missing",
        "Phase 1316 handoff is missing",
        "competing or superseding Window 1317+ sequence lock",
        "Atlas-G tail work is hidden inside CCSS phases 1324-1328",
        "DigitalOcean/OpenClaw/NemoClaw dry-run plans require public inbound ports",
        "No stop condition was triggered during Phase 1317",
    ):
        assert phrase in lock


def test_phase_1317_preserves_public_rc_non_authorization() -> None:
    lock = read(SEQUENCE_LOCK)

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
        "Genesis Atlas mutation/regeneration/signing",
        "v0.2 signing",
        "CDL-088 opening",
        "wallet-facing withdrawal request",
        "wallet-facing transfer request",
        "wallet-facing spend request",
        "ECU minting",
        "ILC settlement",
        "public confidential messaging",
        "public confidential coordination serving",
    ):
        assert phrase in lock


def test_phase_1317_discovery_and_human_escalation_are_recorded() -> None:
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


def test_phase_1317_does_not_open_cdl_088_or_signing_authority() -> None:
    cdl = read(CDL)
    lock = read(SEQUENCE_LOCK)

    assert "| CDL-088 |" not in cdl
    assert "CDL-088 is not opened" in lock
    assert "CDL mutation" in lock
    assert "v0.2 signing" in lock
    assert "Genesis Atlas signing" in lock


def test_phase_1317_graph_delta_is_recorded() -> None:
    lock = read(SEQUENCE_LOCK)
    walkthrough = read(WALKTHROUGH)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_phase_1317_1329_sequence_lock_v0.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_window_1317_1329_candidate_phase_grouping_v0.1.md -> planning/frontier",
        "graph_delta=support_tests_added:tests/test_phase_1317_window_1317_1329_sequence_lock.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1317_window_1317_1329_sequence_lock_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    ):
        assert graph_delta in lock
        assert graph_delta in walkthrough
