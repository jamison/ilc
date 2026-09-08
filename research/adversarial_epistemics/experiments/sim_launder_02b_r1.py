"""
SIM-LAUNDER-02B-R1 — Observer Epistemics: Corrected Context Separation
=======================================================================

Corrects the measurement confound in SIM-LAUNDER-02B.

Bug: context_separation(claim, 30, rng) sliced claim.observers[:30].
For CONTEXTUAL/SUBJECTIVE, observers 0–49 are context_id=1 and 50–99 are
context_id=2. Slicing [:30] returned only context_id=1 → single group →
ctx_sep=0.0 for all claim types (uninterpretable).

Fix: replace sequential slice with random sampling from all N_OBS observers,
so both context groups are represented at every n_obs_used.

Additionally: sweep n_obs_used ∈ {7, 15, 30, 50, 100} to test whether
context recovery is a sample-size phenomenon (parallel to SIM-PANEL-01 finding
that probe size dramatically changed signal detectability).

Report (within_context_agreement, between_context_agreement) separately, not
just ctx_sep = within − between. Astra's key distinction:

  CONTEXTUAL:  high within, low between   → context-relative truth
  SUBJECTIVE:  high within, low between   → value-driven polarization
  OBJECTIVE:   high within, high between  → true independent of context
  CONTESTED:   moderate within, moderate between → genuine ambiguity

All claim types, jury parameters, and voter model frozen from 02B.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
import math
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SIM_ID       = "SIM-LAUNDER-02B-R1"
N_TRIALS     = 10_000
PANEL_SIZE   = 7
N_OBS        = 100
N_OBS_SWEEP  = [7, 15, 30, 50, 100]

CLAIM_TYPES  = ["OBJECTIVE", "CONTESTED", "CONTEXTUAL", "SUBJECTIVE"]


@dataclass
class Observer:
    obs_id: int
    context_id: int
    base_accuracy: float


@dataclass
class Claim:
    claim_type: str
    ground_truth: bool
    context_truths: Dict[int, bool] = field(default_factory=dict)
    observers: List[Observer] = field(default_factory=list)


def build_claim(claim_type: str, rng: np.random.Generator) -> Claim:
    if claim_type == "OBJECTIVE":
        return Claim("OBJECTIVE", True, {},
                     [Observer(i, 0, rng.beta(7, 2)) for i in range(N_OBS)])
    elif claim_type == "CONTESTED":
        return Claim("CONTESTED", True, {},
                     [Observer(i, 0, rng.beta(3, 3)) for i in range(N_OBS)])
    elif claim_type == "CONTEXTUAL":
        ctx_truths = {1: True, 2: False}
        obs = [Observer(i, 1 if i < N_OBS // 2 else 2, rng.beta(7, 2))
               for i in range(N_OBS)]
        return Claim("CONTEXTUAL", True, ctx_truths, obs)
    elif claim_type == "SUBJECTIVE":
        ctx_truths = {1: True, 2: False}
        obs = [Observer(i, 1 if i < N_OBS // 2 else 2, 0.92)
               for i in range(N_OBS)]
        return Claim("SUBJECTIVE", True, ctx_truths, obs)
    else:
        raise ValueError(f"Unknown claim type: {claim_type}")


def vote(observer: Observer, claim: Claim, rng: np.random.Generator) -> int:
    if claim.context_truths:
        truth = claim.context_truths.get(observer.context_id, claim.ground_truth)
    else:
        truth = claim.ground_truth
    signal = 1.0 if truth else -1.0
    raw = signal * observer.base_accuracy * 2 + rng.normal(0, 1)
    return 1 if raw > 0 else 0


def jury_trial(claim: Claim, panel_size: int,
               rng: np.random.Generator) -> Tuple[int, List[int]]:
    panel = rng.choice(len(claim.observers), size=panel_size, replace=False)
    votes = [vote(claim.observers[p], claim, rng) for p in panel]
    verdict = 1 if sum(votes) > panel_size / 2 else 0
    return verdict, votes


def context_separation(claim: Claim, n_obs_used: int,
                        rng: np.random.Generator) -> Tuple[float, float, float]:
    """
    Returns (within_ctx_agreement, between_ctx_agreement, ctx_sep).

    FIX from 02B: random sampling, not sequential slice.
    This ensures both context groups are represented at all n_obs_used values.

    within_ctx_agreement: mean max(p, 1-p) within each context group.
    between_ctx_agreement: mean (1 - |mean_i - mean_j|) across context pairs.
    ctx_sep = within - between.

    For single-context claims (OBJECTIVE, CONTESTED): between = within, sep = 0.
    """
    if n_obs_used >= len(claim.observers):
        obs = claim.observers
    else:
        indices = rng.choice(len(claim.observers), size=n_obs_used, replace=False)
        obs = [claim.observers[i] for i in indices]

    votes_by_ctx: Dict[int, List[int]] = {}
    for o in obs:
        v = vote(o, claim, rng)
        votes_by_ctx.setdefault(o.context_id, []).append(v)

    # Within-context agreement
    within_agreements = []
    for ctx_votes in votes_by_ctx.values():
        if len(ctx_votes) < 2:
            continue
        p = sum(ctx_votes) / len(ctx_votes)
        within_agreements.append(max(p, 1 - p))
    within_ctx = (sum(within_agreements) / len(within_agreements)
                  if within_agreements else 0.5)

    # Between-context agreement
    ctx_means = {c: sum(v) / len(v) for c, v in votes_by_ctx.items() if v}
    if len(ctx_means) < 2:
        # Only one context observed — no between-context signal
        return within_ctx, within_ctx, 0.0

    means = list(ctx_means.values())
    ctx_pairs = [(means[i], means[j])
                 for i in range(len(means))
                 for j in range(i + 1, len(means))]
    between_ctx = (sum(1 - abs(a - b) for a, b in ctx_pairs)
                   / len(ctx_pairs))

    sep = within_ctx - between_ctx
    return within_ctx, between_ctx, sep


def main() -> None:
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] {len(CLAIM_TYPES)} claim types × {N_TRIALS} trials "
          f"× {len(N_OBS_SWEEP)} n_obs_used values", file=sys.stderr)

    # ── Jury verdicts (unchanged from 02B) ──────────────────────────────────
    verdict_results: dict = {}
    for ct in CLAIM_TYPES:
        claim = build_claim(ct, rng)
        verdicts, vote_fracs = [], []
        for _ in range(N_TRIALS):
            v, votes = jury_trial(claim, PANEL_SIZE, rng)
            verdicts.append(v)
            vote_fracs.append(sum(votes) / len(votes))
        p_true = sum(verdicts) / N_TRIALS
        h = -(p_true * math.log2(max(p_true, 1e-9))
              + (1 - p_true) * math.log2(max(1 - p_true, 1e-9)))
        verdict_results[ct] = {
            "p_verdict_true": round(p_true, 4),
            "verdict_entropy": round(h, 4),
            "mean_vote_fraction": round(sum(vote_fracs) / N_TRIALS, 4),
        }

    # ── Context separation sweep — corrected ────────────────────────────────
    print(f"\n{'Claim type':15s} {'n_obs':>6} {'within':>8} {'between':>8} "
          f"{'ctx_sep':>8}", file=sys.stderr)

    context_results: dict = {}
    for ct in CLAIM_TYPES:
        claim = build_claim(ct, rng)
        context_results[ct] = {}
        for n_obs in N_OBS_SWEEP:
            w_list, b_list, s_list = [], [], []
            for _ in range(N_TRIALS):
                w, b, s = context_separation(claim, n_obs, rng)
                w_list.append(w)
                b_list.append(b)
                s_list.append(s)
            mean_w = round(sum(w_list) / N_TRIALS, 4)
            mean_b = round(sum(b_list) / N_TRIALS, 4)
            mean_s = round(sum(s_list) / N_TRIALS, 4)
            context_results[ct][n_obs] = {
                "mean_within_ctx": mean_w,
                "mean_between_ctx": mean_b,
                "mean_ctx_sep": mean_s,
            }
            print(f"  {ct:13s} {n_obs:6d} {mean_w:8.4f} {mean_b:8.4f} {mean_s:8.4f}",
                  file=sys.stderr)

    # ── Prediction verdicts ─────────────────────────────────────────────────

    # P1 (inherited from 02B): CONTEXTUAL and CONTESTED jury entropy
    h_ctx  = verdict_results["CONTEXTUAL"]["verdict_entropy"]
    h_cont = verdict_results["CONTESTED"]["verdict_entropy"]
    p1_v = "CONFIRMED" if abs(h_ctx - h_cont) < 0.05 else "REFUTED"
    print(f"\nP1: CONTEXTUAL H={h_ctx:.4f} vs CONTESTED H={h_cont:.4f} "
          f"diff={abs(h_ctx-h_cont):.4f} [{p1_v}]", file=sys.stderr)

    # P2 (corrected): at n_obs_used=100, CONTEXTUAL ctx_sep >> CONTESTED
    ctx_sep_100  = context_results["CONTEXTUAL"][100]["mean_ctx_sep"]
    cont_sep_100 = context_results["CONTESTED"][100]["mean_ctx_sep"]
    p2_v = "CONFIRMED" if ctx_sep_100 > cont_sep_100 + 0.05 else "REFUTED"
    print(f"P2 (n=100): CONTEXTUAL ctx_sep={ctx_sep_100:.4f} vs "
          f"CONTESTED ctx_sep={cont_sep_100:.4f} [{p2_v}]", file=sys.stderr)

    # P3: SUBJECTIVE vs CONTEXTUAL jury entropy indistinguishable
    h_subj = verdict_results["SUBJECTIVE"]["verdict_entropy"]
    p3_v = "CONFIRMED" if abs(h_subj - h_ctx) < 0.10 else "REFUTED"
    print(f"P3: SUBJECTIVE H={h_subj:.4f} vs CONTEXTUAL H={h_ctx:.4f} [{p3_v}]",
          file=sys.stderr)

    # P4 (new): SUBJECTIVE and CONTEXTUAL distinguishable by (within, between)?
    subj_w100 = context_results["SUBJECTIVE"][100]["mean_within_ctx"]
    subj_b100 = context_results["SUBJECTIVE"][100]["mean_between_ctx"]
    ctx_w100  = context_results["CONTEXTUAL"][100]["mean_within_ctx"]
    ctx_b100  = context_results["CONTEXTUAL"][100]["mean_between_ctx"]
    between_gap = abs(subj_b100 - ctx_b100)
    p4_v = "CONFIRMED" if between_gap > 0.05 else "REFUTED"
    print(f"P4: SUBJECTIVE between={subj_b100:.4f} vs "
          f"CONTEXTUAL between={ctx_b100:.4f} gap={between_gap:.4f} [{p4_v}]",
          file=sys.stderr)
    print(f"    (SUBJECTIVE within={subj_w100:.4f}, CONTEXTUAL within={ctx_w100:.4f})",
          file=sys.stderr)

    # P5: ctx_sep for CONTEXTUAL increases with n_obs_used (sample-size effect)
    ctxl_seps = [context_results["CONTEXTUAL"][n]["mean_ctx_sep"] for n in N_OBS_SWEEP]
    # Check if generally increasing (allow small dips < 0.02)
    monotone = all(ctxl_seps[i+1] >= ctxl_seps[i] - 0.02
                   for i in range(len(ctxl_seps) - 1))
    p5_v = "CONFIRMED" if monotone else "REFUTED"
    print(f"P5: CONTEXTUAL ctx_sep vs n_obs: "
          f"{list(zip(N_OBS_SWEEP, [round(s, 4) for s in ctxl_seps]))} [{p5_v}]",
          file=sys.stderr)

    # ── Key (within, between) table at n_obs=100 ───────────────────────────
    print(f"\n{'Claim type':15s} {'within@100':>11} {'between@100':>12} "
          f"{'ctx_sep@100':>12}", file=sys.stderr)
    for ct in CLAIM_TYPES:
        r = context_results[ct][100]
        print(f"  {ct:13s} {r['mean_within_ctx']:11.4f} {r['mean_between_ctx']:12.4f} "
              f"{r['mean_ctx_sep']:12.4f}", file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Corrected context separation: random sampling, (within, between) reported separately",
        "fix_applied": (
            "context_separation() now uses rng.choice(N_OBS, n_obs_used, replace=False) "
            "instead of observers[:n_obs_used]. Both context groups are sampled at all "
            "n_obs_used values."
        ),
        "verdict_results": verdict_results,
        "context_results": {ct: {str(k): v for k, v in d.items()}
                            for ct, d in context_results.items()},
        "predictions": {
            "P1": "CONTEXTUAL and CONTESTED have different jury entropy (>0.05)",
            "P2": "CORRECTED: at n_obs=100, CONTEXTUAL ctx_sep >> CONTESTED (+0.05)",
            "P3": "SUBJECTIVE and CONTEXTUAL indistinguishable by jury entropy (<0.10)",
            "P4": "SUBJECTIVE and CONTEXTUAL distinguishable by between_ctx gap (>0.05)",
            "P5": "CONTEXTUAL ctx_sep increases (or stays stable) with n_obs_used",
        },
        "prediction_verdicts": {
            "P1": p1_v, "P2": p2_v, "P3": p3_v, "P4": p4_v, "P5": p5_v,
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha384(payload).hexdigest()
    result["sha384"] = sha
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha}", file=sys.stderr)


if __name__ == "__main__":
    main()
