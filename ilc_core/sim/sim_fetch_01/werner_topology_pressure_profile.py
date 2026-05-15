"""Phase 1269 Werner default topology-pressure profile adapter.

This module is simulation/evidence only. It records an explicit
``topology_pressure_model`` selector over the existing SIM-FETCH Werner overlay
without authorizing ECU minting, ILC settlement, public claimability, or CDL-087
ratification.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Mapping

from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import run_sim_fetch_01


WERNER_DEFAULT_TOPOLOGY_PRESSURE_PROFILE_VERSION = (
    "werner_default_topology_pressure_profile_phase_1269.v0.1"
)
TOPOLOGY_PRESSURE_MODEL_WERNER_V1_TOKEN = (
    "topology_pressure_model_werner_v1_profile_recorded_phase_1269"
)
WERNER_NONE_PROFILE_CONTROL_TOKEN = "werner_none_profile_control_preserved_phase_1269"
NO_WERNER_ECU_MINTING_OR_ILC_SETTLEMENT_TOKEN = (
    "no_werner_ecu_minting_or_ilc_settlement_phase_1269"
)

TOPOLOGY_PRESSURE_MODEL_WERNER_V1 = "werner_v1"
TOPOLOGY_PRESSURE_MODEL_NONE = "none"
DEFAULT_WERNER_SMOOTHING_ALPHA = "0.50"
DEFAULT_WERNER_HEAT_SIGNAL_THRESHOLD = 50
DEFAULT_WERNER_COOLING_SIGNAL_THRESHOLD = 2
DEFAULT_WERNER_PRESSURE_TIERS = ("B", "C")
DEFAULT_WERNER_PROFILE_MAX_BYTES = 5_000_000


def _reject_float_tree(value: Any, path: str) -> None:
    if isinstance(value, float):
        raise ValueError(f"werner_profile_float_forbidden:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("werner_profile_mapping_keys_must_be_strings")
            _reject_float_tree(item, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float_tree(item, f"{path}[{index}]")


def _prepare_for_export(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        raise ValueError("werner_profile_float_forbidden")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("werner_profile_decimal_must_be_finite")
        return str(value)
    if isinstance(value, Mapping):
        return {
            str(key): _prepare_for_export(item)
            for key, item in sorted(value.items(), key=lambda entry: str(entry[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_prepare_for_export(item) for item in value]
    return value


def _normalize_topology_pressure_model(model: str) -> str:
    if not isinstance(model, str) or not model.strip():
        raise ValueError("werner_profile_topology_pressure_model_invalid")
    normalized = model.strip().lower()
    if normalized not in {TOPOLOGY_PRESSURE_MODEL_WERNER_V1, TOPOLOGY_PRESSURE_MODEL_NONE}:
        raise ValueError("werner_profile_topology_pressure_model_unsupported")
    return normalized


def build_werner_topology_pressure_profile_config(
    base_config: Mapping[str, object],
    *,
    topology_pressure_model: str = TOPOLOGY_PRESSURE_MODEL_WERNER_V1,
) -> dict[str, Any]:
    """Return a SIM-FETCH config with an explicit topology-pressure profile."""

    if not isinstance(base_config, Mapping):
        raise ValueError("werner_profile_base_config_must_be_mapping")
    _reject_float_tree(base_config, "base_config")
    model = _normalize_topology_pressure_model(topology_pressure_model)
    profile_config = dict(base_config)
    profile_config["topology_pressure_model"] = model
    if model == TOPOLOGY_PRESSURE_MODEL_WERNER_V1:
        profile_config["werner_overlay_enabled"] = True
        profile_config.setdefault("werner_smoothing_alpha", DEFAULT_WERNER_SMOOTHING_ALPHA)
        profile_config.setdefault(
            "werner_heat_signal_threshold",
            DEFAULT_WERNER_HEAT_SIGNAL_THRESHOLD,
        )
        profile_config.setdefault(
            "werner_cooling_signal_threshold",
            DEFAULT_WERNER_COOLING_SIGNAL_THRESHOLD,
        )
        profile_config.setdefault("werner_pressure_tiers", list(DEFAULT_WERNER_PRESSURE_TIERS))
    else:
        profile_config["werner_overlay_enabled"] = False
    return profile_config


def run_werner_topology_pressure_profile(
    base_config: Mapping[str, object],
    *,
    topology_pressure_model: str = TOPOLOGY_PRESSURE_MODEL_WERNER_V1,
) -> dict[str, Any]:
    """Run SIM-FETCH with an explicit Werner or none topology-pressure profile."""

    profile_config = build_werner_topology_pressure_profile_config(
        base_config,
        topology_pressure_model=topology_pressure_model,
    )
    model = profile_config["topology_pressure_model"]
    sim_result = run_sim_fetch_01(profile_config)
    aggregate = sim_result["aggregate_over_epochs"]
    return {
        "authorization": {
            "cdl_087_authorized": False,
            "ecu_mint_authorized": False,
            "ilc_settlement_authorized": False,
            "public_claimability_authorized": False,
            "runtime_policy_authorized": False,
        },
        "non_authorization_note": (
            "Werner topology pressure profile is simulation evidence only; it does not "
            "mint ECU, settle ILC, authorize public claimability, authorize CDL-087, "
            "or activate runtime economic policy."
        ),
        "profile_config": profile_config,
        "profile_metrics": {
            "werner_ecu_pressure_mint_authorized": aggregate[
                "werner_ecu_pressure_mint_authorized"
            ],
            "werner_ecu_pressure_signal_by_tier": aggregate[
                "werner_ecu_pressure_signal_by_tier"
            ],
            "werner_heat_signal_count_by_tier": aggregate[
                "werner_heat_signal_count_by_tier"
            ],
            "werner_ilc_settlement_authorized": aggregate[
                "werner_ilc_settlement_authorized"
            ],
            "werner_overlay_enabled": aggregate["werner_overlay_enabled"],
            "werner_raw_pressure_by_epoch_by_tier": aggregate[
                "werner_raw_pressure_by_epoch_by_tier"
            ],
            "werner_smoothed_pressure_by_epoch_by_tier": aggregate[
                "werner_smoothed_pressure_by_epoch_by_tier"
            ],
            "werner_topology_recommendation_by_tier": aggregate[
                "werner_topology_recommendation_by_tier"
            ],
        },
        "sim_result": sim_result,
        "tokens": [
            WERNER_DEFAULT_TOPOLOGY_PRESSURE_PROFILE_VERSION,
            TOPOLOGY_PRESSURE_MODEL_WERNER_V1_TOKEN,
            WERNER_NONE_PROFILE_CONTROL_TOKEN,
            NO_WERNER_ECU_MINTING_OR_ILC_SETTLEMENT_TOKEN,
        ],
        "topology_pressure_model": model,
        "version": WERNER_DEFAULT_TOPOLOGY_PRESSURE_PROFILE_VERSION,
    }


def export_werner_topology_pressure_profile_json(
    payload: Mapping[str, object],
    *,
    max_bytes: int = DEFAULT_WERNER_PROFILE_MAX_BYTES,
) -> str:
    """Canonical JSON export for Phase 1269 Werner profile evidence."""

    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("werner_profile_invalid_json_max_bytes")
    _reject_float_tree(payload, "payload")
    prepared = _prepare_for_export(payload)
    body = json.dumps(
        prepared,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    if len(body.encode("utf-8")) > max_bytes:
        raise ValueError("werner_profile_json_max_bytes_exceeded")
    return body
