# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 1315 ECU/ILC value-path activation boundary preflight.

This module records the ledger-truth boundary for ECU minting, ILC settlement,
withdrawal runtime, wallet writes, and public claimability. It does not mint
ECU, settle ILC, construct withdrawal/signing payloads, mutate ledgers, serve a
public claim endpoint, produce release artifacts, open CDL-088, or activate any
economic value path.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from ilc_core.ledger.ecu_ilc_lifecycle_runtime import ECU_ILC_LIFECYCLE_RUNTIME_VERSION
from ilc_core.protocol.public_wallet_runtime import PUBLIC_WALLET_RUNTIME_VERSION
from ilc_core.sidecars.claimability_receipt_verifier import (
    OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
)
from ilc_core.sidecars.wallet_action_semantics_preflight import (
    WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION,
    WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN,
)


VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION = (
    "ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1"
)
ECU_MINTING_NOT_AUTHORIZED_TOKEN = "ecu_minting_not_authorized_phase_1315"
ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN = "ilc_settlement_not_authorized_phase_1315"
VALUE_PATH_ACTIVATION_BOUNDARY_RECORDED_TOKEN = (
    "value_path_activation_boundary_recorded_phase_1315"
)
PHASE_1316_NEXT_TOKEN = "phase_1316_window_1303_1316_closure_audit_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1315_TOKEN = (
    "public_rc_remains_blocked_after_phase_1315"
)

PREFLIGHT_STATE = "value_path_activation_boundary_preflight_no_activation_phase_1315"
PREFLIGHT_REF_PREFIX = "value_path_activation_boundary_preflight_sha256"

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_EPOCH = 1_000_000_000_000
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")

_FALSE_AUTHORIZATION_FLAGS = (
    "ecu_mint_authorized",
    "ecu_creation_enabled",
    "ecu_supply_policy_authorized",
    "ilc_settlement_authorized",
    "ilc_transfer_enabled",
    "ilc_settlement_root_authorized",
    "withdrawal_runtime_enabled",
    "withdrawal_endpoint_enabled",
    "wallet_write_authorized",
    "wallet_signing_authorized",
    "wallet_ledger_write_authorized",
    "public_claimability_activated",
    "public_claim_endpoint_enabled",
    "public_verifier_service_enabled",
    "external_chain_bridge_enabled",
    "release_artifact_authorized",
    "release_key_material_authorized",
    "cdl088_opened",
)
_PERMITTED_LOCAL_READ_SUBSTRATES = (
    "ecu_active_layer_read",
    "ecu_ilc_lifecycle_status",
    "wallet_status",
    "wallet_history",
    "wallet_export",
    "ledger_summary",
    "offline_claimability_receipt_verifier",
    "wallet_action_semantics_preflight",
)
_PROHIBITED_VALUE_PATH_ACTIONS = (
    "ecu_mint_request",
    "ecu_creation",
    "ecu_supply_policy_mutation",
    "ilc_settlement_execution",
    "ilc_transfer_execution",
    "ilc_settlement_root_publication",
    "withdrawal_runtime_execution",
    "withdrawal_endpoint_submission",
    "wallet_write_mutation",
    "wallet_signature_payload",
    "wallet_ledger_write_mutation",
    "public_claim_endpoint_submission",
    "public_verifier_service_request",
    "external_chain_destination_submission",
    "payment_runtime_execution",
    "release_artifact_materialization",
)
_REQUIRED_BEFORE_VALUE_PATH_ACTIVATION = (
    "explicit_value_path_activation_authority",
    "ecu_mint_policy_and_supply_invariant",
    "ilc_settlement_authority_and_replay_policy",
    "settlement_root_namespace_and_binding_contract",
    "withdrawal_runtime_contract",
    "wallet_provider_signing_payload_contract",
    "wallet_ledger_write_authority_and_replay_policy",
    "public_claimability_api_or_local_claim_endpoint_authority",
    "replay_nullifier_duplicate_claim_registry_policy",
    "transport_principal_public_path_authority_if_non_loopback",
    "release_materialization_and_package_profile_authority_if_public_rc_claimed",
    "separate_human_authorization_after_phase_1315",
)
_PREFLIGHT_PACKET_KEYS = frozenset(
    {
        "authorization_flags",
        "candidate_sha256",
        "current_epoch",
        "ledger_truth_boundary",
        "local_only",
        "next_phase",
        "permitted_local_read_substrates",
        "preflight_only",
        "prohibited_value_path_actions",
        "readiness_verdict",
        "required_before_value_path_activation",
        "source_evidence",
        "state",
        "tokens",
        "version",
    }
)


