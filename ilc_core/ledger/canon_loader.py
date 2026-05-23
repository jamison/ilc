# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import TypedDict, cast

from ilc_core.ledger.canon_export import compute_canon_hash
from ilc_core.exceptions import CanonVerificationError


JsonObject = dict[str, object]
JsonObjectMap = dict[str, JsonObject]


class CanonVerifyMeta(TypedDict):
    canon_export_version: str | None
    epoch_count: int | None
    snapshot_count: int | None
    balance_count: int | None
    kpi_epoch_count: int | None
    kpi_snapshot_count: int | None
    kpi_balance_count: int | None


class CanonVerifyReport(TypedDict):
    ok: bool
    canon_hash: str | None
    computed_hash: str | None
    errors: list[str]
    meta: CanonVerifyMeta


@dataclass(frozen=True)
class CanonState:
    canon_export_version: str
    canon_hash: str
    generated_at: str
    epoch_records: JsonObjectMap
    stake_snapshots: JsonObjectMap
    balances: JsonObject


def _as_json_object(value: object, *, context: str) -> JsonObject:
    if not isinstance(value, dict):
        raise CanonVerificationError(
            f"Invalid type for '{context}': expected dict, got {type(value).__name__}"
        )
    return cast(JsonObject, value)


def _as_json_object_map(value: object, *, context: str) -> JsonObjectMap:
    obj = _as_json_object(value, context=context)
    return cast(JsonObjectMap, obj)


def verify_canon_hash(payload: JsonObject) -> bool:
    """
    Verify the integrity of a canon payload.

    Returns:
        True if the computed hash matches payload['canon_hash'].

    Raises:
        CanonVerificationError if 'canon_hash' is missing or verification fails.
    """
    if "canon_hash" not in payload:
        raise CanonVerificationError("Missing 'canon_hash' field in payload.")

    expected_hash = payload["canon_hash"]

    # Replicate export logic:
    # 1. Copy payload
    # 2. Remove non-hashed fields (canon_hash, generated_at)
    verify_payload = payload.copy()

    # Must remove the hash itself
    del verify_payload["canon_hash"]

    # Must remove generated_at (as per export fix)
    if "generated_at" in verify_payload:
        del verify_payload["generated_at"]

    computed_hash = compute_canon_hash(verify_payload)

    if computed_hash != expected_hash:
        raise CanonVerificationError(
            f"Hash mismatch! Expected {expected_hash}, computed {computed_hash}"
        )

    return True


