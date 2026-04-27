from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string


DEFAULT_FIXED_EXPIRY_VALIDATION_EPOCHS = 2880
DEFAULT_ACTIVE_EARMARK_CAP_PER_AGENT = 8

# "delivered" is intentionally included: an earmark remains reserved until the
# debit occurs in the epoch AFTER delivery (see process_epoch_boundary).
# This prevents a race where the commissioning agent spends funds that are
# already committed to a pending debit.
RESERVED_STATES = frozenset({"proposed", "accepted", "delivered"})
TERMINAL_STATES = frozenset({"debited", "expired"})
ZERO = Decimal("0")


@dataclass
class EarmarkRecord:
    earmark_id: str
    commission_id: str
    commissioning_agent_id: str
    performing_agent_id: str
    earmark_amount: Decimal
    state: str
    proposal_epoch: int
    expiry_epoch: int
    acceptance_epoch: int | None
    delivery_epoch: int | None
    debit_epoch: int | None
    task_description_hash: str
    contribution_id: str | None

    def to_json(self) -> dict[str, object]:
        payload = asdict(self)
        payload["earmark_amount"] = _decimal_to_string(self.earmark_amount)
        return payload


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
        self._accrued_ecu: dict[str, Decimal] = {}
        self._earmarks: dict[str, EarmarkRecord] = {}

    def set_accrued_ecu(self, agent_id: str, amount: int | float | str | Decimal) -> None:
        try:
            normalized_amount = _to_decimal(amount)
        except ValueError as exc:
            if str(exc) == "non_finite_amount":
                raise ValueError("accrued_ecu_cannot_be_non_finite") from exc
            raise
        if normalized_amount < ZERO:
            raise ValueError("accrued_ecu_cannot_be_negative")
        if normalized_amount < self._reserved_earmark_total(agent_id):
            raise ValueError("accrued_ecu_cannot_drop_below_reserved_earmarks")
        self._accrued_ecu[agent_id] = normalized_amount

    def get_accrued_ecu(self, agent_id: str) -> str:
        return _decimal_to_string(self._accrued_ecu.get(agent_id, ZERO))

    def spendable_ecu(self, agent_id: str) -> str:
        return _decimal_to_string(self._spendable_ecu_decimal(agent_id))

    def earmark_propose(
        self,
        *,
        earmark_id: str,
        commission_id: str,
        commissioning_agent_id: str,
        performing_agent_id: str,
        earmark_amount: int | float | str | Decimal,
        proposal_epoch: int,
        task_description_hash: str,
    ) -> dict[str, object]:
        if earmark_id in self._earmarks:
            return self._failure("earmark_id_conflict", earmark_id=earmark_id)
        try:
            earmark_amount_decimal = _to_decimal(earmark_amount)
        except ValueError as exc:
            if str(exc) == "non_finite_amount":
                return self._failure(
                    "invalid_earmark_amount_non_finite",
                    earmark_amount=earmark_amount,
                )
            return self._failure("invalid_earmark_amount", earmark_amount=earmark_amount)
        if earmark_amount_decimal <= ZERO:
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
        spendable_ecu_decimal = self._spendable_ecu_decimal(commissioning_agent_id)
        if spendable_ecu_decimal < earmark_amount_decimal:
            return self._failure(
                "oversubscribed_earmark_blocked",
                spendable_ecu=_decimal_to_string(spendable_ecu_decimal),
                earmark_amount=_decimal_to_string(earmark_amount_decimal),
            )

        record = EarmarkRecord(
            earmark_id=earmark_id,
            commission_id=commission_id,
            commissioning_agent_id=commissioning_agent_id,
            performing_agent_id=performing_agent_id,
            earmark_amount=earmark_amount_decimal,
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
        if int(acceptance_epoch) > record.expiry_epoch:
            return self._failure(
                "earmark_past_expiry",
                earmark_id=earmark_id,
                expiry_epoch=record.expiry_epoch,
                attempted_epoch=int(acceptance_epoch),
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
        if int(delivery_epoch) > record.expiry_epoch:
            return self._failure(
                "earmark_past_expiry",
                earmark_id=earmark_id,
                expiry_epoch=record.expiry_epoch,
                attempted_epoch=int(delivery_epoch),
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
                # Debit fires the epoch AFTER delivery (strict > check).
                # This gives the delivery epoch time to settle before funds move.
                if record.delivery_epoch is not None and int(commit_epoch) > record.delivery_epoch:
                    commissioning_balance = self._accrued_ecu.get(
                        record.commissioning_agent_id,
                        ZERO,
                    )
                    if commissioning_balance < record.earmark_amount:
                        raise ValueError(
                            f"earmark_debit_would_underflow_balance: "
                            f"earmark_id={record.earmark_id} "
                            f"balance={commissioning_balance} "
                            f"earmark_amount={record.earmark_amount}; "
                            f"invariant violated — accrued balance must cover all "
                            f"reserved earmarks at all times"
                        )
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

    def _reserved_earmark_total(self, agent_id: str) -> Decimal:
        return sum(
            (
                record.earmark_amount
                for record in self._earmarks.values()
                if record.commissioning_agent_id == agent_id
                and record.state in RESERVED_STATES
            ),
            ZERO,
        )

    def _spendable_ecu_decimal(self, agent_id: str) -> Decimal:
        return self._accrued_ecu.get(agent_id, ZERO) - self._reserved_earmark_total(agent_id)

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


def _str_to_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid_decimal_string") from exc


def _to_decimal(value: int | float | str | Decimal) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean_not_valid_amount")
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, float):
        number = Decimal(str(value))
    elif isinstance(value, str):
        number = _str_to_decimal(value)
    else:
        raise ValueError("unsupported_amount_type")

    if not number.is_finite():
        raise ValueError("non_finite_amount")
    return number


def _decimal_to_string(value: Decimal) -> str:
    return decimal_to_canonical_string(value)
