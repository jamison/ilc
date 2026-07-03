from __future__ import annotations

from copy import deepcopy

from ilc_core.ledger.fix2s_activation_packet_verifier import (
    FIX2S_ACTIVATION_PACKET_VERIFIER_VERSION,
    OUTPUT_TOKENS,
    REQUIRED_ROLLBACK_STEP_COUNT,
    verify_activation_packet,
)


def _guard_entry(
    *,
    module_path: str,
    allowed_namespace_value: bool,
    production_value_retained: bool,
) -> dict[str, object]:
    return {
        "allowed_namespace_value": allowed_namespace_value,
        "module_path": module_path,
        "production_value_retained": production_value_retained,
        "rollback_action": "restore production value and discard scratch namespace",
        "scope": "disposable_namespace_only",
    }


def _packet() -> dict[str, object]:
    return {
        "packet_version": FIX2S_ACTIVATION_PACKET_VERIFIER_VERSION,
        "disposable_namespace": {
            "destroy_after_rerun_required": True,
            "namespace_id": "block6_private_value_write_soft_rc_<run_id>",
            "persistent_state_outside_namespace_allowed": False,
            "production_atlas_registration_allowed": False,
            "scratch_lmdb_path_pattern": (
                "out/block6_rehearsal/<run_id>/scratch_value_write.lmdb"
            ),
            "session_lifetime": "single_private_soft_rc_rerun",
        },
        "guard_clearance_table": {
            "PRODUCTION_EMISSION_NOT_ACTIVATED": _guard_entry(
                module_path="ilc_core/epoch/epoch_emission_production_path.py",
                allowed_namespace_value=False,
                production_value_retained=True,
            ),
            "wallet_write_authorized": _guard_entry(
                module_path="ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
                allowed_namespace_value=True,
                production_value_retained=False,
            ),
            "treasury_write_authorized": _guard_entry(
                module_path="ilc_core/epoch/treasury_validator_reward_production_path.py",
                allowed_namespace_value=True,
                production_value_retained=False,
            ),
            "ecu_mint_authorized": _guard_entry(
                module_path="ilc_core/epoch/epoch_emission_production_path.py",
                allowed_namespace_value=True,
                production_value_retained=False,
            ),
            "ilc_settlement_authorized": _guard_entry(
                module_path="ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
                allowed_namespace_value=True,
                production_value_retained=False,
            ),
        },
        "rollback_protocol": {
            "failure_disposition": "discard_run_and_do_not_cite_as_evidence",
            "minimum_step_count": REQUIRED_ROLLBACK_STEP_COUNT,
            "no_persistent_state_outside_namespace": True,
            "ordered_steps": [
                "stop private value-write services",
                "export scratch namespace hashes for audit only",
                "verify no production Atlas registration occurred for scratch state",
                "destroy scratch LMDB and wallet/treasury state",
                "confirm source guard values remain at production-safe values",
                "rerun production Atlas validation",
                "record final rollback receipt with hashes and non-secret confirmations",
            ],
            "rollback_confirmation_required": True,
        },
        "cdl057_real_witness_binding_minimum": {
            "absent_token": "cdl057_witness_absent_fix2r",
            "absent_token_allowed_when_write_flags_true": False,
            "conversion_epoch_match_required": True,
            "sub_gap_get_latest_witness_ref_epoch_missing_recorded": True,
            "witness_epoch_binding_required": True,
            "witness_hash_or_root_pinned_required": True,
            "witness_payload_retrievable_required": True,
        },
        "genesis_tranche_disposition": {
            "c_max_ilc": "25920000",
            "carry_forward_plan": (
                "Exercise only in a separately authorized value-path rerun after "
                "CDL-057 real witness binding and accepted-work adapters are live."
            ),
            "disposition": "deferred_to_later_value_path_activation",
            "fixed_tranche_ilc": "1296000",
            "rationale": (
                "Fix2s defines the packet boundary only and performs no value write."
            ),
        },
        "obligation_disposition": {
            "OBL-041": "closed_packet_spec_level",
            "OBL-043": "routed_to_fix2t",
            "OBL-044": "routed_to_fix2u",
        },
        "non_authorizations": {
            "no_genesis_signing_authorized_by_fix2s": True,
            "no_guard_cleared_by_fix2s": True,
            "no_ledger_write_executed_by_fix2s": True,
            "no_production_minting_activated_by_fix2s": True,
            "no_public_rc_activated_by_fix2s": True,
            "no_scratch_lmdb_created_by_fix2s": True,
            "no_treasury_write_executed_by_fix2s": True,
            "no_wallet_write_executed_by_fix2s": True,
        },
        "tokens": list(OUTPUT_TOKENS),
    }


