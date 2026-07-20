# SPDX-License-Identifier: AGPL-3.0-only
"""Phase-312 genesis state bundle generator/verifier runtime."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Iterable


GENESIS_BUNDLE_RUNTIME_VERSION = "genesis_state_bundle_312.v0.1"
SCHEMA_BASELINE_DEPENDENCY = "d2_schema_baseline_310.v0.1"
CEREMONY_REQUIRED_STEPS = (
    "prepare_bundle",
    "announce_signers",
    "collect_attestations",
    "finalize_bundle",
)


CANONICAL_GENESIS_VECTORS: list[dict[str, Any]] = [
    {
        "bundle": {
            "bundle_id": "genesis-mainnet-0",
            "epoch_zero": 0,
            "network": "mainnet",
            "allocations": [{"account": "genesis-core", "units": 1000}],
            "signers": [
                {"signer_id": "signer-a", "signature": "sig-a"},
                {"signer_id": "signer-b", "signature": "sig-b"},
            ],
        },
        "ceremony": [
            {"step": "prepare_bundle", "actor": "coordinator"},
            {"step": "announce_signers", "actor": "coordinator"},
            {"step": "collect_attestations", "actor": "signer-a"},
            {"step": "finalize_bundle", "actor": "coordinator"},
        ],
    },
    {
        "bundle": {
            "bundle_id": "genesis-testnet-0",
            "epoch_zero": 0,
            "network": "testnet",
            "allocations": [{"account": "genesis-test", "units": 500}],
            "signers": [
                {"signer_id": "signer-x", "signature": "sig-x"},
                {"signer_id": "signer-y", "signature": "sig-y"},
            ],
        },
        "ceremony": [
            {"step": "prepare_bundle", "actor": "coordinator"},
            {"step": "announce_signers", "actor": "coordinator"},
            {"step": "collect_attestations", "actor": "signer-x"},
            {"step": "finalize_bundle", "actor": "coordinator"},
        ],
    },
]


class GenesisBundleValidationError(ValueError):
    """Typed validation exception with deterministic error token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _sorted_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sorted_mapping(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, list):
        return [_sorted_mapping(item) for item in value]
    return value


def _coerce_list(value: Any, token: str, message: str) -> list[Any]:
    if not isinstance(value, list):
        raise GenesisBundleValidationError(token, message)
    return value


def _normalize_signers(raw_signers: Any, bundle_id: str) -> list[dict[str, str]]:
    signers = _coerce_list(raw_signers, "genesis_bundle_signers_not_list", "signers_not_list")
    if not signers:
        raise GenesisBundleValidationError("genesis_bundle_signers_empty", f"signers_empty:{bundle_id}")
    normalized: list[dict[str, str]] = []
    signer_ids: set[str] = set()
    for signer in signers:
        if not isinstance(signer, dict):
            raise GenesisBundleValidationError(
                "genesis_bundle_signer_not_object",
                f"signer_not_object:{bundle_id}",
            )
        signer_id = signer.get("signer_id")
        signature = signer.get("signature")
        if not isinstance(signer_id, str) or not signer_id.strip():
            raise GenesisBundleValidationError(
                "genesis_bundle_signer_id_missing",
                f"signer_id_missing:{bundle_id}",
            )
        if not isinstance(signature, str) or not signature.strip():
            raise GenesisBundleValidationError(
                "genesis_bundle_signature_missing",
                f"signature_missing:{bundle_id}:{signer_id}",
            )
        if signer_id in signer_ids:
            raise GenesisBundleValidationError(
                "genesis_bundle_duplicate_signer",
                f"duplicate_signer:{bundle_id}:{signer_id}",
            )
        signer_ids.add(signer_id)
        normalized.append({"signature": signature, "signer_id": signer_id})
    return sorted(normalized, key=lambda item: item["signer_id"])


def _normalize_allocations(raw_allocations: Any, bundle_id: str) -> list[dict[str, Any]]:
    allocations = _coerce_list(
        raw_allocations,
        "genesis_bundle_allocations_not_list",
        "allocations_not_list",
    )
    if not allocations:
        raise GenesisBundleValidationError(
            "genesis_bundle_allocations_empty",
            f"allocations_empty:{bundle_id}",
        )
    normalized: list[dict[str, Any]] = []
    for allocation in allocations:
        if not isinstance(allocation, dict):
            raise GenesisBundleValidationError(
                "genesis_bundle_allocation_not_object",
                f"allocation_not_object:{bundle_id}",
            )
        account = allocation.get("account")
        units = allocation.get("units")
        if not isinstance(account, str) or not account.strip():
            raise GenesisBundleValidationError(
                "genesis_bundle_allocation_account_missing",
                f"allocation_account_missing:{bundle_id}",
            )
        if not isinstance(units, int) or units < 0:
            raise GenesisBundleValidationError(
                "genesis_bundle_allocation_units_invalid",
                f"allocation_units_invalid:{bundle_id}:{account}",
            )
        normalized.append({"account": account, "units": units})
    return sorted(normalized, key=lambda item: item["account"])


