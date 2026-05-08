"""Local CDL-087 observability and limiter regression helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime import (
    PERSISTENT_RATE_LIMITER_VERSION,
    PersistentFetchRateLimiter,
)
from ilc_core.network.d2d.truth_primitive_fetch_runtime import (
    WANT_BLOCK_RATE_LIMIT_PER_MINUTE,
)

CDL087_OBSERVABILITY_COLLECTION_VERSION = (
    "cdl_087_observability_collection_window_phase_1260.v0.1"
)
CDL077_RATE_LIMITER_FINAL_REGRESSION_TOKEN = (
    "cdl_077_rate_limiter_final_regression_recorded_phase_1260"
)
CDL087_RATIFICATION_READINESS_TOKEN = (
    "cdl_087_ratification_readiness_verdict_recorded_phase_1260"
)
NO_CDL087_RATIFICATION_TOKEN = "no_cdl_087_ratification_phase_1260"

REQUIRED_CDL087_SIGNAL_NAMES = (
    "fetch_requests_by_tier",
    "want_have_hit_rate",
    "want_have_miss_rate",
    "want_block_success_count",
    "want_block_error_404",
    "want_block_error_429",
    "want_block_error_400",
    "cache_hit_rate_tier_a",
    "bytes_served_by_tier",
    "non_cacheable_request_volume",
    "circuit_breaker_activations",
    "serve_events_credited_cdl_078",
)

_TIERS = ("Tier A", "Tier B", "Tier C")
DEFAULT_MAX_EPOCHS = 128
DEFAULT_MAX_JSON_BYTES = 2_000_000


def build_observability_collection_window(
    epoch_metrics: Sequence[Mapping[str, Any]],
    *,
    serving_peer_id: str,
    collection_window_id: str,
    max_epochs: int = DEFAULT_MAX_EPOCHS,
) -> dict[str, Any]:
    """Build a canonical local CDL-087 observability collection artifact."""

    _require_non_empty_text(serving_peer_id, "serving_peer_id_required")
    _require_non_empty_text(collection_window_id, "collection_window_id_required")
    if type(max_epochs) is not int or max_epochs < 1:
        raise ValueError("max_epochs_invalid")
    if not isinstance(epoch_metrics, Sequence) or isinstance(epoch_metrics, (str, bytes)):
        raise ValueError("epoch_metrics_sequence_required")
    if not epoch_metrics:
        raise ValueError("epoch_metrics_required")
    if len(epoch_metrics) > max_epochs:
        raise ValueError("epoch_metrics_count_exceeded")

    normalized_epochs = [
        _normalize_epoch_metrics(item)
        for item in sorted(epoch_metrics, key=lambda entry: int(entry["epoch_sequence"]))
    ]
    epoch_sequences = [item["epoch_sequence"] for item in normalized_epochs]
    if len(set(epoch_sequences)) != len(epoch_sequences):
        raise ValueError("epoch_sequence_duplicate")

    artifact = {
        "collection_window_id": collection_window_id,
        "epoch_sequence_axis": "protocol_epoch_sequence",
        "per_requester_dossiers_included": False,
        "required_signal_names": list(REQUIRED_CDL087_SIGNAL_NAMES),
        "serving_peer_id": serving_peer_id,
        "signal_epochs": normalized_epochs,
        "tokens": {
            "no_ratification": NO_CDL087_RATIFICATION_TOKEN,
            "readiness": CDL087_RATIFICATION_READINESS_TOKEN,
            "version": CDL087_OBSERVABILITY_COLLECTION_VERSION,
        },
        "wall_clock_time_included": False,
        "version": CDL087_OBSERVABILITY_COLLECTION_VERSION,
    }
    _enforce_json_size(artifact)
    return artifact


def record_cdl077_limiter_regression(
    *,
    requester_id: str = "phase-1260-requester",
    window_id: int = 1260,
    limit_per_window: int = WANT_BLOCK_RATE_LIMIT_PER_MINUTE,
) -> dict[str, Any]:
    """Run a deterministic persistent limiter regression and return evidence."""

    _require_non_empty_text(requester_id, "requester_id_required")
    if type(window_id) is not int or window_id < 0:
        raise ValueError("window_id_invalid")
    if type(limit_per_window) is not int or limit_per_window < 1:
        raise ValueError("limit_per_window_invalid")

    limiter = PersistentFetchRateLimiter(limit_per_window=limit_per_window)
    allowed = [limiter.check_and_consume(requester_id, window_id) for _ in range(limit_per_window)]
    over_limit_allowed = limiter.check_and_consume(requester_id, window_id)
    next_window_allowed = limiter.check_and_consume(requester_id, window_id + 1)

    return {
        "all_within_window_allowed": all(allowed),
        "limit_per_window": limit_per_window,
        "next_window_allowed": next_window_allowed,
        "over_limit_allowed": over_limit_allowed,
        "persistent_limiter_version": PERSISTENT_RATE_LIMITER_VERSION,
        "token": CDL077_RATE_LIMITER_FINAL_REGRESSION_TOKEN,
        "window_id": window_id,
    }


def record_ratification_readiness_verdict(
    *,
    collection_window: Mapping[str, Any],
    limiter_regression: Mapping[str, Any],
    conditions_2_and_3_recorded: bool,
) -> dict[str, Any]:
    """Record whether CDL-087 is ready for a later sensitive ratification phase."""

    if not conditions_2_and_3_recorded:
        verdict = "not_ready"
        blockers = ("conditions_2_and_3_evidence_not_recorded",)
    elif limiter_regression.get("over_limit_allowed") is not False:
        verdict = "not_ready"
        blockers = ("cdl_077_limiter_regression_failed",)
    elif collection_window.get("per_requester_dossiers_included") is not False:
        verdict = "not_ready"
        blockers = ("per_requester_dossiers_forbidden",)
    else:
        verdict = "ready_for_later_sensitive_ratification_review"
        blockers = ()

    return {
        "blockers": list(blockers),
        "conditions_2_and_3_recorded": conditions_2_and_3_recorded,
        "no_ratification_token": NO_CDL087_RATIFICATION_TOKEN,
        "token": CDL087_RATIFICATION_READINESS_TOKEN,
        "verdict": verdict,
    }


def export_observability_json(
    artifact: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_MAX_JSON_BYTES,
) -> str:
    """Export canonical JSON for CDL-087 observability artifacts."""

    payload = json.dumps(
        _canonicalize(artifact),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError("observability_json_size_exceeded")
    return payload


def _normalize_epoch_metrics(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("epoch_metrics_mapping_required")
    epoch_sequence = value.get("epoch_sequence")
    if type(epoch_sequence) is not int or epoch_sequence < 0:
        raise ValueError("epoch_sequence_invalid")

    metrics = value.get("signals")
    if not isinstance(metrics, Mapping):
        raise ValueError("signals_mapping_required")
    _reject_per_requester_keys(metrics)
    missing = set(REQUIRED_CDL087_SIGNAL_NAMES) - set(metrics)
    if missing:
        raise ValueError("required_observability_signal_missing")
    extra = set(metrics) - set(REQUIRED_CDL087_SIGNAL_NAMES)
    if extra:
        raise ValueError("unexpected_observability_signal")

    return {
        "epoch_sequence": epoch_sequence,
        "signals": _canonicalize(metrics),
    }


def _reject_per_requester_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_")
            if "requester" in normalized:
                raise ValueError("per_requester_observability_forbidden")
            _reject_per_requester_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _reject_per_requester_keys(item)


def _canonicalize(value: Any) -> Any:
    if isinstance(value, float):
        raise ValueError("float_values_forbidden")
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    return value


def _require_non_empty_text(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(token)
    return value


def _enforce_json_size(artifact: Mapping[str, Any]) -> None:
    export_observability_json(artifact)
