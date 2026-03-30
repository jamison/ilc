from __future__ import annotations

from collections import defaultdict
import random

AESTHETIC_PANEL_RUNTIME_VERSION = 'aesthetic_panel_runtime_532.v0.1'
CDL_059_DEPENDENCY = 'cdl_059_ratified_531.v0.1'
BLOCKING_AUTHORITY_ACTIVE = False


def _validated_pool(agent_pool: list[dict]) -> list[dict]:
    validated: list[dict] = []
    for agent in agent_pool:
        if 'agent_id' not in agent or 'model_type' not in agent:
            raise ValueError('agent_pool_entries_require_agent_id_and_model_type')
        validated.append(agent)
    return validated


def compose_aesthetic_panel(agent_pool: list[dict], panel_size: int, seed: int | None = None) -> list[str]:
    if not isinstance(panel_size, int) or isinstance(panel_size, bool) or panel_size <= 0:
        raise ValueError('panel_size_must_be_positive_int')
    validated = _validated_pool(agent_pool)
    if len(validated) < panel_size:
        raise ValueError('insufficient_agent_pool_size')

    rng = random.Random(seed)
    buckets: dict[str, list[str]] = defaultdict(list)
    for agent in validated:
        buckets[str(agent['model_type'])].append(str(agent['agent_id']))
    for ids in buckets.values():
        rng.shuffle(ids)

    ordered_types = sorted(buckets.keys(), key=lambda model_type: (len(buckets[model_type]), model_type))
    selected: list[str] = []
    while len(selected) < panel_size:
        progressed = False
        for model_type in ordered_types:
            if not buckets[model_type]:
                continue
            selected.append(buckets[model_type].pop())
            progressed = True
            if len(selected) == panel_size:
                break
        if not progressed:
            break
    if len(selected) != panel_size:
        raise ValueError('insufficient_agent_pool_size')
    return selected


def compute_aesthetic_score(votes: list[float]) -> float:
    if not votes:
        raise ValueError('votes_must_be_non_empty')
    normalized: list[float] = []
    for vote in votes:
        if isinstance(vote, bool) or not isinstance(vote, (int, float)):
            raise ValueError('vote_out_of_range')
        value = float(vote)
        if value < 0.0 or value > 1.0:
            raise ValueError('vote_out_of_range')
        normalized.append(value)
    mean = sum(normalized) / len(normalized)
    return max(0.0, min(1.0, mean))


def format_transparency_label(score: float) -> dict:
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError('score_out_of_range')
    value = float(score)
    if value < 0.0 or value > 1.0:
        raise ValueError('score_out_of_range')
    return {
        'panel_type': 'digital_agent_aesthetic_consensus',
        'not_objective_truth': True,
        'score': value,
    }


def is_blocking_authority_active() -> bool:
    return False
