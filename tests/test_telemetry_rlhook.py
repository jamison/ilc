import pytest
from ilc_core.economics.telemetry import EconomicTelemetry, RLHook
from ilc_core.economics.outcome import TaskOutcome

def test_telemetry_and_rlhook_noop():
    telemetry = EconomicTelemetry()
    rl = RLHook()

    outcome = TaskOutcome(
        task_type="claim.submit",
        domain="test",
        stake_spent=1.0,
        reward_paid=2.0,
        success=True,
    )

    # Log outcome and notify hook
    telemetry.log_task_outcome(outcome)
    rl.on_task_outcome(outcome)  # Should not raise

    # Check epoch summary
    epoch_summary = telemetry.get_epoch_summary()
    rl.on_epoch_end(epoch_summary)  # Should not raise

    # Verify telemetry aggregation
    task_summary = telemetry.get_outcome_summary()
    assert task_summary["count"] == 1
    assert task_summary["total_stake"] == 1.0
    assert task_summary["total_reward"] == 2.0
