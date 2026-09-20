"""Regression tests for attribution settlement hardening."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import AttributionEvent
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.types import EdgeType, EpochAttributionBatch


STAR_NODE_ID = node_id_from_obj({"test": "epoch_attribution_settle_runtime_hardening"})
HONEST_AGENT_ID = "1" * 96
NEGATIVE_AGENT_ID = "2" * 96
NAN_AGENT_ID = "3" * 96
INTEGER_AGENT_ID = "4" * 96


def _coauthorship_batch() -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, HONEST_AGENT_ID, STAR_NODE_ID, 1))
    batch.seal()
    return batch


def test_coauthorship_rejects_negative_member_stake() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="non_negative_finite_decimal"):
        batch.settle({STAR_NODE_ID: {HONEST_AGENT_ID: Decimal("2"), NEGATIVE_AGENT_ID: Decimal("-1")}})


def test_coauthorship_rejects_non_finite_member_stake() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="non_negative_finite_decimal"):
        batch.settle({STAR_NODE_ID: {NAN_AGENT_ID: Decimal("NaN")}})


def test_coauthorship_rejects_non_decimal_member_stake() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="stake_must_be_decimal"):
        batch.settle({STAR_NODE_ID: {INTEGER_AGENT_ID: 1}})  # type: ignore[dict-item]


def test_coauthorship_rejects_non_dict_member_map() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="members_must_be_dict"):
        batch.settle({STAR_NODE_ID: [(HONEST_AGENT_ID, Decimal("1"))]})  # type: ignore[dict-item]


def test_coauthorship_rejects_non_string_member_id() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="member_id_must_be_non_empty_string"):
        batch.settle({STAR_NODE_ID: {1: Decimal("1")}})  # type: ignore[dict-item]
