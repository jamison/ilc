from __future__ import annotations

import subprocess
from pathlib import Path


SCRIPT_PATH = Path("tools/check_d2e_03_prototype_closure_phase_265.sh")
HANDOFF_PATH = Path("docs/specs/ilc_d2e_03_prototype_handoff_265_v0.1.md")


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_dry_run_lists_all_required_commands() -> None:
    result = _run_script("--dry-run")
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "test_d2e_03_cli_prototype_264.py" in output
    assert "test_d2e_03_prototype_contract_263.py" in output
    assert "python3 -m ilc_core.cli.main --help" in output
    assert "python3 tools/run_phase_236_preflight.py" in output


def test_help_exits_zero_and_contains_usage() -> None:
    result = _run_script("--help")
    assert result.returncode == 0
    assert "usage" in (result.stdout + result.stderr).lower()


def test_unknown_arg_exits_two() -> None:
    result = _run_script("--unknown-arg")
    assert result.returncode == 2


def test_handoff_exists_and_has_required_sections() -> None:
    assert HANDOFF_PATH.exists()
    text = _read(HANDOFF_PATH)
    headings = [
        "## 1. Window summary and closure status",
        "## 2. Verified closure evidence from gate components",
        "## 3. Hard prerequisites for Phase 266",
        "## 4. Soft carry-forward items",
        "## 5. Next sequence pointer",
        "## 6. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_handoff_references_phase_266_and_mutation_scope_fixture() -> None:
    text = _read(HANDOFF_PATH)
    assert "Phase 266" in text
    assert "mutation-scope fixture" in text


def test_handoff_references_contract_and_runtime_test_anchors() -> None:
    text = _read(HANDOFF_PATH)
    assert "ilc_d2e_03_prototype_contract_263_v0.1.md" in text
    assert "tests/test_d2e_03_cli_prototype_264.py" in text
