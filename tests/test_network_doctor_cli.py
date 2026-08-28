from __future__ import annotations

import json
import subprocess
import sys

from ilc_core.cli import network_doctor
from ilc_core.network.connectivity_mode import ConnectivityMode, ConnectivityReceipt


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_network_doctor_help_exits_zero() -> None:
    result = _run_cli("network-doctor", "--help")
    assert result.returncode == 0
    assert "Read-only connectivity mode diagnostic" in result.stdout
    assert "--text" in result.stdout
    assert "--out" in result.stdout


def test_network_doctor_default_json_stub_receipt() -> None:
    result = _run_cli("network-doctor")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert payload["command"] == "network-doctor"
    assert data["connectivity_mode"] == "outbound_only"
    assert data["receipt"]["mode"] == "outbound_only"
    assert data["receipt"]["probe_epoch"] == 0
    assert data["receipt"]["schema_version"] == "gap_connectivity_mode_runtime_00.v0.1"
    assert network_doctor.NETWORK_DOCTOR_STUB_WARNING in data["warnings"]
    assert network_doctor.NETWORK_DOCTOR_STUB_WARNING in result.stderr


def test_network_doctor_text_stub_receipt() -> None:
    result = _run_cli("network-doctor", "--text")
    assert result.returncode == 0
    assert result.stdout.startswith("ILC network doctor\n")
    assert "connectivity_mode: outbound_only" in result.stdout
    assert "warning: CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED=True" in result.stdout


def test_network_doctor_out_writes_canonical_receipt(tmp_path) -> None:
    receipt_path = tmp_path / "receipt.json"
    result = _run_cli("network-doctor", "--out", str(receipt_path))
    assert result.returncode == 0
    written = receipt_path.read_bytes()
    assert written.startswith(b'{"mode":')
    assert written.endswith(b"\n")
    assert json.loads(written) == json.loads(result.stdout)["data"]["receipt"]


def test_upnp_tip_present_for_relay_reachable_text() -> None:
    receipt = ConnectivityReceipt(
        mode=ConnectivityMode.RELAY_REACHABLE,
        observed_endpoint=None,
        relay_endpoint="relay.example:50151",
        probe_observer_agent_id=None,
        probe_epoch=0,
    )
    rendered = network_doctor._format_network_doctor_text(  # noqa: SLF001
        receipt,
        [],
    )
    assert network_doctor.UPNP_RELAY_TIP in rendered
    assert "--enable-upnp" in rendered
    assert "Security note: UPnP port mapping" in rendered


def test_upnp_tip_absent_for_non_relay_text_modes() -> None:
    receipt = ConnectivityReceipt(
        mode=ConnectivityMode.OUTBOUND_ONLY,
        observed_endpoint=None,
        relay_endpoint=None,
        probe_observer_agent_id=None,
        probe_epoch=0,
    )
    rendered = network_doctor._format_network_doctor_text(  # noqa: SLF001
        receipt,
        [],
    )
    assert network_doctor.UPNP_RELAY_TIP not in rendered
    assert "--enable-upnp" not in rendered


def test_upnp_tip_absent_in_json_even_when_relay_reachable(monkeypatch) -> None:
    monkeypatch.setattr(
        network_doctor,
        "_current_probe_result",
        lambda: network_doctor.ProbeResult(
            has_public_ip=False,
            observed_ip=None,
            observed_port=None,
            relay_available=True,
            validator_participation_enabled=False,
            has_outbound_connectivity=True,
        ),
    )
    payload = network_doctor.build_network_doctor_payload(text=False)
    encoded = json.dumps(payload, sort_keys=True)
    assert payload["connectivity_mode"] == "relay_reachable"
    assert network_doctor.UPNP_RELAY_TIP not in encoded
