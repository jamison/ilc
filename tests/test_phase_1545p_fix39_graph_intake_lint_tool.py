from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/check_new_file_graph_coverage.py"


def _ledger(tmp_path: Path, *paths: str) -> Path:
    path = tmp_path / "ledger.json"
    payload = {"annotations": [{"repo_path": item} for item in paths]}
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )
    return path


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_covered_file_with_ledger_entry_passes(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path, "docs/specs/example.md")
    result = _run("--ledger", str(ledger), "--files", "docs/specs/example.md")
    assert result.returncode == 0
    assert "graph_intake_all_covered_files_registered" in result.stdout


def test_covered_file_without_ledger_entry_fails(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    result = _run("--ledger", str(ledger), "--files", "docs/specs/missing.md")
    assert result.returncode == 1
    assert "docs/specs/missing.md" in result.stdout
    assert "graph_intake_docs_specs_missing_md" in result.stdout


def test_out_file_is_excluded_from_graph_intake(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    result = _run("--ledger", str(ledger), "--files", "out/generated.json")
    assert result.returncode == 0
    assert "graph_intake_all_covered_files_registered" in result.stdout


def test_empty_explicit_file_list_passes(tmp_path: Path) -> None:
    ledger = _ledger(tmp_path)
    result = _run("--ledger", str(ledger), "--files")
    assert result.returncode == 0
    assert "graph_intake_all_covered_files_registered" in result.stdout


def test_missing_ledger_exits_two(tmp_path: Path) -> None:
    result = _run("--ledger", str(tmp_path / "missing.json"), "--files", "docs/specs/example.md")
    assert result.returncode == 2
    assert "graph_intake_ledger_not_found" in result.stderr
