from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.cli.main import INSTALL_PROBE_OBSERVER_MAX_COUNT
from ilc_core.identity import first_run_provisioning as provisioning
from ilc_core.identity.first_run_provisioning import (
    identity_root,
    invite_pop_payload_ref,
    provision_new_identity,
    record_install_connectivity_receipt,
)
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    sign_invite_pop_digest,
    sign_relay_bootstrap_capsule_digest,
)
from ilc_core.network.relay.relay_server import (
    RelayServerConfig,
    build_relay_bootstrap_record,
    relay_bootstrap_capsule_payload_ref,
    sign_relay_bootstrap_record,
)
from ilc_core.network.relay.relay_client import RelayAdmissionRequest
from ilc_core.network.connectivity_mode import (
    ConnectivityMode,
    ConnectivityReceipt,
    ProbeResult,
)
from ilc_core.network.nat_probe import NatProbeReport
from ilc_core.sidecars.openclaw_invite_bootstrap import build_synthetic_invite_bundle


AGENT_ID_HEX = "8e5a712e4cb2c51893c27ae19afb3455f3efcc66030dc25e13eb1afc2edf397317a0bb2d28a55513a32d7dcc404be3ba"
SIGNING_KEY_HEX = "344dc8b38c3d76ded943ea518dfcd0184c8730f1d1a9a444e0bdd6ecc9742825"
FIXTURE_MANIFEST = Path("tests/fixtures/starmap/core_public_rc_slice_fixture.json")


