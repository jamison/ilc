# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import math
from pathlib import Path

import pytest

from ilc_model_router.adapter import (
    ProviderAdapter,
    ProviderAdapterError,
    ProviderResponse,
    RouterRequest,
)
from ilc_model_router.anthropic_adapter import AnthropicAdapter
from ilc_model_router.receipt_schema import RouterReceiptError
from ilc_model_router.receipt_store import (
    check_nullifier,
    lookup_by_token,
    open_router_receipt_env,
    reserve_router_nullifier,
)
from ilc_model_router.router_engine import (
    ROUTER_DST,
    RouterEngine,
    _build_inputs_hash,
    _build_nullifier,
)

AGENT_ID = "b" * 96


class StubAdapter(ProviderAdapter):
    def __init__(self, response: ProviderResponse) -> None:
        self.response = response
        self.calls = 0

    def route(self, request: RouterRequest) -> ProviderResponse:
        self.calls += 1
        return self.response


class ReservationCheckingAdapter(ProviderAdapter):
    def __init__(self, env) -> None:
        self.env = env
        self.calls = 0
        self.saw_reserved_nullifier = False

    def route(self, request: RouterRequest) -> ProviderResponse:
        self.calls += 1
        nullifier = _build_nullifier(
            ROUTER_DST,
            request.agent_id_hex,
            request.request_nonce,
            request.epoch,
        )
        self.saw_reserved_nullifier = check_nullifier(self.env, nullifier)
        return _success_response("reserved")


class RaisingAdapter(ProviderAdapter):
    def __init__(self) -> None:
        self.calls = 0

    def route(self, request: RouterRequest) -> ProviderResponse:
        self.calls += 1
        raise RuntimeError("boom")


def _success_response(content: str = "hello") -> ProviderResponse:
    return ProviderResponse(
        status="success",
        content=content,
        error_token="",
        token_counts_input=3,
        token_counts_output=5,
    )


def _failure_response() -> ProviderResponse:
    return ProviderResponse(
        status="failure",
        content="",
        error_token="provider_timeout",
        token_counts_input=7,
        token_counts_output=0,
    )


def _partial_response() -> ProviderResponse:
    return ProviderResponse(
        status="partial",
        content="partial text",
        error_token="provider_partial_response",
        token_counts_input=11,
        token_counts_output=13,
    )


def _request(*, nonce: bytes = b"\x01" * 16, epoch: int = 7) -> RouterRequest:
    return RouterRequest(
        model_id="anthropic/test-model",
        provider="anthropic",
        messages=({"role": "user", "content": "hello"},),
        agent_id_hex=AGENT_ID,
        epoch=epoch,
        request_nonce=nonce,
    )


def _env(tmp_path: Path):
    return open_router_receipt_env(tmp_path / "model_router.lmdb")


