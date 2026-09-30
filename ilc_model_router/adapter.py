# SPDX-License-Identifier: AGPL-3.0-only
"""Provider adapter contracts for the local-first Model Router."""

from __future__ import annotations

import json
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

PROVIDER_ADAPTER_VERSION = "provider_adapter_phase_1613.v0.1"
PROVIDER_RESPONSE_STATUSES = frozenset({"failure", "partial", "success"})
MAX_ROUTER_MESSAGES = 64
MAX_ROUTER_REQUEST_BYTES = 64 * 1024
MAX_PROVIDER_CONTENT_CHARS = 64 * 1024
MAX_ROUTER_TEXT_CHARS = 256
_HEX = frozenset("0123456789abcdef")


class ProviderAdapterError(ValueError):
    """Stable provider adapter validation error."""


@dataclass(frozen=True)
class RouterRequest:
    """Canonical router request metadata.

    The raw message content is only used transiently to build commitments and
    provider requests. It is never stored in Model Router receipts.
    """

    model_id: str
    provider: str
    messages: tuple[dict[str, Any], ...]
    agent_id_hex: str
    epoch: int
    request_nonce: bytes

    def __post_init__(self) -> None:
        _require_text(self.model_id, "model_router_model_id_invalid")
        _require_text(self.provider, "model_router_provider_invalid")
        _require_hex(self.agent_id_hex, "model_router_agent_id_invalid", length=96)
        _require_non_negative_int(self.epoch, "model_router_epoch_invalid")
        if type(self.request_nonce) is not bytes or len(self.request_nonce) != 16:
            raise ProviderAdapterError("model_router_request_nonce_invalid")
        if not isinstance(self.messages, tuple) or not self.messages:
            raise ProviderAdapterError("model_router_messages_invalid")
        if len(self.messages) > MAX_ROUTER_MESSAGES:
            raise ProviderAdapterError("model_router_messages_too_many")
        for message in self.messages:
            if not isinstance(message, dict):
                raise ProviderAdapterError("model_router_message_invalid")
        encoded = _canonical_json_bytes(list(self.messages), "model_router_messages_invalid")
        if len(encoded) > MAX_ROUTER_REQUEST_BYTES:
            raise ProviderAdapterError("model_router_messages_too_large")

    @classmethod
    def build(
        cls,
        *,
        model_id: str,
        provider: str,
        messages: tuple[dict[str, Any], ...],
        agent_id_hex: str,
        epoch: int,
    ) -> "RouterRequest":
        """Build a request with a fresh secure per-request nonce."""

        return cls(
            model_id=model_id,
            provider=provider,
            messages=messages,
            agent_id_hex=agent_id_hex,
            epoch=epoch,
            request_nonce=secrets.token_bytes(16),
        )


@dataclass(frozen=True)
class ProviderResponse:
    """Provider response contract. Adapters return this instead of raising."""

    status: str
    content: str
    error_token: str
    token_counts_input: int
    token_counts_output: int

    def __post_init__(self) -> None:
        if self.status not in PROVIDER_RESPONSE_STATUSES:
            raise ProviderAdapterError("provider_response_status_invalid")
        if type(self.content) is not str:
            raise ProviderAdapterError("provider_response_content_invalid")
        if len(self.content) > MAX_PROVIDER_CONTENT_CHARS:
            raise ProviderAdapterError("provider_response_content_too_large")
        _require_non_negative_int(
            self.token_counts_input,
            "provider_response_token_counts_input_invalid",
        )
        _require_non_negative_int(
            self.token_counts_output,
            "provider_response_token_counts_output_invalid",
        )
        if type(self.error_token) is not str or len(self.error_token) > MAX_ROUTER_TEXT_CHARS:
            raise ProviderAdapterError("provider_response_error_token_invalid")
        if self.status == "success":
            if not self.content:
                raise ProviderAdapterError("provider_response_success_content_required")
            if self.error_token:
                raise ProviderAdapterError("provider_response_success_error_token_forbidden")
        if self.status in {"failure", "partial"} and not self.error_token:
            raise ProviderAdapterError("provider_response_error_token_required")


class ProviderAdapter(ABC):
    """Abstract provider adapter. Concrete adapters must not raise from route()."""

    @abstractmethod
    def route(
        self,
        request: RouterRequest,
        *,
        timeout: float | None = None,
    ) -> ProviderResponse:
        """Route a request to the provider and return a receipt-shaped response."""


def _canonical_json_bytes(payload: object, token: str) -> bytes:
    try:
        return json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ProviderAdapterError(token) from exc


def _require_text(value: Any, token: str) -> str:
    if type(value) is not str or not value or len(value) > MAX_ROUTER_TEXT_CHARS:
        raise ProviderAdapterError(token)
    return value


def _require_non_negative_int(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProviderAdapterError(token)
    return value


def _require_hex(value: Any, token: str, *, length: int) -> str:
    if type(value) is not str or len(value) != length:
        raise ProviderAdapterError(token)
    if value.lower() != value or any(char not in _HEX for char in value):
        raise ProviderAdapterError(token)
    return value


__all__ = [
    "MAX_PROVIDER_CONTENT_CHARS",
    "MAX_ROUTER_MESSAGES",
    "MAX_ROUTER_REQUEST_BYTES",
    "MAX_ROUTER_TEXT_CHARS",
    "PROVIDER_ADAPTER_VERSION",
    "PROVIDER_RESPONSE_STATUSES",
    "ProviderAdapter",
    "ProviderAdapterError",
    "ProviderResponse",
    "RouterRequest",
]
