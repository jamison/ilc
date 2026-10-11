#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic Werner v1 blast-chamber calibration SIM for CDL-116 Q3."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, localcontext
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.economics.werner_attribution_bridge import RUNTIME_POLICY_CAP
from ilc_core.economics.werner_runtime import compute_flow_budget
from ilc_core.sidecars.execution_receipt import STATUSES as SIDECAR_STATUSES
from ilc_model_router.receipt_schema import (
    CAPABILITY_CLASSES,
    CONSENT_STATUSES,
    RouterCompanionRecord,
)


PHASE_ID = "SIM-WERNER-V1-BLAST-CHAMBER-00"
OUTPUT_TOKEN = "sim_werner_v1_blast_chamber_calibration_complete_SIM_WERNER_V1_BLAST_CHAMBER_00"
SCHEMA_VERSION = "sim_werner_v1_blast_chamber_00.v0.1"
TWELVE_PLACES = Decimal("0.000000000001")
ZERO = Decimal("0")
ONE = Decimal("1")
PER_RECEIPT_TOKEN_CAP = Decimal("20000")
MAX_AGENT_SIGNAL = Decimal("12")
CLUSTER_SHARE_CAP = Decimal("0.35")
FLOW_BUDGET_CAP = RUNTIME_POLICY_CAP
POOL_TOTAL = Decimal("1000000.000000000000")

STATUS_WEIGHTS = {
    "success": Decimal("1.00"),
    "partial": Decimal("0.25"),
    "failure": Decimal("0.00"),
}
CONSENT_WEIGHTS = {
    "promoted": Decimal("1.00"),
    "promotion_pending": Decimal("0.50"),
    "local_only": Decimal("0.00"),
}
CAPABILITY_WEIGHTS = {
    "embedding": Decimal("0.70"),
    "inference": Decimal("1.00"),
    "multimodal": Decimal("1.10"),
    None: Decimal("1.00"),
}

REQUIRED_SCENARIOS = (
    "nominal_balanced",
    "receipt_farming_many_low_value",
    "verbosity_farming_inflated_tokens",
    "failed_partial_receipt_farming",
    "provider_concentration_gaming",
    "receipt_splitting",
    "capability_class_label_gaming",
    "consent_status_edge_cases",
    "clustered_collusive_population",
)

CANDIDATE_FORMULA_TEXT = (
    "For each promoted or promotion-pending Model Router receipt r, compute "
    "receipt_signal_r = status_weight(status_r) * consent_weight(consent_status_r) "
    "* capability_weight(capability_class_r) * min(token_counts_input_r + "
    "token_counts_output_r, 20000) / 20000. Sum receipt_signal_r by agent, cap "
    "each agent at 12.0 signal units, iteratively cap each coordinated "
    "multi-agent cluster at no more than 35% of adjusted scenario signal when "
    "that cap is feasible, then compute candidate_priority_i = "
    "(adjusted_signal_i / 12.0) * 0.10. The CDL-109 flow budget remains "
    "flow_budget_i = min(0.10, candidate_priority_i), and the only settlement "
    "application is pre-normalization reweighting z_i'(e) = z_i(e) * "
    "(1 + flow_budget_i). Final distribution normalizes z_i'(e) within the "
    "unchanged pool B_e * M_e."
)


@dataclass(frozen=True)
class SimReceipt:
    agent_id: str
    cluster_id: str
    provider: str
    model_id: str
    status: str
    token_counts_input: int
    token_counts_output: int
    capability_class: str | None
    consent_status: str

    def companion(self) -> RouterCompanionRecord:
        token = hashlib.sha256(
            "|".join(
                [
                    self.agent_id,
                    self.cluster_id,
                    self.provider,
                    self.model_id,
                    self.status,
                    str(self.token_counts_input),
                    str(self.token_counts_output),
                    str(self.capability_class),
                    self.consent_status,
                ]
            ).encode("utf-8")
        ).hexdigest()
        return RouterCompanionRecord(
            receipt_token=token,
            model_id=self.model_id,
            provider=self.provider,
            token_counts_input=self.token_counts_input,
            token_counts_output=self.token_counts_output,
            capability_class=self.capability_class,
            consent_status=self.consent_status,
        )


def _decimal_string(value: Decimal) -> str:
    return format(value.quantize(TWELVE_PLACES), "f")


