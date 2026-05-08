import json

import pytest

from ilc_core.network.d2d.cdl087_observability import (
    CDL077_RATE_LIMITER_FINAL_REGRESSION_TOKEN,
    CDL087_OBSERVABILITY_COLLECTION_VERSION,
    CDL087_RATIFICATION_READINESS_TOKEN,
    NO_CDL087_RATIFICATION_TOKEN,
    REQUIRED_CDL087_SIGNAL_NAMES,
    build_observability_collection_window,
    export_observability_json,
    record_cdl077_limiter_regression,
    record_ratification_readiness_verdict,
)


def _signals() -> dict[str, object]:
    return {
        "fetch_requests_by_tier": {"Tier A": 3, "Tier B": 2, "Tier C": 1},
        "want_have_hit_rate": "0.833333",
        "want_have_miss_rate": "0.166667",
        "want_block_success_count": 5,
        "want_block_error_404": 1,
        "want_block_error_429": 1,
        "want_block_error_400": 0,
        "cache_hit_rate_tier_a": "1.000000",
        "bytes_served_by_tier": {"Tier A": "300", "Tier B": "200", "Tier C": "100"},
        "non_cacheable_request_volume": 0,
        "circuit_breaker_activations": 1,
        "serve_events_credited_cdl_078": 5,
    }


def test_collection_window_requires_exact_cdl087_signal_names() -> None:
    artifact = build_observability_collection_window(
        [{"epoch_sequence": 1260, "signals": _signals()}],
        collection_window_id="phase-1260-window",
        serving_peer_id="local-serving-peer",
    )

    assert artifact["version"] == CDL087_OBSERVABILITY_COLLECTION_VERSION
    assert tuple(artifact["required_signal_names"]) == REQUIRED_CDL087_SIGNAL_NAMES
    assert artifact["epoch_sequence_axis"] == "protocol_epoch_sequence"
    assert artifact["wall_clock_time_included"] is False
    assert artifact["per_requester_dossiers_included"] is False
    assert artifact["tokens"]["no_ratification"] == NO_CDL087_RATIFICATION_TOKEN


def test_collection_window_exports_canonical_json() -> None:
    artifact = build_observability_collection_window(
        [{"epoch_sequence": 1260, "signals": _signals()}],
        collection_window_id="phase-1260-window",
        serving_peer_id="local-serving-peer",
    )
    payload = export_observability_json(artifact)

    assert payload == json.dumps(artifact, allow_nan=False, separators=(",", ":"), sort_keys=True)


def test_collection_window_rejects_missing_signal() -> None:
    signals = _signals()
    signals.pop("want_block_error_400")

    with pytest.raises(ValueError, match="required_observability_signal_missing"):
        build_observability_collection_window(
            [{"epoch_sequence": 1260, "signals": signals}],
            collection_window_id="phase-1260-window",
            serving_peer_id="local-serving-peer",
        )


def test_collection_window_rejects_extra_signal() -> None:
    signals = _signals()
    signals["extra_metric"] = 1

    with pytest.raises(ValueError, match="unexpected_observability_signal"):
        build_observability_collection_window(
            [{"epoch_sequence": 1260, "signals": signals}],
            collection_window_id="phase-1260-window",
            serving_peer_id="local-serving-peer",
        )


def test_collection_window_rejects_per_requester_dossiers() -> None:
    signals = _signals()
    signals["fetch_requests_by_tier"] = {
        "Tier A": 3,
        "requester_id": "agent-1",
    }

    with pytest.raises(ValueError, match="per_requester_observability_forbidden"):
        build_observability_collection_window(
            [{"epoch_sequence": 1260, "signals": signals}],
            collection_window_id="phase-1260-window",
            serving_peer_id="local-serving-peer",
        )


def test_collection_window_rejects_float_values() -> None:
    signals = _signals()
    signals["want_have_hit_rate"] = 0.5

    with pytest.raises(ValueError, match="float_values_forbidden"):
        build_observability_collection_window(
            [{"epoch_sequence": 1260, "signals": signals}],
            collection_window_id="phase-1260-window",
            serving_peer_id="local-serving-peer",
        )


def test_collection_window_rejects_duplicate_epoch_sequence() -> None:
    with pytest.raises(ValueError, match="epoch_sequence_duplicate"):
        build_observability_collection_window(
            [
                {"epoch_sequence": 1260, "signals": _signals()},
                {"epoch_sequence": 1260, "signals": _signals()},
            ],
            collection_window_id="phase-1260-window",
            serving_peer_id="local-serving-peer",
        )


def test_cdl077_limiter_regression_preserves_limit_and_next_window_reset() -> None:
    regression = record_cdl077_limiter_regression(
        requester_id="agent-1260",
        window_id=1260,
        limit_per_window=2,
    )

    assert regression["token"] == CDL077_RATE_LIMITER_FINAL_REGRESSION_TOKEN
    assert regression["all_within_window_allowed"] is True
    assert regression["over_limit_allowed"] is False
    assert regression["next_window_allowed"] is True


def test_ratification_readiness_verdict_records_no_ratification() -> None:
    collection = build_observability_collection_window(
        [{"epoch_sequence": 1260, "signals": _signals()}],
        collection_window_id="phase-1260-window",
        serving_peer_id="local-serving-peer",
    )
    limiter_regression = record_cdl077_limiter_regression(limit_per_window=1)
    verdict = record_ratification_readiness_verdict(
        collection_window=collection,
        limiter_regression=limiter_regression,
        conditions_2_and_3_recorded=True,
    )

    assert verdict["token"] == CDL087_RATIFICATION_READINESS_TOKEN
    assert verdict["no_ratification_token"] == NO_CDL087_RATIFICATION_TOKEN
    assert verdict["verdict"] == "ready_for_later_sensitive_ratification_review"


def test_ratification_readiness_verdict_stays_not_ready_without_1259_evidence() -> None:
    collection = build_observability_collection_window(
        [{"epoch_sequence": 1260, "signals": _signals()}],
        collection_window_id="phase-1260-window",
        serving_peer_id="local-serving-peer",
    )
    limiter_regression = record_cdl077_limiter_regression(limit_per_window=1)
    verdict = record_ratification_readiness_verdict(
        collection_window=collection,
        limiter_regression=limiter_regression,
        conditions_2_and_3_recorded=False,
    )

    assert verdict["verdict"] == "not_ready"
    assert verdict["blockers"] == ["conditions_2_and_3_evidence_not_recorded"]
