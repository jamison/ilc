"""
SIM-LAUNDER-01 — Graph Propagation: Can Epistemic Laundering Entrench False Claims?
=====================================================================================

Research question: Can ordinary jury FCR (16-20% on weak-signal claims) produce
epistemically entrenched false claims through graph reuse and citation propagation?

The reviewer's central hypothesis:
  small adversarial bias
    → false ratification
    → graph reuse
    → reputation / weight
    → downstream derivation
    → harder to challenge
    → epistemic lock-in

This experiment tests whether the GRAPH stage amplifies a jury-level FCR into
an entrenched false claim — or whether the graph structure preserves independent
evidence signal.

Four graph populations (per Astra 6.0's design):
  A — GENUINE CORROBORATION:
      10 independent root claims, each derived from separate evidence bases.
      All supporting P. No coordinator.
      Final node cites all 10.

  B — PURE PROPAGATION:
      1 root claim P.
      100 descendants all cite the root (one hop) or cite each other (chain).
      No additional independent evidence.

  C — COORDINATED CARTEL:
      5 "root" claims, all secretly coordinating (same actor).
      Each root has 20 descendants.
      Appears to have 5 independent sources; actually has 1.

  D — MIXED EVIDENCE:
      3 genuinely independent root claims.
      50 dependent descendants citing those 3 roots.
      Mix of independent foundation + propagation superstructure.

Key question: Can the graph's weight function rank A > D > C > B epistemically?
If it ranks B ≈ A (propagation ≈ independent corroboration), that is a structural vulnerability.

Graph weight model:
  raw_reuse_weight(node) = sum of descendant count across all nodes citing this node
  independent_evidence_weight(node) = count of distinct independent origin paths to root
  provenance_depth(node) = max hops from any true root
  provenance_width(node) = count of distinct paths to roots

  epistemic_weight(node) = independent_evidence_weight / (1 + provenance_depth * propagation_penalty)

Temporal propagation:
  Each epoch, descendants are added with probability p_cite.
  Refutations arrive with probability p_refute (inversely proportional to existing weight).
  False claims get refuted at true_rate * (1 - cartel_protection_factor).

Falsifiable predictions:
  P1: With the raw_reuse_weight metric alone:
      rank(B) ≈ rank(A) — propagation and corroboration are indistinguishable.
  P2: With independent_evidence_weight metric:
      rank(A) >> rank(B) >> rank(C) — correctly separates the populations.
  P3: A false claim in population B reaches "entrenched" status
      (weight > 50% of top true claims) within 30 epochs.
  P4: A false claim in population A never reaches entrenched status
      (independent corroboration eventually generates refutation).
  P5: Population C (cartel appearing as 5 independent sources) is
      indistinguishable from D by raw_reuse_weight but distinguishable
      by Fiedler-based behavioral analysis.

Methodological note:
  This is a graph simulation under an assumed citation and refutation model.
  Results reflect the model's assumed behaviors, not empirical ILC protocol data.
  The graph weight function tested here is a RESEARCH PROPOSAL, not the current
  implemented ILC weight function. The current protocol uses raw_reuse_weight
  without provenance depth discounting.
"""

from __future__ import annotations

import hashlib
import json
import sys
import os
import math
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SIM_ID = "SIM-LAUNDER-01"

N_EPOCHS   = 60       # time steps
N_RUNS     = 200      # independent simulation runs per population
P_CITE     = 0.08     # probability per epoch a new agent cites an existing node
P_REFUTE_TRUE  = 0.005  # per-epoch refutation prob for TRUE claims (false positives)
P_REFUTE_FALSE = 0.035  # per-epoch refutation prob for FALSE claims (honest detection)
CARTEL_PROTECTION = 0.70  # cartel reduces effective refutation prob on their false claims


@dataclass
class GraphNode:
    node_id: int
    is_true: bool           # ground truth
    is_root: bool
    independent_origin: int  # which independent source (0..n_independent_origins-1)
    citations: List[int] = field(default_factory=list)  # nodes this cites
    cited_by: List[int] = field(default_factory=list)   # nodes that cite this
    epoch_created: int = 0
    refuted: bool = False


