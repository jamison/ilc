# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1568-Fix2b-3 Python-to-Rust attribution batch bridge.

This module converts accepted agent-loop ECU claim payloads into the narrow
JSON shape consumed by the Rust `attribution_batch_ingest` binary. It is not a
review, jury, CDL-048, ILC allocation, or settlement-root runtime.

GAP-ECU-04b extension point: when backward-attribution traversal is ratified
and implemented, this bridge schema is the place to add a `provenance_chain`
field. Until then, provenance fields are intentionally absent so fixed
per-event provenance cannot masquerade as graph-derived backward attribution.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from pathlib import Path
from typing import Any

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string
from ilc_core.economics.backward_attribution_traversal import (
    BACKWARD_ATTRIBUTION_CDL_VERSION,
    BACKWARD_ATTRIBUTION_SYBIL_DIVERSITY_GUARD_CDL_GAP,
    BackwardAttributionTraversal,
)
from ilc_core.economics.werner_attribution_bridge import (
    WERNER_APPLICATION_STAGE,
    WERNER_BRIDGE_SCOPE,
    WERNER_CDL_109_VERSION,
    WernerAttributionContext,
)

ATTRIBUTION_BATCH_BRIDGE_VERSION = "attribution_batch_bridge_1568_fix2b3.v0.1"
MICRO_ECU_PER_ECU = Decimal("1000000")
MAX_CLAIMS_PER_BATCH = 10_000
MAX_BACKWARD_ATTRIBUTION_EVENTS_PER_BATCH = 1_000
MAX_U64 = 18_446_744_073_709_551_615
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
ATTRIBUTION_EVENT_LOG_KEY_PREFIX = b"attr_event:"


