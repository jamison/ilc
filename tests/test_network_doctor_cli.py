from __future__ import annotations

import json
import subprocess
import sys

from ilc_core.cli import network_doctor
from ilc_core.network.connectivity_mode import ConnectivityMode, ConnectivityReceipt
from ilc_core.network.nat_probe import NatProbeReport


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
    assert "Connectivity mode diagnostic" in result.stdout
    assert "Read-only unless --enable-upnp is supplied" in result.stdout
    assert "--text" in result.stdout
    assert "--out" in result.stdout
    assert "--probe-observer" in result.stdout
    assert "--relay-url" in result.stdout
    assert "--relay-admission-material" in result.stdout
    assert "--probe-epoch" in result.stdout
    assert "--enable-upnp" in result.stdout
    assert "UPnP IGD has no" in result.stdout
    assert "authentication; any process" in result.stdout


def test_network_doctor_default_json_live_non_mutating_receipt() -> None:
    result = _run_cli("network-doctor")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert payload["command"] == "network-doctor"
    assert data["connectivity_mode"] == "local_only"
    assert data["firewall_mutation_attempted"] is False
    assert data["router_mapping"] is None
    assert data["receipt"]["mode"] == "local_only"
    assert data["receipt"]["probe_epoch"] == 0
    assert data["receipt"]["schema_version"] == "gap_connectivity_mode_runtime_00.v0.1"
    assert "no_ilc_probe_observer_configured" in data["warnings"]
    assert "no_ilc_probe_observer_configured" in result.stderr


def test_network_doctor_text_live_non_mutating_receipt() -> None:
    result = _run_cli("network-doctor", "--text")
    assert result.returncode == 0
    assert result.stdout.startswith("ILC network doctor\n")
    assert "connectivity_mode: local_only" in result.stdout
    assert "warning: no_ilc_probe_observer_configured" in result.stdout


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
    probe_result = network_doctor.ProbeResult(
        has_public_ip=False,
        observed_ip=None,
        observed_port=None,
        relay_available=True,
        validator_participation_enabled=False,
        has_outbound_connectivity=True,
    )
    receipt = ConnectivityReceipt(
        mode=ConnectivityMode.RELAY_REACHABLE,
        observed_endpoint=None,
        relay_endpoint="relay.example:50151",
        probe_observer_agent_id=None,
        probe_epoch=0,
    )
    monkeypatch.setattr(
        network_doctor,
        "_current_probe_report",
        lambda **_: NatProbeReport(
            connectivity_receipt=receipt,
            probe_result=probe_result,
            observer_endpoint_url=None,
            firewall_mutation_attempted=False,
            router_mapping=None,
            attempt_receipts=(),
            warnings=(),
        ),
    )
    payload = network_doctor.build_network_doctor_payload(text=False)
    encoded = json.dumps(payload, sort_keys=True)
    assert payload["connectivity_mode"] == "relay_reachable"
    assert network_doctor.UPNP_RELAY_TIP not in encoded


def test_network_doctor_passes_enable_upnp_to_live_probe(monkeypatch) -> None:
    calls: list[dict[str, object]] = []
    probe_result = network_doctor.ProbeResult(
        has_public_ip=False,
        observed_ip=None,
        observed_port=None,
        relay_available=False,
        validator_participation_enabled=False,
        has_outbound_connectivity=True,
    )
    receipt = ConnectivityReceipt(
        mode=ConnectivityMode.OUTBOUND_ONLY,
        observed_endpoint=None,
        relay_endpoint=None,
        probe_observer_agent_id=None,
        probe_epoch=7,
    )

    def fake_report(**kwargs: object) -> NatProbeReport:
        calls.append(kwargs)
        return NatProbeReport(
            connectivity_receipt=receipt,
            probe_result=probe_result,
            observer_endpoint_url=None,
            firewall_mutation_attempted=False,
            router_mapping=None,
            attempt_receipts=(),
            warnings=(),
        )

    monkeypatch.setattr(network_doctor, "_current_probe_report", fake_report)
    payload = network_doctor.build_network_doctor_payload(
        enable_upnp=True,
        probe_epoch=7,
        probe_observers=("https://observer.example/probe",),
        relay_server_url="https://relay.example",
    )
    assert payload["receipt"]["probe_epoch"] == 7
    assert calls == [
        {
            "attempt_router_mapping": True,
            "probe_epoch": 7,
            "probe_observers": ("https://observer.example/probe",),
            "relay_admission_material": {},
            "relay_server_url": "https://relay.example",
        }
    ]


def test_network_doctor_loads_relay_admission_material(tmp_path, monkeypatch) -> None:
    material_path = tmp_path / "relay_material.json"
    material_path.write_text(
        json.dumps({"agent_id": "a" * 96}, sort_keys=True),
        encoding="utf-8",
    )
    calls: list[dict[str, object]] = []
    probe_result = network_doctor.ProbeResult(
        has_public_ip=False,
        observed_ip=None,
        observed_port=None,
        relay_available=False,
        validator_participation_enabled=False,
        has_outbound_connectivity=True,
    )
    receipt = ConnectivityReceipt(
        mode=ConnectivityMode.OUTBOUND_ONLY,
        observed_endpoint=None,
        relay_endpoint=None,
        probe_observer_agent_id=None,
        probe_epoch=3,
    )

    def fake_report(**kwargs: object) -> NatProbeReport:
        calls.append(kwargs)
        return NatProbeReport(
            connectivity_receipt=receipt,
            probe_result=probe_result,
            observer_endpoint_url=None,
            firewall_mutation_attempted=False,
            router_mapping=None,
            attempt_receipts=(),
            warnings=(),
        )

    monkeypatch.setattr(network_doctor, "_current_probe_report", fake_report)
    network_doctor.build_network_doctor_payload(
        probe_epoch=3,
        relay_admission_material_path=str(material_path),
    )
    assert calls[0]["relay_admission_material"] == {"agent_id": "a" * 96}
