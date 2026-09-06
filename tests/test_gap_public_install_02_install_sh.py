from __future__ import annotations

import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from ilc_core.release.install_sh_manifest_sync import verify_install_sh_manifest_sync


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = ROOT / "tools" / "install.sh"
MANIFEST = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_0416_GAP_CONSENSUS_BINARY_DEPLOY_00_v0.1.json"
)
EXPECTED_URL = (
    "https://files.pythonhosted.org/packages/2f/f4/"
    "d87d5575c32f4f03d3be9f420740e1dd62e11c96a6c7c2d25380fb900278/"
    "ilc_core-0.4.16-py3-none-any.whl"
)
EXPECTED_SHA256 = "c5ddec63bc5ed446ca08cec1bc9b714fed66b94ab84981ac8f9f4bc1397cfc14"
EXPECTED_SIZE = "1459734"
EXPECTED_CONSENSUS_URL = (
    "https://github.com/jamison/ilc/releases/download/v0.4.16/"
    "ilc-consensus-linux-x86_64-v0.4.16.tar.gz"
)
EXPECTED_CONSENSUS_SHA256 = "adde50e924c1ac0e0259998b29ef2778f4a4a7a8b4dfbfed72c206ca9f20bc42"
EXPECTED_CONSENSUS_SIZE = "4304398"


