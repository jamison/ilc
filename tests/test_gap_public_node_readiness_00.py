# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-PUBLIC-NODE-READINESS-00 operator readiness diagnostics tests."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.node.operator_init_runtime import check_node_config, generate_node_init_material
from ilc_core.node.readiness_runtime import (
    PROPOSAL_IDENTITY_NOTE,
    build_readiness_report,
    host_is_tailscale_cidr,
    udp_quic_probe,
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=30,
    )


def _generated_node(tmp_path: Path, *, host: str = "127.0.0.1", valid_days: int = 365):
    return generate_node_init_material(
        root=tmp_path / "node",
        network_id="ilc-rc01",
        host=host,
        grpc_port=50151,
        quic_port=7101,
        valid_days=valid_days,
        allow_test_stub_crypto=True,
    )


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("expected object")
    return payload


def _rewrite_endpoint(generated, endpoint: str) -> None:
    payload = _load_json(generated.endpoint_assertion_path)
    payload["grpc_endpoint"] = endpoint
    generated.endpoint_assertion_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n",
        encoding="utf-8",
    )
    config = generated.config_path.read_text(encoding="utf-8")
    config = config.replace(f'grpc_endpoint = "{generated.grpc_endpoint}"', f'grpc_endpoint = "{endpoint}"')
    generated.config_path.write_text(config, encoding="utf-8")


def test_readiness_help_discoverable() -> None:
    result = _run_cli("node", "readiness", "--help")
    assert result.returncode == 0
    assert "--network" in result.stdout
    assert "--peer" in result.stdout
    assert "--config" in result.stdout


