from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix44_g10_starmap_signing_packet.md"
CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
LMDB_REEXPORT = ROOT / "out/genesis_base_graph_v0.4_lmdb_reexport.json"
LMDB_DIGEST = ROOT / "out/genesis_base_graph_v0.4_lmdb_digest.json"
STAR_MAP = ROOT / "out/genesis_base_graph_v0.4_star_map_index.json"
PREIMAGES = ROOT / "out/genesis_base_graph_v0.4_node_preimages.jsonl"
SIGNING_PACKET = ROOT / "docs/specs/ilc_genesis_base_graph_v04_signing_packet.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix44_starmap_signing_packet_walkthrough.md"
QUEUE = ROOT / "out/genesis_base_graph_fix44_target_queue.json"
STATUS = ROOT / "docs/phases/STATUS.md"
BUILDER = ROOT / "tools/evaluators/sim_genesis_base_graph_starmap_preimages_1545p_fix44.py"
EXPECTED_FIX41A_SHA256 = "3bcf8cdf248ea44248e72dce0c8209c92302826399b42524235cf8ee59936e52"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_sha(path: Path) -> str:
    payload = _load(path)
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _preimage_rows() -> list[dict]:
    return [json.loads(line) for line in PREIMAGES.read_text(encoding="utf-8").splitlines() if line]


def test_fix44_prompt_uses_fix41a_and_fix43_dependency() -> None:
    text = PROMPT.read_text(encoding="utf-8")
    assert "genesis_atlas_enriched_candidate_fix41a.json" in text
    assert "| `fix43_complete` |" in text
    assert "| `fix44_complete` | this phase |" in text
    assert "Do NOT use `genesis_atlas_enriched_candidate_fix40.json`" in text
    assert "does NOT consume the Fix43 target queue" in text


def test_candidate_lmdb_digest_equivalence() -> None:
    digest = _load(LMDB_DIGEST)
    assert _file_sha(CANDIDATE) == EXPECTED_FIX41A_SHA256
    assert _canonical_sha(CANDIDATE) == EXPECTED_FIX41A_SHA256
    assert _canonical_sha(LMDB_REEXPORT) == EXPECTED_FIX41A_SHA256
    assert digest["digests"]["source_file_sha256"] == EXPECTED_FIX41A_SHA256
    assert digest["digests"]["reexport_canonical_sha256"] == EXPECTED_FIX41A_SHA256
    assert all(digest["round_trip"].values())


def test_preimages_cover_every_candidate_node_once() -> None:
    candidate = _load(CANDIDATE)
    candidate_node_ids = {node["candidate_id"] for node in candidate["nodes"]}
    rows = _preimage_rows()
    preimage_node_ids = [row["node_id"] for row in rows]
    assert len(rows) == len(candidate["nodes"]) == 15676
    assert len(set(preimage_node_ids)) == len(preimage_node_ids)
    assert set(preimage_node_ids) == candidate_node_ids
    assert all(row["cid"] == "pending_float_free_dag_cbor_preimage_contract" for row in rows)
    assert all(row["preimage_encoding"] == "canonical_json_utf8" for row in rows)
    assert all(len(row["preimage_sha256"]) == 64 for row in rows)


def test_star_map_index_is_derived_and_has_no_phantom_nodes() -> None:
    candidate = _load(CANDIDATE)
    star_map = _load(STAR_MAP)
    candidate_node_ids = {node["candidate_id"] for node in candidate["nodes"]}
    assert star_map["artifact_class"] == "star_map_index"
    assert star_map["is_authority_bearing"] is False
    assert star_map["derived_from"] == "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
    assert star_map["node_count"] == len(candidate["nodes"]) == 15676
    assert star_map["edge_count"] == len(candidate["edges"]) == 75279
    assert len(star_map["index"]["by_tier"]["canonical"]) == 54
    assert len(star_map["index"]["by_tier"]["private"]) == 861
    assert len(star_map["index"]["by_tier"]["support"]) == 14761
    indexed_nodes: set[str] = set()
    for mapping_name in ("by_node_type", "by_exact_tier", "by_annotation_method"):
        for values in star_map["index"][mapping_name].values():
            indexed_nodes.update(values)
    for values in star_map["index"]["by_tier"].values():
        indexed_nodes.update(values)
    indexed_nodes.update(star_map["index"]["authority_spine_nodes"])
    assert indexed_nodes <= candidate_node_ids


def test_signing_packet_and_walkthrough_preserve_non_claims_and_counts() -> None:
    packet = SIGNING_PACKET.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    assert "UNSIGNED CANDIDATE SIGNING PACKET" in packet
    assert "does not sign any artifact" in " ".join(packet.split())
    assert "Core star-map nodes | `57`" in packet
    assert "Nodes | `15676`" in packet
    assert "CID pending rows | `15676`" in packet
    assert "entry_count=500" in packet
    assert "is_authority_bearing=false" in walkthrough
    assert "Fix43 carry-forward queue" in walkthrough
    assert "No Genesis signing occurred." in walkthrough


def test_fix44_queue_and_status_tokens_are_present() -> None:
    queue = _load(QUEUE)
    status = STATUS.read_text(encoding="utf-8")
    assert queue["entry_count"] == 500
    for token in (
        "fix44_star_map_index_produced",
        "fix44_node_preimages_produced",
        "fix44_signing_packet_committed",
        "fix44_digest_equivalence_tests_passing",
        "fix44_complete",
        "genesis_base_graph_v04_candidate_pipeline_complete",
        "public_path_remains_blocked_phase_1545p_fix44",
    ):
        assert token in status


def test_fix44_builder_uses_atomic_canonical_writes_and_public_rc_exclude() -> None:
    text = BUILDER.read_text(encoding="utf-8")
    assert "PUBLIC_RC_EXCLUDE: genesis_base_graph_starmap_preimages_fix44_research_only" in text
    assert "tempfile.mkstemp" in text
    assert "os.replace" in text
    assert "sort_keys=True" in text
    assert "allow_nan=False" in text
