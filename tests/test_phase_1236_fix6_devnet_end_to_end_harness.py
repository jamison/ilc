from __future__ import annotations

import re
from decimal import Decimal

import pytest

from ilc_core.protocol.commit_epoch_emission_runtime import (
    COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION,
    adapt_finalized_epoch_to_connector_inputs,
    build_commit_epoch_causal_frontier_projection,
    build_quorum_proof_projection,
    compute_causal_frontier_ref,
    compute_quorum_proof_ref,
)

GENESIS_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
SHA_REF_RE = re.compile(r"sha256:[0-9a-f]{64}")


def _state_root_for_epoch(epoch_index: int) -> str:
    return (bytes([epoch_index % 256]) * 36).hex()


def _agg_sig_for_epoch(epoch_index: int) -> str:
    return (bytes([(epoch_index + 64) % 256]) * 96).hex()


def _source_digest_for_epoch(epoch_index: int) -> str:
    return "sha256:" + (bytes([(epoch_index + 128) % 256]) * 32).hex()


def _genesis_causal_frontier_ref() -> str:
    projection = build_commit_epoch_causal_frontier_projection(
        epoch_sequence=0,
        state_root_cidv1_hex=None,
        causal_predecessor_ref=None,
        quorum_proof_ref=None,
        causal_frontier_refs=[f"genesis_root:{GENESIS_HASH}"],
        genesis_domain_hash=GENESIS_HASH,
    )
    return compute_causal_frontier_ref(projection)


def _quorum_ref_for_epoch(epoch_index: int) -> str:
    return compute_quorum_proof_ref(
        build_quorum_proof_projection(
            epoch_sequence=epoch_index,
            state_root_cidv1_hex=_state_root_for_epoch(epoch_index),
            signers=[0, 1, 2],
            agg_sig_bytes_hex=_agg_sig_for_epoch(epoch_index),
            source_record_digest=_source_digest_for_epoch(epoch_index),
        )
    )


def _adapter_epoch(epoch_index: int, predecessor_ref: str) -> dict[str, object]:
    quorum_ref = _quorum_ref_for_epoch(epoch_index)
    return adapt_finalized_epoch_to_connector_inputs(
        epoch_index=epoch_index,
        epoch_id=f"epoch-{epoch_index:04d}",
        namespace_id="ilc:devnet",
        finalization_state="committed",
        quorum_records=[
            {
                "block_hash": f"block-{epoch_index:04d}",
                "epoch_index": epoch_index,
                "finalization_state": "committed",
                "quorum_state_digest": f"quorum-state-{epoch_index:04d}",
                "vote_weight": 1,
            }
        ],
        state_root_cidv1_hex=_state_root_for_epoch(epoch_index),
        agg_sig_bytes_hex=_agg_sig_for_epoch(epoch_index),
        signers=[2, 0, 1],
        source_record_digest=_source_digest_for_epoch(epoch_index),
        causal_predecessor_ref=predecessor_ref,
        causal_frontier_refs=[quorum_ref],
        genesis_domain_hash=GENESIS_HASH,
        reward_total=Decimal("10.50"),
        stake_total=Decimal("20"),
        task_count=epoch_index,
        agent_count=3,
    )


def _build_devnet_chain(start_epoch: int, length: int) -> list[dict[str, object]]:
    if start_epoch < 1:
        raise ValueError("devnet_chain_start_epoch_must_be_post_genesis")
    if length < 1:
        raise ValueError("devnet_chain_length_must_be_positive")

    chain: list[dict[str, object]] = []
    predecessor_ref = _genesis_causal_frontier_ref()
    for epoch_index in range(start_epoch, start_epoch + length):
        result = _adapter_epoch(epoch_index, predecessor_ref)
        chain.append(result)
        predecessor_ref = result["causal_frontier_ref"]  # type: ignore[assignment]
    return chain


