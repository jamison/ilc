# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1568-Fix2s private value-write activation packet verifier.

This module is a read-model verifier only. It validates that a proposed
private Soft-RC activation/rollback packet is internally complete before any
future sensitive rerun can rely on it. It does not clear guards, write wallets,
write treasury state, mint, settle, create scratch databases, or activate public
RC.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from ilc_core.ledger.distributed_conversion_schema import CDL057_WITNESS_ABSENT_TOKEN


FIX2S_ACTIVATION_PACKET_VERIFIER_VERSION = (
    "fix2s_activation_packet_verifier_1568_fix2s.v0.1"
)
GENESIS_FIXED_TRANCHE_ILC = "1296000"
GENESIS_C_MAX_ILC = "25920000"

OUTPUT_TOKENS: tuple[str, ...] = (
    "phase_1568_fix2s_private_value_write_activation_packet_committed",
    "phase_1568_fix2s_disposable_namespace_defined",
    "phase_1568_fix2s_rollback_protocol_defined",
    "phase_1568_fix2s_obl_041_packet_level_closed",
    "phase_1568_fix2s_cdl057_real_witness_binding_minimum_defined",
    "phase_1568_fix2s_genesis_tranche_disposition_recorded",
    "phase_1568_fix2s_obl_043_routed_to_fix2t_confirmed",
    "phase_1568_fix2s_obl_044_routed_to_fix2u_confirmed",
    "phase_1568_fix2s_no_guard_cleared",
    "phase_1568_fix2s_no_wallet_write_executed",
    "public_path_remains_blocked_phase_1568_fix2s",
)

REQUIRED_SECTIONS: tuple[str, ...] = (
    "packet_version",
    "disposable_namespace",
    "guard_clearance_table",
    "rollback_protocol",
    "cdl057_real_witness_binding_minimum",
    "genesis_tranche_disposition",
    "obligation_disposition",
    "non_authorizations",
    "tokens",
)

FORBIDDEN_PACKET_TRUE_FIELDS: frozenset[str] = frozenset(
    {
        "guard_cleared",
        "wallet_write_authorized",
        "treasury_write_authorized",
        "ecu_mint_authorized",
        "production_minting_authorized",
        "ilc_settlement_authorized",
        "public_claimability_activated",
        "public_rc_activated",
        "wallet_write_executed",
        "treasury_write_executed",
        "ledger_write_executed",
        "scratch_lmdb_materialized",
    }
)

REQUIRED_GUARDS: dict[str, dict[str, Any]] = {
    "PRODUCTION_EMISSION_NOT_ACTIVATED": {
        "allowed_namespace_value": False,
        "module_path": "ilc_core/epoch/epoch_emission_production_path.py",
        "production_value_retained": True,
    },
    "wallet_write_authorized": {
        "allowed_namespace_value": True,
        "module_path": "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
        "production_value_retained": False,
    },
    "treasury_write_authorized": {
        "allowed_namespace_value": True,
        "module_path": "ilc_core/epoch/treasury_validator_reward_production_path.py",
        "production_value_retained": False,
    },
    "ecu_mint_authorized": {
        "allowed_namespace_value": True,
        "module_path": "ilc_core/epoch/epoch_emission_production_path.py",
        "production_value_retained": False,
    },
    "ilc_settlement_authorized": {
        "allowed_namespace_value": True,
        "module_path": "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
        "production_value_retained": False,
    },
}

REQUIRED_NON_AUTHORIZATIONS: tuple[str, ...] = (
    "no_guard_cleared_by_fix2s",
    "no_wallet_write_executed_by_fix2s",
    "no_treasury_write_executed_by_fix2s",
    "no_ledger_write_executed_by_fix2s",
    "no_scratch_lmdb_created_by_fix2s",
    "no_production_minting_activated_by_fix2s",
    "no_public_rc_activated_by_fix2s",
    "no_genesis_signing_authorized_by_fix2s",
)

ALLOWED_GENESIS_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "exercise_in_disposable_namespace",
        "deferred_to_later_value_path_activation",
    }
)


