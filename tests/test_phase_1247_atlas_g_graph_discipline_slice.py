from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc.atlas_graph_discipline import (
    ATLAS_GRAPH_DISCIPLINE_VERSION,
    export_package_profile_reachability_manifest_json,
    package_profile_reachability_manifest,
    validate_graph_delta,
)
from ilc_core.rc.package_profiles import (
    NON_EXCISABLE_COMPONENTS,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
)
import tools.compare_genesis_star_map_to_repo_graph as compiler
from tools.compare_genesis_star_map_to_repo_graph import (
    MAX_OBSERVED_HYPEREDGES,
    MAX_OBSERVED_INCIDENCE,
    MAX_OBSERVED_VERTICES,
    MAX_SCAN_FILE_BYTES,
    MAX_SCAN_FILES,
    MAX_SCAN_LINES_PER_FILE,
    OBSERVED_REPO_HYPERGRAPH_COMPILER_VERSION,
)

ROOT = Path(__file__).resolve().parents[1]
LOCAL_MANIFEST = (
    ROOT / "docs/specs/ilc_package_profile_reachability_manifest_openclaw_skill_local_1247_v0.1.json"
)
CLAIMABLE_MANIFEST = (
    ROOT / "docs/specs/ilc_package_profile_reachability_manifest_openclaw_skill_claimable_1247_v0.1.json"
)


def _write_tiny_star_map_fixture(tmp_path: Path) -> tuple[Path, Path]:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "sample.md").write_text(
        "Genesis theta_hard GENESIS_THETA_HARD hypergraph Phase 1247\n",
        encoding="utf-8",
    )
    star_map = {
        "edges": [
            {
                "edge_id": "edge:tiny",
                "edge_type": "GOVERNS",
                "feature_hints": {"proposed_edge_type": False, "sim_weight_seed": "1"},
                "relation": "tiny_edge",
                "source": "policy:genesis_theta_hard_0_05",
                "target": "truth_primitive:assert.truth",
            }
        ],
        "nodes": [
            {
                "candidate_id": "policy:genesis_theta_hard_0_05",
                "canonicality_tier": "core",
                "category": "policy",
                "evidence": [{"evidence_text": "theta_hard", "source_path": "docs/sample.md"}],
                "inclusion_status": "included",
                "label": "Genesis theta hard",
                "layer": "genesis",
                "node_kind": "policy",
                "symbol": "GENESIS_THETA_HARD",
            },
            {
                "candidate_id": "truth_primitive:assert.truth",
                "canonicality_tier": "core",
                "category": "primitive",
                "evidence": [{"evidence_text": "assert.truth", "source_path": "docs/sample.md"}],
                "inclusion_status": "included",
                "label": "assert.truth",
                "layer": "truth",
                "node_kind": "primitive",
            },
        ],
    }
    crawl = {"nodes": star_map["nodes"]}
    star_map_path = tmp_path / "star_map.json"
    crawl_path = tmp_path / "crawl.json"
    star_map_path.write_text(json.dumps(star_map, allow_nan=False, sort_keys=True), encoding="utf-8")
    crawl_path.write_text(json.dumps(crawl, allow_nan=False, sort_keys=True), encoding="utf-8")
    return star_map_path, crawl_path


def test_phase_1247_graph_delta_validator_accepts_locked_shapes() -> None:
    parsed = validate_graph_delta("graph_delta=none:no load-bearing graph impact")
    assert parsed["kind"] == "none"
    assert parsed["load_bearing"] is False

    support = validate_graph_delta("graph_delta=support_only:docs/phases/example.md")
    assert support["kind"] == "support_only"
    assert support["paths"] == ["docs/phases/example.md"]

    added = validate_graph_delta(
        "graph_delta=load_bearing_artifact_added:docs/specs/manifest.json -> genesis/ilc/ecu/hypergraph"
    )
    assert added["kind"] == "load_bearing_artifact_added"
    assert added["load_bearing"] is True
    assert added["paths"] == ["docs/specs/manifest.json"]
    assert added["anchors"] == ["ecu", "genesis", "hypergraph", "ilc"]


