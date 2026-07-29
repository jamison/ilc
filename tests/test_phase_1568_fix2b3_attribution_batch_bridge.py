from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    apply_attribution_batch_with_rust,
    build_attribution_batch_from_claims,
)
from tools import agent_loop_v1
from tests.test_agent_loop_v1_runtime import _cdl069_seed, _legacy_seed, _submission, _task


ROOT = Path(__file__).resolve().parents[1]


def _cargo() -> str:
    discovered = shutil.which("cargo")
    if discovered:
        return discovered
    fallback = Path.home() / ".cargo" / "bin" / "cargo"
    if fallback.exists():
        return str(fallback)
    return "cargo"


@pytest.fixture(scope="session")
def attribution_binary() -> Path:
    result = subprocess.run(
        [
            _cargo(),
            "build",
            "--manifest-path",
            str(ROOT / "ilc_consensus" / "Cargo.toml"),
            "--bin",
            "attribution_batch_ingest",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr
    binary = ROOT / "ilc_consensus" / "target" / "debug" / "attribution_batch_ingest"
    assert binary.exists()
    return binary


def _passing_claim_payload() -> dict[str, object]:
    submissions = [
        _submission(1, _cdl069_seed("01"), "cluster-a"),
        _submission(2, _cdl069_seed("02"), "cluster-b"),
        _submission(3, _cdl069_seed("03"), "cluster-c"),
        _submission(4, _cdl069_seed("04"), "cluster-a"),
        _submission(5, _cdl069_seed("05"), "cluster-b"),
        _submission(6, _cdl069_seed("06"), "cluster-c"),
        _submission(7, _cdl069_seed("07"), "cluster-d", variant="divergent"),
    ]
    outsider = agent_loop_v1._build_outsider_submission(_task(), _legacy_seed("08"), "cluster-e", "ilc-node-1")
    panel_payload = agent_loop_v1.evaluate_panel(task=_task(), submissions=submissions, outsider_submission=outsider)
    return agent_loop_v1.build_ecu_claim_batch(_task(), panel_payload)


def test_claim_payload_converts_to_consensus_attribution_batch_with_dust_accounting() -> None:
    claim_payload = _passing_claim_payload()

    batch = build_attribution_batch_from_claims(claim_payload)

    assert batch["marker"] == "attribution_batch_bridge_ok"
    assert batch["epoch"] == 574
    assert batch["rounding"] == "floor_to_micro_ecu_no_over_credit"
    assert batch["source_claim_count"] == 6
    assert batch["attribution_count"] == 6
    assert batch["total_source_ecu"] == "5.8173828125"
    assert batch["total_micro_ecu"] == 5817378
    assert batch["total_dust_ecu"] == "0.0000048125"
    assert [item["agent_id_hex"] for item in batch["attributions"]] == sorted(
        item["agent_id_hex"] for item in batch["attributions"]
    )
    assert all(item["amount_micro_ecu"] > 0 for item in batch["attributions"])


def test_bridge_rejects_malformed_agent_id() -> None:
    claim_payload = _passing_claim_payload()
    claim_payload["claims"][0]["agent_id"] = "AA"

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "agent_id_hex_must_be_96_lower_hex"


def test_bridge_rejects_duplicate_claim_id_in_same_batch() -> None:
    claim_payload = _passing_claim_payload()
    claim_payload["claims"][1]["claim_id"] = claim_payload["claims"][0]["claim_id"]

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "claim_id_duplicate_in_batch"


def test_bridge_rejects_claim_count_above_maximum() -> None:
    claim_payload = _passing_claim_payload()
    claim_payload["claims"] = [claim_payload["claims"][0]] * 10_001

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "claim_count_exceeds_maximum"


def test_bridge_wraps_rust_ingest_timeout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def _timeout_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd=["attribution_batch_ingest"], timeout=1)

    fake_binary = tmp_path / "attribution_batch_ingest"
    fake_binary.touch()
    monkeypatch.setattr(subprocess, "run", _timeout_run)

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        apply_attribution_batch_with_rust(
            build_attribution_batch_from_claims(_passing_claim_payload()),
            consensus_lmdb=tmp_path / "store.lmdb",
            rust_binary=fake_binary,
            dry_run=True,
            timeout_seconds=1,
        )

    assert excinfo.value.token == "rust_attribution_batch_ingest_timeout"


def test_agent_loop_cli_builds_attribution_batch(tmp_path: Path) -> None:
    claims_path = tmp_path / "ecu_claims.json"
    claims_path.write_text(
        json.dumps(_passing_claim_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "tools/agent_loop_v1.py",
            "build-attribution-batch",
            "--ecu-claims-file",
            str(claims_path),
            "--emit-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["marker"] == "attribution_batch_bridge_ok"
    assert (tmp_path / "consensus_attribution_batch.json").exists()


def test_rust_ingest_applies_batch_and_rejects_same_epoch_replay(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = build_attribution_batch_from_claims(_passing_claim_payload())
    lmdb_path = tmp_path / "consensus-balances.lmdb"

    dry_run = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=lmdb_path,
        rust_binary=attribution_binary,
        dry_run=True,
    )
    assert dry_run["marker"] == "attribution_batch_ingest_ok"
    assert dry_run["dry_run"] is True
    assert dry_run["total_micro_ecu"] == 5817378
    assert not lmdb_path.exists()

    applied = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=lmdb_path,
        rust_binary=attribution_binary,
    )
    assert applied["marker"] == "attribution_batch_ingest_ok"
    assert applied["dry_run"] is False
    assert applied["attribution_count"] == 6
    assert sum(item["amount_micro_ecu"] for item in applied["balances"]) == 5817378
    assert all(item["epoch"] == 574 for item in applied["balances"])

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        apply_attribution_batch_with_rust(
            batch,
            consensus_lmdb=lmdb_path,
            rust_binary=attribution_binary,
        )
    assert excinfo.value.token == "rust_attribution_batch_ingest_failed"
    assert "Invalid epoch reference" in str(excinfo.value)


def test_agent_loop_cli_apply_attribution_batch(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch_path = tmp_path / "consensus_attribution_batch.json"
    batch_path.write_text(
        json.dumps(build_attribution_batch_from_claims(_passing_claim_payload()), sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "tools/agent_loop_v1.py",
            "apply-attribution-batch",
            "--attribution-batch-file",
            str(batch_path),
            "--consensus-lmdb",
            str(tmp_path / "store.lmdb"),
            "--rust-binary",
            str(attribution_binary),
            "--emit-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["marker"] == "attribution_batch_ingest_ok"
    assert (tmp_path / "consensus_attribution_apply_receipt.json").exists()
