from __future__ import annotations

import pytest

from ilc_core.economics.agent_reputation_extractor import (
    AgentReputationRecord,
    compute_agent_reputation_root,
    extract_agent_reputation_record,
)
from ilc_core.economics.agent_reputation_lmdb_store import (
    PRODUCTION_REPUTATION_STORE_NOT_ACTIVATED_TOKEN,
    AgentReputationLmdbStore,
    require_production_reputation_store_activation,
)


AGENT_A = "a" * 96
AGENT_B = "b" * 96
ROOT_A = "1" * 64


def _evidence(*, agent_id: str = AGENT_A, epoch: int = 10) -> dict[str, object]:
    return {
        "agent_id": agent_id,
        "epoch": epoch,
        "graph_snapshot_evidence": {
            "snapshot_id": f"graph-snapshot-{epoch}",
            "node_count": 3,
            "edge_count": 2,
        },
        "lifecycle_evidence": {
            "last_active_epoch": epoch,
            "trust_vector": {
                "accuracy": "0.80",
                "precision": "0.70",
                "potential": "0.20",
            },
        },
        "liveness_evidence": {
            "stake": "400",
            "consecutive_missed_epochs": 0,
            "equivocation_state": False,
        },
        "equivocation_evidence": {
            "equivocation_state": False,
            "evidence_count": 0,
        },
        "sybil_evidence": {
            "unresolved_sybil_risk": False,
            "advisory_cluster_risk": "0.10",
        },
        "attribution_evidence": {
            "backward_attribution_batch_root": ROOT_A,
            "credited_paths": 2,
        },
    }


def _record(*, agent_id: str = AGENT_A, epoch: int = 10) -> AgentReputationRecord:
    return extract_agent_reputation_record(**_evidence(agent_id=agent_id, epoch=epoch))


def test_write_and_read_single_epoch(tmp_path) -> None:
    record = _record()
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        root = store.write_epoch_records(10, [record])
        records, stored_root = store.read_epoch_records(10)

    assert stored_root == root
    assert records == [record.to_canonical_record()]


def test_write_and_read_multiple_agents(tmp_path) -> None:
    first = _record(agent_id=AGENT_B)
    second = _record(agent_id=AGENT_A)
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        root = store.write_epoch_records(10, [first, second])
        records, stored_root = store.read_epoch_records(10)

    assert stored_root == root
    assert [item["agent_id"] for item in records] == [AGENT_A, AGENT_B]


def test_root_matches_compute_agent_reputation_root(tmp_path) -> None:
    records = [_record(agent_id=AGENT_A), _record(agent_id=AGENT_B)]
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        root = store.write_epoch_records(10, records)

    assert root == compute_agent_reputation_root(records)


def test_epoch_already_written_rejected(tmp_path) -> None:
    record = _record()
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        store.write_epoch_records(10, [record])
        with pytest.raises(ValueError, match="reputation_store_epoch_already_written"):
            store.write_epoch_records(10, [_record(agent_id=AGENT_B)])


def test_empty_records_rejected(tmp_path) -> None:
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        with pytest.raises(ValueError, match="reputation_store_empty_records_rejected"):
            store.write_epoch_records(10, [])


def test_epoch_not_found_raises(tmp_path) -> None:
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        with pytest.raises(ValueError, match="reputation_store_epoch_not_found"):
            store.read_epoch_records(10)
        with pytest.raises(ValueError, match="reputation_store_epoch_not_found"):
            store.get_committed_root(10)


def test_get_committed_root_matches_written(tmp_path) -> None:
    record = _record()
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        root = store.write_epoch_records(10, [record])

        assert store.get_committed_root(10) == root


def test_production_guard_raises() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_REPUTATION_STORE_NOT_ACTIVATED_TOKEN):
        require_production_reputation_store_activation()


def test_epoch_zero_accepted(tmp_path) -> None:
    record = _record(epoch=0)
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        root = store.write_epoch_records(0, [record])
        records, stored_root = store.read_epoch_records(0)

    assert stored_root == root
    assert records[0]["epoch"] == 0


def test_different_epochs_stored_independently(tmp_path) -> None:
    epoch_10 = _record(agent_id=AGENT_A, epoch=10)
    epoch_11 = _record(agent_id=AGENT_A, epoch=11)
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        root_10 = store.write_epoch_records(10, [epoch_10])
        root_11 = store.write_epoch_records(11, [epoch_11])

        assert store.get_committed_root(10) == root_10
        assert store.get_committed_root(11) == root_11
        assert root_10 != root_11


def test_epoch_key_must_match_record_epoch(tmp_path) -> None:
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        with pytest.raises(ValueError, match="reputation_store_epoch_mismatch_rejected"):
            store.write_epoch_records(11, [_record(epoch=10)])


def test_invalid_epoch_rejected(tmp_path) -> None:
    with AgentReputationLmdbStore(tmp_path / "reputation") as store:
        with pytest.raises(ValueError, match="reputation_store_epoch_must_be_non_negative_int"):
            store.write_epoch_records(True, [_record()])
        with pytest.raises(ValueError, match="reputation_store_epoch_must_be_non_negative_int"):
            store.read_epoch_records(-1)


def test_reopened_store_reads_committed_records(tmp_path) -> None:
    storage_dir = tmp_path / "reputation"
    record = _record()
    with AgentReputationLmdbStore(storage_dir) as store:
        root = store.write_epoch_records(10, [record])

    with AgentReputationLmdbStore(storage_dir) as reopened:
        records, stored_root = reopened.read_epoch_records(10)

    assert stored_root == root
    assert records == [record.to_canonical_record()]
