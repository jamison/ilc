"""Validator trust-tier runtime.

The consensus-dispute tiebreaker never sorts candidates internally. Callers must provide
deterministic candidate ordering, because the first candidate becomes the fallback winner
when no trust-tier candidate is available.
"""

from __future__ import annotations

from . import staking_liveness_runtime

TRUST_TIER_RUNTIME_VERSION = "trust_tier_runtime_507.v0.1"
CDL_056_DEPENDENCY = "cdl_056_ratified_501.v0.1"
CDL_055_STAKING_DEPENDENCY = staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION
CONSENSUS_DISPUTE_TYPES = frozenset(("block_proposal", "equivocation", "fork_choice"))


def _require_non_negative_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name}_must_be_positive_int")


def is_trust_tier_eligible(
    consecutive_missed_epochs: int,
    liveness_miss_threshold: int,
    equivocation_state: bool,
) -> bool:
    _require_non_negative_int(consecutive_missed_epochs, "consecutive_missed_epochs")
    _require_positive_int(liveness_miss_threshold, "liveness_miss_threshold")
    if not isinstance(equivocation_state, bool):
        raise ValueError("equivocation_state_must_be_bool")
    if equivocation_state:
        return False
    return consecutive_missed_epochs < liveness_miss_threshold


def revoke_trust_tier_if_below_threshold(
    current_flag: bool,
    consecutive_missed_epochs: int,
    liveness_miss_threshold: int,
) -> bool:
    if not isinstance(current_flag, bool):
        raise ValueError("current_flag_must_be_bool")
    _require_non_negative_int(consecutive_missed_epochs, "consecutive_missed_epochs")
    _require_positive_int(liveness_miss_threshold, "liveness_miss_threshold")
    if not current_flag:
        return False
    return consecutive_missed_epochs < liveness_miss_threshold


def apply_consensus_dispute_tiebreaker(
    dispute_type: str,
    candidates: list[dict[str, object]],
) -> dict[str, object] | None:
    """Return the trust-tier winner or the first caller-supplied candidate deterministically."""
    if dispute_type not in CONSENSUS_DISPUTE_TYPES:
        raise ValueError("non_consensus_dispute_type")
    if not candidates:
        return None
    trust_tier_candidates = [
        candidate for candidate in candidates if bool(candidate.get("trust_tier", False))
    ]
    if trust_tier_candidates:
        return trust_tier_candidates[0]
    # Caller-supplied ordering is the deterministic fallback when no trust-tier flag is present.
    return candidates[0]


__all__ = [
    "CDL_055_STAKING_DEPENDENCY",
    "CDL_056_DEPENDENCY",
    "CONSENSUS_DISPUTE_TYPES",
    "TRUST_TIER_RUNTIME_VERSION",
    "apply_consensus_dispute_tiebreaker",
    "is_trust_tier_eligible",
    "revoke_trust_tier_if_below_threshold",
]
