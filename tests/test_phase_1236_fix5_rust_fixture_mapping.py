from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ilc_core.protocol.commit_epoch_emission_runtime import (
    adapt_finalized_epoch_to_connector_inputs,
    build_quorum_proof_projection,
    compute_causal_frontier_ref,
    compute_quorum_proof_ref,
)

TYPES_RS = Path("ilc_consensus/src/types.rs")
EPOCH_SETTLEMENT_RS = Path("ilc_consensus/src/epoch_settlement.rs")

GENESIS_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
STATE_ROOT_BYTES = bytes(range(36))
STATE_ROOT_HEX = STATE_ROOT_BYTES.hex()
AGG_SIG_BYTES = bytes([0xCD]) * 96
AGG_SIG_HEX = AGG_SIG_BYTES.hex()
SOURCE_RECORD_DIGEST = "sha256:" + "ef" * 32
PREDECESSOR_REF = "sha256:" + "a1" * 32


def _rust_sources() -> tuple[str, str]:
    return TYPES_RS.read_text(), EPOCH_SETTLEMENT_RS.read_text()


def _rust_shaped_fixture() -> dict[str, object]:
    return {
        "record": {
            "epoch": 12,
            "state_root_p1": STATE_ROOT_BYTES[:32],
            "state_root_p2": STATE_ROOT_BYTES[32:],
        },
        "agg_sig_bytes": AGG_SIG_BYTES,
        "signers": [2, 0, 1],
    }


def _state_root_hex_from_fixture(fixture: dict[str, object]) -> str:
    record = fixture["record"]
    assert isinstance(record, dict)
    p1 = record["state_root_p1"]
    p2 = record["state_root_p2"]
    assert isinstance(p1, bytes)
    assert isinstance(p2, bytes)
    return (p1 + p2).hex()


def _adapter_from_fixture(**overrides: object) -> dict[str, object]:
    fixture = _rust_shaped_fixture()
    state_root = _state_root_hex_from_fixture(fixture)
    quorum_ref = compute_quorum_proof_ref(
        build_quorum_proof_projection(
            epoch_sequence=12,
            state_root_cidv1_hex=state_root,
            signers=fixture["signers"],  # type: ignore[arg-type]
            agg_sig_bytes_hex=fixture["agg_sig_bytes"].hex(),  # type: ignore[union-attr]
            source_record_digest=SOURCE_RECORD_DIGEST,
        )
    )
    kwargs = {
        "epoch_index": 12,
        "epoch_id": "epoch-0012",
        "namespace_id": "ilc:test",
        "finalization_state": "committed",
        "quorum_records": [
            {
                "block_hash": "block-alpha",
                "epoch_index": 12,
                "finalization_state": "committed",
                "quorum_state_digest": "quorum-state-alpha",
                "vote_weight": 1,
            }
        ],
        "state_root_cidv1_hex": state_root,
        "agg_sig_bytes_hex": fixture["agg_sig_bytes"].hex(),  # type: ignore[union-attr]
        "signers": fixture["signers"],
        "source_record_digest": SOURCE_RECORD_DIGEST,
        "causal_predecessor_ref": PREDECESSOR_REF,
        "causal_frontier_refs": [quorum_ref],
        "genesis_domain_hash": GENESIS_HASH,
        "reward_total": Decimal("10.50"),
        "stake_total": Decimal("20"),
        "task_count": 3,
        "agent_count": 2,
    }
    kwargs.update(overrides)
    return adapt_finalized_epoch_to_connector_inputs(**kwargs)


def test_epoch_settlement_record_rust_field_names_match_projection_inputs():
    types_rs, _ = _rust_sources()

    assert "pub struct EpochSettlementRecord" in types_rs
    assert "pub epoch: EpochSeq" in types_rs
    assert "pub state_root: CIDv1Root" in types_rs


def test_cidv1root_rust_layout_maps_to_72_hex_chars():
    types_rs, epoch_settlement_rs = _rust_sources()

    assert "pub p1: [u8; 32]" in types_rs
    assert "pub p2: [u8; 4]" in types_rs
    assert "pub fn new(bytes: [u8; 36])" in types_rs
    assert "assert_eq!(size_of::<CIDv1Root>(), 36)" in epoch_settlement_rs
    assert len(STATE_ROOT_HEX) == 72


def test_validator_id_rust_layout_maps_to_non_negative_python_ints():
    types_rs, _ = _rust_sources()

    assert "pub struct ValidatorID(pub u32)" in types_rs
    projection = build_quorum_proof_projection(
        epoch_sequence=12,
        state_root_cidv1_hex=STATE_ROOT_HEX,
        signers=[0, 2**32 - 1],
        agg_sig_bytes_hex=AGG_SIG_HEX,
    )
    assert projection["signers"] == [0, 2**32 - 1]


