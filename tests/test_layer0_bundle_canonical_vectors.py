from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from ilc_core.bundle.layer0_protocol_bundle import (
    MAX_SCHEMA_COUNT,
    generate_layer0_protocol_bundle,
    verify_layer0_protocol_bundle,
)
from ilc_core.encoding.cidv1 import node_id_from_bytes


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_BUNDLE_ID = "phase-1573ao-canonical-layer0"
CANONICAL_VERSION = "1573ao.v1"
CANONICAL_SCHEMAS = [
    {
        "schema_kind": "fixture",
        "schema_version": "1573ao.v1",
        "type_name": "fixture.layer0.canonical",
    }
]
CANONICAL_PARAMETERS = {"network": "fixture", "phase": "1573ao"}

# Canonical test vector SHA-256 values - Phase 1573ao.
# If these change, the change is intentional and requires explicit update.
CANONICAL_SHA256 = {
    "without_truth_primitives": "268a64fa5c7c4e3eeef96e96c5fffea5a19bc327238c3a15934257c1c6a7b6b5",
    "with_truth_primitives": "f8d7da0c0bf40cadf0573f59615ea2767f96006a545c9688b30efbc6ede66609",
}


def _bundle(*, include_truth_primitives: bool = False):
    return generate_layer0_protocol_bundle(
        bundle_id=CANONICAL_BUNDLE_ID,
        version=CANONICAL_VERSION,
        schemas=CANONICAL_SCHEMAS,
        parameters=CANONICAL_PARAMETERS,
        include_truth_primitive_schemas=include_truth_primitives,
    )


def test_layer0_bundle_dag_cbor_sha256_stable() -> None:
    first = _bundle()
    second = _bundle()
    assert first.sha256 == second.sha256
    assert first.sha256 == CANONICAL_SHA256["without_truth_primitives"]


def test_layer0_bundle_cidv1_deterministic() -> None:
    first = _bundle()
    second = _bundle()
    assert first.cidv1 == second.cidv1


def test_layer0_bundle_canonical_json_stable() -> None:
    first = _bundle()
    second = _bundle()
    assert first.canonical_json == second.canonical_json
    assert json.loads(first.canonical_json)["bundle_id"] == CANONICAL_BUNDLE_ID


def test_layer0_bundle_with_truth_primitives_sha256_stable() -> None:
    bundle = _bundle(include_truth_primitives=True)
    assert bundle.sha256 == CANONICAL_SHA256["with_truth_primitives"]


def test_layer0_bundle_invalid_id_raises() -> None:
    try:
        generate_layer0_protocol_bundle(
            bundle_id="",
            version=CANONICAL_VERSION,
            schemas=CANONICAL_SCHEMAS,
            parameters=CANONICAL_PARAMETERS,
        )
    except ValueError as exc:
        assert str(exc) == "layer0_bundle_missing_identifier"
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")


def test_layer0_bundle_schema_count_limit() -> None:
    schemas = [
        {
            "schema_kind": "fixture",
            "schema_version": "1573ao.v1",
            "type_name": f"fixture.layer0.{index}",
        }
        for index in range(MAX_SCHEMA_COUNT + 1)
    ]
    try:
        generate_layer0_protocol_bundle(
            bundle_id=CANONICAL_BUNDLE_ID,
            version=CANONICAL_VERSION,
            schemas=schemas,
            parameters=CANONICAL_PARAMETERS,
        )
    except ValueError as exc:
        assert str(exc) == "layer0_bundle_invalid_schema_count"
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")


def test_layer0_bundle_float_rejected() -> None:
    try:
        generate_layer0_protocol_bundle(
            bundle_id=CANONICAL_BUNDLE_ID,
            version=CANONICAL_VERSION,
            schemas=[
                {
                    "schema_kind": "fixture",
                    "schema_version": "1573ao.v1",
                    "type_name": "fixture.layer0.float",
                    "bad_float": 1.25,
                }
            ],
            parameters=CANONICAL_PARAMETERS,
        )
    except ValueError as exc:
        assert "layer0_protocol_bundle_float_not_allowed" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")


def test_layer0_bundle_sha256_matches_dag_cbor() -> None:
    bundle = _bundle()
    assert hashlib.sha256(bundle.dag_cbor).hexdigest() == bundle.sha256


def test_layer0_bundle_public_rc_exclude_is_true() -> None:
    assert _bundle().public_rc_exclude is True


def test_layer0_bundle_hb002_compat_cidv1_from_dag_cbor() -> None:
    bundle = _bundle()
    assert node_id_from_bytes(bundle.dag_cbor) == bundle.cidv1


def test_layer0_bundle_roundtrip_via_verify() -> None:
    assert verify_layer0_protocol_bundle(_bundle()) is True


def test_cli_generate_layer0_stdout(tmp_path: Path) -> None:
    schemas = tmp_path / "schemas.json"
    parameters = tmp_path / "parameters.json"
    schemas.write_text(json.dumps(CANONICAL_SCHEMAS, sort_keys=True), encoding="utf-8")
    parameters.write_text(json.dumps(CANONICAL_PARAMETERS, sort_keys=True), encoding="utf-8")
    result = subprocess.run(
        [
            str(ROOT / ".venv/bin/python"),
            "-m",
            "ilc_core.cli.main",
            "bundle",
            "generate-layer0",
            "--bundle-id",
            CANONICAL_BUNDLE_ID,
            "--version",
            CANONICAL_VERSION,
            "--schemas",
            str(schemas),
            "--parameters",
            str(parameters),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["sha256"] == CANONICAL_SHA256["without_truth_primitives"]
    assert payload["data"]["output_written"] is False


def test_cli_generate_layer0_output_file_atomic_result(tmp_path: Path) -> None:
    schemas = tmp_path / "schemas.json"
    parameters = tmp_path / "parameters.json"
    output = tmp_path / "bundle.json"
    schemas.write_text(json.dumps(CANONICAL_SCHEMAS, sort_keys=True), encoding="utf-8")
    parameters.write_text(json.dumps(CANONICAL_PARAMETERS, sort_keys=True), encoding="utf-8")
    result = subprocess.run(
        [
            str(ROOT / ".venv/bin/python"),
            "-m",
            "ilc_core.cli.main",
            "bundle",
            "generate-layer0",
            "--bundle-id",
            CANONICAL_BUNDLE_ID,
            "--version",
            CANONICAL_VERSION,
            "--schemas",
            str(schemas),
            "--parameters",
            str(parameters),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    written = json.loads(output.read_text(encoding="utf-8"))
    assert payload["data"]["output_written"] is True
    assert payload["data"]["output_path"] == str(output)
    assert written["sha256"] == CANONICAL_SHA256["without_truth_primitives"]
    assert written["public_rc_exclude"] is True
