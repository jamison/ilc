"""
SIM-CORR-02 — Signal Strength × Correlation Phase Surface
===========================================================

SIM-CORR-01 result: under strong signal, correlation degrades FCR 3.2× but
does not collapse accuracy. The real vulnerability is at WEAK SIGNAL — when
genuine experts legitimately disagree.

This experiment maps the 2D surface:
  signal_strength × rho → FCR, accuracy, effective_n

Finding the phase transition: at what (signal_strength, rho) does FCR
cross a threshold that is operationally significant?

Design:
  signal_strength (label → actual value):
    "strong"   → 1.0 (SIM-CORR-01 baseline)
    "medium"   → 0.5 (experts agree but less confidently)
    "weak"     → 0.2 (genuine expert disagreement)
    "marginal" → 0.1 (claim near-indistinguishable from noise)

  rho in [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]

  10,000 trials per cell = 24 cells × 10,000 = 240,000 simulated claims.

Falsifiable predictions (SIM-CORR-02-P*):
  P1: At weak signal (0.2) + rho >= 0.6, FCR exceeds 15%.
  P2: At marginal signal (0.1) + rho >= 0.4, FCR exceeds 30%.
  P3: The phase transition is sharp: small rho increase near rho_critical
      causes a nonlinear jump in FCR (doubling within one rho step).
  P4: The dangerous region (FCR > 10%) begins at approximately:
      marginal: rho >= 0.0
      weak:     rho >= 0.4
      medium:   rho >= 0.8
      strong:   never (within this parameter range)
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import SimulationConfig
from agents import build_population
from jury import evaluate_jury_accuracy

SIM_ID = "SIM-CORR-02"

SIGNAL_CONDITIONS = [
    ("strong",   1.0),
    ("medium",   0.5),
    ("weak",     0.2),
    ("marginal", 0.1),
]

RHO_VALUES = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]
N_TRIALS = 10_000
FALSE_CLAIM_RATE = 0.30


def run_cell(agents, eligible_indices, cfg, signal_label, signal_val, rho, rng):
    correct = 0
    false_total = 0
    false_accepted = 0
    true_total = 0
    true_rejected = 0

    for _ in range(N_TRIALS):
        domain = int(rng.integers(0, cfg.n_domains))
        eligible = [i for i in eligible_indices if agents[i].expertise_for(domain) >= cfg.expertise_threshold]
        if len(eligible) < 3:
            continue

        ground_truth = rng.random() >= FALSE_CLAIM_RATE
        is_correct = evaluate_jury_accuracy(
            agents, eligible, cfg.panel_size, ground_truth, rho, rng,
            signal_strength=signal_val,
        )

        if is_correct:
            correct += 1
        if not ground_truth:
            false_total += 1
            if not is_correct:
                false_accepted += 1
        else:
            true_total += 1
            if not is_correct:
                true_rejected += 1

    n = false_total + true_total
    fcr = false_accepted / false_total if false_total else 0.0
    trr = true_rejected / true_total if true_total else 0.0
    acc = correct / n if n else 0.0

    return {
        "signal": signal_label,
        "signal_value": signal_val,
        "rho": rho,
        "jury_accuracy": round(acc, 4),
        "false_consensus_rate": round(fcr, 4),
        "true_rejection_rate": round(trr, 4),
        "n_trials": n,
    }


def main():
    cfg = SimulationConfig(
        n_validators=1000,
        n_operator_clusters=10,
        n_domains=5,
        panel_size=7,
        trials_per_condition=N_TRIALS,
        false_claim_rate=FALSE_CLAIM_RATE,
        expertise_threshold=0.60,
        adversarial_fraction=0.0,
        random_seed=42,
    )

    rng = np.random.default_rng(cfg.random_seed)
    agents = build_population(cfg, rng)
    eligible_all = list(range(len(agents)))

    total_cells = len(SIGNAL_CONDITIONS) * len(RHO_VALUES)
    print(f"[{SIM_ID}] Starting — {total_cells} conditions × {N_TRIALS} trials = {total_cells * N_TRIALS:,} simulated claims", file=sys.stderr)

    rows = []
    for signal_label, signal_val in SIGNAL_CONDITIONS:
        for rho in RHO_VALUES:
            row = run_cell(agents, eligible_all, cfg, signal_label, signal_val, rho, rng)
            rows.append(row)
            print(
                f"  signal={signal_label:8s}({signal_val:.1f}) rho={rho:.1f} | "
                f"acc={row['jury_accuracy']:.4f} FCR={row['false_consensus_rate']:.4f} TRR={row['true_rejection_rate']:.4f}",
                file=sys.stderr,
            )

    result = {
        "sim_id": SIM_ID,
        "description": "2D phase surface: signal_strength × rho → FCR",
        "condition_variables": ["signal_strength", "rho"],
        "rows": rows,
        "config": cfg.__dict__,
        "predictions": {
            "SIM-CORR-02-P1": "weak(0.2) + rho>=0.6 => FCR > 15%",
            "SIM-CORR-02-P2": "marginal(0.1) + rho>=0.4 => FCR > 30%",
            "SIM-CORR-02-P3": "phase transition is sharp: FCR doubles within one rho step near rho_critical",
            "SIM-CORR-02-P4": "dangerous region (FCR>10%): marginal@rho>=0, weak@rho>=0.4, medium@rho>=0.8, strong: never",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sha384 = hashlib.sha384(payload_bytes).hexdigest()
    result["sha384"] = sha384

    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha384}", file=sys.stderr)

    # Summary table
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"SIM-CORR-02 — FCR surface (signal × rho)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    header = f"{'signal':>10}  {'val':>5}  " + "  ".join(f"rho={r:.1f}" for r in RHO_VALUES)
    print(header, file=sys.stderr)
    print("-" * len(header), file=sys.stderr)
    for signal_label, signal_val in SIGNAL_CONDITIONS:
        fcrs = [r["false_consensus_rate"] for r in rows if r["signal"] == signal_label]
        row_str = f"{signal_label:>10}  {signal_val:>5.1f}  " + "  ".join(f"{f:>7.4f}" for f in fcrs)
        print(row_str, file=sys.stderr)

    # Prediction verification
    print(f"\nPrediction verification:", file=sys.stderr)
    for row in rows:
        if row["signal"] == "weak" and row["rho"] >= 0.6:
            v = "CONFIRMED" if row["false_consensus_rate"] > 0.15 else "REFUTED"
            print(f"  P1: weak+rho={row['rho']:.1f}: FCR={row['false_consensus_rate']:.4f} [{v}]", file=sys.stderr)
        if row["signal"] == "marginal" and row["rho"] >= 0.4:
            v = "CONFIRMED" if row["false_consensus_rate"] > 0.30 else "REFUTED"
            print(f"  P2: marginal+rho={row['rho']:.1f}: FCR={row['false_consensus_rate']:.4f} [{v}]", file=sys.stderr)

    # FCR > 10% threshold
    print(f"\nFCR > 10% occurrences (operationally significant):", file=sys.stderr)
    for row in rows:
        if row["false_consensus_rate"] > 0.10:
            print(
                f"  signal={row['signal']:8s} rho={row['rho']:.1f} => FCR={row['false_consensus_rate']:.4f}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
