from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_readme_quickstart_commands_present() -> None:
    readme = (_repo_root() / "README.md").read_text(encoding="utf-8")
    assert "python3 tools/genesis_boot.py" in readme
    assert "python3 run_node.py" in readme
    assert "python3 tools/demo_walkthrough.py" in readme
    # HISTORICAL_SNAPSHOT: Phase 998 used an older explanatory sentence. The
    # current README keeps the same quickstart contract in command-comment form.
    assert "prints Genesis hash from config/genesis.json" in readme


def test_genesis_boot_quickstart_behavior() -> None:
    proc = subprocess.run(
        [sys.executable, "tools/genesis_boot.py"],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = proc.stdout
    assert "--- ILC GENESIS BOOT SEQUENCE ---" in stdout
    assert "STATUS:  SUCCESS" in stdout
    assert "BLOCK:   config/genesis.json" in stdout
    assert "HASH:" in stdout
