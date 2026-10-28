from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


RUNNER = Path("tools/run_mutation_canary_phase_297.py")
GOSSIP_TRANSPORT = Path("ilc_core/network/d2d/gossip_transport.py")
HTTP_GOSSIP_RUNTIME = Path("ilc_core/network/d2d/http_gossip_transport_runtime.py")
ROOT_CONFTEST = Path("conftest.py")


def _load_runner_module():
    spec = importlib.util.spec_from_file_location("mutation_canary_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_root_conftest_module():
    spec = importlib.util.spec_from_file_location("root_conftest_for_canary_test", ROOT_CONFTEST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_d2d_transport_canaries_target_current_runtime_versions() -> None:
    expected_gossip_line = (
        'GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_1572.v0.1"'
    )
    expected_http_line = (
        'HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION = "http_gossip_transport_runtime_1572.v0.1"'
    )
    runner_text = RUNNER.read_text(encoding="utf-8")
    gossip_text = GOSSIP_TRANSPORT.read_text(encoding="utf-8")
    runtime_text = HTTP_GOSSIP_RUNTIME.read_text(encoding="utf-8")

    assert expected_gossip_line in runner_text
    assert expected_gossip_line in gossip_text
    assert expected_http_line in runner_text
    assert expected_http_line in runtime_text
    assert "gossip_transport_runtime_558.v0.1" not in runner_text
    assert "http_gossip_transport_runtime_568.v0.1" not in runner_text


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


def test_full_run_restores_all_unique_targets_without_mtime_drift() -> None:
    runner = _load_runner_module()
    targets = tuple(dict.fromkeys(probe.path for probe in runner.PROBES))
    # NOTE: the before/after mtime measurement is not covered by the runner's
    # flock, so this test requires exclusive access to the probe files.  Run it
    # in isolation or as part of a sequential gate — not alongside a concurrent
    # canary invocation (which would legitimately shift mtimes between measurements).
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
        ["git", "status", "--short", "--", *(str(path) for path in targets)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert status.stdout.strip() == ""


def test_dirty_probe_target_is_rejected_without_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner_module()
    repo = tmp_path / "repo"
    target = repo / "target.py"
    repo.mkdir()
    target.write_text("VALUE = 'clean'\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "canary@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Canary Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "target.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=repo, check=True)
    target.write_text("VALUE = 'local work'\n", encoding="utf-8")
    probe = runner.Probe("dirty", Path("target.py"), "clean", "mutant", (sys.executable, "-V"))
    monkeypatch.setattr(runner, "REPO_ROOT", repo)
    monkeypatch.setattr(runner, "PROBES", (probe,))

    assert runner._capture_clean_target_states() is None
    assert target.read_text(encoding="utf-8") == "VALUE = 'local work'\n"


def test_recovery_state_is_repository_scoped_and_hash_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = _load_runner_module()
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    repo_a.mkdir()
    repo_b.mkdir()
    assert runner._state_dir_for_repo(repo_a) != runner._state_dir_for_repo(repo_b)

    target = repo_a / "target.py"
    original = b"VALUE = 'clean'\n"
    target.write_bytes(original)
    probe = runner.Probe("recovery", Path("target.py"), "clean", "mutant", (sys.executable, "-V"))
    state_dir = tmp_path / "state-a"
    monkeypatch.setattr(runner, "REPO_ROOT", repo_a)
    monkeypatch.setattr(runner, "_CANARY_STATE_DIR", state_dir)
    target_stat = target.stat()
    runner._write_dirty_sentinel(
        probe,
        original,
        b"VALUE = 'mutant'\n",
        target_stat.st_mode & 0o7777,
        (target_stat.st_atime_ns, target_stat.st_mtime_ns),
    )

    record = json.loads(runner._sentinel_path("recovery").read_text(encoding="utf-8"))
    assert record["repo_root"] == str(repo_a)
    assert record["relative_target"] == "target.py"
    assert record["original_sha256"] == hashlib.sha256(original).hexdigest()
    assert record["mutated_sha256"] == hashlib.sha256(b"VALUE = 'mutant'\n").hexdigest()
    assert Path(record["backup_path"]).read_bytes() == original
    runner._clear_dirty_sentinel(probe)
    assert not list(state_dir.glob("dirty_*"))


def test_recovery_restores_only_the_recorded_mutant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = _load_runner_module()
    root_conftest = _load_root_conftest_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.py"
    original = b"VALUE = 'clean'\n"
    mutant = b"VALUE = 'mutant'\n"
    target.write_bytes(original)
    probe = runner.Probe("recovery", Path("target.py"), "clean", "mutant", (sys.executable, "-V"))
    state_dir = tmp_path / "state"
    monkeypatch.setattr(runner, "REPO_ROOT", repo)
    monkeypatch.setattr(runner, "_CANARY_STATE_DIR", state_dir)
    target_stat = target.stat()
    runner._write_dirty_sentinel(
        probe,
        original,
        mutant,
        target_stat.st_mode & 0o7777,
        (target_stat.st_atime_ns, target_stat.st_mtime_ns),
    )
    sentinel = runner._sentinel_path("recovery")

    target.write_bytes(mutant)
    root_conftest._recover_canary_record(sentinel, repo, state_dir)
    assert target.read_bytes() == original
    assert not sentinel.exists()

    target.write_bytes(original)
    runner._write_dirty_sentinel(
        probe,
        original,
        mutant,
        target_stat.st_mode & 0o7777,
        (target_stat.st_atime_ns, target_stat.st_mtime_ns),
    )
    sentinel = runner._sentinel_path("recovery")
    target.write_bytes(b"VALUE = 'human edit'\n")
    with pytest.raises(ValueError, match="refusing overwrite"):
        root_conftest._recover_canary_record(sentinel, repo, state_dir)
    assert target.read_bytes() == b"VALUE = 'human edit'\n"
    assert sentinel.exists()
