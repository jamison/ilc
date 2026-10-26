#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic ECU adversarial receipt-farming SIM.

This tool models virtual adversarial receipt populations by formula and writes
the Row 21p Markdown and JSON artifacts atomically. It intentionally does not
materialize receipt bodies or touch runtime state.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PHASE = "SIM-ECU-ADVERSARIAL-RECEIPT-FARMING-00"
SCHEMA_VERSION = "sim_ecu_adversarial_receipt_farming_00.v0.1"
OUTPUT_TOKEN = "sim_ecu_adversarial_receipt_farming_complete_SIM_ECU_ADVERSARIAL_RECEIPT_FARMING_00"
DATE = "2026-10-14"


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    adversarial_goal: str
    method: str
    model_inputs: dict[str, Any]
    disposition_under_current_design: str
    undeserved_credit_possible: str
    gap_exploited: str
    proposed_hardening_gate: str
    verdict: str


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _scenarios() -> list[Scenario]:
    return [
        Scenario(
            "S1",
            "collusive_low_value_receipt_flood",
            "Convert high receipt volume into close-facing credit without genuine economic contribution.",
            "A coordinated farm submits low or zero-value service receipts at high volume, hoping volume alone becomes weight.",
            {
                "virtual_agents": 100_000,
                "receipts_per_agent": 100_000,
                "total_virtual_receipts": 10_000_000_000,
                "raw_receipts_materialized": False,
            },
            "Receipts remain evidence only; Row 21m local receipts are not settlement, minting, or wallet writes. Volume alone has no close-facing authority.",
            "conditional",
            "temporal_service_receipt_farming_guard_gap",
            "receipt_economic_admissibility_and_service_quality_gate",
            "GAPS",
        ),
        Scenario(
            "S2",
            "sybil_mutual_attestation_ring",
            "Create synthetic interactions that look mutually authorized and diverse enough to receive credit.",
            "A cluster of Sybil agents signs circular sender-authorized receipts for one another.",
            {
                "cluster_agents": 10_000,
                "ring_degree": 8,
                "synthetic_edges": 80_000,
                "sender_authorization_present": True,
            },
            "CDL-066 sender authorization is necessary but not sufficient; circular authorization does not prove genuine contribution or independent provenance.",
            "conditional",
            "temporal_sybil_diversity_floor_gap",
            "sybil_diversity_and_independent_origin_gate",
            "GAPS",
        ),
        Scenario(
            "S3",
            "service_receipt_spam",
            "Exploit service-receipt volume to inflate temporal influence, routing weight, or Werner-adjacent credit.",
            "An agent submits delivery-confirmation style service receipts far above genuine service contribution.",
            {
                "honest_baseline_receipts": 1_000,
                "spam_receipts": 10_000_000,
                "volume_multiplier": "10000",
            },
            "Row 21l already classifies service receipts as evidence, not direct minting. The farming guard remains unresolved before activation.",
            "conditional",
            "temporal_service_receipt_farming_guard_gap",
            "service_receipt_attempt_cap_and_value_evidence_gate",
            "GAPS",
        ),
        Scenario(
            "S4",
            "backward_attribution_reward_shaping",
            "Engineer superficially novel receipts to maximize CDL-108 backward-attribution score.",
            "The adversary emits many thin claims with distinct identifiers and high self-declared novelty inputs.",
            {
                "candidate_claims": 1_000_000,
                "cdl_108_max_depth": 3,
                "cdl_108_per_node_cap": "0.05",
                "cdl_108_per_agent_cap": "0.10",
                "cdl_108_per_cluster_cap": "0.25",
            },
            "CDL-108 caps and duplicate collapse bound event-local extraction, but activation still needs root-committed novelty and source-quality evidence.",
            "conditional",
            "backward_attribution_novelty_evidence_binding_gap",
            "root_committed_novelty_and_quality_evidence_gate",
            "GAPS",
        ),
        Scenario(
            "S5",
            "shard_boundary_replay_same_nullifier",
            "Receive duplicate credit by replaying the same source event into multiple shards.",
            "The same receipt is submitted to multiple shards with different shard_id values.",
            {
                "shards_targeted": 1_000,
                "receipt_nullifier_scope": "global",
                "shard_id_in_nullifier_preimage": False,
            },
            "Row 21m excludes shard_id from the nullifier preimage; Row 21n proves duplicate_credit_amount is 0 for identical nullifiers across shards.",
            "no",
            "none",
            "none_existing_global_nullifier_rule_sufficient",
            "PASS",
        ),
        Scenario(
            "S6",
            "shard_splitting_to_evade_caps",
            "Avoid shard-local admission or rate caps by splitting one source event across many shards.",
            "An operator controls shard assignment and routes equivalent receipts into separate shard windows.",
            {
                "shards_controlled": 64,
                "source_events": 1,
                "attempted_admissions": 64,
                "global_nullifier_collapses_duplicate_credit": True,
            },
            "Duplicate credit still collapses by global nullifier, but any future cap expressed only as shard-local would be gameable.",
            "conditional",
            "global_cap_accounting_for_shard_split_gap",
            "global_nullifier_cap_and_admission_accounting_gate",
            "GAPS",
        ),
        Scenario(
            "S7",
            "selectively_omitted_manifest",
            "Commit a valid-looking checkpoint root while hiding or misrepresenting specific nullifiers.",
            "The adversary publishes a checkpoint root and compact manifest that omit receipts relevant to later challenge or settlement selection.",
            {
                "checkpoint_roots": 1,
                "omitted_nullifiers": 10_000,
                "manifest_root_bound_to_receipt_root": False,
            },
            "Row 21o identifies compact manifests as necessary, but the canonical manifest completeness proof remains an activation-time gap.",
            "conditional",
            "canonical_checkpoint_tree_and_inclusion_proof_verifier_binding",
            "manifest_root_completeness_and_receipt_root_binding_gate",
            "GAPS",
        ),
        Scenario(
            "S8",
            "withheld_inclusion_proof",
            "Let a fraudulent or disputed receipt survive until challenge expiry by withholding proof material.",
            "The checkpoint root is published, but the operator does not serve the inclusion path or raw receipt during the challenge window.",
            {
                "challenge_window_epochs": 16,
                "proof_requested": True,
                "proof_served": False,
            },
            "Current design names challenge windows but not the proof-availability state machine or penalty path.",
            "conditional",
            "challenge_window_state_machine_and_proof_protocol",
            "proof_availability_timeout_and_checkpoint_ineligibility_gate",
            "GAPS",
        ),
        Scenario(
            "S9",
            "challenge_flooding",
            "Block honest checkpoints by exhausting challenge processing capacity.",
            "The adversary opens many spurious duplicate-nullifier and invalid-proof challenges against valid checkpoints.",
            {
                "spurious_challenges": 1_000_000,
                "valid_challenges": 1,
                "challenge_deposit_required": False,
            },
            "The challenge path is required, but activation needs bounded queueing, deposits or rate limits, and deterministic prioritization.",
            "conditional",
            "challenge_window_state_machine_and_proof_protocol",
            "challenge_rate_limit_deposit_and_priority_gate",
            "GAPS",
        ),
        Scenario(
            "S10",
            "queue_retry_double_admission",
            "Exploit restart timing to pass pre-queue and post-restart nullifier checks twice.",
            "The adversary submits a receipt, interrupts the writer before durable nullifier commit, then resubmits after restart.",
            {
                "submissions": 2,
                "durable_append_before_ack": False,
                "atomic_nullifier_reservation": False,
            },
            "Row 21o classifies silent drop and non-durable buffering as unsafe. Activation requires exactly-once queue/log semantics.",
            "conditional",
            "durable_queue_log_backpressure_design",
            "durable_append_before_ack_and_idempotent_replay_gate",
            "GAPS",
        ),
        Scenario(
            "S11",
            "nullifier_store_time_of_check_time_of_use",
            "Submit identical receipts fast enough that both observe the nullifier as absent before either write commits.",
            "Parallel submissions race the exact nullifier store between check and insert.",
            {
                "parallel_submissions": 2,
                "atomic_check_insert": False,
                "expected_duplicate_credit_with_atomic_insert": "0",
            },
            "The global nullifier rule is sound only if implementation uses atomic check-and-insert or reservation before admission.",
            "conditional",
            "exact_nullifier_store_false_positive_recovery_design",
            "atomic_nullifier_reservation_gate",
            "GAPS",
        ),
        Scenario(
            "S12",
            "bloom_only_value_bearing_authority",
            "Use probabilistic duplicate suppression as final value authority.",
            "The adversary relies on Bloom-only state, reset windows, or filter misuse instead of exact recovery and canonical nullifier storage.",
            {
                "row_21o_modeled_false_positive_rate": "0.008193722066",
                "row_21o_suppressed_valid_receipts_per_shard_epoch": "8193723",
                "bloom_false_negatives_under_standard_bloom": "0",
            },
            "Bloom-only authority is unsafe. A standard Bloom filter has no false negatives absent implementation error, but false positives suppress valid receipts and reset/misuse can launder duplicates.",
            "conditional",
            "exact_nullifier_store_false_positive_recovery_design",
            "bloom_prefilter_only_with_exact_recovery_gate",
            "GAPS",
        ),
        Scenario(
            "S13",
            "high_reputation_abuse",
            "Use existing reputation to bypass scrutiny for low-quality high-volume receipts.",
            "A high-scoring agent submits a large batch and depends on reputation-weighted challenge sampling to avoid audit.",
            {
                "agent_reputation_state": "high",
                "receipts_submitted": 1_000_000,
                "challenge_sampling_reputation_only": True,
            },
            "Reputation can route attention but must not replace random or risk-based challenge coverage for close-facing receipts.",
            "conditional",
            "reputation_weighted_challenge_sampling_gap",
            "challenge_sampling_floor_independent_of_reputation_gate",
            "GAPS",
        ),
        Scenario(
            "S14",
            "partial_failed_receipt_relabeling",
            "Relabel failed or partial receipts as succeeded after the checkpoint window closes.",
            "The adversary withholds final status or changes status metadata after checkpoint commitment.",
            {
                "partial_receipts": 500_000,
                "failed_receipts": 500_000,
                "status_bound_to_source_evidence": False,
            },
            "Row 21n already carries the receipt_status_integrity_gate_gap. Status must be committed before challenge/settlement consumption.",
            "conditional",
            "receipt_status_integrity_gate_gap",
            "receipt_status_commitment_and_transition_proof_gate",
            "GAPS",
        ),
    ]


