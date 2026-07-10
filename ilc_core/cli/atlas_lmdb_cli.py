# SPDX-License-Identifier: AGPL-3.0-only
"""Read-first CLI helpers for the unsigned Genesis Atlas LMDB projection.

PUBLIC_RC_EXCLUDE: genesis_atlas_lmdb_local_maintenance_cli_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB inspection helper; not
public graph activation, Genesis signing, canonical graph mutation, runtime
activation, public serving, or economic settlement.

The default surface is read-only. Mutating subcommands are local maintenance
helpers that require explicit write flags and route through AtlasLmdbSafeWriter.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.bundle.atlas_slice_manifest import (
    build_atlas_slice_manifest_from_lmdb,
    load_atlas_slice_manifest,
    sign_atlas_slice_manifest,
    verify_atlas_slice_manifest,
    write_atlas_slice_manifest,
)
from ilc_core.ledger.exact_numeric import normalize_json_scalars
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    write_json_atomic,
)


ATLAS_LMDB_CLI_VERSION = "atlas_lmdb_cli_1545p_fix59d.v0.1"
AUTHORITY_EDGE_TYPES = frozenset({"GOVERNS", "ATTESTATION"})
AUTHORITY_EDGE_ENV = "ILC_ATLAS_AUTHORITY_EDGE_AUTHORIZED"


class AtlasLmdbCliError(ValueError):
    """Typed error for Atlas LMDB read CLI failures."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(f"{token}: {message}")
        self.token = token
        self.message = message