def verify_activation_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Verify a Fix2s activation packet without executing it."""

    try:
        _verify_activation_packet_or_raise(packet)
    except ValueError as exc:
        return {"ok": False, "reason": str(exc)}

    return {
        "ok": True,
        "packet_sha256": _sha256_payload(packet),
        "tokens": list(OUTPUT_TOKENS),
        "verifier_version": FIX2S_ACTIVATION_PACKET_VERIFIER_VERSION,
    }


def _verify_activation_packet_or_raise(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict):
        raise ValueError("activation_packet_must_be_object")
    _reject_float_tree(packet)
    for section in REQUIRED_SECTIONS:
        if section not in packet:
            raise ValueError(f"activation_packet_missing_required_section:{section}")
    if packet.get("packet_version") != FIX2S_ACTIVATION_PACKET_VERIFIER_VERSION:
        raise ValueError("activation_packet_version_invalid")

    for field in sorted(FORBIDDEN_PACKET_TRUE_FIELDS):
        if packet.get(field) is True:
            raise ValueError(f"{field}_forbidden_phase_1568_fix2s")

    _verify_disposable_namespace(
        _require_mapping(packet["disposable_namespace"], "disposable_namespace_invalid")
    )
    _verify_guard_clearance_table(
        _require_mapping(packet["guard_clearance_table"], "guard_clearance_table_invalid")
    )
    _verify_rollback_protocol(
        _require_mapping(packet["rollback_protocol"], "rollback_protocol_invalid")
    )
    _verify_cdl057_binding(
        _require_mapping(
            packet["cdl057_real_witness_binding_minimum"],
            "cdl057_real_witness_binding_minimum_invalid",
        )
    )
    _verify_genesis_tranche_disposition(
        _require_mapping(
            packet["genesis_tranche_disposition"],
            "genesis_tranche_disposition_invalid",
        )
    )
    _verify_obligation_disposition(
        _require_mapping(packet["obligation_disposition"], "obligation_disposition_invalid")
    )
    _verify_non_authorizations(
        _require_mapping(packet["non_authorizations"], "non_authorizations_invalid")
    )
    if packet.get("tokens") != list(OUTPUT_TOKENS):
        raise ValueError("activation_packet_tokens_invalid")


def _verify_disposable_namespace(namespace: Mapping[str, Any]) -> None:
    _require_text(namespace.get("namespace_id"), "disposable_namespace_id_required")
    _require_text(
        namespace.get("scratch_lmdb_path_pattern"),
        "disposable_namespace_scratch_lmdb_path_pattern_required",
    )
    if namespace.get("session_lifetime") != "single_private_soft_rc_rerun":
        raise ValueError("disposable_namespace_session_lifetime_invalid")
    if namespace.get("production_atlas_registration_allowed") is not False:
        raise ValueError("disposable_namespace_atlas_registration_must_be_false")
    if namespace.get("persistent_state_outside_namespace_allowed") is not False:
        raise ValueError("disposable_namespace_persistent_state_must_be_false")
    if namespace.get("destroy_after_rerun_required") is not True:
        raise ValueError("disposable_namespace_destroy_after_rerun_required")


def _verify_guard_clearance_table(guard_table: Mapping[str, Any]) -> None:
    missing = sorted(set(REQUIRED_GUARDS) - set(guard_table))
    if missing:
        raise ValueError(f"guard_clearance_table_missing_required_guard:{missing[0]}")
    for guard_name, expected in REQUIRED_GUARDS.items():
        entry = _require_mapping(
            guard_table[guard_name],
            f"guard_clearance_entry_invalid:{guard_name}",
        )
        for field, expected_value in expected.items():
            if entry.get(field) != expected_value:
                raise ValueError(f"guard_clearance_entry_{field}_invalid:{guard_name}")
        _require_text(
            entry.get("rollback_action"),
            f"guard_clearance_entry_rollback_action_required:{guard_name}",
        )
        if entry.get("scope") != "disposable_namespace_only":
            raise ValueError(f"guard_clearance_entry_scope_invalid:{guard_name}")


def _verify_rollback_protocol(protocol: Mapping[str, Any]) -> None:
    ordered_steps = protocol.get("ordered_steps")
    if (
        not isinstance(ordered_steps, Sequence)
        or isinstance(ordered_steps, (str, bytes))
        or not ordered_steps
    ):
        raise ValueError("rollback_protocol_ordered_steps_required")
    for step in ordered_steps:
        _require_text(step, "rollback_protocol_ordered_step_invalid")
    if protocol.get("rollback_confirmation_required") is not True:
        raise ValueError("rollback_protocol_confirmation_required")
    if protocol.get("failure_disposition") != "discard_run_and_do_not_cite_as_evidence":
        raise ValueError("rollback_protocol_failure_disposition_invalid")
    if protocol.get("no_persistent_state_outside_namespace") is not True:
        raise ValueError("rollback_protocol_no_persistent_state_required")


def _verify_cdl057_binding(binding: Mapping[str, Any]) -> None:
    if binding.get("absent_token") != CDL057_WITNESS_ABSENT_TOKEN:
        raise ValueError("cdl057_absent_token_invalid")
    if binding.get("absent_token_allowed_when_write_flags_true") is not False:
        raise ValueError("cdl057_absent_token_must_fail_when_write_flags_true")
    for field in (
        "witness_payload_retrievable_required",
        "witness_epoch_binding_required",
        "witness_hash_or_root_pinned_required",
        "conversion_epoch_match_required",
        "sub_gap_get_latest_witness_ref_epoch_missing_recorded",
    ):
        if binding.get(field) is not True:
            raise ValueError(f"cdl057_binding_{field}_required")


def _verify_genesis_tranche_disposition(disposition: Mapping[str, Any]) -> None:
    if disposition.get("c_max_ilc") != GENESIS_C_MAX_ILC:
        raise ValueError("genesis_tranche_c_max_invalid")
    if disposition.get("fixed_tranche_ilc") != GENESIS_FIXED_TRANCHE_ILC:
        raise ValueError("genesis_tranche_amount_invalid")
    if disposition.get("disposition") not in ALLOWED_GENESIS_DISPOSITIONS:
        raise ValueError("genesis_tranche_disposition_value_invalid")
    _require_text(disposition.get("rationale"), "genesis_tranche_rationale_required")
    if disposition.get("disposition") == "deferred_to_later_value_path_activation":
        _require_text(
            disposition.get("carry_forward_plan"),
            "genesis_tranche_carry_forward_plan_required",
        )


def _verify_obligation_disposition(disposition: Mapping[str, Any]) -> None:
    if disposition.get("OBL-041") != "closed_packet_spec_level":
        raise ValueError("obl_041_packet_level_closure_required")
    if disposition.get("OBL-043") != "routed_to_fix2t":
        raise ValueError("obl_043_fix2t_routing_required")
    if disposition.get("OBL-044") != "routed_to_fix2u":
        raise ValueError("obl_044_fix2u_routing_required")


def _verify_non_authorizations(non_authorizations: Mapping[str, Any]) -> None:
    for field in REQUIRED_NON_AUTHORIZATIONS:
        if non_authorizations.get(field) is not True:
            raise ValueError(f"non_authorization_missing:{field}")


def _require_mapping(value: Any, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(token)
    return value


def _require_text(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value.strip()


def _reject_float_tree(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("activation_packet_float_rejected")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float_tree(key)
            _reject_float_tree(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_float_tree(item)


def _stable_json_bytes(payload: Any) -> bytes:
    _reject_float_tree(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    ).encode("utf-8")


def _sha256_payload(payload: Any) -> str:
    return hashlib.sha256(_stable_json_bytes(payload)).hexdigest()


__all__ = [
    "FIX2S_ACTIVATION_PACKET_VERIFIER_VERSION",
    "GENESIS_C_MAX_ILC",
    "GENESIS_FIXED_TRANCHE_ILC",
    "OUTPUT_TOKENS",
    "verify_activation_packet",
]
