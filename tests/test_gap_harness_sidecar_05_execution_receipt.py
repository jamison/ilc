# SPDX-License-Identifier: AGPL-3.0-only
"""Sidecar execution receipt tests for GAP-HARNESS-SIDECAR-05."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from ilc_core.sidecars.execution_receipt import (
    RECEIPTS_DB_NAME,
    SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
    TOKEN_INDEX_DB_NAME,
    SidecarExecutionReceipt,
    SidecarExecutionReceiptError,
    SidecarExecutionReceiptStore,
    hash_receipt_component,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ilc_core/sidecars/execution_receipt.py"
AGENT_ID = "a" * 96


def _hash(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _receipt(**overrides: Any) -> SidecarExecutionReceipt:
    params = {
        "action_type": "graph_submit",
        "agent_id_hex": AGENT_ID,
        "epoch": 7,
        "error_token": "",
        "inputs_hash": _hash({"input": "x"}),
        "outputs_hash": _hash({"output": "y"}),
        "status": "success",
        "tool_id": "graph_submit_local",
    }
    params.update(overrides)
    return SidecarExecutionReceipt(**params)


def test_receipt_token_is_sha256_of_all_non_token_fields() -> None:
    receipt = _receipt()
    expected = _hash(
        {
            "action_type": "graph_submit",
            "agent_id_hex": AGENT_ID,
            "epoch": 7,
            "error_token": "",
            "inputs_hash": _hash({"input": "x"}),
            "outputs_hash": _hash({"output": "y"}),
            "status": "success",
            "tool_id": "graph_submit_local",
        }
    )

    assert receipt.receipt_token == expected
    assert receipt.to_dict()["schema_version"] == SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION


def test_receipt_round_trips_from_dict_and_detects_token_tamper() -> None:
    receipt = _receipt()
    round_trip = SidecarExecutionReceipt.from_dict(receipt.to_dict())

    assert round_trip == receipt

    tampered = receipt.to_dict()
    tampered["outputs_hash"] = "b" * 64
    with pytest.raises(SidecarExecutionReceiptError, match="sidecar_execution_receipt_token_mismatch"):
        SidecarExecutionReceipt.from_dict(tampered)


def test_receipt_from_dict_rejects_extra_fields() -> None:
    payload = _receipt().to_dict()
    payload["future_field"] = "unexpected"

    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_field_set_invalid",
    ):
        SidecarExecutionReceipt.from_dict(payload)


def test_hash_receipt_component_rejects_non_canonical_float() -> None:
    with pytest.raises(ValueError):
        hash_receipt_component({"bad": float("nan")})


def test_status_failure_requires_error_token() -> None:
    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_failure_error_token_required",
    ):
        _receipt(status="failure")


def test_non_failure_rejects_error_token() -> None:
    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_error_token_without_failure",
    ):
        _receipt(status="success", error_token="unexpected")


def test_receipt_validates_agent_id_and_hash_formats() -> None:
    with pytest.raises(SidecarExecutionReceiptError, match="sidecar_execution_receipt_agent_id_invalid"):
        _receipt(agent_id_hex="A" * 96)
    with pytest.raises(SidecarExecutionReceiptError, match="sidecar_execution_receipt_inputs_hash_invalid"):
        _receipt(inputs_hash="a" * 63)
    with pytest.raises(SidecarExecutionReceiptError, match="sidecar_execution_receipt_epoch_invalid"):
        _receipt(epoch=-1)


def test_store_appends_reads_epoch_in_ordinal_order_and_looks_up_token(tmp_path: Path) -> None:
    store = SidecarExecutionReceiptStore(tmp_path / "receipts")
    first = _receipt(epoch=2, tool_id="tool-a")
    second = _receipt(epoch=2, tool_id="tool-b")
    third = _receipt(epoch=3, tool_id="tool-c")

    store.append_receipt(first)
    store.append_receipt(second)
    store.append_receipt(third)

    assert store.read_receipts_for_epoch(2) == [first, second]
    assert store.read_receipts_for_epoch(3) == [third]
    assert store.lookup_by_token(second.receipt_token) == second
    assert store.lookup_by_token("f" * 64) is None


def test_store_rejects_duplicate_receipt_token(tmp_path: Path) -> None:
    store = SidecarExecutionReceiptStore(tmp_path / "receipts")
    receipt = _receipt()

    store.append_receipt(receipt)
    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_token_duplicate",
    ):
        store.append_receipt(receipt)


def test_store_uses_exact_lmdb_sub_database_names(tmp_path: Path) -> None:
    store = SidecarExecutionReceiptStore(tmp_path / "receipts")

    assert store.env.open_db(RECEIPTS_DB_NAME) is not None
    assert store.env.open_db(TOKEN_INDEX_DB_NAME) is not None


def test_store_fails_closed_on_corrupted_token_index(tmp_path: Path) -> None:
    store = SidecarExecutionReceiptStore(tmp_path / "receipts")
    receipt = _receipt()
    store.append_receipt(receipt)

    with store.env.begin(write=True) as txn:
        txn.put(receipt.receipt_token.encode("utf-8"), b"bad", db=store._token_index_db)

    with pytest.raises(
        SidecarExecutionReceiptError,
        match="sidecar_execution_receipt_token_index_corrupted",
    ):
        store.lookup_by_token(receipt.receipt_token)


def test_store_fails_closed_on_corrupted_receipt_payload(tmp_path: Path) -> None:
    store = SidecarExecutionReceiptStore(tmp_path / "receipts")
    receipt = _receipt()
    store.append_receipt(receipt)

    with store.env.begin(write=True) as txn:
        key = txn.get(receipt.receipt_token.encode("utf-8"), db=store._token_index_db)
        assert key is not None
        txn.put(key, b"not-json", db=store._receipts_db)

    with pytest.raises(SidecarExecutionReceiptError, match="sidecar_execution_receipt_corrupted"):
        store.read_receipts_for_epoch(receipt.epoch)


def test_module_has_no_wall_clock_network_or_public_serving_surface() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "datetime.now" not in source
    assert "time.time" not in source
    forbidden_import_roots = {"aiohttp", "fastapi", "httpx", "requests", "socket", "urllib"}
    forbidden_function_prefixes = ("serve_", "publish_", "delete_", "remove_")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_import_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_import_roots
        if isinstance(node, ast.FunctionDef):
            assert not node.name.startswith(forbidden_function_prefixes)


def test_json_dumps_calls_lock_sort_keys_and_allow_nan_false() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    dumps_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "dumps"
    ]

    assert dumps_calls
    for call in dumps_calls:
        kwargs = {keyword.arg: keyword.value for keyword in call.keywords}
        assert isinstance(kwargs["sort_keys"], ast.Constant)
        assert kwargs["sort_keys"].value is True
        assert isinstance(kwargs["allow_nan"], ast.Constant)
        assert kwargs["allow_nan"].value is False
