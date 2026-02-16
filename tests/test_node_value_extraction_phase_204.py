import json
from pathlib import Path
from typing import Mapping

from ilc_core.analysis.node_value_extraction import (
    build_node_value_replay_fixture_from_ndjson,
    build_node_value_replay_fixture_from_rows,
    write_node_value_replay_fixture,
)


def test_build_fixture_from_rows_is_deterministic() -> None:
    rows: list[Mapping[str, object]] = [
        {
            "kind": "task_outcome",
            "payload": {
                "task_id": "task-1",
                "agent_id": "agent-a",
                "epoch": 1,
                "reward_paid": 4.0,
                "stake_spent": 1.5,
                "success": True,
                "domain": "logic",
            },
        },
        {
            "kind": "invalid_kind",
            "payload": {},
        },
        {
            "kind": "claim",
            "payload": {
                "id": "claim-1",
                "agent_id": "agent-a",
                "timestamp": "2026-02-16T00:00:00Z",
                "net_stake": 2.0,
                "parent_ids": ["root-1"],
                "target_id": "node-1",
            },
        },
    ]

    fixture_a = build_node_value_replay_fixture_from_rows(rows)
    fixture_b = build_node_value_replay_fixture_from_rows(rows)

    assert fixture_a["accepted_count"] == 2
    assert fixture_a["accepted_rows_sha256"] == fixture_b["accepted_rows_sha256"]
    assert fixture_a["telemetry"] == {
        "total_seen": 3,
        "accepted": 2,
        "rejected_invalid_shape": 0,
        "rejected_unknown_kind": 1,
    }


def test_build_fixture_from_ndjson_has_stable_hash(tmp_path: Path) -> None:
    ndjson_path = tmp_path / "node_value_inputs.ndjson"
    entries = [
        {
            "kind": "task_outcome",
            "payload": {
                "task_id": "task-1",
                "agent_id": "agent-a",
                "epoch": 1,
                "reward_paid": 4.0,
                "stake_spent": 1.5,
                "success": True,
                "domain": "logic",
            },
        },
        {
            "kind": "commit.epoch",
            "payload": {
                "event_kind": "commit.epoch",
                "epoch_index": 1,
                "epoch_id": "epoch-1",
                "namespace_id": "ns-a",
            },
        },
    ]
    ndjson_path.write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in entries) + "\n",
        encoding="utf-8",
    )

    fixture_1 = build_node_value_replay_fixture_from_ndjson(ndjson_path)
    fixture_2 = build_node_value_replay_fixture_from_ndjson(str(ndjson_path))

    assert fixture_1["accepted_count"] == 2
    assert fixture_1["accepted_rows_sha256"] == fixture_2["accepted_rows_sha256"]


def test_write_node_value_replay_fixture_writes_json(tmp_path: Path) -> None:
    fixture = build_node_value_replay_fixture_from_rows(
        [
            {
                "kind": "task_outcome",
                "payload": {
                    "task_id": "task-9",
                    "agent_id": "agent-z",
                    "epoch": 5,
                    "reward_paid": 9.0,
                    "stake_spent": 3.0,
                    "success": False,
                    "domain": "synthesis",
                },
            }
        ]
    )

    out_path = tmp_path / "fixture.json"
    write_node_value_replay_fixture(fixture, out_path)

    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["accepted_count"] == 1
    assert isinstance(loaded["accepted_rows_sha256"], str)
    assert loaded["telemetry"]["accepted"] == 1
