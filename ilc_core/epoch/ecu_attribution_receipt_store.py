# SPDX-License-Identifier: AGPL-3.0-only
"""Attribution-origin ECU receipt summaries for monthly close evidence."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from ilc_core.ledger.exact_numeric import (
    decimal_to_canonical_string,
    parse_non_negative_decimal,
)


ATTRIBUTION_RECEIPT_STORE_SCHEMA_VERSION = (
    "attribution_origin_receipt_store_GAP_ECU_ACCRUAL_EVIDENCE_SOURCE_BRIDGE_00.v0.1"
)
ATTRIBUTION_RECEIPT_STORE_FILE = "attribution_origin_receipts.json"
MAX_ATTRIBUTION_RECEIPTS = 100_000
MAX_ATTRIBUTION_RECEIPT_STORE_BYTES = 8_388_608
MICRO_ECU_PER_ECU = Decimal("1000000")
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
_ZERO = Decimal("0")


@dataclass(frozen=True, kw_only=True)
class AttributionOriginReceipt:
    """One claim-bearing attribution-origin ECU credit."""

    agent_id: str
    amount_ecu: str
    epoch: int
    receipt_ref: str

    def to_record(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "amount_ecu": self.amount_ecu,
            "epoch": self.epoch,
            "receipt_ref": self.receipt_ref,
        }


class AttributionOriginAccrualRuntime:
    """`EcuAccrualRuntime` implementation backed by attribution receipts only."""

    def __init__(self, store_path: str | Path) -> None:
        self.store_path = Path(store_path)

    def get_accrued_ecu(self, agent_id: str) -> str:
        normalized_agent_id = _require_agent_id(agent_id)
        return _cumulative_amounts(self.store_path).get(normalized_agent_id, "0")

    def list_agents_with_attribution_receipts(self) -> list[str]:
        return list_agents_with_attribution_receipts(self.store_path)

    def lmdb_state_root_sha256(self) -> str:
        return compute_attribution_receipt_state_root_sha256(self.store_path)


def record_attribution_origin_receipt(
    store_path: str | Path,
    *,
    agent_id: str,
    amount_ecu: str | int | Decimal,
    epoch: int,
    receipt_ref: str,
) -> AttributionOriginReceipt:
    """Persist a single attribution-origin receipt in the sidecar store."""

    receipt = AttributionOriginReceipt(
        agent_id=_require_agent_id(agent_id),
        amount_ecu=_canonical_amount(amount_ecu),
        epoch=_require_non_negative_int(epoch, "attribution_receipt_epoch_invalid"),
        receipt_ref=_require_receipt_ref(receipt_ref),
    )
    if parse_non_negative_decimal(receipt.amount_ecu) == _ZERO:
        raise ValueError("attribution_receipt_amount_must_be_positive")
    records = _read_receipt_records(store_path)
    records.append(receipt.to_record())
    _write_receipt_records(store_path, records)
    return receipt


def record_attribution_ingest_report(
    store_path: str | Path,
    ingest_report: Mapping[str, Any],
    *,
    batch_payload: Mapping[str, Any] | None = None,
    receipt_ref: str | None = None,
) -> list[AttributionOriginReceipt]:
    """Persist attribution-origin deltas after a successful Rust ingest report.

    The Rust bridge report's ``balances`` rows are post-apply cumulative balances,
    not per-batch deltas. Claim-bearing monthly-close receipts therefore come
    from the original attribution batch ``attributions`` rows after the Rust
    report proves the batch was accepted.
    """

    report = _require_mapping(ingest_report, "attribution_ingest_report_required")
    if report.get("marker") != "attribution_batch_ingest_ok":
        raise ValueError("attribution_ingest_report_marker_invalid")
    if report.get("dry_run") is not False:
        raise ValueError("attribution_ingest_report_dry_run_not_persisted")
    batch = _require_attribution_batch_payload(batch_payload)
    batch_attributions = batch["attributions"]
    batch_epoch = batch["epoch"]
    batch_total = sum(_require_micro_ecu(item["amount_micro_ecu"]) for item in batch_attributions)
    report_total = _require_micro_ecu(report.get("total_micro_ecu"))
    if report_total != batch_total:
        raise ValueError("attribution_ingest_report_total_mismatch")
    report_count = _require_non_negative_int(
        report.get("attribution_count"),
        "attribution_ingest_report_count_invalid",
    )
    if report_count != len(batch_attributions):
        raise ValueError("attribution_ingest_report_count_mismatch")
    balances = report.get("balances")
    if not isinstance(balances, list):
        raise ValueError("attribution_ingest_report_balances_required")
    default_ref = receipt_ref
    if default_ref is None:
        input_hash = report.get("input_sha256")
        if isinstance(input_hash, str) and _HEX_64_RE.fullmatch(input_hash):
            default_ref = f"rust_ingest_input_sha256:{input_hash}"
        else:
            raise ValueError("attribution_ingest_report_input_sha256_invalid")

    records = _read_receipt_records(store_path)
    receipts: list[AttributionOriginReceipt] = []
    for attribution in batch_attributions:
        micro_ecu = _require_micro_ecu(attribution["amount_micro_ecu"])
        if micro_ecu == 0:
            continue
        receipt = AttributionOriginReceipt(
            agent_id=_require_agent_id(attribution["agent_id_hex"]),
            amount_ecu=_micro_ecu_to_canonical_amount(micro_ecu),
            epoch=batch_epoch,
            receipt_ref=_require_receipt_ref(default_ref),
        )
        records.append(receipt.to_record())
        receipts.append(receipt)
    _write_receipt_records(store_path, records)
    return receipts


def list_agents_with_attribution_receipts(lmdb_path: str | Path) -> list[str]:
    """Return agents with nonzero cumulative attribution-origin ECU."""

    return [
        agent_id
        for agent_id, amount in sorted(_cumulative_amounts(lmdb_path).items())
        if parse_non_negative_decimal(amount) > _ZERO
    ]


def compute_attribution_receipt_state_root_sha256(lmdb_path: str | Path) -> str:
    """Hash sorted cumulative attribution-origin ECU by agent."""

    payload = {
        "cumulative_agent_ecu": _cumulative_amounts(lmdb_path),
        "schema_version": ATTRIBUTION_RECEIPT_STORE_SCHEMA_VERSION,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
            "utf-8"
        )
    ).hexdigest()


def _store_file(store_path: str | Path) -> Path:
    path = Path(store_path)
    if path.suffix == ".json":
        return path
    return path / ATTRIBUTION_RECEIPT_STORE_FILE


def _read_store_payload(store_path: str | Path) -> dict[str, Any]:
    source = _store_file(store_path)
    if not source.exists():
        return {
            "receipts": [],
            "schema_version": ATTRIBUTION_RECEIPT_STORE_SCHEMA_VERSION,
        }
    data = source.read_bytes()
    if len(data) > MAX_ATTRIBUTION_RECEIPT_STORE_BYTES:
        raise ValueError("attribution_receipt_store_exceeds_max_bytes")
    try:
        payload = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("attribution_receipt_store_json_invalid") from exc
    return _require_store_payload(payload)


def _read_receipt_records(store_path: str | Path) -> list[dict[str, Any]]:
    payload = _read_store_payload(store_path)
    receipts = payload["receipts"]
    return [dict(item) for item in receipts]


def _write_receipt_records(store_path: str | Path, records: list[dict[str, Any]]) -> None:
    if len(records) > MAX_ATTRIBUTION_RECEIPTS:
        raise ValueError("attribution_receipt_store_exceeds_max_count")
    normalized = [_require_receipt_record(item) for item in records]
    target = _store_file(store_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "receipts": normalized,
        "schema_version": ATTRIBUTION_RECEIPT_STORE_SCHEMA_VERSION,
    }
    content = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_ATTRIBUTION_RECEIPT_STORE_BYTES:
        raise ValueError("attribution_receipt_store_exceeds_max_bytes")
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
        os.replace(tmp_path, target)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _cumulative_amounts(store_path: str | Path) -> dict[str, str]:
    totals: dict[str, Decimal] = {}
    for raw_receipt in _read_receipt_records(store_path):
        receipt = _require_receipt_record(raw_receipt)
        agent_id = receipt["agent_id"]
        amount = parse_non_negative_decimal(
            receipt["amount_ecu"],
            token="attribution_receipt_amount_invalid",
        )
        totals[agent_id] = totals.get(agent_id, _ZERO) + amount
    return {
        agent_id: decimal_to_canonical_string(amount)
        for agent_id, amount in sorted(totals.items())
    }


def _require_store_payload(value: object) -> dict[str, Any]:
    payload = _require_mapping(value, "attribution_receipt_store_record_required")
    if set(payload) != {"receipts", "schema_version"}:
        raise ValueError("attribution_receipt_store_fields_invalid")
    if payload["schema_version"] != ATTRIBUTION_RECEIPT_STORE_SCHEMA_VERSION:
        raise ValueError("attribution_receipt_store_schema_version_invalid")
    receipts = payload["receipts"]
    if not isinstance(receipts, list):
        raise ValueError("attribution_receipt_store_receipts_must_be_list")
    if len(receipts) > MAX_ATTRIBUTION_RECEIPTS:
        raise ValueError("attribution_receipt_store_exceeds_max_count")
    return {
        "receipts": [_require_receipt_record(item) for item in receipts],
        "schema_version": payload["schema_version"],
    }


def _require_receipt_record(value: object) -> dict[str, Any]:
    record = _require_mapping(value, "attribution_receipt_record_required")
    if set(record) != {"agent_id", "amount_ecu", "epoch", "receipt_ref"}:
        raise ValueError("attribution_receipt_record_fields_invalid")
    return {
        "agent_id": _require_agent_id(record["agent_id"]),
        "amount_ecu": _canonical_amount(record["amount_ecu"]),
        "epoch": _require_non_negative_int(
            record["epoch"],
            "attribution_receipt_epoch_invalid",
        ),
        "receipt_ref": _require_receipt_ref(record["receipt_ref"]),
    }


def _require_attribution_batch_payload(value: object) -> dict[str, Any]:
    batch = _require_mapping(value, "attribution_batch_payload_required")
    if batch.get("marker") != "attribution_batch_bridge_ok":
        raise ValueError("attribution_batch_payload_marker_invalid")
    attributions = batch.get("attributions")
    if not isinstance(attributions, list):
        raise ValueError("attribution_batch_payload_attributions_required")
    normalized_attributions: list[dict[str, int | str]] = []
    for raw_attribution in attributions:
        attribution = _require_mapping(raw_attribution, "attribution_batch_entry_required")
        normalized_attributions.append(
            {
                "agent_id_hex": _require_agent_id(attribution.get("agent_id_hex")),
                "amount_micro_ecu": _require_micro_ecu(attribution.get("amount_micro_ecu")),
            }
        )
    return {
        "attributions": normalized_attributions,
        "epoch": _require_non_negative_int(
            batch.get("epoch"),
            "attribution_batch_epoch_invalid",
        ),
    }


def _require_mapping(value: object, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(token)
    return value


def _require_agent_id(value: object) -> str:
    if not isinstance(value, str) or _AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError("attribution_receipt_agent_id_must_be_96_hex")
    return value


def _require_receipt_ref(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("attribution_receipt_ref_required")
    if len(value.encode("utf-8")) > 512:
        raise ValueError("attribution_receipt_ref_exceeds_max_bytes")
    return value


def _canonical_amount(value: object) -> str:
    if isinstance(value, float):
        raise ValueError("attribution_receipt_amount_must_be_exact_decimal")
    amount = parse_non_negative_decimal(
        value,  # type: ignore[arg-type]
        token="attribution_receipt_amount_must_be_non_negative_decimal",
    )
    canonical = decimal_to_canonical_string(amount)
    if value != canonical and isinstance(value, str):
        raise ValueError("attribution_receipt_amount_must_be_canonical_decimal_string")
    if isinstance(value, Decimal) and str(value) != canonical:
        raise ValueError("attribution_receipt_amount_must_be_canonical_decimal")
    return canonical


def _require_micro_ecu(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("attribution_ingest_amount_micro_ecu_invalid")
    return value


def _micro_ecu_to_canonical_amount(value: int) -> str:
    return decimal_to_canonical_string(Decimal(value) / MICRO_ECU_PER_ECU)


def _require_non_negative_int(value: object, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("attribution_receipt_store_duplicate_json_key")
        record[key] = value
    return record


__all__ = [
    "ATTRIBUTION_RECEIPT_STORE_FILE",
    "ATTRIBUTION_RECEIPT_STORE_SCHEMA_VERSION",
    "AttributionOriginAccrualRuntime",
    "AttributionOriginReceipt",
    "compute_attribution_receipt_state_root_sha256",
    "list_agents_with_attribution_receipts",
    "record_attribution_ingest_report",
    "record_attribution_origin_receipt",
]
