"""Diagnostic IEC + K metrics for CDL-120 implementation evidence.

This module is deliberately not wired into settlement, ECU minting, jury
verdicts, or raw-reuse-weight computation. It provides a deterministic Python
surface for the GAP-IEC-K-IMPL-00 evidence lane.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from itertools import combinations
from typing import Iterable


IEC_K_METRICS_VERSION = "iec_k_metrics_GAP_IEC_K_IMPL_00.v0.1"
MAX_IEC_K_IDENTIFIER_CHARS = 512
MAX_IEC_K_COUNT = 18_446_744_073_709_551_615
MAX_IEC_K_COEFFICIENT = Decimal("1000000000000000000")
IEC_K_DIAGNOSTIC_DECIMAL_QUANTUM = Decimal("0.000000000001")


def _validate_optional_identifier(value: str | None, token: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(token)
    if not value or value != value.strip():
        raise ValueError(token)
    if len(value) > MAX_IEC_K_IDENTIFIER_CHARS:
        raise ValueError(token)
    return value


def _validate_optional_stance(value: str | None) -> str | None:
    normalized = _validate_optional_identifier(
        value,
        "iec_k_stance_must_be_non_empty_string",
    )
    if normalized is not None and any(char.isspace() for char in normalized):
        raise ValueError("iec_k_stance_must_be_single_token")
    return normalized


def _require_non_negative_int(value: int, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_bounded_non_negative_int(value: int, token: str, max_token: str) -> int:
    normalized = _require_non_negative_int(value, token)
    if normalized > MAX_IEC_K_COUNT:
        raise ValueError(max_token)
    return normalized


def _require_decimal(value: Decimal, token: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise ValueError(token)
    if not value.is_finite():
        raise ValueError(token)
    return value


def _require_non_negative_decimal(
    value: Decimal,
    type_token: str,
    range_token: str,
) -> Decimal:
    normalized = _require_decimal(value, type_token)
    if normalized < 0:
        raise ValueError(range_token)
    return normalized


def _materialize_records(
    attribution_events: Iterable["AttributionRecord"],
) -> tuple["AttributionRecord", ...]:
    if isinstance(attribution_events, Iterator):
        raise ValueError("iec_k_attribution_events_must_be_reiterable")
    return tuple(attribution_events)


@dataclass(frozen=True)
class AttributionRecord:
    origin_id: str | None
    context_id: str | None
    rrw: Decimal | None
    stance: str | None = None
    has_surviving_descendant: bool = True

    def __post_init__(self) -> None:
        _validate_optional_identifier(
            self.origin_id,
            "iec_k_origin_id_must_be_non_empty_string",
        )
        _validate_optional_identifier(
            self.context_id,
            "iec_k_context_id_must_be_non_empty_string",
        )
        _validate_optional_stance(self.stance)
        if self.rrw is not None:
            _require_non_negative_decimal(
                self.rrw,
                "iec_k_rrw_must_be_decimal",
                "iec_k_rrw_must_be_non_negative",
            )
        if not isinstance(self.has_surviving_descendant, bool):
            raise ValueError("iec_k_has_surviving_descendant_must_be_bool")


def compute_iec(attribution_events: Iterable[AttributionRecord]) -> int:
    """Count distinct surviving origin IDs."""

    records = _materialize_records(attribution_events)
    origins: set[str] = set()
    for event in records:
        if event.origin_id is None:
            continue
        if event.has_surviving_descendant:
            origins.add(event.origin_id)
    return len(origins)


def _mean(scores: list[float]) -> float:
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def compute_k(attribution_events: Iterable[AttributionRecord]) -> tuple[float, float]:
    """Return ``(within_ctx, between_ctx)`` pairwise same-stance agreement."""

    records = _materialize_records(attribution_events)
    comparable = [
        event
        for event in records
        if event.context_id is not None and event.stance is not None
    ]
    # K is a diagnostic-only graph signal in CDL-120 v0.1. Do not promote this
    # float tuple into ECU, settlement, jury, or attribution weights without a
    # separate governance phase that defines exact numeric semantics.
    within_scores: list[float] = []
    between_scores: list[float] = []
    for left, right in combinations(comparable, 2):
        score = 1.0 if left.stance == right.stance else 0.0
        if left.context_id == right.context_id:
            within_scores.append(score)
        else:
            between_scores.append(score)
    return (_mean(within_scores), _mean(between_scores))


def compute_elf(rrw: Decimal, iec: int) -> Decimal | None:
    """Return RRW divided by IEC, or ``None`` when IEC is zero."""

    normalized_rrw = _require_non_negative_decimal(
        rrw,
        "iec_k_rrw_must_be_decimal",
        "iec_k_rrw_must_be_non_negative",
    )
    normalized_iec = _require_bounded_non_negative_int(
        iec,
        "iec_k_iec_must_be_non_negative_int",
        "iec_k_iec_exceeds_maximum",
    )
    if normalized_iec == 0:
        return None
    with localcontext() as ctx:
        ctx.prec = 80
        return (normalized_rrw / Decimal(normalized_iec)).quantize(
            IEC_K_DIAGNOSTIC_DECIMAL_QUANTUM,
            rounding=ROUND_HALF_EVEN,
        )


def compute_popperian_weight(
    iec: int,
    survived_refutation_attempts: int,
    coefficient: Decimal = Decimal("0.5"),
) -> Decimal:
    """Return IEC plus the provisional CDL-120 refutation-resistance term."""

    normalized_iec = _require_bounded_non_negative_int(
        iec,
        "iec_k_iec_must_be_non_negative_int",
        "iec_k_iec_exceeds_maximum",
    )
    normalized_attempts = _require_bounded_non_negative_int(
        survived_refutation_attempts,
        "iec_k_survived_refutation_attempts_must_be_non_negative_int",
        "iec_k_survived_refutation_attempts_exceeds_maximum",
    )
    normalized_coefficient = _require_decimal(
        coefficient,
        "iec_k_coefficient_must_be_decimal",
    )
    if normalized_coefficient < 0:
        raise ValueError("iec_k_coefficient_must_be_non_negative")
    if normalized_coefficient > MAX_IEC_K_COEFFICIENT:
        raise ValueError("iec_k_coefficient_exceeds_maximum")
    with localcontext() as ctx:
        ctx.prec = 80
        return Decimal(normalized_iec) + (
            normalized_coefficient * Decimal(normalized_attempts)
        )
