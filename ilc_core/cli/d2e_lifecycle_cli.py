# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase 421 D2e lifecycle CLI helpers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ilc_core.network.d2d.gossip import D2D_GOSSIP_DEPENDENCY as GOSSIP_D2D_GOSSIP_DEPENDENCY
from ilc_core.network.d2d.gossip import build_transport_envelope
from ilc_core.node.timed_out_lifecycle_runtime_411 import (
    CDL_046_DEPENDENCY as RUNTIME_CDL_046_DEPENDENCY,
    ORPHAN_TIMEOUT_EPOCHS,
    RECOVERY_POLICY,
    TIMED_OUT_LIFECYCLE_RUNTIME_VERSION,
    get_recovery_policy,
    is_claim_timed_out,
)

D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"
CDL_046_DEPENDENCY = RUNTIME_CDL_046_DEPENDENCY
D2D_GOSSIP_DEPENDENCY = GOSSIP_D2D_GOSSIP_DEPENDENCY

if CDL_046_DEPENDENCY != "cdl_046_ratified_409.v0.1":
    raise ValueError("node_cli_dependency_mismatch")
if D2D_GOSSIP_DEPENDENCY != "d2d_gossip_382.v0.1":
    raise ValueError("node_cli_d2d_dependency_mismatch")


def _load_record(record_json: str) -> dict[str, Any]:
    path = Path(record_json)
    if not path.exists():
        raise ValueError("node_inspect_record_not_found")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("node_inspect_record_invalid_json") from exc
    if not isinstance(record, dict):
        raise ValueError("node_inspect_record_not_object")
    return record


def _claim_id(record: dict[str, Any]) -> str:
    claim_id = record.get("claim_id")
    if not isinstance(claim_id, str) or not claim_id.strip():
        raise ValueError("node_inspect_missing_claim_id")
    return claim_id


def _orphaned_since_epoch(record: dict[str, Any]) -> int:
    if "orphaned_since_epoch" not in record:
        raise ValueError("node_inspect_missing_orphaned_since_epoch")
    return record["orphaned_since_epoch"]


def handle_node_constants() -> dict[str, Any]:
    """Return the ratified timed-out lifecycle constants."""

    return {
        "subcommand": "constants",
        "orphan_timeout_epochs": ORPHAN_TIMEOUT_EPOCHS,
        "recovery_policy": RECOVERY_POLICY,
        "timed_out_runtime_version": TIMED_OUT_LIFECYCLE_RUNTIME_VERSION,
        "version": D2E_LIFECYCLE_CLI_VERSION,
    }


def handle_node_timed_out_inspect(record_json: str, current_epoch: int) -> dict[str, Any]:
    """Inspect timed-out lifecycle status from a serialized record."""

    record = _load_record(record_json)
    claim_id = _claim_id(record)
    orphaned_since_epoch = _orphaned_since_epoch(record)
    timed_out = is_claim_timed_out(current_epoch, orphaned_since_epoch)
    return {
        "subcommand": "timed-out-inspect",
        "claim_id": claim_id,
        "current_epoch": current_epoch,
        "orphaned_since_epoch": orphaned_since_epoch,
        "timed_out": timed_out,
        "orphan_timeout_epochs": ORPHAN_TIMEOUT_EPOCHS,
        "recovery_policy": get_recovery_policy(),
        "lifecycle_path": "timed_out_recovery" if timed_out else "pending_orphan_grace",
        "version": D2E_LIFECYCLE_CLI_VERSION,
    }


def handle_node_timed_out_d2d(
    record_json: str,
    current_epoch: int,
    channel_id: str,
    sender_peer_id: str,
) -> dict[str, Any]:
    """Build the D2d dissemination envelope for a timed-out claim."""

    record = _load_record(record_json)
    claim_id = _claim_id(record)
    orphaned_since_epoch = _orphaned_since_epoch(record)
    payload_cid = record.get("payload_cid")
    if not isinstance(payload_cid, str) or not payload_cid.strip():
        raise ValueError("node_d2d_payload_cid_missing")
    timed_out = is_claim_timed_out(current_epoch, orphaned_since_epoch)
    if not timed_out:
        raise ValueError("node_d2d_not_timed_out")
    envelope = build_transport_envelope(
        message_id=f"timed-out:{claim_id}:{current_epoch}",
        payload_cid=payload_cid,
        channel_id=channel_id,
        sender_peer_id=sender_peer_id,
        transport_headers={"event": "claim_timed_out", "recovery_policy": get_recovery_policy()},
    )
    return {
        "subcommand": "timed-out-d2d",
        "claim_id": claim_id,
        "timed_out": True,
        "recovery_policy": get_recovery_policy(),
        "envelope": envelope,
        "version": D2E_LIFECYCLE_CLI_VERSION,
    }


def run_node_command(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch node subcommand from argparse Namespace. Called by main.py."""

    subcommand = getattr(args, "node_subcommand", None)
    if subcommand == "constants":
        return handle_node_constants()
    if subcommand == "timed-out-inspect":
        return handle_node_timed_out_inspect(args.record_json, args.current_epoch)
    if subcommand == "timed-out-d2d":
        return handle_node_timed_out_d2d(
            args.record_json,
            args.current_epoch,
            args.channel_id,
            args.sender_peer_id,
        )
    raise ValueError("node_subcommand_missing")
