#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SENSITIVE_SCAN_ROOTS = (
    "ilc_core/protocol",
    "ilc_core/ledger",
    "ilc_core/consensus",
    "ilc_core/mcp",
    "ilc_core/storage",
)

EXPLICIT_SCAN_FILES = {
    "ilc_core/network/peer.py",
    "ilc_core/network/d2d/http_gossip_transport_runtime.py",
}

PRNG_FORBIDDEN_FILES = {
    "ilc_core/network/d2d/spectral_routing_runtime.py",
}

# Repo-local rule from AGENTS.md Section 7 still allows diagnostic/operator
# timestamps. Keep that allowance explicit rather than pretending these are
# protocol-time violations.
WALL_CLOCK_ALLOWLIST = {
    "ilc_core/protocol/event_log.py",
    "ilc_core/protocol/ndjson_bundle.py",
    "ilc_core/ledger/canon_bundle_audit_artifact.py",
    "ilc_core/ledger/canon_bundle_pipeline_report.py",
    "ilc_core/ledger/canon_bundle_replay_report.py",
    "ilc_core/ledger/canon_export.py",
    "ilc_core/ledger/canon_export_bundle_report.py",
    "ilc_core/ledger/canon_export_format.py",
}

STRICT_MACHINE_JSON_FILES = {
    "ilc_core/protocol/public_init_admission_runtime.py",
    "ilc_core/protocol/public_receipt_runtime.py",
    "ilc_core/protocol/public_wallet_runtime.py",
    "ilc_core/ledger/ecu_ilc_lifecycle_runtime.py",
    "ilc_core/mcp/service.py",
    "ilc_core/storage/lmdb_public_runtime.py",
}

NETWORK_TIMEOUT_FILES = {
    "ilc_core/network/peer.py",
    "ilc_core/network/d2d/http_gossip_transport_runtime.py",
    "ilc_core/ledger/canon_bundle_key_registry_fetch.py",
}


def _iter_python_files() -> list[Path]:
    files: set[Path] = set()
    for rel_root in SENSITIVE_SCAN_ROOTS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            continue
        files.update(root.rglob("*.py"))
    for rel_file in EXPLICIT_SCAN_FILES | PRNG_FORBIDDEN_FILES:
        path = REPO_ROOT / rel_file
        if path.exists():
            files.add(path)
    return sorted(files)


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _is_name(node: ast.AST | None, value: str) -> bool:
    return isinstance(node, ast.Name) and node.id == value


def _is_attr(node: ast.AST | None, attr: str) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == attr


def _bool_keyword(call: ast.Call, name: str) -> bool | None:
    for kw in call.keywords:
        if kw.arg != name:
            continue
        if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, bool):
            return kw.value.value
        return None
    return None


def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts: list[str] = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return "<unknown>"


def _is_datetime_now(call: ast.Call) -> bool:
    func = call.func
    if not isinstance(func, ast.Attribute) or func.attr != "now":
        return False
    return _is_name(func.value, "datetime") or (
        isinstance(func.value, ast.Attribute)
        and func.value.attr == "datetime"
        and _is_name(func.value.value, "datetime")
    )


def _is_time_time(call: ast.Call) -> bool:
    func = call.func
    return isinstance(func, ast.Attribute) and func.attr == "time" and _is_name(func.value, "time")


def _is_date_today(call: ast.Call) -> bool:
    func = call.func
    if not isinstance(func, ast.Attribute) or func.attr != "today":
        return False
    return _is_name(func.value, "date") or (
        isinstance(func.value, ast.Attribute)
        and func.value.attr == "date"
        and _is_name(func.value.value, "datetime")
    )


def _is_random_random(
    call: ast.Call,
    *,
    random_module_aliases: set[str],
    random_constructor_names: set[str],
) -> bool:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id in random_constructor_names
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "Random"
        and isinstance(func.value, ast.Name)
        and func.value.id in random_module_aliases
    )


