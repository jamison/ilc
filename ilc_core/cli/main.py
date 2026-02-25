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
QUERY_SCHEMA_VERSION = "299.v0.1"
VERIFY_SCHEMA_VERSION = "301.v0.1"

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


class QueryCommandError(Exception):
    """Typed error carrying query contract error token and message."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class VerifyCommandError(Exception):
    """Typed error carrying verify contract error token and message."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


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


def _infer_query_command_token_from_argv() -> str:
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
        return f"query {sys.argv[2]}"
    return "query"


def _infer_verify_command_token_from_argv() -> str:
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
        return f"verify {sys.argv[2]}"
    return "verify"


def _query_success_payload(command_token: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "meta": {
            "command": command_token,
            "schema_version": QUERY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _query_error_payload(command_token: str, code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "meta": {
            "command": command_token,
            "schema_version": QUERY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _verify_success_payload(command_token: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "meta": {
            "command": command_token,
            "schema_version": VERIFY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _verify_error_payload(command_token: str, code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "meta": {
            "command": command_token,
            "schema_version": VERIFY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


class JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that emits JSON errors with exit code 2."""

    def error(self, message: str) -> None:  # pragma: no cover - exercised via subprocess
        command = _infer_command_from_argv()
        if command == "query":
            payload = _query_error_payload(
                command_token=_infer_query_command_token_from_argv(),
                code="query_invalid_input",
                message=message,
            )
        elif command == "verify":
            payload = _verify_error_payload(
                command_token=_infer_verify_command_token_from_argv(),
                code="verify_invalid_input",
                message=message,
            )
        else:
            payload = _error_payload(
                command=command,
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


def _identity_state_path(graph_state_path: Path) -> Path:
    env_override = os.environ.get("ILC_IDENTITY_STATE_PATH")
    if env_override:
        return Path(env_override)
    return graph_state_path.with_name(".ilc_d2e04_identity_state.json")


def _load_identity_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("identity_state_not_object")
    return data


def _write_identity_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _run_identity_subcommand(args: argparse.Namespace, graph_state_path: Path) -> dict[str, Any]:
    state_path = _identity_state_path(graph_state_path)
    subcommand = getattr(args, "identity_subcommand", None)

    # Preserve D2e-03 compatibility for bare `ilc identity`.
    if not subcommand:
        return {
            "lineage_id": "lineage-local",
            "status": "active",
            "export_ref": "identity-local",
            "mode": "prototype_compat",
        }

    current = _load_identity_state(state_path)

    if subcommand == "init":
        if current is not None:
            raise ValueError("identity_already_initialized")
        lineage_id = getattr(args, "lineage_id", None) or "lineage-local"
        key_ref = getattr(args, "key_ref", None) or "key-local-0"
        state = {
            "lineage_id": lineage_id,
            "status": "active",
            "key_ref": key_ref,
            "rotation_count": 0,
            "updated_at": _now_rfc3339_utc(),
        }
        _write_identity_state(state_path, state)
        return {"action": "init", "state_path": str(state_path), "state": state}

    if current is None:
        raise ValueError("identity_not_initialized")

    if subcommand == "show":
        return {"action": "show", "state_path": str(state_path), "state": current}

    if subcommand == "rotate":
        new_key_ref = getattr(args, "new_key_ref", None)
        next_count = int(current.get("rotation_count", 0)) + 1
        current["rotation_count"] = next_count
        current["key_ref"] = new_key_ref or f"key-local-{next_count}"
        current["status"] = "active"
        current["updated_at"] = _now_rfc3339_utc()
        _write_identity_state(state_path, current)
        return {"action": "rotate", "state_path": str(state_path), "state": current}

    if subcommand == "export":
        return {
            "action": "export",
            "state_path": str(state_path),
            "export": {
                "lineage_id": current.get("lineage_id"),
                "status": current.get("status"),
                "rotation_count": current.get("rotation_count"),
                "key_ref": current.get("key_ref"),
            },
        }

    raise ValueError(f"unknown_identity_subcommand:{subcommand}")


def _read_graph_state(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"graph_state_read_failed:{exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"graph_state_invalid_json:{exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError("graph_state_not_object")
    return data


def _load_graph_state_for_query(path: Path) -> dict[str, Any]:
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise QueryCommandError("query_backend_unavailable", str(exc)) from exc


def _load_graph_state_for_verify(path: Path) -> dict[str, Any]:
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise VerifyCommandError("verify_backend_unavailable", str(exc)) from exc


def _sorted_mapping(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: _sorted_mapping(obj[key]) for key in sorted(obj)}
    if isinstance(obj, list):
        return [_sorted_mapping(item) for item in obj]
    return obj


def _coerce_list(obj: Any, code: str, message: str) -> list[dict[str, Any]]:
    if obj is None:
        return []
    if not isinstance(obj, list):
        raise QueryCommandError(code, message)
    rows: list[dict[str, Any]] = []
    for item in obj:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _query_node(state: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = _coerce_list(state.get("nodes"), "query_backend_unavailable", "graph_nodes_not_list")
    node: dict[str, Any] | None = None
    for candidate in nodes:
        token = candidate.get("node_id", candidate.get("id"))
        if token is not None and str(token) == node_id:
            node = candidate
            break
    if node is None:
        raise QueryCommandError("query_not_found", f"node_not_found:{node_id}")
    return {"node_id": node_id, "node": _sorted_mapping(node), "query": "node"}


def _query_epoch(state: dict[str, Any], epoch_token: int) -> dict[str, Any]:
    epochs = _coerce_list(state.get("epochs"), "query_backend_unavailable", "graph_epochs_not_list")
    epoch: dict[str, Any] | None = None
    for candidate in epochs:
        value = candidate.get("epoch")
        if value is None:
            value = candidate.get("epoch_id")
        if value is None:
            continue
        if str(value) == str(epoch_token):
            epoch = candidate
            break
    if epoch is None:
        raise QueryCommandError("query_not_found", f"epoch_not_found:{epoch_token}")
    return {"epoch": _sorted_mapping(epoch), "query": "epoch", "requested_epoch": epoch_token}


def _query_claim(state: dict[str, Any], claim_id: str) -> dict[str, Any]:
    nodes = _coerce_list(state.get("nodes"), "query_backend_unavailable", "graph_nodes_not_list")
    matches: list[dict[str, Any]] = []
    for candidate in nodes:
        token = candidate.get("claim_id")
        if token is not None and str(token) == claim_id:
            matches.append(candidate)
    if not matches:
        raise QueryCommandError("query_not_found", f"claim_not_found:{claim_id}")
    stable_matches = sorted(
        (_sorted_mapping(match) for match in matches),
        key=lambda item: json.dumps(item, sort_keys=True),
    )
    return {
        "claim_id": claim_id,
        "count": len(stable_matches),
        "matches": stable_matches,
        "query": "claim",
    }


def _query_command_token(args: argparse.Namespace) -> str:
    subcommand = getattr(args, "query_subcommand", None)
    if subcommand:
        return f"query {subcommand}"
    return "query"


def _run_query_subcommand(args: argparse.Namespace, graph_state_path: Path) -> tuple[str, dict[str, Any]]:
    state = _load_graph_state_for_query(graph_state_path)
    subcommand = getattr(args, "query_subcommand", None)

    if subcommand == "node":
        return _query_command_token(args), _query_node(state, str(args.node_id))
    if subcommand == "epoch":
        return _query_command_token(args), _query_epoch(state, args.epoch)
    if subcommand == "claim":
        return _query_command_token(args), _query_claim(state, str(args.claim_id))
    raise QueryCommandError("query_invalid_input", "query_subcommand_missing")


def _verify_command_token(args: argparse.Namespace) -> str:
    subcommand = getattr(args, "verify_subcommand", None)
    if subcommand:
        return f"verify {subcommand}"
    return "verify"


def _check(check_type: str, passed: bool, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    item = {"check_type": check_type, "passed": bool(passed)}
    if detail:
        item["detail"] = _sorted_mapping(detail)
    return item


def _verify_claim(state: dict[str, Any], claim_id: str) -> dict[str, Any]:
    nodes = _coerce_list(state.get("nodes"), "verify_backend_unavailable", "graph_nodes_not_list")
    matches = [candidate for candidate in nodes if str(candidate.get("claim_id", "")) == claim_id]
    checks = [
        _check("subject_exists", len(matches) > 0),
        _check("multi_match_supported", True, {"match_count": len(matches)}),
    ]
    if not matches:
        raise VerifyCommandError("verify_not_found", f"claim_not_found:{claim_id}")
    return {
        "subject": {"claim_id": claim_id},
        "verdict": {"verified": True, "verdict_code": "verify_claim_passed"},
        "checks": checks,
    }


def _verify_node(state: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = _coerce_list(state.get("nodes"), "verify_backend_unavailable", "graph_nodes_not_list")
    node: dict[str, Any] | None = None
    for candidate in nodes:
        token = candidate.get("node_id", candidate.get("id"))
        if token is not None and str(token) == node_id:
            node = candidate
            break
    checks = [
        _check("subject_exists", node is not None),
        _check("node_identifier_consistency", True, {"accepted_keys": ["node_id", "id"]}),
    ]
    if node is None:
        raise VerifyCommandError("verify_not_found", f"node_not_found:{node_id}")
    return {
        "subject": {"node_id": node_id},
        "verdict": {"verified": True, "verdict_code": "verify_node_passed"},
        "checks": checks,
    }


def _verify_lineage(args: argparse.Namespace, graph_state_path: Path) -> dict[str, Any]:
    lineage_id = str(args.lineage_id)
    state_path = _identity_state_path(graph_state_path)
    current = _load_identity_state(state_path)
    if current is None:
        raise VerifyCommandError("verify_not_found", f"lineage_not_initialized:{lineage_id}")

    observed_lineage = str(current.get("lineage_id", ""))
    matched = observed_lineage == lineage_id
    checks = [
        _check("identity_state_present", True, {"state_path": str(state_path)}),
        _check("lineage_id_match", matched, {"observed_lineage_id": observed_lineage}),
    ]
    if not matched:
        raise VerifyCommandError("verify_not_found", f"lineage_not_found:{lineage_id}")

    return {
        "subject": {"lineage_id": lineage_id},
        "verdict": {"verified": True, "verdict_code": "verify_lineage_passed"},
        "checks": checks,
    }


def _run_verify_subcommand(args: argparse.Namespace, graph_state_path: Path) -> tuple[str, dict[str, Any]]:
    # Lineage verification is intentionally local-state only in Phase 302.
    subcommand = getattr(args, "verify_subcommand", None)
    if subcommand == "lineage":
        return _verify_command_token(args), _verify_lineage(args, graph_state_path)

    state = _load_graph_state_for_verify(graph_state_path)
    if subcommand == "claim":
        return _verify_command_token(args), _verify_claim(state, str(args.claim_id))
    if subcommand == "node":
        return _verify_command_token(args), _verify_node(state, str(args.node_id))
    raise VerifyCommandError("verify_invalid_input", "verify_subcommand_missing")


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
        if command == "query":
            query_parser = subparsers.add_parser("query", help="Prototype `query` command")
            query_subparsers = query_parser.add_subparsers(dest="query_subcommand", required=True)

            p_node = query_subparsers.add_parser("node", help="Query by node identifier")
            p_node.add_argument("--node-id", required=True, help="Node identifier")

            p_epoch = query_subparsers.add_parser("epoch", help="Query by epoch identifier")
            p_epoch.add_argument("--epoch", type=int, required=True, help="Epoch number")

            p_claim = query_subparsers.add_parser("claim", help="Query by claim identifier")
            p_claim.add_argument("--claim-id", required=True, help="Claim identifier")
            continue

        if command == "verify":
            verify_parser = subparsers.add_parser("verify", help="Prototype `verify` command")
            verify_subparsers = verify_parser.add_subparsers(dest="verify_subcommand", required=True)

            p_verify_claim = verify_subparsers.add_parser("claim", help="Verify by claim identifier")
            p_verify_claim.add_argument("--claim-id", required=True, help="Claim identifier")

            p_verify_node = verify_subparsers.add_parser("node", help="Verify by node identifier")
            p_verify_node.add_argument("--node-id", required=True, help="Node identifier")

            p_verify_lineage = verify_subparsers.add_parser("lineage", help="Verify by lineage identifier")
            p_verify_lineage.add_argument("--lineage-id", required=True, help="Lineage identifier")
            continue

        if command != "identity":
            subparsers.add_parser(command, help=f"Prototype `{command}` command")
            continue

        identity_parser = subparsers.add_parser("identity", help="Prototype `identity` command")
        identity_subparsers = identity_parser.add_subparsers(dest="identity_subcommand")

        p_init = identity_subparsers.add_parser("init", help="Initialize local identity state")
        p_init.add_argument("--lineage-id", default="lineage-local", help="Lineage identifier")
        p_init.add_argument("--key-ref", default="key-local-0", help="Initial key reference")

        identity_subparsers.add_parser("show", help="Show local identity state")

        p_rotate = identity_subparsers.add_parser("rotate", help="Rotate identity key reference")
        p_rotate.add_argument("--new-key-ref", default=None, help="Replacement key reference")

        identity_subparsers.add_parser("export", help="Export sanitized identity snapshot")

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
        graph_state_path = Path(args.graph_state)
        if command not in {"query", "verify"}:
            _ensure_local_graph_state(graph_state_path, command)

        if command == "query":
            query_command, data = _run_query_subcommand(args, graph_state_path)
            payload = _query_success_payload(query_command, data)
        elif command == "verify":
            verify_command, data = _run_verify_subcommand(args, graph_state_path)
            payload = _verify_success_payload(verify_command, data)
        elif command == "identity":
            data = _run_identity_subcommand(args, graph_state_path)
            payload = _success_payload(command, data)
        else:
            data = _prototype_data_for_command(command)
            payload = _success_payload(command, data)
        print(json.dumps(payload, sort_keys=True))
        return 0
    except QueryCommandError as exc:
        payload = _query_error_payload(
            command_token=_query_command_token(args),
            code=exc.code,
            message=exc.message,
        )
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return 1
    except VerifyCommandError as exc:
        payload = _verify_error_payload(
            command_token=_verify_command_token(args),
            code=exc.code,
            message=exc.message,
        )
        print(json.dumps(payload, sort_keys=True), file=sys.stderr)
        return 1
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
