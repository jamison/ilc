from dataclasses import dataclass, field
from typing import Dict, Any, List
from ilc_core.analysis.claim_scores import ClaimInfluenceRow
from os import PathLike

from ilc_core.analysis.econ_kpis import (
    load_tasks_csv,
    load_epochs_csv,
    load_claims_csv,
    compute_agent_econ_kpis,
    compute_claim_kpis,
)

@dataclass
class AgentProfile:
    agent_id: str

    # Econ KPIs (from compute_basic_kpis)
    econ: Dict[str, float] = field(default_factory=dict)

    # Claim KPIs (from compute_claim_kpis)
    claims: Dict[str, float] = field(default_factory=dict)

    # Influence KPIs (from compute_agent_influence_kpis)
    influence: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        """
        Flatten into a single dict for printing/JSON export.
        Namespaces econ_* and claim_* keys to avoid collisions.
        """
        data: Dict[str, Any] = {"agent_id": self.agent_id}
        for k, v in self.econ.items():
            data[f"econ_{k}"] = v
        for k, v in self.claims.items():
            data[f"claim_{k}"] = v
        for k, v in self.influence.items():
            data[f"influence_{k}"] = v
        return data

def build_agent_profiles(
    tasks_csv_path: PathLike,
    epochs_csv_path: PathLike,
    claims_csv_path: PathLike,
) -> Dict[str, AgentProfile]:
    """
    Load CSVs, compute econ + claim KPIs, and join them into AgentProfile objects.

    Returns:
        {agent_id: AgentProfile}
    """
    tasks = load_tasks_csv(tasks_csv_path)
    epochs = load_epochs_csv(epochs_csv_path)
    claims = load_claims_csv(claims_csv_path)

    econ_kpis = compute_agent_econ_kpis(tasks)
    claim_kpis = compute_claim_kpis(claims)

    profiles: Dict[str, AgentProfile] = {}

    # Seed profiles from econ
    for agent_id, econ_stats in econ_kpis.items():
        profiles.setdefault(agent_id, AgentProfile(agent_id=agent_id)).econ = dict(econ_stats)

    # Merge claim stats
    for agent_id, claim_stats in claim_kpis.items():
        profile = profiles.setdefault(agent_id, AgentProfile(agent_id=agent_id))
        profile.claims = dict(claim_stats)

    return profiles

def compute_agent_influence_kpis(
    claim_influence_rows: List[ClaimInfluenceRow],
    claims_csv_path: PathLike,
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate claim influence metrics per agent.

    Uses claims.csv to map claim_id -> agent_id, then aggregates:

        total_influence
        avg_influence
        num_influenced_claims
        total_net_support

    Returns:
        {agent_id: {metric_name: value}}
    """
    claim_rows = load_claims_csv(claims_csv_path)
    claim_to_agent: Dict[str, str] = {}
    for row in claim_rows:
        cid = row.get("id")
        aid = row.get("agent_id") or "unknown"
        if cid:
            claim_to_agent[cid] = aid

    per_agent: Dict[str, Dict[str, float]] = {}

    for row in claim_influence_rows:
        claim_id = row.claim_id
        agent_id = claim_to_agent.get(claim_id, "unknown")

        stats = per_agent.setdefault(
            agent_id,
            {
                "total_influence": 0.0,
                "num_influenced_claims": 0.0,
                "total_net_support": 0.0,
            },
        )

        stats["total_influence"] += row.influence_score
        stats["num_influenced_claims"] += 1.0
        stats["total_net_support"] += float(row.net_support)

    # Compute derived metrics like avg_influence
    for stats in per_agent.values():
        n = stats["num_influenced_claims"]
        stats["avg_influence"] = stats["total_influence"] / n if n > 0 else 0.0

    return per_agent

def attach_influence_to_profiles(
    profiles: Dict[str, AgentProfile],
    claim_influence_rows: List[ClaimInfluenceRow],
    claims_csv_path: PathLike,
) -> None:
    """
    Compute per-agent influence KPIs and merge them into existing profiles in-place.
    """
    influence_kpis = compute_agent_influence_kpis(
        claim_influence_rows,
        claims_csv_path,
    )

    for agent_id, stats in influence_kpis.items():
        profile = profiles.setdefault(agent_id, AgentProfile(agent_id=agent_id))
        profile.influence = dict(stats)
