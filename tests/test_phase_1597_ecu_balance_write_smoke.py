from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ilc_core.consensus.attribution_batch_bridge import AttributionBatchBridgeError
from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from tools.ecu.ecu_balance_write_smoke import (
    AMOUNT_MICRO_ECU,
    ARCHITECTURE_GAP_TOKEN,
    OUTPUT_TOKEN,
    Phase1597SmokeError,
    _require_test_lmdb_path,
    build_phase_1597_batch,
    run_smoke,
)


def _binary(tmp_path: Path) -> Path:
    path = tmp_path / "attribution_batch_ingest"
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def _mutate_lmdb(path: Path, label: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "data.mdb").write_bytes(label.encode("utf-8"))


class MockBridge:
    def __init__(self, *, bad_marker: bool = False) -> None:
        self.bad_marker = bad_marker
        self.calls: list[dict[str, Any]] = []
        self.committed_epochs: set[int] = set()

    def __call__(
        self,
        batch_payload: dict[str, Any],
        *,
        consensus_lmdb: Path,
        rust_binary: Path,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "batch_payload": batch_payload,
                "consensus_lmdb": Path(consensus_lmdb),
                "dry_run": dry_run,
                "rust_binary": Path(rust_binary),
            }
        )
        epoch = int(batch_payload["epoch"])
        marker = "bad_marker" if self.bad_marker else "attribution_batch_ingest_ok"
        if dry_run:
            return {
                "attribution_count": 1,
                "balances": [],
                "dry_run": True,
                "epoch": epoch,
                "input_sha256": "0" * 64,
                "marker": marker,
                "total_micro_ecu": AMOUNT_MICRO_ECU,
            }
        if epoch in self.committed_epochs:
            raise AttributionBatchBridgeError(
                "rust_attribution_batch_ingest_failed",
                "balance_store_apply_attribution_failed: Invalid epoch reference",
            )
        self.committed_epochs.add(epoch)
        _mutate_lmdb(Path(consensus_lmdb), f"applied:{epoch}:{AMOUNT_MICRO_ECU}")
        return {
            "attribution_count": 1,
            "balances": [
                {
                    "agent_id_hex": GENESIS_AGENT1_AGENT_ID,
                    "amount_micro_ecu": AMOUNT_MICRO_ECU,
                    "epoch": epoch,
                    "version": 0,
                }
            ],
            "dry_run": False,
            "epoch": epoch,
            "input_sha256": "0" * 64,
            "marker": marker,
            "total_micro_ecu": AMOUNT_MICRO_ECU,
        }


