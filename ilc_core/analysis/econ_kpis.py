# SPDX-License-Identifier: AGPL-3.0-or-later
import csv
from pathlib import Path
from typing import Dict, List, TypedDict, TypeAlias, Union

from ilc_core.protocol.event_export import (
    TASK_OUTCOME_HEADERS,
    EPOCH_SUMMARY_HEADERS,
)

PathLike = Union[str, Path]


class BasicKPIs(TypedDict):
    total_tasks: int
    total_reward_ilc: float
    total_ecu_spent: float
    avg_reward_per_task: float
    realized_price_ilc_per_ecu: float
    tasks_by_domain: Dict[str, int]
    reward_by_domain: Dict[str, float]
    avg_reward_by_domain: Dict[str, float]
    epochs_count: int
    max_epoch: int | None
    total_tasks_from_epochs: int
    avg_tasks_per_epoch: float
    avg_clearing_price_ilc_per_ecu: float


class AgentEconRow(TypedDict):
    tasks: float
    reward: float
    stake_spent: float


class ClaimKpiRow(TypedDict):
    num_claims: float
    total_net_stake: float


AgentEconMap: TypeAlias = Dict[str, AgentEconRow]
ClaimKpiMap: TypeAlias = Dict[str, ClaimKpiRow]
NumericScalar: TypeAlias = str | int | float | bool | None

def load_tasks_csv(path: PathLike) -> List[Dict[str, str]]:
    """
    Load a tasks CSV (task_outcome rows) into a list of dict rows (string values).
    Returns [] if file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return []
    
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_epochs_csv(path: PathLike) -> List[Dict[str, str]]:
    """
    Load an epochs CSV (epoch_summary rows) into a list of dict rows (string values).
    Returns [] if file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return []
    
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_claims_csv(path: PathLike) -> List[Dict[str, str]]:
    """
    Load a claims CSV into a list of dict rows (string values).
    Returns [] if file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return []

    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def _to_float(value: NumericScalar, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def _to_int(value: NumericScalar, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def compute_basic_kpis(
    task_rows: List[Dict[str, str]],
    epoch_rows: List[Dict[str, str]],
) -> BasicKPIs:
    """
    Compute basic economic KPIs from tasks.csv and epochs.csv rows.

    Assumes field names match TASK_OUTCOME_HEADERS / EPOCH_SUMMARY_HEADERS.
    Returns a dict suitable for JSON logging or test assertions.
    """
    # --- Global Task Metrics ---
    total_tasks = len(task_rows)
    total_reward_ilc = 0.0
    total_ecu_spent = 0.0
    
    # Domain breakdown
    tasks_by_domain: Dict[str, int] = {}
    reward_by_domain: Dict[str, float] = {}

    for row in task_rows:
        reward = _to_float(row.get("reward_paid"))
        stake = _to_float(row.get("stake_spent"))
        domain = row.get("domain") or "unknown"

        total_reward_ilc += reward
        total_ecu_spent += stake

        tasks_by_domain[domain] = tasks_by_domain.get(domain, 0) + 1
        reward_by_domain[domain] = reward_by_domain.get(domain, 0.0) + reward

    avg_reward_per_task = total_reward_ilc / total_tasks if total_tasks > 0 else 0.0
    realized_price_ilc_per_ecu = (
        total_reward_ilc / total_ecu_spent if total_ecu_spent > 0 else 0.0
    )

    avg_reward_by_domain: Dict[str, float] = {}
    for d, count in tasks_by_domain.items():
        total_r = reward_by_domain.get(d, 0.0)
        avg_reward_by_domain[d] = total_r / count if count > 0 else 0.0

    # --- Epoch Metrics ---
    epochs_count = len(epoch_rows)
    max_epoch = None
    total_tasks_from_epochs = 0
    sum_clearing_price = 0.0

    for row in epoch_rows:
        ep = _to_int(row.get("epoch"), -1)
        if max_epoch is None or ep > max_epoch:
            max_epoch = ep
        
        total_tasks_from_epochs += _to_int(row.get("total_tasks"))
        sum_clearing_price += _to_float(row.get("clearing_price_ilc_per_ecu"))

    avg_tasks_per_epoch = (
        total_tasks_from_epochs / epochs_count if epochs_count > 0 else 0.0
    )
    avg_clearing_price_ilc_per_ecu = (
        sum_clearing_price / epochs_count if epochs_count > 0 else 0.0
    )

    return {
        "total_tasks": total_tasks,
        "total_reward_ilc": total_reward_ilc,
        "total_ecu_spent": total_ecu_spent,
        "avg_reward_per_task": avg_reward_per_task,
        "realized_price_ilc_per_ecu": realized_price_ilc_per_ecu,
        "tasks_by_domain": tasks_by_domain,
        "reward_by_domain": reward_by_domain,
        "avg_reward_by_domain": avg_reward_by_domain,
        "epochs_count": epochs_count,
        "max_epoch": max_epoch,
        "total_tasks_from_epochs": total_tasks_from_epochs,
        "avg_tasks_per_epoch": avg_tasks_per_epoch,
        "avg_clearing_price_ilc_per_ecu": avg_clearing_price_ilc_per_ecu,
    }


def compute_agent_econ_kpis(
    task_rows: List[Dict[str, str]],
) -> AgentEconMap:
    """
    Compute per-agent economic KPIs from tasks.csv rows.

    Returns:
        {
            agent_id: {
                "tasks": ...,
                "reward": ...,
                "stake_spent": ...,
            },
            ...
        }
    """
    per_agent: AgentEconMap = {}

    for row in task_rows:
        agent_id = row.get("agent_id") or "unknown"
        reward = _to_float(row.get("reward_paid"))
        stake = _to_float(row.get("stake_spent"))

        stats = per_agent.setdefault(
            agent_id,
            {"tasks": 0.0, "reward": 0.0, "stake_spent": 0.0},
        )
        stats["tasks"] += 1.0
        stats["reward"] += reward
        stats["stake_spent"] += stake

    return per_agent

def compute_claim_kpis(
    claim_rows: List[Dict[str, str]]
) -> ClaimKpiMap:
    """
    Compute basic per-agent claim KPIs from claims.csv rows.

    Returns:
        {
            agent_id: {
                "num_claims": ...,
                "total_net_stake": ...,
            },
            ...
        }
    """
    per_agent: ClaimKpiMap = {}

    for row in claim_rows:
        agent_id = row.get("agent_id") or "unknown"
        net_stake_str = row.get("net_stake") or "0"
        try:
            net_stake = float(net_stake_str)
        except ValueError:
            net_stake = 0.0

        stats = per_agent.setdefault(
            agent_id,
            {"num_claims": 0.0, "total_net_stake": 0.0},
        )
        stats["num_claims"] += 1.0
        stats["total_net_stake"] += net_stake

    return per_agent
