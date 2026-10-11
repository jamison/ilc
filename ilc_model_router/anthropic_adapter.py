# SPDX-License-Identifier: AGPL-3.0-only
"""Anthropic/OpenRouter-compatible Model Router adapter."""

from __future__ import annotations

import json
import math
import socket
import urllib.error
import urllib.request
import urllib.parse
from typing import Any, Mapping

from .adapter import (
    MAX_PROVIDER_CONTENT_CHARS,
    ProviderAdapter,
    ProviderResponse,
    RouterRequest,
)

ANTHROPIC_ADAPTER_VERSION = "anthropic_adapter_phase_1613.v0.1"
DEFAULT_ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
DEFAULT_OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 30.0
MAX_PROVIDER_RESPONSE_BYTES = 256 * 1024


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        raise urllib.error.HTTPError(req.full_url, code, "redirects_not_allowed", headers, fp)


class AnthropicAdapter(ProviderAdapter):
    """Concrete timeout-bound provider adapter.

    Tests for this phase use stub adapters and do not make live API calls. This
    implementation is included so the router package has a production-shaped
    adapter with bounded I/O and no redirect-following.
    """

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: str = DEFAULT_ANTHROPIC_ENDPOINT,
        timeout: float = DEFAULT_PROVIDER_TIMEOUT_SECONDS,
        provider_id: str = "anthropic",
    ) -> None:
        if type(api_key) is not str or not api_key:
            raise ValueError("anthropic_adapter_api_key_required")
        if type(endpoint) is not str or not _is_valid_https_endpoint(endpoint):
            raise ValueError("anthropic_adapter_endpoint_invalid")
        if type(provider_id) is not str or not provider_id:
            raise ValueError("anthropic_adapter_provider_id_invalid")
        self._api_key = api_key
        self._endpoint = endpoint
        self._provider_id = provider_id
        self._timeout = _require_timeout(timeout)
        self._opener = urllib.request.build_opener(_NoRedirectHandler())

    def route(
        self,
        request: RouterRequest,
        *,
        timeout: float | None = None,
    ) -> ProviderResponse:
        try:
            request_timeout = self._timeout if timeout is None else _require_timeout(timeout)
            payload = self._payload_for_request(request)
            encoded = json.dumps(
                payload,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            http_request = urllib.request.Request(
                self._endpoint,
                data=encoded,
                headers=self._headers(),
                method="POST",
            )
            with self._opener.open(http_request, timeout=request_timeout) as response:
                body = response.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
            if len(body) > MAX_PROVIDER_RESPONSE_BYTES:
                return _failure("provider_response_too_large")
            return self._parse_response(body)
        except TimeoutError:
            return _failure("provider_timeout")
        except socket.timeout:
            return _failure("provider_timeout")
        except urllib.error.HTTPError as exc:
            if exc.reason == "redirects_not_allowed":
                return _failure("provider_redirect_forbidden")
            return _failure(f"provider_http_{int(exc.code)}")
        except (urllib.error.URLError, OSError):
            return _failure("provider_network_error")
        except Exception:
            return _failure("provider_adapter_exception")

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ilc-model-router/phase-1613",
        }
        if self._provider_id == "openrouter":
            headers["Authorization"] = f"Bearer {self._api_key}"
        else:
            headers["x-api-key"] = self._api_key
            headers["anthropic-version"] = "2023-06-01"
        return headers

    def _payload_for_request(self, request: RouterRequest) -> dict[str, Any]:
        if self._provider_id == "openrouter":
            return {
                "messages": list(request.messages),
                "model": request.model_id,
                "stream": False,
            }
        return {
            "max_tokens": 1024,
            "messages": list(request.messages),
            "model": request.model_id,
        }

    def _parse_response(self, body: bytes) -> ProviderResponse:
        try:
            decoded = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return _failure("provider_response_invalid_json")
        if not isinstance(decoded, Mapping):
            return _failure("provider_response_invalid_shape")
        if self._provider_id == "openrouter":
            content = _extract_openrouter_content(decoded)
            usage = decoded.get("usage")
        else:
            content = _extract_anthropic_content(decoded)
            usage = decoded.get("usage")
        if content is None:
            return _failure("provider_response_missing_content")
        if len(content) > MAX_PROVIDER_CONTENT_CHARS:
            return _failure("provider_response_content_too_large")
        counts = _extract_usage_counts(usage)
        if counts is None:
            return _failure("provider_response_usage_invalid")
        input_tokens, output_tokens = counts
        return ProviderResponse(
            status="success",
            content=content,
            error_token="",
            token_counts_input=input_tokens,
            token_counts_output=output_tokens,
        )


def _failure(token: str) -> ProviderResponse:
    return ProviderResponse(
        status="failure",
        content="",
        error_token=token,
        token_counts_input=0,
        token_counts_output=0,
    )


def _require_timeout(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("anthropic_adapter_timeout_invalid")
    timeout_float = float(value)
    if not math.isfinite(timeout_float) or timeout_float <= 0:
        raise ValueError("anthropic_adapter_timeout_non_finite_or_non_positive")
    return timeout_float


def _extract_openrouter_content(decoded: Mapping[str, Any]) -> str | None:
    choices = decoded.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, Mapping):
        return None
    message = first.get("message")
    if not isinstance(message, Mapping):
        return None
    content = message.get("content")
    return content if type(content) is str and content else None


def _extract_anthropic_content(decoded: Mapping[str, Any]) -> str | None:
    blocks = decoded.get("content")
    if not isinstance(blocks, list):
        return None
    text_parts: list[str] = []
    for block in blocks:
        if isinstance(block, Mapping) and block.get("type") == "text":
            text = block.get("text")
            if type(text) is str:
                text_parts.append(text)
    content = "".join(text_parts)
    return content or None


def _is_valid_https_endpoint(endpoint: str) -> bool:
    parsed = urllib.parse.urlparse(endpoint)
    return parsed.scheme == "https" and bool(parsed.netloc) and bool(parsed.path)


def _extract_usage_counts(usage: object) -> tuple[int, int] | None:
    if not isinstance(usage, Mapping):
        return 0, 0
    input_value = usage.get("input_tokens", usage.get("prompt_tokens", 0))
    output_value = usage.get("output_tokens", usage.get("completion_tokens", 0))
    input_count = _non_negative_int(input_value)
    output_count = _non_negative_int(output_value)
    if input_count is None or output_count is None:
        return None
    return input_count, output_count


def _non_negative_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str) and value and value.isdecimal():
        return int(value)
    return None


__all__ = [
    "ANTHROPIC_ADAPTER_VERSION",
    "DEFAULT_ANTHROPIC_ENDPOINT",
    "DEFAULT_OPENROUTER_ENDPOINT",
    "DEFAULT_PROVIDER_TIMEOUT_SECONDS",
    "MAX_PROVIDER_RESPONSE_BYTES",
    "AnthropicAdapter",
]
