# SPDX-License-Identifier: AGPL-3.0-only
from os import PathLike
from pathlib import Path
from typing import Dict, List, TypeAlias
import csv
import json

from ilc_core.analysis.agent_profiles import AgentProfile

ScalarValue: TypeAlias = str | int | float | bool | None
AgentDossierRow: TypeAlias = Dict[str, ScalarValue]
AgentDossierRows: TypeAlias = List[AgentDossierRow]


def flatten_profile_for_csv(profile: AgentProfile) -> AgentDossierRow:
    """
    Flatten an AgentProfile into a 1-level dict suitable for CSV export.

    Strategy:
      - Use profile.as_dict() as the base.
      - Keep simple scalar fields (agent_id, econ_*, claim_*, influence_*, etc.).
      - For nested dicts (competency, stress_response, light_cone), extract
        a small number of top-level summary scalars, and also include a
        *_json column with the full nested data as JSON.
    """
    base = profile.as_dict()
    row: AgentDossierRow = {}

    # Always include agent_id
    row["agent_id"] = base.get("agent_id")

    # Pass through flat econ/claim/influence keys
    for k, v in base.items():
        if k == "agent_id":
            continue
        if k in ("competency", "stress_response", "light_cone"):
            continue
        # Only include scalars; skip any unexpected nested structures
        if not isinstance(v, (dict, list)):
            row[k] = v

    # Competency summary
    comp = base.get("competency") or {}
    if comp:
        global_c = comp.get("global") or {}
        row["competency_total_tasks"] = global_c.get("total_tasks", 0)
        row["competency_avg_success_rate"] = global_c.get("avg_success_rate", 0.0)
        row["competency_json"] = json.dumps(comp)

    # Stress-response summary
    stress = base.get("stress_response") or {}
    if stress:
        # Expect shape like {"by_stress_bucket": {...}, "preference": "..."} for example.
        row["stress_preference"] = stress.get("preference", "")
        row["stress_response_json"] = json.dumps(stress)

    # Light-cone summary
    lc = base.get("light_cone") or {}
    if lc:
        row["light_cone_score"] = lc.get("light_cone_score", 0.0)
        row["light_cone_reach"] = lc.get("reach_score", 0.0)
        row["light_cone_horizon"] = lc.get("horizon_score", 0.0)
        row["light_cone_domain_span"] = lc.get("domain_span", 0)
        row["light_cone_json"] = json.dumps(lc)

    return row

def export_agent_dossiers_to_csv(
    profiles: Dict[str, AgentProfile],
    path: PathLike,
) -> None:
    """
    Export all AgentProfiles to a CSV file.

    - Unions all keys across flattened rows to form the header.
    - Writes one row per agent.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    rows: AgentDossierRows = [flatten_profile_for_csv(pf) for pf in profiles.values()]

    # Handle empty gracefully
    if not rows:
        fieldnames = ["agent_id"]
    else:
        # Union of all keys
        keys = set()
        for r in rows:
            keys.update(r.keys())
        fieldnames = sorted(keys)

    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def export_agent_dossiers_to_json(
    profiles: Dict[str, AgentProfile],
    path: PathLike,
) -> None:
    """
    Export all AgentProfiles to a JSON file as a list of flattened rows.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    rows = [flatten_profile_for_csv(pf) for pf in profiles.values()]
    with p.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
