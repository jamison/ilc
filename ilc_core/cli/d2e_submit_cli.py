# SPDX-License-Identifier: AGPL-3.0-only
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
import re
import stat
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.encoding.cidv1 import parse_nodeid_strict
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    CDL_074_DEPENDENCY as RUNTIME_CDL_074_DEPENDENCY,
    AGENT_ISSUABLE_PRIMITIVES,
    validate_truth_primitive_submission,
)
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_sig_verifier import attach_truth_primitive_signature
from ilc_core.value_action.local_signing_provider import LocalEd25519SigningProvider

D2E_SUBMIT_CLI_VERSION = "d2e_submit_cli_874_GAP_GRAPH_SIGN_00.v0.1"
CDL_074_DEPENDENCY = RUNTIME_CDL_074_DEPENDENCY
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"
_MAX_SUBMIT_PAYLOAD_BYTES = 256 * 1024
_GRAPH_SUBMIT_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_MAX_REFUTATION_CRITERION_BYTES = 500
_MAX_SOURCE_REFS = 64
_MAX_SUBMIT_ENDPOINT_RESPONSE_BYTES = 262_144
_SUBMIT_ENDPOINT_READ_CHUNK_BYTES = 64 * 1024

if CDL_074_DEPENDENCY != "cdl_074_truth_primitive_runtime_ratified.v0.1":
    raise ValueError("submit_cli_dependency_mismatch")


@dataclass(frozen=True)
class GraphSubmitAdvisoryEnvelope:
    """Graph-native advisory wrapper for signed CDL-073 submissions."""

    agent_id_hex: str
    epoch: int
    truth_primitive: dict[str, Any]
    sig: str
    sig_pubkey_hex: str
    sig_pubkey_fingerprint: str
    sig_scheme: str


