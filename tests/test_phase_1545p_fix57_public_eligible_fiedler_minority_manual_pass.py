import hashlib
import json
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
REPORT = ROOT / "out/genesis_atlas_fix57_manual_bridge_edge_application_report_v0.1.json"
LMDB_ROOT = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"

ALLOWED_EDGE_TYPES = {
    "DERIVED_FROM",
    "GENERATED_BY",
    "EVIDENCES",
    "CLASSIFIED_BY",
    "SOURCE_TREE_MEMBER",
    "TESTS",
    "IMPLEMENTS",
    "REFERENCES_AUTHORITY",
    "CARRIES_FORWARD",
}


def _report() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def _lmdb_edges_by_id() -> dict[str, dict]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        return {
            str(edge["edge_id"]): edge
            for edge in store.iter_edges()
            if isinstance(edge.get("edge_id"), str)
        }
    finally:
        store.close()


def test_fix57_complete_token_in_status() -> None:
    text = STATUS.read_text(encoding="utf-8")
    assert "fix57_complete" in text
    assert "public_path_remains_blocked_phase_1545p_fix57" in text


def test_fix57_report_exists_and_valid() -> None:
    data = _report()
    assert data["status"] == "PASS"
    assert "edge_application" in data
    assert "lmdb_edge_counts" in data
    assert "fiedler" in data
    assert data["ledger_entry_counts"]["full_non_out_pass_status"] == "deep_manual_confirmation_complete"


def test_fix57_new_edges_are_bridge_types_only() -> None:
    data = _report()
    for edge in data["new_edges"]:
        assert edge["edge_type"] in ALLOWED_EDGE_TYPES
        assert edge["edge_type"] != "GOVERNS"


def test_fix57_new_edges_have_manual_reviewed_annotation() -> None:
    data = _report()
    edges_by_id = _lmdb_edges_by_id()
    for edge in data["new_edges"]:
        lmdb_edge = edges_by_id[edge["edge_id"]]
        assert lmdb_edge["annotation_method"] == "manual_reviewed"
        assert lmdb_edge["annotation_phase"] == "phase_1545p_fix57"
        assert lmdb_edge["annotation_reviewer"] == "human"
        assert lmdb_edge.get("source_annotation_method")


def test_fix57_new_edges_have_deterministic_edge_ids() -> None:
    data = _report()
    for edge in data["new_edges"]:
        expected = "edge:" + hashlib.sha256(
            f"{edge['src']}|{edge['edge_type']}|{edge['tgt']}".encode()
        ).hexdigest()[:16]
        assert edge["edge_id"] == expected


def test_fix57_no_duplicate_edge_ids() -> None:
    data = _report()
    edge_ids = [edge["edge_id"] for edge in data["new_edges"]]
    assert len(edge_ids) == len(set(edge_ids))


def test_fix57_lmdb_edge_count_increased() -> None:
    data = _report()
    counts = data["lmdb_edge_counts"]
    assert counts["post_application"] == counts["pre_application"] + counts["delta"]
    if data["edge_application"]["validated_and_applied"] > 0:
        assert counts["post_application"] > counts["pre_application"]
    else:
        assert counts["post_application"] == counts["pre_application"]


def test_fix57_post_application_fiedler_reported() -> None:
    data = _report()
    assert isinstance(data["fiedler"]["post_application_lambda2"], float)
    assert data["fiedler"]["post_application_lambda2"] > 0.0
