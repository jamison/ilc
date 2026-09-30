# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1611 regression tests for model_inference sidecar action type."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from ilc_core.sidecars.execution_receipt import (
    ACTION_TYPES,
    SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
    SidecarExecutionReceipt,
    SidecarExecutionReceiptError,
    SidecarExecutionReceiptStore,
)


AGENT_ID = "a" * 96
ORIGINAL_ACTION_TYPES = (
    "attribution_batch",
    "ecu_transfer",
    "graph_submit",
    "ilc_transfer",
    "query",
    "unknown",
)


def _hash(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _receipt(**overrides: Any) -> SidecarExecutionReceipt:
    params = {
        "action_type": "model_inference",
        "agent_id_hex": AGENT_ID,
        "epoch": 1611,
        "error_token": "",
        "inputs_hash": _hash({"prompt_hash": "x"}),
        "outputs_hash": _hash({"completion_hash": "y"}),
        "status": "success",
        "tool_id": "ilc-model-router-v1",
    }
    params.update(overrides)
    return SidecarExecutionReceipt(**params)


def test_model_inference_is_in_action_types() -> None:
    assert "model_inference" in ACTION_TYPES


def test_model_inference_receipt_is_accepted() -> None:
    receipt = _receipt()

    assert receipt.action_type == "model_inference"
    assert receipt.to_dict()["action_type"] == "model_inference"


def test_model_inference_store_roundtrip_preserves_action_type(tmp_path: Path) -> None:
    store = SidecarExecutionReceiptStore(tmp_path / "receipts")
    receipt = _receipt()

    store.append_receipt(receipt)

    assert store.lookup_by_token(receipt.receipt_token) == receipt
    assert store.read_receipts_for_epoch(1611) == [receipt]
    assert store.lookup_by_token(receipt.receipt_token).action_type == "model_inference"


def test_execution_receipt_epoch_cap_accepts_final_slot_then_rejects_next(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.sidecars.execution_receipt as execution_receipt

    monkeypatch.setattr(execution_receipt, "MAX_SIDECAR_EXECUTION_RECEIPTS_PER_EPOCH", 3)
    store = SidecarExecutionReceiptStore(tmp_path / "cap")
    try:
        for index in range(3):
            store.append_receipt(
                _receipt(
                    epoch=42,
                    inputs_hash=_hash({"slot": index}),
                )
            )

        with pytest.raises(
            SidecarExecutionReceiptError,
            match="sidecar_execution_receipt_epoch_full",
        ):
            store.append_receipt(_receipt(epoch=42, inputs_hash=_hash({"slot": "overflow"})))
    finally:
        store.env.close()


def test_execution_receipt_rejects_uint64_epoch_overflow() -> None:
    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_epoch_invalid",
    ):
        _receipt(epoch=0x10000000000000000)


def test_schema_version_remains_v0_1() -> None:
    assert SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION == (
        "sidecar_execution_receipt_GAP_HARNESS_SIDECAR_05.v0.1"
    )
    assert _receipt().to_dict()["schema_version"] == SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION


@pytest.mark.parametrize("action_type", ORIGINAL_ACTION_TYPES)
def test_original_action_types_still_accept_and_roundtrip(
    tmp_path: Path,
    action_type: str,
) -> None:
    store = SidecarExecutionReceiptStore(tmp_path / action_type)
    receipt = _receipt(action_type=action_type, tool_id=f"tool-{action_type}")

    store.append_receipt(receipt)

    assert store.lookup_by_token(receipt.receipt_token) == receipt
    assert store.read_receipts_for_epoch(1611) == [receipt]


def test_invalid_action_type_still_rejected() -> None:
    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_action_type_invalid",
    ):
        _receipt(action_type="not_a_valid_action")


def test_model_inference_action_type_is_case_sensitive() -> None:
    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_action_type_invalid",
    ):
        _receipt(action_type="MODEL_INFERENCE")
