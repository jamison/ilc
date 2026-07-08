import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V03 = ROOT / "out/genesis_core_star_map_v0.3_candidate.json"
V04 = ROOT / "out/genesis_core_star_map_v0.4_candidate.json"
QUEUE = ROOT / "out/genesis_common_registry_node_candidates_1545p_fix7.json"
SIM_JSON = ROOT / "out/sim_genesis_01_v04_candidate_assembly_1545p_fix18.json"
SIM_REPORT = ROOT / "docs/sims/sim_genesis_01_v04_candidate_assembly_1545p_fix18_v0.1.md"
DIAG_JSON = ROOT / "out/genesis_compile_coverage_diagnostic_v0.4_candidate.json"
DIAG_REPORT = ROOT / "docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.4_candidate.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix18_sim_genesis_01_v04_candidate_assembly_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


SELECTED = {
    "adr:0009_protocol_native_bundle_distribution",
    "adr:0035_type_definition_authority",
    "cdl:096_werner_global_tier_authority",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v04_candidate_is_assembled_from_exact_must_include_set() -> None:
    v03 = read_json(V03)
    v04 = read_json(V04)
    queue = read_json(QUEUE)

    assert len(v03["nodes"]) == 54
    assert len(v03["edges"]) == 77
    assert len(v04["nodes"]) == 57
    assert len(v04["edges"]) == 80

    v04_ids = {node["candidate_id"] for node in v04["nodes"]}
    assert SELECTED <= v04_ids

    deferred_ids = {
        candidate["candidate_id"]
        for candidate in queue["candidates"]
        if candidate["classification"] != "must_include_genesis_node"
    }
    assert not (deferred_ids & SELECTED)
    assert not (deferred_ids & (v04_ids - {node["candidate_id"] for node in v03["nodes"]}))


def test_v04_candidate_is_unsigned_support_only_and_endpoint_valid() -> None:
    v04 = read_json(V04)
    node_ids = {node["candidate_id"] for node in v04["nodes"]}

    assert v04["metadata"]["signature_status"] == "unsigned_support_only"
    assert v04["metadata"]["successor_candidate_status"] == "support_only_not_canonical"
    assert v04["metadata"]["public_path"] == "blocked"

    for node in v04["nodes"]:
        if node["candidate_id"] in SELECTED:
            assert node["authority_status"] == "successor_candidate_support_only"
            assert node["signature_status"] == "unsigned_support_only"
            assert node["promotion_path"] == "successor_manifest_candidate_requires_block6_signing"

    for edge in v04["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids


def test_sim_json_and_report_record_scientific_findings_and_non_claims() -> None:
    payload = read_json(SIM_JSON)
    report = read(SIM_REPORT)

    assert payload["sim_id"] == "SIM-GENESIS-01"
    assert payload["canonicality"] == "unsigned_not_canonical"
    assert payload["metrics"]["assembly"]["selected_candidate_count"] == 3
    assert payload["metrics"]["assembly"]["deferred_candidate_count"] == 25
    assert payload["metrics"]["edge_endpoint_validity"]["invalid_endpoint_count"] == 0
    assert payload["metrics"]["basis_reachability"]["basis_reachable_ratio"] == "57/57"
    assert payload["metrics"]["authority_traceability"]["authority_traceable_ratio"] == "56/57"

    for token in [
        "sim_genesis_01_v04_candidate_assembly_committed_phase_1545p_fix18",
        "genesis_v04_candidate_assembled_phase_1545p_fix18",
        "genesis_v04_candidate_unsigned_support_only_phase_1545p_fix18",
        "fix7_must_include_candidates_consumed_phase_1545p_fix18",
        "public_path_remains_blocked_phase_1545p_fix18",
    ]:
        assert token in payload["tokens"]
        assert token in report

    for phrase in [
        "support-only and not canonical",
        "does not mutate the signed v0.3 baseline",
        "does not sign a successor manifest",
        "does not activate public RC",
        "Canonical successor-manifest authority remains gated by Block 6",
    ]:
        assert phrase in report


def test_existing_compile_diagnostic_runs_against_v04_candidate() -> None:
    diagnostic = read_json(DIAG_JSON)
    report = read(DIAG_REPORT)

    assert diagnostic["verdict"] == "GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL"
    assert diagnostic["compile_coverage"]["core_nodes_total"] == 57
    assert diagnostic["compile_coverage"]["basis_reachable_core_nodes"] == 57
    assert diagnostic["authority_traceability"]["authority_traceable_core_nodes"] == 56
    assert diagnostic["compile_coverage"]["core_explainable_sources"] == 801
    assert "Core nodes: `57`" in report


def test_frontier_records_fix18_without_claiming_public_activation() -> None:
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)
    planning = read(PLANNING)

    assert "Phase 1545p-Fix18" in status
    assert "Phase 1545p-Fix18" in planning
    # HISTORICAL_SNAPSHOT: exact current-marker cardinality is not a live invariant.
    assert planning.count("⬅ CURRENT") >= 1
    fix18_line = planning.split("Phase 1545p-Fix18", 1)[1].splitlines()[0]
    assert (
        "⬅ CURRENT" in fix18_line
        or "COMPLETE" in fix18_line
        or "Superseded as current frontier" in fix18_line
    )

    for phrase in [
        "No signed successor manifest",
        "No canonical Genesis mutation",
        "No public RC activation",
        "No runtime activation",
        "No economic activation",
        "No sidecar activation",
    ]:
        assert phrase in walkthrough
