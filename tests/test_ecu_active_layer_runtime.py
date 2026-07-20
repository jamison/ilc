from __future__ import annotations

import pytest

from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime


def test_oversubscription_blocked() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "5.0")
    result = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="6.0",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert result["ok"] is False
    assert result["token"] == "oversubscribed_earmark_blocked"


def test_delivered_earmark_remains_reserved_until_debited() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "10.0")
    runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="3.0",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    runtime.earmark_accept(earmark_id="e-1", performing_agent_id="agent-b", acceptance_epoch=11)
    runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        contribution_id="contrib-1",
        delivery_epoch=12,
    )
    assert runtime.earmark_status(earmark_id="e-1")["data"]["state"] == "delivered"
    assert runtime.spendable_ecu("agent-a") == "7"


def test_debit_occurs_only_at_commit_boundary() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "10.0")
    runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="4.0",
        proposal_epoch=20,
        task_description_hash="hash-1",
    )
    runtime.earmark_accept(earmark_id="e-1", performing_agent_id="agent-b", acceptance_epoch=21)
    runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        contribution_id="contrib-1",
        delivery_epoch=22,
    )
    runtime.process_epoch_boundary(commit_epoch=22)
    assert runtime.earmark_status(earmark_id="e-1")["data"]["state"] == "delivered"
    assert runtime.get_accrued_ecu("agent-a") == "10"
    runtime.process_epoch_boundary(commit_epoch=23)
    assert runtime.earmark_status(earmark_id="e-1")["data"]["state"] == "debited"
    assert runtime.get_accrued_ecu("agent-a") == "6"


def test_expiry_releases_reserves() -> None:
    runtime = EcuActiveLayerRuntime(fixed_expiry_validation_epochs=5)
    runtime.set_accrued_ecu("agent-a", "10.0")
    runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="4.0",
        proposal_epoch=30,
        task_description_hash="hash-1",
    )
    assert runtime.spendable_ecu("agent-a") == "6"
    runtime.process_epoch_boundary(commit_epoch=35)
    assert runtime.earmark_status(earmark_id="e-1")["data"]["state"] == "expired"
    assert runtime.spendable_ecu("agent-a") == "10"


def test_active_earmark_cap_enforced() -> None:
    runtime = EcuActiveLayerRuntime(active_earmark_cap_per_agent=2)
    runtime.set_accrued_ecu("agent-a", "10.0")
    for earmark_id in ("e-1", "e-2"):
        result = runtime.earmark_propose(
            earmark_id=earmark_id,
            commission_id=f"c-{earmark_id}",
            commissioning_agent_id="agent-a",
            performing_agent_id=f"agent-{earmark_id}",
            earmark_amount="1.0",
            proposal_epoch=10,
            task_description_hash=f"hash-{earmark_id}",
        )
        assert result["ok"] is True
    blocked = runtime.earmark_propose(
        earmark_id="e-3",
        commission_id="c-3",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-c",
        earmark_amount="1.0",
        proposal_epoch=10,
        task_description_hash="hash-3",
    )
    assert blocked["ok"] is False
    assert blocked["token"] == "active_earmark_cap_exceeded"


def test_only_named_performing_agent_can_accept_or_deliver() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "10.0")
    proposed = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="2.0",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert proposed["ok"] is True

    wrong_accept = runtime.earmark_accept(
        earmark_id="e-1",
        performing_agent_id="agent-c",
        acceptance_epoch=11,
    )
    assert wrong_accept["ok"] is False
    assert wrong_accept["token"] == "performing_agent_mismatch"

    accepted = runtime.earmark_accept(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        acceptance_epoch=11,
    )
    assert accepted["ok"] is True

    wrong_deliver = runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-c",
        contribution_id="contrib-1",
        delivery_epoch=12,
    )
    assert wrong_deliver["ok"] is False
    assert wrong_deliver["token"] == "performing_agent_mismatch"

    delivered = runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        contribution_id="contrib-1",
        delivery_epoch=12,
    )
    assert delivered["ok"] is True