class ValuePathActivationBoundaryPreflightError(ValueError):
    """Fail-closed Phase 1315 preflight error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def value_path_activation_boundary_preflight_required_tokens() -> list[str]:
    return [
        VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION,
        ECU_MINTING_NOT_AUTHORIZED_TOKEN,
        ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
        VALUE_PATH_ACTIVATION_BOUNDARY_RECORDED_TOKEN,
        PHASE_1316_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1315_TOKEN,
    ]


def value_path_activation_boundary_preflight_manifest() -> dict[str, Any]:
    """Return deterministic local/package metadata for the value-path boundary."""

    manifest = {
        "contract_version": VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION,
        "ecu_creation_enabled": False,
        "ecu_mint_authorized": False,
        "ilc_settlement_authorized": False,
        "ilc_transfer_enabled": False,
        "local_only": True,
        "preflight_only": True,
        "public_claim_endpoint_enabled": False,
        "public_claimability_activated": False,
        "tokens": value_path_activation_boundary_preflight_required_tokens(),
        "wallet_ledger_write_authorized": False,
        "wallet_signing_authorized": False,
        "wallet_write_authorized": False,
        "withdrawal_runtime_enabled": False,
    }
    _reject_unsafe_json_tree(manifest)
    return manifest


def build_value_path_activation_boundary_preflight_packet(
    *,
    current_epoch: int,
    ecu_mint_authorized: bool = False,
    ecu_creation_enabled: bool = False,
    ecu_supply_policy_authorized: bool = False,
    ilc_settlement_authorized: bool = False,
    ilc_transfer_enabled: bool = False,
    ilc_settlement_root_authorized: bool = False,
    withdrawal_runtime_enabled: bool = False,
    withdrawal_endpoint_enabled: bool = False,
    wallet_write_authorized: bool = False,
    wallet_signing_authorized: bool = False,
    wallet_ledger_write_authorized: bool = False,
    public_claimability_activated: bool = False,
    public_claim_endpoint_enabled: bool = False,
    public_verifier_service_enabled: bool = False,
    external_chain_bridge_enabled: bool = False,
    release_artifact_authorized: bool = False,
    release_key_material_authorized: bool = False,
    cdl088_opened: bool = False,
) -> dict[str, Any]:
    """Build a deterministic ECU/ILC value-path boundary preflight packet."""

    current = _require_epoch("current", current_epoch)
    flags = {
        "ecu_mint_authorized": ecu_mint_authorized,
        "ecu_creation_enabled": ecu_creation_enabled,
        "ecu_supply_policy_authorized": ecu_supply_policy_authorized,
        "ilc_settlement_authorized": ilc_settlement_authorized,
        "ilc_transfer_enabled": ilc_transfer_enabled,
        "ilc_settlement_root_authorized": ilc_settlement_root_authorized,
        "withdrawal_runtime_enabled": withdrawal_runtime_enabled,
        "withdrawal_endpoint_enabled": withdrawal_endpoint_enabled,
        "wallet_write_authorized": wallet_write_authorized,
        "wallet_signing_authorized": wallet_signing_authorized,
        "wallet_ledger_write_authorized": wallet_ledger_write_authorized,
        "public_claimability_activated": public_claimability_activated,
        "public_claim_endpoint_enabled": public_claim_endpoint_enabled,
        "public_verifier_service_enabled": public_verifier_service_enabled,
        "external_chain_bridge_enabled": external_chain_bridge_enabled,
        "release_artifact_authorized": release_artifact_authorized,
        "release_key_material_authorized": release_key_material_authorized,
        "cdl088_opened": cdl088_opened,
    }
    _require_all_false(
        flags,
        token_by_name={
            "ecu_mint_authorized": ECU_MINTING_NOT_AUTHORIZED_TOKEN,
            "ecu_creation_enabled": ECU_MINTING_NOT_AUTHORIZED_TOKEN,
            "ecu_supply_policy_authorized": ECU_MINTING_NOT_AUTHORIZED_TOKEN,
            "ilc_settlement_authorized": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "ilc_transfer_enabled": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "ilc_settlement_root_authorized": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "withdrawal_runtime_enabled": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "withdrawal_endpoint_enabled": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
        },
        default_token="value_path_activation_authority_forbidden_phase_1315",
    )

    packet: dict[str, Any] = {
        "authorization_flags": {name: False for name in _FALSE_AUTHORIZATION_FLAGS},
        "current_epoch": current,
        "ledger_truth_boundary": _ledger_truth_boundary(),
        "local_only": True,
        "next_phase": PHASE_1316_NEXT_TOKEN,
        "permitted_local_read_substrates": list(_PERMITTED_LOCAL_READ_SUBSTRATES),
        "preflight_only": True,
        "prohibited_value_path_actions": list(_PROHIBITED_VALUE_PATH_ACTIONS),
        "readiness_verdict": "preflight_recorded_value_path_activation_blocked",
        "required_before_value_path_activation": list(
            _REQUIRED_BEFORE_VALUE_PATH_ACTIVATION
        ),
        "source_evidence": _source_evidence(),
        "state": PREFLIGHT_STATE,
        "tokens": value_path_activation_boundary_preflight_required_tokens(),
        "version": VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION,
    }
    packet["candidate_sha256"] = _packet_sha256(packet)
    return validate_value_path_activation_boundary_preflight_packet(packet)


def validate_value_path_activation_boundary_preflight_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a Phase 1315 value-path preflight packet without activation."""

    if not isinstance(packet, Mapping):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_packet_invalid_phase_1315",
            "value-path preflight packet must be a mapping",
        )
    _reject_unsafe_json_tree(packet)
    if set(packet) != _PREFLIGHT_PACKET_KEYS:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_packet_keys_invalid_phase_1315",
            "value-path preflight packet keys do not match the Phase 1315 contract",
        )
    if packet.get("version") != VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_version_invalid_phase_1315",
            "value-path preflight version is invalid",
        )
    if packet.get("state") != PREFLIGHT_STATE:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_state_invalid_phase_1315",
            "value-path preflight state is invalid",
        )
    current = _require_epoch("current", packet.get("current_epoch"))
    if packet.get("local_only") is not True or packet.get("preflight_only") is not True:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_local_preflight_required_phase_1315",
            "Phase 1315 packet must remain local and preflight-only",
        )
    if packet.get("tokens") != value_path_activation_boundary_preflight_required_tokens():
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_tokens_invalid_phase_1315",
            "Phase 1315 required tokens are invalid",
        )
    if packet.get("next_phase") != PHASE_1316_NEXT_TOKEN:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_next_phase_invalid_phase_1315",
            "Phase 1315 next phase token is invalid",
        )

    flags = _require_mapping(
        packet.get("authorization_flags"),
        token="value_path_activation_boundary_authorization_flags_invalid_phase_1315",
    )
    if set(flags) != set(_FALSE_AUTHORIZATION_FLAGS):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_authorization_flags_invalid_phase_1315",
            "Phase 1315 authorization flags are invalid",
        )
    _require_all_false(
        flags,
        token_by_name={
            "ecu_mint_authorized": ECU_MINTING_NOT_AUTHORIZED_TOKEN,
            "ecu_creation_enabled": ECU_MINTING_NOT_AUTHORIZED_TOKEN,
            "ecu_supply_policy_authorized": ECU_MINTING_NOT_AUTHORIZED_TOKEN,
            "ilc_settlement_authorized": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "ilc_transfer_enabled": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "ilc_settlement_root_authorized": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "withdrawal_runtime_enabled": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
            "withdrawal_endpoint_enabled": ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN,
        },
        default_token="value_path_activation_authority_forbidden_phase_1315",
    )
    if packet.get("permitted_local_read_substrates") != list(
        _PERMITTED_LOCAL_READ_SUBSTRATES
    ):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_permitted_substrates_invalid_phase_1315",
            "Phase 1315 permitted local read substrates are invalid",
        )
    if packet.get("prohibited_value_path_actions") != list(_PROHIBITED_VALUE_PATH_ACTIONS):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_prohibited_actions_invalid_phase_1315",
            "Phase 1315 prohibited value-path actions are invalid",
        )
    if packet.get("required_before_value_path_activation") != list(
        _REQUIRED_BEFORE_VALUE_PATH_ACTIVATION
    ):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_requirements_invalid_phase_1315",
            "Phase 1315 value-path requirements are invalid",
        )
    if packet.get("ledger_truth_boundary") != _ledger_truth_boundary():
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_ledger_truth_invalid_phase_1315",
            "Phase 1315 ledger-truth boundary is invalid",
        )
    if packet.get("source_evidence") != _source_evidence():
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_source_evidence_invalid_phase_1315",
            "Phase 1315 source evidence is invalid",
        )
    if packet.get("readiness_verdict") != "preflight_recorded_value_path_activation_blocked":
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_readiness_verdict_invalid_phase_1315",
            "Phase 1315 readiness verdict is invalid",
        )
    candidate_sha256 = _require_hex_digest(packet.get("candidate_sha256"))
    if candidate_sha256 != _packet_sha256(packet):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_candidate_hash_mismatch_phase_1315",
            "Phase 1315 value-path preflight packet hash mismatch",
        )

    validated = dict(packet)
    validated["current_epoch"] = current
    canonical_value_path_activation_boundary_preflight_json(validated)
    return validated


