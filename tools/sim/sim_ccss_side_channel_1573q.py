#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1573q CCSS side-channel traffic-analysis simulation.

This script is simulation-only. It is not imported by runtime paths and does
not activate CCSS-SPECTRAL, public relay serving, public RC, or any guard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


SEED = 1573
N_VALUES = (100, 500, 1000)
T_OBS_VALUES = (5, 20, 50)
TRIALS = 32
MAX_TIMING_CANDIDATES = 128
ROUTE_PURPOSES = ("bootstrap", "direct-message", "query", "relay")
SIZE_CLASSES = ("tiny", "small", "medium", "large")
VERDICT_REQUIRES_COVER_BATCHING = "sim_requires_cover_batching_before_stronger_claim"
RECOMMENDED_POLICY_TOKEN = "ccss_pre_rc_cover_batch_profile_v1_candidate"


@dataclass(frozen=True)
class Profile:
    offset: float
    interval: float
    size_class: str
    route_purpose: str
    relay_path: tuple[int, ...]


@dataclass(frozen=True)
class MitigationCandidate:
    name: str
    batch_window_seconds: int
    min_batch_anonymity_set: int
    fixed_bundle: bool
    route_purpose_visible: bool
    rotate_paths: bool
    cover_ratio: int


MITIGATION_CANDIDATES = (
    MitigationCandidate(
        name="current_no_cover_no_batch",
        batch_window_seconds=0,
        min_batch_anonymity_set=1,
        fixed_bundle=False,
        route_purpose_visible=True,
        rotate_paths=False,
        cover_ratio=0,
    ),
    MitigationCandidate(
        name="fixed_bundle_only",
        batch_window_seconds=0,
        min_batch_anonymity_set=1,
        fixed_bundle=True,
        route_purpose_visible=True,
        rotate_paths=False,
        cover_ratio=0,
    ),
    MitigationCandidate(
        name="batch_fixed_bundle_concealed_purpose",
        batch_window_seconds=120,
        min_batch_anonymity_set=64,
        fixed_bundle=True,
        route_purpose_visible=False,
        rotate_paths=False,
        cover_ratio=4,
    ),
    MitigationCandidate(
        name=RECOMMENDED_POLICY_TOKEN,
        batch_window_seconds=120,
        min_batch_anonymity_set=128,
        fixed_bundle=True,
        route_purpose_visible=False,
        rotate_paths=True,
        cover_ratio=8,
    ),
)


def _stable_seed(*parts: Any) -> int:
    payload = json.dumps(parts, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest()[:16], 16)


def _profiles(n: int, relay_count: int, *, seed: int) -> list[Profile]:
    rng = random.Random(seed)
    profiles: list[Profile] = []
    for agent_index in range(n):
        relay_path = tuple(
            sorted(rng.sample(range(max(relay_count * 8, 16)), k=relay_count))
        )
        profiles.append(
            Profile(
                offset=rng.uniform(0.0, 60.0),
                interval=rng.uniform(25.0, 180.0),
                size_class=SIZE_CLASSES[agent_index % len(SIZE_CLASSES)],
                route_purpose=ROUTE_PURPOSES[agent_index % len(ROUTE_PURPOSES)],
                relay_path=relay_path,
            )
        )
    return profiles


def _target_times(profile: Profile, t_obs: int, *, rng: random.Random, jitter: float) -> list[float]:
    return [
        profile.offset + (profile.interval * step) + rng.gauss(0.0, jitter)
        for step in range(t_obs)
    ]


def _batch_times(times: list[float], window_seconds: float) -> list[float]:
    if window_seconds <= 0:
        return times
    return [round(value / window_seconds) * window_seconds for value in times]


def _timing_match(
    profiles: list[Profile],
    target_index: int,
    t_obs: int,
    *,
    rng: random.Random,
    jitter: float,
    batch_window_seconds: float,
) -> bool:
    observed = _batch_times(
        _target_times(profiles[target_index], t_obs, rng=rng, jitter=jitter),
        batch_window_seconds,
    )
    candidate_indices = list(range(len(profiles)))
    if len(candidate_indices) > MAX_TIMING_CANDIDATES:
        distractors = [idx for idx in candidate_indices if idx != target_index]
        candidate_indices = [target_index] + rng.sample(
            distractors,
            k=MAX_TIMING_CANDIDATES - 1,
        )
    best_index = -1
    best_score = math.inf
    for candidate_index in candidate_indices:
        profile = profiles[candidate_index]
        expected = _batch_times(
            [profile.offset + (profile.interval * step) for step in range(t_obs)],
            batch_window_seconds,
        )
        score = mean(abs(obs - exp) for obs, exp in zip(observed, expected))
        if score < best_score:
            best_score = score
            best_index = candidate_index
    return best_index == target_index


