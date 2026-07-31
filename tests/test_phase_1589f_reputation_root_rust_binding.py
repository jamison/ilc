from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    apply_attribution_batch_with_rust,
    build_attribution_batch_from_claims,
)


ROOT = Path(__file__).resolve().parents[1]
AGENT_A = "a" * 96
AGENT_ROOT = "cd" * 32


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


def _claim_payload(epoch: int = 19) -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": AGENT_A,
                "amount": "1",
                "claim_id": "claim-reputation-root",
                "epoch": epoch,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def test_bridge_emits_reputation_root_when_present() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        agent_reputation_root=AGENT_ROOT,
    )

    assert batch["agent_reputation_root"] == AGENT_ROOT
    assert re.fullmatch(r"[0-9a-f]{64}", batch["agent_reputation_root"])


def test_bridge_emits_none_when_reputation_absent() -> None:
    batch = build_attribution_batch_from_claims(_claim_payload())

    assert "agent_reputation_root" not in batch


def test_bridge_rejects_malformed_reputation_root_before_rust() -> None:
    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            agent_reputation_root="0" * 63,
        )

    assert excinfo.value.token == "agent_reputation_root_must_be_64_lower_hex"

    with pytest.raises(AttributionBatchBridgeError) as uppercase_excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            agent_reputation_root=AGENT_ROOT.upper(),
        )

    assert uppercase_excinfo.value.token == "agent_reputation_root_must_be_64_lower_hex"


def test_rust_ingestion_accepts_batch_with_reputation_root(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        agent_reputation_root=AGENT_ROOT,
    )

    report = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=tmp_path / "store.lmdb",
        rust_binary=attribution_binary,
        dry_run=True,
    )

    assert report["marker"] == "attribution_batch_ingest_ok"
    assert report["dry_run"] is True
    assert report["agent_reputation_root"] == AGENT_ROOT


def test_rust_ingestion_accepts_batch_without_reputation_root(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    report = apply_attribution_batch_with_rust(
        build_attribution_batch_from_claims(_claim_payload()),
        consensus_lmdb=tmp_path / "store.lmdb",
        rust_binary=attribution_binary,
        dry_run=True,
    )

    assert report["marker"] == "attribution_batch_ingest_ok"
    assert report["agent_reputation_root"] is None


def test_rust_ingestion_rejects_malformed_reputation_root(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = build_attribution_batch_from_claims(_claim_payload())
    batch["agent_reputation_root"] = "x" * 64

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        apply_attribution_batch_with_rust(
            batch,
            consensus_lmdb=tmp_path / "store.lmdb",
            rust_binary=attribution_binary,
            dry_run=True,
        )

    assert excinfo.value.token == "rust_attribution_batch_ingest_failed"
    assert "agent_reputation_root_must_be_64_hex" in str(excinfo.value)


def test_epoch_settlement_record_schema_not_modified_for_reputation_root() -> None:
    source = (ROOT / "ilc_consensus" / "src" / "types.rs").read_text(encoding="utf-8")
    settlement_match = re.search(
        r"struct EpochSettlementRecord \{(?P<body>.*?)\n\}",
        source,
        flags=re.DOTALL,
    )
    attribution_match = re.search(
        r"struct AttributionBatch \{(?P<body>.*?)\n\}",
        source,
        flags=re.DOTALL,
    )

    assert settlement_match is not None
    assert attribution_match is not None
    assert "agent_reputation_root" not in settlement_match.group("body")
    assert "agent_reputation_root: Option<[u8; 32]>" in attribution_match.group("body")


def test_rust_ingest_report_json_contains_reputation_root_key(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(epoch=20),
        agent_reputation_root=AGENT_ROOT,
    )
    batch_path = tmp_path / "batch.json"
    batch_path.write_text(json.dumps(batch, sort_keys=True) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            str(attribution_binary),
            "--input-file",
            str(batch_path),
            "--lmdb",
            str(tmp_path / "store.lmdb"),
            "--dry-run",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["agent_reputation_root"] == AGENT_ROOT
