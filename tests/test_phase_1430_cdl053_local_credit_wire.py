"""Phase 1430 CDL-053 local credit wiring tests."""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epistemic import (
    CDL_053_LOCAL_CREDIT_WIRED_TOKEN,
    MAINTENANCE_LOTTERY_NOT_ACTIVATED,
    MAINTENANCE_LOTTERY_NOT_ACTIVATED_PHASE_1430_TOKEN,
    NO_ECU_DISTRIBUTION_PHASE_1430_TOKEN,
    MaintenanceLocalCreditTaskRecord,
    ReviewerAttestation,
    TaxonomyClass,
    quote_review_lane_admission,
    wire_cdl_053_local_credit_eligibility,
)
from ilc_core.epistemic import maintenance_lottery_runtime as runtime
from ilc_core.epistemic.review_lane_admission_runtime import ReviewLaneAdmissionRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = REPO_ROOT / "ilc_core/epistemic/maintenance_lottery_runtime.py"
CDL_053_EVIDENCE_PATH = (
    REPO_ROOT
    / "docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md"
)


def _approvals() -> list[ReviewerAttestation]:
    return [
        ReviewerAttestation(reviewer_agent_id=f"reviewer-{index}", verdict="approve")
        for index in range(5)
    ]


def _decision(
    *,
    task_id: str = "maintenance-task-1430",
    epoch_id: int = 1430,
    review_lane: str = "star.map.embedding",
    admitted: bool = True,
):
    attestations = _approvals() if admitted else _approvals()[:4]
    return quote_review_lane_admission(
        ReviewLaneAdmissionRequest(
            submission_id=task_id,
            submission_content_hash="sha256:" + "a" * 64,
            current_taxonomy_class=TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION,
            target_taxonomy_class=TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE,
            submitter_agent_id="agent-maintenance-author",
            review_epoch=epoch_id,
            review_lane=review_lane,
            reviewer_attestations=attestations,
        )
    )


def _task_record(**overrides: object) -> MaintenanceLocalCreditTaskRecord:
    values: dict[str, object] = {
        "agent_id": "agent-maintenance-author",
        "task_id": "maintenance-task-1430",
        "epoch_id": 1430,
        "task_class": "star.map.embedding",
        "review_lane_decision": _decision(),
    }
    values.update(overrides)
    return MaintenanceLocalCreditTaskRecord(**values)


def test_required_phase_1430_tokens_are_exported_and_recorded() -> None:
    assert CDL_053_LOCAL_CREDIT_WIRED_TOKEN == (
        "cdl_053_local_credit_wired_maintenance_lottery_phase_1430"
    )
    assert MAINTENANCE_LOTTERY_NOT_ACTIVATED_PHASE_1430_TOKEN == (
        "maintenance_lottery_not_activated_phase_1430"
    )
    assert NO_ECU_DISTRIBUTION_PHASE_1430_TOKEN == "no_ecu_distribution_phase_1430"
    assert CDL_053_LOCAL_CREDIT_WIRED_TOKEN in runtime.PHASE_TOKENS
    assert MAINTENANCE_LOTTERY_NOT_ACTIVATED_PHASE_1430_TOKEN in runtime.PHASE_TOKENS
    assert NO_ECU_DISTRIBUTION_PHASE_1430_TOKEN in runtime.PHASE_TOKENS


def test_cdl_053_scope_is_narrow_non_settlement_local_credit() -> None:
    text = CDL_053_EVIDENCE_PATH.read_text(encoding="utf-8")

    assert "cdl_053_ratified_phase_1407_fix2" in text
    assert "review-lane-passed maintenance-equivalent productive work only" in text
    assert "WERNER_DIRECT_ECU_CREATION_AUTHORIZED` | `false" in text
    assert "WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE` | `false" in text
    assert "WERNER_WALLET_MUTATION_AUTHORIZED` | `false" in text


def test_eligible_maintenance_task_accumulates_decimal_local_credit() -> None:
    quote = wire_cdl_053_local_credit_eligibility(
        _task_record(),
        existing_local_credit=Decimal("2"),
    )

    assert quote.eligible is True
    assert quote.status == "local_credit_eligible"
    assert quote.failure_reasons == ()
    assert quote.local_credit_delta == Decimal("1")
    assert quote.accumulated_local_credit == Decimal("3")
    assert isinstance(quote.local_credit_delta, Decimal)
    assert isinstance(quote.accumulated_local_credit, Decimal)


def test_noneligible_task_returns_zero_credit_without_distribution() -> None:
    quote = wire_cdl_053_local_credit_eligibility(
        _task_record(
            task_class="non.maintenance.work",
            review_lane_decision=_decision(review_lane="non.maintenance.work"),
        ),
        existing_local_credit=Decimal("7"),
    )

    assert quote.eligible is False
    assert quote.local_credit_delta == Decimal("0")
    assert quote.accumulated_local_credit == Decimal("7")
    assert quote.failure_reasons == ("cdl_053_task_class_not_maintenance_equivalent",)
    assert quote.ecu_distribution_authorized is False
    assert quote.wallet_write_authorized is False
    assert quote.ledger_write_authorized is False
    assert quote.treasury_write_authorized is False


def test_review_lane_rejection_returns_zero_credit() -> None:
    quote = wire_cdl_053_local_credit_eligibility(
        _task_record(review_lane_decision=_decision(admitted=False)),
    )

    assert quote.eligible is False
    assert quote.local_credit_delta == Decimal("0")
    assert "cdl_053_review_lane_not_passed" in quote.failure_reasons


def test_maintenance_lottery_remains_default_off_and_non_settlement() -> None:
    quote = wire_cdl_053_local_credit_eligibility(_task_record())

    assert MAINTENANCE_LOTTERY_NOT_ACTIVATED is True
    assert runtime.MAINTENANCE_LOTTERY_NOT_ACTIVATED is True
    assert quote.maintenance_lottery_activated is False
    assert quote.lottery_entry_enqueued is False
    assert quote.draw_authorized is False
    assert quote.ecu_distribution_authorized is False
    assert quote.wallet_write_authorized is False
    assert quote.settlement_grade_ecu is False
    assert quote.wallet_visible is False
    assert quote.transferable is False


def test_invalid_decimal_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="invalid_existing_local_credit"):
        wire_cdl_053_local_credit_eligibility(_task_record(), existing_local_credit="NaN")

    with pytest.raises(ValueError, match="invalid_existing_local_credit"):
        wire_cdl_053_local_credit_eligibility(_task_record(), existing_local_credit=1.0)

    with pytest.raises(ValueError, match="invalid_existing_local_credit"):
        wire_cdl_053_local_credit_eligibility(_task_record(), existing_local_credit="-1")


def test_runtime_hygiene_decimal_no_float_random_or_assert() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    float_nodes = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    import_from_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert float_nodes == []
    assert "float(" not in source
    assert "random" not in imported_names
    assert "random" not in import_from_modules
    assert not [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]


def test_exported_from_epistemic_package() -> None:
    import ilc_core.epistemic as epistemic

    assert epistemic.wire_cdl_053_local_credit_eligibility is (
        wire_cdl_053_local_credit_eligibility
    )
    assert epistemic.MaintenanceLocalCreditTaskRecord is MaintenanceLocalCreditTaskRecord
    assert epistemic.CDL_053_LOCAL_CREDIT_WIRED_TOKEN == CDL_053_LOCAL_CREDIT_WIRED_TOKEN
