from __future__ import annotations

import io
import json
import subprocess
import sys

import pytest

from ilc_core.cli import network_doctor
from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH
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
    assert "--fetch-peers" in result.stdout
    assert "--bootstrap-seed-peer" in result.stdout
    assert "--bootstrap-bundle-cid" in result.stdout
    assert "--genesis-authority-pubkey-hex" in result.stdout
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


def test_network_doctor_guarded_stub_is_local_only_without_name_error(monkeypatch) -> None:
    monkeypatch.setattr(network_doctor, "CONNECTIVITY_PROBE_RUNTIME_NOT_ACTIVATED", True)

    payload = network_doctor.build_network_doctor_payload()

    assert payload["connectivity_mode"] == "local_only"
    assert payload["receipt"]["mode"] == "local_only"
    assert payload["firewall_mutation_attempted"] is False
    assert payload["warnings"] == [network_doctor.NETWORK_DOCTOR_STUB_WARNING]


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


def test_network_doctor_rejects_oversized_relay_admission_material(tmp_path) -> None:
    material_path = tmp_path / "relay_material.json"
    material_path.write_bytes(b"{" + b'"x":' + b'"a"' * 70_000 + b"}")

    with pytest.raises(
        ValueError,
        match="network_doctor_relay_admission_material_too_large",
    ):
        network_doctor._load_relay_admission_material(str(material_path))  # noqa: SLF001


def test_network_doctor_relay_admission_material_uses_bounded_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reads: list[int] = []

    class BoundedBytesIO(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            reads.append(size)
            return b'{"agent_id":"%s"}' % (b"a" * 96)

    def fake_open(self: object, mode: str = "r", *_args: object, **_kwargs: object) -> BoundedBytesIO:
        assert mode == "rb"
        return BoundedBytesIO()

    monkeypatch.setattr(network_doctor.Path, "open", fake_open)

    assert network_doctor._load_relay_admission_material("relay_material.json") == {
        "agent_id": "a" * 96,
    }
    assert reads == [network_doctor.MAX_RELAY_ADMISSION_MATERIAL_BYTES + 1]


@pytest.mark.parametrize("payload", ["[]", "1", "true", '"string"'])
def test_network_doctor_rejects_non_object_relay_admission_material(
    tmp_path,
    payload: str,
) -> None:
    material_path = tmp_path / "relay_material.json"
    material_path.write_text(payload, encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="network_doctor_relay_admission_material_must_be_object",
    ):
        network_doctor._load_relay_admission_material(str(material_path))  # noqa: SLF001


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_network_doctor_rejects_nonfinite_relay_admission_material(
    tmp_path,
    constant: str,
) -> None:
    material_path = tmp_path / "relay_material.json"
    material_path.write_text(f'{{"value":{constant}}}', encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="network_doctor_relay_admission_material_json_invalid",
    ):
        network_doctor._load_relay_admission_material(str(material_path))  # noqa: SLF001


def test_network_doctor_rejects_finite_float_relay_admission_material(tmp_path) -> None:
    material_path = tmp_path / "relay_material.json"
    material_path.write_text('{"nested":{"value":1.25}}', encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="network_doctor_relay_admission_material_float_forbidden",
    ):
        network_doctor._load_relay_admission_material(str(material_path))  # noqa: SLF001


def test_network_doctor_rejects_deeply_nested_relay_admission_material(tmp_path) -> None:
    material_path = tmp_path / "relay_material.json"
    material_path.write_text('{"nested":' + "[" * 80 + "0" + "]" * 80 + "}", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="network_doctor_relay_admission_material_json_too_deep",
    ):
        network_doctor._load_relay_admission_material(str(material_path))  # noqa: SLF001


def test_network_doctor_bootstrap_fetch_requires_flag() -> None:
    with pytest.raises(ValueError, match="network_doctor_bootstrap_fetch_flag_required"):
        network_doctor.build_network_doctor_payload(
            bootstrap_seed_peer="https://seed.ilc.example:443",
        )


def test_network_doctor_bootstrap_fetch_requires_complete_material() -> None:
    with pytest.raises(
        ValueError,
        match="network_doctor_bootstrap_fetch_material_incomplete",
    ):
        network_doctor.build_network_doctor_payload(
            fetch_peers=True,
            bootstrap_seed_peer="https://seed.ilc.example:443",
            bootstrap_bundle_cid="bafybootstrap",
        )


def test_network_doctor_bootstrap_fetch_empty_pubkey_is_invalid_not_incomplete() -> None:
    with pytest.raises(
        ValueError,
        match="network_doctor_genesis_authority_pubkey_invalid",
    ):
        network_doctor.build_network_doctor_payload(
            fetch_peers=True,
            bootstrap_seed_peer="https://seed.ilc.example:443",
            bootstrap_bundle_cid="bafybootstrap",
            genesis_authority_pubkey_hex="",
        )


def test_network_doctor_bootstrap_fetch_rejects_uppercase_pubkey() -> None:
    with pytest.raises(
        ValueError,
        match="network_doctor_genesis_authority_pubkey_invalid",
    ):
        network_doctor.build_network_doctor_payload(
            fetch_peers=True,
            bootstrap_seed_peer="https://seed.ilc.example:443",
            bootstrap_bundle_cid="bafybootstrap",
            genesis_authority_pubkey_hex="B" * _MLDSA_PK_HEX_LENGTH,
        )


def test_network_doctor_bootstrap_fetch_verifies_before_extract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    calls: list[str] = []
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: {"bundle_cid": "bafybootstrap"},
    )

    def fake_verify(_bundle: dict[str, object], _pubkey: str) -> bool:
        calls.append("verify")
        return False

    def fake_extract(_bundle: dict[str, object]) -> list[str]:
        calls.append("extract")
        return ["https://peer-a.ilc.example:443"]

    monkeypatch.setattr(bootstrap_fetch_runtime, "verify_bootstrap_bundle_signature", fake_verify)
    monkeypatch.setattr(bootstrap_fetch_runtime, "extract_peer_endpoints", fake_extract)

    with pytest.raises(
        ValueError,
        match="network_doctor_bootstrap_bundle_signature_invalid",
    ):
        network_doctor.build_network_doctor_payload(
            fetch_peers=True,
            bootstrap_seed_peer="https://seed.ilc.example:443",
            bootstrap_bundle_cid="bafybootstrap",
            genesis_authority_pubkey_hex="b" * _MLDSA_PK_HEX_LENGTH,
        )

    assert calls == ["verify"]