@pytest.fixture()
def fake_keygen(tmp_path: Path) -> list[str]:
    script = tmp_path / "fake_keygen.py"
    script.write_text(
        "\n".join(
            [
                "import pathlib, sys",
                "out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1])",
                f"out.write_text('{SIGNING_KEY_HEX}\\n', encoding='utf-8')",
                f"print('{AGENT_ID_HEX}')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return [sys.executable, str(script)]


@pytest.fixture()
def install_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    return home


def _bundle() -> dict[str, object]:
    bundle = build_synthetic_invite_bundle()
    bundle["atlas_slice_manifest_witness"] = {"slice_id": "test-slice"}
    bundle["starmap_manifest_payload"] = json.loads(
        FIXTURE_MANIFEST.read_text(encoding="utf-8")
    )
    return bundle


def _write_bundle(path: Path) -> Path:
    path.write_text(
        json.dumps(_bundle(), sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_bundle_payload(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    return path


def _signed_relay_bootstrap_capsule() -> tuple[dict[str, object], str]:
    genesis_secret_key, genesis_agent_id = keypair_from_ikm_hex("47" * 32)
    relay_secret_key, relay_agent_id = keypair_from_ikm_hex("45" * 32)
    record = build_relay_bootstrap_record(
        RelayServerConfig(
            relay_agent_id=relay_agent_id,
            relay_host="relay.ilc.example",
            ssl_certfile="/tmp/relay-cert.pem",
            ssl_keyfile="/tmp/relay-key.pem",
        ),
        issued_epoch=0,
        expires_epoch=4,
        tls_cert_der_sha256="cd" * 32,
    )
    signed_record = sign_relay_bootstrap_record(
        record,
        relay_secret_key_hex=relay_secret_key,
        signing_key_id=relay_agent_id,
    )
    payload = {
        "expires_epoch": 4,
        "issued_epoch": 0,
        "network_id": "public-rc",
        "relay_records": [signed_record],
        "schema_version": "relay_bootstrap_capsule_v0.1",
    }
    payload_ref = relay_bootstrap_capsule_payload_ref(payload)
    return (
        {
            **payload,
            "payload_sha384": payload_ref,
            "signature": sign_relay_bootstrap_capsule_digest(
                secret_key_hex=genesis_secret_key,
                digest_hex=payload_ref,
            ),
            "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
            "signing_key_id": genesis_agent_id,
        },
        genesis_agent_id,
    )


def _args(invite: Path, target: Path, receipt: Path, **overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "enable_upnp": False,
        "force_reprovision": False,
        "from_invite": str(invite),
        "output_receipt": str(receipt),
        "probe_observer": [],
        "relay_admission_material": "",
        "relay_internal_port": 50151,
        "relay_network_id": "public-rc",
        "relay_tls_cert_der_sha256": "",
        "relay_url": "",
        "target_dir": str(target),
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _fake_pop_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pop = tmp_path / "fake_invite_pop.py"
    pop.write_text(
        "\n".join(
            [
                "import sys",
                "sys.stdin.read()",
                "if sys.argv[1] == 'verify':",
                "    print('invite_pop_bls_valid')",
                "else:",
                "    print('" + ("c" * 192) + "')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ILC_ONBOARDING_BLS_POP_COMMAND", f"{sys.executable} {pop}")


def test_install_help_exposes_explicit_upnp_consent_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "install", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--enable-upnp" in result.stdout
    normalized = " ".join(result.stdout.split())
    assert "default install performs no router mutation" in normalized

def test_record_install_connectivity_receipt_success_updates_identity_files(
    tmp_path: Path,
    fake_keygen: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeNatProbeEngine:
        def __init__(self, **kwargs: Any) -> None:
            calls.append(kwargs)

        def run_probe(self, *, attempt_router_mapping: bool, probe_epoch: int) -> NatProbeReport:
            calls.append(
                {
                    "attempt_router_mapping": attempt_router_mapping,
                    "probe_epoch": probe_epoch,
                }
            )
            receipt = ConnectivityReceipt(
                mode=ConnectivityMode.DIRECT_PUBLIC,
                observed_endpoint="203.0.113.10:50151",
                relay_endpoint=None,
                probe_observer_agent_id=None,
                probe_epoch=probe_epoch,
            )
            probe_result = ProbeResult(
                has_public_ip=True,
                observed_ip="203.0.113.10",
                observed_port=50151,
                relay_available=False,
                validator_participation_enabled=False,
                has_outbound_connectivity=True,
            )
            return NatProbeReport(
                connectivity_receipt=receipt,
                probe_result=probe_result,
                observer_endpoint_url="https://observer.ilc.example/probe",
                firewall_mutation_attempted=False,
                router_mapping=None,
                attempt_receipts=(),
                warnings=(),
            )

    calls: list[dict[str, Any]] = []
    import ilc_core.network.nat_probe as nat_probe

    monkeypatch.setattr(nat_probe, "NatProbeEngine", FakeNatProbeEngine)
    provision_new_identity(
        tmp_path,
        invite_id="invite-connectivity",
        keygen_command=fake_keygen,
        emit_warning=False,
    )

    result = record_install_connectivity_receipt(
        tmp_path,
        agent_id=AGENT_ID_HEX,
        epoch=3,
        attempt_router_mapping=True,
        observers=("https://observer.ilc.example/probe",),
        relay_server_url="https://relay.ilc.example:51151",
        relay_admission_material={"agent_id": AGENT_ID_HEX},
    )

    root = identity_root(tmp_path)
    stored = json.loads((root / "connectivity_receipt.json").read_text(encoding="utf-8"))
    onboarding = json.loads((root / "onboarding_receipt.json").read_text(encoding="utf-8"))
    assert calls[0]["observers"] == ("https://observer.ilc.example/probe",)
    assert calls[1] == {"attempt_router_mapping": True, "probe_epoch": 3}
    assert stored["connectivity_mode"] == "direct_public"
    assert stored["connectivity_evidence_status"] == "probe_succeeded"
    assert stored["connectivity_receipt_path"] == str(root / "connectivity_receipt.json")
    assert stored["observed_endpoint"] == "203.0.113.10:50151"
    assert stored["firewall_mutation_attempted"] is False
    assert stored["firewall_mutation_status"] == "confirmed_not_mutated"
    assert stored["connectivity_summary"] == "Detected mode: direct_public at 203.0.113.10:50151"
    assert onboarding["connectivity_receipt_path"] == str(root / "connectivity_receipt.json")
    assert onboarding["connectivity_receipt_sha384"] == stored["connectivity_receipt_sha384"]
    assert result["onboarding_receipt"]["connectivity_mode"] == "direct_public"


def test_record_install_connectivity_receipt_probe_failure_falls_back_to_local_only(
    tmp_path: Path,
    fake_keygen: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingNatProbeEngine:
        def __init__(self, **_kwargs: Any) -> None:
            pass

        def run_probe(self, **_kwargs: Any) -> NatProbeReport:
            raise TimeoutError("synthetic timeout")

    import ilc_core.network.nat_probe as nat_probe

    monkeypatch.setattr(nat_probe, "NatProbeEngine", FailingNatProbeEngine)
    provision_new_identity(
        tmp_path,
        invite_id="invite-connectivity",
        keygen_command=fake_keygen,
        emit_warning=False,
    )

    result = record_install_connectivity_receipt(
        tmp_path,
        agent_id=AGENT_ID_HEX,
        epoch=0,
    )

    receipt = result["connectivity_receipt"]
    assert receipt["connectivity_mode"] == "local_only"
    assert receipt["connectivity_evidence_status"] == "probe_failed_connectivity_unverified"
    assert receipt["observed_endpoint"] is None
    assert receipt["relay_endpoint"] is None
    assert receipt["firewall_mutation_attempted"] is False
    assert receipt["firewall_mutation_status"] == "confirmed_not_mutated"
    assert receipt["nat_probe_report"]["warnings"] == [
        "connectivity_probe_failed:TimeoutError"
    ]


def test_record_install_connectivity_receipt_malformed_probe_report_falls_back(
    tmp_path: Path,
    fake_keygen: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MalformedReport:
        def to_dict(self) -> dict[str, object]:
            return {
                "connectivity_receipt": {
                    "mode": "direct_public",
                    "observed_endpoint": None,
                    "probe_epoch": 0,
                    "probe_observer_agent_id": None,
                    "relay_endpoint": None,
                },
                "firewall_mutation_attempted": False,
            }

    class MalformedNatProbeEngine:
        def __init__(self, **_kwargs: Any) -> None:
            pass

        def run_probe(self, **_kwargs: Any) -> MalformedReport:
            return MalformedReport()

    import ilc_core.network.nat_probe as nat_probe

    monkeypatch.setattr(nat_probe, "NatProbeEngine", MalformedNatProbeEngine)
    provision_new_identity(
        tmp_path,
        invite_id="invite-connectivity",
        keygen_command=fake_keygen,
        emit_warning=False,
    )

    result = record_install_connectivity_receipt(
        tmp_path,
        agent_id=AGENT_ID_HEX,
        epoch=0,
    )

    receipt = result["connectivity_receipt"]
    assert receipt["connectivity_mode"] == "local_only"
    assert receipt["firewall_mutation_attempted"] is False
    assert receipt["firewall_mutation_status"] == "confirmed_not_mutated"
    assert receipt["nat_probe_report"]["warnings"] == [
        "connectivity_probe_failed:ValueError"
    ]


def test_install_from_invite_records_connectivity_without_router_mutation_by_default(
    tmp_path: Path,
    install_home: Path,
    fake_keygen: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier

    _fake_pop_command(tmp_path, monkeypatch)
    monkeypatch.setenv("ILC_ONBOARDING_BLS_KEYGEN_COMMAND", " ".join(fake_keygen))
    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"verified": True, "slice_id": witness["slice_id"]},
    )
    calls: list[dict[str, Any]] = []

    def fake_record(install_dir: Path, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        onboarding_path = identity_root(install_dir) / "onboarding_receipt.json"
        onboarding = json.loads(onboarding_path.read_text(encoding="utf-8"))
        connectivity = {
            "agent_id": kwargs["agent_id"],
            "attempt_router_mapping": kwargs["attempt_router_mapping"],
            "connectivity_evidence_status": "probe_succeeded",
            "connectivity_mode": "local_only",
            "connectivity_receipt_path": str(
                identity_root(install_dir) / "connectivity_receipt.json"
            ),
            "connectivity_receipt_sha384": "d" * 96,
            "connectivity_summary": "Detected mode: local_only",
            "firewall_mutation_attempted": False,
            "firewall_mutation_status": "confirmed_not_mutated",
            "observed_endpoint": None,
            "relay_endpoint": None,
            "schema_version": provisioning.INSTALL_CONNECTIVITY_RECEIPT_VERSION,
        }
        onboarding.update(
            {
                "connectivity_evidence_status": "probe_succeeded",
                "connectivity_mode": "local_only",
                "connectivity_receipt_path": connectivity["connectivity_receipt_path"],
                "connectivity_receipt_sha384": "d" * 96,
                "connectivity_summary": "Detected mode: local_only",
                "firewall_mutation_attempted": False,
                "firewall_mutation_status": "confirmed_not_mutated",
                "observed_endpoint": None,
                "relay_endpoint": None,
            }
        )
        onboarding_path.write_text(
            json.dumps(onboarding, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        return {
            "connectivity_receipt": connectivity,
            "onboarding_receipt": onboarding,
        }

    monkeypatch.setattr(provisioning, "record_install_connectivity_receipt", fake_record)
    invite_path = _write_bundle(tmp_path / "invite.json")
    receipt_path = tmp_path / "install_receipt.json"

    result = cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target", receipt_path)
    )

    written_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert result["connectivity_summary"] == "Detected mode: local_only"
    assert result["connectivity_receipt"]["connectivity_mode"] == "local_only"
    assert result["onboarding_receipt"]["connectivity_mode"] == "local_only"
    assert written_receipt["connectivity_mode"] == "local_only"
    assert written_receipt["firewall_mutation_attempted"] is False
    assert calls[0]["attempt_router_mapping"] is False
    assert calls[0]["relay_server_url"] is None
    assert calls[0]["observers"] == ()
    assert identity_root(install_home).exists()


def test_install_from_invite_passes_explicit_probe_and_relay_options(
    tmp_path: Path,
    install_home: Path,
    fake_keygen: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier

    _fake_pop_command(tmp_path, monkeypatch)
    monkeypatch.setenv("ILC_ONBOARDING_BLS_KEYGEN_COMMAND", " ".join(fake_keygen))
    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"verified": True, "slice_id": witness["slice_id"]},
    )
    material_path = tmp_path / "relay_material.json"
    material_path.write_text(
        json.dumps(
            {
                "agent_id": AGENT_ID_HEX,
                "relay_base_url": "https://relay.ilc.example:51151",
                "tls_cert_der_sha256": "cd" * 32,
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    calls: list[dict[str, Any]] = []

    def fake_record(install_dir: Path, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        onboarding = json.loads(
            (identity_root(install_dir) / "onboarding_receipt.json").read_text(
                encoding="utf-8"
            )
        )
        connectivity = {
            "agent_id": kwargs["agent_id"],
            "attempt_router_mapping": True,
            "connectivity_evidence_status": "probe_succeeded",
            "connectivity_mode": "relay_reachable",
            "connectivity_receipt_path": str(
                identity_root(install_dir) / "connectivity_receipt.json"
            ),
            "connectivity_receipt_sha384": "e" * 96,
            "connectivity_summary": "Detected mode: relay_reachable via relay.example:51151",
            "firewall_mutation_attempted": False,
            "firewall_mutation_status": "confirmed_not_mutated",
            "observed_endpoint": None,
            "relay_endpoint": "relay.example:51151",
            "schema_version": provisioning.INSTALL_CONNECTIVITY_RECEIPT_VERSION,
        }
        onboarding.update(
            {
                "connectivity_evidence_status": "probe_succeeded",
                "connectivity_mode": "relay_reachable",
                "connectivity_receipt_path": connectivity["connectivity_receipt_path"],
                "firewall_mutation_status": "confirmed_not_mutated",
            }
        )
        (identity_root(install_dir) / "onboarding_receipt.json").write_text(
            json.dumps(onboarding, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        return {"connectivity_receipt": connectivity, "onboarding_receipt": onboarding}

    monkeypatch.setattr(provisioning, "record_install_connectivity_receipt", fake_record)
    invite_path = _write_bundle(tmp_path / "invite.json")

    cli_main._run_install_subcommand(
        _args(
            invite_path,
            tmp_path / "target",
            tmp_path / "install_receipt.json",
            enable_upnp=True,
            probe_observer=["https://observer.ilc.example/probe"],
            relay_admission_material=str(material_path),
            relay_url="https://relay.ilc.example:51151",
        )
    )

    assert calls[0]["attempt_router_mapping"] is True
    assert calls[0]["observers"] == ("https://observer.ilc.example/probe",)
    assert calls[0]["relay_server_url"] == "https://relay.ilc.example:51151"
    assert calls[0]["relay_admission_material"] == {
        "agent_id": AGENT_ID_HEX,
        "relay_base_url": "https://relay.ilc.example:51151",
        "tls_cert_der_sha256": "cd" * 32,
    }
    assert identity_root(install_home).exists()


def test_install_builds_relay_admission_material_from_fresh_identity(
    tmp_path: Path,
    install_home: Path,
) -> None:
    secret_key_hex, agent_id = keypair_from_ikm_hex("12" * 32)
    root = identity_root(install_home)
    root.mkdir(parents=True)
    (root / "signing_key.hex").write_text(f"{secret_key_hex}\n", encoding="utf-8")
    (root / "agent_id").write_text(f"{agent_id}\n", encoding="utf-8")
    invite_id = "install-relay-auto-admission-test"
    invite_nullifier = "ab" * 32
    invite_pop_ref = invite_pop_payload_ref(
        agent_id_hex=agent_id,
        invite_nullifier=invite_nullifier,
        invite_id=invite_id,
        epoch=0,
    )
    invite_pop = sign_invite_pop_digest(secret_key_hex, invite_pop_ref)
    args = argparse.Namespace(
        relay_admission_material="",
        relay_internal_port=50152,
        relay_network_id="public-rc",
        relay_tls_cert_der_sha256="cd" * 32,
        relay_url="https://relay.ilc.example:51151",
    )

    material = cli_main._install_relay_admission_material(
        args,
        agent_id=agent_id,
        invite_id=invite_id,
        invite_nullifier=invite_nullifier,
        invite_pop=invite_pop,
        invite_pop_payload_ref_value=invite_pop_ref,
        invite_pop_epoch=0,
    )

    assert material is not None
    assert material["agent_id"] == agent_id
    assert material["requested_internal_port"] == 50152
    assert material["tls_cert_der_sha256"] == "cd" * 32
    assert len(str(material["relay_admission_signature"])) == 192
    request_material = {
        key: value for key, value in material.items() if key != "tls_cert_der_sha256"
    }
    RelayAdmissionRequest(**request_material)


def test_install_from_invite_auto_generates_relay_material_for_connectivity_probe(
    tmp_path: Path,
    install_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier

    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"verified": True, "slice_id": witness["slice_id"]},
    )
    calls: list[dict[str, Any]] = []

    def fake_record(install_dir: Path, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        material = kwargs["relay_admission_material"]
        request_material = {
            key: value
            for key, value in material.items()
            if key != "tls_cert_der_sha256"
        }
        RelayAdmissionRequest(**request_material)
        onboarding_path = identity_root(install_dir) / "onboarding_receipt.json"
        onboarding = json.loads(onboarding_path.read_text(encoding="utf-8"))
        connectivity = {
            "agent_id": kwargs["agent_id"],
            "attempt_router_mapping": False,
            "connectivity_evidence_status": "probe_succeeded",
            "connectivity_mode": "relay_reachable",
            "connectivity_receipt_path": str(
                identity_root(install_dir) / "connectivity_receipt.json"
            ),
            "connectivity_receipt_sha384": "e" * 96,
            "connectivity_summary": "Detected mode: relay_reachable via relay.example:52000",
            "firewall_mutation_attempted": False,
            "firewall_mutation_status": "confirmed_not_mutated",
            "observed_endpoint": None,
            "relay_endpoint": "relay.example:52000",
            "schema_version": provisioning.INSTALL_CONNECTIVITY_RECEIPT_VERSION,
        }
        onboarding.update(
            {
                "connectivity_evidence_status": "probe_succeeded",
                "connectivity_mode": "relay_reachable",
                "connectivity_receipt_path": connectivity["connectivity_receipt_path"],
                "connectivity_receipt_sha384": connectivity["connectivity_receipt_sha384"],
                "connectivity_summary": connectivity["connectivity_summary"],
                "firewall_mutation_attempted": False,
                "firewall_mutation_status": "confirmed_not_mutated",
                "observed_endpoint": None,
                "relay_endpoint": "relay.example:52000",
            }
        )
        onboarding_path.write_text(
            json.dumps(onboarding, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        return {"connectivity_receipt": connectivity, "onboarding_receipt": onboarding}

    monkeypatch.setattr(provisioning, "record_install_connectivity_receipt", fake_record)
    invite_path = _write_bundle(tmp_path / "invite.json")

    result = cli_main._run_install_subcommand(
        _args(
            invite_path,
            tmp_path / "target",
            tmp_path / "install_receipt.json",
            relay_network_id="public-rc",
            relay_tls_cert_der_sha256="cd" * 32,
            relay_url="https://relay.ilc.example:51151",
        )
    )

    material = calls[0]["relay_admission_material"]
    assert result["connectivity_receipt"]["connectivity_mode"] == "relay_reachable"
    assert calls[0]["relay_server_url"] == "https://relay.ilc.example:51151"
    assert calls[0]["internal_port"] == 50151
    assert material["agent_id"] == result["identity_provisioning"]["agent_id"]
    assert material["relay_base_url"] == "https://relay.ilc.example:51151"
    assert material["tls_cert_der_sha256"] == "cd" * 32
    assert len(material["relay_admission_signature"]) == 192


def test_install_from_invite_uses_signed_relay_bootstrap_capsule_without_manual_flags(
    tmp_path: Path,
    install_home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier
    from ilc_core.epoch import genesis_settlement_destination as genesis_destination

    capsule, genesis_agent_id = _signed_relay_bootstrap_capsule()
    monkeypatch.setattr(genesis_destination, "GENESIS_AGENT1_AGENT_ID", genesis_agent_id)
    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"verified": True, "slice_id": witness["slice_id"]},
    )
    calls: list[dict[str, Any]] = []

    def fake_record(install_dir: Path, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        material = kwargs["relay_admission_material"]
        request_material = {
            key: value
            for key, value in material.items()
            if key != "tls_cert_der_sha256"
        }
        RelayAdmissionRequest(**request_material)
        onboarding_path = identity_root(install_dir) / "onboarding_receipt.json"
        onboarding = json.loads(onboarding_path.read_text(encoding="utf-8"))
        connectivity = {
            "agent_id": kwargs["agent_id"],
            "attempt_router_mapping": False,
            "connectivity_evidence_status": "probe_succeeded",
            "connectivity_mode": "relay_reachable",
            "connectivity_receipt_path": str(
                identity_root(install_dir) / "connectivity_receipt.json"
            ),
            "connectivity_receipt_sha384": "e" * 96,
            "connectivity_summary": "Detected mode: relay_reachable via relay.ilc.example:52000",
            "firewall_mutation_attempted": False,
            "firewall_mutation_status": "confirmed_not_mutated",
            "observed_endpoint": None,
            "relay_endpoint": "relay.ilc.example:52000",
            "schema_version": provisioning.INSTALL_CONNECTIVITY_RECEIPT_VERSION,
        }
        onboarding.update(
            {
                "connectivity_evidence_status": "probe_succeeded",
                "connectivity_mode": "relay_reachable",
                "connectivity_receipt_path": connectivity["connectivity_receipt_path"],
                "connectivity_receipt_sha384": connectivity["connectivity_receipt_sha384"],
                "connectivity_summary": connectivity["connectivity_summary"],
                "firewall_mutation_attempted": False,
                "firewall_mutation_status": "confirmed_not_mutated",
                "observed_endpoint": None,
                "relay_endpoint": "relay.ilc.example:52000",
            }
        )
        onboarding_path.write_text(
            json.dumps(onboarding, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        return {"connectivity_receipt": connectivity, "onboarding_receipt": onboarding}

    monkeypatch.setattr(provisioning, "record_install_connectivity_receipt", fake_record)
    bundle = _bundle()
    bundle["relay_bootstrap_capsule"] = capsule
    invite_path = _write_bundle_payload(tmp_path / "invite.json", bundle)

    result = cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target", tmp_path / "install_receipt.json")
    )

    material = calls[0]["relay_admission_material"]
    assert result["connectivity_receipt"]["connectivity_mode"] == "relay_reachable"
    assert calls[0]["relay_server_url"] == "https://relay.ilc.example:51151"
    assert material["relay_base_url"] == "https://relay.ilc.example:51151"
    assert material["tls_cert_der_sha256"] == "cd" * 32


def test_install_rejects_untrusted_relay_bootstrap_capsule(tmp_path: Path) -> None:
    capsule, _genesis_agent_id = _signed_relay_bootstrap_capsule()
    args = argparse.Namespace(
        relay_network_id="public-rc",
        relay_tls_cert_der_sha256="",
        relay_url="",
    )

    with pytest.raises(
        ValueError,
        match="install_relay_bootstrap_capsule_no_verified_records",
    ):
        cli_main._install_relay_bootstrap_selection(
            args,
            invite_bundle={"relay_bootstrap_capsule": capsule},
            current_epoch=0,
        )


def test_install_rejects_untrusted_relay_bootstrap_capsule_even_with_manual_relay_flags(
    tmp_path: Path,
) -> None:
    capsule, _genesis_agent_id = _signed_relay_bootstrap_capsule()
    args = argparse.Namespace(
        relay_admission_material="",
        relay_network_id="public-rc",
        relay_tls_cert_der_sha256="cd" * 32,
        relay_url="https://relay.ilc.example:51151",
    )

    with pytest.raises(
        ValueError,
        match="install_relay_bootstrap_capsule_no_verified_records",
    ):
        cli_main._install_relay_bootstrap_selection(
            args,
            invite_bundle={"relay_bootstrap_capsule": capsule},
            current_epoch=0,
        )


def test_install_prebuilt_relay_material_supplies_selection_without_manual_pin(
    tmp_path: Path,
) -> None:
    material_path = tmp_path / "relay_material.json"
    material_path.write_text(
        json.dumps(
            {
                "relay_base_url": "https://relay.ilc.example:51151",
                "tls_cert_der_sha256": "cd" * 32,
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        relay_admission_material=str(material_path),
        relay_network_id="public-rc",
        relay_tls_cert_der_sha256="",
        relay_url="",
    )

    selection = cli_main._install_relay_bootstrap_selection(
        args,
        invite_bundle={},
        current_epoch=0,
    )

    assert selection == {
        "relay_base_url": "https://relay.ilc.example:51151",
        "relay_admission_material": {
            "relay_base_url": "https://relay.ilc.example:51151",
            "tls_cert_der_sha256": "cd" * 32,
        },
        "tls_cert_der_sha256": "cd" * 32,
    }


def test_install_prebuilt_relay_material_must_match_valid_capsule(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.epoch import genesis_settlement_destination as genesis_destination

    capsule, genesis_agent_id = _signed_relay_bootstrap_capsule()
    monkeypatch.setattr(genesis_destination, "GENESIS_AGENT1_AGENT_ID", genesis_agent_id)
    material_path = tmp_path / "relay_material.json"
    material_path.write_text(
        json.dumps(
            {
                "relay_base_url": "https://other-relay.ilc.example:51151",
                "tls_cert_der_sha256": "cd" * 32,
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(
        relay_admission_material=str(material_path),
        relay_network_id="public-rc",
        relay_tls_cert_der_sha256="",
        relay_url="",
    )

    with pytest.raises(ValueError, match="install_relay_bootstrap_control_url_mismatch"):
        cli_main._install_relay_bootstrap_selection(
            args,
            invite_bundle={"relay_bootstrap_capsule": capsule},
            current_epoch=0,
        )


def test_install_relay_url_without_tls_pin_fails_closed(tmp_path: Path) -> None:
    args = argparse.Namespace(
        relay_admission_material="",
        relay_url="https://relay.ilc.example:51151",
    )

    with pytest.raises(ValueError, match="install_relay_tls_cert_der_sha256_required"):
        cli_main._install_relay_admission_material(
            args,
            agent_id=AGENT_ID_HEX,
            invite_id="invite-1",
            invite_nullifier="ab" * 32,
            invite_pop="c" * 192,
            invite_pop_payload_ref_value="d" * 96,
            invite_pop_epoch=0,
        )


def test_install_from_invite_reuses_validated_prebuilt_relay_material(
    tmp_path: Path,
    install_home: Path,
    fake_keygen: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier
    import ilc_core.cli.network_doctor as network_doctor

    _fake_pop_command(tmp_path, monkeypatch)
    monkeypatch.setenv("ILC_ONBOARDING_BLS_KEYGEN_COMMAND", " ".join(fake_keygen))
    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"verified": True, "slice_id": witness["slice_id"]},
    )
    material = {
        "agent_id": AGENT_ID_HEX,
        "relay_base_url": "https://relay.ilc.example:51151",
        "tls_cert_der_sha256": "cd" * 32,
    }
    material_path = tmp_path / "relay_material.json"
    material_path.write_text(
        json.dumps(material, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    load_count = 0
    real_load_material = network_doctor._load_relay_admission_material

    def counted_load(path_value: str) -> dict[str, Any]:
        nonlocal load_count
        load_count += 1
        if load_count > 1:
            material_path.write_text(
                json.dumps(
                    {
                        "agent_id": AGENT_ID_HEX,
                        "relay_base_url": "https://changed-relay.ilc.example:51151",
                        "tls_cert_der_sha256": "ef" * 32,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
        return real_load_material(path_value)

    monkeypatch.setattr(network_doctor, "_load_relay_admission_material", counted_load)
    calls: list[dict[str, Any]] = []

    def fake_record(install_dir: Path, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        onboarding_path = identity_root(install_dir) / "onboarding_receipt.json"
        onboarding = json.loads(onboarding_path.read_text(encoding="utf-8"))
        connectivity = {
            "agent_id": kwargs["agent_id"],
            "attempt_router_mapping": False,
            "connectivity_evidence_status": "probe_succeeded",
            "connectivity_mode": "relay_reachable",
            "connectivity_receipt_path": str(
                identity_root(install_dir) / "connectivity_receipt.json"
            ),
            "connectivity_receipt_sha384": "e" * 96,
            "connectivity_summary": "Detected mode: relay_reachable via relay.ilc.example:52000",
            "firewall_mutation_attempted": False,
            "firewall_mutation_status": "confirmed_not_mutated",
            "observed_endpoint": None,
            "relay_endpoint": "relay.ilc.example:52000",
            "schema_version": provisioning.INSTALL_CONNECTIVITY_RECEIPT_VERSION,
        }
        onboarding.update(
            {
                "connectivity_evidence_status": "probe_succeeded",
                "connectivity_mode": "relay_reachable",
                "connectivity_receipt_path": connectivity["connectivity_receipt_path"],
                "connectivity_receipt_sha384": connectivity["connectivity_receipt_sha384"],
                "connectivity_summary": connectivity["connectivity_summary"],
                "firewall_mutation_attempted": False,
                "firewall_mutation_status": "confirmed_not_mutated",
                "observed_endpoint": None,
                "relay_endpoint": "relay.ilc.example:52000",
            }
        )
        onboarding_path.write_text(
            json.dumps(onboarding, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        return {"connectivity_receipt": connectivity, "onboarding_receipt": onboarding}

    monkeypatch.setattr(provisioning, "record_install_connectivity_receipt", fake_record)
    invite_path = _write_bundle(tmp_path / "invite.json")

    cli_main._run_install_subcommand(
        _args(
            invite_path,
            tmp_path / "target",
            tmp_path / "install_receipt.json",
            relay_admission_material=str(material_path),
        )
    )

    assert load_count == 1
    assert calls[0]["relay_server_url"] == "https://relay.ilc.example:51151"
    assert calls[0]["relay_admission_material"] == material


def test_load_install_invite_bundle_uses_bounded_path_reader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invite_path = _write_bundle(tmp_path / "invite.json")

    def fail_read_bytes(self: Path) -> bytes:
        raise AssertionError("read_bytes_must_not_be_used_for_install_invite_bundle")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    loaded = cli_main._load_install_invite_bundle(str(invite_path))

    assert loaded["private_invite_nonce"] == _bundle()["private_invite_nonce"]


def test_load_install_invite_bundle_rejects_oversized_path(tmp_path: Path) -> None:
    invite_path = tmp_path / "oversized_invite.json"
    invite_path.write_bytes(b"{" + (b'"x":' + b'"a"' * 600_000) + b"}")

    with pytest.raises(ValueError, match="install_invite_bundle_too_large"):
        cli_main._load_install_invite_bundle(str(invite_path))


def test_install_probe_observers_rejects_unbounded_observer_fanout() -> None:
    args = argparse.Namespace(
        probe_observer=[
            f"https://observer-{index}.ilc.example/probe"
            for index in range(INSTALL_PROBE_OBSERVER_MAX_COUNT + 1)
        ]
    )

    with pytest.raises(ValueError, match="install_probe_observer_count_exceeded"):
        cli_main._install_probe_observers(args)


def test_record_install_connectivity_receipt_upnp_failure_does_not_underclaim_mutation(
    tmp_path: Path,
    fake_keygen: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingNatProbeEngine:
        def __init__(self, **_kwargs: Any) -> None:
            pass

        def run_probe(self, **_kwargs: Any) -> NatProbeReport:
            raise TimeoutError("synthetic timeout")

    import ilc_core.network.nat_probe as nat_probe

    monkeypatch.setattr(nat_probe, "NatProbeEngine", FailingNatProbeEngine)
    provision_new_identity(
        tmp_path,
        invite_id="invite-connectivity",
        keygen_command=fake_keygen,
        emit_warning=False,
    )

    result = record_install_connectivity_receipt(
        tmp_path,
        agent_id=AGENT_ID_HEX,
        epoch=0,
        attempt_router_mapping=True,
    )

    receipt = result["connectivity_receipt"]
    assert receipt["firewall_mutation_attempted"] is False
    assert receipt["firewall_mutation_status"] == "unknown_after_opt_in_probe_failure"
    assert receipt["connectivity_evidence_status"] == "probe_failed_connectivity_unverified"
