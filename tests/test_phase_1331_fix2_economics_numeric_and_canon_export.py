from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

import ilc_core.ledger.canon_export as canon_export
from ilc_core.economics.entropy import entropy_weight, learning_signal
from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    evaluate_ejected_stake_vote,
)
from ilc_core.economics.epoch_ledger import SimpleEpochLedger
from ilc_core.economics.reward import simple_claim_reward
from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.exact_numeric import to_decimal
from ilc_core.ledger.settlement_verification import verify_stake_distribution
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import ProtocolEvent
from ilc_core.types import EdgeType, EpochAttributionBatch


ROOT = Path(__file__).resolve().parents[1]
SPEC_DOC = ROOT / "docs/specs/ilc_phase_1331_fix2_economics_numeric_canon_export_v0.1.md"
WALKTHROUGH_DOC = (
    ROOT / "docs/phases/phase_1331_fix2_economics_numeric_canon_export_walkthrough.md"
)
STATUS_DOC = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"

REQUIRED_TOKENS = (
    "phase_1331_fix2_economics_numeric_canon_export.v0.1",
    "economics_entropy_decimal_only_phase_1331_fix2",
    "epoch_ledger_clearing_price_decimal_phase_1331_fix2",
    "exact_numeric_float_boundary_rejected_phase_1331_fix2",
    "proportional_payout_round_down_residual_phase_1331_fix2",
    "settlement_verification_quantum_aligned_phase_1331_fix2",
    "canon_export_atomic_write_phase_1331_fix2",
    "phase_1332_final_deterministic_code_security_audit_still_next_after_fix2",
    "public_rc_remains_blocked_after_phase_1331_fix2",
)


def _commit_event(epoch_id: str, reward_total: str) -> ProtocolEvent:
    return ProtocolEvent(
        kind="commit.epoch",
        payload={
            "event_kind": "commit.epoch",
            "epoch_index": 1,
            "epoch_id": epoch_id,
            "namespace_id": "test_ns",
            "created_at": "2026-05-14T00:00:00Z",
            "finalization_state": "committed",
            "summary": {
                "reward_total": reward_total,
                "stake_total": "3",
                "task_count": 1,
                "agent_count": 3,
            },
            "checksums": {
                "epoch_events_cid": "cid-events",
                "epoch_state_cid": "cid-state",
            },
        },
        received_at="2026-05-14T00:00:00Z",
        source="test",
    )


def test_entropy_reward_and_clearing_price_are_decimal_only() -> None:
    assert learning_signal(Decimal("0.5")) == Decimal("0.25")
    assert entropy_weight(Decimal("0.5")) == Decimal("2.0")
    assert simple_claim_reward(
        Decimal("10"),
        Decimal("0.5"),
        success_rate=Decimal("0.5"),
    ) == Decimal("25.000")

    ledger = SimpleEpochLedger()
    ledger.record_task(epoch=1, ecu_spent=Decimal("1.5"), reward=Decimal("2.25"))
    price = ledger.clearing_price()
    assert price == Decimal("1.5")
    assert isinstance(price, Decimal)


@pytest.mark.parametrize("value", [0.0, 0.1, 1.0, float("nan"), float("inf")])
def test_exact_numeric_and_entropy_reject_float_boundary(value: float) -> None:
    with pytest.raises(ValueError):
        to_decimal(value)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        learning_signal(value)


def test_backend_distribution_rounds_down_and_assigns_residual_to_last_agent() -> None:
    ledger = InMemoryLedgerBackend()
    snapshot = StakeSnapshot(
        epoch_id="epoch-residual",
        epoch_index=1,
        namespace_id="test_ns",
        stakes={
            "agent-a": Decimal("1"),
            "agent-b": Decimal("1"),
            "agent-c": Decimal("1"),
        },
        total_stake=Decimal("3"),
        created_at="2026-05-14T00:00:00Z",
    )
    ledger.put_stake_snapshot(snapshot)
    ledger.apply_epoch_settlement(_commit_event("epoch-residual", "1"))

    assert ledger.get_balance("agent-a") == Decimal("0.333333333")
    assert ledger.get_balance("agent-b") == Decimal("0.333333333")
    assert ledger.get_balance("agent-c") == Decimal("0.333333334")

    result = verify_stake_distribution(
        ledger.get_epoch_record("epoch-residual"),  # type: ignore[arg-type]
        snapshot,
        {"agent-a": "0", "agent-b": "0", "agent-c": "0"},
        {
            "agent-a": ledger.get_balance("agent-a"),
            "agent-b": ledger.get_balance("agent-b"),
            "agent-c": ledger.get_balance("agent-c"),
        },
    )
    assert result["ok"] is True
    assert result["max_agent_error"] == "0"


def test_attribution_proportional_payouts_preserve_total_with_residual() -> None:
    ok, payouts = evaluate_ejected_stake_vote(
        Decimal("1"),
        {"agent-a": Decimal("1"), "agent-b": Decimal("1"), "agent-c": Decimal("1")},
        approve_votes=3,
        participating_voters=3,
    )
    assert ok is True
    assert payouts == [
        ("agent-a", Decimal("0.333333333")),
        ("agent-b", Decimal("0.333333333")),
        ("agent-c", Decimal("0.333333334")),
    ]
    assert sum((amount for _, amount in payouts), Decimal("0")) == Decimal("1")

    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star-1", 1))
    batch.seal()
    coauthor_payouts = batch.settle(
        {"star-1": {"agent-a": Decimal("1"), "agent-b": Decimal("1"), "agent-c": Decimal("1")}}
    )
    assert sum((amount for _, amount in coauthor_payouts), Decimal("0")) == Decimal("0.20")


def test_canon_export_uses_atomic_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger = InMemoryLedgerBackend()
    ledger._set_balance("agent-a", Decimal("1.25"))
    out_path = tmp_path / "canon.json"
    replace_calls: list[tuple[object, object]] = []
    original_replace = canon_export.os.replace

    def recording_replace(src: str, dst: str) -> None:
        replace_calls.append((src, dst))
        original_replace(src, dst)

    monkeypatch.setattr(canon_export.os, "replace", recording_replace)
    canon_export.export_canon_state_json(ledger, out_path)

    assert replace_calls
    assert Path(replace_calls[0][1]) == out_path
    assert out_path.exists()
    assert json.loads(out_path.read_text(encoding="utf-8"))["balances"] == {
        "agent-a": "1.25"
    }
    assert not list(tmp_path.glob(".canon.json.*.tmp"))


@pytest.mark.parametrize(
    "path",
    (SPEC_DOC, WALKTHROUGH_DOC, STATUS_DOC, PLANNING_INDEX),
)
def test_phase_1331_fix2_tokens_are_recorded(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    for token in REQUIRED_TOKENS:
        assert token in text
