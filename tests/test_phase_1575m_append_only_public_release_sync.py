from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_append_only_public_release_sync_1575m_v0.1.md"
TOOL = ROOT / "tools/public_release_append_only_sync.py"


def _load_tool_module():
    spec = importlib.util.spec_from_file_location("public_release_append_only_sync", TOOL)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _git(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _make_repo(path: Path) -> Path:
    path.mkdir()
    _git(["init", "-q"], path)
    _git(["config", "user.name", "Test User"], path)
    _git(["config", "user.email", "test@example.invalid"], path)
    (path / "README.md").write_text("initial\n", encoding="utf-8")
    _git(["add", "README.md"], path)
    _git(["commit", "-q", "-m", "initial"], path)
    return path


def _make_sanitized_tree(path: Path) -> Path:
    (path / "release_artifacts/genesis_v05").mkdir(parents=True)
    (path / "README.md").write_text("public\n", encoding="utf-8")
    (path / "release_artifacts/genesis_v05/manifest.json").write_text(
        json.dumps({"schema_version": "test", "files": []}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def test_spec_contains_required_sections_and_policy_terms() -> None:
    text = SPEC.read_text(encoding="utf-8")
    required_sections = [
        "## 1. Purpose and Post-Initial-Repair Boundary",
        "## 2. Why Force-Pushed Public Mirror History Is Deprecated",
        "## 3. Public Repository Contribution Model",
        "## 4. Private-Source Reconciliation Model",
        "## 5. Append-Only Public Sync Algorithm",
        "## 6. Public-Only File Policy",
        "## 7. Public PR Backport Policy",
        "## 8. Emergency Force-Push Policy",
        "## 9. Receipt Schema",
        "## 10. Migration Path to Graph-Native Exporter",
    ]
    for section in required_sections:
        assert section in text
    assert "The contribution-era rule is:" in text
    assert "backport_required" in text
    assert "needs_cdl_or_phase" in text
    assert "graph_native_exporter_status` remains `not_activated" in text


def test_tool_writes_deterministic_dry_run_receipts(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_sanitized_tree(tmp_path / "sanitized")
    receipt_a = tmp_path / "receipt_a.json"
    receipt_b = tmp_path / "receipt_b.json"
    argv = [
        "--public-repo",
        str(public_repo),
        "--sanitized-tree",
        str(sanitized_tree),
        "--source-private-commit",
        "abc123",
        "--dry-run",
    ]
    assert module.main([*argv, "--json-out", str(receipt_a)]) == 0
    assert module.main([*argv, "--json-out", str(receipt_b)]) == 0
    assert receipt_a.read_bytes() == receipt_b.read_bytes()
    payload = json.loads(receipt_a.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "ilc_public_release_append_only_sync_receipt.v0.1"
    assert payload["source_private_commit"] == "abc123"
    assert payload["previous_public_head"] == _git(["rev-parse", "HEAD"], public_repo)
    assert payload["sanitized_tree_digest"]
    assert payload["sanitized_tree_file_count"] == 2
    assert payload["public_push_authorized"] is False
    assert payload["release_artifact_manifest_sha256"]
    assert payload["homoiconic_forward_fields"]["graph_native_exporter_status"] == "not_activated"


def test_tool_rejects_dirty_public_repo(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_sanitized_tree(tmp_path / "sanitized")
    (public_repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(ValueError, match="public_repo_dirty"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit="abc123",
            dry_run=True,
        )


def test_tool_rejects_missing_sanitized_tree(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    with pytest.raises(ValueError, match="sanitized_tree_missing"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=tmp_path / "missing",
            source_private_commit="abc123",
            dry_run=True,
        )


def test_tool_requires_dry_run(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_sanitized_tree(tmp_path / "sanitized")
    with pytest.raises(ValueError, match="dry_run_required"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit="abc123",
            dry_run=False,
        )


def test_tool_source_has_no_publish_or_overwrite_execution_path() -> None:
    source = TOOL.read_text(encoding="utf-8")
    assert "git push" not in source
    assert "--force" not in source
    assert "force-with-lease" not in source
    assert "public_push_authorized\": False" in source
    assert "public_push_authorized_must_be_false" in source
