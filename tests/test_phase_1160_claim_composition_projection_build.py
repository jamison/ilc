import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/build_genesis_claim_composition_projection.py"
PROJECTION = ROOT / "out/genesis_claim_composition_projection_v0.1.json"


def test_phase_1160_projection_tool_exists() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "build_genesis_claim_composition_projection" in text
    assert "sort_keys=True" in text
    assert "allow_nan=False" in text


def test_phase_1160_projection_schema_and_counts() -> None:
    data = json.loads(PROJECTION.read_text(encoding="utf-8"))
    assert data["artifact"] == "genesis_claim_composition_projection_v0.1"
    assert data["token"] == "sim_spectral_04_claim_composition_projection_built_phase_1160"
    assert data["authority_source_count"] == 32
    assert data["vertex_count"] == 56
    assert data["edge_count"] == 125


def test_phase_1160_every_vertex_has_authority_source_ref() -> None:
    data = json.loads(PROJECTION.read_text(encoding="utf-8"))
    vertices = data["vertices"]
    assert vertices
    assert all(vertex.get("authority_source_ref") for vertex in vertices)


def test_phase_1160_edges_use_allowed_reasons() -> None:
    data = json.loads(PROJECTION.read_text(encoding="utf-8"))
    allowed = set(data["allowed_edge_reasons"])
    assert data["edges"]
    assert {edge["reason"] for edge in data["edges"]}.issubset(allowed)
