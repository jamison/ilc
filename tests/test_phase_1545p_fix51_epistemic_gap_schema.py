import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "phases" / "STATUS.md"
SCHEMA = ROOT / "docs" / "specs" / "ilc_epistemic_gap_node_schema_v0.1.json"
VALIDATOR = ROOT / "tools" / "validate_epistemic_gap_nodes.py"
BASE = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix50.json"
FIX51 = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix51.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _gap_nodes() -> list[dict]:
    return [
        node
        for node in _load(FIX51)["nodes"]
        if node.get("node_kind") == "epistemic_gap"
    ]


def test_fix51_status_token_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    assert "fix51_epistemic_gap_schema_defined" in status
    assert "fix51_complete" in status
    assert "public_path_remains_blocked_phase_1545p_fix51" in status


def test_fix51_schema_exists_and_locks_kgc_score_as_string() -> None:
    schema = _load(SCHEMA)
    score_schema = schema["properties"]["candidate_targets"]["items"]["properties"]["kgc_score"]
    assert score_schema["type"] == "string"
    assert "pattern" in score_schema


def test_fix51_validator_passes_on_candidate() -> None:
    result = subprocess.run(
        ["python3", str(VALIDATOR), str(FIX51)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "VALID:" in result.stdout


def test_fix51_candidate_contains_valid_seed_gap_node() -> None:
    gaps = _gap_nodes()
    assert len(gaps) >= 1
    for gap in gaps:
        assert gap["candidate_id"].startswith("gap:")
        assert gap["gap_id"].startswith("gap:")
        assert gap["status"] in {"open", "resolved", "expired_unresolved", "deferred"}
        assert gap["authority_boundary"] == "not_authority_promotion"
        assert gap["authority_effect"] == "none_until_resolved"
        assert gap["signing_posture"] == "not_atlas_signing_ready"
        assert gap["candidate_status"] == "fix51_support_only_not_canonical"
        assert gap["signature_status"] == "unsigned_candidate_preimage"
        assert gap["candidate_targets"] == []
        assert gap["projection_policy"] == {
            "authority_projection": "excluded",
            "frontier_projection": "included",
            "research_projection": "included",
        }


def test_fix51_gap_nodes_have_inbound_expects_resolution_and_no_governs_contact() -> None:
    candidate = _load(FIX51)
    node_ids = {node["candidate_id"] for node in candidate["nodes"] if "candidate_id" in node}
    gap_ids = {gap["candidate_id"] for gap in _gap_nodes()}
    inbound = {gap_id: 0 for gap_id in gap_ids}

    for edge in candidate["edges"]:
        if edge.get("edge_type") == "GOVERNS":
            assert edge.get("source") not in gap_ids
            assert edge.get("target") not in gap_ids
        if edge.get("edge_type") == "EXPECTS_RESOLUTION" and edge.get("target") in gap_ids:
            assert edge["source"] in node_ids
            assert edge["source"] not in gap_ids
            expected = "edge:" + hashlib.sha256(
                f"{edge['source']}|{edge['edge_type']}|{edge['target']}".encode("utf-8")
            ).hexdigest()[:16]
            assert edge["edge_id"] == expected
            inbound[edge["target"]] += 1

    assert inbound
    assert all(count >= 1 for count in inbound.values())


def test_fix51_preserves_fix50_content_and_adds_only_minimal_seed() -> None:
    base = _load(BASE)
    fix51 = _load(FIX51)
    report = fix51["fix51_generation_report"]
    assert len(fix51["nodes"]) == len(base["nodes"]) + report["seed_gap_nodes_added"]
    assert len(fix51["edges"]) == len(base["edges"]) + report["expects_resolution_edges_added"]
    assert report["seed_gap_nodes_added"] == 1
    assert report["expects_resolution_edges_added"] == 1


def test_fix51_does_not_recreate_fix38_source_tree_hub_edges() -> None:
    hub = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
    fix51_edges = [
        edge
        for edge in _load(FIX51)["edges"]
        if edge.get("annotation_phase") == "phase_1545p_fix51"
    ]
    for edge in fix51_edges:
        assert not (
            edge["edge_type"] == "SOURCE_TREE_MEMBER"
            and (edge["source"] == hub or edge["target"] == hub)
        )