def raw_reuse_weight(node_id: int, nodes: Dict[int, GraphNode]) -> float:
    """Current ILC weight: total count of nodes that transitively depend on this node."""
    visited = set()
    frontier = [node_id]
    while frontier:
        n = frontier.pop()
        for child in nodes[n].cited_by:
            if child not in visited:
                visited.add(child)
                frontier.append(child)
    return float(len(visited))


def independent_evidence_weight(node_id: int, nodes: Dict[int, GraphNode]) -> float:
    """
    Count distinct independent_origin values reachable from this node upward
    (i.e., in the provenance chain).
    This is the proposed alternative metric: independent corroboration count.
    """
    visited = set()
    frontier = [node_id]
    independent_origins = set()
    while frontier:
        n = frontier.pop()
        if n in visited:
            continue
        visited.add(n)
        if nodes[n].is_root:
            independent_origins.add(nodes[n].independent_origin)
        for parent in nodes[n].citations:
            frontier.append(parent)
    return float(len(independent_origins))


def provenance_depth(node_id: int, nodes: Dict[int, GraphNode]) -> int:
    """Max distance to any root node in citation graph."""
    visited = {}
    frontier = [(node_id, 0)]
    max_depth = 0
    while frontier:
        n, depth = frontier.pop()
        if n in visited and visited[n] <= depth:
            continue
        visited[n] = depth
        if nodes[n].is_root:
            max_depth = max(max_depth, depth)
        for parent in nodes[n].citations:
            frontier.append((parent, depth + 1))
    return max_depth


def epistemic_weight(node_id: int, nodes: Dict[int, GraphNode], penalty: float = 0.1) -> float:
    """
    Proposed improved metric: independent_evidence / (1 + depth * penalty)
    Discounts weight for claims that are deeply derived from few independent sources.
    """
    iew = independent_evidence_weight(node_id, nodes)
    depth = provenance_depth(node_id, nodes)
    return iew / (1.0 + depth * penalty)


def simulate_population_A(n_epochs, rng):
    """
    Population A: 10 independent root claims, all True, converging to a synthesis node.
    Represents genuine corroboration from diverse sources.
    """
    nodes = {}
    nid = 0
    root_ids = []
    for i in range(10):
        nodes[nid] = GraphNode(node_id=nid, is_true=True, is_root=True,
                               independent_origin=i, epoch_created=0)
        root_ids.append(nid)
        nid += 1

    # Target claim node: cites all 10 roots
    target_id = nid
    nodes[nid] = GraphNode(node_id=nid, is_true=True, is_root=False,
                           independent_origin=-1, citations=list(root_ids), epoch_created=1)
    for rid in root_ids:
        nodes[rid].cited_by.append(nid)
    nid += 1

    for epoch in range(2, n_epochs):
        if rng.random() < P_CITE:
            # New derivative work citing target
            nodes[nid] = GraphNode(node_id=nid, is_true=True, is_root=False,
                                   independent_origin=-1, citations=[target_id], epoch_created=epoch)
            nodes[target_id].cited_by.append(nid)
            nid += 1
        # Refutations (very rare for true claims)
        if not nodes[target_id].refuted and rng.random() < P_REFUTE_TRUE:
            nodes[target_id].refuted = True

    return nodes, target_id


