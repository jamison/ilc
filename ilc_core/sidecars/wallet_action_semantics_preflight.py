# SPDX-License-Identifier: AGPL-3.0-only
"""Wallet-facing value-action semantics preflight.

This module records the boundary where any wallet provider could request
withdrawal, transfer, spend, signing, or ledger-write behavior. It does not
create those methods, signature payloads, ledger writes, claim endpoints, ECU
minting, release artifacts, or public serving surfaces. Phase 1592 authorizes
public claimability visibility and ILC settlement state while keeping wallet
actions blocked. The ledger/graph/receipt substrate remains the truth object;
wallets are adapters.
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


WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION = (
    "wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1"
)
WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN = (
    "wallet_withdrawal_transfer_spend_not_activated_phase_1314"
)
WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN = (
    "wallet_signing_ledger_write_not_authorized_phase_1314"
)
PUBLIC_CLAIMABILITY_USER_ACTION_BOUNDARY_RECORDED_TOKEN = (
    "public_claimability_user_action_boundary_recorded_phase_1314"
)
PUBLIC_CLAIMABILITY_AUTHORIZED_PHASE_1592_TOKEN = (
    "public_claimability_authorized_phase_1592"
)
ILC_SETTLEMENT_AUTHORIZED_PHASE_1592_TOKEN = "ilc_settlement_authorized_phase_1592"
PHASE_1315_NEXT_TOKEN = "phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next"
PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1314_TOKEN = (
    "public_rc_remains_blocked_after_phase_1314"
)
WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN = (
    "wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314"
)

PREFLIGHT_STATE = (
    "wallet_action_semantics_preflight_rc_claimability_authorized_phase_1592"
)
PREFLIGHT_REF_PREFIX = "wallet_action_semantics_preflight_sha256"

_MAX_PAYLOAD_DEPTH = 32
_MAX_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_EPOCH = 1_000_000_000_000
_HEX_DIGEST_LENGTH = 64
_HEX = frozenset("0123456789abcdef")
_AUTHORIZATION_FLAGS = (
    "wallet_withdrawal_enabled",
    "wallet_transfer_enabled",
    "wallet_spend_enabled",
    "wallet_signing_authorized",
    "wallet_ledger_write_authorized",
    "public_claimability_activated",
    "public_claim_endpoint_enabled",
    "withdrawal_endpoint_enabled",
    "transfer_endpoint_enabled",
    "spend_endpoint_enabled",
    "external_chain_bridge_enabled",
    "withdrawal_runtime_enabled",
    "ecu_mint_authorized",
    "ilc_settlement_authorized",
    "release_artifact_authorized",
    "cdl088_opened",
)
_RC_AUTHORIZED_FLAGS = (
    "public_claimability_activated",
    "ilc_settlement_authorized",
)
_FALSE_AUTHORIZATION_FLAGS = tuple(
    name for name in _AUTHORIZATION_FLAGS if name not in _RC_AUTHORIZED_FLAGS
)
_PERMITTED_WALLET_QUERY_OPERATIONS = (
    "wallet_status",
    "wallet_history",
    "wallet_export",
    "ledger_summary",
)
_BLOCKED_USER_VALUE_ACTIONS = (
    "withdrawal_request",
    "transfer_request",
    "spend_request",
    "claim_endpoint_submission",
    "wallet_signature_payload",
    "ledger_write_mutation",
    "external_chain_destination_submission",
)
_REQUIRED_BEFORE_WALLET_ACTION_ACTIVATION = (
    "explicit_public_claimability_user_action_authority",
    "public_claimability_api_or_local_claim_endpoint_authority",
    "wallet_signing_key_lifecycle_and_payload_contract",
    "wallet_ledger_write_authority_and_replay_policy",
    "duplicate_claim_replay_nullifier_registry_policy",
    "public_safe_disclosure_and_receipt_binding_contract",
    "ecu_minting_ilc_settlement_boundary_preflight_phase_1315",
    "release_materialization_and_package_profile_authority_if_public_rc_claimed",
    "separate_human_authorization_after_phase_1314",
)
_PREFLIGHT_PACKET_KEYS = frozenset(
    {
        "authorization_flags",
        "candidate_sha256",
        "current_epoch",
        "local_only",
        "next_phase",
        "permitted_wallet_query_operations",
        "preflight_only",
        "prohibited_user_value_actions",
        "readiness_verdict",
        "required_before_wallet_action_activation",
        "source_evidence",
        "state",
        "tokens",
        "user_action_boundary",
        "version",
    }
)


class WalletActionSemanticsPreflightError(ValueError):
    """Fail-closed Phase 1314 preflight error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def wallet_action_semantics_preflight_required_tokens() -> list[str]:
    return [
        WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION,
        WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
        WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN,
        PUBLIC_CLAIMABILITY_USER_ACTION_BOUNDARY_RECORDED_TOKEN,
        PUBLIC_CLAIMABILITY_AUTHORIZED_PHASE_1592_TOKEN,
        ILC_SETTLEMENT_AUTHORIZED_PHASE_1592_TOKEN,
        PHASE_1315_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1314_TOKEN,
    ]


