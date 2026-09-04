from __future__ import annotations

import copy
import json
import subprocess
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.identity import first_run_provisioning
from ilc_core.release.installable_release_manifest import load_installable_release_manifest
from ilc_core.release.update_signature_verifier import (
    MAX_ENVELOPE_SET_BYTES,
    PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
    fetch_and_validate_envelope_set,
    verify_artifact_signature,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_0415_GAP_INVITE_SHORTCODE_DEPLOY_00_v0.1.json"
)
ENVELOPE_PATH = (
    ROOT / "docs/specs/ilc_core_0415_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json"
)
INSTALL_SH = ROOT / "tools/install.sh"
VERIFIER_PATH = ROOT / "ilc_core/release/update_signature_verifier.py"


def _manifest() -> dict[str, Any]:
    return load_installable_release_manifest(MANIFEST_PATH)


def _envelope_set() -> dict[str, Any]:
    return json.loads(ENVELOPE_PATH.read_text(encoding="utf-8"))


def _wheel_artifact() -> dict[str, Any]:
    for artifact in _manifest()["artifacts"]:
        if artifact["artifact_type"] == "python_wheel":
            return artifact
    raise AssertionError("wheel artifact missing")


def test_fetch_envelope_set_from_local_path() -> None:
    envelope_set = fetch_and_validate_envelope_set(str(ENVELOPE_PATH), manifest=_manifest())
    assert len(envelope_set["envelopes"]) == 2


def test_fetch_envelope_set_rejects_http_url() -> None:
    with pytest.raises(ValueError, match="release_envelope_fetch_insecure_url"):
        fetch_and_validate_envelope_set("http://example.invalid/envelopes.json")


def test_fetch_envelope_set_rejects_https_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    class _RedirectResponse:
        status_code = 302
        headers: dict[str, str] = {}

        def iter_content(self, *, chunk_size: int) -> tuple[bytes, ...]:
            return ()

    def _get(*_args: object, **kwargs: object) -> _RedirectResponse:
        assert kwargs["allow_redirects"] is False
        assert kwargs["verify"] is True
        return _RedirectResponse()

    import requests

    monkeypatch.setattr(requests, "get", _get)
    with pytest.raises(ValueError, match="release_envelope_fetch_redirect_forbidden"):
        fetch_and_validate_envelope_set("https://example.invalid/envelopes.json")


def test_fetch_envelope_set_rejects_oversized(tmp_path: Path) -> None:
    path = tmp_path / "oversized.json"
    path.write_bytes(b"{" + (b'"a":' + b'"b"' * MAX_ENVELOPE_SET_BYTES))
    with pytest.raises(ValueError, match="release_envelope_set_too_large"):
        fetch_and_validate_envelope_set(str(path))


def test_verify_artifact_signature_preimage_mismatch() -> None:
    artifact = _wheel_artifact()
    with pytest.raises(ValueError, match="release_envelope_preimage_mismatch"):
        verify_artifact_signature(
            artifact["artifact_id"],
            "0" * 64,
            _envelope_set(),
            release_id=_manifest()["release_id"],
            expected_signer_public_key_hex=PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
        )


def test_verify_artifact_signature_missing_artifact() -> None:
    with pytest.raises(ValueError, match="release_envelope_missing_artifact"):
        verify_artifact_signature(
            "ilc-artifact:ilc-core-python-missing-0415@phase-1627",
            "0" * 64,
            _envelope_set(),
            release_id="ilc-core-0.4.15",
            expected_signer_public_key_hex=PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
        )


def test_verify_artifact_signature_bad_signature() -> None:
    artifact = _wheel_artifact()
    envelope_set = copy.deepcopy(_envelope_set())
    envelope_set["envelopes"][artifact["artifact_id"]]["signature_hex"] = "0" * 128
    with pytest.raises(ValueError, match="release_envelope_signature_invalid"):
        verify_artifact_signature(
            artifact["artifact_id"],
            artifact["canonical_hash"],
            envelope_set,
            release_id=_manifest()["release_id"],
            expected_signer_public_key_hex=PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
        )


def test_verify_artifact_signature_rejects_untrusted_signer_key() -> None:
    artifact = _wheel_artifact()
    envelope_set = copy.deepcopy(_envelope_set())
    envelope_set["envelopes"][artifact["artifact_id"]]["signer_public_key_hex"] = "a" * 64
    with pytest.raises(ValueError, match="release_envelope_signer_public_key_mismatch"):
        verify_artifact_signature(
            artifact["artifact_id"],
            artifact["canonical_hash"],
            envelope_set,
            release_id=_manifest()["release_id"],
            expected_signer_public_key_hex=PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
        )


