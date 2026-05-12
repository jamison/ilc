"""Phase 1308 deterministic PUBLIC_RC_EXCLUDE disposition inventory.

This module records planning metadata only. It does not remove markers, strip a
public export tree, promote helpers, publish packages, or activate public
claimability, transport, sidecar serving, wallet, ECU, or ILC paths.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ilc_core.epistemic.truth_primitive_submission_runtime import (
    AGENT_ISSUABLE_PRIMITIVES,
)


PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION = (
    "public_rc_exclude_helper_pruning_replacement_plan_phase_1308.v0.1"
)
PUBLIC_RC_EXCLUDE_HELPER_DISPOSITION_INVENTORY_RECORDED_TOKEN = (
    "public_rc_exclude_helper_disposition_inventory_recorded_phase_1308"
)
TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN = (
    "truth_primitive_sidecar_boundary_recorded_phase_1308"
)
HELPER_STRIPPING_NOT_EXECUTED_TOKEN = "helper_stripping_not_executed_phase_1308"
SOURCE_ALLOWLIST_EXPORT_NOT_EXECUTED_TOKEN = (
    "source_allowlist_export_not_executed_phase_1308"
)
PHASE_1309_NEXT_TOKEN = (
    "phase_1309_transport_principal_admission_sidecar_lifecycle_next"
)
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1308_TOKEN = (
    "public_rc_remains_blocked_after_phase_1308"
)

DISPOSITION_REPLACE_BEFORE_EXPORT = "replace_before_export"
DISPOSITION_STRIP_FROM_EXPORT = "strip_from_export"
DISPOSITION_DEFER_PUBLIC_RC = "defer_public_rc"

_ALLOWED_DISPOSITIONS = (
    DISPOSITION_REPLACE_BEFORE_EXPORT,
    DISPOSITION_STRIP_FROM_EXPORT,
    DISPOSITION_DEFER_PUBLIC_RC,
)
_PUBLIC_RC_EXCLUDE_MARKER = (
    "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface"
)
_REQUIRED_RUNTIME_HELPER_PATHS = (
    "ilc_core/graph/sidecar_public_path_preflight.py",
    "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
    "ilc_core/ledger/claimability_proof_binding_runtime.py",
    "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
)
_LOCAL_WIRING_MODES = ("in_process_import", "local_cli_subprocess")

_NON_AUTHORIZATION_BOUNDARY = (
    "no_public_rc_claim",
    "no_public_launch_claim",
    "no_source_allowlist_export_execution",
    "no_clean_public_tree_materialization",
    "no_public_repository_publication",
    "no_public_package_publication",
    "no_release_artifact_production",
    "no_release_key_generation",
    "no_release_envelope_production",
    "no_helper_promotion",
    "no_marker_removal",
    "no_helper_stripping_execution",
    "no_public_claimability_api_activation",
    "no_public_verifier_service",
    "no_public_claim_endpoint",
    "no_public_p2p_or_fetch_serving",
    "no_public_sidecar_or_projection_serving",
    "no_non_loopback_bind_or_listener",
    "no_genesis_atlas_mutation_or_signing",
    "no_v0_2_signing",
    "no_cdl_mutation_or_cdl_088_opening",
    "no_wallet_withdrawal_transfer_or_spend",
    "no_ecu_minting",
    "no_ilc_settlement",
    "no_public_confidential_messaging",
    "no_public_confidential_coordination_serving",
)

_RUNTIME_HELPERS = (
    {
        "affected_blocker": "sidecar_public_projection_serving_authority",
        "disposition": DISPOSITION_REPLACE_BEFORE_EXPORT,
        "earliest_followup_phase": "1311_1312_projection_sidecar_privacy_then_1333_export_gate",
        "helper_id": "sidecar_public_path_preflight",
        "marker": _PUBLIC_RC_EXCLUDE_MARKER,
        "path": "ilc_core/graph/sidecar_public_path_preflight.py",
        "phase_1293_register_decision": "keep_internal",
        "replacement_boundary": "local_graph_memory_projection_sidecar_public_safe_projection",
        "replacement_requirement": (
            "Implement a public-safe projection component and remove exported-code "
            "dependencies on the internal Phase 1278 preflight scaffold before any "
            "public source/package/release export."
        ),
        "surface": "graph_sidecar_public_path_preflight_scaffold",
    },
    {
        "affected_blocker": "claimability_conversion_receipt_public_contract",
        "disposition": DISPOSITION_REPLACE_BEFORE_EXPORT,
        "earliest_followup_phase": "1314_1315_value_path_preflight_then_1333_export_gate",
        "helper_id": "cdl048_conversion_sweeper_runtime",
        "marker": _PUBLIC_RC_EXCLUDE_MARKER,
        "path": "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
        "phase_1293_register_decision": "keep_internal",
        "replacement_boundary": "public_safe_claimability_receipt_contract",
        "replacement_requirement": (
            "Compile the local conversion-sweeper scaffold into a public-safe "
            "claimability receipt contract or keep the affected profile blocked; "
            "do not export the internal Phase 1274 helper."
        ),
        "surface": "claimability_conversion_sweeper_scaffold",
    },
    {
        "affected_blocker": "public_claimability_verifier_authority",
        "disposition": DISPOSITION_REPLACE_BEFORE_EXPORT,
        "earliest_followup_phase": "1305_1306_local_verifier_then_1314_1333_export_gate",
        "helper_id": "claimability_proof_binding_runtime",
        "marker": _PUBLIC_RC_EXCLUDE_MARKER,
        "path": "ilc_core/ledger/claimability_proof_binding_runtime.py",
        "phase_1293_register_decision": "keep_internal",
        "replacement_boundary": "offline_claimability_receipt_verifier_sidecar",
        "replacement_requirement": (
            "Use the graph-native offline verifier sidecar and later public verifier "
            "contract as the public-safe path; do not export the internal Phase 1275 "
            "proof-binding scaffold."
        ),
        "surface": "claimability_proof_binding_scaffold",
    },
    {
        "affected_blocker": "transport_principal_public_path_lifecycle_authority",
        "disposition": DISPOSITION_REPLACE_BEFORE_EXPORT,
        "earliest_followup_phase": "1309_1310_transport_admission_then_1313_1333_export_gate",
        "helper_id": "transport_principal_public_path_preflight",
        "marker": _PUBLIC_RC_EXCLUDE_MARKER,
        "path": "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
        "phase_1293_register_decision": "keep_internal",
        "replacement_boundary": "transport_principal_admission_sidecar",
        "replacement_requirement": (
            "Replace the stale Phase 1277 pre-ratification scaffold with a "
            "post-CDL-087 TransportPrincipal admission sidecar substrate before "
            "any public fetch/P2P or export claim."
        ),
        "surface": "transport_principal_public_path_preflight_scaffold",
    },
)

_DOCUMENT_AND_LEGACY_POLICY = (
    {
        "default_disposition": DISPOSITION_STRIP_FROM_EXPORT,
        "policy_id": "marked_public_rc_exclude_files",
        "reason": (
            "Any source, test, tool, or document carrying PUBLIC_RC_EXCLUDE is "
            "excluded unless a later explicit gate removes or supersedes the marker."
        ),
        "selector": "PUBLIC_RC_EXCLUDE",
    },
    {
        "default_disposition": DISPOSITION_STRIP_FROM_EXPORT,
        "policy_id": "private_phase_execution_docs",
        "reason": "Phase walkthroughs and prompt drafts are private execution history by default.",
        "selector": "docs/phases/ and docs/antigravity_tasks/",
    },
    {
        "default_disposition": DISPOSITION_STRIP_FROM_EXPORT,
        "policy_id": "patent_publication_sensitive_research",
        "reason": "Patent, counsel, and unpublished research material requires later review.",
        "selector": "docs/research/",
    },
    {
        "default_disposition": DISPOSITION_DEFER_PUBLIC_RC,
        "policy_id": "legacy_untagged_docs",
        "reason": (
            "Absence of PUBLIC_RC_EXCLUDE is not allowlist clearance; legacy docs "
            "need explicit manifest review before inclusion."
        ),
        "selector": "untagged legacy docs and roadmap fragments",
    },
)


def public_rc_exclude_required_tokens() -> list[str]:
    return [
        PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION,
        PUBLIC_RC_EXCLUDE_HELPER_DISPOSITION_INVENTORY_RECORDED_TOKEN,
        TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN,
        HELPER_STRIPPING_NOT_EXECUTED_TOKEN,
        SOURCE_ALLOWLIST_EXPORT_NOT_EXECUTED_TOKEN,
        PHASE_1309_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1308_TOKEN,
    ]


def build_public_rc_exclude_disposition_inventory() -> dict[str, Any]:
    """Build and validate the Phase 1308 disposition inventory."""

    inventory = {
        "allowed_dispositions": list(_ALLOWED_DISPOSITIONS),
        "document_and_legacy_policy": _document_policy_records(),
        "helper_disposition_inventory": _runtime_helper_records(),
        "non_authorization_boundary": list(_NON_AUTHORIZATION_BOUNDARY),
        "phase_1308_execution_state": {
            "clean_public_tree_materialized": False,
            "helper_promotion_authorized": False,
            "helper_stripping_executed": False,
            "marker_removal_authorized": False,
            "source_allowlist_export_executed": False,
        },
        "public_rc_claimed": False,
        "public_rc_remains_blocked": True,
        "required_tokens": public_rc_exclude_required_tokens(),
        "source_allowlist_export_executed": False,
        "truth_primitive_sidecar_boundary": _truth_primitive_boundary(),
        "version": PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION,
    }
    return validate_public_rc_exclude_disposition_inventory(inventory)


def validate_public_rc_exclude_disposition_inventory(
    inventory: Mapping[str, Any] | None = None,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    active = _raw_public_rc_exclude_disposition_inventory() if inventory is None else dict(inventory)
    if active.get("version") != PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION:
        raise ValueError("public_rc_exclude_disposition_version_invalid_phase_1308")
    if active.get("required_tokens") != public_rc_exclude_required_tokens():
        raise ValueError("public_rc_exclude_disposition_tokens_invalid_phase_1308")
    if active.get("allowed_dispositions") != list(_ALLOWED_DISPOSITIONS):
        raise ValueError("public_rc_exclude_disposition_set_invalid_phase_1308")
    if active.get("public_rc_claimed") is not False:
        raise ValueError("public_rc_claim_forbidden_phase_1308")
    if active.get("public_rc_remains_blocked") is not True:
        raise ValueError("public_rc_blocked_flag_required_phase_1308")
    if active.get("source_allowlist_export_executed") is not False:
        raise ValueError("source_allowlist_export_forbidden_phase_1308")
    if active.get("non_authorization_boundary") != list(_NON_AUTHORIZATION_BOUNDARY):
        raise ValueError("non_authorization_boundary_invalid_phase_1308")

    _validate_execution_state(active.get("phase_1308_execution_state"))
    helpers = _validate_helper_records(active.get("helper_disposition_inventory"))
    _validate_document_policy(active.get("document_and_legacy_policy"))
    _validate_truth_primitive_boundary(active.get("truth_primitive_sidecar_boundary"))
    if repo_root is not None:
        _validate_repo_markers(helpers, Path(repo_root))
    canonical_public_rc_exclude_disposition_inventory_json(active)
    return active


def canonical_public_rc_exclude_disposition_inventory_json(
    inventory: Mapping[str, Any],
) -> str:
    return json.dumps(inventory, allow_nan=False, separators=(",", ":"), sort_keys=True)


def export_public_rc_exclude_disposition_inventory_json(
    inventory: Mapping[str, Any] | None = None,
) -> str:
    active = (
        build_public_rc_exclude_disposition_inventory()
        if inventory is None
        else validate_public_rc_exclude_disposition_inventory(inventory)
    )
    return canonical_public_rc_exclude_disposition_inventory_json(active)


def _raw_public_rc_exclude_disposition_inventory() -> dict[str, Any]:
    return {
        "allowed_dispositions": list(_ALLOWED_DISPOSITIONS),
        "document_and_legacy_policy": _document_policy_records(),
        "helper_disposition_inventory": _runtime_helper_records(),
        "non_authorization_boundary": list(_NON_AUTHORIZATION_BOUNDARY),
        "phase_1308_execution_state": {
            "clean_public_tree_materialized": False,
            "helper_promotion_authorized": False,
            "helper_stripping_executed": False,
            "marker_removal_authorized": False,
            "source_allowlist_export_executed": False,
        },
        "public_rc_claimed": False,
        "public_rc_remains_blocked": True,
        "required_tokens": public_rc_exclude_required_tokens(),
        "source_allowlist_export_executed": False,
        "truth_primitive_sidecar_boundary": _truth_primitive_boundary(),
        "version": PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION,
    }


def _runtime_helper_records() -> list[dict[str, Any]]:
    records = []
    for helper in _RUNTIME_HELPERS:
        records.append(
            {
                **helper,
                "export_import_dependency_must_be_absent": True,
                "helper_promotion_authorized": False,
                "helper_stripping_executed": False,
                "marker_removal_authorized": False,
                "public_rc_blocker": True,
            }
        )
    return sorted(records, key=lambda item: item["path"])


def _document_policy_records() -> list[dict[str, Any]]:
    return sorted(
        ({**record, "source_allowlist_review_required": True} for record in _DOCUMENT_AND_LEGACY_POLICY),
        key=lambda item: item["policy_id"],
    )


def _truth_primitive_boundary() -> dict[str, Any]:
    return {
        "agent_issuable_primitives": sorted(AGENT_ISSUABLE_PRIMITIVES),
        "boundary_id": "truth_primitive_submission_sidecar_boundary",
        "commit_epoch_agent_submission_rejected": True,
        "consensus_only_primitives": ["commit.epoch"],
        "existing_runtime": "ilc_core/epistemic/truth_primitive_submission_runtime.py",
        "graph_persistence_authorized": False,
        "network_delivery_authorized": False,
        "public_api_enabled": False,
        "public_confidential_coordination_serving_enabled": False,
        "public_confidential_messaging_claimed": False,
        "public_sidecar_serving_enabled": False,
        "replacement_role": (
            "Local graph-native sidecar boundary for truth primitive submissions; "
            "public export must use this explicit boundary rather than importing "
            "internal helper scaffolds."
        ),
        "required_capabilities": [
            "assert_truth_submission",
            "validate_claim_submission",
            "contradict_assert_submission",
            "refute_claim_submission",
            "revise_assert_submission",
            "link_claim_submission",
        ],
        "required_token": TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN,
        "source_export_authorized": False,
        "wiring_modes": list(_LOCAL_WIRING_MODES),
    }


def _validate_execution_state(value: object) -> None:
    state = _require_mapping(value, token="execution_state_invalid_phase_1308")
    for key in (
        "clean_public_tree_materialized",
        "helper_promotion_authorized",
        "helper_stripping_executed",
        "marker_removal_authorized",
        "source_allowlist_export_executed",
    ):
        if state.get(key) is not False:
            raise ValueError("phase_1308_execution_forbidden")


def _validate_helper_records(value: object) -> list[dict[str, Any]]:
    helpers = _require_records(value, token="helper_inventory_invalid_phase_1308")
    paths = [_require_text(helper.get("path")) for helper in helpers]
    if tuple(paths) != _REQUIRED_RUNTIME_HELPER_PATHS:
        raise ValueError("helper_inventory_paths_invalid_phase_1308")
    ids = [_require_text(helper.get("helper_id")) for helper in helpers]
    if len(ids) != len(set(ids)):
        raise ValueError("helper_inventory_ids_invalid_phase_1308")
    for helper in helpers:
        disposition = _require_text(helper.get("disposition"))
        if disposition not in _ALLOWED_DISPOSITIONS:
            raise ValueError("helper_inventory_disposition_invalid_phase_1308")
        if disposition == DISPOSITION_REPLACE_BEFORE_EXPORT:
            _require_text(helper.get("replacement_boundary"))
            _require_text(helper.get("replacement_requirement"))
            _require_text(helper.get("earliest_followup_phase"))
        for key in (
            "export_import_dependency_must_be_absent",
            "public_rc_blocker",
        ):
            if helper.get(key) is not True:
                raise ValueError("helper_inventory_gate_flag_invalid_phase_1308")
        for key in (
            "helper_promotion_authorized",
            "helper_stripping_executed",
            "marker_removal_authorized",
        ):
            if helper.get(key) is not False:
                raise ValueError("helper_inventory_execution_forbidden_phase_1308")
        if helper.get("marker") != _PUBLIC_RC_EXCLUDE_MARKER:
            raise ValueError("helper_inventory_marker_invalid_phase_1308")
    return helpers


def _validate_document_policy(value: object) -> None:
    policies = _require_records(value, token="document_policy_invalid_phase_1308")
    policy_ids = [_require_text(policy.get("policy_id")) for policy in policies]
    if policy_ids != sorted(policy_ids) or len(policy_ids) != len(set(policy_ids)):
        raise ValueError("document_policy_ids_invalid_phase_1308")
    for policy in policies:
        disposition = _require_text(policy.get("default_disposition"))
        if disposition not in _ALLOWED_DISPOSITIONS:
            raise ValueError("document_policy_disposition_invalid_phase_1308")
        if policy.get("source_allowlist_review_required") is not True:
            raise ValueError("document_policy_review_required_phase_1308")
        _require_text(policy.get("selector"))
        _require_text(policy.get("reason"))


def _validate_truth_primitive_boundary(value: object) -> None:
    boundary = _require_mapping(value, token="truth_primitive_boundary_invalid_phase_1308")
    if boundary.get("required_token") != TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN:
        raise ValueError("truth_primitive_boundary_token_invalid_phase_1308")
    if boundary.get("agent_issuable_primitives") != sorted(AGENT_ISSUABLE_PRIMITIVES):
        raise ValueError("truth_primitive_boundary_primitives_invalid_phase_1308")
    if boundary.get("consensus_only_primitives") != ["commit.epoch"]:
        raise ValueError("truth_primitive_boundary_consensus_primitives_invalid_phase_1308")
    if boundary.get("commit_epoch_agent_submission_rejected") is not True:
        raise ValueError("truth_primitive_boundary_commit_epoch_invalid_phase_1308")
    for key in (
        "graph_persistence_authorized",
        "network_delivery_authorized",
        "public_api_enabled",
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_sidecar_serving_enabled",
        "source_export_authorized",
    ):
        if boundary.get(key) is not False:
            raise ValueError("truth_primitive_boundary_public_authority_forbidden_phase_1308")
    if boundary.get("wiring_modes") != list(_LOCAL_WIRING_MODES):
        raise ValueError("truth_primitive_boundary_wiring_invalid_phase_1308")
    _require_text(boundary.get("boundary_id"))
    _require_text(boundary.get("existing_runtime"))
    _require_text(boundary.get("replacement_role"))
    capabilities = _require_text_list(
        boundary.get("required_capabilities"),
        token="truth_primitive_boundary_capabilities_invalid_phase_1308",
    )
    if len(capabilities) != len(set(capabilities)):
        raise ValueError("truth_primitive_boundary_capabilities_invalid_phase_1308")


def _validate_repo_markers(helpers: list[Mapping[str, Any]], repo_root: Path) -> None:
    if not repo_root.exists() or not repo_root.is_dir():
        raise ValueError("repo_root_invalid_phase_1308")
    for helper in helpers:
        rel = Path(_require_text(helper.get("path")))
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("helper_path_invalid_phase_1308")
        source = (repo_root / rel).read_text(encoding="utf-8")
        if _require_text(helper.get("marker")) not in source:
            raise ValueError("helper_marker_missing_phase_1308")


def _require_records(value: object, *, token: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError(token)
    records: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(token)
        records.append(dict(item))
    return records


def _require_mapping(value: object, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(token)
    return value


def _require_text_list(value: object, *, token: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(token)
    return [_require_text(item) for item in value]


def _require_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("text_invalid_phase_1308")
    if len(value) > 4096:
        raise ValueError("text_too_large_phase_1308")
    return value


__all__ = [
    "DISPOSITION_DEFER_PUBLIC_RC",
    "DISPOSITION_REPLACE_BEFORE_EXPORT",
    "DISPOSITION_STRIP_FROM_EXPORT",
    "HELPER_STRIPPING_NOT_EXECUTED_TOKEN",
    "PHASE_1309_NEXT_TOKEN",
    "PUBLIC_RC_EXCLUDE_DISPOSITION_PLAN_VERSION",
    "PUBLIC_RC_EXCLUDE_HELPER_DISPOSITION_INVENTORY_RECORDED_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1308_TOKEN",
    "SOURCE_ALLOWLIST_EXPORT_NOT_EXECUTED_TOKEN",
    "TRUTH_PRIMITIVE_SIDECAR_BOUNDARY_RECORDED_TOKEN",
    "build_public_rc_exclude_disposition_inventory",
    "canonical_public_rc_exclude_disposition_inventory_json",
    "export_public_rc_exclude_disposition_inventory_json",
    "public_rc_exclude_required_tokens",
    "validate_public_rc_exclude_disposition_inventory",
]
