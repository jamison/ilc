from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import ilc_core.identity.pq_agent_sign_bridge as pq_agent_sign_bridge
from tools import agent_loop_v1
from tools.agent_loop_v1 import AgentLoopRuntimeError
from ilc_core.identity.pq_agent_sign_bridge import sign_agent_submission
from tools.testbed import run_three_node_seven_agent_scenario as scenario_runner


REPO_ROOT = Path(__file__).resolve().parents[1]
VALID_AGENT_ID = "a" * 96


def _minimal_task() -> dict[str, object]:
    return {
        "task_id": "task:phase1568-fix2k",
        "task_class": "graph.compression",
        "channel": "phase1568-fix2k",
        "region_scope": ["private-rehearsal"],
        "verification_method": "replayable-simulation",
        "difficulty_factor": "1",
        "ecu_estimate": "1",
        "timestamp_created": 1_700_000_000,
        "epoch": 0,
    }


def _broadcast_args(artifact_file: Path, *, signer_agent_id: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        artifact_file=str(artifact_file),
        task_spec=None,
        task_json=json.dumps(_minimal_task(), sort_keys=True),
        task_json_base64=None,
        node_config=str(REPO_ROOT / "testbed/configs/ilc-node-1/node_config.json"),
        gossip_type="panel_verdict",
        signer_agent_id=signer_agent_id,
        emit_dir=None,
    )


def test_pq_agent_sign_binary_is_declared_in_cargo_toml() -> None:
    cargo_toml = (REPO_ROOT / "ilc_consensus/Cargo.toml").read_text(encoding="utf-8")
    assert 'name = "pq_agent_sign"' in cargo_toml


def test_pq_agent_sign_bridge_module_exists() -> None:
    bridge = REPO_ROOT / "ilc_core/identity/pq_agent_sign_bridge.py"
    assert bridge.is_file()
    source = bridge.read_text(encoding="utf-8")
    assert "def sign_agent_submission(" in source


def test_pq_agent_sign_bridge_has_public_rc_exclude() -> None:
    source = (REPO_ROOT / "ilc_core/identity/pq_agent_sign_bridge.py").read_text(encoding="utf-8")
    assert "PUBLIC_RC_EXCLUDE: pq_agent_sign_bridge" in source
    assert "PRIVATE_REHEARSAL_ONLY" in source


def test_pq_agent_sign_bridge_rejects_non_bytes_payload() -> None:
    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        sign_agent_submission(agent_id_hex=VALID_AGENT_ID, payload_bytes="not-bytes")  # type: ignore[arg-type]
    assert exc_info.value.token == "pq_agent_sign_payload_bytes_required"


def test_pq_agent_sign_bridge_rejects_missing_binary(tmp_path: Path) -> None:
    missing_binary = tmp_path / "missing-pq-agent-sign"
    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        sign_agent_submission(
            agent_id_hex=VALID_AGENT_ID,
            payload_bytes=b"{}",
            binary_path=str(missing_binary),
        )
    assert exc_info.value.token == "pq_agent_sign_binary_missing"


def test_pq_agent_sign_bridge_requires_interactive_tty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")

    class NonTty:
        def isatty(self) -> bool:
            return False

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", NonTty())

    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        sign_agent_submission(
            agent_id_hex=VALID_AGENT_ID,
            payload_bytes=b"{}",
            binary_path=str(fake_binary),
            manifest_path=str(fake_manifest),
        )

    assert exc_info.value.token == "pq_agent_sign_seed_tty_required"


