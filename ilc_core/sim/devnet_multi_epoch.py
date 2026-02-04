from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from os import PathLike
from pathlib import Path

from ilc_core.network.topology import DevnetTopology
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.sim.devnet_epoch_orchestrator import DevnetEpochResult, run_devnet_epoch
from ilc_core.protocol.event_log import EventLogger, write_events_to_file, make_commit_epoch_event
from ilc_core.protocol.params import ProtocolParams
from ilc_core.ledger.backend import LedgerBackend
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.ledger.ledger_export import (
    export_ledger_state_json, 
    export_ledger_state_csv,
    export_ledger_distribution_checks_csv
)
from ilc_core.ledger.canon_export import export_canon_state_json

from datetime import datetime, timezone

@dataclass
class DevnetMultiEpochResult:
    namespace_id: str
    topology: DevnetTopology
    epoch_results: List[DevnetEpochResult]
    aggregate_node_load: Dict[str, Dict[str, float]]

def run_devnet_multi_epoch(
    topology: DevnetTopology,
    snapshots: List[NamespaceHealthSnapshot],
    profiles: Dict[str, AgentProfile],
    *,
    export_root: Optional[PathLike] = None,
    export_prefix: str = "epoch",
    rng_seed: Optional[int] = None,
    protocol_params: Optional[ProtocolParams] = None,
    ledger_backend: Optional[LedgerBackend] = None,
) -> DevnetMultiEpochResult:
    """
    Execute multiple devnet epochs sequentially based on a list of snapshots.
    
    Args:
        topology: The network topology (assumed static across epochs).
        snapshots: A list of NamespaceHealthSnapshot objects defining the sequence of epochs.
        profiles: Agent profiles (assumed static).
        export_root: Optional directory to create per-epoch export subdirectories in.
        export_prefix: Prefix for per-epoch directories (e.g. "epoch_0010").
        rng_seed: Optional seed for Python's global random number generator. 
                  If provided, random.seed(rng_seed) is called before execution.
        ledger_backend: Optional ledger backend for settlement and persistence.
                        If provided, settles the epoch and stores snapshots.
        
    Returns:
        DevnetMultiEpochResult containing all per-epoch results and aggregated node load metrics.
    """
    if rng_seed is not None:
        import random
        random.seed(rng_seed)
    
    # 1. Preconditions
    if not snapshots:
        return DevnetMultiEpochResult(
            namespace_id="",
            topology=topology,
            epoch_results=[],
            aggregate_node_load={}
        )

    # 2. Epoch Loop
    epoch_results: List[DevnetEpochResult] = []
    
    for snapshot in snapshots:
        epoch_index = snapshot.epoch_index
        export_dir_for_epoch = None
        event_logger = None
        
        if export_root:
            p_root = Path(export_root)
            # e.g. epoch_0010
            dir_name = f"{export_prefix}_{epoch_index:04d}"
            export_dir_for_epoch = p_root / dir_name
            # Enable logging if exporting
            event_logger = EventLogger(events=[])
            
        result = run_devnet_epoch(
            epoch_index=epoch_index,
            topology=topology,
            namespace_snapshot=snapshot,
            profiles=profiles,
            export_dir=export_dir_for_epoch,
            event_logger=event_logger,
            protocol_params=protocol_params
        )

        # Ledger Settlement
        if ledger_backend:
            # 1. Store Stake Snapshot
            # Construct a synthetic snapshot assuming uniform stake for now (or from ledger?)
            # Prompt says: "stakes = {agent_id: 1.0 for agent_id in profiles.keys()}"
            epoch_id = f"{snapshot.namespace_id}:{epoch_index:04d}"
            stakes = {agent_id: 1.0 for agent_id in profiles.keys()}
            
            stake_snapshot = StakeSnapshot(
                epoch_id=epoch_id,
                epoch_index=epoch_index,
                namespace_id=snapshot.namespace_id,
                stakes=stakes,
                total_stake=float(len(stakes)),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            ledger_backend.put_stake_snapshot(stake_snapshot)

            # 2. Compute Summary from Result
            # result.node_load_metrics is Dict[node_id, Dict[metric, value]]
            total_tasks = int(sum(m.get("num_tasks", 0) for m in result.node_load_metrics.values()))
            total_reward = float(sum(m.get("total_reward", 0.0) for m in result.node_load_metrics.values()))
            
            # 3. Create Commit Event
            commit_evt = make_commit_epoch_event(
                epoch_index=epoch_index,
                epoch_id=epoch_id,
                namespace_id=snapshot.namespace_id,
                created_at=datetime.now(timezone.utc).isoformat(),
                finalization_state="committed",
                summary={
                    "task_count": total_tasks,
                    "agent_count": len(stakes),
                    "reward_total": total_reward,
                    "stake_total": float(len(stakes)),
                },
                checksums={
                    "epoch_events_cid": "devnet:events",  # Placeholder
                    "epoch_state_cid": "devnet:state",    # Placeholder
                },
                source="sim:devnet_multi_epoch",
            )
            
            # 4. Apply Settlement
            # Capture balances before settlement for verification (Phase 70H)
            balances_before = None
            if hasattr(ledger_backend, "balances"):
                 balances_before = ledger_backend.balances.copy()
            
            ledger_backend.apply_epoch_settlement(commit_evt)
            
            # 5. Log Event (Task B)
            if event_logger:
                event_logger.events.append(commit_evt)
        
        # If we logged events, write them out
        if export_dir_for_epoch and event_logger:
            write_events_to_file(
                event_logger.events,
                export_dir_for_epoch / "devnet_events.ndjson"
            )

        # 6. Phase 70G/H: Ledger Export & Verification
        if export_dir_for_epoch and ledger_backend:
            # Export with verification check
            check = export_ledger_state_json(
                ledger_backend, 
                export_dir_for_epoch / "ledger_state.json",
                balances_before=balances_before,
                target_epoch_id=epoch_id
            )
            export_ledger_state_csv(ledger_backend, export_dir_for_epoch / "ledger_state.csv")

            # If we performed a check, write the verification CSV
            if check:
                # Add epoch_id to the check result for the CSV row
                check["epoch_id"] = epoch_id
                export_ledger_distribution_checks_csv(
                    [check],
                    export_dir_for_epoch / "ledger_distribution_checks.csv"
                )

            # Phase 71: Canon Export
            export_canon_state_json(
                ledger_backend,
                export_dir_for_epoch / "canon_state.json"
            )

        epoch_results.append(result)

    # 3. Aggregate Node Load
    # We want to sum num_tasks and total_reward across all epochs per node.
    # Then recompute avg_reward.
    
    # First, gather all node IDs seen across any epoch
    all_nodes = set()
    for res in epoch_results:
        all_nodes.update(res.node_load_metrics.keys())
        
    agg_load: Dict[str, Dict[str, float]] = {}
    
    for node_id in all_nodes:
        total_tasks = 0.0
        total_reward = 0.0
        
        for res in epoch_results:
            metrics = res.node_load_metrics.get(node_id)
            if metrics:
                total_tasks += metrics.get("num_tasks", 0.0)
                total_reward += metrics.get("total_reward", 0.0)
        
        avg_rew = (total_reward / total_tasks) if total_tasks > 0 else 0.0
        
        agg_load[node_id] = {
            "num_tasks": total_tasks,
            "total_reward": total_reward,
            "avg_reward": avg_rew
        }

    # 4. Namespace ID
    # Assume single namespace for MVP
    ns_id = snapshots[0].namespace_id
    
    return DevnetMultiEpochResult(
        namespace_id=ns_id,
        topology=topology,
        epoch_results=epoch_results,
        aggregate_node_load=agg_load
    )
