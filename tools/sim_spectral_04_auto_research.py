#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""SIM-SPECTRAL-04 Auto-Research: structural perturbation search.

Systematically applies node/edge additions and removals to the claim-composition
projection and runs SIM-SPECTRAL-04 gate evaluation for each variant.  Reports
S3/S1 and G2/S1 ratios so the human can identify which structural changes pass
the CDL-085 gate criterion.

Gate criterion (pass = ALL must hold across all seeds):
  - S1 slope positive
  - matched S3/S1 < 0.6416011282246747
  - matched G2/S1 < 0.8640456434014127

Usage:
  .venv/bin/python tools/sim_spectral_04_auto_research.py [--seeds 42,1337,2026]
"""

from __future__ import annotations

import copy
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Thresholds (from SIM-SPECTRAL-03 corrected baseline)
# ---------------------------------------------------------------------------
S3_S1_THRESHOLD = 0.6416011282246747
G2_S1_THRESHOLD = 0.8640456434014127

PROJECTION_PATH = Path("out/genesis_claim_composition_projection_v0.1.json")
SEEDS = [42, 1337, 2026]
EPOCHS = 30
K = 0.3          # matches Phase 1161 run (worst-case / lowest k)
WEIGHT_PROFILE = "uniform_available"  # matches Phase 1161 run

# ---------------------------------------------------------------------------
# Simulation runner (imports from the real harness)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.sim_spectral_02 import run_simulation  # noqa: E402


def _slope(tmp_path: Path, scenario: str, seed: int, node_count: int | None) -> float:
    result = run_simulation(
        scenario=scenario,
        k=K,
        weight_profile=WEIGHT_PROFILE,
        seed=seed,
        epochs=EPOCHS,
        s1_projection_file=tmp_path if scenario == "S1" else None,
        node_count_override=node_count if scenario != "S1" else None,
    )
    return float(result["rolling_slope"])


def run_gate(proj: dict[str, Any]) -> dict[str, Any]:
    """Run the full gate evaluation for one projection variant.

    Returns a dict with per-seed ratios and a pass/fail verdict.
    """
    # Write a temp file for the projection
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(proj, f, sort_keys=True, allow_nan=False)
        tmp = Path(f.name)

    n_nodes = len(proj["vertices"])
    per_seed: list[dict[str, float]] = []
    try:
        for seed in SEEDS:
            s1 = _slope(tmp, "S1", seed, None)
            s3 = _slope(tmp, "S3", seed, n_nodes)
            g2 = _slope(tmp, "G2", seed, n_nodes)
            # Avoid division by zero / near-zero
            s3_s1 = abs(s3 / s1) if abs(s1) > 1e-9 else math.inf
            g2_s1 = abs(g2 / s1) if abs(s1) > 1e-9 else math.inf
            per_seed.append(
                {
                    "seed": seed,
                    "s1_slope": round(s1, 6),
                    "s3_slope": round(s3, 6),
                    "g2_slope": round(g2, 6),
                    "s3_s1": round(s3_s1, 6),
                    "g2_s1": round(g2_s1, 6),
                }
            )
    finally:
        tmp.unlink(missing_ok=True)

    s1_positive = all(r["s1_slope"] > 0 for r in per_seed)
    s3_pass = all(r["s3_s1"] < S3_S1_THRESHOLD for r in per_seed)
    g2_pass = all(r["g2_s1"] < G2_S1_THRESHOLD for r in per_seed)
    gate = "PASS" if (s1_positive and s3_pass and g2_pass) else "FAIL"

    # Worst-case (highest) ratio across seeds
    max_s3_s1 = max(r["s3_s1"] for r in per_seed)
    max_g2_s1 = max(r["g2_s1"] for r in per_seed)

    return {
        "gate": gate,
        "s1_positive": s1_positive,
        "s3_pass": s3_pass,
        "g2_pass": g2_pass,
        "max_s3_s1": round(max_s3_s1, 6),
        "max_g2_s1": round(max_g2_s1, 6),
        "per_seed": per_seed,
    }


# ---------------------------------------------------------------------------
# Perturbation helpers
# ---------------------------------------------------------------------------

def _load_projection() -> dict[str, Any]:
    return json.loads(PROJECTION_PATH.read_text(encoding="utf-8"))


def _vertex_degrees(proj: dict[str, Any]) -> dict[str, int]:
    deg: dict[str, int] = {v["vertex_id"]: 0 for v in proj["vertices"]}
    for e in proj["edges"]:
        s, t = e["source"], e["target"]
        if s in deg:
            deg[s] += 1
        if t in deg:
            deg[t] += 1
    return deg


def _remove_vertex(proj: dict[str, Any], vertex_id: str) -> dict[str, Any]:
    p = copy.deepcopy(proj)
    p["vertices"] = [v for v in p["vertices"] if v["vertex_id"] != vertex_id]
    p["edges"] = [
        e for e in p["edges"]
        if e["source"] != vertex_id and e["target"] != vertex_id
    ]
    return p


def _add_hub_vertex(
    proj: dict[str, Any],
    hub_id: str,
    label: str,
    reason: str,
    connect_to: list[str],
    authority_ref: str,
) -> dict[str, Any]:
    """Add a new hub vertex with edges to all vertices in connect_to."""
    p = copy.deepcopy(proj)
    p["vertices"].append({
        "vertex_id": hub_id,
        "label": label,
        "authority_source_ref": authority_ref,
        "vertex_class": "composition_invariant",
    })
    for target in connect_to:
        p["edges"].append({
            "source": hub_id,
            "target": target,
            "reason": reason,
            "weight": 1.0,
        })
    return p


def _add_community_nodes(
    proj: dict[str, Any],
    communities: list[dict[str, Any]],
) -> dict[str, Any]:
    """Add multiple community hub nodes, each connecting to a subset of vertices."""
    p = copy.deepcopy(proj)
    for comm in communities:
        p["vertices"].append({
            "vertex_id": comm["id"],
            "label": comm["label"],
            "authority_source_ref": comm["authority_ref"],
            "vertex_class": "claim_class_hub",
        })
        for target in comm["members"]:
            p["edges"].append({
                "source": comm["id"],
                "target": target,
                "reason": comm["reason"],
                "weight": 1.0,
            })
    return p


# ---------------------------------------------------------------------------
# Build experiment catalogue
# ---------------------------------------------------------------------------

def build_experiments(proj: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    deg = _vertex_degrees(proj)
    sorted_by_deg = sorted(deg.items(), key=lambda x: -x[1])
    top1 = sorted_by_deg[0][0]   # degree-21 hub
    top2 = sorted_by_deg[1][0]   # degree-14 hub
    top3 = sorted_by_deg[2][0]   # degree-11 hub

    # All vertex ids
    all_v = [v["vertex_id"] for v in proj["vertices"]]

    # Degree-2 nodes (chain/consequence nodes)
    deg2_nodes = [v for v, d in deg.items() if d == 2]
    # derives_from edge sources
    derives_sources = list({e["source"] for e in proj["edges"] if e.get("reason") == "derives_from"})
    # invokes_primitive edge sources
    invokes_sources = list({e["source"] for e in proj["edges"] if e.get("reason") == "invokes_primitive"})

    # Rough community split by prefix
    epistemic = [v for v in all_v if any(
        k in v for k in ("adr_00", "axiom", "truth_primitive_assert", "truth_primitive_link")
    )]
    temporal = [v for v in all_v if any(
        k in v for k in ("commit_epoch", "temporal", "provenance", "history")
    )]
    economic = [v for v in all_v if any(
        k in v for k in ("policy", "accrual", "governance", "ecu", "economic")
    )]

    experiments: list[tuple[str, dict[str, Any]]] = []

    # --- Baseline (no change) ---
    experiments.append(("baseline (no change)", copy.deepcopy(proj)))

    # --- Subtractions ---
    experiments.append((
        f"remove top hub (deg {sorted_by_deg[0][1]}): {top1[:50]}",
        _remove_vertex(proj, top1),
    ))
    experiments.append((
        f"remove 2nd hub (deg {sorted_by_deg[1][1]}): {top2[:50]}",
        _remove_vertex(proj, top2),
    ))
    experiments.append((
        f"remove top 2 hubs",
        _remove_vertex(_remove_vertex(proj, top1), top2),
    ))
    experiments.append((
        f"remove top 3 hubs",
        _remove_vertex(_remove_vertex(_remove_vertex(proj, top1), top2), top3),
    ))

    # --- Add isolated node (control — should not help) ---
    p_iso = copy.deepcopy(proj)
    p_iso["vertices"].append({
        "vertex_id": "research:isolated_control",
        "label": "isolated control node",
        "authority_source_ref": "artifact:genesis_intent_attestation_init_authority_map",
        "vertex_class": "research_control",
    })
    experiments.append(("add isolated node (control)", p_iso))

    # --- Add +1 universal hub: phi-bound invariant → all derives_from sources ---
    experiments.append((
        f"+1 phi-bound hub → all derives_from sources ({len(derives_sources)} edges)",
        _add_hub_vertex(
            proj,
            hub_id="invariant:phi_bound_composition_limit",
            label="Werner phi-bound composition invariant",
            reason="bounded_by_composition_invariant",
            connect_to=derives_sources,
            authority_ref="artifact:genesis_intent_attestation_init_authority_map",
        ),
    ))

    # --- Add +1 hub → all degree-2 chain nodes ---
    experiments.append((
        f"+1 consequence hub → all degree-2 nodes ({len(deg2_nodes)} edges)",
        _add_hub_vertex(
            proj,
            hub_id="invariant:claim_consequence_anchor",
            label="Claim consequence structural anchor",
            reason="anchors_claim_consequence",
            connect_to=deg2_nodes,
            authority_ref="artifact:genesis_intent_attestation_init_authority_map",
        ),
    ))

    # --- Add +1 hub → all invokes_primitive sources ---
    experiments.append((
        f"+1 primitive-invocation hub → invokes_primitive sources ({len(invokes_sources)} edges)",
        _add_hub_vertex(
            proj,
            hub_id="invariant:primitive_invocation_anchor",
            label="Primitive invocation structural anchor",
            reason="anchors_primitive_invocation",
            connect_to=invokes_sources,
            authority_ref="artifact:genesis_intent_attestation_init_authority_map",
        ),
    ))

    # --- Add +1 hub → top half of nodes by degree ---
    top_half = [v for v, d in sorted_by_deg[:len(all_v) // 2]]
    experiments.append((
        f"+1 hub → top-half nodes by degree ({len(top_half)} edges)",
        _add_hub_vertex(
            proj,
            hub_id="invariant:high_degree_anchor",
            label="High-degree node structural anchor",
            reason="anchors_high_degree",
            connect_to=top_half,
            authority_ref="artifact:genesis_intent_attestation_init_authority_map",
        ),
    ))

    # --- Add +1 hub → all nodes (max connectivity) ---
    experiments.append((
        f"+1 hub → ALL nodes ({len(all_v)} edges)",
        _add_hub_vertex(
            proj,
            hub_id="invariant:universal_anchor",
            label="Universal structural anchor",
            reason="universal_composition_invariant",
            connect_to=all_v,
            authority_ref="artifact:genesis_intent_attestation_init_authority_map",
        ),
    ))

    # --- Add +2 community hubs: epistemic + temporal ---
    if epistemic and temporal:
        experiments.append((
            f"+2 community hubs (epistemic {len(epistemic)}, temporal {len(temporal)})",
            _add_community_nodes(proj, [
                {
                    "id": "class:epistemic_claims",
                    "label": "Epistemic claim class hub",
                    "reason": "epistemic_class_membership",
                    "authority_ref": "adr:0004_genesis_truth_primitives",
                    "members": epistemic,
                },
                {
                    "id": "class:temporal_claims",
                    "label": "Temporal claim class hub",
                    "reason": "temporal_class_membership",
                    "authority_ref": "adr:0004_genesis_truth_primitives",
                    "members": temporal,
                },
            ]),
        ))

    # --- Add +3 community hubs: epistemic + temporal + economic ---
    if epistemic and temporal and economic:
        experiments.append((
            f"+3 community hubs (epistemic {len(epistemic)}, temporal {len(temporal)}, economic {len(economic)})",
            _add_community_nodes(proj, [
                {
                    "id": "class:epistemic_claims",
                    "label": "Epistemic claim class hub",
                    "reason": "epistemic_class_membership",
                    "authority_ref": "adr:0004_genesis_truth_primitives",
                    "members": epistemic,
                },
                {
                    "id": "class:temporal_claims",
                    "label": "Temporal claim class hub",
                    "reason": "temporal_class_membership",
                    "authority_ref": "adr:0004_genesis_truth_primitives",
                    "members": temporal,
                },
                {
                    "id": "class:economic_claims",
                    "label": "Economic claim class hub",
                    "reason": "economic_class_membership",
                    "authority_ref": "adr:0004_genesis_truth_primitives",
                    "members": economic if economic else epistemic[:3],
                },
            ]),
        ))

    # --- Remove top hub + add phi-bound hub ---
    experiments.append((
        f"remove top hub + add phi-bound hub",
        _add_hub_vertex(
            _remove_vertex(proj, top1),
            hub_id="invariant:phi_bound_composition_limit",
            label="Werner phi-bound composition invariant",
            reason="bounded_by_composition_invariant",
            connect_to=[s for s in derives_sources if s != top1],
            authority_ref="artifact:genesis_intent_attestation_init_authority_map",
        ),
    ))

    # --- Remove top 2 hubs + add phi-bound hub ---
    base_no_top2 = _remove_vertex(_remove_vertex(proj, top1), top2)
    experiments.append((
        f"remove top 2 hubs + add phi-bound hub",
        _add_hub_vertex(
            base_no_top2,
            hub_id="invariant:phi_bound_composition_limit",
            label="Werner phi-bound composition invariant",
            reason="bounded_by_composition_invariant",
            connect_to=[s for s in derives_sources if s not in (top1, top2)],
            authority_ref="artifact:genesis_intent_attestation_init_authority_map",
        ),
    ))

    return experiments


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    proj = _load_projection()
    experiments = build_experiments(proj)

    print(f"SIM-SPECTRAL-04 Auto-Research — {len(experiments)} variants")
    print(f"Seeds: {SEEDS}  |  Epochs: {EPOCHS}  |  k: {K}")
    print(f"Gate thresholds: S3/S1 < {S3_S1_THRESHOLD:.4f},  G2/S1 < {G2_S1_THRESHOLD:.4f}")
    print(f"{'─' * 90}")
    print(f"{'Variant':<55} {'nodes':>5} {'edges':>5} {'maxS3/S1':>9} {'maxG2/S1':>9} {'S3ok':>5} {'G2ok':>5} {'gate':>6}")
    print(f"{'─' * 90}")

    results: list[dict[str, Any]] = []
    for name, variant in experiments:
        n = len(variant["vertices"])
        e = len(variant["edges"])
        try:
            gate_result = run_gate(variant)
        except Exception as exc:
            print(f"  {'ERR':<52} {n:5d} {e:5d}   ERROR: {exc}")
            continue

        s3_ok = "✓" if gate_result["s3_pass"] else "✗"
        g2_ok = "✓" if gate_result["g2_pass"] else "✗"
        gate = gate_result["gate"]
        max_s3 = gate_result["max_s3_s1"]
        max_g2 = gate_result["max_g2_s1"]

        flag = " ◄ PASS" if gate == "PASS" else ""
        print(f"  {name:<53} {n:5d} {e:5d} {max_s3:9.4f} {max_g2:9.4f} {s3_ok:>5} {g2_ok:>5} {gate:>6}{flag}")
        results.append({"name": name, "nodes": n, "edges": e, **gate_result})

    print(f"{'─' * 90}")
    passes = [r for r in results if r["gate"] == "PASS"]
    print(f"\nSummary: {len(passes)}/{len(results)} variants pass the gate.")
    if passes:
        print("\nPassing variants:")
        for r in passes:
            print(f"  [{r['nodes']}n {r['edges']}e] {r['name']}")

    # Save results
    out_path = Path("out/sim_spectral_04_auto_research_results.json")
    out_path.write_text(
        json.dumps({"experiments": results}, sort_keys=True, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print(f"\nFull results → {out_path}")


if __name__ == "__main__":
    main()
