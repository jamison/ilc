"""Phase 420 D2e agent identity CLI helpers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ilc_core.identity.agent_id_runtime import (
    CDL_042_DEPENDENCY as RUNTIME_CDL_042_DEPENDENCY,
    derive_agent_id,
)

D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"
CDL_042_DEPENDENCY = RUNTIME_CDL_042_DEPENDENCY

if CDL_042_DEPENDENCY != "cdl_042_ratified_407.v0.1":
    raise ValueError("agent_cli_dependency_mismatch")


def handle_agent_derive(root_key_hex: str) -> dict[str, Any]:
    """Execute the derive subcommand given the hex-encoded root key string."""

    try:
        key_bytes = bytes.fromhex(root_key_hex)
    except ValueError as exc:
        raise ValueError("agent_derive_invalid_hex") from exc

    return {
        "subcommand": "derive",
        "agent_id": derive_agent_id(key_bytes),
        "version": D2E_AGENT_CLI_VERSION,
    }


def handle_agent_inspect(record_json: str) -> dict[str, Any]:
    """Execute the inspect subcommand given the record JSON file path string."""

    path = Path(record_json)
    if not path.exists():
        raise ValueError("agent_inspect_record_not_found")

    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("agent_inspect_record_invalid_json") from exc

    if not isinstance(record, dict):
        raise ValueError("agent_inspect_record_not_object")

    return {
        "subcommand": "inspect",
        "record_path": str(path),
        "fields": sorted(record.keys()),
        "record": record,
        "version": D2E_AGENT_CLI_VERSION,
    }


def run_agent_command(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch agent subcommand from argparse Namespace. Called by main.py."""

    subcommand = getattr(args, "agent_subcommand", None)
    if subcommand == "derive":
        return handle_agent_derive(args.root_key_hex)
    if subcommand == "inspect":
        return handle_agent_inspect(args.record_json)
    raise ValueError("agent_subcommand_missing")
