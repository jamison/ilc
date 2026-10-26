#!/usr/bin/env python3
"""Run the Row 35b local package and tensor demonstration."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import tempfile
from importlib.metadata import distribution, version
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import numpy._core._multiarray_umath as numpy_multiarray

from ilc_core.sufficiency.local_interp import (
    EXECUTION_PROFILE,
    RECIPE_SCHEMA_VERSION,
    LocalFixtureStore,
    OperationDefinition,
    execute_recipe,
)


SCHEMA_VERSION = "sufficiency_package_tensor_demo_v0"
COMPLETED_AT = "2026-10-22T14:00:00Z"
TENSOR_PROFILE_REF = "fixture:tensor-profile:int32-le-row-major-v0"
TENSOR_INTEGRITY_DOMAIN = "ilc.tensor.raw-bytes.v0"
TENSOR_DESCRIPTOR_KEYS = frozenset(
    {
        "schema_version",
        "encoding_version",
        "implementation_profile_ref",
        "dtype",
        "itemsize_bytes",
        "shape",
        "element_count",
        "byte_order",
        "layout",
        "major_order",
        "strides_bytes",
        "byte_length",
        "payload_integrity",
        "view",
        "semantic_labels",
        "created_at",
        "author_ref",
        "supersedes_descriptor_ref",
    }
)
MAX_TENSOR_BYTES = 4_096
MAX_TENSOR_ELEMENTS = 1_024
MAX_TENSOR_RANK = 8
MAX_TENSOR_DIMENSION = 1_024
MAX_SEMANTIC_LABELS = 32
MAX_METADATA_STRING_LENGTH = 1_024
MAX_METADATA_NODES = 256
MAX_METADATA_DEPTH = 4


class FixtureValidationError(ValueError):
    """Stable pre-execution rejection for the bounded demonstration fixture."""


def _validate_semantic_labels(value: Any) -> None:
    nodes = 0

    def walk(item: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > MAX_METADATA_NODES or depth > MAX_METADATA_DEPTH:
            raise FixtureValidationError("tensor_semantic_labels_invalid")
        if item is None or type(item) is bool:
            return
        if type(item) is int:
            if abs(item) > 2**53:
                raise FixtureValidationError("tensor_semantic_labels_invalid")
            return
        if type(item) is str:
            if len(item) > MAX_METADATA_STRING_LENGTH:
                raise FixtureValidationError("tensor_semantic_labels_invalid")
            return
        if type(item) is list:
            if len(item) > MAX_SEMANTIC_LABELS:
                raise FixtureValidationError("tensor_semantic_labels_invalid")
            for child in item:
                walk(child, depth + 1)
            return
        if type(item) is dict:
            if len(item) > MAX_SEMANTIC_LABELS:
                raise FixtureValidationError("tensor_semantic_labels_invalid")
            for key, child in item.items():
                if type(key) is not str or not key or len(key) > MAX_METADATA_STRING_LENGTH:
                    raise FixtureValidationError("tensor_semantic_labels_invalid")
                walk(child, depth + 1)
            return
        raise FixtureValidationError("tensor_semantic_labels_invalid")

    walk(value, 0)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _numpy_license_path() -> Path:
    dist = distribution("numpy")
    matches = [
        dist.locate_file(item)
        for item in (dist.files or ())
        if str(item).endswith("dist-info/licenses/LICENSE.txt")
    ]
    if len(matches) != 1:
        raise FixtureValidationError("numpy_license_file_unresolved")
    return Path(matches[0]).resolve()


def verify_bsd3_license_text(license_text: str) -> None:
    markers = (
        "Redistribution and use in source and binary forms",
        "Redistributions of source code must retain",
        "Redistributions in binary form must reproduce",
        "Neither the name of the NumPy Developers",
        "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS",
    )
    if type(license_text) is not str or not all(
        marker in license_text for marker in markers
    ):
        raise FixtureValidationError("package_license_not_verified")


def verify_package_fixture(
    *,
    artifact_path: Path | None = None,
    expected_sha256: str | None = None,
    expected_version: str | None = None,
    operation_id: str = "numpy.gcd",
) -> dict[str, Any]:
    """Verify the exact local NumPy artifact and permissive license."""

    if operation_id != "numpy.gcd":
        raise FixtureValidationError("package_operation_identity_mismatch")
    numpy_version = version("numpy")
    if expected_version is not None and numpy_version != expected_version:
        raise FixtureValidationError("package_version_mismatch")
    license_path = _numpy_license_path()
    license_text = license_path.read_text(encoding="utf-8")
    verify_bsd3_license_text(license_text)
    canonical_artifact = Path(numpy_multiarray.__file__).resolve()
    canonical_sha256 = _sha256_file(canonical_artifact)
    resolved_artifact = (
        Path(artifact_path).resolve()
        if artifact_path is not None
        else canonical_artifact
    )
    if not resolved_artifact.is_file():
        raise FixtureValidationError("package_artifact_missing")
    artifact_sha256 = _sha256_file(resolved_artifact)
    if artifact_sha256 != canonical_sha256:
        raise FixtureValidationError("package_artifact_digest_mismatch")
    if expected_sha256 is not None and canonical_sha256 != expected_sha256:
        raise FixtureValidationError("package_expected_digest_mismatch")
    return {
        "package": "numpy",
        "version": numpy_version,
        "operation_id": operation_id,
        "artifact_filename": resolved_artifact.name,
        "artifact_sha256": artifact_sha256,
        "implementation_ref": (
            f"sha256:{artifact_sha256}#numpy.gcd@{numpy_version}"
        ),
        "license": {
            "spdx": "BSD-3-Clause",
            "verified": True,
            "evidence_filename": license_path.name,
            "evidence_sha256": _sha256_file(license_path),
        },
    }


def build_tensor_fixture() -> tuple[dict[str, Any], bytes]:
    values = (1, 2, 3, 4)
    payload = struct.pack("<4i", *values)
    descriptor = {
        "schema_version": "tensor_payload_descriptor_v0",
        "encoding_version": "raw_contiguous_v0",
        "implementation_profile_ref": TENSOR_PROFILE_REF,
        "dtype": "int32",
        "itemsize_bytes": 4,
        "shape": [2, 2],
        "element_count": 4,
        "byte_order": "little",
        "layout": "contiguous",
        "major_order": "row_major",
        "strides_bytes": [8, 4],
        "byte_length": len(payload),
        "payload_integrity": {
            "algorithm": "sha256",
            "digest": _sha256_bytes(payload),
            "hashed_byte_length": len(payload),
            "domain": TENSOR_INTEGRITY_DOMAIN,
        },
        "view": None,
        "semantic_labels": {"axes": ["row", "column"]},
        "created_at": COMPLETED_AT,
        "author_ref": "fixture:row35b",
        "supersedes_descriptor_ref": None,
    }
    validate_tensor_fixture(descriptor, payload)
    return descriptor, payload


def validate_tensor_fixture(descriptor: Mapping[str, Any], payload: bytes) -> None:
    """Validate the complete bounded local Phase 1622 descriptor profile."""

    if type(descriptor) is not dict:
        raise FixtureValidationError("tensor_descriptor_type_invalid")
    if set(descriptor) != TENSOR_DESCRIPTOR_KEYS:
        raise FixtureValidationError("tensor_descriptor_fields_invalid")
    if type(payload) is not bytes:
        raise FixtureValidationError("tensor_payload_type_invalid")
    if len(payload) > MAX_TENSOR_BYTES:
        raise FixtureValidationError("tensor_payload_size_exceeded")
    exact = {
        "schema_version": "tensor_payload_descriptor_v0",
        "encoding_version": "raw_contiguous_v0",
        "implementation_profile_ref": TENSOR_PROFILE_REF,
        "dtype": "int32",
        "itemsize_bytes": 4,
        "byte_order": "little",
        "layout": "contiguous",
        "major_order": "row_major",
        "view": None,
    }
    for field, expected in exact.items():
        if descriptor[field] != expected or type(descriptor[field]) is not type(expected):
            raise FixtureValidationError(f"tensor_{field}_invalid")
    shape = descriptor["shape"]
    if type(shape) is not list or len(shape) > MAX_TENSOR_RANK:
        raise FixtureValidationError("tensor_shape_invalid")
    if any(
        type(dim) is not int or dim < 0 or dim > MAX_TENSOR_DIMENSION
        for dim in shape
    ):
        raise FixtureValidationError("tensor_dimension_invalid")
    element_count = 1
    for dim in shape:
        element_count *= dim
        if element_count > MAX_TENSOR_ELEMENTS:
            raise FixtureValidationError("tensor_element_count_exceeded")
    if type(descriptor["element_count"]) is not int or descriptor["element_count"] != element_count:
        raise FixtureValidationError("tensor_element_count_invalid")
    expected_length = element_count * descriptor["itemsize_bytes"]
    if type(descriptor["byte_length"]) is not int or descriptor["byte_length"] != expected_length:
        raise FixtureValidationError("tensor_byte_length_invalid")
    if len(payload) != expected_length:
        raise FixtureValidationError("tensor_payload_length_mismatch")
    expected_strides: list[int] = []
    stride = descriptor["itemsize_bytes"]
    for dim in reversed(shape):
        expected_strides.append(stride)
        stride *= dim
    expected_strides.reverse()
    strides = descriptor["strides_bytes"]
    if (
        type(strides) is not list
        or len(strides) != len(shape)
        or any(type(value) is not int or value < 0 for value in strides)
        or strides != expected_strides
    ):
        raise FixtureValidationError("tensor_strides_invalid")
    integrity = descriptor["payload_integrity"]
    if type(integrity) is not dict or set(integrity) != {
        "algorithm", "digest", "hashed_byte_length", "domain"
    }:
        raise FixtureValidationError("tensor_payload_integrity_fields_invalid")
    if integrity["algorithm"] != "sha256" or integrity["domain"] != TENSOR_INTEGRITY_DOMAIN:
        raise FixtureValidationError("tensor_payload_integrity_profile_invalid")
    if type(integrity["hashed_byte_length"]) is not int or integrity["hashed_byte_length"] != len(payload):
        raise FixtureValidationError("tensor_hashed_byte_length_invalid")
    digest = integrity["digest"]
    if type(digest) is not str or len(digest) != 64 or digest != digest.lower():
        raise FixtureValidationError("tensor_payload_digest_format_invalid")
    if _sha256_bytes(payload) != digest:
        raise FixtureValidationError("tensor_payload_digest_mismatch")
    semantic_labels = descriptor["semantic_labels"]
    if type(semantic_labels) not in (dict, type(None)):
        raise FixtureValidationError("tensor_semantic_labels_invalid")
    _validate_semantic_labels(semantic_labels)
    for field in ("created_at", "author_ref"):
        if type(descriptor[field]) is not str or not descriptor[field]:
            raise FixtureValidationError(f"tensor_{field}_invalid")
    if descriptor["supersedes_descriptor_ref"] is not None and type(
        descriptor["supersedes_descriptor_ref"]
    ) is not str:
        raise FixtureValidationError("tensor_supersedes_descriptor_ref_invalid")


def _one_step_recipe(
    *,
    operation_id: str,
    implementation_ref: str,
    inputs: list[dict[str, str]],
    bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": RECIPE_SCHEMA_VERSION,
        "recipe_version": "row35b.v0",
        "execution_profile": EXECUTION_PROFILE,
        "inputs": inputs,
        "steps": [
            {
                "step_id": "compute",
                "operation_ref": {
                    "operation_id": operation_id,
                    "operation_version": "1",
                    "implementation_ref": implementation_ref,
                },
                "bindings": bindings,
                "outputs": ["result"],
                "effects": [],
            }
        ],
        "outputs": [{"name": "result", "value_ref": "value:result"}],
        "effects": [],
        "limits": {"expanded_steps": 1},
    }


def run_demonstrations() -> dict[str, Any]:
    package = verify_package_fixture()
    package_calls = 0

    def package_handler(left: int, right: int):
        nonlocal package_calls
        package_calls += 1
        return {"result": int(np.gcd(left, right))}

    roles = (("left", 0), ("right", 1))
    package_store = LocalFixtureStore(
        (
            OperationDefinition(
                "numpy.gcd", "1", package["implementation_ref"], roles,
                ("result",), package_handler,
            ),
        )
    )
    package_recipe = _one_step_recipe(
        operation_id="numpy.gcd",
        implementation_ref=package["implementation_ref"],
        inputs=[{"name": "left", "type": "integer"}, {"name": "right", "type": "integer"}],
        bindings=[
            {"role_name": "left", "ordinal": 0, "value_ref": "input:left"},
            {"role_name": "right", "ordinal": 1, "value_ref": "input:right"},
        ],
    )
    package_receipt = execute_recipe(
        store=package_store,
        recipe=package_recipe,
        inputs={"left": 84, "right": 30},
        root_invocation_id="fixture:row35b:package",
        completed_at=COMPLETED_AT,
    )
    package_reference = math.gcd(84, 30)

    descriptor, payload = build_tensor_fixture()
    validate_tensor_fixture(descriptor, payload)
    tensor_calls = 0
    tensor_implementation_sha = _sha256_file(Path(__file__).resolve())
    tensor_implementation_ref = f"sha256:{tensor_implementation_sha}#tensor-sum-int32-v1"

    def tensor_handler(bound_descriptor: dict[str, Any], payload_hex: str):
        nonlocal tensor_calls
        tensor_calls += 1
        raw = bytes.fromhex(payload_hex)
        validate_tensor_fixture(bound_descriptor, raw)
        element_count = bound_descriptor["element_count"]
        values = struct.unpack(f"<{element_count}i", raw) if element_count else ()
        return {"result": sum(values)}

    tensor_store = LocalFixtureStore(
        (
            OperationDefinition(
                "tensor.sum.int32", "1", tensor_implementation_ref,
                (("descriptor", 0), ("payload", 1)), ("result",), tensor_handler,
            ),
        )
    )
    tensor_recipe = _one_step_recipe(
        operation_id="tensor.sum.int32",
        implementation_ref=tensor_implementation_ref,
        inputs=[{"name": "descriptor", "type": "json"}, {"name": "payload_hex", "type": "string"}],
        bindings=[
            {"role_name": "descriptor", "ordinal": 0, "value_ref": "input:descriptor"},
            {"role_name": "payload", "ordinal": 1, "value_ref": "input:payload_hex"},
        ],
    )
    tensor_receipt = execute_recipe(
        store=tensor_store,
        recipe=tensor_recipe,
        inputs={"descriptor": descriptor, "payload_hex": payload.hex()},
        root_invocation_id="fixture:row35b:tensor",
        completed_at=COMPLETED_AT,
    )
    tensor_reference = 1 + 2 + 3 + 4

    demonstrations = [
        {
            "type": "package_function",
            "operation_name": "numpy.gcd",
            "pinned_implementation_identity": package["implementation_ref"],
            "pinned_payload_identity": None,
            "reference_output": package_reference,
            "interpreter_output": package_receipt["output_values"]["result"],
            "match": package_reference == package_receipt["output_values"]["result"],
            "handler_call_count": package_calls,
            "receipt_input_commitment": package_receipt["input_commitment"],
            "receipt_schedule_digest": package_receipt["schedule_digest"],
        },
        {
            "type": "tensor_numerical",
            "operation_name": "tensor.sum.int32",
            "pinned_implementation_identity": tensor_implementation_ref,
            "pinned_payload_identity": f"sha256:{descriptor['payload_integrity']['digest']}",
            "tensor_descriptor": descriptor,
            "reference_output": tensor_reference,
            "interpreter_output": tensor_receipt["output_values"]["result"],
            "match": tensor_reference == tensor_receipt["output_values"]["result"],
            "handler_call_count": tensor_calls,
            "receipt_input_commitment": tensor_receipt["input_commitment"],
            "receipt_schedule_digest": tensor_receipt["schedule_digest"],
        },
    ]
    if not all(item["match"] for item in demonstrations):
        raise RuntimeError("demonstration_reference_mismatch")
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": COMPLETED_AT,
        "execution_scope": "local_fixture",
        "package_fixture": package,
        "demonstrations": demonstrations,
        "non_claims": [
            "no_distributed_fetch",
            "no_portable_package_identity_claim",
            "no_graph_materialization",
            "no_cdl_or_economic_authority",
        ],
    }


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_results(output_dir: Path) -> dict[str, Any]:
    results = run_demonstrations()
    encoded = json.dumps(results, sort_keys=True, indent=2, ensure_ascii=True).encode("utf-8") + b"\n"
    _atomic_write(output_dir / "demo_results.json", encoded)
    package_demo, tensor_demo = results["demonstrations"]
    summary = (
        "# Sufficiency Package And Tensor Demonstration\n\n"
        f"- NumPy fixture: {results['package_fixture']['version']} "
        f"({results['package_fixture']['license']['spdx']} verified)\n"
        f"- Package result: {package_demo['interpreter_output']} "
        f"(reference {package_demo['reference_output']})\n"
        f"- Tensor result: {tensor_demo['interpreter_output']} "
        f"(reference {tensor_demo['reference_output']})\n"
        f"- Tensor payload: {tensor_demo['pinned_payload_identity']}\n"
        "- Scope: local fixture only; generated output has graph_delta=none.\n"
    )
    _atomic_write(output_dir / "demo_summary.md", summary.encode("utf-8"))
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("out/sufficiency_package_tensor_00"),
    )
    args = parser.parse_args()
    results = write_results(args.output_dir)
    print(json.dumps({
        "demonstrations": len(results["demonstrations"]),
        "all_match": all(item["match"] for item in results["demonstrations"]),
        "output_dir": str(args.output_dir),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
