from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_append_only_public_release_sync_1575m_v0.1.md"
TOOL = ROOT / "tools/public_release_append_only_sync.py"
SOURCE_COMMIT = "a" * 40


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


def _make_candidate_repo(path: Path, public_repo: Path) -> Path:
    subprocess.check_call(["git", "clone", "-q", str(public_repo), str(path)])
    _git(["config", "user.name", "Test User"], path)
    _git(["config", "user.email", "test@example.invalid"], path)
    _make_sanitized_tree(path)
    _git(["add", "README.md", "release_artifacts/genesis_v05/manifest.json"], path)
    _git(["commit", "-q", "-m", "candidate"], path)
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
    assert "1575m-Fix1" in text
    assert "previous public HEAD must be an ancestor" in text
    assert "denylist_scan_result" in text
    assert "public_rc_exclude_scan_result" in text


def test_tool_writes_deterministic_dry_run_receipts(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_candidate_repo(tmp_path / "sanitized", public_repo)
    receipt_a = tmp_path / "receipt_a.json"
    receipt_b = tmp_path / "receipt_b.json"
    argv = [
        "--public-repo",
        str(public_repo),
        "--sanitized-tree",
        str(sanitized_tree),
        "--source-private-commit",
        SOURCE_COMMIT,
        "--dry-run",
    ]
    assert module.main([*argv, "--json-out", str(receipt_a)]) == 0
    assert module.main([*argv, "--json-out", str(receipt_b)]) == 0
    assert receipt_a.read_bytes() == receipt_b.read_bytes()
    payload = json.loads(receipt_a.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "ilc_public_release_append_only_sync_receipt.v0.1"
    assert payload["source_private_commit"] == SOURCE_COMMIT
    assert payload["previous_public_head"] == _git(["rev-parse", "HEAD"], public_repo)
    assert payload["append_only_check"]["candidate_public_head"] == _git(
        ["rev-parse", "HEAD"], sanitized_tree
    )
    assert payload["append_only_check"]["previous_public_head_is_ancestor"] is True
    assert payload["denylist_scan_result"] == "pass"
    assert payload["public_rc_exclude_scan_result"] == "pass"
    assert payload["public_remote_status"]["remote_fetch_result"] == "skipped_no_remote"
    assert payload["sanitized_tree_digest"]
    assert payload["sanitized_tree_file_count"] == 2
    assert payload["public_push_authorized"] is False
    assert payload["release_artifact_manifest_sha256"]
    assert payload["homoiconic_forward_fields"]["graph_native_exporter_status"] == "not_activated"


def test_tool_rejects_dirty_public_repo(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_candidate_repo(tmp_path / "sanitized", public_repo)
    (public_repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(ValueError, match="public_repo_dirty"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit=SOURCE_COMMIT,
            dry_run=True,
        )


def test_tool_rejects_missing_sanitized_tree(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    with pytest.raises(ValueError, match="sanitized_tree_missing"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=tmp_path / "missing",
            source_private_commit=SOURCE_COMMIT,
            dry_run=True,
        )


def test_tool_requires_dry_run(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_candidate_repo(tmp_path / "sanitized", public_repo)
    with pytest.raises(ValueError, match="dry_run_required"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit=SOURCE_COMMIT,
            dry_run=False,
        )


def test_tool_rejects_non_ancestor_candidate(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_repo(tmp_path / "sanitized")
    _make_sanitized_tree(sanitized_tree)
    _git(["add", "README.md", "release_artifacts/genesis_v05/manifest.json"], sanitized_tree)
    _git(["commit", "-q", "-m", "unrelated candidate"], sanitized_tree)
    with pytest.raises(ValueError, match="public_head_not_ancestor_of_candidate"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit=SOURCE_COMMIT,
            dry_run=True,
        )


def test_tool_rejects_public_rc_exclude_marker(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_candidate_repo(tmp_path / "sanitized", public_repo)
    (sanitized_tree / "private_runtime.py").write_text(
        "# PUBLIC_RC_EXCLUDE: synthetic test marker\n",
        encoding="utf-8",
    )
    _git(["add", "private_runtime.py"], sanitized_tree)
    _git(["commit", "-q", "-m", "add excluded marker"], sanitized_tree)
    with pytest.raises(ValueError, match="public_rc_exclude_marker_found_in_sanitized_tree"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit=SOURCE_COMMIT,
            dry_run=True,
        )


def test_tool_rejects_docstring_public_rc_exclude_marker(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_candidate_repo(tmp_path / "sanitized", public_repo)
    (sanitized_tree / "private_runtime.py").write_text(
        '"""Private helper.\n\n'
        "Line 3\n"
        "Line 4\n"
        "Line 5\n"
        "Line 6\n"
        "Line 7\n"
        "Line 8\n"
        "Line 9\n"
        "Line 10\n"
        "PUBLIC_RC_EXCLUDE: synthetic_docstring_marker\n"
        '"""\n',
        encoding="utf-8",
    )
    _git(["add", "private_runtime.py"], sanitized_tree)
    _git(["commit", "-q", "-m", "add excluded marker"], sanitized_tree)
    with pytest.raises(ValueError, match="public_rc_exclude_marker_found_in_sanitized_tree"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit=SOURCE_COMMIT,
            dry_run=True,
        )


@pytest.mark.parametrize("term", ["ilcops@proton.me", "Genesis operator", "jurisdiction_redacted"])
def test_tool_rejects_denylist_term(tmp_path: Path, term: str) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_candidate_repo(tmp_path / "sanitized", public_repo)
    (sanitized_tree / "leak.txt").write_text(f"{term}\n", encoding="utf-8")
    _git(["add", "leak.txt"], sanitized_tree)
    _git(["commit", "-q", "-m", "add denied term"], sanitized_tree)
    with pytest.raises(ValueError, match="denylist_term_found_in_sanitized_tree"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit=SOURCE_COMMIT,
            dry_run=True,
        )


def test_tool_rejects_source_private_commit_not_40_char_hex(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    sanitized_tree = _make_candidate_repo(tmp_path / "sanitized", public_repo)
    with pytest.raises(ValueError, match="source_private_commit_must_be_40_char_hex"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=sanitized_tree,
            source_private_commit="abc123",
            dry_run=True,
        )


def test_tool_rejects_forbidden_sanitized_tree_root(tmp_path: Path) -> None:
    module = _load_tool_module()
    public_repo = _make_repo(tmp_path / "public")
    with pytest.raises(ValueError, match="sanitized_tree_root_forbidden"):
        module.build_receipt(
            public_repo=public_repo,
            sanitized_tree=Path("/"),
            source_private_commit=SOURCE_COMMIT,
            dry_run=True,
        )


def test_tool_source_has_no_publish_or_overwrite_execution_path() -> None:
    source = TOOL.read_text(encoding="utf-8")
    assert "git push" not in source
    assert "--force" not in source
    assert "force-with-lease" not in source
    assert "public_push_authorized\": False" in source
    assert "public_push_authorized_must_be_false" in source