class SubmitCommandError(Exception):
    """Typed error carrying submit contract error token and message."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> None:
        raise SubmitCommandError(
            "submit_endpoint_redirect_forbidden",
            "submit endpoint redirects are forbidden",
        )


def _reject_non_finite_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _require_graph_submit_agent_id(agent_id_hex: str) -> None:
    if not isinstance(agent_id_hex, str):
        raise ValueError("invalid_agent_id_hex")
    if _GRAPH_SUBMIT_AGENT_ID_RE.fullmatch(agent_id_hex) is None:
        raise ValueError("invalid_agent_id_hex")


def _require_graph_submit_epoch(epoch: int) -> None:
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise ValueError("invalid_epoch")


def build_graph_submit_envelope(
    truth_primitive: dict[str, Any],
    agent_id_hex: str,
    epoch: int,
    private_key: ed25519.Ed25519PrivateKey,
) -> GraphSubmitAdvisoryEnvelope:
    """Return a graph-specific advisory envelope signed over CDL-073 fields."""

    _require_graph_submit_agent_id(agent_id_hex)
    _require_graph_submit_epoch(epoch)
    if not isinstance(truth_primitive, dict):
        raise ValueError("invalid_truth_primitive")
    payload = truth_primitive.get("payload")
    primitive = truth_primitive.get("primitive")
    version = truth_primitive.get("v", 1)
    if not isinstance(payload, dict) or not isinstance(primitive, str) or not primitive:
        raise ValueError("invalid_truth_primitive")
    if version != 1:
        raise ValueError("invalid_truth_primitive")

    # GRAPH_SUBMIT type is advisory pending CDL-111 ratification — do not wire to AgentActionEnvelope dispatch until ratified
    envelope_dict: dict[str, Any] = {
        "agent_id": agent_id_hex,
        "epoch": epoch,
        "payload": payload,
        "primitive": primitive,
        "v": 1,
    }
    signed = attach_truth_primitive_signature(envelope_dict, private_key)
    return GraphSubmitAdvisoryEnvelope(
        agent_id_hex=agent_id_hex,
        epoch=epoch,
        truth_primitive=dict(envelope_dict),
        sig=str(signed["sig"]),
        sig_pubkey_hex=str(signed["sig_pubkey_hex"]),
        sig_pubkey_fingerprint=str(signed["sig_pubkey_fingerprint"]),
        sig_scheme=str(signed["sig_scheme"]),
    )


def build_refutation_primitive(
    target_node_id: str,
    refutation_criterion_text: str,
    evidence_node_ids: list[Any],
    agent_id_hex: str,
    epoch: int,
) -> dict[str, Any]:
    """Build a CDL-073 refute.claim submission dict accepted by CDL-074."""

    _require_graph_submit_agent_id(agent_id_hex)
    _require_graph_submit_epoch(epoch)
    if not isinstance(target_node_id, str) or not target_node_id:
        raise ValueError("invalid_refutation_target_empty")
    if not isinstance(refutation_criterion_text, str):
        raise ValueError("invalid_refutation_criterion_type")
    if len(refutation_criterion_text.encode("utf-8")) > _MAX_REFUTATION_CRITERION_BYTES:
        raise ValueError("invalid_refutation_reason_too_long")
    if not isinstance(evidence_node_ids, list):
        raise ValueError("invalid_evidence_node_id")
    for evidence_node_id in evidence_node_ids:
        if not isinstance(evidence_node_id, str) or not evidence_node_id:
            raise ValueError("invalid_evidence_node_id")

    return {
        "agent_id": agent_id_hex,
        "epoch": epoch,
        "payload": {
            "evidence_node_ids": list(evidence_node_ids),
            "refutation_criterion": {
                "claim": refutation_criterion_text,
                "claim_form": "singular",
                "evidence_type": "logical",
                "has_falsifiable_test": True,
                "scope_boundary": f"target_node_id:{target_node_id}",
            },
            "target_node_id": target_node_id,
        },
        "primitive": "refute.claim",
        "v": 1,
    }


def check_graph_mutation_allowed(public_path_guard_value: bool) -> None:
    """Fail closed before graph mutation when the caller's guard remains set."""

    if not isinstance(public_path_guard_value, bool):
        raise TypeError("invalid_guard_value_not_bool")
    if public_path_guard_value is True:
        raise ValueError("graph_mutation_blocked_public_path_not_cleared")


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
            flags = os.O_RDONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = -1
            fd = os.open(path, flags)
            try:
                file_stat = os.fstat(fd)
                if not stat.S_ISREG(file_stat.st_mode):
                    raise SubmitCommandError(
                        "submit_payload_file_not_regular",
                        "payload file must be a regular file",
                    )
                if file_stat.st_size > _MAX_SUBMIT_PAYLOAD_BYTES:
                    raise SubmitCommandError(
                        "submit_payload_too_large",
                        "payload exceeds maximum submit payload size",
                    )
                with os.fdopen(fd, "rb") as handle:
                    fd = -1
                    raw_bytes = handle.read(_MAX_SUBMIT_PAYLOAD_BYTES + 1)
            finally:
                if fd >= 0:
                    os.close(fd)
        except OSError as exc:
            raise SubmitCommandError(
                "submit_payload_file_read_error",
                f"could not read payload file: {exc}",
            ) from exc
        if len(raw_bytes) > _MAX_SUBMIT_PAYLOAD_BYTES:
            raise SubmitCommandError(
                "submit_payload_too_large",
                "payload exceeds maximum submit payload size",
            )
        try:
            raw = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SubmitCommandError(
                "submit_payload_file_read_error",
                f"payload file is not valid UTF-8: {exc}",
            ) from exc

    if not isinstance(raw, str):
        raise SubmitCommandError(
            "submit_payload_invalid_type",
            "payload source must produce text JSON",
        )
    if len(raw.encode("utf-8")) > _MAX_SUBMIT_PAYLOAD_BYTES:
        raise SubmitCommandError(
            "submit_payload_too_large",
            "payload exceeds maximum submit payload size",
        )

    try:
        payload = json.loads(raw, parse_constant=_reject_non_finite_json_constant)
    except json.JSONDecodeError as exc:
        raise SubmitCommandError(
            "submit_payload_invalid_json",
            f"payload is not valid JSON: {exc}",
        ) from exc
    except ValueError as exc:
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


def _apply_source_refs(payload: dict[str, Any], source_refs: list[str] | None) -> dict[str, Any]:
    """Inject strict CIDv1 source refs into payload.content.source_refs."""

    if not source_refs:
        return payload
    if len(source_refs) > _MAX_SOURCE_REFS:
        raise SubmitCommandError(
            "source_refs_count_exceeded",
            f"--source-refs accepts at most {_MAX_SOURCE_REFS} values",
        )

    content = payload.get("content")
    if not isinstance(content, dict):
        raise SubmitCommandError(
            "source_refs_content_object_required",
            "payload.content must be an object when --source-refs is supplied",
        )

    validated: list[str] = []
    for raw_ref in source_refs:
        if not isinstance(raw_ref, str) or raw_ref != raw_ref.strip():
            raise SubmitCommandError(
                "source_refs_cid_invalid",
                "--source-refs values must be strict CIDv1 NodeIDs",
            )
        try:
            parse_nodeid_strict(raw_ref)
        except ValueError as exc:
            raise SubmitCommandError(
                "source_refs_cid_invalid",
                "--source-refs values must be strict CIDv1 NodeIDs",
            ) from exc
        validated.append(raw_ref)

    patched_payload = dict(payload)
    patched_content = dict(content)
    patched_content["source_refs"] = validated
    patched_payload["content"] = patched_content
    return patched_payload


