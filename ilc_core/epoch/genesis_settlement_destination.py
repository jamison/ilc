# SPDX-License-Identifier: AGPL-3.0-only
"""Genesis settlement destination binding.

Binds the CDL-029 genesis overhead pool to the canonical Genesis Agent 1
identity. Phase 1575s clears settlement/minting accounting for Option C2
settled-balance writes while keeping wallet-provider spend/transfer/withdrawal
authority disabled.
"""

from __future__ import annotations

from typing import Any

GENESIS_DESTINATION_BINDING_TOKEN = (
    "genesis_settlement_destination_bound_phase_1575c_fix3e.v0.1"
)
CDL048_TREATMENT_APPLIED_TOKEN = (
    "cdl_048_genesis_tranche_treatment_applied_phase_1575c_fix3e.v0.1"
)
GENESIS_5PCT_RETAINED_REHEARSAL_TOKEN = (
    "genesis_5pct_retained_rehearsal_1575c_fix3f.v0.1"
)
GENESIS_SETTLEMENT_DESTINATION_RUNTIME_VERSION = (
    "genesis_settlement_destination_runtime_1575c_fix3e.v0.1"
)

# The canonical Genesis Agent 1 identity from
# docs/genesis/genesis_agent1_pubkey_record_838a.txt, ceremony phase 838a
# (2026-04-25). This is an on-graph identity, not a wallet address.
GENESIS_AGENT1_AGENT_ID = (
    "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9"
)
GENESIS_AGENT1_PUBKEY_RECORD_PATH = "docs/genesis/genesis_agent1_pubkey_record_838a.txt"
GENESIS_AGENT1_PUBKEY_RECORD_CEREMONY = "838a"

# The CDL-028 genesis_burn_pool is NOT routed to this agent. As amended in
# GAP-PUBLIC-RC-CDL028-AMENDMENT-00, it is a non-circulating protocol reserve
# distinct from the CDL-029 Genesis 5% tranche.
GENESIS_BURN_POOL_NOT_ROUTED_TO_GENESIS_AGENT_TOKEN = (
    "genesis_burn_pool_not_routed_to_genesis_agent_phase_1575c_fix3e"
)

# Activation guards. Phase 1575s clears only the internal settled-balance
# accounting path; wallet-provider spend/transfer/withdrawal authority remains
# blocked until a separate wallet authority phase.
GENESIS_WALLET_WRITE_AUTHORIZED = False
GENESIS_SETTLEMENT_WRITE_AUTHORIZED = True
GENESIS_MINTING_AUTHORIZED = True

CDL_048_GENESIS_TRANCHE_TREATMENT = "explicitly_applied_by_authorized_value_path"

_FORBIDDEN_TRUE_FIELDS = frozenset(
    {
        "genesis_wallet_write_authorized",
    }
)

_REQUIRED_TRUE_FIELDS_PHASE_1575S = frozenset(
    {
        "genesis_settlement_write_authorized",
        "genesis_minting_authorized",
    }
)


def get_genesis_settlement_destination_record() -> dict[str, Any]:
    """Return the canonical genesis settlement destination record.

    This record is constitutionally bound by the CDL-048 amendment in Phase
    1575c-Fix3e and authorized for internal settled-balance accounting by Phase
    1575s. It does not authorize wallet-provider spend/transfer/withdrawal.
    """

    return {
        "agent_id": GENESIS_AGENT1_AGENT_ID,
        "pubkey_record_path": GENESIS_AGENT1_PUBKEY_RECORD_PATH,
        "pubkey_record_ceremony": GENESIS_AGENT1_PUBKEY_RECORD_CEREMONY,
        "cdl_048_genesis_tranche_treatment": CDL_048_GENESIS_TRANCHE_TREATMENT,
        "genesis_wallet_write_authorized": GENESIS_WALLET_WRITE_AUTHORIZED,
        "genesis_settlement_write_authorized": GENESIS_SETTLEMENT_WRITE_AUTHORIZED,
        "genesis_minting_authorized": GENESIS_MINTING_AUTHORIZED,
        "genesis_burn_pool_routed_to_genesis_agent": False,
        "binding_token": GENESIS_DESTINATION_BINDING_TOKEN,
        "cdl048_treatment_token": CDL048_TREATMENT_APPLIED_TOKEN,
        "runtime_version": GENESIS_SETTLEMENT_DESTINATION_RUNTIME_VERSION,
        "invariant_cert_token": "genesis_5pct_surface_reconciliation_certificate_1575c_fix3b.v0.1",
    }


def verify_genesis_settlement_destination_record(record: dict[str, Any]) -> None:
    """Verify the Genesis destination record invariants.

    Raises ValueError with a machine-readable token if any invariant is violated.
    """

    if not isinstance(record, dict):
        raise ValueError("genesis_settlement_destination_must_be_dict")
    for field in _FORBIDDEN_TRUE_FIELDS:
        if record.get(field) is not False:
            raise ValueError(f"genesis_settlement_{field}_must_be_false")
    for field in _REQUIRED_TRUE_FIELDS_PHASE_1575S:
        if record.get(field) is not True:
            raise ValueError(f"genesis_settlement_{field}_must_be_true_phase_1575s")
    if record.get("agent_id") != GENESIS_AGENT1_AGENT_ID:
        raise ValueError("genesis_settlement_agent_id_mismatch")
    if record.get("cdl_048_genesis_tranche_treatment") != (
        CDL_048_GENESIS_TRANCHE_TREATMENT
    ):
        raise ValueError("genesis_settlement_cdl048_treatment_mismatch")
    if record.get("genesis_burn_pool_routed_to_genesis_agent") is not False:
        raise ValueError("genesis_burn_pool_must_not_route_to_genesis_agent")


__all__ = [
    "CDL048_TREATMENT_APPLIED_TOKEN",
    "CDL_048_GENESIS_TRANCHE_TREATMENT",
    "GENESIS_5PCT_RETAINED_REHEARSAL_TOKEN",
    "GENESIS_AGENT1_AGENT_ID",
    "GENESIS_AGENT1_PUBKEY_RECORD_CEREMONY",
    "GENESIS_AGENT1_PUBKEY_RECORD_PATH",
    "GENESIS_BURN_POOL_NOT_ROUTED_TO_GENESIS_AGENT_TOKEN",
    "GENESIS_DESTINATION_BINDING_TOKEN",
    "GENESIS_MINTING_AUTHORIZED",
    "GENESIS_SETTLEMENT_DESTINATION_RUNTIME_VERSION",
    "GENESIS_SETTLEMENT_WRITE_AUTHORIZED",
    "GENESIS_WALLET_WRITE_AUTHORIZED",
    "get_genesis_settlement_destination_record",
    "verify_genesis_settlement_destination_record",
]
