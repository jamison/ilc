from __future__ import annotations

import pytest

from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.exceptions import EventLogValidationError
from ilc_core.network.topology import NodeRole, assign_agents_round_robin, build_star_topology
from ilc_core.protocol.event_log import EventLogger
from ilc_core.sim.devnet_epoch_orchestrator import run_devnet_epoch


def _build_epoch_inputs() -> tuple[object, NamespaceHealthSnapshot, dict[str, AgentProfile]]:
    topology = build_star_topology(center_id="orch", leaf_ids=["worker1"])
    assign_agents_round_robin(["agent_1"], topology, role=NodeRole.WORKER)

    profiles = {
        "agent_1": AgentProfile(
            agent_id="agent_1",
            node_id="worker1",
            competency={
                "global": {"avg_success_rate": 0.8},
                "by_space": {"PLANNING": {"tasks": 8, "success_rate": 0.8}},
            },
            stress_response={"preference": "neutral"},
        )
    }

    snapshot = NamespaceHealthSnapshot(
        namespace_id="phase194_ns",
        epoch_index=9,
        total_stress=0.5,
        cohesion_score=0.55,
        contradiction_overflow=0.0,
        support_ratio=1.0,
        validation_depth_error=0.0,
        crosslink_deficit=0.0,
        controversy_ratio=0.0,
        mean_abs_influence=0.0,
    )

    return topology, snapshot, profiles


def test_phase_194_event_logger_rejects_invalid_epoch_summary_payload() -> None:
    logger = EventLogger(events=[])
    with pytest.raises(EventLogValidationError, match="Missing required epoch_summary fields"):
        logger.emit(
            kind="epoch_summary",
            payload={"epoch_index": 1, "total_reward": 3.0},
            source="test:phase194",
        )


def test_phase_194_devnet_epoch_emits_valid_epoch_summary() -> None:
    topology, snapshot, profiles = _build_epoch_inputs()
    logger = EventLogger(events=[])

    run_devnet_epoch(
        epoch_index=snapshot.epoch_index,
        topology=topology,
        namespace_snapshot=snapshot,
        profiles=profiles,
        event_logger=logger,
    )

    summaries = [evt.payload for evt in logger.events if evt.kind == "epoch_summary"]
    assert len(summaries) == 1
    payload = summaries[0]
    assert payload["epoch_index"] == snapshot.epoch_index
    assert isinstance(payload["total_tasks"], int)
    assert payload["total_tasks"] >= 0
    assert isinstance(payload["total_reward"], (int, float))
    assert payload["total_reward"] >= 0
