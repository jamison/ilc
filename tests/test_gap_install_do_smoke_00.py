from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_tool():
    path = Path(__file__).resolve().parents[1] / "tools" / "do_install_smoke.py"
    spec = importlib.util.spec_from_file_location("_do_install_smoke", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_stable_json_rejects_nan() -> None:
    tool = _load_tool()
    with pytest.raises(ValueError):
        tool.stable_json({"x": float("nan")})


def test_atomic_write_json_uses_canonical_private_file(tmp_path: Path) -> None:
    tool = _load_tool()
    out = tmp_path / "receipt.json"
    tool.atomic_write_json(out, {"b": 2, "a": 1})
    assert out.read_text() == '{"a":1,"b":2}\n'
    assert out.stat().st_mode & 0o777 == 0o600


def test_sha_precheck_matches_installer_and_receipt(tmp_path: Path) -> None:
    tool = _load_tool()
    installer = tmp_path / "install.sh"
    receipt = tmp_path / "build.json"
    installer.write_text('RC_WHEEL_SHA256="abc123"\n', encoding="utf-8")
    receipt.write_text(json.dumps({"artifacts": {"wheel": {"sha256": "abc123"}}}), encoding="utf-8")
    assert tool.verify_sha_precheck(installer, receipt) == "abc123"


def test_sha_precheck_matches_flattened_fix2_build_receipt(tmp_path: Path) -> None:
    tool = _load_tool()
    installer = tmp_path / "install.sh"
    receipt = tmp_path / "build.json"
    installer.write_text('RC_WHEEL_SHA256="abc123"\n', encoding="utf-8")
    receipt.write_text(json.dumps({"wheel_sha256": "abc123"}), encoding="utf-8")
    assert tool.verify_sha_precheck(installer, receipt) == "abc123"


def test_sha_precheck_rejects_mismatch(tmp_path: Path) -> None:
    tool = _load_tool()
    installer = tmp_path / "install.sh"
    receipt = tmp_path / "build.json"
    installer.write_text('RC_WHEEL_SHA256="abc123"\n', encoding="utf-8")
    receipt.write_text(json.dumps({"artifacts": {"wheel": {"sha256": "def456"}}}), encoding="utf-8")
    with pytest.raises(ValueError, match="install_sh_build_receipt_sha256_mismatch"):
        tool.verify_sha_precheck(installer, receipt)


def test_missing_invite_bundle_hard_stops_before_droplet(tmp_path: Path) -> None:
    tool = _load_tool()
    installer = tmp_path / "install.sh"
    build_receipt = tmp_path / "build.json"
    envelope = tmp_path / "envelope.json"
    installer.write_text('RC_WHEEL_SHA256="abc123"\n', encoding="utf-8")
    build_receipt.write_text(json.dumps({"artifacts": {"wheel": {"sha256": "abc123"}}}), encoding="utf-8")
    envelope.write_text("{}", encoding="utf-8")
    config = tool.SmokeConfig(
        token="",
        ssh_key_id="",
        ssh_private_key_path=tmp_path / "missing-key",
        invite_bundle_path=tmp_path / "missing-invite.json",
        installer_path=installer,
        build_receipt_path=build_receipt,
        release_envelope_path=envelope,
        dry_run=True,
    )
    with pytest.raises(ValueError, match="invite_bundle_missing"):
        tool.validate_preconditions(config)


def test_consensus_binary_metadata_from_install_sh(tmp_path: Path) -> None:
    tool = _load_tool()
    installer = tmp_path / "install.sh"
    installer.write_text(
        "\n".join(
            [
                'CONSENSUS_BIN_URL="https://github.com/jamison/ilc/releases/download/v0.4.16/ilc-consensus-linux-x86_64-v0.4.16.tar.gz"',
                'CONSENSUS_BIN_SHA256="' + "a" * 64 + '"',
                'CONSENSUS_BIN_SIZE="4304398"',
            ]
        ),
        encoding="utf-8",
    )

    metadata = tool.consensus_binary_metadata_from_install_sh(installer)

    assert metadata["url"].endswith("ilc-consensus-linux-x86_64-v0.4.16.tar.gz")
    assert metadata["sha256"] == "a" * 64
    assert metadata["size"] == "4304398"


def test_signed_0417_smoke_uses_release_signature_verification() -> None:
    tool = _load_tool()
    assert tool.EXPECTED_ILC_CORE_VERSION == "0.4.17"
    assert tool.VERIFY_SIGNATURE_DURING_SMOKE is True
    assert "0417" in str(tool.DEFAULT_RELEASE_ENVELOPE_PATH)


def test_remote_diagnostic_commands_match_cli_shapes() -> None:
    source = (Path(__file__).resolve().parents[1] / "tools" / "do_install_smoke.py").read_text(
        encoding="utf-8"
    )
    assert "ilc_core.cli.main doctor 2>&1" in source
    assert "ilc_core.cli.main network-doctor --json 2>&1" in source
    assert "ilc_core.cli.main ccss status 2>&1" in source
    assert "ilc_core.cli.main ccss status --json" not in source
    assert "ilc_core.cli.main sidecar list 2>&1" in source
    assert "ilc_core.cli.main sidecar list --json" not in source


def test_run_ssh_quotes_remote_bash_payload(monkeypatch, tmp_path: Path) -> None:
    tool = _load_tool()
    config = tool.SmokeConfig(
        token="",
        ssh_key_id="",
        ssh_private_key_path=tmp_path / "key",
        invite_bundle_path=tmp_path / "invite.json",
        dry_run=True,
    )
    captured: list[str] = []

    def fake_run_local(args, *, timeout=120):
        import subprocess

        captured.extend(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(tool, "run_local", fake_run_local)

    tool.run_ssh(config, "203.0.113.9", "chmod 700 /tmp/ilc_install.sh && echo ok")

    assert captured[-3:] == ["bash", "-lc", "'chmod 700 /tmp/ilc_install.sh && echo ok'"]


def test_consensus_binary_metadata_rejects_insecure_url(tmp_path: Path) -> None:
    tool = _load_tool()
    installer = tmp_path / "install.sh"
    installer.write_text(
        "\n".join(
            [
                'CONSENSUS_BIN_URL="http://example.invalid/ilc-consensus-linux-x86_64-v0.4.16.tar.gz"',
                'CONSENSUS_BIN_SHA256="' + "a" * 64 + '"',
                'CONSENSUS_BIN_SIZE="4304398"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="consensus_binary_url_not_https"):
        tool.consensus_binary_metadata_from_install_sh(installer)


def test_blocked_receipt_is_redacted(tmp_path: Path) -> None:
    tool = _load_tool()
    config = tool.SmokeConfig(
        token="not-recorded",
        ssh_key_id="123",
        ssh_private_key_path=tmp_path / "identity-key",
        invite_bundle_path=tmp_path / "invite.json",
        dry_run=True,
    )
    receipt = tool.blocked_receipt(
        config,
        reason="install_sh_consensus_binary_metadata_missing",
        wheel_sha256="abc123",
        consensus_binary_metadata={
            "url": "https://example.invalid/a.tgz",
            "sha256": "a" * 64,
            "size": "1",
        },
    )
    tool.validate_receipt_redacted(receipt)
    assert receipt["blocked_before_droplet_create"] is True
    assert receipt["droplet_destroyed"] is True
    assert receipt["rust_binary_service_user_check"] == "fail"


def test_destroy_runs_in_finally(monkeypatch, tmp_path: Path) -> None:
    tool = _load_tool()
    invite = tmp_path / "invite.json"
    installer = tmp_path / "install.sh"
    build_receipt = tmp_path / "build.json"
    envelope = tmp_path / "envelope.json"
    invite.write_text("{}", encoding="utf-8")
    installer.write_text(
        "\n".join(
            [
                'RC_WHEEL_SHA256="abc123"',
                'CONSENSUS_BIN_URL="https://github.com/jamison/ilc/releases/download/v0.4.16/ilc-consensus-linux-x86_64-v0.4.16.tar.gz"',
                'CONSENSUS_BIN_SHA256="' + "a" * 64 + '"',
                'CONSENSUS_BIN_SIZE="4304398"',
            ]
        ),
        encoding="utf-8",
    )
    build_receipt.write_text(json.dumps({"artifacts": {"wheel": {"sha256": "abc123"}}}), encoding="utf-8")
    envelope.write_text("{}", encoding="utf-8")
    config = tool.SmokeConfig(
        token="token",
        ssh_key_id="123",
        ssh_private_key_path=tmp_path / "key",
        invite_bundle_path=invite,
        installer_path=installer,
        build_receipt_path=build_receipt,
        release_envelope_path=envelope,
        dry_run=True,
    )
    destroyed: list[int] = []

    monkeypatch.setattr(tool, "create_droplet", lambda _config, _name: (777, {"droplet": {"id": 777}}))

    def fail_poll(_config, _droplet_id):
        raise RuntimeError("poll_failed")

    monkeypatch.setattr(tool, "poll_droplet", fail_poll)
    monkeypatch.setattr(tool, "destroy_droplet", lambda _config, droplet_id: (destroyed.append(droplet_id) or True, "deleted"))

    receipt = tool.run_remote_smoke(config)

    assert destroyed == [777]
    assert receipt["blocker"] == "RuntimeError:poll_failed"
    assert receipt["droplet"]["id"] == "777"
    assert receipt["droplet"]["ipv4"] is None
    assert receipt["droplet_destroyed"] is True
    assert receipt["install_result"] == "fail"


def test_install_failure_preserves_live_failure_evidence(monkeypatch, tmp_path: Path) -> None:
    import subprocess

    tool = _load_tool()
    invite = tmp_path / "invite.json"
    installer = tmp_path / "install.sh"
    build_receipt = tmp_path / "build.json"
    envelope = tmp_path / "envelope.json"
    invite.write_text("{}", encoding="utf-8")
    installer.write_text(
        "\n".join(
            [
                'RC_WHEEL_SHA256="abc123"',
                'CONSENSUS_BIN_URL="https://github.com/jamison/ilc/releases/download/v0.4.16/ilc-consensus-linux-x86_64-v0.4.16.tar.gz"',
                'CONSENSUS_BIN_SHA256="' + "a" * 64 + '"',
                'CONSENSUS_BIN_SIZE="4304398"',
            ]
        ),
        encoding="utf-8",
    )
    build_receipt.write_text(json.dumps({"artifacts": {"wheel": {"sha256": "abc123"}}}), encoding="utf-8")
    envelope.write_text("{}", encoding="utf-8")
    config = tool.SmokeConfig(
        token="token",
        ssh_key_id="123",
        ssh_private_key_path=tmp_path / "key",
        invite_bundle_path=invite,
        installer_path=installer,
        build_receipt_path=build_receipt,
        release_envelope_path=envelope,
        dry_run=True,
    )
    destroyed: list[int] = []

    monkeypatch.setattr(tool, "create_droplet", lambda _config, _name: (777, {"droplet": {"id": 777}}))
    monkeypatch.setattr(
        tool,
        "poll_droplet",
        lambda _config, _droplet_id: {
            "droplet": {
                "status": "active",
                "networks": {"v4": [{"type": "public", "ip_address": "203.0.113.9"}]},
            }
        },
    )
    monkeypatch.setattr(tool, "wait_for_ssh", lambda _config, _ipv4: None)
    monkeypatch.setattr(
        tool,
        "copy_to_remote",
        lambda _config, _local, _ipv4, _remote: subprocess.CompletedProcess([], 0, "", ""),
    )
    monkeypatch.setattr(tool, "destroy_droplet", lambda _config, droplet_id: (destroyed.append(droplet_id) or True, "deleted"))

    def fake_run_ssh(_config, _ipv4, command, *, timeout=600):
        if "remote_os_prerequisites_ready" in command:
            return subprocess.CompletedProcess([], 0, "remote_os_prerequisites_ready\n", "")
        if command.startswith("chmod 700 "):
            return subprocess.CompletedProcess([], 0, "", "")
        if "--invite-bundle" in command:
            return subprocess.CompletedProcess([], 1, "install stdout sentinel", "install stderr sentinel")
        raise AssertionError(f"unexpected ssh command after install failure: {command}")

    monkeypatch.setattr(tool, "run_ssh", fake_run_ssh)

    receipt = tool.run_remote_smoke(config)

    assert destroyed == [777]
    assert receipt["blocker"] == "RuntimeError:install_failed:1"
    assert receipt["droplet"]["id"] == "777"
    assert receipt["droplet"]["ipv4"] == "203.0.113.9"
    assert receipt["install_stdout"] == "install stdout sentinel"
    assert receipt["install_stderr"] == "install stderr sentinel"
    assert receipt["invite_smoke_attempted"] is True
    assert receipt["droplet_destroyed"] is True
    assert receipt["install_result"] == "fail"


def test_destroy_failure_forces_phase_failure(monkeypatch, tmp_path: Path) -> None:
    tool = _load_tool()
    receipt_path = tmp_path / "receipt.json"
    config = tool.SmokeConfig(
        token="",
        ssh_key_id="",
        ssh_private_key_path=tmp_path / "key",
        invite_bundle_path=tmp_path / "invite.json",
        receipt_path=receipt_path,
        dry_run=True,
    )
    receipt = {
        "install_result": "pass",
        "invite_smoke_result": "pass",
        "droplet_destroyed": False,
    }
    monkeypatch.setattr(sys, "argv", ["do_install_smoke.py"])
    monkeypatch.setattr(tool, "load_config_from_env", lambda dry_run=False: config)
    monkeypatch.setattr(tool, "run_remote_smoke", lambda _config: receipt)

    assert tool.main() == 1
    assert receipt_path.is_file()
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["droplet_destroyed"] is False


def test_install_sh_release_envelope_override_dry_run() -> None:
    import subprocess

    proc = subprocess.run(
        [
            "bash",
            "tools/install.sh",
            "--dry-run",
            "--invite-bundle",
            "/tmp/example.json",
            "--verify-signature",
        ],
        check=True,
        text=True,
        capture_output=True,
        env={"ILC_INSTALL_RELEASE_ENVELOPE_REF": "/tmp/envelope.json", "PATH": "/bin:/usr/bin:/usr/local/bin"},
    )
    assert "verify_signature=true" in proc.stdout
    assert "RC_RELEASE_ENVELOPE_REF=/tmp/envelope.json" in proc.stdout
