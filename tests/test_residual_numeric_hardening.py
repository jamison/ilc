from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.exceptions import EventLogValidationError, LedgerExportContractError
from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
from ilc_core.ledger.canon_export_format import export_canon_format_v0_1
from ilc_core.ledger.canon_export_validate import validate_canon_export_v0_1
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.settlement_metrics import compute_settlement_metrics
from ilc_core.protocol.event_log import make_epoch_summary_event, make_task_outcome_event
from ilc_core.protocol.mapper import epoch_summary_to_protocol
from ilc_core.types import ClaimRecord, Node


def test_shared_contract_exact_numeric_stability_and_non_finite_rejection() -> None:
    node = Node(
        id="node:test",
        type="claim",
        content="x",
        agent_id="agent:test",
        signature="sig",
        net_stake="10.5000",
    )
    claim = ClaimRecord(
        id="claim:test",
        type="claim",
        agent_id="agent:test",
        content="x",
        signature="sig",
        net_stake=Decimal("2.25"),
    )
    assert node.model_dump(mode="json")["net_stake"] == "10.5"
    assert claim.model_dump(mode="json")["net_stake"] == "2.25"

    with pytest.raises(ValueError, match="invalid_net_stake"):
        ClaimRecord(
            id="claim:float",
            type="claim",
            agent_id="agent:test",
            content="x",
            signature="sig",
            net_stake=2.25,
        )

    try:
        Node(
            id="bad",
            type="claim",
            content="x",
            agent_id="agent:test",
            signature="sig",
            net_stake="Infinity",
        )
    except ValueError as exc:
        assert "invalid_net_stake" in str(exc)
    else:
        raise AssertionError("non_finite_net_stake_not_rejected")


def test_protocol_mapping_exact_numeric_stability_uses_string_defaults() -> None:
    summary = epoch_summary_to_protocol(7, {"total_tasks": 3})
    assert summary["total_ecu_spent"] == "0"
    assert summary["total_reward_paid"] == "0"
    assert summary["clearing_price_ilc_per_ecu"] == "0"

    populated = epoch_summary_to_protocol(
        8,
        {
            "total_tasks": 1,
            "total_ecu_spent": Decimal("1.25"),
            "total_reward_paid": "2.5",
            "clearing_price_ilc_per_ecu": Decimal("0.3333"),
        },
    )
    assert populated["total_ecu_spent"] == "1.25"
    assert populated["total_reward_paid"] == "2.5"
    assert populated["clearing_price_ilc_per_ecu"] == "0.3333"


def test_runtime_adjacent_boundaries_reject_non_finite_and_emit_canonical_strings() -> None:
    task_event = make_task_outcome_event(
        agent_id="agent:test",
        epoch_index=1,
        namespace_id="ns",
        task_type="reasoning",
        reward=2.5,
        success=True,
    )
    epoch_event = make_epoch_summary_event(epoch_index=1, total_tasks=1, total_reward=3.75)
    assert task_event.payload["reward"] == "2.5"
    assert epoch_event.payload["total_reward"] == "3.75"

    for value in ("Infinity", "NaN"):
        try:
            make_task_outcome_event(
                agent_id="agent:test",
                epoch_index=1,
                namespace_id="ns",
                task_type="reasoning",
                reward=value,
                success=True,
            )
        except EventLogValidationError:
            pass
        else:
            raise AssertionError("event_log_non_finite_not_rejected")

    ledger = InMemoryLedgerBackend()
    ledger.epoch_records["epoch-1"] = {
        "epoch_id": "epoch-1",
        "epoch_index": 1,
        "namespace_id": "ns",
        "created_at": "2026-01-01T00:00:00+00:00",
        "finalization_state": "committed",
        "summary": {"reward_total": "4.5", "task_count": 1, "agent_count": 1, "stake_total": "2"},
        "checksums": {"epoch_events_cid": "cid:1", "epoch_state_cid": "cid:2"},
        "status": "settled",
        "distribution_status": "distributed",
    }
    metrics = compute_settlement_metrics(ledger)
    assert metrics["total_rewards_distributed"] == "4.5"

    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu("agent:a", "10.5")
    assert runtime.get_accrued_ecu("agent:a") == "10.5"
    assert runtime.spendable_ecu("agent:a") == "10.5"
    try:
        runtime.set_accrued_ecu("agent:a", "Infinity")
    except ValueError as exc:
        assert "accrued_ecu_cannot_be_non_finite" in str(exc)
    else:
        raise AssertionError("active_layer_non_finite_not_rejected")


def test_canon_export_companion_layer_coherence_rejects_non_finite_values(tmp_path) -> None:
    export_payload = export_canon_format_v0_1(
        {
            "canon_hash": "hash:1",
            "canon_export_version": "v0.1",
            "epochs": [{"epoch_id": "e1"}],
            "snapshots": [{"epoch_id": "e1", "balances": {"alice": Decimal("1.25")}}],
            "balances": {"alice": Decimal("1.25")},
        },
        exported_at="2026-02-05T00:00:00+00:00",
    )
    assert export_payload["snapshots"][0]["balances"]["alice"] == "1.25"

    with pytest.raises(ValueError, match="invalid_numeric_scalar_in_canon_export"):
        export_canon_format_v0_1(
            {
                "canon_hash": "hash:1",
                "canon_export_version": "v0.1",
                "epochs": [{"epoch_id": "e1"}],
                "snapshots": [{"epoch_id": "e1", "balances": {"alice": 1.25}}],
                "balances": {"alice": Decimal("1.25")},
            },
            exported_at="2026-02-05T00:00:00+00:00",
        )

    validation = validate_canon_export_v0_1(
        {
            "canon_export_format": "v0.1",
            "canon_hash": "h",
            "exported_at": "2026-02-05T00:00:00Z",
            "meta": {
                "canon_export_version": "v",
                "epoch_count": 0,
                "snapshot_count": 1,
                "balance_count": 1,
            },
            "epochs": [],
            "snapshots": [{"epoch_id": "e1", "balances": {"alice": "Infinity"}}],
        }
    )
    assert validation["ok"] is False

    try:
        write_canon_export_bundle(
            {"canon_hash": "h1", "canon_export_format": "v0.1", "bad": float("inf")},
            {"ok": True},
            tmp_path / "bundle",
        )
    except LedgerExportContractError as exc:
        assert "non_finite_numeric_scalar_in_bundle_payload" in str(exc)
    else:
        raise AssertionError("bundle_writer_non_finite_not_rejected")
