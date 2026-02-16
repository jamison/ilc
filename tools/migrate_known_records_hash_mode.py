#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.protocol.known_records_migration import (
    migrate_known_records_payload_hash_to_record_digest,
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate known_records hash mode from payload_hash_v0 to record_digest_v1.",
    )
    parser.add_argument("--policy-state", required=True, help="Path to policy state JSON")
    parser.add_argument("--records", required=True, help="Path to governance records JSON")
    parser.add_argument("--out", help="Output path for migrated policy state JSON")
    parser.add_argument("--dry-run", action="store_true", help="Print summary only")
    args = parser.parse_args()

    policy_state_path = Path(args.policy_state)
    records_path = Path(args.records)

    policy_state = _load_json(policy_state_path)
    records_input = _load_json(records_path)

    result = migrate_known_records_payload_hash_to_record_digest(policy_state, records_input)
    if not result["ok"]:
        print("migration_failed")
        for error in result["errors"]:
            print(f"error={error}")
        return 1

    data = result["data"] or {}
    migrated_state = data.get("policy_state_migrated")

    print("migration_ok")
    print(f"migrated_count={data.get('migrated_count', 0)}")
    print(f"known_records_hash_mode={data.get('known_records_hash_mode')}")
    for warning in result["warnings"]:
        print(f"warning={warning}")

    if args.dry_run:
        print("dry_run=true")
        return 0

    if not args.out:
        print("error=missing_out_path")
        return 2

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(migrated_state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
