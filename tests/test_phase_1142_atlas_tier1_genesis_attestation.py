import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "specs" / "ilc_genesis_intent_attestation_and_init_authority_map_v0.1.md"
SEED = ROOT / "docs" / "sims" / "sim_spectral_02" / "genesis_core_star_map_curated_seed_v0.1.json"
STAR_MAP = ROOT / "out" / "genesis_core_star_map_v0.1.json"
DIAGNOSTIC = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.1.json"
CRAWLER = ROOT / "tools" / "crawl_genesis_node_candidates.py"


ATTESTATION_NODE = "artifact:genesis_intent_attestation_init_authority_map"
GENESIS_AGENT = "genesis_agent:01"
SIGNING_KEY = "artifact:genesis_agent1_pubkey_record_838a"


def _json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_t1_attestation_spec_exists_with_ex_post_facto_token() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert "genesis_intent_attestation_committed_phase_1142" in text
    assert "attestation_type: ex_post_facto" in text
    assert "signature_status: pending_human_signature" in text


def test_t2_curated_seed_contains_attestation_node_edges_and_overrides() -> None:
    seed = _json(SEED)
    node_ids = {node["candidate_id"] for node in seed["nodes"]}
    assert ATTESTATION_NODE in node_ids
    assert len(seed["edges"]) >= 27
    assert len(seed["genesis_attested_overrides"]) == 31
    assert all(override["signing_key_ref"] == SIGNING_KEY for override in seed["genesis_attested_overrides"])


def test_t3_star_map_regenerated_to_32_nodes() -> None:
    star_map = _json(STAR_MAP)
    assert len(star_map["nodes"]) == 32
    assert any(node["candidate_id"] == ATTESTATION_NODE for node in star_map["nodes"])


def test_t4_all_star_map_nodes_are_genesis_attested_with_signing_metadata() -> None:
    star_map = _json(STAR_MAP)
    for node in star_map["nodes"]:
        assert node["genesis_attested"] is True, node["candidate_id"]
        assert node["genesis_attested_by"] == GENESIS_AGENT, node["candidate_id"]
        assert node["signing_key_ref"] == SIGNING_KEY, node["candidate_id"]
        assert node["signature_status"] in {
            "pending_human_signature",
            "signed",
        }, node["candidate_id"]


def test_t5_diagnostic_contains_authority_traceability_gate() -> None:
    diagnostic = _json(DIAGNOSTIC)
    authority = diagnostic["authority_traceability"]
    assert authority["attestation_root"] == ATTESTATION_NODE
    assert authority["authority_traceable_core_nodes"] >= 28
    assert authority["authority_traceable_core_nodes_ratio"] == "0.968750"


def test_t6_proposed_governs_edges_have_decomposition_recipes() -> None:
    diagnostic = _json(DIAGNOSTIC)
    assert diagnostic["edge_recipe_analysis"]["missing_decomposition_recipe_count"] == 0


def test_t7_crawler_compiles_curated_authority_metadata_and_fails_stale_refs() -> None:
    text = CRAWLER.read_text(encoding="utf-8")
    assert "crawler is not the authority source for Genesis attestation" in text
    assert "genesis_attested_override_unknown_candidate" in text
