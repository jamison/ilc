#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build the Phase 1575i treasury readiness certificate.

This tool is documentation/evidence only. It does not clear treasury guards,
write wallets, execute transfers, or submit settlement records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.epoch.epoch_emission_production_path import (
    GENESIS_FIXED_TRANCHE_FRACTION,
    GENESIS_FIXED_TRANCHE_ILC,
)
from ilc_core.epoch.epoch_emission_runtime import C_MAX_ILC
from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_DESTINATION_BINDING_TOKEN,
    GENESIS_MINTING_AUTHORIZED,
    GENESIS_SETTLEMENT_WRITE_AUTHORIZED,
    GENESIS_WALLET_WRITE_AUTHORIZED,
)
from ilc_core.epoch.treasury_governance_runtime import (
    BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET,
    BURN_FLOOR_FRACTION,
    CDL_047_DEPENDENCY,
    PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN,
    TREASURY_GOVERNANCE_RUNTIME_VERSION,
    VELOCITY_ALERT_FLOOR,
)
from ilc_core.epoch.treasury_validator_reward_production_path import (
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
    TREASURY_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    TREASURY_VALIDATOR_REWARD_PRODUCTION_PATH_VERSION,
)
from ilc_core.epoch.validator_reward_pool_routing_runtime import (
    CDL_054_DEPENDENCY,
    VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN,
    VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION,
)


PHASE = "1575i"
SCHEMA_VERSION = "ilc.treasury_readiness_certificate.1575i.v1"
READINESS_VERDICT = "ready_for_1575k_design_decision_no_activation"
GENERATED_AT_SOURCE = "deterministic_static_phase_1575i"

OUTPUT_TOKENS = (
    "treasury_role_reconciliation_committed_phase_1575i",
    "treasury_no_wallet_write_readiness_certificate_phase_1575i",
    "treasury_genesis_non_overlap_confirmed_phase_1575i",
    "treasury_guard_not_cleared_phase_1575i",
)


def _decimal_to_string(value: Decimal) -> str:
    if not isinstance(value, Decimal):
        raise ValueError("value_must_be_decimal")
    if not value.is_finite():
        raise ValueError("decimal_value_must_be_finite")
    return format(value.normalize(), "f")


