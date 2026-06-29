from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

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


def test_broadcast_from_home_exposes_signer_prompt_stderr(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        captured["command"] = command
        captured.update(kwargs)
        return SimpleNamespace(stdout=json.dumps({"send_statuses": []}))

    monkeypatch.setattr(scenario_runner, "_run", fake_run)
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}", encoding="utf-8")

    result = scenario_runner._broadcast_from_home(
        _minimal_task(),
        artifact,
        "agent_submission",
        tmp_path,
        signer_agent_id=VALID_AGENT_ID,
    )

    assert result == {"send_statuses": []}
    assert captured["cwd"] == REPO_ROOT
    assert captured["stderr_to_terminal"] is True
    assert "--signer-agent-id" in captured["command"]


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
