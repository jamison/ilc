# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 521 validator re-admission runtime."""

from __future__ import annotations

from . import staking_liveness_runtime

RE_ADMISSION_RUNTIME_VERSION = "re_admission_runtime_521.v0.1"
CDL_058_DEPENDENCY = "cdl_058_ratified_520.v0.1"
CDL_055_STAKING_DEPENDENCY = staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION
EXIT_REASONS = frozenset(("liveness_miss", "equivocation", "voluntary_exit"))
COOLDOWN_EPOCHS_LIVENESS_MISS = 2
COOLDOWN_EPOCHS_EQUIVOCATION = 12
COOLDOWN_EPOCHS_VOLUNTARY_EXIT = 1


def _require_non_negative_int(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    return value


def _cooldown_for_exit_reason(exit_reason: str) -> int:
    if exit_reason not in EXIT_REASONS:
        raise ValueError("unrecognized_exit_reason")
    if exit_reason == "liveness_miss":
        return COOLDOWN_EPOCHS_LIVENESS_MISS
    if exit_reason == "equivocation":
        return COOLDOWN_EPOCHS_EQUIVOCATION
    if exit_reason == "voluntary_exit":
        return COOLDOWN_EPOCHS_VOLUNTARY_EXIT
    raise ValueError("recognized_exit_reason_without_cooldown_mapping")


def evaluate_re_admission_eligibility(exit_reason: str, epochs_since_exit: int) -> dict[str, bool | int]:
    cooldown = _cooldown_for_exit_reason(exit_reason)
    elapsed = _require_non_negative_int(epochs_since_exit, "epochs_since_exit")
    remaining = max(0, cooldown - elapsed)
    return {
        "eligible": elapsed >= cooldown,
        "cooldown_remaining": remaining,
    }


__all__ = [
    "CDL_055_STAKING_DEPENDENCY",
    "CDL_058_DEPENDENCY",
    "COOLDOWN_EPOCHS_EQUIVOCATION",
    "COOLDOWN_EPOCHS_LIVENESS_MISS",
    "COOLDOWN_EPOCHS_VOLUNTARY_EXIT",
    "EXIT_REASONS",
    "RE_ADMISSION_RUNTIME_VERSION",
    "evaluate_re_admission_eligibility",
]
