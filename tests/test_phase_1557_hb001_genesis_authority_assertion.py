from __future__ import annotations

import json

import pytest

from ilc_core.genesis.assertion_schema import (
    GENESIS_ASSERTION_SCHEMA_VERSION,
    GenesisAssertionError,
    verify_genesis_assertion_schema,
)
from ilc_core.genesis.genesis_authority_assertion import (
    GENESIS_AUTHORITY_ASSERTION_BUILDER_VERSION,
    build_genesis_authority_assertions,
    verify_genesis_authority_assertions,
)


AGENT_ID = "a" * 96
VALIDATOR_KEY_1 = "b" * 96
VALIDATOR_KEY_2 = "c" * 96
ML_DSA_PUBLIC_KEY = "d" * 3328


def fixture_config() -> dict:
    return {
        "agent_id": AGENT_ID,
        "network_id": "ilc-genesis-rehearsal",
        "is_testnet": True,
        "real_ecu": False,
        "genesis_authority_key": {
            "algorithm": "ML-DSA-65",
            "public_key_hex": ML_DSA_PUBLIC_KEY,
        },
        "validators": [
            {
                "agent_id": AGENT_ID,
                "validator_key": VALIDATOR_KEY_1,
                "stake_micro_ecu": "1000",
                "role": "genesis_validator",
            },
            {
                "agent_id": "e" * 96,
                "validator_public_key": VALIDATOR_KEY_2,
                "stake": "1000.000",
                "role": "bootstrap_validator",
            },
        ],
        "f": 0,
    }


def test_builder_imports_phase_858_schema_source():
    assert "858" in GENESIS_ASSERTION_SCHEMA_VERSION
    assert GENESIS_AUTHORITY_ASSERTION_BUILDER_VERSION.endswith("1557.v0.1")


def test_build_genesis_authority_assertions_returns_assert_truth_shape():
    assertions = build_genesis_authority_assertions(fixture_config())
    assert len(assertions) == 1
    assertion = assertions[0]
    assert assertion["primitive"] == "assert.truth"
    assert assertion["epoch"] == 0
    assert assertion["agent_id"] == AGENT_ID
    assert assertion["sig"] == ""
    assert assertion["payload"]["primitive_type"] == "genesis_authority_assertion"


def test_generated_assertion_passes_phase_858_schema_verifier():
    assertion = build_genesis_authority_assertions(fixture_config())[0]
    content = verify_genesis_assertion_schema(
        assertion,
        expected_network_id="ilc-genesis-rehearsal",
    )
    assert content.network_id == "ilc-genesis-rehearsal"
    assert len(content.validators) == 2


def test_verify_genesis_authority_assertions_checks_expected_agent_id():
    assertions = build_genesis_authority_assertions(fixture_config())
    assert verify_genesis_authority_assertions(
        assertions,
        expected_network_id="ilc-genesis-rehearsal",
        expected_agent_id=AGENT_ID,
    ) is True
    with pytest.raises(GenesisAssertionError, match="agent_id"):
        verify_genesis_authority_assertions(
            assertions,
            expected_network_id="ilc-genesis-rehearsal",
            expected_agent_id="f" * 96,
        )


def test_builder_rejects_float_inputs_before_schema_encoding():
    config = fixture_config()
    config["validators"][0]["stake_micro_ecu"] = 1.25
    with pytest.raises(ValueError, match="genesis_authority_assertion_float_not_allowed"):
        build_genesis_authority_assertions(config)


def test_builder_rejects_structural_violation_with_genesis_assertion_error():
    config = fixture_config()
    config["validators"][0]["validator_key"] = "too-short"
    with pytest.raises(GenesisAssertionError, match="validator_key"):
        build_genesis_authority_assertions(config)


def test_builder_rejects_invalid_authority_public_key_hex_with_structured_error():
    config = fixture_config()
    config["genesis_authority_key"]["public_key_hex"] = "not-hex"
    with pytest.raises(GenesisAssertionError) as exc_info:
        build_genesis_authority_assertions(config)
    assert exc_info.value.token == "genesis_authority_key_public_key_hex_invalid"


def test_builder_output_is_canonical_json_stable():
    assertion = build_genesis_authority_assertions(fixture_config())[0]
    first = json.dumps(assertion, sort_keys=True, separators=(",", ":"))
    second = json.dumps(assertion, sort_keys=True, separators=(",", ":"))
    assert first == second
