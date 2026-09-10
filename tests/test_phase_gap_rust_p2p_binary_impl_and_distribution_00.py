from __future__ import annotations

import inspect
import subprocess
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ilc_core.consensus import binary_paths
from ilc_core.network import rust_p2p_bridge


ROOT = Path(__file__).resolve().parents[1]
CARGO_TOML = ROOT / "ilc_consensus" / "Cargo.toml"
BRIDGE_SOURCE = ROOT / "ilc_consensus" / "src" / "ilc_p2p_bridge_main.rs"
LOCAL_TARBALL_DIR = ROOT / "out" / "gap_rust_p2p_binary_impl_and_distribution_00"
EXPECTED_TARBALL_MEMBERS = {
    "bls_verify_digest",
    "invite_pop_bls",
    "keygen",
    "validator_endpoint_assertion_bls",
    "validator_harness",
    "ilc_p2p_bridge",
}


def test_cargo_declares_ilc_p2p_bridge_binary_target() -> None:
    text = CARGO_TOML.read_text(encoding="utf-8")

    assert 'name = "ilc_p2p_bridge"' in text
    assert 'path = "src/ilc_p2p_bridge_main.rs"' in text
    assert BRIDGE_SOURCE.is_file()


def test_python_bridge_uses_release_path_and_installed_binary_discovery() -> None:
    source = inspect.getsource(rust_p2p_bridge)

    assert 'Path("ilc_consensus") / "target" / "release" / "ilc_p2p_bridge"' in source
    assert 'installed_consensus_binary_command("ilc_p2p_bridge")' in source
    assert 'target" / "debug" / "ilc_p2p_bridge"' not in source


def test_ilc_p2p_bridge_allowed_installed_helper_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = tmp_path / "ilc_p2p_bridge"
    helper.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    helper.chmod(0o700)
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(tmp_path))

    assert binary_paths.installed_consensus_binary_command("ilc_p2p_bridge") == (
        str(helper),
    )


def test_ilc_p2p_bridge_helper_name_still_rejects_path_like_values() -> None:
    with pytest.raises(ValueError, match="consensus_binary_name_invalid"):
        binary_paths.installed_consensus_binary_command("subdir/ilc_p2p_bridge")


def test_guard_closed_python_bridge_does_not_spawn_installed_or_repo_binary() -> None:
    bridge = rust_p2p_bridge.RustP2PBridge()

    with patch("ilc_core.network.rust_p2p_bridge.subprocess.run") as run:
        assert bridge.send_via_rust_p2p("validator-1", b"payload") is False

    run.assert_not_called()
    assert rust_p2p_bridge.RUST_P2P_BRIDGE_NOT_ACTIVATED is True
    assert rust_p2p_bridge.CDL_094_ADMISSION_WIRE_NOT_ACTIVATED is False


def test_rust_bridge_source_fails_closed_until_activation() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")

    assert "rust_p2p_bridge_runtime_not_activated" in source
    assert "serde(deny_unknown_fields)" in source
    assert "MAX_PAYLOAD_BYTES" in source
    assert "MAX_REQUEST_JSON_BYTES" in source


def test_local_distribution_tarball_membership_if_built() -> None:
    tarballs = sorted(LOCAL_TARBALL_DIR.glob("ilc-consensus-*-v0.4.20-prep.tar.gz"))
    if not tarballs:
        pytest.skip("local distribution tarball is built during phase execution")

    assert len(tarballs) == 1
    with tarfile.open(tarballs[0], "r:gz") as archive:
        members = archive.getmembers()
    names = {member.name for member in members}

    assert names == EXPECTED_TARBALL_MEMBERS
    for member in members:
        assert member.isfile()
        assert "/" not in member.name
        assert member.mode & 0o111


def test_release_binary_reports_not_activated_if_built() -> None:
    binary = ROOT / "ilc_consensus" / "target" / "release" / "ilc_p2p_bridge"
    if not binary.exists():
        pytest.skip("release binary is built during phase execution")

    result = subprocess.run(
        [
            str(binary),
            "send",
            "--request-json",
            '{"endpoint_id":"validator-1","payload_hex":"7061796c6f6164"}',
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode != 0
    assert "rust_p2p_bridge_runtime_not_activated" in result.stderr
