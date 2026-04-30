#!/usr/bin/env python3
"""SIM-PROVENANCE-01: PROVENANCE decay alpha calibration harness.

AutoResearch-pattern mutable harness. Modify the PARAMETERS block to explore
the alpha calibration space. See docs/sims/sim_provenance_01/program.md for
the research objective, hard metric, and stopping condition.

CDL-084 Q2 token: q2_geometric_decay_alpha_decimal_0_5_provisional
CDL-084 Q8 token: q8_epoch_mint_source_sim_provenance_01_required
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
import json
import random  # simulation-only PRNG; not ilc_core/; permitted by AGENTS.md §2
import statistics
from pathlib import Path
from typing import Any

from ilc_core.economics import epoch_attribution_settle_runtime as _settle_runtime
from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    settle_attribution_batch,
)
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
    REUSE_ATTRIBUTION_RATE,
)


# ---------------------------------------------------------------------------
# PARAMETERS — agent mutates this block
# ---------------------------------------------------------------------------
ALPHA = Decimal("0.5")
ALPHA_SWEEP = tuple(Decimal(i) / Decimal("100") for i in range(30, 71, 5))
CHAIN_DEPTH_WEIGHTS = [0.5, 0.3, 0.2]  # P(1-hop), P(2-hop), P(3-hop)
CREATOR_OVERLAP_RATE = Decimal("0.1")
N_EPOCHS = 200
EVENTS_PER_EPOCH = 50
N_NODES = 100
N_CREATORS = 30
RANDOM_SEED = 42
OUT_DIR = Path("out")
TIME_SERIES_PATH = OUT_DIR / "sim_provenance_01_time_series.json"
SUMMARY_PATH = OUT_DIR / "sim_provenance_01_summary.json"
# ---------------------------------------------------------------------------


def generate_chain(
    node_pool: list[str],
    creator_pool: list[str],
    depth: int,
    overlap_rate: Decimal,
    rng: random.Random,
) -> tuple[tuple[str, str], ...]:
    """Generate one nearest-first PROVENANCE chain."""
    if depth < 1 or depth > PROVENANCE_MAX_DEPTH:
        raise ValueError("sim_provenance_depth_out_of_range")

    node_ids = rng.sample(node_pool, depth)
    creators_seen: list[str] = []
    chain: list[tuple[str, str]] = []
    for hop_index, node_id in enumerate(node_ids):
        should_overlap = (
            hop_index > 0
            and creators_seen
            and Decimal(str(rng.random())) < overlap_rate
        )
        if should_overlap:
            creator_id = rng.choice(creators_seen)
        else:
            creator_id = rng.choice(creator_pool)
        creators_seen.append(creator_id)
        chain.append((node_id, creator_id))
    return tuple(chain)


def _choose_depth(rng: random.Random) -> int:
    return rng.choices((1, 2, 3), weights=CHAIN_DEPTH_WEIGHTS, k=1)[0]


def run_epoch(
    epoch_num: int,
    alpha: Decimal,
    rng: random.Random,
    *,
    node_pool: list[str] | None = None,
    creator_pool: list[str] | None = None,
) -> dict[str, Any]:
    """Run one simulated epoch through the production PROVENANCE settle path."""
    nodes = node_pool or [f"node_{i}" for i in range(N_NODES)]
    creators = creator_pool or [f"creator_{i}" for i in range(N_CREATORS)]
    batch = EpochAttributionBatch(epoch=epoch_num)
    epoch_node_counts: dict[str, int] = {node_id: 0 for node_id in nodes}

    for _ in range(EVENTS_PER_EPOCH):
        depth = _choose_depth(rng)
        chain = generate_chain(nodes, creators, depth, CREATOR_OVERLAP_RATE, rng)
        for node_id, _ in chain:
            epoch_node_counts[node_id] += 1
        batch.add_event(
            AttributionEvent(
                edge_type=EdgeType.PROVENANCE,
                target_creator_id="unused_target_creator",
                star_node_id=None,
                epoch=epoch_num,
                provenance_chain=chain,
            )
        )
    batch.seal()

    old_alpha = _settle_runtime.PROVENANCE_DECAY_ALPHA
    try:
        _settle_runtime.PROVENANCE_DECAY_ALPHA = alpha
        payouts = settle_attribution_batch(batch, stake_map={})
    finally:
        _settle_runtime.PROVENANCE_DECAY_ALPHA = old_alpha

    creator_payouts: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for creator_id, amount in payouts:
        creator_payouts[creator_id] += amount

    return {
        "epoch": epoch_num,
        "gini": _gini([amount for _, amount in payouts]),
        "total_minted": sum((amount for _, amount in payouts), Decimal("0")),
        "creator_payouts": dict(creator_payouts),
        "node_counts": epoch_node_counts,
    }


def _gini(amounts: list[Decimal]) -> float:
    """Compute Gini coefficient over Decimal payout amounts."""
    if not amounts:
        return 0.0
    sorted_amounts = sorted(float(amount) for amount in amounts)
    n = len(sorted_amounts)
    total = sum(sorted_amounts)
    if total <= 0:
        return 0.0
    cumsum = 0.0
    for index, value in enumerate(sorted_amounts):
        cumsum += (2 * (index + 1) - n - 1) * value
    return cumsum / (n * total)


def evaluate(
    epoch_results: list[dict[str, Any]],
    node_descendant_counts: dict[str, list[int]],
    *,
    alpha: Decimal,
) -> dict[str, Any]:
    mint_surface = [result["total_minted"] for result in epoch_results]
    mean_total_payout = (
        sum(mint_surface, Decimal("0")) / Decimal(len(mint_surface))
        if mint_surface else Decimal("0")
    )
    epoch_0_mint = mint_surface[0] if mint_surface else Decimal("0")
    mint_drift = (
        (max(mint_surface) - min(mint_surface)) / epoch_0_mint
        if epoch_0_mint > 0 else Decimal("0")
    )
    mean_gini = statistics.mean(result["gini"] for result in epoch_results) if epoch_results else 0.0
    max_single_creator_share = _max_creator_share_100_epoch_window(epoch_results)
    concentration_metric_pass = mean_gini < 0.6 and max_single_creator_share < 0.40
    mint_surface_stable = mint_drift <= Decimal("0.20")
    return {
        "alpha_value": str(alpha),
        "mean_gini": mean_gini,
        "max_single_creator_share": max_single_creator_share,
        "mint_surface": mint_surface,
        "mint_drift": mint_drift,
        "mint_surface_stable": mint_surface_stable,
        "mean_total_payout": mean_total_payout,
        "hard_metric_pass": concentration_metric_pass,
        "configuration_keep": concentration_metric_pass and mint_surface_stable,
        "node_descendant_time_series": node_descendant_counts,
        "alpha_sensitivity": None,
    }


def _max_creator_share_100_epoch_window(epoch_results: list[dict[str, Any]]) -> float:
    if not epoch_results:
        return 0.0
    max_share = 0.0
    window_size = min(100, len(epoch_results))
    for start in range(0, len(epoch_results) - window_size + 1):
        window = epoch_results[start:start + window_size]
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for result in window:
            for creator_id, amount in result["creator_payouts"].items():
                totals[creator_id] += amount
        window_total = sum(totals.values(), Decimal("0"))
        if window_total <= 0:
            continue
        max_share = max(max_share, max(float(amount / window_total) for amount in totals.values()))
    return max_share


def run_alpha(alpha: Decimal, *, seed: int = RANDOM_SEED) -> dict[str, Any]:
    rng = random.Random(seed)
    node_pool = [f"node_{i}" for i in range(N_NODES)]
    creator_pool = [f"creator_{i}" for i in range(N_CREATORS)]
    node_descendant_counts: dict[str, list[int]] = {node_id: [] for node_id in node_pool}
    epoch_results: list[dict[str, Any]] = []
    for epoch in range(N_EPOCHS):
        result = run_epoch(
            epoch,
            alpha,
            rng,
            node_pool=node_pool,
            creator_pool=creator_pool,
        )
        epoch_results.append(result)
        for node_id in node_pool:
            node_descendant_counts[node_id].append(result["node_counts"][node_id])
    return evaluate(epoch_results, node_descendant_counts, alpha=alpha)


def run_sweep(alpha_values: tuple[Decimal, ...] = ALPHA_SWEEP) -> dict[str, Any]:
    summaries = [run_alpha(alpha) for alpha in alpha_values]
    _apply_alpha_sensitivity(summaries)
    passing = [summary for summary in summaries if summary["configuration_keep"]]
    recommended = min(passing, key=lambda item: item["mean_gini"]) if passing else None
    if recommended is None:
        recommended = min(summaries, key=lambda item: item["mean_gini"]) if summaries else None
    return {
        "summaries": summaries,
        "recommended": recommended,
        "provisional_alpha_passes": any(
            summary["alpha_value"] == str(PROVENANCE_DECAY_ALPHA)
            and summary["hard_metric_pass"]
            for summary in summaries
        ),
        "provisional_alpha_keep": any(
            summary["alpha_value"] == str(PROVENANCE_DECAY_ALPHA)
            and summary["configuration_keep"]
            for summary in summaries
        ),
    }


def _apply_alpha_sensitivity(summaries: list[dict[str, Any]]) -> None:
    ordered = sorted(summaries, key=lambda item: Decimal(item["alpha_value"]))
    for index, summary in enumerate(ordered):
        if len(ordered) == 1:
            summary["alpha_sensitivity"] = None
            continue
        if index == 0:
            other = ordered[index + 1]
        elif index == len(ordered) - 1:
            other = ordered[index - 1]
        else:
            prev_item = ordered[index - 1]
            next_item = ordered[index + 1]
            delta_payout = next_item["mean_total_payout"] - prev_item["mean_total_payout"]
            delta_alpha = Decimal(next_item["alpha_value"]) - Decimal(prev_item["alpha_value"])
            summary["alpha_sensitivity"] = delta_payout / delta_alpha
            continue
        delta_payout = summary["mean_total_payout"] - other["mean_total_payout"]
        delta_alpha = Decimal(summary["alpha_value"]) - Decimal(other["alpha_value"])
        summary["alpha_sensitivity"] = delta_payout / delta_alpha


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def main() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sweep = run_sweep()
    recommended = sweep["recommended"]
    if recommended is None:
        raise RuntimeError("sim_provenance_01_no_results")

    TIME_SERIES_PATH.write_text(
        json.dumps(
            recommended["node_descendant_time_series"],
            allow_nan=False,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    summary_payload = {
        "parameters": {
            "alpha_sweep": [str(alpha) for alpha in ALPHA_SWEEP],
            "chain_depth_weights": CHAIN_DEPTH_WEIGHTS,
            "creator_overlap_rate": str(CREATOR_OVERLAP_RATE),
            "n_epochs": N_EPOCHS,
            "events_per_epoch": EVENTS_PER_EPOCH,
            "n_nodes": N_NODES,
            "n_creators": N_CREATORS,
            "random_seed": RANDOM_SEED,
        },
        "summaries": [
            {
                key: value
                for key, value in summary.items()
                if key not in {"node_descendant_time_series", "mint_surface"}
            }
            for summary in sweep["summaries"]
        ],
        "recommended_alpha": recommended["alpha_value"],
        "recommendation_basis": "lowest_gini_among_configuration_keep_candidates",
        "provisional_alpha_passes": sweep["provisional_alpha_passes"],
        "provisional_alpha_keep": sweep["provisional_alpha_keep"],
        "time_series_path": str(TIME_SERIES_PATH),
        "time_series_shape": {
            "nodes": len(recommended["node_descendant_time_series"]),
            "epochs": len(next(iter(recommended["node_descendant_time_series"].values()))),
        },
    }
    SUMMARY_PATH.write_text(
        json.dumps(_json_safe(summary_payload), allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_safe(summary_payload), allow_nan=False, indent=2, sort_keys=True))
    print(f"\nTime series written to {TIME_SERIES_PATH}")
    return sweep


if __name__ == "__main__":
    main()
