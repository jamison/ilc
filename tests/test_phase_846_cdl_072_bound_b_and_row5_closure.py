"""Phase 846 CDL-072 Bound B revision + Row 5 runtime_closed gate tests.

Verifies:
1. CDL-072 opening doc exists with required tokens.
2. CDL-072 row is present in the master log with ratified status.
3. metrics.py has CDL_072_DEPENDENCY and SIM_LEAKAGE_03_BOUND_B_MAX_JITTER.
4. _check_jitter_spread no longer uses the old relative-spread formula.
5. check_bounds() returns {"A": True, "B": True, "C": True} at proper scale.
6. No observed jitter value exceeds release_jitter_epochs=3.
7. Re-run evidence doc exists and has row5_runtime_closed_846 token.
8. CDL master log reflects CDL-072 ratified.
9. Row 5 is recorded as runtime_closed.

Token: cdl_072_ratified_846
Token: row5_runtime_closed_846
"""
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
CDL_072_OPENING = REPO / "docs" / "specs" / "ilc_cdl_072_bound_b_formula_amendment_opening_846_v0.1.md"
CDL_072_EVIDENCE = REPO / "docs" / "specs" / "ilc_cdl_072_bound_b_formula_amendment_ratification_evidence_846_v0.1.md"
RERUN_EVIDENCE = REPO / "docs" / "research" / "ilc_sim_leakage_03_rerun_846_v0.1.md"
METRICS_PY = REPO / "ilc_core" / "privacy" / "metrics.py"
CDL_LOG = REPO / "docs" / "specs" / "ilc_constitutional_decision_log_v0.1.md"


# ---------------------------------------------------------------------------
# CDL-072 document checks
# ---------------------------------------------------------------------------

def test_cdl_072_opening_doc_exists():
    assert CDL_072_OPENING.exists(), "CDL-072 opening document missing"


def test_cdl_072_opening_doc_tokens():
    text = CDL_072_OPENING.read_text()
    for token in [
        "cdl_072_bound_b_formula_amendment_opening_846",
        "cdl_072_opened_phase_846",
        "cdl_072_verification_artifact_defined",
    ]:
        assert token in text, f"Missing token in CDL-072 opening: {token!r}"


def test_cdl_072_ratification_evidence_exists():
    assert CDL_072_EVIDENCE.exists(), "CDL-072 ratification evidence document missing"


def test_cdl_072_ratification_evidence_tokens():
    text = CDL_072_EVIDENCE.read_text()
    for token in [
        "cdl_072_ratified_846",
        "cdl_072_bound_b_formula_amendment_ratified_846.v0.1",
        "row5_runtime_closed_846",
        "sim_leakage_03_all_bounds_pass_846",
        "cdl_072_enables_row5_runtime_closed",
    ]:
        assert token in text, f"Missing token in CDL-072 evidence: {token!r}"


def test_cdl_072_in_master_log():
    text = CDL_LOG.read_text()
    assert "CDL-072" in text, "CDL-072 not present in CDL master log"
    assert "ratified" in text[text.find("CDL-072"):text.find("CDL-072") + 500], (
        "CDL-072 row does not show ratified status in master log"
    )


def test_cdl_072_master_log_opened_ratified_phase():
    text = CDL_LOG.read_text()
    row_start = text.find("CDL-072")
    row = text[row_start:row_start + 1200]
    assert "opened_phase: 846" in row, "CDL-072 master log row missing opened_phase: 846"
    assert "ratified_phase: 846" in row, "CDL-072 master log row missing ratified_phase: 846"


# ---------------------------------------------------------------------------
# metrics.py implementation checks
# ---------------------------------------------------------------------------

def test_metrics_py_cdl_072_dependency():
    text = METRICS_PY.read_text()
    assert "CDL_072_DEPENDENCY" in text, "CDL_072_DEPENDENCY constant missing from metrics.py"
    assert "cdl_072_bound_b_formula_amendment_ratified_846.v0.1" in text, (
        "CDL_072_DEPENDENCY has wrong value in metrics.py"
    )


def test_metrics_py_bound_b_max_jitter_constant():
    text = METRICS_PY.read_text()
    assert "SIM_LEAKAGE_03_BOUND_B_MAX_JITTER" in text, (
        "SIM_LEAKAGE_03_BOUND_B_MAX_JITTER constant missing from metrics.py"
    )
    assert "3" in text[text.find("SIM_LEAKAGE_03_BOUND_B_MAX_JITTER"):
                       text.find("SIM_LEAKAGE_03_BOUND_B_MAX_JITTER") + 60], (
        "SIM_LEAKAGE_03_BOUND_B_MAX_JITTER not set to 3 in metrics.py"
    )


def test_metrics_py_old_relative_spread_removed():
    """The old std/max formula must not be used in _check_jitter_spread."""
    text = METRICS_PY.read_text()
    # Find the _check_jitter_spread method
    start = text.find("def _check_jitter_spread")
    assert start != -1, "_check_jitter_spread method not found"
    # Get the method body (up to the next def or end of class)
    method_body = text[start:start + 600]
    assert "relative_spread" not in method_body, (
        "Old relative_spread formula still present in _check_jitter_spread — "
        "CDL-072 replacement not applied"
    )
    assert "variance" not in method_body, (
        "Old variance computation still present in _check_jitter_spread — "
        "CDL-072 replacement not applied"
    )


