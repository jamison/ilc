# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1568-Fix2b-3 Python-to-Rust attribution batch bridge.

This module converts accepted agent-loop ECU claim payloads into the narrow
JSON shape consumed by the Rust `attribution_batch_ingest` binary. It is not a
review, jury, CDL-048, ILC allocation, or settlement-root runtime.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from pathlib import Path
from typing import Any

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string

ATTRIBUTION_BATCH_BRIDGE_VERSION = "attribution_batch_bridge_1568_fix2b3.v0.1"
MICRO_ECU_PER_ECU = Decimal("1000000")
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")


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


def _amount_to_micro_ecu(amount: Decimal) -> tuple[int, Decimal]:
    scaled = amount * MICRO_ECU_PER_ECU
    floored = scaled.to_integral_value(rounding=ROUND_FLOOR)
    if floored <= 0:
        raise AttributionBatchBridgeError(
            "claim_amount_below_one_micro_ecu",
            "claim amount floors to zero micro-ECU",
        )
    dust = (scaled - floored) / MICRO_ECU_PER_ECU
    return int(floored), dust


def build_attribution_batch_from_claims(
    claim_payload: dict[str, Any],
    *,
    epoch: int | None = None,
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

    selected_epoch: int | None = epoch
    aggregated: dict[str, dict[str, Any]] = {}
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
        micro_amount, dust = _amount_to_micro_ecu(amount)
        total_source += amount
        total_dust += dust
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise AttributionBatchBridgeError("claim_id_required", "each claim must have a claim_id")
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
        entry["source_claim_ids"].append(claim_id)

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

    return {
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
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
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
