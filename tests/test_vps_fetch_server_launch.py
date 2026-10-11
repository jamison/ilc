from __future__ import annotations

import pytest

from tools import vps_fetch_server_launch as launch


def test_parse_port_rejects_invalid_values() -> None:
    assert launch._parse_port("8081") == 8081
    for raw in ("", "0", "-1", "65536", "not-a-port"):
        with pytest.raises(ValueError, match="fetch_server_port_invalid"):
            launch._parse_port(raw)


def test_build_config_requires_existing_lmdb_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(tmp_path / "missing.lmdb"))
    monkeypatch.setenv("HTTP_FETCH_BIND_HOST", "127.0.0.1")
    monkeypatch.setenv("HTTP_FETCH_BIND_PORT", "8081")

    with pytest.raises(ValueError, match="fetch_server_lmdb_path_missing"):
        launch._build_config()


def test_build_config_loopback_does_not_build_public_transport_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    store = tmp_path / "truth_graph.lmdb"
    store.mkdir()
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store))
    monkeypatch.setenv("HTTP_FETCH_BIND_HOST", "127.0.0.1")
    monkeypatch.setenv("HTTP_FETCH_BIND_PORT", "8081")

    config = launch._build_config()

    assert config.bind_host == "127.0.0.1"
    assert config.bind_port == 8081
    assert config.public_fetch_serving_enabled is False
    assert config.transport_principal_context is None
    assert config.rate_limit_window_id == 0


def test_build_config_non_loopback_uses_epoch_env_for_transport_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    store = tmp_path / "truth_graph.lmdb"
    store.mkdir()
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store))
    monkeypatch.setenv("HTTP_FETCH_BIND_HOST", "0.0.0.0")
    monkeypatch.setenv("HTTP_FETCH_BIND_PORT", "8081")
    monkeypatch.setenv("ILC_FETCH_TRANSPORT_EPOCH", "7")
    monkeypatch.setenv("ILC_FETCH_TRANSPORT_EXPIRES_EPOCH", "99")

    config = launch._build_config()

    assert config.public_fetch_serving_enabled is True
    assert config.rate_limit_window_id == 7
    assert config.transport_principal_context is not None
    assert config.transport_principal_context["current_epoch"] == 7
    assert config.transport_principal_context["expires_epoch"] == 99


def test_build_config_rejects_expiry_before_current_epoch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    store = tmp_path / "truth_graph.lmdb"
    store.mkdir()
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store))
    monkeypatch.setenv("HTTP_FETCH_BIND_HOST", "0.0.0.0")
    monkeypatch.setenv("HTTP_FETCH_BIND_PORT", "8081")
    monkeypatch.setenv("ILC_FETCH_TRANSPORT_EPOCH", "7")
    monkeypatch.setenv("ILC_FETCH_TRANSPORT_EXPIRES_EPOCH", "6")

    with pytest.raises(ValueError, match="ilc_fetch_transport_expires_epoch_invalid"):
        launch._build_config()