def _estimate_timing_linking_probability(
    n: int,
    t_obs: int,
    *,
    batch_window_seconds: float,
    seed: int,
) -> float:
    rng = random.Random(seed)
    profiles = _profiles(n, relay_count=3, seed=seed + 1)
    successes = 0
    for trial in range(TRIALS):
        target_index = rng.randrange(n)
        if _timing_match(
            profiles,
            target_index,
            t_obs,
            rng=rng,
            jitter=1.5,
            batch_window_seconds=batch_window_seconds,
        ):
            successes += 1
    return successes / TRIALS


def _estimate_size_linking_probability(n: int, *, fixed_bundle: bool) -> float:
    if fixed_bundle:
        return 1.0 / n
    # Four coarse classes leak approximately log2(4) bits under a uniform class
    # distribution. Within the class, the adversary still has no token signal.
    return min(1.0, 4.0 / n)


def _estimate_route_purpose_linking_probability(n: int, *, purpose_visible: bool) -> float:
    if not purpose_visible:
        return 1.0 / n
    return min(1.0, len(ROUTE_PURPOSES) / n)


def _estimate_relay_overlap_probability(
    n: int,
    t_obs: int,
    *,
    relay_count: int,
    rotate_paths: bool,
    seed: int,
) -> float:
    rng = random.Random(seed)
    profiles = _profiles(n, relay_count=relay_count, seed=seed + 11)
    successes = 0
    for _trial in range(TRIALS):
        target_index = rng.randrange(n)
        if rotate_paths:
            # Path rotation makes relay overlap non-stable in this model; the
            # adversary falls back to the no-token-signal baseline.
            successes += 1 if rng.random() < (1.0 / n) else 0
            continue
        target_path = set(profiles[target_index].relay_path)
        best_index = max(
            range(n),
            key=lambda idx: len(target_path.intersection(profiles[idx].relay_path)),
        )
        successes += int(best_index == target_index)
    return successes / TRIALS


def _configured_anonymity_bound(n: int, candidate: MitigationCandidate) -> float:
    if candidate.min_batch_anonymity_set <= 1:
        return 1.0
    cover_amplified_set = candidate.min_batch_anonymity_set * (candidate.cover_ratio + 1)
    return 1.0 / min(n, cover_amplified_set)


def _candidate_worst_linking_probability(
    n: int,
    candidate: MitigationCandidate,
    *,
    unmitigated_timing: float,
    unmitigated_relay: float,
) -> dict[str, float]:
    anonymity_bound = _configured_anonymity_bound(n, candidate)
    timing = (
        min(unmitigated_timing, anonymity_bound)
        if candidate.batch_window_seconds > 0
        else unmitigated_timing
    )
    size = _estimate_size_linking_probability(n, fixed_bundle=candidate.fixed_bundle)
    route = _estimate_route_purpose_linking_probability(
        n,
        purpose_visible=candidate.route_purpose_visible,
    )
    relay = (
        min(unmitigated_relay, 1.0 / n)
        if candidate.rotate_paths
        else unmitigated_relay
    )
    return {
        "timing": timing,
        "message_size": size,
        "route_purpose": route,
        "relay_overlap": relay,
        "worst": max(timing, size, route, relay),
        "no_signal_baseline": 1.0 / n,
        "configured_anonymity_bound": anonymity_bound,
    }


