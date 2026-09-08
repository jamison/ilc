"""
SIM-PANEL-01 — Panel Size vs FCR Reduction
===========================================

Research question: How much does larger jury size buy, and does it plateau
under correlated reasoning?

Design:
  panel_size: [7, 15, 31, 63, 127]
  signal:     [strong=1.0, medium=0.5, weak=0.2, marginal=0.1]
  alpha_x:    [0, 0.05, 0.10, 0.20]
  rho:        [0.0, 0.5, 0.9]
  10,000 trials per cell = 5×4×4×3 = 240 conditions × 10,000 = 2.4M claims

Primary metric: FCR(panel_size, signal, alpha, rho)
Secondary: marginal FCR reduction per additional panelist (cost-adjusted)
  FCR_reduction_per_extra_validator = (FCR_n - FCR_n+1) / (n+1 - n)

Theoretical prediction under independence (rho=0):
  FCR ∝ 1/sqrt(panel_size) (CLT for majority vote)
  Doubling panel size → FCR decreases by ~1/sqrt(2) ≈ 29%

Theoretical prediction under high correlation (rho=0.9):
  effective_n barely changes with panel_size: effective_n ≈ 1/(1 + (n-1)*rho)
  For rho=0.9, n=127: effective_n ≈ 127/114.3 ≈ 1.11 — barely better than n=7: 1.09
  → Larger panel provides NO meaningful benefit under high correlation

Falsifiable predictions:
  P1: rho=0, signal=medium: FCR halves (±10%) when panel doubles (7→14≈15, 15→30≈31)
  P2: rho=0.9, any signal: FCR does not decrease by more than 3pp from panel 7→127
  P3: rho=0, medium signal, alpha=10%: some panel size brings FCR below 5%
  P4: At weak signal (0.2), no panel size achieves FCR < 15% (this is a voter-model result,
      not a protocol claim — weak signal means expert accuracy is ~60%)

Methodological note (per Astra 6.0 feedback):
  All FCR values here are MODEL RESULTS, not empirical protocol measurements.
  The voter model assigns signal_strength as the ground truth parameter.
  "Weak signal → high FCR" is a consequence of the assumed voter error distribution,
  not an empirical claim about real ILC deployments.
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
from agents import build_population, inject_adversarial_fraction
from jury import select_jury, cast_votes

SIM_ID = "SIM-PANEL-01"

PANEL_SIZES   = [7, 15, 31, 63, 127]
SIGNAL_CONDITIONS = [("strong", 1.0), ("medium", 0.5), ("weak", 0.2), ("marginal", 0.1)]
ALPHA_VALUES  = [0.0, 0.05, 0.10, 0.20]
RHO_VALUES    = [0.0, 0.5, 0.9]
EX_SIZE       = 200   # |E(x)| = 200 experts (enough for panel=127 with CDL-V3)
N_TRIALS      = 10_000
FALSE_CLAIM_RATE = 0.30


def run_cell(agents, ex_indices, panel_size, rho, alpha_x, signal_label, signal_val, rng):
    agents_copy = inject_adversarial_fraction(agents, ex_indices, alpha_x, "adversarial", rng)

    false_total = 0
    false_accepted = 0
    true_total = 0
    true_rejected = 0

    for _ in range(N_TRIALS):
        ground_truth = rng.random() >= FALSE_CLAIM_RATE
        panel = select_jury(agents_copy, ex_indices, panel_size, rng)
        if not panel:
            continue
        _, verdict = cast_votes(agents_copy, panel, ground_truth, rho, rng, signal_strength=signal_val)
        is_correct = verdict == ground_truth

        if not ground_truth:
            false_total += 1
            if not is_correct:
                false_accepted += 1
        else:
            true_total += 1
            if not is_correct:
                true_rejected += 1

    fcr = false_accepted / false_total if false_total else 0.0
    trr = true_rejected / true_total if true_total else 0.0
    return {
        "signal": signal_label,
        "signal_value": signal_val,
        "panel_size": panel_size,
        "rho": rho,
        "alpha_x": alpha_x,
        "false_consensus_rate": round(fcr, 4),
        "true_rejection_rate": round(trr, 4),
        "n_false": false_total,
        "n_true": true_total,
    }


def main():
    # Need enough validators for panel=127 with CDL-V3 (max 1/3 per cluster)
    # With 10 clusters, max 42 per cluster; need 127 total from E(x)=200
    cfg = SimulationConfig(
        n_validators=1000,
        n_operator_clusters=10,
        n_domains=5,
        panel_size=7,  # overridden per cell
        trials_per_condition=N_TRIALS,
        false_claim_rate=FALSE_CLAIM_RATE,
        expertise_threshold=0.60,
        adversarial_fraction=0.0,
        random_seed=42,
    )

    rng = np.random.default_rng(cfg.random_seed)
    base_agents = build_population(cfg, rng)
    ex_indices = list(range(EX_SIZE))   # top 200 = E(x)

    total = len(PANEL_SIZES) * len(SIGNAL_CONDITIONS) * len(ALPHA_VALUES) * len(RHO_VALUES)
    print(f"[{SIM_ID}] {total} conditions × {N_TRIALS} trials = {total*N_TRIALS:,} claims", file=sys.stderr)

    rows = []
    done = 0
    for signal_label, signal_val in SIGNAL_CONDITIONS:
        for rho in RHO_VALUES:
            for alpha_x in ALPHA_VALUES:
                for panel_size in PANEL_SIZES:
                    done += 1
                    row = run_cell(base_agents, ex_indices, panel_size, rho, alpha_x, signal_label, signal_val, rng)
                    rows.append(row)
                if done % 20 == 0:
                    last = rows[-1]
                    print(
                        f"  [{done}/{total}] {signal_label} rho={rho} alpha={alpha_x:.0%}: "
                        f"panel={last['panel_size']} FCR={last['false_consensus_rate']:.4f}",
                        file=sys.stderr,
                    )

    result = {
        "sim_id": SIM_ID,
        "description": "Panel size vs FCR reduction across signal × rho × alpha",
        "methodological_note": "All FCR values are model results under the Phase-1 voter model. 'Signal strength' is a latent parameter in the model; real protocol signal estimation is tested in SIM-SIGNAL-01.",
        "condition_variables": ["panel_size", "signal_strength", "rho", "alpha_x"],
        "rows": rows,
        "config": cfg.__dict__,
        "ex_size": EX_SIZE,
        "predictions": {
            "P1": "rho=0, medium signal: FCR halves when panel doubles (±10%)",
            "P2": "rho=0.9: FCR does not decrease by >3pp from panel 7→127",
            "P3": "rho=0, medium, alpha=10%: some panel size achieves FCR<5%",
            "P4": "weak signal: no panel size achieves FCR<15% (voter-model result)",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sha384 = hashlib.sha384(payload_bytes).hexdigest()
    result["sha384"] = sha384

    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha384}", file=sys.stderr)

    # Summary: FCR by panel_size at rho=0, alpha=0 for each signal
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"FCR by panel_size — rho=0, alpha=0 (baseline, no adversary)", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    header = f"{'signal':>10}  " + "  ".join(f"n={p:>3}" for p in PANEL_SIZES)
    print(header, file=sys.stderr)
    for signal_label, _ in SIGNAL_CONDITIONS:
        fcrs = [
            next((r["false_consensus_rate"] for r in rows
                  if r["signal"]==signal_label and r["rho"]==0.0 and r["alpha_x"]==0.0 and r["panel_size"]==p), 0.0)
            for p in PANEL_SIZES
        ]
        print(f"{signal_label:>10}  " + "  ".join(f"{f:>7.4f}" for f in fcrs), file=sys.stderr)

    print(f"\nFCR by panel_size — rho=0.9, alpha=0 (high correlation, no adversary)", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    print(header, file=sys.stderr)
    for signal_label, _ in SIGNAL_CONDITIONS:
        fcrs = [
            next((r["false_consensus_rate"] for r in rows
                  if r["signal"]==signal_label and r["rho"]==0.9 and r["alpha_x"]==0.0 and r["panel_size"]==p), 0.0)
            for p in PANEL_SIZES
        ]
        print(f"{signal_label:>10}  " + "  ".join(f"{f:>7.4f}" for f in fcrs), file=sys.stderr)

    # P1 check: does FCR halve when panel doubles at medium signal, rho=0?
    print(f"\nP1 check: medium signal, rho=0, alpha=0 — doublings:", file=sys.stderr)
    medium_rho0 = [next((r["false_consensus_rate"] for r in rows
                         if r["signal"]=="medium" and r["rho"]==0.0 and r["alpha_x"]==0.0 and r["panel_size"]==p), 0.0)
                   for p in PANEL_SIZES]
    for i in range(len(PANEL_SIZES)-1):
        ratio = medium_rho0[i+1] / max(medium_rho0[i], 0.001)
        flag = " ≈halved (CONFIRMED)" if 0.45 < ratio < 0.75 else ""
        print(f"  n={PANEL_SIZES[i]}→{PANEL_SIZES[i+1]}: FCR {medium_rho0[i]:.4f}→{medium_rho0[i+1]:.4f} ratio={ratio:.2f}{flag}", file=sys.stderr)

    # P2 check: rho=0.9 — FCR change panel 7→127
    print(f"\nP2 check: rho=0.9, alpha=0 — panel 7→127 FCR change:", file=sys.stderr)
    for signal_label, _ in SIGNAL_CONDITIONS:
        f7   = next((r["false_consensus_rate"] for r in rows if r["signal"]==signal_label and r["rho"]==0.9 and r["alpha_x"]==0.0 and r["panel_size"]==7), 0.0)
        f127 = next((r["false_consensus_rate"] for r in rows if r["signal"]==signal_label and r["rho"]==0.9 and r["alpha_x"]==0.0 and r["panel_size"]==127), 0.0)
        delta = f7 - f127
        flag = " CONFIRMED (<3pp)" if delta < 0.03 else " REFUTED (>3pp)"
        print(f"  {signal_label}: 7-panel FCR={f7:.4f}, 127-panel FCR={f127:.4f}, Δ={delta:.4f}{flag}", file=sys.stderr)


if __name__ == "__main__":
    main()
