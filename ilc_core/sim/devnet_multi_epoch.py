from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, TypeAlias
from os import PathLike
from pathlib import Path
from datetime import datetime, timezone

from ilc_core.network.topology import DevnetTopology
from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.sim.devnet_epoch_orchestrator import DevnetEpochResult, run_devnet_epoch
from ilc_core.protocol.event_log import EventLogger, write_events_to_file, make_canonical_commit_epoch_event
from ilc_core.protocol.params import ProtocolParams
from ilc_core.ledger.backend import LedgerBackend
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.ledger.ledger_export import (
    export_ledger_state_json, 
    export_ledger_state_csv,
    export_ledger_distribution_checks_csv
)
from ilc_core.ledger.canon_export import export_canon_state_json
from ilc_core.analysis.utility_flow_rewards import (
    assert_refutation_profitability_invariant,
    UtilityFlowRewardAllocation,
)

BalanceSnapshot: TypeAlias = Dict[str, float]
NodeLoadRow: TypeAlias = Dict[str, float]
NodeLoadMap: TypeAlias = Dict[str, NodeLoadRow]


@dataclass
class DevnetMultiEpochResult:
    namespace_id: str
    topology: DevnetTopology
    epoch_results: List[DevnetEpochResult]
    aggregate_node_load: NodeLoadMap

def _prepare_epoch_env(
    export_root: Optional[PathLike],
    export_prefix: str,
    epoch_index: int
) -> Tuple[Optional[Path], Optional[EventLogger]]:
    if not export_root:
        return None, None
        
    p_root = Path(export_root)
    dir_name = f"{export_prefix}_{epoch_index:04d}"
    export_dir = p_root / dir_name
    # Enable logging if exporting
    return export_dir, EventLogger(events=[])

