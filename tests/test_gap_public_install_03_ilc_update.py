from __future__ import annotations

import hashlib
import inspect
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
from ilc_core.release.update_runtime import (
    artifact_version,
    enforce_download_size,
    is_already_current,
    select_update_artifact,
    verify_download_hash,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_020_GAP_PUBLIC_INSTALL_01_v0.1.json"
)
UPDATE_RUNTIME_PATH = ROOT / "ilc_core/release/update_runtime.py"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _manifest() -> dict[str, Any]:
    return load_installable_release_manifest(MANIFEST_PATH)


def _wheel_artifact() -> dict[str, Any]:
    return select_update_artifact(_manifest(), "rc")


def _manifest_with_single_artifact(artifact: dict[str, Any], tmp_path: Path) -> Path:
    manifest = _manifest()
    manifest["artifacts"] = [artifact]
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )
    return path


def test_ilc_update_help_discoverable() -> None:
    result = _run_cli("update", "--help")
    assert result.returncode == 0
    assert "--channel" in result.stdout
    assert "--manifest-path" in result.stdout
    assert "--manifest-url" in result.stdout


def test_ilc_update_dry_run_with_local_manifest() -> None:
    result = _run_cli(
        "update",
        "--channel",
        "rc",
        "--manifest-path",
        str(MANIFEST_PATH),
        "--dry-run",
    )
    assert result.returncode == 0, result.stderr
    assert "ilc_update_would_install" in result.stdout
    assert "ilc-artifact:ilc-core-python-wheel@phase-1575" in result.stdout
    assert "https://files.pythonhosted.org/" in result.stdout


def test_ilc_update_invalid_channel_exits_error() -> None:
    result = _run_cli("update", "--channel", "nightly")
    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_select_update_artifact_returns_wheel_for_rc() -> None:
    artifact = _wheel_artifact()
    assert artifact["artifact_type"] == "python_wheel"
    assert artifact["channel"] == "rc"
    assert artifact["platform"] == "any"
    assert artifact["arch"] == "any"


def test_select_update_artifact_raises_for_missing_channel() -> None:
    with pytest.raises(ValueError, match="ilc_update_no_wheel_for_channel:dev"):
        select_update_artifact(_manifest(), "dev")


def test_verify_download_hash_passes_on_correct_hash(tmp_path: Path) -> None:
    path = tmp_path / "payload.whl"
    path.write_bytes(b"known bytes")
    digest = hashlib.sha256(b"known bytes").hexdigest()
    verify_download_hash(path, f"sha256:{digest}")


def test_verify_download_hash_raises_on_wrong_hash(tmp_path: Path) -> None:
    path = tmp_path / "payload.whl"
    path.write_bytes(b"known bytes")
    with pytest.raises(ValueError, match="ilc_update_hash_mismatch"):
        verify_download_hash(path, f"sha256:{'0' * 64}")


def test_is_already_current_returns_false_on_package_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.metadata

    def _missing(_name: str) -> str:
        raise importlib.metadata.PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", _missing)
    assert is_already_current(_wheel_artifact()) is False


