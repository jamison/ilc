import pytest
from ilc_core.economics.outcome import OutcomeLogger, TaskOutcome

def test_outcome_logger_basic():
    logger = OutcomeLogger()
    
    # Log a successful task
    logger.log(TaskOutcome(
        task_type="claim.submit",
        domain="medium",
        stake_spent=2.0,
        reward_paid=3.0,
        success=True,
    ))
    
    # Log a failed task
    logger.log(TaskOutcome(
        task_type="claim.submit",
        domain="hard",
        stake_spent=1.0,
        reward_paid=0.5,
        success=False,
    ))

    summary = logger.summary()
    
    assert summary["count"] == 2
    assert summary["total_stake"] == 3.0
    assert summary["total_reward"] == 3.5
