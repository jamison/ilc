from __future__ import annotations

from types import SimpleNamespace

import pytest

from ilc_core.cli.mcp_cli import _invoke_tool, _read_payload
from ilc_core.exceptions import CliPayloadError, CliToolInvocationError


def test_read_payload_missing_raises_cli_payload_error() -> None:
    args = SimpleNamespace(payload_file=None, payload=None)
    with pytest.raises(CliPayloadError, match="No payload provided"):
        _read_payload(args)


def test_read_payload_invalid_json_raises_cli_payload_error() -> None:
    args = SimpleNamespace(payload_file=None, payload="{invalid")
    with pytest.raises(CliPayloadError, match="Invalid JSON payload"):
        _read_payload(args)


def test_read_payload_missing_file_raises_cli_payload_error() -> None:
    args = SimpleNamespace(payload_file="missing_payload.json", payload=None)
    with pytest.raises(CliPayloadError, match="Payload file not found"):
        _read_payload(args)


def test_invoke_tool_wraps_value_error_as_cli_tool_invocation_error() -> None:
    class _FailingService:
        def handle_request(self, tool_name: str, payload: dict) -> dict:
            raise ValueError("Unknown tool: bad.tool")

    with pytest.raises(CliToolInvocationError, match="Unknown tool: bad.tool"):
        _invoke_tool(_FailingService(), "bad.tool", {})


def test_invoke_tool_returns_result_on_success() -> None:
    expected = {"ok": True}

    class _SuccessfulService:
        def handle_request(self, tool_name: str, payload: dict) -> dict:
            return expected

    assert _invoke_tool(_SuccessfulService(), "ilc.capabilities.get", {}) == expected
