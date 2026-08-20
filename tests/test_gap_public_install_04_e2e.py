from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/test_install_e2e.sh"


def test_install_e2e_script_exists_and_is_executable() -> None:
    assert SCRIPT.exists()
    assert os.access(SCRIPT, os.X_OK)


def test_install_e2e_script_syntax_passes() -> None:
    result = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_install_e2e_script_mounts_install_sh_read_only() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert '-v "${INSTALL_SH}:/tmp/install.sh:ro"' in text
    assert "--no-onboard" in text
    assert "--from-invite" not in text
    assert "80e53ea18aea0a7c474400a41e20f346c00ee3e36e8f0dd60f233cca2b0e2f1d" not in text
    assert 'grep -E "RC_WHEEL_SHA256=[0-9a-f]{64}"' in text


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
def test_install_e2e_dry_run_docker_smoke() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr
    assert "install_e2e_pass mode=dry-run" in result.stdout


def test_install_e2e_live_mode_is_manual_only() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "--live" in text
    assert 'if [[ "${ILC_INSTALL_E2E_LIVE}" == "1" ]]' in text
    assert "python3 -m ilc_core.cli.main --help" in text