def _settle_epoch(
    ledger_backend: LedgerBackend,
    snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    result: DevnetEpochResult,
    event_logger: Optional[EventLogger],
    epoch_id: str
) -> Optional[BalanceSnapshot]:
    # 1. Store Stake Snapshot
    stakes = {
        agent_id: Decimal(str(getattr(profile, "stake", Decimal("1"))))
        for agent_id, profile in profiles.items()
    }
    
    stake_snapshot = StakeSnapshot(
        epoch_id=epoch_id,
        epoch_index=snapshot.epoch_index,
        namespace_id=snapshot.namespace_id,
        stakes=stakes,
        total_stake=sum(stakes.values(), Decimal("0")),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    ledger_backend.put_stake_snapshot(stake_snapshot)

    # 2. Compute Summary from Result
    total_tasks = int(sum(m.get("num_tasks", 0) for m in result.node_load_metrics.values()))
    total_reward = sum(
        Decimal(str(m.get("total_reward", 0)))
        for m in result.node_load_metrics.values()
    )

    invariant_rows: list[UtilityFlowRewardAllocation] = []
    for index, task in enumerate(result.routed_task_rows):
        reward = task.get("reward")
        if not isinstance(reward, (int, float)) or reward <= 0.0:
            continue
        task_type = str(task.get("task_type", "")).lower()
        action_kind = "other"
        if "refute" in task_type:
            action_kind = "refutation"
        elif "valid" in task_type:
            action_kind = "validation"

        invariant_rows.append(
            {
                "node_id": f"{task.get('agent_id', 'agent')}:{index}",
                "is_genesis": False,
                "utility_flow": float(reward),
                "weighted_utility_flow": float(reward),
                "action_kind": action_kind,
                "stake_spent": 0.0,
                "effort_units": 1.0,
                "pairing_key": str(task.get("problem_space", "")),
                "reward_share": 0.0,
                "reward_amount": float(reward),
                "net_reward": float(reward),
            }
        )
    assert_refutation_profitability_invariant(invariant_rows)
    
    # 3. Create Commit Event
    commit_evt = make_canonical_commit_epoch_event(
        epoch_index=snapshot.epoch_index,
        epoch_id=epoch_id,
        namespace_id=snapshot.namespace_id,
        finalization_state="committed",
        summary={
            "task_count": total_tasks,
            "agent_count": len(stakes),
            "reward_total": total_reward,
            "stake_total": sum(stakes.values(), Decimal("0")),
        },
        checksums={
            "epoch_events_cid": "devnet:events",  # Placeholder
            "epoch_state_cid": "devnet:state",    # Placeholder
        },
        source="sim:devnet_multi_epoch",
    )
    
    # 4. Apply Settlement
    balances_before = None
    if hasattr(ledger_backend, "balances"):
         balances_before = ledger_backend.balances.copy()
    
    ledger_backend.apply_epoch_settlement(commit_evt)
    
    # 5. Log Event
    if event_logger:
        event_logger.emit(
            kind="commit.epoch",
            payload=commit_evt.payload,
            source=commit_evt.source,
        )
        
    return balances_before

def _export_epoch_ledger_artifacts(
    export_dir: Path,
    ledger_backend: LedgerBackend,
    balances_before: Optional[BalanceSnapshot],
    epoch_id: str
) -> None:
    # Export with verification check
    check = export_ledger_state_json(
        ledger_backend, 
        export_dir / "ledger_state.json",
        balances_before=balances_before,
        target_epoch_id=epoch_id
    )
    export_ledger_state_csv(ledger_backend, export_dir / "ledger_state.csv")

    # If we performed a check, write the verification CSV
    if check:
        # Add epoch_id to the check result for the CSV row
        check["epoch_id"] = epoch_id
        export_ledger_distribution_checks_csv(
            [check],
            export_dir / "ledger_distribution_checks.csv"
        )

    # Phase 71: Canon Export
    export_canon_state_json(
        ledger_backend,
        export_dir / "canon_state.json"
    )

def _aggregate_metrics(
    epoch_results: List[DevnetEpochResult]
) -> NodeLoadMap:
    # Gather all node IDs seen across any epoch
    all_nodes = set()
    for res in epoch_results:
        all_nodes.update(res.node_load_metrics.keys())
        
    agg_load: NodeLoadMap = {}
    
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
    return agg_load

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
        rng_seed: Deprecated compatibility parameter. No global PRNG state is
                  mutated; devnet execution must remain deterministic from
                  explicit fixture inputs.
        ledger_backend: Optional ledger backend for settlement and persistence.
                        If provided, settles the epoch and stores snapshots.
        
    Returns:
        DevnetMultiEpochResult containing all per-epoch results and aggregate metrics.
    """
    _ = rng_seed
    
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
        export_dir, event_logger = _prepare_epoch_env(
            export_root, export_prefix, snapshot.epoch_index
        )
            
        result = run_devnet_epoch(
            epoch_index=snapshot.epoch_index,
            topology=topology,
            namespace_snapshot=snapshot,
            profiles=profiles,
            export_dir=export_dir,
            event_logger=event_logger,
            protocol_params=protocol_params
        )

        epoch_id = f"{snapshot.namespace_id}:{snapshot.epoch_index:04d}"
        balances_before = None

        if ledger_backend:
            balances_before = _settle_epoch(
                ledger_backend, snapshot, profiles, result, event_logger, epoch_id
            )
        
        # If we logged events (sim or commit), write them out
        if export_dir and event_logger:
            write_events_to_file(
                event_logger.events,
                export_dir / "devnet_events.ndjson"
            )

        # Ledger Export & Verification
        if export_dir and ledger_backend:
            _export_epoch_ledger_artifacts(
                export_dir, ledger_backend, balances_before, epoch_id
            )

        epoch_results.append(result)

    # 3. Aggregate Node Load
    agg_load = _aggregate_metrics(epoch_results)

    # 4. Namespace ID
    ns_id = snapshots[0].namespace_id
    
    return DevnetMultiEpochResult(
        namespace_id=ns_id,
        topology=topology,
        epoch_results=epoch_results,
        aggregate_node_load=agg_load
    )
