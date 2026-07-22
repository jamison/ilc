#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1575l ejected-stake redistribution readiness evidence builder."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import fields, is_dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from ilc_core.epoch.ejected_stake_distribution_production_path import (
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED_TOKEN,
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_PATH_VERSION,
    build_canonical_ejected_stake_event_payloads,
    build_ejected_stake_distribution_result,
    compute_ejected_stake_settlement_root,
    emit_canonical_ejected_stake_distribution_events,
    require_ejected_stake_distribution_production_activation,
)


OUTPUT_DIR = Path("out/ejected_stake_readiness_1575l")
EVENT_PATH = OUTPUT_DIR / "ejection_rehearsal_event.json"
CERTIFICATE_PATH = OUTPUT_DIR / "ejected_stake_readiness_certificate.json"
PHASE_1575L_TOOL_VERSION = "phase_1575l_ejected_stake_readiness.v0.1"
SYNTHETIC_EJECTED_VALIDATOR_AGENT_CID = "agent:phase1575l_ejected_validator_synthetic"
SYNTHETIC_REMAINING_MEMBER_STAKES = {
    "agent:phase1575l_validator_a": Decimal("100.000000000"),
    "agent:phase1575l_validator_b": Decimal("200.000000000"),
    "agent:phase1575l_validator_c": Decimal("300.000000000"),
}
SYNTHETIC_EJECTED_STAKE_ILC = Decimal("123.456789123")
SYNTHETIC_DISTRIBUTION_EPOCH = 1575


