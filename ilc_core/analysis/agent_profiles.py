from dataclasses import dataclass, field
from typing import Dict, Any
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
