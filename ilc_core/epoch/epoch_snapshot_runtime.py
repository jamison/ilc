"""Phase-314 epoch snapshot generator/verifier runtime."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


EPOCH_SNAPSHOT_RUNTIME_VERSION = "epoch_snapshot_runtime_314.v0.1"
SCHEMA_BASELINE_DEPENDENCY = "d2_schema_baseline_310.v0.1"
GENESIS_BUNDLE_DEPENDENCY = "genesis_state_bundle_312.v0.1"


CANONICAL_EPOCH_SNAPSHOT_VECTORS: list[dict[str, Any]] = [
    {
        "snapshot": {
            "snapshot_id": "snapshot-mainnet-100",
            "network": "mainnet",
            "epoch": 100,
            "retained_epochs": [98, 99, 100],
            "checkpoint_refs": [
                {"kind": "genesis_bundle", "ref": "genesis-mainnet-0"},
                {"kind": "state_root", "ref": "state-root-100"},
            ],
        },
        "bootstrap": {
            "start_epoch": 98,
            "target_epoch": 100,
            "required_artifacts": ["genesis_bundle", "snapshot_chain"],
        },
        "retention": {
            "keep_last_n_epochs": 3,
            "minimum_epoch": 98,
        },
    },
    {
        "snapshot": {
            "snapshot_id": "snapshot-testnet-42",
            "network": "testnet",
            "epoch": 42,
            "retained_epochs": [40, 41, 42],
            "checkpoint_refs": [
                {"kind": "genesis_bundle", "ref": "genesis-testnet-0"},
                {"kind": "state_root", "ref": "state-root-42"},
            ],
        },
        "bootstrap": {
            "start_epoch": 40,
            "target_epoch": 42,
            "required_artifacts": ["genesis_bundle", "snapshot_chain"],
        },
        "retention": {
            "keep_last_n_epochs": 3,
            "minimum_epoch": 40,
        },
    },
]


class EpochSnapshotValidationError(ValueError):
    """Typed validation exception with deterministic error token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _sorted_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sorted_mapping(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, list):
        return [_sorted_mapping(item) for item in value]
    return value


def _normalize_checkpoint_refs(raw_refs: Any, snapshot_id: str) -> list[dict[str, str]]:
    if not isinstance(raw_refs, list):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_checkpoint_refs_not_list",
            f"checkpoint_refs_not_list:{snapshot_id}",
        )
    if not raw_refs:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_checkpoint_refs_empty",
            f"checkpoint_refs_empty:{snapshot_id}",
        )

    normalized: list[dict[str, str]] = []
    for entry in raw_refs:
        if not isinstance(entry, dict):
            raise EpochSnapshotValidationError(
                "epoch_snapshot_checkpoint_ref_not_object",
                f"checkpoint_ref_not_object:{snapshot_id}",
            )
        kind = entry.get("kind")
        ref = entry.get("ref")
        if not isinstance(kind, str) or not kind.strip():
            raise EpochSnapshotValidationError(
                "epoch_snapshot_checkpoint_kind_missing",
                f"checkpoint_kind_missing:{snapshot_id}",
            )
        if not isinstance(ref, str) or not ref.strip():
            raise EpochSnapshotValidationError(
                "epoch_snapshot_checkpoint_ref_missing",
                f"checkpoint_ref_missing:{snapshot_id}:{kind}",
            )
        normalized.append({"kind": kind, "ref": ref})

    normalized = sorted(normalized, key=lambda item: (item["kind"], item["ref"]))
    dedupe_key = {(item["kind"], item["ref"]) for item in normalized}
    if len(dedupe_key) != len(normalized):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_checkpoint_ref_duplicate",
            f"checkpoint_ref_duplicate:{snapshot_id}",
        )
    return normalized


def _normalize_retained_epochs(raw_epochs: Any, snapshot_id: str, target_epoch: int) -> list[int]:
    if not isinstance(raw_epochs, list):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_retained_epochs_not_list",
            f"retained_epochs_not_list:{snapshot_id}",
        )
    if not raw_epochs:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_retained_epochs_empty",
            f"retained_epochs_empty:{snapshot_id}",
        )

    normalized: list[int] = []
    for raw_epoch in raw_epochs:
        if not isinstance(raw_epoch, int) or raw_epoch < 0:
            raise EpochSnapshotValidationError(
                "epoch_snapshot_retained_epoch_invalid",
                f"retained_epoch_invalid:{snapshot_id}",
            )
        normalized.append(raw_epoch)

    normalized = sorted(set(normalized))
    if target_epoch not in normalized:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_target_epoch_not_retained",
            f"target_epoch_not_retained:{snapshot_id}:{target_epoch}",
        )
    return normalized