def _is_json_dumps(call: ast.Call) -> bool:
    func = call.func
    return isinstance(func, ast.Attribute) and func.attr == "dumps" and _is_name(func.value, "json")


def _is_requests_call(call: ast.Call) -> bool:
    func = call.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr in {"get", "post", "put", "delete", "patch", "head", "request"}
        and _is_name(func.value, "requests")
    )


def _is_urllib_urlopen(call: ast.Call) -> bool:
    func = call.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "urlopen"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "request"
        and _is_name(func.value.value, "urllib")
    )


def _is_socket_create_connection(call: ast.Call) -> bool:
    func = call.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "create_connection"
        and _is_name(func.value, "socket")
    )


def find_violations() -> list[str]:
    violations: list[str] = []

    for path in _iter_python_files():
        rel = _rel(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        in_sensitive_roots = any(rel.startswith(f"{root}/") for root in SENSITIVE_SCAN_ROOTS)
        prng_forbidden = in_sensitive_roots or rel in PRNG_FORBIDDEN_FILES
        random_module_aliases: set[str] = set()
        random_constructor_names: set[str] = set()

        if rel in NETWORK_TIMEOUT_FILES:
            network_call_seen = False
        else:
            network_call_seen = False

        for node in ast.walk(tree):
            if in_sensitive_roots and isinstance(node, ast.Assert):
                violations.append(f"{rel}:{node.lineno}:assert_forbidden_in_sensitive_runtime")

            if prng_forbidden and isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "random":
                        random_module_aliases.add(alias.asname or alias.name)
                        violations.append(f"{rel}:{node.lineno}:predictable_prng_import_forbidden")

            if prng_forbidden and isinstance(node, ast.ImportFrom) and node.module == "random":
                for alias in node.names:
                    random_constructor_names.add(alias.asname or alias.name)
                violations.append(f"{rel}:{node.lineno}:predictable_prng_import_forbidden")

            if not isinstance(node, ast.Call):
                continue

            if in_sensitive_roots and rel not in WALL_CLOCK_ALLOWLIST:
                if _is_datetime_now(node):
                    violations.append(f"{rel}:{node.lineno}:datetime_now_forbidden")
                if _is_time_time(node):
                    violations.append(f"{rel}:{node.lineno}:time_time_forbidden")
                if _is_date_today(node):
                    violations.append(f"{rel}:{node.lineno}:date_today_forbidden")

            if prng_forbidden and _is_random_random(
                node,
                random_module_aliases=random_module_aliases,
                random_constructor_names=random_constructor_names,
            ):
                violations.append(f"{rel}:{node.lineno}:predictable_prng_forbidden")

            if rel in STRICT_MACHINE_JSON_FILES and _is_json_dumps(node):
                sort_keys = _bool_keyword(node, "sort_keys")
                allow_nan = _bool_keyword(node, "allow_nan")
                if sort_keys is not True:
                    violations.append(f"{rel}:{node.lineno}:json_dumps_missing_sort_keys_true")
                if allow_nan is not False:
                    violations.append(f"{rel}:{node.lineno}:json_dumps_missing_allow_nan_false")

            if rel in NETWORK_TIMEOUT_FILES:
                if _is_requests_call(node) or _is_urllib_urlopen(node) or _is_socket_create_connection(node):
                    network_call_seen = True
                    if not any(kw.arg == "timeout" for kw in node.keywords):
                        violations.append(f"{rel}:{node.lineno}:network_call_missing_timeout")

        if rel in NETWORK_TIMEOUT_FILES and not network_call_seen:
            violations.append(f"{rel}:network_timeout_check_target_has_no_detected_network_call")

    return violations


def main() -> int:
    violations = find_violations()
    if violations:
        print("FAIL: sensitive runtime coding taboos")
        for item in violations:
            print(f"- {item}")
        return 1

    print("PASS: sensitive runtime coding taboos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
