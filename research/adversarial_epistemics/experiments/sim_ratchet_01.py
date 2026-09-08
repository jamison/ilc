"""
SIM-RATCHET-01 — Combined: Signal × Correlation × Cartel
==========================================================

The key unmeasured interaction from SIM-CORR-01 and SIM-CARTEL-01:
What happens when BOTH correlation (rho) and adversarial presence (alpha_x)
are nonzero simultaneously?

The reviewer's hypothesis:
  A small adversarial bias (10-20% of E(x)) pushing a correlated honest
  jury (rho=0.6-0.8) on a weak-signal claim may only need 1-2 well-placed
  votes to push the correlated honest bloc over the threshold.

This produces the epistemic lock-in chain:
  small adversarial bias
    → weak-signal claim
    → correlated jury
    → slightly elevated FCR
    → false ratification
    → graph reuse (amplified downstream)

Design:
  rho:      [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]
  alpha_x:  [0.0, 0.05, 0.10, 0.20, 0.30, 0.40]
  signal:   [strong=1.0, medium=0.5, weak=0.2, marginal=0.1]
  |E(x)|:   fixed at 10% of N (100 validators)
  panel:    7 (DEFAULT_PANEL_SIZE), CDL-V3 enforced
  trials:   10,000 per cell

Total: 6 × 6 × 4 = 144 conditions × 10,000 = 1.44 million simulated claims.

Key metric: FCR_ratchet(rho, alpha_x, signal) — the joint effect.

Comparison baseline: FCR_additive = FCR_corr(rho, signal) + FCR_cartel(alpha_x, signal)
                     FCR_multiplicative = FCR_corr × (1 + alpha_x × amplification)

If FCR_ratchet >> FCR_additive, the effects superlinearly compound.
That is the finding that would indicate a genuine architectural problem.

Falsifiable predictions:
  SIM-RATCHET-01-P1: At weak signal (0.2), rho=0.6, alpha_x=20%:
    FCR > 30% (both threats compound superlinearly beyond their individual sum).
  SIM-RATCHET-01-P2: At medium signal (0.5), strong CDL-V3 (alpha_x <= 10%),
    rho <= 0.4: FCR remains below 10% (within acceptable range).
  SIM-RATCHET-01-P3: There exists a dangerous region where small increases in
    either rho OR alpha_x cause nonlinear FCR jumps (interaction term dominates).
  SIM-RATCHET-01-P4: At marginal signal (0.1), even alpha_x=5% + rho=0.4
    produces FCR > 25%.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
from datetime import datetime, timezone
from typing import List

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import SimulationConfig
from agents import build_population, inject_adversarial_fraction
from jury import select_jury, cast_votes

SIM_ID = "SIM-RATCHET-01"

RHO_VALUES    = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]
ALPHA_X_VALUES = [0.0, 0.05, 0.10, 0.20, 0.30, 0.40]
SIGNAL_CONDITIONS = [
    ("strong",   1.0),
    ("medium",   0.5),
    ("weak",     0.2),
    ("marginal", 0.1),
]
EX_SIZE_FRACTION = 0.10   # |E(x)| = 10% of N = 100 validators
N_TRIALS = 10_000
FALSE_CLAIM_RATE = 0.30


def run_cell(base_agents, ex_indices, panel_size, rho, alpha_x, signal_label, signal_val, rng):
    # Fresh agent list with adversarial injection for this condition
    agents = inject_adversarial_fraction(base_agents, ex_indices, alpha_x, "adversarial", rng)

    correct = 0
    false_total = 0
    false_accepted = 0
    true_total = 0
    true_rejected = 0

    for _ in range(N_TRIALS):
        ground_truth = rng.random() >= FALSE_CLAIM_RATE
        panel = select_jury(agents, ex_indices, panel_size, rng)
        if not panel:
            continue

        _, verdict = cast_votes(agents, panel, ground_truth, rho, rng, signal_strength=signal_val)
        is_correct = verdict == ground_truth

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
        "alpha_x": alpha_x,
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
    base_agents = build_population(cfg, rng)

    n_ex = int(cfg.n_validators * EX_SIZE_FRACTION)
    ex_indices = list(range(n_ex))

    total_cells = len(SIGNAL_CONDITIONS) * len(RHO_VALUES) * len(ALPHA_X_VALUES)
    print(f"[{SIM_ID}] Starting — {total_cells} conditions × {N_TRIALS} trials = {total_cells * N_TRIALS:,} simulated claims", file=sys.stderr)
    print(f"[{SIM_ID}] |E(x)|={n_ex} ({EX_SIZE_FRACTION:.0%}), panel_size={cfg.panel_size}", file=sys.stderr)

    rows = []
    cell_num = 0
    for signal_label, signal_val in SIGNAL_CONDITIONS:
        for rho in RHO_VALUES:
            for alpha_x in ALPHA_X_VALUES:
                cell_num += 1
                row = run_cell(base_agents, ex_indices, cfg.panel_size, rho, alpha_x, signal_label, signal_val, rng)
                rows.append(row)
                if cell_num % 12 == 0 or (row["false_consensus_rate"] > 0.15):
                    print(
                        f"  [{cell_num:3d}/{total_cells}] signal={signal_label:8s} rho={rho:.1f} alpha={alpha_x:.0%} | "
                        f"FCR={row['false_consensus_rate']:.4f} acc={row['jury_accuracy']:.4f}",
                        file=sys.stderr,
                    )

    result = {
        "sim_id": SIM_ID,
        "description": "3D FCR surface: signal × rho × alpha_x (combined correlation + cartel)",
        "condition_variables": ["signal_strength", "rho", "alpha_x"],
        "rows": rows,
        "config": cfg.__dict__,
        "ex_size_fraction": EX_SIZE_FRACTION,
        "predictions": {
            "SIM-RATCHET-01-P1": "weak(0.2)+rho=0.6+alpha=20% => FCR > 30%",
            "SIM-RATCHET-01-P2": "medium(0.5)+alpha<=10%+rho<=0.4 => FCR < 10%",
            "SIM-RATCHET-01-P3": "dangerous nonlinear region exists where small delta_rho or delta_alpha causes FCR to double",
            "SIM-RATCHET-01-P4": "marginal(0.1)+rho=0.4+alpha=5% => FCR > 25%",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sha384 = hashlib.sha384(payload_bytes).hexdigest()
    result["sha384"] = sha384

    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha384}", file=sys.stderr)

    # FCR heatmap by signal level
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"SIM-RATCHET-01 — FCR heatmap (dangerous cells marked **)", file=sys.stderr)

    for signal_label, signal_val in SIGNAL_CONDITIONS:
        print(f"\n  Signal={signal_label} ({signal_val}):", file=sys.stderr)
        header = f"    {'alpha\\rho':>10} " + " ".join(f"{r:>8.1f}" for r in RHO_VALUES)
        print(header, file=sys.stderr)
        for alpha_x in ALPHA_X_VALUES:
            fcrs = []
            for rho in RHO_VALUES:
                match = next((r for r in rows if r["signal"]==signal_label and r["rho"]==rho and abs(r["alpha_x"]-alpha_x)<0.001), None)
                fcrs.append(match["false_consensus_rate"] if match else 0.0)
            flags = ["**" if f > 0.15 else "  " for f in fcrs]
            row_str = f"    {alpha_x:>9.0%}  " + " ".join(f"{f:>6.4f}{flag}" for f, flag in zip(fcrs, flags))
            print(row_str, file=sys.stderr)

    # Check for superlinear compounding
    print(f"\nSuperlinearity check (FCR_joint vs FCR_additive):", file=sys.stderr)
    for signal_label, signal_val in SIGNAL_CONDITIONS:
        baseline_corr = {r["rho"]: r["false_consensus_rate"] for r in rows if r["signal"]==signal_label and r["alpha_x"]==0.0}
        baseline_cartel = {r["alpha_x"]: r["false_consensus_rate"] for r in rows if r["signal"]==signal_label and r["rho"]==0.0}
        baseline_both_zero = next((r["false_consensus_rate"] for r in rows if r["signal"]==signal_label and r["rho"]==0.0 and r["alpha_x"]==0.0), 0.0)
        print(f"\n  {signal_label}:", file=sys.stderr)
        for rho in [0.6, 0.8]:
            for alpha_x in [0.10, 0.20]:
                joint = next((r["false_consensus_rate"] for r in rows if r["signal"]==signal_label and r["rho"]==rho and abs(r["alpha_x"]-alpha_x)<0.001), None)
                if joint is None:
                    continue
                additive = baseline_corr.get(rho, 0) + baseline_cartel.get(alpha_x, 0) - baseline_both_zero
                ratio = joint / max(additive, 0.001)
                flag = " <-- SUPERLINEAR" if ratio > 1.5 else ""
                print(f"    rho={rho:.1f} alpha={alpha_x:.0%}: joint={joint:.4f} additive={additive:.4f} ratio={ratio:.2f}x{flag}", file=sys.stderr)

    # Prediction verdicts
    print(f"\nPrediction verdicts:", file=sys.stderr)
    p1 = next((r for r in rows if r["signal"]=="weak" and r["rho"]==0.6 and abs(r["alpha_x"]-0.20)<0.001), None)
    if p1:
        v = "CONFIRMED" if p1["false_consensus_rate"] > 0.30 else "REFUTED"
        print(f"  P1 (weak+rho=0.6+alpha=20%): FCR={p1['false_consensus_rate']:.4f} [{v}]", file=sys.stderr)

    p4 = next((r for r in rows if r["signal"]=="marginal" and r["rho"]==0.4 and abs(r["alpha_x"]-0.05)<0.001), None)
    if p4:
        v = "CONFIRMED" if p4["false_consensus_rate"] > 0.25 else "REFUTED"
        print(f"  P4 (marginal+rho=0.4+alpha=5%): FCR={p4['false_consensus_rate']:.4f} [{v}]", file=sys.stderr)

    p2_cells = [r for r in rows if r["signal"]=="medium" and r["alpha_x"]<=0.10 and r["rho"]<=0.4]
    p2_max = max((r["false_consensus_rate"] for r in p2_cells), default=0)
    v = "CONFIRMED" if p2_max < 0.10 else "REFUTED"
    print(f"  P2 (medium+alpha<=10%+rho<=0.4): max FCR={p2_max:.4f} [{v}]", file=sys.stderr)


if __name__ == "__main__":
    main()