def _run_install_sh(*args: str, path: Path = INSTALL_SH) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(path), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _copy_script(tmp_path: Path, *, replacements: dict[str, str]) -> Path:
    script = INSTALL_SH.read_text(encoding="utf-8")
    for old, new in replacements.items():
        script = script.replace(old, new)
    path = tmp_path / "install.sh"
    path.write_text(script, encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    return path


def test_install_sh_exists_and_is_executable() -> None:
    assert INSTALL_SH.exists()
    assert os.access(INSTALL_SH, os.X_OK)


def test_install_sh_dry_run_exits_zero() -> None:
    result = _run_install_sh(
        "--channel",
        "rc",
        "--dry-run",
        "--invite-bundle",
        "/tmp/example-invite.json",
    )
    assert result.returncode == 0
    assert result.stderr == ""
    assert f"RC_WHEEL_URL={EXPECTED_URL}" in result.stdout
    assert f"RC_WHEEL_SHA256={EXPECTED_SHA256}" in result.stdout
    assert "invite_bundle=/tmp/example-invite.json" in result.stdout
    assert f"CONSENSUS_BIN_URL={EXPECTED_CONSENSUS_URL}" in result.stdout
    assert f"CONSENSUS_BIN_SHA256={EXPECTED_CONSENSUS_SHA256}" in result.stdout
    assert f"CONSENSUS_BIN_SIZE={EXPECTED_CONSENSUS_SIZE}" in result.stdout


def test_install_sh_dry_run_records_connectivity_options() -> None:
    result = _run_install_sh(
        "--channel",
        "rc",
        "--dry-run",
        "--invite-bundle",
        "/tmp/example-invite.json",
        "--relay-url",
        "https://relay.ilc.example:51151",
        "--relay-tls-cert-der-sha256",
        "a" * 64,
        "--relay-network-id",
        "public-rc",
        "--relay-internal-port",
        "50152",
        "--probe-observer",
        "https://observer.ilc.example/probe",
        "--enable-upnp",
    )

    assert result.returncode == 0
    assert "relay_url=https://relay.ilc.example:51151" in result.stdout
    assert f"relay_tls_cert_der_sha256={'a' * 64}" in result.stdout
    assert "relay_network_id=public-rc" in result.stdout
    assert "relay_internal_port=50152" in result.stdout
    assert "probe_observer=https://observer.ilc.example/probe" in result.stdout
    assert "enable_upnp=true" in result.stdout


def test_install_sh_usage_lists_relay_internal_port() -> None:
    result = _run_install_sh("--help")

    assert result.returncode == 0
    assert "--relay-internal-port PORT" in result.stderr


def test_install_sh_rejects_missing_connectivity_option_values() -> None:
    result = _run_install_sh(
        "--dry-run",
        "--invite-bundle",
        "/tmp/example-invite.json",
        "--relay-url",
    )

    assert result.returncode == 2
    assert "install_sh_missing_relay_url_value" in result.stderr


def test_install_sh_unsupported_channel_exits_error() -> None:
    result = _run_install_sh("--channel", "stable")
    assert result.returncode == 1
    assert "install_sh_channel_not_embedded:stable" in result.stderr


def test_install_sh_dev_channel_exits_error() -> None:
    result = _run_install_sh(
        "--channel",
        "dev",
        "--dry-run",
        "--invite-bundle",
        "/tmp/example-invite.json",
    )
    assert result.returncode == 1
    assert "install_sh_channel_not_embedded:dev" in result.stderr


def test_install_sh_missing_invite_bundle_required() -> None:
    result = _run_install_sh("--dry-run")
    assert result.returncode == 2
    assert "install_sh_invite_bundle_or_code_required" in result.stderr


def test_install_sh_no_onboard_flag_is_not_public_install_bypass() -> None:
    result = _run_install_sh("--dry-run", "--no-onboard")
    assert result.returncode == 2
    assert "install_sh_unknown_argument:--no-onboard" in result.stderr


def test_install_sh_target_dir_dry_run_records_target(tmp_path: Path) -> None:
    target = tmp_path / "venv"
    result = _run_install_sh(
        "--dry-run",
        "--invite-bundle",
        "/tmp/example-invite.json",
        "--target-dir",
        str(target),
    )
    assert result.returncode == 0
    assert f"target_dir={target}" in result.stdout


def test_install_sh_invite_bundle_not_found_exits_1(tmp_path: Path) -> None:
    result = _run_install_sh("--invite-bundle", str(tmp_path / "missing.json"))
    assert result.returncode == 1
    assert "install_sh_invite_bundle_not_found" in result.stderr


def test_install_sh_rejects_existing_non_venv_target_before_download(
    tmp_path: Path,
) -> None:
    target = tmp_path / "not-a-venv"
    target.mkdir()
    (target / "keep.txt").write_text("do not contaminate", encoding="utf-8")
    invite = tmp_path / "invite.json"
    invite.write_text("{}", encoding="utf-8")

    result = _run_install_sh("--invite-bundle", str(invite), "--target-dir", str(target))

    assert result.returncode == 1
    assert "install_sh_target_dir_exists_not_venv" in result.stderr


def test_install_sh_rejects_existing_venv_without_python(tmp_path: Path) -> None:
    target = tmp_path / "broken-venv"
    target.mkdir()
    (target / "pyvenv.cfg").write_text("home = /usr/bin\n", encoding="utf-8")
    invite = tmp_path / "invite.json"
    invite.write_text("{}", encoding="utf-8")

    result = _run_install_sh("--invite-bundle", str(invite), "--target-dir", str(target))

    assert result.returncode == 1
    assert "install_sh_target_venv_python_missing" in result.stderr


def test_install_sh_hash_mismatch_exits_error(tmp_path: Path) -> None:
    payload = tmp_path / "ilc_core-0.4.15-py3-none-any.whl"
    payload.write_bytes(b"not a wheel")
    invite = tmp_path / "invite.json"
    invite.write_text("{}", encoding="utf-8")
    bad_script = _copy_script(
        tmp_path,
        replacements={
            EXPECTED_URL: payload.as_uri(),
            f'RC_WHEEL_SIZE="{EXPECTED_SIZE}"': f'RC_WHEEL_SIZE="{payload.stat().st_size}"',
        },
    )
    result = _run_install_sh("--invite-bundle", str(invite), path=bad_script)
    assert result.returncode == 1
    assert "install_sh_hash_verification_failed" in result.stderr


def test_install_sh_manifest_sync_passes() -> None:
    verify_install_sh_manifest_sync(INSTALL_SH, MANIFEST)


def test_install_sh_consensus_binary_download_is_bounded_and_verified() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")

    assert 'CONSENSUS_BIN_URL="' in text
    assert 'CONSENSUS_BIN_SHA256="' in text
    assert 'CONSENSUS_BIN_SIZE="' in text
    assert "CONSENSUS_BIN_SIZE_CAP" in text
    assert "response.read(65536)" in text
    assert "install_sh_consensus_binary_hash_verification_failed" in text
    assert "tarfile.open" in text
    assert "tar xzf" not in text
    assert "curl | tar" not in text


def _install_sh_consensus_extractor_source() -> str:
    text = INSTALL_SH.read_text(encoding="utf-8")
    marker = 'python3 - "${CONSENSUS_TARBALL}" "${CONSENSUS_BIN_INSTALL_DIR}" <<\'PY\''
    start = text.index("\n", text.index(marker)) + 1
    end = text.index("\nPY\n", start)
    return text[start:end]


def _write_tar(path: Path, members: list[tuple[str, bytes, str]]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name, payload, kind in members:
            info = tarfile.TarInfo(name)
            if kind == "file":
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = "keygen"
                archive.addfile(info)
            else:
                raise AssertionError(kind)


def _run_consensus_extractor(tmp_path: Path, members: list[tuple[str, bytes, str]]) -> subprocess.CompletedProcess[str]:
    tarball = tmp_path / "helpers.tar.gz"
    destination = tmp_path / "bin"
    destination.mkdir()
    _write_tar(tarball, members)
    script = tmp_path / "extractor.py"
    script.write_text(_install_sh_consensus_extractor_source(), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(script), str(tarball), str(destination)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _valid_consensus_members() -> list[tuple[str, bytes, str]]:
    return [
        ("bls_verify_digest", b"#!/bin/sh\nexit 0\n", "file"),
        ("invite_pop_bls", b"#!/bin/sh\nexit 0\n", "file"),
        ("keygen", b"#!/bin/sh\nexit 0\n", "file"),
        ("validator_endpoint_assertion_bls", b"#!/bin/sh\nexit 0\n", "file"),
        ("validator_harness", b"#!/bin/sh\nexit 0\n", "file"),
    ]


def test_install_sh_consensus_extractor_rejects_duplicate_member(tmp_path: Path) -> None:
    members = _valid_consensus_members() + [("keygen", b"#!/bin/sh\nexit 1\n", "file")]

    result = _run_consensus_extractor(tmp_path, members)

    assert result.returncode != 0
    assert "install_sh_consensus_binary_tar_member_count_invalid" in result.stderr


def test_install_sh_consensus_extractor_rejects_nested_member(tmp_path: Path) -> None:
    members = _valid_consensus_members()
    members[0] = ("nested/bls_verify_digest", b"#!/bin/sh\nexit 0\n", "file")

    result = _run_consensus_extractor(tmp_path, members)

    assert result.returncode != 0
    assert "install_sh_consensus_binary_tar_members_invalid" in result.stderr


def test_install_sh_consensus_extractor_rejects_symlink_member(tmp_path: Path) -> None:
    members = _valid_consensus_members()
    members[0] = ("bls_verify_digest", b"", "symlink")

    result = _run_consensus_extractor(tmp_path, members)

    assert result.returncode != 0
    assert "install_sh_consensus_binary_tar_member_unsafe" in result.stderr


def test_install_sh_manifest_sync_fails_on_url_mismatch(tmp_path: Path) -> None:
    bad_script = _copy_script(
        tmp_path,
        replacements={EXPECTED_URL: "https://files.pythonhosted.org/packages/wrong.whl"},
    )
    with pytest.raises(ValueError, match="RC_WHEEL_URL"):
        verify_install_sh_manifest_sync(bad_script, MANIFEST)


def test_install_sh_manifest_sync_fails_on_hash_mismatch(tmp_path: Path) -> None:
    bad_script = _copy_script(
        tmp_path,
        replacements={EXPECTED_SHA256: "0" * 64},
    )
    with pytest.raises(ValueError, match="RC_WHEEL_SHA256"):
        verify_install_sh_manifest_sync(bad_script, MANIFEST)


def test_install_sh_manifest_sync_fails_on_size_mismatch(tmp_path: Path) -> None:
    bad_script = _copy_script(
        tmp_path,
        replacements={f'RC_WHEEL_SIZE="{EXPECTED_SIZE}"': 'RC_WHEEL_SIZE="1"'},
    )
    with pytest.raises(ValueError, match="RC_WHEEL_SIZE"):
        verify_install_sh_manifest_sync(bad_script, MANIFEST)


def test_install_sh_manifest_sync_fails_on_tmp_wheel_mismatch(tmp_path: Path) -> None:
    bad_script = _copy_script(
        tmp_path,
        replacements={
            'TMP_WHEEL="${TMP_DIR}/${WHEEL_BASENAME}"': 'TMP_WHEEL="${TMP_DIR}/ilc-core-0.4.4.whl"',
        },
    )
    with pytest.raises(ValueError, match="TMP_WHEEL"):
        verify_install_sh_manifest_sync(bad_script, MANIFEST)


def test_install_sh_manifest_sync_validates_consensus_binary_fields() -> None:
    verify_install_sh_manifest_sync(INSTALL_SH, MANIFEST)


def test_install_sh_manifest_sync_fails_on_consensus_url_mismatch(
    tmp_path: Path,
) -> None:
    bad_script = _copy_script(
        tmp_path,
        replacements={EXPECTED_CONSENSUS_URL: "https://example.invalid/helpers.tar.gz"},
    )
    with pytest.raises(ValueError, match="CONSENSUS_BIN_URL"):
        verify_install_sh_manifest_sync(bad_script, MANIFEST)


def test_install_sh_manifest_sync_fails_on_consensus_hash_mismatch(
    tmp_path: Path,
) -> None:
    bad_script = _copy_script(
        tmp_path,
        replacements={EXPECTED_CONSENSUS_SHA256: "0" * 64},
    )
    with pytest.raises(ValueError, match="CONSENSUS_BIN_SHA256"):
        verify_install_sh_manifest_sync(bad_script, MANIFEST)


def test_install_sh_manifest_sync_fails_on_consensus_size_mismatch(
    tmp_path: Path,
) -> None:
    bad_script = _copy_script(
        tmp_path,
        replacements={
            f'CONSENSUS_BIN_SIZE="{EXPECTED_CONSENSUS_SIZE}"': 'CONSENSUS_BIN_SIZE="1"',
        },
    )
    with pytest.raises(ValueError, match="CONSENSUS_BIN_SIZE"):
        verify_install_sh_manifest_sync(bad_script, MANIFEST)


def test_install_sh_manifest_sync_rejects_manifest_without_cli_binary(
    tmp_path: Path,
) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["artifacts"] = [
        artifact
        for artifact in manifest["artifacts"]
        if artifact["artifact_type"] != "cli_binary"
    ]
    manifest_path = tmp_path / "manifest_without_cli_binary.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="cli_binary_record_missing"):
        verify_install_sh_manifest_sync(INSTALL_SH, manifest_path)


def test_install_sh_manifest_sync_rejects_oversized_script(tmp_path: Path) -> None:
    path = tmp_path / "install.sh"
    path.write_bytes(b"#" * (1_048_576 + 1))
    with pytest.raises(ValueError, match="install_sh_too_large"):
        verify_install_sh_manifest_sync(path, MANIFEST)


def test_install_sh_manifest_sync_rejects_duplicate_assignments(tmp_path: Path) -> None:
    duplicate = f'RC_WHEEL_URL="{EXPECTED_URL}"\n'
    path = _copy_script(
        tmp_path,
        replacements={"#!/usr/bin/env bash\n": f"#!/usr/bin/env bash\n{duplicate}"},
    )
    with pytest.raises(ValueError, match="duplicate_assignment:RC_WHEEL_URL"):
        verify_install_sh_manifest_sync(path, MANIFEST)


def test_install_sh_executes_invite_onboarding_after_verified_install() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    hash_check = text.index('if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]')
    onboard = text.index("install_sh_running_invite_onboard")
    assert hash_check < onboard
    assert "--from-invite" in text
    assert "--output-receipt" in text
    assert "--relay-url" in text
    assert "--relay-tls-cert-der-sha256" in text
    assert "--relay-network-id" in text
    assert "--probe-observer" in text
    assert "install_sh_invite_onboard_complete" in text


def test_install_sh_set_e_pipefail_present() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert "set -euo pipefail" in text


def test_install_sh_verifies_hash_before_pip_install() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    hash_check = text.index('if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]')
    pip_install = text.index("pip install")
    assert hash_check < pip_install


def test_install_sh_uses_private_temp_directory_for_wheel() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert 'TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ilc-install-XXXXXX")"' in text
    assert 'WHEEL_BASENAME="${RC_WHEEL_URL##*/}"' in text
    assert 'TMP_WHEEL="${TMP_DIR}/${WHEEL_BASENAME}"' in text
    assert "ilc-core-0.4.3.whl" not in text
    assert "ilc-core-0.4.4.whl" not in text
    assert "XXXXXX.whl" not in text


def test_install_sh_rejects_non_canonical_wheel_basename() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert "install_sh_wheel_filename_invalid" in text
    assert "py3-none-any\\.whl" in text


def test_install_sh_download_has_pre_hash_size_cap() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    cap = text.index("RC_WHEEL_SIZE_CAP=")
    download = text.index("urlopen(request, timeout=120)")
    hash_check = text.index('if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]')
    assert cap < download < hash_check
    assert "install_sh_download_size_exceeded" in text


def test_install_sh_post_install_check_is_path_independent() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert (
        '"${TARGET_DIR}/bin/python" -m ilc_core.cli.main --help >/dev/null 2>&1'
        in text
    )
    assert "ilc --help >/dev/null" not in text


def test_install_sh_defaults_to_managed_venv_not_active_python() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")

    assert 'TARGET_DIR="${HOME}/.ilc/venv"' in text
    assert 'python3 -m pip install --quiet "${TMP_WHEEL}"' not in text


def test_install_sh_does_not_disable_tls_verification() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert "curl -k" not in text
    assert "--insecure" not in text
    assert "--no-check-certificate" not in text


def test_install_sh_embedded_values_are_present_once() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert text.count(f'RC_WHEEL_URL="{EXPECTED_URL}"') == 1
    assert text.count(f'RC_WHEEL_SHA256="{EXPECTED_SHA256}"') == 1
    assert text.count(f'RC_WHEEL_SIZE="{EXPECTED_SIZE}"') == 1


def test_install_sh_hash_tool_detection_matches_sidecar_pattern() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    assert "command -v shasum" in text
    assert "command -v sha256sum" in text


def test_sync_module_has_no_network_or_shell_execution_imports() -> None:
    text = (ROOT / "ilc_core/release/install_sh_manifest_sync.py").read_text(
        encoding="utf-8"
    )
    assert "subprocess" not in text
    assert "urllib" not in text
    assert "requests" not in text


def test_sync_module_extracts_quoted_assignments_only() -> None:
    text = (ROOT / "ilc_core/release/install_sh_manifest_sync.py").read_text(
        encoding="utf-8"
    )
    assert re.search(r"_ASSIGNMENT_RE = re\.compile", text)
    assert "?P<name>" in text
    assert "?P<value>" in text