def test_python_projection_enforces_u32_upper_bound():
    import pytest

    with pytest.raises(ValueError, match="quorum_projection_signer_must_be_non_negative_int"):
        build_quorum_proof_projection(
            epoch_sequence=12,
            state_root_cidv1_hex=STATE_ROOT_HEX,
            signers=[2**32],
            agg_sig_bytes_hex=AGG_SIG_HEX,
        )


def test_stored_checkpoint_rust_fields_match_projection_material():
    _, epoch_settlement_rs = _rust_sources()

    assert "pub struct StoredCheckpoint" in epoch_settlement_rs
    assert "pub record: EpochSettlementRecord" in epoch_settlement_rs
    assert "pub agg_sig_bytes: Vec<u8>" in epoch_settlement_rs
    assert "pub signers: Vec<ValidatorID>" in epoch_settlement_rs


def test_testnet_fault_sim_empty_agg_sig_is_not_adapter_eligible():
    _, epoch_settlement_rs = _rust_sources()

    assert "agg_sig_bytes: vec![]" in epoch_settlement_rs
    assert "testnet_fault_sim path: no BLS sig, no signers" in epoch_settlement_rs


def test_empty_agg_sig_hex_is_rejected_by_projection_layer():
    import pytest

    with pytest.raises(ValueError, match="quorum_projection_agg_sig_bytes_hex_invalid"):
        build_quorum_proof_projection(
            epoch_sequence=12,
            state_root_cidv1_hex=STATE_ROOT_HEX,
            signers=[0],
            agg_sig_bytes_hex="",
        )


def test_bls_g1_min_pk_96_byte_aggregate_signature_hex_is_accepted():
    projection = build_quorum_proof_projection(
        epoch_sequence=12,
        state_root_cidv1_hex=STATE_ROOT_HEX,
        signers=[0, 1],
        agg_sig_bytes_hex=AGG_SIG_HEX,
    )

    assert len(AGG_SIG_HEX) == 192
    assert projection["agg_sig_bytes_hex"] == AGG_SIG_HEX


def test_state_root_p1_p2_concatenation_matches_projection_value():
    fixture = _rust_shaped_fixture()

    assert _state_root_hex_from_fixture(fixture) == STATE_ROOT_HEX
    assert build_quorum_proof_projection(
        epoch_sequence=12,
        state_root_cidv1_hex=_state_root_hex_from_fixture(fixture),
        signers=[0],
        agg_sig_bytes_hex=AGG_SIG_HEX,
    )["state_root_cidv1_hex"] == STATE_ROOT_HEX


def test_full_round_trip_from_rust_shaped_fixture_to_adapter():
    result = _adapter_from_fixture()

    assert result["quorum_proof_projection"]["epoch_sequence"] == 12
    assert result["quorum_proof_projection"]["state_root_cidv1_hex"] == STATE_ROOT_HEX
    assert result["causal_frontier_projection"]["state_root_cidv1_hex"] == STATE_ROOT_HEX
    assert result["commit_epoch_event"].payload["epoch_index"] == 12


def test_rust_fixture_signers_sort_ascending_in_python_projection():
    result = _adapter_from_fixture()

    assert result["quorum_proof_projection"]["signers"] == [0, 1, 2]


def test_quorum_proof_ref_deterministic_from_rust_shaped_fixture():
    first = _adapter_from_fixture()
    second = _adapter_from_fixture()

    assert first["quorum_proof_ref"] == second["quorum_proof_ref"]


def test_causal_frontier_ref_deterministic_from_rust_shaped_fixture():
    first = _adapter_from_fixture()
    second = _adapter_from_fixture()

    assert first["causal_frontier_ref"] == second["causal_frontier_ref"]
    assert compute_causal_frontier_ref(first["causal_frontier_projection"]) == first["causal_frontier_ref"]


def test_full_chain_event_has_no_created_at_or_payload_source():
    event = _adapter_from_fixture()["commit_epoch_event"]

    assert "created_at" not in event.payload
    assert "source" not in event.payload
    assert event.payload["checksums"]["epoch_state_cid"].startswith("sha256:")
    assert event.payload["checksums"]["epoch_events_cid"].startswith("sha256:")


def test_epoch_checkpoint_sigs_are_distinct_from_stored_checkpoint_agg_sig_bytes():
    types_rs, epoch_settlement_rs = _rust_sources()

    assert "pub sigs: AggSig" in types_rs
    assert "pub agg_sig_bytes: Vec<u8>" in epoch_settlement_rs
    assert "EpochCheckpoint" in types_rs
    assert "StoredCheckpoint" in epoch_settlement_rs
