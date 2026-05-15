from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import lmdb
import pytest

from ilc_core.protocol.event_log_retention import (
    CDL_043_ADAPTIVE_PRUNING_VERSION,
    CDL_043_SNAPSHOT_INTERVAL_EPOCHS,
    CDL_044_EPOCH_SCOPE,
    CDL_044_RETENTION_EPOCHS,
    build_adaptive_event_log_retention_plan,
    compute_adaptive_pruning_threshold,
    is_below_adaptive_pruning_floor,
)
from ilc_core.storage.lmdb_graph_pruning_runtime import (
    CDL_071_TIER_2_EPOCH_SCOPE_TOKEN,
    LMDB_GRAPH_LEVEL_PRUNING_VERSION,
    MAX_LMDB_PRUNING_RECORD_BYTES,
    PRODUCTION_PRUNING_NOT_ACTIVATED_TOKEN,
    prune_lmdb_graph_tier_2_records,
)


def _write_epoch_dir(root: Path, epoch: int) -> None:
    path = root / f"epoch_{epoch:04d}"
    path.mkdir()
    (path / "devnet_events.ndjson").write_text("event\n", encoding="utf-8")


def _put_json(env: lmdb.Environment, db: lmdb._Database, key: str, payload: dict[str, object]) -> None:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    with env.begin(write=True, db=db) as txn:
        txn.put(key.encode("utf-8"), encoded)