class NonMutatingBridge(MockBridge):
    def __call__(
        self,
        batch_payload: dict[str, Any],
        *,
        consensus_lmdb: Path,
        rust_binary: Path,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if dry_run:
            return super().__call__(
                batch_payload,
                consensus_lmdb=consensus_lmdb,
                rust_binary=rust_binary,
                dry_run=dry_run,
            )
        epoch = int(batch_payload["epoch"])
        self.calls.append(
            {
                "batch_payload": batch_payload,
                "consensus_lmdb": Path(consensus_lmdb),
                "dry_run": dry_run,
                "rust_binary": Path(rust_binary),
            }
        )
        return {
            "attribution_count": 1,
            "balances": [
                {
                    "agent_id_hex": GENESIS_AGENT1_AGENT_ID,
                    "amount_micro_ecu": AMOUNT_MICRO_ECU,
                    "epoch": epoch,
                    "version": 0,
                }
            ],
            "dry_run": False,
            "epoch": epoch,
            "input_sha256": "0" * 64,
            "marker": "attribution_batch_ingest_ok",
            "total_micro_ecu": AMOUNT_MICRO_ECU,
        }


def _run_with_mock(tmp_path: Path, bridge: MockBridge | None = None) -> dict[str, Any]:
    return run_smoke(
        rust_binary=_binary(tmp_path),
        consensus_lmdb=tmp_path / "test_ecu_balances.lmdb",
        evidence_path=tmp_path / "evidence.json",
        bridge_func=bridge or MockBridge(),
    )


def _walk_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise AssertionError("float found")
    if isinstance(value, dict):
        for item in value.values():
            _walk_no_float(item)
    if isinstance(value, list):
        for item in value:
            _walk_no_float(item)


def test_write_readback_exact_micro_ecu(tmp_path: Path) -> None:
    evidence = _run_with_mock(tmp_path)

    assert evidence["output_token"] == OUTPUT_TOKEN
    assert evidence["first_write_amount_micro_ecu"] == AMOUNT_MICRO_ECU
    assert evidence["replay_balance_proof"] == "first_write_report_plus_replay_lmdb_data_mdb_sha256_unchanged"
    assert isinstance(evidence["binary_sha256"], str)
    assert len(evidence["binary_sha256"]) == 64
    assert evidence["binary_size_bytes"] > 0
    assert evidence["architecture_gap_documented"] == ARCHITECTURE_GAP_TOKEN


def test_test_lmdb_path_not_public_wallet() -> None:
    with pytest.raises(ValueError, match="test_lmdb_path_points_at_live_wallet"):
        _require_test_lmdb_path(Path("out/public_runtime/wallet"))


def test_ingest_marker_must_be_ok(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="attribution_batch_ingest_marker_invalid"):
        _run_with_mock(tmp_path, MockBridge(bad_marker=True))


def test_replay_guard_second_epoch_rejected(tmp_path: Path) -> None:
    evidence = _run_with_mock(tmp_path)

    assert evidence["replay_rejected"] is True
    assert evidence["replay_error_token"] == "rust_attribution_batch_ingest_failed"
    assert evidence["replay_lmdb_data_mdb_sha256_unchanged"] is True


def test_mock_rejects_same_epoch_but_allows_new_epoch(tmp_path: Path) -> None:
    bridge = MockBridge()
    binary = _binary(tmp_path)
    lmdb = tmp_path / "store.lmdb"

    bridge(build_phase_1597_batch(epoch=1), consensus_lmdb=lmdb, rust_binary=binary, dry_run=False)
    bridge(build_phase_1597_batch(epoch=2), consensus_lmdb=lmdb, rust_binary=binary, dry_run=False)

    with pytest.raises(AttributionBatchBridgeError):
        bridge(build_phase_1597_batch(epoch=2), consensus_lmdb=lmdb, rust_binary=binary, dry_run=False)


def test_dry_run_does_not_mutate(tmp_path: Path) -> None:
    evidence = _run_with_mock(tmp_path)

    assert evidence["same_batch_dry_run_balances_empty"] is True
    assert evidence["dry_run_lmdb_data_mdb_sha256_unchanged"] is True


def test_write_must_mutate_test_lmdb(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="test_lmdb_sha256_did_not_change_after_write"):
        _run_with_mock(tmp_path, NonMutatingBridge())


def test_no_float_in_evidence(tmp_path: Path) -> None:
    evidence_path = tmp_path / "evidence.json"
    run_smoke(
        rust_binary=_binary(tmp_path),
        consensus_lmdb=tmp_path / "test_ecu_balances.lmdb",
        evidence_path=evidence_path,
        bridge_func=MockBridge(),
    )
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))

    _walk_no_float(payload)


def test_binary_missing_raises_with_token(tmp_path: Path) -> None:
    with pytest.raises(Phase1597SmokeError) as excinfo:
        run_smoke(
            rust_binary=tmp_path / "missing-attribution-binary",
            consensus_lmdb=tmp_path / "test_ecu_balances.lmdb",
            evidence_path=tmp_path / "evidence.json",
            bridge_func=MockBridge(),
        )
    assert excinfo.value.token == "attribution_batch_ingest_binary_missing_phase_1597"


def test_binary_not_executable_raises_with_token(tmp_path: Path) -> None:
    binary = tmp_path / "attribution_batch_ingest"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    binary.chmod(0o644)

    with pytest.raises(Phase1597SmokeError) as excinfo:
        run_smoke(
            rust_binary=binary,
            consensus_lmdb=tmp_path / "test_ecu_balances.lmdb",
            evidence_path=tmp_path / "evidence.json",
            bridge_func=MockBridge(),
        )
    assert excinfo.value.token == "attribution_batch_ingest_binary_not_executable_phase_1597"


def test_reset_lmdb_refuses_existing_path_outside_evidence_scope(tmp_path: Path) -> None:
    outside = tmp_path / "outside" / "test_ecu_balances.lmdb"
    outside.mkdir(parents=True)
    (outside / "data.mdb").write_text("old", encoding="utf-8")

    with pytest.raises(Phase1597SmokeError) as excinfo:
        run_smoke(
            rust_binary=_binary(tmp_path),
            consensus_lmdb=outside,
            evidence_path=tmp_path / "evidence" / "evidence.json",
            bridge_func=MockBridge(),
        )
    assert excinfo.value.token == "test_lmdb_reset_path_outside_phase_scope"
