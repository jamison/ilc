from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pytest

from ilc_core.cli.main import _build_parser, _run_identity_subcommand
from ilc_core.identity.agent_id_runtime import derive_agent_id_v2
from ilc_core.identity.genesis_record_schema import compute_identity_seed_commitment
from ilc_core.validator import (
    VALIDATOR_KEY_DERIVATION_DOMAIN,
    VALIDATOR_KEY_DERIVATION_VERSION,
    VALIDATOR_ROLE_RECORD_VERSION,
    ValidatorRoleRecord,
    build_validator_key_derivation_record,
    build_validator_role_record,
    derive_validator_key_ikm,
    derive_validator_key_ikm_hex,
    validate_validator_role_record_id_uniqueness,
)


IDENTITY_SEED = bytes(range(32))
IDENTITY_SEED_HEX = IDENTITY_SEED.hex()
AGENT_ID = derive_agent_id_v2(IDENTITY_SEED)
NETWORK_ID = "public-rc"
VALIDATOR_KEY = (
    "8fc76b0b897092833d575794290242b4dfd41a39eb59a081"
    "89c4dbd805612749a35b47b7a2dd7d31c9bfd353ebdfb833"
)
VALIDATOR_ENDPOINT = "validator.example:9101"


def _identity_args(**overrides: object) -> argparse.Namespace:
    payload: dict[str, object] = {
        "identity_subcommand": "init",
        "lineage_id": "lineage-local",
        "key_ref": "key-local-0",
        "invite": "",
        "enable_invites": False,
        "identity_seed_hex": "",
        "no_validator": False,
        "validator_id": 1,
        "validator_key": "",
        "validator_endpoint": "",
        "validator_network_id": NETWORK_ID,
        "validator_effective_from_epoch": 1,
        "redeemer_pubkey_cid": "",
        "redemption_epoch": 0,
    }
    payload.update(overrides)
    return argparse.Namespace(**payload)


def test_validator_key_ikm_is_deterministic_and_32_bytes() -> None:
    first = derive_validator_key_ikm(IDENTITY_SEED)
    second = derive_validator_key_ikm(IDENTITY_SEED)

    assert first == second
    assert len(first) == 32


def test_validator_key_ikm_uses_domain_separation() -> None:
    expected = hashlib.sha384(VALIDATOR_KEY_DERIVATION_DOMAIN + IDENTITY_SEED).digest()[:32]

    assert derive_validator_key_ikm(IDENTITY_SEED) == expected
    assert derive_validator_key_ikm_hex(IDENTITY_SEED) == expected.hex()
    assert VALIDATOR_KEY_DERIVATION_DOMAIN == b"ilc-validator-key-v1:"


@pytest.mark.parametrize("bad_seed", [b"", b"short", "not-bytes", bytearray(32)])
def test_validator_key_ikm_rejects_invalid_seed_type_or_length(bad_seed: object) -> None:
    with pytest.raises(ValueError, match="validator_key_identity_seed_must"):
        derive_validator_key_ikm(bad_seed)  # type: ignore[arg-type]


def test_validator_key_ikm_rejects_all_zero_identity_seed() -> None:
    with pytest.raises(ValueError, match="validator_key_identity_seed_must_not_be_all_zero"):
        derive_validator_key_ikm(bytes(32))


def test_validator_key_derivation_record_contains_only_non_secret_commitment() -> None:
    record = build_validator_key_derivation_record(IDENTITY_SEED)

    assert record == {
        "identity_lineage_ref_version": "adr0038_identity_seed_commitment.v0.1",
        "identity_seed_commitment": compute_identity_seed_commitment(IDENTITY_SEED),
        "validator_key_derivation_domain": "ilc-validator-key-v1:",
        "validator_key_derivation_version": VALIDATOR_KEY_DERIVATION_VERSION,
    }
    assert IDENTITY_SEED_HEX not in str(record)


