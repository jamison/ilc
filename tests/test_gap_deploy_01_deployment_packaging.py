from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_dockerfile_exists_and_uses_real_entrypoints() -> None:
    dockerfile = _read("Dockerfile")

    assert "COPY run_node.py ./run_node.py" in dockerfile
    assert 'ENTRYPOINT ["python3", "run_node.py"]' in dockerfile
    assert "validator_harness" in dockerfile
    assert "attribution_batch_ingest" in dockerfile


def test_dockerfile_does_not_copy_secret_or_runtime_artifact_paths() -> None:
    dockerfile = _read("Dockerfile")

    forbidden_fragments = (
        "COPY . .",
        "COPY keys",
        "COPY .ssh",
        "COPY out",
        "COPY .env",
        "genesis_private_key",
        "TWINE_PASSWORD",
        "PYPI_TOKEN",
    )
    for fragment in forbidden_fragments:
        assert fragment not in dockerfile


def test_dockerignore_excludes_secret_and_generated_paths() -> None:
    dockerignore = _read(".dockerignore")

    for required in (
        ".claude",
        ".venv",
        "out",
        "*.mldsa_seed",
        "*.mnemonic",
        ".env",
        "signer_sessions",
        "agent_sessions",
        "ilc_consensus/target",
    ):
        assert required in dockerignore


def test_compose_file_has_three_internal_services_and_no_host_ports() -> None:
    compose = yaml.safe_load(_read("docker-compose.yml"))
    services = compose["services"]

    assert sorted(services) == ["ilc-bootstrap-1", "ilc-observer-2", "ilc-observer-3"]
    assert compose["networks"]["ilc-local"]["internal"] is True
    for service in services.values():
        assert "ports" not in service
        assert service["networks"] == ["ilc-local"]
        assert service["environment"]["ILC_DATA_DIR"] == "/var/lib/ilc"


def test_docker_compose_config_when_docker_available() -> None:
    if shutil.which("docker") is None:
        pytest.skip("docker_not_available_in_current_shell")

    result = subprocess.run(
        ["docker", "compose", "config"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_operator_guide_records_key_boundary_and_static_discovery() -> None:
    guide = _read("docs/OPERATOR_GUIDE.md")

    assert "ILC Genesis Agent keys are NOT provisioned" in guide
    assert "The operator must supply their own node key" in guide
    assert "validator_harness --config <path> --genesis <path>" in guide
    assert "Dynamic discovery requires the separate CDL-103 lane" in guide
    assert "node_daemon_starting" in guide


def test_monitoring_dashboard_is_valid_json_with_expected_panels() -> None:
    dashboard = json.loads(_read("monitoring/dashboards/ilc_node_dashboard.json"))

    assert dashboard["uid"] == "ilc-node-v1"
    assert dashboard["schemaVersion"] == 38
    titles = {panel["title"] for panel in dashboard["panels"]}
    assert {
        "Peer Count (Static)",
        "Peer Count (Dynamic)",
        "Epoch Settlement Latency (ms)",
        "ECU Attribution Event Rate",
        "Decay Application Events",
    } <= titles


def test_status_records_gap_deploy_completion_tokens() -> None:
    status = _read("docs/phases/STATUS.md")

    for token in (
        "gap_deploy_01_complete_phase_1577e",
        "dockerfile_ilc_core_consensus_combined_committed_gap_deploy_01",
        "docker_compose_3_node_testnet_committed_gap_deploy_01",
        "operator_guide_committed_gap_deploy_01",
        "monitoring_dashboards_committed_gap_deploy_01",
        "deployment_packaging_test_suite_5_plus_gap_deploy_01",
    ):
        assert token in status