def test_accept_and_deliver_reject_epochs_past_expiry() -> None:
    # LOW-007 fix: earmark_accept and earmark_deliver use >= for expiry check,
    # consistent with process_epoch_boundary. expiry_epoch = proposal_epoch + 5 = 15.
    # The last valid acceptance/delivery epoch is 14; epoch 15 is the expiry epoch itself.
    runtime = EcuActiveLayerRuntime(fixed_expiry_validation_epochs=5)
    runtime.set_accrued_ecu("agent-a", "10.0")
    proposed = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="2.0",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert proposed["ok"] is True

    # Accept at expiry epoch (15) is now rejected — consistent with process_epoch_boundary.
    at_expiry_accept = runtime.earmark_accept(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        acceptance_epoch=15,
    )
    assert at_expiry_accept["ok"] is False
    assert at_expiry_accept["token"] == "earmark_past_expiry"

    # Accept past expiry also rejected.
    late_accept = runtime.earmark_accept(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        acceptance_epoch=16,
    )
    assert late_accept["ok"] is False
    assert late_accept["token"] == "earmark_past_expiry"

    # Accept before expiry epoch succeeds.
    accepted = runtime.earmark_accept(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        acceptance_epoch=14,
    )
    assert accepted["ok"] is True

    # Deliver at expiry epoch (15) is also rejected.
    at_expiry_deliver = runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        contribution_id="contrib-1",
        delivery_epoch=15,
    )
    assert at_expiry_deliver["ok"] is False
    assert at_expiry_deliver["token"] == "earmark_past_expiry"

    # Deliver past expiry is also rejected.
    late_deliver = runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        contribution_id="contrib-1",
        delivery_epoch=16,
    )
    assert late_deliver["ok"] is False
    assert late_deliver["token"] == "earmark_past_expiry"


def test_set_accrued_ecu_rejects_drop_below_reserved_balance() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "10.0")
    proposed = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="3.0",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert proposed["ok"] is True

    with pytest.raises(ValueError, match="accrued_ecu_cannot_drop_below_reserved_earmarks"):
        runtime.set_accrued_ecu("agent-a", "2.0")


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_string_amounts_are_rejected(value: object) -> None:
    runtime = EcuActiveLayerRuntime()

    with pytest.raises(ValueError, match="accrued_ecu_cannot_be_non_finite"):
        runtime.set_accrued_ecu("agent-a", value)  # type: ignore[arg-type]

    result = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount=value,  # type: ignore[arg-type]
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert result["ok"] is False
    assert result["token"] == "invalid_earmark_amount_non_finite"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_float_amounts_are_rejected_before_non_finite_classification(value: object) -> None:
    runtime = EcuActiveLayerRuntime()

    with pytest.raises(ValueError, match="accrued_ecu_float_input_rejected"):
        runtime.set_accrued_ecu("agent-a", value)  # type: ignore[arg-type]

    result = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount=value,  # type: ignore[arg-type]
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert result["ok"] is False
    assert result["token"] == "invalid_earmark_amount_float"


def test_multiple_delivered_earmarks_debit_in_same_epoch_boundary() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "10.0")
    for earmark_id, amount, performer in (("e-1", "2.0", "agent-b"), ("e-2", "3.0", "agent-c")):
        proposed = runtime.earmark_propose(
            earmark_id=earmark_id,
            commission_id=f"c-{earmark_id}",
            commissioning_agent_id="agent-a",
            performing_agent_id=performer,
            earmark_amount=amount,
            proposal_epoch=10,
            task_description_hash=f"hash-{earmark_id}",
        )
        assert proposed["ok"] is True
        accepted = runtime.earmark_accept(
            earmark_id=earmark_id,
            performing_agent_id=performer,
            acceptance_epoch=11,
        )
        assert accepted["ok"] is True
        delivered = runtime.earmark_deliver(
            earmark_id=earmark_id,
            performing_agent_id=performer,
            contribution_id=f"contrib-{earmark_id}",
            delivery_epoch=12,
        )
        assert delivered["ok"] is True

    result = runtime.process_epoch_boundary(commit_epoch=13)
    assert result["ok"] is True
    assert set(result["data"]["debited_earmark_ids"]) == {"e-1", "e-2"}
    assert runtime.get_accrued_ecu("agent-a") == "5"


def test_earmark_history_returns_records_for_both_agents() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "10.0")
    proposed = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="2.5",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert proposed["ok"] is True

    history_a = runtime.earmark_history("agent-a")
    assert history_a["ok"] is True
    assert history_a["token"] == "earmark_history_returned"
    assert history_a["data"]["agent_id"] == "agent-a"
    assert len(history_a["data"]["history"]) == 1
    assert history_a["data"]["history"][0]["earmark_id"] == "e-1"

    history_b = runtime.earmark_history("agent-b")
    assert history_b["ok"] is True
    assert history_b["token"] == "earmark_history_returned"
    assert history_b["data"]["agent_id"] == "agent-b"
    assert len(history_b["data"]["history"]) == 1
    assert history_b["data"]["history"][0]["commissioning_agent_id"] == "agent-a"
    assert history_b["data"]["history"][0]["performing_agent_id"] == "agent-b"


def test_runtime_has_no_ilc_or_wallet_widening_surface() -> None:
    runtime = EcuActiveLayerRuntime()
    assert not hasattr(runtime, "wallet_status")
    assert not hasattr(runtime, "transfer_ilc")
    assert not hasattr(runtime, "withdraw_ilc")
