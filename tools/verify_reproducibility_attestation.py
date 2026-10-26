#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Verify the bounded GAP-REPRODUCIBLE-BUILD-ATTESTATION-00 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_DEPTH = 12
MAX_NODES = 10_000
MAX_STRING = 8_192
MAX_LIST = 128
MAX_INT = (1 << 53) - 1
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
HEX_40 = re.compile(r"^[0-9a-f]{40}$")

ROOT_FIELDS = {
    "schema_version",
    "phase",
    "attested_at",
    "source_commit",
    "attestation_scope",
    "component_verdicts",
    "carry_forward_dispositions",
    "build_evidence_path",
    "build_evidence_sha256",
    "environment",
    "attestation_sha256",
}
COMPONENT_FIELDS = {
    "artifact_id",
    "artifact_type",
    "sha256",
    "reproducibility_verdict",
    "build_pins",
    "evidence_summary",
    "evidence_sha256",
}
PIN_FIELDS = {
    "python_version",
    "setuptools_version",
    "wheel_version",
    "source_date_epoch",
    "rustc_version",
    "cargo_lock_sha256",
}
EXPECTED_PINS = {
    "python_version": "3.14.3",
    "setuptools_version": "84.2.1",
    "wheel_version": "0.48.0",
    "source_date_epoch": "0",
    "rustc_version": "absent",
    "cargo_lock_sha256": "6ad2f9370d6228fd416689449d1b95eae7d856122e114c34045f33df833c378b",
}
EXPECTED_PYTHON_TOOLCHAIN = {
    "python": "3.14.3",
    "build": "1.5.0",
    "setuptools": "84.2.1",
    "wheel": "0.48.0",
}
EXPECTED_COMPONENTS = {
    "ilc_core-0.4.33-py3-none-any.whl": ("wheel", "reproducible_with_pinning"),
    "ilc_core-0.4.33.tar.gz": ("sdist", "not_reproducible"),
    "libilc_consensus.rlib": ("rust_library", "blocked_toolchain_absent"),
    "ilc_native_submit_receiver_full": ("rust_binary", "blocked_toolchain_absent"),
    "ilc_native_submit_client": ("rust_binary", "blocked_toolchain_absent"),
    "attribution_batch_ingest": ("rust_binary", "blocked_toolchain_absent"),
}
BUILD_EVIDENCE_FIELDS = {
    "schema_version",
    "source_commit",
    "source_date_epoch",
    "commands",
    "python_toolchain",
    "artifacts",
    "rust",
}


