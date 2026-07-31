# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-REPUTATION-02 AgentReputationRecord extractor.

This module creates deterministic, epoch-bound reputation evidence records.
It is intentionally standalone: it does not activate production reputation
scoring, validator admission, settlement, or wallet state.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

from ilc_core.consensus.reputation import (
    REPUTATION_SCORE_QUANTUM,
    apply_atrophy,
    calculate_voting_power,
)
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string
from ilc_core.validator.staking_liveness_runtime import (
    LIVENESS_MISS_THRESHOLD,
    validate_staking_and_liveness_state,
)
from ilc_core.validator.trust_tier_runtime import is_trust_tier_eligible


AGENT_REPUTATION_EXTRACTOR_VERSION = "agent_reputation_extractor_GAP_REPUTATION_02.v0.1"
CDL_106_DEPENDENCY = "cdl_106_agent_reputation_record_opened_GAP_REPUTATION_01"
PRODUCTION_REPUTATION_EXTRACTOR_NOT_ACTIVATED_TOKEN = (
    "production_reputation_extractor_not_activated_GAP_REPUTATION_02"
)
DEPLOYMENT_EFFICIENCY_REQUIRES_CDL_107_TOKEN = (
    "deployment_efficiency_requires_cdl_107_authority_GAP_REPUTATION_02"
)

AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
ELIGIBILITY_FLAG_KEYS = frozenset(
    (
        "panel_eligible",
        "validator_tier_candidate",
        "validator_tier_provisional",
        "validator_tier_official",
    )
)
ZERO = Decimal("0")
ONE = Decimal("1")


def require_production_reputation_extractor_activation() -> None:
    raise ValueError(PRODUCTION_REPUTATION_EXTRACTOR_NOT_ACTIVATED_TOKEN)


def _require_agent_id(value: object) -> str:
    if not isinstance(value, str) or AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError("agent_id_must_be_96_lower_hex_GAP_REPUTATION_02")
    return value