def wallet_action_semantics_preflight_manifest() -> dict[str, Any]:
    """Return deterministic local/package metadata for the value-action preflight."""

    manifest = {
        "contract_version": WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION,
        "local_only": True,
        "preflight_only": True,
        "public_claim_endpoint_enabled": False,
        "public_claimability_activated": True,
        "ilc_settlement_authorized": True,
        "tokens": wallet_action_semantics_preflight_required_tokens(),
        "wallet_ledger_write_authorized": False,
        "wallet_signing_authorized": False,
        "wallet_spend_enabled": False,
        "wallet_transfer_enabled": False,
        "wallet_withdrawal_enabled": False,
    }
    _reject_unsafe_json_tree(manifest)
    return manifest


def build_wallet_action_semantics_preflight_packet(
    *,
    current_epoch: int,
    wallet_withdrawal_enabled: bool = False,
    wallet_transfer_enabled: bool = False,
    wallet_spend_enabled: bool = False,
    wallet_signing_authorized: bool = False,
    wallet_ledger_write_authorized: bool = False,
    public_claimability_activated: bool = True,
    public_claim_endpoint_enabled: bool = False,
    withdrawal_endpoint_enabled: bool = False,
    transfer_endpoint_enabled: bool = False,
    spend_endpoint_enabled: bool = False,
    external_chain_bridge_enabled: bool = False,
    withdrawal_runtime_enabled: bool = False,
    ecu_mint_authorized: bool = False,
    ilc_settlement_authorized: bool = True,
    release_artifact_authorized: bool = False,
    cdl088_opened: bool = False,
) -> dict[str, Any]:
    """Build a deterministic wallet-facing value-action preflight packet."""

    current = _require_epoch("current", current_epoch)
    flags = {
        "wallet_withdrawal_enabled": wallet_withdrawal_enabled,
        "wallet_transfer_enabled": wallet_transfer_enabled,
        "wallet_spend_enabled": wallet_spend_enabled,
        "wallet_signing_authorized": wallet_signing_authorized,
        "wallet_ledger_write_authorized": wallet_ledger_write_authorized,
        "public_claimability_activated": public_claimability_activated,
        "public_claim_endpoint_enabled": public_claim_endpoint_enabled,
        "withdrawal_endpoint_enabled": withdrawal_endpoint_enabled,
        "transfer_endpoint_enabled": transfer_endpoint_enabled,
        "spend_endpoint_enabled": spend_endpoint_enabled,
        "external_chain_bridge_enabled": external_chain_bridge_enabled,
        "withdrawal_runtime_enabled": withdrawal_runtime_enabled,
        "ecu_mint_authorized": ecu_mint_authorized,
        "ilc_settlement_authorized": ilc_settlement_authorized,
        "release_artifact_authorized": release_artifact_authorized,
        "cdl088_opened": cdl088_opened,
    }
    _require_rc_authorized_flags(flags)
    _require_all_false(
        _blocked_authorization_flags(flags),
        token_by_name={
            "wallet_withdrawal_enabled": WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
            "wallet_transfer_enabled": WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
            "wallet_spend_enabled": WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
            "wallet_signing_authorized": WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN,
            "wallet_ledger_write_authorized": WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN,
        },
        default_token="wallet_action_semantics_activation_forbidden_phase_1314",
    )

    packet: dict[str, Any] = {
        "authorization_flags": {name: flags[name] for name in _AUTHORIZATION_FLAGS},
        "current_epoch": current,
        "local_only": True,
        "next_phase": PHASE_1315_NEXT_TOKEN,
        "permitted_wallet_query_operations": list(_PERMITTED_WALLET_QUERY_OPERATIONS),
        "preflight_only": True,
        "prohibited_user_value_actions": list(_BLOCKED_USER_VALUE_ACTIONS),
        "readiness_verdict": "rc_claimability_and_ilc_settlement_authorized_wallet_actions_blocked",
        "required_before_wallet_action_activation": list(
            _REQUIRED_BEFORE_WALLET_ACTION_ACTIVATION
        ),
        "source_evidence": _source_evidence(),
        "state": PREFLIGHT_STATE,
        "tokens": wallet_action_semantics_preflight_required_tokens(),
        "user_action_boundary": _user_action_boundary(),
        "version": WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION,
    }
    packet["candidate_sha256"] = _packet_sha256(packet)
    return validate_wallet_action_semantics_preflight_packet(packet)


