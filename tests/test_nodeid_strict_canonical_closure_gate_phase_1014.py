from __future__ import annotations

from pathlib import Path
import subprocess


CLOSURE_GATE_SCRIPT = Path("tools/check_nodeid_strict_canonical_closure_1014.sh")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CLOSURE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_phase_1014_closure_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: nodeid strict canonical closure gate (phase 1014) commands" in result.stdout
    assert "tests/test_node_id_dual_contract_phase_1002.py" in result.stdout
    assert "tests/test_node_id_runtime_bridge_phase_1003.py" in result.stdout


def test_phase_1014_closure_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_1014_closure_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_nodeid_strict_canonical_closure_1014.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_1014_closure_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== NodeID Strict Canonical Closure Gate (Phase 1014) ===" in result.stdout
    assert "NodeID strict canonical closure gate: PASS" in result.stdout
