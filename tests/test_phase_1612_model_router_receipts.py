# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ilc_core.sidecars.execution_receipt import SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION
from ilc_core.sidecars.execution_receipt import SidecarExecutionReceiptError

from ilc_model_router import receipt_store
from ilc_model_router.receipt_schema import (
    MODEL_ROUTER_COMPANION_SCHEMA_VERSION,
    MODEL_ROUTER_TOOL_ID,
    RouterCompanionRecord,
    RouterReceipt,
    RouterReceiptError,
)
from ilc_model_router.receipt_store import (
    check_nullifier,
    lookup_by_token,
    open_router_receipt_env,
    store_router_receipt,
)

AGENT_ID = "a" * 96
INPUTS_HASH = hashlib.sha256(b"inputs").hexdigest()
OUTPUTS_HASH = hashlib.sha256(b"outputs").hexdigest()


def _core_token(
    *,
    agent_id: str = AGENT_ID,
    epoch: int = 7,
    status: str = "success",
    error_token: str = "",
    inputs_hash: str = INPUTS_HASH,
    outputs_hash: str = OUTPUTS_HASH,
) -> str:
    payload = {
        "action_type": "model_inference",
        "agent_id_hex": agent_id,
        "epoch": epoch,
        "error_token": error_token,
        "inputs_hash": inputs_hash,
        "outputs_hash": outputs_hash,
        "status": status,
        "tool_id": MODEL_ROUTER_TOOL_ID,
    }
    encoded = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _companion(token: str, *, consent_status: str = "local_only") -> RouterCompanionRecord:
    return RouterCompanionRecord(
        receipt_token=token,
        model_id="openrouter/test-model",
        provider="openrouter",
        token_counts_input=11,
        token_counts_output=13,
        capability_class="inference",
        consent_status=consent_status,
    )


def _receipt(
    *,
    epoch: int = 7,
    status: str = "success",
    error_token: str = "",
    inputs_hash: str = INPUTS_HASH,
    outputs_hash: str = OUTPUTS_HASH,
) -> RouterReceipt:
    token = _core_token(
        epoch=epoch,
        status=status,
        error_token=error_token,
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
    )
    return RouterReceipt(
        action_type="model_inference",
        agent_id_hex=AGENT_ID,
        epoch=epoch,
        error_token=error_token,
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        receipt_token=token,
        schema_version=SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
        status=status,
        tool_id=MODEL_ROUTER_TOOL_ID,
        companion=_companion(token),
    )


def _env(tmp_path: Path):
    return open_router_receipt_env(tmp_path / "router_receipts.lmdb")


