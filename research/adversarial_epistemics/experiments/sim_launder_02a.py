"""
SIM-LAUNDER-02A — Provenance Stress Test: ELF Across Refutation Rates
======================================================================

LAUNDER-01 confirmed: raw_reuse_weight ranks pure propagation (B) ≈ genuine
corroboration (A). This experiment quantifies the Epistemic Laundering Factor (ELF)
across a refutation rate sweep and extends to 8 claim populations.

Key metric introduced:
  ELF(x) = raw_reuse_weight / max(1, independent_evidence_count)
  ELF ≈ 1.0 → reuse weight tracks evidence (calibrated)
  ELF >> 1.0 → reuse weight far exceeds evidence (laundering detected)

  Also: Propagation Ratio PR(x) = descendant_count / independent_roots
         Laundering Gain LG = ELF(propagation) / ELF(corroboration)
         → If LG >> 1.0: the metric launders propagation into apparent evidence.

Eight populations (from Astra 6.0 design):
  A — objective true,  10 indep roots, low reuse,    normal refutation
  B — objective true,   1 root,        high reuse,   normal refutation
  C — objective false,  1 root,        high reuse,   suppressed refutation (cartel)
  D — objective true,   3 roots,       high reuse,   normal refutation
  E — contextual,       2+ roots,      high reuse,   context-split observations
  F — contested true,  20 roots,       medium reuse, high refutation attempts (17/20 fail)
  G — subjective,      N/A,            high reuse,   legitimate disagreement
  H — underspecified,   2 contexts,    high reuse,   conflicting observations

Refutation rate sweep: [0.005, 0.01, 0.035, 0.10]
Reuse rate (P_CITE):   [0.03, 0.08, 0.15]
N_EPOCHS = 60, N_RUNS = 300

Primary falsifiable prediction:
  P1: ELF(B_propagation) >> ELF(A_corroboration) at all refutation rates —
      the laundering gap widens as refutation rate decreases.
  P2: At low refutation rate (0.5%/epoch), LG > 5.0 — propagation earns 5×
      more standing-per-evidence than genuine corroboration.
  P3: IEW-based ranking (A > D > B > C) is stable across all refutation rates.
  P4: Population F (contested true, high refutation) has higher epistemic standing
      under IEW than B (pure propagation, low refutation) despite lower raw reuse.

Methodological note: All results are consequences of the graph simulation model.
  ELF, IEW, and IEC are research proposals, not current ILC metrics.
  raw_reuse_weight is the current implemented metric.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SIM_ID = "SIM-LAUNDER-02A"
N_EPOCHS = 60
N_RUNS = 300
P_CITE_DEFAULT = 0.08
CARTEL_PROTECTION = 0.70
POPPERIAN_REFUTE_BONUS = 0.60  # fraction of refutation attempts that fail (contested claim hardiness)


@dataclass
class Obs:
    """A single observation in the graph."""
    oid: int
    is_true: bool
    is_root: bool
    independent_origin: int   # which independent evidence source (0..n_origins-1)
    context_id: int           # 0 = no context; 1,2,... = distinct contexts
    cited: List[int] = field(default_factory=list)    # edges out (parents)
    cited_by: List[int] = field(default_factory=list) # edges in (children)
    refuted: bool = False
    refutation_count: int = 0  # number of refutation attempts received
    failed_refutations: int = 0  # attempts that were repelled (Popperian hardness)


def raw_reuse_weight(oid: int, obs: Dict[int, Obs]) -> float:
    visited, frontier = set(), [oid]
    while frontier:
        n = frontier.pop()
        for c in obs[n].cited_by:
            if c not in visited:
                visited.add(c)
                frontier.append(c)
    return float(len(visited))


def independent_evidence_count(oid: int, obs: Dict[int, Obs]) -> int:
    visited, frontier = set(), [oid]
    origins = set()
    while frontier:
        n = frontier.pop()
        if n in visited:
            continue
        visited.add(n)
        if obs[n].is_root:
            origins.add(obs[n].independent_origin)
        for p in obs[n].cited:
            frontier.append(p)
    return len(origins)


def epistemic_laundering_factor(oid: int, obs: Dict[int, Obs]) -> float:
    rrw = raw_reuse_weight(oid, obs)
    iec = max(1, independent_evidence_count(oid, obs))
    return rrw / iec


def propagation_ratio(oid: int, obs: Dict[int, Obs]) -> float:
    iec = max(1, independent_evidence_count(oid, obs))
    n_desc = len(obs[oid].cited_by)
    return n_desc / iec


def measure(obs: Dict[int, Obs], target: int) -> dict:
    if obs[target].refuted:
        return {"refuted": True, "rrw": 0.0, "iec": 0, "elf": 0.0, "pr": 0.0,
                "refutation_count": obs[target].refutation_count}
    rrw = raw_reuse_weight(target, obs)
    iec = independent_evidence_count(target, obs)
    return {
        "refuted": False,
        "rrw": round(rrw, 2),
        "iec": iec,
        "elf": round(rrw / max(1, iec), 3),
        "pr": round(len(obs[target].cited_by) / max(1, iec), 3),
        "refutation_count": obs[target].refutation_count,
    }


def mean_of(results: List[dict], key: str) -> float:
    vals = [r[key] for r in results if not r["refuted"]]
    return round(sum(vals) / len(vals), 4) if vals else 0.0


# ─── Population builders ────────────────────────────────────────────────────

def pop_A(epochs, p_cite, p_refute, rng):
    """10 independent roots, target cites all, descendants propagate."""
    obs, nid = {}, 0
    roots = []
    for i in range(10):
        obs[nid] = Obs(nid, True, True, i, 0)
        roots.append(nid); nid += 1
    target = nid
    obs[nid] = Obs(nid, True, False, -1, 0, cited=list(roots))
    for r in roots: obs[r].cited_by.append(nid)
    nid += 1
    for ep in range(2, epochs):
        if rng.random() < p_cite:
            obs[nid] = Obs(nid, True, False, -1, 0, cited=[target])
            obs[target].cited_by.append(nid); nid += 1
        if not obs[target].refuted and rng.random() < p_refute * 0.3:  # true claims rarely refuted
            obs[target].refuted = True
    return obs, target


def pop_B(epochs, p_cite, p_refute, rng, is_true=True, cartel=False):
    """1 root, high propagation chain."""
    obs, nid = {}, 0
    obs[0] = Obs(0, is_true, True, 0, 0)
    nid = 1; target = 0
    for ep in range(1, epochs):
        if rng.random() < p_cite:
            existing = [i for i, o in obs.items() if not o.refuted]
            if not existing: continue
            cite = target if (rng.random() < 0.7 and not obs[target].refuted) else int(rng.choice(existing))
            obs[nid] = Obs(nid, is_true, False, 0, 0, cited=[cite])
            obs[cite].cited_by.append(nid); nid += 1
        if not obs[target].refuted:
            p = p_refute if is_true else (p_refute * (1 - CARTEL_PROTECTION) if cartel else p_refute)
            obs[target].refutation_count += (1 if rng.random() < p_refute else 0)
            if rng.random() < p:
                obs[target].refuted = True
    return obs, target


def pop_C(epochs, p_cite, p_refute, rng):
    """Cartel: 5 coordinated false sources, all same independent_origin=0."""
    obs, nid = {}, 0
    roots = []
    for i in range(5):
        obs[nid] = Obs(nid, False, True, 0, 0)  # all origin=0
        roots.append(nid); nid += 1
    target = nid
    obs[nid] = Obs(nid, False, False, 0, 0, cited=list(roots))
    for r in roots: obs[r].cited_by.append(nid)
    nid += 1
    for ep in range(2, epochs):
        if rng.random() < p_cite:
            obs[nid] = Obs(nid, False, False, 0, 0, cited=[target])
            obs[target].cited_by.append(nid); nid += 1
        if not obs[target].refuted:
            obs[target].refutation_count += (1 if rng.random() < p_refute else 0)
            if rng.random() < p_refute * (1 - CARTEL_PROTECTION):
                obs[target].refuted = True
    return obs, target


def pop_D(epochs, p_cite, p_refute, rng):
    """3 independent roots + propagation superstructure."""
    obs, nid = {}, 0
    roots = []
    for i in range(3):
        obs[nid] = Obs(nid, True, True, i, 0)
        roots.append(nid); nid += 1
    target = nid
    obs[nid] = Obs(nid, True, False, -1, 0, cited=list(roots))
    for r in roots: obs[r].cited_by.append(nid)
    nid += 1
    for ep in range(2, epochs):
        if rng.random() < p_cite:
            obs[nid] = Obs(nid, True, False, -1, 0, cited=[target])
            obs[target].cited_by.append(nid); nid += 1
        if not obs[target].refuted and rng.random() < p_refute * 0.3:
            obs[target].refuted = True
    return obs, target


def pop_F(epochs, p_cite, p_refute, rng):
    """Contested true: 20 independent roots, medium reuse, most refutation attempts FAIL."""
    obs, nid = {}, 0
    roots = []
    for i in range(20):
        obs[nid] = Obs(nid, True, True, i, 0)
        roots.append(nid); nid += 1
    target = nid
    obs[nid] = Obs(nid, True, False, -1, 0, cited=list(roots))
    for r in roots: obs[r].cited_by.append(nid)
    nid += 1
    for ep in range(2, epochs):
        if rng.random() < p_cite * 0.5:  # medium reuse
            obs[nid] = Obs(nid, True, False, -1, 0, cited=[target])
            obs[target].cited_by.append(nid); nid += 1
        if not obs[target].refuted:
            # High refutation attempt rate but most fail (Popperian hardiness)
            if rng.random() < p_refute * 5:  # many attempts
                obs[target].refutation_count += 1
                if rng.random() > POPPERIAN_REFUTE_BONUS:  # 60% fail
                    obs[target].failed_refutations += 1
                else:
                    obs[target].refuted = True  # 40% succeed
    return obs, target


# ─── Main ───────────────────────────────────────────────────────────────────

POPULATIONS = {
    "A_corroboration":   lambda ep, pc, pr, rng: pop_A(ep, pc, pr, rng),
    "B_propagation":     lambda ep, pc, pr, rng: pop_B(ep, pc, pr, rng, is_true=True),
    "C_cartel_false":    lambda ep, pc, pr, rng: pop_C(ep, pc, pr, rng),
    "D_mixed":           lambda ep, pc, pr, rng: pop_D(ep, pc, pr, rng),
    "F_contested":       lambda ep, pc, pr, rng: pop_F(ep, pc, pr, rng),
}

REFUTATION_RATES = [0.005, 0.010, 0.035, 0.100]
P_CITE_VALUES    = [0.03, 0.08, 0.15]


def main():
    rng = np.random.default_rng(42)
    total = len(POPULATIONS) * len(REFUTATION_RATES) * len(P_CITE_VALUES) * N_RUNS
    print(f"[{SIM_ID}] {len(POPULATIONS)} pops × {len(REFUTATION_RATES)} refute rates × "
          f"{len(P_CITE_VALUES)} cite rates × {N_RUNS} runs = {total:,} simulations", file=sys.stderr)

    rows = []
    for pop_name, builder in POPULATIONS.items():
        for p_refute in REFUTATION_RATES:
            for p_cite in P_CITE_VALUES:
                run_data = [measure(*builder(N_EPOCHS, p_cite, p_refute, rng)) for _ in range(N_RUNS)]
                refuted_frac = sum(1 for r in run_data if r["refuted"]) / N_RUNS
                row = {
                    "population": pop_name,
                    "p_refute": p_refute,
                    "p_cite": p_cite,
                    "mean_rrw":  mean_of(run_data, "rrw"),
                    "mean_iec":  mean_of(run_data, "iec"),
                    "mean_elf":  mean_of(run_data, "elf"),
                    "mean_pr":   mean_of(run_data, "pr"),
                    "refuted_fraction": round(refuted_frac, 4),
                    "n_runs": N_RUNS,
                }
                rows.append(row)

    # ELF table at p_cite=0.08 (LAUNDER-01 baseline cite rate)
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"ELF (Epistemic Laundering Factor) — p_cite=0.08", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    header = f"{'population':>22} " + "  ".join(f"ref={r}" for r in REFUTATION_RATES)
    print(header, file=sys.stderr)
    for pop_name in POPULATIONS:
        elfs = [next((r["mean_elf"] for r in rows if r["population"]==pop_name and
                      r["p_refute"]==pr and abs(r["p_cite"]-0.08)<0.001), 0.0) for pr in REFUTATION_RATES]
        print(f"{pop_name:>22} " + "  ".join(f"{e:>8.3f}" for e in elfs), file=sys.stderr)

    # Laundering Gain: ELF(B) / ELF(A)
    print(f"\nLaundering Gain LG = ELF(B_propagation) / ELF(A_corroboration) — p_cite=0.08:", file=sys.stderr)
    for pr in REFUTATION_RATES:
        elf_A = next((r["mean_elf"] for r in rows if r["population"]=="A_corroboration" and r["p_refute"]==pr and abs(r["p_cite"]-0.08)<0.001), 1.0)
        elf_B = next((r["mean_elf"] for r in rows if r["population"]=="B_propagation" and r["p_refute"]==pr and abs(r["p_cite"]-0.08)<0.001), 1.0)
        lg = elf_B / max(elf_A, 0.001)
        flag = " <-- LAUNDERING" if lg > 2.0 else ""
        print(f"  p_refute={pr}: ELF(A)={elf_A:.3f} ELF(B)={elf_B:.3f} LG={lg:.2f}x{flag}", file=sys.stderr)

    # IEW ranking check: does A > D > B > C hold?
    print(f"\nIEC ranking — p_cite=0.08, p_refute=0.035:", file=sys.stderr)
    iec_vals = {}
    for pop_name in POPULATIONS:
        iec = next((r["mean_iec"] for r in rows if r["population"]==pop_name and
                    abs(r["p_refute"]-0.035)<0.001 and abs(r["p_cite"]-0.08)<0.001), 0.0)
        iec_vals[pop_name] = iec
    for pn, v in sorted(iec_vals.items(), key=lambda x: -x[1]):
        print(f"  {pn}: IEC={v:.2f}", file=sys.stderr)

    # P4: Does F (contested) have higher IEC than B (propagation)?
    iec_F = iec_vals.get("F_contested", 0)
    iec_B = iec_vals.get("B_propagation", 0)
    p4_v = "CONFIRMED" if iec_F > iec_B else "REFUTED"
    print(f"\nP4: F_IEC={iec_F:.2f} vs B_IEC={iec_B:.2f} [{p4_v}]", file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Provenance stress test: ELF across refutation rates, 5 populations",
        "methodological_note": "ELF, IEC, IEW are research proposals. raw_reuse_weight is current ILC metric.",
        "rows": rows,
        "predictions": {
            "P1": "ELF(B_propagation) >> ELF(A_corroboration) at all refutation rates; gap widens at low refutation",
            "P2": "At p_refute=0.005: LG > 5.0",
            "P3": "IEW ranking A>D>B>C stable across all refutation rates",
            "P4": "F (contested, high failed refutations) has higher IEC than B (propagation)",
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
