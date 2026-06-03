# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any, TypedDict

import lmdb

from ilc_core.protocol.event_log_retention import (
    CDL_043_ADAPTIVE_PRUNING_VERSION,
    CDL_043_ECU_SCORE_FLOOR,
    CDL_043_SNAPSHOT_INTERVAL_EPOCHS,
    CDL_044_EPOCH_SCOPE,
    CDL_044_RETENTION_EPOCHS,
    compute_adaptive_pruning_threshold,
)


LMDB_GRAPH_LEVEL_PRUNING_VERSION = "lmdb_graph_level_pruning_path_phase_1361"
CDL_071_TIER_2_EPOCH_SCOPE_TOKEN = "cdl_071_tier_2_epoch_scope_enforcement_phase_1361"
PRODUCTION_PRUNING_NOT_ACTIVATED_TOKEN = "production_pruning_not_activated_phase_1361"
PRODUCTION_PRUNING_ACTIVE = False
MAX_LMDB_PRUNING_RECORDS_PER_BATCH = 1024
MAX_LMDB_PRUNING_RECORD_BYTES = 64 * 1024
CDL_071_TIER_2 = "tier_2"


class LmdbGraphPruningResult(TypedDict):
    version: str
    adaptive_pruning_version: str
    dry_run: bool
    production_requested: bool
    current_issuance_epoch: int
    eligible_before_or_at_epoch: int
    retention_epochs: int
    epoch_scope: str
    ecu_score_floor: str
    snapshot_interval_epochs: int
    scanned: int
    planned_prune: int
    deleted: int
    retained: int
    skipped_not_tier_2: int
    stopped_at_batch_cap: bool
    planned_prune_keys: list[str]


def require_production_pruning_activation() -> None:
    if not PRODUCTION_PRUNING_ACTIVE:
        raise ValueError(PRODUCTION_PRUNING_NOT_ACTIVATED_TOKEN)


def _require_batch_cap(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("lmdb_pruning_batch_cap_invalid_phase_1361")
    if value < 1 or value > MAX_LMDB_PRUNING_RECORDS_PER_BATCH:
        raise ValueError("lmdb_pruning_batch_cap_invalid_phase_1361")
    return value


def _require_uint_epoch(value: Any, *, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_finite_decimal(value: Any, *, token: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(token)
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(token) from exc
    if not number.is_finite():
        raise ValueError(token)
    return number


def _decode_record(value: bytes) -> dict[str, Any]:
    if len(value) > MAX_LMDB_PRUNING_RECORD_BYTES:
        raise ValueError("lmdb_pruning_record_too_large_phase_1361")
    try:
        payload = json.loads(value.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("lmdb_pruning_record_invalid_json_phase_1361") from exc
    if not isinstance(payload, dict):
        raise ValueError("lmdb_pruning_record_invalid_json_phase_1361")
    return payload


def _is_tier_2_issuance_epoch_record(payload: dict[str, Any]) -> bool:
    return payload.get("temporal_tier") == CDL_071_TIER_2 and payload.get("epoch_scope") == CDL_044_EPOCH_SCOPE


def _is_prunable_tier_2_record(
    payload: dict[str, Any],
    *,
    eligible_before_or_at_epoch: int,
) -> bool:
    if not _is_tier_2_issuance_epoch_record(payload):
        return False

    record_epoch = payload.get("issuance_epoch")
    if not isinstance(record_epoch, int) or isinstance(record_epoch, bool) or record_epoch < 0:
        return False
    if record_epoch > eligible_before_or_at_epoch:
        return False

    ecu_score = _require_finite_decimal(
        payload.get("ecu_score"),
        token="lmdb_pruning_record_ecu_score_invalid_phase_1361",
    )
    if ecu_score < Decimal("0"):
        raise ValueError("lmdb_pruning_record_ecu_score_invalid_phase_1361")
    return ecu_score < CDL_043_ECU_SCORE_FLOOR


def prune_lmdb_graph_tier_2_records(
    env: lmdb.Environment,
    db: lmdb._Database,
    *,
    current_issuance_epoch: int,
    minting_confirmed: bool,
    dry_run: bool = True,
    production: bool = False,
    max_records_per_batch: int = MAX_LMDB_PRUNING_RECORDS_PER_BATCH,
    retention_epochs: int | None = None,
) -> LmdbGraphPruningResult:
    if production:
        require_production_pruning_activation()
    if not isinstance(dry_run, bool) or not isinstance(production, bool):
        raise ValueError("lmdb_pruning_mode_invalid_phase_1361")

    batch_cap = _require_batch_cap(max_records_per_batch)
    _require_uint_epoch(
        current_issuance_epoch,
        token="current_issuance_epoch_invalid_phase_1361",
    )
    threshold = compute_adaptive_pruning_threshold(
        current_issuance_epoch=current_issuance_epoch,
        minting_confirmed=minting_confirmed,
        retention_epochs=retention_epochs,
    )
    eligible_before_or_at_epoch = threshold["eligible_before_or_at_epoch"]

    scanned = 0
    planned_prune = 0
    deleted = 0
    retained = 0
    skipped_not_tier_2 = 0
    stopped_at_batch_cap = False
    planned_prune_keys: list[str] = []

    with env.begin(write=not dry_run, db=db) as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            if planned_prune >= batch_cap:
                stopped_at_batch_cap = True
                break

            scanned += 1
            payload = _decode_record(value)
            if not _is_tier_2_issuance_epoch_record(payload):
                skipped_not_tier_2 += 1
                retained += 1
                continue

            if minting_confirmed and _is_prunable_tier_2_record(
                payload,
                eligible_before_or_at_epoch=eligible_before_or_at_epoch,
            ):
                planned_prune += 1
                planned_prune_keys.append(key.decode("utf-8", errors="replace"))
                if not dry_run:
                    cursor.delete()
                    deleted += 1
            else:
                retained += 1

    return {
        "version": LMDB_GRAPH_LEVEL_PRUNING_VERSION,
        "adaptive_pruning_version": CDL_043_ADAPTIVE_PRUNING_VERSION,
        "dry_run": dry_run,
        "production_requested": production,
        "current_issuance_epoch": threshold["current_issuance_epoch"],
        "eligible_before_or_at_epoch": eligible_before_or_at_epoch,
        "retention_epochs": CDL_044_RETENTION_EPOCHS,
        "epoch_scope": CDL_044_EPOCH_SCOPE,
        "ecu_score_floor": format(CDL_043_ECU_SCORE_FLOOR.normalize(), "f"),
        "snapshot_interval_epochs": CDL_043_SNAPSHOT_INTERVAL_EPOCHS,
        "scanned": scanned,
        "planned_prune": planned_prune,
        "deleted": deleted,
        "retained": retained,
        "skipped_not_tier_2": skipped_not_tier_2,
        "stopped_at_batch_cap": stopped_at_batch_cap,
        "planned_prune_keys": planned_prune_keys,
    }


__all__ = [
    "CDL_071_TIER_2",
    "CDL_071_TIER_2_EPOCH_SCOPE_TOKEN",
    "LMDB_GRAPH_LEVEL_PRUNING_VERSION",
    "LmdbGraphPruningResult",
    "MAX_LMDB_PRUNING_RECORD_BYTES",
    "MAX_LMDB_PRUNING_RECORDS_PER_BATCH",
    "PRODUCTION_PRUNING_ACTIVE",
    "PRODUCTION_PRUNING_NOT_ACTIVATED_TOKEN",
    "prune_lmdb_graph_tier_2_records",
    "require_production_pruning_activation",
]