@pytest.mark.parametrize(
    "declaration, token",
    [
        ("none:no prefix", "atlas_graph_delta_missing_prefix"),
        ("graph_delta=unknown:thing", "atlas_graph_delta_unknown_kind"),
        ("graph_delta=load_bearing_artifact_added:docs/specs/x.json", "anchor_required"),
        ("graph_delta=load_bearing_artifact_changed: -> genesis", "path_required"),
        ("graph_delta=support_only:", "payload_required"),
        ("graph_delta=load_bearing_artifact_added:docs/specs/x.json -> moon", "unknown_anchor"),
        ("graph_delta=load_bearing_artifact_added:/tmp/x.json -> genesis", "repo_relative"),
        ("graph_delta=load_bearing_artifact_added:../x.json -> genesis", "repo_relative"),
        ("graph_delta=load_bearing_artifact_added:docs/specs/\nx.json -> genesis", "path_invalid"),
    ],
)
def test_phase_1247_graph_delta_validator_rejects_malformed_inputs(
    declaration: str,
    token: str,
) -> None:
    with pytest.raises(ValueError, match=token):
        validate_graph_delta(declaration)


def test_phase_1247_local_skill_reachability_manifest_preserves_non_excisable_anchors() -> None:
    manifest = package_profile_reachability_manifest(PROFILE_OPENCLAW_SKILL_LOCAL)
    assert manifest["version"] == ATLAS_GRAPH_DISCIPLINE_VERSION
    assert manifest["status"] == "pass"
    assert manifest["package_profile"]["profile_id"] == PROFILE_OPENCLAW_SKILL_LOCAL
    assert manifest["package_profile"]["public_p2p"] is False
    assert manifest["package_profile"]["public_rc_eligible"] is False
    assert manifest["package_profile"]["public_claimability"] is False
    assert set(manifest["non_excisable_components"]) == set(NON_EXCISABLE_COMPONENTS)
    assert set(manifest["reachable_anchor_set"]) == {"ecu", "genesis", "hypergraph", "ilc"}
    assert manifest["missing_required_anchors"] == []
    assert manifest["missing_representative_paths"] == []
    components = {item["component"]: item for item in manifest["component_reachability"]}
    assert all(item["representative_paths_present"] for item in components.values())
    assert components["genesis_lineage_verification"]["non_excisable"] is True
    assert "genesis" in components["genesis_lineage_verification"]["anchors"]
    assert components["ecu_ilc_economic_boundary"]["non_excisable"] is True
    assert {"ecu", "ilc"} <= set(components["ecu_ilc_economic_boundary"]["anchors"])


def test_phase_1247_claimable_skill_reachability_manifest_is_public_rc_target_without_p2p() -> None:
    manifest = package_profile_reachability_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    assert manifest["status"] == "pass"
    assert manifest["package_profile"]["profile_id"] == PROFILE_OPENCLAW_SKILL_CLAIMABLE
    assert manifest["package_profile"]["public_rc_eligible"] is True
    assert manifest["package_profile"]["public_claimability"] is True
    assert manifest["package_profile"]["public_p2p"] is False
    assert manifest["missing_required_anchors"] == []
    assert manifest["missing_representative_paths"] == []
    components = {item["component"]: item for item in manifest["component_reachability"]}
    assert "public_claimability_runtime" in components
    assert {"ecu", "ilc"} <= set(components["public_claimability_runtime"]["anchors"])
    assert "rust_public_p2p_node" not in components


