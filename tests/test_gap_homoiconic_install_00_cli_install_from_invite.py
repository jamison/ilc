# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-HOMOICONIC-INSTALL-00 CLI orchestration tests."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.sidecars.openclaw_invite_bootstrap import build_synthetic_invite_bundle


FIXTURE_MANIFEST = Path("tests/fixtures/starmap/core_public_rc_slice_fixture.json")


class _Decision:
    def __init__(self, *, allowed: bool, token: str | None = None) -> None:
        self.bootstrap_allowed = allowed
        self.defect_token = token

    def to_dict(self) -> dict[str, object]:
        return {
            "bootstrap_allowed": self.bootstrap_allowed,
            "defect_token": self.defect_token,
            "nullifier_status": "local_recorded_not_persisted",
        }


def _bundle() -> dict[str, object]:
    bundle = build_synthetic_invite_bundle()
    bundle["atlas_slice_manifest_witness"] = {"slice_id": "test-slice"}
    bundle["starmap_manifest_payload"] = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    return bundle


def _write_bundle(path: Path, payload: dict[str, object] | None = None) -> Path:
    path.write_text(
        json.dumps(payload or _bundle(), sort_keys=True, allow_nan=False),
        encoding="utf-8",
    )
    return path


def _args(invite: Path | str, target: Path, receipt: Path) -> argparse.Namespace:
    return argparse.Namespace(
        from_invite=str(invite),
        target_dir=str(target),
        output_receipt=str(receipt),
    )


def test_install_from_invite_help_is_discoverable() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "install", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--from-invite" in result.stdout
    assert "--target-dir" in result.stdout
    assert "--output-receipt" in result.stdout
    assert "Install a verified local graph slice" in result.stdout


def test_install_from_invite_missing_invite_arg_exits_error() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "install"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "from-invite" in result.stderr


def test_install_from_invite_invalid_json_file_exits_error(tmp_path: Path) -> None:
    invite_path = tmp_path / "invite.json"
    invite_path.write_text("{not-json", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "install",
            "--from-invite",
            str(invite_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["message"] == "install_invite_bundle_json_invalid"


def test_install_from_invite_missing_manifest_witness_in_bundle(tmp_path: Path) -> None:
    bundle = build_synthetic_invite_bundle()
    invite_path = _write_bundle(tmp_path / "invite.json", bundle)

    with pytest.raises(ValueError, match="invite_bundle_missing_atlas_slice_manifest_witness"):
        cli_main._run_install_subcommand(
            _args(invite_path, tmp_path / "target", tmp_path / "receipt.json")
        )


def test_install_from_invite_invite_verification_failure_exits_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.sidecars.openclaw_invite_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "verify_invite_bootstrap",
        lambda *args, **kwargs: _Decision(allowed=False, token="synthetic_reject"),
    )
    invite_path = _write_bundle(tmp_path / "invite.json")

    with pytest.raises(ValueError, match="invite_verification_failed:synthetic_reject"):
        cli_main._run_install_subcommand(
            _args(invite_path, tmp_path / "target", tmp_path / "receipt.json")
        )


def test_install_from_invite_manifest_verification_failure_exits_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier

    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"valid": False, "error": "synthetic_manifest_reject"},
    )
    invite_path = _write_bundle(tmp_path / "invite.json")

    with pytest.raises(ValueError, match="manifest_verification_failed:synthetic_manifest_reject"):
        cli_main._run_install_subcommand(
            _args(invite_path, tmp_path / "target", tmp_path / "receipt.json")
        )


def test_install_from_invite_successful_path_writes_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier

    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"valid": True, "slice_id": witness["slice_id"]},
    )
    invite_path = _write_bundle(tmp_path / "invite.json")
    receipt_path = tmp_path / "receipt.json"

    result = cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target", receipt_path)
    )

    assert result["status"] == "ok"
    assert receipt_path.exists()
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["receipt_sha256"]
    assert len(list((tmp_path / "target").rglob("*.node.json"))) == 5


def test_install_from_invite_receipt_is_atomic_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    receipt_path = tmp_path / "install_receipt.json"
    observed_temp_names: list[str] = []
    original_replace = os.replace

    def _replace(src: str | bytes | os.PathLike[str] | os.PathLike[bytes], dst: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> None:
        observed_temp_names.append(Path(src).name)
        original_replace(src, dst)

    monkeypatch.setattr(cli_main.os, "replace", _replace)

    cli_main._write_install_receipt_atomic(receipt_path, {"ok": True})

    assert receipt_path.exists()
    assert observed_temp_names
    assert observed_temp_names[0].startswith(".install_receipt.json.")
    assert not list(tmp_path.glob("*.tmp"))


def test_install_from_invite_rejects_url_fetch() -> None:
    with pytest.raises(ValueError, match="install_invite_url_fetch_not_supported"):
        cli_main._load_install_invite_bundle("https://example.invalid/invite.json")


def test_install_from_invite_rejects_relative_file_uri() -> None:
    with pytest.raises(ValueError, match="install_invite_file_uri_must_be_absolute"):
        cli_main._load_install_invite_bundle("file://relative/invite.json")


def test_install_from_invite_does_not_create_graph_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier

    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"valid": True, "slice_id": witness["slice_id"]},
    )
    graph_state = tmp_path / "graph.json"
    invite_path = _write_bundle(tmp_path / "invite.json")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "--graph-state",
            str(graph_state),
            "install",
            "--from-invite",
            str(invite_path),
            "--target-dir",
            str(tmp_path / "target"),
            "--output-receipt",
            str(tmp_path / "receipt.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert not graph_state.exists()
