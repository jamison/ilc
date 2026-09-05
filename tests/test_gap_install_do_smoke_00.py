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

    with pytest.raises(RuntimeError, match="poll_failed"):
        tool.run_remote_smoke(config)
    assert destroyed == [777]


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
