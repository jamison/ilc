#!/usr/bin/env python3
"""Launch the CDL-077 HTTP fetch server for public-RC release discovery."""

from __future__ import annotations

import os
import signal
import sys
import threading
from pathlib import Path

from ilc_core.network.d2d.http_fetch_transport_runtime import (
    FetchTransportConfig,
    HttpFetchTransportRuntime,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.sidecars.public_path_activation import is_loopback_bind_host


_FETCH_SERVER_CREDENTIAL = b"ilc-node-2-vps-fetch-server-093bdc01507a062f"
_FETCH_SERVER_NONCE = b"ilc-fetch-server-vps-deploy-00-genesis-node-2"
_DEFAULT_TRANSPORT_EPOCH = 1
_DEFAULT_TRANSPORT_EXPIRES_EPOCH = 100_000


def _required_env(name: str, token: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(token)
    return value


def _parse_port(raw: str) -> int:
    try:
        port = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("fetch_server_port_invalid") from exc
    if not (0 < port <= 65535):
        raise ValueError("fetch_server_port_invalid")
    return port


def _parse_epoch_env(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default)).strip()
    try:
        epoch = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name.lower()}_invalid") from exc
    if epoch < 0:
        raise ValueError(f"{name.lower()}_invalid")
    return epoch


def _build_config() -> FetchTransportConfig:
    store_path = _required_env(
        "ILC_TRUTH_GRAPH_STORE_PATH",
        "fetch_server_lmdb_path_missing",
    )
    # Refuse accidental empty-store creation if the service env points at the
    # wrong path; the LMDB adapter intentionally creates missing directories.
    if not Path(store_path).is_dir():
        raise ValueError("fetch_server_lmdb_path_missing")

    bind_host = os.environ.get("HTTP_FETCH_BIND_HOST", "127.0.0.1").strip()
    if not bind_host:
        raise ValueError("fetch_server_bind_host_invalid")
    bind_port = _parse_port(os.environ.get("HTTP_FETCH_BIND_PORT", "0"))

    transport_context = None
    public_fetch_serving_enabled = False
    if not is_loopback_bind_host(bind_host):
        transport_epoch = _parse_epoch_env(
            "ILC_FETCH_TRANSPORT_EPOCH",
            _DEFAULT_TRANSPORT_EPOCH,
        )
        expires_epoch = _parse_epoch_env(
            "ILC_FETCH_TRANSPORT_EXPIRES_EPOCH",
            _DEFAULT_TRANSPORT_EXPIRES_EPOCH,
        )
        if expires_epoch < transport_epoch:
            raise ValueError("ilc_fetch_transport_expires_epoch_invalid")
        transport_context = build_transport_principal_context(
            credential_kind="transport_credential",
            credential_material=_FETCH_SERVER_CREDENTIAL,
            handshake_nonce=_FETCH_SERVER_NONCE,
            issued_epoch=transport_epoch,
            expires_epoch=expires_epoch,
            current_epoch=transport_epoch,
        )
        public_fetch_serving_enabled = True

    return FetchTransportConfig(
        bind_host=bind_host,
        bind_port=bind_port,
        store_path=store_path,
        rate_limit_window_id=(
            transport_context["current_epoch"] if transport_context is not None else 0
        ),
        public_fetch_serving_enabled=public_fetch_serving_enabled,
        transport_principal_context=transport_context,
    )


def main() -> int:
    runtime = HttpFetchTransportRuntime(_build_config())
    stop_event = threading.Event()

    def _stop(_signum: int, _frame: object) -> None:
        runtime.stop()
        stop_event.set()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    runtime.start()
    print(f"fetch_server_ready port={runtime.state['bound_port']}", flush=True)
    stop_event.wait()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"fetch_server_start_failed: {exc}", file=sys.stderr, flush=True)
        raise