def test_validator_role_record_defaults_participation_enabled_true() -> None:
    record = build_validator_role_record(
        agent_id=AGENT_ID,
        validator_id=1,
        validator_key=VALIDATOR_KEY,
        validator_endpoint=VALIDATOR_ENDPOINT,
        effective_from_epoch=1,
        network_id=NETWORK_ID,
    )

    assert record.validator_participation_enabled is True
    assert record.identity_seed_commitment is None
    assert record.schema_version == VALIDATOR_ROLE_RECORD_VERSION


def test_validator_role_record_serializes_public_rc_fields() -> None:
    commitment = compute_identity_seed_commitment(IDENTITY_SEED)
    record = build_validator_role_record(
        agent_id=AGENT_ID,
        validator_id=1,
        validator_key=VALIDATOR_KEY,
        validator_endpoint=VALIDATOR_ENDPOINT,
        effective_from_epoch=1,
        network_id=NETWORK_ID,
        identity_seed_commitment=commitment,
    )

    canonical = record.to_canonical_record()
    assert canonical["validator_participation_enabled"] is True
    assert canonical["identity_seed_commitment"] == commitment
    assert canonical["role_status"] == "candidate"
    assert canonical["quorum_weight"] == 0


@pytest.mark.parametrize("bad_value", [None, "not-bool", 1, 0])
def test_validator_role_record_rejects_non_bool_participation_flag(
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match="validator_participation_enabled_must_be_bool"):
        build_validator_role_record(
            agent_id=AGENT_ID,
            validator_id=1,
            validator_key=VALIDATOR_KEY,
            validator_endpoint=VALIDATOR_ENDPOINT,
            effective_from_epoch=1,
            network_id=NETWORK_ID,
            validator_participation_enabled=bad_value,  # type: ignore[arg-type]
        )


def test_validator_role_record_rejects_bad_identity_seed_commitment() -> None:
    with pytest.raises(ValueError, match="identity_seed_commitment_must_be_sha384_hex"):
        build_validator_role_record(
            agent_id=AGENT_ID,
            validator_id=1,
            validator_key=VALIDATOR_KEY,
            validator_endpoint=VALIDATOR_ENDPOINT,
            effective_from_epoch=1,
            network_id=NETWORK_ID,
            identity_seed_commitment="bad",
        )


def test_validator_role_record_rejects_oversized_endpoint() -> None:
    with pytest.raises(ValueError, match="validator_endpoint_exceeds_bound"):
        build_validator_role_record(
            agent_id=AGENT_ID,
            validator_id=1,
            validator_key=VALIDATOR_KEY,
            validator_endpoint="a" * 513,
            effective_from_epoch=1,
            network_id=NETWORK_ID,
        )


def test_cli_help_exposes_no_validator_flag(capsys: pytest.CaptureFixture[str]) -> None:
    identity_parser = _build_parser()
    with pytest.raises(SystemExit):
        identity_parser.parse_args(["identity", "init", "--help"])
    help_text = capsys.readouterr().out

    assert "--no-validator" in help_text
    assert "--validator-key" in help_text


def test_identity_init_no_validator_records_opt_out(tmp_path: Path) -> None:
    result = _run_identity_subcommand(
        _identity_args(no_validator=True, identity_seed_hex="not-hex"),
        tmp_path / "graph.json",
    )

    state = result["state"]
    assert state["validator_participation_enabled"] is False
    assert state["validator_role_record_status"] == "opted_out"
    assert "validator_role_record" not in state


def test_identity_init_default_on_without_material_records_pending(tmp_path: Path) -> None:
    result = _run_identity_subcommand(_identity_args(identity_seed_hex="not-hex"), tmp_path / "graph.json")

    state = result["state"]
    assert state["validator_participation_enabled"] is True
    assert state["validator_role_record_status"] == "candidate_pending_validator_key_material"
    assert "validator_role_record" not in state


