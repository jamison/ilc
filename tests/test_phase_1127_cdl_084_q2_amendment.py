"""Phase 1127 — CDL-084 Q2 amendment evidence tests."""

from __future__ import annotations

import pathlib
import subprocess
from decimal import Decimal

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    AttributionEvent,
    settle_attribution_batch,
)
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
)


def test_e1_provenance_decay_alpha_value_and_type():
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)


def test_e2_provenance_decay_alpha_not_float():
    assert type(PROVENANCE_DECAY_ALPHA).__name__ == "Decimal"


def test_e3_cdl_084_q2_locked_token_present():
    text = pathlib.Path(
        "docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md"
    ).read_text(encoding="utf-8")
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in text


def test_e4_cdl_084_q2_provisional_token_superseded():
    text = pathlib.Path(
        "docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md"
    ).read_text(encoding="utf-8")
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in text
    assert "q2_geometric_decay_alpha_decimal_0_5_provisional" in text
    assert "Supersedes: `q2_geometric_decay_alpha_decimal_0_5_provisional`" in text


def test_e5_historical_phase_1113_commit_shows_old_alpha():
    result = subprocess.run(
        ["git", "show", "3d943f32:ilc_core/types.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert 'Decimal("0.5")' in result.stdout, (
        "Phase 1113 ratification commit must still show "
        "PROVENANCE_DECAY_ALPHA = Decimal('0.5') in git history"
    )


def test_e6_runtime_version_v0_4():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"


def test_e7_three_hop_provenance_payout_alpha_0_45():
    event = AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id="c0",
        star_node_id=None,
        epoch=1,
        provenance_chain=(
            ("n1", "c1"),
            ("n2", "c2"),
            ("n3", "c3"),
        ),
    )
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(event)
    batch.seal()
    payouts = settle_attribution_batch(batch, stake_map={})

    assert len(payouts) == 3
    assert payouts[0] == ("c1", Decimal("0.09"))
    assert payouts[1] == ("c2", Decimal("0.0405"))
    assert payouts[2] == ("c3", Decimal("0.018225"))
    for _, amount in payouts:
        assert isinstance(amount, Decimal)


def test_e8_prelock_hardening_token_present():
    text = pathlib.Path(
        "docs/specs/ilc_cdl_084_q2_amendment_prelock_1125_v0.1.md"
    ).read_text(encoding="utf-8")
    assert "cdl_084_q2_prelock_hardened_phase_1125" in text
