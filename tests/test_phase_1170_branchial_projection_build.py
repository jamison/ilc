"""Phase 1170 — SIM-SPECTRAL-05 Track B branchial projection build."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECTION_PATH = ROOT / "out/genesis_branchial_claim_projection_v0.1.json"
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
ALLOWED_OPS = {"compose", "refute", "amend", "succeed"}


def _json(path: pathlib.Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_branchial_projection_exists_and_is_valid_json() -> None:
    assert PROJECTION_PATH.exists()
    projection = _json(PROJECTION_PATH)
    assert isinstance(projection, dict)
    assert projection["projection_type"] == "branchial_claim_state"
    assert projection["phase"] == 1170
    assert projection["token"] == "sim_spectral_05_track_b_projection_built_phase_1170"


def test_branchial_vertices_have_required_schema_fields() -> None:
    projection = _json(PROJECTION_PATH)
    assert isinstance(projection, dict)
    vertices = projection["vertices"]
    assert len(vertices) >= 80
    for vertex in vertices:
        assert "derivation_state_type" in vertex
        assert "genesis_anchor" in vertex
        assert "claim_id" in vertex
        assert "version" in vertex
        assert "status" in vertex


def test_branchial_edges_have_allowed_operation_types() -> None:
    projection = _json(PROJECTION_PATH)
    assert isinstance(projection, dict)
    edges = projection["edges"]
    assert len(edges) >= 180
    observed = {edge["operation_type"] for edge in edges}
    assert observed == ALLOWED_OPS


def test_branchial_projection_is_byte_deterministic() -> None:
    before = _sha256(PROJECTION_PATH)
    subprocess.run(
        [sys.executable, "tools/build_genesis_branchial_claim_projection.py"],
        cwd=ROOT,
        check=True,
    )
    after = _sha256(PROJECTION_PATH)
    assert before == after


def test_signed_v01_star_map_unchanged() -> None:
    star_map = _json(ROOT / "out/genesis_core_star_map_v0.1.json")
    envelope = _json(ROOT / "out/genesis_signing_root_envelope_v0.1.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH


def test_branchial_metadata_records_sybil_template_and_adr_0037_criterion() -> None:
    projection = _json(PROJECTION_PATH)
    assert isinstance(projection, dict)
    metadata = projection["metadata"]
    assert metadata["provenance_equivalence_criterion"] == "ADR-0037 §3.2"
    assert metadata["sybil_branchial_template"]["topology_label"] == "sybil_cluster_branchial"
