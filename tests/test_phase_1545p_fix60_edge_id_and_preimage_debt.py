from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


STATUS_PATH = Path("docs/phases/STATUS.md")
REPORT_PATH = Path("out/genesis_atlas_fix60_edge_id_preimage_debt_report_v0.1.json")
FIX61_SUMMARY_PATH = Path("out/genesis_atlas_fix61_projection_summary_v0.1.json")
LMDB_ROOT = Path("out/genesis_base_graph_v0.4_unified.lmdb")


def _report() -> dict:
    payload = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _canonical_sha256(fields: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            fields,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def test_fix60_complete_token_in_status() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix60_complete" in text
    assert "public_path_remains_blocked_phase_1545p_fix60" in text


def test_fix60_report_exists_and_valid() -> None:
    report = _report()
    assert report["phase"] == "1545p-Fix60"
    assert report["status"] == "PASS"
    assert isinstance(report["lmdb_node_count"], int)
    assert isinstance(report["node_preimage_count_written"], int)


def test_fix60_zero_edges_missing_edge_id() -> None:
    report = _report()
    assert report["edges_missing_edge_id_after"] == 0


def test_fix60_preimage_count_equals_node_count() -> None:
    report = _report()
    assert report["node_preimage_count_written"] == report["lmdb_node_count"]
    assert report["node_preimage_readback_count"] == report["lmdb_node_count"]


def test_fix60_preimage_has_canonical_sha256() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        node_preimages = [
            record
            for record in store.iter_preimages()
            if isinstance(record.get("node_id"), str) and record.get("node_id")
        ]
    finally:
        store.close()
    assert node_preimages
    observed = node_preimages[0]
    digest = observed.get("canonical_sha256")
    assert isinstance(digest, str)
    assert len(digest) == 64
    assert all(char in "0123456789abcdef" for char in digest)


def test_fix60_preimage_sha256_is_correct() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        node_preimages = [
            record
            for record in store.iter_preimages()
            if isinstance(record.get("node_id"), str) and record.get("node_id")
        ]
    finally:
        store.close()
    assert len(node_preimages) >= 5
    for record in node_preimages[:5]:
        fields = record["fields"]
        assert record["canonical_sha256"] == _canonical_sha256(fields)


def test_fix60_lmdb_node_count_not_below_report_and_matches_latest_summary() -> None:
    report = _report()
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        node_count = len(store.iter_nodes())
    finally:
        store.close()
    assert node_count >= report["lmdb_node_count"]
    if FIX61_SUMMARY_PATH.exists():
        summary = json.loads(FIX61_SUMMARY_PATH.read_text(encoding="utf-8"))
        assert node_count == summary["lmdb_node_count_total"]


def test_fix60_evaluator_uses_safe_writer_not_raw_adapter_writes() -> None:
    text = Path("tools/evaluators/sim_genesis_atlas_fix60_edge_id_and_preimage_debt.py").read_text(
        encoding="utf-8"
    )
    assert "AtlasLmdbSafeWriter" in text
    assert ".put_edges(" not in text
    assert ".put_preimages(" not in text
    assert ".put_meta(" not in text