def _hardening_gates(scenarios: list[Scenario]) -> dict[str, dict[str, Any]]:
    prior_refs = {
        "receipt_economic_admissibility_and_service_quality_gate": "temporal_service_receipt_farming_guard_gap",
        "sybil_diversity_and_independent_origin_gate": "temporal_sybil_diversity_floor_gap",
        "service_receipt_attempt_cap_and_value_evidence_gate": "temporal_service_receipt_farming_guard_gap",
        "root_committed_novelty_and_quality_evidence_gate": "newly_surfaced",
        "global_nullifier_cap_and_admission_accounting_gate": "newly_surfaced",
        "manifest_root_completeness_and_receipt_root_binding_gate": "canonical_checkpoint_tree_and_inclusion_proof_verifier_binding",
        "proof_availability_timeout_and_checkpoint_ineligibility_gate": "challenge_window_state_machine_and_proof_protocol",
        "challenge_rate_limit_deposit_and_priority_gate": "challenge_window_state_machine_and_proof_protocol",
        "durable_append_before_ack_and_idempotent_replay_gate": "durable_queue_log_backpressure_design",
        "atomic_nullifier_reservation_gate": "exact_nullifier_store_false_positive_recovery_design",
        "bloom_prefilter_only_with_exact_recovery_gate": "exact_nullifier_store_false_positive_recovery_design",
        "challenge_sampling_floor_independent_of_reputation_gate": "newly_surfaced",
        "receipt_status_commitment_and_transition_proof_gate": "receipt_status_integrity_gate_gap",
    }
    gates: dict[str, dict[str, Any]] = {}
    for scenario in scenarios:
        if scenario.proposed_hardening_gate.startswith("none_"):
            continue
        gate = gates.setdefault(
            scenario.proposed_hardening_gate,
            {
                "classification": "blocker_requires_gate_before_activation",
                "source_scenarios": [],
                "prior_carry_forward_ref": prior_refs.get(
                    scenario.proposed_hardening_gate, "newly_surfaced"
                ),
            },
        )
        gate["source_scenarios"].append(scenario.scenario_id)
    return gates


