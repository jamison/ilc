# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only ECU status CLI surface for public-RC smoke tests."""

from __future__ import annotations

import argparse
import json
import os
import re
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

ECU_STATUS_CLI_VERSION = "ecu_status_cli_GAP_ECU_CLI_SURFACE_00.v0.1"
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_DEFAULT_TIMEOUT_SECONDS = 10.0
_MIN_TIMEOUT_SECONDS = 1.0
_MAX_TIMEOUT_SECONDS = 30.0


class EcuStatusCliError(ValueError):
    """Typed ECU status error that preserves stable phase tokens."""


def _require_agent_id(agent_id: str) -> str:
    if not isinstance(agent_id, str) or _AGENT_ID_RE.fullmatch(agent_id) is None:
        raise EcuStatusCliError("ecu_status_agent_id_invalid")
    return agent_id


def _endpoint_from_args(args: argparse.Namespace) -> str:
    endpoint = str(getattr(args, "endpoint", "") or "").strip()
    if not endpoint:
        endpoint = os.environ.get("ILC_ECU_STATUS_ENDPOINT", "").strip()
    if not endpoint:
        raise EcuStatusCliError("ecu_status_endpoint_missing_GAP_ECU_CLI_SURFACE_00")
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise EcuStatusCliError("ecu_status_endpoint_invalid")
    return endpoint


def _timeout_from_args(args: argparse.Namespace) -> float:
    timeout = getattr(args, "timeout", _DEFAULT_TIMEOUT_SECONDS)
    try:
        timeout_decimal = Decimal(str(timeout))
    except (InvalidOperation, ValueError) as exc:
        raise EcuStatusCliError("ecu_status_timeout_invalid") from exc
    if not timeout_decimal.is_finite():
        raise EcuStatusCliError("ecu_status_timeout_invalid")
    if timeout_decimal < Decimal(str(_MIN_TIMEOUT_SECONDS)) or timeout_decimal > Decimal(str(_MAX_TIMEOUT_SECONDS)):
        raise EcuStatusCliError("ecu_status_timeout_invalid")
    return float(timeout_decimal)


def _status_url(endpoint: str, agent_id: str) -> str:
    if "{agent_id}" in endpoint:
        return endpoint.replace("{agent_id}", agent_id)
    parsed = urlparse(endpoint)
    query = parsed.query
    agent_query = urlencode({"agent_id": agent_id})
    query = f"{query}&{agent_query}" if query else agent_query
    return urlunparse(parsed._replace(query=query))


def _require_decimal_string(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise EcuStatusCliError(f"ecu_status_{field_name}_invalid")
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise EcuStatusCliError(f"ecu_status_{field_name}_invalid") from exc
    if not parsed.is_finite():
        raise EcuStatusCliError(f"ecu_status_{field_name}_invalid")
    return value


def _load_status_payload(url: str, *, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(262_145)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise EcuStatusCliError("ecu_status_endpoint_unreachable") from exc
    if len(raw) > 262_144:
        raise EcuStatusCliError("ecu_status_response_too_large")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EcuStatusCliError("ecu_status_response_invalid_json") from exc
    if not isinstance(payload, dict):
        raise EcuStatusCliError("ecu_status_response_not_object")
    return payload


def normalize_ecu_status_payload(payload: dict[str, Any], *, agent_id: str, endpoint: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise EcuStatusCliError("ecu_status_response_not_object")
    response_agent_id = payload.get("agent_id", agent_id)
    if response_agent_id != agent_id:
        raise EcuStatusCliError("ecu_status_agent_id_mismatch")
    quote = _require_decimal_string(
        payload.get("pending_attribution_quote", payload.get("pending_attribution_quote_ecu", "0")),
        field_name="pending_attribution_quote",
    )
    balance = payload.get("committed_ecu_balance", payload.get("balance_ecu", "0"))
    balance = _require_decimal_string(balance, field_name="committed_ecu_balance")
    status = payload.get("status", payload.get("quote_status", "endpoint_response"))
    if not isinstance(status, str) or not status:
        raise EcuStatusCliError("ecu_status_status_invalid")
    return {
        "subcommand": "status",
        "agent_id": agent_id,
        "endpoint": endpoint,
        "pending_attribution_quote": quote,
        "committed_ecu_balance": balance,
        "status": status,
        "quote_epoch": payload.get("quote_epoch"),
        "non_claim": "quote_visibility_only_not_committed_balance",
        "version": ECU_STATUS_CLI_VERSION,
    }


def handle_ecu_status(args: argparse.Namespace) -> dict[str, Any]:
    agent_id = _require_agent_id(str(getattr(args, "agent_id", "") or ""))
    endpoint = _endpoint_from_args(args)
    timeout = _timeout_from_args(args)
    url = _status_url(endpoint, agent_id)
    payload = _load_status_payload(url, timeout=timeout)
    return normalize_ecu_status_payload(payload, agent_id=agent_id, endpoint=endpoint)


def run_ecu_command(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "ecu_subcommand", None)
    if subcommand == "status":
        return handle_ecu_status(args)
    raise EcuStatusCliError("ecu_subcommand_missing")
