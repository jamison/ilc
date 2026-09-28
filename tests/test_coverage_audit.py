from __future__ import annotations

import json
from pathlib import Path

import tools.coverage_audit as coverage_audit


def test_walk_paths_extracts_manual_additions_repo_path() -> None:
    payload = {"_manual_additions": [{"repo_path": "docs/specs/foo.md"}]}

    assert "docs/specs/foo.md" in coverage_audit._walk_paths(payload)


def test_walk_paths_extracts_legacy_annotations_path() -> None:
    payload = {"annotations": [{"path": "ilc_core/foo.py"}]}

    assert "ilc_core/foo.py" in coverage_audit._walk_paths(payload)


def test_walk_paths_handles_deep_nesting() -> None:
    payload = {"outer": [{"middle": {"inner": [{"repo_path": "tools/deep.py"}]}}]}

    assert "tools/deep.py" in coverage_audit._walk_paths(payload)


def test_audit_counts_registered_and_unregistered_with_file_list(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(
        json.dumps({"_manual_additions": [{"repo_path": "docs/specs/registered.md"}]}),
        encoding="utf-8",
    )

    result = coverage_audit.audit(
        tmp_path,
        [ledger],
        files=[
            "docs/specs/registered.md",
            "docs/specs/unregistered.md",
            "README.md",
        ],
    )

    assert result["total_covered"] == 2
    assert result["registered_paths_all_ledgers"] == 1
    assert result["registered_tracked_covered_count"] == 1
    assert result["unregistered_count"] == 1
    assert result["coverage_pct"] == 50.0
    assert result["unregistered_files"] == ["docs/specs/unregistered.md"]


def test_fail_on_unregistered_returns_one(monkeypatch, tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"_manual_additions": []}), encoding="utf-8")

    monkeypatch.setattr(
        coverage_audit,
        "_all_tracked_files",
        lambda repo_root: ["tools/unregistered.py"],
    )

    rc = coverage_audit.main(
        [
            "--repo-root",
            str(tmp_path),
            "--ledger",
            str(ledger),
            "--fail-on-unregistered",
        ]
    )

    assert rc == 1


def test_default_mode_returns_zero_with_unregistered(monkeypatch, tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"_manual_additions": []}), encoding="utf-8")

    monkeypatch.setattr(
        coverage_audit,
        "_all_tracked_files",
        lambda repo_root: ["tools/unregistered.py"],
    )

    rc = coverage_audit.main(["--repo-root", str(tmp_path), "--ledger", str(ledger)])

    assert rc == 0
