"""Regression tests for attribution settlement hardening."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import AttributionEvent
from ilc_core.types import EdgeType, EpochAttributionBatch


def _coauthorship_batch() -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(AttributionEvent(EdgeType.CO_AUTHORSHIP, "", "star_1", 1))
    batch.seal()
    return batch


def test_coauthorship_rejects_negative_member_stake() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="non_negative_finite_decimal"):
        batch.settle({"star_1": {"honest": Decimal("2"), "negative": Decimal("-1")}})


def test_coauthorship_rejects_non_finite_member_stake() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="non_negative_finite_decimal"):
        batch.settle({"star_1": {"nan": Decimal("NaN")}})


def test_coauthorship_rejects_non_decimal_member_stake() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="stake_must_be_decimal"):
        batch.settle({"star_1": {"integer": 1}})  # type: ignore[dict-item]


def test_coauthorship_rejects_non_dict_member_map() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="members_must_be_dict"):
        batch.settle({"star_1": [("agent", Decimal("1"))]})  # type: ignore[dict-item]


def test_coauthorship_rejects_non_string_member_id() -> None:
    batch = _coauthorship_batch()
    with pytest.raises(ValueError, match="member_id_must_be_string"):
        batch.settle({"star_1": {1: Decimal("1")}})  # type: ignore[dict-item]
