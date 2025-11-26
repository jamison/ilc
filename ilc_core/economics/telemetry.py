from .epoch_ledger import SimpleEpochLedger
from .outcome import OutcomeLogger, TaskOutcome

class EconomicTelemetry:
    """
    Simple façade over epoch-level and task-level economic data.

    This is sim-only for now, and provides a stable surface for:
    - analytics
    - future RL agents
    - monitoring / dashboards
    """

    def __init__(self) -> None:
        self.ledger = SimpleEpochLedger()
        self.outcomes = OutcomeLogger()

    def log_task_outcome(self, outcome: TaskOutcome) -> None:
        self.outcomes.log(outcome)
        # NOTE: We do NOT mutate ledger here; caller still decides
        # how to aggregate ECU spent / rewards per epoch.

    def get_epoch_summary(self) -> dict:
        agg = self.ledger.total_aggregate()
        return {
            "tasks": agg.tasks,
            "ecu_spent": agg.ecu_spent,
            "rewards_paid": agg.rewards_paid,
        }

    def get_outcome_summary(self) -> dict:
        return self.outcomes.summary()

    def snapshot(self) -> dict:
        """
        Combined view, useful for debugging and future RL.
        """
        return {
            "epoch": self.get_epoch_summary(),
            "tasks": self.get_outcome_summary(),
        }


class RLHook:
    """
    Minimal RL hook interface (sim-only).

    This does NOT change consensus or L1 semantics.
    It only observes task outcomes and epoch summaries.
    """

    def on_task_outcome(self, outcome: TaskOutcome) -> None:
        """
        Called whenever a task outcome is logged.
        Default implementation: no-op.
        """
        pass

    def on_epoch_end(self, epoch_summary: dict) -> None:
        """
        Called at the end of an epoch (or sim step) with aggregated data.
        Default implementation: no-op.
        """
        pass
