"""Phase 1307 deterministic graph-native sidecar registry manifest.

The registry is local/package metadata. It does not create a server, listener,
public sidecar endpoint, package publication, source export, wallet action, ECU
mint, ILC settlement, or public confidential messaging authority.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ilc_core.rc.package_profiles import (
    PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    profile_manifest,
    validate_all_package_profiles,
)
from ilc_core.sidecars.claimability_receipt_verifier import (
    claimability_receipt_verifier_manifest,
)
from ilc_core.sidecars.confidential_coordination_capability import (
    ccss_002_capability_membership_boundary_manifest,
)
from ilc_core.sidecars.confidential_coordination_sealed_sender import (
    ccss_003_sealed_sender_local_delivery_manifest,
)
from ilc_core.sidecars.confidential_coordination_shard import (
    ccss_001_private_gated_shard_manifest,
)
from ilc_core.sidecars.local_graph_memory_projection import (
    local_graph_memory_projection_sidecar_manifest,
)
from ilc_core.sidecars.public_fetch_p2p_readiness import (
    public_fetch_p2p_readiness_candidate_manifest,
)
from ilc_core.sidecars.transport_principal_admission import (
    transport_principal_admission_sidecar_manifest,
)
from ilc_core.sidecars.value_path_activation_boundary_preflight import (
    value_path_activation_boundary_preflight_manifest,
)
from ilc_core.sidecars.wallet_action_semantics_preflight import (
    wallet_action_semantics_preflight_manifest,
)


SIDECAR_REGISTRY_MANIFEST_VERSION = "graph_native_sidecar_registry_manifest_phase_1307.v0.1"
SIDECAR_MANIFEST_DETERMINISTIC_PROFILE_DECLARED_TOKEN = (
    "sidecar_manifest_deterministic_profile_declared_phase_1307"
)
OPENCLAW_COMPATIBLE_LOCAL_BRIDGE_PROFILE_DECLARED_TOKEN = (
    "openclaw_compatible_local_bridge_profile_declared_phase_1307"
)
CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW_PROFILE_DECLARED_TOKEN = (
    "confidential_coordination_local_preview_profile_declared_phase_1307"
)
PACKAGE_PROFILE_INTEGRITY_HARDENED_TOKEN = (
    "package_profile_integrity_hardened_phase_1307"
)
PHASE_1308_NEXT_TOKEN = "phase_1308_public_rc_exclude_helper_pruning_replacement_plan_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1307_TOKEN = (
    "public_rc_remains_blocked_after_phase_1307"
)

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_JSON_BYTES = 10_000_000
_MAX_PROTOCOL_INT = 1_000_000_000_000

_PRIVATE_WIRING_MODES = (
    "in_process_import",
    "local_cli_subprocess",
    "private_loopback",
    "private_overlay",
)
_LOCAL_OPENCLAW_WIRING_MODES = (
    "in_process_import",
    "local_cli_subprocess",
    "private_loopback",
)

_SOURCE_ALLOWLIST_DISPOSITIONS = (
    "compile_into_contract",
    "retain_as_public_metadata",
    "retain_internal_only",
    "strip_from_export",
    "replace_before_export",
)

_NON_AUTHORIZATION_BOUNDARY = (
    "no_public_rc_claim",
    "no_source_allowlist_export_execution",
    "no_public_repository_publication",
    "no_public_package_publication",
    "no_release_artifact_production",
    "no_release_key_generation",
    "no_release_envelope_production",
    "no_public_claimability_api_activation",
    "no_public_verifier_service",
    "no_public_claim_endpoint",
    "no_public_p2p_or_fetch_serving",
    "no_public_sidecar_or_projection_serving",
    "no_non_loopback_bind_or_listener",
    "no_helper_promotion_marker_removal_or_stripping",
    "no_genesis_atlas_mutation_or_signing",
    "no_v0_2_signing",
    "no_cdl_mutation_or_cdl_088_opening",
    "no_wallet_withdrawal_transfer_or_spend",
    "no_wallet_signing_or_ledger_write",
    "no_value_path_activation",
    "no_ecu_minting",
    "no_ilc_settlement",
    "no_public_confidential_messaging",
    "no_public_confidential_coordination_serving",
)

_SIDECAR_DEFINITIONS = (
    {
        "authority_gate": "phase_1307_local_package_metadata_only",
        "component": "graph_native_sidecar_registry_manifest",
        "implementation_status": "implemented_phase_1307",
        "public_serving_enabled": False,
        "required_capabilities": (
            "deterministic_manifest",
            "package_profile_binding",
            "explicit_non_claims",
        ),
        "sidecar_id": "sidecar_registry_manifest",
        "wiring_modes": _LOCAL_OPENCLAW_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1305_1306_local_verifier_only",
        "component": "offline_claimability_receipt_verifier_sidecar",
        "implementation_status": "implemented_phase_1305_hardened_phase_1306",
        "public_serving_enabled": False,
        "required_capabilities": (
            "canonical_receipt_verification",
            "proof_binding_hash_check",
            "exact_numeric_guard",
            "activation_flag_fail_closed",
        ),
        "sidecar_id": "offline_claimability_receipt_verifier",
        "wiring_modes": ("in_process_import", "local_cli_subprocess"),
    },
    {
        "authority_gate": "phase_1308_boundary_recorded_public_export_still_blocked",
        "component": "graph_native_sidecar_registry_manifest",
        "implementation_status": "boundary_recorded_phase_1308_no_public_serving",
        "public_serving_enabled": False,
        "required_capabilities": (
            "assert_truth_submission",
            "validate_claim_submission",
            "contradict_refute_revise_link_submission",
            "truth_primitive_sidecar_boundary_recorded_phase_1308",
        ),
        "sidecar_id": "truth_primitive_submission_boundary",
        "wiring_modes": ("in_process_import", "local_cli_subprocess"),
    },
    {
        "authority_gate": "phase_1309_1310_local_lifecycle_substrate_public_path_blocked",
        "component": "transport_principal_identity",
        "implementation_status": "lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310",
        "public_serving_enabled": False,
        "required_capabilities": (
            "credential_lifecycle",
            "revocation_registry",
            "replay_cache",
            "admission_ban_rate_privacy_policy",
            "transport_principal_lifecycle_policy_local_substrate_phase_1309",
            "transport_principal_revocation_replay_tests_hardened_phase_1310",
            "admission_ban_rate_privacy_tests_hardened_phase_1310",
        ),
        "sidecar_id": "transport_principal_admission",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1311_1312_local_projection_substrate_privacy_hardened_public_serving_blocked",
        "component": "local_sidecar_query_runtime",
        "implementation_status": "local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312",
        "public_serving_enabled": False,
        "required_capabilities": (
            "bounded_local_projection",
            "public_safe_field_filtering",
            "private_shard_header_projection",
            "encrypted_coordination_reference_projection",
            "public_safe_projection_implementation_local_only_phase_1311",
            "confidential_coordination_projection_reference_local_only_phase_1311",
            "projection_privacy_filters_hardened_phase_1312",
            "confidential_coordination_projection_non_leakage_tests_phase_1312",
            "public_sidecar_projection_serving_not_enabled_phase_1312",
        ),
        "sidecar_id": "local_graph_memory_projection",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1313_default_off_readiness_only_rust_public_p2p_gate_required",
        "component": "public_fetch_p2p_readiness_candidate",
        "implementation_status": "readiness_candidate_recorded_phase_1313_default_off",
        "public_serving_enabled": False,
        "required_capabilities": (
            "rust_public_p2p_substrate_gate_status_recorded_phase_1313",
            "public_p2p_default_off_phase_1313",
            "public_fetch_serving_default_off_phase_1313",
            "transport_public_path_activation_not_authorized_phase_1313",
        ),
        "sidecar_id": "public_fetch_p2p_readiness_candidate",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1314_preflight_only_wallet_actions_blocked",
        "component": "wallet_action_semantics_preflight",
        "implementation_status": "preflight_recorded_phase_1314_no_wallet_action_activation",
        "public_serving_enabled": False,
        "required_capabilities": (
            "wallet_withdrawal_transfer_spend_not_activated_phase_1314",
            "wallet_signing_ledger_write_not_authorized_phase_1314",
            "public_claimability_user_action_boundary_recorded_phase_1314",
            "phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next",
            "public_rc_remains_blocked_after_phase_1314",
        ),
        "sidecar_id": "wallet_action_semantics_preflight",
        "wiring_modes": ("in_process_import", "local_cli_subprocess"),
    },
    {
        "authority_gate": "phase_1315_preflight_only_value_path_activation_blocked",
        "component": "value_path_activation_boundary_preflight",
        "implementation_status": "preflight_recorded_phase_1315_no_ecu_mint_or_ilc_settlement_activation",
        "public_serving_enabled": False,
        "required_capabilities": (
            "ecu_minting_not_authorized_phase_1315",
            "ilc_settlement_not_authorized_phase_1315",
            "value_path_activation_boundary_recorded_phase_1315",
            "phase_1316_window_1303_1316_closure_audit_next",
            "public_rc_remains_blocked_after_phase_1315",
        ),
        "sidecar_id": "value_path_activation_boundary_preflight",
        "wiring_modes": ("in_process_import", "local_cli_subprocess"),
    },
    {
        "authority_gate": "phase_1324_1329_required_for_runtime_dry_run",
        "component": "confidential_coordination_local_preview_profile",
        "implementation_status": "profile_declared_phase_1307",
        "public_serving_enabled": False,
        "required_capabilities": (
            "private_gated_shard_header",
            "capability_membership_reference",
            "sealed_sender_boundary",
            "gossip_jitter_cover_policy_boundary",
        ),
        "sidecar_id": "confidential_coordination_local_preview",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1324_private_local_contract_only",
        "component": "ccss_001_private_gated_shard_contract",
        "implementation_status": "contract_recorded_phase_1324_no_public_serving",
        "public_serving_enabled": False,
        "required_capabilities": (
            "PrivateShardRef",
            "EncryptedCoordinationNodeEnvelope",
            "ShardHeaderProjection",
            "PromotionEvidenceRef",
            "DisclosureDenial",
        ),
        "sidecar_id": "confidential_coordination_private_gated_shard",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1325_private_local_contract_only",
        "component": "ccss_002_capability_membership_boundary",
        "implementation_status": "contract_recorded_phase_1325_no_public_serving",
        "public_serving_enabled": False,
        "required_capabilities": (
            "CapabilityPolicyRef",
            "MembershipBoundaryRef",
            "CapabilityGrantRef",
            "CapabilityRevocationRef",
            "ZKMembershipInterfaceRef",
            "local_access_state_fail_closed",
        ),
        "sidecar_id": "confidential_coordination_capability_membership_boundary",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1326_private_local_contract_only",
        "component": "ccss_003_sealed_sender_local_delivery_boundary",
        "implementation_status": "contract_recorded_phase_1326_no_public_serving",
        "public_serving_enabled": False,
        "required_capabilities": (
            "SealedPayloadClassRef",
            "SealedLocalDeliveryIntent",
            "SealedLocalDeliveryReceipt",
            "SealedDeliveryProjection",
            "fixed_size_payload_boundary",
            "sealed_delivery_state_fail_closed",
        ),
        "sidecar_id": "confidential_coordination_sealed_sender_local_delivery",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
    {
        "authority_gate": "phase_1323_1328_private_dry_run_before_public_claim",
        "component": "openclaw_compatible_local_bridge",
        "implementation_status": "profile_declared_phase_1307",
        "public_serving_enabled": False,
        "required_capabilities": (
            "harness_agnostic_import",
            "local_cli_subprocess",
            "private_loopback_or_overlay_when_authorized_by_harness",
        ),
        "sidecar_id": "openclaw_nemoclaw_local_bridge",
        "wiring_modes": _PRIVATE_WIRING_MODES,
    },
)


def sidecar_registry_required_tokens() -> list[str]:
    return [
        SIDECAR_REGISTRY_MANIFEST_VERSION,
        SIDECAR_MANIFEST_DETERMINISTIC_PROFILE_DECLARED_TOKEN,
        OPENCLAW_COMPATIBLE_LOCAL_BRIDGE_PROFILE_DECLARED_TOKEN,
        CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW_PROFILE_DECLARED_TOKEN,
        PACKAGE_PROFILE_INTEGRITY_HARDENED_TOKEN,
        PHASE_1308_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1307_TOKEN,
    ]


def build_sidecar_registry_manifest() -> dict[str, Any]:
    """Build and validate the deterministic local sidecar registry manifest."""

    validate_all_package_profiles()
    sidecars = sorted(
        (_sidecar_record(record) for record in _SIDECAR_DEFINITIONS),
        key=lambda item: item["sidecar_id"],
    )
    profiles = sorted(
        [
            _profile_record(
                profile_id="openclaw_compatible_local_bridge",
                package_profile_id=PROFILE_OPENCLAW_SKILL_LOCAL,
                required_sidecars=(
                    "sidecar_registry_manifest",
                    "openclaw_nemoclaw_local_bridge",
                ),
                optional_sidecars=(
                    "offline_claimability_receipt_verifier",
                    "truth_primitive_submission_boundary",
                    "local_graph_memory_projection",
                ),
                wiring_modes=_LOCAL_OPENCLAW_WIRING_MODES,
                public_claimability_runtime_activated=False,
            ),
            _profile_record(
                profile_id="openclaw_claimable_local_bridge",
                package_profile_id=PROFILE_OPENCLAW_SKILL_CLAIMABLE,
                required_sidecars=(
                    "sidecar_registry_manifest",
                    "offline_claimability_receipt_verifier",
                    "openclaw_nemoclaw_local_bridge",
                    "value_path_activation_boundary_preflight",
                    "wallet_action_semantics_preflight",
                ),
                optional_sidecars=(
                    "truth_primitive_submission_boundary",
                    "local_graph_memory_projection",
                    "transport_principal_admission",
                ),
                wiring_modes=_LOCAL_OPENCLAW_WIRING_MODES,
                public_claimability_runtime_activated=False,
            ),
            _profile_record(
                profile_id=PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
                package_profile_id=PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
                required_sidecars=(
                    "sidecar_registry_manifest",
                    "confidential_coordination_capability_membership_boundary",
                    "confidential_coordination_private_gated_shard",
                    "confidential_coordination_sealed_sender_local_delivery",
                    "confidential_coordination_local_preview",
                    "local_graph_memory_projection",
                    "openclaw_nemoclaw_local_bridge",
                ),
                optional_sidecars=(
                    "transport_principal_admission",
                    "truth_primitive_submission_boundary",
                ),
                wiring_modes=_PRIVATE_WIRING_MODES,
                public_claimability_runtime_activated=False,
            ),
        ],
        key=lambda item: item["profile_id"],
    )
    manifest = {
        "deterministic_manifest": True,
        "local_package_metadata_only": True,
        "non_authorization_boundary": list(_NON_AUTHORIZATION_BOUNDARY),
        "package_profile_integrity": {
            "claimable_profile_requires_offline_verifier": True,
            "confidential_coordination_capability_manifest": ccss_002_capability_membership_boundary_manifest(),
            "confidential_coordination_sealed_sender_manifest": ccss_003_sealed_sender_local_delivery_manifest(),
            "confidential_coordination_shard_manifest": ccss_001_private_gated_shard_manifest(),
            "confidential_coordination_profile_is_private_local_only": True,
            "local_graph_memory_projection_sidecar_manifest": local_graph_memory_projection_sidecar_manifest(),
            "offline_claimability_verifier_manifest": claimability_receipt_verifier_manifest(),
            "openclaw_nemoclaw_are_hosts_not_protocol_substrates": True,
            "public_claimability_runtime_activation_authorized": False,
            "public_fetch_p2p_readiness_candidate_manifest": public_fetch_p2p_readiness_candidate_manifest(),
            "public_p2p_activation_authorized": False,
            "transport_principal_admission_sidecar_manifest": transport_principal_admission_sidecar_manifest(),
            "value_path_activation_boundary_preflight_manifest": value_path_activation_boundary_preflight_manifest(),
            "wallet_action_semantics_preflight_manifest": wallet_action_semantics_preflight_manifest(),
        },
        "profiles": profiles,
        "public_confidential_coordination_serving_enabled": False,
        "public_confidential_messaging_claimed": False,
        "public_package_publication_authorized": False,
        "public_rc_claimed": False,
        "public_serving_enabled": False,
        "required_tokens": sidecar_registry_required_tokens(),
        "sidecars": sidecars,
        "source_allowlist_readiness": {
            "clean_public_tree_materialized": False,
            "deterministic_scaffold_dispositions": list(_SOURCE_ALLOWLIST_DISPOSITIONS),
            "legacy_untagged_docs_review_required": True,
            "marker_scan_required_before_export": True,
            "phase_1308_public_rc_exclude_disposition_required": True,
            "source_allowlist_export_executed": False,
        },
        "version": SIDECAR_REGISTRY_MANIFEST_VERSION,
    }
    return validate_sidecar_registry_manifest(manifest)


def validate_sidecar_registry_manifest(manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active = build_sidecar_registry_manifest() if manifest is None else dict(manifest)
    if active.get("version") != SIDECAR_REGISTRY_MANIFEST_VERSION:
        raise ValueError("sidecar_registry_manifest_version_invalid_phase_1307")
    if active.get("required_tokens") != sidecar_registry_required_tokens():
        raise ValueError("sidecar_registry_manifest_required_tokens_invalid_phase_1307")
    for key in (
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_package_publication_authorized",
        "public_rc_claimed",
        "public_serving_enabled",
    ):
        _require_false(active.get(key), token="sidecar_registry_public_authority_forbidden_phase_1307")
    if active.get("deterministic_manifest") is not True:
        raise ValueError("sidecar_registry_manifest_not_deterministic_phase_1307")
    if active.get("local_package_metadata_only") is not True:
        raise ValueError("sidecar_registry_manifest_not_local_metadata_phase_1307")
    if active.get("non_authorization_boundary") != list(_NON_AUTHORIZATION_BOUNDARY):
        raise ValueError("sidecar_registry_non_authorization_boundary_invalid_phase_1307")
    _validate_package_profile_integrity(active.get("package_profile_integrity"))

    sidecars = _require_records(active.get("sidecars"), token="sidecar_registry_sidecars_invalid_phase_1307")
    sidecar_ids = _ids(sidecars, "sidecar_id", token="sidecar_registry_sidecar_id_invalid_phase_1307")
    for sidecar in sidecars:
        _validate_sidecar_record(sidecar)

    profiles = _require_records(active.get("profiles"), token="sidecar_registry_profiles_invalid_phase_1307")
    _ids(profiles, "profile_id", token="sidecar_registry_profile_id_invalid_phase_1307")
    for profile in profiles:
        _validate_profile_record(profile, sidecar_ids=sidecar_ids)

    source = dict(
        _require_mapping(
            active.get("source_allowlist_readiness"),
            token="sidecar_registry_source_allowlist_invalid_phase_1307",
        )
    )
    if source.get("source_allowlist_export_executed") is not False:
        raise ValueError("sidecar_registry_source_allowlist_export_forbidden_phase_1307")
    if source.get("clean_public_tree_materialized") is not False:
        raise ValueError("sidecar_registry_clean_public_tree_forbidden_phase_1307")
    for key in (
        "legacy_untagged_docs_review_required",
        "marker_scan_required_before_export",
        "phase_1308_public_rc_exclude_disposition_required",
    ):
        if source.get(key) is not True:
            raise ValueError("sidecar_registry_source_allowlist_readiness_invalid_phase_1307")
    if source.get("deterministic_scaffold_dispositions") != list(_SOURCE_ALLOWLIST_DISPOSITIONS):
        raise ValueError("sidecar_registry_scaffold_dispositions_invalid_phase_1307")

    canonical_sidecar_registry_manifest_json(active)
    return active


def canonical_sidecar_registry_manifest_json(manifest: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(manifest)
    canonical = json.dumps(manifest, allow_nan=False, separators=(",", ":"), sort_keys=True)
    if len(canonical.encode("utf-8")) > _MAX_CANONICAL_JSON_BYTES:
        raise ValueError("sidecar_registry_payload_size_exceeded_phase_1307")
    return canonical


def export_sidecar_registry_manifest_json(manifest: Mapping[str, Any] | None = None) -> str:
    active = build_sidecar_registry_manifest() if manifest is None else validate_sidecar_registry_manifest(manifest)
    return canonical_sidecar_registry_manifest_json(active)


def _sidecar_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "authority_gate": _require_text(record["authority_gate"]),
        "component": _require_text(record["component"]),
        "implementation_status": _require_text(record["implementation_status"]),
        "public_serving_enabled": False,
        "required_capabilities": sorted(_require_text_tuple(record["required_capabilities"])),
        "sidecar_id": _require_text(record["sidecar_id"]),
        "wiring_modes": list(_require_text_tuple(record["wiring_modes"])),
    }


def _profile_record(
    *,
    profile_id: str,
    package_profile_id: str,
    required_sidecars: tuple[str, ...],
    optional_sidecars: tuple[str, ...],
    wiring_modes: tuple[str, ...],
    public_claimability_runtime_activated: bool,
) -> dict[str, Any]:
    package = profile_manifest(package_profile_id)
    return {
        "optional_sidecars": sorted(_require_text_tuple(optional_sidecars)),
        "package_profile": package,
        "package_profile_id": package_profile_id,
        "private_wiring_modes": list(_require_text_tuple(wiring_modes)),
        "profile_id": _require_text(profile_id),
        "public_claimability_runtime_activated": public_claimability_runtime_activated,
        "public_confidential_messaging_claimed": False,
        "public_p2p_activated": False,
        "public_serving_enabled": False,
        "required_sidecars": sorted(_require_text_tuple(required_sidecars)),
    }


def _validate_sidecar_record(record: Mapping[str, Any]) -> None:
    for key in ("authority_gate", "component", "implementation_status", "sidecar_id"):
        _require_text(record.get(key))
    for key in ("required_capabilities", "wiring_modes"):
        _require_text_list(record.get(key), token="sidecar_registry_sidecar_list_invalid_phase_1307")
    _require_false(record.get("public_serving_enabled"), token="sidecar_registry_sidecar_public_serving_forbidden_phase_1307")


def _validate_profile_record(record: Mapping[str, Any], *, sidecar_ids: set[str]) -> None:
    profile_id = _require_text(record.get("profile_id"))
    package_profile_id = _require_text(record.get("package_profile_id"))
    package = profile_manifest(package_profile_id)
    if record.get("package_profile") != package:
        raise ValueError("sidecar_registry_package_profile_mismatch_phase_1307")
    required = set(
        _require_text_list(
            record.get("required_sidecars"),
            token="sidecar_registry_profile_sidecars_invalid_phase_1307",
        )
    )
    optional = set(
        _require_text_list(
            record.get("optional_sidecars"),
            token="sidecar_registry_profile_sidecars_invalid_phase_1307",
        )
    )
    if not required <= sidecar_ids or not optional <= sidecar_ids:
        raise ValueError("sidecar_registry_profile_unknown_sidecar_phase_1307")
    if set(record["required_sidecars"]) & set(record["optional_sidecars"]):
        raise ValueError("sidecar_registry_profile_sidecar_overlap_phase_1307")
    for key in (
        "public_claimability_runtime_activated",
        "public_confidential_messaging_claimed",
        "public_p2p_activated",
        "public_serving_enabled",
    ):
        _require_false(record.get(key), token="sidecar_registry_profile_public_authority_forbidden_phase_1307")
    _require_text_list(
        record.get("private_wiring_modes"),
        token="sidecar_registry_profile_wiring_invalid_phase_1307",
    )
    if profile_id == "openclaw_claimable_local_bridge":
        if package_profile_id != PROFILE_OPENCLAW_SKILL_CLAIMABLE:
            raise ValueError("sidecar_registry_openclaw_claimable_profile_invalid_phase_1307")
        if package["public_claimability"] is not True or package["public_p2p"] is not False:
            raise ValueError("sidecar_registry_claimable_profile_claims_invalid_phase_1307")
        if "offline_claimability_receipt_verifier" not in required:
            raise ValueError("sidecar_registry_claimable_profile_missing_verifier_phase_1307")
        if "wallet_action_semantics_preflight" not in required:
            raise ValueError("sidecar_registry_claimable_profile_missing_wallet_action_boundary_phase_1314")
        if "value_path_activation_boundary_preflight" not in required:
            raise ValueError("sidecar_registry_claimable_profile_missing_value_path_boundary_phase_1315")
    if profile_id == PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW:
        if package_profile_id != PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW:
            raise ValueError("sidecar_registry_confidential_profile_invalid_phase_1307")
        if package["public_claimability"] or package["public_p2p"] or package["public_rc_eligible"]:
            raise ValueError("sidecar_registry_confidential_profile_public_claim_forbidden_phase_1307")
        if "confidential_coordination_local_preview" not in required:
            raise ValueError("sidecar_registry_confidential_profile_missing_sidecar_phase_1307")
        if "confidential_coordination_private_gated_shard" not in required:
            raise ValueError("sidecar_registry_confidential_profile_missing_ccss_001_phase_1324")
        if "confidential_coordination_capability_membership_boundary" not in required:
            raise ValueError("sidecar_registry_confidential_profile_missing_ccss_002_phase_1325")
        if "confidential_coordination_sealed_sender_local_delivery" not in required:
            raise ValueError("sidecar_registry_confidential_profile_missing_ccss_003_phase_1326")


def _validate_package_profile_integrity(value: object) -> None:
    integrity = _require_mapping(
        value,
        token="sidecar_registry_package_profile_integrity_invalid_phase_1307",
    )
    for key in (
        "claimable_profile_requires_offline_verifier",
        "confidential_coordination_profile_is_private_local_only",
        "openclaw_nemoclaw_are_hosts_not_protocol_substrates",
    ):
        if integrity.get(key) is not True:
            raise ValueError("sidecar_registry_package_profile_integrity_invalid_phase_1307")
    for key in (
        "public_claimability_runtime_activation_authorized",
        "public_p2p_activation_authorized",
    ):
        _require_false(
            integrity.get(key),
            token="sidecar_registry_package_profile_integrity_public_authority_forbidden_phase_1307",
        )
    ccss = _require_mapping(
        integrity.get("confidential_coordination_shard_manifest"),
        token="sidecar_registry_package_profile_integrity_ccss_manifest_invalid_phase_1324",
    )
    if ccss.get("contract_version") != (
        "ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1"
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_manifest_invalid_phase_1324"
        )
    for key in (
        "encrypted_coordination_node_envelope_contract_recorded",
        "local_only",
        "private_to_public_promotion_evidence_shape_recorded",
        "shard_header_projection_contract_recorded",
    ):
        if ccss.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_ccss_manifest_invalid_phase_1324"
            )
    for key in ("public_confidential_coordination_serving_enabled", "public_p2p_enabled"):
        _require_false(
            ccss.get(key),
            token="sidecar_registry_package_profile_integrity_ccss_public_authority_forbidden_phase_1324",
        )
    if ccss.get("next_phase") != "phase_1325_ccss_capability_membership_boundary_next":
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_manifest_invalid_phase_1324"
        )
    if ccss.get("tokens") != [
        "ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1",
        "encrypted_coordination_node_envelope_contract_recorded_phase_1324",
        "shard_header_projection_contract_recorded_phase_1324",
        "private_to_public_promotion_evidence_shape_recorded_phase_1324",
        "ccss_public_serving_not_enabled_phase_1324",
        "phase_1325_ccss_capability_membership_boundary_next",
        "public_rc_remains_blocked_after_phase_1324",
    ]:
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_manifest_invalid_phase_1324"
        )
    ccss_capability = _require_mapping(
        integrity.get("confidential_coordination_capability_manifest"),
        token="sidecar_registry_package_profile_integrity_ccss_capability_manifest_invalid_phase_1325",
    )
    if ccss_capability.get("contract_version") != (
        "ccss_002_capability_membership_grant_revocation_boundary_phase_1325.v0.1"
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_capability_manifest_invalid_phase_1325"
        )
    for key in (
        "grant_revocation_boundary_recorded",
        "local_only",
        "membership_plaintext_disclosure_forbidden",
        "optional_zk_interface_boundary_recorded",
        "private_shard_access_control_boundary_recorded",
    ):
        if ccss_capability.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_ccss_capability_manifest_invalid_phase_1325"
            )
    for key in (
        "public_confidential_coordination_serving_enabled",
        "public_membership_directory_enabled",
        "public_p2p_enabled",
        "public_zk_verifier_enabled",
    ):
        _require_false(
            ccss_capability.get(key),
            token="sidecar_registry_package_profile_integrity_ccss_capability_public_authority_forbidden_phase_1325",
        )
    if ccss_capability.get("next_phase") != "phase_1326_ccss_sealed_sender_boundary_next":
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_capability_manifest_invalid_phase_1325"
        )
    if ccss_capability.get("tokens") != [
        "ccss_002_capability_membership_grant_revocation_boundary_phase_1325.v0.1",
        "private_shard_access_control_boundary_recorded_phase_1325",
        "membership_plaintext_disclosure_forbidden_phase_1325",
        "optional_zk_interface_boundary_recorded_phase_1325",
        "phase_1326_ccss_sealed_sender_boundary_next",
        "public_rc_remains_blocked_after_phase_1325",
    ]:
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_capability_manifest_invalid_phase_1325"
        )
    ccss_sealed_sender = _require_mapping(
        integrity.get("confidential_coordination_sealed_sender_manifest"),
        token="sidecar_registry_package_profile_integrity_ccss_sealed_sender_manifest_invalid_phase_1326",
    )
    if ccss_sealed_sender.get("contract_version") != (
        "ccss_003_sealed_sender_local_delivery_boundary_phase_1326.v0.1"
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_sealed_sender_manifest_invalid_phase_1326"
        )
    for key in (
        "fixed_size_payload_boundary_recorded",
        "h013_h015_dependency_seams_recorded",
        "local_only",
        "sealed_sender_fixed_size_payload_boundary_recorded",
    ):
        if ccss_sealed_sender.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_ccss_sealed_sender_manifest_invalid_phase_1326"
            )
    for key in (
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_p2p_enabled",
        "public_relay_serving_enabled",
    ):
        _require_false(
            ccss_sealed_sender.get(key),
            token="sidecar_registry_package_profile_integrity_ccss_sealed_sender_public_authority_forbidden_phase_1326",
        )
    if ccss_sealed_sender.get("next_phase") != "phase_1327_ccss_gossip_jitter_cover_policy_next":
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_sealed_sender_manifest_invalid_phase_1326"
        )
    if ccss_sealed_sender.get("tokens") != [
        "ccss_003_sealed_sender_local_delivery_boundary_phase_1326.v0.1",
        "sealed_sender_fixed_size_payload_boundary_recorded_phase_1326",
        "h013_h015_dependency_seams_recorded_phase_1326",
        "public_p2p_not_activated_by_ccss_phase_1326",
        "phase_1327_ccss_gossip_jitter_cover_policy_next",
        "public_rc_remains_blocked_after_phase_1326",
    ]:
        raise ValueError(
            "sidecar_registry_package_profile_integrity_ccss_sealed_sender_manifest_invalid_phase_1326"
        )
    verifier = _require_mapping(
        integrity.get("offline_claimability_verifier_manifest"),
        token="sidecar_registry_package_profile_integrity_verifier_manifest_invalid_phase_1307",
    )
    for key in (
        "non_loopback_claimability_api_enabled",
        "public_api_enabled",
        "public_claimability_activated",
        "receipt_verifier_public_serving_enabled",
    ):
        _require_false(
            verifier.get(key),
            token="sidecar_registry_package_profile_integrity_verifier_public_authority_forbidden_phase_1307",
        )
    transport = _require_mapping(
        integrity.get("transport_principal_admission_sidecar_manifest"),
        token="sidecar_registry_package_profile_integrity_transport_manifest_invalid_phase_1310",
    )
    for key in (
        "local_only",
        "admission_ban_rate_privacy_tests_hardened",
        "hostile_network_public_path_blocked",
        "revocation_replay_tests_hardened",
    ):
        if transport.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_transport_manifest_invalid_phase_1310"
            )
    for key in (
        "public_credential_issuer_authorized",
        "public_fetch_serving_enabled",
        "public_path_activation_authorized",
        "public_p2p_enabled",
        "public_rate_limit_state_activated",
        "public_replay_cache_activated",
        "public_revocation_registry_activated",
        "public_sidecar_serving_enabled",
    ):
        _require_false(
            transport.get(key),
            token="sidecar_registry_package_profile_integrity_transport_public_authority_forbidden_phase_1310",
        )
    projection = _require_mapping(
        integrity.get("local_graph_memory_projection_sidecar_manifest"),
        token="sidecar_registry_package_profile_integrity_projection_manifest_invalid_phase_1311",
    )
    for key in (
        "local_only",
        "bounded_projection_serving_blocker_tests_hardened",
        "confidential_coordination_projection_non_leakage_tests",
        "private_gated_shard_header_projection_supported",
        "projection_privacy_filtering_hardened",
        "public_safe_projection_local_only",
    ):
        if projection.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_projection_manifest_invalid_phase_1312"
            )
    if projection.get("projection_privacy_field_filtering_tests_version") != (
        "projection_privacy_field_filtering_tests_phase_1312.v0.1"
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_projection_manifest_invalid_phase_1312"
        )
    if projection.get("phase_1312_tokens") != sorted(
        [
            "projection_privacy_field_filtering_tests_phase_1312.v0.1",
            "projection_privacy_filters_hardened_phase_1312",
            "confidential_coordination_projection_non_leakage_tests_phase_1312",
            "public_sidecar_projection_serving_not_enabled_phase_1312",
            "phase_1313_public_fetch_p2p_activation_candidate_default_off_next",
            "public_rc_remains_blocked_after_phase_1312",
        ]
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_projection_manifest_invalid_phase_1312"
        )
    for key in (
        "public_confidential_coordination_serving_enabled",
        "public_confidential_messaging_claimed",
        "public_fetch_serving_enabled",
        "public_listener_enabled",
        "public_p2p_enabled",
        "public_sidecar_projection_serving_enabled",
    ):
        _require_false(
            projection.get(key),
            token="sidecar_registry_package_profile_integrity_projection_public_authority_forbidden_phase_1311",
        )
    readiness = _require_mapping(
        integrity.get("public_fetch_p2p_readiness_candidate_manifest"),
        token="sidecar_registry_package_profile_integrity_public_fetch_p2p_manifest_invalid_phase_1313",
    )
    if readiness.get("contract_version") != (
        "public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1"
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_public_fetch_p2p_manifest_invalid_phase_1313"
        )
    for key in (
        "local_only",
        "readiness_only",
        "rust_public_p2p_substrate_gate_required",
    ):
        if readiness.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_public_fetch_p2p_manifest_invalid_phase_1313"
            )
    for key in (
        "activation_candidate_authorized",
        "public_fetch_serving_enabled",
        "public_listener_enabled",
        "public_p2p_enabled",
        "transport_public_path_activation_authorized",
    ):
        _require_false(
            readiness.get(key),
            token="sidecar_registry_package_profile_integrity_public_fetch_p2p_authority_forbidden_phase_1313",
        )
    if readiness.get("tokens") != [
        "public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1",
        "rust_public_p2p_substrate_gate_status_recorded_phase_1313",
        "public_p2p_default_off_phase_1313",
        "public_fetch_serving_default_off_phase_1313",
        "transport_public_path_activation_not_authorized_phase_1313",
        "phase_1314_wallet_withdrawal_transfer_spend_preflight_next",
        "public_rc_remains_blocked_after_phase_1313",
    ]:
        raise ValueError(
            "sidecar_registry_package_profile_integrity_public_fetch_p2p_manifest_invalid_phase_1313"
        )
    wallet_actions = _require_mapping(
        integrity.get("wallet_action_semantics_preflight_manifest"),
        token="sidecar_registry_package_profile_integrity_wallet_actions_manifest_invalid_phase_1314",
    )
    if wallet_actions.get("contract_version") != (
        "wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1"
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_wallet_actions_manifest_invalid_phase_1314"
        )
    for key in ("local_only", "preflight_only"):
        if wallet_actions.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_wallet_actions_manifest_invalid_phase_1314"
            )
    for key in (
        "public_claim_endpoint_enabled",
        "public_claimability_activated",
        "wallet_ledger_write_authorized",
        "wallet_signing_authorized",
        "wallet_spend_enabled",
        "wallet_transfer_enabled",
        "wallet_withdrawal_enabled",
    ):
        _require_false(
            wallet_actions.get(key),
            token="sidecar_registry_package_profile_integrity_wallet_actions_authority_forbidden_phase_1314",
        )
    if wallet_actions.get("tokens") != [
        "wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1",
        "wallet_withdrawal_transfer_spend_not_activated_phase_1314",
        "wallet_signing_ledger_write_not_authorized_phase_1314",
        "public_claimability_user_action_boundary_recorded_phase_1314",
        "phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next",
        "public_rc_remains_blocked_after_phase_1314",
    ]:
        raise ValueError(
            "sidecar_registry_package_profile_integrity_wallet_actions_manifest_invalid_phase_1314"
        )
    value_path = _require_mapping(
        integrity.get("value_path_activation_boundary_preflight_manifest"),
        token="sidecar_registry_package_profile_integrity_value_path_manifest_invalid_phase_1315",
    )
    if value_path.get("contract_version") != (
        "ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1"
    ):
        raise ValueError(
            "sidecar_registry_package_profile_integrity_value_path_manifest_invalid_phase_1315"
        )
    for key in ("local_only", "preflight_only"):
        if value_path.get(key) is not True:
            raise ValueError(
                "sidecar_registry_package_profile_integrity_value_path_manifest_invalid_phase_1315"
            )
    for key in (
        "ecu_creation_enabled",
        "ecu_mint_authorized",
        "ilc_settlement_authorized",
        "ilc_transfer_enabled",
        "public_claim_endpoint_enabled",
        "public_claimability_activated",
        "wallet_ledger_write_authorized",
        "wallet_signing_authorized",
        "wallet_write_authorized",
        "withdrawal_runtime_enabled",
    ):
        _require_false(
            value_path.get(key),
            token="sidecar_registry_package_profile_integrity_value_path_authority_forbidden_phase_1315",
        )
    if value_path.get("tokens") != [
        "ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1",
        "ecu_minting_not_authorized_phase_1315",
        "ilc_settlement_not_authorized_phase_1315",
        "value_path_activation_boundary_recorded_phase_1315",
        "phase_1316_window_1303_1316_closure_audit_next",
        "public_rc_remains_blocked_after_phase_1315",
    ]:
        raise ValueError(
            "sidecar_registry_package_profile_integrity_value_path_manifest_invalid_phase_1315"
        )


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


def _ids(records: list[Mapping[str, Any]], key: str, *, token: str) -> set[str]:
    values = [_require_text(record.get(key)) for record in records]
    if len(set(values)) != len(values):
        raise ValueError(token)
    if values != sorted(values):
        raise ValueError(token)
    return set(values)


def _require_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("sidecar_registry_text_invalid_phase_1307")
    if len(value) > _MAX_TEXT_LENGTH:
        raise ValueError("sidecar_registry_text_too_large_phase_1307")
    if any(ord(char) < 0x20 or char == "\x7f" for char in value):
        raise ValueError("sidecar_registry_text_invalid_phase_1307")
    return value


def _require_text_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple) or not value:
        raise ValueError("sidecar_registry_tuple_invalid_phase_1307")
    return tuple(_require_text(item) for item in value)


def _require_text_list(value: object, *, token: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(token)
    normalized = [_require_text(item) for item in value]
    if normalized != sorted(normalized) or len(set(normalized)) != len(normalized):
        raise ValueError(token)
    return normalized


def _require_false(value: object, *, token: str) -> None:
    if value is not False:
        raise ValueError(token)


def _reject_unsafe_json_tree(value: object) -> None:
    seen: set[int] = set()
    node_count = 0

    def visit(item: object, depth: int) -> None:
        nonlocal node_count
        if depth > _MAX_PAYLOAD_DEPTH:
            raise ValueError("sidecar_registry_payload_too_deep_phase_1307")
        node_count += 1
        if node_count > _MAX_PAYLOAD_NODES:
            raise ValueError("sidecar_registry_payload_too_large_phase_1307")
        if isinstance(item, float):
            raise ValueError("sidecar_registry_payload_float_forbidden_phase_1307")
        if item is None or isinstance(item, bool):
            return
        if isinstance(item, int):
            if item < 0 or item > _MAX_PROTOCOL_INT:
                raise ValueError("sidecar_registry_payload_int_invalid_phase_1307")
            return
        if isinstance(item, str):
            _require_text(item)
            return
        if isinstance(item, tuple):
            raise ValueError("sidecar_registry_tuple_values_forbidden_phase_1307")
        if isinstance(item, (Mapping, list)):
            marker = id(item)
            if marker in seen:
                raise ValueError("sidecar_registry_payload_cycle_forbidden_phase_1307")
            seen.add(marker)
            if isinstance(item, Mapping):
                for key, nested in item.items():
                    if not isinstance(key, str):
                        raise ValueError("sidecar_registry_payload_key_invalid_phase_1307")
                    _require_text(key)
                    node_count += 1
                    if node_count > _MAX_PAYLOAD_NODES:
                        raise ValueError("sidecar_registry_payload_too_large_phase_1307")
                    visit(nested, depth + 1)
            else:
                for nested in item:
                    visit(nested, depth + 1)
            seen.remove(marker)
            return
        raise ValueError("sidecar_registry_payload_type_invalid_phase_1307")

    visit(value, 0)


__all__ = [
    "CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW_PROFILE_DECLARED_TOKEN",
    "OPENCLAW_COMPATIBLE_LOCAL_BRIDGE_PROFILE_DECLARED_TOKEN",
    "PACKAGE_PROFILE_INTEGRITY_HARDENED_TOKEN",
    "PHASE_1308_NEXT_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1307_TOKEN",
    "SIDECAR_MANIFEST_DETERMINISTIC_PROFILE_DECLARED_TOKEN",
    "SIDECAR_REGISTRY_MANIFEST_VERSION",
    "build_sidecar_registry_manifest",
    "canonical_sidecar_registry_manifest_json",
    "claimability_receipt_verifier_manifest",
    "export_sidecar_registry_manifest_json",
    "public_fetch_p2p_readiness_candidate_manifest",
    "sidecar_registry_required_tokens",
    "transport_principal_admission_sidecar_manifest",
    "validate_sidecar_registry_manifest",
    "value_path_activation_boundary_preflight_manifest",
    "wallet_action_semantics_preflight_manifest",
]
