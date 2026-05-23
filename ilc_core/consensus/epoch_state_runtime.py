# SPDX-License-Identifier: AGPL-3.0-or-later
"""Phase-444 epoch-state and quorum-record runtime surfaces."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


EPOCH_STATE_RUNTIME_VERSION = "epoch_state_runtime_444.v0.1"
CDL_051_RATIFICATION_DEPENDENCY = "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"

_ALLOWED_FINALITY_STATUSES = {"provisional", "finalized", "conflict"}

_CANONICAL_VECTOR_SPECS: list[dict[str, Any]] = [
    {
        "quorum_records": [
            {
                "attestation_ref": "attest:epoch-7:validator-a:block-alpha",
                "block_hash": "block-alpha",
                "epoch_index": 7,
                "quorum_state_digest": "quorum-state-7",
                "validator_id": "validator-a",
                "vote_weight": 40,
            },
            {
                "attestation_ref": "attest:epoch-7:validator-b:block-alpha",
                "block_hash": "block-alpha",
                "epoch_index": 7,
                "quorum_state_digest": "quorum-state-7",
                "validator_id": "validator-b",
                "vote_weight": 35,
            },
        ],
        "epoch_state": {
            "candidate_block_hash": "block-alpha",
            "epoch_index": 7,
            "finality_status": "finalized",
            "parent_epoch_state_digest": "state-6-root",
            "quorum_record_digests": [],
            "quorum_state_digest": "quorum-state-7",
            "quorum_threshold": {"numerator": 2, "denominator": 3},
        },
    },
    {
        "quorum_records": [
            {
                "attestation_ref": "attest:epoch-8:validator-a:block-beta",
                "block_hash": "block-beta",
                "epoch_index": 8,
                "quorum_state_digest": "quorum-state-8",
                "validator_id": "validator-a",
                "vote_weight": 34,
            },
            {
                "attestation_ref": "attest:epoch-8:validator-b:block-gamma",
                "block_hash": "block-gamma",
                "epoch_index": 8,
                "quorum_state_digest": "quorum-state-8",
                "validator_id": "validator-b",
                "vote_weight": 33,
            },
        ],
        "epoch_state": {
            "candidate_block_hash": "block-beta",
            "epoch_index": 8,
            "finality_status": "conflict",
            "parent_epoch_state_digest": "state-7-root",
            "quorum_record_digests": [],
            "quorum_state_digest": "quorum-state-8",
            "quorum_threshold": {"numerator": 2, "denominator": 3},
        },
    },
]


class ConsensusEpochStateValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _check(check_type: str, passed: bool) -> dict[str, Any]:
    return {"check_type": check_type, "passed": passed}


def _require_mapping(value: Any, token: str, message: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConsensusEpochStateValidationError(token, message)
    return value


def _require_non_empty_str(raw: Any, token: str, message: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ConsensusEpochStateValidationError(token, message)
    return raw


def _require_epoch_index(raw: Any, token: str, message: str) -> int:
    if type(raw) is not int or raw < 0:
        raise ConsensusEpochStateValidationError(token, message)
    return raw


def _require_positive_number(raw: Any, token: str, message: str) -> int:
    # Phase 1235: quorum-record vote_weight follows Genesis bootstrap positive-int intent.
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ConsensusEpochStateValidationError(token, message)
    if raw <= 0:
        raise ConsensusEpochStateValidationError(token, message)
    return raw


def _normalize_quorum_threshold(raw: Any) -> dict[str, int]:
    if raw is None:
        raise ConsensusEpochStateValidationError(
            "consensus_epoch_state_quorum_threshold_missing",
            "quorum_threshold is required",
        )
    data = _require_mapping(
        raw,
        "consensus_epoch_state_quorum_threshold_invalid",
        "quorum_threshold must be an object",
    )
    numerator = data.get("numerator")
    denominator = data.get("denominator")
    if type(numerator) is not int or numerator <= 0:
        raise ConsensusEpochStateValidationError(
            "consensus_epoch_state_quorum_threshold_invalid",
            "quorum_threshold.numerator must be a positive integer",
        )
    if type(denominator) is not int or denominator <= 0:
        raise ConsensusEpochStateValidationError(
            "consensus_epoch_state_quorum_threshold_invalid",
            "quorum_threshold.denominator must be a positive integer",
        )
    if numerator > denominator:
        raise ConsensusEpochStateValidationError(
            "consensus_epoch_state_quorum_threshold_invalid",
            "quorum_threshold numerator cannot exceed denominator",
        )
    return {"numerator": numerator, "denominator": denominator}


def _normalize_quorum_record_digests(raw: Any) -> list[str]:
    if not isinstance(raw, list) or not raw:
        raise ConsensusEpochStateValidationError(
            "consensus_epoch_state_quorum_record_digests_invalid",
            "quorum_record_digests must be a non-empty list",
        )
    digests: list[str] = []
    for entry in raw:
        digests.append(
            _require_non_empty_str(
                entry,
                "consensus_epoch_state_quorum_record_digests_invalid",
                "quorum_record_digests entries must be non-empty strings",
            )
        )
    return sorted(set(digests))


def _normalize_quorum_record(raw_record: Any) -> dict[str, Any]:
    data = _require_mapping(
        raw_record,
        "consensus_quorum_record_not_object",
        "quorum record must be an object",
    )
    digest_payload = {
        "attestation_ref": _require_non_empty_str(
            data.get("attestation_ref"),
            "consensus_quorum_record_attestation_ref_missing",
            "attestation_ref is required",
        ),
        "block_hash": _require_non_empty_str(
            data.get("block_hash"),
            "consensus_quorum_record_block_hash_missing",
            "block_hash is required",
        ),
        "epoch_index": _require_epoch_index(
            data.get("epoch_index"),
            "consensus_quorum_record_epoch_index_invalid",
            "epoch_index must be an integer >= 0",
        ),
        "quorum_state_digest": _require_non_empty_str(
            data.get("quorum_state_digest"),
            "consensus_quorum_record_quorum_state_digest_missing",
            "quorum_state_digest is required",
        ),
        "validator_id": _require_non_empty_str(
            data.get("validator_id"),
            "consensus_quorum_record_validator_id_missing",
            "validator_id is required",
        ),
        "vote_weight": _require_positive_number(
            data.get("vote_weight"),
            "consensus_quorum_record_vote_weight_invalid",
            "vote_weight must be > 0",
        ),
    }
    record_digest = _stable_sha256(digest_payload)
    return {
        "attestation_ref": digest_payload["attestation_ref"],
        "block_hash": digest_payload["block_hash"],
        "epoch_index": digest_payload["epoch_index"],
        "quorum_state_digest": digest_payload["quorum_state_digest"],
        "record_digest": record_digest,
        "validator_id": digest_payload["validator_id"],
        "vote_weight": digest_payload["vote_weight"],
    }


def _normalize_epoch_state_record(raw_record: Any) -> dict[str, Any]:
    data = _require_mapping(
        raw_record,
        "consensus_epoch_state_not_object",
        "epoch state record must be an object",
    )
    finality_status = _require_non_empty_str(
        data.get("finality_status"),
        "consensus_epoch_state_finality_status_invalid",
        "finality_status is required",
    )
    if finality_status not in _ALLOWED_FINALITY_STATUSES:
        raise ConsensusEpochStateValidationError(
            "consensus_epoch_state_finality_status_invalid",
            "unsupported finality_status",
        )

    normalized = {
        "candidate_block_hash": _require_non_empty_str(
            data.get("candidate_block_hash"),
            "consensus_epoch_state_candidate_block_hash_missing",
            "candidate_block_hash is required",
        ),
        "epoch_index": _require_epoch_index(
            data.get("epoch_index"),
            "consensus_epoch_state_epoch_index_invalid",
            "epoch_index must be an integer >= 0",
        ),
        "finality_status": finality_status,
        "parent_epoch_state_digest": _require_non_empty_str(
            data.get("parent_epoch_state_digest"),
            "consensus_epoch_state_parent_digest_missing",
            "parent_epoch_state_digest is required",
        ),
        "quorum_record_digests": _normalize_quorum_record_digests(data.get("quorum_record_digests")),
        "quorum_state_digest": _require_non_empty_str(
            data.get("quorum_state_digest"),
            "consensus_epoch_state_quorum_state_digest_missing",
            "quorum_state_digest is required",
        ),
        "quorum_threshold": _normalize_quorum_threshold(data.get("quorum_threshold")),
    }
    digest_payload = dict(normalized)
    normalized["state_digest"] = _stable_sha256(digest_payload)
    return normalized


def canonical_epoch_state_vectors() -> list[dict[str, Any]]:
    vectors = copy.deepcopy(_CANONICAL_VECTOR_SPECS)
    for vector in vectors:
        digests = [generate_quorum_record(raw)["record_digest"] for raw in vector["quorum_records"]]
        vector["epoch_state"]["quorum_record_digests"] = sorted(set(digests))
    return vectors


def generate_quorum_record(raw_record: Any) -> dict[str, Any]:
    return _normalize_quorum_record(raw_record)


def verify_quorum_record(record: Any) -> dict[str, Any]:
    normalized = _normalize_quorum_record(record)
    source = _require_mapping(
        record,
        "consensus_quorum_record_not_object",
        "quorum record must be an object",
    )
    actual_digest = source.get("record_digest")
    checks = [
        _check("epoch_index_valid", True),
        _check("validator_id_present", True),
        _check("block_hash_present", True),
        _check("quorum_state_digest_present", True),
        _check("vote_weight_positive", True),
        _check("attestation_ref_present", True),
        _check("record_digest_matches", actual_digest == normalized["record_digest"]),
    ]
    return {
        "valid": all(item["passed"] for item in checks),
        "record_digest": normalized["record_digest"],
        "runtime_version": EPOCH_STATE_RUNTIME_VERSION,
        "dependency": CDL_051_RATIFICATION_DEPENDENCY,
        "checks": checks,
    }


def generate_epoch_state_record(raw_record: Any) -> dict[str, Any]:
    return _normalize_epoch_state_record(raw_record)


def verify_epoch_state_record(record: Any) -> dict[str, Any]:
    normalized = _normalize_epoch_state_record(record)
    source = _require_mapping(
        record,
        "consensus_epoch_state_not_object",
        "epoch state record must be an object",
    )
    actual_digest = source.get("state_digest")
    checks = [
        _check("epoch_index_valid", True),
        _check("candidate_block_hash_present", True),
        _check("quorum_state_digest_present", True),
        _check("parent_epoch_state_digest_present", True),
        _check("quorum_threshold_valid", True),
        _check("quorum_record_digests_non_empty", True),
        _check("finality_status_supported", True),
        _check("state_digest_matches", actual_digest == normalized["state_digest"]),
    ]
    return {
        "valid": all(item["passed"] for item in checks),
        "state_digest": normalized["state_digest"],
        "runtime_version": EPOCH_STATE_RUNTIME_VERSION,
        "dependency": CDL_051_RATIFICATION_DEPENDENCY,
        "checks": checks,
    }


__all__ = [
    "CDL_051_RATIFICATION_DEPENDENCY",
    "EPOCH_STATE_RUNTIME_VERSION",
    "ConsensusEpochStateValidationError",
    "canonical_epoch_state_vectors",
    "generate_epoch_state_record",
    "generate_quorum_record",
    "verify_epoch_state_record",
    "verify_quorum_record",
]
