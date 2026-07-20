from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.exact_numeric import parse_non_negative_decimal, to_decimal
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import make_commit_epoch_event


MIGRATED_TIER0_FILES = (
    Path("ilc_core/ledger/backend.py"),
    Path("ilc_core/ledger/settlement_verification.py"),
    Path("ilc_core/rc/economic_cycle_runtime.py"),
)


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity", float("nan"), float("inf"), float("-inf")])
def test_exact_numeric_helper_rejects_non_finite_values(value: object) -> None:
    with pytest.raises(ValueError):
        to_decimal(value)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        parse_non_negative_decimal(value)  # type: ignore[arg-type]


def test_backend_internal_balances_remain_decimal_after_distribution() -> None:
    ledger = InMemoryLedgerBackend()
    snapshot = StakeSnapshot(
        epoch_id="epoch-1",
        epoch_index=1,
        namespace_id="ns",
        stakes={"agent-a": "600", "agent-b": "400"},
        total_stake="1000",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    ledger.put_stake_snapshot(snapshot)

    event = make_commit_epoch_event(
        epoch_index=1,
        epoch_id="epoch-1",
        namespace_id="ns",
        created_at=datetime.now(timezone.utc).isoformat(),
        finalization_state="committed",
        summary={
            "task_count": 1,
            "agent_count": 2,
            "reward_total": "100.0",
            "stake_total": "1000.0",
        },
        checksums={
            "epoch_events_cid": "QmEvents",
            "epoch_state_cid": "QmState",
        },
    )
    ledger.apply_epoch_settlement(event)

    assert isinstance(ledger.balances["agent-a"], Decimal)
    assert isinstance(ledger.balances["agent-b"], Decimal)
    assert ledger.balances["agent-a"] == Decimal("60")
    assert ledger.balances["agent-b"] == Decimal("40")


def test_commit_epoch_event_emits_canonical_decimal_strings() -> None:
    event = make_commit_epoch_event(
        epoch_index=7,
        epoch_id="epoch-7",
        namespace_id="ns",
        created_at=datetime.now(timezone.utc).isoformat(),
        finalization_state="committed",
        summary={
            "task_count": 3,
            "agent_count": 2,
            "reward_total": "001.2300",
            "stake_total": "010.0",
        },
        checksums={
            "epoch_events_cid": "QmEvents",
            "epoch_state_cid": "QmState",
        },
    )

    assert event.payload["summary"]["reward_total"] == "1.23"
    assert event.payload["summary"]["stake_total"] == "10"


def test_migrated_tier0_files_have_no_legacy_tolerance_patterns() -> None:
    for path in MIGRATED_TIER0_FILES:
        text = path.read_text(encoding="utf-8")
        assert "1e-9" not in text
        assert "round(claim_totals.get" not in text
        assert "abs(reward_total - float(rewards_paid))" not in text


@pytest.mark.parametrize("value", ["NaN", "Infinity"])
def test_active_layer_runtime_rejects_non_finite_string_amounts(value: object) -> None:
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


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_active_layer_runtime_rejects_float_amounts(value: object) -> None:
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
