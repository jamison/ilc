"""Phase 874/882 — CDL-074/075 truth primitive submit CLI helper.

Wires validate_truth_primitive_submission into the ILC CLI `submit` command.
Validates a CDL-073 wire-format submission envelope, optionally persists to
an LMDB graph store (CDL-075), and returns the graph-output contract.

Graph persistence is activated when ILC_TRUTH_GRAPH_STORE_PATH is set in the
environment.  Without that env var, behaviour is identical to Phase 874.

Command surface:
    ilc submit --primitive <name> --payload-json <json-string>
               --agent-id <hex> --epoch <n>
    ilc submit --primitive <name> --payload-file <path>
               --agent-id <hex> --epoch <n>
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from ilc_core.epistemic.truth_primitive_submission_runtime import (
    CDL_074_DEPENDENCY as RUNTIME_CDL_074_DEPENDENCY,
    AGENT_ISSUABLE_PRIMITIVES,
    validate_truth_primitive_submission,
)
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError

D2E_SUBMIT_CLI_VERSION = "d2e_submit_cli_874.v0.1"
CDL_074_DEPENDENCY = RUNTIME_CDL_074_DEPENDENCY
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"

if CDL_074_DEPENDENCY != "cdl_074_truth_primitive_runtime_ratified.v0.1":
    raise ValueError("submit_cli_dependency_mismatch")


class SubmitCommandError(Exception):
    """Typed error carrying submit contract error token and message."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _load_payload(args: argparse.Namespace) -> dict[str, Any]:
    """Load payload from --payload-json string or --payload-file path."""
    json_str = getattr(args, "payload_json", None)
    file_path = getattr(args, "payload_file", None)

    if json_str and file_path:
        raise SubmitCommandError(
            "submit_payload_ambiguous",
            "provide --payload-json or --payload-file, not both",
        )
    if not json_str and not file_path:
        raise SubmitCommandError(
            "submit_payload_missing",
            "one of --payload-json or --payload-file is required",
        )

    raw = json_str
    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise SubmitCommandError(
                "submit_payload_file_not_found",
                f"payload file not found: {file_path}",
            )
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SubmitCommandError(
                "submit_payload_file_read_error",
                f"could not read payload file: {exc}",
            ) from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SubmitCommandError(
            "submit_payload_invalid_json",
            f"payload is not valid JSON: {exc}",
        ) from exc

    if not isinstance(payload, dict):
        raise SubmitCommandError(
            "submit_payload_not_object",
            "payload must be a JSON object",
        )
    return payload


def handle_submit(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the submit command.

    Builds a CDL-073 submission envelope from CLI arguments, validates it via
    validate_truth_primitive_submission, and returns the graph-output contract.
    """
    primitive = getattr(args, "primitive", None)
    if not primitive:
        raise SubmitCommandError("submit_primitive_missing", "--primitive is required")

    agent_id = getattr(args, "agent_id", None)
    if not agent_id:
        raise SubmitCommandError("submit_agent_id_missing", "--agent-id is required")

    epoch = getattr(args, "epoch", None)
    if epoch is None or not isinstance(epoch, int) or epoch < 0:
        raise SubmitCommandError(
            "submit_epoch_invalid",
            "--epoch must be a non-negative integer",
        )

    payload = _load_payload(args)

    envelope: dict[str, Any] = {
        "v": 1,
        "primitive": primitive,
        "agent_id": agent_id,
        "epoch": epoch,
        "payload": payload,
        "sig": args.sig if hasattr(args, "sig") and args.sig else "UNSIGNED",
    }

    try:
        result = validate_truth_primitive_submission(envelope)
    except EpistemicSubmissionError as exc:
        raise SubmitCommandError(exc.token, str(exc)) from exc

    edges_out = [
        {"edge_type": e.edge_type, "source": e.source, "target": e.target}
        for e in result.edges
    ]

    # CDL-075: persist to LMDB graph store when ILC_TRUTH_GRAPH_STORE_PATH is set.
    node_id: str | None = None
    graph_persistence: str = "deferred — CDL-075 graph store path not configured"
    store_path = os.environ.get("ILC_TRUTH_GRAPH_STORE_PATH", "").strip()
    if store_path:
        from ilc_core.epistemic.truth_primitive_graph_store import (
            TruthPrimitiveGraphStore,
            write_truth_primitive_result,
        )
        store = TruthPrimitiveGraphStore(store_path)
        try:
            write_receipt = write_truth_primitive_result(store, envelope, result)
            node_id = write_receipt["node_id"]
            graph_persistence = "persisted"
        finally:
            store.close()

    return {
        "subcommand": "submit",
        "primitive": result.primitive,
        "creates_node": result.creates_node,
        "node_primitive_type": result.node_primitive_type,
        "node_id": node_id,
        "edges": edges_out,
        "graph_persistence": graph_persistence,
        "version": D2E_SUBMIT_CLI_VERSION,
    }
