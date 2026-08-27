from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = ROOT / "tools" / "install.sh"


def _run_install_sh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(INSTALL_SH), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_install_sh_dry_run_shows_invite_bundle_flag() -> None:
    result = _run_install_sh(
        "--channel",
        "rc",
        "--dry-run",
        "--invite-bundle",
        "/tmp/public-rc-invite.json",
    )
    assert result.returncode == 0
    assert "install_sh_dry_run" in result.stdout
    assert "invite_bundle=/tmp/public-rc-invite.json" in result.stdout


def test_install_sh_invite_bundle_not_found_exits_1(tmp_path: Path) -> None:
    result = _run_install_sh("--invite-bundle", str(tmp_path / "missing.json"))
    assert result.returncode == 1
    assert "install_sh_invite_bundle_not_found" in result.stderr


def test_install_sh_missing_invite_bundle_required() -> None:
    result = _run_install_sh("--dry-run")
    assert result.returncode == 2
    assert "install_sh_invite_bundle_required" in result.stderr


def test_install_sh_no_onboard_is_not_accepted_bypass() -> None:
    result = _run_install_sh("--dry-run", "--no-onboard")
    assert result.returncode == 2
    assert "install_sh_unknown_argument:--no-onboard" in result.stderr


def test_install_sh_runs_invite_onboard_after_hash_verification() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    hash_check = text.index('if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]')
    onboard = text.index("install_sh_running_invite_onboard")
    assert hash_check < onboard
    assert "--from-invite" in text
    assert "--target-dir" in text
    assert 'INSTALL_SLICE_DIR="${HOME}/.ilc/installed_slices"' in text
    assert 'INSTALL_RECEIPT="${INSTALL_SLICE_DIR}/install_receipt.json"' in text
