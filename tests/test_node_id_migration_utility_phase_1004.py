from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ilc_core.types import Node
from tools.migrate_node_ids_to_canonical import migrate_records


def _legacy_record(content: str = "migrate-test") -> dict[str, object]:
    node = Node(
        id="",
        type="claim",
        content={"text": content},
        agent_id="agent:migration",
        signature="sig",
    )
    legacy_id = node.compute_legacy_id()
    return {
        "id": legacy_id,
        "type": "claim",
        "content": {"text": content},
        "agent_id": "agent:migration",
        "signature": "sig",
        "net_stake": 0.0,
        "parent_ids": [],
    }


def test_migrate_records_rewrites_legacy_to_canonical() -> None:
    record = _legacy_record()
    migrated, stats = migrate_records([record], "legacy_id")
    assert stats["total_records"] == 1
    assert stats["rewritten_to_canonical"] == 1
    assert stats["already_canonical"] == 0
    assert stats["skipped_invalid"] == 0
    assert migrated[0]["id"].startswith("b")
    assert migrated[0]["legacy_id"] == record["id"]


def test_migrate_records_preserves_already_canonical() -> None:
    record = _legacy_record("canonical")
    node = Node(
        id=str(record["id"]),
        type=str(record["type"]),
        content=record["content"],
        agent_id=str(record["agent_id"]),
        signature=str(record["signature"]),
    )
    record["id"] = node.compute_canonical_id()

    migrated, stats = migrate_records([record], "legacy_id")
    assert stats["total_records"] == 1
    assert stats["rewritten_to_canonical"] == 0
    assert stats["already_canonical"] == 1
    assert stats["skipped_invalid"] == 0
    assert migrated[0]["id"] == record["id"]
    assert "legacy_id" not in migrated[0]


def test_cli_migration_utility_rewrites_file(tmp_path: Path) -> None:
    in_path = tmp_path / "input.json"
    out_path = tmp_path / "output.json"
    in_path.write_text(json.dumps([_legacy_record("cli")]), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "tools/migrate_node_ids_to_canonical.py",
            "--in",
            str(in_path),
            "--out",
            str(out_path),
            "--legacy-field",
            "legacy_id",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    stdout = json.loads(result.stdout.strip())
    assert stdout["ok"] is True
    assert stdout["stats"]["rewritten_to_canonical"] == 1

    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert isinstance(written, list)
    assert written[0]["id"].startswith("b")
    assert written[0]["legacy_id"]