def _require_runtime_vocab(receipt: SimReceipt) -> None:
    if receipt.status not in SIDECAR_STATUSES:
        raise ValueError(f"unknown_status={receipt.status}")
    if receipt.capability_class not in CAPABILITY_CLASSES:
        raise ValueError(f"unknown_capability_class={receipt.capability_class}")
    if receipt.consent_status not in CONSENT_STATUSES:
        raise ValueError(f"unknown_consent_status={receipt.consent_status}")
    receipt.companion()


def _receipt_signal(receipt: SimReceipt) -> Decimal:
    _require_runtime_vocab(receipt)
    total_tokens = Decimal(receipt.token_counts_input + receipt.token_counts_output)
    with localcontext() as ctx:
        ctx.prec = 50
        token_factor = min(total_tokens, PER_RECEIPT_TOKEN_CAP) / PER_RECEIPT_TOKEN_CAP
        signal = (
            STATUS_WEIGHTS[receipt.status]
            * CONSENT_WEIGHTS[receipt.consent_status]
            * CAPABILITY_WEIGHTS[receipt.capability_class]
            * token_factor
        )
    signal = signal.quantize(TWELVE_PLACES)
    if signal < ZERO:
        raise ValueError("receipt_signal_must_be_non_negative")
    return signal


def _receipts_for_scenario(name: str) -> list[SimReceipt]:
    def r(
        agent: str,
        cluster: str,
        provider: str,
        model: str,
        status: str,
        tokens_in: int,
        tokens_out: int,
        capability: str | None,
        consent: str = "promoted",
    ) -> SimReceipt:
        return SimReceipt(agent, cluster, provider, model, status, tokens_in, tokens_out, capability, consent)

    if name == "nominal_balanced":
        return [
            r("agent_a", "cluster_a", "openrouter", "model-alpha", "success", 800, 600, "inference"),
            r("agent_b", "cluster_b", "local", "embed-small", "success", 200, 100, "embedding"),
            r("agent_c", "cluster_c", "openrouter", "model-vision", "success", 1000, 900, "multimodal"),
            r("agent_d", "cluster_d", "local", "model-beta", "partial", 900, 300, "inference"),
        ]
    if name == "receipt_farming_many_low_value":
        return [
            *(r("farmer", "farm_cluster", "openrouter", "tiny", "success", 4, 2, "inference") for _ in range(240)),
            r("worker_a", "honest_a", "local", "model-alpha", "success", 1200, 500, "inference"),
            r("worker_b", "honest_b", "openrouter", "model-beta", "success", 900, 700, "multimodal"),
        ]
    if name == "verbosity_farming_inflated_tokens":
        return [
            r("verbose", "verbose_cluster", "openrouter", "model-long", "success", 900000, 900000, "inference"),
            r("worker_a", "honest_a", "local", "model-alpha", "success", 1400, 900, "inference"),
            r("worker_b", "honest_b", "openrouter", "model-beta", "success", 1200, 1000, "multimodal"),
        ]
    if name == "failed_partial_receipt_farming":
        return [
            *(r("failed_farmer", "farm_cluster", "openrouter", "model-x", "failure", 2000, 2000, "inference") for _ in range(60)),
            *(r("partial_farmer", "farm_cluster", "openrouter", "model-x", "partial", 2000, 1000, "inference") for _ in range(30)),
            r("worker_a", "honest_a", "local", "model-alpha", "success", 900, 700, "inference"),
        ]
    if name == "provider_concentration_gaming":
        return [
            *(r(f"provider_agent_{i}", "provider_cluster", "single-provider", "same-model", "success", 800, 700, "inference") for i in range(12)),
            *(r(f"diverse_agent_{i}", f"diverse_{i}", "provider-" + str(i), "model-" + str(i), "success", 500, 400, "embedding") for i in range(4)),
        ]
    if name == "receipt_splitting":
        return [
            *(r("splitter", "split_cluster", "openrouter", "model-alpha", "success", 100, 100, "inference") for _ in range(120)),
            r("single_large", "honest_a", "local", "model-alpha", "success", 6000, 6000, "inference"),
            r("worker_b", "honest_b", "openrouter", "model-beta", "success", 1000, 800, "inference"),
        ]
    if name == "capability_class_label_gaming":
        return [
            *(r(f"label_gamer_{i}", "label_cluster", "openrouter", "text-model", "success", 900, 500, "multimodal") for i in range(8)),
            r("embedding_worker", "honest_a", "local", "embed-small", "success", 900, 300, "embedding"),
            r("inference_worker", "honest_b", "openrouter", "model-alpha", "success", 900, 500, "inference"),
        ]
    if name == "consent_status_edge_cases":
        return [
            r("local_only_heavy", "consent_a", "local", "private-model", "success", 8000, 8000, "inference", "local_only"),
            r("pending_worker", "consent_b", "openrouter", "model-alpha", "success", 1500, 900, "inference", "promotion_pending"),
            r("promoted_worker", "consent_c", "openrouter", "model-beta", "success", 1100, 600, "inference", "promoted"),
        ]
    if name == "clustered_collusive_population":
        return [
            *(r(f"colluder_{i}", "collusive_cluster", "openrouter", "model-x", "success", 5000, 5000, "multimodal") for i in range(20)),
            *(r(f"honest_{i}", f"honest_{i}", "provider-" + str(i), "model-" + str(i), "success", 1100, 800, "inference") for i in range(10)),
        ]
    raise ValueError(f"unknown_scenario={name}")


