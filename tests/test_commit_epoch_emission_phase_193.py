from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.exceptions import EventLogValidationError
from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.network.topology import NodeRole, assign_agents_round_robin, build_star_topology
from ilc_core.protocol.event_log import EventLogger
from ilc_core.sim.devnet_multi_epoch import run_devnet_multi_epoch


def _build_minimal_devnet_inputs() -> tuple[object, dict[str, AgentProfile], list[NamespaceHealthSnapshot]]:
    topology = build_star_topology(center_id="orch", leaf_ids=["worker1"])
    assign_agents_round_robin(["agent_1"], topology, role=NodeRole.WORKER)

    profiles = {
        "agent_1": AgentProfile(
            agent_id="agent_1",
            node_id="worker1",
            competency={
                "global": {"avg_success_rate": 0.75},
                "by_space": {"PLANNING": {"tasks": 4, "success_rate": 0.75}},
            },
            stress_response={"preference": "neutral"},
        )
    }

    snapshot = NamespaceHealthSnapshot(
        namespace_id="phase193_ns",
        epoch_index=3,
        total_stress=0.4,
        cohesion_score=0.6,
        contradiction_overflow=0.0,
        support_ratio=1.0,
        validation_depth_error=0.0,
        crosslink_deficit=0.0,
        controversy_ratio=0.0,
        mean_abs_influence=0.0,
    )

    return topology, profiles, [snapshot]


def test_phase_193_devnet_finalization_emits_commit_epoch_via_logger(tmp_path: Path) -> None:
    topology, profiles, snapshots = _build_minimal_devnet_inputs()
    ledger = InMemoryLedgerBackend()

    run_devnet_multi_epoch(
        topology,
        snapshots,
        profiles,
        export_root=tmp_path,
        ledger_backend=ledger,
    )

    log_path = tmp_path / "epoch_0003" / "devnet_events.ndjson"
    assert log_path.exists()

    commit_events = []
    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            event = json.loads(line)
            if event.get("kind") == "commit.epoch":
                commit_events.append(event)

    assert len(commit_events) == 1
    payload = commit_events[0]["payload"]
    assert payload["event_kind"] == "commit.epoch"
    assert payload["epoch_index"] == 3
    assert payload["finalization_state"] == "committed"
    assert "summary" in payload
    assert "checksums" in payload


def test_phase_193_event_logger_rejects_invalid_commit_epoch_payload() -> None:
    event_logger = EventLogger(events=[])

    with pytest.raises(EventLogValidationError, match="Missing required top-level fields"):
        event_logger.emit(
            kind="commit.epoch",
            payload={"event_kind": "commit.epoch"},
            source="test:phase193",
        )