class AttributionBatchBridgeError(ValueError):
    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _require_dict(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AttributionBatchBridgeError(f"{name}_must_be_object", f"{name} must be an object")
    return value


def _require_claims(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise AttributionBatchBridgeError(
            "accepted_claims_required",
            "accepted claim payload must contain at least one claim",
        )
    if len(value) > MAX_CLAIMS_PER_BATCH:
        raise AttributionBatchBridgeError(
            "claim_count_exceeds_maximum",
            f"accepted claim payload exceeds maximum of {MAX_CLAIMS_PER_BATCH} claims",
        )
    claims: list[dict[str, Any]] = []
    for item in value:
        claims.append(_require_dict("claim", item))
    return claims


def _require_epoch(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AttributionBatchBridgeError("claim_epoch_must_be_non_negative_int", "claim epoch must be >= 0")
    return value


def _require_agent_id(value: Any) -> str:
    if not isinstance(value, str):
        raise AttributionBatchBridgeError("agent_id_hex_must_be_96_lower_hex", "agent_id must be a hex string")
    normalized = value.strip().lower()
    if not _AGENT_ID_RE.fullmatch(normalized):
        raise AttributionBatchBridgeError(
            "agent_id_hex_must_be_96_lower_hex",
            "agent_id must be 96 lowercase hex characters",
        )
    return normalized


def _require_optional_sha256_hex(value: Any, token: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise AttributionBatchBridgeError(token, "root must be a lowercase 64-hex string")
    normalized = value.strip()
    if not _SHA256_HEX_RE.fullmatch(normalized):
        raise AttributionBatchBridgeError(token, "root must be a lowercase 64-hex string")
    return normalized


def _require_decimal_amount(value: Any) -> Decimal:
    if isinstance(value, (bool, float)):
        raise AttributionBatchBridgeError("claim_amount_must_be_exact_decimal", "claim amount must be exact")
    if not isinstance(value, (Decimal, int, str)):
        raise AttributionBatchBridgeError("claim_amount_must_be_exact_decimal", "claim amount must be exact")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AttributionBatchBridgeError("claim_amount_must_be_exact_decimal", "claim amount must be exact") from exc
    if not amount.is_finite() or amount <= Decimal("0"):
        raise AttributionBatchBridgeError(
            "claim_amount_must_be_positive_finite",
            "claim amount must be positive and finite",
        )
    return amount


def _require_werner_pressure(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, (bool, float)):
        raise AttributionBatchBridgeError(
            "werner_raw_pressure_must_be_exact_decimal",
            "Werner pressure must be exact",
        )
    if not isinstance(value, (Decimal, int, str)):
        raise AttributionBatchBridgeError(
            "werner_raw_pressure_must_be_exact_decimal",
            "Werner pressure must be exact",
        )
    try:
        pressure = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AttributionBatchBridgeError(
            "werner_raw_pressure_must_be_exact_decimal",
            "Werner pressure must be exact",
        ) from exc
    if not pressure.is_finite() or pressure < Decimal("0"):
        raise AttributionBatchBridgeError(
            "werner_raw_pressure_must_be_non_negative_finite",
            "Werner pressure must be non-negative and finite",
        )
    return pressure


def _amount_to_micro_ecu(amount: Decimal) -> tuple[int, Decimal]:
    scaled = amount * MICRO_ECU_PER_ECU
    floored = scaled.to_integral_value(rounding=ROUND_FLOOR)
    if floored <= 0:
        raise AttributionBatchBridgeError(
            "claim_amount_below_one_micro_ecu",
            "claim amount floors to zero micro-ECU",
        )
    if floored > MAX_U64:
        raise AttributionBatchBridgeError(
            "claim_amount_micro_ecu_exceeds_u64",
            "claim amount exceeds Rust u64 micro-ECU boundary",
        )
    dust = (scaled - floored) / MICRO_ECU_PER_ECU
    return int(floored), dust


def _append_amount(
    aggregated: dict[str, dict[str, Any]],
    *,
    agent_id: str,
    amount: Decimal,
    source_id: str,
) -> tuple[int, Decimal]:
    micro_amount, dust = _amount_to_micro_ecu(amount)
    entry = aggregated.setdefault(
        agent_id,
        {
            "agent_id_hex": agent_id,
            "amount_micro_ecu": 0,
            "source_amount_ecu": Decimal("0"),
            "source_claim_ids": [],
            "dust_ecu": Decimal("0"),
        },
    )
    entry["amount_micro_ecu"] += micro_amount
    entry["source_amount_ecu"] += amount
    entry["dust_ecu"] += dust
    entry["source_claim_ids"].append(source_id)
    return micro_amount, dust


def _require_backward_graph_context(value: Any) -> dict[str, Any]:
    context = _require_dict("backward_attribution_graph_context", value)
    if not isinstance(context.get("nodes"), dict):
        raise AttributionBatchBridgeError(
            "backward_attribution_nodes_required",
            "backward attribution graph context requires nodes",
        )
    if not isinstance(context.get("edges"), list):
        raise AttributionBatchBridgeError(
            "backward_attribution_edges_required",
            "backward attribution graph context requires edges",
        )
    if not isinstance(context.get("events"), list) or not context["events"]:
        raise AttributionBatchBridgeError(
            "backward_attribution_events_required",
            "backward attribution graph context requires events",
        )
    if len(context["events"]) > MAX_BACKWARD_ATTRIBUTION_EVENTS_PER_BATCH:
        raise AttributionBatchBridgeError(
            "backward_attribution_event_count_exceeds_maximum",
            "backward attribution graph context contains too many events",
        )
    return context


def _require_werner_context_by_agent_id(
    value: Any,
) -> dict[str, WernerAttributionContext]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise AttributionBatchBridgeError(
            "werner_context_by_agent_id_must_be_object",
            "Werner context must be keyed by agent id",
        )
    contexts: dict[str, WernerAttributionContext] = {}
    for raw_agent_id, raw_context in value.items():
        agent_id = _require_agent_id(raw_agent_id)
        context = _require_dict("werner_context", raw_context)
        declared_agent_id = context.get("agent_id")
        if declared_agent_id is not None and _require_agent_id(declared_agent_id) != agent_id:
            raise AttributionBatchBridgeError(
                "werner_context_agent_id_mismatch",
                "Werner context agent_id must match its map key",
            )
        contexts[agent_id] = WernerAttributionContext(
            agent_id=agent_id,
            epoch=_require_epoch(context.get("epoch")),
            raw_werner_pressure=_require_werner_pressure(
                context.get("raw_werner_pressure"),
            ),
        )
    return contexts


def _require_backward_event(value: Any) -> dict[str, Any]:
    event = _require_dict("backward_attribution_event", value)
    _require_non_empty_bridge_string(event.get("event_id"), "backward_event_id_required")
    _require_non_empty_bridge_string(
        event.get("source_node_id"),
        "backward_source_node_id_required",
    )
    _require_epoch(event.get("event_epoch"))
    _require_decimal_amount(event.get("event_budget_ecu"))
    return event


def _require_non_empty_bridge_string(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AttributionBatchBridgeError(token, token)
    return value.strip()


def _attribution_event_log_key(epoch: int, ordinal: int) -> str:
    key = (
        ATTRIBUTION_EVENT_LOG_KEY_PREFIX
        + epoch.to_bytes(8, "little", signed=False)
        + ordinal.to_bytes(8, "little", signed=False)
    )
    return key.hex()


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise AttributionBatchBridgeError(
            "attribution_event_log_file_exists",
            f"attribution event log already exists: {path}",
        )
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _backward_attribution_batch_root(backward_entries: list[dict[str, Any]]) -> str | None:
    if not backward_entries:
        return None
    sorted_entries = _require_sorted_backward_entries(backward_entries)
    preimage = json.dumps(
        sorted_entries,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()


def _backward_entry_sort_key(item: dict[str, Any]) -> tuple[object, object, object]:
    return (
        item["event_id"],
        item["upstream_artifact_id"],
        item["recipient_agent_id"],
    )


def _require_sorted_backward_entries(
    backward_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sorted_entries = sorted(backward_entries, key=_backward_entry_sort_key)
    if backward_entries != sorted_entries:
        raise AttributionBatchBridgeError(
            "backward_attribution_entries_must_be_canonical_sorted",
            "backward attribution entries must be sorted before hashing",
        )
    return backward_entries


def build_attribution_batch_from_claims(
    claim_payload: dict[str, Any],
    *,
    epoch: int | None = None,
    backward_attribution_graph_context: dict[str, Any] | None = None,
    agent_reputation_root: str | None = None,
    attribution_event_log_dir: str | Path | None = None,
    cdl084_settled_event_ids: set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    """Build a Rust `AttributionBatch` JSON payload from accepted claims.

    Amounts are floored to integer micro-ECU so the bridge never over-credits
    relative to the Decimal claim artifact. Any sub-micro remainder is recorded
    as dust in the bridge artifact.
    """

    payload = _require_dict("claim_payload", claim_payload)
    if payload.get("marker") not in {None, "agent_loop_claims_ok"}:
        raise AttributionBatchBridgeError(
            "accepted_claim_payload_required",
            "only accepted agent_loop_claims_ok payloads can be bridged",
        )
    claims = _require_claims(payload.get("claims"))
    normalized_agent_reputation_root = _require_optional_sha256_hex(
        agent_reputation_root,
        "agent_reputation_root_must_be_64_lower_hex",
    )

    selected_epoch: int | None = epoch
    aggregated: dict[str, dict[str, Any]] = {}
    seen_claim_ids: set[str] = set()
    total_source = Decimal("0")
    total_dust = Decimal("0")
    for claim in claims:
        claim_epoch = _require_epoch(claim.get("epoch"))
        if selected_epoch is None:
            selected_epoch = claim_epoch
        elif selected_epoch != claim_epoch:
            raise AttributionBatchBridgeError(
                "claim_epochs_must_match",
                "all accepted claims must share the attribution batch epoch",
            )
        agent_id = _require_agent_id(claim.get("agent_id"))
        amount = _require_decimal_amount(claim.get("amount"))
        total_source += amount
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise AttributionBatchBridgeError("claim_id_required", "each claim must have a claim_id")
        if claim_id in seen_claim_ids:
            raise AttributionBatchBridgeError(
                "claim_id_duplicate_in_batch",
                "claim_id values must be unique within an attribution batch",
            )
        seen_claim_ids.add(claim_id)
        _, dust = _append_amount(
            aggregated,
            agent_id=agent_id,
            amount=amount,
            source_id=claim_id,
        )
        total_dust += dust

    backward_entries: list[dict[str, Any]] = []
    attribution_event_log: list[dict[str, Any]] = []
    total_backward_final = Decimal("0")
    total_backward_unissued = Decimal("0")
    if backward_attribution_graph_context is not None:
        context = _require_backward_graph_context(backward_attribution_graph_context)
        traversal = BackwardAttributionTraversal(context["nodes"], context["edges"])
        werner_contexts = _require_werner_context_by_agent_id(
            context.get("werner_context_by_agent_id"),
        )
        settled_ids = frozenset(cdl084_settled_event_ids or ())
        seen_backward_event_ids: set[str] = set()
        for ordinal, raw_event in enumerate(context["events"]):
            event = _require_backward_event(raw_event)
            event_id = _require_non_empty_bridge_string(
                event["event_id"],
                "backward_event_id_required",
            )
            if event_id in seen_backward_event_ids:
                raise AttributionBatchBridgeError(
                    "backward_event_id_duplicate_in_batch",
                    "backward attribution event IDs must be unique in a batch",
                )
            seen_backward_event_ids.add(event_id)
            event_epoch = _require_epoch(event["event_epoch"])
            if selected_epoch is not None and event_epoch != selected_epoch:
                raise AttributionBatchBridgeError(
                    "backward_event_epoch_must_match_batch_epoch",
                    "backward attribution events must share the batch epoch",
                )
            selected_epoch = event_epoch
            source_node_id = _require_non_empty_bridge_string(
                event["source_node_id"],
                "backward_source_node_id_required",
            )
            event_budget = _require_decimal_amount(event["event_budget_ecu"])
            log_key = _attribution_event_log_key(event_epoch, ordinal)
            if event_id in settled_ids or event.get("already_settled_by_cdl084") is True:
                log_record = {
                    "cdl084_explicit_chain_preserved": True,
                    "credit_amount": "0",
                    "dedup_reason": "cdl084_explicit_chain_already_settled",
                    "edge_type": "PROVENANCE",
                    "epoch": event_epoch,
                    "event_id": event_id,
                    "lmdb_key_hex": log_key,
                    "source_node_cid": source_node_id,
                }
                attribution_event_log.append(log_record)
                continue

            result = traversal.traverse(
                source_node_id,
                event_id=event_id,
                event_budget_ecu=event_budget,
                event_epoch=event_epoch,
                apply_antigaming_caps=True,
                werner_context_by_agent_id=werner_contexts,
            )
            total_backward_unissued += result.unissued_backward_pool_ecu
            for final_credit in result.final_credits:
                cap_applied = (
                    final_credit.node_cap_applied
                    or final_credit.agent_cap_applied
                    or final_credit.cluster_cap_applied
                )
                applied_cap_values = []
                if final_credit.node_cap_applied:
                    applied_cap_values.append(result.node_cap_amount_ecu)
                if final_credit.agent_cap_applied:
                    applied_cap_values.append(result.agent_cap_amount_ecu)
                if final_credit.cluster_cap_applied:
                    applied_cap_values.append(result.cluster_cap_amount_ecu)
                cap_value = min(applied_cap_values) if applied_cap_values else None
                entry = {
                    "agent_cap_applied": final_credit.agent_cap_applied,
                    "anti_gaming_cap_applied": cap_applied,
                    "cap_value": (
                        decimal_to_canonical_string(cap_value)
                        if cap_value is not None
                        else None
                    ),
                    "clipped_residual_ecu": decimal_to_canonical_string(
                        final_credit.clipped_residual_ecu
                    ),
                    "cluster_cap_applied": final_credit.cluster_cap_applied,
                    "cluster_id": final_credit.cluster_id,
                    "credit_amount": decimal_to_canonical_string(
                        final_credit.final_credit_ecu
                    ),
                    "edge_type": "PROVENANCE",
                    "epoch": event_epoch,
                    "event_id": final_credit.event_id,
                    "hop_count": final_credit.depth,
                    "lmdb_key_hex": log_key,
                    "node_cap_applied": final_credit.node_cap_applied,
                    "pre_cap_credit_ecu": decimal_to_canonical_string(
                        final_credit.pre_cap_credit_ecu
                    ),
                    "recipient_agent_id": final_credit.recipient_agent_id,
                    "source_node_cid": source_node_id,
                    "upstream_artifact_id": final_credit.upstream_artifact_id,
                    "werner_context_present": final_credit.werner_context_present,
                    "werner_flow_budget": decimal_to_canonical_string(
                        final_credit.werner_flow_budget
                    ),
                    "werner_multiplier": decimal_to_canonical_string(
                        final_credit.werner_multiplier
                    ),
                }
                _require_agent_id(final_credit.recipient_agent_id)
                attribution_event_log.append(entry)
                backward_entries.append(entry)
                if final_credit.final_credit_ecu > Decimal("0"):
                    _, dust = _append_amount(
                        aggregated,
                        agent_id=final_credit.recipient_agent_id,
                        amount=final_credit.final_credit_ecu,
                        source_id=f"backward:{event_id}:{final_credit.upstream_artifact_id}",
                    )
                    total_dust += dust
                    total_backward_final += final_credit.final_credit_ecu
        if attribution_event_log_dir is not None:
            log_dir = Path(attribution_event_log_dir)
            for index, record in enumerate(attribution_event_log):
                _write_json_atomic(
                    log_dir / f"attr_event_{selected_epoch}_{index:04d}.json",
                    record,
                )
        total_source += total_backward_final

    if selected_epoch is None:
        raise AttributionBatchBridgeError("attribution_epoch_required", "attribution epoch is required")

    attributions: list[dict[str, Any]] = []
    for agent_id in sorted(aggregated):
        entry = aggregated[agent_id]
        attributions.append(
            {
                "agent_id_hex": entry["agent_id_hex"],
                "amount_micro_ecu": entry["amount_micro_ecu"],
                "source_amount_ecu": decimal_to_canonical_string(entry["source_amount_ecu"]),
                "source_claim_ids": sorted(entry["source_claim_ids"]),
                "source_claim_count": len(entry["source_claim_ids"]),
                "dust_ecu": decimal_to_canonical_string(entry["dust_ecu"]),
            }
        )

    batch = {
        "marker": "attribution_batch_bridge_ok",
        "runtime_version": ATTRIBUTION_BATCH_BRIDGE_VERSION,
        "epoch": selected_epoch,
        "micro_ecu_per_ecu": int(MICRO_ECU_PER_ECU),
        "rounding": "floor_to_micro_ecu_no_over_credit",
        "source_claim_count": len(claims),
        "attribution_count": len(attributions),
        "total_source_ecu": decimal_to_canonical_string(total_source),
        "total_micro_ecu": sum(item["amount_micro_ecu"] for item in attributions),
        "total_dust_ecu": decimal_to_canonical_string(total_dust),
        "attributions": attributions,
    }
    if batch["total_micro_ecu"] > MAX_U64:
        raise AttributionBatchBridgeError(
            "attribution_batch_total_micro_ecu_exceeds_u64",
            "attribution batch total exceeds Rust u64 micro-ECU boundary",
        )
    if backward_attribution_graph_context is not None:
        sorted_backward_entries = sorted(
            backward_entries,
            key=_backward_entry_sort_key,
        )
        batch.update(
            {
                "backward_attribution_caps_applied": True,
                "backward_attribution_entry_count": len(backward_entries),
                "backward_attribution_entries": sorted_backward_entries,
                "backward_attribution_batch_root": (
                    _backward_attribution_batch_root(sorted_backward_entries)
                ),
                "backward_attribution_batch_root_algorithm": (
                    "sha256_sorted_backward_attribution_entries_v1"
                ),
                "backward_attribution_marker": (
                    "backward_attribution_runtime_wired_GAP_ECU_04b"
                ),
                "backward_attribution_runtime_version": BACKWARD_ATTRIBUTION_CDL_VERSION,
                "backward_attribution_total_final_credit_ecu": (
                    decimal_to_canonical_string(total_backward_final)
                ),
                "backward_attribution_total_unissued_ecu": (
                    decimal_to_canonical_string(total_backward_unissued)
                ),
                "attribution_event_log": sorted(
                    attribution_event_log,
                    key=lambda item: (
                        item["event_id"],
                        item.get("upstream_artifact_id", ""),
                        item.get("recipient_agent_id", ""),
                    ),
                ),
                "sybil_diversity_guard_cdl_gap": (
                    BACKWARD_ATTRIBUTION_SYBIL_DIVERSITY_GUARD_CDL_GAP
                ),
                "werner_application_stage": WERNER_APPLICATION_STAGE,
                "werner_attribution_bridge_scope": WERNER_BRIDGE_SCOPE,
                "werner_attribution_bridge_version": WERNER_CDL_109_VERSION,
                "werner_context_count": len(werner_contexts),
            }
        )
    if normalized_agent_reputation_root is not None:
        batch["agent_reputation_root"] = normalized_agent_reputation_root
    return batch


def apply_attribution_batch_with_rust(
    batch_payload: dict[str, Any],
    *,
    consensus_lmdb: str | Path,
    rust_binary: str | Path,
    dry_run: bool = False,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Apply a bridge batch through the Rust `attribution_batch_ingest` binary."""

    binary_path = Path(rust_binary)
    if not binary_path.exists():
        raise AttributionBatchBridgeError(
            "rust_attribution_batch_ingest_binary_missing",
            f"Rust attribution binary not found: {binary_path}",
        )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
        json.dump(batch_payload, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
        handle.write("\n")
        input_path = Path(handle.name)
    try:
        command = [
            str(binary_path),
            "--input-file",
            str(input_path),
            "--lmdb",
            str(consensus_lmdb),
        ]
        if dry_run:
            command.append("--dry-run")
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise AttributionBatchBridgeError(
                "rust_attribution_batch_ingest_timeout",
                f"Rust attribution binary timed out after {timeout_seconds} seconds",
            ) from exc
    finally:
        input_path.unlink(missing_ok=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise AttributionBatchBridgeError(
            "rust_attribution_batch_ingest_failed",
            detail,
        )
    try:
        return _require_dict("rust_ingest_report", json.loads(result.stdout))
    except json.JSONDecodeError as exc:
        raise AttributionBatchBridgeError(
            "rust_attribution_batch_ingest_invalid_json",
            "Rust attribution binary emitted invalid JSON",
        ) from exc
