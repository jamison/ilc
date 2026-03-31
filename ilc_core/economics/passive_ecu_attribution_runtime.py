"""Phase 550 passive ECU attribution runtime."""

from __future__ import annotations

import math

from ilc_core.network.d2d.centrality_delta_gossip_runtime import (
    CDL_060_GOSSIP_RUNTIME_VERSION as _CDL_060_GOSSIP_RUNTIME_CHECK,
)

PASSIVE_ECU_ATTRIBUTION_RUNTIME_VERSION = "passive_ecu_attribution_runtime_550.v0.1"
CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"
CDL_060_GOSSIP_RUNTIME_DEPENDENCY = "cdl_060_gossip_runtime_548.v0.1"
PASSIVE_ATTRIBUTION_RATE = 0.20
DECAY_FLOOR = 0.05
ATTRIBUTION_CAP = 0.15
GAMMA = 0.15

assert _CDL_060_GOSSIP_RUNTIME_CHECK == CDL_060_GOSSIP_RUNTIME_DEPENDENCY, (
    f"dep chain mismatch: {_CDL_060_GOSSIP_RUNTIME_CHECK}"
)
assert PASSIVE_ATTRIBUTION_RATE * (1.0 + GAMMA) < 1.0, (
    "authorship_primacy_invariant_violated: passive rate exceeds direct reward"
)
assert ATTRIBUTION_CAP < 1.0, (
    "authorship_primacy_invariant_violated: attribution cap exceeds direct reward"
)


def quality_factor(q_i: float) -> float:
    """Compute the bounded quality multiplier for a normalized quality score."""

    if isinstance(q_i, bool) or not isinstance(q_i, (int, float)):
        raise ValueError("q_i_must_be_float_in_unit_interval")
    normalized = float(q_i)
    if not math.isfinite(normalized) or normalized < 0.0 or normalized > 1.0:
        raise ValueError("q_i_must_be_float_in_unit_interval")
    return round(1.0 + GAMMA * (2.0 * normalized - 1.0), 12)


def compute_passive_ecu(base_reward: float, centrality_score: float, q_i: float) -> float:
    """Compute passive ECU attribution for one reuse path."""

    if isinstance(base_reward, bool) or not isinstance(base_reward, (int, float)):
        raise ValueError("base_reward_must_be_non_negative_float")
    normalized_base_reward = float(base_reward)
    if not math.isfinite(normalized_base_reward) or normalized_base_reward < 0.0:
        raise ValueError("base_reward_must_be_non_negative_float")
    if normalized_base_reward == 0.0:
        return 0.0

    if isinstance(centrality_score, bool) or not isinstance(centrality_score, (int, float)):
        raise ValueError("centrality_score_must_be_non_negative_float")
    normalized_centrality = float(centrality_score)
    if (
        not math.isfinite(normalized_centrality)
        or normalized_centrality < 0.0
        or normalized_centrality > 1.0
    ):
        raise ValueError("centrality_score_must_be_non_negative_float")
    if normalized_centrality < DECAY_FLOOR:
        return 0.0

    raw = (
        normalized_base_reward
        * PASSIVE_ATTRIBUTION_RATE
        * normalized_centrality
        * quality_factor(q_i)
    )
    return round(min(raw, normalized_base_reward * ATTRIBUTION_CAP), 12)
