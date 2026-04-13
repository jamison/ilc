from __future__ import annotations

from dataclasses import asdict, dataclass


DEFAULT_FIXED_EXPIRY_VALIDATION_EPOCHS = 2880
DEFAULT_ACTIVE_EARMARK_CAP_PER_AGENT = 8

RESERVED_STATES = frozenset({"proposed", "accepted", "delivered"})
TERMINAL_STATES = frozenset({"debited", "expired"})


@dataclass
class EarmarkRecord:
    earmark_id: str
    commission_id: str
    commissioning_agent_id: str
    performing_agent_id: str
    earmark_amount: float
    state: str
    proposal_epoch: int
    expiry_epoch: int
    acceptance_epoch: int | None
    delivery_epoch: int | None
    debit_epoch: int | None
    task_description_hash: str
    contribution_id: str | None

    def to_json(self) -> dict[str, object]:
        return asdict(self)


class EcuActiveLayerRuntime:
    """Bounded internal ECU active layer for directed commissions."""

    def __init__(
        self,
        *,
        fixed_expiry_validation_epochs: int = DEFAULT_FIXED_EXPIRY_VALIDATION_EPOCHS,
        active_earmark_cap_per_agent: int = DEFAULT_ACTIVE_EARMARK_CAP_PER_AGENT,
    ) -> None:
        if fixed_expiry_validation_epochs <= 0:
            raise ValueError("fixed_expiry_validation_epochs_must_be_positive")
        if active_earmark_cap_per_agent <= 0:
            raise ValueError("active_earmark_cap_per_agent_must_be_positive")

        self.fixed_expiry_validation_epochs = fixed_expiry_validation_epochs
        self.active_earmark_cap_per_agent = active_earmark_cap_per_agent
        self._accrued_ecu: dict[str, float] = {}
        self._earmarks: dict[str, EarmarkRecord] = {}

    def set_accrued_ecu(self, agent_id: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("accrued_ecu_cannot_be_negative")
        if float(amount) < self._reserved_earmark_total(agent_id):
            raise ValueError("accrued_ecu_cannot_drop_below_reserved_earmarks")
        self._accrued_ecu[agent_id] = float(amount)

    def get_accrued_ecu(self, agent_id: str) -> float:
        return self._accrued_ecu.get(agent_id, 0.0)

    def spendable_ecu(self, agent_id: str) -> float:
        return self.get_accrued_ecu(agent_id) - self._reserved_earmark_total(agent_id)

    def earmark_propose(
        self,
        *,
        earmark_id: str,
        commission_id: str,
        commissioning_agent_id: str,
        performing_agent_id: str,
        earmark_amount: float,
        proposal_epoch: int,
        task_description_hash: str,
    ) -> dict[str, object]:
        if earmark_id in self._earmarks:
            return self._failure("earmark_id_conflict", earmark_id=earmark_id)
        if earmark_amount <= 0:
            return self._failure("invalid_earmark_amount", earmark_amount=earmark_amount)
        if commissioning_agent_id == performing_agent_id:
            return self._failure(
                "same_key_self_commission_prohibited",
                commissioning_agent_id=commissioning_agent_id,
            )
        if self._active_earmark_count(commissioning_agent_id) >= self.active_earmark_cap_per_agent:
            return self._failure(
                "active_earmark_cap_exceeded",
                active_earmark_cap_per_agent=self.active_earmark_cap_per_agent,
            )
        if self.spendable_ecu(commissioning_agent_id) < float(earmark_amount):
            return self._failure(
                "oversubscribed_earmark_blocked",
                spendable_ecu=self.spendable_ecu(commissioning_agent_id),
                earmark_amount=float(earmark_amount),
            )

        record = EarmarkRecord(
            earmark_id=earmark_id,
            commission_id=commission_id,
            commissioning_agent_id=commissioning_agent_id,
            performing_agent_id=performing_agent_id,
            earmark_amount=float(earmark_amount),
            state="proposed",
            proposal_epoch=int(proposal_epoch),
            expiry_epoch=int(proposal_epoch) + self.fixed_expiry_validation_epochs,
            acceptance_epoch=None,
            delivery_epoch=None,
            debit_epoch=None,
            task_description_hash=task_description_hash,
            contribution_id=None,
        )
        self._earmarks[earmark_id] = record
        return {
            "ok": True,
            "token": "earmark_proposed",
            "data": record.to_json(),
        }

    def earmark_accept(
        self,
        *,
        earmark_id: str,
        performing_agent_id: str,
        acceptance_epoch: int,
    ) -> dict[str, object]:
        record = self._earmarks.get(earmark_id)
        if record is None:
            return self._failure("earmark_not_found", earmark_id=earmark_id)
        if record.performing_agent_id != performing_agent_id:
            return self._failure(
                "performing_agent_mismatch",
                earmark_id=earmark_id,
                expected_performing_agent_id=record.performing_agent_id,
                performing_agent_id=performing_agent_id,
            )
        if record.state != "proposed":
            return self._failure(
                "invalid_state_transition",
                earmark_id=earmark_id,
                current_state=record.state,
                attempted_state="accepted",
            )
        record.state = "accepted"
        record.acceptance_epoch = int(acceptance_epoch)
        return {
            "ok": True,
            "token": "earmark_acceptance_recorded",
            "data": record.to_json(),
        }

    def earmark_deliver(
        self,
        *,
        earmark_id: str,
        performing_agent_id: str,
        contribution_id: str,
        delivery_epoch: int,
    ) -> dict[str, object]:
        record = self._earmarks.get(earmark_id)
        if record is None:
            return self._failure("earmark_not_found", earmark_id=earmark_id)
        if record.performing_agent_id != performing_agent_id:
            return self._failure(
                "performing_agent_mismatch",
                earmark_id=earmark_id,
                expected_performing_agent_id=record.performing_agent_id,
                performing_agent_id=performing_agent_id,
            )
        if record.state != "accepted":
            return self._failure(
                "invalid_state_transition",
                earmark_id=earmark_id,
                current_state=record.state,
                attempted_state="delivered",
            )
        record.state = "delivered"
        record.delivery_epoch = int(delivery_epoch)
        record.contribution_id = contribution_id
        return {
            "ok": True,
            "token": "earmark_delivery_recorded",
            "data": record.to_json(),
        }

    def process_epoch_boundary(self, *, commit_epoch: int) -> dict[str, object]:
        debited: list[str] = []
        expired: list[str] = []
        for record in self._earmarks.values():
            if record.state in TERMINAL_STATES:
                continue
            if record.state == "delivered":
                if record.delivery_epoch is not None and int(commit_epoch) > record.delivery_epoch:
                    commissioning_balance = self.get_accrued_ecu(record.commissioning_agent_id)
                    self._accrued_ecu[record.commissioning_agent_id] = (
                        commissioning_balance - record.earmark_amount
                    )
                    record.state = "debited"
                    record.debit_epoch = int(commit_epoch)
                    debited.append(record.earmark_id)
                continue
            if record.state in {"proposed", "accepted"} and int(commit_epoch) >= record.expiry_epoch:
                record.state = "expired"
                expired.append(record.earmark_id)
        return {
            "ok": True,
            "token": "epoch_boundary_processed",
            "data": {
                "commit_epoch": int(commit_epoch),
                "debited_earmark_ids": debited,
                "expired_earmark_ids": expired,
            },
        }

    def earmark_status(self, *, earmark_id: str) -> dict[str, object]:
        record = self._earmarks.get(earmark_id)
        if record is None:
            return self._failure("earmark_not_found", earmark_id=earmark_id)
        return {
            "ok": True,
            "token": "earmark_status_found",
            "data": record.to_json(),
        }

    def earmark_history(self, agent_id: str) -> dict[str, object]:
        records = [
            record.to_json()
            for record in sorted(
                self._earmarks.values(),
                key=lambda item: (item.proposal_epoch, item.earmark_id),
            )
            if item_involves_agent(record=record, agent_id=agent_id)
        ]
        return {
            "ok": True,
            "token": "earmark_history_returned",
            "data": {
                "agent_id": agent_id,
                "history": records,
            },
        }

    def _active_earmark_count(self, agent_id: str) -> int:
        return sum(
            1
            for record in self._earmarks.values()
            if record.commissioning_agent_id == agent_id and record.state in RESERVED_STATES
        )

    def _reserved_earmark_total(self, agent_id: str) -> float:
        return sum(
            record.earmark_amount
            for record in self._earmarks.values()
            if record.commissioning_agent_id == agent_id and record.state in RESERVED_STATES
        )

    def _failure(self, token: str, **data: object) -> dict[str, object]:
        return {
            "ok": False,
            "token": token,
            "data": data,
        }


def item_involves_agent(*, record: EarmarkRecord, agent_id: str) -> bool:
    return (
        record.commissioning_agent_id == agent_id
        or record.performing_agent_id == agent_id
    )