def test_verify_artifact_signature_passes_for_committed_envelopes() -> None:
    manifest = _manifest()
    envelope_set = _envelope_set()
    for artifact in manifest["artifacts"]:
        verify_artifact_signature(
            artifact["artifact_id"],
            artifact["canonical_hash"],
            envelope_set,
            release_id=manifest["release_id"],
            expected_signer_public_key_hex=PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
        )


def test_signed_manifest_no_longer_claims_no_release_signing() -> None:
    manifest = _manifest()
    assert "no_release_signing" not in manifest["non_claims"]
    assert {artifact["signing_status"] for artifact in manifest["artifacts"]} == {"signed"}


def test_ilc_update_verify_signature_flag_exists() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "update", "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "--verify-signature" in result.stdout


def test_ilc_update_signature_verification_runs_before_pip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _wheel_artifact()
    payload = b"wheel"
    artifact["canonical_hash"] = (
        "sha256:e3b0c44298fc1c149afbf4c8996fb924"
        "27ae41e4649b934ca495991b7852b855"
    )
    artifact["size_bytes"] = len(payload)
    manifest = _manifest()
    manifest["artifacts"] = [artifact]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    order: list[str] = []

    def _download(_url: str, destination: Path, _size: int) -> None:
        order.append("download")
        destination.write_bytes(b"")

    def _verify(**_kwargs: object) -> None:
        order.append("signature")

    def _run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        order.append("pip" if command[2:4] == ["pip", "install"] else "post-check")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(cli_main, "_download_update_wheel", _download)
    monkeypatch.setattr(cli_main, "_verify_update_artifact_signature", _verify)
    monkeypatch.setattr(cli_main.subprocess, "run", _run)
    monkeypatch.setattr(
        first_run_provisioning,
        "migrate_identity_schema_if_needed",
        lambda _home: {"status": "test_identity_migration_skipped"},
    )
    result = cli_main._run_update_subcommand(
        Namespace(
            channel="rc",
            dry_run=False,
            manifest_path=str(manifest_path),
            manifest_url="",
            verify_signature=True,
            yes=True,
        )
    )
    assert result["status"] == "updated"
    assert result["signature_verification"] == "passed"
    assert order == ["download", "signature", "pip", "post-check"]


def test_install_sh_verify_signature_flag_and_order() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert "--verify-signature" in text
    hash_check = text.index('if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]')
    signature_check = text.index('python3 - "${TMP_WHEEL}"', hash_check)
    pip_install = text.index('"${TARGET_DIR}/bin/python" -m pip install')
    assert hash_check < signature_check < pip_install


def test_install_sh_verify_signature_runs_without_preinstalled_ilc_core(
    tmp_path: Path,
) -> None:
    payload = ROOT / "dist/ilc_core-0.4.15-py3-none-any.whl"
    if not payload.exists():
        pytest.skip("local 0.4.15 wheel not present")
    invite = tmp_path / "invite.json"
    invite.write_text("{}", encoding="utf-8")
    script = INSTALL_SH.read_text(encoding="utf-8")
    script = script.replace(
        'RC_WHEEL_URL="https://files.pythonhosted.org/packages/18/dc/8dfef2e09b2892fb6c8b724e1fd41982dd1ce90d9b82b959a846e3e1ee28/ilc_core-0.4.15-py3-none-any.whl"',
        f'RC_WHEEL_URL="{payload.as_uri()}"',
    )
    script_path = tmp_path / "install.sh"
    script_path.write_text(script, encoding="utf-8")
    script_path.chmod(0o700)

    result = subprocess.run(
        [
            "bash",
            str(script_path),
            "--invite-bundle",
            str(invite),
            "--target-dir",
            str(tmp_path / "venv"),
            "--verify-signature",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode != 0
    assert (
        "install_sh_signature_verified:ilc-artifact:ilc-core-python-wheel-0415@phase-1627"
        in result.stdout
    )


def test_no_tls_bypass_in_verifier() -> None:
    text = VERIFIER_PATH.read_text(encoding="utf-8")
    assert "verify=False" not in text
    assert "ssl=False" not in text
    assert "check_hostname=False" not in text
    assert "allow_redirects=False" in text
