from __future__ import annotations

import math

from ilc_core.economics import passive_ecu_attribution_runtime as passive_runtime
from ilc_core.network.d2d import centrality_delta_gossip_runtime as gossip_runtime


def _valid_message() -> dict[str, object]:
    return {
        'cid': 'bafycentralitydelta',
        'score_delta': 0.20,
        'epoch': 1,
        'signature': 'sig-alpha',
        'hop_count': 1,
        'fanout': 3,
        'channel': 'cid:9f7a8c42bb11ddee99aa22cc33ff44aa',
    }


def test_passive_runtime_rejects_non_finite_quality_scores() -> None:
    for invalid in (math.inf, -math.inf, math.nan):
        try:
            passive_runtime.quality_factor(invalid)
        except ValueError as exc:
            assert str(exc) == 'q_i_must_be_float_in_unit_interval'
        else:
            raise AssertionError('expected ValueError for non-finite q_i')


def test_passive_runtime_rejects_non_finite_base_reward() -> None:
    for invalid in (math.inf, -math.inf, math.nan):
        try:
            passive_runtime.compute_passive_ecu(invalid, 0.5, 0.5)
        except ValueError as exc:
            assert str(exc) == 'base_reward_must_be_non_negative_float'
        else:
            raise AssertionError('expected ValueError for non-finite base_reward')


def test_passive_runtime_rejects_non_finite_or_out_of_range_centrality_scores() -> None:
    for invalid in (math.inf, -math.inf, math.nan, 1.01):
        try:
            passive_runtime.compute_passive_ecu(1.0, invalid, 0.5)
        except ValueError as exc:
            assert str(exc) == 'centrality_score_must_be_non_negative_float'
        else:
            raise AssertionError('expected ValueError for invalid centrality_score')


def test_gossip_runtime_rejects_fanout_zero_with_bounded_fanout_token() -> None:
    message = _valid_message()
    message['fanout'] = 0
    try:
        gossip_runtime.validate_centrality_delta_message(message)
    except ValueError as exc:
        assert str(exc) == 'cdl_060_fanout_violation: exceeds_bounded_fanout'
    else:
        raise AssertionError('expected fanout=0 to be rejected')


def test_gossip_accumulator_caps_centrality_before_passive_ecu_runtime() -> None:
    state: dict[str, object] = {}
    gossip_runtime.accumulate_centrality_delta('node-cap', 0.75, 1, state)
    gossip_runtime.accumulate_centrality_delta('node-cap', 0.75, 1, state)
    if gossip_runtime.ACCUMULATION_MODEL == 'write_through':
        committed_score = state['node-cap']
    else:
        gossip_runtime.commit_epoch_buffer(1, state)
        committed_score = state['node-cap']
    assert committed_score == gossip_runtime.CENTRALITY_SCORE_CAP
    assert passive_runtime.compute_passive_ecu(1.0, committed_score, 0.5) == 0.15
