import pytest

from ilc_core.analysis.node_value_policy_migration import normalize_node_value_policy_bundle
from ilc_core.exceptions import PolicyMigrationError


def _canonical_policy_bundle() -> dict[str, object]:
    return {
        "contract_version": "v0.1",
        "ew_weights": {
            "reuse": 0.35,
            "contradiction_resilience": 0.25,
            "validation_integrity": 0.20,
            "path_uplift": 0.20,
        },
        "governance_policy": {
            "inactivity_decay_lambda": 0.05,
            "genesis_baseline_weight": 1.0,
            "allow_genesis_bonus": True,
        },
        "reward_policy": {
            "epoch_reward_budget": 100.0,
            "max_genesis_share": 0.5,
            "min_flow_threshold": 0.0,
        },
    }


def test_strict_mode_accepts_canonical_bundle() -> None:
    report = normalize_node_value_policy_bundle(_canonical_policy_bundle())

    assert report["compatibility_mode_used"] is False
    assert report["migrated_fields"] == []
    assert report["normalized_bundle"]["contract_version"] == "v0.1"
    assert report["normalized_bundle"]["compatibility_mode"] == "strict"


def test_strict_mode_rejects_legacy_alias_keys() -> None:
    legacy_in_strict = _canonical_policy_bundle()
    legacy_in_strict["weights"] = legacy_in_strict["ew_weights"]

    with pytest.raises(PolicyMigrationError) as exc_info:
        normalize_node_value_policy_bundle(legacy_in_strict)
    assert str(exc_info.value) == "policy_migration_legacy_keys_in_strict_mode"


def test_legacy_bridge_migrates_alias_fields() -> None:
    legacy_bundle = {
        "contract_version": "legacy",
        "weights": {
            "reuse": 0.35,
            "contradiction_resilience": 0.25,
            "validation_integrity": 0.20,
            "path_uplift": 0.20,
        },
        "governance_weight_policy": {
            "inactivity_decay_lambda": 0.05,
            "genesis_baseline_weight": 1.0,
            "allow_genesis_bonus": True,
        },
        "reward_governor_policy": {
            "epoch_reward_budget": 100.0,
            "max_genesis_share": 0.5,
            "min_flow_threshold": 0.0,
        },
    }

    report = normalize_node_value_policy_bundle(legacy_bundle, allow_legacy_bridge=True)

    assert report["compatibility_mode_used"] is True
    assert report["normalized_bundle"]["compatibility_mode"] == "legacy_bridge"
    assert set(report["migrated_fields"]) == {
        "weights->ew_weights",
        "governance_weight_policy->governance_policy",
        "reward_governor_policy->reward_policy",
    }


def test_unsupported_contract_version_rejected() -> None:
    with pytest.raises(PolicyMigrationError) as exc_info:
        normalize_node_value_policy_bundle(
            {
                "contract_version": "v2",
                "ew_weights": {},
                "governance_policy": {},
                "reward_policy": {},
            }
        )
    assert str(exc_info.value) == "policy_migration_unsupported_contract_version"
