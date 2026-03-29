"""Genesis validator bootstrap admission-control runtime."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .validator_bootstrap_runtime import (
    GENESIS_BOOTSTRAP_VERSION,
    GenesisBootstrapError,
    verify_epoch_zero_state,
    verify_genesis_enrollment,
)

CDL_040_DEPENDENCY = "cdl_040_ratified_393.v0.1"
GENESIS_BOOTSTRAP_PART2_VERSION = "genesis_admission_control_bootstrap_481.v0.1"
GENESIS_BOOTSTRAP_PART1_DEPENDENCY = "genesis_validator_bootstrap_runtime_480.v0.1"


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def build_genesis_admission_control_bundle(
    enrollment_records: list[dict[str, Any]],
    epoch_zero_state: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(enrollment_records, list) or not enrollment_records:
        raise GenesisBootstrapError(
            "ADMISSION_BUNDLE_INVALID_ENROLLMENT_RECORDS",
            "enrollment_records must be a non-empty list",
        )
    normalized_records: list[dict[str, Any]] = []
    for record in enrollment_records:
        verify_genesis_enrollment(record)
        normalized_records.append(dict(record))
    normalized_records.sort(key=lambda record: record["validator_id"])
    verify_epoch_zero_state(epoch_zero_state)
    payload = {
        "enrollment_records": normalized_records,
        "epoch_zero_state": dict(epoch_zero_state),
        "admitted_validator_ids": [record["validator_id"] for record in normalized_records],
        "part1_dependency": GENESIS_BOOTSTRAP_VERSION,
    }
    return {
        **payload,
        "bundle_integrity_hash": _stable_sha256(payload),
    }


def verify_admission_control_bundle(bundle: dict[str, Any]) -> None:
    if not isinstance(bundle, dict):
        raise GenesisBootstrapError(
            "ADMISSION_BUNDLE_INVALID_STRUCTURE",
            "bundle must be a dict",
        )
    required_fields = (
        "enrollment_records",
        "epoch_zero_state",
        "admitted_validator_ids",
        "part1_dependency",
        "bundle_integrity_hash",
    )
    for field in required_fields:
        if field not in bundle:
            raise GenesisBootstrapError(
                "ADMISSION_BUNDLE_MISSING_REQUIRED_FIELD",
                f"bundle missing field: {field}",
            )
    rebuilt_bundle = build_genesis_admission_control_bundle(
        bundle["enrollment_records"],
        bundle["epoch_zero_state"],
    )
    if bundle["part1_dependency"] != GENESIS_BOOTSTRAP_VERSION:
        raise GenesisBootstrapError(
            "ADMISSION_BUNDLE_INVALID_PART1_DEPENDENCY",
            "bundle part1_dependency does not match Phase 480 runtime token",
        )
    if bundle["admitted_validator_ids"] != rebuilt_bundle["admitted_validator_ids"]:
        raise GenesisBootstrapError(
            "ADMISSION_BUNDLE_INVALID_VALIDATOR_SET",
            "bundle admitted_validator_ids do not match canonical enrollment set",
        )
    if bundle["bundle_integrity_hash"] != rebuilt_bundle["bundle_integrity_hash"]:
        raise GenesisBootstrapError(
            "ADMISSION_BUNDLE_HASH_MISMATCH",
            "bundle_integrity_hash does not match canonical bundle payload",
        )


def enforce_genesis_admission(validator_id: str, bundle: dict[str, Any] | None) -> bool:
    if bundle is None:
        raise GenesisBootstrapError(
            "ADMISSION_BUNDLE_NOT_INITIALIZED",
            "admission-control bundle must be initialized before enforcement",
        )
    verify_admission_control_bundle(bundle)
    if not isinstance(validator_id, str) or not validator_id:
        raise GenesisBootstrapError(
            "ADMISSION_BUNDLE_INVALID_VALIDATOR_ID",
            "validator_id must be a non-empty string",
        )
    return validator_id in bundle["admitted_validator_ids"]
