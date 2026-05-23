from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
import shutil
from pathlib import Path
from typing import List, TypedDict


CDL_043_ADAPTIVE_PRUNING_VERSION = "cdl_043_adaptive_pruning_threshold_runtime_phase_1361.v0.1"
CDL_044_RETENTION_EPOCHS_CONSTANT_TOKEN = "cdl_044_retention_epochs_constitutional_constant_phase_1361"
CDL_044_RETENTION_EPOCHS = 1
CDL_044_EPOCH_SCOPE = "issuance_epoch"
CDL_043_ECU_SCORE_FLOOR = Decimal("0.5")
CDL_043_SNAPSHOT_INTERVAL_EPOCHS = 50
EVENT_LOG_RETENTION_INTERNAL_PLAN_PROVENANCE_TOKEN = (
    "event_log_retention_internal_plan_builder_phase_1440"
)
FINDING_14_EVENT_LOG_RETENTION_PROVENANCE_GUARD_RESOLVED_TOKEN = (
    "finding_14_event_log_retention_provenance_guard_resolved_phase_1440"
)


_EPOCH_DIR_PATTERN = re.compile(r"^epoch_(\d{4,})$")


class EventLogRetentionPlan(TypedDict):
    plan_provenance_token: str
    root: str
    keep_last: int
    discovered: List[str]
    keep: List[str]
    prune: List[str]


class EventLogRetentionApplyResult(TypedDict):
    dry_run: bool
    planned_prune: int
    deleted: int
    kept: int
    pruned_dirs: List[str]


class AdaptivePruningThreshold(TypedDict):
    version: str
    epoch_scope: str
    current_issuance_epoch: int
    eligible_before_or_at_epoch: int
    retention_epochs: int
    ecu_score_floor: str
    snapshot_interval_epochs: int
    minting_confirmed: bool


class AdaptiveEventLogRetentionPlan(EventLogRetentionPlan):
    threshold: AdaptivePruningThreshold
    ecu_score: str
    pruning_enabled: bool


