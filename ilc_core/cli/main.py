# SPDX-License-Identifier: AGPL-3.0-only
"""D2e-03 JSON-first CLI prototype.

This module implements the Phase-264 prototype runtime aligned to the locked
command surface. DAG-CBOR encoding remains deferred to later phases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "254.v0.1"
QUERY_SCHEMA_VERSION = "299.v0.1"
VERIFY_SCHEMA_VERSION = "301.v0.1"
BUNDLE_SCHEMA_VERSION = "303.v0.1"

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
    "agent",
    "node",
    "sidecar",
    "ccss",
    "submit",
    "version",
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


class BundleCommandError(Exception):
    """Typed error carrying bundle contract error token and message."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _version_data() -> dict[str, Any]:
    return {
        "schema_versions": {
            "primary": SCHEMA_VERSION,
            "query": QUERY_SCHEMA_VERSION,
            "verify": VERIFY_SCHEMA_VERSION,
            "bundle": BUNDLE_SCHEMA_VERSION,
        },
        "supported_commands": sorted(ALL_COMMANDS),
    }


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


def _infer_bundle_command_token_from_argv() -> str:
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
        return f"bundle {sys.argv[2]}"
    return "bundle"


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


def _bundle_success_payload(command_token: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "meta": {
            "command": command_token,
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _bundle_error_payload(command_token: str, code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "meta": {
            "command": command_token,
            "schema_version": BUNDLE_SCHEMA_VERSION,
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
        elif command == "bundle":
            payload = _bundle_error_payload(
                command_token=_infer_bundle_command_token_from_argv(),
                code="bundle_invalid_input",
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


def _default_bundle_state_path() -> Path:
    return Path(os.environ.get("ILC_BUNDLE_STATE_PATH", ".ilc_d2e07_bundle_state.json"))


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


def _load_graph_state_for_bundle(path: Path) -> dict[str, Any]:
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise BundleCommandError("bundle_backend_unavailable", str(exc)) from exc


def _load_bundle_state_for_bundle(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "d2e07.v0.1", "bundles": []}
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise BundleCommandError("bundle_backend_unavailable", str(exc)) from exc


def _sorted_mapping(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: _sorted_mapping(obj[key]) for key in sorted(obj)}
    if isinstance(obj, list):
        return [_sorted_mapping(item) for item in obj]
    return obj


def _coerce_list(
    obj: Any,
    error_cls: type[QueryCommandError] | type[VerifyCommandError] | type[BundleCommandError],
    code: str,
    message: str,
) -> list[dict[str, Any]]:
    if obj is None:
        return []
    if not isinstance(obj, list):
        raise error_cls(code, message)
    rows: list[dict[str, Any]] = []
    for item in obj:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _query_node(state: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = _coerce_list(
        state.get("nodes"), QueryCommandError, "query_backend_unavailable", "graph_nodes_not_list"
    )
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
    epochs = _coerce_list(
        state.get("epochs"), QueryCommandError, "query_backend_unavailable", "graph_epochs_not_list"
    )
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
    nodes = _coerce_list(
        state.get("nodes"), QueryCommandError, "query_backend_unavailable", "graph_nodes_not_list"
    )
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
    subcommand = getattr(args, "query_subcommand", None)

    # CDL-075 truth primitive read path — does not load JSON graph state.
    if subcommand in {"truth-node", "truth-edges"}:
        from ilc_core.cli.d2e_query_truth_cli import (
            handle_query_truth_node,
            handle_query_truth_edges,
            QueryTruthCommandError,
        )
        try:
            if subcommand == "truth-node":
                data = handle_query_truth_node(str(args.node_id))
            else:
                data = handle_query_truth_edges(str(args.node_id))
        except QueryTruthCommandError as exc:
            raise QueryCommandError(exc.token, exc.message) from exc
        return _query_command_token(args), data

    state = _load_graph_state_for_query(graph_state_path)
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
    nodes = _coerce_list(
        state.get("nodes"), VerifyCommandError, "verify_backend_unavailable", "graph_nodes_not_list"
    )
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
    nodes = _coerce_list(
        state.get("nodes"), VerifyCommandError, "verify_backend_unavailable", "graph_nodes_not_list"
    )
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


def _bundle_command_token(args: argparse.Namespace) -> str:
    subcommand = getattr(args, "bundle_subcommand", None)
    if subcommand:
        return f"bundle {subcommand}"
    return "bundle"


def _bundle_entry(
    state: dict[str, Any],
    bundle_cid: str,
) -> dict[str, Any]:
    bundles = _coerce_list(
        state.get("bundles"),
        BundleCommandError,
        "bundle_backend_unavailable",
        "bundle_entries_not_list",
    )
    for candidate in bundles:
        token = candidate.get("bundle_cid")
        if token is not None and str(token) == bundle_cid:
            return candidate
    raise BundleCommandError("bundle_not_found", f"bundle_not_found:{bundle_cid}")


def _canonical_sha256(value: Any) -> str:
    stable = json.dumps(_sorted_mapping(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _bundle_inspect(bundle_cid: str, entry: dict[str, Any], bundle_state_path: Path) -> dict[str, Any]:
    provider = str(entry.get("provider", "local"))
    if provider == "blocked":
        raise BundleCommandError("bundle_provider_blocked", f"bundle_provider_blocked:{bundle_cid}")

    manifest = entry.get("manifest")
    checks = [
        _check("subject_exists", True),
        _check("manifest_object_present", isinstance(manifest, dict)),
        _check("provider_policy_allowed", True, {"provider": provider}),
    ]
    if not isinstance(manifest, dict):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_manifest_missing:{bundle_cid}")

    return {
        "subject": {
            "bundle_cid": bundle_cid,
            "bundle_state_path": str(bundle_state_path),
            "provider": provider,
            "subcommand": "inspect",
        },
        "result": {
            "status": "inspected",
            "manifest_keys": sorted(str(key) for key in manifest.keys()),
            "manifest_sha256": _canonical_sha256(manifest),
        },
        "checks": checks,
    }


def _bundle_verify(bundle_cid: str, entry: dict[str, Any], bundle_state_path: Path) -> dict[str, Any]:
    provider = str(entry.get("provider", "local"))
    if provider == "blocked":
        raise BundleCommandError("bundle_provider_blocked", f"bundle_provider_blocked:{bundle_cid}")

    manifest = entry.get("manifest")
    if not isinstance(manifest, dict):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_manifest_missing:{bundle_cid}")

    integrity: dict[str, Any] = {}
    raw_integrity = entry.get("integrity")
    if isinstance(raw_integrity, dict):
        integrity = raw_integrity
    expected_digest = None
    if isinstance(entry.get("manifest_sha256"), str):
        expected_digest = str(entry["manifest_sha256"])
    elif isinstance(integrity.get("manifest_sha256"), str):
        expected_digest = str(integrity["manifest_sha256"])

    observed_digest = _canonical_sha256(manifest)
    digest_matches = expected_digest is None or expected_digest == observed_digest
    checks = [
        _check("subject_exists", True),
        _check("manifest_object_present", True),
        _check("integrity_digest_available", expected_digest is not None),
        _check("integrity_digest_matches", digest_matches),
    ]
    if not digest_matches:
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_digest_mismatch:{bundle_cid}")

    return {
        "subject": {
            "bundle_cid": bundle_cid,
            "bundle_state_path": str(bundle_state_path),
            "provider": provider,
            "subcommand": "verify",
        },
        "result": {
            "status": "verified",
            "digest_source": "provided" if expected_digest is not None else "computed",
            "manifest_sha256": observed_digest,
        },
        "checks": checks,
    }


def _bundle_validate_local(
    bundle_cid: str,
    entry: dict[str, Any],
    graph_state_path: Path,
    bundle_state_path: Path,
) -> dict[str, Any]:
    provider = str(entry.get("provider", "local"))
    if provider == "blocked":
        raise BundleCommandError("bundle_provider_blocked", f"bundle_provider_blocked:{bundle_cid}")

    graph_state = _load_graph_state_for_bundle(graph_state_path)
    nodes = _coerce_list(
        graph_state.get("nodes"),
        BundleCommandError,
        "bundle_backend_unavailable",
        "graph_nodes_not_list",
    )

    graph_refs = entry.get("graph_refs")
    if graph_refs is None:
        graph_refs = {}
    if not isinstance(graph_refs, dict):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_graph_refs_invalid:{bundle_cid}")

    referenced_node_ids = graph_refs.get("node_ids", [])
    referenced_claim_ids = graph_refs.get("claim_ids", [])
    if not isinstance(referenced_node_ids, list) or not isinstance(referenced_claim_ids, list):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_graph_refs_invalid:{bundle_cid}")

    node_id_set = {
        str(item.get("node_id", item.get("id")))
        for item in nodes
        if item.get("node_id", item.get("id")) is not None
    }
    claim_id_set = {str(item.get("claim_id")) for item in nodes if item.get("claim_id") is not None}

    requested_nodes = [str(token) for token in referenced_node_ids]
    requested_claims = [str(token) for token in referenced_claim_ids]
    missing_nodes = sorted(token for token in requested_nodes if token not in node_id_set)
    missing_claims = sorted(token for token in requested_claims if token not in claim_id_set)
    nodes_ok = not missing_nodes
    claims_ok = not missing_claims

    checks = [
        _check("subject_exists", True),
        _check("graph_state_loaded", True, {"graph_state_path": str(graph_state_path)}),
        _check("referenced_nodes_present", nodes_ok, {"missing_nodes": missing_nodes}),
        _check("referenced_claims_present", claims_ok, {"missing_claims": missing_claims}),
    ]
    if not nodes_ok or not claims_ok:
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_graph_refs_missing:{bundle_cid}")

    return {
        "subject": {
            "bundle_cid": bundle_cid,
            "bundle_state_path": str(bundle_state_path),
            "graph_state_path": str(graph_state_path),
            "provider": provider,
            "subcommand": "validate-local",
        },
        "result": {
            "status": "validated_local",
            "validated_node_refs": len(requested_nodes),
            "validated_claim_refs": len(requested_claims),
        },
        "checks": checks,
    }


def _run_bundle_subcommand(args: argparse.Namespace, _graph_state_path: Path) -> tuple[str, dict[str, Any]]:
    bundle_state_path = _default_bundle_state_path()
    subcommand = getattr(args, "bundle_subcommand", None)
    bundle_cid = str(getattr(args, "bundle_cid", ""))
    if not subcommand or not bundle_cid:
        raise BundleCommandError("bundle_invalid_input", "bundle_subcommand_missing")

    try:
        state = _load_bundle_state_for_bundle(bundle_state_path)
        entry = _bundle_entry(state, bundle_cid)

        if subcommand == "inspect":
            return _bundle_command_token(args), _bundle_inspect(bundle_cid, entry, bundle_state_path)
        if subcommand == "verify":
            return _bundle_command_token(args), _bundle_verify(bundle_cid, entry, bundle_state_path)
        if subcommand == "validate-local":
            graph_state_path = Path(str(args.bundle_graph_state))
            return _bundle_command_token(args), _bundle_validate_local(
                bundle_cid,
                entry,
                graph_state_path,
                bundle_state_path,
            )
        raise BundleCommandError("bundle_invalid_input", "bundle_subcommand_missing")
    except BundleCommandError:
        raise
    except (OSError, PermissionError) as exc:
        raise BundleCommandError("bundle_io_error", type(exc).__name__) from exc
    except json.JSONDecodeError as exc:
        raise BundleCommandError("bundle_json_invalid", f"byte_offset:{exc.pos}") from exc
    except Exception as exc:  # pragma: no cover - defensive mapping to contract token
        raise BundleCommandError("bundle_internal_error", type(exc).__name__) from exc


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

            p_truth_node = query_subparsers.add_parser(
                "truth-node",
                help="Query a persisted CDL-075 truth primitive node by CIDv1",
            )
            p_truth_node.add_argument(
                "--node-id", required=True, help="CIDv1 node identifier"
            )

            p_truth_edges = query_subparsers.add_parser(
                "truth-edges",
                help="List CDL-075 edges whose source or target matches the given identifier",
            )
            p_truth_edges.add_argument(
                "--node-id", required=True, help="CIDv1 node identifier or agent_id"
            )
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

        if command == "bundle":
            bundle_parser = subparsers.add_parser("bundle", help="Prototype `bundle` command")
            bundle_subparsers = bundle_parser.add_subparsers(dest="bundle_subcommand", required=True)

            p_bundle_inspect = bundle_subparsers.add_parser(
                "inspect",
                help="Inspect bundle metadata from local bundle state",
            )
            p_bundle_inspect.add_argument("--bundle-cid", required=True, help="Bundle CID")

            p_bundle_verify = bundle_subparsers.add_parser(
                "verify",
                help="Verify bundle manifest integrity from local bundle state",
            )
            p_bundle_verify.add_argument("--bundle-cid", required=True, help="Bundle CID")

            p_bundle_validate_local = bundle_subparsers.add_parser(
                "validate-local",
                help="Validate bundle graph references against supplied graph state path",
            )
            p_bundle_validate_local.add_argument("--bundle-cid", required=True, help="Bundle CID")
            p_bundle_validate_local.add_argument(
                "--graph-state",
                dest="bundle_graph_state",
                required=True,
                help="Path used only for validate-local graph-state checks",
            )
            continue

        if command == "agent":
            agent_parser = subparsers.add_parser("agent", help="D2e agent identity commands")
            agent_subparsers = agent_parser.add_subparsers(dest="agent_subcommand", required=True)

            p_derive = agent_subparsers.add_parser("derive", help="Derive agent_id from root key hex")
            p_derive.add_argument(
                "--root-key-hex",
                required=True,
                help="Hex-encoded canonical root key bytes",
            )

            p_inspect = agent_subparsers.add_parser("inspect", help="Inspect serialized agent record JSON")
            p_inspect.add_argument(
                "--record-json",
                required=True,
                help="Path to agent record JSON file",
            )
            continue

        if command == "node":
            node_parser = subparsers.add_parser("node", help="D2e node lifecycle commands")
            node_subparsers = node_parser.add_subparsers(dest="node_subcommand", required=True)

            node_subparsers.add_parser("constants", help="Show ratified timed-out lifecycle constants")

            p_node_inspect = node_subparsers.add_parser("timed-out-inspect", help="Inspect timed-out lifecycle status from a record")
            p_node_inspect.add_argument(
                "--record-json", required=True, help="Path to node or claim record JSON file"
            )
            p_node_inspect.add_argument(
                "--current-epoch", type=int, required=True, help="Current issuance epoch"
            )

            p_node_d2d = node_subparsers.add_parser("timed-out-d2d", help="Build D2d dissemination envelope for a timed-out claim")
            p_node_d2d.add_argument(
                "--record-json", required=True, help="Path to node or claim record JSON file"
            )
            p_node_d2d.add_argument(
                "--current-epoch", type=int, required=True, help="Current issuance epoch"
            )
            p_node_d2d.add_argument(
                "--channel-id", required=True, help="Opaque D2d channel identifier"
            )
            p_node_d2d.add_argument(
                "--sender-peer-id", required=True, help="D2d sender peer identifier"
            )
            continue

        if command == "sidecar":
            sidecar_parser = subparsers.add_parser(
                "sidecar",
                help="Sidecar discovery and recipe commands",
            )
            sidecar_subparsers = sidecar_parser.add_subparsers(
                dest="sidecar_subcommand",
                required=True,
            )
            sidecar_subparsers.add_parser("list", help="List packaged sidecars")
            p_sidecar_inspect = sidecar_subparsers.add_parser(
                "inspect",
                help="Inspect one packaged sidecar",
            )
            p_sidecar_inspect.add_argument("sidecar_id")

            recipe_parser = sidecar_subparsers.add_parser(
                "recipe",
                help="Sidecar recipe commands",
            )
            recipe_subparsers = recipe_parser.add_subparsers(
                dest="sidecar_recipe_subcommand",
                required=True,
            )
            recipe_subparsers.add_parser("list", help="List sidecar recipes")
            p_recipe_inspect = recipe_subparsers.add_parser(
                "inspect",
                help="Inspect one sidecar recipe",
            )
            p_recipe_inspect.add_argument("recipe_id")
            p_recipe_apply = recipe_subparsers.add_parser(
                "apply",
                help="Apply a local sidecar recipe",
            )
            p_recipe_apply.add_argument("recipe_id")
            p_recipe_apply.add_argument("--home", dest="ccss_home", default="")
            p_recipe_apply.add_argument("--id", default="local-user")
            p_recipe_apply.add_argument("--name", default="Local ILC User")
            p_recipe_apply.add_argument("--peer-endpoint", default="")
            p_recipe_apply.add_argument("--overwrite-identity", action="store_true")
            continue

        if command == "ccss":
            ccss_parser = subparsers.add_parser(
                "ccss",
                help="Confidential Coordination Sidecar Suite message commands",
            )
            ccss_subparsers = ccss_parser.add_subparsers(dest="ccss_subcommand", required=True)

            p_ccss_init = ccss_subparsers.add_parser("init", help="Create local CCSS identity")
            p_ccss_init.add_argument("--home", dest="ccss_home", default="")
            p_ccss_init.add_argument("--id", default="local-user")
            p_ccss_init.add_argument("--name", default="Local ILC User")
            p_ccss_init.add_argument("--peer-endpoint", default="")
            p_ccss_init.add_argument("--onion", default="")
            p_ccss_init.add_argument("--overwrite", action="store_true")

            p_ccss_apply = ccss_subparsers.add_parser(
                "apply-recipe",
                help="Apply the confidential-contact recipe",
            )
            p_ccss_apply.add_argument("--home", dest="ccss_home", default="")
            p_ccss_apply.add_argument("--id", default="local-user")
            p_ccss_apply.add_argument("--name", default="Local ILC User")
            p_ccss_apply.add_argument("--peer-endpoint", default="")
            p_ccss_apply.add_argument("--overwrite-identity", action="store_true")

            p_ccss_contacts = ccss_subparsers.add_parser("contacts", help="List CCSS contacts")
            p_ccss_contacts.add_argument("--home", dest="ccss_home", default="")

            p_ccss_import = ccss_subparsers.add_parser(
                "import-genesis",
                help="Import Genesis contact placeholder or published values",
            )
            p_ccss_import.add_argument("--home", dest="ccss_home", default="")
            p_ccss_import.add_argument("--overwrite", action="store_true")

            p_ccss_add = ccss_subparsers.add_parser("add-contact", help="Add a CCSS contact")
            p_ccss_add.add_argument("--home", dest="ccss_home", default="")
            p_ccss_add.add_argument("--id", required=True)
            p_ccss_add.add_argument("--name", required=True)
            p_ccss_add.add_argument("--pubkey", required=True)
            p_ccss_add.add_argument("--description", default="")
            p_ccss_add.add_argument("--peer-endpoint", default="")
            p_ccss_add.add_argument("--onion", default="")
            p_ccss_add.add_argument("--agent-id", default="")
            p_ccss_add.add_argument("--overwrite", action="store_true")

            p_ccss_send = ccss_subparsers.add_parser("send", help="Send a sealed CCSS message")
            p_ccss_send.add_argument("--home", dest="ccss_home", default="")
            p_ccss_send.add_argument("--allow-reply", action="store_true",
                help="Include your pubkey+endpoint in the encrypted payload so the "
                     "recipient can respond. Once received and decrypted, they have "
                     "your key permanently.")
            p_ccss_send.add_argument("contact_id")
            p_ccss_send.add_argument("message")

            p_ccss_inbox = ccss_subparsers.add_parser("inbox", help="List local CCSS inbox")
            p_ccss_inbox.add_argument("--home", dest="ccss_home", default="")
            p_ccss_inbox.add_argument("--count", action="store_true",
                help="Print only the number of envelopes (machine-readable)")

            p_ccss_status = ccss_subparsers.add_parser(
                "status", help="Print pending inbox count; exits 0 if empty, 1 if messages waiting")
            p_ccss_status.add_argument("--home", dest="ccss_home", default="")

            p_ccss_read = ccss_subparsers.add_parser("read", help="Read/decrypt a CCSS envelope")
            p_ccss_read.add_argument("--home", dest="ccss_home", default="")
            read_group = p_ccss_read.add_mutually_exclusive_group(required=True)
            read_group.add_argument("--latest", action="store_true")
            read_group.add_argument("--envelope", default="")
            p_ccss_read.add_argument("--redact", action="store_true")

            p_ccss_serve = ccss_subparsers.add_parser(
                "serve",
                help="Run a local direct CCSS peer receiver",
            )
            p_ccss_serve.add_argument("--home", dest="ccss_home", default="")
            p_ccss_serve.add_argument("--host", default="127.0.0.1")
            p_ccss_serve.add_argument("--port", type=int, default=9001)
            continue

        if command == "submit":
            submit_parser = subparsers.add_parser(
                "submit",
                help="Validate a CDL-073 truth primitive submission and return graph-output contract",
            )
            submit_parser.add_argument(
                "--primitive",
                required=True,
                help="Truth primitive name (assert.truth, validate.claim, etc.)",
            )
            submit_group = submit_parser.add_mutually_exclusive_group(required=True)
            submit_group.add_argument(
                "--payload-json",
                dest="payload_json",
                help="Payload as a JSON string",
            )
            submit_group.add_argument(
                "--payload-file",
                dest="payload_file",
                help="Path to a JSON file containing the payload",
            )
            submit_parser.add_argument(
                "--agent-id",
                dest="agent_id",
                required=True,
                help="Submitting agent's canonical agent_id",
            )
            submit_parser.add_argument(
                "--epoch",
                type=int,
                required=True,
                help="Current epoch at submission time (non-negative integer)",
            )
            submit_parser.add_argument(
                "--sig",
                default="UNSIGNED",
                help="COSE Sign1 signature (hex or placeholder). Default: UNSIGNED",
            )
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


def _write_json_payload(payload: dict[str, Any], *, stderr: bool = False) -> None:
    print(json.dumps(payload, sort_keys=True), file=sys.stderr if stderr else sys.stdout)


def _simulate_network_error_result(command: str) -> tuple[int, dict[str, Any]]:
    return 3, _error_payload(
        command=command,
        code=3,
        message="simulated network transport failure",
        details={"phase": "264"},
    )


def _run_top_level_command(
    command: str,
    args: argparse.Namespace,
    graph_state_path: Path,
) -> dict[str, Any]:
    if command not in {"query", "verify", "bundle", "agent", "node", "sidecar", "ccss"}:
        _ensure_local_graph_state(graph_state_path, command)

    if command == "version":
        return _success_payload(command, _version_data())
    if command == "query":
        query_command, data = _run_query_subcommand(args, graph_state_path)
        return _query_success_payload(query_command, data)
    if command == "verify":
        verify_command, data = _run_verify_subcommand(args, graph_state_path)
        return _verify_success_payload(verify_command, data)
    if command == "bundle":
        bundle_command, data = _run_bundle_subcommand(args, graph_state_path)
        return _bundle_success_payload(bundle_command, data)
    if command == "identity":
        data = _run_identity_subcommand(args, graph_state_path)
        return _success_payload(command, data)
    if command == "agent":
        from ilc_core.cli.d2e_agent_cli import run_agent_command

        data = run_agent_command(args)
        return _success_payload(command, data)
    if command == "node":
        from ilc_core.cli.d2e_lifecycle_cli import run_node_command

        data = run_node_command(args)
        return _success_payload(command, data)
    if command == "sidecar":
        from ilc_core.cli.sidecar_cli import run_sidecar_command

        data = run_sidecar_command(args)
        return _success_payload(command, data)
    if command == "ccss":
        from ilc_core.cli.ccss_cli import run_ccss_command

        data = run_ccss_command(args)
        return _success_payload(command, data)
    if command == "submit":
        from ilc_core.cli.d2e_submit_cli import handle_submit, SubmitCommandError

        try:
            data = handle_submit(args)
        except SubmitCommandError as exc:
            raise ValueError(exc.message) from exc
        return _success_payload(command, data)

    data = _prototype_data_for_command(command)
    return _success_payload(command, data)


def _query_error_result(
    args: argparse.Namespace,
    exc: QueryCommandError,
) -> tuple[int, dict[str, Any]]:
    return 1, _query_error_payload(
        command_token=_query_command_token(args),
        code=exc.code,
        message=exc.message,
    )


def _verify_error_result(
    args: argparse.Namespace,
    exc: VerifyCommandError,
) -> tuple[int, dict[str, Any]]:
    return 1, _verify_error_payload(
        command_token=_verify_command_token(args),
        code=exc.code,
        message=exc.message,
    )


def _bundle_error_result(
    args: argparse.Namespace,
    exc: BundleCommandError,
) -> tuple[int, dict[str, Any]]:
    return 1, _bundle_error_payload(
        command_token=_bundle_command_token(args),
        code=exc.code,
        message=exc.message,
    )


def _value_error_result(command: str, exc: ValueError) -> tuple[int, dict[str, Any]]:
    return 1, _error_payload(
        command=command,
        code=1,
        message=str(exc),
        details={"phase": "264"},
    )


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    command = str(args.command)

    if args.simulate_network_error:
        code, payload = _simulate_network_error_result(command)
        _write_json_payload(payload, stderr=True)
        return code

    graph_state_path = Path(args.graph_state)

    try:
        payload = _run_top_level_command(command, args, graph_state_path)
        data = payload.get("data") or {}
        # Machine-readable raw output — print bare value, no JSON wrapper.
        # Used by: ilc ccss inbox --count
        raw_val = data.get("_raw")
        if raw_val is not None:
            print(raw_val)
            return 0
        _write_json_payload(payload)
        # Surface any warnings as human-readable stderr lines so they are
        # visible to interactive users without breaking JSON stdout for scripts.
        for w in data.get("warnings", []):
            print(f"[ilc warning] {w}", file=sys.stderr)
        # Safety warning for decrypted messages flagged by the content inspector.
        # Printed to stderr so JSON stdout stays machine-readable.
        if data.get("subcommand") == "read" and not data.get("safe", True):
            flags_str = json.dumps(sorted(data.get("flags", [])))
            print(
                f"[ccss] SAFETY WARNING: message flagged safe=false flags={flags_str}",
                file=sys.stderr,
            )
        # ilc ccss status exits 1 when messages are waiting (shell-condition friendly).
        if data.get("subcommand") == "status" and data.get("has_messages"):
            return 1
        return 0
    except QueryCommandError as exc:
        code, payload = _query_error_result(args, exc)
    except VerifyCommandError as exc:
        code, payload = _verify_error_result(args, exc)
    except BundleCommandError as exc:
        code, payload = _bundle_error_result(args, exc)
    except ValueError as exc:
        code, payload = _value_error_result(command, exc)

    _write_json_payload(payload, stderr=True)
    return code


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
