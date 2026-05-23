# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Mapping, TypedDict

from ilc_core.protocol.ilc_cluster_a_ingest import (
    KNOWN_RECORDS_HASH_MODE_DIGEST,
    KNOWN_RECORDS_HASH_MODE_PAYLOAD,
    canonical_governance_record_digest,
)


class KnownRecordsMigrationResult(TypedDict):
    ok: bool
    errors: List[str]
    warnings: List[str]
    data: Dict[str, Any] | None


def _result(
    ok: bool,
    *,
    errors: List[str] | None = None,
    warnings: List[str] | None = None,
    data: Dict[str, Any] | None = None,
) -> KnownRecordsMigrationResult:
    return {
        "ok": ok,
        "errors": sorted(errors or []),
        "warnings": sorted(warnings or []),
        "data": data,
    }


def _normalize_records_map(records_input: Any) -> Dict[str, Dict[str, Any]]:
    if isinstance(records_input, Mapping):
        output: Dict[str, Dict[str, Any]] = {}
        for key, value in records_input.items():
            if isinstance(key, str) and isinstance(value, dict):
                output[key] = value
        return output

    if isinstance(records_input, list):
        output = {}
        for entry in records_input:
            if not isinstance(entry, dict):
                continue
            rec_id = entry.get("gov_record_id")
            if isinstance(rec_id, str):
                output[rec_id] = entry
        return output

    return {}


def migrate_known_records_payload_hash_to_record_digest(
    policy_state: Dict[str, Any],
    records_input: Any,
) -> KnownRecordsMigrationResult:
    if not isinstance(policy_state, dict):
        return _result(False, errors=["schema_violation:invalid_type:policy_state.root"])

    known_records = policy_state.get("known_records", {})
    if not isinstance(known_records, dict):
        return _result(False, errors=["schema_violation:invalid_type:policy_state.known_records"])

    mode = policy_state.get("known_records_hash_mode")
    if mode is not None and not isinstance(mode, str):
        return _result(False, errors=["schema_violation:invalid_type:policy_state.known_records_hash_mode"])

    if mode == KNOWN_RECORDS_HASH_MODE_DIGEST:
        return _result(
            True,
            warnings=["known_records_migration_noop_already_record_digest_v1"],
            data={
                "policy_state_migrated": deepcopy(policy_state),
                "migrated_count": 0,
                "known_records_hash_mode": KNOWN_RECORDS_HASH_MODE_DIGEST,
            },
        )

    if mode not in (None, KNOWN_RECORDS_HASH_MODE_PAYLOAD):
        return _result(False, errors=["context_violation:unknown_known_records_hash_mode"])

    records_map = _normalize_records_map(records_input)

    migrated_known_records: Dict[str, str] = {}
    errors: List[str] = []

    for record_id in sorted(known_records.keys()):
        if not isinstance(record_id, str):
            errors.append("schema_violation:invalid_type:known_records.key")
            continue
        record = records_map.get(record_id)
        if record is None:
            errors.append(f"context_violation:migration_missing_record:{record_id}")
            continue
        migrated_known_records[record_id] = canonical_governance_record_digest(record)

    if errors:
        return _result(False, errors=errors)

    migrated_state = deepcopy(policy_state)
    migrated_state["known_records"] = migrated_known_records
    migrated_state["known_records_hash_mode"] = KNOWN_RECORDS_HASH_MODE_DIGEST

    return _result(
        True,
        data={
            "policy_state_migrated": migrated_state,
            "migrated_count": len(migrated_known_records),
            "known_records_hash_mode": KNOWN_RECORDS_HASH_MODE_DIGEST,
        },
    )
