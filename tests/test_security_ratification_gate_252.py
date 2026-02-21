"""
Phase 252 — Security Ratification Gate Tests

Verifies:
- gate script exists
- --dry-run exits 0 and output includes all four composed command targets
- --help exits 0 and contains 'usage'
- unknown arg exits 2
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GATE_SCRIPT = REPO_ROOT / "tools/run_phase_252_security_ratification_gate.py"

COMPOSED_TARGETS = [
    "test_security_cdl_ratification_251.py",
    "test_security_runtime_cross_cdl_interactions_244.py",
    "run_phase_244_security_runtime_gate.py",
    "run_phase_236_preflight.py",
]


class TestGateScriptExists:
    def test_gate_script_exists(self):
        assert GATE_SCRIPT.exists(), f"Gate script not found: {GATE_SCRIPT}"


class TestGateDryRun:
    def setup_method(self):
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.returncode = result.returncode
        self.stdout = result.stdout

    def test_dry_run_exits_zero(self):
        assert self.returncode == 0, f"--dry-run exited {self.returncode}; stdout: {self.stdout}"

    def test_dry_run_includes_all_four_composed_targets(self):
        for target in COMPOSED_TARGETS:
            assert target in self.stdout, (
                f"Composed target '{target}' missing from --dry-run output; stdout: {self.stdout}"
            )


class TestGateHelp:
    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, f"--help exited {result.returncode}"

    def test_help_contains_usage(self):
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        combined = result.stdout + result.stderr
        assert "usage" in combined.lower(), f"'usage' not found in --help output: {combined}"


class TestUnknownArgExitsTwo:
    def test_unknown_arg_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), "--unknown-option"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 2, (
            f"Unknown arg should exit 2, got {result.returncode}; stderr: {result.stderr}"
        )
