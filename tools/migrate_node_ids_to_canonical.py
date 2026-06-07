#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Allow direct script execution without requiring package installation.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.types import Node


def _load_input(path: Path) -> tuple[list[dict[str, Any]], str]:
    if path.suffix.lower() == ".ndjson":
        records: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
        return records, "ndjson"

    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise ValueError("input_json_must_be_list")
    records = [obj for obj in loaded if isinstance(obj, dict)]
    return records, "json"


def _coerce_node(record: dict[str, Any]) -> Node:
    return Node(
        id=str(record.get("id", "")),
        type=str(record.get("type", "claim")),  # type: ignore[arg-type]
        content=record.get("content", ""),
        agent_id=str(record.get("agent_id", "agent:migration")),
        signature=str(record.get("signature", "migration_unsigned")),
        net_stake=str(record.get("net_stake", "0")),
        target_id=record.get("target_id"),
        parent_ids=list(record.get("parent_ids", [])),
    )


def migrate_records(
    records: list[dict[str, Any]],
    legacy_field: str,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    migrated: list[dict[str, Any]] = []
    stats = {
        "total_records": 0,
        "rewritten_to_canonical": 0,
        "already_canonical": 0,
        "skipped_invalid": 0,
    }

    for record in records:
        stats["total_records"] += 1
        try:
            node = _coerce_node(record)
            legacy_id = node.compute_legacy_id()
            canonical_id = node.compute_canonical_id()
            current_id = str(record.get("id", ""))
        except Exception:
            stats["skipped_invalid"] += 1
            migrated.append(record)
            continue

        updated = dict(record)
        if current_id == canonical_id:
            stats["already_canonical"] += 1
            migrated.append(updated)
            continue

        updated[legacy_field] = current_id if current_id else legacy_id
        updated["id"] = canonical_id
        stats["rewritten_to_canonical"] += 1
        migrated.append(updated)

    return migrated, stats


def _write_output(
    path: Path,
    records: list[dict[str, Any]],
    fmt: str,
    pretty: bool,
) -> None:
    if fmt == "ndjson":
        lines = [json.dumps(rec, separators=(",", ":"), sort_keys=False) for rec in records]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    if pretty:
        payload = json.dumps(records, indent=2, sort_keys=False)
    else:
        payload = json.dumps(records, separators=(",", ":"), sort_keys=False)
    path.write_text(payload + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite node records from legacy ids to canonical CIDv1 ids."
    )
    parser.add_argument("--in", dest="input_path", required=True, help="Input JSON or NDJSON file")
    parser.add_argument("--out", dest="output_path", required=True, help="Output JSON or NDJSON file")
    parser.add_argument(
        "--legacy-field",
        default="legacy_id",
        help="Field name that stores the prior id value when rewritten",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_path = Path(args.output_path)

    records, fmt = _load_input(input_path)
    migrated, stats = migrate_records(records, args.legacy_field)
    _write_output(output_path, migrated, fmt, args.pretty)

    print(json.dumps({"ok": True, "stats": stats, "out": str(output_path)}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