def value_path_activation_boundary_preflight_ref(packet: Mapping[str, Any]) -> str:
    validated = validate_value_path_activation_boundary_preflight_packet(packet)
    return f"{PREFLIGHT_REF_PREFIX}:{validated['candidate_sha256']}"


def canonical_value_path_activation_boundary_preflight_json(
    packet: Mapping[str, Any],
) -> str:
    _reject_unsafe_json_tree(packet)
    return json.dumps(packet, allow_nan=False, separators=(",", ":"), sort_keys=True)


def export_value_path_activation_boundary_preflight_json(
    packet: Mapping[str, Any] | None = None,
) -> str:
    active = (
        build_value_path_activation_boundary_preflight_packet(current_epoch=0)
        if packet is None
        else validate_value_path_activation_boundary_preflight_packet(packet)
    )
    return canonical_value_path_activation_boundary_preflight_json(active)


def _source_evidence() -> dict[str, str]:
    return {
        "claimability_receipt_verifier": OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        "ecu_active_layer_runtime": "ecu_active_layer_runtime_present_no_mint_authority",
        "ecu_ilc_lifecycle_runtime": ECU_ILC_LIFECYCLE_RUNTIME_VERSION,
        "phase_615_lifecycle_contract": "visible_ilc_lifecycle_no_public_claimability_or_withdrawal",
        "phase_617_public_wallet_surface": "read_only_query_operations_only",
        "phase_1314_wallet_action_semantics": WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION,
        "phase_1315_scope": "ecu_ilc_value_path_boundary_preflight_no_activation",
        "public_wallet_runtime": PUBLIC_WALLET_RUNTIME_VERSION,
    }


