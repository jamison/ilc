# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass, asdict
from typing import List, Dict, Iterable
from os import PathLike
from pathlib import Path

from ilc_core.analysis.epistemic_code import TargetEpistemicConfig, NamespaceStats
from ilc_core.analysis.stress_and_cohesion import (
    EpistemicStress,
    CohesionMetrics,
    compute_epistemic_stress,
    compute_cohesion_metrics,
)
from ilc_core.graph import EpistemicGraph
from ilc_core.protocol.params import ProtocolParams


@dataclass
class NamespaceHealthSnapshot:
    epoch_index: int
    namespace_id: str

    # Stress
    validation_depth_error: float
    contradiction_overflow: float
    crosslink_deficit: float
    total_stress: float

    # Cohesion
    support_ratio: float
    controversy_ratio: float
    mean_abs_influence: float
    cohesion_score: float

    def as_dict(self) -> Dict[str, float]:
        return asdict(self)


def build_namespace_health_snapshot(
    epoch_index: int,
    namespace_id: str,
    *,
    target: TargetEpistemicConfig,
    stats: NamespaceStats,
    graph: EpistemicGraph,
    params: ProtocolParams,
) -> NamespaceHealthSnapshot:
    """
    Compute a single NamespaceHealthSnapshot given config, stats, and graph
    for one namespace at one epoch.
    """
    stress = compute_epistemic_stress(namespace_id, target, stats)
    cohesion = compute_cohesion_metrics(namespace_id, graph, params)

    return NamespaceHealthSnapshot(
        epoch_index=epoch_index,
        namespace_id=namespace_id,
        validation_depth_error=stress.validation_depth_error,
        contradiction_overflow=stress.contradiction_overflow,
        crosslink_deficit=stress.crosslink_deficit,
        total_stress=stress.total_stress,
        support_ratio=cohesion.support_ratio,
        controversy_ratio=cohesion.controversy_ratio,
        mean_abs_influence=cohesion.mean_abs_influence,
        cohesion_score=cohesion.cohesion_score,
    )


def build_namespace_health_timeseries(
    records: Iterable[Dict],
    *,
    params: ProtocolParams,
) -> List[NamespaceHealthSnapshot]:
    """
    Build a list of NamespaceHealthSnapshot objects from a sequence of
    configuration/stat/graph records.

    Each record is expected to contain:
      - "epoch_index": int
      - "namespace_id": str
      - "target": TargetEpistemicConfig
      - "stats": NamespaceStats
      - "graph": EpistemicGraph
    """
    snapshots: List[NamespaceHealthSnapshot] = []
    for rec in records:
        snapshot = build_namespace_health_snapshot(
            epoch_index=int(rec["epoch_index"]),
            namespace_id=str(rec["namespace_id"]),
            target=rec["target"],
            stats=rec["stats"],
            graph=rec["graph"],
            params=params,
        )
        snapshots.append(snapshot)
    return snapshots


def write_namespace_health_csv(
    snapshots: List[NamespaceHealthSnapshot],
    path: PathLike,
) -> None:
    """
    Write a namespace health time-series to CSV.

    Always writes a header row; if snapshots is empty, writes only the header.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    import csv

    fieldnames = [
        "epoch_index",
        "namespace_id",
        "validation_depth_error",
        "contradiction_overflow",
        "crosslink_deficit",
        "total_stress",
        "support_ratio",
        "controversy_ratio",
        "mean_abs_influence",
        "cohesion_score",
    ]
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for snap in snapshots:
            row = snap.as_dict()
            # Ensure only expected columns, in order
            writer.writerow({k: row[k] for k in fieldnames})
