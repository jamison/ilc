#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
SIM: CCSS Global Passive Observer (GPO) Timing Correlation v0.1
Phase: research / forward-planning (Window 1576+ lane)
Seed: 1576

Research question
-----------------
Against a Global Passive Observer (GPO) who can observe ALL relay edges
simultaneously with per-packet timestamps, what privacy does the
CCSS-SPECTRAL-01 stable cover set + L2 timing jitter provide?

Two baselines and one main sweep:

  Baseline A — no jitter, no cover:
    GPO directly observes injection time → P(success) = 1.0 (analytical).

  Baseline B — stable cover set, no jitter:
    GPO sees k_batch * cover_ratio + 1 bundles per epoch but can resolve
    exact injection times → trivially links each bundle to its sender
    → P(success) = 1.0 (analytical). Cover set alone does nothing vs GPO.

  Main sweep — stable cover set + L2 timing jitter:
    Each bundle injection time ~ U(0, batch_window_s).
    GPO has timing precision eps_gpo seconds: any two injections within
    eps_gpo of each other are indistinguishable.
    Injection density = k_batch * cover_ratio / batch_window_s ≈ 8.5 inj/s
    at k_batch=128, cover_ratio=8, window=120s.

    GPO strategy: observe t_real (the real bundle's injection time at the
    first relay hop). Find all senders who injected within [t_real - eps_gpo,
    t_real + eps_gpo]. Guess uniformly among those. Success iff |ambiguity| = 1.

    Extended: temporal intersection over T epochs. With stable cover set the
    same k_batch senders appear every epoch. GPO intersects ambiguity windows
    across epochs. Does not eliminate ambiguity if eps_gpo is large relative
    to cover injection density.

GPO adversary model
-------------------
  - Observes all edge-level events (node_i → relay_j) with timestamp precision
    eps_gpo seconds (clock skew / measurement jitter / processing delay).
  - Knows relay propagation latency is < eps_gpo (conservative: GPO has already
    corrected for latency). This is the strongest plausible GPO.
  - Bundles are indistinguishable in content and size.
  - GPO does NOT know a priori which bundle is real vs cover.
  - Success criterion: |final candidate set| == 1.

Cover model (matching ccss_pre_rc_cover_batch_profile_v1_candidate)
--------------------------------------------------------------------
  - k_batch = 128 senders per epoch batch
  - cover_ratio: cover bundles per real bundle (spec recommends 8:1)
  - Real sender index: 0 (arbitrary; cover senders are 1..k_batch-1)
  - All injection times ~ U(0, batch_window_s) independently

Non-claims
----------
  This SIM does not model mix-net re-ordering, onion routing, or any
  network-layer anonymity system. It does not prove formal unlinkability.
  It does not activate CCSS-SPECTRAL-01 runtime or any guard.
  It models a single relay hop; multi-hop relay path obscuring is separate.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# GPO Resistance Path (L6) - NOT IMPLEMENTED, documented for forward planning
# ---------------------------------------------------------------------------
#
# Sim 4 (this file) shows that L2 sub-epoch jitter alone cannot defeat a
# multi-epoch GPO. At T >= 5 epochs, temporal intersection collapses the
# ambiguity set to ~1 at any realistic timing precision (eps < 1s).
#
# The only mechanism that defeats multi-epoch GPO temporal intersection is
# relay-side shuffle-and-batch release (mix-net style):
#
#   1. Relay collects all inbound bundles for the full batch_window (120s).
#   2. Relay shuffles the collected set uniformly at random.
#   3. Relay releases the shuffled batch at the epoch boundary.
#   4. GPO sees batch release events, not per-sender injection timestamps.
#   5. Temporal intersection no longer has per-sender injection times to anchor.
#
# Required properties for L6 to provide GPO resistance:
#   - Relay must not know which bundles are real vs. cover (cover provenance)
#   - Batch release must be at fixed epoch boundary (not adaptive)
#   - Cover continuity: cover emission continues during sender absence epochs
#   - Minimum batch size >= k_batch before release (hold if insufficient)
#
# L6 is a Window 1576+ design and implementation target.
# It requires: cover provenance spec, relay shuffle protocol, constant-rate
# cover emission protocol, and a dedicated GPO-resistance SIM that models
# the shuffle against a timing adversary.
#
# CCSS_L6_MIX_SHUFFLE_NOT_ACTIVATED = True  (future guard token)
# ---------------------------------------------------------------------------

import json
import random
import time
from pathlib import Path
from typing import Any

SEED: int = 1576
K_BATCH: int = 128
BATCH_WINDOW_S: float = 120.0
TARGET_P_SUCCESS: float = 0.01
OUTPUT_PATH: Path = Path("out/sim_ccss_gpo_timing_results.json")


# ---------------------------------------------------------------------------
# Trial functions
# ---------------------------------------------------------------------------


