from ilc_core.analysis.epistemic_code import (
    TargetEpistemicConfig,
    NamespaceStats,
    compute_config_error,
)
import pytest

def test_compute_config_error_no_overflow_or_deficit():
    target = TargetEpistemicConfig(
        target_avg_validation_depth=2.0,
        max_contradiction_density=0.2,
        min_crosslink_ratio=0.1,
    )
    stats = NamespaceStats(
        avg_validation_depth=2.0,
        contradiction_density=0.1,
        crosslink_ratio=0.2,
    )

    errors = compute_config_error(target, stats)
    assert errors["validation_depth_error"] == 0.0
    assert errors["contradiction_overflow"] == 0.0
    assert errors["crosslink_deficit"] == 0.0

def test_compute_config_error_with_overflow_and_deficit():
    target = TargetEpistemicConfig(
        target_avg_validation_depth=1.5,
        max_contradiction_density=0.2,
        min_crosslink_ratio=0.3,
    )
    stats = NamespaceStats(
        avg_validation_depth=2.0,
        contradiction_density=0.5,
        crosslink_ratio=0.1,
    )

    errors = compute_config_error(target, stats)
    # depth is above target
    assert errors["validation_depth_error"] == 0.5
    # contradiction overflow: 0.5 - 0.2 = 0.3
    assert errors["contradiction_overflow"] == pytest.approx(0.3)
    # crosslink deficit: 0.3 - 0.1 = 0.2
    assert errors["crosslink_deficit"] == pytest.approx(0.2)