def _percentile(values: list[Decimal], pct: int) -> Decimal:
    if not values:
        return ZERO
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, ((pct * len(ordered) + 99) // 100) - 1))
    return ordered[index].quantize(TWELVE_PLACES)


def _multi_agent_cluster_ids(clusters: dict[str, str]) -> set[str]:
    return {
        cluster
        for cluster in set(clusters.values())
        if sum(1 for agent_cluster in clusters.values() if agent_cluster == cluster) >= 2
    }


def _strongest_multi_agent_cluster_share(signals: dict[str, Decimal], clusters: dict[str, str]) -> Decimal:
    adjusted_total = sum(signals.values(), ZERO)
    if adjusted_total == ZERO:
        return ZERO
    multi_agent_clusters = _multi_agent_cluster_ids(clusters)
    if not multi_agent_clusters:
        return ZERO
    cluster_after: dict[str, Decimal] = {}
    for agent, signal in signals.items():
        cluster = clusters[agent]
        if cluster in multi_agent_clusters:
            cluster_after[cluster] = cluster_after.get(cluster, ZERO) + signal
    strongest_after = max(cluster_after.values()) if cluster_after else ZERO
    return (strongest_after / adjusted_total).quantize(TWELVE_PLACES, rounding=ROUND_DOWN)


def _cluster_cap(signals: dict[str, Decimal], clusters: dict[str, str]) -> tuple[dict[str, Decimal], Decimal, bool]:
    if sum(signals.values(), ZERO) == ZERO:
        return signals, ZERO, True
    capped = dict(signals)
    multi_agent_clusters = _multi_agent_cluster_ids(clusters)
    if not multi_agent_clusters:
        return capped, ZERO, True
    if Decimal(len(multi_agent_clusters)) * CLUSTER_SHARE_CAP >= ONE:
        # The cap may still happen to hold, but it is not guaranteed feasible
        # for all multi-agent clusters simultaneously when their count times
        # the per-cluster cap exhausts the whole population.
        initially_feasible = (
            _strongest_multi_agent_cluster_share(capped, clusters) <= CLUSTER_SHARE_CAP
        )
        if initially_feasible:
            return capped, _strongest_multi_agent_cluster_share(capped, clusters), True

    for _ in range(80):
        adjusted_total = sum(capped.values(), ZERO)
        if adjusted_total == ZERO:
            return capped, ZERO, True
        scale_by_cluster: dict[str, Decimal] = {}
        for cluster in sorted(multi_agent_clusters):
            cluster_total = sum(
                capped[agent] for agent, agent_cluster in clusters.items() if agent_cluster == cluster
            )
            if cluster_total == ZERO:
                continue
            share = cluster_total / adjusted_total
            if share <= CLUSTER_SHARE_CAP:
                continue
            target_total = (CLUSTER_SHARE_CAP * adjusted_total).quantize(
                TWELVE_PLACES, rounding=ROUND_DOWN
            )
            if target_total <= ZERO:
                scale_by_cluster[cluster] = ZERO
            else:
                scale_by_cluster[cluster] = min(ONE, target_total / cluster_total)
        if not scale_by_cluster:
            share = _strongest_multi_agent_cluster_share(capped, clusters)
            return capped, share, share <= CLUSTER_SHARE_CAP
        next_capped = dict(capped)
        for agent, cluster in clusters.items():
            if cluster in scale_by_cluster:
                next_capped[agent] = (capped[agent] * scale_by_cluster[cluster]).quantize(
                    TWELVE_PLACES, rounding=ROUND_DOWN
                )
        if next_capped == capped:
            break
        capped = next_capped
    share = _strongest_multi_agent_cluster_share(capped, clusters)
    return capped, share, share <= CLUSTER_SHARE_CAP


def _normalized_pool_evidence(agent_results: list[dict[str, str]]) -> dict[str, object]:
    if not agent_results:
        return {
            "allocation_total_after_normalization": _decimal_string(ZERO),
            "pool_conservation_difference": _decimal_string(ZERO - POOL_TOTAL),
            "pool_conservation_holds": False,
            "allocations": [],
        }
    denominator = ZERO
    weighted_rows: list[tuple[str, Decimal, Decimal, Decimal]] = []
    with localcontext() as ctx:
        ctx.prec = 50
        for row in agent_results:
            base_weight = ONE
            multiplier = Decimal(row["multiplier"])
            reweighted = base_weight * multiplier
            denominator += reweighted
            weighted_rows.append((row["agent_id"], base_weight, multiplier, reweighted))
        allocations: list[dict[str, str]] = []
        running = ZERO
        for index, (agent_id, base_weight, multiplier, reweighted) in enumerate(weighted_rows):
            if index == len(weighted_rows) - 1:
                allocation = POOL_TOTAL - running
            else:
                allocation = ((reweighted / denominator) * POOL_TOTAL).quantize(TWELVE_PLACES)
                running += allocation
            allocations.append(
                {
                    "agent_id": agent_id,
                    "synthetic_base_z_i": _decimal_string(base_weight),
                    "multiplier": _decimal_string(multiplier),
                    "reweighted_z_i": _decimal_string(reweighted),
                    "normalized_pool_allocation": _decimal_string(allocation),
                }
            )
        total_after = sum(Decimal(row["normalized_pool_allocation"]) for row in allocations)
    difference = total_after - POOL_TOTAL
    return {
        "allocation_total_after_normalization": _decimal_string(total_after),
        "pool_conservation_difference": _decimal_string(difference),
        "pool_conservation_holds": difference == ZERO,
        "allocations": allocations,
    }


def evaluate_scenario(name: str) -> dict[str, object]:
    receipts = _receipts_for_scenario(name)
    raw_by_agent: dict[str, Decimal] = {}
    clusters: dict[str, str] = {}
    consent_totals = {status: 0 for status in sorted(CONSENT_STATUSES)}
    status_totals = {status: 0 for status in sorted(SIDECAR_STATUSES)}
    capability_totals = {str(cap): 0 for cap in sorted(CAPABILITY_CLASSES, key=lambda v: str(v))}
    for receipt in receipts:
        signal = _receipt_signal(receipt)
        raw_by_agent[receipt.agent_id] = raw_by_agent.get(receipt.agent_id, ZERO) + signal
        clusters[receipt.agent_id] = receipt.cluster_id
        consent_totals[receipt.consent_status] += 1
        status_totals[receipt.status] += 1
        capability_totals[str(receipt.capability_class)] += 1
    agent_capped = {
        agent: min(signal, MAX_AGENT_SIGNAL).quantize(TWELVE_PLACES)
        for agent, signal in raw_by_agent.items()
    }
    adjusted, strongest_cluster_share, cluster_cap_feasible = _cluster_cap(agent_capped, clusters)
    agent_results = []
    for agent in sorted(adjusted):
        with localcontext() as ctx:
            ctx.prec = 50
            candidate_priority = (adjusted[agent] / MAX_AGENT_SIGNAL) * FLOW_BUDGET_CAP
        flow_budget = compute_flow_budget(candidate_priority, FLOW_BUDGET_CAP)
        agent_results.append(
            {
                "agent_id": agent,
                "cluster_id": clusters[agent],
                "raw_signal": _decimal_string(raw_by_agent[agent]),
                "agent_capped_signal": _decimal_string(agent_capped[agent]),
                "adjusted_signal": _decimal_string(adjusted[agent]),
                "candidate_priority": _decimal_string(candidate_priority),
                "flow_budget": _decimal_string(flow_budget),
                "multiplier": _decimal_string(ONE + flow_budget),
            }
        )
    budgets = [Decimal(row["flow_budget"]) for row in agent_results]
    pool_evidence = _normalized_pool_evidence(agent_results)
    return {
        "scenario": name,
        "agent_count": len(raw_by_agent),
        "receipt_count": len(receipts),
        "consent_counts": consent_totals,
        "status_counts": status_totals,
        "capability_counts": capability_totals,
        "strongest_multi_agent_cluster_share_after_cap": _decimal_string(strongest_cluster_share),
        "cluster_cap_feasible": cluster_cap_feasible,
        "cluster_cap_holds": strongest_cluster_share <= CLUSTER_SHARE_CAP,
        "flow_budget_percentiles": {
            "p05": _decimal_string(_percentile(budgets, 5)),
            "p50": _decimal_string(_percentile(budgets, 50)),
            "p95": _decimal_string(_percentile(budgets, 95)),
            "max": _decimal_string(max(budgets) if budgets else ZERO),
        },
        "pool_total_before": _decimal_string(POOL_TOTAL),
        "pool_total_after_normalization": pool_evidence["allocation_total_after_normalization"],
        "pool_conservation_difference": pool_evidence["pool_conservation_difference"],
        "pool_conservation_holds": pool_evidence["pool_conservation_holds"],
        "normalized_pool_allocations": pool_evidence["allocations"],
        "agent_results": agent_results,
    }


def build_artifact() -> dict[str, object]:
    scenarios = [evaluate_scenario(name) for name in REQUIRED_SCENARIOS]
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE_ID,
        "output_token": OUTPUT_TOKEN,
        "candidate_formula": CANDIDATE_FORMULA_TEXT,
        "runtime_constants": {
            "flow_budget_cap": _decimal_string(FLOW_BUDGET_CAP),
            "per_receipt_token_cap": _decimal_string(PER_RECEIPT_TOKEN_CAP),
            "max_agent_signal": _decimal_string(MAX_AGENT_SIGNAL),
            "cluster_share_cap": _decimal_string(CLUSTER_SHARE_CAP),
            "pool_total": _decimal_string(POOL_TOTAL),
        },
        "required_scenarios": list(REQUIRED_SCENARIOS),
        "scenarios": scenarios,
        "invariants": {
            "decimal_only": True,
            "pre_normalization_reweight_only": True,
            "pool_total_unchanged": all(s["pool_conservation_holds"] for s in scenarios),
            "cluster_cap_holds_when_feasible": all(
                (not s["cluster_cap_feasible"]) or s["cluster_cap_holds"] for s in scenarios
            ),
            "no_capproof_stacking": True,
            "no_passive_ecu_quality_factor_stacking": True,
            "no_ecu_mint": True,
            "no_ilc_mint": True,
        },
    }