def _sign_submission_envelope(envelope: dict[str, Any], signing_key_uri: str | None) -> dict[str, Any]:
    """Attach optional Ed25519 hotkey signature metadata to a submission envelope."""

    if not signing_key_uri:
        return envelope
    if envelope.get("sig") not in {None, "", "UNSIGNED"}:
        raise SubmitCommandError(
            "submit_signature_ambiguous",
            "provide --sig or --signing-key, not both",
        )
    try:
        private_key = LocalEd25519SigningProvider()._load_private_key(signing_key_uri)
        return attach_truth_primitive_signature(envelope, private_key)
    except SubmitCommandError:
        raise
    except (OSError, ValueError) as exc:
        raise SubmitCommandError("submit_signing_key_invalid", str(exc)) from exc


def _submit_endpoint_from_args(args: argparse.Namespace) -> str:
    endpoint = str(getattr(args, "endpoint", "") or "").strip()
    if not endpoint:
        endpoint = os.environ.get("ILC_TRUTH_SUBMIT_ENDPOINT", "").strip()
    if not endpoint:
        return ""
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        if parsed.scheme == "http":
            raise SubmitCommandError(
                "submit_endpoint_https_required",
                "truth submit endpoint must use HTTPS",
            )
        raise SubmitCommandError(
            "submit_endpoint_invalid",
            "truth submit endpoint must be an absolute HTTPS URL",
        )
    if parsed.username or parsed.password:
        raise SubmitCommandError(
            "submit_endpoint_userinfo_forbidden",
            "truth submit endpoint URL must not include userinfo",
        )
    return endpoint


def _open_submit_request(request: Request, *, timeout: float) -> object:
    opener = urllib.request.build_opener(_NoRedirectHandler())
    return opener.open(request, timeout=timeout)


def _load_submit_endpoint_response(
    request: Request,
    *,
    timeout: float = 10.0,
) -> dict[str, Any]:
    try:
        chunks: list[bytes] = []
        total = 0
        with _open_submit_request(request, timeout=timeout) as response:
            while True:
                chunk = response.read(_SUBMIT_ENDPOINT_READ_CHUNK_BYTES)
                if not chunk:
                    break
                total += len(chunk)
                if total > _MAX_SUBMIT_ENDPOINT_RESPONSE_BYTES:
                    raise SubmitCommandError(
                        "submit_endpoint_response_too_large",
                        "truth submit endpoint response exceeds maximum size",
                    )
                chunks.append(chunk)
    except SubmitCommandError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise SubmitCommandError(
            "submit_endpoint_unreachable",
            "truth submit endpoint could not be reached",
        ) from exc
    raw = b"".join(chunks)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SubmitCommandError(
            "submit_endpoint_response_invalid_json",
            "truth submit endpoint response was not valid JSON",
        ) from exc
    if not isinstance(payload, dict):
        raise SubmitCommandError(
            "submit_endpoint_response_not_object",
            "truth submit endpoint response must be a JSON object",
        )
    return payload


def _normalize_submit_endpoint_response(
    payload: dict[str, Any],
    *,
    fallback_edges: list[dict[str, Any]],
) -> dict[str, Any]:
    ok = payload.get("ok")
    if not isinstance(ok, bool) or ok != True:
        raise SubmitCommandError(
            "submit_endpoint_rejected",
            "truth submit endpoint did not return ok=true",
        )
    data = payload.get("data")
    if not isinstance(data, dict):
        raise SubmitCommandError(
            "submit_endpoint_data_missing",
            "truth submit endpoint response must include a data object",
        )
    node_id = data.get("node_id")
    if not isinstance(node_id, str) or not node_id:
        raise SubmitCommandError(
            "submit_endpoint_node_id_missing",
            "truth submit endpoint did not return a node_id",
        )
    try:
        parse_nodeid_strict(node_id)
    except ValueError as exc:
        raise SubmitCommandError(
            "submit_endpoint_node_id_invalid",
            "truth submit endpoint returned a non-CIDv1 node_id",
        ) from exc
    edges = data.get("edges", fallback_edges)
    if not isinstance(edges, list):
        raise SubmitCommandError(
            "submit_endpoint_edges_invalid",
            "truth submit endpoint returned invalid edges",
        )
    normalized = dict(data)
    normalized["node_id"] = node_id
    normalized["edges"] = edges
    return normalized


