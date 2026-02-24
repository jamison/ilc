from __future__ import annotations

import subprocess
import sys
from pathlib import Path


RUNNER = Path("tools/run_mutation_canary_phase_297.py")


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER)] + args,
        check=False,
        capture_output=True,
        text=True,
    )


def test_runner_exists() -> None:
    assert RUNNER.exists()


def test_help_contract() -> None:
    result = _run(["--help"])
    assert result.returncode == 0
    assert "Usage: run_mutation_canary_phase_297.py" in result.stdout
    assert "--dry-run" in result.stdout


def test_dry_run_contract_and_probe_order() -> None:
    result = _run(["--dry-run"])
    assert result.returncode == 0
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert any("Dry run: mutation canary probe plan" in line for line in lines)
    expected = [
        "[1/3] lineage_rotated_authority_guard",
        "[2/3] compromise_containment_sequence_order_guard",
        "[3/3] non_target_phase_stamp_poisoning_guard",
    ]
    for token in expected:
        assert token in lines


def test_unknown_arg_returns_exit_2() -> None:
    result = _run(["--bogus"])
    assert result.returncode == 2
    assert "Unknown argument: --bogus" in result.stderr


def test_full_run_kills_all_required_mutants() -> None:
    result = _run([])
    assert result.returncode == 0
    assert "[lineage_rotated_authority_guard] MUTATION_KILLED" in result.stdout
    assert "[compromise_containment_sequence_order_guard] MUTATION_KILLED" in result.stdout
    assert "[non_target_phase_stamp_poisoning_guard] MUTATION_KILLED" in result.stdout
    assert "PASS: all mutation canary probes were killed by target tests" in result.stdout