def load_canon_state(path: PathLike[str]) -> JsonObject:
    """
    Load canon state from JSON file and verify integrity.

    Args:
        path: Path to canon_state.json

    Returns:
        Verified payload dict.

    Raises:
        CanonVerificationError: If verification fails.
        KeyError/ValueError: If schema is invalid.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Canon file not found: {p}")

    with p.open("r", encoding="utf-8") as f:
        try:
            payload_obj = json.load(f)
        except json.JSONDecodeError as e:
            raise CanonVerificationError(f"Invalid JSON: {e}")

    if not isinstance(payload_obj, dict):
        raise CanonVerificationError(
            f"Invalid type for 'payload': expected dict, got {type(payload_obj).__name__}"
        )
    payload = cast(JsonObject, payload_obj)

    # Basic Schema Sanity
    required_keys: dict[str, type[object]] = {
        "canon_export_version": str,
        "canon_hash": str,
        "generated_at": str,
        "epoch_records": dict,
        "stake_snapshots": dict,
        "balances": dict,
    }

    for key, expected_type in required_keys.items():
        if key not in payload:
            raise CanonVerificationError(f"Missing required key: {key}")
        if not isinstance(payload[key], expected_type):
            raise CanonVerificationError(
                f"Invalid type for '{key}': expected {expected_type.__name__}, got {type(payload[key]).__name__}"
            )

    if payload["canon_export_version"] != "v0.1":
        raise CanonVerificationError(
            f"Unsupported version: {payload.get('canon_export_version')}"
        )

    # Verify Hash
    verify_canon_hash(payload)

    return payload


def verify_canon_state(path: PathLike[str]) -> CanonVerifyReport:
    """
    Verify canon state file and return a verification report.
    Does NOT raise exceptions for verification failures (returns ok=False).

    Returns:
        Dict with keys:
            - ok (bool): True if verified
            - canon_hash (str | None): The hash found in the file, or None if parse failed
            - computed_hash (str | None): The hash re-computed, or None if parse failed
            - errors (list[str]): List of error messages (empty if verification passed)
            - meta (dict): Metadata including version and record counts
    """
    errors: list[str] = []

    # Default meta
    meta: CanonVerifyMeta = {
        "canon_export_version": None,
        "epoch_count": None,
        "snapshot_count": None,
        "balance_count": None,
        "kpi_epoch_count": None,
        "kpi_snapshot_count": None,
        "kpi_balance_count": None,
    }

    try:
        p = Path(path)
        if not p.exists():
            return {
                "ok": False,
                "canon_hash": None,
                "computed_hash": None,
                "errors": [f"File not found: {path}"],
                "meta": meta,
            }

        with p.open("r", encoding="utf-8") as f:
            try:
                payload_obj = json.load(f)
            except json.JSONDecodeError as e:
                return {
                    "ok": False,
                    "canon_hash": None,
                    "computed_hash": None,
                    "errors": [f"Invalid JSON: {e}"],
                    "meta": meta,
                }

        if not isinstance(payload_obj, dict):
            return {
                "ok": False,
                "canon_hash": None,
                "computed_hash": None,
                "errors": [
                    f"Invalid type for 'payload': expected dict, got {type(payload_obj).__name__}"
                ],
                "meta": meta,
            }
        payload = cast(JsonObject, payload_obj)

        # Extract meta early
        canon_export_version = payload.get("canon_export_version")
        meta["canon_export_version"] = (
            canon_export_version if isinstance(canon_export_version, str) else None
        )
        epoch_records = payload.get("epoch_records")
        stake_snapshots = payload.get("stake_snapshots")
        balances = payload.get("balances")
        meta["epoch_count"] = len(epoch_records) if isinstance(epoch_records, dict) else None
        meta["snapshot_count"] = (
            len(stake_snapshots) if isinstance(stake_snapshots, dict) else None
        )
        meta["balance_count"] = len(balances) if isinstance(balances, dict) else None

        # Mirror for KPIs
        meta["kpi_epoch_count"] = meta["epoch_count"]
        meta["kpi_snapshot_count"] = meta["snapshot_count"]
        meta["kpi_balance_count"] = meta["balance_count"]

        # Minimal schema checks for report
        if "canon_hash" not in payload:
            errors.append("Missing 'canon_hash' field")

        if payload.get("canon_export_version") != "v0.1":
            errors.append(f"Unsupported version: {payload.get('canon_export_version')}")

        if errors:
            canon_hash = payload.get("canon_hash")
            return {
                "ok": False,
                "canon_hash": canon_hash if isinstance(canon_hash, str) else None,
                "computed_hash": None,
                "errors": errors,
                "meta": meta,
            }

        expected_hash = payload["canon_hash"]
        expected_hash_str = expected_hash if isinstance(expected_hash, str) else None

        # Compute
        try:
            verify_payload = payload.copy()
            del verify_payload["canon_hash"]
            if "generated_at" in verify_payload:
                del verify_payload["generated_at"]

            computed_hash = compute_canon_hash(verify_payload)
        except Exception as e:
            return {
                "ok": False,
                "canon_hash": expected_hash_str,
                "computed_hash": None,
                "errors": [f"Hash computation failed: {e}"],
                "meta": meta,
            }

        if computed_hash == expected_hash:
            return {
                "ok": True,
                "canon_hash": expected_hash_str,
                "computed_hash": computed_hash,
                "errors": [],
                "meta": meta,
            }

        return {
            "ok": False,
            "canon_hash": expected_hash_str,
            "computed_hash": computed_hash,
            "errors": ["Hash mismatch"],
            "meta": meta,
        }

    except Exception as e:
        return {
            "ok": False,
            "canon_hash": None,
            "computed_hash": None,
            "errors": [str(e)],
            "meta": meta,
        }


def load_canon_state_obj(path: PathLike[str]) -> CanonState:
    """
    Load canon state and return typed wrapper.
    """
    data = load_canon_state(path)

    canon_export_version = data["canon_export_version"]
    canon_hash = data["canon_hash"]
    generated_at = data["generated_at"]

    return CanonState(
        canon_export_version=cast(str, canon_export_version),
        canon_hash=cast(str, canon_hash),
        generated_at=cast(str, generated_at),
        epoch_records=_as_json_object_map(data["epoch_records"], context="epoch_records"),
        stake_snapshots=_as_json_object_map(
            data["stake_snapshots"], context="stake_snapshots"
        ),
        balances=_as_json_object(data["balances"], context="balances"),
    )