def test_is_already_current_returns_true_on_matching_version(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.metadata

    monkeypatch.setattr(importlib.metadata, "version", lambda _name: "0.2.0")
    assert is_already_current(_wheel_artifact()) is True


def test_artifact_version_is_extracted_from_wheel_url() -> None:
    assert artifact_version(_wheel_artifact()) == "0.2.0"


def test_ilc_update_http_manifest_url_rejected() -> None:
    result = _run_cli("update", "--manifest-url", "http://example.com/manifest.json")
    assert result.returncode == 1
    assert "ilc_update_manifest_url_not_https" in result.stderr


def test_ilc_update_manifest_path_rejects_uri_scheme() -> None:
    result = _run_cli("update", "--manifest-path", "file:///tmp/manifest.json")
    assert result.returncode == 1
    assert "ilc_update_manifest_path_must_be_bare_path" in result.stderr


def test_ilc_update_manifest_flags_are_mutually_exclusive() -> None:
    result = _run_cli(
        "update",
        "--manifest-url",
        "https://ilc.network/release/manifest.json",
        "--manifest-path",
        str(MANIFEST_PATH),
    )
    assert result.returncode == 2
    assert "not allowed with argument" in result.stderr


def test_ilc_update_size_cap_enforced() -> None:
    enforce_download_size(110, 100)
    with pytest.raises(ValueError, match="ilc_update_size_exceeded"):
        enforce_download_size(111, 100)


def test_download_update_wheel_enforces_declared_content_length(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Response:
        status = 200
        headers = {"Content-Length": "111"}

        def __enter__(self) -> "_Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self, _size: int) -> bytes:
            return b""

    monkeypatch.setattr(cli_main, "urlopen", lambda *_args, **_kwargs: _Response())

    with pytest.raises(ValueError, match="ilc_update_size_exceeded"):
        cli_main._download_update_wheel(
            "https://files.pythonhosted.org/packages/test/ilc_core-0.4.2-py3-none-any.whl",
            tmp_path / "download.whl",
            100,
        )


def test_ilc_update_non_dry_run_hash_verifies_before_pip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"mock wheel bytes"
    artifact = _wheel_artifact()
    artifact["canonical_hash"] = f"sha256:{hashlib.sha256(payload).hexdigest()}"
    artifact["size_bytes"] = len(payload)
    manifest_path = _manifest_with_single_artifact(artifact, tmp_path)
    call_order: list[str] = []
    pip_install_path: Path | None = None

    def _download(_download_url: str, destination: Path, _expected_size_bytes: int) -> None:
        call_order.append("download")
        destination.write_bytes(payload)

    def _run(
        command: list[str],
        *,
        check: bool,
        timeout: int,
        capture_output: bool = False,
        text: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        nonlocal pip_install_path
        call_order.append("pip" if command[2:4] == ["pip", "install"] else "post-check")
        if command[2:4] == ["pip", "install"]:
            pip_install_path = Path(command[-1])
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(cli_main, "_download_update_wheel", _download)
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
            yes=True,
        )
    )
    assert result["status"] == "updated"
    assert call_order == ["download", "pip", "post-check"]
    assert pip_install_path is not None
    assert pip_install_path.name == "ilc_core-0.2.0-py3-none-any.whl"


def test_ilc_update_rejects_invalid_wheel_filename() -> None:
    with pytest.raises(ValueError, match="ilc_update_wheel_filename_invalid"):
        cli_main._update_wheel_filename_from_url("https://files.pythonhosted.org/packages/x/not-a-wheel.whl")


@pytest.mark.parametrize(
    "url",
    (
        "https://files.pythonhosted.org/packages/x/ilc-core-0.4.4.whl",
        "https://files.pythonhosted.org/packages/x/not-a-real-wheel-name-with-many-parts.whl",
        "https://files.pythonhosted.org/packages/x/evil-1-2-3-4.whl",
    ),
)
def test_ilc_update_rejects_malformed_wheel_filenames(url: str) -> None:
    with pytest.raises(ValueError, match="ilc_update_wheel_filename_invalid"):
        cli_main._update_wheel_filename_from_url(url)


def test_ilc_update_accepts_canonical_ilc_core_wheel_filename() -> None:
    assert (
        cli_main._update_wheel_filename_from_url(
            "https://files.pythonhosted.org/packages/x/ilc_core-0.4.4-py3-none-any.whl?download=1"
        )
        == "ilc_core-0.4.4-py3-none-any.whl"
    )


def test_ilc_update_no_graph_onboarding_calls() -> None:
    handler_source = inspect.getsource(cli_main._run_update_subcommand)
    runtime_source = UPDATE_RUNTIME_PATH.read_text(encoding="utf-8")
    for source in (handler_source, runtime_source):
        for token in ("from-invite", "lmdb", "graph_state", "install --from"):
            assert token not in source


def test_update_runtime_has_no_network_or_subprocess_imports() -> None:
    source = UPDATE_RUNTIME_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "urlopen" not in source
    assert "requests" not in source


def test_update_code_does_not_disable_tls_verification() -> None:
    combined = UPDATE_RUNTIME_PATH.read_text(encoding="utf-8") + inspect.getsource(cli_main)
    for token in ("verify=False", "ssl=False", "check_hostname=False"):
        assert token not in combined


def test_update_runtime_has_no_bare_assert_or_float_arithmetic() -> None:
    source = UPDATE_RUNTIME_PATH.read_text(encoding="utf-8")
    assert "\nassert " not in source
    assert "float(" not in source
