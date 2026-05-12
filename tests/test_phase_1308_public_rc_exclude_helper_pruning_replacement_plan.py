from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from ilc_core.epistemic.truth_primitive_submission_runtime import (
    AGENT_ISSUABLE_PRIMITIVES,
)
from ilc_core.rc.public_rc_exclude_disposition import (
    DISPOSITION_DEFER_PUBLIC_RC,
    DISPOSITION_REPLACE_BEFORE_EXPORT,
    DISPOSITION_STRIP_FROM_EXPORT,
    HELPER_STRIPPING_NOT_EXECUTED_TOKEN,
    PHASE_1309_NEXT_TOKEN,
    PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION,
    PUBLIC_RC_EXCLUDE_HELPER_DISPOSITION_INVENTORY_RECORDED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1308_TOKEN,
    SOURCE_ALLOWLIST_EXPORT_NOT_EXECUTED_TOKEN,
    TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN,
    build_public_rc_exclude_disposition_inventory,
    export_public_rc_exclude_disposition_inventory_json,
    public_rc_exclude_required_tokens,
    validate_public_rc_exclude_disposition_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/rc/public_rc_exclude_disposition.py"
REGISTRY_PATH = ROOT / "ilc_core/sidecars/registry_manifest.py"
SPEC_PATH = ROOT / "docs/specs/ilc_public_rc_exclude_helper_pruning_replacement_plan_1308_v0.1.md"
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1308_public_rc_exclude_helper_pruning_replacement_plan_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PACKAGING_GATE_PATH = ROOT / "docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md"
SIDECAR_ARCH_PATH = ROOT / "docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md"

HELPER_PATHS = (
    "ilc_core/graph/sidecar_public_path_preflight.py",
    "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
    "ilc_core/ledger/claimability_proof_binding_runtime.py",
    "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
)
REQUIRED_TOKENS = [
    PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION,
    PUBLIC_RC_EXCLUDE_HELPER_DISPOSITION_INVENTORY_RECORDED_TOKEN,
    TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN,
    HELPER_STRIPPING_NOT_EXECUTED_TOKEN,
    SOURCE_ALLOWLIST_EXPORT_NOT_EXECUTED_TOKEN,
    PHASE_1309_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1308_TOKEN,
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1308_inventory_is_canonical_and_local_only() -> None:
    inventory = build_public_rc_exclude_disposition_inventory()
    exported_once = export_public_rc_exclude_disposition_inventory_json()
    exported_twice = export_public_rc_exclude_disposition_inventory_json()

    assert inventory["version"] == PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION
    assert inventory["required_tokens"] == REQUIRED_TOKENS
    assert public_rc_exclude_required_tokens() == REQUIRED_TOKENS
    assert inventory["allowed_dispositions"] == [
        DISPOSITION_REPLACE_BEFORE_EXPORT,
        DISPOSITION_STRIP_FROM_EXPORT,
        DISPOSITION_DEFER_PUBLIC_RC,
    ]
    assert inventory["public_rc_claimed"] is False
    assert inventory["public_rc_remains_blocked"] is True
    assert inventory["source_allowlist_export_executed"] is False
    assert inventory["phase_1308_execution_state"] == {
        "clean_public_tree_materialized": False,
        "helper_promotion_authorized": False,
        "helper_stripping_executed": False,
        "marker_removal_authorized": False,
        "source_allowlist_export_executed": False,
    }
    assert exported_once == exported_twice
    assert exported_once == json.dumps(
        json.loads(exported_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_phase_1308_helper_disposition_inventory_matches_current_marked_helpers() -> None:
    inventory = validate_public_rc_exclude_disposition_inventory(repo_root=ROOT)
    helpers = inventory["helper_disposition_inventory"]
    by_path = {helper["path"]: helper for helper in helpers}

    assert tuple(by_path) == HELPER_PATHS
    for path in HELPER_PATHS:
        source = _read(ROOT / path)
        helper = by_path[path]
        assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in source
        assert helper["marker"] in source
        assert helper["phase_1293_register_decision"] == "keep_internal"
        assert helper["disposition"] == DISPOSITION_REPLACE_BEFORE_EXPORT
        assert helper["helper_promotion_authorized"] is False
        assert helper["marker_removal_authorized"] is False
        assert helper["helper_stripping_executed"] is False
        assert helper["export_import_dependency_must_be_absent"] is True
        assert helper["public_rc_blocker"] is True

    assert by_path[
        "ilc_core/ledger/claimability_proof_binding_runtime.py"
    ]["replacement_boundary"] == "offline_claimability_receipt_verifier_sidecar"
    assert by_path[
        "ilc_core/network/d2d/transport_principal_public_path_preflight.py"
    ]["replacement_boundary"] == "transport_principal_admission_sidecar"


def test_phase_1308_truth_primitive_boundary_is_graph_native_and_not_public_serving() -> None:
    boundary = build_public_rc_exclude_disposition_inventory()[
        "truth_primitive_sidecar_boundary"
    ]

    assert boundary["required_token"] == TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN
    assert boundary["agent_issuable_primitives"] == sorted(AGENT_ISSUABLE_PRIMITIVES)
    assert boundary["consensus_only_primitives"] == ["commit.epoch"]
    assert boundary["commit_epoch_agent_submission_rejected"] is True
    assert boundary["wiring_modes"] == ["in_process_import", "local_cli_subprocess"]
    for key in (
        "graph_persistence_authorized",
        "network_delivery_authorized",
        "public_api_enabled",
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_sidecar_serving_enabled",
        "source_export_authorized",
    ):
        assert boundary[key] is False

    registry = build_public_rc_exclude_disposition_inventory()
    assert "truth_primitive_sidecar_boundary_recorded_phase_1308" in json.dumps(
        registry,
        allow_nan=False,
        sort_keys=True,
    )
    assert "truth_primitive_sidecar_boundary_recorded_phase_1308" in _read(REGISTRY_PATH)


def test_phase_1308_document_policy_preserves_exclude_by_default_materialization_rule() -> None:
    policies = build_public_rc_exclude_disposition_inventory()["document_and_legacy_policy"]
    by_id = {policy["policy_id"]: policy for policy in policies}

    assert by_id["marked_public_rc_exclude_files"]["default_disposition"] == (
        DISPOSITION_STRIP_FROM_EXPORT
    )
    assert by_id["private_phase_execution_docs"]["selector"] == (
        "docs/phases/ and docs/antigravity_tasks/"
    )
    assert by_id["patent_publication_sensitive_research"]["default_disposition"] == (
        DISPOSITION_STRIP_FROM_EXPORT
    )
    assert by_id["legacy_untagged_docs"]["default_disposition"] == (
        DISPOSITION_DEFER_PUBLIC_RC
    )
    for policy in policies:
        assert policy["source_allowlist_review_required"] is True


def test_phase_1308_inventory_validation_fails_closed_on_public_or_execution_mutations() -> None:
    inventory = build_public_rc_exclude_disposition_inventory()

    public_claim = copy.deepcopy(inventory)
    public_claim["public_rc_claimed"] = True
    with pytest.raises(ValueError, match="public_rc_claim_forbidden"):
        validate_public_rc_exclude_disposition_inventory(public_claim)

    source_export = copy.deepcopy(inventory)
    source_export["phase_1308_execution_state"]["source_allowlist_export_executed"] = True
    with pytest.raises(ValueError, match="phase_1308_execution_forbidden"):
        validate_public_rc_exclude_disposition_inventory(source_export)

    marker_removed = copy.deepcopy(inventory)
    marker_removed["helper_disposition_inventory"][0]["marker"] = "removed"
    with pytest.raises(ValueError, match="helper_inventory_marker_invalid"):
        validate_public_rc_exclude_disposition_inventory(marker_removed)

    public_truth = copy.deepcopy(inventory)
    public_truth["truth_primitive_sidecar_boundary"]["public_api_enabled"] = True
    with pytest.raises(ValueError, match="truth_primitive_boundary_public_authority_forbidden"):
        validate_public_rc_exclude_disposition_inventory(public_truth)


def test_phase_1308_source_has_no_public_server_or_randomness_surface() -> None:
    tree = ast.parse(_read(MODULE_PATH))
    forbidden_import_roots = {
        "aiohttp",
        "datetime",
        "fastapi",
        "http",
        "random",
        "requests",
        "socket",
        "time",
        "urllib",
        "uvicorn",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_import_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_import_roots
        if isinstance(node, ast.Assert):
            raise AssertionError("assert forbidden in Phase 1308 RC disposition module")


def test_phase_1308_docs_status_and_frontier_record_tokens_and_nonclaims() -> None:
    corpus = "\n".join(
        _read(path)
        for path in (
            MODULE_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            PACKAGING_GATE_PATH,
            SIDECAR_ARCH_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for phrase in (
        "Window 1303-1316 is OPEN through Phase 1308",
        "Phase 1309 is sensitive and requires explicit `GO Phase 1309`",
        "helper promotion",
        "marker removal",
        "helper stripping",
        "source allowlist export",
        "clean public tree",
        "public verifier service",
        "public P2P",
        "public sidecar/projection serving",
        "wallet withdrawal",
        "ECU minting",
        "ILC settlement",
    ):
        assert phrase in corpus
