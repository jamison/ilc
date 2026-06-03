# SPDX-License-Identifier: AGPL-3.0-only
"""Genesis validator bootstrap runtime."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from ilc_core.consensus.finality_evaluator import CDL_051_RATIFICATION_DEPENDENCY
from ilc_core.identity.agent_id_runtime import CDL_042_DEPENDENCY, derive_agent_id

GENESIS_BOOTSTRAP_VERSION = "genesis_validator_bootstrap_runtime_480.v0.1"


@dataclass(frozen=True)
class GenesisBootstrapError(ValueError):
    token: str
    message: str

    def __str__(self) -> str:
        return self.message


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _expected_quorum_record_seed(genesis_block_cid: str, validator_set_hash: str) -> str:
    return _stable_sha256_text(f"{genesis_block_cid}:{validator_set_hash}")


def _decode_public_key_b64url(public_key_b64url: str) -> bytes:
    if not isinstance(public_key_b64url, str) or not public_key_b64url:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_PUBLIC_KEY",
            "public_key_b64url must be a non-empty string",
        )
    padding = "=" * ((4 - len(public_key_b64url) % 4) % 4)
    try:
        public_key_bytes = base64.urlsafe_b64decode(public_key_b64url + padding)
    except Exception as exc:  # pragma: no cover - deterministic token path
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_PUBLIC_KEY",
            "public_key_b64url must be valid base64url",
        ) from exc
    if len(public_key_bytes) != 32:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_PUBLIC_KEY",
            "Ed25519 public keys must decode to 32 bytes",
        )
    return public_key_bytes


def generate_validator_enrollment_record(
    public_key_b64url: str,
    cluster_id: str,
    vote_weight: int,
    enrolled_by: str,
    display_name: str | None = None,
) -> dict[str, Any]:
    public_key_bytes = _decode_public_key_b64url(public_key_b64url)
    if not isinstance(cluster_id, str) or not cluster_id:
        raise GenesisBootstrapError("GENESIS_BOOTSTRAP_INVALID_CLUSTER_ID", "cluster_id must be non-empty")
    if not isinstance(vote_weight, int) or vote_weight <= 0:
        raise GenesisBootstrapError("GENESIS_BOOTSTRAP_INVALID_VOTE_WEIGHT", "vote_weight must be positive int")
    if not isinstance(enrolled_by, str) or not enrolled_by:
        raise GenesisBootstrapError("GENESIS_BOOTSTRAP_INVALID_ENROLLED_BY", "enrolled_by must be non-empty")
    record: dict[str, Any] = {
        "validator_id": derive_agent_id(public_key_bytes),
        "public_key_b64url": public_key_b64url,
        "cluster_id": cluster_id,
        "vote_weight": vote_weight,
        "epoch_zero": 0,
        "enrolled_by": enrolled_by,
    }
    if display_name is not None:
        record["display_name"] = display_name
    return record


def verify_genesis_enrollment(enrollment_record: dict) -> None:
    if not isinstance(enrollment_record, dict):
        raise GenesisBootstrapError("GENESIS_BOOTSTRAP_INVALID_ENROLLMENT", "enrollment_record must be dict")
    required_fields = (
        "validator_id",
        "public_key_b64url",
        "cluster_id",
        "vote_weight",
        "epoch_zero",
        "enrolled_by",
    )
    for field in required_fields:
        if field not in enrollment_record:
            raise GenesisBootstrapError(
                "GENESIS_BOOTSTRAP_MISSING_REQUIRED_FIELD",
                f"enrollment_record missing field: {field}",
            )
    public_key_bytes = _decode_public_key_b64url(enrollment_record["public_key_b64url"])
    expected_validator_id = derive_agent_id(public_key_bytes)
    if enrollment_record["validator_id"] != expected_validator_id:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_VALIDATOR_ID",
            "validator_id does not match CDL-042 derivation",
        )
    if enrollment_record["epoch_zero"] != 0:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_EPOCH_ZERO",
            "epoch_zero must equal 0",
        )
    if not isinstance(enrollment_record["vote_weight"], int) or enrollment_record["vote_weight"] <= 0:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_VOTE_WEIGHT",
            "vote_weight must be positive int",
        )


def materialize_epoch_zero_state(
    genesis_block_cid: str,
    validator_enrollment_records: list[dict],
) -> dict[str, Any]:
    if not isinstance(genesis_block_cid, str) or not genesis_block_cid:
        raise GenesisBootstrapError("GENESIS_BOOTSTRAP_INVALID_GENESIS_BLOCK", "genesis_block_cid must be non-empty")
    if not isinstance(validator_enrollment_records, list) or not validator_enrollment_records:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_VALIDATOR_SET",
            "validator_enrollment_records must be a non-empty list",
        )
    normalized_records: list[dict[str, Any]] = []
    for record in validator_enrollment_records:
        verify_genesis_enrollment(record)
        normalized_records.append(dict(record))
    normalized_records.sort(key=lambda record: record["validator_id"])
    validator_set_hash = _stable_sha256_text(_stable_json(normalized_records))
    quorum_record_seed = _expected_quorum_record_seed(genesis_block_cid, validator_set_hash)
    return {
        "epoch": 0,
        "genesis_block_cid": genesis_block_cid,
        "quorum_record_seed": quorum_record_seed,
        "validator_set_hash": validator_set_hash,
    }


def verify_epoch_zero_state(epoch_zero_state: dict) -> None:
    if not isinstance(epoch_zero_state, dict):
        raise GenesisBootstrapError("GENESIS_BOOTSTRAP_INVALID_EPOCH_STATE", "epoch_zero_state must be dict")
    required_fields = ("epoch", "genesis_block_cid", "quorum_record_seed", "validator_set_hash")
    for field in required_fields:
        if field not in epoch_zero_state:
            raise GenesisBootstrapError(
                "GENESIS_BOOTSTRAP_MISSING_REQUIRED_FIELD",
                f"epoch_zero_state missing field: {field}",
            )
    if epoch_zero_state["epoch"] != 0:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_EPOCH_STATE",
            "epoch_zero_state.epoch must equal 0",
        )
    for field in ("genesis_block_cid", "quorum_record_seed", "validator_set_hash"):
        if not isinstance(epoch_zero_state[field], str) or not epoch_zero_state[field]:
            raise GenesisBootstrapError(
                "GENESIS_BOOTSTRAP_INVALID_EPOCH_STATE",
                f"{field} must be a non-empty string",
            )
    expected_quorum_record_seed = _expected_quorum_record_seed(
        epoch_zero_state["genesis_block_cid"],
        epoch_zero_state["validator_set_hash"],
    )
    if epoch_zero_state["quorum_record_seed"] != expected_quorum_record_seed:
        raise GenesisBootstrapError(
            "GENESIS_BOOTSTRAP_INVALID_EPOCH_STATE",
            "quorum_record_seed does not match genesis_block_cid and validator_set_hash",
        )
