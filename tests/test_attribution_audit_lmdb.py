from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.consensus.attribution_audit_lmdb import (
    ATTR_EVENTS_DB_NAME,
    EPOCH_INDEX_DB_NAME,
    AttributionAuditLmdbStore,
    MAX_ATTRIBUTION_AUDIT_EVENT_BYTES,
    MAX_ATTRIBUTION_AUDIT_EVENT_COUNT,
)
from ilc_core.consensus import attribution_audit_lmdb as audit_lmdb
from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    build_attribution_batch_from_claims,
)


AGENT_ID = "a" * 96


def test_write_and_read_epoch_events_in_ordinal_order(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")
    events = [
        {"event_id": "event-1", "credit_amount": "0.1"},
        {"event_id": "event-2", "credit_amount": "0.2"},
    ]
    store.write_epoch_events(3, events)

    assert store.read_epoch_events(3) == events
    assert store.get_epoch_count(3) == 2


def test_list_epochs_returns_written_epochs_in_numeric_order(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")
    store.write_epoch_events(9, [{"event_id": "event-9"}])
    store.write_epoch_events(2, [{"event_id": "event-2"}])
    store.write_epoch_events(11, [])

    assert store.list_epochs() == [2, 9, 11]


def test_empty_epoch_write_blocks_later_overwrite(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")
    store.write_epoch_events(11, [])

    with pytest.raises(ValueError, match="attribution_audit_epoch_already_written"):
        store.write_epoch_events(11, [{"event_id": "late"}])


def test_epoch_overwrite_rejected(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")
    store.write_epoch_events(3, [{"event_id": "event-1"}])

    with pytest.raises(ValueError, match="attribution_audit_epoch_already_written"):
        store.write_epoch_events(3, [{"event_id": "event-2"}])


def test_absent_epoch_returns_empty_list(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")

    assert store.read_epoch_events(9) == []
    assert store.get_epoch_count(9) == 0


def test_invalid_epoch_and_event_inputs_rejected(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")

    with pytest.raises(ValueError, match="attribution_audit_epoch_invalid"):
        store.write_epoch_events(True, [])
    with pytest.raises(ValueError, match="attribution_audit_event_invalid"):
        store.write_epoch_events(1, ["not-object"])  # type: ignore[list-item]


def test_oversized_audit_inputs_rejected(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")

    with pytest.raises(ValueError, match="attribution_audit_events_too_many"):
        store.write_epoch_events(1, [{} for _ in range(MAX_ATTRIBUTION_AUDIT_EVENT_COUNT + 1)])

    with pytest.raises(ValueError, match="attribution_audit_event_too_large"):
        store.write_epoch_events(2, [{"payload": "x" * (MAX_ATTRIBUTION_AUDIT_EVENT_BYTES + 1)}])


def test_corrupted_lmdb_event_and_index_raise_stable_tokens(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")
    store.write_epoch_events(3, [{"event_id": "event-1"}])
    event_key = audit_lmdb._event_key(3, 0)  # noqa: SLF001 - corruption harness.
    with store.env.begin(write=True) as txn:
        txn.put(event_key, b"{not-json", db=store._attr_events_db)  # noqa: SLF001

    with pytest.raises(ValueError, match="attribution_audit_event_corrupted"):
        store.read_epoch_events(3)

    with store.env.begin(write=True) as txn:
        txn.put(
            audit_lmdb._epoch_index_key(3),  # noqa: SLF001
            b"{not-json",
            db=store._epoch_index_db,  # noqa: SLF001
        )

    with pytest.raises(ValueError, match="attribution_audit_epoch_index_corrupted"):
        store.read_epoch_events(3)


def test_subdatabase_names_are_phase_1594_contract() -> None:
    assert ATTR_EVENTS_DB_NAME == b"attr_events"
    assert EPOCH_INDEX_DB_NAME == b"epoch_index"


def test_batch_bridge_writes_empty_epoch_when_audit_store_has_no_backward_context(
    tmp_path: Path,
) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")
    payload = {
        "marker": "agent_loop_claims_ok",
        "claims": [
            {
                "agent_id": AGENT_ID,
                "amount": "1.0",
                "claim_id": "claim-1",
                "epoch": 4,
            }
        ],
    }

    batch = build_attribution_batch_from_claims(payload, attribution_audit_store=store)

    assert batch["epoch"] == 4
    assert store.read_epoch_events(4) == []


def test_batch_bridge_rejects_dual_file_and_lmdb_audit_backends(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "audit")
    payload = {
        "marker": "agent_loop_claims_ok",
        "claims": [
            {
                "agent_id": AGENT_ID,
                "amount": "1.0",
                "claim_id": "claim-1",
                "epoch": 4,
            }
        ],
    }

    with pytest.raises(
        AttributionBatchBridgeError,
        match="attribution_audit_dual_backend_not_permitted",
    ):
        build_attribution_batch_from_claims(
            payload,
            attribution_audit_store=store,
            attribution_event_log_dir=tmp_path / "events",
        )