def build_artifact() -> dict[str, Any]:
    scenarios = _scenarios()
    scenario_payload = {
        scenario.scenario_id: {
            "name": scenario.name,
            "adversarial_goal": scenario.adversarial_goal,
            "method": scenario.method,
            "model_inputs": scenario.model_inputs,
            "disposition_under_current_design": scenario.disposition_under_current_design,
            "undeserved_credit_possible": scenario.undeserved_credit_possible,
            "gap_exploited": scenario.gap_exploited,
            "proposed_hardening_gate": scenario.proposed_hardening_gate,
            "verdict": scenario.verdict,
        }
        for scenario in scenarios
    }
    verdict_counts = {
        "PASS": sum(1 for scenario in scenarios if scenario.verdict == "PASS"),
        "GAPS": sum(1 for scenario in scenarios if scenario.verdict == "GAPS"),
        "BLOCKER": sum(1 for scenario in scenarios if scenario.verdict == "BLOCKER"),
    }
    return {
        "aggregate_verdict": "GAPS",
        "blocker_level_findings_count": verdict_counts["BLOCKER"],
        "canon_lineage": {
            "direct_authority": [
                "Row 21m spec",
                "Row 21n SIM",
                "Row 21o SIM",
            ],
            "design_lineage_only": [
                "Row 21l temporal-influence SIM",
                "CDL-066 sender authorization",
                "CDL-084 explicit-chain provenance / no double-settlement precedent",
                "CDL-108 backward attribution caps and duplicate collapse",
                "CDL-110 Genesis value policy certificate boundary",
                "ADR-0045 native QUIC submit payload cap",
            ],
            "whitepaper_terms_not_authority": [
                "ILC Agent Rollup",
                "Trillion-Agent Coordination Protocol",
            ],
        },
        "consolidated_hardening_gates": _hardening_gates(scenarios),
        "date": DATE,
        "deterministic_simulation": {
            "generator": "tools/sim/sim_ecu_adversarial_receipt_farming_00.py",
            "materializes_raw_receipts": False,
            "uses_randomness": False,
            "uses_floats": False,
            "scenario_count": len(scenarios),
            "adversarial_model": "virtual_agent_formula_construction",
        },
        "fast_path_ecu_cdl_open_blocked": True,
        "interesting_results": {
            "duplicate_credit_closed_by_row_21m_21n": True,
            "same_nullifier_shard_replay_undeserved_credit": "0",
            "scenarios_needing_activation_gates": verdict_counts["GAPS"],
            "bloom_only_authority": "unsafe_even_without_standard_bloom_false_negatives",
            "central_result": "security_boundary_is_not_duplicate_credit_math_but_activation_time_admission_proof_status_queue_and_challenge_protocol",
        },
        "non_claims": [
            "no_runtime_code",
            "no_runtime_tests",
            "no_cdl_mutation",
            "no_fast_path_ecu_activation",
            "no_passive_ecu_activation",
            "no_bls_signer_activation",
            "no_slow_path_ilc_settlement_change",
            "no_direct_ecu_minting",
            "no_direct_ilc_minting",
            "no_wallet_write",
            "no_monthly_close",
            "no_genesis_wallet_spend_authority",
            "no_werner_direct_ecu_creation",
            "no_public_mirror_push",
            "no_package_publication",
            "no_vps_mutation",
            "no_live_graph_atlas_lmdb_write",
            "no_public_rc_activation",
            "no_mainnet_activation",
            "no_epoch_transition",
        ],
        "output_token": OUTPUT_TOKEN,
        "phase": PHASE,
        "row_21q_may_proceed": True,
        "runtime_changes": False,
        "scenario_count": len(scenarios),
        "scenarios": scenario_payload,
        "schema_version": SCHEMA_VERSION,
        "status": "Complete",
        "verdict_counts": verdict_counts,
    }


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def render_markdown(artifact: dict[str, Any]) -> str:
    scenario_rows = [
        [
            scenario_id,
            data["verdict"],
            data["undeserved_credit_possible"],
            data["gap_exploited"],
            data["proposed_hardening_gate"],
        ]
        for scenario_id, data in artifact["scenarios"].items()
    ]
    gate_rows = [
        [
            name,
            data["classification"],
            ", ".join(data["source_scenarios"]),
            data["prior_carry_forward_ref"],
        ]
        for name, data in artifact["consolidated_hardening_gates"].items()
    ]
    parts = [
        "# SIM-ECU-ADVERSARIAL-RECEIPT-FARMING-00 v0.1",
        "",
        f"**Date:** {artifact['date']}",
        f"**Status:** {artifact['status']}",
        f"**Aggregate verdict:** `{artifact['aggregate_verdict']}`",
        f"**Output token:** `{artifact['output_token']}`",
        "",
        "## Summary",
        "",
        "The SIM exercises adversarial receipt farming against the Row 21m-21o sharded receipt-rollup design. It uses virtual adversary populations and exact integer/string model values rather than raw receipt datasets.",
        "",
        "The main result is narrow but important: cross-shard replay of the same receipt is closed by the globally scoped `receipt_nullifier`, but the activation boundary remains open around economic admissibility, Sybil diversity, manifest completeness, proof availability, challenge flooding, durable queue semantics, atomic nullifier reservation, status integrity, and proof-selection rules.",
        "",
        "No scenario found an unbounded no-gate duplicate-credit failure in the Row 21m/21n nullifier design. Thirteen scenarios carry activation-time gates into Row 21q.",
        "",
        "## Scenario Results",
        "",
        _markdown_table(
            [
                "Scenario",
                "Verdict",
                "Undeserved credit possible",
                "Gap exploited",
                "Hardening gate",
            ],
            scenario_rows,
        ),
        "",
        "## Scenario Details",
        "",
    ]
    for scenario_id, data in artifact["scenarios"].items():
        parts.extend(
            [
                f"### {scenario_id} - {data['name']}",
                "",
                f"**Adversarial goal:** {data['adversarial_goal']}",
                "",
                f"**Method:** {data['method']}",
                "",
                f"**Disposition under current design:** {data['disposition_under_current_design']}",
                "",
                f"**Undeserved close-facing projection possible:** `{data['undeserved_credit_possible']}`",
                "",
                f"**Gap exploited:** `{data['gap_exploited']}`",
                "",
                f"**Proposed hardening gate:** `{data['proposed_hardening_gate']}`",
                "",
                f"**Verdict:** `{data['verdict']}`",
                "",
            ]
        )
    parts.extend(
        [
            "## Consolidated Hardening Gates",
            "",
            _markdown_table(
                [
                    "Gate",
                    "Classification",
                    "Source scenarios",
                    "Prior carry-forward reference",
                ],
                gate_rows,
            ),
            "",
            "## Carry-Forward To Row 21q",
            "",
            "Row 21q must classify and disposition every hardening gate above before any fast-path ECU CDL opening. The duplicate-credit math itself is not the blocker; the blocker surface is activation-time proof, admission, queue, challenge, and status behavior.",
            "",
            "## Non-Claims",
            "",
            "\n".join(f"- `{claim}`" for claim in artifact["non_claims"]),
            "",
            artifact["output_token"],
            "",
        ]
    )
    return "\n".join(parts)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    _atomic_write_text(path, text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("docs/sims/sim_ecu_adversarial_receipt_farming_00_v0.1.json"),
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=Path("docs/sims/sim_ecu_adversarial_receipt_farming_00_v0.1.md"),
    )
    args = parser.parse_args()

    artifact = build_artifact()
    _atomic_write_json(args.json_out, artifact)
    _atomic_write_text(args.md_out, render_markdown(artifact))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    print(f"aggregate_verdict {artifact['aggregate_verdict']}")
    print(f"scenario_count {artifact['scenario_count']}")
    print(artifact["output_token"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
