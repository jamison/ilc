from __future__ import annotations

import copy
import hashlib
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
CURRENT_MANIFEST_PATH = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_0422_GAP_PACKAGE_0422_00b_v0.1.json"
)
CURRENT_ENVELOPE_PATH = (
    ROOT / "docs/specs/ilc_core_0422_release_envelopes_GAP_PACKAGE_0422_00b_v0.1.json"
)
INSTALL_SH = ROOT / "tools/install.sh"
VERIFIER_PATH = ROOT / "ilc_core/release/update_signature_verifier.py"
CURRENT_RC_WHEEL_URL = (
    "https://files.pythonhosted.org/packages/30/a3/"
    "dc7c20e0ac7c28f46a8d19df80bef0f6c04d8df98133e28f3bfde6bf1002/"
    "ilc_core-0.4.22-py3-none-any.whl"
)
CURRENT_RC_WHEEL_SHA256 = "07c59b68b8d0b2447f499ddb60fcc6dd62c9a6425021fbd612aa8b6367c776b3"
CURRENT_RC_WHEEL_SIZE = "1495190"
CURRENT_DEFAULT_ENVELOPE_REF = (
    "https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/"
    "ilc_core_0422_release_envelopes_GAP_PACKAGE_0422_00b_v0.1.json"
)


def _manifest() -> dict[str, Any]:
    return load_installable_release_manifest(MANIFEST_PATH)


def _envelope_set() -> dict[str, Any]:
    return json.loads(ENVELOPE_PATH.read_text(encoding="utf-8"))


def _current_manifest() -> dict[str, Any]:
    return load_installable_release_manifest(CURRENT_MANIFEST_PATH)


def _current_envelope_set() -> dict[str, Any]:
    return json.loads(CURRENT_ENVELOPE_PATH.read_text(encoding="utf-8"))


def _envelope_set_for_current_install_sh_inline_verifier() -> dict[str, Any]:
    return _current_envelope_set()


def _wheel_artifact() -> dict[str, Any]:
    for artifact in _manifest()["artifacts"]:
        if artifact["artifact_type"] == "python_wheel":
            return artifact
    raise AssertionError("wheel artifact missing")


def _artifact_by_type(artifact_type: str) -> dict[str, Any]:
    for artifact in _manifest()["artifacts"]:
        if artifact["artifact_type"] == artifact_type:
            return artifact
    raise AssertionError(f"{artifact_type} artifact missing")


def _current_artifact_by_type(artifact_type: str) -> dict[str, Any]:
    for artifact in _current_manifest()["artifacts"]:
        if artifact["artifact_type"] == artifact_type:
            return artifact
    raise AssertionError(f"{artifact_type} artifact missing")


def _install_sh_signature_verifier_source() -> str:
    text = INSTALL_SH.read_text(encoding="utf-8")
    marker = '${RC_SDIST_SIZE}" "${INSTALLER_ROOT}" <<\'PY\''
    marker_index = text.index(marker)
    start = text.index("\n", marker_index) + 1
    end = text.index("\nPY\n", start)
    return text[start:end]


