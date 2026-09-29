# SPDX-License-Identifier: AGPL-3.0-only
"""CLI surface for the local-first Model Router sidecar."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .adapter import ProviderAdapter, ProviderResponse, RouterRequest
from .anthropic_adapter import AnthropicAdapter, DEFAULT_OPENROUTER_ENDPOINT
from .receipt_schema import RouterReceiptError
from .receipt_store import (
    list_router_receipts,
    lookup_by_token,
    open_router_receipt_env,
)
from .router_engine import RouterEngine

MODEL_ROUTER_CLI_VERSION = "model_router_cli_phase_1614.v0.1"
MODEL_ROUTER_PROMOTION_NON_CLAIM = "graph_promotion_requires_cdl_116_phase_1615"
DEFAULT_MODEL_ROUTER_STORE_PATH = Path.home() / ".ilc" / "model_router" / "receipts.lmdb"
DEFAULT_PROMOTION_DIR = Path("out/model_router_promotions")
_HEX = frozenset("0123456789abcdef")


class _DryRunAdapter(ProviderAdapter):
    def route(self, request: RouterRequest) -> ProviderResponse:
        return ProviderResponse(
            status="success",
            content=f"dry-run response for {request.model_id}",
            error_token="",
            token_counts_input=10,
            token_counts_output=5,
        )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_model_router_command(args)
    except ValueError as exc:
        _write_json({"ok": False, "error": True, "message": str(exc)}, stderr=True)
        return 1
    _write_json(result)
    return 0


def run_model_router_command(args: argparse.Namespace) -> dict[str, Any]:
    command = getattr(args, "model_router_command", "")
    if command == "route":
        return _route(args)
    if command == "list-receipts":
        return _list_receipts(args)
    if command == "promote-receipt":
        return _promote_receipt(args)
    raise ValueError(f"model_router_unknown_command:{command}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ilc sidecar model-router")
    subparsers = parser.add_subparsers(dest="model_router_command", required=True)

    route = subparsers.add_parser("route", help="Route a local model request")
    route.add_argument("--model", required=True, dest="model_id")
    route.add_argument("--provider", required=True)
    route.add_argument("--message", required=True)
    route.add_argument("--agent-id", default="c" * 96)
    route.add_argument("--epoch", type=int, default=0)
    route.add_argument("--store-path", default="")
    route.add_argument("--dry-run", action="store_true")
    route.add_argument("--timeout", type=float, default=30.0)

    list_receipts = subparsers.add_parser("list-receipts", help="List local router receipts")
    list_receipts.add_argument("--store-path", default="")
    list_receipts.add_argument("--limit", type=int, default=100)

    promote = subparsers.add_parser("promote-receipt", help="Write a local promotion preview")
    promote.add_argument("receipt_token")
    promote.add_argument("--store-path", default="")
    promote.add_argument("--out-dir", default="")

    return parser


def _route(args: argparse.Namespace) -> dict[str, Any]:
    request = RouterRequest.build(
        model_id=args.model_id,
        provider=args.provider,
        messages=(_parse_message(args.message),),
        agent_id_hex=args.agent_id,
        epoch=args.epoch,
    )
    adapter = _DryRunAdapter() if args.dry_run else _adapter_from_args(args)
    env = open_router_receipt_env(_store_path(args.store_path))
    try:
        receipt = RouterEngine(adapter, env, timeout=args.timeout).route(request)
    finally:
        env.close()
    return {
        "consent_status": receipt.companion.consent_status,
        "model_id": receipt.companion.model_id,
        "receipt_token": receipt.receipt_token,
        "status": receipt.status,
        "token_counts_input": receipt.companion.token_counts_input,
        "token_counts_output": receipt.companion.token_counts_output,
        "version": MODEL_ROUTER_CLI_VERSION,
    }


def _list_receipts(args: argparse.Namespace) -> dict[str, Any]:
    env = open_router_receipt_env(_store_path(args.store_path))
    try:
        receipts = list_router_receipts(env, limit=args.limit)
    finally:
        env.close()
    return {
        "receipts": [
            {
                "consent_status": receipt.companion.consent_status,
                "epoch": receipt.epoch,
                "model_id": receipt.companion.model_id,
                "receipt_token": receipt.receipt_token,
                "status": receipt.status,
            }
            for receipt in receipts
        ],
        "version": MODEL_ROUTER_CLI_VERSION,
    }


def _promote_receipt(args: argparse.Namespace) -> dict[str, Any]:
    receipt_token = _require_receipt_token(args.receipt_token)
    env = open_router_receipt_env(_store_path(args.store_path))
    try:
        receipt = lookup_by_token(env, receipt_token)
    finally:
        env.close()
    if receipt is None:
        raise ValueError("model_router_receipt_not_found")
    payload = {
        "model_id": receipt.companion.model_id,
        "non_claim": MODEL_ROUTER_PROMOTION_NON_CLAIM,
        "promotion_status": "local_only_stub",
        "receipt_token": receipt.receipt_token,
        "status": receipt.status,
        "version": MODEL_ROUTER_CLI_VERSION,
    }
    out_dir = _promotion_dir(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(out_dir / f"{receipt.receipt_token}.json", payload)
    return payload


def _adapter_from_args(args: argparse.Namespace) -> ProviderAdapter:
    if args.provider not in {"anthropic", "openrouter"}:
        raise ValueError(f"model_router_provider_not_supported:{args.provider}")
    api_key = (
        os.environ.get("ILC_MODEL_ROUTER_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
        or ""
    )
    if not api_key:
        raise ValueError("model_router_api_key_required")
    endpoint = DEFAULT_OPENROUTER_ENDPOINT if args.provider == "openrouter" else None
    kwargs: dict[str, Any] = {
        "api_key": api_key,
        "provider_id": args.provider,
        "timeout": args.timeout,
    }
    if endpoint is not None:
        kwargs["endpoint"] = endpoint
    return AnthropicAdapter(**kwargs)


def _parse_message(raw: str) -> dict[str, Any]:
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("model_router_message_json_invalid") from exc
    if not isinstance(decoded, dict):
        raise ValueError("model_router_message_json_invalid")
    return decoded


def _store_path(value: str) -> Path:
    raw = value or os.environ.get("ILC_MODEL_ROUTER_STORE_PATH", "")
    return Path(raw).expanduser() if raw else DEFAULT_MODEL_ROUTER_STORE_PATH


def _promotion_dir(value: str) -> Path:
    raw = value or os.environ.get("ILC_MODEL_ROUTER_PROMOTION_DIR", "")
    return Path(raw).expanduser() if raw else DEFAULT_PROMOTION_DIR


def _require_receipt_token(value: str) -> str:
    if type(value) is not str or len(value) != 64:
        raise ValueError("model_router_receipt_token_invalid")
    if value.lower() != value or any(char not in _HEX for char in value):
        raise ValueError("model_router_receipt_token_invalid")
    return value


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload, allow_nan=False, indent=2, sort_keys=True).encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.write(b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _write_json(payload: dict[str, Any], *, stderr: bool = False) -> None:
    import sys

    stream = sys.stderr if stderr else sys.stdout
    print(json.dumps(payload, allow_nan=False, sort_keys=True), file=stream)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())


__all__ = [
    "MODEL_ROUTER_CLI_VERSION",
    "MODEL_ROUTER_PROMOTION_NON_CLAIM",
    "main",
    "run_model_router_command",
]