def test_readiness_local_pass_on_valid_config(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    report = build_readiness_report(config_path=generated.config_path)

    assert report["readiness_verdict"] == "pass"
    assert report["network_checks"]["enabled"] is False
    assert report["network_checks"]["network_grpc_tcp_probe"] == "skipped_network_flag_absent"


def test_readiness_tailscale_ip_fails(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)
    _rewrite_endpoint(generated, "100.100.100.100:50151")

    report = build_readiness_report(config_path=generated.config_path)

    assert report["local_checks"]["endpoint_host_is_tailscale_cidr"] is True
    assert report["readiness_verdict"] == "fail"
    assert "endpoint_assertion_host_in_tailscale_cidr" in report["warnings"]


def test_readiness_tailscale_boundary_public_ip_passes() -> None:
    assert host_is_tailscale_cidr("100.64.0.1") is True
    assert host_is_tailscale_cidr("100.63.255.255") is False


def test_readiness_wildcard_listen_recorded(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    check = check_node_config(generated.config_path)

    assert check["grpc_listen_is_wildcard"] is True


def test_readiness_cert_days_remaining_positive(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    check = check_node_config(generated.config_path)

    assert check["tls_cert_days_remaining"] >= 364


def test_readiness_cert_days_remaining_low_warns(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path, valid_days=10)

    report = build_readiness_report(config_path=generated.config_path)

    assert report["local_checks"]["tls_cert_days_remaining"] < 30
    assert "tls_cert_expires_within_30_days" in report["warnings"]
    assert report["readiness_verdict"] == "warn"


def test_readiness_network_skipped_without_flag(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    report = build_readiness_report(config_path=generated.config_path, network=False)

    assert report["network_checks"]["enabled"] is False
    assert report["network_checks"]["network_quic_udp_probe"] == "skipped_network_flag_absent"


def test_readiness_tcp_probe_skips_wildcard_host(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)
    _rewrite_endpoint(generated, "0.0.0.0:50151")

    report = build_readiness_report(config_path=generated.config_path, network=True)

    assert report["network_checks"]["network_grpc_tcp_reachable"] is False
    assert report["network_checks"]["network_grpc_tcp_error"] == "network_probe_skipped_wildcard_host"
    assert "network_probe_skipped_wildcard_host" in report["warnings"]


def test_readiness_tcp_probe_records_refused(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)
    _rewrite_endpoint(generated, "127.0.0.1:1")

    report = build_readiness_report(config_path=generated.config_path, network=True)

    assert report["network_checks"]["network_grpc_tcp_reachable"] is False
    assert "network_grpc_tcp_error" in report["network_checks"]
    assert report["readiness_verdict"] == "fail"


def test_readiness_udp_probe_skipped_without_peer(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    report = build_readiness_report(config_path=generated.config_path, network=True)

    assert report["network_checks"]["network_quic_udp_probe"] == "skipped_no_peer"


def test_readiness_udp_probe_sets_socket_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[float] = []

    class FakeSocket:
        def settimeout(self, value: float) -> None:
            calls.append(value)

        def sendto(self, _payload: bytes, _addr: tuple[str, int]) -> int:
            return 1

        def recvfrom(self, _size: int) -> tuple[bytes, tuple[str, int]]:
            raise TimeoutError

        def close(self) -> None:
            return None

    monkeypatch.setattr(socket, "socket", lambda *_args, **_kwargs: FakeSocket())

    assert udp_quic_probe("127.0.0.1:7101")["network_quic_udp_probe"] == "timeout"
    assert calls == [3.0]


def test_readiness_udp_probe_any_response_counts_reachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSocket:
        def settimeout(self, _value: float) -> None:
            return None

        def sendto(self, _payload: bytes, _addr: tuple[str, int]) -> int:
            return 1

        def recvfrom(self, _size: int) -> tuple[bytes, tuple[str, int]]:
            return b"not-quic", ("127.0.0.1", 7101)

        def close(self) -> None:
            return None

    monkeypatch.setattr(socket, "socket", lambda *_args, **_kwargs: FakeSocket())

    result = udp_quic_probe("127.0.0.1:7101")

    assert result["network_quic_udp_probe"] == "reachable"
    assert result["network_quic_udp_warning"] == "non_quic_response_received"


def test_readiness_udp_unreachable_fails_when_peer_requested(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generated = _generated_node(tmp_path)

    monkeypatch.setattr(
        "ilc_core.node.readiness_runtime.tcp_reachability_probe",
        lambda _endpoint: {
            "network_grpc_tcp_latency_ms": 1,
            "network_grpc_tcp_reachable": True,
        },
    )
    monkeypatch.setattr(
        "ilc_core.node.readiness_runtime.udp_quic_probe",
        lambda _peer: {"network_quic_udp_probe": "unreachable"},
    )

    report = build_readiness_report(
        config_path=generated.config_path,
        network=True,
        peer="127.0.0.1:7101",
    )

    assert report["readiness_verdict"] == "fail"
    assert "network_quic_udp_probe_not_confirmed" in report["warnings"]


def test_readiness_udp_timeout_warns_without_quic_overclaim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generated = _generated_node(tmp_path)

    monkeypatch.setattr(
        "ilc_core.node.readiness_runtime.tcp_reachability_probe",
        lambda _endpoint: {
            "network_grpc_tcp_latency_ms": 1,
            "network_grpc_tcp_reachable": True,
        },
    )
    monkeypatch.setattr(
        "ilc_core.node.readiness_runtime.udp_quic_probe",
        lambda _peer: {"network_quic_udp_probe": "timeout"},
    )

    report = build_readiness_report(
        config_path=generated.config_path,
        network=True,
        peer="127.0.0.1:7101",
    )

    assert report["readiness_verdict"] == "warn"
    assert "network_quic_udp_probe_not_confirmed" in report["warnings"]


def test_readiness_no_network_or_subprocess_imports() -> None:
    source = Path("ilc_core/node/readiness_runtime.py").read_text(encoding="utf-8")

    assert "subprocess" not in source
    assert "requests" not in source
    assert "urllib.request" not in source
    assert "socket.create_connection" in source
    assert "settimeout" in source


def test_readiness_proposal_identity_note_in_output(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    report = build_readiness_report(config_path=generated.config_path)

    assert report["local_checks"]["proposal_identity_note"] == PROPOSAL_IDENTITY_NOTE


def test_node_check_emits_new_fields(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    check = check_node_config(generated.config_path)

    for key in (
        "endpoint_assertion_host",
        "endpoint_host_is_tailscale_cidr",
        "grpc_listen_is_wildcard",
        "proposal_identity_note",
        "tls_cert_days_remaining",
    ):
        assert key in check


def test_readiness_cli_outputs_json_first_payload(tmp_path: Path) -> None:
    generated = _generated_node(tmp_path)

    result = _run_cli("node", "readiness", "--config", str(generated.config_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["command"] == "node readiness"
    assert payload["ok"] is True
    assert payload["data"]["readiness_verdict"] == "pass"
