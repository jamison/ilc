from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

from ilc_core.release.install_sh_manifest_sync import verify_install_sh_manifest_sync


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = ROOT / "tools" / "install.sh"
MANIFEST = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_044_GAP_ONBOARDING_PACKAGE_044_00a_v0.1.json"
)
EXPECTED_URL = (
    "https://files.pythonhosted.org/packages/01/1e/"
    "78a69d572d4fa7e563a5d20ae5e2dbcca94f1b511c4373d09137639095c9/"
    "ilc_core-0.4.4-py3-none-any.whl"
)
EXPECTED_SHA256 = "4e6891c836d2b9c6757fa798b41b0fd1758b17503248783e89a94c60c6bfbd13"
EXPECTED_SIZE = "1364353"


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
    result = _run_install_sh("--channel", "rc", "--dry-run")
    assert result.returncode == 0
    assert f"RC_WHEEL_URL={EXPECTED_URL}" in result.stdout
    assert f"RC_WHEEL_SHA256={EXPECTED_SHA256}" in result.stdout


def test_install_sh_unsupported_channel_exits_error() -> None:
    result = _run_install_sh("--channel", "stable")
    assert result.returncode == 1
    assert "install_sh_channel_not_embedded:stable" in result.stderr


def test_install_sh_dev_channel_exits_error() -> None:
    result = _run_install_sh("--channel", "dev", "--dry-run")
    assert result.returncode == 1
    assert "install_sh_channel_not_embedded:dev" in result.stderr


def test_install_sh_dry_run_no_onboard_suppresses_hint() -> None:
    result = _run_install_sh("--dry-run", "--no-onboard")
    assert result.returncode == 0
    assert "ilc install --from-invite" not in result.stdout


def test_install_sh_dry_run_default_no_onboard_flag_includes_hint() -> None:
    result = _run_install_sh("--dry-run")
    assert result.returncode == 0
    assert "ilc install --from-invite" in result.stdout


def test_install_sh_target_dir_dry_run_records_target(tmp_path: Path) -> None:
    target = tmp_path / "venv"
    result = _run_install_sh("--dry-run", "--target-dir", str(target))
    assert result.returncode == 0
    assert f"target_dir={target}" in result.stdout


def test_install_sh_rejects_existing_non_venv_target_before_download(
    tmp_path: Path,
) -> None:
    target = tmp_path / "not-a-venv"
    target.mkdir()
    (target / "keep.txt").write_text("do not contaminate", encoding="utf-8")

    result = _run_install_sh("--target-dir", str(target))

    assert result.returncode == 1
    assert "install_sh_target_dir_exists_not_venv" in result.stderr


def test_install_sh_rejects_existing_venv_without_python(tmp_path: Path) -> None:
    target = tmp_path / "broken-venv"
    target.mkdir()
    (target / "pyvenv.cfg").write_text("home = /usr/bin\n", encoding="utf-8")

    result = _run_install_sh("--target-dir", str(target))

    assert result.returncode == 1
    assert "install_sh_target_venv_python_missing" in result.stderr


def test_install_sh_hash_mismatch_exits_error(tmp_path: Path) -> None:
    payload = tmp_path / "ilc_core-0.4.4-py3-none-any.whl"
    payload.write_bytes(b"not a wheel")
    bad_script = _copy_script(
        tmp_path,
        replacements={
            EXPECTED_URL: payload.as_uri(),
            f'RC_WHEEL_SIZE="{EXPECTED_SIZE}"': f'RC_WHEEL_SIZE="{payload.stat().st_size}"',
        },
    )
    result = _run_install_sh(path=bad_script)
    assert result.returncode == 1
    assert "install_sh_hash_verification_failed" in result.stderr


def test_install_sh_manifest_sync_passes() -> None:
    verify_install_sh_manifest_sync(INSTALL_SH, MANIFEST)


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


def test_install_sh_does_not_execute_graph_onboarding_calls() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    forbidden = ("\nilc install", " --from-invite ", "lmdb", "graph")
    for token in forbidden:
        assert token not in text
    assert "next_step_hint: ilc %s --from-%s <path>" in text


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
