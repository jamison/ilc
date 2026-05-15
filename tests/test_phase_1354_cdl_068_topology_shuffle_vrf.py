from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ilc_core.validator import (
    CDL_068_TOPOLOGY_SHUFFLE_VRF_RUNTIME_TOKEN,
    EPOCH_HASH_V1_POSTURE_TOKEN,
    K_DEGREE_FLOOR,
    K_REGULAR_SIZING_RUNTIME_TOKEN,
    PRODUCTION_TOPOLOGY_SHUFFLE_ACTIVATION_TOKEN,
    PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN,
    SHUFFLE_CADENCE_EPOCHS,
    SHUFFLE_CADENCE_EPOCHS_1_RUNTIME_TOKEN,
    TEN_VALIDATOR_VRF_UPGRADE_TRIGGER_TOKEN,
    TOPOLOGY_SHUFFLE_RUNTIME_VERSION,
    VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN,
    VRF_UPGRADE_REQUIRED_TOKEN,
    VRF_UPGRADE_THRESHOLD_VALIDATOR_COUNT,
    build_topology_shuffle_plan,
    evaluate_vrf_upgrade_requirement,
    require_production_topology_shuffle_activation,
    validate_validator_cluster_constraints,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/validator/topology_shuffle_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1354_g8_cdl_068_topology_shuffle_vrf_runtime.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1354_cdl_068_topology_shuffle_vrf_runtime_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _imports_module(path: Path, module_name: str) -> bool:
    tree = ast.parse(_read(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == module_name for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom) and node.module == module_name:
            return True
    return False


def test_phase_1354_builds_default_off_epoch_hash_plan_for_nine_validators() -> None:
    plan = build_topology_shuffle_plan(
        issuance_epoch=54,
        validator_ids=[9, 1, 5, 3, 7, 2, 4, 6, 8],
        previous_shuffle_epoch=53,
    )
    repeat = build_topology_shuffle_plan(
        issuance_epoch=54,
        validator_ids=[8, 6, 4, 2, 7, 3, 5, 1, 9],
        previous_shuffle_epoch=53,
    )

    assert plan.runtime_version == TOPOLOGY_SHUFFLE_RUNTIME_VERSION
    assert plan.validator_ids == (1, 2, 3, 4, 5, 6, 7, 8, 9)
    assert plan.shuffle_order == repeat.shuffle_order
    assert plan.shuffle_order != tuple(sorted(plan.shuffle_order))
    assert plan.shuffle_cadence_epochs == SHUFFLE_CADENCE_EPOCHS
    assert plan.cadence_token == SHUFFLE_CADENCE_EPOCHS_1_RUNTIME_TOKEN
    assert plan.k_degree == K_DEGREE_FLOOR
    assert plan.k_regular_token == K_REGULAR_SIZING_RUNTIME_TOKEN
    assert plan.vrf_trigger_token == TEN_VALIDATOR_VRF_UPGRADE_TRIGGER_TOKEN
    assert plan.epoch_hash_v1_token == EPOCH_HASH_V1_POSTURE_TOKEN
    assert plan.rotation_dependency_token == VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN
    assert plan.randomness_mode == "epoch_hash_v1"
    assert plan.vrf_upgrade_required is False
    assert plan.production_topology_shuffle_activated is False
    assert plan.decision_token == PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN

    for neighbor_set in plan.neighbor_sets:
        assert len(neighbor_set.peer_validator_ids) == K_DEGREE_FLOOR
        assert neighbor_set.validator_id not in neighbor_set.peer_validator_ids
        assert set(neighbor_set.peer_validator_ids).issubset(set(plan.validator_ids))


def test_phase_1354_epoch_hash_plan_changes_across_epochs() -> None:
    epoch_54 = build_topology_shuffle_plan(
        issuance_epoch=54,
        validator_ids=[1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    epoch_55 = build_topology_shuffle_plan(
        issuance_epoch=55,
        validator_ids=[1, 2, 3, 4, 5, 6, 7, 8, 9],
    )

    assert epoch_54.shuffle_order != epoch_55.shuffle_order
    assert json.loads(epoch_54.to_canonical_json())["decision_token"] == (
        PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN
    )


def test_phase_1354_vrf_upgrade_trigger_boundary_is_fail_closed() -> None:
    assert evaluate_vrf_upgrade_requirement(9) is False
    assert evaluate_vrf_upgrade_requirement(VRF_UPGRADE_THRESHOLD_VALIDATOR_COUNT) is True

    with pytest.raises(ValueError, match=VRF_UPGRADE_REQUIRED_TOKEN):
        build_topology_shuffle_plan(
            issuance_epoch=54,
            validator_ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        )


def test_phase_1354_cadence_and_validator_input_guards_are_stable_tokens() -> None:
    with pytest.raises(ValueError, match="shuffle_cadence_not_elapsed_phase_1354"):
        build_topology_shuffle_plan(
            issuance_epoch=54,
            validator_ids=[1, 2, 3, 4, 5],
            previous_shuffle_epoch=54,
        )
    with pytest.raises(ValueError, match="validator_ids_must_be_unique_phase_1354"):
        build_topology_shuffle_plan(issuance_epoch=54, validator_ids=[1, 2, 3, 4, 4])
    with pytest.raises(ValueError, match="validator_count_below_k_regular_floor_phase_1354"):
        build_topology_shuffle_plan(issuance_epoch=54, validator_ids=[1, 2, 3, 4])
    with pytest.raises(ValueError, match="validator_id_must_be_positive_u32"):
        build_topology_shuffle_plan(issuance_epoch=54, validator_ids=[1, 2, 3, 4, True])


def test_phase_1354_validator_cluster_constraints_are_explicit_boundary() -> None:
    clusters = validate_validator_cluster_constraints(
        {
            1: "a",
            2: "a",
            3: "b",
            4: "b",
            5: "c",
            6: "c",
            7: "d",
            8: "d",
            9: "e",
            10: "e",
        }
    )
    assert clusters == ("a", "b", "c", "d", "e")

    with pytest.raises(ValueError, match="distinct_cluster_floor_not_met_phase_1354"):
        validate_validator_cluster_constraints({1: "a", 2: "b", 3: "c", 4: "c"})
    with pytest.raises(ValueError, match="max_cluster_share_ceiling_exceeded_phase_1354"):
        validate_validator_cluster_constraints(
            {1: "a", 2: "a", 3: "a", 4: "a", 5: "b", 6: "c", 7: "d"}
        )


def test_phase_1354_production_activation_remains_unimplemented() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN):
        require_production_topology_shuffle_activation()
    with pytest.raises(
        ValueError,
        match="production_topology_shuffle_activation_not_implemented_phase_1354",
    ):
        require_production_topology_shuffle_activation(
            PRODUCTION_TOPOLOGY_SHUFFLE_ACTIVATION_TOKEN
        )


def test_phase_1354_docs_record_tokens_and_epoch_hash_boundary() -> None:
    tokens = (
        CDL_068_TOPOLOGY_SHUFFLE_VRF_RUNTIME_TOKEN,
        SHUFFLE_CADENCE_EPOCHS_1_RUNTIME_TOKEN,
        K_REGULAR_SIZING_RUNTIME_TOKEN,
        TEN_VALIDATOR_VRF_UPGRADE_TRIGGER_TOKEN,
        PRODUCTION_TOPOLOGY_SHUFFLE_NOT_ACTIVATED_TOKEN,
        EPOCH_HASH_V1_POSTURE_TOKEN,
        VRF_UPGRADE_REQUIRED_TOKEN,
    )
    for path in (RUNTIME, PROMPT, WALKTHROUGH, STATUS, INDEX):
        text = _read(path)
        for token in tokens:
            assert token in text
    assert "epoch-hash v1" in _read(PROMPT)
    assert "fail closed at ≥10" in _read(PROMPT)


def test_phase_1354_no_predictable_prng_import_in_runtime_or_test() -> None:
    assert not _imports_module(RUNTIME, "random")
    assert not _imports_module(Path(__file__), "random")
