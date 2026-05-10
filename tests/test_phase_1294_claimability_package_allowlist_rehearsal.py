from pathlib import Path

from ilc_core.rc.package_profile_ci_gate import build_package_profile_ci_audit
from ilc_core.rc.package_profiles import (
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
)
from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_claimability_package_allowlist_rehearsal_1294_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1294_g8_sidecar_public_safe_projection_schema_preflight.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1294_claimability_package_allowlist_rehearsal_walkthrough.md"
LOCK = "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"
SIDECAR_HELPER = "ilc_core/graph/sidecar_public_path_preflight.py"

PUBLIC_RC_EXCLUDE_HELPERS = (
    "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
    "ilc_core/ledger/claimability_proof_binding_runtime.py",
    "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
    "ilc_core/graph/sidecar_public_path_preflight.py",
)

PUBLIC_CLAIMABILITY_FILES = (
    "ilc_core/ledger/ecu_active_layer_runtime.py",
    "ilc_core/ledger/ecu_ilc_lifecycle_runtime.py",
    "ilc_core/ledger/exact_numeric.py",
    "ilc_core/protocol/public_init_admission_runtime.py",
    "ilc_core/protocol/public_receipt_runtime.py",
    "ilc_core/protocol/public_wallet_runtime.py",
)

REQUIRED_TOKENS = (
    "claimability_package_allowlist_rehearsal_phase_1294.v0.1",
    "claimability_package_allowlist_verdict_phase_1294=rehearsal_pass_export_blocked",
    "openclaw_skill_claimable_allowlist_rehearsed_phase_1294",
    "public_rc_exclude_helpers_excluded_from_export_phase_1294",
    "claimability_package_manifest_not_materialized_phase_1294",
    "source_allowlist_export_not_executed_phase_1294",
    "public_repository_publication_not_authorized_phase_1294",
    "public_package_publication_not_authorized_phase_1294",
    "public_claimability_activation_not_authorized_phase_1294",
    "public_rc_remains_blocked_after_phase_1294",
    "phase_1295_transport_principal_lifecycle_revocation_replay_preflight_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1294_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:4]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1294_prompt_uses_active_1289_1302_scope() -> None:
    prompt_path = ROOT / PROMPT
    prompt = read(PROMPT)

    assert validate(prompt_path) == []
    assert "Claimability Package Allowlist Rehearsal" in prompt
    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_public_rc_exclude_helper_promotion_removal_register_1293_v0.1.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt
    assert "sidecar_public_safe_projection_schema_preflight_phase_1294.v0.1" not in prompt


def test_phase_1294_active_lock_controls_allowlist_scope() -> None:
    lock = read(LOCK)
    guidance = read(GUIDANCE)
    spec = read(SPEC)

    assert "| 6 | 1294 | Claimability package allowlist rehearsal | SENSITIVE |" in lock
    assert "| 1294 | Claimability package allowlist rehearsal | SENSITIVE" in guidance
    assert "active 1289-1302" in spec


def test_phase_1294_package_profile_ci_remains_pass_without_public_claims() -> None:
    audit = build_package_profile_ci_audit()

    assert audit["audit_status"] == "pass"
    assert audit["failing_profiles"] == []
    assert tuple(audit["selected_profile_ids"]) == (
        PROFILE_OPENCLAW_SKILL_LOCAL,
        PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    )

    claimable = audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE]
    assert claimable["profile_status"] == "pass"
    assert claimable["claim_status"] == {
        "package_publication": False,
        "public_claimability_declared": True,
        "public_claimability_runtime_activated": False,
        "public_p2p_declared": False,
        "public_rc_claimed": False,
        "public_repository_publication": False,
    }

    spec = read(SPEC)
    assert "Package-profile CI" in spec
    assert "public_claimability_runtime_activated=False" in spec


def test_phase_1294_rehearsal_excludes_public_rc_exclude_helpers() -> None:
    spec = read(SPEC)
    audit = build_package_profile_ci_audit()
    claimable = audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE]
    ilc_logic_files = {
        record["path"]
        for record in claimable["surface_measurements"]["ilc_logic"]["files"]
    }

    assert SIDECAR_HELPER in ilc_logic_files
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in read(
        SIDECAR_HELPER
    )
    assert "raw measured `openclaw_skill_claimable` profile is not directly exportable" in spec

    for helper in PUBLIC_RC_EXCLUDE_HELPERS:
        assert helper in spec
        assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in read(
            helper
        )

    assert "exclude_by_public_rc_exclude_marker" in spec
    assert "public_rc_exclude_helpers_excluded_from_export_phase_1294" in spec


def test_phase_1294_claimability_files_are_candidate_hold_only() -> None:
    spec = read(SPEC)

    for path in PUBLIC_CLAIMABILITY_FILES:
        assert path in spec

    for phrase in (
        "candidate_hold_no_public_claimability_activation",
        "candidate_hold_no_wallet_spend_or_settlement_activation",
        "candidate_hold_no_public_endpoint_activation",
        "candidate_hold_no_public_verifier_service_activation",
        "candidate_hold_no_wallet_withdrawal_transfer_spend_activation",
    ):
        assert phrase in spec


def test_phase_1294_future_manifest_contract_is_non_executable_and_canonical() -> None:
    spec = read(SPEC)

    assert "Phase 1294 does not" in spec
    assert "claimability_package_manifest_not_materialized_phase_1294" in spec
    assert "json.dumps(..., sort_keys=True, allow_nan=False, separators=(\",\", \":\"))" in spec
    for field in (
        "`schema_version`",
        "`source_commit`",
        "`capsule`",
        "`mode`",
        "`profile_id`",
        "`include_rules`",
        "`exclude_rules`",
        "`review_required`",
        "`file_hashes`",
        "`non_claims`",
    ):
        assert field in spec


def test_phase_1294_non_claims_keep_export_and_activation_blocked() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "materialized export manifest",
            "source allowlist export",
            "public repository publication",
            "public package publication",
            "release artifact",
            "release-key generation",
            "helper promotion",
            "marker removal",
            "public claimability",
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


def test_phase_1294_updates_frontier_without_public_rc_claim() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)

    assert "Window 1289-1302 is OPEN through Phase 1294" in planning
    assert "Window 1289-1302 is open through Phase 1294" in capsule
    assert "Window 1289-1302 OPEN through Phase 1294" in roadmap
    assert "Phase 1295 is sensitive" in planning
    assert "Phase 1295 is sensitive" in capsule
    assert "Phase 1295 is the next sensitive phase" in roadmap

    assert "Window 1289-1302 is OPEN through Phase 1293" in planning
    assert "Window 1289-1302 is open through Phase 1293" in capsule
    assert "Window 1289-1302 OPEN through Phase 1293" in roadmap
    assert "public_rc_remains_blocked_after_phase_1294" in planning
    assert "public_rc_remains_blocked_after_phase_1294" in capsule
    assert "public_rc_remains_blocked_after_phase_1294" in roadmap


def test_phase_1294_graph_delta_records_docs_only_rehearsal() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for graph_delta in (
        "graph_delta=support_only:docs/specs/ilc_claimability_package_allowlist_rehearsal_1294_v0.1.md -> package/public_rc",
        "graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1294_g8_sidecar_public_safe_projection_schema_preflight.md -> planning/prompts",
        "graph_delta=support_tests_added:tests/test_phase_1294_claimability_package_allowlist_rehearsal.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1294_claimability_package_allowlist_rehearsal_walkthrough.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status