def _require_epoch(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("epoch_must_be_non_negative_int_GAP_REPUTATION_02")
    return value


def _require_root(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or SHA256_HEX_RE.fullmatch(value) is None:
        raise ValueError(f"{field_name}_must_be_64_lower_hex_GAP_REPUTATION_02")
    return value


def _require_optional_root(value: object, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_root(value, field_name=field_name)


def _require_mapping(value: object, *, token: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(token)
    return value


def _require_bool(value: object, *, token: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(token)
    return value


def _require_non_negative_int(value: object, *, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_non_negative_decimal(value: object, *, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(token) from exc
    else:
        raise ValueError(token)
    if not number.is_finite():
        raise ValueError("invalid_amount_non_finite")
    if number < ZERO:
        raise ValueError(token)
    if number.is_signed():
        return ZERO
    return number


def _require_unit_decimal(value: object, *, token: str) -> Decimal:
    number = _require_non_negative_decimal(value, token=token)
    if number > ONE:
        raise ValueError(token)
    return number


def _normalize_json_value(value: object) -> object:
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("reputation_evidence_non_finite_decimal_GAP_REPUTATION_02")
        return decimal_to_canonical_string(value)
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, bytes):
        raise ValueError("reputation_evidence_bytes_not_json_safe_GAP_REPUTATION_02")
    if isinstance(value, Sequence):
        return [_normalize_json_value(item) for item in value]
    if isinstance(value, Mapping):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("reputation_evidence_mapping_keys_must_be_strings_GAP_REPUTATION_02")
            normalized[key] = _normalize_json_value(item)
        return normalized
    raise ValueError("reputation_evidence_value_not_json_safe_GAP_REPUTATION_02")


def _canonical_json_bytes(value: object) -> bytes:
    normalized = _normalize_json_value(value)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _stable_sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _normalize_eligibility_flags(value: Mapping[str, object]) -> dict[str, bool]:
    if set(value) != ELIGIBILITY_FLAG_KEYS:
        raise ValueError("eligibility_flags_schema_mismatch_GAP_REPUTATION_02")
    return {
        key: _require_bool(value[key], token="eligibility_flags_must_be_bool_GAP_REPUTATION_02")
        for key in sorted(ELIGIBILITY_FLAG_KEYS)
    }


def _normalize_reputation_score(value: object) -> Decimal:
    score = _require_non_negative_decimal(
        value,
        token="reputation_score_must_be_non_negative_decimal_GAP_REPUTATION_02",
    )
    return score.quantize(REPUTATION_SCORE_QUANTUM)


def _read_trust_vector(lifecycle_evidence: Mapping[str, object]) -> dict[str, Decimal]:
    raw_trust_vector = _require_mapping(
        lifecycle_evidence.get("trust_vector"),
        token="lifecycle_trust_vector_must_be_mapping_GAP_REPUTATION_02",
    )
    return {
        "accuracy": _require_unit_decimal(
            raw_trust_vector.get("accuracy", ZERO),
            token="lifecycle_accuracy_must_be_unit_decimal_GAP_REPUTATION_02",
        ),
        "precision": _require_unit_decimal(
            raw_trust_vector.get("precision", ZERO),
            token="lifecycle_precision_must_be_unit_decimal_GAP_REPUTATION_02",
        ),
        "potential": _require_unit_decimal(
            raw_trust_vector.get("potential", ZERO),
            token="lifecycle_potential_must_be_unit_decimal_GAP_REPUTATION_02",
        ),
    }


def _read_liveness_inputs(
    liveness_evidence: Mapping[str, object],
) -> tuple[Decimal, int, bool]:
    stake = _require_non_negative_decimal(
        liveness_evidence.get("stake"),
        token="liveness_stake_must_be_non_negative_decimal_GAP_REPUTATION_02",
    )
    if stake <= ZERO:
        raise ValueError("liveness_stake_must_be_positive_decimal_GAP_REPUTATION_02")
    missed = _require_non_negative_int(
        liveness_evidence.get("consecutive_missed_epochs"),
        token="liveness_missed_epochs_must_be_non_negative_int_GAP_REPUTATION_02",
    )
    equivocation_state = _require_bool(
        liveness_evidence.get("equivocation_state"),
        token="liveness_equivocation_state_must_be_bool_GAP_REPUTATION_02",
    )
    return stake, missed, equivocation_state


def _read_equivocation_state(
    equivocation_evidence: Mapping[str, object],
    liveness_equivocation_state: bool,
) -> bool:
    if "equivocation_state" in equivocation_evidence:
        equivocation_state = _require_bool(
            equivocation_evidence["equivocation_state"],
            token="equivocation_state_must_be_bool_GAP_REPUTATION_02",
        )
    elif "equivocation_detected" in equivocation_evidence:
        equivocation_state = _require_bool(
            equivocation_evidence["equivocation_detected"],
            token="equivocation_state_must_be_bool_GAP_REPUTATION_02",
        )
    else:
        raise ValueError("equivocation_state_required_GAP_REPUTATION_02")
    if equivocation_state != liveness_equivocation_state:
        raise ValueError("equivocation_state_mismatch_GAP_REPUTATION_02")
    return equivocation_state


def _sybil_unresolved(sybil_evidence: Mapping[str, object]) -> bool:
    value = sybil_evidence.get("unresolved_sybil_risk", False)
    return _require_bool(value, token="sybil_unresolved_flag_must_be_bool_GAP_REPUTATION_02")


@dataclass(frozen=True)
class AgentReputationRecord:
    agent_id: str
    epoch: int
    graph_snapshot_root: str
    lifecycle_event_root: str
    attribution_root: str | None
    liveness_root: str
    equivocation_root: str
    sybil_risk_root: str
    reputation_score: Decimal
    eligibility_flags: dict[str, bool]
    previous_reputation_record_root: str | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "agent_id", _require_agent_id(self.agent_id))
        object.__setattr__(self, "epoch", _require_epoch(self.epoch))
        object.__setattr__(
            self,
            "graph_snapshot_root",
            _require_root(self.graph_snapshot_root, field_name="graph_snapshot_root"),
        )
        object.__setattr__(
            self,
            "lifecycle_event_root",
            _require_root(self.lifecycle_event_root, field_name="lifecycle_event_root"),
        )
        object.__setattr__(
            self,
            "attribution_root",
            _require_optional_root(self.attribution_root, field_name="attribution_root"),
        )
        object.__setattr__(
            self,
            "liveness_root",
            _require_root(self.liveness_root, field_name="liveness_root"),
        )
        object.__setattr__(
            self,
            "equivocation_root",
            _require_root(self.equivocation_root, field_name="equivocation_root"),
        )
        object.__setattr__(
            self,
            "sybil_risk_root",
            _require_root(self.sybil_risk_root, field_name="sybil_risk_root"),
        )
        object.__setattr__(
            self,
            "reputation_score",
            _normalize_reputation_score(self.reputation_score),
        )
        object.__setattr__(
            self,
            "eligibility_flags",
            _normalize_eligibility_flags(self.eligibility_flags),
        )
        object.__setattr__(
            self,
            "previous_reputation_record_root",
            _require_optional_root(
                self.previous_reputation_record_root,
                field_name="previous_reputation_record_root",
            ),
        )

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "attribution_root": self.attribution_root,
            "eligibility_flags": dict(sorted(self.eligibility_flags.items())),
            "epoch": self.epoch,
            "equivocation_root": self.equivocation_root,
            "graph_snapshot_root": self.graph_snapshot_root,
            "lifecycle_event_root": self.lifecycle_event_root,
            "liveness_root": self.liveness_root,
            "previous_reputation_record_root": self.previous_reputation_record_root,
            "reputation_score": decimal_to_canonical_string(self.reputation_score),
            "sybil_risk_root": self.sybil_risk_root,
        }


def extract_agent_reputation_record(
    *,
    agent_id: str,
    epoch: int,
    graph_snapshot_evidence: Mapping[str, object],
    lifecycle_evidence: Mapping[str, object],
    liveness_evidence: Mapping[str, object],
    equivocation_evidence: Mapping[str, object],
    sybil_evidence: Mapping[str, object],
    attribution_evidence: Mapping[str, object] | None = None,
    previous_reputation_record_root: str | None = None,
    deployment_efficiency: Decimal | int | str | None = None,
) -> AgentReputationRecord:
    """Extract one immutable reputation record from epoch evidence.

    The score is a non-production, unit-normalized Decimal score derived from the
    existing reputation helper surface. CDL-107 must ratify binding thresholds
    and any pressure-flow deployment-efficiency formula before admission use.
    """

    if deployment_efficiency is not None:
        _require_non_negative_decimal(
            deployment_efficiency,
            token="deployment_efficiency_must_be_non_negative_decimal_GAP_REPUTATION_02",
        )
        raise ValueError(DEPLOYMENT_EFFICIENCY_REQUIRES_CDL_107_TOKEN)

    normalized_agent_id = _require_agent_id(agent_id)
    normalized_epoch = _require_epoch(epoch)
    graph_snapshot = _require_mapping(
        graph_snapshot_evidence,
        token="graph_snapshot_evidence_must_be_mapping_GAP_REPUTATION_02",
    )
    lifecycle = _require_mapping(
        lifecycle_evidence,
        token="lifecycle_evidence_must_be_mapping_GAP_REPUTATION_02",
    )
    liveness = _require_mapping(
        liveness_evidence,
        token="liveness_evidence_must_be_mapping_GAP_REPUTATION_02",
    )
    equivocation = _require_mapping(
        equivocation_evidence,
        token="equivocation_evidence_must_be_mapping_GAP_REPUTATION_02",
    )
    sybil = _require_mapping(
        sybil_evidence,
        token="sybil_evidence_must_be_mapping_GAP_REPUTATION_02",
    )
    attribution = (
        None
        if attribution_evidence is None
        else _require_mapping(
            attribution_evidence,
            token="attribution_evidence_must_be_mapping_GAP_REPUTATION_02",
        )
    )

    trust_vector = _read_trust_vector(lifecycle)
    last_active_epoch = _require_epoch(lifecycle.get("last_active_epoch", normalized_epoch))
    stake, missed_epochs, liveness_equivocation = _read_liveness_inputs(liveness)
    equivocation_state = _read_equivocation_state(equivocation, liveness_equivocation)

    adjusted_state = apply_atrophy(
        {"trust_vector": trust_vector, "last_active_epoch": last_active_epoch},
        current_epoch=normalized_epoch,
    )
    score = calculate_voting_power(ONE, adjusted_state["trust_vector"])
    reputation_score = _normalize_reputation_score(score)

    staking_status = validate_staking_and_liveness_state(
        stake,
        missed_epochs,
        liveness_equivocation,
    )
    trust_tier_ok = is_trust_tier_eligible(
        missed_epochs,
        LIVENESS_MISS_THRESHOLD,
        equivocation_state,
    )
    unresolved_sybil = _sybil_unresolved(sybil)
    base_eligible = (
        staking_status["status"] == "active"
        and trust_tier_ok
        and not equivocation_state
        and not unresolved_sybil
    )
    eligibility_flags = {
        "panel_eligible": base_eligible,
        "validator_tier_candidate": base_eligible,
        "validator_tier_provisional": False,
        "validator_tier_official": False,
    }

    return AgentReputationRecord(
        agent_id=normalized_agent_id,
        epoch=normalized_epoch,
        graph_snapshot_root=_stable_sha256(graph_snapshot),
        lifecycle_event_root=_stable_sha256(lifecycle),
        attribution_root=None if attribution is None else _stable_sha256(attribution),
        liveness_root=_stable_sha256(liveness),
        equivocation_root=_stable_sha256(equivocation),
        sybil_risk_root=_stable_sha256(sybil),
        reputation_score=reputation_score,
        eligibility_flags=eligibility_flags,
        previous_reputation_record_root=previous_reputation_record_root,
    )


def canonical_agent_reputation_records_json(
    records: Sequence[AgentReputationRecord],
) -> str:
    canonical_records = [record.to_canonical_record() for record in records]
    return json.dumps(canonical_records, sort_keys=True, separators=(",", ":"), allow_nan=False)


def compute_agent_reputation_root(records: Sequence[AgentReputationRecord]) -> str:
    if not records:
        raise ValueError("agent_reputation_root_requires_records_GAP_REPUTATION_02")
    epochs = {record.epoch for record in records}
    if len(epochs) != 1:
        raise ValueError("agent_reputation_root_requires_single_epoch_GAP_REPUTATION_02")
    agent_ids = [record.agent_id for record in records]
    if len(set(agent_ids)) != len(agent_ids):
        raise ValueError("agent_reputation_root_duplicate_agent_id_GAP_REPUTATION_02")
    sorted_records = sorted(records, key=lambda record: record.agent_id)
    return hashlib.sha256(
        canonical_agent_reputation_records_json(sorted_records).encode("utf-8")
    ).hexdigest()


__all__ = [
    "AGENT_REPUTATION_EXTRACTOR_VERSION",
    "CDL_106_DEPENDENCY",
    "DEPLOYMENT_EFFICIENCY_REQUIRES_CDL_107_TOKEN",
    "ELIGIBILITY_FLAG_KEYS",
    "PRODUCTION_REPUTATION_EXTRACTOR_NOT_ACTIVATED_TOKEN",
    "AgentReputationRecord",
    "canonical_agent_reputation_records_json",
    "compute_agent_reputation_root",
    "extract_agent_reputation_record",
    "require_production_reputation_extractor_activation",
]