def run_simulation() -> dict[str, Any]:
    timing_points: list[dict[str, Any]] = []
    relay_points: list[dict[str, Any]] = []
    size_points: list[dict[str, Any]] = []
    route_purpose_points: list[dict[str, Any]] = []
    mixed_population_points: list[dict[str, Any]] = []
    candidate_points: list[dict[str, Any]] = []

    for n in N_VALUES:
        baseline = 1.0 / n
        for t_obs in T_OBS_VALUES:
            for batch_window_seconds in (0.0, 30.0, 120.0):
                timing_points.append(
                    {
                        "n": n,
                        "t_obs": t_obs,
                        "batch_window_seconds": batch_window_seconds,
                        "linking_probability": _estimate_timing_linking_probability(
                            n,
                            t_obs,
                            batch_window_seconds=batch_window_seconds,
                            seed=_stable_seed("timing", n, t_obs, batch_window_seconds, SEED),
                        ),
                        "no_signal_baseline": baseline,
                    }
                )
            for relay_count in (1, 3, 5):
                relay_points.append(
                    {
                        "n": n,
                        "t_obs": t_obs,
                        "relay_count": relay_count,
                        "rotate_paths": False,
                        "linking_probability": _estimate_relay_overlap_probability(
                            n,
                            t_obs,
                            relay_count=relay_count,
                            rotate_paths=False,
                            seed=_stable_seed("relay", n, t_obs, relay_count, False, SEED),
                        ),
                        "no_signal_baseline": baseline,
                    }
                )
                relay_points.append(
                    {
                        "n": n,
                        "t_obs": t_obs,
                        "relay_count": relay_count,
                        "rotate_paths": True,
                        "linking_probability": _estimate_relay_overlap_probability(
                            n,
                            t_obs,
                            relay_count=relay_count,
                            rotate_paths=True,
                            seed=_stable_seed("relay", n, t_obs, relay_count, True, SEED),
                        ),
                        "no_signal_baseline": baseline,
                    }
                )

        size_points.append(
            {
                "n": n,
                "fixed_bundle": False,
                "linking_probability": _estimate_size_linking_probability(
                    n,
                    fixed_bundle=False,
                ),
                "no_signal_baseline": baseline,
            }
        )
        size_points.append(
            {
                "n": n,
                "fixed_bundle": True,
                "linking_probability": _estimate_size_linking_probability(
                    n,
                    fixed_bundle=True,
                ),
                "no_signal_baseline": baseline,
            }
        )
        route_purpose_points.append(
            {
                "n": n,
                "purpose_visible": True,
                "linking_probability": _estimate_route_purpose_linking_probability(
                    n,
                    purpose_visible=True,
                ),
                "no_signal_baseline": baseline,
            }
        )
        route_purpose_points.append(
            {
                "n": n,
                "purpose_visible": False,
                "linking_probability": _estimate_route_purpose_linking_probability(
                    n,
                    purpose_visible=False,
                ),
                "no_signal_baseline": baseline,
            }
        )
        mixed_population_points.append(
            {
                "n": n,
                "adversary_knows_observation_grouping": False,
                "candidate_set_multiplier": 20,
                "linking_probability": min(1.0, 4.0 / (n * 20.0)),
                "no_signal_baseline": baseline,
                "interpretation": "mixed traffic helps when grouping is unknown, but visible size or route-purpose classes still leak cohort information",
            }
        )
        worst_unmitigated_timing_n = max(
            point["linking_probability"]
            for point in timing_points
            if point["n"] == n and point["batch_window_seconds"] == 0.0
        )
        worst_unmitigated_relay_n = max(
            point["linking_probability"]
            for point in relay_points
            if point["n"] == n and point["rotate_paths"] is False
        )
        for candidate in MITIGATION_CANDIDATES:
            metrics = _candidate_worst_linking_probability(
                n,
                candidate,
                unmitigated_timing=worst_unmitigated_timing_n,
                unmitigated_relay=worst_unmitigated_relay_n,
            )
            candidate_points.append(
                {
                    "n": n,
                    "candidate": candidate.name,
                    "batch_window_seconds": candidate.batch_window_seconds,
                    "min_batch_anonymity_set": candidate.min_batch_anonymity_set,
                    "fixed_bundle": candidate.fixed_bundle,
                    "route_purpose_visible": candidate.route_purpose_visible,
                    "rotate_paths": candidate.rotate_paths,
                    "cover_ratio": candidate.cover_ratio,
                    **metrics,
                }
            )

    worst_timing = max(point["linking_probability"] for point in timing_points)
    worst_size = max(point["linking_probability"] for point in size_points)
    worst_route = max(point["linking_probability"] for point in route_purpose_points)
    worst_relay = max(point["linking_probability"] for point in relay_points)
    recommended_points = [
        point for point in candidate_points if point["candidate"] == RECOMMENDED_POLICY_TOKEN
    ]
    recommended_worst = max(point["worst"] for point in recommended_points)
    result = {
        "schema_version": "ilc_ccss_side_channel_sim_1573q.v0.1",
        "phase": "1573q",
        "seed": SEED,
        "verdict": VERDICT_REQUIRES_COVER_BATCHING,
        "non_claim": "SIM evidence does not constitute formal anonymity, differential privacy, full unlinkability, or Signal-equivalent sealed sender.",
        "parameter_grid": {
            "n_values": list(N_VALUES),
            "t_obs_values": list(T_OBS_VALUES),
            "trials": TRIALS,
            "max_timing_candidates": MAX_TIMING_CANDIDATES,
            "route_purposes": list(ROUTE_PURPOSES),
            "size_classes": list(SIZE_CLASSES),
        },
        "surfaces": {
            "timing_correlation": timing_points,
            "message_size_class": size_points,
            "route_purpose": route_purpose_points,
            "relay_overlap": relay_points,
            "mixed_population_unknown_grouping": mixed_population_points,
            "mitigation_candidates": candidate_points,
        },
        "summary": {
            "worst_timing_linking_probability": worst_timing,
            "worst_size_class_linking_probability": worst_size,
            "worst_route_purpose_linking_probability": worst_route,
            "worst_relay_overlap_linking_probability": worst_relay,
            "recommended_policy": RECOMMENDED_POLICY_TOKEN,
            "recommended_policy_worst_linking_probability": recommended_worst,
            "recommended_policy_max_configured_bound": max(
                point["configured_anonymity_bound"] for point in recommended_points
            ),
            "requires_cover_traffic": True,
            "requires_batching_or_mixing": True,
            "requires_fixed_bundle_or_size_class_policy": True,
            "requires_relay_path_rotation_or_path_hiding": True,
            "supports_1573o_boundary": True,
            "supports_stronger_anonymity_claim": False,
            "supports_configured_anonymity_set_claim_with_1573r_design": True,
        },
        "recommended_controls_for_1573r": {
            "policy_token": RECOMMENDED_POLICY_TOKEN,
            "batch_window_seconds": 120,
            "min_batch_anonymity_set": 128,
            "cover_ratio": 8,
            "fixed_bundle": True,
            "route_purpose_visible_to_relay": False,
            "relay_path_rotation": True,
            "ttl_required": True,
            "offline_mailbox_policy_required": True,
            "claim_shape": "configured_anonymity_set_and_metadata_minimization_claim_only",
        },
        "non_authorizations": {
            "public_rc": False,
            "public_relay_serving": False,
            "formal_dp_claim": False,
            "network_anonymity_claim": False,
            "guard_clearance": False,
        },
    }
    return result


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    text = f"""# ILC CCSS Side-Channel SIM 1573q v0.1

**Phase:** 1573q
**Seed:** {result["seed"]}
**Verdict:** `{result["verdict"]}`

## Summary

This simulation evaluates relay-observable side channels that remain after
SpectralRouteToken removes raw spectral values from relay-visible envelopes.
It supports the Phase 1573o narrow non-disclosure boundary, but it does not
support stronger public-RC anonymity or formal DP claims.

| Metric | Value |
| --- | --- |
| Worst timing-correlation linking probability | {summary["worst_timing_linking_probability"]:.6f} |
| Worst size-class linking probability | {summary["worst_size_class_linking_probability"]:.6f} |
| Worst route-purpose linking probability | {summary["worst_route_purpose_linking_probability"]:.6f} |
| Worst relay-overlap linking probability | {summary["worst_relay_overlap_linking_probability"]:.6f} |
| Recommended policy | `{summary["recommended_policy"]}` |
| Recommended policy worst modeled linking probability | {summary["recommended_policy_worst_linking_probability"]:.6f} |
| Recommended policy max configured anonymity bound | {summary["recommended_policy_max_configured_bound"]:.6f} |

## Interpretation

The opaque route token removes the stable spectral signal, but traffic-analysis
surfaces remain. Timing, route-purpose, message-size class, and relay-path
overlap can provide cohort-level or direct linking evidence depending on
deployment choices. Mixed population traffic helps when an adversary cannot
group observations, but it does not remove the need for cover traffic,
batching or mixing, size policy, and relay-path controls.

## Recommended Pre-RC Candidate

The best candidate in this sweep is
`{result["recommended_controls_for_1573r"]["policy_token"]}`:

- 120-second release batch window
- minimum batch anonymity set of 128
- cover ratio of 8 cover bundles per real bundle where natural traffic is low
- fixed-size bundles
- route purpose concealed from relays
- relay-path rotation
- explicit TTL and offline-recipient mailbox policy

This supports a configured anonymity-set and metadata-minimization design
target for Phase 1573r. It still does not prove network anonymity against a
global observer.

## Required Follow-Up

- Phase 1573r must specify cover traffic, batching or mixing, fixed bundle or
  coarse size policy, relay-path rotation or hiding, and TTL/offline-recipient
  handling before any stronger network-anonymity claim is allowed.
- Phase 1574 must preserve the non-proof boundary unless later evidence
  explicitly clears these side-channel constraints.

## Non-Claims

This SIM does not prove formal `(epsilon, delta)` differential privacy,
network anonymity, full unlinkability, timing immunity, size-class immunity,
Signal-equivalent sealed sender, public relay activation, or public RC.
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    result = run_simulation()
    json_path = Path(args.output_json)
    md_path = Path(args.output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(result, md_path)
    print(json.dumps({"ok": True, "verdict": result["verdict"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
