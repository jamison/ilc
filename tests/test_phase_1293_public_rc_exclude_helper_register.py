from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_public_rc_exclude_helper_promotion_removal_register_1293_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1293_g8_transport_principal_lifecycle_activation_blocker_preflight.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1293_public_rc_exclude_helper_register_walkthrough.md"
LOCK = "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"

HELPERS = (
    "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
    "ilc_core/ledger/claimability_proof_binding_runtime.py",
    "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
    "ilc_core/graph/sidecar_public_path_preflight.py",
)

REQUIRED_TOKENS = (
    "public_rc_exclude_helper_promotion_removal_register_phase_1293.v0.1",
    "public_rc_exclude_helpers_keep_internal_phase_1293",
    "public_rc_exclude_helper_promotion_not_authorized_phase_1293",
    "public_rc_exclude_helper_removal_not_authorized_phase_1293",
    "public_rc_exclude_helper_replacement_required_before_public_export_phase_1293",
    "source_allowlist_export_not_executed_phase_1293",
    "public_package_publication_not_authorized_phase_1293",
    "public_rc_remains_blocked_after_phase_1293",
    "phase_1294_claimability_package_allowlist_rehearsal_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1293_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1293_prompt_uses_active_1289_1302_scope() -> None:
    prompt_path = ROOT / PROMPT
    prompt = read(PROMPT)

    assert validate(prompt_path) == []
    assert "PUBLIC_RC_EXCLUDE Helper Promotion/Removal Register" in prompt
    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt
    assert "transport_principal_lifecycle_activation_blocker_preflight_phase_1293.v0.1" not in prompt


def test_phase_1293_active_lock_controls_helper_register_scope() -> None:
    lock = read(LOCK)
    guidance = read(GUIDANCE)
    spec = read(SPEC)

    assert "| 5 | 1293 | PUBLIC_RC_EXCLUDE helper promotion/removal register | SENSITIVE |" in lock
    assert "| 1293 | PUBLIC_RC_EXCLUDE helper promotion/removal register | SENSITIVE" in guidance
    assert "active 1289-1302 lock and Capsule v5.52 control" in spec


def test_phase_1293_helper_register_keeps_all_helpers_internal() -> None:
    spec = read(SPEC)

    for helper in HELPERS:
        source = read(helper)
        assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in source
        assert helper in spec

    assert spec.count("| `ilc_core/") >= len(HELPERS)
    assert "No `remove` decision is made" in spec
    assert "No `promote` decision is made" in spec
    assert "No `replace_with_public_safe_module` decision is executed" in spec
    assert "public_rc_exclude_helper_register_verdict_phase_1293=all_current_helpers_keep_internal_no_promotion" in spec


def test_phase_1293_records_future_promotion_prerequisites() -> None:
    spec = read(SPEC)

    for phrase in (
        "public claimability authority",
        "verifier/API hardening",
        "replay/nullifier policy",
        "duplicate-claim registry",
        "TransportPrincipal public-path authority",
        "lifecycle/revocation/replay closure",
        "hostile-network admission/ban/rate/privacy closure",
        "sidecar public-safe projection schema",
        "bind/listener/peer-discovery authority",
        "release allowlist review",
    ):
        assert phrase in spec


def test_phase_1293_non_claims_keep_export_and_activation_blocked() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "helper promotion",
            "marker removal",
            "source allowlist export",
            "public repository publication",
            "public package publication",
            "release artifact",
            "release-key generation",
            "public verifier service",
            "public P2P",
            "public fetch serving",
            "public sidecar/projection serving",
            "wallet withdrawal",
            "wallet transfer",
            "wallet spend",
            "ECU minting",
            "ILC settlement",
            "CDL-088",
            "Genesis",
            "v0.2 signing",
        ):
            assert phrase in text


def test_phase_1293_updates_frontier_without_public_rc_claim() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)

    assert "Window 1289-1302 is OPEN through Phase 1293" in planning
    assert "Window 1289-1302 is open through Phase 1293" in capsule
    assert "Window 1289-1302 OPEN through Phase 1293" in roadmap
    assert "Phase 1294 is sensitive" in planning
    assert "Phase 1294 is sensitive" in capsule
    assert "Phase 1294 is the next sensitive phase" in roadmap

    assert "public RC remains blocked after Phase 1293" in planning
    assert "public_rc_remains_blocked_after_phase_1293" in capsule
    assert "public_rc_remains_blocked_after_phase_1293" in roadmap


def test_phase_1293_graph_delta_records_docs_only_register() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_public_rc_exclude_helper_promotion_removal_register_1293_v0.1.md -> package/public_rc",
        "graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1293_g8_transport_principal_lifecycle_activation_blocker_preflight.md -> planning/prompts",
        "graph_delta=support_tests_added:tests/test_phase_1293_public_rc_exclude_helper_register.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1293_public_rc_exclude_helper_register_walkthrough.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status
