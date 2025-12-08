import pytest
from ilc_core.consensus.governance import Governance, BacklogMetrics

def test_hardware_scale_faster_network_cheaper_ecu():
    """
    If network median potential > genesis potential, hardware_scale should be < 1.0.
    """
    gov = Governance()
    # Genesis is 0.1 by default
    
    # Case 1: Same as genesis -> scale ~ 1.0
    gov.update_hardware_potential([0.1, 0.1, 0.1])
    assert abs(gov.hardware_scale - 1.0) < 1e-6
    
    # Case 2: Faster (0.5) -> scale should be 1 / (0.5/0.1) = 1/5 = 0.2
    # But it is clamped to 0.25
    gov.update_hardware_potential([0.4, 0.5, 0.6])
    assert gov.hardware_scale == 0.25
    
    # Case 3: Moderately faster (0.2) -> scale = 1 / (0.2/0.1) = 0.5
    gov.update_hardware_potential([0.2])
    assert abs(gov.hardware_scale - 0.5) < 1e-6

def test_hardware_scale_slower_network_more_expensive_ecu():
    """
    If network median potential < genesis potential, hardware_scale should be > 1.0.
    """
    gov = Governance()
    # Genesis 0.1
    
    # Case: Slower (0.05) -> scale = 1 / (0.05/0.1) = 1 / 0.5 = 2.0
    gov.update_hardware_potential([0.05])
    assert abs(gov.hardware_scale - 2.0) < 1e-6
    
    # Case: Very slow (0.01) -> scale = 1 / 0.1 = 10.0 -> clamped to 4.0
    gov.update_hardware_potential([0.01])
    assert gov.hardware_scale == 4.0

def test_congestion_multiplier_increases_with_backlog():
    """
    Congestion multiplier should rise as backlog increases.
    """
    gov = Governance()
    
    # Initial state -> 1.0
    assert gov.congestion_multiplier == 1.0
    
    # Add backlog
    # backlog_gain is 0.05 by default
    # Update 1: backlog=20, finalized=0 -> raw_score=20 -> normalized=10 (cap)
    # factor = 1 + 0.05 * 10 = 1.5 (price_max)
    # But wait, congestion score is smoothed with alpha=0.5
    # score = 0.5 * 20 + 0.5 * 0 = 10
    # normalized = 10
    # factor = 1.5
    
    metrics = BacklogMetrics(backlog_len=20, finalized_last_epoch=0)
    gov.update_congestion(metrics)
    
    assert gov.congestion_multiplier > 1.0
    assert gov.congestion_multiplier <= gov.price_max
    
    # Check exact value if we trust the math:
    # score = 10.0
    # normalized = 10.0
    # factor = 1.0 + 0.05 * 10.0 = 1.5
    assert abs(gov.congestion_multiplier - 1.5) < 1e-6

def test_get_task_fee_ecu_combines_hardware_and_congestion():
    """
    Fee should reflect both hardware scaling and congestion.
    """
    # Fix base cost for predictability
    config = {
        "ecu": {"base_costs": {"claim.submit": 0.05}},
        "backlog_hotspot_pricing": {"enabled": True}
    }
    gov = Governance(config=config)
    
    # 1. Baseline
    # hardware_scale = 1.0 (default 0.1 / 0.1)
    # congestion = 1.0
    # fee = 0.05 * 1.0 * 1.0 = 0.05
    assert gov.get_task_fee_ecu("claim.submit") == 0.05
    
    # 2. Fast Hardware (4x genesis -> 0.25 scale)
    gov.update_hardware_potential([0.4]) # median 0.4 = 4x 0.1
    # scale = 0.25
    # fee = 0.05 * 0.25 = 0.0125
    assert gov.get_task_fee_ecu("claim.submit") == 0.0125
    
    # 3. Add Congestion
    # backlog=20 -> score=10 -> mult=1.5
    gov.update_congestion(BacklogMetrics(backlog_len=20, finalized_last_epoch=0))
    
    # fee = 0.05 * 0.25 * 1.5 = 0.0125 * 1.5 = 0.01875
    expected = 0.01875
    assert abs(gov.get_task_fee_ecu("claim.submit") - expected) < 1e-8