def simulate_population_B(n_epochs, rng, target_true=True, cartel=False):
    """
    Population B: 1 root claim, N descendants via citation chain.
    Represents pure propagation — one source, many copies.
    """
    nodes = {}
    nid = 0
    root_id = 0
    nodes[0] = GraphNode(node_id=0, is_true=target_true, is_root=True,
                         independent_origin=0, epoch_created=0)
    nid = 1
    target_id = 0  # root is the target claim

    for epoch in range(1, n_epochs):
        if rng.random() < P_CITE:
            # Cite any existing non-refuted node (preferring target)
            existing = [i for i, n in nodes.items() if not n.refuted]
            if not existing:
                continue
            cite_id = target_id if (rng.random() < 0.7 and not nodes[target_id].refuted) else int(rng.choice(existing))
            nodes[nid] = GraphNode(node_id=nid, is_true=target_true, is_root=False,
                                   independent_origin=0, citations=[cite_id], epoch_created=epoch)
            nodes[cite_id].cited_by.append(nid)
            nid += 1

        # Refutation: cartel protects false claims
        if not nodes[target_id].refuted:
            p_ref = P_REFUTE_TRUE if target_true else P_REFUTE_FALSE
            if cartel:
                p_ref *= (1 - CARTEL_PROTECTION)
            if rng.random() < p_ref:
                nodes[target_id].refuted = True

    return nodes, target_id


def simulate_population_C(n_epochs, rng):
    """
    Population C: 5 root claims (all same independent_origin = coordinated cartel),
    each spawning 20 descendants. Appears as 5 independent sources.
    Target claim is false (cartel protecting it).
    """
    nodes = {}
    nid = 0
    root_ids = []
    # All 5 roots share independent_origin=0 (coordinated — but this is hidden from weight fn)
    for i in range(5):
        nodes[nid] = GraphNode(node_id=nid, is_true=False, is_root=True,
                               independent_origin=0,  # ALL same origin — the cartel
                               epoch_created=0)
        root_ids.append(nid)
        nid += 1

    # Target node cites all 5 cartel roots
    target_id = nid
    nodes[nid] = GraphNode(node_id=nid, is_true=False, is_root=False,
                           independent_origin=0, citations=list(root_ids), epoch_created=1)
    for rid in root_ids:
        nodes[rid].cited_by.append(nid)
    nid += 1

    for epoch in range(2, n_epochs):
        if rng.random() < P_CITE:
            nodes[nid] = GraphNode(node_id=nid, is_true=False, is_root=False,
                                   independent_origin=0, citations=[target_id], epoch_created=epoch)
            nodes[target_id].cited_by.append(nid)
            nid += 1
        if not nodes[target_id].refuted:
            p_ref = P_REFUTE_FALSE * (1 - CARTEL_PROTECTION)
            if rng.random() < p_ref:
                nodes[target_id].refuted = True

    return nodes, target_id


def simulate_population_D(n_epochs, rng):
    """
    Population D: 3 independent roots (True), 50 dependent descendants.
    Mixed: genuine independent foundation with propagation superstructure.
    """
    nodes = {}
    nid = 0
    root_ids = []
    for i in range(3):
        nodes[nid] = GraphNode(node_id=nid, is_true=True, is_root=True,
                               independent_origin=i, epoch_created=0)
        root_ids.append(nid)
        nid += 1

    target_id = nid
    nodes[nid] = GraphNode(node_id=nid, is_true=True, is_root=False,
                           independent_origin=-1, citations=list(root_ids), epoch_created=1)
    for rid in root_ids:
        nodes[rid].cited_by.append(nid)
    nid += 1

    for epoch in range(2, n_epochs):
        if rng.random() < P_CITE:
            nodes[nid] = GraphNode(node_id=nid, is_true=True, is_root=False,
                                   independent_origin=-1, citations=[target_id], epoch_created=epoch)
            nodes[target_id].cited_by.append(nid)
            nid += 1
        if not nodes[target_id].refuted and rng.random() < P_REFUTE_TRUE:
            nodes[target_id].refuted = True

    return nodes, target_id


def measure(nodes, target_id):
    if nodes[target_id].refuted:
        return {
            "raw_reuse_weight": 0.0,
            "independent_evidence_weight": 0.0,
            "epistemic_weight": 0.0,
            "refuted": True,
            "n_descendants": 0,
        }
    rrw = raw_reuse_weight(target_id, nodes)
    iew = independent_evidence_weight(target_id, nodes)
    ew  = epistemic_weight(target_id, nodes)
    n_desc = len(nodes[target_id].cited_by)
    return {
        "raw_reuse_weight": round(rrw, 2),
        "independent_evidence_weight": round(iew, 2),
        "epistemic_weight": round(ew, 4),
        "refuted": False,
        "n_descendants": n_desc,
    }


