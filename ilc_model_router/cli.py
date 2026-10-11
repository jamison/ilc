# SPDX-License-Identifier: AGPL-3.0-only
"""CLI surface for the local-first Model Router sidecar."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import lmdb

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore

from .adapter import ProviderAdapter, ProviderResponse, ROUTER_CAPABILITY_CLASSES, RouterRequest
from .anthropic_adapter import AnthropicAdapter, DEFAULT_OPENROUTER_ENDPOINT
from .receipt_schema import RouterReceipt, RouterReceiptError
from .receipt_store import (
    list_router_receipts,
    lookup_by_token,
    open_router_receipt_env,
    update_receipt_consent_status,
)
from .router_engine import RouterEngine

MODEL_ROUTER_CLI_VERSION = "model_router_cli_phase_1614.v0.1"
GRAPH_PROMOTION_NOT_ACTIVATED = False
MODEL_ROUTER_CONSENT_SCHEMA_VERSION = "model_router_consent.v0.1"
MODEL_INFERENCE_NODE_SCHEMA_VERSION = "model_inference_node.v0.1"
MODEL_ROUTER_GRAPH_PROMOTION_CDL_AUTHORITY = (
    "cdl_116_model_router_v1_ratified_GAP_CDL_MODEL_ROUTER_RATIFY_00"
)
MODEL_ROUTER_FIRST_RUN_NOTICE = (
    "Model Router will promote eligible receipt metadata to the public ILC graph by default.\n"
    "Only allowlisted bounded metadata is published — never raw prompts, completions, or API keys.\n"
    "To disable: ilc sidecar model-router set-consent disabled\n"
    "To suppress per call: ilc sidecar model-router route ... --no-promote"
)
DEFAULT_MODEL_ROUTER_STORE_PATH = Path.home() / ".ilc" / "model_router" / "receipts.lmdb"
DEFAULT_MODEL_ROUTER_CONSENT_PATH = Path.home() / ".ilc" / "model_router" / "consent.json"
DEFAULT_MODEL_ROUTER_GRAPH_STORE_PATH = Path.home() / ".ilc" / "model_router" / "truth_graph.lmdb"
DEFAULT_PROMOTION_DIR = Path("out/model_router_promotions")
_PROMOTED_FIELD_ORDER = (
    "agent_id",
    "capability_class",
    "cdl_authority",
    "consent_status",
    "epoch",
    "model_id",
    "node_kind",
    "privacy_boundary",
    "provider",
    "receipt_payload_sha256",
    "receipt_status",
    "receipt_token",
    "schema_version",
    "source",
    "token_counts_input",
    "token_counts_output",
)
_PROMOTED_FIELDS_ALLOWLIST = frozenset(_PROMOTED_FIELD_ORDER)
_PROMOTION_RECEIPT_EXPORT_FIELD_ORDER = (
    "consent_status",
    "model_id",
    "node_id",
    "node_written",
    "promotion_status",
    "receipt_token",
    "status",
    "version",
)
_HEX = frozenset("0123456789abcdef")


class _DryRunAdapter(ProviderAdapter):
    def route(
        self,
        request: RouterRequest,
        *,
        timeout: float | None = None,
    ) -> ProviderResponse:
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
    if command == "set-consent":
        return _set_consent(args)
    if command == "werner-context":
        return _werner_context(args)
    raise ValueError(f"model_router_unknown_command:{command}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ilc sidecar model-router")
    subparsers = parser.add_subparsers(dest="model_router_command", required=True)

    route = subparsers.add_parser("route", help="Route a local model request")
    route.add_argument("--model", required=True, dest="model_id")
    route.add_argument("--provider", required=True)
    route.add_argument("--message", required=True)
    route.add_argument(
        "--capability-class",
        choices=sorted(ROUTER_CAPABILITY_CLASSES),
        default="inference",
    )
    route.add_argument("--agent-id", default="c" * 96)
    route.add_argument("--epoch", type=int, default=0)
    route.add_argument("--store-path", default="")
    route.add_argument("--graph-store-path", default="")
    route.add_argument("--no-promote", action="store_true")
    route.add_argument("--dry-run", action="store_true")
    route.add_argument("--timeout", type=float, default=30.0)

    list_receipts = subparsers.add_parser("list-receipts", help="List local router receipts")
    list_receipts.add_argument("--store-path", default="")
    list_receipts.add_argument("--limit", type=int, default=100)

    promote = subparsers.add_parser("promote-receipt", help="Promote a local receipt to the graph")
    promote.add_argument("receipt_token")
    promote.add_argument("--store-path", default="")
    promote.add_argument("--graph-store-path", default="")
    promote.add_argument("--out-dir", default="")

    set_consent = subparsers.add_parser("set-consent", help="Set Model Router graph-promotion consent")
    set_consent.add_argument("state", choices=("enabled", "disabled"))

    werner_ctx = subparsers.add_parser(
        "werner-context",
        help="Compute Werner flow budget from local receipts for an agent/epoch",
    )
    werner_ctx.add_argument("--agent-id", required=True)
    werner_ctx.add_argument("--epoch", type=int, required=True)
    werner_ctx.add_argument("--store-path", default="")
    werner_ctx.add_argument("--limit", type=int, default=500)

    return parser


def _route(args: argparse.Namespace) -> dict[str, Any]:
    request = RouterRequest.build(
        model_id=args.model_id,
        provider=args.provider,
        messages=(_parse_message(args.message),),
        agent_id_hex=args.agent_id,
        epoch=args.epoch,
        capability_class=args.capability_class,
    )
    adapter = _DryRunAdapter() if args.dry_run else _adapter_from_args(args)
    env = open_router_receipt_env(_store_path(args.store_path))
    try:
        receipt = RouterEngine(adapter, env, timeout=args.timeout).route(request)
        result = _route_result(receipt)
        if getattr(args, "no_promote", False):
            result["promotion_status"] = "suppressed_no_promote"
            return result
        try:
            consent = _load_consent_state()
        except ValueError as exc:
            result["consent_status"] = "local_only"
            result["promotion_status"] = "local_only"
            result["consent_error_token"] = str(exc)
            return result
        if not consent["promotion_enabled"]:
            result["promotion_status"] = "local_only"
            return result
        if not consent["first_run_notice_acknowledged"]:
            result["first_run_notice"] = MODEL_ROUTER_FIRST_RUN_NOTICE
            _write_consent_state(
                promotion_enabled=True,
                first_run_notice_acknowledged=True,
            )
        if GRAPH_PROMOTION_NOT_ACTIVATED:
            raise ValueError("model_router_graph_promotion_guard_active")
        node_payload = _promotion_node_payload(receipt)
        update_receipt_consent_status(env, receipt.receipt_token, "promotion_pending")
        try:
            promoted = _write_promotion_node(
                receipt,
                graph_store_path=_graph_store_path(getattr(args, "graph_store_path", "")),
                node_payload=node_payload,
            )
        except (OSError, lmdb.Error) as exc:
            result["consent_status"] = "promotion_pending"
            result["promotion_status"] = "pending_catch_up"
            result["catch_up_token"] = receipt.receipt_token
            result["promotion_error_token"] = f"model_router_graph_promotion_failed:{type(exc).__name__}"
            return result
        update_receipt_consent_status(env, receipt.receipt_token, "promoted")
        result["consent_status"] = "promoted"
        result["node_id"] = promoted["node_id"]
        result["node_written"] = promoted["node_written"]
        result["promotion_status"] = "promoted"
        return result
    finally:
        env.close()


def _route_result(receipt: RouterReceipt) -> dict[str, Any]:
    return {
        "consent_status": receipt.companion.consent_status,
        "error_token": receipt.error_token,
        "capability_class": receipt.companion.capability_class,
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
        if receipt is None:
            raise ValueError("model_router_receipt_not_found")
        promoted = _write_promotion_node(
            receipt,
            graph_store_path=_graph_store_path(getattr(args, "graph_store_path", "")),
        )
        update_receipt_consent_status(env, receipt.receipt_token, "promoted")
    finally:
        env.close()
    payload = _promotion_receipt_export_payload(receipt, promoted)
    out_dir = _promotion_dir(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(out_dir / f"{receipt.receipt_token}.json", payload)
    return payload


def _set_consent(args: argparse.Namespace) -> dict[str, Any]:
    promotion_enabled = args.state == "enabled"
    state = _write_consent_state(
        promotion_enabled=promotion_enabled,
        first_run_notice_acknowledged=promotion_enabled,
    )
    return {
        "consent_path": str(_consent_path()),
        "first_run_notice_acknowledged": state["first_run_notice_acknowledged"],
        "promotion_enabled": state["promotion_enabled"],
        "schema_version": state["schema_version"],
        "version": MODEL_ROUTER_CLI_VERSION,
    }


def _werner_context(args: argparse.Namespace) -> dict[str, Any]:
    from .werner_model_router_bridge import compute_werner_model_router_context

    env = open_router_receipt_env(_store_path(args.store_path))
    try:
        all_receipts = list_router_receipts(env, limit=args.limit)
    finally:
        env.close()
    agent_receipts = [
        receipt
        for receipt in all_receipts
        if receipt.agent_id_hex == args.agent_id and receipt.epoch == args.epoch
    ]
    context = compute_werner_model_router_context(
        agent_id=args.agent_id,
        epoch=args.epoch,
        receipts=agent_receipts,
    )
    return {
        "absent_token": context.absent_token,
        "agent_id": context.agent_id,
        "bridge_version": context.bridge_version,
        "candidate_priority": str(context.candidate_priority),
        "capped_agent_signal": str(context.capped_agent_signal),
        "cdl_version": context.cdl_version,
        "epoch": context.epoch,
        "flow_budget": str(context.flow_budget),
        "non_claims": list(context.non_claims),
        "receipt_count": context.receipt_count,
        "version": MODEL_ROUTER_CLI_VERSION,
        "werner_context_present": context.werner_context_present,
    }


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


def _graph_store_path(value: str) -> Path:
    raw = value or os.environ.get("ILC_MODEL_ROUTER_GRAPH_STORE_PATH", "")
    return Path(raw).expanduser() if raw else DEFAULT_MODEL_ROUTER_GRAPH_STORE_PATH


def _consent_path() -> Path:
    raw = os.environ.get("ILC_MODEL_ROUTER_CONSENT_PATH", "")
    return Path(raw).expanduser() if raw else DEFAULT_MODEL_ROUTER_CONSENT_PATH


def _promotion_dir(value: str) -> Path:
    raw = value or os.environ.get("ILC_MODEL_ROUTER_PROMOTION_DIR", "")
    return Path(raw).expanduser() if raw else DEFAULT_PROMOTION_DIR


def _require_receipt_token(value: str) -> str:
    if type(value) is not str or len(value) != 64:
        raise ValueError("model_router_receipt_token_invalid")
    if value.lower() != value or any(char not in _HEX for char in value):
        raise ValueError("model_router_receipt_token_invalid")
    return value


def _load_consent_state() -> dict[str, Any]:
    path = _consent_path()
    if not path.exists():
        return {
            "schema_version": MODEL_ROUTER_CONSENT_SCHEMA_VERSION,
            "promotion_enabled": True,
            "first_run_notice_acknowledged": False,
            "updated_at_utc": "",
            "source": "ilc_model_router_cli",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("model_router_consent_file_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("model_router_consent_file_invalid")
    if payload.get("schema_version") != MODEL_ROUTER_CONSENT_SCHEMA_VERSION:
        raise ValueError("model_router_consent_schema_version_invalid")
    if type(payload.get("promotion_enabled")) is not bool:
        raise ValueError("model_router_consent_promotion_enabled_invalid")
    if type(payload.get("first_run_notice_acknowledged")) is not bool:
        raise ValueError("model_router_consent_first_run_notice_acknowledged_invalid")
    if payload.get("source") != "ilc_model_router_cli":
        raise ValueError("model_router_consent_source_invalid")
    return payload


def _write_consent_state(
    *,
    promotion_enabled: bool,
    first_run_notice_acknowledged: bool,
) -> dict[str, Any]:
    if type(promotion_enabled) is not bool or type(first_run_notice_acknowledged) is not bool:
        raise ValueError("model_router_consent_state_invalid")
    payload = {
        "first_run_notice_acknowledged": first_run_notice_acknowledged,
        "promotion_enabled": promotion_enabled,
        "schema_version": MODEL_ROUTER_CONSENT_SCHEMA_VERSION,
        "source": "ilc_model_router_cli",
        "updated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    path = _consent_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(path, payload)
    return payload


def _receipt_payload_sha256(receipt: RouterReceipt) -> str:
    # The public graph node records the publication event. Canonicalize the
    # companion status to "promoted" before hashing so local_only, pending, and
    # already-promoted catch-up paths converge on the same node ID. to_dict()
    # returns fresh nested dicts, so this normalization does not mutate receipt.
    payload = receipt.to_dict()
    payload["companion"]["consent_status"] = "promoted"
    encoded = json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _promoted_node_record(receipt: RouterReceipt) -> dict[str, Any]:
    record = {
        "agent_id": receipt.agent_id_hex,
        "capability_class": receipt.companion.capability_class,
        "cdl_authority": MODEL_ROUTER_GRAPH_PROMOTION_CDL_AUTHORITY,
        "consent_status": "promoted",
        "epoch": receipt.epoch,
        "model_id": receipt.companion.model_id,
        "node_kind": "model_inference",
        "privacy_boundary": "allowlisted_metadata_only",
        "provider": receipt.companion.provider,
        "receipt_payload_sha256": _receipt_payload_sha256(receipt),
        "receipt_status": receipt.status,
        "receipt_token": receipt.receipt_token,
        "schema_version": MODEL_INFERENCE_NODE_SCHEMA_VERSION,
        "source": "ilc_model_router",
        "token_counts_input": receipt.companion.token_counts_input,
        "token_counts_output": receipt.companion.token_counts_output,
    }
    if frozenset(record) != _PROMOTED_FIELDS_ALLOWLIST:
        raise ValueError("model_router_promoted_node_field_set_invalid")
    return {field: record[field] for field in _PROMOTED_FIELD_ORDER}


def _write_promotion_node(
    receipt: RouterReceipt,
    *,
    graph_store_path: Path,
    node_payload: tuple[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if GRAPH_PROMOTION_NOT_ACTIVATED:
        raise ValueError("model_router_graph_promotion_guard_active")
    node_id, node_record = node_payload or _promotion_node_payload(receipt)
    store = TruthPrimitiveGraphStore(graph_store_path)
    try:
        node_written = store.put_node_if_absent(node_id, node_record)
    finally:
        store.close()
    return {
        "node_id": node_id,
        "node_record": node_record,
        "node_written": node_written,
    }


def _promotion_node_payload(receipt: RouterReceipt) -> tuple[str, dict[str, Any]]:
    node_record = _promoted_node_record(receipt)
    node_id = node_id_from_obj(node_record)
    return node_id, node_record


def _promotion_receipt_export_payload(
    receipt: RouterReceipt,
    promoted: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "consent_status": "promoted",
        "model_id": receipt.companion.model_id,
        "node_id": promoted["node_id"],
        "node_written": promoted["node_written"],
        "promotion_status": "promoted",
        "receipt_token": receipt.receipt_token,
        "status": receipt.status,
        "version": MODEL_ROUTER_CLI_VERSION,
    }
    if tuple(payload) != _PROMOTION_RECEIPT_EXPORT_FIELD_ORDER:
        raise ValueError("model_router_promotion_export_field_order_invalid")
    return payload


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    "DEFAULT_MODEL_ROUTER_CONSENT_PATH",
    "DEFAULT_MODEL_ROUTER_GRAPH_STORE_PATH",
    "MODEL_ROUTER_CLI_VERSION",
    "GRAPH_PROMOTION_NOT_ACTIVATED",
    "MODEL_INFERENCE_NODE_SCHEMA_VERSION",
    "MODEL_ROUTER_CONSENT_SCHEMA_VERSION",
    "_PROMOTED_FIELDS_ALLOWLIST",
    "main",
    "run_model_router_command",
]