def stable_json(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


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


def build_treasury_readiness_certificate() -> dict[str, Any]:
    """Return the canonical Phase 1575i readiness certificate payload."""

    return {
        "authorities": {
            "treasury_governance": {
                "cdl": "CDL-047",
                "dependency_token": CDL_047_DEPENDENCY,
                "status": "ratified",
                "runtime_version": TREASURY_GOVERNANCE_RUNTIME_VERSION,
            },
            "validator_reward_routing": {
                "cdl": "CDL-054",
                "dependency_token": CDL_054_DEPENDENCY,
                "status": "ratified",
                "runtime_version": VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_VERSION,
            },
            "genesis_fixed_tranche": {
                "cdl": "CDL-029",
                "fraction": _decimal_to_string(GENESIS_FIXED_TRANCHE_FRACTION),
                "cap_ilc": _decimal_to_string(GENESIS_FIXED_TRANCHE_ILC),
                "destination_binding_token": GENESIS_DESTINATION_BINDING_TOKEN,
            },
        },
        "constraints": {
            "bounty_cap_fraction_of_epoch_budget": _decimal_to_string(
                BOUNTY_CAP_FRACTION_OF_EPOCH_BUDGET
            ),
            "burn_floor_fraction": _decimal_to_string(BURN_FLOOR_FRACTION),
            "velocity_alert_floor": _decimal_to_string(VELOCITY_ALERT_FLOOR),
            "validator_reward_fraction_of_write_fee_burn": _decimal_to_string(
                VALIDATOR_REWARD_FRACTION_OF_WRITE_FEE_BURN
            ),
            "cmax_ilc": _decimal_to_string(C_MAX_ILC),
        },
        "destination_requirements": {
            "treasury_destination_class": "governance_controlled_account_pending_1575k",
            "treasury_live_wallet_address": None,
            "validator_reward_destination_class": (
                "validator_destination_registry_pending_1575j_1575k"
            ),
            "must_not_default_to_genesis_agent1": True,
        },
        "genesis_non_overlap": {
            "genesis_agent1_agent_id": GENESIS_AGENT1_AGENT_ID,
            "genesis_5pct_is_bootstrap_fixed_tranche": True,
            "treasury_is_long_term_network_maintenance_lane": True,
            "treasury_routes_to_genesis_agent1_by_default": False,
            "requires_separate_cdl_to_route_treasury_to_genesis_identity": True,
        },
        "guard_state": {
            "treasury_distribution_not_activated": TREASURY_DISTRIBUTION_NOT_ACTIVATED,
            "treasury_distribution_guard_token": TREASURY_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
            "production_treasury_guard_token": PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN,
            "validator_reward_distribution_guard_token": (
                VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN
            ),
            "genesis_wallet_write_authorized": GENESIS_WALLET_WRITE_AUTHORIZED,
            "genesis_settlement_write_authorized": GENESIS_SETTLEMENT_WRITE_AUTHORIZED,
            "genesis_minting_authorized": GENESIS_MINTING_AUTHORIZED,
        },
        "non_claims": {
            "clears_treasury_guard": False,
            "activates_treasury_distribution": False,
            "writes_wallet": False,
            "executes_transfer": False,
            "executes_settlement": False,
            "routes_treasury_to_genesis": False,
            "public_mirror_updated": False,
            "epoch_transition_executed": False,
        },
        "output_tokens": list(OUTPUT_TOKENS),
        "phase": PHASE,
        "readiness_verdict": READINESS_VERDICT,
        "schema_version": SCHEMA_VERSION,
        "source_pools": [
            {
                "name": "fee_revenue",
                "status": "treasury_source_candidate",
                "authority": "CDL-047/CDL-028",
            },
            {
                "name": "transfer_tax_revenue",
                "status": "treasury_source_candidate",
                "authority": "ADR-0015/CDL-047",
            },
            {
                "name": "governed_bounty_budget",
                "status": "ecu_side_credit_governor",
                "authority": "ADR-0016/CDL-047",
            },
            {
                "name": "node_reversion_or_ejected_stake_routes",
                "status": "conditional_on_later_runtime_readiness",
                "authority": "ADR-0015/CDL-083/1575l",
            },
            {
                "name": "genesis_fixed_5pct_tranche",
                "status": "excluded_from_treasury_default_routes",
                "authority": "CDL-029/1575c-Fix3e",
            },
        ],
        "generated_at_source": GENERATED_AT_SOURCE,
    }


def verify_treasury_readiness_certificate(certificate: dict[str, Any]) -> None:
    if certificate.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("treasury_readiness_schema_version_mismatch")
    if certificate.get("phase") != PHASE:
        raise ValueError("treasury_readiness_phase_mismatch")
    if certificate.get("readiness_verdict") != READINESS_VERDICT:
        raise ValueError("treasury_readiness_verdict_mismatch")
    guards = certificate.get("guard_state")
    if not isinstance(guards, dict):
        raise ValueError("treasury_readiness_guard_state_missing")
    if guards.get("treasury_distribution_not_activated") is not True:
        raise ValueError("treasury_guard_must_remain_not_activated")
    if not isinstance(guards.get("genesis_wallet_write_authorized"), bool):
        raise ValueError("genesis_wallet_write_authorized_guard_state_must_be_bool")
    for key in ("genesis_settlement_write_authorized", "genesis_minting_authorized"):
        if not isinstance(guards.get(key), bool):
            raise ValueError(f"{key}_guard_state_must_be_bool")
    non_claims = certificate.get("non_claims")
    if not isinstance(non_claims, dict):
        raise ValueError("treasury_readiness_non_claims_missing")
    for key, value in non_claims.items():
        if value is not False:
            raise ValueError(f"non_claim_must_be_false:{key}")
    non_overlap = certificate.get("genesis_non_overlap")
    if not isinstance(non_overlap, dict):
        raise ValueError("treasury_readiness_non_overlap_missing")
    if non_overlap.get("treasury_routes_to_genesis_agent1_by_default") is not False:
        raise ValueError("treasury_must_not_default_route_to_genesis")
    destinations = certificate.get("destination_requirements")
    if not isinstance(destinations, dict):
        raise ValueError("treasury_readiness_destinations_missing")
    if destinations.get("treasury_live_wallet_address") is not None:
        raise ValueError("treasury_live_wallet_address_must_not_be_set_phase_1575i")


def certificate_sha256(certificate: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json(certificate).encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    certificate = build_treasury_readiness_certificate()
    verify_treasury_readiness_certificate(certificate)
    atomic_write_json(args.out, certificate)
    print(certificate_sha256(certificate))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
