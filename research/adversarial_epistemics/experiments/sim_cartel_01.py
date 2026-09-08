"""
SIM-CARTEL-01 — Epistemic Minority Capture (Domain Cartel)
===========================================================

Research question:
  At what fraction alpha(x) of E(x) (the relevant-expertise population)
  can an adversarial cartel achieve reliable control of jury verdicts,
  as a function of E(x) size and CDL-V3 diversity constraints?

Critical insight being tested:
  The adversary does NOT need to control alpha(N) — a plurality of the
  full network. They only need to control alpha(E(x)) — a plurality of
  validators with EXPERTISE in domain x. If |E(x)| << N, alpha(x) can
  be large even when the attacker controls a negligible fraction of N.

Independent variables:
  - alpha_x: adversarial fraction of E(x), in [0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
  - ex_size_fraction: size of E(x) as fraction of N, in [0.05, 0.10, 0.20]

Controlled:
  - N = 1000 validators
  - rho = 0.0 (honest validators fully independent — isolates cartel effect)
  - Panel size = 7
  - CDL-V3: max 1/3 per operator cluster on panel
  - False claim rate = 1.0 (measuring cartel ability to pass false claims)

Metrics:
  - cartel_success_rate: fraction of false claims incorrectly ratified
  - cartel_representation_rate: mean fraction of cartel members on panel
  - effective_n_in_ex: |E(x)| / N (how concentrated is the expertise)
  - alpha_n_equivalent: alpha_x * |E(x)| / N (global adversarial fraction)

Falsifiable predictions:
  SIM-CARTEL-01-P1: With |E(x)| = 5% of N, alpha(x) = 20% is sufficient
    for cartel success rate > 0.50, even when alpha(N) = 1%.
  SIM-CARTEL-01-P2: CDL-V3 (max 1/3 per cluster) provides limited defense
    when cartel spans multiple operator clusters.
  SIM-CARTEL-01-P3: With |E(x)| = 20% of N, alpha(x) must exceed 40%
    for reliable cartel control (cartel success rate > 0.70).

Output: JSON to stdout, SHA-384 fingerprint for graph intake.
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
from agents import build_population, inject_adversarial_fraction, Agent
from jury import select_jury, cast_votes
from metrics import false_consensus_rate, gini_coefficient

ALPHA_X_VALUES = [0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
EX_SIZE_FRACTIONS = [0.05, 0.10, 0.20]
SIM_ID = "SIM-CARTEL-01"

# For cartel SIM: all claims are false (stress test cartel's ability to pass them)
N_TRIALS = 10_000


def run_cartel_condition(
    base_agents: List[Agent],
    ex_size_fraction: float,
    alpha_x: float,
    panel_size: int,
    cfg: SimulationConfig,
    rng: np.random.Generator,
) -> dict:
    """Run N_TRIALS for a single (ex_size_fraction, alpha_x) condition."""
    # E(x): use the first domain only, with explicit size control
    # Instead of relying on Beta-distributed expertise, we directly assign
    # a fixed-size E(x) for clean experimental control.
    n_ex = max(MIN_EXPERTS, int(cfg.n_validators * ex_size_fraction))
    eligible_indices = list(range(n_ex))  # top n_ex validators are "experts" for this domain

    # Inject adversarial agents into E(x)
    agents = inject_adversarial_fraction(
        base_agents, eligible_indices, alpha_x, "adversarial", rng
    )

    n_adversarial_in_ex = sum(1 for i in eligible_indices if agents[i].strategy == "adversarial")
    alpha_n_global = n_adversarial_in_ex / cfg.n_validators

    ground_truth = False   # all claims are false — measuring cartel's success in passing them

    cartel_successes = 0
    panel_cartel_fractions = []

    for _ in range(N_TRIALS):
        panel = select_jury(agents, eligible_indices, panel_size, rng)
        if not panel:
            continue

        # Record cartel fraction on panel
        n_cartel_on_panel = sum(1 for idx in panel if agents[idx].strategy == "adversarial")
        panel_cartel_fractions.append(n_cartel_on_panel / len(panel))

        _, verdict = cast_votes(agents, panel, ground_truth, rho=0.0, rng=rng)
        if verdict:  # cartel succeeded in passing the false claim
            cartel_successes += 1

    cartel_success_rt = cartel_successes / N_TRIALS
    mean_panel_cartel = sum(panel_cartel_fractions) / len(panel_cartel_fractions) if panel_cartel_fractions else 0.0

    return {
        "ex_size_fraction": ex_size_fraction,
        "ex_size_n": n_ex,
        "alpha_x": alpha_x,
        "alpha_n_global": round(alpha_n_global, 5),
        "n_adversarial_in_ex": n_adversarial_in_ex,
        "cartel_success_rate": round(cartel_success_rt, 4),
        "mean_cartel_fraction_on_panel": round(mean_panel_cartel, 4),
        "n_trials": N_TRIALS,
    }


MIN_EXPERTS = 5  # degenerate if fewer than this


def main():
    cfg = SimulationConfig(
        n_validators=1000,
        n_operator_clusters=10,
        n_domains=5,
        panel_size=7,
        trials_per_condition=N_TRIALS,
        false_claim_rate=1.0,
        expertise_threshold=0.60,
        adversarial_fraction=0.0,
        random_seed=42,
    )

    rng = np.random.default_rng(cfg.random_seed)
    base_agents = build_population(cfg, rng)

    print(f"[{SIM_ID}] Starting — N={cfg.n_validators}, panel_size={cfg.panel_size}", file=sys.stderr)
    print(f"[{SIM_ID}] {len(EX_SIZE_FRACTIONS)} x {len(ALPHA_X_VALUES)} = {len(EX_SIZE_FRACTIONS)*len(ALPHA_X_VALUES)} conditions", file=sys.stderr)

    rows = []
    for ex_frac in EX_SIZE_FRACTIONS:
        for alpha_x in ALPHA_X_VALUES:
            row = run_cartel_condition(base_agents, ex_frac, alpha_x, cfg.panel_size, cfg, rng)
            rows.append(row)
            print(
                f"  |E(x)|={ex_frac:.0%} | alpha(x)={alpha_x:.0%} | "
                f"alpha(N)={row['alpha_n_global']:.4%} | "
                f"cartel_success={row['cartel_success_rate']:.4f} | "
                f"panel_cartel={row['mean_cartel_fraction_on_panel']:.3f}",
                file=sys.stderr,
            )

    result = {
        "sim_id": SIM_ID,
        "description": "Epistemic minority capture: domain cartel vs CDL-V3",
        "condition_variables": ["ex_size_fraction", "alpha_x"],
        "rows": rows,
        "config": cfg.__dict__,
        "predictions": {
            "SIM-CARTEL-01-P1": "|E(x)|=5%, alpha(x)=20% => cartel_success > 0.50 even with alpha(N)=1%",
            "SIM-CARTEL-01-P2": "CDL-V3 (max 1/3 per cluster) provides limited defense when cartel spans multiple clusters",
            "SIM-CARTEL-01-P3": "|E(x)|=20%, alpha(x) must exceed 40% for cartel_success > 0.70",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sha384 = hashlib.sha384(payload_bytes).hexdigest()
    result["sha384"] = sha384

    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha384}", file=sys.stderr)

    # Readable summary by E(x) size
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"SIM-CARTEL-01 RESULTS — Cartel success rate by alpha(x) and |E(x)|", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)

    for ex_frac in EX_SIZE_FRACTIONS:
        print(f"\n  |E(x)| = {ex_frac:.0%} of N (= {int(cfg.n_validators * ex_frac)} validators):", file=sys.stderr)
        print(f"  {'alpha(x)':>10} {'alpha(N)':>10} {'success':>10} {'panel%':>8}", file=sys.stderr)
        for row in rows:
            if row["ex_size_fraction"] == ex_frac:
                print(
                    f"  {row['alpha_x']:>10.0%} {row['alpha_n_global']:>10.4%} "
                    f"{row['cartel_success_rate']:>10.4f} {row['mean_cartel_fraction_on_panel']:>8.3f}",
                    file=sys.stderr,
                )

    # Prediction verification
    print(f"\nPrediction verification:", file=sys.stderr)
    p1_rows = [r for r in rows if r["ex_size_fraction"] == 0.05 and abs(r["alpha_x"] - 0.20) < 0.001]
    if p1_rows:
        r = p1_rows[0]
        v = "CONFIRMED" if r["cartel_success_rate"] > 0.50 else "REFUTED"
        print(f"  P1: |E(x)|=5%, alpha(x)=20% => success={r['cartel_success_rate']:.4f} [{v}]", file=sys.stderr)

    p3_rows = [r for r in rows if r["ex_size_fraction"] == 0.20 and abs(r["alpha_x"] - 0.40) < 0.001]
    if p3_rows:
        r = p3_rows[0]
        v = "CONFIRMED" if r["cartel_success_rate"] > 0.70 else "REFUTED"
        print(f"  P3: |E(x)|=20%, alpha(x)=40% => success={r['cartel_success_rate']:.4f} [{v}]", file=sys.stderr)


if __name__ == "__main__":
    main()
