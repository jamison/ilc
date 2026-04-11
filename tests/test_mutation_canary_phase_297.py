from __future__ import annotations

import hashlib
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
        "[1/9] lineage_rotated_authority_guard",
        "[2/9] compromise_containment_sequence_order_guard",
        "[3/9] non_target_phase_stamp_poisoning_guard",
        "[4/9] centrality_delta_gossip_version_guard",
        "[5/9] centrality_delta_gossip_d2d_dependency_guard",
        "[6/9] gossip_transport_cdl_039_forbidden_key_guard",
        "[7/9] gossip_transport_version_guard",
        "[8/9] gossip_transport_cdl_061_dep_guard",
        "[9/9] http_gossip_transport_runtime_version_guard",
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
    for probe_name in (
        "lineage_rotated_authority_guard",
        "compromise_containment_sequence_order_guard",
        "non_target_phase_stamp_poisoning_guard",
        "centrality_delta_gossip_version_guard",
        "centrality_delta_gossip_d2d_dependency_guard",
        "gossip_transport_cdl_039_forbidden_key_guard",
        "gossip_transport_version_guard",
        "gossip_transport_cdl_061_dep_guard",
        "http_gossip_transport_runtime_version_guard",
    ):
        assert f"[{probe_name}] MUTATION_KILLED" in result.stdout
    assert "PASS: all mutation canary probes were killed by target tests" in result.stdout


def test_full_run_restores_security_files_without_mtime_drift() -> None:
    targets = (
        Path("ilc_core/security/signer_lineage_runtime.py"),
        Path("ilc_core/security/key_compromise_runtime.py"),
    )
    before = {
        path: (
            path.stat().st_mtime_ns,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in targets
    }

    result = _run([])

    assert result.returncode == 0
    for path in targets:
        after_mtime = path.stat().st_mtime_ns
        after_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        assert after_hash == before[path][1]
        assert after_mtime == before[path][0]

    status = subprocess.run(
        ["git", "status", "--short", "ilc_core/security/"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert status.stdout.strip() == ""
