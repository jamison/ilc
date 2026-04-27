"""Phase 858 tests — HB-001 genesis assertion schema runtime.

Tests cover CDL-073 Evidence items 3, 5, and 6 (partial):
  Evidence 3 — runtime implementation: encode/verify functions present and correct
  Evidence 5 — primitive_type extension: SYSTEM_PRIMITIVE_TYPES contains the value
  Evidence 6 — test coverage (this file)

Dependency tokens carried:
  cdl_073_homoiconic_bootstrap_schema_ratified.v0.1
  hb_001_genesis_authority_assertion_schema
"""
from __future__ import annotations

import json

import pytest

from ilc_core.genesis.assertion_schema import (
    ASSERTION_PROTOCOL_VERSION,
    CDL_073_DEPENDENCY,
    GENESIS_ASSERTION_SCHEMA_VERSION,
    GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE,
    GENESIS_EPOCH,
    GenesisAssertionContent,
    GenesisAssertionError,
    GenesisAuthorityKey,
    GenesisValidatorEntry,
    encode_genesis_assertion_payload,
    verify_genesis_assertion_schema,
)
from ilc_core.node.node_schema_core_runtime_360 import (
    ALLOWED_PRIMITIVE_TYPES,
    SYSTEM_PRIMITIVE_TYPES,
    CDL_073_DEPENDENCY as NODE_CDL_073_DEPENDENCY,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

_FAKE_MLDSA_PK_HEX = "a" * 3328
_FAKE_KEY_ID = "b" * 16
_FAKE_AGENT_ID = "c" * 96
_FAKE_VALIDATOR_KEY = "d" * 96


def _make_authority_key(**overrides) -> GenesisAuthorityKey:
    return GenesisAuthorityKey(
        algorithm=overrides.get("algorithm", "ML-DSA-65"),
        public_key_hex=overrides.get("public_key_hex", _FAKE_MLDSA_PK_HEX),
        key_id=overrides.get("key_id", _FAKE_KEY_ID),
    )


def _make_validator(validator_id: int = 1, **overrides) -> GenesisValidatorEntry:
    return GenesisValidatorEntry(
        validator_id=overrides.get("validator_id", validator_id),
        agent_id=overrides.get("agent_id", _FAKE_AGENT_ID),
        validator_key=overrides.get("validator_key", _FAKE_VALIDATOR_KEY),
        stake_micro_ecu=overrides.get("stake_micro_ecu", "1000000"),
        role=overrides.get("role", "genesis_validator"),
    )


def _make_content(**overrides) -> GenesisAssertionContent:
    validators = overrides.pop("validators", (_make_validator(1),))
    return GenesisAssertionContent(
        kind=overrides.get("kind", GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE),
        schema_version=overrides.get("schema_version", ASSERTION_PROTOCOL_VERSION),
        network_id=overrides.get("network_id", "ilc-mysticeti-testnet-m009"),
        is_testnet=overrides.get("is_testnet", True),
        real_ecu=overrides.get("real_ecu", False),
        genesis_epoch=overrides.get("genesis_epoch", GENESIS_EPOCH),
        genesis_authority_key=overrides.get("genesis_authority_key", _make_authority_key()),
        validators=validators,
        f=overrides.get("f", 0),
        predecessor_genesis_cid=overrides.get("predecessor_genesis_cid", None),
    )


# ---------------------------------------------------------------------------
# Dependency tokens
# ---------------------------------------------------------------------------

def test_cdl_073_dependency_token_present():
    assert CDL_073_DEPENDENCY == "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"


def test_genesis_assertion_schema_version_token_present():
    assert "858" in GENESIS_ASSERTION_SCHEMA_VERSION


def test_node_schema_cdl_073_dependency_token_present():
    assert NODE_CDL_073_DEPENDENCY == "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"


# ---------------------------------------------------------------------------
# Evidence 5 — primitive_type extension
# ---------------------------------------------------------------------------

def test_genesis_primitive_type_in_system_primitive_types():
    """CDL-073 Evidence 5: genesis_authority_assertion is in SYSTEM_PRIMITIVE_TYPES."""
    assert "genesis_authority_assertion" in SYSTEM_PRIMITIVE_TYPES


def test_epoch_record_in_system_primitive_types():
    """epoch_record is also a system primitive."""
    assert "epoch_record" in SYSTEM_PRIMITIVE_TYPES


def test_system_primitive_types_disjoint_from_allowed_primitive_types():
    """SYSTEM_PRIMITIVE_TYPES and ALLOWED_PRIMITIVE_TYPES must not overlap."""
    overlap = SYSTEM_PRIMITIVE_TYPES & set(ALLOWED_PRIMITIVE_TYPES)
    assert not overlap, f"Unexpected overlap: {overlap}"


# ---------------------------------------------------------------------------
# Evidence 3 — encode_genesis_assertion_payload
# ---------------------------------------------------------------------------

def test_encode_genesis_assertion_payload_returns_bytes():
    content = _make_content()
    result = encode_genesis_assertion_payload(content)
    assert isinstance(result, bytes)


def test_encode_genesis_assertion_payload_is_valid_json():
    content = _make_content()
    result = encode_genesis_assertion_payload(content)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_encode_genesis_assertion_payload_structure():
    content = _make_content()
    result = json.loads(encode_genesis_assertion_payload(content))
    assert result["v"] == ASSERTION_PROTOCOL_VERSION
    assert result["primitive"] == "assert.truth"
    assert result["epoch"] == GENESIS_EPOCH
    assert "payload" in result
    assert result["payload"]["primitive_type"] == GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE
    assert result["payload"]["epistemic_type"] == "objective"
    assert result["payload"]["refutation_criterion"] is None
    assert result["payload"]["parent_node_ids"] == []
    # shard_id must NOT be present (system-scope)
    assert "shard_id" not in result


def test_encode_genesis_assertion_payload_content_fields():
    content = _make_content(network_id="ilc-genesis-v1", is_testnet=False, real_ecu=True)
    result = json.loads(encode_genesis_assertion_payload(content))
    c = result["payload"]["content"]
    assert c["kind"] == GENESIS_AUTHORITY_ASSERTION_PRIMITIVE_TYPE
    assert c["schema_version"] == ASSERTION_PROTOCOL_VERSION
    assert c["network_id"] == "ilc-genesis-v1"
    assert c["is_testnet"] is False
    assert c["real_ecu"] is True
    assert c["genesis_epoch"] == 0


def test_encode_genesis_assertion_payload_canonical_json_sorted_keys():
    """Canonical JSON must have sort_keys=True."""
    content = _make_content()
    result_str = encode_genesis_assertion_payload(content).decode("utf-8")
    # Decode and re-encode with sort_keys=True — must match
    parsed = json.loads(result_str)
    re_encoded = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
    assert result_str == re_encoded


def test_encode_genesis_assertion_payload_rejects_invalid_content():
    """encode validates content before producing bytes."""
    bad_content = _make_content(genesis_epoch=1)  # must be 0
    with pytest.raises(GenesisAssertionError) as exc_info:
        encode_genesis_assertion_payload(bad_content)
    assert "genesis_epoch" in exc_info.value.token


# ---------------------------------------------------------------------------
# Evidence 3 — verify_genesis_assertion_schema
# ---------------------------------------------------------------------------

def _make_valid_assertion_dict(network_id: str = "ilc-mysticeti-testnet-m009") -> dict:
    content = _make_content(network_id=network_id)
    payload_bytes = encode_genesis_assertion_payload(content)
    outer = json.loads(payload_bytes)
    outer["agent_id"] = _FAKE_AGENT_ID
    outer["sig"] = "fakesig"
    return outer


def test_verify_genesis_assertion_schema_correct_network_id():
    data = _make_valid_assertion_dict(network_id="ilc-mysticeti-testnet-m009")
    result = verify_genesis_assertion_schema(data, expected_network_id="ilc-mysticeti-testnet-m009")
    assert isinstance(result, GenesisAssertionContent)
    assert result.network_id == "ilc-mysticeti-testnet-m009"


def test_verify_genesis_assertion_schema_wrong_network_id_rejected():
    data = _make_valid_assertion_dict(network_id="ilc-mysticeti-testnet-m009")
    with pytest.raises(GenesisAssertionError) as exc_info:
        verify_genesis_assertion_schema(data, expected_network_id="ilc-genesis-v1")
    assert "network_id_mismatch" in exc_info.value.token


def test_verify_genesis_assertion_schema_wrong_primitive_rejected():
    data = _make_valid_assertion_dict()
    data["primitive"] = "validate.claim"
    with pytest.raises(GenesisAssertionError) as exc_info:
        verify_genesis_assertion_schema(data, expected_network_id="ilc-mysticeti-testnet-m009")
    assert "primitive_mismatch" in exc_info.value.token


def test_verify_genesis_assertion_schema_wrong_epoch_rejected():
    data = _make_valid_assertion_dict()
    data["epoch"] = 1
    with pytest.raises(GenesisAssertionError) as exc_info:
        verify_genesis_assertion_schema(data, expected_network_id="ilc-mysticeti-testnet-m009")
    assert "epoch" in exc_info.value.token


def test_verify_genesis_assertion_schema_non_dict_rejected():
    with pytest.raises(GenesisAssertionError) as exc_info:
        verify_genesis_assertion_schema("not a dict", expected_network_id="any")
    assert "must_be_dict" in exc_info.value.token


def test_verify_genesis_assertion_schema_returns_content_fields():
    data = _make_valid_assertion_dict()
    result = verify_genesis_assertion_schema(data, expected_network_id="ilc-mysticeti-testnet-m009")
    assert result.genesis_epoch == 0
    assert result.is_testnet is True
    assert result.f == 0
    assert len(result.validators) == 1
    assert result.validators[0].validator_id == 1


# ---------------------------------------------------------------------------
# GenesisAssertionContent validation
# ---------------------------------------------------------------------------

def test_genesis_assertion_content_schema_fields_present():
    """CDL-073 Evidence 6: all required fields are present and validated."""
    content = _make_content()
    content.validate()  # must not raise


def test_genesis_assertion_content_wrong_kind_rejected():
    content = _make_content(kind="wrong_kind")
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "kind_invalid" in exc_info.value.token


def test_genesis_assertion_content_wrong_schema_version_rejected():
    content = _make_content(schema_version=99)
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "schema_version_invalid" in exc_info.value.token


def test_genesis_assertion_content_empty_network_id_rejected():
    content = _make_content(network_id="")
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "network_id_empty" in exc_info.value.token


def test_genesis_assertion_content_nonzero_epoch_rejected():
    content = _make_content(genesis_epoch=5)
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "genesis_epoch_must_be_zero" in exc_info.value.token


def test_genesis_assertion_content_empty_validators_rejected():
    content = _make_content(validators=())
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "validators_empty" in exc_info.value.token


def test_genesis_assertion_content_f_too_large_rejected():
    # f=2 with 1 validator: quorum = 5 > n=1
    content = _make_content(f=2, validators=(_make_validator(1),))
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "f_too_large" in exc_info.value.token


def test_genesis_assertion_content_f_valid_with_four_validators():
    # f=1 with 4 validators: quorum = 3 ≤ 4 — valid
    validators = tuple(_make_validator(i) for i in range(1, 5))
    content = _make_content(f=1, validators=validators)
    content.validate()  # must not raise


def test_genesis_assertion_content_duplicate_validator_ids_rejected():
    validators = (
        _make_validator(1),
        GenesisValidatorEntry(
            validator_id=1,  # duplicate
            agent_id="e" * 96,
            validator_key="f" * 96,
            stake_micro_ecu="500000",
            role="genesis_validator",
        ),
    )
    content = _make_content(f=0, validators=validators)
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "duplicate_validator_ids" in exc_info.value.token


def test_genesis_assertion_content_non_sequential_validator_ids_rejected():
    validators = (
        _make_validator(1),
        GenesisValidatorEntry(
            validator_id=3,  # skips 2
            agent_id="e" * 96,
            validator_key="f" * 96,
            stake_micro_ecu="500000",
            role="genesis_validator",
        ),
    )
    content = _make_content(f=0, validators=validators)
    with pytest.raises(GenesisAssertionError) as exc_info:
        content.validate()
    assert "not_sequential" in exc_info.value.token


# ---------------------------------------------------------------------------
# GenesisAuthorityKey validation
# ---------------------------------------------------------------------------

def test_genesis_authority_key_wrong_algorithm_rejected():
    key = _make_authority_key(algorithm="Ed25519")
    with pytest.raises(GenesisAssertionError) as exc_info:
        key.validate()
    assert "algorithm_invalid" in exc_info.value.token


def test_genesis_authority_key_short_hex_rejected():
    key = _make_authority_key(public_key_hex="a" * 100)  # too short
    with pytest.raises(GenesisAssertionError) as exc_info:
        key.validate()
    assert "hex_length_invalid" in exc_info.value.token


def test_genesis_authority_key_wrong_key_id_length_rejected():
    key = _make_authority_key(key_id="b" * 8)  # too short
    with pytest.raises(GenesisAssertionError) as exc_info:
        key.validate()
    assert "key_id_length_invalid" in exc_info.value.token


# ---------------------------------------------------------------------------
# GenesisValidatorEntry validation
# ---------------------------------------------------------------------------

def test_genesis_validator_entry_invalid_role_rejected():
    v = GenesisValidatorEntry(
        validator_id=1,
        agent_id=_FAKE_AGENT_ID,
        validator_key=_FAKE_VALIDATOR_KEY,
        stake_micro_ecu="1000000",
        role="operator",  # invalid
    )
    with pytest.raises(GenesisAssertionError) as exc_info:
        v.validate()
    assert "role_invalid" in exc_info.value.token


def test_genesis_validator_entry_negative_stake_rejected():
    v = GenesisValidatorEntry(
        validator_id=1,
        agent_id=_FAKE_AGENT_ID,
        validator_key=_FAKE_VALIDATOR_KEY,
        stake_micro_ecu="-1",  # negative
        role="genesis_validator",
    )
    with pytest.raises(GenesisAssertionError) as exc_info:
        v.validate()
    assert "stake_micro_ecu" in exc_info.value.token


def test_genesis_validator_entry_short_agent_id_rejected():
    v = GenesisValidatorEntry(
        validator_id=1,
        agent_id="abc",  # too short
        validator_key=_FAKE_VALIDATOR_KEY,
        stake_micro_ecu="1000000",
        role="genesis_validator",
    )
    with pytest.raises(GenesisAssertionError) as exc_info:
        v.validate()
    assert "agent_id" in exc_info.value.token


def test_genesis_validator_entry_zero_validator_id_rejected():
    v = GenesisValidatorEntry(
        validator_id=0,  # must be >= 1
        agent_id=_FAKE_AGENT_ID,
        validator_key=_FAKE_VALIDATOR_KEY,
        stake_micro_ecu="1000000",
        role="genesis_validator",
    )
    with pytest.raises(GenesisAssertionError) as exc_info:
        v.validate()
    assert "validator_id_must_be_positive" in exc_info.value.token
