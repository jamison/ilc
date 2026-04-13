from __future__ import annotations

from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime


def test_decimal_boundary_allows_exact_reservation_of_point_three() -> None:
    runtime = EcuActiveLayerRuntime(active_earmark_cap_per_agent=4)
    runtime.set_accrued_ecu("agent-a", "0.3")

    first = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="0.1",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert first["ok"] is True

    second = runtime.earmark_propose(
        earmark_id="e-2",
        commission_id="c-2",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-c",
        earmark_amount="0.2",
        proposal_epoch=10,
        task_description_hash="hash-2",
    )
    assert second["ok"] is True
    assert runtime.spendable_ecu("agent-a") == 0.0


def test_repeated_small_debits_drain_balance_to_exact_zero() -> None:
    runtime = EcuActiveLayerRuntime(active_earmark_cap_per_agent=20)
    runtime.set_accrued_ecu("agent-a", "1.0")

    for idx in range(10):
        earmark_id = f"e-{idx}"
        performer = f"agent-{idx}"
        proposed = runtime.earmark_propose(
            earmark_id=earmark_id,
            commission_id=f"c-{idx}",
            commissioning_agent_id="agent-a",
            performing_agent_id=performer,
            earmark_amount="0.1",
            proposal_epoch=10,
            task_description_hash=f"hash-{idx}",
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
            contribution_id=f"contrib-{idx}",
            delivery_epoch=12,
        )
        assert delivered["ok"] is True

    processed = runtime.process_epoch_boundary(commit_epoch=13)
    assert processed["ok"] is True
    assert len(processed["data"]["debited_earmark_ids"]) == 10
    assert runtime.get_accrued_ecu("agent-a") == 0.0


def test_idempotent_epoch_processing_for_terminal_earmarks() -> None:
    runtime = EcuActiveLayerRuntime(fixed_expiry_validation_epochs=5)
    runtime.set_accrued_ecu("agent-a", "1.0")

    active = runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="0.4",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )
    assert active["ok"] is True
    assert runtime.earmark_accept(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        acceptance_epoch=11,
    )["ok"] is True
    assert runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        contribution_id="contrib-1",
        delivery_epoch=12,
    )["ok"] is True

    expiring = runtime.earmark_propose(
        earmark_id="e-2",
        commission_id="c-2",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-c",
        earmark_amount="0.1",
        proposal_epoch=10,
        task_description_hash="hash-2",
    )
    assert expiring["ok"] is True

    first = runtime.process_epoch_boundary(commit_epoch=15)
    assert set(first["data"]["debited_earmark_ids"]) == {"e-1"}
    assert set(first["data"]["expired_earmark_ids"]) == {"e-2"}

    balance_after_first = runtime.get_accrued_ecu("agent-a")
    second = runtime.process_epoch_boundary(commit_epoch=16)
    assert second["data"]["debited_earmark_ids"] == []
    assert second["data"]["expired_earmark_ids"] == []
    assert runtime.get_accrued_ecu("agent-a") == balance_after_first


def test_delivery_cannot_bypass_expiry_before_boundary_processing() -> None:
    runtime = EcuActiveLayerRuntime(fixed_expiry_validation_epochs=5)
    runtime.set_accrued_ecu("agent-a", "1.0")
    assert runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="0.4",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )["ok"] is True
    assert runtime.earmark_accept(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        acceptance_epoch=11,
    )["ok"] is True

    late_delivery = runtime.earmark_deliver(
        earmark_id="e-1",
        performing_agent_id="agent-b",
        contribution_id="contrib-1",
        delivery_epoch=16,
    )
    assert late_delivery["ok"] is False
    assert late_delivery["token"] == "earmark_past_expiry"

    processed = runtime.process_epoch_boundary(commit_epoch=16)
    assert processed["ok"] is True
    assert processed["data"]["debited_earmark_ids"] == []
    assert processed["data"]["expired_earmark_ids"] == ["e-1"]
    assert runtime.earmark_status(earmark_id="e-1")["data"]["state"] == "expired"


def test_status_and_history_outputs_are_stable_for_decimal_amounts() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent-a", "0.5")
    assert runtime.earmark_propose(
        earmark_id="e-1",
        commission_id="c-1",
        commissioning_agent_id="agent-a",
        performing_agent_id="agent-b",
        earmark_amount="0.1",
        proposal_epoch=10,
        task_description_hash="hash-1",
    )["ok"] is True

    status = runtime.earmark_status(earmark_id="e-1")
    history = runtime.earmark_history("agent-a")

    assert status["ok"] is True
    assert history["ok"] is True
    assert status["data"]["earmark_amount"] == "0.1"
    assert history["data"]["history"][0]["earmark_amount"] == "0.1"


def test_runtime_still_has_no_wallet_or_ilc_transfer_surface() -> None:
    runtime = EcuActiveLayerRuntime()
    assert not hasattr(runtime, "wallet_status")
    assert not hasattr(runtime, "transfer_ilc")
    assert not hasattr(runtime, "withdraw_ilc")
