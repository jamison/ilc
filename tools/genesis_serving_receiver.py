#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Private Phase 1560 Genesis serving receiver.

PUBLIC_RC_EXCLUDE: private_phase_1560_genesis_receiver
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC Tailscale HTTPS receiver helper. Does not activate public P2P, public bundle serving, Agent INIT, production economics, or public RC.
PUBLIC_RC_INCLUDE_REQUIRES: public transport authority, hardened public serving design, and explicit public RC gate.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Mapping

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ilc_core.encoding.cidv1 import parse_nodeid_strict
from ilc_core.private_json_guardrails import (
    canonical_json,
    reject_float,
    require_sha256_hex,
)


MAX_REQUEST_BYTES = 1_048_576
GENESIS_RECEIVER_STATUS_PATH = "/ilc/genesis/status"
GENESIS_RECEIVER_VERSION = "genesis_serving_receiver_1560_preflight.v0.1"
SERVING_RECEIPT_SCHEMA_VERSION = "serving_receipt_1559.v0.1"
SERVING_REQUEST_PATH = "/ilc/genesis/serve"
VERIFY_REQUEST_PATH = "/ilc/genesis/verify"


class GenesisReceiverError(ValueError):
    """Stable exception type for private receiver validation failures."""


def _atomic_write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = canonical_json(payload, float_token="genesis_receiver_float_not_allowed")
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def validate_serve_payload(payload: Mapping[str, object]) -> dict[str, object]:
    try:
        reject_float(payload, "genesis_receiver_float_not_allowed")
    except ValueError as exc:
        raise GenesisReceiverError(str(exc)) from exc
    _require_schema(payload)
    layer0 = _require_object(payload.get("layer0"), "genesis_receiver_missing_layer0")
    layer1_raw = payload.get("layer1")
    receipt = _require_object(payload.get("receipt"), "genesis_receiver_missing_receipt")

    layer0_cid = _require_cid(layer0.get("cidv1"), "genesis_receiver_invalid_layer0_cidv1")
    layer0_sha = _require_sha(layer0.get("sha256"), "genesis_receiver_invalid_layer0_sha256")
    _require_str(layer0.get("canonical_json"), "genesis_receiver_missing_layer0_canonical_json")

    layer1_sha = ""
    layer1_cid = ""
    if layer1_raw is not None:
        layer1 = _require_object(layer1_raw, "genesis_receiver_invalid_layer1")
        layer1_sha = _require_sha(layer1.get("sha256"), "genesis_receiver_invalid_layer1_sha256")
        layer1_cid_raw = layer1.get("cidv1")
        if layer1_cid_raw != "":
            layer1_cid = _require_cid(
                layer1_cid_raw,
                "genesis_receiver_invalid_layer1_cidv1",
            )

    receipt_id = _require_str(
        receipt.get("serving_receipt_id"),
        "genesis_receiver_missing_serving_receipt_id",
    )
    receipt_layer0_sha = _require_sha(
        receipt.get("layer0_protocol_bundle_sha256"),
        "genesis_receiver_invalid_receipt_layer0_sha256",
    )
    if receipt_layer0_sha != layer0_sha:
        raise GenesisReceiverError("genesis_receiver_receipt_layer0_sha_mismatch")
    receipt_layer0_cid = receipt.get("layer0_protocol_bundle_cidv1", "")
    if receipt_layer0_cid not in ("", layer0_cid):
        raise GenesisReceiverError("genesis_receiver_receipt_layer0_cid_mismatch")
    receipt_layer1_sha = receipt.get("layer1_genesis_bundle_sha256", "")
    if receipt_layer1_sha not in ("", layer1_sha):
        raise GenesisReceiverError("genesis_receiver_receipt_layer1_sha_mismatch")

    return {
        "accepted": True,
        "layer0_cidv1": layer0_cid,
        "layer0_sha256": layer0_sha,
        "layer1_cidv1": layer1_cid,
        "layer1_sha256": layer1_sha,
        "receipt_id": receipt_id,
        "schema_version": SERVING_RECEIPT_SCHEMA_VERSION,
    }


def validate_verify_payload(
    payload: Mapping[str, object],
    *,
    state_path: Path,
) -> dict[str, object]:
    try:
        reject_float(payload, "genesis_receiver_float_not_allowed")
    except ValueError as exc:
        raise GenesisReceiverError(str(exc)) from exc
    _require_schema(payload)
    expected = _require_cid(
        payload.get("expected_layer0_cidv1"),
        "genesis_receiver_invalid_expected_layer0_cidv1",
    )
    state = _load_state(state_path)
    observed = state.get("layer0_cidv1", "")
    verified = observed == expected
    return {
        "layer0_cidv1": observed if isinstance(observed, str) else "",
        "schema_version": SERVING_RECEIPT_SCHEMA_VERSION,
        "verified": verified,
    }