def _get_json(env: lmdb.Environment, db: lmdb._Database, key: str) -> dict[str, object] | None:
    with env.begin(db=db) as txn:
        value = txn.get(key.encode("utf-8"))
    if value is None:
        return None
    payload = json.loads(value.decode("utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_adaptive_threshold_binds_cdl_043_and_044_issuance_epoch_constants() -> None:
    threshold = compute_adaptive_pruning_threshold(
        current_issuance_epoch=10,
        minting_confirmed=True,
    )

    assert threshold["version"] == CDL_043_ADAPTIVE_PRUNING_VERSION
    assert threshold["epoch_scope"] == CDL_044_EPOCH_SCOPE
    assert threshold["eligible_before_or_at_epoch"] == 9
    assert threshold["retention_epochs"] == CDL_044_RETENTION_EPOCHS == 1
    assert threshold["ecu_score_floor"] == "0.5"
    assert threshold["snapshot_interval_epochs"] == CDL_043_SNAPSHOT_INTERVAL_EPOCHS == 50


def test_retention_epochs_override_rejected_as_constitutional_constant(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="retention_epochs_is_constitutional_constant"):
        compute_adaptive_pruning_threshold(
            current_issuance_epoch=10,
            minting_confirmed=True,
            retention_epochs=2,
        )

    with pytest.raises(ValueError, match="retention_epochs_is_constitutional_constant"):
        build_adaptive_event_log_retention_plan(
            tmp_path,
            current_issuance_epoch=10,
            ecu_score=Decimal("0.4"),
            minting_confirmed=True,
            retention_epochs=2,
        )


def test_adaptive_event_log_plan_prunes_low_score_confirmed_epochs(tmp_path: Path) -> None:
    for epoch in range(1, 6):
        _write_epoch_dir(tmp_path, epoch)

    plan = build_adaptive_event_log_retention_plan(
        tmp_path,
        current_issuance_epoch=5,
        ecu_score=Decimal("0.4"),
        minting_confirmed=True,
    )

    assert plan["pruning_enabled"] is True
    assert [Path(path).name for path in plan["prune"]] == [
        "epoch_0001",
        "epoch_0002",
        "epoch_0003",
        "epoch_0004",
    ]
    assert [Path(path).name for path in plan["keep"]] == ["epoch_0005"]


def test_adaptive_event_log_plan_retains_high_score_or_unconfirmed_epochs(tmp_path: Path) -> None:
    for epoch in range(1, 4):
        _write_epoch_dir(tmp_path, epoch)

    high_score = build_adaptive_event_log_retention_plan(
        tmp_path,
        current_issuance_epoch=3,
        ecu_score=Decimal("0.5"),
        minting_confirmed=True,
    )
    unconfirmed = build_adaptive_event_log_retention_plan(
        tmp_path,
        current_issuance_epoch=3,
        ecu_score=Decimal("0.1"),
        minting_confirmed=False,
    )

    assert high_score["prune"] == []
    assert high_score["pruning_enabled"] is False
    assert unconfirmed["prune"] == []
    assert unconfirmed["pruning_enabled"] is False


def test_non_finite_and_float_scores_are_rejected() -> None:
    with pytest.raises(ValueError, match="ecu_score_invalid_phase_1361"):
        is_below_adaptive_pruning_floor(Decimal("Infinity"))

    with pytest.raises(ValueError, match="ecu_score_invalid_phase_1361"):
        is_below_adaptive_pruning_floor(0.4)


def test_lmdb_pruning_deletes_only_tier_2_issuance_epoch_low_score_records(tmp_path: Path) -> None:
    env = lmdb.open(str(tmp_path), max_dbs=1, map_size=1024 * 1024)
    db = env.open_db(b"nodes")
    try:
        _put_json(
            env,
            db,
            "old-low",
            {
                "id": "old-low",
                "temporal_tier": "tier_2",
                "epoch_scope": "issuance_epoch",
                "issuance_epoch": 3,
                "ecu_score": "0.4",
            },
        )
        _put_json(
            env,
            db,
            "old-floor",
            {
                "id": "old-floor",
                "temporal_tier": "tier_2",
                "epoch_scope": "issuance_epoch",
                "issuance_epoch": 3,
                "ecu_score": "0.5",
            },
        )
        _put_json(
            env,
            db,
            "recent-low",
            {
                "id": "recent-low",
                "temporal_tier": "tier_2",
                "epoch_scope": "issuance_epoch",
                "issuance_epoch": 10,
                "ecu_score": "0.1",
            },
        )
        _put_json(
            env,
            db,
            "tier3-old",
            {
                "id": "tier3-old",
                "temporal_tier": "tier_3",
                "epoch_scope": "permanent",
                "issuance_epoch": 1,
                "ecu_score": "0.0",
            },
        )
        _put_json(
            env,
            db,
            "validation-old",
            {
                "id": "validation-old",
                "temporal_tier": "tier_2",
                "epoch_scope": "validation_epoch",
                "issuance_epoch": 1,
                "ecu_score": "0.0",
            },
        )

        result = prune_lmdb_graph_tier_2_records(
            env,
            db,
            current_issuance_epoch=10,
            minting_confirmed=True,
            dry_run=False,
        )

        assert result["version"] == LMDB_GRAPH_LEVEL_PRUNING_VERSION
        assert result["deleted"] == 1
        assert result["planned_prune"] == 1
        assert result["skipped_not_tier_2"] == 2
        assert _get_json(env, db, "old-low") is None
        assert _get_json(env, db, "old-floor") is not None
        assert _get_json(env, db, "recent-low") is not None
        assert _get_json(env, db, "tier3-old") is not None
        assert _get_json(env, db, "validation-old") is not None
    finally:
        env.close()


def test_lmdb_pruning_dry_run_and_batch_cap_are_bounded(tmp_path: Path) -> None:
    env = lmdb.open(str(tmp_path), max_dbs=1, map_size=1024 * 1024)
    db = env.open_db(b"nodes")
    try:
        for key in ("old-low-a", "old-low-b"):
            _put_json(
                env,
                db,
                key,
                {
                    "id": key,
                    "temporal_tier": "tier_2",
                    "epoch_scope": "issuance_epoch",
                    "issuance_epoch": 1,
                    "ecu_score": "0.1",
                },
            )

        result = prune_lmdb_graph_tier_2_records(
            env,
            db,
            current_issuance_epoch=5,
            minting_confirmed=True,
            dry_run=True,
            max_records_per_batch=1,
        )

        assert result["scanned"] == 1
        assert result["planned_prune"] == 1
        assert result["deleted"] == 0
        assert result["stopped_at_batch_cap"] is True
        assert _get_json(env, db, "old-low-a") is not None
        assert _get_json(env, db, "old-low-b") is not None
    finally:
        env.close()


def test_lmdb_pruning_requires_minting_confirmation(tmp_path: Path) -> None:
    env = lmdb.open(str(tmp_path), max_dbs=1, map_size=1024 * 1024)
    db = env.open_db(b"nodes")
    try:
        _put_json(
            env,
            db,
            "old-low",
            {
                "id": "old-low",
                "temporal_tier": "tier_2",
                "epoch_scope": "issuance_epoch",
                "issuance_epoch": 1,
                "ecu_score": "0.1",
            },
        )

        result = prune_lmdb_graph_tier_2_records(
            env,
            db,
            current_issuance_epoch=5,
            minting_confirmed=False,
            dry_run=False,
        )

        assert result["planned_prune"] == 0
        assert result["deleted"] == 0
        assert _get_json(env, db, "old-low") is not None
    finally:
        env.close()


def test_lmdb_pruning_rejects_oversized_record_payload(tmp_path: Path) -> None:
    env = lmdb.open(str(tmp_path), max_dbs=1, map_size=1024 * 1024)
    db = env.open_db(b"nodes")
    try:
        with env.begin(write=True, db=db) as txn:
            txn.put(b"oversized", b"{" + (b" " * MAX_LMDB_PRUNING_RECORD_BYTES) + b"}")

        with pytest.raises(ValueError, match="lmdb_pruning_record_too_large_phase_1361"):
            prune_lmdb_graph_tier_2_records(
                env,
                db,
                current_issuance_epoch=5,
                minting_confirmed=True,
            )
    finally:
        env.close()


def test_lmdb_production_pruning_gate_and_retention_override(tmp_path: Path) -> None:
    env = lmdb.open(str(tmp_path), max_dbs=1, map_size=1024 * 1024)
    db = env.open_db(b"nodes")
    try:
        with pytest.raises(ValueError, match=PRODUCTION_PRUNING_NOT_ACTIVATED_TOKEN):
            prune_lmdb_graph_tier_2_records(
                env,
                db,
                current_issuance_epoch=5,
                minting_confirmed=True,
                production=True,
            )

        with pytest.raises(ValueError, match="retention_epochs_is_constitutional_constant"):
            prune_lmdb_graph_tier_2_records(
                env,
                db,
                current_issuance_epoch=5,
                minting_confirmed=True,
                retention_epochs=2,
            )
    finally:
        env.close()


def test_required_phase_1361_tokens_are_exposed() -> None:
    assert CDL_043_ADAPTIVE_PRUNING_VERSION == "cdl_043_adaptive_pruning_threshold_runtime_phase_1361.v0.1"
    assert LMDB_GRAPH_LEVEL_PRUNING_VERSION == "lmdb_graph_level_pruning_path_phase_1361"
    assert CDL_071_TIER_2_EPOCH_SCOPE_TOKEN == "cdl_071_tier_2_epoch_scope_enforcement_phase_1361"
    assert PRODUCTION_PRUNING_NOT_ACTIVATED_TOKEN == "production_pruning_not_activated_phase_1361"
