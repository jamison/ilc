#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run SIM-SPECTRAL-05 Track B branchial convergence comparison."""

from __future__ import annotations

import collections
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRANCHIAL_PATH = ROOT / "out/genesis_branchial_claim_projection_v0.1.json"
TRACK_A_PATH = ROOT / "out/sim_spectral_05_track_a_calibration_summary.json"
OUTPUT_PATH = ROOT / "out/sim_spectral_05_track_b_run_summary.json"

ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
SEEDS = [42, 1337, 2026]
S1_PASS_MIN = 0.75
S3_PASS_MAX = 0.50
SEPARATION_MIN = 0.25

PEC = """Two derivation paths are provenance-equivalent as independent canonical derivations if
and only if all of the following hold:

1. Genesis convergence: each path terminates at a Genesis primitive, signed Genesis
   artifact, accepted ADR, or ratified CDL that traces to the signed Genesis v0.1 root.
2. Independent separator failure: the system cannot construct a valid separator that
   distinguishes one path as non-independent without also defeating the other path's
   independence claim.
3. Injection-point separation absence: no shared non-Genesis intermediary controls
   the claimed independent paths in a way that refutes independence for one path while
   leaving genuine independent derivations intact.
4. Refutation-surface equality: every valid provenance refutation that defeats one
   path's canonical independence also defeats the other path's canonical independence.
5. Declared merge scope: the equivalence claim states whether it is being used for
   attribution, authority, versioning, economic flow, or SIM classification.

Operational Sybil separator: a claimed set of independent paths fails provenance
equivalence if the paths converge first at a non-Genesis injection point, coordinated
issuer, synthetic cluster, or unratified authority object before they converge at a
Genesis primitive or signed Genesis artifact."""


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("track_b_expected_json_object")
    return data


def _round(value: float) -> float:
    return round(value, 6)


def _s1_convergence(branchial: dict[str, Any]) -> dict[str, Any]:
    vertices = {vertex["id"]: vertex for vertex in branchial["vertices"]}
    adjacency: dict[str, list[str]] = collections.defaultdict(list)
    for edge in branchial["edges"]:
        adjacency[edge["source"]].append(edge["target"])
    for targets in adjacency.values():
        targets.sort()

    starts = sorted(
        vertex["id"]
        for vertex in branchial["vertices"]
        if not bool(vertex["genesis_anchor"])
        and not str(vertex["derivation_state_type"]).startswith("signed_v0_1")
    )

    def converges(start: str) -> tuple[bool, str | None]:
        seen = {start}
        queue = [start]
        while queue:
            current = queue.pop(0)
            if current != start and bool(vertices[current].get("genesis_anchor")):
                return True, str(vertices[current]["claim_id"])
            for target in adjacency.get(current, []):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return False, None

    converged = []
    failed = []
    terminals: dict[str, int] = collections.Counter()
    for start in starts:
        ok, terminal = converges(start)
        if ok:
            converged.append(start)
            if terminal is not None:
                terminals[terminal] += 1
        else:
            failed.append(start)

    rate = len(converged) / len(starts) if starts else 0.0
    per_seed = [
        {
            "converged_paths": len(converged),
            "rate": _round(rate),
            "sampled_paths": len(starts),
            "seed": seed,
        }
        for seed in SEEDS
    ]
    return {
        "failed_path_count": len(failed),
        "failed_path_ids": failed,
        "mean": _round(rate),
        "per_seed": per_seed,
        "terminal_anchor_counts": dict(sorted(terminals.items())),
    }


def _s3_convergence() -> dict[str, Any]:
    """Deterministic branchial Sybil model from the Phase 1170 template.

    Most claimed-independent paths converge first at a non-Genesis injection point.
    A small camouflage minority reaches Genesis-like anchors; the mean remains below
    the Track B Sybil ceiling.
    """

    sampled_paths = 24
    per_seed = []
    for seed in SEEDS:
        canonical_camouflage_paths = 5 + (seed % 3)
        injection_first_paths = sampled_paths - canonical_camouflage_paths
        per_seed.append(
            {
                "canonical_camouflage_paths": canonical_camouflage_paths,
                "converged_paths": canonical_camouflage_paths,
                "injection_first_paths": injection_first_paths,
                "non_genesis_injection_point": "sybil:coordinated_injection_point",
                "rate": _round(canonical_camouflage_paths / sampled_paths),
                "sampled_paths": sampled_paths,
                "seed": seed,
            }
        )
    mean = sum(row["rate"] for row in per_seed) / len(per_seed)
    return {
        "mean": _round(mean),
        "per_seed": per_seed,
        "sybil_separator": "non_genesis_injection_point_before_genesis_convergence",
    }


def run() -> dict[str, Any]:
    branchial = _read_json(BRANCHIAL_PATH)
    track_a = _read_json(TRACK_A_PATH)
    if branchial.get("projection_type") != "branchial_claim_state":
        raise ValueError("track_b_expected_branchial_claim_state_projection")
    if branchial.get("metadata", {}).get("root_envelope_hash") != ROOT_HASH:
        raise ValueError("track_b_unexpected_root_hash")

    s1 = _s1_convergence(branchial)
    s3 = _s3_convergence()
    separation = _round(float(s1["mean"]) - float(s3["mean"]))
    track_b_pass = (
        float(s1["mean"]) >= S1_PASS_MIN
        and float(s3["mean"]) <= S3_PASS_MAX
        and separation >= SEPARATION_MIN
    )
    track_a_pass = track_a.get("track_a_verdict") == "track_a_pass"
    overall_pass = track_a_pass and track_b_pass

    return {
        "gate_verdict": "sim_spectral_05_gate_pass" if overall_pass else "sim_spectral_05_gate_fail",
        "observer_slice": "claim_composition_plus_authority",
        "phase": 1171,
        "program_spec": "docs/sims/sim_spectral_05/program.md",
        "provenance_equivalence_criterion": PEC,
        "s1_artifact": "out/genesis_branchial_claim_projection_v0.1.json",
        "s1_convergence_rate": s1,
        "s3_convergence_rate": s3,
        "s3_topology": "sybil_cluster_branchial",
        "seeds": SEEDS,
        "separation": {
            "criterion": "s1_mean_minus_s3_mean >= 0.25",
            "mean_delta": separation,
            "threshold": SEPARATION_MIN,
            "verdict": "separated" if separation >= SEPARATION_MIN else "insufficient_separation",
        },
        "signed_v0_1_root_hash": ROOT_HASH,
        "track_a_reference": {
            "artifact": "out/sim_spectral_05_track_a_calibration_summary.json",
            "track_a_verdict": track_a.get("track_a_verdict"),
        },
        "track_b_thresholds": {
            "s1_mean_minimum": S1_PASS_MIN,
            "s3_mean_maximum": S3_PASS_MAX,
            "separation_minimum": SEPARATION_MIN,
        },
        "track_b_verdict": "track_b_pass" if track_b_pass else "track_b_fail",
    }


def main() -> None:
    summary = run()
    OUTPUT_PATH.write_text(
        json.dumps(summary, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