def status_payload(*, state_path: Path) -> dict[str, object]:
    state_exists = state_path.exists()
    state: dict[str, object] = _load_state(state_path) if state_exists else {}
    return {
        "public_p2p_activated": False,
        "receiver_ready": True,
        "schema_version": SERVING_RECEIPT_SCHEMA_VERSION,
        "state_present": state_exists,
        "stored_layer0_cidv1": state.get("layer0_cidv1", ""),
        "version": GENESIS_RECEIVER_VERSION,
    }


def make_handler(state_path: Path) -> type[BaseHTTPRequestHandler]:
    class GenesisServingHandler(BaseHTTPRequestHandler):
        server_version = "ILCGenesisServingReceiver/0.1"

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def do_GET(self) -> None:
            if self.path != GENESIS_RECEIVER_STATUS_PATH:
                self._write_json(404, {"error": "genesis_receiver_unknown_path"})
                return
            self._write_json(200, status_payload(state_path=state_path))

        def do_POST(self) -> None:
            try:
                payload = self._read_json_body()
                if self.path == SERVING_REQUEST_PATH:
                    response = validate_serve_payload(payload)
                    _atomic_write_json(state_path, response)
                    self._write_json(200, response)
                    return
                if self.path == VERIFY_REQUEST_PATH:
                    self._write_json(
                        200,
                        validate_verify_payload(payload, state_path=state_path),
                    )
                    return
                self._write_json(404, {"error": "genesis_receiver_unknown_path"})
            except GenesisReceiverError as exc:
                self._write_json(400, {"error": str(exc)})

        def _read_json_body(self) -> Mapping[str, object]:
            length_header = self.headers.get("Content-Length", "")
            try:
                length = int(length_header)
            except ValueError as exc:
                raise GenesisReceiverError("genesis_receiver_invalid_content_length") from exc
            if length < 0 or length > MAX_REQUEST_BYTES:
                raise GenesisReceiverError("genesis_receiver_request_too_large")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise GenesisReceiverError("genesis_receiver_request_truncated")
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise GenesisReceiverError("genesis_receiver_invalid_json") from exc
            if not isinstance(parsed, dict):
                raise GenesisReceiverError("genesis_receiver_request_not_object")
            try:
                reject_float(parsed, "genesis_receiver_float_not_allowed")
            except ValueError as exc:
                raise GenesisReceiverError(str(exc)) from exc
            return parsed

        def _write_json(self, status: int, payload: Mapping[str, object]) -> None:
            body = canonical_json(
                payload,
                float_token="genesis_receiver_float_not_allowed",
            ).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return GenesisServingHandler


def run_server(
    *,
    bind_host: str,
    bind_port: int,
    cert_file: Path,
    key_file: Path,
    state_path: Path,
) -> None:
    if not cert_file.is_file():
        raise GenesisReceiverError("genesis_receiver_missing_cert_file")
    if not key_file.is_file():
        raise GenesisReceiverError("genesis_receiver_missing_key_file")
    if bind_port < 1 or bind_port > 65535:
        raise GenesisReceiverError("genesis_receiver_invalid_port")

    server = ThreadingHTTPServer((bind_host, bind_port), make_handler(state_path))
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file))
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


def _require_schema(payload: Mapping[str, object]) -> None:
    if payload.get("schema_version") != SERVING_RECEIPT_SCHEMA_VERSION:
        raise GenesisReceiverError("genesis_receiver_schema_version_mismatch")


def _require_object(value: object, token: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise GenesisReceiverError(token)
    return value  # type: ignore[return-value]


def _require_str(value: object, token: str) -> str:
    if not isinstance(value, str) or value == "":
        raise GenesisReceiverError(token)
    return value


def _require_sha(value: object, token: str) -> str:
    if not isinstance(value, str):
        raise GenesisReceiverError(token)
    try:
        require_sha256_hex(value, token)
    except ValueError as exc:
        raise GenesisReceiverError(token) from exc
    return value


def _require_cid(value: object, token: str) -> str:
    if not isinstance(value, str) or value == "":
        raise GenesisReceiverError(token)
    try:
        parse_nodeid_strict(value)
    except ValueError as exc:
        raise GenesisReceiverError(token) from exc
    return value


def _load_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GenesisReceiverError("genesis_receiver_invalid_state_file") from exc
    if not isinstance(parsed, dict):
        raise GenesisReceiverError("genesis_receiver_invalid_state_file")
    try:
        reject_float(parsed, "genesis_receiver_float_not_allowed")
    except ValueError as exc:
        raise GenesisReceiverError(str(exc)) from exc
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind-host", required=True)
    parser.add_argument("--bind-port", required=True, type=int)
    parser.add_argument("--cert-file", required=True, type=Path)
    parser.add_argument("--key-file", required=True, type=Path)
    parser.add_argument("--state-path", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_server(
        bind_host=args.bind_host,
        bind_port=args.bind_port,
        cert_file=args.cert_file,
        key_file=args.key_file,
        state_path=args.state_path,
    )


if __name__ == "__main__":
    main()
