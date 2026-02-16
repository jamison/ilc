from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Dict, List, TypedDict


_EPOCH_DIR_PATTERN = re.compile(r"^epoch_(\d{4,})$")


class EventLogRetentionPlan(TypedDict):
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
        "root": str(root_path),
        "keep_last": keep_last,
        "discovered": [str(path) for path in discovered],
        "keep": [str(path) for path in keep_paths],
        "prune": [str(path) for path in prune_paths],
    }


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def apply_event_log_retention_plan(
    plan: EventLogRetentionPlan,
    *,
    dry_run: bool,
) -> EventLogRetentionApplyResult:
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
