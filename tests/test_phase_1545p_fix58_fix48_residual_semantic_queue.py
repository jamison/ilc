from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES


REPORT_PATH = Path("out/genesis_atlas_fix58_residual_queue_application_report_v0.1.json")
STATUS_PATH = Path("docs/phases/STATUS.md")
LMDB_ROOT = Path("out/genesis_base_graph_v0.4_unified.lmdb")


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def _edge_id(source: str, edge_type: str, target: str) -> str:
    digest = hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]
    return f"edge:{digest}"


def _fix58_edges_by_id() -> dict[str, dict]:
    store = GenesisAtlasCandidateStore(
        LMDB_ROOT,
        allow_synthetic_edge_keys=True,
        map_size=DEFAULT_MAP_SIZE_BYTES * 4,
    )
    try:
        return {
            edge["edge_id"]: edge
            for edge in store.iter_edges()
            if edge.get("annotation_phase") == "phase_1545p_fix58"
        }
    finally:
        store.close()


def test_fix58_complete_token_in_status() -> None:
    assert "fix58_complete" in STATUS_PATH.read_text(encoding="utf-8")


def test_fix58_report_exists_and_valid() -> None:
    report = _report()
    assert report["status"] == "PASS"
    assert report["total_queue_entries"] == 101
    assert set(report["dispositions"]) == {"add_edge", "support_only", "defer"}


def test_fix58_new_edges_have_manual_reviewed_annotation() -> None:
    report = _report()
    edges_by_id = _fix58_edges_by_id()
    assert set(report["new_edge_ids"]) <= set(edges_by_id)
    for edge_id in report["new_edge_ids"]:
        assert edges_by_id[edge_id]["annotation_method"] == "manual_reviewed"
        assert edges_by_id[edge_id]["annotation_phase"] == "phase_1545p_fix58"


def test_fix58_new_edges_have_deterministic_edge_ids() -> None:
    edges_by_id = _fix58_edges_by_id()
    for edge in edges_by_id.values():
        assert edge["edge_id"] == _edge_id(edge["src"], edge["edge_type"], edge["tgt"])


def test_fix58_no_governs_edges_added() -> None:
    edges_by_id = _fix58_edges_by_id()
    assert edges_by_id
    assert all(edge["edge_type"] != "GOVERNS" for edge in edges_by_id.values())


def test_fix58_lmdb_edge_count_nondecreasing() -> None:
    report = _report()
    assert report["edge_count_nondecreasing"] is True
    assert report["post_application_edge_count"] >= report["pre_application_edge_count"]
    assert (
        report["post_application_edge_count"] - report["pre_application_edge_count"]
        == report["new_edges_applied"]
    )


def test_fix58_residual_queue_fully_dispositioned() -> None:
    report = _report()
    dispositions = report["dispositions"]
    assert dispositions["add_edge"] + dispositions["support_only"] + dispositions["defer"] == 101
    assert report["new_edges_attempted"] == 118
    assert report["new_edges_applied"] + len(report["missing_target_rejections"]) == 118