def _require_uint_epoch(value: int, *, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_finite_decimal(value: Decimal | int | str, *, token: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(token)
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(token) from exc
    if not number.is_finite():
        raise ValueError(token)
    return number


def _reject_retention_override(retention_epochs: int | None) -> None:
    if retention_epochs is not None:
        raise ValueError("retention_epochs_is_constitutional_constant")


def _decimal_to_string(value: Decimal) -> str:
    return format(value.normalize(), "f")


def compute_adaptive_pruning_threshold(
    *,
    current_issuance_epoch: int,
    minting_confirmed: bool,
    retention_epochs: int | None = None,
) -> AdaptivePruningThreshold:
    """Build the CDL-043/044 issuance-epoch pruning threshold.

    The threshold deliberately returns epoch eligibility only. ECU-score
    eligibility is record-specific and must be checked with
    ``is_below_adaptive_pruning_floor`` so high-score graph data is retained.
    """
    _reject_retention_override(retention_epochs)
    current_epoch = _require_uint_epoch(
        current_issuance_epoch,
        token="current_issuance_epoch_invalid_phase_1361",
    )
    if not isinstance(minting_confirmed, bool):
        raise ValueError("minting_confirmed_invalid_phase_1361")

    eligible_before_or_at = 0
    if minting_confirmed and current_epoch >= CDL_044_RETENTION_EPOCHS:
        eligible_before_or_at = current_epoch - CDL_044_RETENTION_EPOCHS

    return {
        "version": CDL_043_ADAPTIVE_PRUNING_VERSION,
        "epoch_scope": CDL_044_EPOCH_SCOPE,
        "current_issuance_epoch": current_epoch,
        "eligible_before_or_at_epoch": eligible_before_or_at,
        "retention_epochs": CDL_044_RETENTION_EPOCHS,
        "ecu_score_floor": _decimal_to_string(CDL_043_ECU_SCORE_FLOOR),
        "snapshot_interval_epochs": CDL_043_SNAPSHOT_INTERVAL_EPOCHS,
        "minting_confirmed": minting_confirmed,
    }


def is_below_adaptive_pruning_floor(ecu_score: Decimal | int | str) -> bool:
    score = _require_finite_decimal(
        ecu_score,
        token="ecu_score_invalid_phase_1361",
    )
    if score < Decimal("0"):
        raise ValueError("ecu_score_invalid_phase_1361")
    return score < CDL_043_ECU_SCORE_FLOOR


def _epoch_index_from_name(name: str) -> int | None:
    match = _EPOCH_DIR_PATTERN.match(name)
    if not match:
        return None
    return int(match.group(1))


def discover_epoch_event_dirs(root: str | Path) -> List[Path]:
    root_path = Path(root)
    if not root_path.exists() or not root_path.is_dir():
        return []

    discovered: List[tuple[int, Path]] = []
    for child in root_path.iterdir():
        if not child.is_dir():
            continue
        epoch_index = _epoch_index_from_name(child.name)
        if epoch_index is None:
            continue
        if not (child / "devnet_events.ndjson").exists():
            continue
        discovered.append((epoch_index, child))

    discovered.sort(key=lambda item: item[0])
    return [path for _, path in discovered]


def build_event_log_retention_plan(
    root: str | Path,
    *,
    keep_last: int,
) -> EventLogRetentionPlan:
    if keep_last < 1:
        raise ValueError("keep_last must be >= 1")

    root_path = Path(root)
    discovered = discover_epoch_event_dirs(root_path)

    keep_paths = discovered[-keep_last:] if len(discovered) > keep_last else discovered
    prune_paths = discovered[:-keep_last] if len(discovered) > keep_last else []

    return {
        "plan_provenance_token": EVENT_LOG_RETENTION_INTERNAL_PLAN_PROVENANCE_TOKEN,
        "root": str(root_path),
        "keep_last": keep_last,
        "discovered": [str(path) for path in discovered],
        "keep": [str(path) for path in keep_paths],
        "prune": [str(path) for path in prune_paths],
    }


def build_adaptive_event_log_retention_plan(
    root: str | Path,
    *,
    current_issuance_epoch: int,
    ecu_score: Decimal | int | str,
    minting_confirmed: bool,
    retention_epochs: int | None = None,
) -> AdaptiveEventLogRetentionPlan:
    _reject_retention_override(retention_epochs)
    threshold = compute_adaptive_pruning_threshold(
        current_issuance_epoch=current_issuance_epoch,
        minting_confirmed=minting_confirmed,
    )
    score = _require_finite_decimal(ecu_score, token="ecu_score_invalid_phase_1361")
    if score < Decimal("0"):
        raise ValueError("ecu_score_invalid_phase_1361")

    root_path = Path(root)
    discovered = discover_epoch_event_dirs(root_path)
    eligible_epoch = threshold["eligible_before_or_at_epoch"]
    pruning_enabled = minting_confirmed and score < CDL_043_ECU_SCORE_FLOOR and eligible_epoch > 0

    keep_paths: List[Path] = []
    prune_paths: List[Path] = []
    for path in discovered:
        epoch_index = _epoch_index_from_name(path.name)
        if epoch_index is None:
            keep_paths.append(path)
            continue
        if pruning_enabled and epoch_index <= eligible_epoch:
            prune_paths.append(path)
        else:
            keep_paths.append(path)

    return {
        "plan_provenance_token": EVENT_LOG_RETENTION_INTERNAL_PLAN_PROVENANCE_TOKEN,
        "root": str(root_path),
        "keep_last": CDL_044_RETENTION_EPOCHS,
        "discovered": [str(path) for path in discovered],
        "keep": [str(path) for path in keep_paths],
        "prune": [str(path) for path in prune_paths],
        "threshold": threshold,
        "ecu_score": _decimal_to_string(score),
        "pruning_enabled": pruning_enabled,
    }


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _require_internal_plan(plan: EventLogRetentionPlan) -> None:
    if plan.get("plan_provenance_token") != EVENT_LOG_RETENTION_INTERNAL_PLAN_PROVENANCE_TOKEN:
        raise ValueError("event_log_retention_plan_provenance_invalid_phase_1440")


def apply_event_log_retention_plan(
    plan: EventLogRetentionPlan,
    *,
    dry_run: bool,
) -> EventLogRetentionApplyResult:
    _require_internal_plan(plan)
    root_path = Path(plan["root"])
    prune_paths = [Path(path) for path in plan["prune"]]

    deleted = 0
    pruned_dirs: List[str] = []

    for path in prune_paths:
        if not _is_within_root(path, root_path):
            continue
        if not path.exists() or not path.is_dir():
            continue
        if not (path / "devnet_events.ndjson").exists():
            continue

        pruned_dirs.append(str(path))
        if not dry_run:
            shutil.rmtree(path)
            deleted += 1

    return {
        "dry_run": dry_run,
        "planned_prune": len(prune_paths),
        "deleted": deleted,
        "kept": len(plan["keep"]),
        "pruned_dirs": pruned_dirs,
    }
