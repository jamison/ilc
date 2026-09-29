# SPDX-License-Identifier: AGPL-3.0-only
"""Router engine orchestration for local-first model inference receipts."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Final

from ilc_core.sidecars.execution_receipt import (
    SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
    SidecarExecutionReceipt,
)

from .adapter import ProviderAdapter, ProviderResponse, RouterRequest
from .receipt_schema import (
    MODEL_ROUTER_TOOL_ID,
    RouterCompanionRecord,
    RouterReceipt,
    RouterReceiptError,
)
from .receipt_store import (
    finalize_reserved_router_receipt,
    reserve_router_nullifier,
)

ROUTER_ENGINE_VERSION: Final[str] = "router_engine_phase_1613.v0.1"
ROUTER_DST: Final[str] = "ilc-model-router-request-v1"
ROUTER_NULLIFIER_SCHEMA_VERSION: Final[str] = "ilc_model_router_nullifier_phase_1610.v0.1"
ROUTER_TIMEOUT_SECONDS: Final[float] = 30.0


class RouterEngine:
    """Orchestrate nullifier reservation, adapter dispatch, receipt creation, and storage."""

    def __init__(
        self,
        adapter: ProviderAdapter,
        store_env,
        timeout: float = ROUTER_TIMEOUT_SECONDS,
    ) -> None:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise RouterReceiptError("router_engine_timeout_invalid")
        timeout_float = float(timeout)
        if not math.isfinite(timeout_float) or timeout_float <= 0:
            raise RouterReceiptError("router_engine_timeout_non_finite_or_non_positive")
        if not isinstance(adapter, ProviderAdapter):
            raise RouterReceiptError("router_engine_adapter_invalid")
        self._adapter = adapter
        self._store_env = store_env
        self._timeout = timeout_float

    @property
    def timeout(self) -> float:
        return self._timeout

    def route(self, request: RouterRequest) -> RouterReceipt:
        if not isinstance(request, RouterRequest):
            raise RouterReceiptError("router_engine_request_invalid")
        nullifier = _build_nullifier(
            ROUTER_DST,
            request.agent_id_hex,
            request.request_nonce,
            request.epoch,
        )
        reserve_router_nullifier(self._store_env, nullifier)
        try:
            response = self._adapter.route(request)
        except Exception:
            response = ProviderResponse(
                status="failure",
                content="",
                error_token="provider_adapter_exception",
                token_counts_input=0,
                token_counts_output=0,
            )
        if not isinstance(response, ProviderResponse):
            response = ProviderResponse(
                status="failure",
                content="",
                error_token="provider_response_invalid",
                token_counts_input=0,
                token_counts_output=0,
            )
        receipt = _build_router_receipt(request, response)
        finalize_reserved_router_receipt(self._store_env, receipt, nullifier)
        return receipt


def _build_nullifier(dst: str, agent_id_hex: str, request_nonce: bytes, epoch: int) -> bytes:
    payload = {
        "agent_id_hex": agent_id_hex,
        "dst": dst,
        "epoch": epoch,
        "request_nonce": request_nonce.hex(),
        "schema_version": ROUTER_NULLIFIER_SCHEMA_VERSION,
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).digest()


def _build_inputs_hash(request: RouterRequest) -> str:
    payload = {
        "agent_id_hex": request.agent_id_hex,
        "epoch": request.epoch,
        "messages": list(request.messages),
        "model_id": request.model_id,
        "provider": request.provider,
        "request_nonce": request.request_nonce.hex(),
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _build_outputs_hash(response: ProviderResponse) -> str:
    payload = {
        "content": response.content,
        "error_token": response.error_token,
        "status": response.status,
        "token_counts_input": response.token_counts_input,
        "token_counts_output": response.token_counts_output,
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _build_router_receipt(request: RouterRequest, response: ProviderResponse) -> RouterReceipt:
    inputs_hash = _build_inputs_hash(request)
    outputs_hash = _build_outputs_hash(response)
    core = SidecarExecutionReceipt(
        tool_id=MODEL_ROUTER_TOOL_ID,
        action_type="model_inference",
        epoch=request.epoch,
        agent_id_hex=request.agent_id_hex,
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        status=response.status,
        error_token=response.error_token,
    )
    companion = RouterCompanionRecord(
        receipt_token=core.receipt_token,
        model_id=request.model_id,
        provider=request.provider,
        token_counts_input=response.token_counts_input,
        token_counts_output=response.token_counts_output,
        capability_class="inference",
        consent_status="local_only",
    )
    return RouterReceipt(
        action_type=core.action_type,
        agent_id_hex=core.agent_id_hex,
        epoch=core.epoch,
        error_token=core.error_token,
        inputs_hash=core.inputs_hash,
        outputs_hash=core.outputs_hash,
        receipt_token=core.receipt_token,
        schema_version=SIDECAR_EXECUTION_RECEIPT_SCHEMA_VERSION,
        status=core.status,
        tool_id=core.tool_id,
        companion=companion,
    )


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


__all__ = [
    "ROUTER_DST",
    "ROUTER_ENGINE_VERSION",
    "ROUTER_NULLIFIER_SCHEMA_VERSION",
    "ROUTER_TIMEOUT_SECONDS",
    "RouterEngine",
    "_build_inputs_hash",
    "_build_nullifier",
    "_build_outputs_hash",
    "_build_router_receipt",
]