def _ledger_truth_boundary() -> dict[str, Any]:
    return {
        "boundary_token": VALUE_PATH_ACTIVATION_BOUNDARY_RECORDED_TOKEN,
        "claim_endpoint_submission_constructed": False,
        "ecu_mint_instruction_constructed": False,
        "external_chain_destination_collected": False,
        "ilc_settlement_instruction_constructed": False,
        "ledger_mutation_emitted": False,
        "ledger_truth_boundary_token": (
            WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN
        ),
        "public_claimability_user_action_authorized": False,
        "settlement_root_published": False,
        "signature_payload_constructed": False,
        "truth_objects": [
            "ledger_state",
            "graph_state",
            "receipt",
            "settled_root",
            "wallet_root_binding",
            "claimability_proof",
            "deterministic_sidecar_manifest",
        ],
        "value_path_activation_authorized": False,
        "wallet_provider_role": "adapter_or_sidecar_not_truth_source",
        "withdrawal_runtime_constructed": False,
    }


def _packet_sha256(packet: Mapping[str, Any]) -> str:
    payload = dict(packet)
    payload.pop("candidate_sha256", None)
    return hashlib.sha256(
        canonical_value_path_activation_boundary_preflight_json(payload).encode(
            "utf-8"
        )
    ).hexdigest()


