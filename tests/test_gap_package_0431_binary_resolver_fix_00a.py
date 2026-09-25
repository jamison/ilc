from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.consensus import attribution_batch_bridge, binary_paths


def _executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o700)
    return path


def test_attribution_batch_ingest_is_allowed_consensus_binary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ILC_CONSENSUS_BIN_DIR", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")

    assert binary_paths.installed_consensus_binary_path("attribution_batch_ingest") is None


def test_attribution_batch_ingest_resolves_from_consensus_bin_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _executable(tmp_path / "managed-bin" / "attribution_batch_ingest")
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(helper.parent))
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")

    assert binary_paths.installed_consensus_binary_path("attribution_batch_ingest") == helper


def test_attribution_bridge_resolves_home_installed_binary_before_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = tmp_path / "home"
    installed = _executable(home / ".ilc" / "bin" / "attribution_batch_ingest")
    path_binary = _executable(tmp_path / "path-bin" / "attribution_batch_ingest")
    monkeypatch.delenv("ILC_CONSENSUS_BIN_DIR", raising=False)
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setattr(
        attribution_batch_bridge,
        "_PACKAGE_ATTRIBUTION_BATCH_INGEST_BINARY",
        tmp_path / "missing-package-bin" / "attribution_batch_ingest",
    )
    monkeypatch.setattr(attribution_batch_bridge.shutil, "which", lambda _name: str(path_binary))

    assert attribution_batch_bridge.resolve_attribution_batch_ingest_binary() == installed


def test_attribution_bridge_resolver_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configured = _executable(tmp_path / "configured" / "attribution_batch_ingest")
    package_binary = _executable(tmp_path / "package" / "attribution_batch_ingest")
    installed = _executable(tmp_path / "installed" / "attribution_batch_ingest")
    path_binary = _executable(tmp_path / "path" / "attribution_batch_ingest")
    source_default = tmp_path / "source" / "attribution_batch_ingest"

    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(installed.parent))
    monkeypatch.setattr(
        attribution_batch_bridge,
        "_PACKAGE_ATTRIBUTION_BATCH_INGEST_BINARY",
        package_binary,
    )
    monkeypatch.setattr(
        attribution_batch_bridge,
        "DEFAULT_ATTRIBUTION_BATCH_INGEST_BINARY",
        source_default,
    )
    monkeypatch.setattr(attribution_batch_bridge.shutil, "which", lambda _name: str(path_binary))

    assert (
        attribution_batch_bridge.resolve_attribution_batch_ingest_binary(configured)
        == configured
    )
    assert attribution_batch_bridge.resolve_attribution_batch_ingest_binary() == package_binary

    package_binary.unlink()
    assert attribution_batch_bridge.resolve_attribution_batch_ingest_binary() == installed

    installed.unlink()
    assert attribution_batch_bridge.resolve_attribution_batch_ingest_binary() == path_binary

    monkeypatch.setattr(attribution_batch_bridge.shutil, "which", lambda _name: None)
    assert attribution_batch_bridge.resolve_attribution_batch_ingest_binary() == source_default


def test_unknown_consensus_binary_still_fails_closed() -> None:
    with pytest.raises(ValueError, match="consensus_binary_name_invalid"):
        binary_paths.installed_consensus_binary_path("not_a_valid_binary")
