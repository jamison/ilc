import json
from pathlib import Path

from ilc_core.rc.package_boundary_inventory import (
    DEFAULT_IMPORT_BOUNDARY_SPECS,
    build_import_boundary_inventory,
)
from ilc_core.rc.package_profile_ci_gate import (
    build_package_profile_ci_audit,
    export_package_profile_ci_audit_json,
    render_package_profile_ci_audit_markdown,
    validate_package_profile_ci_audit,
)
from ilc_core.rc.package_profiles import (
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
)


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1292_g8_claimability_package_profile_allowlist_rehearsal.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1292_claimability_package_profile_allowlist_rehearsal_walkthrough.md"
SIDE_CAR_HELPER = "ilc_core/graph/sidecar_public_path_preflight.py"
PACKAGE_AUDIT_JSON = "docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json"
PACKAGE_AUDIT_MD = "docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md"

REQUIRED_TOKENS = (
    "claimability_package_profile_allowlist_rehearsal_phase_1292.v0.1",
    "source_allowlist_export_not_executed_phase_1292",
    "public_package_publication_not_authorized_phase_1292",
    "public_rc_exclude_helpers_preserved_phase_1292",
    "public_rc_remains_blocked_after_phase_1292",
)

EXTRA_TOKENS = (
    "verifier_negative_path_corpus_recorded_phase_1292",
    "claimability_package_profile_boundary_verdict_phase_1292=pass_import_boundary_publication_blocked",
    "ilc_logic_network_import_boundary_repaired_phase_1292",
    "package_profile_ci_artifacts_refreshed_phase_1292",
    "phase_1293_public_rc_exclude_helper_promotion_removal_register_next",
)

HELPERS = (
    "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
    "ilc_core/ledger/claimability_proof_binding_runtime.py",
    "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
    "ilc_core/graph/sidecar_public_path_preflight.py",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1292_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in EXTRA_TOKENS:
        assert token in read(SPEC)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)


def test_phase_1292_prompt_references_active_1289_1302_window() -> None:
    prompt = read(PROMPT)

    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt


def test_phase_1292_package_profile_gate_passes_without_publication_claims() -> None:
    audit = validate_package_profile_ci_audit()

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
    assert "Package-profile CI pass is not source-publication authorization" in spec
    assert "Package-profile CI pass is not release artifact authorization" in spec


def test_phase_1292_repaired_ilc_logic_network_import_boundary() -> None:
    inventory = build_import_boundary_inventory(DEFAULT_IMPORT_BOUNDARY_SPECS["ilc_logic"])
    helper_source = read(SIDE_CAR_HELPER)

    assert inventory["status"] == "pass"
    assert inventory["violations"] == []
    assert "from ilc_core.network" not in helper_source
    assert "ilc_core.network.d2d" not in helper_source
    assert "ilc_logic_network_import_boundary_repaired_phase_1292" in read(SPEC)


def test_phase_1292_package_ci_artifacts_match_current_deterministic_builder() -> None:
    audit = build_package_profile_ci_audit()
    expected_json = export_package_profile_ci_audit_json(audit)
    expected_markdown = render_package_profile_ci_audit_markdown(audit) + "\n"

    assert json.loads(expected_json) == audit
    assert read(PACKAGE_AUDIT_JSON).strip() == expected_json
    assert read(PACKAGE_AUDIT_MD) == expected_markdown


def test_phase_1292_negative_path_corpus_records_denials() -> None:
    spec = read(SPEC)

    for phrase in (
        "Any activation flag is `true`",
        "Forged conversion receipt SHA-256",
        "Wrong root namespace",
        "Stale or mismatched settled runtime root",
        "Wallet-state root mismatch",
        "Latest balance receipt ref mismatch",
        "History digest mismatch",
        "Conversion key replay",
        "Missing replay/nullifier policy",
        "CDL-048 conversion deadline violation",
        "Python float",
        "`NaN`",
        "`Infinity`",
        "non-string JSON keys",
        "recursive cycles",
        "excessive traversal depth",
        "field-level disclosure schema",
        "`PUBLIC_RC_EXCLUDE`",
    ):
        assert phrase in spec


def test_phase_1292_public_rc_exclude_helpers_are_preserved() -> None:
    spec = read(SPEC)

    for helper in HELPERS:
        source = read(helper)
        assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in source
        assert helper in spec

    assert "files carrying `PUBLIC_RC_EXCLUDE` are excluded" in spec
    assert "phase_1293_public_rc_exclude_helper_promotion_removal_register_next" in spec


def test_phase_1292_non_claims_keep_public_rc_blocked() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "source allowlist export",
            "public repository publication",
            "public package publication",
            "release-key generation",
            "release envelope production",
            "public verifier service",
            "wallet withdrawal",
            "wallet transfer",
            "wallet spend",
            "ECU minting",
            "ILC settlement",
            "CDL-088",
            "Genesis Atlas mutation",
            "v0.2 signing",
        ):
            assert phrase in text


def test_phase_1292_updates_frontier_without_breaking_history() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)

    assert "Window 1289-1302 is OPEN through Phase 1292" in planning
    assert "Window 1289-1302 is open through Phase 1292" in capsule
    assert "Window 1289-1302 OPEN through Phase 1292" in roadmap
    assert "Phase 1293 is sensitive" in planning
    assert "Phase 1293 is sensitive" in capsule

    assert "Window 1289-1302 is OPEN through Phase 1291" in planning
    assert "Window 1289-1302 is open through Phase 1291" in capsule
    assert "Window 1289-1302 is open through Phase 1290" in capsule


def test_phase_1292_graph_delta_records_code_artifact_and_frontier_updates() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for graph_delta in (
        "graph_delta=load_bearing_code_changed:ilc_core/graph/sidecar_public_path_preflight.py -> sidecar/public_path/import_boundary",
        "graph_delta=support_artifact_changed:docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.json -> package/public_rc",
        "graph_delta=support_artifact_changed:docs/specs/ilc_gap14_package_profile_audit_1251_v0.1.md -> package/public_rc",
        "graph_delta=support_only:docs/specs/ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md -> package/public_rc",
        "graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1292_g8_claimability_package_profile_allowlist_rehearsal.md -> planning/prompts",
        "graph_delta=support_tests_added:tests/test_phase_1292_claimability_package_profile_allowlist_rehearsal.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1292_claimability_package_profile_allowlist_rehearsal_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    ):
        assert graph_delta in walkthrough
        assert graph_delta in status
