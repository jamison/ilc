# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass, asdict
from typing import Dict, List, TypedDict
from os import PathLike
from pathlib import Path
import csv

from ilc_core.graph import EpistemicGraph
from ilc_core.protocol.params import ProtocolParams
from ilc_core.analysis.graph_kpis import (
    compute_claim_link_stats,
    get_local_influence_scores,
)


class ClaimInfluenceRowDict(TypedDict):
    claim_id: str
    supports_in: int
    refutes_in: int
    equivalent_in: int
    depends_on_in: int
    net_support: int
    influence_score: float

@dataclass
class ClaimInfluenceRow:
    claim_id: str
    supports_in: int
    refutes_in: int
    equivalent_in: int
    depends_on_in: int
    net_support: int
    influence_score: float

    def as_dict(self) -> ClaimInfluenceRowDict:
        return asdict(self)

def build_claim_influence_table(
    graph: EpistemicGraph,
    params: ProtocolParams,
) -> List[ClaimInfluenceRow]:
    """
    Build a claim influence table from the current graph and protocol params.

    Combines link stats with local influence scores.
    Only claims that appear as targets of at least one link are included for now.
    """
    stats = compute_claim_link_stats(graph)
    scores = get_local_influence_scores(graph, params)

    rows: List[ClaimInfluenceRow] = []

    for claim_id, s in stats.items():
        score = float(scores.get(claim_id, 0.0))
        rows.append(
            ClaimInfluenceRow(
                claim_id=claim_id,
                supports_in=s.supports_in,
                refutes_in=s.refutes_in,
                equivalent_in=s.equivalent_in,
                depends_on_in=s.depends_on_in,
                net_support=s.net_support,
                influence_score=score,
            )
        )

    return rows

def write_claim_influence_csv(
    rows: List[ClaimInfluenceRow],
    path: PathLike,
) -> None:
    """
    Write the claim influence table to a CSV file.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        # Still write header for consistency
        fieldnames = [
            "claim_id",
            "supports_in",
            "refutes_in",
            "equivalent_in",
            "depends_on_in",
            "net_support",
            "influence_score",
        ]
        with p.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
        return

    fieldnames = list(rows[0].as_dict().keys())
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())
