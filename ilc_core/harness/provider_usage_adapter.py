"""PUBLIC_RC_EXCLUDE: private_provider_usage_adapter
PUBLIC_RC_EXCLUDE_REASON: Private local token-budget tracker. Provider telemetry is operational-only and not protocol truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Mapping

MAX_USAGE_RECORDS = 256
PROVIDER_USAGE_ADAPTER_NOT_PROTOCOL_TRUTH = True


def _decimal_from_value(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    try:
        out = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(token) from None
    if not out.is_finite():
        raise ValueError(token)
    if out < Decimal("0"):
        raise ValueError(token)
    return out


def _int_from_value(value: object, token: str) -> int:
    if isinstance(value, bool):
        raise ValueError(token)
    try:
        out = int(str(value))
    except ValueError:
        raise ValueError(token) from None
    if out < 0:
        raise ValueError(token)
    return out


@dataclass(frozen=True)
class ProviderQuotaSignal:
    provider_id: str
    remaining_tokens: int | None
    limit_tokens: int | None
    reset_after_seconds: Decimal | None
    operational_signal_only: bool = True


@dataclass(frozen=True)
class ProviderUsageRecord:
    provider_id: str
    input_tokens: int
    output_tokens: int
    cost_proxy: Decimal
    quota_signal: ProviderQuotaSignal


@dataclass(frozen=True)
class ProviderBudgetSnapshot:
    provider_id: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost_proxy: Decimal
    remaining_tokens: int | None
    operational_signal_only: bool = True


class ProviderUsageAdapter:
    """Bounded local token-budget tracker for private harness scheduling."""

    def __init__(self, *, max_records: int = MAX_USAGE_RECORDS) -> None:
        if max_records < 1 or max_records > MAX_USAGE_RECORDS:
            raise ValueError("provider_usage_invalid_max_records")
        self._max_records = max_records
        self._records: list[ProviderUsageRecord] = []

    @staticmethod
    def parse_quota_headers(
        provider_id: str,
        headers: Mapping[str, object] | None,
    ) -> ProviderQuotaSignal:
        if provider_id == "":
            raise ValueError("provider_usage_missing_provider_id")
        headers = {} if headers is None else headers
        lower_headers = {str(key).lower(): value for key, value in headers.items()}

        remaining = lower_headers.get("x-ratelimit-remaining-tokens")
        limit = lower_headers.get("x-ratelimit-limit-tokens")
        reset = lower_headers.get("x-ratelimit-reset-seconds")

        return ProviderQuotaSignal(
            provider_id=provider_id,
            remaining_tokens=(
                None
                if remaining is None
                else _int_from_value(remaining, "provider_usage_invalid_remaining_tokens")
            ),
            limit_tokens=(
                None
                if limit is None
                else _int_from_value(limit, "provider_usage_invalid_limit_tokens")
            ),
            reset_after_seconds=(
                None
                if reset is None
                else _decimal_from_value(reset, "provider_usage_invalid_reset_seconds")
            ),
        )

    def record_usage(
        self,
        *,
        provider_id: str,
        input_tokens: object,
        output_tokens: object,
        cost_proxy: object,
        quota_headers: Mapping[str, object] | None = None,
    ) -> ProviderUsageRecord:
        if provider_id == "":
            raise ValueError("provider_usage_missing_provider_id")
        if len(self._records) >= self._max_records:
            raise ValueError("provider_usage_record_cap_exceeded")
        record = ProviderUsageRecord(
            provider_id=provider_id,
            input_tokens=_int_from_value(input_tokens, "provider_usage_invalid_input_tokens"),
            output_tokens=_int_from_value(output_tokens, "provider_usage_invalid_output_tokens"),
            cost_proxy=_decimal_from_value(cost_proxy, "provider_usage_invalid_cost_proxy"),
            quota_signal=self.parse_quota_headers(provider_id, quota_headers),
        )
        self._records.append(record)
        return record

    def records(self) -> list[ProviderUsageRecord]:
        return list(self._records)

    def snapshot(self, provider_id: str) -> ProviderBudgetSnapshot:
        rows = [record for record in self._records if record.provider_id == provider_id]
        remaining_values = [
            row.quota_signal.remaining_tokens
            for row in rows
            if row.quota_signal.remaining_tokens is not None
        ]
        return ProviderBudgetSnapshot(
            provider_id=provider_id,
            total_input_tokens=sum(row.input_tokens for row in rows),
            total_output_tokens=sum(row.output_tokens for row in rows),
            total_tokens=sum(row.input_tokens + row.output_tokens for row in rows),
            total_cost_proxy=sum((row.cost_proxy for row in rows), Decimal("0")),
            remaining_tokens=min(remaining_values) if remaining_values else None,
        )
