# SPDX-License-Identifier: AGPL-3.0-only
"""Structural checks for GAP-CDL017-IMPL-DELTA-00b Rust AgentID migration."""

from __future__ import annotations

from pathlib import Path
from dataclasses import fields

from ilc_core.validator.admission_ejection_runtime import (
    GENESIS_STAKE_AMOUNT,
    ValidatorRoleRecord,
    build_validator_role_record,
    validate_validator_role_record_id_uniqueness,
)


RUST_SRC = Path("ilc_consensus/src")


def _read(relative: str) -> str:
    return (RUST_SRC / relative).read_text(encoding="utf-8")


def test_validator_id_newtype_removed_from_rust_consensus_sources() -> None:
    remaining = [
        str(path)
        for path in RUST_SRC.glob("*.rs")
        if "ValidatorID" in path.read_text(encoding="utf-8")
    ]
    assert remaining == []


def test_agent_id_is_48_byte_consensus_identity() -> None:
    text = _read("types.rs")
    assert "pub struct AgentID(pub [u8; 48]);" in text
    assert "pub struct AgentID(pub u32);" not in text


def test_validator_set_checkpoint_and_certificate_are_agent_id_keyed() -> None:
    types_text = _read("types.rs")
    settlement_text = _read("epoch_settlement.rs")
    assert "pub validators: HashMap<AgentID, ValidatorKey>" in types_text
    assert "pub signers: Vec<AgentID>" in types_text
    assert "pub sigs: Vec<(AgentID, ValidatorSig)>" in types_text
    assert "let mut seen: HashSet<AgentID>" in settlement_text


def test_startup_derives_node_agent_id_from_genesis_metadata() -> None:
    text = _read("main.rs")
    assert "load_genesis_with_metadata(&genesis_path)" in text
    assert "agent_by_config_id" in text
    assert "let own_agent_id =" in text
    assert "AgentID(cfg.validator_id)" not in text


def test_peer_network_authenticates_to_agent_id_not_u32() -> None:
    text = _read("network.rs")
    assert "peer_agent_ids: Arc<HashMap<u32, AgentID>>" in text
    assert "pub fn with_peer_agent_ids" in text
    assert ") -> Result<AgentID, ILCConsensusError>" in text
    assert "if envelope.peer_id != authenticated_id" in text
    assert "missing genesis AgentID metadata" in text
    assert "AgentID::from_testnet_validator_index(*id)" not in text


def test_persistent_quic_projection_and_sessions_are_agent_id_keyed() -> None:
    text = _read("persistent_quic.rs")
    assert "direct_endpoints: HashMap<AgentID, QuicEndpointEdge>" in text
    assert "relay_endpoints: HashMap<AgentID, QuicEndpointEdge>" in text
    assert "sessions: Mutex<HashMap<AgentID, PersistentQuicSession>>" in text
    assert ".get(&validator_id.0)" not in text
    assert "sessions.insert(validator_id.0" not in text


def test_dag_audit_maps_genesis_agent_ids_to_public_keys() -> None:
    text = _read("dag_audit_main.rs")
    assert "public_keys_by_agent_id" in text
    assert 'validator.get("agent_id").and_then(Value::as_str)' in text
    assert "AgentID((idx + 1) as u32)" not in text


def test_testnet_numeric_indices_are_explicit_compatibility_mapping_only() -> None:
    types_text = _read("types.rs")
    client_text = _read("testnet_client_main.rs")
    assert "from_testnet_validator_index" in types_text
    assert "AgentID::from_testnet_validator_index(args.peer_id)" in client_text
    assert "AgentID(args.peer_id)" not in client_text


def test_validator_role_record_validator_id_is_deprecated_optional_field() -> None:
    validator_id_field = next(item for item in fields(ValidatorRoleRecord) if item.name == "validator_id")
    assert validator_id_field.default is None
    assert "Deprecated by GAP-CDL017-IMPL-DELTA-00b" in Path(
        "ilc_core/validator/admission_ejection_runtime.py"
    ).read_text(encoding="utf-8")
    assert validate_validator_role_record_id_uniqueness([]) == ()


def test_validator_role_record_builder_does_not_require_deprecated_validator_id() -> None:
    record = build_validator_role_record(
        agent_id="a" * 96,
        validator_key="b" * 96,
        validator_endpoint="validator.example.test:9443",
        effective_from_epoch=1,
        network_id="public-rc",
    )

    assert record.validator_id is None


def test_cdl055_stake_threshold_matches_rust_micro_ecu_constant() -> None:
    text = _read("validator.rs")
    expected_micro_ecu = int(GENESIS_STAKE_AMOUNT * 1_000_000)
    assert f"pub const MIN_STAKE_MICRO_ECU: u64 = {expected_micro_ecu:_};" in text
