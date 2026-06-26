"""Tests for Fix85 public/private node visual encoding.

Phase: 1545p-Fix85
Tests rc_visibility scanner, graph HTML injection, and filter controls.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS_DIR = str(REPO / "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from rc_visibility_scanner import scan_rc_visibility, PUBLIC_RC_EXCLUDE_MARKER, MAX_FILES


# ── test 1: file with PUBLIC_RC_EXCLUDE marker → "excluded" ───────────────────

def test_scan_rc_visibility_excluded(tmp_path):
    f = tmp_path / "test_excluded.py"
    f.write_bytes(b"<!-- PUBLIC_RC_EXCLUDE: test -->\n# This file is excluded\n")
    result = scan_rc_visibility(["test_excluded.py"], tmp_path)
    assert result["test_excluded.py"] == "excluded"


# ── test 2: file with no marker → "public" ───────────────────────────────────

def test_scan_rc_visibility_public(tmp_path):
    f = tmp_path / "test_public.py"
    f.write_bytes(b"# A normal public source file\ndef foo(): pass\n")
    result = scan_rc_visibility(["test_public.py"], tmp_path)
    assert result["test_public.py"] == "public"


# ── test 3: file with both markers → "private_historical" ────────────────────

def test_scan_rc_visibility_private_historical(tmp_path):
    f = tmp_path / "test_priv.py"
    f.write_bytes(
        b"# PUBLIC_RC_EXCLUDE: local_only\n"
        b"# genesis_private_historical_material\n"
        b"# Both markers present\n"
    )
    result = scan_rc_visibility(["test_priv.py"], tmp_path)
    assert result["test_priv.py"] == "private_historical"


# ── test 4: nonexistent path → "unknown" ─────────────────────────────────────

def test_scan_rc_visibility_missing_file(tmp_path):
    result = scan_rc_visibility(["does_not_exist.py"], tmp_path)
    assert result["does_not_exist.py"] == "unknown"


# ── test 5: OOM guard — 20,001 paths, mostly under out/ ──────────────────────

def test_scan_rc_visibility_oom_guard(tmp_path):
    # Create one real file under out/ and one real file not under out/
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    real_out_file = out_dir / "data.json"
    real_out_file.write_bytes(b"{}")
    real_other = tmp_path / "src.py"
    real_other.write_bytes(b"# public source\n")

    # Build 20,001 paths: mostly fake out/ paths (don't need to exist)
    paths = [f"out/fake_{i}.json" for i in range(20_000)]
    paths.append("src.py")  # the real non-out/ file

    assert len(paths) == 20_001

    result = scan_rc_visibility(paths, tmp_path)

    # All out/ paths should be "excluded" (OOM guard, not actually scanned)
    assert result["out/fake_0.json"] == "excluded"
    assert result["out/fake_9999.json"] == "excluded"

    # The non-out/ real file should be scanned properly
    assert result["src.py"] == "public"

    # Confirm we have a result for all 20,001 paths
    assert len(result) == 20_001


# ── test 6: graph HTML contains rc_visibility ─────────────────────────────────

def test_graph_html_contains_rc_visibility(tmp_path):
    sys.path.insert(0, str(REPO / "ilc-graphics-sidecar"))
    from ilc_graph_viz.__main__ import _load_atlas, _html

    # Build a minimal atlas JSON fixture
    fixture = {
        "nodes": [
            {
                "candidate_id": "cdl:cdl_001",
                "label": "Test CDL",
                "node_kind": "cdl",
                "tier": "genesis_core",
                "source_path": "",
            }
        ],
        "edges": [],
    }
    fixture_path = tmp_path / "test_atlas.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")

    nodes, links = _load_atlas(fixture, max_nodes=10)

    # Every node should have rc_visibility
    assert all("rc_visibility" in n for n in nodes), "rc_visibility missing from nodes"

    # Build HTML and confirm rc_visibility appears in output
    from ilc_graph_viz.__main__ import _compute_star_rank, _detect_communities
    star_rank = _compute_star_rank(nodes, links)
    communities = _detect_communities(nodes, links)
    for n in nodes:
        n["community"] = communities.get(n["id"], -1)
    html = _html(nodes, links, star_rank)

    assert "rc_visibility" in html, "rc_visibility not found in HTML output"


# ── test 7: filter controls present — rcvis group, no old tier-based pair ──────

def test_filter_controls_present(tmp_path):
    sys.path.insert(0, str(REPO / "ilc-graphics-sidecar"))
    from ilc_graph_viz.__main__ import _load_atlas, _html, _compute_star_rank, _detect_communities

    fixture = {
        "nodes": [
            {
                "candidate_id": "artifact:genesis_root",
                "label": "Root",
                "node_kind": "genesis_authority_root",
                "tier": "genesis_core",
                "source_path": "",
            }
        ],
        "edges": [],
    }

    nodes, links = _load_atlas(fixture, max_nodes=10)
    star_rank = _compute_star_rank(nodes, links)
    communities = _detect_communities(nodes, links)
    for n in nodes:
        n["community"] = communities.get(n["id"], -1)
    html = _html(nodes, links, star_rank)

    # New rcvis radio group must be present
    assert 'name="rcvis"' in html, "rcvis radio group not found in HTML"

    # Old tier-based 'public'/'private' radio values should NOT appear as standalone
    # (the governance view still has a "view" radio, but no view='public'/'private')
    # Check that there is no radio input with name="view" and value="public" or "private"
    import re
    old_public_radio = re.search(r'name=["\']view["\'].*?value=["\']public["\']', html)
    old_private_radio = re.search(r'name=["\']view["\'].*?value=["\']private["\']', html)
    assert old_public_radio is None, "Old tier-based 'Public only' view radio still present"
    assert old_private_radio is None, "Old tier-based 'Private only' view radio still present"
