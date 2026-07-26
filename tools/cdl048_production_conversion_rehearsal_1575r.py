#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1575r CDL-048 production conversion rehearsal.

This is an isolated private rehearsal caller. It does not mutate wallet,
settlement, validator, or public mirror state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from ilc_core.consensus.attribution_batch_bridge import (
    ATTRIBUTION_BATCH_BRIDGE_VERSION,
    build_attribution_batch_from_claims,
)
from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    AttributionEvent,
    settle_attribution_batch,
)
from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
    CDL048_ACTIVATION_RUNTIME_VERSION,
    CONVERSION_SWEEPER_NO_PUBLIC_CLAIMABILITY_TOKEN,
    WALLET_WITHDRAWAL_TRANSFER_SPEND_BLOCKED_TOKEN,
    build_cdl048_dry_run_wire_quote,
    conversion_dry_run_wire_quote_payload,
    conversion_sweeper_state_root,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    REUSE_ATTRIBUTION_RATE,
)


PHASE = "1575r"
SCHEMA_VERSION = "ilc.phase1575r.cdl048_production_conversion_rehearsal.v1"
ECU_LOTS_SCHEMA_VERSION = "ilc.phase1575r.ecu_lots.v1"
REHEARSAL_RECEIPT_SCHEMA_VERSION = "ilc.phase1575r.cdl048_rehearsal_receipt.v1"
ISSUE_EPOCH = 49
CONVERSION_EPOCH = 53
PROPOSED_P_E = Decimal("1.00")
OUTPUT_TOKENS = (
    "cdl048_production_conversion_rehearsal_committed_phase_1575r",
    "cdl048_double_entry_conservation_proven_rehearsal_phase_1575r",
    "cdl048_public_rc_exclude_disposition_phase_1575r",
    "cdl048_activation_token_live_in_production_caller_phase_1575r",
    "cdl048_wire_quote_activation_rehearsed_phase_1575r",
    "cdl048_conversion_receipt_activation_deferred_phase_1575r",
)
NON_CLAIMS = {
    "activates_public_claimability": False,
    "clears_wallet_withdrawal": False,
    "clears_wallet_transfer": False,
    "clears_wallet_spend": False,
    "pushes_public_mirror": False,
    "executes_mainnet": False,
    "mints_genesis_ilc": False,
    "changes_cdl048_parameters": False,
    "implies_global_production_activation": False,
    "writes_wallet_state": False,
    "writes_settlement_state": False,
}
PHASE_1560_AGENT_INIT_PATH = Path("out/agent_init_ceremony_1560.json")


def stable_json(payload: Any) -> str:
    _reject_float_tree(payload)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def stable_sha256(payload: Any) -> str:
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, stable_json(payload) + "\n")


