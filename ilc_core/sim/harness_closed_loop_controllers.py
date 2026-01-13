from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Optional, List, Dict, Tuple

import csv

from ilc_core.sim.devnet_scenarios import (
    DevnetScenarioConfig,
    build_topology_and_profiles,
)
from ilc_core.sim.devnet_epoch_orchestrator import run_devnet_epoch
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.protocol.params import ProtocolParams
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.network.topology import DevnetTopology

@dataclass(frozen=True)
class ClosedLoopEpochMetrics:
    epoch_index: int
    total_tasks: int
    backlog_proxy: int
    total_reward: float
    avg_reward_per_task: float
    # Optional but useful: total_suggestions = executed + backlog_proxy by default.
    total_suggestions: Optional[int] = None

# Functional controller: MUST return a new ProtocolParams instance.
ClosedLoopControllerFn = Callable[[int, ClosedLoopEpochMetrics, "ProtocolParams"], "ProtocolParams"]

@dataclass
class ClosedLoopRunConfig:
    scenario: "DevnetScenarioConfig"
    initial_params: "ProtocolParams"
    num_epochs: int
    label: str = "phase_65b"

    # Option 1: pass builder explicitly (NO monkeypatching)
    topology_builder_fn: Optional[
        Callable[["DevnetScenarioConfig", int], Tuple["DevnetTopology", Dict[str, "AgentProfile"]]]
    ] = None

def run_closed_loop_devnet(
    config: ClosedLoopRunConfig,
    controller_step: ClosedLoopControllerFn,
    rng_seed: int = 0,
) -> List[ClosedLoopEpochMetrics]:
    """
    Run a closed-loop devnet simulation for config.num_epochs.
    Controller is functional: returns new ProtocolParams each epoch.
    Topology/profiles are built once (deterministic) via topology_builder_fn if provided.
    Writes CSV history into out/<label>/backlog_control_history.csv
    """
    out_dir = Path("out") / config.label
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "backlog_control_history.csv"

    # Build topology/profiles once (stationary environment unless scenario itself changes internally)
    builder = config.topology_builder_fn or build_topology_and_profiles
    scenario_topology, scenario_profiles = builder(config.scenario, rng_seed)

    current_params = config.initial_params
    metrics_log: List[ClosedLoopEpochMetrics] = []
    history_rows: list[dict] = []

    for epoch_idx_zero in range(config.num_epochs):
        epoch_idx = epoch_idx_zero + 1 # 1-based for events/snapshots
        
        # Store qa_used BEFORE running this epoch
        qa_used = current_params.qa_min_score
        
        # 1. Determine Stress from Schedule
        sched = config.scenario.stress_schedule
        if epoch_idx_zero < len(sched):
            stress_val = sched[epoch_idx_zero]
        else:
            stress_val = sched[-1] if sched else 0.5

        # 2. Build Snapshot for this epoch
        # We need a minimal snapshot to drive routing
        snapshot = NamespaceHealthSnapshot(
            namespace_id=config.scenario.namespace_id,
            total_stress=float(stress_val),
            epoch_index=epoch_idx,
            # Defaults
            cohesion_score=0.8,
            contradiction_overflow=0.0,
            validation_depth_error=0.0,
            mean_abs_influence=0.5,
            crosslink_deficit=0.0,
            support_ratio=0.9,
            controversy_ratio=0.1
        )

        # Run epoch with current_params (which has qa_used)
        epoch_result = run_devnet_epoch(
            epoch_index=epoch_idx,
            topology=scenario_topology,
            namespace_snapshot=snapshot,
            profiles=scenario_profiles,
            protocol_params=current_params,
            # No rng_seed supported in run_devnet_epoch currently
        )

        executed = int(epoch_result.num_executed)
        backlog = int(epoch_result.backlog_count)
        # Check if suggestion_count exists, otherwise infer
        suggestions = getattr(epoch_result, "num_suggestions", None)

        # Compute metrics from node_load_metrics
        # node_load_metrics is Dict[node_id, Dict[str, float]]
        # e.g. {"w1": {"num_tasks": 10, "total_reward": 5.5, ...}}
        epoch_total_reward = sum(load.get("total_reward", 0.0) for load in epoch_result.node_load_metrics.values())
        
        if executed > 0:
            avg_reward = epoch_total_reward / executed
        else:
            avg_reward = 0.0

        m = ClosedLoopEpochMetrics(
            epoch_index=epoch_idx,
            total_tasks=executed,
            backlog_proxy=backlog,
            total_reward=float(epoch_total_reward),
            avg_reward_per_task=float(avg_reward),
            total_suggestions=int(suggestions) if suggestions is not None else (executed + backlog),
        )
        metrics_log.append(m)

        # Controller step MUST return a new params object
        new_params = controller_step(epoch_idx, m, current_params)
        if not isinstance(new_params, type(current_params)):
            raise TypeError(
                f"controller_step must return ProtocolParams, got: {type(new_params)}"
            )
        
        # Compute qa_next and delta AFTER controller returned
        qa_next = new_params.qa_min_score
        delta_qa = qa_next - qa_used
        
        # Update current_params for next epoch
        current_params = new_params

        total_sugg = m.total_suggestions if m.total_suggestions is not None else (executed + backlog)
        backlog_ratio = backlog / max(1, total_sugg)

        history_rows.append(
            {
                "epoch": epoch_idx,
                "qa_used": float(qa_used),
                "qa_next": float(qa_next),
                "delta_qa": float(delta_qa),
                "executed_tasks": executed,
                "backlog_count": backlog,
                "total_suggestions": total_sugg,
                "backlog_ratio": float(backlog_ratio),
                "avg_reward_per_task": float(m.avg_reward_per_task),
            }
        )

    # Write CSV
    fieldnames = [
        "epoch",
        "qa_used",
        "qa_next",
        "delta_qa",
        "executed_tasks",
        "backlog_count",
        "total_suggestions",
        "backlog_ratio",
        "avg_reward_per_task",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in history_rows:
            w.writerow(row)

    return metrics_log
