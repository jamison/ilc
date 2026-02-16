from __future__ import annotations

from pathlib import Path
import subprocess


GUARDRAIL_GATE_SCRIPT = Path("tools/check_non_replay_domain_exception_migration_guardrails.sh")


def _run_guardrail_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GUARDRAIL_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_non_replay_domain_exception_guardrail_gate_dry_run_contract() -> None:
    result = _run_guardrail_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: non-replay domain exception migration guardrail gate commands" in result.stdout
    assert (
        "python3 -m pytest tests/test_non_replay_domain_exception_migration_guardrail.py "
        "tests/test_event_log_validators.py tests/test_ilc_cluster_a_clause_binding.py "
        "tests/test_governance_ingest_helper_domain_exceptions.py "
        "tests/test_ledger_export_domain_exceptions.py "
        "tests/test_mcp_cli_domain_exceptions.py -q"
    ) in result.stdout


def test_non_replay_domain_exception_guardrail_gate_unknown_argument_exit_code() -> None:
    result = _run_guardrail_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_non_replay_domain_exception_guardrail_gate_help_contract() -> None:
    result = _run_guardrail_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_non_replay_domain_exception_migration_guardrails.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_non_replay_domain_exception_guardrail_gate_runs_successfully() -> None:
    result = _run_guardrail_gate([])
    assert result.returncode == 0
    assert "=== Non-Replay Domain Exception Migration Guardrail Gate ===" in result.stdout
    assert "Non-replay domain exception migration guardrail gate: PASS" in result.stdout
