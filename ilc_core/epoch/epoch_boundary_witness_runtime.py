"""Epoch-boundary witness runtime."""

from __future__ import annotations

from ilc_core.validator import staking_liveness_runtime


EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION = "epoch_boundary_witness_blocking_active_phase_1364.v0.1"
CDL_057_DEPENDENCY = "cdl_057_ratified_511.v0.1"
CDL_055_STAKING_DEPENDENCY = staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION
BLOCKING_AUTHORITY_DEFERRED = False


def _require_non_empty_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name}_must_be_non_empty_string")
    return value.strip()


def _require_epoch_id(value: int | str) -> str:
    if isinstance(value, bool):
        raise ValueError("epoch_id_must_be_non_negative_int_or_digit_string")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("epoch_id_must_be_non_negative_int_or_digit_string")
        return str(value)
    epoch = _require_non_empty_string(value, "epoch_id")
    if not epoch.isdigit():
        raise ValueError("epoch_id_must_be_non_negative_int_or_digit_string")
    return epoch


def record_epoch_boundary_witness(validator_id: str, epoch_id: int | str, batch_cid: str) -> dict[str, str]:
    validator = _require_non_empty_string(validator_id, "validator_id")
    epoch = _require_epoch_id(epoch_id)
    batch = _require_non_empty_string(batch_cid, "batch_cid")
    return {
        "status": "witnessed",
        # Blocking scope remains tied to the specific conversion batch.
        "batch_cid": batch,
        "provenance_tag": f"{validator}@epoch_{epoch}",
    }


def is_blocking_authority_active() -> bool:
    return not BLOCKING_AUTHORITY_DEFERRED


__all__ = [
    "BLOCKING_AUTHORITY_DEFERRED",
    "CDL_055_STAKING_DEPENDENCY",
    "CDL_057_DEPENDENCY",
    "EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION",
    "is_blocking_authority_active",
    "record_epoch_boundary_witness",
]