def stable_json(payload: Any) -> str:
    _reject_float_or_non_finite(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sha256_stable_json(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(stable_json(payload))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            tmp_path.unlink()
        finally:
            raise


def build_phase_1575l_evidence() -> dict[str, Any]:
    result = build_ejected_stake_distribution_result(
        {
            "distribution_epoch": SYNTHETIC_DISTRIBUTION_EPOCH,
            "ejected_stake_ilc": SYNTHETIC_EJECTED_STAKE_ILC,
            "remaining_member_stakes": SYNTHETIC_REMAINING_MEMBER_STAKES,
            "approve_votes": 3,
            "participating_voters": 3,
        }
    )
    settlement_root = compute_ejected_stake_settlement_root(result)
    canonical_events = [
        event.to_canonical_record()
        for event in emit_canonical_ejected_stake_distribution_events(result, settlement_root)
    ]
    quote = result.distribution_quote
    payouts = tuple(quote.payouts)
    payout_total = sum((amount for _, amount in payouts), Decimal("0"))
    decimal_conservation_verified = payout_total == quote.ejected_stake_ilc
    fail_closed_behavior_verified = _verify_fail_closed_behavior()
    guard_exception_type = _guard_exception_type()
    recipient_ids = [agent_id for agent_id, _amount in payouts]
    treasury_routes_to_genesis_agent1 = "genesis_agent:01" in recipient_ids

    event_record = {
        "canonical_event_payloads": build_canonical_ejected_stake_event_payloads(result),
        "decimal_conservation_verified": decimal_conservation_verified,
        "distribution_quote": quote.to_canonical_record(),
        "ejected_validator_agent_cid": SYNTHETIC_EJECTED_VALIDATOR_AGENT_CID,
        "fail_closed_behavior_verified": fail_closed_behavior_verified,
        "guard_value": EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
        "phase": "1575l",
        "production_ejected_stake_distribution_activated": False,
        "quorum_condition_met": True,
        "redistribution_recipients": [
            {"amount": _decimal_to_string(amount), "validator_agent_cid": agent_id}
            for agent_id, amount in payouts
        ],
        "scenario": "rehearsal_4_validator_1_ejected",
        "settlement_root": settlement_root.to_canonical_record(),
        "staked_ecu_total": _decimal_to_string(quote.ejected_stake_ilc),
        "staked_ilc_total": _decimal_to_string(quote.ejected_stake_ilc),
        "treasury_amount": None,
        "treasury_routes_to_genesis_agent1": treasury_routes_to_genesis_agent1,
        "treasury_routing_rule": (
            "current_runtime_routes_ejected_stake_to_remaining_members_only_no_named_treasury_recipient"
        ),
        "version": PHASE_1575L_TOOL_VERSION,
    }
    event_record["event_record_sha256"] = sha256_stable_json(
        {k: v for k, v in event_record.items() if k != "event_record_sha256"}
    )

    certificate = {
        "carry_forward_to_guard_clearance": "requires_later_sensitive_go",
        "decimal_conservation_verified": decimal_conservation_verified,
        "double_lock_exception_type": guard_exception_type,
        "double_lock_token": EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED_TOKEN,
        "event_record_sha256": event_record["event_record_sha256"],
        "fail_closed_verified": fail_closed_behavior_verified,
        "guard": "EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED",
        "guard_cleared": False,
        "guard_value": EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
        "no_ecu_minted": True,
        "no_ilc_settled": True,
        "no_live_stake_redistribution": True,
        "no_wallet_writes": True,
        "phase": "1575l",
        "production_path_version": EJECTED_STAKE_DISTRIBUTION_PRODUCTION_PATH_VERSION,
        "rehearsal_passed": (
            decimal_conservation_verified
            and fail_closed_behavior_verified
            and not treasury_routes_to_genesis_agent1
        ),
        "settlement_root_hex": settlement_root.root_hex,
        "treasury_routing_non_genesis": not treasury_routes_to_genesis_agent1,
        "treasury_routing_rule": event_record["treasury_routing_rule"],
        "version": PHASE_1575L_TOOL_VERSION,
    }
    certificate["certificate_sha256"] = sha256_stable_json(
        {k: v for k, v in certificate.items() if k != "certificate_sha256"}
    )
    return {"certificate": certificate, "event_record": event_record}


def write_phase_1575l_evidence() -> dict[str, Any]:
    evidence = build_phase_1575l_evidence()
    write_json_atomic(EVENT_PATH, evidence["event_record"])
    write_json_atomic(CERTIFICATE_PATH, evidence["certificate"])
    return {
        "certificate_path": str(CERTIFICATE_PATH),
        "certificate_sha256": hashlib.sha256(CERTIFICATE_PATH.read_bytes()).hexdigest(),
        "event_path": str(EVENT_PATH),
        "event_sha256": hashlib.sha256(EVENT_PATH.read_bytes()).hexdigest(),
        "phase": "1575l",
        "status": "PASS",
    }


def _verify_fail_closed_behavior() -> bool:
    try:
        build_ejected_stake_distribution_result(
            {
                "distribution_epoch": SYNTHETIC_DISTRIBUTION_EPOCH,
                "ejected_stake_ilc": SYNTHETIC_EJECTED_STAKE_ILC,
                "remaining_member_stakes": SYNTHETIC_REMAINING_MEMBER_STAKES,
                "approve_votes": 1,
                "participating_voters": 1,
            }
        )
    except ValueError as exc:
        return "h_con_02_quorum_guard_minimum_voters_not_met_phase_1350" in str(exc)
    return False


def _guard_exception_type() -> str:
    try:
        require_ejected_stake_distribution_production_activation()
    except Exception as exc:
        if str(exc) != EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED_TOKEN:
            raise
        return type(exc).__name__
    raise AssertionError("ejected_stake_distribution_guard_did_not_raise")


def _decimal_to_string(value: Decimal) -> str:
    if not isinstance(value, Decimal):
        raise ValueError("amount_must_be_decimal")
    if not value.is_finite():
        raise ValueError("invalid_amount_non_finite")
    return format(value.normalize(), "f")


def _reject_float_or_non_finite(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_in_phase_1575l_evidence_rejected")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("invalid_decimal_in_phase_1575l_evidence")
        return
    if is_dataclass(value) and not isinstance(value, type):
        for field in fields(value):
            _reject_float_or_non_finite(getattr(value, field.name))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float_or_non_finite(key)
            _reject_float_or_non_finite(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_float_or_non_finite(item)


def main() -> None:
    print(stable_json(write_phase_1575l_evidence()))


if __name__ == "__main__":
    main()
