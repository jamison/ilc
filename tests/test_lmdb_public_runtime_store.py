from __future__ import annotations

from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ilc_core.ledger import get_ledger_backend
from ilc_core.ledger.lmdb_backend import LmdbLedgerBackend
from ilc_core.ledger.stake_snapshot import StakeSnapshot
from ilc_core.protocol.event_log import ProtocolEvent
from ilc_core.storage.lmdb_public_runtime import LmdbGraphStore, LmdbWalletStore
from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedger


def _commit_event(
    epoch_id: str,
    index: int,
    reward: Decimal | str = Decimal("50"),
) -> ProtocolEvent:
    return ProtocolEvent(
        kind="commit.epoch",
        received_at=datetime.now(timezone.utc).isoformat(),
        source="test",
        payload={
            "event_kind": "commit.epoch",
            "epoch_index": index,
            "epoch_id": epoch_id,
            "namespace_id": "test_ns",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "finalization_state": "committed",
            "summary": {
                "reward_total": str(reward),
                "stake_total": "100",
                "task_count": 1,
                "agent_count": 1,
            },
            "checksums": {"epoch_events_cid": "cid-events", "epoch_state_cid": "cid-state"},
        },
    )


def test_lmdb_graph_store_persists_nodes_links_and_quorum(tmp_path: Path) -> None:
    store_root = tmp_path / "graph-store"
    graph_store = LmdbGraphStore(store_root)
    graph_store.put_node("node-a", {"id": "node-a", "type": "claim"})
    graph_store.put_node("node-b", {"id": "node-b", "type": "claim"})
    graph_store.put_link("link-1", {"id": "link-1", "source_id": "node-a", "target_id": "node-b"})
    graph_store.put_quorum_record({"task_id": "task-1", "verdict_token": "panel_quorum_passed"})

    graph_store_reloaded = LmdbGraphStore(store_root)
    assert [row["id"] for row in graph_store_reloaded.iter_nodes()] == ["node-a", "node-b"]
    assert graph_store_reloaded.iter_links()[0]["id"] == "link-1"
    assert graph_store_reloaded.get_quorum_record()["task_id"] == "task-1"


def test_lmdb_wallet_store_persists_wallet_rows_and_history(tmp_path: Path) -> None:
    store_root = tmp_path / "wallet-store"
    wallet_store = LmdbWalletStore(store_root)
    wallet_store.put_wallet("agent-a", {"balance_ilc": 3.0, "reward_status": "rewarded"})
    wallet_store.put_wallet_history("agent-a", {"claim_history": [{"claim_id": "c1"}], "epoch_history": [{"epoch_id": "e1"}]})

    wallet_store_reloaded = LmdbWalletStore(store_root)
    assert wallet_store_reloaded.get_wallet("agent-a")["balance_ilc"] == 3.0
    assert wallet_store_reloaded.get_wallet_history("agent-a")["claim_history"][0]["claim_id"] == "c1"


def test_lmdb_wallet_store_env_has_headroom_for_transfer_ledger(tmp_path: Path) -> None:
    store_root = tmp_path / "wallet-store"
    wallet_store = LmdbWalletStore(store_root)
    try:
        ledger = ILCTransferLedger(wallet_store.env)
        assert ledger.get_balance("a" * 96) == Decimal("0")
    finally:
        wallet_store.close()


def test_lmdb_graph_store_normalizes_decimal_payloads(tmp_path: Path) -> None:
    store_root = tmp_path / "graph-store"
    graph_store = LmdbGraphStore(store_root)

    graph_store.put_node(
        "node-a",
        {
            "id": "node-a",
            "type": "claim",
            "net_stake": Decimal("2.5"),
            "nested": {"reward": Decimal("1.25")},
        },
    )

    row = graph_store.get_node("node-a")
    assert row == {
        "id": "node-a",
        "type": "claim",
        "net_stake": "2.5",
        "nested": {"reward": "1.25"},
    }


def test_lmdb_ledger_backend_survives_restart_and_factory_supports_it(tmp_path: Path) -> None:
    ledger_root = tmp_path / "ledger-store"
    ledger = LmdbLedgerBackend(ledger_root)
    snapshot = StakeSnapshot(
        epoch_id="epoch-1",
        epoch_index=1,
        namespace_id="test_ns",
        stakes={"agent-a": Decimal("100")},
        total_stake=Decimal("100"),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    ledger.put_stake_snapshot(snapshot)
    ledger.apply_epoch_settlement(_commit_event("epoch-1", 1))

    reloaded = LmdbLedgerBackend(ledger_root)
    assert reloaded.get_balance("agent-a") == Decimal("50")
    assert reloaded.get_epoch_record("epoch-1")["status"] == "settled"
    assert reloaded.get_stake_snapshot("epoch-1") == snapshot

    factory_backend = get_ledger_backend("lmdb", storage_dir=str(ledger_root))
    assert isinstance(factory_backend, LmdbLedgerBackend)


def test_lmdb_ledger_backend_rolls_back_partial_epoch_settlement_on_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ledger_root = tmp_path / "ledger-store"
    ledger = LmdbLedgerBackend(ledger_root)
    snapshot = StakeSnapshot(
        epoch_id="epoch-rollback",
        epoch_index=2,
        namespace_id="test_ns",
        stakes={"agent-a": Decimal("50"), "agent-b": Decimal("50")},
        total_stake=Decimal("100"),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    ledger.put_stake_snapshot(snapshot)

    original_set_balance = ledger._set_balance
    call_count = 0

    def flaky_set_balance(agent_id: str, new_balance: Decimal | int | str) -> None:
        nonlocal call_count
        call_count += 1
        original_set_balance(agent_id, new_balance)
        if call_count == 1:
            raise RuntimeError("simulated_settlement_failure")

    monkeypatch.setattr(ledger, "_set_balance", flaky_set_balance)

    with pytest.raises(RuntimeError, match="simulated_settlement_failure"):
        ledger.apply_epoch_settlement(_commit_event("epoch-rollback", 2))

    assert ledger.get_balance("agent-a") == Decimal("0")
    assert ledger.get_balance("agent-b") == Decimal("0")
    assert ledger.get_epoch_record("epoch-rollback") is None

    reloaded = LmdbLedgerBackend(ledger_root)
    assert reloaded.get_balance("agent-a") == Decimal("0")
    assert reloaded.get_balance("agent-b") == Decimal("0")
    assert reloaded.get_epoch_record("epoch-rollback") is None
