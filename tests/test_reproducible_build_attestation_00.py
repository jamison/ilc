# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[1] / "tools" / "verify_reproducibility_attestation.py"
SPEC = importlib.util.spec_from_file_location("verify_reproducibility_attestation", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _canonical(value: dict) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()


def _write_fixture(tmp_path: Path) -> Path:
    evidence = {
        "schema_version": "build_comparison_evidence.v0.1",
        "source_commit": "a" * 40,
        "source_date_epoch": "0",
        "commands": ["build run 1", "build run 2"],
        "python_toolchain": {
            "python": "3.14.3",
            "build": "1.5.0",
            "setuptools": "84.2.1",
            "wheel": "0.48.0",
        },
        "artifacts": {
            "ilc_core-0.4.33-py3-none-any.whl": {
                "run1_sha256": "1" * 64,
                "run2_sha256": "1" * 64,
                "run1_size": 1,
                "run2_size": 1,
                "identical": True,
            },
            "ilc_core-0.4.33.tar.gz": {
                "run1_sha256": "2" * 64,
                "run2_sha256": "3" * 64,
                "run1_size": 2,
                "run2_size": 3,
                "identical": False,
            },
        },
        "rust": {"available": False, "blocker": "rust_reproducibility_blocked_rustc_absent"},
    }
    evidence_path = tmp_path / "build.json"
    evidence_path.write_bytes(json.dumps(evidence, sort_keys=True, indent=2).encode() + b"\n")
    evidence_sha = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    pins = {
        "python_version": "3.14.3",
        "setuptools_version": "84.2.1",
        "wheel_version": "0.48.0",
        "source_date_epoch": "0",
        "rustc_version": "absent",
        "cargo_lock_sha256": "6ad2f9370d6228fd416689449d1b95eae7d856122e114c34045f33df833c378b",
    }
    components = []
    for artifact_id, (artifact_type, verdict) in MODULE.EXPECTED_COMPONENTS.items():
        artifact_sha = "absent"
        if artifact_id.endswith(".whl"):
            artifact_sha = "1" * 64
        elif artifact_id.endswith(".tar.gz"):
            artifact_sha = "2" * 64
        components.append(
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "sha256": artifact_sha,
                "reproducibility_verdict": verdict,
                "build_pins": copy.deepcopy(pins),
                "evidence_summary": "fixture evidence",
                "evidence_sha256": evidence_sha,
            }
        )
    attestation = {
        "schema_version": "reproducibility_attestation.v0.1",
        "phase": "GAP-REPRODUCIBLE-BUILD-ATTESTATION-00",
        "attested_at": "2026-10-24T12:00:00Z",
        "source_commit": "a" * 40,
        "attestation_scope": ["ilc_core-0.4.33-py3-none-any.whl"],
        "component_verdicts": components,
        "carry_forward_dispositions": {
            "reproducible_build_empirical_validation_deferred_to_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00": "blocked_rustc_absent:rust_reproducibility_blocked_rustc_absent",
            "build_reproduction_attestation_signing_profile_unresolved_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00": "emitted_unsigned_only",
            "build_reproduction_attestation_node_kind_authorization_deferred_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00": "emitted_no_node_kind_activation",
        },
        "build_evidence_path": "build.json",
        "build_evidence_sha256": evidence_sha,
        "environment": {
            "os": "test",
            "machine": "test",
            "python_implementation": "CPython",
            "independent_operator_reproduction": False,
        },
        "attestation_sha256": "pending",
    }
    attestation["attestation_sha256"] = hashlib.sha256(_canonical(attestation)).hexdigest()
    path = tmp_path / "attestation.json"
    path.write_text(json.dumps(attestation, sort_keys=True, indent=2) + "\n")
    return path


def _mutate(path: Path, mutation) -> None:
    value = json.loads(path.read_text())
    mutation(value)
    value["attestation_sha256"] = "pending"
    value["attestation_sha256"] = hashlib.sha256(_canonical(value)).hexdigest()
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def test_valid_attestation(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    MODULE.validate_attestation(path, repo_root=tmp_path)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(unknown=True),
        lambda d: d.update(attestation_scope=[]),
        lambda d: d.update(source_commit="not-a-commit"),
        lambda d: d["component_verdicts"][0].update(reproducibility_verdict="not_reproducible"),
        lambda d: d["component_verdicts"][0].update(sha256=True),
        lambda d: d["component_verdicts"][0]["build_pins"].update(source_date_epoch="1"),
        lambda d: d["environment"].update(independent_operator_reproduction=True),
        lambda d: d["carry_forward_dispositions"].pop(
            "reproducible_build_empirical_validation_deferred_to_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00"
        ),
    ],
)
def test_semantic_mutations_rejected(tmp_path: Path, mutation) -> None:
    path = _write_fixture(tmp_path)
    _mutate(path, mutation)
    with pytest.raises(MODULE.AttestationValidationError):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_duplicate_keys_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema_version":"a","schema_version":"b"}')
    with pytest.raises(MODULE.AttestationValidationError, match="duplicate_key"):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_nonfinite_number_rejected(tmp_path: Path) -> None:
    path = tmp_path / "nan.json"
    path.write_text('{"value":NaN}')
    with pytest.raises(MODULE.AttestationValidationError, match="non_finite_number"):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_invalid_utf8_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_bytes(b"\xff")
    with pytest.raises(MODULE.AttestationValidationError, match="invalid_json"):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_tampered_attestation_hash_rejected(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    value = json.loads(path.read_text())
    value["attested_at"] = "2026-10-25T12:00:00Z"
    path.write_text(json.dumps(value))
    with pytest.raises(MODULE.AttestationValidationError, match="attestation_hash_mismatch"):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_tampered_build_evidence_rejected(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    (tmp_path / "build.json").write_text("{}")
    with pytest.raises(MODULE.AttestationValidationError, match="build_evidence_hash_mismatch"):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_oversized_build_evidence_rejected_before_read(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    with (tmp_path / "build.json").open("wb") as handle:
        handle.truncate(MODULE.MAX_JSON_BYTES + 1)
    with pytest.raises(MODULE.AttestationValidationError, match="json_byte_limit_exceeded"):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_non_utc_timestamp_rejected(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    _mutate(path, lambda d: d.update(attested_at="2026-10-24T14:00:00+02:00"))
    with pytest.raises(MODULE.AttestationValidationError, match="attested_at_must_be_utc_z"):
        MODULE.validate_attestation(path, repo_root=tmp_path)


def test_unsafe_evidence_path_rejected(tmp_path: Path) -> None:
    path = _write_fixture(tmp_path)
    _mutate(path, lambda d: d.update(build_evidence_path="../build.json"))
    with pytest.raises(MODULE.AttestationValidationError, match="build_evidence_path_unsafe"):
        MODULE.validate_attestation(path, repo_root=tmp_path)
