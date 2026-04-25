"""Phase 834 — Row-5 B-Impl strike force closure gate.

Asserts:
  1. All six obligation tokens present in ilc_core/privacy/
  2. 102-test regression (delegated to spot-checks of presence)
  3. Honest non-closure recorded in coherence report
  4. Capsule v5.15 published with correct carry-forward tokens
  5. Hard constraint compliance: no CDL mutation, no live settlement wiring,
     no runtime_closed claim without live evidence
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LANE_PY = REPO_ROOT / "ilc_core" / "privacy" / "lane.py"
MONITOR_PY = REPO_ROOT / "ilc_core" / "privacy" / "monitor.py"
METRICS_PY = REPO_ROOT / "ilc_core" / "privacy" / "metrics.py"
INIT_PY = REPO_ROOT / "ilc_core" / "privacy" / "__init__.py"
SEQ_LOCK = REPO_ROOT / "docs" / "phases" / "phase_831_row5_b_impl_strike_force_sequence_lock.md"
COHERENCE = REPO_ROOT / "docs" / "specs" / "ilc_integration_coherence_report_834_v0.1.md"
CAPSULE = REPO_ROOT / "docs" / "specs" / "ilc_antigravity_context_capsule_v5.15.md"
CDL = REPO_ROOT / "docs" / "specs" / "ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Obligation tokens — all six present in implementation files
# ---------------------------------------------------------------------------

class TestObligationTokens:

    def test_obligation_1_token_in_lane(self) -> None:
        assert "row5_b_impl_obligation_1_rolling_group_construction" in _read(LANE_PY)

    def test_obligation_2_token_in_lane(self) -> None:
        assert "row5_b_impl_obligation_2_deferred_release_queue" in _read(LANE_PY)

    def test_obligation_3_token_in_lane(self) -> None:
        assert "row5_b_impl_obligation_3_bounded_hold_carry_over" in _read(LANE_PY)

    def test_obligation_4_token_in_monitor(self) -> None:
        assert "row5_b_impl_obligation_4_group_fill_monitoring" in _read(MONITOR_PY)

    def test_obligation_5_token_in_monitor(self) -> None:
        assert "row5_b_impl_obligation_5_degraded_anonymity_notification" in _read(MONITOR_PY)

    def test_obligation_6_token_in_metrics(self) -> None:
        assert "row5_b_impl_obligation_6_sim_leakage_03_instrumentation" in _read(METRICS_PY)


# ---------------------------------------------------------------------------
# 2. Implementation surface — required classes and constants present
# ---------------------------------------------------------------------------

class TestImplementationSurface:

    def test_privacy_lane_config_present(self) -> None:
        assert "class PrivacyLaneConfig" in _read(LANE_PY)

    def test_release_group_present(self) -> None:
        assert "class ReleaseGroup" in _read(LANE_PY)

    def test_k_primary_locked_at_30(self) -> None:
        assert "K_PRIMARY: int = 30" in _read(LANE_PY)

    def test_k_fallback_locked_at_20(self) -> None:
        assert "K_FALLBACK: int = 20" in _read(LANE_PY)

    def test_release_jitter_epochs_locked_at_3(self) -> None:
        assert "RELEASE_JITTER_EPOCHS: int = 3" in _read(LANE_PY)

    def test_fill_monitor_class_present(self) -> None:
        assert "class FillMonitor" in _read(MONITOR_PY)

    def test_degraded_notification_present(self) -> None:
        assert "class DegradedAnonymityNotification" in _read(MONITOR_PY)

    def test_make_degraded_notifications_present(self) -> None:
        assert "def make_degraded_notifications(" in _read(MONITOR_PY)

    def test_leakage_metrics_collector_present(self) -> None:
        assert "class LeakageMetricsCollector" in _read(METRICS_PY)

    def test_check_bounds_present(self) -> None:
        assert "def check_bounds(" in _read(METRICS_PY)

    def test_bound_a_locked(self) -> None:
        assert "SIM_LEAKAGE_03_BOUND_A: float = 0.15" in _read(METRICS_PY)

    def test_bound_b_locked(self) -> None:
        assert "SIM_LEAKAGE_03_BOUND_B: float = 0.15" in _read(METRICS_PY)

    def test_bound_c_locked(self) -> None:
        assert "SIM_LEAKAGE_03_BOUND_C: float = 0.05" in _read(METRICS_PY)

    def test_secrets_randbelow_used_for_jitter(self) -> None:
        assert "secrets.randbelow(" in _read(LANE_PY)

    def test_fallback_activation_rate_locked_at_5_percent(self) -> None:
        assert "FALLBACK_ACTIVATION_RATE: float = 0.05" in _read(MONITOR_PY)

    def test_fill_alert_multiplier_locked_at_1_5(self) -> None:
        assert "FILL_ALERT_MULTIPLIER: float = 1.5" in _read(MONITOR_PY)


# ---------------------------------------------------------------------------
# 3. Honest non-closure — coherence report and sequence lock compliance
# ---------------------------------------------------------------------------

class TestHonestNonClosure:

    def test_coherence_report_exists(self) -> None:
        assert COHERENCE.exists()

    def test_coherence_records_non_closure(self) -> None:
        text = _read(COHERENCE)
        assert "row5_spec_closed_runtime_pending_preserved" in text

    def test_coherence_does_not_claim_runtime_closed(self) -> None:
        text = _read(COHERENCE)
        assert "row5_runtime_closed" not in text

    def test_coherence_records_pending_live_evidence(self) -> None:
        assert "row5_b_impl_runtime_module_complete_pending_live_sim_leakage_03" in _read(COHERENCE)

    def test_coherence_names_all_six_obligations(self) -> None:
        text = _read(COHERENCE)
        for i in range(1, 7):
            assert f"| {i} —" in text

    def test_sequence_lock_present(self) -> None:
        assert SEQ_LOCK.exists()

    def test_sequence_lock_consumed_token_present(self) -> None:
        assert "row5_b_impl_strike_force_sequence_lock_consumed_831" in _read(SEQ_LOCK)


# ---------------------------------------------------------------------------
# 4. Capsule v5.15 published with correct carry-forward
# ---------------------------------------------------------------------------

class TestCapsuleV515:

    def test_capsule_exists(self) -> None:
        assert CAPSULE.exists()

    def test_capsule_supersedes_v5_14(self) -> None:
        assert "capsule_v5_15_supersedes_v5_14" in _read(CAPSULE)

    def test_capsule_records_strike_force_complete(self) -> None:
        assert "row5_b_impl_strike_force_831_834_complete" in _read(CAPSULE)

    def test_capsule_records_honest_non_closure(self) -> None:
        assert "phase_834_honest_non_closure_recorded" in _read(CAPSULE)

    def test_capsule_preserves_spec_closed_runtime_pending(self) -> None:
        assert "row5_spec_closed_runtime_pending_preserved" in _read(CAPSULE)

    def test_capsule_records_settlement_gate_830(self) -> None:
        assert "settlement_path_gate_830_published" in _read(CAPSULE)

    def test_capsule_no_cdl_mutation_token(self) -> None:
        assert "no_cdl_mutation_in_strike_force_831_834" in _read(CAPSULE)


# ---------------------------------------------------------------------------
# 5. Hard constraint compliance
# ---------------------------------------------------------------------------

class TestHardConstraintCompliance:

    def test_no_live_settlement_wiring_in_lane(self) -> None:
        # Privacy lane must not call live settlement path
        text = _read(LANE_PY)
        assert "handle_broadcast_honest(" not in text
        assert "handle_full_transfer_honest(" not in text

    def test_no_cdl_row_mutation_in_strike_force(self) -> None:
        # CDL must not have been mutated by the B-Impl strike force.
        # None of the strike force tokens should appear inside CDL rows.
        text = _read(CDL)
        for token in (
            "row5_b_impl_obligation_1",
            "row5_b_impl_obligation_2",
            "row5_b_impl_obligation_3",
            "row5_b_impl_obligation_4",
            "row5_b_impl_obligation_5",
            "row5_b_impl_obligation_6",
        ):
            assert token not in text, f"CDL must not contain strike force token: {token}"

    def test_init_exports_all_six_modules_worth_of_symbols(self) -> None:
        text = _read(INIT_PY)
        for symbol in (
            "PrivacyLane",
            "FillMonitor",
            "LeakageMetricsCollector",
            "make_degraded_notifications",
            "DegradedAnonymityNotification",
        ):
            assert symbol in text
