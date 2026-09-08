"""
SIM-LAUNDER-02G — Factorial IEC × Refutation × Context
=======================================================

Tests whether the epistemic dimensions (I, R, K) are orthogonal or interact.
The key question: does high IEC × high refutation_resistance produce qualitatively
better epistemic standing than either alone? Or is the benefit purely additive?

If the dimensions interact, the right epistemic model is conjunctive (high I AND high R
produce something qualitatively different). If they are additive, a weighted scalar
sum would suffice.

Factorial design: 4 IEC levels × 2 R levels × 2 K levels = 16 conditions
  IEC ∈ {1, 5, 10, 20}          — independent evidence origins
  R_mode ∈ {low, high}          — p_survive = {0.25, 0.85}
  K_mode ∈ {absent, present}    — context structure {no, yes}

200 runs per condition = 3,200 total simulations.

Metrics per condition:
  ELF      = mean_rrw / mean_iec   (laundering factor — lower is better)
  IEC      = mean distinct surviving origins
  RRW      = mean descendant count
  R_surv   = mean fraction surviving refutation
  Popperian_weight = mean (iec + survived_refutations × 0.5)
  K_sep    = mean context separation score

Predictions:
  P1: ELF decreases monotonically with IEC level (more origins = less laundering)
  P2: ELF is unaffected by R_mode (refutation resistance doesn't change laundering)
  P3: Popperian_weight increases with both IEC and R (partial additivity expected)
  P4: High IEC + High R produces HIGHER popperian_weight than either alone,
      and the joint gain exceeds the sum of individual gains (interaction)
  P5: K_mode does not affect IEC or ELF (K is orthogonal to I at the graph level)
  P6: At low IEC, ELF remains high regardless of R or K (I is the binding constraint)

Key architectural question: if P4 is confirmed (superadditive interaction), a scalar
score cannot capture epistemic quality — the profile must remain multidimensional.
If P4 is refuted (purely additive), a weighted sum might suffice.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
import math
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SIM_ID   = "SIM-LAUNDER-02G"
N_EPOCHS = 60
N_RUNS   = 200

IEC_LEVELS   = [1, 5, 10, 20]      # number of independent origins
R_MODES      = ["low", "high"]     # p_survive = 0.25 vs 0.85
K_MODES      = ["absent", "present"]

R_PARAMS     = {"low": 0.25, "high": 0.85}
P_CITE       = 0.08     # standard citation rate
P_REFUTE     = 0.02     # standard refutation rate


@dataclass
class GNode:
    node_id: int
    origin_id: int
    context_id: int
    refuted: bool = False


def simulate_condition(
    n_origins: int,
    p_survive: float,
    has_context: bool,
    n_epochs: int,
    rng: np.random.Generator,
) -> dict:
    """
    Returns per-run metrics for one (IEC, R, K) condition.
    """
    # Build origin nodes
    nodes: List[GNode] = []
    refutation_attempts = 0
    refutation_survived = 0

    for i in range(n_origins):
        ctx = ((i % 2) + 1) if has_context else 0  # alternating C1/C2 or all C0
        nodes.append(GNode(len(nodes), i, ctx))

    next_id = n_origins

    for _ in range(n_epochs):
        alive = [n for n in nodes if not n.refuted]
        if not alive:
            break

        # Citation phase
        for node in list(alive):
            if rng.random() < P_CITE:
                child = GNode(next_id, node.origin_id, node.context_id)
                nodes.append(child)
                next_id += 1

        # Refutation phase
        for node in nodes:
            if node.refuted:
                continue
            if rng.random() < P_REFUTE:
                refutation_attempts += 1
                if rng.random() < p_survive:
                    refutation_survived += 1  # survived challenge
                else:
                    node.refuted = True

    # ── Metrics ──────────────────────────────────────────────────────────────

    origin_counts: Dict[int, int] = {}
    for node in nodes:
        if not node.refuted:
            origin_counts[node.origin_id] = origin_counts.get(node.origin_id, 0) + 1

    mean_rrw = (sum(origin_counts.values()) / len(origin_counts)
                if origin_counts else 0.0)
    iec_actual = len(origin_counts)
    elf = mean_rrw / max(1, iec_actual)

    total_nodes = len(nodes)
    alive_count = sum(1 for n in nodes if not n.refuted)
    r_surv = alive_count / total_nodes if total_nodes > 0 else 0.0

    # Popperian weight: IEC + 0.5 × survived refutations per surviving origin
    popperian_weight = iec_actual + refutation_survived * 0.5

    # K_sep: context separation
    ctx_counts: Dict[int, int] = {}
    for node in nodes:
        if not node.refuted:
            ctx_counts[node.context_id] = ctx_counts.get(node.context_id, 0) + 1

    if 0 in ctx_counts or len(ctx_counts) < 2:
        k_sep = 0.0
    else:
        total_alive = sum(ctx_counts.values())
        fracs = [ctx_counts[c] / total_alive for c in sorted(ctx_counts.keys())]
        k_sep = abs(fracs[0] - fracs[1]) if len(fracs) >= 2 else 0.0

    return {
        "mean_rrw": mean_rrw,
        "iec_actual": iec_actual,
        "elf": elf,
        "r_surv": r_surv,
        "popperian_weight": popperian_weight,
        "k_sep": k_sep,
        "refutation_attempts": refutation_attempts,
        "refutation_survived": refutation_survived,
    }


def condition_key(n_origins: int, r_mode: str, k_mode: str) -> str:
    return f"IEC{n_origins:02d}_{r_mode}R_{k_mode}K"


def main() -> None:
    rng = np.random.default_rng(42)
    n_conds = len(IEC_LEVELS) * len(R_MODES) * len(K_MODES)
    print(f"[{SIM_ID}] {n_conds} conditions × {N_RUNS} runs = {n_conds*N_RUNS} simulations",
          file=sys.stderr)

    results: dict = {}

    for n_orig in IEC_LEVELS:
        for r_mode in R_MODES:
            for k_mode in K_MODES:
                p_surv = R_PARAMS[r_mode]
                has_ctx = (k_mode == "present")
                key = condition_key(n_orig, r_mode, k_mode)

                elf_list, iec_list, rrw_list, rsurv_list, pp_list, ksep_list = (
                    [], [], [], [], [], []
                )

                for _ in range(N_RUNS):
                    m = simulate_condition(n_orig, p_surv, has_ctx, N_EPOCHS, rng)
                    elf_list.append(m["elf"])
                    iec_list.append(m["iec_actual"])
                    rrw_list.append(m["mean_rrw"])
                    rsurv_list.append(m["r_surv"])
                    pp_list.append(m["popperian_weight"])
                    ksep_list.append(m["k_sep"])

                results[key] = {
                    "n_origins": n_orig,
                    "r_mode": r_mode,
                    "k_mode": k_mode,
                    "p_survive": p_surv,
                    "mean_elf": round(float(np.mean(elf_list)), 4),
                    "mean_iec": round(float(np.mean(iec_list)), 3),
                    "mean_rrw": round(float(np.mean(rrw_list)), 3),
                    "mean_r_surv": round(float(np.mean(rsurv_list)), 4),
                    "mean_popperian_weight": round(float(np.mean(pp_list)), 3),
                    "mean_k_sep": round(float(np.mean(ksep_list)), 4),
                }

    # ── Summary tables ────────────────────────────────────────────────────────
    print(f"\nELF by IEC × R (K=absent):", file=sys.stderr)
    print(f"{'IEC':>5} {'R=low ELF':>12} {'R=high ELF':>12} {'diff':>8}", file=sys.stderr)
    for n_orig in IEC_LEVELS:
        klo = results[condition_key(n_orig, "low",  "absent")]
        khi = results[condition_key(n_orig, "high", "absent")]
        diff = khi["mean_elf"] - klo["mean_elf"]
        print(f"  {n_orig:3d}  {klo['mean_elf']:12.4f} {khi['mean_elf']:12.4f} {diff:8.4f}",
              file=sys.stderr)

    print(f"\nPopperian weight by IEC × R (K=absent):", file=sys.stderr)
    print(f"{'IEC':>5} {'R=low PP':>10} {'R=high PP':>11} {'gain':>7}", file=sys.stderr)
    for n_orig in IEC_LEVELS:
        rlo = results[condition_key(n_orig, "low",  "absent")]
        rhi = results[condition_key(n_orig, "high", "absent")]
        gain = rhi["mean_popperian_weight"] - rlo["mean_popperian_weight"]
        print(f"  {n_orig:3d}  {rlo['mean_popperian_weight']:10.3f} "
              f"{rhi['mean_popperian_weight']:11.3f} {gain:7.3f}", file=sys.stderr)

    print(f"\nPopperian weight by IEC (R=high, K=absent):", file=sys.stderr)
    pp_vals = [results[condition_key(n_orig, "high", "absent")]["mean_popperian_weight"]
               for n_orig in IEC_LEVELS]
    for n_orig, pp in zip(IEC_LEVELS, pp_vals):
        print(f"  IEC={n_orig:2d}: {pp:.3f}", file=sys.stderr)

    # ── Interaction test (P4) ─────────────────────────────────────────────────
    # Compare: gain from high R at low IEC vs gain from high R at high IEC
    # If superadditive: gain_highIEC > gain_lowIEC substantially
    def r_gain(n_orig: int, k_mode: str) -> float:
        lo = results[condition_key(n_orig, "low", k_mode)]["mean_popperian_weight"]
        hi = results[condition_key(n_orig, "high", k_mode)]["mean_popperian_weight"]
        return hi - lo

    gain_iec1  = r_gain(1,  "absent")
    gain_iec20 = r_gain(20, "absent")
    interaction = gain_iec20 - gain_iec1

    print(f"\nInteraction test (P4):", file=sys.stderr)
    print(f"  R-gain at IEC=1:  {gain_iec1:.3f}", file=sys.stderr)
    print(f"  R-gain at IEC=20: {gain_iec20:.3f}", file=sys.stderr)
    print(f"  Interaction (gain_IEC20 - gain_IEC1): {interaction:.3f}", file=sys.stderr)

    # ── Prediction verdicts ───────────────────────────────────────────────────
    # P1: ELF decreases with IEC
    elf_vals_low_r = [results[condition_key(n, "low", "absent")]["mean_elf"]
                      for n in IEC_LEVELS]
    p1_v = "CONFIRMED" if all(elf_vals_low_r[i] > elf_vals_low_r[i+1]
                              for i in range(len(elf_vals_low_r)-1)) else "REFUTED"
    print(f"\nP1 ELF monotone with IEC (R=low): "
          f"{[round(e,3) for e in elf_vals_low_r]} [{p1_v}]", file=sys.stderr)

    # P2: ELF unaffected by R at same IEC
    elf_diffs_by_r = [
        abs(results[condition_key(n, "low", "absent")]["mean_elf"] -
            results[condition_key(n, "high", "absent")]["mean_elf"])
        for n in IEC_LEVELS
    ]
    max_elf_diff = max(elf_diffs_by_r)
    p2_v = "CONFIRMED" if max_elf_diff < 0.30 else "REFUTED"
    print(f"P2 ELF unaffected by R: max_diff={max_elf_diff:.4f} [{p2_v}]",
          file=sys.stderr)

    # P3: Popperian increases with IEC (at high R)
    pp_high_r = [results[condition_key(n, "high", "absent")]["mean_popperian_weight"]
                 for n in IEC_LEVELS]
    p3_v = "CONFIRMED" if all(pp_high_r[i] < pp_high_r[i+1]
                              for i in range(len(pp_high_r)-1)) else "REFUTED"
    print(f"P3 Popperian monotone with IEC (R=high): "
          f"{[round(p,2) for p in pp_high_r]} [{p3_v}]", file=sys.stderr)

    # P4: Superadditive interaction: gain from R at high IEC > gain at low IEC
    p4_v = "CONFIRMED" if interaction > 1.0 else "REFUTED"
    print(f"P4 Superadditive interaction={interaction:.3f} > 1.0 [{p4_v}]",
          file=sys.stderr)

    # P5: K_mode doesn't affect IEC or ELF
    k_diffs_iec = [
        abs(results[condition_key(n, "low", "absent")]["mean_iec"] -
            results[condition_key(n, "low", "present")]["mean_iec"])
        for n in IEC_LEVELS
    ]
    max_k_diff_iec = max(k_diffs_iec)
    p5_v = "CONFIRMED" if max_k_diff_iec < 1.0 else "REFUTED"
    print(f"P5 K_mode effect on IEC: max_diff={max_k_diff_iec:.4f} [{p5_v}]",
          file=sys.stderr)

    # P6: At IEC=1, ELF remains high regardless of R or K
    elf_iec1_variants = [
        results[condition_key(1, r, k)]["mean_elf"]
        for r in R_MODES for k in K_MODES
    ]
    min_elf_iec1 = min(elf_iec1_variants)
    p6_v = "CONFIRMED" if min_elf_iec1 > 2.0 else "REFUTED"
    print(f"P6 ELF at IEC=1 min={min_elf_iec1:.4f} > 2.0 [{p6_v}]",
          file=sys.stderr)

    result_out = {
        "sim_id": SIM_ID,
        "description": "Factorial IEC × R × K: orthogonality and interaction effects",
        "design": {
            "iec_levels": IEC_LEVELS,
            "r_modes": R_MODES,
            "k_modes": K_MODES,
            "n_runs_per_condition": N_RUNS,
            "n_epochs": N_EPOCHS,
        },
        "conditions": results,
        "interaction_analysis": {
            "r_gain_at_iec1":  round(gain_iec1, 3),
            "r_gain_at_iec20": round(gain_iec20, 3),
            "interaction_term": round(interaction, 3),
            "interpretation": (
                "superadditive" if interaction > 1.0
                else "additive-or-subadditive"
            ),
        },
        "predictions": {
            "P1": "ELF decreases monotonically with IEC level",
            "P2": "ELF unaffected by R mode (max diff < 0.30)",
            "P3": "Popperian weight increases monotonically with IEC at R=high",
            "P4": "Superadditive: R-gain at IEC=20 > R-gain at IEC=1 (>1.0)",
            "P5": "K mode does not affect IEC (orthogonal; max diff < 1.0)",
            "P6": "ELF at IEC=1 stays high (> 2.0) regardless of R or K",
        },
        "prediction_verdicts": {
            "P1": p1_v, "P2": p2_v, "P3": p3_v,
            "P4": p4_v, "P5": p5_v, "P6": p6_v,
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload = json.dumps(result_out, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha384(payload).hexdigest()
    result_out["sha384"] = sha
    print(json.dumps(result_out, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha}", file=sys.stderr)


if __name__ == "__main__":
    main()
