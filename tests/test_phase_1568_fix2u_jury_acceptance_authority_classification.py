from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.epistemic.jury_acceptance_authority_classification import (
    GLOBAL_TIER_DEFERRED_TO_CDL_096,
    JURY_ACCEPTANCE_AUTHORITY_CLASSIFICATION_NOT_EXECUTION,
    JURY_ACCEPTANCE_AUTHORITY_LABELS,
    JURY_ACCEPTANCE_AUTHORITY_POSITIVE_CLAIM_BLOCKED_TOKEN,
    JURY_ACCEPTANCE_AUTHORITY_PRODUCTION_CLAIM_BLOCKED_TOKEN,
    JURY_ACCEPTANCE_AUTHORITY_UNCLASSIFIED_TOKEN,
    LOCAL_JURY_FINALITY_NONPRODUCTION,
    PANEL_PROXY_ACCEPTANCE,
    PRODUCTION_ASSIGNMENT_QUOTE_ACTIVE,
    PRODUCTION_JURY_FINALITY_NOT_PROVEN,
    SHARD_TIER_RATIFIED_NOT_ACTIVATED,
    acceptance_authority_table,
    classify_acceptance_authority,
    validate_manifest_acceptance_authority,
)
from ilc_core.epistemic.jury_assignment_runtime import PRODUCTION_ASSIGNMENT_NOT_ACTIVATED
from ilc_core.epistemic.jury_finality_evaluator import (
    JURY_FINALITY_EVALUATOR_NOT_PRODUCTION,
    JURY_GLOBAL_TIER_ACTIVATION_STATUS,
    JURY_SHARD_ACTIVATION_STATUS,
)
from tools.testbed.run_three_node_seven_agent_scenario import _scenario_manifest

REPO = Path(__file__).resolve().parents[1]
CLASSIFIER = REPO / "ilc_core/epistemic/jury_acceptance_authority_classification.py"


def _manifest_for_label(label: str, *, positive: bool, production: bool = False) -> dict[str, object]:
    row = next(item for item in acceptance_authority_table() if item.label == label)
    return {
        "acceptance_authority_label": row.label,
        "acceptance_authority_lane": row.lane,
        "acceptance_authority_panel_type": row.panel_type,
        "acceptance_authority_guard_state": row.guard_state,
        "acceptance_authority_positive_acceptance_claim": positive,
        "acceptance_authority_production_grade_claim": production,
    }


def test_fix2u_sentinel_is_classification_only() -> None:
    assert JURY_ACCEPTANCE_AUTHORITY_CLASSIFICATION_NOT_EXECUTION is True


def test_six_canonical_labels_are_exact() -> None:
    assert JURY_ACCEPTANCE_AUTHORITY_LABELS == (
        PANEL_PROXY_ACCEPTANCE,
        LOCAL_JURY_FINALITY_NONPRODUCTION,
        PRODUCTION_ASSIGNMENT_QUOTE_ACTIVE,
        PRODUCTION_JURY_FINALITY_NOT_PROVEN,
        SHARD_TIER_RATIFIED_NOT_ACTIVATED,
        GLOBAL_TIER_DEFERRED_TO_CDL_096,
    )


def test_table_is_complete_for_current_reachable_authority_combinations() -> None:
    table = acceptance_authority_table()
    assert len(table) == len(JURY_ACCEPTANCE_AUTHORITY_LABELS)
    assert {row.label for row in table} == set(JURY_ACCEPTANCE_AUTHORITY_LABELS)
    for row in table:
        classified = classify_acceptance_authority(
            lane=row.lane,
            panel_type=row.panel_type,
            guard_state=row.guard_state,
        )
        assert classified == row


def test_unlabeled_combination_fails_closed() -> None:
    with pytest.raises(ValueError, match=JURY_ACCEPTANCE_AUTHORITY_UNCLASSIFIED_TOKEN):
        classify_acceptance_authority(
            lane="unknown_lane",
            panel_type="panel_proxy",
            guard_state="panel_proxy_nonproduction",
        )


def test_current_runtime_guard_states_match_classification_inputs() -> None:
    assert PRODUCTION_ASSIGNMENT_NOT_ACTIVATED is False
    assert JURY_FINALITY_EVALUATOR_NOT_PRODUCTION is True
    assert JURY_SHARD_ACTIVATION_STATUS == "ratified_not_activated"
    assert JURY_GLOBAL_TIER_ACTIVATION_STATUS == "deferred_to_cdl_096"


def test_production_jury_finality_not_proven_cannot_be_positive_acceptance_claim() -> None:
    manifest = _manifest_for_label(PRODUCTION_JURY_FINALITY_NOT_PROVEN, positive=True)
    with pytest.raises(ValueError, match=JURY_ACCEPTANCE_AUTHORITY_POSITIVE_CLAIM_BLOCKED_TOKEN):
        validate_manifest_acceptance_authority(manifest)


def test_global_tier_deferred_to_cdl096_cannot_be_positive_acceptance_claim() -> None:
    manifest = _manifest_for_label(GLOBAL_TIER_DEFERRED_TO_CDL_096, positive=True)
    with pytest.raises(ValueError, match=JURY_ACCEPTANCE_AUTHORITY_POSITIVE_CLAIM_BLOCKED_TOKEN):
        validate_manifest_acceptance_authority(manifest)


def test_non_production_labels_cannot_claim_production_grade_authority() -> None:
    manifest = _manifest_for_label(PANEL_PROXY_ACCEPTANCE, positive=True, production=True)
    with pytest.raises(ValueError, match=JURY_ACCEPTANCE_AUTHORITY_PRODUCTION_CLAIM_BLOCKED_TOKEN):
        validate_manifest_acceptance_authority(manifest)


def test_current_scenario_manifest_declares_panel_proxy_acceptance() -> None:
    panel_payload = {
        "panel_result": {
            "verdict_token": "agent_loop_panel_ok",
            "passed": True,
            "yes_votes": 7,
            "no_votes": 0,
            "agreement_score": "1.000000",
            "direct_author_agent_id": "agent-1",
            "task_id": "task-1",
            "epoch": 0,
        },
        "ecu_claim_batch": {
            "claims": [{"agent_id": "agent-1", "ecu": "1"}],
            "ledger": {"rewards_paid": "1"},
        },
    }
    manifest = _scenario_manifest(
        scenario_path=REPO / "testbed/scenarios/block6_seven_agent_v1.json",
        hosts_path=REPO / "testbed/configs/block6_hosts.json",
        output_root=REPO / "out/testbed/fix2u",
        start_output="already_running",
        submissions=[{"submission_id": "sub-1"}],
        panel_payload=panel_payload,
        panel_broadcast={"send_statuses": []},
        claims_broadcast={"send_statuses": []},
        benchmark_metrics={},
    )
    assert manifest["acceptance_authority_label"] == PANEL_PROXY_ACCEPTANCE
    assert manifest["acceptance_authority_positive_acceptance_claim"] is True
    assert manifest["acceptance_authority_production_grade_claim"] is False
    validate_manifest_acceptance_authority(manifest)
    json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False)


def test_no_random_import_in_classifier_source() -> None:
    source = CLASSIFIER.read_text(encoding="utf-8")
    assert "import random" not in source