def _run_install_sh_signature_verifier(
    tmp_path: Path,
    *,
    envelope_set: dict[str, Any],
) -> subprocess.CompletedProcess[str]:
    envelope_path = tmp_path / "envelopes.json"
    envelope_path.write_text(
        json.dumps(envelope_set, sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )
    script_path = tmp_path / "install_verifier.py"
    script_path.write_text(_install_sh_signature_verifier_source(), encoding="utf-8")
    script_args = [
        sys.executable,
        str(script_path),
        "/tmp/unused.whl",
        _current_manifest()["release_id"],
        _current_artifact_by_type("python_wheel")["artifact_id"],
        _current_artifact_by_type("python_wheel")["canonical_hash"].removeprefix("sha256:"),
        str(_current_artifact_by_type("python_wheel")["size_bytes"]),
        str(envelope_path),
        PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
        _current_artifact_by_type("python_sdist")["artifact_id"],
        _current_artifact_by_type("python_sdist")["canonical_hash"].removeprefix("sha256:"),
        str(_current_artifact_by_type("python_sdist")["size_bytes"]),
        str(ROOT),
    ]
    return subprocess.run(
        script_args,
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


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


def test_verify_artifact_signature_direct_call_rejects_missing_signature_field() -> None:
    artifact = _wheel_artifact()
    envelope_set = copy.deepcopy(_envelope_set())
    del envelope_set["envelopes"][artifact["artifact_id"]]["signature_hex"]
    with pytest.raises(ValueError, match="release_envelope_missing_field:signature_hex"):
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


def test_ilc_update_verifies_sdist_signature_too(tmp_path: Path) -> None:
    manifest = _manifest()
    manifest["release_envelope_ref"] = "envelopes.json"
    envelope_set = copy.deepcopy(_envelope_set())
    sdist = _artifact_by_type("python_sdist")
    envelope_set["envelopes"][sdist["artifact_id"]]["signature_hex"] = "0" * 128
    (tmp_path / "envelopes.json").write_text(
        json.dumps(envelope_set, sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )
    wheel = _artifact_by_type("python_wheel")
    with pytest.raises(ValueError, match="release_envelope_signature_invalid"):
        cli_main._verify_update_artifact_signature(
            manifest=manifest,
            artifact_id=wheel["artifact_id"],
            artifact_sha256=wheel["canonical_hash"],
            manifest_base_dir=tmp_path,
        )


def test_ilc_update_resolves_relative_envelope_ref_against_manifest_dir(tmp_path: Path) -> None:
    manifest = _manifest()
    manifest["release_envelope_ref"] = "envelopes.json"
    (tmp_path / "envelopes.json").write_text(
        json.dumps(_envelope_set(), sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )
    wheel = _artifact_by_type("python_wheel")
    cli_main._verify_update_artifact_signature(
        manifest=manifest,
        artifact_id=wheel["artifact_id"],
        artifact_sha256=wheel["canonical_hash"],
        manifest_base_dir=tmp_path,
    )


def test_install_sh_verify_signature_flag_and_order() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert "--verify-signature" in text
    hash_check = text.index('if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]')
    signature_check = text.index('python3 - "${TMP_WHEEL}"', hash_check)
    pip_install = text.index('"${TARGET_DIR}/bin/python" -m pip install')
    assert hash_check < signature_check < pip_install


def test_install_sh_inline_manifest_uses_current_artifact_metadata() -> None:
    source = _install_sh_signature_verifier_source()
    assert '"produced_phase": 1628' in source
    assert '"manifest_produced_phase": 1628' in source
    assert '"size_bytes": int(artifact_size)' in source
    assert '"produced_phase": 1627' not in source
    assert 'int("1459734")' not in source


def test_install_sh_verify_signature_fails_closed_without_cryptography(tmp_path: Path) -> None:
    payload = tmp_path / "ilc_core-0.4.22-py3-none-any.whl"
    payload.write_bytes(b"not-a-real-wheel")
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    invite = tmp_path / "invite.json"
    invite.write_text("{}", encoding="utf-8")
    script = INSTALL_SH.read_text(encoding="utf-8")
    script = script.replace(
        f'RC_WHEEL_URL="{CURRENT_RC_WHEEL_URL}"',
        f'RC_WHEEL_URL="{payload.as_uri()}"',
    )
    script = script.replace(
        f'DEFAULT_RC_RELEASE_ENVELOPE_REF="{CURRENT_DEFAULT_ENVELOPE_REF}"',
        f'DEFAULT_RC_RELEASE_ENVELOPE_REF="{ENVELOPE_PATH}"',
    )
    script = script.replace(
        f'RC_WHEEL_SHA256="{CURRENT_RC_WHEEL_SHA256}"',
        f'RC_WHEEL_SHA256="{digest}"',
    )
    script = script.replace(
        f'RC_WHEEL_SIZE="{CURRENT_RC_WHEEL_SIZE}"',
        f'RC_WHEEL_SIZE="{payload.stat().st_size}"',
    )
    script = script.replace(
        'python3 -c "import cryptography"',
        'python3 -c "raise ImportError"',
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
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 1
    assert "install_sh_signature_verification_failed:cryptography_not_available" in result.stderr


def test_install_sh_inline_verifier_rejects_bad_sdist_signature(tmp_path: Path) -> None:
    envelope_set = copy.deepcopy(_envelope_set_for_current_install_sh_inline_verifier())
    sdist = _current_artifact_by_type("python_sdist")
    envelope_set["envelopes"][sdist["artifact_id"]]["signature_hex"] = "0" * 128

    result = _run_install_sh_signature_verifier(tmp_path, envelope_set=envelope_set)

    assert result.returncode != 0
    assert "release_envelope_signature_invalid" in result.stderr


def test_install_sh_inline_verifier_rejects_bad_preimage_algorithm(tmp_path: Path) -> None:
    envelope_set = copy.deepcopy(_envelope_set_for_current_install_sh_inline_verifier())
    wheel = _current_artifact_by_type("python_wheel")
    envelope_set["envelopes"][wheel["artifact_id"]]["signed_preimage_algorithm"] = "sha384"

    result = _run_install_sh_signature_verifier(tmp_path, envelope_set=envelope_set)

    assert result.returncode != 0
    assert "release_envelope_preimage_algorithm_invalid" in result.stderr


def test_install_sh_verify_signature_fails_closed_for_stale_envelope_set(
    tmp_path: Path,
) -> None:
    payload = tmp_path / "ilc_core-0.4.22-py3-none-any.whl"
    payload.write_bytes(b"not-a-real-wheel")
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    invite = tmp_path / "invite.json"
    invite.write_text("{}", encoding="utf-8")
    script = INSTALL_SH.read_text(encoding="utf-8")
    script = script.replace(
        f'RC_WHEEL_URL="{CURRENT_RC_WHEEL_URL}"',
        f'RC_WHEEL_URL="{payload.as_uri()}"',
    )
    script = script.replace(
        f'RC_WHEEL_SHA256="{CURRENT_RC_WHEEL_SHA256}"',
        f'RC_WHEEL_SHA256="{digest}"',
    )
    script = script.replace(
        f'RC_WHEEL_SIZE="{CURRENT_RC_WHEEL_SIZE}"',
        f'RC_WHEEL_SIZE="{payload.stat().st_size}"',
    )
    script = script.replace(
        f'DEFAULT_RC_RELEASE_ENVELOPE_REF="{CURRENT_DEFAULT_ENVELOPE_REF}"',
        f'DEFAULT_RC_RELEASE_ENVELOPE_REF="{ENVELOPE_PATH}"',
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
    assert "release_envelope_set_schema_version_invalid" in result.stderr


def test_no_tls_bypass_in_verifier() -> None:
    text = VERIFIER_PATH.read_text(encoding="utf-8")
    assert "verify=False" not in text
    assert "ssl=False" not in text
    assert "check_hostname=False" not in text
    assert "allow_redirects=False" in text


def test_install_sh_redirect_handler_fails_with_redirect_token() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert "raise HTTPError(req.full_url, code, \"redirect_forbidden\", headers, fp)" in text
    assert "return None" not in text[
        text.index("class NoRedirectHandler") : text.index("def fail", text.index("class NoRedirectHandler"))
    ]
