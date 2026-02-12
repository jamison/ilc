from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, TypedDict, TypeAlias
from ilc_core.analysis.claim_scores import ClaimInfluenceRow
from ilc_core.analysis.light_cone_kpis import AgentLightConeRow
from os import PathLike

from ilc_core.analysis.econ_kpis import (
    load_tasks_csv,
    load_epochs_csv,
    load_claims_csv,
    compute_agent_econ_kpis,
    compute_claim_kpis,
)


class AgentInfluenceRow(TypedDict):
    total_influence: float
    num_influenced_claims: float
    total_net_support: float
    avg_influence: float


AgentInfluenceMap: TypeAlias = Dict[str, AgentInfluenceRow]
AgentLightConeMap: TypeAlias = Dict[str, AgentLightConeRow]

@dataclass
class AgentProfile:
    agent_id: str
    node_id: Optional[str] = None

    # Econ KPIs (from compute_basic_kpis)
    econ: Dict[str, float] = field(default_factory=dict)

    # Claim KPIs (from compute_claim_kpis)
    claims: Dict[str, float] = field(default_factory=dict)

    # Influence KPIs (from compute_agent_influence_kpis)
    influence: Dict[str, float] = field(default_factory=dict)

    # Competency (from attach_competency_to_profiles)
    competency: Dict[str, Any] = field(default_factory=dict)

    # Stress response patterns (from stress_response_kpis)
    stress_response: Dict[str, Any] = field(default_factory=dict)

    # Light Cone KPIs (from light_cone_kpis)
    light_cone: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        """
        Flatten into a single dict for printing/JSON export.
        Namespaces econ_* and claim_* keys to avoid collisions.
        """
        data: Dict[str, Any] = {"agent_id": self.agent_id}
        if self.node_id is not None:
            data["node_id"] = self.node_id

        for k, v in self.econ.items():
            data[f"econ_{k}"] = v
        for k, v in self.claims.items():
            data[f"claim_{k}"] = v
        for k, v in self.influence.items():
            data[f"influence_{k}"] = v
        if self.competency:
            data["competency"] = self.competency
        if self.stress_response:
            data["stress_response"] = self.stress_response
        if self.light_cone:
            data["light_cone"] = self.light_cone
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


def attach_competency_to_profiles(
    profiles: Dict[str, AgentProfile],
    competency_summary: Dict[str, Dict[str, Any]],
) -> Dict[str, AgentProfile]:
    """
    Attach competency summaries to existing AgentProfile objects.
    If an agent_id in competency_summary is not present in profiles,
    create a new profile shell for it.
    """
    for agent_id, comp in competency_summary.items():
        profile = profiles.get(agent_id)
        if profile is None:
            profile = AgentProfile(agent_id=agent_id)
            profiles[agent_id] = profile
        profile.competency = comp
    return profiles

def compute_agent_influence_kpis(
    claim_influence_rows: List[ClaimInfluenceRow],
    claims_csv_path: PathLike,
) -> AgentInfluenceMap:
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

    per_agent: AgentInfluenceMap = {}

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

def attach_light_cone_to_profiles(
    profiles: Dict[str, AgentProfile],
    light_cone_rows: AgentLightConeMap,
) -> Dict[str, AgentProfile]:
    """
    Attach light-cone metrics to existing AgentProfile objects.
    If an agent_id appears only in light_cone_rows, create a shell profile.
    """
    # Note: light_cone_rows is expected to be Dict[str, AgentLightConeRow]
    # We iterate and access attributes.
    for agent_id, row in light_cone_rows.items():
        profile = profiles.get(agent_id)
        if profile is None:
            profile = AgentProfile(agent_id=agent_id)
            profiles[agent_id] = profile
        profile.light_cone = {
            "reach_score": row.reach_score,
            "horizon_score": row.horizon_score,
            "domain_span": row.domain_span,
            "light_cone_score": row.light_cone_score,
        }
    return profiles
