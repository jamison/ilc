# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1354 default-off CDL-068 topology shuffle runtime.

CDL-068 ratifies epoch-hash v1 as the production-v1 topology randomness
posture below the hard VRF threshold and requires a VRF upgrade at 10 active
validators. This module therefore builds deterministic epoch-hash v1 topology
quotes for sub-threshold validator sets and fails closed once the ratified VRF
threshold is reached. It does not verify VRF proofs, mutate live validator
topology, deploy validators, or activate production topology shuffling.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .admission_ejection_runtime import VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN


TOPOLOGY_SHUFFLE_RUNTIME_VERSION = "topology_shuffle_runtime_1354.v0.1"
CDL_068_DEPENDENCY = (
    "cdl_068_topology_shuffle_authorization_ratified_phase_743.v0.1"
)
CDL_068_TOPOLOGY_SHUFFLE_VRF_RUNTIME_TOKEN = (
    "cdl_068_topology_shuffle_vrf_runtime_phase_1354.v0.1"
)
SHUFFLE_CADENCE_EPOCHS = 1
SHUFFLE_CADENCE_EPOCHS_1_RUNTIME_TOKEN = (
    "shuffle_cadence_epochs_1_runtime_phase_1354"
)
K_DEGREE_FLOOR = 4
K_REGULAR_SIZING_RUNTIME_TOKEN = "k_regular_sizing_runtime_phase_1354"
PUSH_FANOUT_CEILING = 3
DISTINCT_CLUSTER_FLOOR = 4
MAX_CLUSTER_SHARE_CEILING_PERCENT = 33
VRF_UPGRADE_THRESHOLD_VALIDATOR_COUNT = 10
TEN_VALIDATOR_VRF_UPGRADE_TRIGGER_TOKEN = (
    "ten_validator_vrf_upgrade_trigger_phase_1354"
)
EPOCH_HASH_V1_POSTURE_TOKEN = "epoch_hash_v1_posture_preserved_phase_1354"
VRF_UPGRADE_REQUIRED_TOKEN = "vrf_upgrade_required_at_10_validators_phase_1354"
PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN = (
    "production_topology_shuffle_not_activated_phase_1354"
)
PRODUCTION_TOPOLOGY_SHUFFLE_ACTIVATION_TOKEN = (
    "phase_1366_soft_rc_eligible_true_value_path_activation_required"
)

MAX_VALIDATOR_ID = 2**32 - 1


@dataclass(frozen=True)
class TopologyNeighborSet:
    validator_id: int
    peer_validator_ids: tuple[int, ...]

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "peer_validator_ids": self.peer_validator_ids,
            "validator_id": self.validator_id,
        }


@dataclass(frozen=True)
class TopologyShufflePlan:
    runtime_version: str
    cdl_068_dependency: str
    issuance_epoch: int
    validator_ids: tuple[int, ...]
    shuffle_order: tuple[int, ...]
    neighbor_sets: tuple[TopologyNeighborSet, ...]
    k_degree: int
    shuffle_cadence_epochs: int
    push_fanout_ceiling: int
    randomness_mode: str
    vrf_upgrade_required: bool
    production_topology_shuffle_activated: bool
    decision_token: str
    cadence_token: str
    k_regular_token: str
    vrf_trigger_token: str
    epoch_hash_v1_token: str
    rotation_dependency_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "cadence_token": self.cadence_token,
            "cdl_068_dependency": self.cdl_068_dependency,
            "decision_token": self.decision_token,
            "epoch_hash_v1_token": self.epoch_hash_v1_token,
            "issuance_epoch": self.issuance_epoch,
            "k_degree": self.k_degree,
            "k_regular_token": self.k_regular_token,
            "neighbor_sets": [
                neighbor_set.to_canonical_record()
                for neighbor_set in self.neighbor_sets
            ],
            "production_topology_shuffle_activated": (
                self.production_topology_shuffle_activated
            ),
            "push_fanout_ceiling": self.push_fanout_ceiling,
            "randomness_mode": self.randomness_mode,
            "rotation_dependency_token": self.rotation_dependency_token,
            "runtime_version": self.runtime_version,
            "shuffle_cadence_epochs": self.shuffle_cadence_epochs,
            "shuffle_order": self.shuffle_order,
            "validator_ids": self.validator_ids,
            "vrf_trigger_token": self.vrf_trigger_token,
            "vrf_upgrade_required": self.vrf_upgrade_required,
        }

    def to_canonical_json(self) -> str:
        return json.dumps(
            self.to_canonical_record(),
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )


def _require_non_negative_int(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    return value


def _require_positive_u32(value: int, field_name: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
        or value > MAX_VALIDATOR_ID
    ):
        raise ValueError(f"{field_name}_must_be_positive_u32")
    return value


def _normalize_validator_ids(values: Sequence[int]) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ValueError("validator_ids_must_be_sequence")
    normalized = tuple(
        _require_positive_u32(value, "validator_id") for value in values
    )
    if len(set(normalized)) != len(normalized):
        raise ValueError("validator_ids_must_be_unique_phase_1354")
    if len(normalized) < K_DEGREE_FLOOR + 1:
        raise ValueError("validator_count_below_k_regular_floor_phase_1354")
    return tuple(sorted(normalized))


def evaluate_vrf_upgrade_requirement(validator_count: int) -> bool:
    count = _require_non_negative_int(validator_count, "validator_count")
    return count >= VRF_UPGRADE_THRESHOLD_VALIDATOR_COUNT


def require_vrf_ready_validator_count(validator_count: int) -> None:
    if evaluate_vrf_upgrade_requirement(validator_count):
        raise ValueError(VRF_UPGRADE_REQUIRED_TOKEN)


def _require_cadence_elapsed(
    issuance_epoch: int,
    previous_shuffle_epoch: int | None,
) -> None:
    if previous_shuffle_epoch is None:
        return
    previous = _require_non_negative_int(
        previous_shuffle_epoch,
        "previous_shuffle_epoch",
    )
    if previous > issuance_epoch:
        raise ValueError("previous_shuffle_epoch_must_not_exceed_issuance_epoch")
    if issuance_epoch - previous < SHUFFLE_CADENCE_EPOCHS:
        raise ValueError("shuffle_cadence_not_elapsed_phase_1354")


def _epoch_hash_sort_key(
    *,
    issuance_epoch: int,
    validator_id: int,
    validator_ids: tuple[int, ...],
) -> str:
    seed_record = {
        "domain": "ilc.cdl_068.topology_shuffle.epoch_hash_v1.phase_1354",
        "issuance_epoch": issuance_epoch,
        "runtime_version": TOPOLOGY_SHUFFLE_RUNTIME_VERSION,
        "validator_id": validator_id,
        "validator_ids": validator_ids,
    }
    seed_bytes = json.dumps(
        seed_record,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(seed_bytes).hexdigest()


def _derive_epoch_hash_v1_order(
    *,
    issuance_epoch: int,
    validator_ids: tuple[int, ...],
) -> tuple[int, ...]:
    return tuple(
        sorted(
            validator_ids,
            key=lambda validator_id: (
                _epoch_hash_sort_key(
                    issuance_epoch=issuance_epoch,
                    validator_id=validator_id,
                    validator_ids=validator_ids,
                ),
                validator_id,
            ),
        )
    )


def _build_k_regular_neighbor_sets(
    shuffle_order: tuple[int, ...],
    *,
    k_degree: int = K_DEGREE_FLOOR,
) -> tuple[TopologyNeighborSet, ...]:
    validator_count = len(shuffle_order)
    if k_degree < K_DEGREE_FLOOR:
        raise ValueError("k_degree_below_cdl_068_floor_phase_1354")
    if k_degree >= validator_count:
        raise ValueError("k_degree_requires_more_validators_phase_1354")
    if k_degree % 2 != 0:
        raise ValueError("odd_k_degree_not_supported_phase_1354")

    neighbor_sets: list[TopologyNeighborSet] = []
    half_degree = k_degree // 2
    for index, validator_id in enumerate(shuffle_order):
        peers: set[int] = set()
        for offset in range(1, half_degree + 1):
            peers.add(shuffle_order[(index - offset) % validator_count])
            peers.add(shuffle_order[(index + offset) % validator_count])
        if validator_id in peers:
            raise ValueError("topology_shuffle_self_edge_phase_1354")
        neighbor_sets.append(
            TopologyNeighborSet(
                validator_id=validator_id,
                peer_validator_ids=tuple(sorted(peers)),
            )
        )
    return tuple(sorted(neighbor_sets, key=lambda item: item.validator_id))


def validate_validator_cluster_constraints(
    validator_cluster_ids: Mapping[int, str],
) -> tuple[str, ...]:
    if not isinstance(validator_cluster_ids, Mapping):
        raise ValueError("validator_cluster_ids_must_be_mapping")
    if not validator_cluster_ids:
        raise ValueError("validator_cluster_ids_must_not_be_empty")

    normalized: dict[int, str] = {}
    for validator_id, cluster_id in validator_cluster_ids.items():
        normalized_id = _require_positive_u32(validator_id, "validator_id")
        if not isinstance(cluster_id, str) or not cluster_id.strip():
            raise ValueError("validator_cluster_id_must_be_non_empty_string")
        normalized[normalized_id] = cluster_id.strip()

    distinct_clusters = tuple(sorted(set(normalized.values())))
    if len(distinct_clusters) < DISTINCT_CLUSTER_FLOOR:
        raise ValueError("distinct_cluster_floor_not_met_phase_1354")

    validator_count = len(normalized)
    for cluster_id in distinct_clusters:
        cluster_count = sum(1 for value in normalized.values() if value == cluster_id)
        if cluster_count * 100 > validator_count * MAX_CLUSTER_SHARE_CEILING_PERCENT:
            raise ValueError("max_cluster_share_ceiling_exceeded_phase_1354")
    return distinct_clusters


def build_topology_shuffle_plan(
    *,
    issuance_epoch: int,
    validator_ids: Sequence[int],
    previous_shuffle_epoch: int | None = None,
) -> TopologyShufflePlan:
    epoch = _require_non_negative_int(issuance_epoch, "issuance_epoch")
    normalized_validator_ids = _normalize_validator_ids(validator_ids)
    _require_cadence_elapsed(epoch, previous_shuffle_epoch)
    require_vrf_ready_validator_count(len(normalized_validator_ids))

    shuffle_order = _derive_epoch_hash_v1_order(
        issuance_epoch=epoch,
        validator_ids=normalized_validator_ids,
    )
    neighbor_sets = _build_k_regular_neighbor_sets(shuffle_order)
    return TopologyShufflePlan(
        runtime_version=TOPOLOGY_SHUFFLE_RUNTIME_VERSION,
        cdl_068_dependency=CDL_068_DEPENDENCY,
        issuance_epoch=epoch,
        validator_ids=normalized_validator_ids,
        shuffle_order=shuffle_order,
        neighbor_sets=neighbor_sets,
        k_degree=K_DEGREE_FLOOR,
        shuffle_cadence_epochs=SHUFFLE_CADENCE_EPOCHS,
        push_fanout_ceiling=PUSH_FANOUT_CEILING,
        randomness_mode="epoch_hash_v1",
        vrf_upgrade_required=evaluate_vrf_upgrade_requirement(len(normalized_validator_ids)),
        production_topology_shuffle_activated=False,
        decision_token=PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN,
        cadence_token=SHUFFLE_CADENCE_EPOCHS_1_RUNTIME_TOKEN,
        k_regular_token=K_REGULAR_SIZING_RUNTIME_TOKEN,
        vrf_trigger_token=TEN_VALIDATOR_VRF_UPGRADE_TRIGGER_TOKEN,
        epoch_hash_v1_token=EPOCH_HASH_V1_POSTURE_TOKEN,
        rotation_dependency_token=VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN,
    )


def require_production_topology_shuffle_activation(
    activation_token: str | None = None,
) -> None:
    if activation_token is None:
        raise ValueError(PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN)
    if activation_token != PRODUCTION_TOPOLOGY_SHUFFLE_ACTIVATION_TOKEN:
        raise ValueError("invalid_topology_shuffle_activation_token_phase_1354")
    raise ValueError("production_topology_shuffle_activation_not_implemented_phase_1354")