def _post_submit_envelope(endpoint: str, envelope: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(
        envelope,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if len(body) > _MAX_SUBMIT_PAYLOAD_BYTES:
        raise SubmitCommandError(
            "submit_payload_too_large",
            "payload exceeds maximum submit payload size",
        )
    request = Request(
        endpoint,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return _load_submit_endpoint_response(request, timeout=10.0)


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
    try:
        _require_graph_submit_agent_id(agent_id)
    except ValueError as exc:
        raise SubmitCommandError(
            "submit_agent_id_invalid",
            "--agent-id must be a 96-character lowercase hex AgentID",
        ) from exc

    epoch = getattr(args, "epoch", None)
    if epoch is None or isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise SubmitCommandError(
            "submit_epoch_invalid",
            "--epoch must be a non-negative integer",
        )

    payload = _apply_source_refs(
        _load_payload(args),
        list(getattr(args, "source_refs", None) or []),
    )

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

    envelope = _sign_submission_envelope(envelope, getattr(args, "signing_key", None))

    edges_out = [
        {"edge_type": e.edge_type, "source": e.source, "target": e.target}
        for e in result.edges
    ]

    submit_endpoint = _submit_endpoint_from_args(args)
    if submit_endpoint:
        endpoint_payload = _post_submit_envelope(submit_endpoint, envelope)
        endpoint_data = _normalize_submit_endpoint_response(
            endpoint_payload,
            fallback_edges=edges_out,
        )
        response = {
            "subcommand": "submit",
            "primitive": result.primitive,
            "creates_node": result.creates_node,
            "node_primitive_type": result.node_primitive_type,
            "node_id": endpoint_data["node_id"],
            "edges": endpoint_data["edges"],
            "graph_persistence": endpoint_data.get("graph_persistence", "persisted"),
            "gossip_delivery": endpoint_data.get("gossip_delivery", "deferred"),
            "public_submit_endpoint": submit_endpoint,
            "version": D2E_SUBMIT_CLI_VERSION,
        }
        if envelope.get("sig") not in {None, "", "UNSIGNED"}:
            response["signature"] = {
                "sig": str(envelope.get("sig", "")),
                "sig_pubkey_hex": str(envelope.get("sig_pubkey_hex", "")),
                "sig_pubkey_fingerprint": str(envelope.get("sig_pubkey_fingerprint", "")),
                "sig_scheme": str(envelope.get("sig_scheme", "")),
            }
        return response

    # CDL-075: persist to LMDB graph store when ILC_TRUTH_GRAPH_STORE_PATH is set.
    node_id: str | None = None
    graph_persistence: str = "deferred — CDL-075 graph store path not configured"
    write_receipt: dict[str, Any] = {}
    store_path = os.environ.get("ILC_TRUTH_GRAPH_STORE_PATH", "").strip()
    if store_path:
        # Missing guard attribute means this caller is using the public-RC-cleared
        # local write path. An explicit True still blocks before any LMDB write.
        check_graph_mutation_allowed(getattr(args, "public_path_guard_value", False))
        from ilc_core.epistemic.truth_primitive_graph_store import (
            write_truth_primitive_result,
        )
        from ilc_core.storage.truth_primitive_graph_lmdb_adapter import (
            TruthPrimitiveGraphStore,
        )
        store = TruthPrimitiveGraphStore(store_path)
        try:
            write_receipt = write_truth_primitive_result(store, envelope, result)
            node_id = write_receipt["node_id"]
            graph_persistence = "persisted"
        finally:
            store.close()

    # CDL-076: announce to gossip peers after confirmed CDL-075 persist.
    gossip_delivery: str = "deferred — gossip peers not configured"
    if node_id:
        from ilc_core.network.d2d.truth_primitive_gossip_runtime import (
            announce_truth_primitive,
        )
        gossip_receipt = announce_truth_primitive(write_receipt, envelope)
        gossip_delivery = gossip_receipt["gossip_delivery"]

    response: dict[str, Any] = {
        "subcommand": "submit",
        "primitive": result.primitive,
        "creates_node": result.creates_node,
        "node_primitive_type": result.node_primitive_type,
        "node_id": node_id,
        "edges": edges_out,
        "graph_persistence": graph_persistence,
        "gossip_delivery": gossip_delivery,
        "version": D2E_SUBMIT_CLI_VERSION,
    }
    if envelope.get("sig") not in {None, "", "UNSIGNED"}:
        response["signature"] = {
            "sig": str(envelope.get("sig", "")),
            "sig_pubkey_hex": str(envelope.get("sig_pubkey_hex", "")),
            "sig_pubkey_fingerprint": str(envelope.get("sig_pubkey_fingerprint", "")),
            "sig_scheme": str(envelope.get("sig_scheme", "")),
        }
    return response
