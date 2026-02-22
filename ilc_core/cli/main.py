"""D2e-03 JSON-first CLI prototype.

This module implements the Phase-264 prototype runtime aligned to the locked
command surface. DAG-CBOR encoding remains deferred to later phases.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "254.v0.1"

PRIMITIVE_COMMANDS = (
    "assert",
    "validate",
    "contradict",
    "refute",
    "revise",
    "link",
    "epoch",
)

OPERATIONAL_COMMANDS = (
    "query",
    "verify",
    "balance",
    "identity",
    "bundle",
    "shard",
    "capproof",
    "config",
)

ALL_COMMANDS = PRIMITIVE_COMMANDS + OPERATIONAL_COMMANDS


def _now_rfc3339_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _success_payload(command: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "ok": True,
        "ts_utc": _now_rfc3339_utc(),
        "data": data,
    }


def _error_payload(
    command: str,
    code: int,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "ok": False,
        "error": True,
        "code": str(code),
        "message": message,
        "details": details or {},
    }


def _infer_command_from_argv() -> str:
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        return sys.argv[1]
    return "unknown"


class JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that emits JSON errors with exit code 2."""

    def error(self, message: str) -> None:  # pragma: no cover - exercised via subprocess
        payload = _error_payload(
            command=_infer_command_from_argv(),
            code=2,
            message=message,
            details={"usage": self.format_usage().strip()},
        )
        print(json.dumps(payload), file=sys.stderr)
        raise SystemExit(2)


def _prototype_data_for_command(command: str) -> dict[str, Any]:
    data_by_command: dict[str, dict[str, Any]] = {
        "assert": {
            "claim_cid": "bafy-prototype-claim",
            "epoch_id": "epoch-local",
            "lineage_id": "lineage-local",
        },
        "validate": {
            "target_cid": "bafy-target",
            "validation_cid": "bafy-validation",
            "accepted": True,
        },
        "contradict": {
            "target_cid": "bafy-target",
            "contradiction_cid": "bafy-contradiction",
            "accepted": True,
        },
        "refute": {
            "target_cid": "bafy-target",
            "refutation_cid": "bafy-refutation",
            "accepted": True,
        },
        "revise": {
            "target_cid": "bafy-original",
            "revision_cid": "bafy-revision",
            "supersedes": "bafy-original",
        },
        "link": {
            "source_cid": "bafy-source",
            "target_cid": "bafy-target",
            "edge_type": "supports",
            "edge_cid": "bafy-edge",
        },
        "epoch": {
            "epoch_id": "epoch-local",
            "state": "open",
            "finalization_hash": "sha256:prototype",
        },
        "query": {
            "query": "prototype",
            "results": [],
            "count": 0,
        },
        "verify": {
            "subject": "prototype",
            "verified": True,
            "verification_type": "prototype",
        },
        "balance": {
            "account_id": "acct-prototype",
            "ecu_balance": 0.0,
            "pending_balance": 0.0,
        },
        "identity": {
            "lineage_id": "lineage-local",
            "status": "active",
            "export_ref": "identity-local",
        },
        "bundle": {
            "bundle_cid": "bafy-bundle",
            "valid": True,
            "manifest_ref": "manifest-local",
        },
        "shard": {
            "shard_id": "shard-local",
            "assignment": "local",
            "routing_status": "deferred_star_map",
        },
        "capproof": {
            "probe_set": "phase-264-prototype",
            "overall_pass": True,
            "probe_results": [],
        },
        "config": {
            "profile": "default",
            "changed_keys": [],
            "effective_config_ref": "config-local",
        },
    }
    if command not in data_by_command:
        raise ValueError(f"unknown_command: {command}")
    return data_by_command[command]


def _default_graph_state_path() -> Path:
    return Path(os.environ.get("ILC_CLI_GRAPH_STATE_PATH", ".ilc_d2e03_graph.json"))


def _ensure_local_graph_state(path: Path, command: str) -> None:
    if path.exists():
        raw = path.read_text(encoding="utf-8")
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            raise ValueError("graph_state_not_object")
    else:
        obj = {
            "schema_version": "d2e03.v0.1",
            "nodes": [],
            "edges": [],
            "epochs": [],
        }

    obj["last_command"] = command
    obj["updated_at"] = _now_rfc3339_utc()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        prog="ilc",
        description="ILC D2e-03 JSON-first CLI prototype",
    )
    parser.add_argument(
        "--graph-state",
        default=str(_default_graph_state_path()),
        help="Path to local JSON graph state file",
    )
    parser.add_argument(
        "--simulate-network-error",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ALL_COMMANDS:
        subparsers.add_parser(command, help=f"Prototype `{command}` command")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    command = str(args.command)

    if args.simulate_network_error:
        payload = _error_payload(
            command=command,
            code=3,
            message="simulated network transport failure",
            details={"phase": "264"},
        )
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return 3

    try:
        _ensure_local_graph_state(Path(args.graph_state), command)
        data = _prototype_data_for_command(command)
        payload = _success_payload(command, data)
        print(json.dumps(payload, sort_keys=True))
        return 0
    except ValueError as exc:
        payload = _error_payload(
            command=command,
            code=1,
            message=str(exc),
            details={"phase": "264"},
        )
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