def _reject_unsafe_json_tree(
    value: Any,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_PAYLOAD_DEPTH:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_payload_too_deep_phase_1315",
            "Phase 1315 value-path preflight payload is too deep",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_PAYLOAD_NODES:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_payload_too_large_phase_1315",
            "Phase 1315 value-path preflight payload is too large",
        )
    if isinstance(value, float):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_float_values_forbidden_phase_1315",
            "Phase 1315 value-path preflight payload cannot contain floats",
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        if value < 0 or value > _MAX_EPOCH:
            raise ValuePathActivationBoundaryPreflightError(
                "value_path_activation_boundary_int_values_invalid_phase_1315",
                "Phase 1315 value-path preflight integers must be non-negative and bounded",
            )
        return
    if isinstance(value, str):
        _require_text(value)
        return
    if value is None:
        return
    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in _seen:
            raise ValuePathActivationBoundaryPreflightError(
                "value_path_activation_boundary_payload_cycle_forbidden_phase_1315",
                "Phase 1315 value-path preflight payload cannot contain cycles",
            )
        _seen.add(object_id)
        try:
            for key, item in value.items():
                _require_text(key)
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if isinstance(value, list):
        object_id = id(value)
        if object_id in _seen:
            raise ValuePathActivationBoundaryPreflightError(
                "value_path_activation_boundary_payload_cycle_forbidden_phase_1315",
                "Phase 1315 value-path preflight payload cannot contain cycles",
            )
        _seen.add(object_id)
        try:
            for item in value:
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    raise ValuePathActivationBoundaryPreflightError(
        "value_path_activation_boundary_payload_type_invalid_phase_1315",
        "Phase 1315 value-path preflight payload contains a non-JSON type",
    )


def _require_epoch(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > _MAX_EPOCH
    ):
        raise ValuePathActivationBoundaryPreflightError(
            f"value_path_activation_boundary_{name}_epoch_invalid_phase_1315",
            "Phase 1315 value-path preflight epoch must be a non-negative integer",
        )
    return value


def _require_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_text_invalid_phase_1315",
            "Phase 1315 value-path preflight text is invalid",
        )
    if len(value) > _MAX_TEXT_LENGTH:
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_text_too_large_phase_1315",
            "Phase 1315 value-path preflight text is too large",
        )
    return value


def _require_mapping(value: object, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValuePathActivationBoundaryPreflightError(token, "expected a mapping")
    return value


def _require_bool(name: str, value: object) -> bool:
    if type(value) is not bool:
        raise ValuePathActivationBoundaryPreflightError(
            f"value_path_activation_boundary_{name}_bool_invalid_phase_1315",
            "Phase 1315 value-path preflight flag must be boolean",
        )
    return value


def _require_all_false(
    values: Mapping[str, Any],
    *,
    token_by_name: Mapping[str, str],
    default_token: str,
) -> None:
    for name, value in values.items():
        flag = _require_bool(name, value)
        if flag is not False:
            token = token_by_name.get(name, default_token)
            raise ValuePathActivationBoundaryPreflightError(
                token,
                f"Phase 1315 cannot authorize {name}",
            )


def _require_hex_digest(value: object) -> str:
    text = _require_text(value)
    if len(text) != _HEX_DIGEST_LENGTH or any(char not in _HEX for char in text):
        raise ValuePathActivationBoundaryPreflightError(
            "value_path_activation_boundary_digest_invalid_phase_1315",
            "Phase 1315 value-path preflight digest is invalid",
        )
    return text


__all__ = [
    "ECU_MINTING_NOT_AUTHORIZED_TOKEN",
    "ILC_SETTLEMENT_NOT_AUTHORIZED_TOKEN",
    "PHASE_1316_NEXT_TOKEN",
    "PREFLIGHT_REF_PREFIX",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1315_TOKEN",
    "VALUE_PATH_ACTIVATION_BOUNDARY_PREFLIGHT_VERSION",
    "VALUE_PATH_ACTIVATION_BOUNDARY_RECORDED_TOKEN",
    "ValuePathActivationBoundaryPreflightError",
    "build_value_path_activation_boundary_preflight_packet",
    "canonical_value_path_activation_boundary_preflight_json",
    "export_value_path_activation_boundary_preflight_json",
    "validate_value_path_activation_boundary_preflight_packet",
    "value_path_activation_boundary_preflight_manifest",
    "value_path_activation_boundary_preflight_ref",
    "value_path_activation_boundary_preflight_required_tokens",
]
