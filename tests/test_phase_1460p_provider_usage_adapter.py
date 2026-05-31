from decimal import Decimal

import pytest

from ilc_core.harness.provider_usage_adapter import (
    MAX_USAGE_RECORDS,
    PROVIDER_USAGE_ADAPTER_NOT_PROTOCOL_TRUTH,
    ProviderUsageAdapter,
)


def test_provider_usage_adapter_tracks_local_budget_with_decimal_costs() -> None:
    adapter = ProviderUsageAdapter()

    record = adapter.record_usage(
        provider_id="fixture-provider",
        input_tokens=10,
        output_tokens=5,
        cost_proxy="0.015",
        quota_headers={
            "x-ratelimit-remaining-tokens": "100",
            "x-ratelimit-limit-tokens": "200",
            "x-ratelimit-reset-seconds": "30.5",
        },
    )

    snapshot = adapter.snapshot("fixture-provider")

    assert PROVIDER_USAGE_ADAPTER_NOT_PROTOCOL_TRUTH is True
    assert record.cost_proxy == Decimal("0.015")
    assert record.quota_signal.operational_signal_only is True
    assert snapshot.total_tokens == 15
    assert snapshot.total_cost_proxy == Decimal("0.015")
    assert snapshot.remaining_tokens == 100
    assert snapshot.operational_signal_only is True


def test_provider_usage_adapter_rejects_non_finite_decimal_inputs() -> None:
    adapter = ProviderUsageAdapter()

    with pytest.raises(ValueError) as exc:
        adapter.record_usage(
            provider_id="fixture-provider",
            input_tokens=1,
            output_tokens=1,
            cost_proxy="NaN",
        )

    assert str(exc.value) == "provider_usage_invalid_cost_proxy"


def test_provider_usage_adapter_enforces_record_cap() -> None:
    adapter = ProviderUsageAdapter(max_records=2)
    for index in range(2):
        adapter.record_usage(
            provider_id="fixture-provider",
            input_tokens=index + 1,
            output_tokens=1,
            cost_proxy="0.01",
        )

    with pytest.raises(ValueError) as exc:
        adapter.record_usage(
            provider_id="fixture-provider",
            input_tokens=1,
            output_tokens=1,
            cost_proxy="0.01",
        )

    assert str(exc.value) == "provider_usage_record_cap_exceeded"
    assert MAX_USAGE_RECORDS >= 2


def test_provider_usage_adapter_rejects_empty_provider_id_on_record_usage() -> None:
    adapter = ProviderUsageAdapter()

    with pytest.raises(ValueError) as exc:
        adapter.record_usage(
            provider_id="",
            input_tokens=1,
            output_tokens=1,
            cost_proxy="0.01",
        )

    assert str(exc.value) == "provider_usage_missing_provider_id"