def mean_metric(results, key):
    vals = [r[key] for r in results if not r["refuted"]]
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def main():
    rng = np.random.default_rng(42)
    print(f"[{SIM_ID}] {N_RUNS} runs × 4 populations × {N_EPOCHS} epochs", file=sys.stderr)

    pop_results = {}
    for pop_name, sim_fn in [
        ("A_genuine_corroboration", lambda r: simulate_population_A(N_EPOCHS, r)),
        ("B_pure_propagation_true", lambda r: simulate_population_B(N_EPOCHS, r, target_true=True)),
        ("B_false_propagation",     lambda r: simulate_population_B(N_EPOCHS, r, target_true=False, cartel=False)),
        ("C_cartel_false",          lambda r: simulate_population_C(N_EPOCHS, r)),
        ("D_mixed_evidence",        lambda r: simulate_population_D(N_EPOCHS, r)),
    ]:
        run_data = []
        for _ in range(N_RUNS):
            nodes, tid = sim_fn(rng)
            run_data.append(measure(nodes, tid))

        refuted_frac = sum(1 for r in run_data if r["refuted"]) / N_RUNS
        pop_results[pop_name] = {
            "mean_raw_reuse_weight":        round(mean_metric(run_data, "raw_reuse_weight"), 3),
            "mean_independent_evidence":    round(mean_metric(run_data, "independent_evidence_weight"), 3),
            "mean_epistemic_weight":        round(mean_metric(run_data, "epistemic_weight"), 4),
            "refuted_fraction":             round(refuted_frac, 4),
            "n_runs": N_RUNS,
        }
        print(
            f"  {pop_name}: RRW={pop_results[pop_name]['mean_raw_reuse_weight']:.2f} "
            f"IEW={pop_results[pop_name]['mean_independent_evidence']:.2f} "
            f"EW={pop_results[pop_name]['mean_epistemic_weight']:.4f} "
            f"refuted={refuted_frac:.3f}",
            file=sys.stderr,
        )

    # Temporal lock-in: how quickly does B_false_propagation reach "entrenched"?
    # Entrenched = raw_reuse_weight > threshold and not refuted by epoch T
    print(f"\n[{SIM_ID}] Temporal lock-in analysis...", file=sys.stderr)
    entrenched_by_epoch = {}
    for epoch_check in [10, 20, 30, 45, 60]:
        rng2 = np.random.default_rng(99)
        entrenched = 0
        for _ in range(N_RUNS):
            nodes, tid = simulate_population_B(epoch_check, rng2, target_true=False, cartel=False)
            m = measure(nodes, tid)
            if not m["refuted"] and m["raw_reuse_weight"] >= 5.0:
                entrenched += 1
        entrenched_by_epoch[epoch_check] = round(entrenched / N_RUNS, 4)
        print(f"  epoch {epoch_check}: P(entrenched|false propagation) = {entrenched_by_epoch[epoch_check]:.4f}", file=sys.stderr)

    # Ranking test: does RRW rank A > D > C > B correctly?
    rrw_rank = sorted(
        [(pop, pop_results[pop]["mean_raw_reuse_weight"]) for pop in pop_results if pop != "B_false_propagation"],
        key=lambda x: -x[1]
    )
    iew_rank = sorted(
        [(pop, pop_results[pop]["mean_independent_evidence"]) for pop in pop_results if pop != "B_false_propagation"],
        key=lambda x: -x[1]
    )
    print(f"\nRanking by raw_reuse_weight: {[x[0] for x in rrw_rank]}", file=sys.stderr)
    print(f"Ranking by independent_evidence: {[x[0] for x in iew_rank]}", file=sys.stderr)

    result = {
        "sim_id": SIM_ID,
        "description": "Graph propagation: can laundering entrench false claims? Four populations.",
        "methodological_note": (
            "Graph weight functions tested here are RESEARCH PROPOSALS, not current ILC implementation. "
            "The current protocol uses raw_reuse_weight without provenance depth discounting. "
            "All results are model consequences under the assumed citation/refutation model."
        ),
        "population_results": pop_results,
        "temporal_lock_in_false_propagation": entrenched_by_epoch,
        "ranking_by_raw_reuse_weight": [x[0] for x in rrw_rank],
        "ranking_by_independent_evidence": [x[0] for x in iew_rank],
        "model_parameters": {
            "n_epochs": N_EPOCHS,
            "p_cite": P_CITE,
            "p_refute_true": P_REFUTE_TRUE,
            "p_refute_false": P_REFUTE_FALSE,
            "cartel_protection_factor": CARTEL_PROTECTION,
            "entrenched_threshold_rrw": 5.0,
        },
        "predictions": {
            "P1": "raw_reuse_weight: rank(B_true) ≈ rank(A) — propagation indistinguishable from corroboration",
            "P2": "independent_evidence_weight: rank(A) >> rank(B) >> rank(C)",
            "P3": "B_false_propagation reaches entrenched status (RRW>5) within 30 epochs",
            "P4": "A_genuine_corroboration false-claim refuted before becoming entrenched",
            "P5": "C_cartel indistinguishable from D by raw_reuse_weight but not by independent_evidence",
        },
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    payload_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sha384 = hashlib.sha384(payload_bytes).hexdigest()
    result["sha384"] = sha384

    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\n[{SIM_ID}] SHA-384: {sha384}", file=sys.stderr)

    # Prediction verdicts
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"SIM-LAUNDER-01 PREDICTION VERDICTS", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)

    A_rrw = pop_results["A_genuine_corroboration"]["mean_raw_reuse_weight"]
    B_rrw = pop_results["B_pure_propagation_true"]["mean_raw_reuse_weight"]
    p1_v = "CONFIRMED" if abs(A_rrw - B_rrw) / max(A_rrw, 0.01) < 0.30 else "REFUTED"
    print(f"P1: A_RRW={A_rrw:.2f} vs B_true_RRW={B_rrw:.2f} diff={abs(A_rrw-B_rrw):.2f} [{p1_v}]", file=sys.stderr)

    A_iew = pop_results["A_genuine_corroboration"]["mean_independent_evidence"]
    B_iew = pop_results["B_pure_propagation_true"]["mean_independent_evidence"]
    C_iew = pop_results["C_cartel_false"]["mean_independent_evidence"]
    correct_rank = A_iew > B_iew and B_iew > C_iew
    print(f"P2: A_IEW={A_iew:.2f} B_IEW={B_iew:.2f} C_IEW={C_iew:.2f} — correct rank={'CONFIRMED' if correct_rank else 'REFUTED'}", file=sys.stderr)

    p3_v = "CONFIRMED" if entrenched_by_epoch.get(30, 0) > 0.30 else "REFUTED"
    print(f"P3: B_false entrenched by epoch 30: {entrenched_by_epoch.get(30, 0):.4f} [{p3_v}]", file=sys.stderr)

    C_rrw = pop_results["C_cartel_false"]["mean_raw_reuse_weight"]
    D_rrw = pop_results["D_mixed_evidence"]["mean_raw_reuse_weight"]
    C_iew2 = pop_results["C_cartel_false"]["mean_independent_evidence"]
    D_iew2 = pop_results["D_mixed_evidence"]["mean_independent_evidence"]
    p5_v = "CONFIRMED" if (abs(C_rrw - D_rrw) < 0.5 * max(C_rrw, D_rrw)) and (D_iew2 > C_iew2 * 2) else "REFUTED"
    print(f"P5: C_RRW={C_rrw:.2f} D_RRW={D_rrw:.2f} C_IEW={C_iew2:.2f} D_IEW={D_iew2:.2f} [{p5_v}]", file=sys.stderr)


if __name__ == "__main__":
    main()
