"""
Outcome logging primitives for the ILC economics sandbox.

TaskOutcome and OutcomeLogger provide a lightweight way to record what happened
to each simulated task (stake_spent, reward_paid, success, domain, etc.) and to
aggregate simple statistics for analysis or RL-style agents.

For how this is used in the economics sandbox and how it might map to future
genesis primitives, see docs/protocol_econ_surfaces_mvp.md.
"""
from dataclasses import dataclass

@dataclass
class TaskOutcome:
    """
    Compact record of a single task's economic outcome in the sandbox.

    This does not attempt to encode full protocol semantics; instead it captures
    just enough information for telemetry, analysis, and future RL agents:
    task_type, domain, stake_spent, reward_paid, and success flag.
    """
    task_type: str           # e.g. "claim.submit"
    domain: str | None       # e.g. "easy", "medium", "hard", or None
    stake_spent: float
    reward_paid: float
    success: bool | None     # None if not applicable


class OutcomeLogger:
    """
    Minimal logger that accumulates TaskOutcome records in memory.

    The logger is used by simulations to track aggregate statistics such as total
    stake_spent, total reward_paid, counts per domain, and simple averages. It is
    intentionally simple and non-persistent; production deployments would use a
    more robust telemetry and storage layer.
    """
    def __init__(self) -> None:
        self.outcomes: list[TaskOutcome] = []

    def log(self, outcome: TaskOutcome) -> None:
        self.outcomes.append(outcome)

    def summary(self) -> dict:
        # Very simple: sum rewards and stakes for now.
        total_stake = sum(o.stake_spent for o in self.outcomes)
        total_reward = sum(o.reward_paid for o in self.outcomes)
        return {
            "count": len(self.outcomes),
            "total_stake": total_stake,
            "total_reward": total_reward,
        }
