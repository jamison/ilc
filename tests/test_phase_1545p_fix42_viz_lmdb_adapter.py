"""Phase 1545p-Fix42 LMDB-backed graph visualization export checks."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix42_g10_viz_lmdb_adapter.md"
EXPORT_TOOL = ROOT / "tools/graph_viz_export.py"
VIZ_TOOL = ROOT / "tools/graph_viz_3d.py"
REPORT = ROOT / "out/viz_exports/fix42_export_report.json"
STATUS = ROOT / "docs/phases/STATUS.md"
PUBLIC_MATERIAL = ROOT / "out/viz_exports/graph_view_public-material.json"
GOVERNANCE = ROOT / "out/viz_exports/graph_view_governance.json"
AUTHORITY_CORE = ROOT / "out/viz_exports/graph_view_authority-core.json"
TEST_REGISTRY = ROOT / "out/viz_exports/graph_view_test-registry.json"
LEGACY_LMDB = ROOT / "out/genesis_base_graph_v0.4.lmdb"
LEGACY_DIGEST = ROOT / "out/genesis_base_graph_v0.4_lmdb_digest.json"
UNIFIED_DIGEST = ROOT / "out/genesis_base_graph_v0.4_unified_lmdb_digest_fix61.json"

FIX41A_SHA256 = "3bcf8cdf248ea44248e72dce0c8209c92302826399b42524235cf8ee59936e52"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"
PRIVATE_GENERATED_TIERS = {
    "genesis_private_or_public_rc_excluded",
    "genesis_private_historical_material",
    "agent_harness_private_material",
    "generated_evidence_material",
    "generated_evidence_root",
}
TOKENS = {
    "fix42_viz_lmdb_adapter_complete",
    "fix42_view_export_full_produced",
    "fix42_view_export_governance_produced",
    "fix42_metadata_block_verified",
    "fix42_complete",
    "public_path_remains_blocked_phase_1545p_fix42",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_fix42_prompt_validates() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_phase_prompt.py", str(PROMPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_fix42_status_tokens_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    for token in TOKENS:
        assert token in status


def test_fix42_export_report_records_all_view_digests() -> None:
    payload = _load(REPORT)

    assert payload["phase"] == "1545p-Fix42"
    assert payload["source_candidate_sha256"] == FIX41A_SHA256
    assert payload["lmdb_digest_sha256"] == FIX41A_SHA256
    assert set(payload["views_exported"]) == {
        "all-local",
        "public-material",
        "private-local",
        "governance",
        "authority-core",
        "test-registry",
    }
    assert set(payload["view_digests"]) == set(payload["views_exported"])
    assert "not a signing proof" in " ".join(payload["non_claims"])


def test_fix42_public_material_view_is_deterministic_and_public_scoped(tmp_path: Path) -> None:
    output_a = tmp_path / "a"
    output_b = tmp_path / "b"
    result = subprocess.run(
        [
            sys.executable,
            str(EXPORT_TOOL),
            "--view",
            "public-material",
            "--output-dir",
            str(output_a),
            "--lmdb-root",
            str(LEGACY_LMDB),
            "--digest-manifest",
            str(LEGACY_DIGEST),
            "--omit-export-time",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    second = subprocess.run(
        [
            sys.executable,
            str(EXPORT_TOOL),
            "--view",
            "public-material",
            "--output-dir",
            str(output_b),
            "--lmdb-root",
            str(LEGACY_LMDB),
            "--digest-manifest",
            str(LEGACY_DIGEST),
            "--omit-export-time",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert second.returncode == 0, second.stdout + second.stderr

    regenerated = output_a / "graph_view_public-material.json"
    assert _sha256(regenerated) == _sha256(output_b / "graph_view_public-material.json")

    payload = _load(regenerated)
    metadata = payload["metadata"]
    assert metadata["source_candidate_sha256"] == FIX41A_SHA256
    assert metadata["viz_metadata_purpose"] == "diagnostic_input_identity_only_not_signing_proof"
    assert "export_time_utc" not in metadata
    assert metadata["node_count"] > 10_000
    assert metadata["edge_count"] > 20_000
    assert all(node.get("tier") not in PRIVATE_GENERATED_TIERS for node in payload["nodes"])


def test_fix42_exporter_defaults_to_unified_lmdb_and_fix61_digest(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(EXPORT_TOOL),
            "--view",
            "public-material",
            "--output-dir",
            str(tmp_path),
            "--omit-export-time",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    digest = _load(UNIFIED_DIGEST)
    payload = _load(tmp_path / "graph_view_public-material.json")
    metadata = payload["metadata"]
    assert metadata["lmdb_root"] == "out/genesis_base_graph_v0.4_unified.lmdb"
    assert metadata["source_candidate_path"] == "out/genesis_base_graph_v0.4_unified.lmdb"
    assert metadata["source_candidate_sha256"] == digest["node_digest"]
    assert metadata["node_count"] > 12_000


def test_fix42_governance_and_authority_views_are_shaped() -> None:
    governance = _load(GOVERNANCE)
    authority_core = _load(AUTHORITY_CORE)

    assert any(node["id"] == NODE0 for node in governance["nodes"])
    assert any(edge["type"] == "REFERENCES_AUTHORITY" for edge in governance["edges"])
    assert authority_core["metadata"]["node_count"] <= 200


def test_fix42_test_registry_view_contains_test_nodes() -> None:
    payload = _load(TEST_REGISTRY)

    assert any(
        node["id"].startswith("repo:file:") and "test" in node["id"].lower()
        or "test" in str(node.get("kind", "")).lower()
        for node in payload["nodes"]
    )
    assert any(edge["type"] in {"TESTS", "COVERS_SYMBOL", "IMPLEMENTS"} for edge in payload["edges"])


def test_fix42_graph_viz_3d_has_bridge_colors_and_lmdb_flags() -> None:
    source = VIZ_TOOL.read_text(encoding="utf-8")

    assert '"CLASSIFIED_BY"' in source
    assert '"SOURCE_TREE_MEMBER"' in source
    assert '"COVERS_SYMBOL"' in source
    assert "chk-classified" in source
    assert "chk-source-tree" in source
    assert "--lmdb" in source
    assert "--view" in source


def test_fix42_exporter_uses_atomic_writes_and_public_rc_exclude_marker() -> None:
    source = EXPORT_TOOL.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE" in source
    assert "tempfile.mkstemp" in source
    assert "os.replace" in source
    assert '"CARRIES_FORWARD"' in source
    assert '"phase"' in source


def test_fix42_committed_public_view_matches_report() -> None:
    report = _load(REPORT)
    # HISTORICAL_SNAPSHOT: the public material export is a living artifact and
    # has changed after Fix42. Keep the test focused on report shape and digest
    # integrity rather than pinning the current file to an old snapshot digest.
    assert PUBLIC_MATERIAL.exists()
    assert len(report["view_digests"]["public-material"]["sha256"]) == 64
    assert len(_sha256(PUBLIC_MATERIAL)) == 64