def test_router_engine_happy_path_stores_receipt(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        adapter = StubAdapter(_success_response())
        receipt = RouterEngine(adapter, env).route(_request())

        assert adapter.calls == 1
        assert receipt.status == "success"
        assert receipt.error_token == ""
        assert receipt.companion.consent_status == "local_only"
        assert receipt.companion.model_id == "anthropic/test-model"
        assert lookup_by_token(env, receipt.receipt_token) == receipt
    finally:
        env.close()


def test_nullifier_collision_rejects_before_second_adapter_call(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        adapter = StubAdapter(_success_response())
        engine = RouterEngine(adapter, env)
        request = _request()
        engine.route(request)

        with pytest.raises(RouterReceiptError, match="model_router_nullifier_collision"):
            engine.route(request)

        assert adapter.calls == 1
    finally:
        env.close()


def test_adapter_failure_response_creates_failure_receipt(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        receipt = RouterEngine(StubAdapter(_failure_response()), env).route(_request())

        assert receipt.status == "failure"
        assert receipt.error_token == "provider_timeout"
        assert receipt.companion.token_counts_input == 7
        assert lookup_by_token(env, receipt.receipt_token) == receipt
    finally:
        env.close()


def test_adapter_partial_response_creates_partial_receipt(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        receipt = RouterEngine(StubAdapter(_partial_response()), env).route(_request())

        assert receipt.status == "partial"
        assert receipt.error_token == "provider_partial_response"
        assert receipt.companion.token_counts_output == 13
    finally:
        env.close()


def test_router_engine_rejects_nan_timeout(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        with pytest.raises(RouterReceiptError, match="router_engine_timeout_non_finite_or_non_positive"):
            RouterEngine(StubAdapter(_success_response()), env, timeout=float("nan"))
    finally:
        env.close()


def test_router_engine_rejects_negative_timeout(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        with pytest.raises(RouterReceiptError, match="router_engine_timeout_non_finite_or_non_positive"):
            RouterEngine(StubAdapter(_success_response()), env, timeout=-1)
    finally:
        env.close()


def test_inputs_hash_is_64_hex_and_not_raw_message_text() -> None:
    digest = _build_inputs_hash(_request())

    assert len(digest) == 64
    int(digest, 16)
    assert "hello" not in digest


def test_outputs_hash_is_64_hex_and_receipt_does_not_store_raw_content(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        receipt = RouterEngine(StubAdapter(_success_response("very private answer")), env).route(_request())

        assert len(receipt.outputs_hash) == 64
        int(receipt.outputs_hash, 16)
        assert "very private answer" not in str(receipt.to_dict())
    finally:
        env.close()


def test_nullifier_is_32_bytes() -> None:
    nullifier = _build_nullifier(ROUTER_DST, AGENT_ID, b"\x02" * 16, 7)

    assert type(nullifier) is bytes
    assert len(nullifier) == 32


def test_dst_changes_nullifier() -> None:
    first = _build_nullifier(ROUTER_DST, AGENT_ID, b"\x03" * 16, 7)
    second = _build_nullifier("different-router-dst", AGENT_ID, b"\x03" * 16, 7)

    assert first != second


def test_provider_response_rejects_success_with_error_token() -> None:
    with pytest.raises(ProviderAdapterError, match="provider_response_success_error_token_forbidden"):
        ProviderResponse(
            status="success",
            content="ok",
            error_token="provider_timeout",
            token_counts_input=1,
            token_counts_output=1,
        )


def test_stub_adapter_failure_scenario_returns_response() -> None:
    adapter = StubAdapter(_failure_response())
    response = adapter.route(_request())

    assert response.status == "failure"
    assert response.error_token == "provider_timeout"


def test_nullifier_is_reserved_before_adapter_dispatch(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        adapter = ReservationCheckingAdapter(env)
        RouterEngine(adapter, env).route(_request(nonce=b"\x04" * 16))

        assert adapter.calls == 1
        assert adapter.saw_reserved_nullifier is True
    finally:
        env.close()


def test_pending_reservation_fails_closed_without_adapter_dispatch(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        request = _request(nonce=b"\x05" * 16)
        nullifier = _build_nullifier(ROUTER_DST, request.agent_id_hex, request.request_nonce, request.epoch)
        reserve_router_nullifier(env, nullifier)
        adapter = StubAdapter(_success_response())

        with pytest.raises(RouterReceiptError, match="model_router_nullifier_collision"):
            RouterEngine(adapter, env).route(request)

        assert adapter.calls == 0
    finally:
        env.close()


def test_unexpected_adapter_exception_finalizes_failure_receipt(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        request = _request(nonce=b"\x06" * 16)
        adapter = RaisingAdapter()
        receipt = RouterEngine(adapter, env).route(request)

        assert adapter.calls == 1
        assert receipt.status == "failure"
        assert receipt.error_token == "provider_adapter_exception"
        assert lookup_by_token(env, receipt.receipt_token) == receipt
    finally:
        env.close()


def test_different_nonces_produce_distinct_input_hashes_and_receipt_tokens(tmp_path: Path) -> None:
    env = _env(tmp_path)
    try:
        adapter = StubAdapter(_success_response("same answer"))
        engine = RouterEngine(adapter, env)
        first = engine.route(_request(nonce=b"\x07" * 16))
        second = engine.route(_request(nonce=b"\x08" * 16))

        assert first.inputs_hash != second.inputs_hash
        assert first.receipt_token != second.receipt_token
    finally:
        env.close()


def test_anthropic_adapter_rejects_non_finite_timeout() -> None:
    assert not math.isfinite(float("inf"))
    with pytest.raises(ValueError, match="anthropic_adapter_timeout_non_finite_or_non_positive"):
        AnthropicAdapter(api_key="test", timeout=float("inf"))
