from __future__ import annotations
import math
from decimal import Decimal
from datetime import datetime, timezone
from typing import TypeAlias, TypedDict

from ilc_core.exceptions import LedgerExportContractError
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, exact_to_canonical_string


JsonScalar: TypeAlias = str | int | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class CanonExportMeta(TypedDict):
    canon_export_version: JsonValue
    epoch_count: int
    snapshot_count: int
    balance_count: int


class CanonExportKpis(TypedDict):
    epoch_count: int
    snapshot_count: int
    balance_count: int


class CanonExportFormatV01(TypedDict, total=False):
    canon_export_format: str
    canon_hash: JsonValue
    exported_at: str
    meta: CanonExportMeta
    epochs: list[JsonValue]
    snapshots: list[JsonValue]
    kpis: CanonExportKpis
    computed_hash: JsonValue


def _normalize_export_value(value: object) -> JsonValue:
    if isinstance(value, bool) or value is None or isinstance(value, str) or isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        return decimal_to_canonical_string(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise LedgerExportContractError("non_finite_numeric_scalar_in_canon_export")
        return exact_to_canonical_string(
            value,
            token="invalid_numeric_scalar_in_canon_export",
        )
    if isinstance(value, dict):
        return {
            str(key): _normalize_export_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_normalize_export_value(item) for item in value]
    raise LedgerExportContractError("unsupported_scalar_in_canon_export")


def export_canon_format_v0_1(
    canon_state: dict[str, JsonValue], exported_at: str | None = None
) -> CanonExportFormatV01:
    """
    Transform a raw canon_state dict into the standardized v0.1 export format.

    Args:
        canon_state: The raw canon state dictionary. Must contain 'canon_hash' and 'canon_export_version'.
                     Optional keys 'epochs' (list), 'snapshots' (list), 'balances' (dict) are used if present.
        exported_at: Optional ISO-8601 timestamp string. If None, current UTC time is used.

    Returns:
        Dict conforming to the canon_export_format_v0.1 schema.

    Raises:
        LedgerExportContractError: If required keys are missing or types are incorrect.
    """
    if "canon_hash" not in canon_state or "canon_export_version" not in canon_state:
        raise LedgerExportContractError("canon_state missing required keys: 'canon_hash' and 'canon_export_version' are mandatory")

    exported_at = exported_at or datetime.now(timezone.utc).isoformat()

    # Extract core data with defaults
    epochs_raw = canon_state.get("epochs", [])
    snapshots_raw = canon_state.get("snapshots", [])
    balances_raw = canon_state.get("balances", {})

    # Validate types minimally to ensure schema compliance
    if not isinstance(epochs_raw, list):
        raise LedgerExportContractError("Field 'epochs' must be a list")
    if not isinstance(snapshots_raw, list):
        raise LedgerExportContractError("Field 'snapshots' must be a list")
    if not isinstance(balances_raw, dict):
        raise LedgerExportContractError("Field 'balances' must be a dict")
    
    epochs = _normalize_export_value(epochs_raw)
    snapshots = _normalize_export_value(snapshots_raw)
    balances = _normalize_export_value(balances_raw)
    if not isinstance(epochs, list):
        raise LedgerExportContractError("epochs must normalize to a list")
    if not isinstance(snapshots, list):
        raise LedgerExportContractError("snapshots must normalize to a list")
    if not isinstance(balances, dict):
        raise LedgerExportContractError("balances must normalize to a dict")

    # Construct Metadata
    meta: CanonExportMeta = {
        "canon_export_version": _normalize_export_value(canon_state.get("canon_export_version")),
        "epoch_count": len(epochs),
        "snapshot_count": len(snapshots),
        "balance_count": len(balances),
    }

    # Construct Payload
    payload: CanonExportFormatV01 = {
        "canon_export_format": "v0.1",
        "canon_hash": _normalize_export_value(canon_state.get("canon_hash")),
        "exported_at": exported_at,
        "meta": meta,
        "epochs": epochs,
        "snapshots": snapshots,
        "kpis": {
            "epoch_count": meta["epoch_count"],
            "snapshot_count": meta["snapshot_count"],
            "balance_count": meta["balance_count"],
        },
    }

    computed_hash = canon_state.get("computed_hash")
    if computed_hash is not None:
        payload["computed_hash"] = _normalize_export_value(computed_hash)

    return payload
