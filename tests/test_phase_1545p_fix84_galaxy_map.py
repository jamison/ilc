"""Tests for Fix84 galaxy map — cuneiform star sprites, multi-repo meta-view.

Phase: 1545p-Fix84
"""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_galaxy_manifest_schema_valid():
    schema = json.loads((REPO / "tools/galaxy_manifest_schema.json").read_text())
    assert "galaxies" in str(schema)  # schema references galaxies
    # Verify it's a proper JSON Schema
    assert schema.get("type") == "object"
    assert "properties" in schema
    assert "galaxies" in schema["properties"]


def test_default_manifest_valid():
    m = json.loads((REPO / "tools/galaxy_manifest_default.json").read_text())
    assert "galaxies" in m
    assert len(m["galaxies"]) == 3
    ids = {g["id"] for g in m["galaxies"]}
    assert "ilc_core" in ids
    for g in m["galaxies"]:
        for field in ("id", "label", "signing_state", "depends_on", "color"):
            assert field in g, f"Missing field '{field}' in galaxy {g.get('id')}"


def test_cuneiform_star_svg_is_valid_svg():
    sys.path.insert(0, str(REPO / "ilc-graphics-sidecar"))
    from ilc_graph_viz.__main__ import _cuneiform_star_svg
    uri = _cuneiform_star_svg("#ffcc00", 64)
    assert uri.startswith("data:image/svg+xml;base64,")
    svg_bytes = base64.b64decode(uri.split(",", 1)[1])
    svg_text = svg_bytes.decode("utf-8")
    assert "<svg" in svg_text
    assert "polygon" in svg_text or "path" in svg_text
    # Should have 8 wedges
    assert svg_text.count("<polygon") == 8
    # Should have the center dot
    assert "<circle" in svg_text


def test_galaxy_html_mode_runs(tmp_path):
    sys.path.insert(0, str(REPO / "ilc-graphics-sidecar"))
    from ilc_graph_viz.__main__ import main
    out = tmp_path / "galaxy.html"
    manifest = REPO / "tools/galaxy_manifest_default.json"
    rc = main(["--galaxy", str(manifest), "--output", str(out)])
    assert rc == 0
    assert out.exists()


def test_galaxy_html_contains_forcegraph(tmp_path):
    sys.path.insert(0, str(REPO / "ilc-graphics-sidecar"))
    from ilc_graph_viz.__main__ import main
    out = tmp_path / "galaxy.html"
    manifest = REPO / "tools/galaxy_manifest_default.json"
    main(["--galaxy", str(manifest), "--output", str(out)])
    html = out.read_text()
    assert "3d-force-graph" in html or "ForceGraph3D" in html


def test_galaxy_html_contains_cuneiform_sprite(tmp_path):
    sys.path.insert(0, str(REPO / "ilc-graphics-sidecar"))
    from ilc_graph_viz.__main__ import main
    out = tmp_path / "galaxy.html"
    manifest = REPO / "tools/galaxy_manifest_default.json"
    main(["--galaxy", str(manifest), "--output", str(out)])
    html = out.read_text()
    # SVG data URI should be present
    assert "data:image/svg+xml;base64," in html


def test_galaxy_map_does_not_import_ilc_core(tmp_path):
    # Check that importing __main__ does NOT cause any actual ilc_core module
    # to be loaded. The editable-install finder (__editable___ilc_core_*) is
    # a packaging artifact, not a real ilc_core import.
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, 'ilc-graphics-sidecar'); "
         "import ilc_graph_viz.__main__; "
         "mods = [m for m in sys.modules if 'ilc_core' in m "
         "        and not m.startswith('__editable__')]; "
         "print(mods)"],
        capture_output=True, text=True, cwd=str(REPO)
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "[]", f"ilc_core imported: {result.stdout}"
