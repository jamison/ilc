"""Regression tests for the Phase 1409 CDL-093 maintenance lottery stub."""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epistemic import (
    MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN,
    MAINTENANCE_LOTTERY_NOT_ACTIVATED,
    MAINTENANCE_LOTTERY_NOT_ACTIVATED_TOKEN,
    MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION,
    MAINTENANCE_LOTTERY_RUNTIME_VERSION,
    request_maintenance_lottery_entry_stub,
)
from ilc_core.epistemic import maintenance_lottery_runtime as runtime

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = REPO_ROOT / "ilc_core/epistemic/maintenance_lottery_runtime.py"


def _source() -> str:
    return RUNTIME_PATH.read_text(encoding="utf-8")


def _tree() -> ast.AST:
    return ast.parse(_source())


def test_runtime_module_importable_and_tokens_present() -> None:
    src = _source()

    assert MAINTENANCE_LOTTERY_RUNTIME_VERSION == "maintenance_lottery_runtime_phase_1409.v0.1"
    assert MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN == "cdl_093_ratified_phase_1408"
    assert MAINTENANCE_LOTTERY_NOT_ACTIVATED is True
    assert MAINTENANCE_LOTTERY_NOT_ACTIVATED_TOKEN == "maintenance_lottery_not_activated_phase_1409"
    assert "maintenance_lottery_runtime_stub_committed_phase_1409" in src


def test_ratified_scope_constants_are_wired() -> None:
    assert runtime.MAINTENANCE_LOTTERY_DRAW_MECHANISM == (
        "production_vrf_or_later_ratified_randomness_required"
    )
    assert runtime.MAINTENANCE_LOTTERY_SHADOW_DRAW_MECHANISM == "epoch_hash_shadow_quote_only"
    assert runtime.MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE == (
        "cdl_053_werner_local_productive_credit"
    )
    assert MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION == Decimal("0.10")
    assert isinstance(runtime.MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION, Decimal)
    assert runtime.MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM is False
    assert runtime.MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH == (
        "cdl_053_werner_local_credit_to_phase_1409_default_off_runtime_stub"
    )


def test_request_entry_stub_returns_not_activated_result() -> None:
    result = request_maintenance_lottery_entry_stub(
        agent_id="agent-maintenance-1",
        task_id="task-maintenance-123",
        epoch_id=1409,
    )

    assert result["status"] == "not_activated"
    assert result["reason"] == "maintenance_lottery_not_activated_phase_1409"
    assert result["runtime_version"] == "maintenance_lottery_runtime_phase_1409.v0.1"
    assert result["lottery_entry_enqueued"] is False
    assert result["draw_authorized"] is False
    assert result["ecu_distribution_authorized"] is False
    assert result["ledger_write_authorized"] is False
    assert result["treasury_write_authorized"] is False


def test_phase_tokens_include_required_tokens() -> None:
    assert isinstance(runtime.PHASE_TOKENS, frozenset)
    assert "maintenance_lottery_runtime_stub_committed_phase_1409" in runtime.PHASE_TOKENS
    assert "maintenance_lottery_not_activated_phase_1409" in runtime.PHASE_TOKENS
    assert "cdl_093_ratified_phase_1408" in runtime.PHASE_TOKENS

    result = request_maintenance_lottery_entry_stub(
        agent_id="agent-maintenance-1",
        task_id="task-maintenance-123",
        epoch_id=1409,
    )
    assert result["phase_tokens"] == sorted(runtime.PHASE_TOKENS)


def test_request_entry_stub_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="invalid_agent_id"):
        request_maintenance_lottery_entry_stub(
            agent_id="",
            task_id="task-maintenance-123",
            epoch_id=1409,
        )

    with pytest.raises(ValueError, match="invalid_task_id"):
        request_maintenance_lottery_entry_stub(
            agent_id="agent-maintenance-1",
            task_id="",
            epoch_id=1409,
        )

    with pytest.raises(ValueError, match="invalid_epoch_id"):
        request_maintenance_lottery_entry_stub(
            agent_id="agent-maintenance-1",
            task_id="task-maintenance-123",
            epoch_id=-1,
        )

    with pytest.raises(ValueError, match="invalid_epoch_id"):
        request_maintenance_lottery_entry_stub(
            agent_id="agent-maintenance-1",
            task_id="task-maintenance-123",
            epoch_id=True,
        )


def test_no_float_constants_in_runtime_module() -> None:
    float_nodes = [
        node for node in ast.walk(_tree())
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    ]
    assert float_nodes == []


def test_no_random_import_in_runtime_module() -> None:
    imports = [
        node for node in ast.walk(_tree())
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    imported_names = {
        alias.name
        for node in imports
        for alias in node.names
    }
    import_from_modules = {
        node.module
        for node in imports
        if isinstance(node, ast.ImportFrom)
    }

    assert "random" not in imported_names
    assert "random" not in import_from_modules


def test_no_production_assert_or_network_json_imports() -> None:
    imports = [
        node for node in ast.walk(_tree())
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    imported_names = {
        alias.name
        for node in imports
        for alias in node.names
    }

    assert not any(isinstance(node, ast.Assert) for node in ast.walk(_tree()))
    assert imported_names.isdisjoint({"json", "requests", "urllib", "socket", "aiohttp"})


def test_exported_from_epistemic_package() -> None:
    import ilc_core.epistemic as epistemic

    assert epistemic.MAINTENANCE_LOTTERY_RUNTIME_VERSION == MAINTENANCE_LOTTERY_RUNTIME_VERSION
    assert epistemic.MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN == (
        MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN
    )
    assert epistemic.MAINTENANCE_LOTTERY_NOT_ACTIVATED is True
    assert epistemic.request_maintenance_lottery_entry_stub is (
        request_maintenance_lottery_entry_stub
    )
