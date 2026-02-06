import pytest
import csv
from pathlib import Path
from ilc_core.analysis.namespace_health import (
    build_namespace_health_snapshot,
    build_namespace_health_timeseries,
    write_namespace_health_csv,
    NamespaceHealthSnapshot,
)
from ilc_core.analysis.epistemic_code import TargetEpistemicConfig, NamespaceStats
from ilc_core.graph import EpistemicGraph
from ilc_core.protocol.params import ProtocolParams
from ilc_core.types import ClaimRecord, LinkRecord

def test_build_namespace_health_snapshot_basic():
    # Setup
    target = TargetEpistemicConfig(
        target_avg_validation_depth=1.0,
        max_contradiction_density=0.1,
        min_crosslink_ratio=0.2,
    )
    stats = NamespaceStats(
        avg_validation_depth=0.5,
        contradiction_density=0.4,
        crosslink_ratio=0.1,
    )
    g = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="foo", signature="sig")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="bar", signature="sig")
    g.add_claim(c1)
    g.add_claim(c2)
    c3 = ClaimRecord(id="c3", type="claim", agent_id="c", content="baz", signature="sig")
    g.add_claim(c3)
    # 1 support, 1 refute on c2 (hotspot)
    g.add_link(LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2"))
    g.add_link(LinkRecord(id="l2", link_type="refutes", source_id="c1", target_id="c2"))
    # 1 support on c3 (not hotspot)
    g.add_link(LinkRecord(id="l3", link_type="supports", source_id="c2", target_id="c3"))
    
    params = ProtocolParams()

    # Execute
    snapshot = build_namespace_health_snapshot(
        epoch_index=10,
        namespace_id="ns:test",
        target=target,
        stats=stats,
        graph=g,
        params=params,
    )

    # Verify
    assert snapshot.epoch_index == 10
    assert snapshot.namespace_id == "ns:test"
    
    # Stress checks (same logic as stress tests)
    # v_err = 0.5 - 1.0 = -0.5 -> abs 0.5
    # c_over = 0.4 - 0.1 = 0.3
    # x_def = 0.2 - 0.1 = 0.1
    # total = 0.9
    assert snapshot.total_stress == pytest.approx(0.9)

    # Cohesion checks
    # support_ratio = (1 + 1) / (2 + 1) = 2/3 = 0.666...
    # controversy_ratio = 1 hotspot / 2 targets = 0.5
    # cohesion = 0.666... * (1 - 0.5) = 0.333...
    assert snapshot.cohesion_score == pytest.approx(0.3333333333333333)

def test_build_namespace_health_timeseries():
    # Setup minimal records
    target = TargetEpistemicConfig(1.0, 0.1, 0.1)
    stats = NamespaceStats(1.0, 0.1, 0.1)
    g = EpistemicGraph()
    params = ProtocolParams()
    
    records = [
        {"epoch_index": 0, "namespace_id": "ns:a", "target": target, "stats": stats, "graph": g},
        {"epoch_index": 1, "namespace_id": "ns:a", "target": target, "stats": stats, "graph": g},
    ]

    snapshots = build_namespace_health_timeseries(records, params=params)
    
    assert len(snapshots) == 2
    assert snapshots[0].epoch_index == 0
    assert snapshots[1].epoch_index == 1
    assert snapshots[0].namespace_id == "ns:a"

def test_write_namespace_health_csv(tmp_path):
    snapshots = [
        NamespaceHealthSnapshot(
            epoch_index=0,
            namespace_id="ns:test",
            validation_depth_error=0.1,
            contradiction_overflow=0.2,
            crosslink_deficit=0.3,
            total_stress=0.6,
            support_ratio=0.8,
            controversy_ratio=0.1,
            mean_abs_influence=0.5,
            cohesion_score=0.72,
        )
    ]
    
    csv_path = tmp_path / "health.csv"
    write_namespace_health_csv(snapshots, csv_path)
    
    assert csv_path.exists()
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 1
    row = rows[0]
    assert row["epoch_index"] == "0"
    assert row["namespace_id"] == "ns:test"
    assert float(row["total_stress"]) == 0.6
    assert float(row["cohesion_score"]) == 0.72
