"""
SIM-SIGNAL-01 — Can the Protocol Detect That It Doesn't Know?
=============================================================

Research question: Can observable disagreement signals (vote entropy, minority
fraction, probe-panel spread) reliably discriminate hard claims from easy ones,
WITHOUT seeing the latent signal_strength?

Motivation (Astra 6.0 feedback): The proposed defense "route weak-signal claims
to larger panels" requires that the protocol can identify weak-signal claims at
evaluation time. If disagreement statistics can't discriminate difficulty, the
routing mechanism is not implementable.

Design:
  - Generate claims with known latent difficulty d ∈ {1.0, 0.7, 0.5, 0.3, 0.2, 0.1}
  - Run a "probe panel" of n_probe=5 validators
  - Observable signals (no ground truth or latent d exposed):
      disagreement  = fraction of minority votes (0=full consensus, 0.5=50-50 split)
      vote_entropy  = H(p, 1-p) where p = fraction voting True
      range_signal  = max - min vote on [0,1] (always 1 for binary, use std instead)
      confidence    = |mean_vote - 0.5| * 2 (0=uncertain, 1=certain)
  - Routing rule: if disagreement > threshold → escalate (larger panel / sequential)
  - Measure:
      AUC of disagreement to separate difficulty classes
      P(escalate | hard) — sensitivity: does disagreement catch hard claims?
      P(escalate | easy) — false escalation rate: does it incorrectly flag easy claims?
      Optimal threshold for each (sensitivity, specificity) tradeoff
  - Critical test: can the protocol correctly rank claim difficulty from probe alone?

Falsifiable predictions:
  P1: AUC(disagreement → difficulty class) > 0.75 when comparing strong vs weak/marginal
  P2: AUC < 0.65 when comparing medium vs weak (adjacent difficulty classes are hard to separate)
  P3: At the optimal threshold: sensitivity > 80% AND false escalation rate < 25%
      for strong vs (weak+marginal) discrimination
  P4: A 5-member probe panel provides sufficient signal — 15-member adds <5pp AUC

Methodological note:
  This tests whether the model's signal_strength parameter (a latent variable) is
  recoverable from observable vote patterns. Real protocol "difficulty estimation"
  faces additional complications: adversarial validators may strategically disagree
  on easy claims to trigger expensive escalation (a resource exhaustion attack).
  That attack is not modeled here — it is the subject of SIM-CAMOUFLAGE-01.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
import math
from datetime import datetime, timezone
from typing import List, Dict, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import SimulationConfig
from agents import build_population
from jury import select_jury, cast_votes

SIM_ID = "SIM-SIGNAL-01"

DIFFICULTY_LEVELS = [1.0, 0.7, 0.5, 0.3, 0.2, 0.1]  # = signal_strength
PROBE_SIZES = [5, 15]
N_CLAIMS = 5000   # per difficulty level
FALSE_RATE = 0.30


def entropy(p: float) -> float:
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def probe_claim(agents, ex_indices, probe_size, signal_val, ground_truth, rho, rng) -> Dict:
    panel = select_jury(agents, ex_indices, probe_size, rng)
    if not panel:
        return {}
    votes, verdict = cast_votes(agents, panel, ground_truth, rho=rho, rng=rng, signal_strength=signal_val)
    n = len(votes)
    p_true = sum(votes) / n
    disagreement = min(p_true, 1 - p_true)  # minority fraction (0=unanimous, 0.5=split)
    vote_entropy = entropy(p_true)
    confidence = abs(p_true - 0.5) * 2    # 0=uncertain, 1=certain
    return {
        "disagreement": disagreement,
        "vote_entropy": vote_entropy,
        "confidence": confidence,
        "verdict": verdict,
        "ground_truth": ground_truth,
        "is_correct": verdict == ground_truth,
    }


def auc_binary(scores, labels) -> float:
    """
    Mann-Whitney U statistic = AUC, with proper tie handling.
    labels: True = positive class (e.g., hard/difficult claim).
    scores: higher = predicted more likely positive.

    For each (positive, negative) pair: +1 if pos_score > neg_score, +0.5 if tie.
    AUC = U / (n_pos * n_neg)
    """
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5

    from collections import defaultdict
    buckets: dict = defaultdict(lambda: [0, 0])  # score → [n_pos, n_neg]
    for s, l in zip(scores, labels):
        if l:
            buckets[s][0] += 1
        else:
            buckets[s][1] += 1

    u = 0.0
    neg_below = 0   # count of negatives with strictly lower score
    for score in sorted(buckets.keys()):
        n_p, n_n = buckets[score][0], buckets[score][1]
        # Each positive at this score beats all negatives below (full credit)
        # and ties with negatives at the same score (half credit)
        u += n_p * neg_below + n_p * n_n * 0.5
        neg_below += n_n

    return u / (n_pos * n_neg)


def find_optimal_threshold(scores, labels, metric="f1") -> Tuple[float, Dict]:
    """Find threshold maximizing balanced accuracy (sensitivity+specificity)/2."""
    unique = sorted(set(scores))
    # Use midpoints between consecutive score values as candidate thresholds
    # so we avoid trivial all-positive or all-negative predictions
    if len(unique) < 2:
        return unique[0], {"threshold": unique[0], "f1": 0.0, "sensitivity": 0.0, "specificity": 0.0, "false_escalation_rate": 1.0}
    thresholds = [(unique[i] + unique[i+1]) / 2.0 for i in range(len(unique)-1)]
    best = {"threshold": thresholds[0], "f1": 0.0, "sensitivity": 0.0, "specificity": 0.0, "false_escalation_rate": 1.0, "balanced_acc": 0.0}
    for t in thresholds:
        preds = [s >= t for s in scores]
        tp = sum(p and l for p, l in zip(preds, labels))
        fp = sum(p and not l for p, l in zip(preds, labels))
        fn = sum(not p and l for p, l in zip(preds, labels))
        tn = sum(not p and not l for p, l in zip(preds, labels))
        sensitivity = tp / max(tp + fn, 1)
        specificity = tn / max(tn + fp, 1)
        precision = tp / max(tp + fp, 1)
        f1 = 2 * precision * sensitivity / max(precision + sensitivity, 1e-9)
        balanced_acc = (sensitivity + specificity) / 2.0
        if balanced_acc > best["balanced_acc"]:
            best = {"threshold": t, "f1": round(f1, 4), "sensitivity": round(sensitivity, 4),
                    "specificity": round(specificity, 4), "false_escalation_rate": round(1 - specificity, 4),
                    "balanced_acc": round(balanced_acc, 4)}
    return best["threshold"], best


def main():
    cfg = SimulationConfig(
        n_validators=1000,
        n_operator_clusters=10,
        n_domains=5,
        panel_size=7,
        trials_per_condition=N_CLAIMS,
        false_claim_rate=FALSE_RATE,
        expertise_threshold=0.60,
        adversarial_fraction=0.0,
        random_seed=42,
    )

    rng = np.random.default_rng(cfg.random_seed)
    agents = build_population(cfg, rng)
    ex_indices = list(range(200))   # E(x) = 200 domain experts

    total = len(DIFFICULTY_LEVELS) * len(PROBE_SIZES) * N_CLAIMS
    print(f"[{SIM_ID}] {len(DIFFICULTY_LEVELS)} difficulty × {len(PROBE_SIZES)} probe sizes × {N_CLAIMS} claims = {total:,}", file=sys.stderr)

    # Collect probe observations per difficulty level
    observations = {}  # (signal_val, probe_size) → list of probe results
    for signal_val in DIFFICULTY_LEVELS:
        for probe_size in PROBE_SIZES:
            obs = []
            for _ in range(N_CLAIMS):
                ground_truth = rng.random() >= FALSE_RATE
                result = probe_claim(agents, ex_indices, probe_size, signal_val, ground_truth, rho=0.0, rng=rng)
                if result:
                    obs.append({**result, "signal_val": signal_val})
            observations[(signal_val, probe_size)] = obs
            mean_disagree = sum(o["disagreement"] for o in obs) / len(obs)
            print(f"  signal={signal_val:.1f} probe={probe_size}: mean_disagreement={mean_disagree:.4f}", file=sys.stderr)

    # AUC analysis: can disagreement separate difficulty classes?
    auc_results = []
    probe_size = 5  # primary probe size for AUC analysis

    # All pairwise class separations
    comparisons = [
        ("strong", 1.0, "weak", 0.2),
        ("strong", 1.0, "marginal", 0.1),
        ("medium", 0.5, "weak", 0.2),
        ("strong", 1.0, "medium", 0.5),
        ("weak", 0.2, "marginal", 0.1),
    ]

    for easy_label, easy_val, hard_label, hard_val in comparisons:
        easy_obs = observations[(easy_val, probe_size)]
        hard_obs  = observations[(hard_val, probe_size)]

        # Use disagreement as score: higher disagreement → more likely hard
        scores = [o["disagreement"] for o in easy_obs] + [o["disagreement"] for o in hard_obs]
        labels = [False] * len(easy_obs) + [True] * len(hard_obs)

        auc = auc_binary(scores, labels)
        _, opt = find_optimal_threshold(scores, labels)

        auc_results.append({
            "comparison": f"{easy_label}(={easy_val}) vs {hard_label}(={hard_val})",
            "easy_signal": easy_val,
            "hard_signal": hard_val,
            "probe_size": probe_size,
            "auc": round(auc, 4),
            "optimal_threshold": round(opt["threshold"], 4),
            "sensitivity_at_optimal": opt["sensitivity"],
            "false_escalation_rate_at_optimal": opt["false_escalation_rate"],
            "f1_at_optimal": opt["f1"],
        })
        print(
            f"  AUC({easy_label} vs {hard_label}): {auc:.4f} | "
            f"opt_threshold={opt['threshold']:.3f} sensitivity={opt['sensitivity']:.3f} "
            f"false_escl={opt['false_escalation_rate']:.3f}",
            file=sys.stderr,
        )

    # Probe size comparison for P4: does larger probe add AUC?
    probe_comparison = []
    easy_val, hard_val = 1.0, 0.2
    for ps in PROBE_SIZES:
        easy_obs = observations[(easy_val, ps)]
        hard_obs  = observations[(hard_val, ps)]
        scores = [o["disagreement"] for o in easy_obs] + [o["disagreement"] for o in hard_obs]
        labels = [False] * len(easy_obs) + [True] * len(hard_obs)
        auc = auc_binary(scores, labels)
        probe_comparison.append({"probe_size": ps, "auc_strong_vs_weak": round(auc, 4)})
    print(f"\nP4 check (probe size vs AUC): {probe_comparison}", file=sys.stderr)

    # Mean disagreement by difficulty level
    disagree_by_signal = {}
    for signal_val in DIFFICULTY_LEVELS:
        obs = observations[(signal_val, 5)]
        disagree_by_signal[str(signal_val)] = {
            "mean_disagreement": round(sum(o["disagreement"] for o in obs) / len(obs), 4),
            "mean_confidence": round(sum(o["confidence"] for o in obs) / len(obs), 4),
            "probe_accuracy": round(sum(o["is_correct"] for o in obs) / len(obs), 4),
        }

    result = {
        "sim_id": SIM_ID,
        "description": "Signal detectability: can observable disagreement identify hard claims?",
        "methodological_note": "Tests whether the model's latent signal_strength is recoverable from probe-panel vote patterns. Real protocol difficulty estimation also faces adversarial probe manipulation (see SIM-CAMOUFLAGE-01).",
        "auc_analysis": auc_results,
        "probe_size_comparison": probe_comparison,
        "disagree_by_signal": disagree_by_signal,
        "config": cfg.__dict__,
        "predictions": {
            "P1": "AUC(strong vs weak/marginal) > 0.75",
            "P2": "AUC(medium vs weak) < 0.65",
            "P3": "At optimal threshold: sensitivity>80% AND false_escalation<25% for strong vs (weak+marginal)",
            "P4": "15-member probe adds <5pp AUC vs 5-member probe",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sha384 = hashlib.sha384(payload_bytes).hexdigest()
    result["sha384"] = sha384

    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha384}", file=sys.stderr)

    # Prediction summary
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"SIM-SIGNAL-01 PREDICTIONS", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    p1_aucs = [r for r in auc_results if r["hard_signal"] in (0.2, 0.1) and r["easy_signal"] == 1.0]
    for r in p1_aucs:
        v = "CONFIRMED" if r["auc"] > 0.75 else "REFUTED"
        print(f"P1: {r['comparison']} AUC={r['auc']:.4f} [{v}]", file=sys.stderr)
    p2 = next((r for r in auc_results if r["easy_signal"] == 0.5 and r["hard_signal"] == 0.2), None)
    if p2:
        v = "CONFIRMED" if p2["auc"] < 0.65 else "REFUTED"
        print(f"P2: {p2['comparison']} AUC={p2['auc']:.4f} [{v}]", file=sys.stderr)
    p3 = next((r for r in auc_results if r["easy_signal"] == 1.0 and r["hard_signal"] == 0.2), None)
    if p3:
        v = "CONFIRMED" if p3["sensitivity_at_optimal"] > 0.80 and p3["false_escalation_rate_at_optimal"] < 0.25 else "REFUTED"
        print(f"P3: strong vs weak — sens={p3['sensitivity_at_optimal']:.3f} false_escl={p3['false_escalation_rate_at_optimal']:.3f} [{v}]", file=sys.stderr)
    p4_auc5  = next((r["auc_strong_vs_weak"] for r in probe_comparison if r["probe_size"]==5),  None)
    p4_auc15 = next((r["auc_strong_vs_weak"] for r in probe_comparison if r["probe_size"]==15), None)
    if p4_auc5 is not None and p4_auc15 is not None:
        delta = p4_auc15 - p4_auc5
        v = "CONFIRMED" if delta < 0.05 else "REFUTED"
        print(f"P4: AUC(5-probe)={p4_auc5:.4f} AUC(15-probe)={p4_auc15:.4f} delta={delta:.4f} [{v}]", file=sys.stderr)


if __name__ == "__main__":
    main()