def test_phase_1247_profile_reachability_manifest_json_is_canonical() -> None:
    payload_once = export_package_profile_reachability_manifest_json(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    payload_twice = export_package_profile_reachability_manifest_json(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    assert payload_once == payload_twice
    assert payload_once == json.dumps(
        json.loads(payload_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_phase_1247_committed_reachability_manifests_match_exporters() -> None:
    assert LOCAL_MANIFEST.read_text(encoding="utf-8").strip() == export_package_profile_reachability_manifest_json(
        PROFILE_OPENCLAW_SKILL_LOCAL
    )
    assert CLAIMABLE_MANIFEST.read_text(
        encoding="utf-8"
    ).strip() == export_package_profile_reachability_manifest_json(PROFILE_OPENCLAW_SKILL_CLAIMABLE)


def test_phase_1247_repo_hypergraph_compiler_exports_versioned_bounded_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(compiler, "SCAN_ROOTS", (Path("docs"),))
    star_map_path, crawl_path = _write_tiny_star_map_fixture(tmp_path)
    observed_out = tmp_path / "observed.json"
    gap_out = tmp_path / "gap.json"
    report_out = tmp_path / "gap.md"
    observed, gap = compiler.run(
        star_map_path=star_map_path,
        crawl_path=crawl_path,
        observed_out=observed_out,
        gap_out=gap_out,
        report_out=report_out,
    )

    assert observed["metadata"]["compiler_version"] == OBSERVED_REPO_HYPERGRAPH_COMPILER_VERSION
    assert gap["metadata"]["compiler_version"] == OBSERVED_REPO_HYPERGRAPH_COMPILER_VERSION
    assert observed["metadata"]["limits"] == {
        "max_observed_hyperedges": MAX_OBSERVED_HYPEREDGES,
        "max_observed_incidence": MAX_OBSERVED_INCIDENCE,
        "max_observed_vertices": MAX_OBSERVED_VERTICES,
        "max_scan_file_bytes": MAX_SCAN_FILE_BYTES,
        "max_scan_files": MAX_SCAN_FILES,
        "max_scan_lines_per_file": MAX_SCAN_LINES_PER_FILE,
    }
    assert observed["metadata"]["scan_roots"] == ["docs"]
    assert observed["vertices"]
    assert observed["hyperedges"]
    assert observed["incidence"]
    assert len(observed["vertices"]) <= MAX_OBSERVED_VERTICES
    assert len(observed["hyperedges"]) <= MAX_OBSERVED_HYPEREDGES
    assert len(observed["incidence"]) <= MAX_OBSERVED_INCIDENCE
    assert observed_out.exists()
    assert gap_out.exists()
    assert report_out.exists()


def test_phase_1247_repo_hypergraph_compiler_output_is_deterministic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(compiler, "SCAN_ROOTS", (Path("docs"),))
    star_map_path, crawl_path = _write_tiny_star_map_fixture(tmp_path)
    first = tmp_path / "first"
    compiler.run(
        star_map_path=star_map_path,
        crawl_path=crawl_path,
        observed_out=first / "observed.json",
        gap_out=first / "gap.json",
        report_out=first / "gap.md",
    )
    observed_once = (first / "observed.json").read_text(encoding="utf-8")
    gap_once = (first / "gap.json").read_text(encoding="utf-8")
    compiler.run(
        star_map_path=star_map_path,
        crawl_path=crawl_path,
        observed_out=first / "observed.json",
        gap_out=first / "gap.json",
        report_out=first / "gap.md",
    )
    assert observed_once == (first / "observed.json").read_text(encoding="utf-8")
    assert gap_once == (first / "gap.json").read_text(encoding="utf-8")


def test_phase_1247_repo_hypergraph_compiler_fails_before_hyperedge_overgrowth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(compiler, "SCAN_ROOTS", (Path("docs"),))
    monkeypatch.setattr(compiler, "MAX_OBSERVED_HYPEREDGES", 1)
    star_map_path, crawl_path = _write_tiny_star_map_fixture(tmp_path)

    with pytest.raises(ValueError, match="observed_repo_hypergraph_hyperedge_limit_exceeded"):
        compiler.run(
            star_map_path=star_map_path,
            crawl_path=crawl_path,
            observed_out=tmp_path / "observed.json",
            gap_out=tmp_path / "gap.json",
            report_out=tmp_path / "gap.md",
        )