class AttestationValidationError(ValueError):
    """Raised when an attestation or its evidence violates the phase contract."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AttestationValidationError(f"duplicate_key:{key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise AttestationValidationError(f"non_finite_number:{value}")


def _bounded_walk(value: Any, *, depth: int = 0, count: list[int] | None = None) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    if count[0] > MAX_NODES:
        raise AttestationValidationError("json_node_limit_exceeded")
    if depth > MAX_DEPTH:
        raise AttestationValidationError("json_depth_limit_exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_INT:
            raise AttestationValidationError("integer_out_of_range")
        return
    if type(value) is float:
        raise AttestationValidationError("floats_not_permitted")
    if type(value) is str:
        if len(value) > MAX_STRING:
            raise AttestationValidationError("string_limit_exceeded")
        return
    if type(value) is list:
        if len(value) > MAX_LIST:
            raise AttestationValidationError("list_limit_exceeded")
        for item in value:
            _bounded_walk(item, depth=depth + 1, count=count)
        return
    if type(value) is dict:
        if len(value) > MAX_LIST:
            raise AttestationValidationError("mapping_limit_exceeded")
        for key, item in value.items():
            if type(key) is not str:
                raise AttestationValidationError("non_string_key")
            _bounded_walk(key, depth=depth + 1, count=count)
            _bounded_walk(item, depth=depth + 1, count=count)
        return
    raise AttestationValidationError(f"unsupported_json_type:{type(value).__name__}")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise AttestationValidationError(f"unreadable_json:{exc}") from exc
    if size > MAX_JSON_BYTES:
        raise AttestationValidationError("json_byte_limit_exceeded")
    try:
        raw = path.read_bytes().decode("utf-8", errors="strict")
        value = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AttestationValidationError(f"invalid_json:{exc}") from exc
    _bounded_walk(value)
    if type(value) is not dict:
        raise AttestationValidationError("root_must_be_object")
    return value


def _require_fields(value: dict[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise AttestationValidationError(
            f"{context}_fields:missing={sorted(expected-actual)}:unknown={sorted(actual-expected)}"
        )


def _require_string(value: Any, context: str, *, nonempty: bool = True) -> str:
    if type(value) is not str or (nonempty and not value):
        raise AttestationValidationError(f"{context}_must_be_string")
    return value


def _require_sha256(value: Any, context: str) -> str:
    text = _require_string(value, context)
    if HEX_64.fullmatch(text) is None:
        raise AttestationValidationError(f"{context}_must_be_sha256")
    return text


def _canonical_sha256(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _bounded_file_sha256(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise AttestationValidationError(f"unreadable_evidence:{exc}") from exc
    if size > MAX_JSON_BYTES:
        raise AttestationValidationError("json_byte_limit_exceeded")
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(64 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise AttestationValidationError(f"unreadable_evidence:{exc}") from exc
    return digest.hexdigest()


def _validate_build_evidence(evidence: dict[str, Any], source_commit: str) -> None:
    _require_fields(evidence, BUILD_EVIDENCE_FIELDS, "build_evidence")
    if evidence["schema_version"] != "build_comparison_evidence.v0.1":
        raise AttestationValidationError("unsupported_build_evidence_schema")
    if evidence["source_commit"] != source_commit:
        raise AttestationValidationError("build_evidence_source_commit_mismatch")
    if evidence["source_date_epoch"] != "0":
        raise AttestationValidationError("source_date_epoch_mismatch")
    commands = evidence["commands"]
    if type(commands) is not list or len(commands) != 2 or not all(type(x) is str and x for x in commands):
        raise AttestationValidationError("build_commands_invalid")
    if evidence["python_toolchain"] != EXPECTED_PYTHON_TOOLCHAIN:
        raise AttestationValidationError("python_toolchain_invalid")
    artifacts = evidence["artifacts"]
    if type(artifacts) is not dict or set(artifacts) != {
        "ilc_core-0.4.33-py3-none-any.whl",
        "ilc_core-0.4.33.tar.gz",
    }:
        raise AttestationValidationError("build_artifact_set_invalid")
    for artifact_id, record in artifacts.items():
        if type(record) is not dict or set(record) != {
            "run1_sha256", "run2_sha256", "run1_size", "run2_size", "identical"
        }:
            raise AttestationValidationError(f"build_artifact_record_invalid:{artifact_id}")
        _require_sha256(record["run1_sha256"], f"{artifact_id}.run1_sha256")
        _require_sha256(record["run2_sha256"], f"{artifact_id}.run2_sha256")
        if type(record["run1_size"]) is not int or record["run1_size"] <= 0:
            raise AttestationValidationError(f"build_artifact_size_invalid:{artifact_id}:run1")
        if type(record["run2_size"]) is not int or record["run2_size"] <= 0:
            raise AttestationValidationError(f"build_artifact_size_invalid:{artifact_id}:run2")
        if type(record["identical"]) is not bool:
            raise AttestationValidationError(f"build_artifact_identity_invalid:{artifact_id}")
    if artifacts["ilc_core-0.4.33-py3-none-any.whl"]["identical"] is not True:
        raise AttestationValidationError("wheel_not_identical")
    if artifacts["ilc_core-0.4.33.tar.gz"]["identical"] is not False:
        raise AttestationValidationError("sdist_boundary_not_demonstrated")
    rust = evidence["rust"]
    if rust != {"available": False, "blocker": "rust_reproducibility_blocked_rustc_absent"}:
        raise AttestationValidationError("rust_blocker_invalid")


def validate_attestation(path: Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    root = _load_json(path)
    _require_fields(root, ROOT_FIELDS, "attestation")
    if root["schema_version"] != "reproducibility_attestation.v0.1":
        raise AttestationValidationError("unsupported_attestation_schema")
    if root["phase"] != "GAP-REPRODUCIBLE-BUILD-ATTESTATION-00":
        raise AttestationValidationError("phase_mismatch")
    timestamp = _require_string(root["attested_at"], "attested_at")
    if not timestamp.endswith("Z"):
        raise AttestationValidationError("attested_at_must_be_utc_z")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AttestationValidationError("attested_at_invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AttestationValidationError("attested_at_must_be_timezone_aware")
    source_commit = _require_string(root["source_commit"], "source_commit")
    if HEX_40.fullmatch(source_commit) is None:
        raise AttestationValidationError("source_commit_invalid")
    scope = root["attestation_scope"]
    if type(scope) is not list or scope != ["ilc_core-0.4.33-py3-none-any.whl"]:
        raise AttestationValidationError("attestation_scope_invalid")
    components = root["component_verdicts"]
    if type(components) is not list or len(components) != len(EXPECTED_COMPONENTS):
        raise AttestationValidationError("component_count_invalid")
    by_id: dict[str, dict[str, Any]] = {}
    for component in components:
        if type(component) is not dict:
            raise AttestationValidationError("component_must_be_object")
        _require_fields(component, COMPONENT_FIELDS, "component")
        artifact_id = _require_string(component["artifact_id"], "artifact_id")
        if artifact_id in by_id:
            raise AttestationValidationError(f"duplicate_artifact_id:{artifact_id}")
        by_id[artifact_id] = component
        if artifact_id not in EXPECTED_COMPONENTS:
            raise AttestationValidationError(f"unexpected_artifact_id:{artifact_id}")
        expected_type, expected_verdict = EXPECTED_COMPONENTS[artifact_id]
        if component["artifact_type"] != expected_type:
            raise AttestationValidationError(f"artifact_type_mismatch:{artifact_id}")
        if component["reproducibility_verdict"] != expected_verdict:
            raise AttestationValidationError(f"verdict_mismatch:{artifact_id}")
        sha = _require_string(component["sha256"], f"sha256:{artifact_id}")
        if expected_verdict == "blocked_toolchain_absent":
            if sha != "absent":
                raise AttestationValidationError(f"blocked_artifact_hash_present:{artifact_id}")
        else:
            _require_sha256(sha, f"sha256:{artifact_id}")
        pins = component["build_pins"]
        if type(pins) is not dict:
            raise AttestationValidationError(f"build_pins_invalid:{artifact_id}")
        _require_fields(pins, PIN_FIELDS, "build_pins")
        for key, value in pins.items():
            _require_string(value, f"build_pins.{key}:{artifact_id}")
        if pins != EXPECTED_PINS:
            raise AttestationValidationError(f"build_pins_mismatch:{artifact_id}")
        _require_string(component["evidence_summary"], f"evidence_summary:{artifact_id}")
        _require_sha256(component["evidence_sha256"], f"evidence_sha256:{artifact_id}")
    if set(by_id) != set(EXPECTED_COMPONENTS):
        raise AttestationValidationError("component_set_invalid")

    dispositions = root["carry_forward_dispositions"]
    if type(dispositions) is not dict or dispositions.get(
        "reproducible_build_empirical_validation_deferred_to_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00"
    ) != "blocked_rustc_absent:rust_reproducibility_blocked_rustc_absent":
        raise AttestationValidationError("rust_carry_forward_not_consumed")
    expected_disposition_keys = {
        "reproducible_build_empirical_validation_deferred_to_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00",
        "build_reproduction_attestation_signing_profile_unresolved_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00",
        "build_reproduction_attestation_node_kind_authorization_deferred_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00",
    }
    if set(dispositions) != expected_disposition_keys:
        raise AttestationValidationError("carry_forward_disposition_set_invalid")

    evidence_path_text = _require_string(root["build_evidence_path"], "build_evidence_path")
    evidence_path = Path(evidence_path_text)
    if evidence_path.is_absolute() or ".." in evidence_path.parts:
        raise AttestationValidationError("build_evidence_path_unsafe")
    base = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    resolved = (base / evidence_path).resolve()
    if not resolved.is_relative_to(base):
        raise AttestationValidationError("build_evidence_path_escape")
    evidence_sha = _bounded_file_sha256(resolved)
    if evidence_sha != _require_sha256(root["build_evidence_sha256"], "build_evidence_sha256"):
        raise AttestationValidationError("build_evidence_hash_mismatch")
    evidence = _load_json(resolved)
    _validate_build_evidence(evidence, source_commit)
    for artifact_id, component in by_id.items():
        if component["evidence_sha256"] != evidence_sha:
            raise AttestationValidationError(f"component_evidence_hash_mismatch:{artifact_id}")
    for artifact_id in ("ilc_core-0.4.33-py3-none-any.whl", "ilc_core-0.4.33.tar.gz"):
        if component_sha := by_id[artifact_id]["sha256"]:
            if component_sha != evidence["artifacts"][artifact_id]["run1_sha256"]:
                raise AttestationValidationError(f"component_artifact_hash_mismatch:{artifact_id}")

    environment = root["environment"]
    if type(environment) is not dict or set(environment) != {
        "os", "machine", "python_implementation", "independent_operator_reproduction"
    }:
        raise AttestationValidationError("environment_invalid")
    if environment["independent_operator_reproduction"] is not False:
        raise AttestationValidationError("independent_reproduction_overclaim")

    stored_hash = _require_sha256(root["attestation_sha256"], "attestation_sha256")
    pending = dict(root)
    pending["attestation_sha256"] = "pending"
    if stored_hash != _canonical_sha256(pending):
        raise AttestationValidationError("attestation_hash_mismatch")
    return root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attestation", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate_attestation(args.attestation, repo_root=args.repo_root)
    except (AttestationValidationError, OSError) as exc:
        print(f"attestation_schema_invalid:{exc}")
        return 1
    print("attestation_schema_valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