def test_store_lookup_roundtrip_preserves_all_fields(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        receipt = _receipt()
        store_router_receipt(env, receipt, b"\x01" * 32)

        found = lookup_by_token(env, receipt.receipt_token)

        assert found == receipt
        assert found is not None
        assert found.companion.model_id == "openrouter/test-model"
    finally:
        env.close()


def test_companion_record_serializes_separately_and_roundtrips(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        receipt = _receipt()
        store_router_receipt(env, receipt, b"\x02" * 32)

        found = lookup_by_token(env, receipt.receipt_token)

        assert found is not None
        assert found.companion.schema_version == MODEL_ROUTER_COMPANION_SCHEMA_VERSION
        assert found.companion.token_counts_input == 11
        assert found.companion.token_counts_output == 13
    finally:
        env.close()


def test_nullifier_collision_fails_closed_without_storing_second_receipt(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        first = _receipt(epoch=1, inputs_hash=hashlib.sha256(b"first").hexdigest())
        second = _receipt(epoch=1, inputs_hash=hashlib.sha256(b"second").hexdigest())
        nullifier = b"\x03" * 32
        store_router_receipt(env, first, nullifier)

        with pytest.raises(RouterReceiptError, match="model_router_nullifier_collision"):
            store_router_receipt(env, second, nullifier)

        assert lookup_by_token(env, second.receipt_token) is None
        assert lookup_by_token(env, first.receipt_token) == first
    finally:
        env.close()


def test_epoch_cap_uses_small_monkeypatched_cap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env = _env(tmp_path)
    monkeypatch.setattr(receipt_store, "MAX_ROUTER_RECEIPTS_PER_EPOCH", 2)
    try:
        store_router_receipt(env, _receipt(epoch=4, inputs_hash=hashlib.sha256(b"1").hexdigest()), b"\x04" * 32)
        store_router_receipt(env, _receipt(epoch=4, inputs_hash=hashlib.sha256(b"2").hexdigest()), b"\x05" * 32)

        with pytest.raises(RouterReceiptError, match="model_router_epoch_cap_exceeded"):
            store_router_receipt(
                env,
                _receipt(epoch=4, inputs_hash=hashlib.sha256(b"3").hexdigest()),
                b"\x06" * 32,
            )
    finally:
        env.close()


def test_epoch_cap_accepts_final_slot_then_rejects_next(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env = _env(tmp_path)
    monkeypatch.setattr(receipt_store, "MAX_ROUTER_RECEIPTS_PER_EPOCH", 3)
    try:
        for index in range(3):
            store_router_receipt(
                env,
                _receipt(epoch=5, inputs_hash=hashlib.sha256(f"slot-{index}".encode()).hexdigest()),
                bytes([10 + index]) * 32,
            )

        with pytest.raises(RouterReceiptError, match="model_router_epoch_cap_exceeded"):
            store_router_receipt(
                env,
                _receipt(epoch=5, inputs_hash=hashlib.sha256(b"overflow").hexdigest()),
                b"\x20" * 32,
            )
    finally:
        env.close()


def test_epoch_rejects_uint64_overflow(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        with pytest.raises(SidecarExecutionReceiptError, match="sidecar_execution_receipt_epoch_invalid"):
            store_router_receipt(env, _receipt(epoch=0x10000000000000000), b"\x21" * 32)
    finally:
        env.close()


def test_action_type_must_be_model_inference() -> None:
    token = _core_token()
    with pytest.raises(RouterReceiptError, match="router_receipt_action_type_must_be_model_inference"):
        RouterReceipt(
            action_type="query",
            agent_id_hex=AGENT_ID,
            epoch=7,
            error_token="",
            inputs_hash=INPUTS_HASH,
            outputs_hash=OUTPUTS_HASH,
            receipt_token=token,
            schema_version=SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
            status="success",
            tool_id=MODEL_ROUTER_TOOL_ID,
            companion=_companion(token),
        )


def test_success_rejects_non_empty_error_token() -> None:
    with pytest.raises(ValueError, match="sidecar_execution_receipt_error_token_without_failure"):
        _receipt(status="success", error_token="provider_timeout")


def test_failure_requires_error_token() -> None:
    with pytest.raises(ValueError, match="sidecar_execution_receipt_failure_error_token_required"):
        _receipt(status="failure", error_token="")


def test_hash_fields_are_64_lower_hex() -> None:
    receipt = _receipt()

    assert len(receipt.inputs_hash) == 64
    assert len(receipt.outputs_hash) == 64
    int(receipt.inputs_hash, 16)
    int(receipt.outputs_hash, 16)

    with pytest.raises(ValueError, match="sidecar_execution_receipt_inputs_hash_invalid"):
        _receipt(inputs_hash="not-a-sha256")


def test_consent_status_defaults_to_local_only() -> None:
    token = _core_token()
    companion = RouterCompanionRecord(
        receipt_token=token,
        model_id="openrouter/test-model",
        provider="openrouter",
        token_counts_input=0,
        token_counts_output=0,
    )

    assert companion.consent_status == "local_only"


def test_lookup_unknown_token_returns_none(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        assert lookup_by_token(env, "f" * 64) is None
    finally:
        env.close()


def test_check_nullifier_tracks_seen_state(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        nullifier = b"\x07" * 32
        assert check_nullifier(env, nullifier) is False
        store_router_receipt(env, _receipt(), nullifier)
        assert check_nullifier(env, nullifier) is True
    finally:
        env.close()


def test_companion_rejects_bad_counts_and_status() -> None:
    token = _core_token()
    with pytest.raises(RouterReceiptError, match="model_router_token_counts_input_invalid"):
        RouterCompanionRecord(
            receipt_token=token,
            model_id="m",
            provider="p",
            token_counts_input=-1,
            token_counts_output=0,
        )
    with pytest.raises(RouterReceiptError, match="model_router_consent_status_invalid"):
        _companion(token, consent_status="publish_now")