def run_trial_single_epoch(
    k_batch: int,
    cover_ratio: int,
    batch_window_s: float,
    eps_gpo: float,
    rng: random.Random,
) -> tuple[bool, int]:
    """
    Single epoch: all k_batch senders inject cover_ratio cover bundles each.
    Real sender (id=0) additionally injects 1 real bundle at t_real.
    GPO finds all senders with any injection in [t_real - eps, t_real + eps].
    Returns (gpo_success, ambiguity_set_size).
    """
    t_real = rng.uniform(0, batch_window_s)

    # Build injection event list: (sender_id, injection_time)
    # Real sender's extra real bundle
    events: list[tuple[int, float]] = [(0, t_real)]

    # Cover bundles from all senders (including real sender)
    for sender_id in range(k_batch):
        for _ in range(cover_ratio):
            events.append((sender_id, rng.uniform(0, batch_window_s)))

    # GPO: find all senders with at least one injection within eps_gpo of t_real
    ambiguous: set[int] = set()
    for sender_id, t in events:
        if abs(t - t_real) <= eps_gpo:
            ambiguous.add(sender_id)

    # Real sender always in set (injected at t_real exactly)
    ambiguous.add(0)

    size = len(ambiguous)
    return size == 1, size


def run_trial_multi_epoch(
    k_batch: int,
    cover_ratio: int,
    batch_window_s: float,
    eps_gpo: float,
    T: int,
    rng: random.Random,
) -> tuple[bool, int]:
    """
    GPO intersects per-epoch ambiguity sets across T epochs.
    Real sender's injection time is freshly sampled each epoch (route rotation).
    With stable cover set, same k_batch senders appear every epoch.
    Returns (gpo_success, |final_candidate_set|).
    """
    candidates: set[int] = set(range(k_batch))

    for _ in range(T):
        t_real = rng.uniform(0, batch_window_s)

        # Cover events
        events: list[tuple[int, float]] = [(0, t_real)]
        for sender_id in range(k_batch):
            for _ in range(cover_ratio):
                events.append((sender_id, rng.uniform(0, batch_window_s)))

        # GPO epoch ambiguity restricted to current candidates
        epoch_amb: set[int] = set()
        for sender_id, t in events:
            if sender_id in candidates and abs(t - t_real) <= eps_gpo:
                epoch_amb.add(sender_id)
        epoch_amb.add(0)

        candidates &= epoch_amb

        if len(candidates) <= 1:
            break

    size = len(candidates)
    return size == 1, size


# ---------------------------------------------------------------------------
# Config runner
# ---------------------------------------------------------------------------


