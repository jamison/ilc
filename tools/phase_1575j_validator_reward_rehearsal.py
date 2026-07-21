#!/usr/bin/env python3
"""Build Phase 1575j validator reward distribution rehearsal evidence.

This tool is retained private rehearsal evidence only. It does not clear
treasury guards, write wallets, execute transfers, submit checkpoints, or
activate live validator reward distribution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.epoch.epoch_emission_runtime import ILC_QUANTUM, build_epoch_emission_quote
from ilc_core.epoch.treasury_validator_reward_production_path import (
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
    TREASURY_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    TREASURY_VALIDATOR_REWARD_PRODUCTION_PATH_VERSION,
    build_treasury_validator_reward_result,
    compute_treasury_distribution_settlement_root,
    emit_canonical_treasury_distribution_events,
)
from ilc_core.epoch.validator_reward_pool_routing_runtime import (
    VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN,
)
from tools.phase_1575i_treasury_readiness import (
    certificate_sha256 as treasury_certificate_payload_sha256,
    stable_json,
    verify_treasury_readiness_certificate,
)


PHASE = "1575j"
SCHEMA_VERSION = "ilc.validator_reward_rehearsal.1575j.v1"
DESTINATION_REGISTRY_SCHEMA_VERSION = "ilc.validator_reward_destination_registry.1575j.v1"
TURN_ON_READY_VERDICT = "ready_for_1575k_review_no_activation"
GENERATED_AT_SOURCE = "deterministic_static_phase_1575j"
DEFAULT_1575I_CERTIFICATE = (
    REPO_ROOT / "out/treasury_readiness_1575i/treasury_no_wallet_write_readiness_certificate.json"
)

OUTPUT_TOKENS = (
    "validator_reward_distribution_rehearsal_committed_phase_1575j",
    "validator_reward_destination_binding_rehearsed_phase_1575j",
    "validator_reward_turn_on_ready_certificate_phase_1575j",
    "treasury_guard_not_cleared_phase_1575j",
)

REHEARSAL_INPUT_ROWS = (
    {
        "issuance_epoch": 1,
        "write_fee_burn_pool_ilc": "10000",
        "observed_velocity": "0.92",
    },
    {
        "issuance_epoch": 2,
        "write_fee_burn_pool_ilc": "12500",
        "observed_velocity": "0.88",
    },
    {
        "issuance_epoch": 3,
        "write_fee_burn_pool_ilc": "9000",
        "observed_velocity": "0.95",
    },
)


def _decimal_to_string(value: Decimal) -> str:
    if not isinstance(value, Decimal):
        raise ValueError("value_must_be_decimal")
    if not value.is_finite():
        raise ValueError("decimal_value_must_be_finite")
    return format(value.normalize(), "f")


def _quantize_ilc(value: Decimal) -> Decimal:
    return value.quantize(ILC_QUANTUM, rounding=ROUND_DOWN)


def _reject_non_json_exact_values(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_in_validator_reward_rehearsal_rejected")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("non_finite_decimal_in_validator_reward_rehearsal")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_non_json_exact_values(key)
            _reject_non_json_exact_values(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_non_json_exact_values(item)


def _sha256_record(record: dict[str, Any]) -> str:
    _reject_non_json_exact_values(record)
    return hashlib.sha256(stable_json(record).encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("json_payload_must_be_object")
    return payload


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validator_agent_id(validator_id: int) -> str:
    if isinstance(validator_id, bool) or not isinstance(validator_id, int) or validator_id < 1:
        raise ValueError("validator_id_must_be_positive_int")
    return hashlib.sha384(f"phase1575j-validator-agent-{validator_id}".encode("ascii")).hexdigest()


def _destination_base_record(validator_id: int) -> dict[str, Any]:
    agent_id = _validator_agent_id(validator_id)
    return {
        "destination_account_ref": f"validator_reward_rehearsal_1575j_validator_{validator_id}",
        "destination_binding_scope": "private_retained_rehearsal_not_live_wallet",
        "destination_live_wallet_address": None,
        "destination_type": "validator_reward_account_candidate",
        "validator_agent_id": agent_id,
        "validator_id": validator_id,
    }


def build_validator_destination_registry() -> dict[str, Any]:
    destinations = []
    for validator_id in range(1, 5):
        record = _destination_base_record(validator_id)
        record["destination_binding_sha256"] = _sha256_record(record)
        destinations.append(record)
    registry_without_digest = {
        "destination_count": len(destinations),
        "destinations": destinations,
        "schema_version": DESTINATION_REGISTRY_SCHEMA_VERSION,
    }
    return {
        **registry_without_digest,
        "registry_sha256": _sha256_record(registry_without_digest),
    }


def _destination_allocations(
    reward_pool: Decimal,
    destination_registry: dict[str, Any],
) -> list[dict[str, Any]]:
    if reward_pool < Decimal("0"):
        raise ValueError("reward_pool_must_be_non_negative")
    destinations = destination_registry.get("destinations")
    if not isinstance(destinations, list) or not destinations:
        raise ValueError("destination_registry_destinations_required")
    base_share = _quantize_ilc(reward_pool / Decimal(len(destinations)))
    allocations: list[dict[str, Any]] = []
    allocated = Decimal("0")
    for index, destination in enumerate(destinations):
        amount = base_share
        if index == len(destinations) - 1:
            amount = _quantize_ilc(reward_pool - allocated)
        allocated += amount
        allocations.append(
            {
                "amount_ilc_str": _decimal_to_string(amount),
                "destination_account_ref": str(destination["destination_account_ref"]),
                "destination_binding_sha256": str(destination["destination_binding_sha256"]),
                "destination_live_wallet_address": None,
                "validator_agent_id": str(destination["validator_agent_id"]),
                "validator_id": int(destination["validator_id"]),
            }
        )
    if allocated != reward_pool:
        raise ValueError("validator_destination_allocation_conservation_failed")
    return allocations


def _epoch_inputs(row: dict[str, object], cumulative_issued_before: Decimal) -> dict[str, object]:
    epoch = row["issuance_epoch"]
    if isinstance(epoch, bool) or not isinstance(epoch, int):
        raise ValueError("issuance_epoch_must_be_int")
    emission_quote = build_epoch_emission_quote(epoch, cumulative_issued_before)
    write_fee_burn_pool = Decimal(str(row["write_fee_burn_pool_ilc"]))
    requested_bounty = _quantize_ilc(write_fee_burn_pool * VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN)
    planned_burn = _quantize_ilc(emission_quote.capped_epoch_budget_ilc * Decimal("0.05"))
    return {
        "cumulative_issued_before_epoch_ilc": _decimal_to_string(cumulative_issued_before),
        "epoch_budget_ilc": _decimal_to_string(emission_quote.capped_epoch_budget_ilc),
        "issuance_epoch": epoch,
        "observed_velocity": str(row["observed_velocity"]),
        "planned_burn_ilc": _decimal_to_string(planned_burn),
        "requested_bounty_ilc": _decimal_to_string(requested_bounty),
        "treasury_planned_burn_ilc": _decimal_to_string(planned_burn),
        "write_fee_burn_pool_ilc": _decimal_to_string(write_fee_burn_pool),
    }


def _build_epoch_record(
    row: dict[str, object],
    cumulative_issued_before: Decimal,
    destination_registry: dict[str, Any],
) -> tuple[dict[str, Any], Decimal]:
    inputs = _epoch_inputs(row, cumulative_issued_before)
    result = build_treasury_validator_reward_result(inputs)
    root = compute_treasury_distribution_settlement_root(result)
    events = emit_canonical_treasury_distribution_events(result, root)
    reward_pool = result.reward_routing_quote.validator_reward_pool_ilc
    allocations = _destination_allocations(reward_pool, destination_registry)
    allocation_total = sum(Decimal(item["amount_ilc_str"]) for item in allocations)
    if allocation_total != reward_pool:
        raise ValueError("validator_reward_allocation_total_mismatch")
    root_payload = json.loads(root.canonical_record_json)
    if "settlement_root_hex" in root.canonical_record_json:
        raise ValueError("settlement_root_self_reference_detected")
    event_records = [event.to_canonical_record() for event in events]
    epoch_record = {
        "canonical_events": event_records,
        "destination_allocation_total_ilc": _decimal_to_string(allocation_total),
        "destination_allocations": allocations,
        "destination_registry_sha256": destination_registry["registry_sha256"],
        "guard_token": result.guard_token,
        "inputs": inputs,
        "integration_gate_result": result.integration_gate_result,
        "issuance_epoch": result.issuance_epoch,
        "production_treasury_distribution_activated": result.production_treasury_distribution_activated,
        "reward_routing_quote": result.reward_routing_quote.to_canonical_record(),
        "root_payload_sha256": _sha256_record(root_payload),
        "settlement_root": root.to_canonical_record(),
        "treasury_quote": result.treasury_quote.to_canonical_record(),
        "validator_reward_pool_ilc": _decimal_to_string(reward_pool),
    }
    epoch_record["epoch_record_sha256"] = _sha256_record(epoch_record)
    next_cumulative = cumulative_issued_before + Decimal(str(inputs["epoch_budget_ilc"]))
    return epoch_record, _quantize_ilc(next_cumulative)


def build_validator_reward_rehearsal_evidence(
    certificate_path: Path = DEFAULT_1575I_CERTIFICATE,
) -> dict[str, Any]:
    certificate = _read_json(certificate_path)
    verify_treasury_readiness_certificate(certificate)
    if TREASURY_DISTRIBUTION_NOT_ACTIVATED is not True:
        raise ValueError("treasury_distribution_guard_must_remain_true_phase_1575j")

    destination_registry = build_validator_destination_registry()
    cumulative = Decimal("0")
    epochs = []
    for row in REHEARSAL_INPUT_ROWS:
        epoch_record, cumulative = _build_epoch_record(row, cumulative, destination_registry)
        epochs.append(epoch_record)

    evidence_without_digest = {
        "dependency_certificates": {
            "phase_1575i": {
                "certificate_path": str(certificate_path.relative_to(REPO_ROOT)),
                "file_sha256": file_sha256(certificate_path),
                "payload_sha256": treasury_certificate_payload_sha256(certificate),
            }
        },
        "generated_at_source": GENERATED_AT_SOURCE,
        "guard_state": {
            "treasury_distribution_not_activated": TREASURY_DISTRIBUTION_NOT_ACTIVATED,
            "treasury_distribution_guard_token": TREASURY_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
            "validator_reward_distribution_guard_token": (
                VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN
            ),
        },
        "non_claims": {
            "activates_validator_rewards": False,
            "clears_treasury_guard": False,
            "executes_live_settlement": False,
            "executes_transfer": False,
            "public_mirror_updated": False,
            "sends_epoch_checkpoint": False,
            "writes_wallet": False,
        },
        "output_tokens": list(OUTPUT_TOKENS),
        "phase": PHASE,
        "rehearsal_epochs": epochs,
        "runtime_versions": {
            "treasury_validator_reward_production_path": (
                TREASURY_VALIDATOR_REWARD_PRODUCTION_PATH_VERSION
            ),
        },
        "schema_version": SCHEMA_VERSION,
        "turn_on_ready_certificate": {
            "requires_later_phase": "1575k",
            "requires_live_destination_governance": True,
            "requires_replay_tests_before_guard_clearance": True,
            "requires_wallet_write_authorization_before_any_transfer": True,
            "verdict": TURN_ON_READY_VERDICT,
        },
        "validator_destination_registry": destination_registry,
    }
    return {
        **evidence_without_digest,
        "evidence_payload_sha256": _sha256_record(evidence_without_digest),
    }


def verify_validator_reward_rehearsal_evidence(evidence: dict[str, Any]) -> None:
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("validator_reward_rehearsal_schema_version_mismatch")
    if evidence.get("phase") != PHASE:
        raise ValueError("validator_reward_rehearsal_phase_mismatch")
    guard_state = evidence.get("guard_state")
    if not isinstance(guard_state, dict):
        raise ValueError("guard_state_missing")
    if guard_state.get("treasury_distribution_not_activated") is not True:
        raise ValueError("treasury_guard_must_remain_true")
    non_claims = evidence.get("non_claims")
    if not isinstance(non_claims, dict):
        raise ValueError("non_claims_missing")
    for key, value in non_claims.items():
        if value is not False:
            raise ValueError(f"non_claim_must_be_false:{key}")
    registry = evidence.get("validator_destination_registry")
    if not isinstance(registry, dict):
        raise ValueError("validator_destination_registry_missing")
    if registry.get("schema_version") != DESTINATION_REGISTRY_SCHEMA_VERSION:
        raise ValueError("destination_registry_schema_version_mismatch")
    registry_copy = dict(registry)
    registry_digest = registry_copy.pop("registry_sha256", None)
    if registry_digest != _sha256_record(registry_copy):
        raise ValueError("destination_registry_digest_mismatch")
    epochs = evidence.get("rehearsal_epochs")
    if not isinstance(epochs, list) or len(epochs) != len(REHEARSAL_INPUT_ROWS):
        raise ValueError("rehearsal_epoch_count_mismatch")
    for epoch in epochs:
        if not isinstance(epoch, dict):
            raise ValueError("rehearsal_epoch_record_must_be_object")
        reward_pool = Decimal(str(epoch["validator_reward_pool_ilc"]))
        allocation_total = Decimal(str(epoch["destination_allocation_total_ilc"]))
        if allocation_total != reward_pool:
            raise ValueError("validator_reward_allocation_total_mismatch")
        if "settlement_root_hex" in str(epoch["settlement_root"]["canonical_record_json"]):
            raise ValueError("settlement_root_self_reference_detected")
        for allocation in epoch["destination_allocations"]:
            if allocation.get("destination_live_wallet_address") is not None:
                raise ValueError("live_wallet_address_must_not_be_set")
    payload_copy = dict(evidence)
    digest = payload_copy.pop("evidence_payload_sha256", None)
    if digest != _sha256_record(payload_copy):
        raise ValueError("evidence_payload_digest_mismatch")


def evidence_sha256(evidence: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json(evidence).encode("utf-8")).hexdigest()


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = stable_json(data) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.chmod(tmp_name, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--treasury-readiness-certificate", type=Path, default=DEFAULT_1575I_CERTIFICATE)
    args = parser.parse_args(argv)

    evidence = build_validator_reward_rehearsal_evidence(args.treasury_readiness_certificate)
    verify_validator_reward_rehearsal_evidence(evidence)
    atomic_write_json(args.out, evidence)
    print(evidence_sha256(evidence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
