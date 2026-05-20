"""Regression tests for the Phase 1401 CDL-091 runtime stub."""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epistemic import (
    BASE_REVIEW_FEE,
    JURY_INCENTIVE_CDL_RATIFIED_TOKEN,
    JURY_INCENTIVE_RUNTIME_VERSION,
    REVIEWER_PAYMENT_NOT_ACTIVATED,
    REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN,
    queue_reviewer_payment_stub,
)
from ilc_core.epistemic import jury_incentive_runtime as runtime

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = REPO_ROOT / "ilc_core/epistemic/jury_incentive_runtime.py"


def _source() -> str:
    return RUNTIME_PATH.read_text(encoding="utf-8")


def _tree() -> ast.AST:
    return ast.parse(_source())


def test_runtime_tokens_present() -> None:
    src = _source()

    assert JURY_INCENTIVE_RUNTIME_VERSION == "jury_incentive_runtime_phase_1401.v0.1"
    assert JURY_INCENTIVE_CDL_RATIFIED_TOKEN == "cdl_091_ratified_phase_1400"
    assert REVIEWER_PAYMENT_NOT_ACTIVATED is True
    assert REVIEWER_PAYMENT_NOT_ACTIVATED_TOKEN == "reviewer_payment_not_activated_phase_1401"
    assert "jury_incentive_runtime_stub_committed_phase_1401" in src


def test_base_fee_and_bonus_parameters_are_decimal() -> None:
    assert BASE_REVIEW_FEE == Decimal("0.05")
    assert isinstance(runtime.BASE_REVIEW_FEE, Decimal)
    assert isinstance(runtime.ACCURACY_BONUS_MAX_MULTIPLIER, Decimal)
    assert isinstance(runtime.APPEAL_SURVIVAL_WEIGHT, Decimal)
    assert isinstance(runtime.REFUTATION_SURVIVAL_WEIGHT, Decimal)
    assert isinstance(runtime.INDEPENDENT_REVIEWER_CONSENSUS_WEIGHT, Decimal)
    assert isinstance(runtime.LONG_RUN_GRAPH_SURVIVAL_WEIGHT, Decimal)


def test_queue_reviewer_payment_stub_returns_not_activated_result() -> None:
    result = queue_reviewer_payment_stub(
        reviewer_id="agent-reviewer-1",
        task_id="task-123",
        base_fee=Decimal("0.05"),
    )

    assert result["status"] == "not_activated"
    assert result["reason"] == "reviewer_payment_not_activated_phase_1401"
    assert result["payment_enqueued"] is False
    assert result["ledger_write_authorized"] is False
    assert result["treasury_write_authorized"] is False
    assert result["ecu_distribution_authorized"] is False
    assert result["base_fee_ecu"] == "0.05"


def test_queue_reviewer_payment_stub_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="invalid_reviewer_id"):
        queue_reviewer_payment_stub(reviewer_id="", task_id="task-123")

    with pytest.raises(ValueError, match="invalid_task_id"):
        queue_reviewer_payment_stub(reviewer_id="agent-reviewer-1", task_id="")

    with pytest.raises(ValueError, match="invalid_base_fee_decimal"):
        queue_reviewer_payment_stub(
            reviewer_id="agent-reviewer-1",
            task_id="task-123",
            base_fee=Decimal("NaN"),
        )


def test_no_float_constants_in_runtime_module() -> None:
    float_nodes = [
        node for node in ast.walk(_tree())
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    assert float_nodes == []


def test_no_random_import_in_runtime_module() -> None:
    src = _source()

    assert "import random" not in src
    assert "from random" not in src


def test_no_production_assert_in_runtime_module() -> None:
    assert not any(isinstance(node, ast.Assert) for node in ast.walk(_tree()))


def test_approval_only_payment_rejected_and_default_off() -> None:
    assert runtime.APPROVAL_ONLY_PAYMENT_REJECTED is True
    assert runtime.REVIEWER_PAYMENT_NOT_ACTIVATED is True
    assert "REVIEWER_PAYMENT_NOT_ACTIVATED: bool = True" in _source()


def test_exported_from_epistemic_package() -> None:
    import ilc_core.epistemic as epistemic

    assert epistemic.JURY_INCENTIVE_RUNTIME_VERSION == JURY_INCENTIVE_RUNTIME_VERSION
    assert epistemic.JURY_INCENTIVE_CDL_RATIFIED_TOKEN == JURY_INCENTIVE_CDL_RATIFIED_TOKEN
    assert epistemic.REVIEWER_PAYMENT_NOT_ACTIVATED is True
    assert epistemic.queue_reviewer_payment_stub is queue_reviewer_payment_stub