def validate_wallet_action_semantics_preflight_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a Phase 1314 wallet action preflight packet without activation."""

    if not isinstance(packet, Mapping):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_preflight_invalid_phase_1314",
            "wallet action preflight packet must be a mapping",
        )
    _reject_unsafe_json_tree(packet)
    if set(packet) != _PREFLIGHT_PACKET_KEYS:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_packet_keys_invalid_phase_1314",
            "wallet action preflight packet keys do not match the Phase 1314 contract",
        )
    if packet.get("version") != WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_version_invalid_phase_1314",
            "wallet action preflight version is invalid",
        )
    if packet.get("state") != PREFLIGHT_STATE:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_state_invalid_phase_1314",
            "wallet action preflight state is invalid",
        )
    current = _require_epoch("current", packet.get("current_epoch"))
    if packet.get("local_only") is not True or packet.get("preflight_only") is not True:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_local_preflight_required_phase_1314",
            "Phase 1314 packet must remain local and preflight-only",
        )
    if packet.get("tokens") != wallet_action_semantics_preflight_required_tokens():
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_tokens_invalid_phase_1314",
            "Phase 1314 required tokens are invalid",
        )
    if packet.get("next_phase") != PHASE_1315_NEXT_TOKEN:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_next_phase_invalid_phase_1314",
            "Phase 1314 next phase token is invalid",
        )

    flags = _require_mapping(
        packet.get("authorization_flags"),
        token="wallet_action_semantics_authorization_flags_invalid_phase_1314",
    )
    if set(flags) != set(_AUTHORIZATION_FLAGS):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_authorization_flags_invalid_phase_1314",
            "wallet action preflight authorization flags are invalid",
        )
    _require_rc_authorized_flags(flags)
    _require_all_false(
        _blocked_authorization_flags(flags),
        token_by_name={
            "wallet_withdrawal_enabled": WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
            "wallet_transfer_enabled": WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
            "wallet_spend_enabled": WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN,
            "wallet_signing_authorized": WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN,
            "wallet_ledger_write_authorized": WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN,
        },
        default_token="wallet_action_semantics_activation_forbidden_phase_1314",
    )
    if packet.get("permitted_wallet_query_operations") != list(
        _PERMITTED_WALLET_QUERY_OPERATIONS
    ):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_permitted_operations_invalid_phase_1314",
            "Phase 1314 permitted wallet operations are invalid",
        )
    if packet.get("prohibited_user_value_actions") != list(_BLOCKED_USER_VALUE_ACTIONS):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_prohibited_actions_invalid_phase_1314",
            "Phase 1314 prohibited user value actions are invalid",
        )
    if packet.get("required_before_wallet_action_activation") != list(
        _REQUIRED_BEFORE_WALLET_ACTION_ACTIVATION
    ):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_requirements_invalid_phase_1314",
            "Phase 1314 wallet action requirements are invalid",
        )
    if packet.get("user_action_boundary") != _user_action_boundary():
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_user_boundary_invalid_phase_1314",
            "Phase 1314 user action boundary is invalid",
        )
    if packet.get("source_evidence") != _source_evidence():
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_source_evidence_invalid_phase_1314",
            "Phase 1314 source evidence is invalid",
        )
    if packet.get("readiness_verdict") != (
        "rc_claimability_and_ilc_settlement_authorized_wallet_actions_blocked"
    ):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_readiness_verdict_invalid_phase_1592",
            "Phase 1592 readiness verdict is invalid",
        )
    candidate_sha256 = _require_hex_digest(packet.get("candidate_sha256"))
    if candidate_sha256 != _packet_sha256(packet):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_candidate_hash_mismatch_phase_1314",
            "Phase 1314 wallet action preflight packet hash mismatch",
        )

    validated = dict(packet)
    validated["current_epoch"] = current
    canonical_wallet_action_semantics_preflight_json(validated)
    return validated


def wallet_action_semantics_preflight_ref(packet: Mapping[str, Any]) -> str:
    validated = validate_wallet_action_semantics_preflight_packet(packet)
    return f"{PREFLIGHT_REF_PREFIX}:{validated['candidate_sha256']}"


def canonical_wallet_action_semantics_preflight_json(packet: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(packet)
    return json.dumps(packet, allow_nan=False, separators=(",", ":"), sort_keys=True)


def export_wallet_action_semantics_preflight_json(
    packet: Mapping[str, Any] | None = None,
) -> str:
    active = (
        build_wallet_action_semantics_preflight_packet(current_epoch=0)
        if packet is None
        else validate_wallet_action_semantics_preflight_packet(packet)
    )
    return canonical_wallet_action_semantics_preflight_json(active)


def _source_evidence() -> dict[str, str]:
    return {
        "claimability_receipt_verifier": OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        "ecu_ilc_lifecycle_runtime": ECU_ILC_LIFECYCLE_RUNTIME_VERSION,
        "phase_576_wallet_boundary": "wallet_visibility_and_accounting_only",
        "phase_615_lifecycle_contract": "no_spend_transfer_withdrawal_signing_authority",
        "phase_617_public_wallet_surface": "read_only_query_operations_only",
        "phase_1314_scope": "wallet_action_semantics_preflight_no_wallet_actions",
        "phase_1592_scope": "public_claimability_and_ilc_settlement_authorized",
        "public_wallet_runtime": PUBLIC_WALLET_RUNTIME_VERSION,
    }


def _user_action_boundary() -> dict[str, Any]:
    return {
        "boundary_token": PUBLIC_CLAIMABILITY_USER_ACTION_BOUNDARY_RECORDED_TOKEN,
        "claim_endpoint_submission_constructed": False,
        "external_chain_destination_collected": False,
        "ledger_mutation_emitted": False,
        "ledger_truth_boundary_token": (
            WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN
        ),
        "public_claimability_user_action_authorized": True,
        "signature_payload_constructed": False,
        "user_visible_allowed_queries": list(_PERMITTED_WALLET_QUERY_OPERATIONS),
        "wallet_action_methods_added": False,
        "wallet_provider_role": "adapter_or_sidecar_not_truth_source",
        "wallet_state_mutation_from_user_action": False,
    }


def _packet_sha256(packet: Mapping[str, Any]) -> str:
    payload = dict(packet)
    payload.pop("candidate_sha256", None)
    return hashlib.sha256(
        canonical_wallet_action_semantics_preflight_json(payload).encode("utf-8")
    ).hexdigest()


def _reject_unsafe_json_tree(
    value: Any,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_PAYLOAD_DEPTH:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_payload_too_deep_phase_1314",
            "Phase 1314 wallet action preflight payload is too deep",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_PAYLOAD_NODES:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_payload_too_large_phase_1314",
            "Phase 1314 wallet action preflight payload is too large",
        )
    if isinstance(value, float):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_float_values_forbidden_phase_1314",
            "Phase 1314 wallet action preflight payload cannot contain floats",
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        if value < 0 or value > _MAX_EPOCH:
            raise WalletActionSemanticsPreflightError(
                "wallet_action_semantics_int_values_invalid_phase_1314",
                "Phase 1314 wallet action preflight integers must be non-negative and bounded",
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
            raise WalletActionSemanticsPreflightError(
                "wallet_action_semantics_payload_cycle_forbidden_phase_1314",
                "Phase 1314 wallet action preflight payload cannot contain cycles",
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
            raise WalletActionSemanticsPreflightError(
                "wallet_action_semantics_payload_cycle_forbidden_phase_1314",
                "Phase 1314 wallet action preflight payload cannot contain cycles",
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
    raise WalletActionSemanticsPreflightError(
        "wallet_action_semantics_payload_type_invalid_phase_1314",
        "Phase 1314 wallet action preflight payload contains a non-JSON type",
    )


def _require_epoch(name: str, value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > _MAX_EPOCH
    ):
        raise WalletActionSemanticsPreflightError(
            f"wallet_action_semantics_{name}_epoch_invalid_phase_1314",
            "Phase 1314 wallet action preflight epoch must be a non-negative integer",
        )
    return value


def _require_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_text_invalid_phase_1314",
            "Phase 1314 wallet action preflight text is invalid",
        )
    if len(value) > _MAX_TEXT_LENGTH:
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_text_too_large_phase_1314",
            "Phase 1314 wallet action preflight text is too large",
        )
    return value


def _require_mapping(value: object, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WalletActionSemanticsPreflightError(token, "expected a mapping")
    return value


def _blocked_authorization_flags(flags: Mapping[str, Any]) -> dict[str, Any]:
    return {name: flags[name] for name in _FALSE_AUTHORIZATION_FLAGS}


def _require_rc_authorized_flags(flags: Mapping[str, Any]) -> None:
    for name in _RC_AUTHORIZED_FLAGS:
        if _require_bool(name, flags.get(name)) is not True:
            raise WalletActionSemanticsPreflightError(
                f"wallet_action_semantics_{name}_required_phase_1592",
                f"Phase 1592 requires {name}",
            )


def _require_bool(name: str, value: object) -> bool:
    if type(value) is not bool:
        raise WalletActionSemanticsPreflightError(
            f"wallet_action_semantics_{name}_bool_invalid_phase_1314",
            "Phase 1314 wallet action preflight flag must be boolean",
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
            raise WalletActionSemanticsPreflightError(
                token,
                f"Phase 1314 cannot authorize {name}",
            )


def _require_hex_digest(value: object) -> str:
    text = _require_text(value)
    if len(text) != _HEX_DIGEST_LENGTH or any(char not in _HEX for char in text):
        raise WalletActionSemanticsPreflightError(
            "wallet_action_semantics_digest_invalid_phase_1314",
            "Phase 1314 wallet action preflight digest is invalid",
        )
    return text


__all__ = [
    "ILC_SETTLEMENT_AUTHORIZED_PHASE_1592_TOKEN",
    "PHASE_1315_NEXT_TOKEN",
    "PREFLIGHT_REF_PREFIX",
    "PUBLIC_CLAIMABILITY_AUTHORIZED_PHASE_1592_TOKEN",
    "PUBLIC_CLAIMABILITY_USER_ACTION_BOUNDARY_RECORDED_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1314_TOKEN",
    "WALLET_ACTION_SEMANTICS_PREFLIGHT_VERSION",
    "WALLET_PROVIDER_AGNOSTIC_LEDGER_TRUTH_BOUNDARY_TOKEN",
    "WALLET_SIGNING_LEDGER_WRITE_NOT_AUTHORIZED_TOKEN",
    "WALLET_WITHDRAWAL_TRANSFER_SPEND_NOT_ACTIVATED_TOKEN",
    "WalletActionSemanticsPreflightError",
    "build_wallet_action_semantics_preflight_packet",
    "canonical_wallet_action_semantics_preflight_json",
    "export_wallet_action_semantics_preflight_json",
    "validate_wallet_action_semantics_preflight_packet",
    "wallet_action_semantics_preflight_manifest",
    "wallet_action_semantics_preflight_ref",
    "wallet_action_semantics_preflight_required_tokens",
]
