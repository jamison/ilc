"""
SIM-CORR-01 — Correlated Jury Reasoning
=========================================

Research question:
  How does pairwise epistemic error correlation (rho) degrade jury accuracy,
  and at what rho threshold does a CDL-V3-constrained panel fail to provide
  meaningful epistemic signal?

Independent variable: rho in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

Controlled:
  - Panel size = 7 (DEFAULT_PANEL_SIZE)
  - N validators = 1000
  - N operator clusters = 10 (CDL-V3: max 1/3 per cluster = max 2 per 7-person panel)
  - False claim rate = 0.30
  - No adversarial agents (alpha_x = 0)
  - Expertise threshold = 0.60; each claim has domain d ~ Uniform[0, N_DOMAINS)

Metrics:
  - jury_accuracy (overall)
  - false_consensus_rate (false claims incorrectly ratified)
  - true_rejection_rate (true claims incorrectly rejected)
  - effective_n for each rho (analytical)

Expected finding from prior art:
  At rho=0.5, n=7: effective_n = 7/4 = 1.75.
  Majority vote over 7 validators with rho=0.5 provides roughly the same
  epistemic signal as a single independent validator.
  At rho=0.8, effective_n ~= 1.3 — near-useless aggregation.

Falsifiable prediction (SIM-CORR-01-P1):
  jury_accuracy will fall below 0.65 (chance + small signal) at rho >= 0.70,
  even with a perfectly honest, expert panel.

Output: JSON to stdout, SHA-384 fingerprint for graph intake.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
from datetime import datetime, timezone

import numpy as np

# Ensure parent directory is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import SimulationConfig, ExperimentResult
from agents import build_population
from jury import evaluate_jury_accuracy
from metrics import effective_n, false_consensus_rate, true_rejection_rate, jury_accuracy, summary_stats


RHO_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
SIM_ID = "SIM-CORR-01"


def run_sim_corr_01(cfg: SimulationConfig) -> list:
    rng = np.random.default_rng(cfg.random_seed)
    agents = build_population(cfg, rng)

    results = []

    for rho in RHO_VALUES:
        correct = 0
        false_total = 0
        false_accepted = 0
        true_total = 0
        true_rejected = 0

        for _ in range(cfg.trials_per_condition):
            # Pick a random domain for this claim
            domain = int(rng.integers(0, cfg.n_domains))
            ground_truth = rng.random() >= cfg.false_claim_rate

            # Build E(x): validators with expertise >= threshold for this domain
            eligible = [
                i for i, a in enumerate(agents)
                if a.qualifies_for(domain, cfg.expertise_threshold)
            ]

            if len(eligible) < 3:
                # Degenerate case: not enough experts, skip trial
                continue

            is_correct = evaluate_jury_accuracy(
                agents, eligible, cfg.panel_size, ground_truth, rho, rng
            )

            if is_correct:
                correct += 1
            if not ground_truth:
                false_total += 1
                if not is_correct:   # jury said True when answer was False
                    false_accepted += 1
            else:
                true_total += 1
                if not is_correct:   # jury said False when answer was True
                    true_rejected += 1

        n_trials = false_total + true_total
        eff_n = effective_n(cfg.panel_size, rho)

        results.append({
            "rho": rho,
            "effective_n": round(eff_n, 4),
            "jury_accuracy": round(jury_accuracy(correct, n_trials), 4),
            "false_consensus_rate": round(false_consensus_rate(false_accepted, false_total), 4),
            "true_rejection_rate": round(true_rejection_rate(true_rejected, true_total), 4),
            "n_trials": n_trials,
            "n_eligible_mean": round(sum(
                len([i for i, a in enumerate(agents) if a.qualifies_for(d, cfg.expertise_threshold)])
                for d in range(cfg.n_domains)
            ) / cfg.n_domains, 1),
        })

        print(
            f"  rho={rho:.1f} | eff_n={eff_n:.2f} | "
            f"accuracy={results[-1]['jury_accuracy']:.4f} | "
            f"FCR={results[-1]['false_consensus_rate']:.4f}",
            file=sys.stderr,
        )

    return results


def main():
    cfg = SimulationConfig(
        n_validators=1000,
        n_operator_clusters=10,
        n_domains=5,
        panel_size=7,
        trials_per_condition=10_000,
        false_claim_rate=0.30,
        expertise_threshold=0.60,
        adversarial_fraction=0.0,
        random_seed=42,
    )

    print(f"[{SIM_ID}] Starting — {cfg.trials_per_condition} trials per rho value", file=sys.stderr)
    print(f"[{SIM_ID}] N={cfg.n_validators}, panel_size={cfg.panel_size}, clusters={cfg.n_operator_clusters}", file=sys.stderr)

    rows = run_sim_corr_01(cfg)

    # Build result record
    result = {
        "sim_id": SIM_ID,
        "description": "Correlated jury reasoning: rho sweep, honest expert panel",
        "condition_variable": "rho (pairwise epistemic error correlation)",
        "rows": rows,
        "config": cfg.__dict__,
        "predictions": {
            "SIM-CORR-01-P1": "jury_accuracy falls below 0.65 at rho >= 0.70",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    # SHA-384 fingerprint of the results (graph intake artifact)
    payload_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sha384 = hashlib.sha384(payload_bytes).hexdigest()
    result["sha384"] = sha384

    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha384}", file=sys.stderr)

    # Print readable summary
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"SIM-CORR-01 RESULTS SUMMARY", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    print(f"{'rho':>6} {'eff_n':>8} {'accuracy':>10} {'FCR':>8} {'TRR':>8}", file=sys.stderr)
    print(f"{'-'*70}", file=sys.stderr)
    for row in rows:
        p1_marker = " <-- P1 threshold" if row["rho"] == 0.7 else ""
        print(
            f"{row['rho']:>6.1f} {row['effective_n']:>8.2f} "
            f"{row['jury_accuracy']:>10.4f} {row['false_consensus_rate']:>8.4f} "
            f"{row['true_rejection_rate']:>8.4f}{p1_marker}",
            file=sys.stderr,
        )

    # Prediction verification
    print(f"\nPrediction SIM-CORR-01-P1: accuracy < 0.65 at rho >= 0.70", file=sys.stderr)
    for row in rows:
        if row["rho"] >= 0.70:
            verdict = "CONFIRMED" if row["jury_accuracy"] < 0.65 else "REFUTED"
            print(f"  rho={row['rho']:.1f}: accuracy={row['jury_accuracy']:.4f} => {verdict}", file=sys.stderr)


if __name__ == "__main__":
    main()