def _normalize_bundle(raw_bundle: Any) -> dict[str, Any]:
    if not isinstance(raw_bundle, dict):
        raise GenesisBundleValidationError("genesis_bundle_not_object", "bundle_not_object")

    bundle_id = raw_bundle.get("bundle_id")
    if not isinstance(bundle_id, str) or not bundle_id.strip():
        raise GenesisBundleValidationError("genesis_bundle_id_missing", "bundle_id_missing")

    epoch_zero = raw_bundle.get("epoch_zero")
    if not isinstance(epoch_zero, int) or epoch_zero < 0:
        raise GenesisBundleValidationError(
            "genesis_bundle_epoch_zero_invalid",
            f"epoch_zero_invalid:{bundle_id}",
        )

    network = raw_bundle.get("network")
    if not isinstance(network, str) or not network.strip():
        raise GenesisBundleValidationError(
            "genesis_bundle_network_missing",
            f"network_missing:{bundle_id}",
        )

    normalized = {
        "allocations": _normalize_allocations(raw_bundle.get("allocations"), bundle_id),
        "bundle_id": bundle_id,
        "epoch_zero": epoch_zero,
        "network": network,
        "signers": _normalize_signers(raw_bundle.get("signers"), bundle_id),
    }
    return normalized


def _normalize_ceremony(raw_ceremony: Any, bundle_id: str) -> list[dict[str, str]]:
    ceremony = _coerce_list(
        raw_ceremony,
        "genesis_ceremony_not_list",
        f"ceremony_not_list:{bundle_id}",
    )
    if not ceremony:
        raise GenesisBundleValidationError(
            "genesis_ceremony_empty",
            f"ceremony_empty:{bundle_id}",
        )

    normalized: list[dict[str, str]] = []
    for entry in ceremony:
        if not isinstance(entry, dict):
            raise GenesisBundleValidationError(
                "genesis_ceremony_entry_not_object",
                f"ceremony_entry_not_object:{bundle_id}",
            )
        step = entry.get("step")
        actor = entry.get("actor")
        if not isinstance(step, str) or not step.strip():
            raise GenesisBundleValidationError(
                "genesis_ceremony_step_missing",
                f"ceremony_step_missing:{bundle_id}",
            )
        if not isinstance(actor, str) or not actor.strip():
            raise GenesisBundleValidationError(
                "genesis_ceremony_actor_missing",
                f"ceremony_actor_missing:{bundle_id}:{step}",
            )
        normalized.append({"actor": actor, "step": step})

    ordered_steps = [entry["step"] for entry in normalized]
    if tuple(ordered_steps) != CEREMONY_REQUIRED_STEPS:
        raise GenesisBundleValidationError(
            "genesis_ceremony_sequence_invalid",
            f"ceremony_sequence_invalid:{bundle_id}:{ordered_steps}",
        )

    return normalized


def _normalize_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise GenesisBundleValidationError("genesis_payload_not_object", "payload_not_object")
    bundle = _normalize_bundle(payload.get("bundle"))
    ceremony = _normalize_ceremony(payload.get("ceremony"), bundle["bundle_id"])
    return {"bundle": bundle, "ceremony": ceremony}


def generate_genesis_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic genesis state bundle output."""

    normalized = _normalize_payload(payload)
    core = {
        "bundle": normalized["bundle"],
        "ceremony": normalized["ceremony"],
        "runtime_version": GENESIS_BUNDLE_RUNTIME_VERSION,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
    }
    return {
        **core,
        "bundle_sha256": _stable_sha256(core),
    }


def verify_genesis_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic genesis state bundle output."""

    if not isinstance(bundle, dict):
        raise GenesisBundleValidationError("genesis_bundle_record_not_object", "bundle_record_not_object")

    runtime_version = bundle.get("runtime_version")
    if runtime_version != GENESIS_BUNDLE_RUNTIME_VERSION:
        raise GenesisBundleValidationError(
            "genesis_bundle_runtime_version_invalid",
            f"runtime_version_invalid:{runtime_version}",
        )

    dependency = bundle.get("schema_dependency")
    if dependency != SCHEMA_BASELINE_DEPENDENCY:
        raise GenesisBundleValidationError(
            "genesis_bundle_schema_dependency_invalid",
            f"schema_dependency_invalid:{dependency}",
        )

    payload = {"bundle": bundle.get("bundle"), "ceremony": bundle.get("ceremony")}
    regenerated = generate_genesis_bundle(payload)

    expected_digest = bundle.get("bundle_sha256")
    if not isinstance(expected_digest, str):
        raise GenesisBundleValidationError(
            "genesis_bundle_digest_missing",
            "bundle_sha256_missing",
        )
    if expected_digest != regenerated["bundle_sha256"]:
        raise GenesisBundleValidationError(
            "genesis_bundle_digest_mismatch",
            "bundle_sha256_mismatch",
        )

    observed_core = {
        "bundle": bundle.get("bundle"),
        "ceremony": bundle.get("ceremony"),
        "runtime_version": runtime_version,
        "schema_dependency": dependency,
    }
    expected_core = {
        "bundle": regenerated["bundle"],
        "ceremony": regenerated["ceremony"],
        "runtime_version": regenerated["runtime_version"],
        "schema_dependency": regenerated["schema_dependency"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise GenesisBundleValidationError(
            "genesis_bundle_not_canonical",
            "bundle_not_canonical",
        )

    return {
        "valid": True,
        "runtime_version": GENESIS_BUNDLE_RUNTIME_VERSION,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
        "bundle_sha256": regenerated["bundle_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "schema_dependency_locked", "passed": True},
            {"check_type": "ceremony_sequence_valid", "passed": True},
            {"check_type": "bundle_digest_matches", "passed": True},
        ],
    }


def canonical_genesis_vectors() -> list[dict[str, Any]]:
    """Return a copy of baseline canonical genesis vectors."""

    return copy.deepcopy(CANONICAL_GENESIS_VECTORS)