def test_pq_agent_sign_bridge_uses_hidden_prompt_and_piped_stdin(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pq_agent_sign_bridge.clear_process_seed_cache()
    monkeypatch.delenv("ILC_PQ_AGENT_SIGN_PROCESS_SEED_CACHE", raising=False)
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")
    seed_words = "abandon " * 23 + "about"
    captured: dict[str, object] = {}

    class Tty:
        def isatty(self) -> bool:
            return True

    def fake_getpass(*, prompt: str, stream: object) -> str:
        captured["prompt"] = prompt
        captured["stream"] = stream
        return seed_words

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        captured["command"] = command
        captured["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="ab" * 3309, stderr="")

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", Tty())
    monkeypatch.setattr(pq_agent_sign_bridge.getpass, "getpass", fake_getpass)
    monkeypatch.setattr(pq_agent_sign_bridge.subprocess, "run", fake_run)

    signature = sign_agent_submission(
        agent_id_hex=VALID_AGENT_ID,
        payload_bytes=b"{}",
        binary_path=str(fake_binary),
        manifest_path=str(fake_manifest),
    )

    assert signature == "ab" * 3309
    assert "input hidden" in str(captured["prompt"])
    assert captured["stream"] is sys.stderr
    command = captured["command"]
    assert isinstance(command, list)
    assert seed_words not in " ".join(command)
    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["input"] == seed_words + "\n"
    assert kwargs["stdout"] is subprocess.PIPE
    assert kwargs["stderr"] is subprocess.PIPE
    assert "stdin" not in kwargs


def test_pq_agent_sign_bridge_retries_seed_entry_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pq_agent_sign_bridge.clear_process_seed_cache()
    monkeypatch.delenv("ILC_PQ_AGENT_SIGN_PROCESS_SEED_CACHE", raising=False)
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")
    seed_values = iter(["bad seed words", "abandon " * 23 + "about"])
    run_inputs: list[str] = []

    class Tty:
        def isatty(self) -> bool:
            return True

    def fake_getpass(*, prompt: str, stream: object) -> str:
        return next(seed_values)

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        run_inputs.append(str(kwargs["input"]))
        if len(run_inputs) == 1:
            return SimpleNamespace(
                returncode=1,
                stdout="",
                stderr=(
                    "Enter ML-DSA-65 mldsa_seed for agent aaaaaaaa... "
                    "as 24 BIP-39 words or 64-char hex, then press Ctrl-D:\n"
                    "invalid BIP-39 mnemonic: mnemonic contains an unknown word (word 23)\n"
                ),
            )
        return SimpleNamespace(returncode=0, stdout="cd" * 3309, stderr="")

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", Tty())
    monkeypatch.setattr(pq_agent_sign_bridge.getpass, "getpass", fake_getpass)
    monkeypatch.setattr(pq_agent_sign_bridge.subprocess, "run", fake_run)

    signature = sign_agent_submission(
        agent_id_hex=VALID_AGENT_ID,
        payload_bytes=b"{}",
        binary_path=str(fake_binary),
        manifest_path=str(fake_manifest),
    )

    assert signature == "cd" * 3309
    assert run_inputs == ["bad seed words\n", ("abandon " * 23 + "about").strip() + "\n"]


def test_pq_agent_sign_bridge_process_seed_cache_reuses_successful_seed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pq_agent_sign_bridge.clear_process_seed_cache()
    monkeypatch.setenv("ILC_PQ_AGENT_SIGN_PROCESS_SEED_CACHE", "1")
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")
    getpass_count = 0
    run_inputs: list[str] = []

    class Tty:
        def isatty(self) -> bool:
            return True

    def fake_getpass(*, prompt: str, stream: object) -> str:
        nonlocal getpass_count
        getpass_count += 1
        return "abandon " * 23 + "about"

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        run_inputs.append(str(kwargs["input"]))
        return SimpleNamespace(returncode=0, stdout="ef" * 3309, stderr="")

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", Tty())
    monkeypatch.setattr(pq_agent_sign_bridge.getpass, "getpass", fake_getpass)
    monkeypatch.setattr(pq_agent_sign_bridge.subprocess, "run", fake_run)

    for _ in range(2):
        assert sign_agent_submission(
            agent_id_hex=VALID_AGENT_ID,
            payload_bytes=b"{}",
            binary_path=str(fake_binary),
            manifest_path=str(fake_manifest),
        ) == "ef" * 3309

    assert getpass_count == 1
    assert run_inputs == [("abandon " * 23 + "about").strip() + "\n"] * 2
    pq_agent_sign_bridge.clear_process_seed_cache()


def test_pq_agent_sign_bridge_process_seed_cache_is_opt_in(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pq_agent_sign_bridge.clear_process_seed_cache()
    monkeypatch.delenv("ILC_PQ_AGENT_SIGN_PROCESS_SEED_CACHE", raising=False)
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")
    getpass_count = 0

    class Tty:
        def isatty(self) -> bool:
            return True

    def fake_getpass(*, prompt: str, stream: object) -> str:
        nonlocal getpass_count
        getpass_count += 1
        return "abandon " * 23 + "about"

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout="12" * 3309, stderr="")

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", Tty())
    monkeypatch.setattr(pq_agent_sign_bridge.getpass, "getpass", fake_getpass)
    monkeypatch.setattr(pq_agent_sign_bridge.subprocess, "run", fake_run)

    for _ in range(2):
        sign_agent_submission(
            agent_id_hex=VALID_AGENT_ID,
            payload_bytes=b"{}",
            binary_path=str(fake_binary),
            manifest_path=str(fake_manifest),
        )

    assert getpass_count == 2


def test_pq_agent_sign_bridge_final_seed_failure_is_sanitized(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pq_agent_sign_bridge.clear_process_seed_cache()
    monkeypatch.delenv("ILC_PQ_AGENT_SIGN_PROCESS_SEED_CACHE", raising=False)
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")
    attempts = 0

    class Tty:
        def isatty(self) -> bool:
            return True

    def fake_getpass(*, prompt: str, stream: object) -> str:
        return "bad seed words"

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        nonlocal attempts
        attempts += 1
        return SimpleNamespace(
            returncode=1,
            stdout="",
            stderr=(
                "Enter ML-DSA-65 mldsa_seed for agent aaaaaaaa... "
                "as 24 BIP-39 words or 64-char hex, then press Ctrl-D:\n"
                "invalid BIP-39 mnemonic: mnemonic contains an unknown word (word 23)\n"
            ),
        )

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", Tty())
    monkeypatch.setattr(pq_agent_sign_bridge.getpass, "getpass", fake_getpass)
    monkeypatch.setattr(pq_agent_sign_bridge.subprocess, "run", fake_run)

    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        sign_agent_submission(
            agent_id_hex=VALID_AGENT_ID,
            payload_bytes=b"{}",
            binary_path=str(fake_binary),
            manifest_path=str(fake_manifest),
        )

    assert attempts == 3
    assert exc_info.value.token == "pq_agent_sign_bridge_failed"
    assert "press Ctrl-D" not in str(exc_info.value)
    assert "invalid BIP-39 mnemonic" in str(exc_info.value)


def test_pq_agent_sign_bridge_does_not_retry_non_seed_signer_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pq_agent_sign_bridge.clear_process_seed_cache()
    monkeypatch.delenv("ILC_PQ_AGENT_SIGN_PROCESS_SEED_CACHE", raising=False)
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")
    attempts = 0

    class Tty:
        def isatty(self) -> bool:
            return True

    def fake_getpass(*, prompt: str, stream: object) -> str:
        return "abandon " * 23 + "about"

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        nonlocal attempts
        attempts += 1
        return SimpleNamespace(
            returncode=1,
            stdout="",
            stderr=(
                "Enter ML-DSA-65 mldsa_seed for agent aaaaaaaa... "
                "as 24 BIP-39 words or 64-char hex, then press Ctrl-D:\n"
                "input file exceeds MAX_SIGN_INPUT_BYTES\n"
            ),
        )

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", Tty())
    monkeypatch.setattr(pq_agent_sign_bridge.getpass, "getpass", fake_getpass)
    monkeypatch.setattr(pq_agent_sign_bridge.subprocess, "run", fake_run)

    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        sign_agent_submission(
            agent_id_hex=VALID_AGENT_ID,
            payload_bytes=b"{}",
            binary_path=str(fake_binary),
            manifest_path=str(fake_manifest),
        )

    assert attempts == 1
    assert exc_info.value.token == "pq_agent_sign_bridge_failed"
    assert "mldsa_seed" not in str(exc_info.value)
    assert "press Ctrl-D" not in str(exc_info.value)
    assert "input file exceeds MAX_SIGN_INPUT_BYTES" in str(exc_info.value)


def test_agent_loop_signature_requires_agent_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ILC_AGENT_LOOP_ALLOW_SYNTHETIC_SIGNATURE_FOR_TESTS", raising=False)
    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        agent_loop_v1._signature({"payload": "value"})
    assert exc_info.value.token == "agent_loop_signature_requires_agent_id"


def test_agent_loop_signature_rejects_invalid_agent_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ILC_AGENT_LOOP_ALLOW_SYNTHETIC_SIGNATURE_FOR_TESTS", raising=False)
    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        agent_loop_v1._signature({"payload": "value"}, agent_id_hex="agent-not-cdl069-v2")
    assert exc_info.value.token == "agent_loop_signature_agent_id_invalid"


def test_agent_loop_synthetic_signature_path_is_still_test_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_AGENT_LOOP_ALLOW_SYNTHETIC_SIGNATURE_FOR_TESTS", "1")
    signature = agent_loop_v1._signature({"payload": "value"})
    assert signature.startswith("agent-loop-v1-test-only:")


def test_submission_loader_ignores_submission_artifacts(tmp_path: Path) -> None:
    submission = {
        "marker": "agent_loop_submission_ok",
        "runtime_version": "agent_loop_v1_runtime_575.v0.1",
        "submission": {
            "task_id": "task:test",
            "epoch": 0,
            "profile": {"agent_id": VALID_AGENT_ID},
            "output_hash": "ab" * 32,
        },
    }
    artifact = {
        "artifact_kind": "agent_submission",
        "profile": {"agent_id": VALID_AGENT_ID},
        "output_hash": "ab" * 32,
    }
    (tmp_path / "submission_1.json").write_text(json.dumps(submission), encoding="utf-8")
    (tmp_path / "submission_artifact_1.json").write_text(json.dumps(artifact), encoding="utf-8")

    loaded = agent_loop_v1._load_submission_payloads(tmp_path)

    assert loaded == [submission["submission"]]


def test_scenario_runner_accepts_outsider_receiver() -> None:
    scenario = {
        "scenario_id": "block6-test",
        "agents": [{} for _ in range(7)],
        "outsider_receiver": {"cluster_id": "gamma", "node_name": "ilc-node-6"},
    }
    loaded = scenario_runner._load_scenario(scenario)
    assert loaded["outsider_receiver"]["node_name"] == "ilc-node-6"


def test_panel_outsider_fixture_derives_synthetic_from_outsider_receiver() -> None:
    scenario = {
        "scenario_id": "block6-test",
        "namespace_id": "phase1568",
        "agents": [{} for _ in range(7)],
        "outsider_receiver": {"cluster_id": "gamma", "node_name": "ilc-node-6"},
    }
    fixture = scenario_runner._panel_outsider_fixture(scenario)
    expected_seed = hashlib.sha256(
        b"REHEARSAL_OUTSIDER_FIXTURE_V1:block6-test:phase1568"
    ).hexdigest()
    assert fixture == {
        "seed_hex": expected_seed,
        "cluster_id": "gamma",
        "node_name": "ilc-node-6",
        "outsider_fixture_synthetic": True,
        "outsider_fixture_source": "derived_from_scenario_id_not_vrf",
    }


def test_panel_outsider_fixture_prefers_explicit_outsider() -> None:
    outsider = {"seed_hex": "01" * 32, "cluster_id": "omega", "node_name": "manual-outsider"}
    scenario = {
        "scenario_id": "block6-test",
        "agents": [{} for _ in range(7)],
        "outsider": outsider,
        "outsider_receiver": {"cluster_id": "gamma", "node_name": "ilc-node-6"},
    }
    assert scenario_runner._panel_outsider_fixture(scenario) == outsider


def test_remote_service_smoke_hosts_use_only_physical_scenario_hosts() -> None:
    scenario = {
        "agents": [
            {"node_name": "jamisons-imac"},
            {"node_name": "ilc-node-2"},
            {"node_name": "ilc-node-2"},
            {"node_name": "ilc-node-3"},
        ],
        "outsider_receiver": {"node_name": "ilc-node-6"},
    }
    remote_hosts = {
        "ilc-node-2": {"name": "ilc-node-2"},
        "ilc-node-3": {"name": "ilc-node-3"},
        "ilc-node-6": {"name": "ilc-node-6"},
    }

    assert scenario_runner._remote_service_smoke_hosts(scenario, remote_hosts) == [
        "ilc-node-2",
        "ilc-node-3",
        "ilc-node-6",
    ]


def test_local_node_names_include_control_machine_aliases() -> None:
    hosts = {
        "control_machine": {
            "name": "ilc-node-1",
            "tailscale_name": "jamisons-imac",
        }
    }

    assert scenario_runner._local_node_names(hosts) == {
        "ilc-node-1",
        "jamisons-imac",
    }


def test_broadcast_from_home_uses_in_process_signer_session(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_broadcast_submission(**kwargs: object) -> list[dict[str, object]]:
        captured.update(kwargs)
        return [{"endpoint": "https://peer.invalid", "status_code": 202}]

    monkeypatch.setattr(scenario_runner, "_agent_loop_broadcast_submission", fake_broadcast_submission)
    artifact = tmp_path / "artifact.json"
    artifact.write_text(
        json.dumps(
            {
                "artifact_kind": "agent_submission",
                "profile": {"agent_id": VALID_AGENT_ID},
                "output_payload": {"ok": True},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    result = scenario_runner._broadcast_from_home(
        _minimal_task(),
        artifact,
        "agent_submission",
        tmp_path,
        signer_agent_id=VALID_AGENT_ID,
    )

    assert result["send_statuses"] == [{"endpoint": "https://peer.invalid", "status_code": 202}]
    assert captured["signer_agent_id_hex"] == VALID_AGENT_ID
    assert captured["gossip_type"] == "agent_submission"
    assert captured["channel"] == _minimal_task()["channel"]
    assert json.loads((tmp_path / "broadcast_agent_submission.json").read_text(encoding="utf-8"))[
        "signer_agent_id"
    ] == VALID_AGENT_ID


def test_broadcast_from_home_prefers_artifact_channel_over_task_channel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}
    artifact_channel = "cid:9f7a8c42bb11ddee99aa22cc33ff44aa"

    def fake_broadcast_submission(**kwargs: object) -> list[dict[str, object]]:
        captured.update(kwargs)
        return [{"endpoint": "https://peer.invalid", "status_code": 202}]

    monkeypatch.setattr(scenario_runner, "_agent_loop_broadcast_submission", fake_broadcast_submission)
    artifact = tmp_path / "artifact.json"
    artifact.write_text(
        json.dumps(
            {
                "artifact_kind": "agent_submission",
                "channel": artifact_channel,
                "profile": {"agent_id": VALID_AGENT_ID},
                "output_payload": {"ok": True},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    result = scenario_runner._broadcast_from_home(
        _minimal_task(),
        artifact,
        "agent_submission",
        tmp_path,
        signer_agent_id=VALID_AGENT_ID,
    )

    assert result["send_statuses"] == [{"endpoint": "https://peer.invalid", "status_code": 202}]
    assert captured["channel"] == artifact_channel


def test_broadcast_artifact_requires_signer_for_non_agent_artifact(tmp_path: Path) -> None:
    artifact_file = tmp_path / "panel.json"
    artifact_file.write_text(json.dumps({"artifact_kind": "panel_verdict"}, sort_keys=True), encoding="utf-8")
    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        agent_loop_v1._run_broadcast_command(_broadcast_args(artifact_file))
    assert exc_info.value.token == "broadcast_signer_agent_id_required"


def test_agent_submission_broadcast_derives_signer_from_profile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_broadcast_submission(**kwargs: object) -> list[dict[str, object]]:
        captured.update(kwargs)
        return [{"endpoint": "https://example.invalid", "delivered": True}]

    monkeypatch.setattr(agent_loop_v1, "_broadcast_submission", fake_broadcast_submission)
    artifact_file = tmp_path / "submission.json"
    artifact_file.write_text(
        json.dumps(
            {
                "artifact_kind": "agent_submission",
                "profile": {"agent_id": VALID_AGENT_ID},
                "output_payload": {"ok": True},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    result = agent_loop_v1._run_broadcast_command(_broadcast_args(artifact_file, signer_agent_id=None))

    assert result == 0
    assert captured["signer_agent_id_hex"] == VALID_AGENT_ID


def test_agent_submission_broadcast_rejects_mismatched_explicit_signer(tmp_path: Path) -> None:
    artifact_file = tmp_path / "submission.json"
    artifact_file.write_text(
        json.dumps(
            {
                "artifact_kind": "agent_submission",
                "profile": {"agent_id": VALID_AGENT_ID},
                "output_payload": {"ok": True},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    with pytest.raises(AgentLoopRuntimeError) as exc_info:
        agent_loop_v1._run_broadcast_command(_broadcast_args(artifact_file, signer_agent_id="b" * 96))
    assert exc_info.value.token == "broadcast_signer_agent_id_mismatch"


def test_production_emission_guard_remains_default_off() -> None:
    source = (REPO_ROOT / "ilc_core/epoch/epoch_emission_production_path.py").read_text(encoding="utf-8")
    assert "PRODUCTION_EMISSION_NOT_ACTIVATED = True" in source
    assert "PRODUCTION_EMISSION_NOT_ACTIVATED = False" not in source


def test_adr0035_type_registry_guard_remains_default_off() -> None:
    source = (REPO_ROOT / "ilc_core/bundle/type_registry.py").read_text(encoding="utf-8")
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in source
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = False" not in source
