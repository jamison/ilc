from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
LEDGER = ROOT / "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json"
AGENTS = ROOT / "AGENTS.md"
CLAUDE = ROOT / "CLAUDE.md"


RECENT_BATCHES = {
    "manual_batch_079_phase_1573e_1573i_retroactive",
    "manual_batch_080_phase_1573j_current",
}


def _annotations() -> list[dict[str, object]]:
    return json.loads(LEDGER.read_text())["annotations"]


def test_taxonomy_documents_live_legacy_references_edge() -> None:
    taxonomy = TAXONOMY.read_text()
    assert "### REFERENCES" in taxonomy
    assert "Legacy generic reference edge" in taxonomy
    assert "Prefer" in taxonomy and "REFERENCES_AUTHORITY" in taxonomy


def test_taxonomy_batch_numbering_matches_post_1573u_state() -> None:
    taxonomy = TAXONOMY.read_text()
    assert "Current last batch (as of Phase 1573u-Fix1)" in taxonomy
    assert "manual_batch_081_phase_1573u_fix1_taxonomy_hardening" in taxonomy
    assert "manual_batch_082_<slug>" in taxonomy


def test_recent_fix38_batches_use_repo_path_not_candidate_id() -> None:
    recent = [
        annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch") in RECENT_BATCHES
    ]
    assert len(recent) == 64
    assert all("repo_path" in annotation for annotation in recent)
    assert all("candidate_id" not in annotation for annotation in recent)
    assert all("proposed_edges" not in annotation for annotation in recent)


def test_taxonomy_hardening_batch_registers_new_phase_files() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch")
        == "manual_batch_081_phase_1573u_fix1_taxonomy_hardening"
    }
    assert set(by_path) == {
        "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md",
        "tests/test_phase_1573u_node_classification_taxonomy.py",
        "docs/phases/phase_1573u_fix1_node_classification_taxonomy_hardening_walkthrough.md",
    }
    assert all("candidate_id" not in annotation for annotation in by_path.values())
    assert by_path[
        "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
    ]["recommended_graph_action"] == "load_bearing_artifact_added"
    assert by_path[
        "tests/test_phase_1573u_node_classification_taxonomy.py"
    ]["recommended_graph_action"] == "support_only"


def test_guidance_distinguishes_new_schema_from_legacy_keys() -> None:
    taxonomy = TAXONOMY.read_text()
    agents = AGENTS.read_text()
    claude = CLAUDE.read_text()
    assert "legacy records may retain it" in taxonomy
    assert "do not use legacy `candidate_id` for new records" in agents
    claude_flat = " ".join(claude.split())
    assert "Historical ledger records may still contain legacy keys" in claude_flat
    assert "Do not copy those keys into new records" in claude_flat
