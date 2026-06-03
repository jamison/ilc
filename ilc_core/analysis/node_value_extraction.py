# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, TypedDict

from ilc_core.analysis.node_value_input_canon import (
    NodeValueInputEvent,
    NodeValueInputTelemetry,
    collect_node_value_input_events,
)


class NodeValueReplayFixture(TypedDict):
    accepted_rows: list[NodeValueInputEvent]
    accepted_rows_sha256: str
    accepted_count: int
    telemetry: NodeValueInputTelemetry


def _stable_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_accepted_rows_sha256(accepted_rows: list[NodeValueInputEvent]) -> str:
    digest = hashlib.sha256()
    digest.update(_stable_json_bytes(accepted_rows))
    return digest.hexdigest()


def extract_node_value_inputs_from_rows(
    rows: Iterable[Mapping[str, object]],
) -> tuple[list[NodeValueInputEvent], NodeValueInputTelemetry]:
    return collect_node_value_input_events(rows)


def extract_node_value_inputs_from_ndjson(
    ndjson_path: str | Path,
) -> tuple[list[NodeValueInputEvent], NodeValueInputTelemetry]:
    path = Path(ndjson_path)
    if not path.exists():
        return extract_node_value_inputs_from_rows([])

    rows: list[Mapping[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                rows.append(parsed)
    return extract_node_value_inputs_from_rows(rows)


def build_node_value_replay_fixture_from_rows(
    rows: Iterable[Mapping[str, object]],
) -> NodeValueReplayFixture:
    accepted_rows, telemetry = extract_node_value_inputs_from_rows(rows)
    return {
        "accepted_rows": accepted_rows,
        "accepted_rows_sha256": compute_accepted_rows_sha256(accepted_rows),
        "accepted_count": len(accepted_rows),
        "telemetry": telemetry,
    }


def build_node_value_replay_fixture_from_ndjson(
    ndjson_path: str | Path,
) -> NodeValueReplayFixture:
    accepted_rows, telemetry = extract_node_value_inputs_from_ndjson(ndjson_path)
    return {
        "accepted_rows": accepted_rows,
        "accepted_rows_sha256": compute_accepted_rows_sha256(accepted_rows),
        "accepted_count": len(accepted_rows),
        "telemetry": telemetry,
    }


def write_node_value_replay_fixture(
    fixture: NodeValueReplayFixture,
    out_path: str | Path,
) -> None:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(fixture, indent=2, sort_keys=True),
        encoding="utf-8",
    )