def test_network_doctor_bootstrap_fetch_caps_peer_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: {"bundle_cid": "bafybootstrap"},
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "verify_bootstrap_bundle_signature",
        lambda _bundle, _pubkey: True,
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "extract_peer_endpoints",
        lambda _bundle: [
            f"https://peer-{index}.ilc.example:443"
            for index in range(network_doctor.MAX_NETWORK_DOCTOR_BOOTSTRAP_FETCH_PEERS + 1)
        ],
    )

    with pytest.raises(
        ValueError,
        match="network_doctor_bootstrap_fetch_peer_endpoints_too_many",
    ):
        network_doctor.build_network_doctor_payload(
            fetch_peers=True,
            bootstrap_seed_peer="https://seed.ilc.example:443",
            bootstrap_bundle_cid="bafybootstrap",
            genesis_authority_pubkey_hex="b" * _MLDSA_PK_HEX_LENGTH,
        )


def test_network_doctor_bootstrap_fetch_success(monkeypatch: pytest.MonkeyPatch) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: {"bundle_cid": "bafybootstrap"},
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "verify_bootstrap_bundle_signature",
        lambda _bundle, _pubkey: True,
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "extract_peer_endpoints",
        lambda _bundle: ["https://peer-a.ilc.example:443"],
    )

    payload = network_doctor.build_network_doctor_payload(
        fetch_peers=True,
        bootstrap_seed_peer="https://seed.ilc.example:443",
        bootstrap_bundle_cid="bafybootstrap",
        genesis_authority_pubkey_hex="b" * _MLDSA_PK_HEX_LENGTH,
    )

    assert payload["bootstrap_fetch"] == {
        "bundle_cid": "bafybootstrap",
        "peer_count": 1,
        "peer_endpoints": ["https://peer-a.ilc.example:443"],
        "seed_peer_endpoint": "https://seed.ilc.example:443",
        "status": "fetched",
    }