def _reject_float_tree(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_forbidden_in_phase_1575r_evidence")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("non_finite_decimal_forbidden_phase_1575r")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float_tree(key)
            _reject_float_tree(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_float_tree(item)


def _require_agent_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("phase1575r_agent_id_must_be_string")
    normalized = value.strip().lower()
    if len(normalized) != 96 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError("phase1575r_agent_id_must_be_96_lower_hex")
    if normalized.startswith("soak_agent_"):
        raise ValueError("phase1575r_soak_agent_ids_forbidden")
    return normalized


def load_phase1560_agent_ids(path: Path = PHASE_1560_AGENT_INIT_PATH) -> tuple[str, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("phase1560_agent_init_payload_must_be_list")
    agent_ids: list[str] = []
    for host in payload:
        if not isinstance(host, dict):
            raise ValueError("phase1560_agent_init_host_must_be_object")
        agents = host.get("agents")
        if not isinstance(agents, list):
            raise ValueError("phase1560_agent_init_agents_must_be_list")
        for agent in agents:
            if not isinstance(agent, dict):
                raise ValueError("phase1560_agent_init_agent_must_be_object")
            agent_ids.append(_require_agent_id(agent.get("agent_id")))
    if len(agent_ids) < 4:
        raise ValueError("phase1575r_requires_at_least_four_phase1560_agent_ids")
    return tuple(agent_ids[:4])


def build_accepted_claim_payload(
    agent_ids: tuple[str, ...],
    *,
    epoch: int = ISSUE_EPOCH,
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = []
    for index, agent_id in enumerate(agent_ids):
        claims.append(
            {
                "agent_id": agent_id,
                "amount": decimal_to_canonical_string(REUSE_ATTRIBUTION_RATE),
                "claim_id": f"phase1575r:reuse:{index}:{agent_id[:16]}",
                "epoch": epoch,
                "event_type": EdgeType.REUSE.value,
            }
        )
        claims.append(
            {
                "agent_id": agent_id,
                "amount": decimal_to_canonical_string(REUSE_ATTRIBUTION_RATE),
                "claim_id": f"phase1575r:provenance:{index}:{agent_id[:16]}",
                "epoch": epoch,
                "event_type": EdgeType.PROVENANCE.value,
            }
        )
    claims.append(
        {
            "agent_id": agent_ids[0],
            "amount": decimal_to_canonical_string(REUSE_ATTRIBUTION_RATE),
            "claim_id": f"phase1575r:coauth:{agent_ids[0][:16]}",
            "epoch": epoch,
            "event_type": EdgeType.CO_AUTHORSHIP.value,
        }
    )
    return {
        "claims": claims,
        "marker": "agent_loop_claims_ok",
        "schema_version": "ilc.phase1575r.accepted_claim_payload.v1",
    }


def build_epoch_attribution_batch(
    agent_ids: tuple[str, ...],
    *,
    epoch: int = ISSUE_EPOCH,
) -> tuple[EpochAttributionBatch, dict[str, dict[str, Decimal]], dict[str, Any]]:
    batch = EpochAttributionBatch(epoch=epoch)
    manifest_events: list[dict[str, Any]] = []

    for index, agent_id in enumerate(agent_ids):
        star_node_id = f"phase1575r_reuse_star_{index:02d}"
        batch.add_event(
            AttributionEvent(
                edge_type=EdgeType.REUSE,
                target_creator_id=agent_id,
                star_node_id=star_node_id,
                epoch=epoch,
            )
        )
        manifest_events.append(
            {
                "edge_type": EdgeType.REUSE.value,
                "epoch": epoch,
                "star_node_id": star_node_id,
                "target_creator_id": agent_id,
            }
        )

    for index in range(len(agent_ids)):
        chain = tuple(
            (
                f"phase1575r_provenance_node_{index:02d}_{hop:02d}",
                agent_ids[(index + hop) % len(agent_ids)],
            )
            for hop in range(3)
        )
        batch.add_event(
            AttributionEvent(
                edge_type=EdgeType.PROVENANCE,
                target_creator_id=agent_ids[index],
                star_node_id=f"phase1575r_provenance_star_{index:02d}",
                epoch=epoch,
                provenance_chain=chain,
            )
        )
        manifest_events.append(
            {
                "edge_type": EdgeType.PROVENANCE.value,
                "epoch": epoch,
                "provenance_chain": [
                    {"creator_id": creator_id, "node_id": node_id}
                    for node_id, creator_id in chain
                ],
                "star_node_id": f"phase1575r_provenance_star_{index:02d}",
                "target_creator_id": agent_ids[index],
            }
        )

    stake_map = {
        "phase1575r_coauth_star": {
            agent_ids[0]: Decimal("1"),
            agent_ids[1]: Decimal("2"),
            agent_ids[2]: Decimal("3"),
            agent_ids[3]: Decimal("5"),
        }
    }
    batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.CO_AUTHORSHIP,
            target_creator_id=agent_ids[0],
            star_node_id="phase1575r_coauth_star",
            epoch=epoch,
        )
    )
    manifest_events.append(
        {
            "edge_type": EdgeType.CO_AUTHORSHIP.value,
            "epoch": epoch,
            "star_node_id": "phase1575r_coauth_star",
            "target_creator_id": agent_ids[0],
        }
    )
    batch.seal()
    manifest = {
        "agent_ids": list(agent_ids),
        "epoch": epoch,
        "events": manifest_events,
        "provenance_decay_alpha": decimal_to_canonical_string(PROVENANCE_DECAY_ALPHA),
        "reuse_attribution_rate": decimal_to_canonical_string(REUSE_ATTRIBUTION_RATE),
        "schema_version": "ilc.phase1575r.attribution_event_manifest.v1",
        "stake_map": {
            star_node_id: {
                agent_id: decimal_to_canonical_string(stake)
                for agent_id, stake in sorted(members.items())
            }
            for star_node_id, members in sorted(stake_map.items())
        },
    }
    return batch, stake_map, manifest


def build_ecu_lot_records() -> dict[str, Any]:
    agent_ids = load_phase1560_agent_ids()
    accepted_claim_payload = build_accepted_claim_payload(agent_ids)
    bridge_payload = build_attribution_batch_from_claims(
        accepted_claim_payload,
        epoch=ISSUE_EPOCH,
    )
    batch, stake_map, attribution_manifest = build_epoch_attribution_batch(agent_ids)
    emitted_tokens: list[str] = []
    payouts = settle_attribution_batch(
        batch,
        stake_map=stake_map,
        emitted_tokens=emitted_tokens,
        epoch_node_mint_count=len(batch.events) * 4,
    )
    aggregated: defaultdict[str, Decimal] = defaultdict(Decimal)
    for agent_id, amount in payouts:
        if not isinstance(amount, Decimal) or not amount.is_finite():
            raise ValueError("phase1575r_payout_must_be_finite_decimal")
        if amount <= Decimal("0"):
            continue
        aggregated[_require_agent_id(agent_id)] += amount

    bridge_sha256 = stable_sha256(bridge_payload)
    attribution_manifest_sha256 = stable_sha256(attribution_manifest)
    lots: list[dict[str, Any]] = []
    for agent_id in sorted(aggregated):
        amount = aggregated[agent_id]
        lot_preimage = {
            "agent_id": agent_id,
            "amount_ecu": decimal_to_canonical_string(amount),
            "attribution_manifest_sha256": attribution_manifest_sha256,
            "bridge_sha256": bridge_sha256,
            "issue_epoch": ISSUE_EPOCH,
            "phase": PHASE,
        }
        lot_id = f"cdl048:1575r:{ISSUE_EPOCH}:{hashlib.sha256(stable_json(lot_preimage).encode('utf-8')).hexdigest()}"
        lots.append(
            {
                "agent_id": agent_id,
                "amount_ecu": decimal_to_canonical_string(amount),
                "deadline_epoch": ISSUE_EPOCH + 4,
                "funding_provenance": [
                    f"attribution_batch_bridge_sha256:{bridge_sha256}",
                    f"attribution_manifest_sha256:{attribution_manifest_sha256}",
                    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
                ],
                "issue_epoch": ISSUE_EPOCH,
                "lot_id": lot_id,
                "origin": "phase_1575r_epoch_attribution_settle_runtime",
            }
        )

    return {
        "accepted_claim_payload": accepted_claim_payload,
        "agent_id_source": str(PHASE_1560_AGENT_INIT_PATH),
        "attribution_batch_bridge": bridge_payload,
        "attribution_batch_bridge_sha256": bridge_sha256,
        "attribution_event_manifest": attribution_manifest,
        "attribution_event_manifest_sha256": attribution_manifest_sha256,
        "attribution_settle_runtime_version": EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
        "conversion_epoch": CONVERSION_EPOCH,
        "ecu_lot_count": len(lots),
        "emitted_tokens": emitted_tokens,
        "issue_epoch": ISSUE_EPOCH,
        "lots": lots,
        "phase": PHASE,
        "schema_version": ECU_LOTS_SCHEMA_VERSION,
        "source_runtime_versions": {
            "attribution_batch_bridge": ATTRIBUTION_BATCH_BRIDGE_VERSION,
            "epoch_attribution_settle_runtime": EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
        },
    }


def _prefixed_sha(prefix: str, payload: Any) -> str:
    return f"{prefix}:{stable_sha256(payload)}"


def _register_lots(lot_records: list[dict[str, Any]]):
    state = empty_conversion_sweeper_state()
    for lot in lot_records:
        state = register_ecu_lot(
            state,
            lot_id=lot["lot_id"],
            agent_id=lot["agent_id"],
            amount_ecu=lot["amount_ecu"],
            issue_epoch=lot["issue_epoch"],
            origin=lot["origin"],
            funding_provenance=tuple(lot["funding_provenance"]),
        )
    return state


def build_rehearsal_evidence() -> dict[str, Any]:
    lot_dataset = build_ecu_lot_records()
    state = _register_lots(lot_dataset["lots"])
    state_root_before = conversion_sweeper_state_root(state)

    quote_payloads: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    for lot in lot_dataset["lots"]:
        wallet_state_root = _prefixed_sha(
            "wallet_state_sha256",
            {
                "agent_id": lot["agent_id"],
                "lot_id": lot["lot_id"],
                "phase": PHASE,
                "purpose": "private_rehearsal_wallet_read_model_root_only",
            },
        )
        settled_runtime_root = _prefixed_sha(
            "settled_runtime_sha256",
            {
                "agent_id": lot["agent_id"],
                "amount_ecu": lot["amount_ecu"],
                "conversion_epoch": CONVERSION_EPOCH,
                "lot_id": lot["lot_id"],
                "phase": PHASE,
            },
        )
        quote = build_cdl048_dry_run_wire_quote(
            state,
            lot_id=lot["lot_id"],
            agent_id=lot["agent_id"],
            conversion_epoch=CONVERSION_EPOCH,
            settled_runtime_epoch=CONVERSION_EPOCH,
            wallet_state_root=wallet_state_root,
            settled_runtime_root=settled_runtime_root,
            proposed_p_e=PROPOSED_P_E,
            activation_requested=True,
        )
        quote_payload = conversion_dry_run_wire_quote_payload(quote)
        if CDL048_ACTIVATED_PHASE_1388_TOKEN not in quote_payload["tokens"]:
            raise ValueError("phase1575r_activation_token_missing")
        if quote_payload["conversion_activation_authorized"] is not True:
            raise ValueError("phase1575r_conversion_activation_not_authorized")
        if quote_payload["ledger_write_authorized"] is not True:
            raise ValueError("phase1575r_ledger_write_not_authorized")
        receipt = {
            "agent_id": lot["agent_id"],
            "amount_ecu": quote_payload["amount_ecu_debit"],
            "amount_ilc_equivalent": quote_payload["amount_ilc_credit"],
            "conversion_epoch": quote_payload["conversion_epoch"],
            "conversion_receipt_not_activated": True,
            "ecu_mint_authorized": False,
            "ilc_settlement_authorized": False,
            "lot_id": lot["lot_id"],
            "public_claimability_activated": False,
            "rehearsal_receipt_sha256": stable_sha256(
                {
                    "agent_id": lot["agent_id"],
                    "amount_ecu": quote_payload["amount_ecu_debit"],
                    "amount_ilc_equivalent": quote_payload["amount_ilc_credit"],
                    "conversion_epoch": quote_payload["conversion_epoch"],
                    "lot_id": lot["lot_id"],
                    "source_quote_sha256": stable_sha256(quote_payload),
                }
            ),
            "runtime_version": REHEARSAL_RECEIPT_SCHEMA_VERSION,
            "source_quote_runtime_version": quote_payload["runtime_version"],
            "source_quote_sha256": stable_sha256(quote_payload),
            "wallet_spend_enabled": False,
            "wallet_transfer_enabled": False,
            "wallet_withdrawal_enabled": False,
        }
        quote_payloads.append(quote_payload)
        receipts.append(receipt)

    total_ecu = sum((Decimal(receipt["amount_ecu"]) for receipt in receipts), Decimal("0"))
    total_ilc = sum(
        (Decimal(receipt["amount_ilc_equivalent"]) for receipt in receipts),
        Decimal("0"),
    )
    if total_ecu != total_ilc:
        raise ValueError("phase1575r_double_entry_conservation_failed")

    payload: dict[str, Any] = {
        "activation_boundary": {
            "activation_token": CDL048_ACTIVATED_PHASE_1388_TOKEN,
            "activation_token_live_in_this_private_rehearsal_caller": True,
            "global_production_activation_claimed": False,
            "source_runtime_version": CDL048_ACTIVATION_RUNTIME_VERSION,
        },
        "double_entry_conservation": {
            "canonical_conversion_rate_p_e": decimal_to_canonical_string(PROPOSED_P_E),
            "conservation_delta_ilc": decimal_to_canonical_string(total_ecu - total_ilc),
            "proven": total_ecu == total_ilc,
            "total_ecu_in": decimal_to_canonical_string(total_ecu),
            "total_ilc_equivalent_out": decimal_to_canonical_string(total_ilc),
        },
        "ecu_lot_dataset": lot_dataset,
        "generated_at_source": "deterministic_phase_1575r",
        "non_claims": NON_CLAIMS,
        "output_tokens": list(OUTPUT_TOKENS),
        "phase": PHASE,
        "public_rc_exclude_disposition": {
            "disposition": "retained_existing_header_unchanged",
            "path": "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
            "public_rc_exclude_removal_authorized": False,
            "required_future_gate": "phase_1575t_complete_and_public_rc_authorized",
            "token": "cdl048_public_rc_exclude_disposition_phase_1575r",
        },
        "quote_payloads": quote_payloads,
        "rehearsal_receipts": receipts,
        "schema_version": SCHEMA_VERSION,
        "source_expansion_disposition": {
            "conversion_receipt_dataclass_guard_fields_remain_false": True,
            "production_rehearsal_receipts_derived_from_activated_wire_quotes": True,
            "reason": "ConversionReceipt validation forbids true authorization fields; activated sweeper evidence is exposed by ConversionDryRunWireQuote.",
        },
        "phase_1575s_gate_evidence": {
            "candidate_set_non_empty": bool(receipts),
            "conversion_rate_readable": all(
                "effective_p_e" in quote for quote in quote_payloads
            ),
            "output_format": REHEARSAL_RECEIPT_SCHEMA_VERSION,
            "output_format_stable_canonical": True,
            "ready_for_1575s": bool(receipts),
        },
        "sweeper_state_root_before": state_root_before,
        "sweeper_state_root_after": conversion_sweeper_state_root(state),
    }
    payload["evidence_payload_sha256"] = stable_sha256(payload)
    return payload


def verify_rehearsal_evidence(evidence: dict[str, Any]) -> None:
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("phase1575r_schema_version_mismatch")
    if evidence.get("generated_at_source") != "deterministic_phase_1575r":
        raise ValueError("phase1575r_generated_at_source_mismatch")
    expected_digest = evidence.get("evidence_payload_sha256")
    body = dict(evidence)
    body.pop("evidence_payload_sha256", None)
    if expected_digest != stable_sha256(body):
        raise ValueError("phase1575r_evidence_payload_digest_mismatch")
    conservation = evidence.get("double_entry_conservation")
    if not isinstance(conservation, dict) or conservation.get("proven") is not True:
        raise ValueError("phase1575r_conservation_not_proven")
    if Decimal(conservation["total_ecu_in"]) != Decimal(conservation["total_ilc_equivalent_out"]):
        raise ValueError("phase1575r_double_entry_conservation_failed")
    for field, value in evidence.get("non_claims", {}).items():
        if value is not False:
            raise ValueError(f"phase1575r_non_claim_must_be_false:{field}")
    for quote in evidence.get("quote_payloads", []):
        if CDL048_ACTIVATED_PHASE_1388_TOKEN not in quote.get("tokens", []):
            raise ValueError("phase1575r_activation_token_missing")
        if quote.get("conversion_activation_authorized") is not True:
            raise ValueError("phase1575r_conversion_activation_not_authorized")
        if quote.get("public_claimability_activated") is not False:
            raise ValueError("phase1575r_public_claimability_forbidden")
    for receipt in evidence.get("rehearsal_receipts", []):
        if receipt.get("conversion_receipt_not_activated") is not True:
            raise ValueError("phase1575r_conversion_receipt_activation_boundary_missing")
        if receipt.get("ecu_mint_authorized") is not False:
            raise ValueError("phase1575r_ecu_mint_authorization_forbidden")
        if receipt.get("ilc_settlement_authorized") is not False:
            raise ValueError("phase1575r_ilc_settlement_authorization_forbidden")
        for field in (
            "wallet_withdrawal_enabled",
            "wallet_transfer_enabled",
            "wallet_spend_enabled",
            "public_claimability_activated",
        ):
            if receipt.get(field) is not False:
                raise ValueError(f"phase1575r_receipt_boundary_field_must_be_false:{field}")
    gate = evidence.get("phase_1575s_gate_evidence")
    if not isinstance(gate, dict) or gate.get("ready_for_1575s") is not True:
        raise ValueError("phase1575r_gate_evidence_missing")
    if gate.get("candidate_set_non_empty") is not True:
        raise ValueError("phase1575r_candidate_set_empty")
    if gate.get("conversion_rate_readable") is not True:
        raise ValueError("phase1575r_conversion_rate_not_readable")
    if gate.get("output_format_stable_canonical") is not True:
        raise ValueError("phase1575r_output_format_not_stable")


def run_rehearsal(output_root: Path) -> dict[str, Any]:
    evidence = build_rehearsal_evidence()
    verify_rehearsal_evidence(evidence)
    lot_dataset = evidence["ecu_lot_dataset"]
    output_root.mkdir(parents=True, exist_ok=True)
    ecu_lots_path = output_root / "ecu_lots.json"
    evidence_path = output_root / "rehearsal_evidence.json"
    sha_path = output_root / "evidence_sha256.txt"
    atomic_write_json(ecu_lots_path, lot_dataset)
    atomic_write_json(evidence_path, evidence)
    atomic_write_text(sha_path, file_sha256(evidence_path) + "\n")
    return {
        "ecu_lots_path": str(ecu_lots_path),
        "evidence_path": str(evidence_path),
        "evidence_sha256": file_sha256(evidence_path),
        "evidence_sha256_path": str(sha_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("out/cdl048_production_conversion_rehearsal_1575r"),
    )
    args = parser.parse_args()
    result = run_rehearsal(args.output_root)
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