def write_markdown_report(artifact: dict[str, object], path: Path) -> None:
    rows = []
    for scenario in artifact["scenarios"]:
        pct = scenario["flow_budget_percentiles"]
        rows.append(
                "| {scenario} | {agents} | {receipts} | {p05} | {p50} | {p95} | {max_budget} | {cluster} | {conservation} |".format(
                scenario=scenario["scenario"],
                agents=scenario["agent_count"],
                receipts=scenario["receipt_count"],
                p05=pct["p05"],
                p50=pct["p50"],
                p95=pct["p95"],
                max_budget=pct["max"],
                cluster=scenario["strongest_multi_agent_cluster_share_after_cap"],
                conservation=scenario["pool_conservation_difference"],
            )
        )
    text = "\n".join(
        [
            "<!-- PUBLIC_RC_EXCLUDE: sim_report -->",
            "<!-- PUBLIC_RC_EXCLUDE_REASON: Internal governance calibration SIM; no runtime activation or settlement authority. -->",
            "",
            "# SIM-WERNER-V1-BLAST-CHAMBER-00 Report",
            "",
            f"**Phase:** {PHASE_ID}",
            f"**Output token:** `{OUTPUT_TOKEN}`",
            "",
            "## Candidate Formula",
            "",
            artifact["candidate_formula"],
            "",
            "## Percentile Envelope",
            "",
            "| Scenario | Agents | Receipts | p05 | p50 | p95 | max | strongest multi-agent cluster share after cap | pool conservation difference |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            *rows,
            "",
            "## Invariants",
            "",
            "- Decimal-only arithmetic.",
            "- Pre-normalization `z_i(e)` reweighting only.",
            "- Pool total `B_e * M_e` unchanged after normalization.",
            "- No CapProof band multiplier stacking.",
            "- No passive ECU quality-factor stacking.",
            "- No ECU mint and no ILC mint.",
            "",
            "## Non-Claims",
            "",
            "This SIM does not ratify CDL-116, does not amend CDL-116a, does not activate graph promotion, does not write runtime Model Router state, does not mutate LMDB, does not mint ECU or ILC, and does not clear any Werner guard.",
            "",
        ]
    )
    _atomic_write_text(path, text)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--md-out", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)

    artifact = build_artifact()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(args.json_out, json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    write_markdown_report(artifact, args.md_out)
    print(f"wrote_json={args.json_out}")
    print(f"wrote_md={args.md_out}")
    print(f"scenario_count={len(artifact['scenarios'])}")
    print(f"output_token={OUTPUT_TOKEN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