def _normalize_snapshot(raw_snapshot: Any) -> dict[str, Any]:
    if not isinstance(raw_snapshot, dict):
        raise EpochSnapshotValidationError("epoch_snapshot_not_object", "snapshot_not_object")

    snapshot_id = raw_snapshot.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not snapshot_id.strip():
        raise EpochSnapshotValidationError("epoch_snapshot_id_missing", "snapshot_id_missing")

    network = raw_snapshot.get("network")
    if not isinstance(network, str) or not network.strip():
        raise EpochSnapshotValidationError(
            "epoch_snapshot_network_missing",
            f"network_missing:{snapshot_id}",
        )

    epoch = raw_snapshot.get("epoch")
    if not isinstance(epoch, int) or epoch < 0:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_epoch_invalid",
            f"epoch_invalid:{snapshot_id}",
        )

    retained_epochs = _normalize_retained_epochs(raw_snapshot.get("retained_epochs"), snapshot_id, epoch)
    checkpoint_refs = _normalize_checkpoint_refs(raw_snapshot.get("checkpoint_refs"), snapshot_id)

    return {
        "checkpoint_refs": checkpoint_refs,
        "epoch": epoch,
        "network": network,
        "retained_epochs": retained_epochs,
        "snapshot_id": snapshot_id,
    }


def _normalize_bootstrap(raw_bootstrap: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw_bootstrap, dict):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_bootstrap_not_object",
            f"bootstrap_not_object:{snapshot['snapshot_id']}",
        )

    start_epoch = raw_bootstrap.get("start_epoch")
    target_epoch = raw_bootstrap.get("target_epoch")

    if not isinstance(start_epoch, int) or start_epoch < 0:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_bootstrap_start_epoch_invalid",
            f"bootstrap_start_epoch_invalid:{snapshot['snapshot_id']}",
        )
    if not isinstance(target_epoch, int) or target_epoch < 0:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_bootstrap_target_epoch_invalid",
            f"bootstrap_target_epoch_invalid:{snapshot['snapshot_id']}",
        )
    if start_epoch > target_epoch:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_bootstrap_epoch_range_invalid",
            f"bootstrap_epoch_range_invalid:{snapshot['snapshot_id']}",
        )
    if target_epoch != snapshot["epoch"]:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_bootstrap_target_epoch_mismatch",
            f"bootstrap_target_epoch_mismatch:{snapshot['snapshot_id']}",
        )

    required_artifacts = raw_bootstrap.get("required_artifacts")
    if not isinstance(required_artifacts, list):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_bootstrap_required_artifacts_not_list",
            f"bootstrap_required_artifacts_not_list:{snapshot['snapshot_id']}",
        )
    if not required_artifacts:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_bootstrap_required_artifacts_empty",
            f"bootstrap_required_artifacts_empty:{snapshot['snapshot_id']}",
        )

    normalized_artifacts: list[str] = []
    for artifact in required_artifacts:
        if not isinstance(artifact, str) or not artifact.strip():
            raise EpochSnapshotValidationError(
                "epoch_snapshot_bootstrap_required_artifact_invalid",
                f"bootstrap_required_artifact_invalid:{snapshot['snapshot_id']}",
            )
        normalized_artifacts.append(artifact)

    normalized_artifacts = sorted(set(normalized_artifacts))

    return {
        "required_artifacts": normalized_artifacts,
        "start_epoch": start_epoch,
        "target_epoch": target_epoch,
    }


def _normalize_retention(raw_retention: Any, snapshot: dict[str, Any], bootstrap: dict[str, Any]) -> dict[str, int]:
    if not isinstance(raw_retention, dict):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_retention_not_object",
            f"retention_not_object:{snapshot['snapshot_id']}",
        )

    keep_last_n_epochs = raw_retention.get("keep_last_n_epochs")
    minimum_epoch = raw_retention.get("minimum_epoch")

    if not isinstance(keep_last_n_epochs, int) or keep_last_n_epochs <= 0:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_retention_keep_last_invalid",
            f"retention_keep_last_invalid:{snapshot['snapshot_id']}",
        )
    if not isinstance(minimum_epoch, int) or minimum_epoch < 0:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_retention_minimum_epoch_invalid",
            f"retention_minimum_epoch_invalid:{snapshot['snapshot_id']}",
        )

    expected_minimum = snapshot["epoch"] - (keep_last_n_epochs - 1)
    if minimum_epoch != expected_minimum:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_retention_window_invalid",
            f"retention_window_invalid:{snapshot['snapshot_id']}:{minimum_epoch}:{expected_minimum}",
        )

    if minimum_epoch != bootstrap["start_epoch"]:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_retention_bootstrap_mismatch",
            f"retention_bootstrap_mismatch:{snapshot['snapshot_id']}",
        )

    return {
        "keep_last_n_epochs": keep_last_n_epochs,
        "minimum_epoch": minimum_epoch,
    }


