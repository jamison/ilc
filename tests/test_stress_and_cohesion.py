import pytest
from ilc_core.analysis.epistemic_code import TargetEpistemicConfig, NamespaceStats
from ilc_core.analysis.stress_and_cohesion import (
    compute_epistemic_stress,
    compute_cohesion_metrics,
)
from ilc_core.graph import EpistemicGraph
from ilc_core.types import ClaimRecord, LinkRecord
from ilc_core.protocol.params import ProtocolParams

def test_compute_epistemic_stress_basic():
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

    stress = compute_epistemic_stress("ns:test", target, stats)
    
    # validation error: 0.5 - 1.0 = -0.5 -> abs = 0.5
    assert stress.validation_depth_error == pytest.approx(-0.5)
    
    # contradiction overflow: 0.4 - 0.1 = 0.3
    assert stress.contradiction_overflow == pytest.approx(0.3)
    
    # crosslink deficit: 0.2 - 0.1 = 0.1
    assert stress.crosslink_deficit == pytest.approx(0.1)

    # total = 0.5 + 0.3 + 0.1 = 0.9
    assert stress.total_stress == pytest.approx(0.9)

def test_compute_cohesion_metrics_basic():
    g = EpistemicGraph()
    c1 = ClaimRecord(id="c1", type="claim", agent_id="a", content="foo")
    c2 = ClaimRecord(id="c2", type="claim", agent_id="b", content="bar")
    g.add_claim(c1)
    g.add_claim(c2)

    c3 = ClaimRecord(id="c3", type="claim", agent_id="c", content="baz")
    g.add_claim(c3)

    # 1 support, 1 refute on c2 (hotspot)
    g.add_link(LinkRecord(id="l1", link_type="supports", source_id="c1", target_id="c2"))
    g.add_link(LinkRecord(id="l2", link_type="refutes", source_id="c1", target_id="c2"))

    # 1 support on c3 (not hotspot)
    g.add_link(LinkRecord(id="l3", link_type="supports", source_id="c2", target_id="c3"))

    params = ProtocolParams()
    metrics = compute_cohesion_metrics("ns:test", g, params)

    # support_ratio = (1 + 1) / (2 + 1) = 2/3 = 0.666...
    # c2: 1 sup, 1 ref. c3: 1 sup. Total sup=2, ref=1.
    assert metrics.support_ratio == pytest.approx(0.6666666666666666)

    # controversy_ratio: 
    # link_stats keys: c2, c3. (c1 has no incoming links). Total = 2.
    # hotspots: c2. Total = 1.
    # Ratio = 1/2 = 0.5
    assert metrics.controversy_ratio == pytest.approx(0.5)

    # cohesion_score = 0.666... * (1 - 0.5) = 0.333...
    assert metrics.cohesion_score == pytest.approx(0.3333333333333333)
