# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Economic telemetry façade and RL hook stubs for the ILC economics sandbox.

EconomicTelemetry wraps the epoch reward ledger and OutcomeLogger to provide a
unified view of simulated economic activity. RLHook defines a minimal observer
interface that future RL agents can implement to receive per-task and per-epoch
signals without being wired into the core protocol.

For how this is used in the economics sandbox and how it might map to future
genesis primitives, see docs/protocol_econ_surfaces_mvp.md.
"""
from .epoch_ledger import SimpleEpochLedger
from .outcome import OutcomeLogger, TaskOutcome

class EconomicTelemetry:
    """
    Façade over the epoch reward ledger and outcome logging for simulations.

    EconomicTelemetry is responsible for:
      * Recording per-task TaskOutcome events.
      * Updating a SimpleEpochLedger with aggregated ECU_spent and rewards.
      * Providing snapshots for analysis and future RL agents.
    It is currently only used in sandbox simulations and is not a mandatory part
    of the on-chain protocol design.
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
    Minimal stub interface for RL-style agents observing economic activity.

    Implementations can override on_task_outcome(...) and on_epoch_summary(...)
    to ingest telemetry from EconomicTelemetry. The default implementation is a
    no-op so that simulations can wire it in without changing behavior.
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
