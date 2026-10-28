# SPDX-License-Identifier: AGPL-3.0-only
"""Strict reusable validation primitives for release upgrade evidence."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Mapping

from ilc_core.encoding.cidv1 import node_id_from_obj, parse_nodeid_strict


class UpgradeCheckError(ValueError):
    """Typed upgrade-check error carrying a stable token."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token
        self.message = message or token


def reject_json_constant(value: str) -> None:
    raise ValueError(f"upgrade_assertion_non_finite_json:{value}")


def require_string(value: Any, field: str, *, max_chars: int = 512) -> str:
    if not isinstance(value, str) or not value:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_string:{field}")
    if len(value) > max_chars:
        raise UpgradeCheckError(f"upgrade_assertion_string_too_long:{field}")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise UpgradeCheckError(f"upgrade_assertion_control_character:{field}")
    return value


def require_literal(value: Any, field: str, expected: str) -> str:
    text = require_string(value, field)
    if text != expected:
        raise UpgradeCheckError(f"upgrade_assertion_literal_mismatch:{field}")
    return text


def require_hex(value: Any, field: str, pattern: re.Pattern[str]) -> str:
    text = require_string(value, field)
    if pattern.fullmatch(text) is None:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_hex:{field}")
    return text


def require_cid_like(value: Any, field: str, pattern: re.Pattern[str]) -> str:
    text = require_string(value, field)
    if pattern.fullmatch(text) is None:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_cid:{field}")
    return text


def require_timestamp(value: Any, field: str, pattern: re.Pattern[str]) -> str:
    text = require_string(value, field)
    if pattern.fullmatch(text) is None:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_timestamp:{field}")
    try:
        datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_timestamp:{field}") from exc
    return text


def require_exact_fields(
    value: Mapping[str, Any],
    *,
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
    object_name: str,
) -> None:
    keys = set(value)
    missing = required - keys
    if missing:
        raise UpgradeCheckError(
            f"upgrade_assertion_required_field_missing:{object_name}:{sorted(missing)[0]}"
        )
    unknown = keys - required - optional
    if unknown:
        raise UpgradeCheckError(
            f"upgrade_assertion_unknown_field:{object_name}:{sorted(unknown)[0]}"
        )


def require_strict_node_cid(
    value: Mapping[str, Any],
    *,
    object_name: str,
) -> str:
    cid = require_string(value.get("cid"), f"{object_name}.cid", max_chars=255)
    try:
        parse_nodeid_strict(cid)
        observed = node_id_from_obj(
            {key: child for key, child in value.items() if key != "cid"}
        )
    except (TypeError, ValueError) as exc:
        raise UpgradeCheckError(f"upgrade_assertion_cid_invalid:{object_name}") from exc
    if observed != cid:
        raise UpgradeCheckError(f"upgrade_assertion_cid_mismatch:{object_name}")
    return cid


def require_bounded_list(
    value: Any,
    *,
    field: str,
    maximum: int,
) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_list:{field}")
    if len(value) > maximum:
        raise UpgradeCheckError(f"upgrade_assertion_list_too_large:{field}")
    return value
