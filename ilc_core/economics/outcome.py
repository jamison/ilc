from dataclasses import dataclass

@dataclass
class TaskOutcome:
    task_type: str           # e.g. "claim.submit"
    domain: str | None       # e.g. "easy", "medium", "hard", or None
    stake_spent: float
    reward_paid: float
    success: bool | None     # None if not applicable


class OutcomeLogger:
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
