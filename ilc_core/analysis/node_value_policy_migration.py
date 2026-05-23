# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from typing import Mapping, TypedDict, cast

from ilc_core.analysis.governance_weight import (
    GovernanceWeightPolicy,
    validate_governance_weight_policy,
)
from ilc_core.analysis.node_value_kernel import EwWeights, validate_ew_weights
from ilc_core.analysis.utility_flow_rewards import (
    RewardGovernorPolicy,
    validate_reward_governor_policy,
)
from ilc_core.exceptions import PolicyMigrationError


class NodeValuePolicyBundle(TypedDict):
    contract_version: str
    compatibility_mode: str
    ew_weights: EwWeights
    governance_policy: GovernanceWeightPolicy
    reward_policy: RewardGovernorPolicy


class NodeValuePolicyMigrationReport(TypedDict):
    normalized_bundle: NodeValuePolicyBundle
    migrated_fields: list[str]
    compatibility_mode_used: bool


_LEGACY_ALIASES = {
    "ew_weights": "weights",
    "governance_policy": "governance_weight_policy",
    "reward_policy": "reward_governor_policy",
}


def _expect_mapping(bundle: Mapping[str, object], key: str, token: str) -> Mapping[str, object]:
    value = bundle.get(key)
    if not isinstance(value, Mapping):
        raise PolicyMigrationError(token)
    return cast(Mapping[str, object], value)


def _normalize_strict(bundle: Mapping[str, object]) -> NodeValuePolicyMigrationReport:
    legacy_keys = set(_LEGACY_ALIASES.values())
    if any(key in bundle for key in legacy_keys):
        raise PolicyMigrationError("policy_migration_legacy_keys_in_strict_mode")

    contract_version = bundle.get("contract_version")
    if contract_version != "v0.1":
        raise PolicyMigrationError("policy_migration_strict_mode_requires_contract_version_v0_1")

    ew_weights = validate_ew_weights(
        cast(Mapping[str, float], _expect_mapping(bundle, "ew_weights", "policy_migration_missing_ew_weights"))
    )
    governance_policy = validate_governance_weight_policy(
        _expect_mapping(bundle, "governance_policy", "policy_migration_missing_governance_policy")
    )
    reward_policy = validate_reward_governor_policy(
        _expect_mapping(bundle, "reward_policy", "policy_migration_missing_reward_policy")
    )

    normalized_bundle: NodeValuePolicyBundle = {
        "contract_version": "v0.1",
        "compatibility_mode": "strict",
        "ew_weights": ew_weights,
        "governance_policy": governance_policy,
        "reward_policy": reward_policy,
    }
    return {
        "normalized_bundle": normalized_bundle,
        "migrated_fields": [],
        "compatibility_mode_used": False,
    }


def _normalize_legacy_bridge(bundle: Mapping[str, object]) -> NodeValuePolicyMigrationReport:
    migrated_fields: list[str] = []

    ew_key = "ew_weights"
    if ew_key not in bundle and _LEGACY_ALIASES[ew_key] in bundle:
        ew_key = _LEGACY_ALIASES[ew_key]
        migrated_fields.append(f"{ew_key}->ew_weights")

    governance_key = "governance_policy"
    if governance_key not in bundle and _LEGACY_ALIASES[governance_key] in bundle:
        governance_key = _LEGACY_ALIASES[governance_key]
        migrated_fields.append(f"{governance_key}->governance_policy")

    reward_key = "reward_policy"
    if reward_key not in bundle and _LEGACY_ALIASES[reward_key] in bundle:
        reward_key = _LEGACY_ALIASES[reward_key]
        migrated_fields.append(f"{reward_key}->reward_policy")

    ew_weights = validate_ew_weights(
        cast(Mapping[str, float], _expect_mapping(bundle, ew_key, "policy_migration_missing_ew_weights"))
    )
    governance_policy = validate_governance_weight_policy(
        _expect_mapping(bundle, governance_key, "policy_migration_missing_governance_policy")
    )
    reward_policy = validate_reward_governor_policy(
        _expect_mapping(bundle, reward_key, "policy_migration_missing_reward_policy")
    )

    normalized_bundle: NodeValuePolicyBundle = {
        "contract_version": "v0.1",
        "compatibility_mode": "legacy_bridge",
        "ew_weights": ew_weights,
        "governance_policy": governance_policy,
        "reward_policy": reward_policy,
    }

    return {
        "normalized_bundle": normalized_bundle,
        "migrated_fields": migrated_fields,
        "compatibility_mode_used": True,
    }


def normalize_node_value_policy_bundle(
    bundle: Mapping[str, object],
    *,
    allow_legacy_bridge: bool = False,
) -> NodeValuePolicyMigrationReport:
    contract_version = bundle.get("contract_version")

    if contract_version == "v0.1":
        return _normalize_strict(bundle)

    if allow_legacy_bridge and (contract_version in (None, "v0", "legacy")):
        return _normalize_legacy_bridge(bundle)

    raise PolicyMigrationError("policy_migration_unsupported_contract_version")
