import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
CORE_PATH = REPO_ROOT / "out/genesis_core_star_map_v0.4.json"
AUTHORITY_PATH = REPO_ROOT / "out/genesis_authority_projection_v0.4.json"
BASE_PATH = REPO_ROOT / "out/genesis_base_graph_v0.4.json"
INDEX_PATH = REPO_ROOT / "out/genesis_core_star_map_index_v0.4.json"
SUMMARY_PATH = REPO_ROOT / "out/genesis_atlas_fix61_projection_summary_v0.1.json"


def _load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _node_ids(payload: dict) -> set[str]:
    return {node["candidate_id"] for node in payload["nodes"]}


def _projection_values(payload: dict) -> set[str]:
    return {str(node.get("graph_projection", "")) for node in payload["nodes"]}


def test_fix61_complete_token_in_status():
    assert "fix61_complete" in STATUS_PATH.read_text(encoding="utf-8")


def test_fix61_core_star_map_json_exists_and_valid():
    payload = _load(CORE_PATH)
    assert set(("nodes", "edges")).issubset(payload)
    assert payload["metadata"]["projection"] == "curated_signing_core"
    assert payload["metadata"]["node_count"] == 57


def test_fix61_authority_projection_json_exists_and_valid():
    payload = _load(AUTHORITY_PATH)
    assert set(("nodes", "edges")).issubset(payload)
    assert payload["metadata"]["projection"] == "authority_projection"


def test_fix61_base_graph_json_exists_and_valid():
    payload = _load(BASE_PATH)
    assert set(("nodes", "edges")).issubset(payload)
    assert payload["metadata"]["projection"] == "public_eligible_base_graph"


def test_fix61_no_private_nodes_in_core_star_map():
    values = _projection_values(_load(CORE_PATH))
    assert "excluded_private_material" not in values
    assert "review_required" not in values


def test_fix61_no_private_nodes_in_authority_projection():
    values = _projection_values(_load(AUTHORITY_PATH))
    assert "excluded_private_material" not in values
    assert "review_required" not in values


def test_fix61_no_private_nodes_in_base_graph():
    values = _projection_values(_load(BASE_PATH))
    assert "excluded_private_material" not in values
    assert "review_required" not in values


def test_fix61_exports_are_subsets_of_base_graph():
    base_ids = _node_ids(_load(BASE_PATH))
    assert _node_ids(_load(CORE_PATH)).issubset(base_ids)
    assert _node_ids(_load(AUTHORITY_PATH)).issubset(base_ids)


def test_fix61_star_map_index_has_authority_coverage_fields():
    payload = _load(INDEX_PATH)
    coverage = payload["authority_coverage"]
    assert "invariant_coverage_fraction" in coverage
    assert "policy_coverage_fraction" in coverage


def test_fix61_projection_summary_has_all_projections():
    payload = _load(SUMMARY_PATH)
    projections = payload["projections"]
    assert "curated_signing_core" in projections
    assert "authority_projection" in projections
    assert "public_eligible_base_graph" in projections
    assert "full_local" in projections


def test_fix61_lmdb_preimage_count_matches_live_graph():
    payload = _load(SUMMARY_PATH)
    assert payload["lmdb_preimage_count_total"] == (
        payload["lmdb_node_count_total"] + payload["lmdb_edge_count_total"]
    )