def run_config(
    cover_ratio: int,
    eps_gpo: float,
    T: int,
    n_trials: int,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    successes = 0
    total_amb = 0

    for _ in range(n_trials):
        if T == 1:
            s, amb = run_trial_single_epoch(
                K_BATCH, cover_ratio, BATCH_WINDOW_S, eps_gpo, rng
            )
        else:
            s, amb = run_trial_multi_epoch(
                K_BATCH, cover_ratio, BATCH_WINDOW_S, eps_gpo, T, rng
            )
        if s:
            successes += 1
        total_amb += amb

    p_success = successes / n_trials
    return {
        "k_batch": K_BATCH,
        "cover_ratio": cover_ratio,
        "batch_window_s": BATCH_WINDOW_S,
        "eps_gpo_s": round(eps_gpo, 5),
        "T": T,
        "p_success": round(p_success, 4),
        "avg_ambiguity_size": round(total_amb / n_trials, 1),
        "n_trials": n_trials,
        "successes": successes,
        "target_met": bool(p_success <= TARGET_P_SUCCESS),
    }


# ---------------------------------------------------------------------------
# Sweep configuration
# ---------------------------------------------------------------------------

# Injection density = K_BATCH * cover_ratio / BATCH_WINDOW_S
# At cover_ratio=8: 128*8/120 ≈ 8.5 inj/s across all senders
# Expected injections per sender in eps window: cover_ratio * (2*eps / window)
# At eps=1s: 8 * (2/120) ≈ 0.133 inj/sender → ~17 senders in window
# At eps=0.1s: 8 * (0.2/120) ≈ 0.013 inj/sender → ~1.7 senders in window
# Threshold for target ≤ 0.01: need avg_ambiguity ≈ 1 → eps << 1/(cover_density)

EPS_GPO_VALUES: list[float] = [
    0.001,   # 1ms — near-perfect clocks
    0.005,   # 5ms
    0.01,    # 10ms
    0.05,    # 50ms
    0.1,     # 100ms — realistic NTP jitter
    0.5,     # 500ms
    1.0,     # 1s
    5.0,     # 5s
    10.0,    # 10s
    30.0,    # 30s
    60.0,    # 1min (half the batch window)
]

COVER_RATIOS: list[int] = [1, 4, 8, 16]
T_VALUES: list[int] = [1, 5, 20]
N_TRIALS: int = 1000


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    t0 = time.time()

    print("CCSS GPO Timing Correlation SIM v0.1")
    print(f"Seed={SEED}  k_batch={K_BATCH}  batch_window={BATCH_WINDOW_S}s")
    print(f"Target P(GPO success) ≤ {TARGET_P_SUCCESS}")
    print()
    print("Baseline A — no jitter, no cover: P(success) = 1.000 (analytical)")
    print("Baseline B — stable cover, no jitter: P(success) = 1.000 (analytical)")
    print("  → Cover set provides NO protection vs GPO without timing jitter.")
    print()

    # Compute analytical expected ambiguity for reference
    print("Analytical expected ambiguity size at cover_ratio=8:")
    for eps in EPS_GPO_VALUES:
        # Expected injections from other senders in [t-eps, t+eps]:
        # Each of the k_batch-1 other senders has cover_ratio inj ~ U(0,W)
        # P(any of their cover_ratio inj lands in window) =
        #   1 - (1 - 2*eps/W)^cover_ratio  ≈ cover_ratio * 2*eps/W for small eps
        p_other = 1 - (1 - 2 * eps / BATCH_WINDOW_S) ** 8
        exp_others = (K_BATCH - 1) * p_other
        print(f"  eps={eps:6.3f}s → E[others in window]={exp_others:6.1f} "
              f"→ E[ambiguity]≈{exp_others+1:6.1f}")
    print()

    sweep: list[tuple[int, float, int]] = [
        (cr, eps, T)
        for cr in COVER_RATIOS
        for eps in EPS_GPO_VALUES
        for T in T_VALUES
    ]
    total = len(sweep)
    results: list[dict[str, Any]] = []

    print(f"Sweep: {total} configs")
    print(f"{'cover_r':>8} {'eps_gpo':>8} {'T':>4}  {'P(succ)':>8}  "
          f"{'avg_amb':>8}  {'✓?':>3}")
    print("-" * 55)

    for i, (cr, eps, T) in enumerate(sweep):
        r = run_config(cr, eps, T, N_TRIALS, SEED + i * 17)
        results.append(r)
        mark = "✓" if r["target_met"] else "✗"
        print(
            f"{cr:>8} {eps:>8.4f} {T:>4}"
            f"  {r['p_success']:>8.4f}  {r['avg_ambiguity_size']:>8.1f}  {mark}"
        )

    # Summary table
    print(f"\n{'='*70}")
    print(f"  Minimum eps_gpo (s) for P(GPO success) ≤ {TARGET_P_SUCCESS}")
    print(f"  k_batch={K_BATCH}, batch_window={BATCH_WINDOW_S}s, L2 jitter active")
    print(f"{'='*70}")
    print(f"{'cover_r':>8}  {'T=1':>14}  {'T=5':>14}  {'T=20':>14}")
    print("-" * 60)

    summary: dict[str, Any] = {}
    for cr in COVER_RATIOS:
        row = [f"{cr:>8}"]
        for T in T_VALUES:
            sub = sorted(
                [r for r in results
                 if r["cover_ratio"] == cr and r["T"] == T],
                key=lambda r: r["eps_gpo_s"],
            )
            min_eps = next(
                (r["eps_gpo_s"] for r in sub if r["target_met"]), None
            )
            summary[f"cover_ratio={cr}_T={T}"] = {
                "min_eps_gpo_s": min_eps,
                "curve": [
                    {
                        "eps_gpo_s": r["eps_gpo_s"],
                        "p_success": r["p_success"],
                        "avg_ambiguity": r["avg_ambiguity_size"],
                    }
                    for r in sub
                ],
            }
            row.append(f"{min_eps:.4f}s    " if min_eps is not None else "  n/a          ")
        print("  ".join(row))

    elapsed = round(time.time() - t0, 1)

    # Interpretation note
    print()
    print("Key finding: cover set alone provides NO GPO protection.")
    print("L2 jitter provides GPO protection proportional to:")
    print("  eps_gpo × (k_batch × cover_ratio / batch_window_s)")
    print("At the spec cover_ratio=8: injection density ≈ 8.5 bundles/s")
    print("Target eps_gpo threshold sets the required clock-sync precision")
    print("that the adversary must exceed to de-anonymize the sender.")

    output: dict[str, Any] = {
        "sim_id": "sim_ccss_gpo_timing_v0.1",
        "seed": SEED,
        "k_batch": K_BATCH,
        "batch_window_s": BATCH_WINDOW_S,
        "target_p_success": TARGET_P_SUCCESS,
        "baselines": {
            "no_jitter_no_cover": "P(success)=1.000 (analytical)",
            "stable_cover_no_jitter": "P(success)=1.000 (analytical)",
        },
        "model_notes": (
            "GPO observes all relay edges simultaneously. "
            "Timing precision eps_gpo is GPO measurement resolution. "
            "Cover bundles indistinguishable from real. "
            "Stable cover set: same k_batch senders every epoch. "
            "Temporal intersection tested across T epochs."
        ),
        "elapsed_seconds": elapsed,
        "results": results,
        "summary": summary,
    }
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2))

    print(f"\nElapsed: {elapsed}s")
    print(f"Results written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
