"""Phase 1129 Fix1 — PROVENANCE input validation and payload bounds."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    MAX_PROVENANCE_CHAIN_INPUT_LENGTH,
    AttributionEvent,
    settle_attribution_batch,
)
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    REUSE_ATTRIBUTION_RATE,
)


def _agent_id(index: int) -> str:
    return f"{index:096x}"


def _node_id(index: int) -> str:
    return node_id_from_obj({"phase": 1129, "node": index})


TARGET_CREATOR = _agent_id(90)
CREATOR_A = _agent_id(1)
CREATOR_B = _agent_id(2)
CREATOR_C = _agent_id(3)
CREATOR_D = _agent_id(4)
NODE_1 = _node_id(1)
NODE_2 = _node_id(2)
NODE_3 = _node_id(3)
NODE_4 = _node_id(4)


def _settle_chain(chain: object) -> list[tuple[str, Decimal]]:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.PROVENANCE,
            target_creator_id=TARGET_CREATOR,
            star_node_id=None,
            epoch=1,
            provenance_chain=chain,  # type: ignore[arg-type]
        )
    )
    batch.seal()
    return settle_attribution_batch(batch, stake_map={})


def test_fix1_runtime_version_records_input_hardening():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_GAP_CDL060.v0.8"


def test_fix1_non_tuple_chain_raises_stable_error():
    with pytest.raises(ValueError, match="provenance_chain_must_be_tuple"):
        _settle_chain([(NODE_1, CREATOR_A)])


def test_fix1_malformed_short_pair_raises_stable_error():
    with pytest.raises(ValueError, match="provenance_chain_entry_must_be_node_creator_pair"):
        _settle_chain(((NODE_1,),))


def test_fix1_malformed_long_pair_raises_stable_error():
    with pytest.raises(ValueError, match="provenance_chain_entry_must_be_node_creator_pair"):
        _settle_chain(((NODE_1, CREATOR_A, "extra"),))


def test_fix1_node_id_must_be_non_empty_string():
    with pytest.raises(ValueError, match="provenance_chain_node_id_must_be_cidv1_nodeid"):
        _settle_chain((([NODE_1], CREATOR_A),))
    with pytest.raises(ValueError, match="provenance_chain_node_id_must_be_cidv1_nodeid"):
        _settle_chain((("", CREATOR_A),))


def test_fix1_creator_id_must_be_non_empty_string():
    with pytest.raises(ValueError, match="provenance_chain_creator_id_must_be_agent_id"):
        _settle_chain(((NODE_1, None),))
    with pytest.raises(ValueError, match="provenance_chain_creator_id_must_be_agent_id"):
        _settle_chain(((NODE_1, ""),))


def test_fix1_chain_input_length_is_bounded_before_payout():
    oversized = tuple(
        (_node_id(index), _agent_id(index))
        for index in range(MAX_PROVENANCE_CHAIN_INPUT_LENGTH + 1)
    )
    with pytest.raises(ValueError, match="provenance_chain_exceeds_input_bound"):
        _settle_chain(oversized)


def test_fix1_valid_over_depth_chain_still_truncates_to_three_hops():
    payouts = _settle_chain((
        (NODE_1, CREATOR_A),
        (NODE_2, CREATOR_B),
        (NODE_3, CREATOR_C),
        (NODE_4, CREATOR_D),
    ))
    assert payouts == [
        (CREATOR_A, REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
        (CREATOR_B, REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
        (CREATOR_C, REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 3)),
    ]
