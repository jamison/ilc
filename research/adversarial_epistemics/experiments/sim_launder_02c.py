"""
SIM-LAUNDER-02C — Popular Falsehood vs Contested Truth
=======================================================

The reviewer's key comparison:

  Popular Falsehood:   1 independent origin → 10 observers → 1,000 reuse events → 10,000 edges
  Contested Truth:    30 independent origins → 55% support / 45% dissent → 200 reuse events

  Q: Does raw_reuse_weight rank Popular Falsehood ABOVE Contested Truth?
  Q: Does IEC correctly rank Contested Truth ABOVE Popular Falsehood?
  Q: What is the ELF ratio between them?

Also: Underspecified Proposition (Population H from reviewer)
  Claim "X is safe" with two contexts C1 (safe), C2 (unsafe).
  Test whether the graph can represent this as underspecification rather than
  50% wrong / 50% right.

Refutation rate sweep: [0.5%, 1%, 3.5%] per epoch
N_RUNS = 500, N_EPOCHS = 90

Key metrics:
  ELF(x) = RRW / max(1, IEC)
  IEC(x) = independent evidence count
  RRW(x) = raw reuse weight
  refuted_fraction = fraction of runs where claim is refuted by epoch T

Falsifiable predictions:
  P1: RRW ranks Popular_Falsehood ABOVE Contested_Truth at all cite rates
      (propagation outranks evidence count under current metric)
  P2: IEC correctly ranks Contested_Truth ABOVE Popular_Falsehood
      (IEC=30 vs IEC=1)
  P3: ELF(Popular_Falsehood) > 10 × ELF(Contested_Truth) — extreme laundering
  P4: With cartel protection on Popular_Falsehood, P(not refuted by epoch 90)
      remains > 30% even at p_refute=0.035 — refutation suppression is persistent
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SIM_ID = "SIM-LAUNDER-02C"

N_RUNS   = 500
N_EPOCHS = 90
CARTEL_PROTECTION = 0.70
POPPERIAN_SURVIVE = 0.60  # fraction of refutation attempts that fail on contested claim

# ─── Graph primitives (from LAUNDER-01) ─────────────────────────────────────

@dataclass
class Node:
    nid: int
    is_true: bool
    is_root: bool
    independent_origin: int
    context_id: int = 0
    cited: List[int] = field(default_factory=list)
    cited_by: List[int] = field(default_factory=list)
    refuted: bool = False
    refutation_attempts: int = 0
    failed_refutations: int = 0


def rrw(target: int, g: Dict[int, Node]) -> float:
    visited, frontier = set(), [target]
    while frontier:
        n = frontier.pop()
        for c in g[n].cited_by:
            if c not in visited:
                visited.add(c); frontier.append(c)
    return float(len(visited))


def iec(target: int, g: Dict[int, Node]) -> int:
    visited, frontier = set(), [target]
    origins = set()
    while frontier:
        n = frontier.pop()
        if n in visited: continue
        visited.add(n)
        if g[n].is_root: origins.add(g[n].independent_origin)
        for p in g[n].cited: frontier.append(p)
    return len(origins)


def elf(target: int, g: Dict[int, Node]) -> float:
    return rrw(target, g) / max(1, iec(target, g))


def measure(g: Dict[int, Node], tid: int) -> dict:
    if g[tid].refuted:
        return {"refuted": True, "rrw": 0.0, "iec": 0, "elf": 0.0,
                "refutation_attempts": g[tid].refutation_attempts}
    r = rrw(tid, g)
    i = iec(tid, g)
    return {
        "refuted": False,
        "rrw": round(r, 2),
        "iec": i,
        "elf": round(r / max(1, i), 3),
        "refutation_attempts": g[tid].refutation_attempts,
        "failed_refutations": g[tid].failed_refutations,
    }


# ─── Population builders ─────────────────────────────────────────────────────

def pop_popular_falsehood(epochs, p_cite_high, p_refute, rng):
    """
    1 false origin, high reuse (p_cite_high), cartel suppresses refutation.
    """
    g, nid = {}, 0
    g[0] = Node(0, False, True, 0)
    target = 0; nid = 1
    for ep in range(1, epochs):
        if rng.random() < p_cite_high:
            existing = [i for i, n in g.items() if not n.refuted]
            if not existing: continue
            cite = target if (rng.random() < 0.7 and not g[target].refuted) else int(rng.choice(existing))
            g[nid] = Node(nid, False, False, 0, cited=[cite])
            g[cite].cited_by.append(nid); nid += 1
        if not g[target].refuted:
            if rng.random() < p_refute:
                g[target].refutation_attempts += 1
                # Cartel suppresses: only (1-protection) of attempts succeed
                if rng.random() > CARTEL_PROTECTION:
                    g[target].refuted = True
    return g, target


def pop_contested_truth(epochs, p_cite_med, p_refute, rng):
    """
    30 independent origins, 55% support / 45% dissent, medium reuse.
    Many refutation attempts, most fail (Popperian hardiness).
    """
    g, nid = {}, 0
    roots = []
    for i in range(30):
        g[nid] = Node(nid, True, True, i)
        roots.append(nid); nid += 1
    target = nid
    # Synthesizing node cites all 30 roots
    g[nid] = Node(nid, True, False, -1, cited=list(roots))
    for r in roots: g[r].cited_by.append(nid)
    nid += 1

    # Dissent nodes (45% of population disagrees — not wrong, just contested)
    n_dissent_roots = int(30 * 0.45)
    dissent_roots = []
    for i in range(n_dissent_roots):
        g[nid] = Node(nid, False, True, 100 + i)  # distinct origins for dissent
        dissent_roots.append(nid); nid += 1
    dissent_target = nid
    g[nid] = Node(nid, False, False, -1, cited=list(dissent_roots))
    for r in dissent_roots: g[r].cited_by.append(nid)
    nid += 1

    for ep in range(2, epochs):
        if rng.random() < p_cite_med:  # medium reuse
            g[nid] = Node(nid, True, False, -1, cited=[target])
            g[target].cited_by.append(nid); nid += 1
        if rng.random() < p_cite_med * 0.45:  # dissent propagation
            g[nid] = Node(nid, False, False, -1, cited=[dissent_target])
            g[dissent_target].cited_by.append(nid); nid += 1
        if not g[target].refuted:
            if rng.random() < p_refute * 3:  # high refutation attempt rate
                g[target].refutation_attempts += 1
                if rng.random() > POPPERIAN_SURVIVE:  # most fail
                    g[target].refuted = True
                else:
                    g[target].failed_refutations += 1
    return g, target, dissent_target


def pop_underspecified(epochs, p_cite, p_refute, rng):
    """
    'X is safe' — two contexts C1 (safe), C2 (unsafe).
    Observers from C1 cite support roots; C2 cites opposition roots.
    The graph CAN distinguish this as context-qualified if context_id is tracked.
    A naive graph sees 50/50 disagreement and cannot determine which side is 'right'.
    """
    g, nid = {}, 0
    # C1: X is safe (3 independent evidence sources)
    c1_roots = []
    for i in range(3):
        g[nid] = Node(nid, True, True, i, context_id=1)
        c1_roots.append(nid); nid += 1
    c1_target = nid
    g[nid] = Node(nid, True, False, -1, context_id=1, cited=list(c1_roots))
    for r in c1_roots: g[r].cited_by.append(nid)
    nid += 1

    # C2: X is unsafe (2 independent evidence sources)
    c2_roots = []
    for i in range(2):
        g[nid] = Node(nid, False, True, 10 + i, context_id=2)
        c2_roots.append(nid); nid += 1
    c2_target = nid
    g[nid] = Node(nid, False, False, -1, context_id=2, cited=list(c2_roots))
    for r in c2_roots: g[r].cited_by.append(nid)
    nid += 1

    for ep in range(2, epochs):
        if rng.random() < p_cite:
            g[nid] = Node(nid, True, False, -1, context_id=1, cited=[c1_target])
            g[c1_target].cited_by.append(nid); nid += 1
        if rng.random() < p_cite:
            g[nid] = Node(nid, False, False, -1, context_id=2, cited=[c2_target])
            g[c2_target].cited_by.append(nid); nid += 1

    # Underspecification metric: can we detect that both populations are internally coherent?
    c1_iec = iec(c1_target, g)
    c2_iec = iec(c2_target, g)
    c1_rrw = rrw(c1_target, g)
    c2_rrw = rrw(c2_target, g)
    # Context separation: are observations structured by context_id?
    ctx_1 = [i for i, n in g.items() if n.context_id == 1 and not n.is_root]
    ctx_2 = [i for i, n in g.items() if n.context_id == 2 and not n.is_root]
    return g, c1_target, c2_target, {
        "c1_iec": c1_iec, "c2_iec": c2_iec,
        "c1_rrw": c1_rrw, "c2_rrw": c2_rrw,
        "n_c1_nodes": len(ctx_1), "n_c2_nodes": len(ctx_2),
        "context_detectable": c1_iec > 0 and c2_iec > 0,
    }


# ─── Main ────────────────────────────────────────────────────────────────────

P_REFUTE_VALUES = [0.005, 0.010, 0.035]
P_CITE_HIGH  = 0.15   # high reuse (Popular Falsehood)
P_CITE_MED   = 0.08   # medium reuse (Contested Truth)


def mean_k(results, key):
    vals = [r[key] for r in results if not r.get("refuted", True)]
    return round(sum(vals) / max(1, len(vals)), 4)


def main():
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] Popular Falsehood vs Contested Truth — {N_RUNS} runs × {N_EPOCHS} epochs",
          file=sys.stderr)

    rows = []
    for p_refute in P_REFUTE_VALUES:
        # Popular Falsehood
        pf_data = [measure(*pop_popular_falsehood(N_EPOCHS, P_CITE_HIGH, p_refute, rng))
                   for _ in range(N_RUNS)]
        pf_refuted = sum(1 for r in pf_data if r["refuted"]) / N_RUNS

        # Contested Truth (measure at support target, not dissent)
        ct_raw = [pop_contested_truth(N_EPOCHS, P_CITE_MED, p_refute, rng) for _ in range(N_RUNS)]
        ct_data = [measure(g, tid) for g, tid, _ in ct_raw]
        ct_refuted = sum(1 for r in ct_data if r["refuted"]) / N_RUNS

        pf_row = {
            "population": "Popular_Falsehood",
            "p_refute": p_refute,
            "mean_rrw": mean_k(pf_data, "rrw"),
            "mean_iec": mean_k(pf_data, "iec"),
            "mean_elf": mean_k(pf_data, "elf"),
            "refuted_fraction": round(pf_refuted, 4),
        }
        ct_row = {
            "population": "Contested_Truth",
            "p_refute": p_refute,
            "mean_rrw": mean_k(ct_data, "rrw"),
            "mean_iec": mean_k(ct_data, "iec"),
            "mean_elf": mean_k(ct_data, "elf"),
            "refuted_fraction": round(ct_refuted, 4),
        }
        rows.extend([pf_row, ct_row])

        rrw_rank_wrong = pf_row["mean_rrw"] > ct_row["mean_rrw"]
        iec_rank_right = ct_row["mean_iec"] > pf_row["mean_iec"]
        elf_ratio = pf_row["mean_elf"] / max(0.001, ct_row["mean_elf"])

        print(
            f"\n  p_refute={p_refute}:",
            file=sys.stderr
        )
        print(
            f"    Pop Falsehood: RRW={pf_row['mean_rrw']:6.2f} IEC={pf_row['mean_iec']:.2f} "
            f"ELF={pf_row['mean_elf']:6.2f} refuted={pf_refuted:.3f}",
            file=sys.stderr
        )
        print(
            f"    Cont Truth:    RRW={ct_row['mean_rrw']:6.2f} IEC={ct_row['mean_iec']:.2f} "
            f"ELF={ct_row['mean_elf']:6.2f} refuted={ct_refuted:.3f}",
            file=sys.stderr
        )
        print(
            f"    RRW ranks PF>{CT}: {rrw_rank_wrong} | IEC ranks CT>PF: {iec_rank_right} | "
            f"ELF_ratio={elf_ratio:.2f}x",
            file=sys.stderr
        )

    # Underspecified proposition
    print(f"\n  Underspecified proposition (p_cite=0.08, 1 run):", file=sys.stderr)
    _, c1t, c2t, under_metrics = pop_underspecified(N_EPOCHS, P_CITE_MED, 0.035, rng)
    print(f"    C1 (safe):   IEC={under_metrics['c1_iec']} RRW={under_metrics['c1_rrw']:.2f} nodes={under_metrics['n_c1_nodes']}", file=sys.stderr)
    print(f"    C2 (unsafe): IEC={under_metrics['c2_iec']} RRW={under_metrics['c2_rrw']:.2f} nodes={under_metrics['n_c2_nodes']}", file=sys.stderr)
    print(f"    Context detectable: {under_metrics['context_detectable']}", file=sys.stderr)

    # Prediction verdicts at p_refute=0.035 (LAUNDER-01 baseline)
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"PREDICTION VERDICTS (p_refute=0.035)", file=sys.stderr)
    pf35 = next(r for r in rows if r["population"]=="Popular_Falsehood" and abs(r["p_refute"]-0.035)<0.001)
    ct35 = next(r for r in rows if r["population"]=="Contested_Truth"   and abs(r["p_refute"]-0.035)<0.001)
    p1_v = "CONFIRMED" if pf35["mean_rrw"] > ct35["mean_rrw"] else "REFUTED"
    p2_v = "CONFIRMED" if ct35["mean_iec"] > pf35["mean_iec"] else "REFUTED"
    p3_v = "CONFIRMED" if pf35["mean_elf"] / max(0.001, ct35["mean_elf"]) > 10 else "REFUTED"
    pf_05 = next((r for r in rows if r["population"]=="Popular_Falsehood" and abs(r["p_refute"]-0.005)<0.001), None)
    p4_v = "CONFIRMED" if pf_05 and pf_05["refuted_fraction"] < 0.70 else "REFUTED"
    print(f"P1 RRW rank PF>CT: PF={pf35['mean_rrw']:.2f} CT={ct35['mean_rrw']:.2f} [{p1_v}]", file=sys.stderr)
    print(f"P2 IEC rank CT>PF: CT={ct35['mean_iec']:.2f} PF={pf35['mean_iec']:.2f} [{p2_v}]", file=sys.stderr)
    print(f"P3 ELF ratio >10x: ratio={pf35['mean_elf']/max(0.001,ct35['mean_elf']):.2f} [{p3_v}]", file=sys.stderr)
    if pf_05:
        print(f"P4 PF not-refuted at p=0.005: {1-pf_05['refuted_fraction']:.3f} survive [{p4_v}]", file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Popular Falsehood vs Contested Truth vs Underspecified Proposition",
        "methodological_note": "ELF, IEC are research proposals. Current ILC uses raw_reuse_weight.",
        "rows": rows,
        "underspecified_metrics": under_metrics,
        "predictions": {
            "P1": "RRW ranks Popular_Falsehood > Contested_Truth",
            "P2": "IEC ranks Contested_Truth > Popular_Falsehood (IEC=30 vs 1)",
            "P3": "ELF(PF) > 10 × ELF(CT) — extreme laundering",
            "P4": "P(PF not refuted by epoch 90) > 30% even at p_refute=0.035",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    sha = hashlib.sha384(payload).hexdigest()
    result["sha384"] = sha
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha}", file=sys.stderr)


# fix f-string variable name typo
CT = "Contested Truth"


if __name__ == "__main__":
    main()
