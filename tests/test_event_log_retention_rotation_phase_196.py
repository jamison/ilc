from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.protocol.event_log_retention import (
    apply_event_log_retention_plan,
    build_event_log_retention_plan,
)


def _mk_epoch_dir(root: Path, epoch_index: int, *, with_events: bool = True) -> Path:
    path = root / f"epoch_{epoch_index:04d}"
    path.mkdir(parents=True, exist_ok=True)
    if with_events:
        (path / "devnet_events.ndjson").write_text('{"kind":"epoch_summary","payload":{}}\n', encoding="utf-8")
    return path


def test_phase_196_retention_plan_keeps_latest_and_prunes_older(tmp_path: Path) -> None:
    for idx in range(1, 6):
        _mk_epoch_dir(tmp_path, idx)

    # Should be ignored by planner: no event log file
    _mk_epoch_dir(tmp_path, 6, with_events=False)
    # Should be ignored by planner: wrong name pattern
    (tmp_path / "random_dir").mkdir()

    plan = build_event_log_retention_plan(tmp_path, keep_last=2)

    assert plan["keep_last"] == 2
    assert plan["keep"] == [str(tmp_path / "epoch_0004"), str(tmp_path / "epoch_0005")]
    assert plan["prune"] == [
        str(tmp_path / "epoch_0001"),
        str(tmp_path / "epoch_0002"),
        str(tmp_path / "epoch_0003"),
    ]


def test_phase_196_retention_apply_dry_run_does_not_delete(tmp_path: Path) -> None:
    for idx in range(1, 5):
        _mk_epoch_dir(tmp_path, idx)

    plan = build_event_log_retention_plan(tmp_path, keep_last=2)
    result = apply_event_log_retention_plan(plan, dry_run=True)

    assert result["dry_run"] is True
    assert result["planned_prune"] == 2
    assert result["deleted"] == 0
    assert sorted(result["pruned_dirs"]) == sorted(
        [str(tmp_path / "epoch_0001"), str(tmp_path / "epoch_0002")]
    )

    assert (tmp_path / "epoch_0001").exists()
    assert (tmp_path / "epoch_0002").exists()


def test_phase_196_retention_apply_deletes_only_planned_epoch_dirs(tmp_path: Path) -> None:
    for idx in range(1, 5):
        _mk_epoch_dir(tmp_path, idx)

    plan = build_event_log_retention_plan(tmp_path, keep_last=1)
    result = apply_event_log_retention_plan(plan, dry_run=False)

    assert result["dry_run"] is False
    assert result["planned_prune"] == 3
    assert result["deleted"] == 3

    assert not (tmp_path / "epoch_0001").exists()
    assert not (tmp_path / "epoch_0002").exists()
    assert not (tmp_path / "epoch_0003").exists()
    assert (tmp_path / "epoch_0004").exists()


def test_phase_196_keep_last_must_be_positive() -> None:
    with pytest.raises(ValueError, match="keep_last must be >= 1"):
        build_event_log_retention_plan(".", keep_last=0)
