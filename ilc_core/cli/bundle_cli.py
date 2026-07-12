# SPDX-License-Identifier: AGPL-3.0-only
"""Bundle CLI helpers for deterministic ADR-0009 Layer0 artifacts."""

from __future__ import annotations

import base64
import json
import os
import tempfile
from pathlib import Path
from typing import Any

def _load_json(path_raw: str, *, default: Any) -> Any:
    if path_raw == "":
        return default
    path = Path(path_raw)
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def generate_layer0_bundle_cli(args: Any) -> dict[str, Any]:
    """Generate an unsigned Layer0 protocol bundle for CLI output."""

    from ilc_core.bundle.layer0_protocol_bundle import generate_layer0_protocol_bundle
    from ilc_core.private_json_guardrails import canonical_json

    schemas = _load_json(str(getattr(args, "schemas", "") or ""), default=[])
    parameters = _load_json(str(getattr(args, "parameters", "") or ""), default={})
    if not isinstance(schemas, list):
        raise ValueError("layer0_cli_schemas_must_be_list")
    if not isinstance(parameters, dict):
        raise ValueError("layer0_cli_parameters_must_be_object")

    include_truth_primitives = bool(getattr(args, "include_truth_primitives", False))
    bundle = generate_layer0_protocol_bundle(
        bundle_id=str(args.bundle_id),
        version=str(args.version),
        schemas=schemas,
        parameters=parameters,
        include_truth_primitive_schemas=include_truth_primitives,
        signing_private_key=None,
    )
    payload: dict[str, Any] = {
        "bundle_id": bundle.bundle_id,
        "canonical_json": bundle.canonical_json,
        "cidv1": bundle.cidv1,
        "cose_sign1_b64": base64.b64encode(bundle.cose_sign1).decode("ascii"),
        "dag_cbor_b64": base64.b64encode(bundle.dag_cbor).decode("ascii"),
        "include_truth_primitives": include_truth_primitives,
        "public_rc_exclude": bundle.public_rc_exclude,
        "sha256": bundle.sha256,
        "version": bundle.version,
    }
    body = canonical_json(payload, float_token="layer0_bundle_cli_float_not_allowed")

    output_raw = str(getattr(args, "output", "") or "")
    if output_raw:
        output_path = Path(output_raw)
        _atomic_write_text(output_path, body)
        payload["output_path"] = str(output_path)
        payload["output_written"] = True
    else:
        payload["output_written"] = False
    return payload


__all__ = ["generate_layer0_bundle_cli"]
