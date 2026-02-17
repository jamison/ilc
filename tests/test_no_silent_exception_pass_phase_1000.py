from __future__ import annotations

from pathlib import Path
import re


SILENT_PASS_RE = re.compile(
    r"except\s+[^\n:]+:\s*(?:\n[ \t]*#.*)*\n[ \t]*pass\b",
    re.MULTILINE,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_no_silent_exception_pass_patterns_in_cli_modules() -> None:
    cli_dir = _repo_root() / "ilc_core" / "cli"
    offenders: list[str] = []
    for py_file in sorted(cli_dir.glob("*.py")):
        text = py_file.read_text(encoding="utf-8")
        if SILENT_PASS_RE.search(text):
            offenders.append(str(py_file.relative_to(_repo_root())))
    assert offenders == []