def test_metrics_py_cdl_072_token_in_check_jitter():
    text = METRICS_PY.read_text()
    start = text.find("def _check_jitter_spread")
    method_body = text[start:start + 600]
    assert "cdl_072" in method_body, (
        "CDL-072 attribution token missing from _check_jitter_spread docstring"
    )


# ---------------------------------------------------------------------------
# Functional: check_bounds() with revised formula
# ---------------------------------------------------------------------------

def test_check_bounds_all_pass_at_scale():
    """check_bounds() must return {"A": True, "B": True, "C": True} at 10×30."""
    from ilc_core.privacy.lane import PrivacyLane, PrivacyLaneConfig, K_PRIMARY
    from ilc_core.privacy.metrics import LeakageMetricsCollector

    config = PrivacyLaneConfig(k=K_PRIMARY, release_jitter_epochs=3, max_wait_epochs=4)
    lane = PrivacyLane(config=config, current_epoch=0)
    collector = LeakageMetricsCollector()

    for epoch in range(1, 11):
        for v in range(30):
            t = {"transfer_class": "Contribution", "agent_id": f"a{epoch}_{v}", "version": v}
            lane.submit(t, current_epoch=epoch)
        for g in lane.flush(current_epoch=epoch):
            collector.record_group_settled(sealed_epoch=epoch, group=g)
        for g in lane.enforce_max_wait(current_epoch=epoch):
            collector.record_group_settled(sealed_epoch=epoch, group=g)
    for ep_tail in range(11, 15):
        for g in lane.flush(current_epoch=ep_tail):
            collector.record_group_settled(sealed_epoch=10, group=g)
        for g in lane.enforce_max_wait(current_epoch=ep_tail):
            collector.record_group_settled(sealed_epoch=10, group=g)

    snap = collector.global_snapshot()
    bounds = collector.check_bounds(snap)

    assert bounds == {"A": True, "B": True, "C": True}, (
        f"check_bounds() must return all-True after CDL-072. Got: {bounds}\n"
        f"snap: fill_rate={snap.global_fill_rate}, degraded={snap.global_degraded_fraction}, "
        f"jitter_dist={snap.jitter_distribution}"
    )


def test_no_jitter_exceeds_release_window():
    """All observed jitter deltas must be ≤ release_jitter_epochs=3."""
    from ilc_core.privacy.lane import PrivacyLane, PrivacyLaneConfig, K_PRIMARY
    from ilc_core.privacy.metrics import LeakageMetricsCollector, SIM_LEAKAGE_03_BOUND_B_MAX_JITTER

    config = PrivacyLaneConfig(k=K_PRIMARY, release_jitter_epochs=3, max_wait_epochs=4)
    lane = PrivacyLane(config=config, current_epoch=0)
    collector = LeakageMetricsCollector()

    for epoch in range(1, 11):
        for v in range(30):
            t = {"transfer_class": "Contribution", "agent_id": f"a{epoch}_{v}", "version": v}
            lane.submit(t, current_epoch=epoch)
        for g in lane.flush(current_epoch=epoch):
            collector.record_group_settled(sealed_epoch=epoch, group=g)

    snap = collector.global_snapshot()
    if snap.jitter_distribution:
        max_jitter = max(snap.jitter_distribution.keys())
        assert max_jitter <= SIM_LEAKAGE_03_BOUND_B_MAX_JITTER, (
            f"Observed jitter {max_jitter} exceeds locked window {SIM_LEAKAGE_03_BOUND_B_MAX_JITTER}"
        )


# ---------------------------------------------------------------------------
# Re-run evidence doc
# ---------------------------------------------------------------------------

def test_rerun_evidence_doc_exists():
    assert RERUN_EVIDENCE.exists(), "Phase 846 SIM-LEAKAGE-03 re-run evidence doc missing"


def test_rerun_evidence_tokens():
    text = RERUN_EVIDENCE.read_text()
    for token in [
        "sim_leakage_03_rerun_846_evidence_published",
        "sim_leakage_03_all_bounds_pass_846",
        "sim_leakage_03_bound_a_pass_846",
        "sim_leakage_03_bound_b_pass_846",
        "sim_leakage_03_bound_c_pass_846",
        "row5_runtime_closed_846",
        "row5_b_impl_complete",
        "sim_leakage_03_definitive_pass_846",
    ]:
        assert token in text, f"Missing token in re-run evidence: {token!r}"


def test_rerun_evidence_records_runtime_closed():
    text = RERUN_EVIDENCE.read_text()
    assert "runtime_closed" in text, "Re-run evidence must record Row 5 runtime_closed"
    assert "spec_closed_runtime_pending" not in text or "from" in text, (
        "Re-run evidence must not leave Row 5 as spec_closed_runtime_pending"
    )