def _normalize_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise EpochSnapshotValidationError("epoch_snapshot_payload_not_object", "payload_not_object")

    snapshot = _normalize_snapshot(payload.get("snapshot"))
    bootstrap = _normalize_bootstrap(payload.get("bootstrap"), snapshot)
    retention = _normalize_retention(payload.get("retention"), snapshot, bootstrap)
    return {
        "bootstrap": bootstrap,
        "retention": retention,
        "snapshot": snapshot,
    }


def generate_epoch_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic epoch snapshot output."""

    normalized = _normalize_payload(payload)
    core = {
        "bootstrap": normalized["bootstrap"],
        "genesis_dependency": GENESIS_BUNDLE_DEPENDENCY,
        "retention": normalized["retention"],
        "runtime_version": EPOCH_SNAPSHOT_RUNTIME_VERSION,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
        "snapshot": normalized["snapshot"],
    }
    return {
        **core,
        "snapshot_sha256": _stable_sha256(core),
    }


def verify_epoch_snapshot(snapshot_record: dict[str, Any]) -> dict[str, Any]:
    """Verify deterministic epoch snapshot output."""

    if not isinstance(snapshot_record, dict):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_record_not_object",
            "snapshot_record_not_object",
        )

    runtime_version = snapshot_record.get("runtime_version")
    if runtime_version != EPOCH_SNAPSHOT_RUNTIME_VERSION:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_runtime_version_invalid",
            f"runtime_version_invalid:{runtime_version}",
        )

    schema_dependency = snapshot_record.get("schema_dependency")
    if schema_dependency != SCHEMA_BASELINE_DEPENDENCY:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_schema_dependency_invalid",
            f"schema_dependency_invalid:{schema_dependency}",
        )

    genesis_dependency = snapshot_record.get("genesis_dependency")
    if genesis_dependency != GENESIS_BUNDLE_DEPENDENCY:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_genesis_dependency_invalid",
            f"genesis_dependency_invalid:{genesis_dependency}",
        )

    payload = {
        "snapshot": snapshot_record.get("snapshot"),
        "bootstrap": snapshot_record.get("bootstrap"),
        "retention": snapshot_record.get("retention"),
    }
    regenerated = generate_epoch_snapshot(payload)

    observed_digest = snapshot_record.get("snapshot_sha256")
    if not isinstance(observed_digest, str):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_digest_missing",
            "snapshot_sha256_missing",
        )
    if observed_digest != regenerated["snapshot_sha256"]:
        raise EpochSnapshotValidationError(
            "epoch_snapshot_digest_mismatch",
            "snapshot_sha256_mismatch",
        )

    observed_core = {
        "bootstrap": snapshot_record.get("bootstrap"),
        "genesis_dependency": genesis_dependency,
        "retention": snapshot_record.get("retention"),
        "runtime_version": runtime_version,
        "schema_dependency": schema_dependency,
        "snapshot": snapshot_record.get("snapshot"),
    }
    expected_core = {
        "bootstrap": regenerated["bootstrap"],
        "genesis_dependency": regenerated["genesis_dependency"],
        "retention": regenerated["retention"],
        "runtime_version": regenerated["runtime_version"],
        "schema_dependency": regenerated["schema_dependency"],
        "snapshot": regenerated["snapshot"],
    }
    if _stable_json(_sorted_mapping(observed_core)) != _stable_json(_sorted_mapping(expected_core)):
        raise EpochSnapshotValidationError(
            "epoch_snapshot_not_canonical",
            "snapshot_not_canonical",
        )

    return {
        "valid": True,
        "runtime_version": EPOCH_SNAPSHOT_RUNTIME_VERSION,
        "schema_dependency": SCHEMA_BASELINE_DEPENDENCY,
        "genesis_dependency": GENESIS_BUNDLE_DEPENDENCY,
        "snapshot_sha256": regenerated["snapshot_sha256"],
        "checks": [
            {"check_type": "runtime_version_supported", "passed": True},
            {"check_type": "schema_dependency_locked", "passed": True},
            {"check_type": "genesis_dependency_locked", "passed": True},
            {"check_type": "bootstrap_window_valid", "passed": True},
            {"check_type": "retention_policy_valid", "passed": True},
            {"check_type": "snapshot_digest_matches", "passed": True},
        ],
    }


def canonical_epoch_snapshot_vectors() -> list[dict[str, Any]]:
    """Return a copy of baseline canonical epoch snapshot vectors."""

    return copy.deepcopy(CANONICAL_EPOCH_SNAPSHOT_VECTORS)