def test_fix2s_well_formed_packet_passes_verifier() -> None:
    result = verify_activation_packet(_packet())

    assert result["ok"] is True
    assert result["tokens"] == list(OUTPUT_TOKENS)
    assert len(result["packet_sha256"]) == 64


def test_fix2s_packet_missing_rollback_protocol_fails() -> None:
    packet = _packet()
    packet.pop("rollback_protocol")

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "activation_packet_missing_required_section:rollback_protocol",
    }


def test_fix2s_packet_missing_rollback_minimum_step_count_fails() -> None:
    packet = _packet()
    del packet["rollback_protocol"]["minimum_step_count"]  # type: ignore[index]

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "rollback_protocol_minimum_step_count_invalid",
    }


def test_fix2s_packet_rollback_steps_below_minimum_fails() -> None:
    packet = _packet()
    packet["rollback_protocol"]["ordered_steps"] = [  # type: ignore[index]
        "stop private value-write services",
        "export scratch namespace hashes for audit only",
        "destroy scratch LMDB and wallet/treasury state",
        "rerun production Atlas validation",
    ]

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "rollback_protocol_ordered_steps_below_minimum",
    }


def test_fix2s_packet_record_write_authorization_fails() -> None:
    packet = _packet()
    packet["wallet_write_authorized"] = True

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "wallet_write_authorized_forbidden_phase_1568_fix2s",
    }


def test_fix2s_packet_missing_cdl057_binding_minimum_fails() -> None:
    packet = _packet()
    packet.pop("cdl057_real_witness_binding_minimum")

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": (
            "activation_packet_missing_required_section:"
            "cdl057_real_witness_binding_minimum"
        ),
    }


def test_fix2s_packet_missing_genesis_tranche_disposition_fails() -> None:
    packet = _packet()
    packet.pop("genesis_tranche_disposition")

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "activation_packet_missing_required_section:genesis_tranche_disposition",
    }


def test_fix2s_packet_missing_obl041_closure_declaration_fails() -> None:
    packet = _packet()
    packet["obligation_disposition"] = {
        "OBL-043": "routed_to_fix2t",
        "OBL-044": "routed_to_fix2u",
    }

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "obl_041_packet_level_closure_required",
    }


def test_fix2s_packet_missing_required_guard_fails() -> None:
    packet = _packet()
    del packet["guard_clearance_table"]["wallet_write_authorized"]  # type: ignore[index]

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "guard_clearance_table_missing_required_guard:wallet_write_authorized",
    }


def test_fix2s_packet_absent_witness_token_cannot_be_allowed_with_write_flags() -> None:
    packet = _packet()
    binding = deepcopy(packet["cdl057_real_witness_binding_minimum"])
    binding["absent_token_allowed_when_write_flags_true"] = True
    packet["cdl057_real_witness_binding_minimum"] = binding

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "cdl057_absent_token_must_fail_when_write_flags_true",
    }


def test_fix2s_packet_float_values_fail() -> None:
    packet = _packet()
    packet["genesis_tranche_disposition"]["fixed_tranche_fraction"] = 0.05  # type: ignore[index]

    assert verify_activation_packet(packet) == {
        "ok": False,
        "reason": "activation_packet_float_rejected",
    }
