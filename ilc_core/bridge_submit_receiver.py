# SPDX-License-Identifier: AGPL-3.0-only
"""Unix-socket worker for native QUIC submit receiver bridges.

Rust owns QUIC/TLS and frame parsing. This module owns the ILC semantic
boundary: CDL-073 envelope validation, CDL-118 native-submit signature checks,
CDL-075 node derivation, and optional truth graph persistence.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import socket
import stat
import sys
import threading
from typing import Any, Final

from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_graph_store import (
    node_id_from_submission,
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    TruthPrimitiveResult,
    consume_native_submit_replay_fallback,
    validate_truth_primitive_submission,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


BRIDGE_SOCKET_ENV: Final[str] = "ILC_SUBMIT_BRIDGE_SOCKET"
TRUTH_GRAPH_STORE_ENV: Final[str] = "ILC_TRUTH_GRAPH_STORE_PATH"
DEFAULT_BRIDGE_SOCKET: Final[str] = "/tmp/ilc_submit_bridge.sock"
MAX_WORKER_LINE_BYTES: Final[int] = 1_048_576 + 1


def _json_line(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _node_id_without_persistence(
    envelope: dict[str, Any],
    result: TruthPrimitiveResult,
) -> str | None:
    if not result.creates_node:
        return None
    return node_id_from_submission(envelope, result)


def process_submission(
    envelope: dict[str, Any],
    *,
    store: TruthPrimitiveGraphStore | None = None,
) -> dict[str, Any]:
    """Validate and optionally persist one native submit envelope."""

    result = validate_truth_primitive_submission(envelope)
    if store is not None:
        receipt = write_truth_primitive_result(store, envelope, result)
    else:
        consume_native_submit_replay_fallback(envelope)
        receipt = {
            "node_id": _node_id_without_persistence(envelope, result),
            "nodes_written": 0,
            "edges_written": 0,
            "native_submit_replay_written": 0,
            "primitive": result.primitive,
            "version": "truth_primitive_graph_store_880.v0.1",
        }
    return {
        "ok": True,
        "receipt": receipt,
        "node_id": receipt.get("node_id"),
        "primitive": receipt.get("primitive"),
    }


def process_line(
    line: bytes,
    *,
    store: TruthPrimitiveGraphStore | None = None,
) -> dict[str, Any]:
    if len(line) > MAX_WORKER_LINE_BYTES:
        return {"ok": False, "error": "native_submit_worker_line_too_large"}
    try:
        decoded = line.decode("utf-8")
    except UnicodeDecodeError:
        return {"ok": False, "error": "native_submit_worker_line_not_utf8"}
    try:
        envelope = json.loads(decoded)
    except json.JSONDecodeError:
        return {"ok": False, "error": "native_submit_worker_json_invalid"}
    if not isinstance(envelope, dict):
        return {"ok": False, "error": "native_submit_worker_envelope_not_object"}
    try:
        return process_submission(envelope, store=store)
    except EpistemicSubmissionError as exc:
        return {"ok": False, "error": exc.token}
    except Exception:
        return {"ok": False, "error": "native_submit_bridge_internal_error"}


def _handle_client(
    conn: socket.socket,
    *,
    store: TruthPrimitiveGraphStore | None,
    stop_event: threading.Event,
) -> None:
    with conn:
        reader = conn.makefile("rb")
        writer = conn.makefile("wb")
        try:
            while not stop_event.is_set():
                line = reader.readline(MAX_WORKER_LINE_BYTES + 1)
                if not line:
                    return
                writer.write(_json_line(process_line(line.rstrip(b"\n"), store=store)))
                writer.flush()
        finally:
            reader.close()
            writer.close()


def _prepare_socket_path(socket_path: Path) -> None:
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        mode = socket_path.stat().st_mode
    except FileNotFoundError:
        return
    if not stat.S_ISSOCK(mode):
        raise RuntimeError("native_submit_bridge_socket_path_not_socket")
    socket_path.unlink()


def serve(
    *,
    socket_path: Path,
    store_path: Path | None,
) -> int:
    stop_event = threading.Event()

    def _request_stop(_signum: int, _frame: Any) -> None:
        stop_event.set()

    old_term = signal.signal(signal.SIGTERM, _request_stop)
    old_int = signal.signal(signal.SIGINT, _request_stop)
    store: TruthPrimitiveGraphStore | None = None
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    threads: list[threading.Thread] = []
    try:
        if store_path is not None:
            store = TruthPrimitiveGraphStore(store_path)
        _prepare_socket_path(socket_path)
        server.bind(str(socket_path))
        server.listen()
        server.settimeout(0.2)
        while not stop_event.is_set():
            try:
                conn, _addr = server.accept()
            except TimeoutError:
                continue
            thread = threading.Thread(
                target=_handle_client,
                kwargs={"conn": conn, "store": store, "stop_event": stop_event},
                daemon=True,
            )
            thread.start()
            threads.append(thread)
    finally:
        stop_event.set()
        server.close()
        for thread in threads:
            thread.join(timeout=1.0)
        if store is not None:
            store.close()
        try:
            if socket_path.exists() and stat.S_ISSOCK(socket_path.stat().st_mode):
                socket_path.unlink()
        except OSError:
            pass
        signal.signal(signal.SIGTERM, old_term)
        signal.signal(signal.SIGINT, old_int)
    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true", help="run Unix-socket worker")
    parser.add_argument(
        "--socket",
        default=None,
        help=f"Unix socket path, defaults to ${BRIDGE_SOCKET_ENV} or {DEFAULT_BRIDGE_SOCKET}",
    )
    parser.add_argument(
        "--store-path",
        default=None,
        help=f"truth graph LMDB path, defaults to ${TRUTH_GRAPH_STORE_ENV} when set",
    )
    parsed = parser.parse_args(argv)
    if parsed.socket is None:
        parsed.socket = os.environ.get(BRIDGE_SOCKET_ENV, DEFAULT_BRIDGE_SOCKET)
    if parsed.store_path is None:
        parsed.store_path = os.environ.get(TRUTH_GRAPH_STORE_ENV)
    return parsed


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(list(sys.argv[1:] if argv is None else argv))
    if not args.worker:
        print("native_submit_bridge_worker_mode_required", file=sys.stderr)
        return 2
    store_path = Path(args.store_path).expanduser() if args.store_path else None
    try:
        return serve(socket_path=Path(args.socket), store_path=store_path)
    except Exception as exc:
        print(f"native_submit_bridge_start_failed:{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BRIDGE_SOCKET_ENV",
    "DEFAULT_BRIDGE_SOCKET",
    "MAX_WORKER_LINE_BYTES",
    "TRUTH_GRAPH_STORE_ENV",
    "main",
    "process_line",
    "process_submission",
    "serve",
]