def test_identity_init_materializes_candidate_role_record(tmp_path: Path) -> None:
    result = _run_identity_subcommand(
        _identity_args(
            identity_seed_hex=IDENTITY_SEED_HEX,
            validator_id=7,
            validator_key=VALIDATOR_KEY,
            validator_endpoint=VALIDATOR_ENDPOINT,
        ),
        tmp_path / "graph.json",
    )

    state = result["state"]
    role = state["validator_role_record"]
    assert state["agent_id"] == AGENT_ID
    assert state["validator_role_record_status"] == "candidate_materialized"
    assert role["agent_id"] == AGENT_ID
    assert role["validator_id"] == 7
    assert role["role_status"] == "candidate"
    assert role["quorum_weight"] == 0
    assert role["validator_participation_enabled"] is True
    assert role["identity_seed_commitment"] == compute_identity_seed_commitment(IDENTITY_SEED)


def test_identity_init_rejects_partial_validator_material(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="validator_candidate_material_incomplete"):
        _run_identity_subcommand(
            _identity_args(
                identity_seed_hex=IDENTITY_SEED_HEX,
                validator_key=VALIDATOR_KEY,
            ),
            tmp_path / "graph.json",
        )


def test_identity_init_requires_seed_for_materialized_candidate(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="identity_seed_hex_required_for_validator_candidate"):
        _run_identity_subcommand(
            _identity_args(
                validator_key=VALIDATOR_KEY,
                validator_endpoint=VALIDATOR_ENDPOINT,
            ),
            tmp_path / "graph.json",
        )


def test_identity_init_rejects_uppercase_seed_for_materialized_candidate(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="identity_seed_hex_must_be_64_lower_hex_chars"):
        _run_identity_subcommand(
            _identity_args(
                identity_seed_hex=IDENTITY_SEED_HEX.upper(),
                validator_key=VALIDATOR_KEY,
                validator_endpoint=VALIDATOR_ENDPOINT,
            ),
            tmp_path / "graph.json",
        )


def test_identity_init_rejects_non_int_validator_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="validator_id_must_be_int"):
        _run_identity_subcommand(
            _identity_args(
                identity_seed_hex=IDENTITY_SEED_HEX,
                validator_id="7",
                validator_key=VALIDATOR_KEY,
                validator_endpoint=VALIDATOR_ENDPOINT,
            ),
            tmp_path / "graph.json",
        )


def test_validator_id_uniqueness_accepts_unique_role_records() -> None:
    first = build_validator_role_record(
        agent_id=AGENT_ID,
        validator_id=1,
        validator_key=VALIDATOR_KEY,
        validator_endpoint=VALIDATOR_ENDPOINT,
        effective_from_epoch=1,
        network_id=NETWORK_ID,
    )
    second = build_validator_role_record(
        agent_id="a" * 95 + "b",
        validator_id=2,
        validator_key="d" * 96,
        validator_endpoint="validator2.example:9101",
        effective_from_epoch=1,
        network_id=NETWORK_ID,
    )

    assert validate_validator_role_record_id_uniqueness([second, first]) == (first, second)


def test_validator_id_uniqueness_rejects_duplicate_u32() -> None:
    first = build_validator_role_record(
        agent_id=AGENT_ID,
        validator_id=1,
        validator_key=VALIDATOR_KEY,
        validator_endpoint=VALIDATOR_ENDPOINT,
        effective_from_epoch=1,
        network_id=NETWORK_ID,
    )
    second = build_validator_role_record(
        agent_id="a" * 95 + "b",
        validator_id=1,
        validator_key="d" * 96,
        validator_endpoint="validator2.example:9101",
        effective_from_epoch=1,
        network_id=NETWORK_ID,
    )

    with pytest.raises(ValueError, match="validator_id_u32_must_be_unique_pending_00b"):
        validate_validator_role_record_id_uniqueness([first, second])


def test_validator_id_uniqueness_rejects_non_records() -> None:
    with pytest.raises(ValueError, match="validator_role_record_required"):
        validate_validator_role_record_id_uniqueness([{}])  # type: ignore[list-item]


def test_validator_registration_class_not_introduced() -> None:
    assert not hasattr(__import__("ilc_core.validator", fromlist=["ValidatorRegistration"]), "ValidatorRegistration")
    assert ValidatorRoleRecord.__name__ == "ValidatorRoleRecord"
