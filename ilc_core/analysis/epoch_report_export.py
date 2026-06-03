# SPDX-License-Identifier: AGPL-3.0-only
from os import PathLike
from pathlib import Path
from typing import Dict, List, TypeAlias
import csv
import json

from ilc_core.analysis.namespace_health import NamespaceHealthSnapshot
from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.agent_dossier_export import AgentDossierRow, flatten_profile_for_csv

EpochAgentRow: TypeAlias = AgentDossierRow
EpochAgentRows: TypeAlias = List[EpochAgentRow]

def build_epoch_agent_rows(
    epoch_index: int,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
) -> EpochAgentRows:
    """
    For each agent, build a flattened row combining:
      - epoch_index
      - namespace fields (e.g. namespace_id, total_stress, cohesion_score, etc.)
      - flattened agent dossier fields (via flatten_profile_for_csv)
    """
    rows: EpochAgentRows = []
    
    # Base/Shared fields for all rows in this epoch
    # We include key metrics. Can include more if needed.
    namespace_base: EpochAgentRow = {
        "epoch_index": epoch_index,
        "namespace_id": namespace_snapshot.namespace_id,
        "total_stress": namespace_snapshot.total_stress,
        "cohesion_score": namespace_snapshot.cohesion_score,
        "contradiction_overflow": namespace_snapshot.contradiction_overflow,
        "validation_depth_error": namespace_snapshot.validation_depth_error,
    }
    
    for profile in profiles.values():
        row = namespace_base.copy()
        agent_flat = flatten_profile_for_csv(profile)
        row.update(agent_flat)
        rows.append(row)
        
    return rows

def export_epoch_report_to_csv(
    epoch_index: int,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    path: PathLike,
) -> None:
    """
    Writes a CSV where each row is one agent at a given epoch, with
    namespace_* and agent_* columns combined.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    rows = build_epoch_agent_rows(epoch_index, namespace_snapshot, profiles)
    
    if not rows:
        # Fallback header if no agents
        fieldnames = ["epoch_index", "namespace_id", "total_stress", "cohesion_score", "agent_id"]
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

def export_epoch_report_to_json(
    epoch_index: int,
    namespace_snapshot: NamespaceHealthSnapshot,
    profiles: Dict[str, AgentProfile],
    path: PathLike,
) -> None:
    """
    Exports a nested JSON structure like:
      {
        "epoch_index": ...,
        "namespace": { ... snapshot.as_dict() ... },
        "agents": [ ... flattened profiles ... ]
      }
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    namespace_dict = namespace_snapshot.as_dict()
    agent_rows = [flatten_profile_for_csv(pf) for pf in profiles.values()]
    
    payload = {
        "epoch_index": epoch_index,
        "namespace": namespace_dict,
        "agents": agent_rows,
    }
    
    with p.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