def run_atlas_command(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch the `ilc atlas` command namespace."""
    subcommand = getattr(args, "atlas_subcommand", "")
    lmdb_path = str(getattr(args, "lmdb", "") or "")
    if subcommand == "status":
        return handle_atlas_status(lmdb_path)
    if subcommand == "validate":
        return handle_atlas_validate(lmdb_path)
    if subcommand == "node":
        return handle_atlas_node(lmdb_path, str(getattr(args, "node_id", "") or ""))
    if subcommand == "edges":
        return handle_atlas_edges(lmdb_path, str(getattr(args, "node_id", "") or ""))
    if subcommand == "register-phase-files":
        return handle_atlas_register_phase_files(
            lmdb_path=lmdb_path,
            phase=str(getattr(args, "phase", "") or ""),
            files=tuple(getattr(args, "files", ()) or ()),
            node_kind=str(getattr(args, "node_kind", "") or "phase_artifact"),
            graph_projection=str(
                getattr(args, "graph_projection", "") or "support_candidate_graph"
            ),
            graph_delta=str(getattr(args, "graph_delta", "") or "support_only"),
            required_edges=tuple(getattr(args, "required_edges", ()) or ()),
            write=bool(getattr(args, "write", False)),
            receipt_path=str(getattr(args, "receipt", "") or ""),
        )
    if subcommand == "apply-edge-batch":
        return handle_atlas_apply_edge_batch(
            lmdb_path=lmdb_path,
            input_path=str(getattr(args, "input", "") or ""),
            write=bool(getattr(args, "write", False)),
            receipt_path=str(getattr(args, "receipt", "") or ""),
        )
    if subcommand == "apply-node-edge-plan":
        return handle_atlas_apply_node_edge_plan(
            lmdb_path=lmdb_path,
            input_path=str(getattr(args, "input", "") or ""),
            write=bool(getattr(args, "write", False)),
            receipt_path=str(getattr(args, "receipt", "") or ""),
        )
    if subcommand == "build-slice":
        return handle_atlas_build_slice(
            lmdb_path=lmdb_path,
            slice_variant=str(getattr(args, "slice_variant", "") or ""),
            projection=str(getattr(args, "projection", "") or ""),
            output_path=str(getattr(args, "output", "") or ""),
            slice_version=str(getattr(args, "slice_version", "") or "0.1"),
        )
    if subcommand == "sign-manifest":
        return handle_atlas_sign_manifest(
            manifest_path=str(getattr(args, "manifest", "") or ""),
            private_key_hex=str(getattr(args, "private_key_hex", "") or ""),
            output_path=str(getattr(args, "output", "") or ""),
        )
    if subcommand == "verify-slice":
        return handle_atlas_verify_slice(
            manifest_path=str(getattr(args, "manifest", "") or ""),
            public_key_hex=str(getattr(args, "public_key_hex", "") or ""),
            require_signature=bool(getattr(args, "require_signature", True)),
        )
    raise AtlasLmdbCliError("atlas_subcommand_missing", "atlas subcommand is required")


def handle_atlas_status(lmdb_path: str) -> dict[str, Any]:
    """Return deterministic status information for a local Atlas LMDB."""
    writer = _open_writer(lmdb_path)
    try:
        inspection = writer.inspect()
        payload = writer.store.get_graph_payload() or {}
        metadata = _metadata_snapshot(writer)
        edge_id_coverage = _edge_id_coverage(writer.store.iter_edges())
        graph_payload_sha256 = _sha256_json(payload) if payload else ""
        return {
            "subcommand": "status",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "counts": {
                "nodes": inspection["node_count"],
                "edges": inspection["edge_count"],
                "preimages": inspection["preimage_count"],
                "graph_payload_nodes": inspection["graph_payload_node_count"],
                "graph_payload_edges": inspection["graph_payload_edge_count"],
            },
            "edge_id_coverage": edge_id_coverage,
            "graph_payload_sha256": graph_payload_sha256,
            "materialization_manifest": metadata.get("materialization_manifest", {}),
            "metadata": metadata,
            "invariants": inspection["invariants"],
            "dangling_edge_count": inspection["dangling_edge_count"],
            "read_only": True,
        }
    finally:
        writer.close()


def handle_atlas_validate(lmdb_path: str) -> dict[str, Any]:
    """Validate the local Atlas LMDB row stores and graph payload."""
    writer = _open_writer(lmdb_path)
    try:
        inspection = writer.inspect()
        edges = writer.store.iter_edges()
        coverage = _edge_id_coverage(edges)
        checks = {
            "no_dangling_edges": inspection["invariants"]["no_dangling_edges"],
            "payload_node_count_matches_rows": inspection["invariants"][
                "payload_node_count_matches_rows"
            ],
            "payload_edge_count_matches_rows": inspection["invariants"][
                "payload_edge_count_matches_rows"
            ],
            "tier_index_matches_rows": inspection["invariants"]["tier_index_matches_rows"],
            "tier_group_index_matches_rows": inspection["invariants"][
                "tier_group_index_matches_rows"
            ],
            "source_path_index_matches_rows": inspection["invariants"][
                "source_path_index_matches_rows"
            ],
        }
        hard_pass = all(checks.values())
        edge_id_status = (
            "complete" if coverage["missing_edge_id_count"] == 0 else "debt_present_carried_to_fix60"
        )
        return {
            "subcommand": "validate",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "verdict": "pass" if hard_pass else "fail",
            "checks": checks,
            "edge_id_coverage": coverage,
            "edge_id_status": edge_id_status,
            "read_only": True,
        }
    finally:
        writer.close()


def handle_atlas_node(lmdb_path: str, node_id: str) -> dict[str, Any]:
    """Return a single Atlas node record by candidate ID."""
    if not node_id:
        raise AtlasLmdbCliError("atlas_node_id_missing", "--node-id must be non-empty")
    writer = _open_writer(lmdb_path)
    try:
        record = writer.store.get_node(node_id)
        if record is None:
            raise AtlasLmdbCliError("atlas_node_not_found", f"node not found: {node_id}")
        return {
            "subcommand": "node",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "node_id": node_id,
            "node_record": _stable_object(record),
            "read_only": True,
        }
    finally:
        writer.close()


def handle_atlas_edges(lmdb_path: str, node_id: str) -> dict[str, Any]:
    """Return Atlas edges where source or target equals candidate ID."""
    if not node_id:
        raise AtlasLmdbCliError("atlas_node_id_missing", "--node-id must be non-empty")
    writer = _open_writer(lmdb_path)
    try:
        edges = [
            _stable_object(edge)
            for edge in writer.store.iter_edges()
            if _edge_source(edge) == node_id or _edge_target(edge) == node_id
        ]
        edges.sort(
            key=lambda edge: (
                str(edge.get("edge_id", "")),
                _edge_source(edge),
                _edge_type(edge),
                _edge_target(edge),
            )
        )
        return {
            "subcommand": "edges",
            "version": ATLAS_LMDB_CLI_VERSION,
            "lmdb_path": str(Path(lmdb_path)),
            "node_id": node_id,
            "count": len(edges),
            "edges": edges,
            "read_only": True,
        }
    finally:
        writer.close()


def handle_atlas_register_phase_files(
    *,
    lmdb_path: str,
    phase: str,
    files: tuple[str, ...],
    node_kind: str,
    graph_projection: str,
    graph_delta: str,
    required_edges: tuple[str, ...],
    write: bool,
    receipt_path: str = "",
) -> dict[str, Any]:
    """Register phase artifacts in the local unsigned Atlas LMDB."""
    if not phase.strip():
        raise AtlasLmdbCliError("atlas_phase_missing", "--phase must be non-empty")
    if not files:
        raise AtlasLmdbCliError("atlas_files_missing", "--file must be provided at least once")
    parsed_required_edges = tuple(_parse_required_edge(item) for item in required_edges)
    registrations = [
        AtlasPhaseFileRegistration(
            path=file_path,
            node_kind=node_kind,
            graph_projection=graph_projection,
            graph_delta=graph_delta,
            required_edges=parsed_required_edges,
        )
        for file_path in files
    ]
    writer = _open_writer(lmdb_path)
    try:
        plan = writer.build_phase_file_registration_plan(
            phase=phase,
            files=registrations,
            dry_run=not write,
        )
        return _guarded_apply_plan(
            writer=writer,
            plan=plan,
            write=write,
            receipt_path=receipt_path,
            operation="register_phase_files",
        )
    finally:
        writer.close()


def handle_atlas_apply_edge_batch(
    *,
    lmdb_path: str,
    input_path: str,
    write: bool,
    receipt_path: str = "",
) -> dict[str, Any]:
    """Apply or dry-run a local edge batch through the safe writer."""
    payload = _load_json_file(input_path)
    if isinstance(payload, list):
        edges = payload
        metadata: dict[str, Any] = {"operation": "edge_batch", "input_shape": "list"}
        phase = "1545p-Fix59d-edge-batch"
    elif isinstance(payload, dict):
        edges = payload.get("edges", payload.get("edges_to_add", ()))
        metadata = _metadata_from_payload(payload, operation="edge_batch")
        phase = str(payload.get("phase", "") or "1545p-Fix59d-edge-batch")
    else:
        raise AtlasLmdbCliError("atlas_input_invalid", "edge batch must be an object or list")
    if not isinstance(edges, list):
        raise AtlasLmdbCliError("atlas_edges_invalid", "edge batch requires a list of edges")
    _assert_json_safe_plan_value({"edges": edges, "metadata": metadata})
    writer = _open_writer(lmdb_path)
    try:
        plan = AtlasLmdbWritePlan(
            edges_to_add=[_require_object(edge, "edge") for edge in edges],
            metadata=metadata,
            phase=phase,
            dry_run=not write,
        )
        return _guarded_apply_plan(
            writer=writer,
            plan=plan,
            write=write,
            receipt_path=receipt_path,
            operation="apply_edge_batch",
        )
    finally:
        writer.close()


def handle_atlas_apply_node_edge_plan(
    *,
    lmdb_path: str,
    input_path: str,
    write: bool,
    receipt_path: str = "",
) -> dict[str, Any]:
    """Apply or dry-run a node+edge materialization plan through the safe writer."""
    payload = _load_json_file(input_path)
    if not isinstance(payload, dict):
        raise AtlasLmdbCliError("atlas_input_invalid", "node-edge plan must be an object")
    nodes = payload.get("nodes", payload.get("nodes_to_add", ()))
    edges = payload.get("edges", payload.get("edges_to_add", ()))
    if not isinstance(nodes, list):
        raise AtlasLmdbCliError("atlas_nodes_invalid", "node-edge plan requires nodes list")
    if not isinstance(edges, list):
        raise AtlasLmdbCliError("atlas_edges_invalid", "node-edge plan requires edges list")
    metadata = _metadata_from_payload(payload, operation="node_edge_plan")
    phase = str(payload.get("phase", "") or "1545p-Fix59d-node-edge-plan")
    _assert_json_safe_plan_value({"nodes": nodes, "edges": edges, "metadata": metadata})
    writer = _open_writer(lmdb_path)
    try:
        plan = AtlasLmdbWritePlan(
            nodes_to_add=[_require_object(node, "node") for node in nodes],
            edges_to_add=[_require_object(edge, "edge") for edge in edges],
            metadata=metadata,
            phase=phase,
            dry_run=not write,
        )
        return _guarded_apply_plan(
            writer=writer,
            plan=plan,
            write=write,
            receipt_path=receipt_path,
            operation="apply_node_edge_plan",
        )
    finally:
        writer.close()


def handle_atlas_build_slice(
    *,
    lmdb_path: str,
    slice_variant: str,
    projection: str,
    output_path: str,
    slice_version: str,
) -> dict[str, Any]:
    """Build an unsigned local AtlasSliceManifest."""

    manifest = build_atlas_slice_manifest_from_lmdb(
        lmdb_path=lmdb_path,
        slice_variant=slice_variant,
        projection=projection,
        slice_version=slice_version,
    )
    if output_path:
        write_atlas_slice_manifest(output_path, manifest)
    return {
        "subcommand": "build-slice",
        "version": ATLAS_LMDB_CLI_VERSION,
        "manifest": manifest.to_json_dict(),
        "output_path": output_path,
        "non_claims": {
            "genesis_signing": False,
            "ml_dsa_manifest_signing": False,
            "public_graph_publication": False,
            "public_rc_activation": False,
        },
        "read_only": True,
    }


def handle_atlas_sign_manifest(
    *,
    manifest_path: str,
    private_key_hex: str,
    output_path: str,
) -> dict[str, Any]:
    """Dev/test-sign an AtlasSliceManifest with Ed25519 COSE-Sign1."""

    if not manifest_path:
        raise AtlasLmdbCliError("atlas_manifest_missing", "--manifest must be provided")
    private_key = _ed25519_private_key_from_hex(private_key_hex)
    signed = sign_atlas_slice_manifest(
        load_atlas_slice_manifest(manifest_path),
        private_key=private_key,
    )
    target_path = output_path or manifest_path
    write_atlas_slice_manifest(target_path, signed)
    return {
        "subcommand": "sign-manifest",
        "version": ATLAS_LMDB_CLI_VERSION,
        "cidv1": signed.cidv1,
        "dev_signed": signed.dev_signed,
        "output_path": target_path,
        "signature_profile": "ed25519_cose_sign1_dev_test_only",
        "non_claims": {
            "genesis_signing": False,
            "ml_dsa_manifest_signing": False,
            "public_graph_publication": False,
            "public_rc_activation": False,
        },
        "read_only": True,
    }


def handle_atlas_verify_slice(
    *,
    manifest_path: str,
    public_key_hex: str,
    require_signature: bool,
) -> dict[str, Any]:
    """Verify deterministic manifest commitments and dev/test signature."""

    if not manifest_path:
        raise AtlasLmdbCliError("atlas_manifest_missing", "--manifest must be provided")
    public_key = _ed25519_public_key_from_hex(public_key_hex) if public_key_hex else None
    manifest = load_atlas_slice_manifest(manifest_path)
    try:
        verify_atlas_slice_manifest(
            manifest,
            public_key=public_key,
            require_signature=require_signature,
        )
    except ValueError as exc:
        raise AtlasLmdbCliError(str(exc).split(":", 1)[0], str(exc)) from exc
    return {
        "subcommand": "verify-slice",
        "version": ATLAS_LMDB_CLI_VERSION,
        "cidv1": manifest.cidv1,
        "dev_signed": manifest.dev_signed,
        "signature_required": require_signature,
        "verdict": "pass",
        "read_only": True,
    }


def _open_writer(lmdb_path: str) -> AtlasLmdbSafeWriter:
    if not isinstance(lmdb_path, str) or not lmdb_path.strip():
        raise AtlasLmdbCliError("atlas_lmdb_path_missing", "--lmdb must be provided")
    root = Path(lmdb_path)
    data_file = root / "data.mdb"
    lock_file = root / "lock.mdb"
    if not data_file.exists() or not lock_file.exists():
        raise AtlasLmdbCliError("atlas_lmdb_not_found", f"LMDB not found: {root}")
    return AtlasLmdbSafeWriter(root)


def _ed25519_private_key_from_hex(value: str) -> ed25519.Ed25519PrivateKey:
    if not value:
        raise AtlasLmdbCliError(
            "atlas_manifest_private_key_missing",
            "--private-key-hex must be provided for dev/test signing",
        )
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise AtlasLmdbCliError("atlas_manifest_private_key_invalid", "invalid hex") from exc
    if len(raw) != 32:
        raise AtlasLmdbCliError(
            "atlas_manifest_private_key_invalid",
            "Ed25519 private key seed must be 32 bytes",
        )
    return ed25519.Ed25519PrivateKey.from_private_bytes(raw)


def _ed25519_public_key_from_hex(value: str) -> ed25519.Ed25519PublicKey:
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise AtlasLmdbCliError("atlas_manifest_public_key_invalid", "invalid hex") from exc
    if len(raw) != 32:
        raise AtlasLmdbCliError(
            "atlas_manifest_public_key_invalid",
            "Ed25519 public key must be 32 bytes",
        )
    return ed25519.Ed25519PublicKey.from_public_bytes(raw)


def _metadata_snapshot(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    keys = (
        "materialization_manifest",
        "fix55_graph_projection_classification",
        "fix59a_deferred_repair_reconciliation",
        "last_safe_writer_receipt",
    )
    return {
        key: value
        for key in keys
        if (value := writer.store.get_meta(key)) is not None
    }


def _guarded_apply_plan(
    *,
    writer: AtlasLmdbSafeWriter,
    plan: AtlasLmdbWritePlan,
    write: bool,
    receipt_path: str,
    operation: str,
) -> dict[str, Any]:
    _assert_authority_gate(plan=plan, write=write)
    validation = writer.validate_plan(plan)
    if validation["rejected_edges"]:
        receipt = _cli_receipt_from_validation(
            validation,
            mutated=False,
            operation=operation,
            reason="rejected_edges_present",
        )
        _write_receipt_if_requested(receipt_path, receipt)
        return receipt
    if not write:
        receipt = _cli_receipt_from_validation(
            validation,
            mutated=False,
            operation=operation,
            reason="dry_run_default",
        )
        _write_receipt_if_requested(receipt_path, receipt)
        return receipt
    receipt = writer.apply_plan(
        AtlasLmdbWritePlan(
            nodes_to_add=plan.nodes_to_add,
            edges_to_add=plan.edges_to_add,
            metadata=plan.metadata,
            phase=plan.phase,
            dry_run=False,
        )
    )
    receipt = _stable_object(
        {
            **receipt,
            "cli_operation": operation,
            "non_claims": _non_claims(),
            "write_requested": True,
        }
    )
    _write_receipt_if_requested(receipt_path, receipt)
    return receipt


def _cli_receipt_from_validation(
    validation: dict[str, Any],
    *,
    mutated: bool,
    operation: str,
    reason: str,
) -> dict[str, Any]:
    return _stable_object(
        {
            "accepted_edge_count": len(validation["accepted_edges"]),
            "accepted_edges": _edge_summary(validation["accepted_edges"]),
            "accepted_node_count": len(validation["accepted_nodes"]),
            "accepted_nodes": _node_summary(validation["accepted_nodes"]),
            "cli_operation": operation,
            "dry_run": bool(validation["dry_run"]),
            "metadata": validation["metadata"],
            "mutated": mutated,
            "non_claims": _non_claims(),
            "phase": validation["phase"],
            "pre_counts": validation["pre_counts"],
            "projected_counts": validation["projected_counts"],
            "projected_dangling_edge_count": len(validation["projected_dangling_edges"]),
            "projected_dangling_edges": validation["projected_dangling_edges"][:50],
            "reason": reason,
            "rejected_edge_count": len(validation["rejected_edges"]),
            "rejected_edges": validation["rejected_edges"],
            "skipped_edge_count": len(validation["skipped_edges"]),
            "skipped_edges": validation["skipped_edges"][:50],
            "skipped_node_count": len(validation["skipped_nodes"]),
            "skipped_nodes": validation["skipped_nodes"],
            "status": "PASS" if not validation["rejected_edges"] else "FAIL",
            "version": ATLAS_LMDB_CLI_VERSION,
            "write_requested": False,
        }
    )


def _assert_authority_gate(*, plan: AtlasLmdbWritePlan, write: bool) -> None:
    authority_edges = [
        edge
        for edge in plan.edges_to_add
        if isinstance(edge, dict) and _edge_type(edge) in AUTHORITY_EDGE_TYPES
    ]
    if not authority_edges:
        return
    if not write:
        raise AtlasLmdbCliError(
            "atlas_authority_edge_write_blocked",
            "authority edge writes require --write and environment authorization",
        )
    if os.environ.get(AUTHORITY_EDGE_ENV) != "1":
        raise AtlasLmdbCliError(
            "atlas_authority_edge_env_missing",
            f"authority edge writes require {AUTHORITY_EDGE_ENV}=1",
        )


def _parse_required_edge(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise AtlasLmdbCliError(
            "atlas_required_edge_invalid",
            "--edge must use EDGE_TYPE:target_id",
        )
    edge_type, target = value.split(":", 1)
    if not edge_type or not target:
        raise AtlasLmdbCliError(
            "atlas_required_edge_invalid",
            "--edge must use EDGE_TYPE:target_id",
        )
    return edge_type, target


def _load_json_file(input_path: str) -> Any:
    if not input_path:
        raise AtlasLmdbCliError("atlas_input_missing", "--input must be provided")
    path = Path(input_path)
    if not path.exists():
        raise AtlasLmdbCliError("atlas_input_not_found", f"input not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AtlasLmdbCliError("atlas_input_invalid_json", str(exc)) from exc
    _assert_json_safe_plan_value(payload)
    return payload


def _metadata_from_payload(payload: dict[str, Any], *, operation: str) -> dict[str, Any]:
    metadata = payload.get("metadata", {})
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise AtlasLmdbCliError("atlas_metadata_invalid", "metadata must be an object")
    return {**metadata, "operation": operation}


def _assert_json_safe_plan_value(value: Any, *, path: str = "plan") -> None:
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, float):
        raise AtlasLmdbCliError("atlas_float_forbidden", f"float forbidden at {path}")
    if isinstance(value, str):
        lowered_path = path.lower()
        if "commit" in lowered_path or "content_digest" in lowered_path:
            raise AtlasLmdbCliError(
                "atlas_self_referential_field_forbidden",
                f"self-referential field forbidden at {path}",
            )
        return
    if isinstance(value, int):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_json_safe_plan_value(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise AtlasLmdbCliError("atlas_key_invalid", f"non-string key at {path}")
            lowered_key = key.lower()
            if "commit" in lowered_key or "content_digest" in lowered_key:
                raise AtlasLmdbCliError(
                    "atlas_self_referential_field_forbidden",
                    f"self-referential field forbidden at {path}.{key}",
                )
            _assert_json_safe_plan_value(item, path=f"{path}.{key}")
        return
    raise AtlasLmdbCliError("atlas_value_invalid", f"unsupported value at {path}")


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AtlasLmdbCliError("atlas_record_invalid", f"{label} must be an object")
    return value


def _write_receipt_if_requested(receipt_path: str, receipt: dict[str, Any]) -> None:
    if receipt_path:
        write_json_atomic(Path(receipt_path), receipt)


def _non_claims() -> dict[str, bool]:
    return {
        "canonical_graph_mutation": False,
        "economic_settlement": False,
        "genesis_signing": False,
        "public_graph_publication": False,
        "public_rc_activation": False,
        "runtime_activation": False,
    }


def _edge_id_coverage(edges: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(edges)
    present = sum(1 for edge in edges if isinstance(edge.get("edge_id"), str) and edge["edge_id"])
    missing = total - present
    return {
        "edge_count": total,
        "present_edge_id_count": present,
        "missing_edge_id_count": missing,
        "present_fraction": _ratio_string(present, total),
    }


def _ratio_string(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0/0"
    return f"{numerator}/{denominator}"


def _sha256_json(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        normalize_json_scalars(payload),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_object(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        normalize_json_scalars(payload),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    value = json.loads(encoded)
    if not isinstance(value, dict):
        raise AtlasLmdbCliError("atlas_record_not_object", "LMDB record was not an object")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise AtlasLmdbCliError("atlas_edge_source_missing", "edge record missing source")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise AtlasLmdbCliError("atlas_edge_target_missing", "edge record missing target")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if isinstance(value, str) and value:
        return value
    raise AtlasLmdbCliError("atlas_edge_type_missing", "edge record missing edge_type")


def _node_summary(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "candidate_id": str(node.get("candidate_id", "")),
            "graph_projection": str(node.get("graph_projection", "")),
            "node_kind": str(node.get("node_kind", "")),
            "source_path": str(node.get("source_path", "")),
        }
        for node in nodes
    ]


def _edge_summary(edges: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "edge_id": str(edge.get("edge_id", "")),
            "edge_type": _edge_type(edge),
            "source": _edge_source(edge),
            "target": _edge_target(edge),
        }
        for edge in edges
    ]


__all__ = [
    "ATLAS_LMDB_CLI_VERSION",
    "AtlasLmdbCliError",
    "handle_atlas_build_slice",
    "handle_atlas_edges",
    "handle_atlas_node",
    "handle_atlas_status",
    "handle_atlas_validate",
    "handle_atlas_register_phase_files",
    "handle_atlas_apply_edge_batch",
    "handle_atlas_apply_node_edge_plan",
    "handle_atlas_sign_manifest",
    "handle_atlas_verify_slice",
    "run_atlas_command",
]
