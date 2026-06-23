from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasPhaseFileRegistration,
    DEFAULT_PUBLIC_PATH_POLICY,
    repo_file_ref_id,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
PROMPT_PATH = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix67_g10_classified_by_sidecar_migration.md"
)
SIDECAR_PATH = REPO_ROOT / "docs/specs/ilc_fix67_public_path_classified_by_receipt_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
ARTIFACT_EDGE_SOURCE = "artifact:genesis_package_merkle_root_v0.4"


def _lmdb_edges() -> list[dict]:
    store = GenesisAtlasCandidateStore(LMDB_ROOT)
    try:
        return store.iter_edges()
    finally:
        store.close()


def test_fix67_prompt_validates_required_surface() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    assert text.startswith("# Phase 1545p-Fix67-G10: Classification Projection Hardening")
    assert "## LMDB Node Registration" in text
    assert "No ellipses in walkthrough." in text


def test_fix67_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix67_classification_projection_hardening_phase_1545p",
        "register_phase_files_public_path_classified_by_removed_phase_1545p_fix67",
        "public_path_hub_edges_migrated_to_sidecar_phase_1545p_fix67",
        "classified_by_fanin_regression_added_phase_1545p_fix67",
        "fix67_complete",
    ):
        assert token in text


def test_public_path_classified_by_spokes_migrated_to_sidecar() -> None:
    payload = json.loads(SIDECAR_PATH.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "ilc_fix67_public_path_classified_by_receipt.v0.1"
    assert payload["target_policy"] == DEFAULT_PUBLIC_PATH_POLICY
    assert payload["pre_public_path_classified_by_edge_count"] == 200
    assert payload["edge_count"] == 199
    assert len(payload["entries"]) == 199
    assert payload["live_receipt_summary"]["removed_edge_count"] == 199
    assert payload["live_receipt_summary"]["post_public_path_classified_by_edge_count"] == 1
    assert payload["preserved_edges"][0]["source"] == ARTIFACT_EDGE_SOURCE
    assert payload["preserved_edges"][0]["adjudication"] == "preserved"


def test_only_package_root_classified_by_edge_remains_for_public_path_policy() -> None:
    remaining = [
        edge
        for edge in _lmdb_edges()
        if edge.get("edge_type") == "CLASSIFIED_BY"
        and edge.get("target") == DEFAULT_PUBLIC_PATH_POLICY
    ]
    assert len(remaining) == 1
    assert remaining[0]["source"] == ARTIFACT_EDGE_SOURCE


def test_no_high_fanin_classified_by_hub() -> None:
    fan_in = Counter(
        edge["target"] for edge in _lmdb_edges() if edge.get("edge_type") == "CLASSIFIED_BY"
    )
    violations = {target: count for target, count in fan_in.items() if count > 100}
    assert not violations, f"High fan-in CLASSIFIED_BY hubs: {violations}"


def test_register_phase_files_does_not_write_public_path_classified_by(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    writer = AtlasLmdbSafeWriter(root)
    try:
        receipt = writer.register_phase_files(
            "1545p-Fix67-test",
            [
                AtlasPhaseFileRegistration(
                    path="docs/phases/fix67_example.md",
                    node_kind="phase_walkthrough_node",
                    graph_projection="support_candidate_graph",
                    required_edges=(("EVIDENCES", "phase:1545p_fix67_test"),),
                )
            ],
            dry_run=False,
        )
        file_id = repo_file_ref_id("docs/phases/fix67_example.md")
        edge_semantics = {
            (edge["source"], edge["edge_type"], edge["target"])
            for edge in writer.store.iter_edges()
        }
        assert receipt["accepted_edge_count"] == 2
        assert (file_id, "CLASSIFIED_BY", DEFAULT_PUBLIC_PATH_POLICY) not in edge_semantics
        assert (file_id, "CARRIES_FORWARD", "phase:1545p_fix67_test") in edge_semantics
        assert (file_id, "EVIDENCES", "phase:1545p_fix67_test") in edge_semantics
    finally:
        writer.close()
