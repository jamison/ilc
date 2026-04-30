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
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    REUSE_ATTRIBUTION_RATE,
)


def _settle_chain(chain: object) -> list[tuple[str, Decimal]]:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.PROVENANCE,
            target_creator_id="target_creator",
            star_node_id=None,
            epoch=1,
            provenance_chain=chain,  # type: ignore[arg-type]
        )
    )
    batch.seal()
    return settle_attribution_batch(batch, stake_map={})


def test_fix1_runtime_version_records_input_hardening():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"


def test_fix1_non_tuple_chain_raises_stable_error():
    with pytest.raises(ValueError, match="provenance_chain_must_be_tuple"):
        _settle_chain([("node_1", "creator_A")])


def test_fix1_malformed_short_pair_raises_stable_error():
    with pytest.raises(ValueError, match="provenance_chain_entry_must_be_node_creator_pair"):
        _settle_chain((("node_1",),))


def test_fix1_malformed_long_pair_raises_stable_error():
    with pytest.raises(ValueError, match="provenance_chain_entry_must_be_node_creator_pair"):
        _settle_chain((("node_1", "creator_A", "extra"),))


def test_fix1_node_id_must_be_non_empty_string():
    with pytest.raises(ValueError, match="provenance_chain_node_id_must_be_non_empty_string"):
        _settle_chain(((["node_1"], "creator_A"),))
    with pytest.raises(ValueError, match="provenance_chain_node_id_must_be_non_empty_string"):
        _settle_chain((("", "creator_A"),))


def test_fix1_creator_id_must_be_non_empty_string():
    with pytest.raises(ValueError, match="provenance_chain_creator_id_must_be_non_empty_string"):
        _settle_chain((("node_1", None),))
    with pytest.raises(ValueError, match="provenance_chain_creator_id_must_be_non_empty_string"):
        _settle_chain((("node_1", ""),))


def test_fix1_chain_input_length_is_bounded_before_payout():
    oversized = tuple(
        (f"node_{index}", f"creator_{index}")
        for index in range(MAX_PROVENANCE_CHAIN_INPUT_LENGTH + 1)
    )
    with pytest.raises(ValueError, match="provenance_chain_exceeds_input_bound"):
        _settle_chain(oversized)


def test_fix1_valid_over_depth_chain_still_truncates_to_three_hops():
    payouts = _settle_chain((
        ("node_1", "creator_A"),
        ("node_2", "creator_B"),
        ("node_3", "creator_C"),
        ("node_4", "creator_D"),
    ))
    assert payouts == [
        ("creator_A", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 1)),
        ("creator_B", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 2)),
        ("creator_C", REUSE_ATTRIBUTION_RATE * (PROVENANCE_DECAY_ALPHA ** 3)),
    ]
