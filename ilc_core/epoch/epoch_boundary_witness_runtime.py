"""Phase 516 epoch-boundary witness runtime."""

from __future__ import annotations

from ilc_core.validator import staking_liveness_runtime


EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION = "epoch_boundary_witness_runtime_516.v0.1"
CDL_057_DEPENDENCY = "cdl_057_ratified_511.v0.1"
CDL_055_STAKING_DEPENDENCY = staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION
BLOCKING_AUTHORITY_DEFERRED = True


def _require_non_empty_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name}_must_be_non_empty_string")
    return value.strip()


def record_epoch_boundary_witness(validator_id: str, epoch_id: str, batch_cid: str) -> dict[str, str]:
    validator = _require_non_empty_string(validator_id, "validator_id")
    epoch = _require_non_empty_string(epoch_id, "epoch_id")
    _require_non_empty_string(batch_cid, "batch_cid")
    return {
        "status": "witnessed",
        "provenance_tag": f"{validator}@epoch_{epoch}",
    }


def is_blocking_authority_active() -> bool:
    return False


__all__ = [
    "BLOCKING_AUTHORITY_DEFERRED",
    "CDL_055_STAKING_DEPENDENCY",
    "CDL_057_DEPENDENCY",
    "EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION",
    "is_blocking_authority_active",
    "record_epoch_boundary_witness",
]
