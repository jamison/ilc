import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli(
    *args: str,
    home: Path | None = None,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if home is not None:
        env["HOME"] = str(home)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", *args],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def test_ilc_bare_command_exits_zero() -> None:
    result = _run_cli()
    assert result.returncode == 0


def test_ilc_bare_command_emits_json_hint() -> None:
    result = _run_cli()
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["hint"] == "ILC — Intelligent Labor Coin CLI"


def test_ilc_bare_command_quick_start_list_is_non_empty() -> None:
    result = _run_cli()
    payload = json.loads(result.stdout)
    assert isinstance(payload["quick_start"], list)
    assert payload["quick_start"]


def test_ilc_doctor_all_checks_ready_when_all_state_files_present(tmp_path: Path) -> None:
    home = tmp_path / "home"
    graph_path = tmp_path / "graph.json"
    balance_path = tmp_path / "balance.json"
    identity_path = tmp_path / "identity.json"
    _write_json(identity_path, {"lineage_id": "lineage-local", "status": "active"})
    _write_json(home / ".ilc" / "invite_nullifiers.json", [])
    _write_json(home / ".ilc" / "consent_gate.json", {"autonomy_level": "bounded_autonomy"})
    _write_json(home / ".ilc" / "sidecar_registry.json", {})
    _write_json(graph_path, {"nodes": []})
    _write_json(balance_path, {"balance_ilc": "0"})
    (home / ".ilc" / "ccss").mkdir(parents=True)

    result = _run_cli(
        "--graph-state",
        str(graph_path),
        "doctor",
        home=home,
        env_overrides={
            "ILC_BALANCE_STATE_PATH": str(balance_path),
            "ILC_IDENTITY_STATE_PATH": str(identity_path),
        },
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["data"]["verdict"] == "ready"
    assert all(payload["data"]["checks"].values())


def test_ilc_doctor_not_setup_when_identity_absent(tmp_path: Path) -> None:
    home = tmp_path / "home"
    graph_path = tmp_path / "graph.json"
    result = _run_cli("--graph-state", str(graph_path), "doctor", home=home)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["data"]["verdict"] == "not_setup"
    assert payload["data"]["checks"]["identity_initialized"] is False


def test_ilc_doctor_partial_setup_when_only_identity_present(tmp_path: Path) -> None:
    home = tmp_path / "home"
    graph_path = tmp_path / "graph.json"
    identity_path = tmp_path / "identity.json"
    _write_json(identity_path, {"lineage_id": "lineage-local", "status": "active"})

    result = _run_cli(
        "--graph-state",
        str(graph_path),
        "doctor",
        home=home,
        env_overrides={"ILC_IDENTITY_STATE_PATH": str(identity_path)},
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["data"]["verdict"] == "partial_setup"
    assert payload["data"]["checks"]["identity_initialized"] is True
    assert payload["data"]["checks"]["local_graph_state_readable"] is False


def test_ilc_doctor_makes_no_writes_to_disk(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    graph_path = tmp_path / "graph.json"
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = _run_cli("--graph-state", str(graph_path), "doctor", home=home)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert result.returncode == 1
    assert before == after
    assert not graph_path.exists()


def test_ilc_doctor_pretty_flag_produces_non_json_output(tmp_path: Path) -> None:
    result = _run_cli("--graph-state", str(tmp_path / "graph.json"), "doctor", "--pretty", home=tmp_path)
    assert result.returncode == 1
    assert not result.stdout.lstrip().startswith("{")
    assert "ILC doctor" in result.stdout


def test_ilc_skills_list_matches_sidecar_list(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    sidecar = _run_cli("--graph-state", str(graph_path), "sidecar", "list", home=tmp_path)
    skills = _run_cli("--graph-state", str(graph_path), "skills", "list", home=tmp_path)

    sidecar_payload = json.loads(sidecar.stdout)
    skills_payload = json.loads(skills.stdout)
    sidecar_payload.pop("ts_utc", None)
    skills_payload.pop("ts_utc", None)
    assert sidecar.returncode == 0
    assert skills.returncode == 0
    assert skills_payload == sidecar_payload
    assert not graph_path.exists()


def test_ilc_skills_install_rejects_with_named_token(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    result = _run_cli(
        "--graph-state",
        str(graph_path),
        "skills",
        "install",
        "ilc-openclaw-local-capture",
        home=tmp_path,
    )

    payload = json.loads(result.stderr)
    assert result.returncode == 1
    assert payload["error"] == "sidecar_install_requires_clawhub_post_fix2g"
    assert not graph_path.exists()
