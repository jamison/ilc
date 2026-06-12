# SPDX-License-Identifier: AGPL-3.0-only
"""HB-001 genesis-authority assertion builder.

Phase 1557 wires caller-facing helpers over the Phase 858 assertion schema.
The schema source remains ``ilc_core.genesis.assertion_schema``.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any, Mapping

from ilc_core.genesis.assertion_schema import (
    GENESIS_AUTHORITY_KEY_ALGORITHM,
    GenesisAssertionContent,
    GenesisAssertionError,
    GenesisAuthorityKey,
    GenesisValidatorEntry,
    encode_genesis_assertion_payload,
    verify_genesis_assertion_schema,
)
from ilc_core.private_json_guardrails import reject_float

GENESIS_AUTHORITY_ASSERTION_BUILDER_VERSION = "genesis_authority_assertion_builder_1557.v0.1"


def build_genesis_authority_assertions(genesis_config: dict[str, Any]) -> list[dict[str, Any]]:
    """Build unsigned ``assert.truth`` genesis-authority assertions from config.

    The returned envelope is ready for the Phase 1560 signing ceremony to attach
    a real ML-DSA-65 signature. This helper does not sign.
    """
    if not isinstance(genesis_config, dict):
        raise GenesisAssertionError(
            "genesis_authority_assertion_config_must_be_dict",
            "genesis_config must be a dict",
        )
    reject_float(genesis_config, "genesis_authority_assertion_float_not_allowed")

    agent_id = _required_str(genesis_config, "agent_id")
    content = GenesisAssertionContent(
        kind="genesis_authority_assertion",
        schema_version=1,
        network_id=_required_str(genesis_config, "network_id"),
        is_testnet=_required_bool(genesis_config, "is_testnet"),
        real_ecu=_required_bool(genesis_config, "real_ecu"),
        genesis_epoch=0,
        genesis_authority_key=_authority_key_from_config(genesis_config),
        validators=_validators_from_config(genesis_config),
        f=_fault_tolerance_from_config(genesis_config),
        predecessor_genesis_cid=_optional_str(genesis_config, "predecessor_genesis_cid"),
    )
    payload = json.loads(encode_genesis_assertion_payload(content).decode("utf-8"))
    payload["agent_id"] = agent_id
    payload["sig"] = _optional_str(genesis_config, "sig") or ""
    return [payload]


def verify_genesis_authority_assertions(
    assertions: list[dict[str, Any]],
    *,
    expected_network_id: str,
    expected_agent_id: str,
) -> bool:
    """Verify unsigned genesis-authority assertion structure and authority agent."""
    if not isinstance(assertions, list) or not assertions:
        raise GenesisAssertionError(
            "genesis_authority_assertions_must_be_non_empty_list",
            "assertions must be a non-empty list",
        )
    if not isinstance(expected_agent_id, str) or not expected_agent_id:
        raise GenesisAssertionError(
            "genesis_authority_expected_agent_id_missing",
            "expected_agent_id must be a non-empty string",
        )
    for assertion in assertions:
        if not isinstance(assertion, dict):
            raise GenesisAssertionError(
                "genesis_authority_assertion_entry_must_be_dict",
                "each assertion must be a dict",
            )
        if assertion.get("agent_id") != expected_agent_id:
            raise GenesisAssertionError(
                "genesis_authority_assertion_agent_id_mismatch",
                "assertion agent_id does not match expected_agent_id",
            )
        verify_genesis_assertion_schema(
            assertion,
            expected_network_id=expected_network_id,
        )
    return True


def _authority_key_from_config(genesis_config: Mapping[str, Any]) -> GenesisAuthorityKey:
    raw = genesis_config.get("genesis_authority_key")
    if not isinstance(raw, dict):
        raise GenesisAssertionError(
            "genesis_authority_key_config_must_be_dict",
            "genesis_authority_key must be a dict",
        )
    public_key_hex = _required_str(raw, "public_key_hex")
    key_id = raw.get("key_id")
    if key_id is None:
        key_id = hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()[:16]
    return GenesisAuthorityKey(
        algorithm=str(raw.get("algorithm", GENESIS_AUTHORITY_KEY_ALGORITHM)),
        public_key_hex=public_key_hex,
        key_id=str(key_id),
    )


def _validators_from_config(genesis_config: Mapping[str, Any]) -> tuple[GenesisValidatorEntry, ...]:
    raw_validators = genesis_config.get("validators")
    if not isinstance(raw_validators, list) or not raw_validators:
        raise GenesisAssertionError(
            "genesis_authority_validators_must_be_non_empty_list",
            "validators must be a non-empty list",
        )
    validators: list[GenesisValidatorEntry] = []
    for index, row in enumerate(raw_validators, start=1):
        if not isinstance(row, dict):
            raise GenesisAssertionError(
                "genesis_authority_validator_config_must_be_dict",
                f"validators[{index - 1}] must be a dict",
            )
        validators.append(
            GenesisValidatorEntry(
                validator_id=_optional_positive_int(row, "validator_id") or index,
                agent_id=_required_str(row, "agent_id"),
                validator_key=_required_one_of(row, ("validator_key", "validator_public_key")),
                stake_micro_ecu=_canonical_non_negative_decimal_str(
                    row.get("stake_micro_ecu", row.get("stake", "0"))
                ),
                role=str(row.get("role", "genesis_validator")),
            )
        )
    return tuple(validators)


def _fault_tolerance_from_config(genesis_config: Mapping[str, Any]) -> int:
    raw = genesis_config.get("f")
    if raw is None:
        validators = genesis_config.get("validators")
        n = len(validators) if isinstance(validators, list) else 0
        return max((n - 1) // 3, 0)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        raise GenesisAssertionError(
            "genesis_authority_f_invalid",
            "f must be a non-negative integer",
        )
    return raw


def _canonical_non_negative_decimal_str(raw: Any) -> str:
    if isinstance(raw, bool) or raw is None:
        raise GenesisAssertionError(
            "genesis_authority_stake_micro_ecu_invalid",
            "stake_micro_ecu must be a non-negative decimal string",
        )
    if isinstance(raw, Decimal):
        value = raw
    elif isinstance(raw, int):
        value = Decimal(raw)
    elif isinstance(raw, str):
        value = Decimal(raw)
    else:
        raise GenesisAssertionError(
            "genesis_authority_stake_micro_ecu_invalid",
            "stake_micro_ecu must be a non-negative decimal string",
        )
    if not value.is_finite() or value < 0:
        raise GenesisAssertionError(
            "genesis_authority_stake_micro_ecu_invalid",
            "stake_micro_ecu must be finite and non-negative",
        )
    return format(value, "f")


def _required_str(source: Mapping[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or value == "":
        raise GenesisAssertionError(
            f"genesis_authority_{key}_missing",
            f"{key} must be a non-empty string",
        )
    return value


def _optional_str(source: Mapping[str, Any], key: str) -> str | None:
    value = source.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise GenesisAssertionError(
            f"genesis_authority_{key}_invalid",
            f"{key} must be a string when present",
        )
    return value


def _required_bool(source: Mapping[str, Any], key: str) -> bool:
    value = source.get(key)
    if not isinstance(value, bool):
        raise GenesisAssertionError(
            f"genesis_authority_{key}_must_be_bool",
            f"{key} must be a bool",
        )
    return value


def _optional_positive_int(source: Mapping[str, Any], key: str) -> int | None:
    value = source.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise GenesisAssertionError(
            f"genesis_authority_{key}_invalid",
            f"{key} must be a positive integer",
        )
    return value


def _required_one_of(source: Mapping[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value:
            return value
    raise GenesisAssertionError(
        "genesis_authority_required_key_missing",
        f"one of {keys!r} must be a non-empty string",
    )


__all__ = [
    "GENESIS_AUTHORITY_ASSERTION_BUILDER_VERSION",
    "build_genesis_authority_assertions",
    "verify_genesis_authority_assertions",
]