def test_genesis_to_epoch_1_causal_predecessor_chains():
    genesis_ref = _genesis_causal_frontier_ref()
    result = _adapter_epoch(1, genesis_ref)

    assert result["causal_frontier_projection"]["causal_predecessor_ref"] == genesis_ref
    assert SHA_REF_RE.fullmatch(genesis_ref)


def test_multi_epoch_chain_propagates_causal_frontier_refs():
    chain = _build_devnet_chain(start_epoch=1, length=3)

    for current, next_epoch in zip(chain, chain[1:]):
        assert current["causal_frontier_ref"] == next_epoch["causal_frontier_projection"]["causal_predecessor_ref"]


def test_multi_epoch_chain_refs_have_sha256_shape():
    chain = _build_devnet_chain(start_epoch=1, length=4)

    for result in chain:
        assert SHA_REF_RE.fullmatch(result["causal_frontier_ref"])
        assert SHA_REF_RE.fullmatch(result["quorum_proof_ref"])


def test_multi_epoch_chain_epoch_sequences_are_distinct_and_ascending():
    chain = _build_devnet_chain(start_epoch=1, length=4)
    sequences = [result["causal_frontier_projection"]["epoch_sequence"] for result in chain]

    assert sequences == [1, 2, 3, 4]


def test_devnet_chain_causal_frontier_refs_are_distinct():
    chain = _build_devnet_chain(start_epoch=1, length=4)
    refs = [result["causal_frontier_ref"] for result in chain]

    assert len(refs) == len(set(refs))


def test_devnet_chain_quorum_refs_are_distinct():
    chain = _build_devnet_chain(start_epoch=1, length=4)
    refs = [result["quorum_proof_ref"] for result in chain]

    assert len(refs) == len(set(refs))


def test_devnet_chain_produces_no_created_at_or_payload_source():
    for result in _build_devnet_chain(start_epoch=1, length=3):
        payload = result["commit_epoch_event"].payload
        assert "created_at" not in payload
        assert "source" not in payload


def test_devnet_chain_serializes_decimal_economics_as_strings():
    for result in _build_devnet_chain(start_epoch=1, length=3):
        summary = result["commit_epoch_event"].payload["summary"]
        assert isinstance(summary["reward_total"], str)
        assert isinstance(summary["stake_total"], str)


def test_devnet_harness_epoch_zero_bypasses_adapter():
    projection = build_commit_epoch_causal_frontier_projection(
        epoch_sequence=0,
        state_root_cidv1_hex=None,
        causal_predecessor_ref=None,
        quorum_proof_ref=None,
        causal_frontier_refs=[f"genesis_root:{GENESIS_HASH}"],
        genesis_domain_hash=GENESIS_HASH,
    )

    assert projection["epoch_sequence"] == 0
    assert projection["quorum_proof_ref"] is None
    assert projection["causal_predecessor_ref"] is None


def test_adapter_rejects_epoch_zero_in_devnet_context():
    with pytest.raises(ValueError, match="finalized_epoch_adapter_genesis_epoch_zero_unsupported"):
        _adapter_epoch(0, _genesis_causal_frontier_ref())


def test_devnet_chain_helper_rejects_bad_start_epoch():
    with pytest.raises(ValueError, match="devnet_chain_start_epoch_must_be_post_genesis"):
        _build_devnet_chain(start_epoch=0, length=1)


def test_devnet_chain_helper_rejects_empty_length():
    with pytest.raises(ValueError, match="devnet_chain_length_must_be_positive"):
        _build_devnet_chain(start_epoch=1, length=0)


def test_fix6_does_not_bump_runtime_adapter_version():
    assert COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION == "commit_epoch_finalized_adapter_1236_fix4.v0.1"


def test_devnet_chain_is_deterministic_across_two_builds():
    first = _build_devnet_chain(start_epoch=1, length=3)
    second = _build_devnet_chain(start_epoch=1, length=3)

    assert [result["causal_frontier_ref"] for result in first] == [
        result["causal_frontier_ref"] for result in second
    ]
