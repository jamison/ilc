# SPDX-License-Identifier: AGPL-3.0-only
"""Distributed CDL-048 conversion read-model schema.

Phase 1568-Fix2r defines schema/read-model records only. These records make
Genesis-tranche treatment and CDL-057 witness status explicit without activating
wallet, treasury, minting, or settlement authority.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
import hashlib
import json
from typing import Any

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string, parse_non_negative_decimal


DISTRIBUTED_CONVERSION_SCHEMA_VERSION = "distributed_conversion_schema_1568_fix2r.v0.1"
CDL057_WITNESS_ABSENT_TOKEN = "cdl057_witness_absent_fix2r"
GENESIS_TRANCHE_EXPLICITLY_DEFERRED = "explicitly_deferred"
GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH = "applied_by_authorized_value_path"
GENESIS_TRANCHE_NOT_APPLICABLE_BY_RATIFIED_RULE = "not_applicable_by_ratified_rule"
CDL029_GENESIS_OVERHEAD_POOL_LABEL = "genesis_overhead_pool"
GENESIS_TRANCHE_ALLOWED_TREATMENTS = frozenset(
    {
        GENESIS_TRANCHE_EXPLICITLY_DEFERRED,
        GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH,
        GENESIS_TRANCHE_NOT_APPLICABLE_BY_RATIFIED_RULE,
    }
)
RESOLUTION_STATUSES = frozenset({"resolved", "omitted", "pending"})
VERIFIER_ROOT_PREFIX = "conversion_resolution_sha256:"
FIX2R_SCHEMA_COMPLETE_TOKEN = "phase_1568_fix2r_distributed_conversion_schema_complete"
FIX2R_CDL057_WITNESS_TOKEN = "phase_1568_fix2r_cdl057_witness_reference_wired"
FIX2R_GENESIS_TRANCHE_FIELD_TOKEN = (
    "phase_1568_fix2r_genesis_tranche_field_required_in_schema"
)
FIX2R_EXPLICIT_DEFERRED_TOKEN = (
    "phase_1568_fix2r_genesis_tranche_treatment_explicitly_deferred_in_rehearsal"
)
FIX2R_CDL029_NOT_TRANCHE_TOKEN = (
    "phase_1568_fix2r_cdl029_overhead_pool_not_fixed_tranche_confirmed"
)
FIX2R_NO_WRITE_TOKEN = "phase_1568_fix2r_no_write_flag_activated"
FIX2R_PUBLIC_BLOCKED_TOKEN = "public_path_remains_blocked_phase_1568_fix2r"

_FORBIDDEN_AUTHORIZATION_FIELDS = frozenset(
    {
        "conversion_activation_authorized",
        "ledger_write_authorized",
        "wallet_write_authorized",
        "treasury_write_authorized",
        "production_minting_authorized",
        "ecu_mint_authorized",
        "ilc_settlement_authorized",
        "public_claimability_activated",
        "wallet_withdrawal_enabled",
        "wallet_transfer_enabled",
        "wallet_spend_enabled",
    }
)


def _reject_float_tree(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("distributed_conversion_float_rejected")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float_tree(key)
            _reject_float_tree(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_float_tree(item)


def _require_text(value: Any, *, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value.strip()


def _require_epoch(value: Any, *, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_amount(value: Any, *, token: str) -> Decimal:
    if isinstance(value, float):
        raise ValueError(token)
    try:
        amount = parse_non_negative_decimal(value, token=token)
    except ValueError as exc:
        raise ValueError(token) from exc
    if not amount.is_finite():
        raise ValueError(token)
    return amount


def _require_treatment(value: Any) -> str:
    treatment = _require_text(value, token="genesis_tranche_treatment_required")
    if treatment not in GENESIS_TRANCHE_ALLOWED_TREATMENTS:
        raise ValueError("genesis_tranche_treatment_invalid")
    return treatment


def _require_witness_ref(value: Any) -> str:
    witness_ref = _require_text(value, token="cdl057_witness_ref_required")
    return witness_ref


def _require_resolution_status(value: Any) -> str:
    status = _require_text(value, token="conversion_resolution_status_required")
    if status not in RESOLUTION_STATUSES:
        raise ValueError("conversion_resolution_status_invalid")
    return status


def _normalize_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_to_canonical_string(value)
    if isinstance(value, dict):
        return {str(key): _normalize_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_json(item) for item in value]
    return value


def _stable_json_bytes(payload: Any) -> bytes:
    normalized = _normalize_json(payload)
    _reject_float_tree(normalized)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    ).encode("utf-8")


def _sha256_payload(payload: Any) -> str:
    return hashlib.sha256(_stable_json_bytes(payload)).hexdigest()


def _assert_no_authorized_write_flags(record: dict[str, Any]) -> None:
    for field in _FORBIDDEN_AUTHORIZATION_FIELDS:
        if record.get(field) is True:
            raise ValueError(f"{field}_forbidden_phase_1568_fix2r")


def validate_genesis_tranche_treatment_source(
    *,
    genesis_tranche_treatment: str,
    source_label: str,
) -> str:
    treatment = _require_treatment(genesis_tranche_treatment)
    source = _require_text(source_label, token="genesis_tranche_source_label_required")
    if (
        treatment == GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH
        and source == CDL029_GENESIS_OVERHEAD_POOL_LABEL
    ):
        raise ValueError(
            "cdl029_overhead_pool_cannot_satisfy_fixed_genesis_tranche"
        )
    return treatment


@dataclass(frozen=True)
class ConversionCandidate:
    lot_id: str
    agent_id: str
    amount_ecu: Decimal
    issue_epoch: int
    deadline_epoch: int
    conversion_epoch: int
    genesis_tranche_treatment: str
    cdl057_witness_ref: str
    candidate_source: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "lot_id", _require_text(self.lot_id, token="lot_id_required"))
        object.__setattr__(
            self,
            "agent_id",
            _require_text(self.agent_id, token="agent_id_required"),
        )
        object.__setattr__(
            self,
            "amount_ecu",
            _require_amount(self.amount_ecu, token="amount_ecu_invalid"),
        )
        object.__setattr__(
            self,
            "issue_epoch",
            _require_epoch(self.issue_epoch, token="issue_epoch_invalid"),
        )
        object.__setattr__(
            self,
            "deadline_epoch",
            _require_epoch(self.deadline_epoch, token="deadline_epoch_invalid"),
        )
        object.__setattr__(
            self,
            "conversion_epoch",
            _require_epoch(self.conversion_epoch, token="conversion_epoch_invalid"),
        )
        if self.deadline_epoch < self.issue_epoch:
            raise ValueError("deadline_epoch_precedes_issue_epoch")
        if self.conversion_epoch < self.issue_epoch:
            raise ValueError("conversion_epoch_precedes_issue_epoch")
        object.__setattr__(
            self,
            "genesis_tranche_treatment",
            _require_treatment(self.genesis_tranche_treatment),
        )
        object.__setattr__(
            self,
            "cdl057_witness_ref",
            _require_witness_ref(self.cdl057_witness_ref),
        )
        object.__setattr__(
            self,
            "candidate_source",
            _require_text(self.candidate_source, token="candidate_source_required"),
        )

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "amount_ecu": decimal_to_canonical_string(self.amount_ecu),
            "candidate_source": self.candidate_source,
            "cdl057_witness_ref": self.cdl057_witness_ref,
            "conversion_epoch": self.conversion_epoch,
            "deadline_epoch": self.deadline_epoch,
            "genesis_tranche_treatment": self.genesis_tranche_treatment,
            "issue_epoch": self.issue_epoch,
            "lot_id": self.lot_id,
            "runtime_version": DISTRIBUTED_CONVERSION_SCHEMA_VERSION,
        }


@dataclass(frozen=True)
class ConversionResolution:
    lot_id: str
    agent_id: str
    amount_ecu: Decimal
    issue_epoch: int
    deadline_epoch: int
    conversion_epoch: int
    genesis_tranche_treatment: str
    cdl057_witness_ref: str
    candidate_source: str
    resolution_status: str
    resolution_epoch: int
    verifier_root: str

    def __post_init__(self) -> None:
        candidate = ConversionCandidate(
            lot_id=self.lot_id,
            agent_id=self.agent_id,
            amount_ecu=self.amount_ecu,
            issue_epoch=self.issue_epoch,
            deadline_epoch=self.deadline_epoch,
            conversion_epoch=self.conversion_epoch,
            genesis_tranche_treatment=self.genesis_tranche_treatment,
            cdl057_witness_ref=self.cdl057_witness_ref,
            candidate_source=self.candidate_source,
        )
        object.__setattr__(self, "lot_id", candidate.lot_id)
        object.__setattr__(self, "agent_id", candidate.agent_id)
        object.__setattr__(self, "amount_ecu", candidate.amount_ecu)
        object.__setattr__(self, "issue_epoch", candidate.issue_epoch)
        object.__setattr__(self, "deadline_epoch", candidate.deadline_epoch)
        object.__setattr__(self, "conversion_epoch", candidate.conversion_epoch)
        object.__setattr__(
            self,
            "genesis_tranche_treatment",
            candidate.genesis_tranche_treatment,
        )
        object.__setattr__(self, "cdl057_witness_ref", candidate.cdl057_witness_ref)
        object.__setattr__(self, "candidate_source", candidate.candidate_source)
        object.__setattr__(
            self,
            "resolution_status",
            _require_resolution_status(self.resolution_status),
        )
        object.__setattr__(
            self,
            "resolution_epoch",
            _require_epoch(self.resolution_epoch, token="resolution_epoch_invalid"),
        )
        expected_root = conversion_resolution_verifier_root_preimage(
            self._record_without_verifier_root()
        )
        object.__setattr__(
            self,
            "verifier_root",
            _require_text(self.verifier_root, token="verifier_root_required"),
        )
        if self.verifier_root != expected_root:
            raise ValueError("conversion_resolution_verifier_root_mismatch")

    def _record_without_verifier_root(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "amount_ecu": decimal_to_canonical_string(self.amount_ecu),
            "candidate_source": self.candidate_source,
            "cdl057_witness_ref": self.cdl057_witness_ref,
            "conversion_epoch": self.conversion_epoch,
            "deadline_epoch": self.deadline_epoch,
            "genesis_tranche_treatment": self.genesis_tranche_treatment,
            "issue_epoch": self.issue_epoch,
            "lot_id": self.lot_id,
            "resolution_epoch": self.resolution_epoch,
            "resolution_status": self.resolution_status,
            "runtime_version": DISTRIBUTED_CONVERSION_SCHEMA_VERSION,
        }

    def to_canonical_record(self) -> dict[str, Any]:
        record = self._record_without_verifier_root()
        record["tokens"] = [
            FIX2R_SCHEMA_COMPLETE_TOKEN,
            FIX2R_CDL057_WITNESS_TOKEN,
            FIX2R_GENESIS_TRANCHE_FIELD_TOKEN,
            FIX2R_CDL029_NOT_TRANCHE_TOKEN,
            FIX2R_NO_WRITE_TOKEN,
            FIX2R_PUBLIC_BLOCKED_TOKEN,
        ]
        if self.genesis_tranche_treatment == GENESIS_TRANCHE_EXPLICITLY_DEFERRED:
            record["tokens"].append(FIX2R_EXPLICIT_DEFERRED_TOKEN)
        record["verifier_root"] = self.verifier_root
        record["wallet_write_authorized"] = False
        record["treasury_write_authorized"] = False
        record["production_minting_authorized"] = False
        record["ilc_settlement_authorized"] = False
        record["public_claimability_activated"] = False
        record["quote_read_model_only"] = True
        return record


def conversion_resolution_verifier_root_preimage(record_without_root: dict[str, Any]) -> str:
    _assert_no_authorized_write_flags(record_without_root)
    return f"{VERIFIER_ROOT_PREFIX}{_sha256_payload(record_without_root)}"


def attach_cdl057_witness_ref(
    candidate: ConversionCandidate,
    witness_runtime: Any,
) -> ConversionCandidate:
    witness_ref = CDL057_WITNESS_ABSENT_TOKEN
    getter = getattr(witness_runtime, "get_latest_witness_ref", None)
    if callable(getter):
        try:
            maybe_ref = getter()
        except Exception:
            maybe_ref = None
        if isinstance(maybe_ref, str) and maybe_ref.strip():
            witness_ref = maybe_ref.strip()
    return replace(candidate, cdl057_witness_ref=witness_ref)


def build_conversion_candidate_from_quote(
    quote_payload: dict[str, Any],
    *,
    genesis_tranche_treatment: str = GENESIS_TRANCHE_EXPLICITLY_DEFERRED,
    cdl057_witness_ref: str = CDL057_WITNESS_ABSENT_TOKEN,
    candidate_source: str = "fix2r_schema_read_model",
    genesis_tranche_source: str | None = None,
) -> ConversionCandidate:
    if not isinstance(quote_payload, dict):
        raise ValueError("conversion_quote_must_be_object")
    _reject_float_tree(quote_payload)
    _assert_no_authorized_write_flags(quote_payload)
    if genesis_tranche_source is not None:
        validate_genesis_tranche_treatment_source(
            genesis_tranche_treatment=genesis_tranche_treatment,
            source_label=genesis_tranche_source,
        )
    return ConversionCandidate(
        lot_id=quote_payload.get("lot_id"),
        agent_id=quote_payload.get("agent_id"),
        amount_ecu=quote_payload.get("amount_ecu_debit"),
        issue_epoch=quote_payload.get("issue_epoch"),
        deadline_epoch=quote_payload.get("deadline_epoch"),
        conversion_epoch=quote_payload.get("conversion_epoch"),
        genesis_tranche_treatment=genesis_tranche_treatment,
        cdl057_witness_ref=cdl057_witness_ref,
        candidate_source=candidate_source,
    )


def build_conversion_resolution(
    candidate: ConversionCandidate,
    *,
    resolution_status: str,
    resolution_epoch: int,
) -> ConversionResolution:
    preimage = {
        **candidate.to_canonical_record(),
        "resolution_epoch": _require_epoch(resolution_epoch, token="resolution_epoch_invalid"),
        "resolution_status": _require_resolution_status(resolution_status),
    }
    verifier_root = conversion_resolution_verifier_root_preimage(preimage)
    return ConversionResolution(
        lot_id=candidate.lot_id,
        agent_id=candidate.agent_id,
        amount_ecu=candidate.amount_ecu,
        issue_epoch=candidate.issue_epoch,
        deadline_epoch=candidate.deadline_epoch,
        conversion_epoch=candidate.conversion_epoch,
        genesis_tranche_treatment=candidate.genesis_tranche_treatment,
        cdl057_witness_ref=candidate.cdl057_witness_ref,
        candidate_source=candidate.candidate_source,
        resolution_status=preimage["resolution_status"],
        resolution_epoch=preimage["resolution_epoch"],
        verifier_root=verifier_root,
    )


def verify_conversion_resolution(resolution: ConversionResolution | dict[str, Any]) -> dict[str, Any]:
    try:
        if isinstance(resolution, ConversionResolution):
            canonical = resolution.to_canonical_record()
        elif isinstance(resolution, dict):
            _reject_float_tree(resolution)
            _assert_no_authorized_write_flags(resolution)
            constructed = ConversionResolution(
                lot_id=resolution.get("lot_id"),
                agent_id=resolution.get("agent_id"),
                amount_ecu=resolution.get("amount_ecu"),
                issue_epoch=resolution.get("issue_epoch"),
                deadline_epoch=resolution.get("deadline_epoch"),
                conversion_epoch=resolution.get("conversion_epoch"),
                genesis_tranche_treatment=resolution.get("genesis_tranche_treatment"),
                cdl057_witness_ref=resolution.get("cdl057_witness_ref"),
                candidate_source=resolution.get("candidate_source"),
                resolution_status=resolution.get("resolution_status"),
                resolution_epoch=resolution.get("resolution_epoch"),
                verifier_root=resolution.get("verifier_root"),
            )
            canonical = constructed.to_canonical_record()
            if _normalize_json(resolution) != canonical:
                return {"ok": False, "reason": "conversion_resolution_not_canonical"}
        else:
            return {"ok": False, "reason": "conversion_resolution_must_be_object"}
    except ValueError as exc:
        return {"ok": False, "reason": str(exc)}

    tokens = set(canonical.get("tokens", ()))
    required = {
        FIX2R_SCHEMA_COMPLETE_TOKEN,
        FIX2R_CDL057_WITNESS_TOKEN,
        FIX2R_GENESIS_TRANCHE_FIELD_TOKEN,
        FIX2R_CDL029_NOT_TRANCHE_TOKEN,
    }
    if not required.issubset(tokens):
        return {"ok": False, "reason": "conversion_resolution_tokens_missing"}
    return {
        "ok": True,
        "tokens": sorted(tokens),
        "verifier_root": canonical["verifier_root"],
    }


__all__ = [
    "CDL057_WITNESS_ABSENT_TOKEN",
    "CDL029_GENESIS_OVERHEAD_POOL_LABEL",
    "DISTRIBUTED_CONVERSION_SCHEMA_VERSION",
    "FIX2R_CDL029_NOT_TRANCHE_TOKEN",
    "FIX2R_CDL057_WITNESS_TOKEN",
    "FIX2R_EXPLICIT_DEFERRED_TOKEN",
    "FIX2R_GENESIS_TRANCHE_FIELD_TOKEN",
    "FIX2R_NO_WRITE_TOKEN",
    "FIX2R_PUBLIC_BLOCKED_TOKEN",
    "FIX2R_SCHEMA_COMPLETE_TOKEN",
    "GENESIS_TRANCHE_ALLOWED_TREATMENTS",
    "GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH",
    "GENESIS_TRANCHE_EXPLICITLY_DEFERRED",
    "GENESIS_TRANCHE_NOT_APPLICABLE_BY_RATIFIED_RULE",
    "VERIFIER_ROOT_PREFIX",
    "ConversionCandidate",
    "ConversionResolution",
    "attach_cdl057_witness_ref",
    "build_conversion_candidate_from_quote",
    "build_conversion_resolution",
    "conversion_resolution_verifier_root_preimage",
    "validate_genesis_tranche_treatment_source",
    "verify_conversion_resolution",
]
