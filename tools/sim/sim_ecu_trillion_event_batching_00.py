#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic ECU trillion-event batching scale SIM.

This tool intentionally models virtual agents and shards by formula instead of
materializing impossible receipt lists. It writes the Row 21o Markdown and JSON
artifacts atomically and deterministically.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, localcontext
from pathlib import Path
from typing import Any


PHASE = "SIM-ECU-TRILLION-EVENT-BATCHING-00"
SCHEMA_VERSION = "sim_ecu_trillion_event_batching_00.v0.1"
OUTPUT_TOKEN = "sim_ecu_trillion_event_batching_complete_SIM_ECU_TRILLION_EVENT_BATCHING_00"
DATE = "2026-10-13"

RECEIPTS_PER_SHARD_PER_EPOCH = 1_000_000_000
EPOCH_SECONDS = 60
CADENCES = (4, 16, 64)
SHARD_CASES = (1, 1_000, 1_000_000)
MEMORY_CAPS_GIB = (4, 8, 32)
PER_RECEIPT_MIN_BYTES = 150
PER_RECEIPT_OPERATIONAL_BYTES = 256
NULLIFIER_BYTES = 32
CID_APPROX_BYTES = 36
HASH_BYTES = 32
ADR_0045_PAYLOAD_CAP_BYTES = 1_048_576
FRAME_OVERHEAD_BYTES = 1_000
BLS_SIGNATURE_BYTES = 96
BLS_SIGNERS_PER_SHARD = 1_000_000
BITMAP_BYTES_FOR_BLS_SIGNERS = 125_000
FULL_BLS_KEY_LIST_BYTES = 96_000_000

HASH_COST_NS_CASES = (100, 1_000, 10_000)
BLS_ADDITION_COST_NS_CASES = (100, 1_000, 10_000)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    scale: str
    result: str
    verdict: str
    carry_forward: str


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _ceil_log2(value: int) -> int:
    if value <= 1:
        return 0
    return (value - 1).bit_length()


def _decimal_string(value: Decimal, places: str = "0.000001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def _bytes_to_gib_string(byte_count: int) -> str:
    with localcontext() as ctx:
        ctx.prec = 50
        gib = Decimal(byte_count) / Decimal(1024**3)
    return _decimal_string(gib, "0.000001")


def _seconds_string_from_ns(units: int, ns_per_unit: int) -> str:
    with localcontext() as ctx:
        ctx.prec = 50
        seconds = Decimal(units) * Decimal(ns_per_unit) / Decimal(1_000_000_000)
    return _decimal_string(seconds, "0.000001")


def _bloom_false_positive_rate(bits_per_element: int, hash_functions: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 60
        ratio = Decimal(-hash_functions) / Decimal(bits_per_element)
        base = Decimal(1) - ratio.exp()
        return base**hash_functions


def _memory_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cap_gib in MEMORY_CAPS_GIB:
        cap_bytes = cap_gib * 1024**3
        min_receipts = cap_bytes // PER_RECEIPT_MIN_BYTES
        operational_receipts = cap_bytes // PER_RECEIPT_OPERATIONAL_BYTES
        rows.append(
            {
                "memory_cap_gib": cap_gib,
                "safe_receipts_min_footprint": min_receipts,
                "safe_receipts_operational_footprint": operational_receipts,
                "safe_per_epoch_at_16_epochs_min_footprint": min_receipts // 16,
                "safe_per_epoch_at_16_epochs_operational_footprint": operational_receipts // 16,
            }
        )
    return rows


def _cadence_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cadence in CADENCES:
        receipts = RECEIPTS_PER_SHARD_PER_EPOCH * cadence
        depth = _ceil_log2(receipts)
        proof_bytes = depth * HASH_BYTES
        min_memory = receipts * PER_RECEIPT_MIN_BYTES
        operational_memory = receipts * PER_RECEIPT_OPERATIONAL_BYTES
        root_hashes = max(0, 2 * receipts - 1)
        rows.append(
            {
                "epochs_per_checkpoint": cadence,
                "receipts_accumulated": receipts,
                "tree_depth": depth,
                "proof_bytes": proof_bytes,
                "min_memory_gib": _bytes_to_gib_string(min_memory),
                "operational_memory_gib": _bytes_to_gib_string(operational_memory),
                "ordered_root_hashes": root_hashes,
                "ordered_root_seconds_by_hash_cost": [
                    {
                        "hash_time_ns": cost,
                        "seconds": _seconds_string_from_ns(root_hashes, cost),
                    }
                    for cost in HASH_COST_NS_CASES
                ],
            }
        )
    return rows


def _minimum_shards_for_network() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    safe_per_epoch_8gib_operational = (8 * 1024**3 // PER_RECEIPT_OPERATIONAL_BYTES) // 16
    for total in (10**9, 10**12, 10**15):
        rows.append(
            {
                "total_network_receipts_per_epoch": total,
                "minimum_shards_for_8gib_16_epoch_operational_buffer": _ceil_div(
                    total,
                    safe_per_epoch_8gib_operational,
                ),
                "receipts_per_shard_per_epoch_target": safe_per_epoch_8gib_operational,
            }
        )
    return rows


def _payload_classes() -> dict[str, Any]:
    proof_1e9 = _ceil_log2(10**9) * HASH_BYTES
    proof_1e12 = _ceil_log2(10**12) * HASH_BYTES
    return {
        "checkpoint_root_manifest": {
            "normal_path": True,
            "target_size": "tens_of_kb",
            "cap_result": "PASS_IF_COMPACT",
        },
        "individual_inclusion_challenge_proof": {
            "proof_bytes_at_1e9_leaves": proof_1e9,
            "proof_bytes_at_1e12_leaves": proof_1e12,
            "cap_result": "PASS",
        },
        "batched_proof_payload": {
            "max_960_byte_proofs_with_1000_byte_overhead": (ADR_0045_PAYLOAD_CAP_BYTES - FRAME_OVERHEAD_BYTES)
            // proof_1e9,
            "max_1280_byte_proofs_with_1000_byte_overhead": (ADR_0045_PAYLOAD_CAP_BYTES - FRAME_OVERHEAD_BYTES)
            // proof_1e12,
            "cap_result": "PASS_IF_SPLIT",
        },
        "raw_receipt_flood": {
            "cap_result": "BLOCKER",
        },
    }


def _nullifier_analysis() -> dict[str, Any]:
    fpr = _bloom_false_positive_rate(bits_per_element=10, hash_functions=7)
    suppressed = int(
        (fpr * Decimal(RECEIPTS_PER_SHARD_PER_EPOCH)).to_integral_value(
            rounding=ROUND_CEILING
        )
    )
    return {
        "global_in_memory_set": {
            "raw_nullifier_bytes": RECEIPTS_PER_SHARD_PER_EPOCH * NULLIFIER_BYTES,
            "raw_nullifier_gib": _bytes_to_gib_string(
                RECEIPTS_PER_SHARD_PER_EPOCH * NULLIFIER_BYTES
            ),
            "false_positive_risk": "none",
            "verdict": "infeasible_for_small_nodes",
        },
        "sorted_on_disk_tree": {
            "memory": "bounded_by_page_cache_and_batch_writer",
            "false_positive_risk": "none",
            "verdict": "preferred_exact_store_candidate",
        },
        "bloom_prefilter_only": {
            "bits_per_element": 10,
            "hash_functions": 7,
            "modeled_false_positive_rate": _decimal_string(fpr, "0.000000000001"),
            "valid_receipts_suppressed_per_shard_per_epoch": suppressed,
            "verdict": "unsafe_without_exact_recovery",
        },
    }


def _tree_options() -> dict[str, Any]:
    return {
        "binary_merkle_sha256": {
            "root_build_cost": "O(N) over ordered batch",
            "pipeline_cost_if_sorting_or_all_proofs": "O(N log N)",
            "proof_bytes_at_1e9": _ceil_log2(10**9) * HASH_BYTES,
            "proof_bytes_at_1e12": _ceil_log2(10**12) * HASH_BYTES,
            "verifier_cost": "O(log N) hashes",
            "implementation_risk": "low",
        },
        "sparse_merkle": {
            "root_build_cost": "O(N) for non-empty leaves",
            "pipeline_cost_with_incremental_updates": "O(N log N)",
            "verifier_cost": "O(log N)",
            "implementation_risk": "medium",
        },
        "verkle": {
            "root_build_cost": "O(N) amortized candidate",
            "proof_size": "sub_logarithmic_candidate",
            "verifier_cost": "O(1)_or_O(log_d_N)",
            "implementation_risk": "high_not_current_ilc_stack",
        },
        "hybrid_bloom_prefilter_binary_merkle": {
            "root_build_cost": "O(N) Merkle over exact-confirmed set",
            "pipeline_cost": "O(N log N) if exact confirmation requires sort/tree",
            "verifier_cost": "O(log N) hashes",
            "implementation_risk": "medium",
        },
    }


def _bls_feasibility() -> dict[str, Any]:
    remaining = (
        ADR_0045_PAYLOAD_CAP_BYTES
        - BLS_SIGNATURE_BYTES
        - BITMAP_BYTES_FOR_BLS_SIGNERS
        - FRAME_OVERHEAD_BYTES
    )
    return {
        "activation_authorized": False,
        "aggregate_signature_bytes": BLS_SIGNATURE_BYTES,
        "compact_bitmap_bytes_for_1e6_signers": BITMAP_BYTES_FOR_BLS_SIGNERS,
        "full_public_key_list_bytes_for_1e6_signers": FULL_BLS_KEY_LIST_BYTES,
        "remaining_manifest_budget_bytes_after_aggregate_bitmap_and_overhead": remaining,
        "manifest_target": "tens_of_kb_not_hundreds_of_kb",
        "aggregation_sensitivity": [
            {
                "addition_cost_ns": cost,
                "aggregate_time_seconds": _seconds_string_from_ns(
                    BLS_SIGNERS_PER_SHARD, cost
                ),
            }
            for cost in BLS_ADDITION_COST_NS_CASES
        ],
        "verdict": "tractable_as_candidate_envelope_inactive",
    }


def _settlement_compression() -> dict[str, Any]:
    receipt_depth = _ceil_log2(10**9)
    shard_depth = _ceil_log2(1_000)
    full_proof_count = RECEIPTS_PER_SHARD_PER_EPOCH
    return {
        "normal_path": {
            "known_shard_id": True,
            "receipt_path_hashes": receipt_depth,
            "shard_checkpoint_path_hashes": shard_depth,
            "total_hashes_per_spot_check": receipt_depth + shard_depth,
            "verdict": "tractable_for_spot_checks",
        },
        "expensive_path": {
            "shard_id_unknown_or_audit_search": True,
            "shards_scanned": 1_000,
            "hashes_per_receipt_search": 1_000 * receipt_depth,
            "verdict": "exceptional_case_only",
        },
        "full_verification_infeasibility": {
            "analytics_only": True,
            "proof_count": full_proof_count,
            "proof_depth": receipt_depth,
            "cases": [
                {
                    "hash_time_ns": cost,
                    "per_receipt_time_seconds": _seconds_string_from_ns(
                        receipt_depth, cost
                    ),
                    "full_shard_time_seconds": _seconds_string_from_ns(
                        full_proof_count * receipt_depth, cost
                    ),
                }
                for cost in HASH_COST_NS_CASES
            ],
        },
    }


def _canon_lineage() -> dict[str, Any]:
    return {
        "direct_authority": [
            {
                "source": "docs/specs/ilc_ecu_sharded_receipt_rollup_spec_GAP_ECU_SHARDED_RECEIPT_ROLLUP_SPEC_00_v0.1.md",
                "role": "Row 21m schema authority for ECULocalReceipt, ECUShardReceiptRollup, ECUShardCheckpoint, globally scoped receipt_nullifier, shard_id provenance semantics, challenge windows, and non-activation boundaries.",
            },
            {
                "source": "docs/sims/sim_ecu_cross_shard_conservation_boundary_00_v0.1.md",
                "role": "Row 21n conservation SIM authority for duplicate-credit collapse and same-nullifier projection mismatch fail-closed behavior.",
            },
        ],
        "design_lineage_only": [
            {
                "source": "CDL-084",
                "role": "Settlement-purity precedent: callers provide explicit evidence; settle paths do not perform graph queries.",
            },
            {
                "source": "CDL-108",
                "role": "Typed backward-attribution and duplicate-collapse precedent; does not activate runtime traversal, ECU minting, settlement, invite credit, wallet writes, or public RC.",
            },
            {
                "source": "SIM-FETCH-01",
                "role": "Fetch-distribution precedent that incomplete or probabilistic hints may route work but cannot be final authority for value-bearing inclusion or exclusion.",
                "metrics": {
                    "want_have_hit_rate": "0.399133",
                    "cache_hit_rate_tail": "0.003757",
                    "verdict": "fail",
                },
            },
            {
                "source": "SIM-004 / CDL-041",
                "role": "Historical deterministic shard-reconciliation precedent; not direct receipt-rollup authority.",
            },
            {
                "source": "CDL-104",
                "role": "Conceptual lineage only for Merkle-plus-spectral epoch-commitment style compact structural commitments; CDL-104 is ratified and the Rust field was committed, but independent spectral recomputation enforcement is not live, and this SIM does not use or modify the epoch-commitment field.",
            },
        ],
        "naming_boundary": {
            "ilc_agent_rollup": "descriptive whitepaper term for the hierarchical evidence-commitment pattern; not a ratified CDL term and not activation authority",
            "trillion_agent_coordination_protocol": "descriptive whitepaper term for the local-to-global coordination architecture; not a separate activated network protocol",
        },
    }


def build_artifact() -> dict[str, Any]:
    memory_rows = _memory_rows()
    cadence_rows = _cadence_rows()
    payload_classes = _payload_classes()
    nullifier_analysis = _nullifier_analysis()

    scenarios = [
        Scenario(
            "S1",
            "memory_growth_under_sustained_receipt_ingestion",
            "10^9 receipts/shard/epoch; 4/8/32 GiB memory caps; 16-epoch candidate window",
            "Full in-memory buffering is infeasible; a streaming writer or durable log is mandatory.",
            "GAPS",
            "durable streaming writer required",
        ),
        Scenario(
            "S2",
            "checkpoint_cadence_comparison",
            "4, 16, and 64 epochs at 10^9 receipts/shard/epoch",
            "Cadence is a tradeoff between churn, memory pressure, settlement latency, and data-loss exposure.",
            "GAPS",
            "calibrate checkpoint cadence after writer design",
        ),
        Scenario(
            "S3",
            "nullifier_deduplication_at_scale",
            "10^9 globally scoped receipt_nullifiers/shard/epoch",
            "Bloom-only duplicate suppression would suppress valid receipts; exact confirmation is required.",
            "GAPS",
            "exact nullifier store and false-positive recovery design",
        ),
        Scenario(
            "S4",
            "proof_tree_choice_at_scale",
            "10^9 to 10^12 leaves; binary Merkle, sparse Merkle, Verkle, and hybrid candidates",
            "Binary Merkle individual proofs fit ADR-0045, but canonical tree/proof binding remains open.",
            "GAPS",
            "canonical tree/proof verifier selection",
        ),
        Scenario(
            "S5",
            "bls_aggregate_checkpoint_feasibility",
            "10^6 local signers/shard/checkpoint with inactive BLS checkpoint label",
            "Aggregate plus compact bitmap fits the frame; full key-list embedding does not.",
            "GAPS",
            "signer roster reference and activation policy",
        ),
        Scenario(
            "S6",
            "slow_path_settlement_compression",
            "10^3 shards x 16-epoch checkpoints; spot checks vs full verification",
            "Root-only normal path is tractable; full per-receipt settlement verification is infeasible.",
            "GAPS",
            "challenge/audit proof protocol",
        ),
        Scenario(
            "S7",
            "backpressure_ingestion_exceeds_checkpoint_write",
            "temporary local receipt arrival rate above checkpoint writer throughput",
            "Silent drop is unsafe; explicit overflow or durable append-log recovery is required.",
            "GAPS",
            "queue/log implementation spec",
        ),
    ]

    return {
        "activation_authorized": False,
        "adr_0045_payload_cap_check": {
            "payload_cap_bytes": ADR_0045_PAYLOAD_CAP_BYTES,
            "raw_receipt_flood_result": "BLOCKER_anti_pattern",
            "result": "PASS_FOR_COMPACT_ROOTS_AND_BOUNDED_PROOFS",
        },
        "adr_0045_payload_classes": payload_classes,
        "agent_model": {
            "simulation_mode": "virtual_agents_formula_scale_no_raw_receipt_allocation",
            "local_agent_receipt_volume_cases_per_epoch": [
                1_000,
                1_000_000,
                10_000_000,
            ],
            "per_shard_receipts_per_epoch": RECEIPTS_PER_SHARD_PER_EPOCH,
            "shard_cases": list(SHARD_CASES),
            "detail_retention": "raw_receipts_and_full_proofs_remain_local_or_shard_retained",
        },
        "aggregate_verdict": "GAPS",
        "backpressure_recommended_shape": "bounded_queue_with_explicit_overflow_error_plus_durable_append_log_or_write_behind_journal_before_activation",
        "backpressure_schema_gap_disposition": "GAPS",
        "bloom_false_positive_analysis": {
            "bits_per_element": 10,
            "hash_functions": 7,
            "modeled_false_positive_rate": nullifier_analysis["bloom_prefilter_only"][
                "modeled_false_positive_rate"
            ],
            "valid_receipts_suppressed_per_shard_per_epoch": str(
                nullifier_analysis["bloom_prefilter_only"][
                    "valid_receipts_suppressed_per_shard_per_epoch"
                ]
            ),
            "verdict": "Bloom-only duplicate suppression is unsafe; Bloom may be a prefilter only with exact recovery.",
        },
        "bloom_false_positive_suppression_acceptable": False,
        "bls_checkpoint_feasibility": _bls_feasibility(),
        "cadence_analysis": cadence_rows,
        "canon_lineage": _canon_lineage(),
        "carry_forward_gaps": [
            "durable_queue_log_backpressure_design",
            "exact_nullifier_store_false_positive_recovery_design",
            "canonical_checkpoint_tree_and_inclusion_proof_verifier_binding",
            "challenge_window_state_machine_and_proof_protocol",
            "bls_signer_roster_reference_and_activation_boundary",
            "settlement_consumer_proof_selection_rules",
            "private_public_proof_boundary_from_rows_21l_21n",
        ],
        "date": DATE,
        "deterministic_simulation": {
            "generator": "tools/sim/sim_ecu_trillion_event_batching_00.py",
            "materializes_raw_receipts": False,
            "uses_randomness": False,
            "uses_floats": False,
            "arithmetic": "integer_and_decimal_string_outputs",
            "scenario_count": 7,
        },
        "hash_cost_sensitivity": {
            "analytics_only": True,
            "cases": _settlement_compression()["full_verification_infeasibility"]["cases"],
            "depth": _ceil_log2(10**9),
        },
        "hierarchical_rollup_model": {
            "central_raw_receipt_verifier": "BLOCKER_anti_pattern",
            "challenge_path": "fetch_individual_inclusion_proof_and_raw_receipt_only_when_challenged_or_audited",
            "design_rule": "detail_downward_commitments_upward",
            "normal_path": "local_receipts_to_shard_rollup_to_checkpoint_root_to_hypergraph",
        },
        "interesting_results": {
            "candidate_window_operational_memory_gib": _bytes_to_gib_string(
                RECEIPTS_PER_SHARD_PER_EPOCH * 16 * PER_RECEIPT_OPERATIONAL_BYTES
            ),
            "safe_per_epoch_at_8gib_16_epoch_operational_footprint": memory_rows[1][
                "safe_per_epoch_at_16_epochs_operational_footprint"
            ],
            "minimum_shards_for_total_network_cases": _minimum_shards_for_network(),
            "bloom_only_suppressed_valid_receipts_per_shard_per_epoch": nullifier_analysis[
                "bloom_prefilter_only"
            ]["valid_receipts_suppressed_per_shard_per_epoch"],
            "adr_0045_max_1e12_proofs_per_frame": payload_classes[
                "batched_proof_payload"
            ]["max_1280_byte_proofs_with_1000_byte_overhead"],
        },
        "memory_analysis": memory_rows,
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
        "nullifier_analysis": nullifier_analysis,
        "phase": PHASE,
        "proof_generation_complexity": "O(log N) for one proof; O(N log N) only if materializing all proofs",
        "root_construction_complexity": "O(N) hash work over an already ordered batch",
        "row_21p_may_proceed": True,
        "row_21q_required_before_fast_path_cdl": True,
        "runtime_changes": False,
        "scale_parameters": {
            "adr_0045_payload_cap_bytes": ADR_0045_PAYLOAD_CAP_BYTES,
            "cadence_comparison_epochs": list(CADENCES),
            "candidate_batch_window_epochs": 16,
            "epoch_duration_seconds": EPOCH_SECONDS,
            "per_shard_per_epoch_receipts": RECEIPTS_PER_SHARD_PER_EPOCH,
            "shard_sensitivity_cases": list(SHARD_CASES),
            "total_network_receipts_per_epoch_cases": [
                RECEIPTS_PER_SHARD_PER_EPOCH * shard_count
                for shard_count in SHARD_CASES
            ],
        },
        "scenario_results": [
            {
                "carry_forward": scenario.carry_forward,
                "id": scenario.scenario_id,
                "name": scenario.name,
                "result": scenario.result,
                "scale": scenario.scale,
                "verdict": scenario.verdict,
            }
            for scenario in scenarios
        ],
        "schema_version": SCHEMA_VERSION,
        "settlement_compression": _settlement_compression(),
        "sorting_or_dynamic_update_complexity": "O(N log N) for sorting nullifiers or N incremental authenticated inserts",
        "tree_options": _tree_options(),
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
            scenario["id"],
            scenario["scale"],
            scenario["result"],
            scenario["verdict"],
        ]
        for scenario in artifact["scenario_results"]
    ]
    memory_rows = [
        [
            row["memory_cap_gib"],
            row["safe_receipts_min_footprint"],
            row["safe_receipts_operational_footprint"],
            row["safe_per_epoch_at_16_epochs_operational_footprint"],
        ]
        for row in artifact["memory_analysis"]
    ]
    cadence_rows = [
        [
            row["epochs_per_checkpoint"],
            row["receipts_accumulated"],
            row["tree_depth"],
            row["proof_bytes"],
            row["operational_memory_gib"],
        ]
        for row in artifact["cadence_analysis"]
    ]
    shard_rows = [
        [
            row["total_network_receipts_per_epoch"],
            row["minimum_shards_for_8gib_16_epoch_operational_buffer"],
            row["receipts_per_shard_per_epoch_target"],
        ]
        for row in artifact["interesting_results"]["minimum_shards_for_total_network_cases"]
    ]
    payload = artifact["adr_0045_payload_classes"]
    bls = artifact["bls_checkpoint_feasibility"]
    settlement = artifact["settlement_compression"]

    parts = [
        "# SIM-ECU-TRILLION-EVENT-BATCHING-00 v0.1",
        "",
        f"**Date:** {DATE}",
        f"**Phase:** `{PHASE}`",
        "**Status:** Complete",
        "**Sensitivity:** NON-SENSITIVE",
        f"**Generated by:** `{artifact['deterministic_simulation']['generator']}`",
        f"**Output token:** `{OUTPUT_TOKEN}`",
        "",
        "## Purpose",
        "",
        "This deterministic SIM models the Row 21m sharded receipt-rollup schema at trillion-scale network volume. It uses virtual agents and shards by formula: no raw billion-row receipt set is allocated, no runtime code is changed, and no activation authority is claimed.",
        "",
        "The controlling architecture is hierarchical: local agents capture deterministic receipts; shards aggregate them into bounded structures; compact roots and manifests move upward; raw receipts and full proof paths are fetched only during challenge or audit.",
        "",
        "## Aggregate Verdict",
        "",
        f"`{artifact['aggregate_verdict']}`. The scale envelope is plausible only when detail remains local/shard-retained and compact commitments move upward. The phase carries forward gaps for queue/log design, exact nullifier storage, canonical proof binding, BLS roster policy, and challenge/audit protocol.",
        "",
        "## Canon Lineage",
        "",
        "Direct Row 21o authority comes from the Row 21m sharded receipt-rollup schema and the Row 21n cross-shard conservation SIM. Prior ILC work provides design lineage only: CDL-084 settlement purity, CDL-108 typed backward-attribution and duplicate-collapse precedent, SIM-FETCH-01 fetch-distribution evidence (`want_have_hit_rate=0.399133`, `cache_hit_rate_tail=0.003757`, verdict `fail`) that probabilistic hints cannot be final value-bearing authority, SIM-004/CDL-041 deterministic shard-reconciliation history, and CDL-104 conceptual compact-commitment lineage only (ratified/Rust field committed, independent spectral recomputation enforcement not live). These sources do not authorize fast-path ECU activation, BLS signer activation, settlement, wallet writes, CDL mutation, or runtime deployment.",
        "",
        "The whitepaper terms `ILC Agent Rollup` and `Trillion-Agent Coordination Protocol` are descriptive names for this hierarchical evidence-commitment pattern. They are not ratified CDL terms and are not activation authority.",
        "",
        "## Scenario Summary",
        "",
        _markdown_table(
            ["Scenario", "Scale", "Result", "Verdict"],
            scenario_rows,
        ),
        "",
    ]

    for scenario in artifact["scenario_results"]:
        parts.extend(
            [
                f"### {scenario['id']} - {scenario['name']}",
                "",
                f"**Scale:** {scenario['scale']}",
                "",
                f"**Model result:** {scenario['result']}",
                "",
                f"**Verdict:** `{scenario['verdict']}`",
                "",
                f"**Carry-forward:** {scenario['carry_forward']}",
                "",
            ]
        )

    parts.extend(
        [
            "## Key Computed Envelope",
            "",
            "### Memory Bounds",
            "",
            _markdown_table(
                [
                    "Cap GiB",
                    "Receipts at 150 B",
                    "Receipts at 256 B",
                    "Safe per epoch at 16 epochs / 256 B",
                ],
                memory_rows,
            ),
            "",
            f"At `10^9` receipts/shard/epoch and 16 epochs, operational buffering at 256 bytes/receipt is `{artifact['interesting_results']['candidate_window_operational_memory_gib']}` GiB. That is not a safe in-memory design; the simulator therefore classifies durable streaming or explicit-overflow backpressure as required.",
            "",
            "### Shard Count Needed For 8 GiB Operators",
            "",
            _markdown_table(
                [
                    "Total network receipts/epoch",
                    "Minimum shards at 8 GiB / 16 epochs / 256 B",
                    "Target receipts/shard/epoch",
                ],
                shard_rows,
            ),
            "",
            "This is the most useful result from the SIM: trillion-event network volume is not automatically impossible, but it requires many shards or shorter checkpoint windows. A single shard receiving `10^9` receipts per minute is an extreme stress case, not a normal target for commodity nodes.",
            "",
            "### Cadence Comparison",
            "",
            _markdown_table(
                [
                    "Epochs",
                    "Receipts/checkpoint",
                    "Tree depth",
                    "Proof bytes",
                    "Operational memory GiB",
                ],
                cadence_rows,
            ),
            "",
            "Merkle root construction over an already ordered batch is O(N). Sorting nullifiers, incremental authenticated inserts, or materializing every proof path can make the end-to-end pipeline O(N log N).",
            "",
            "### ADR-0045 Payload Classes",
            "",
            _markdown_table(
                ["Payload", "Computed result", "Verdict"],
                [
                    [
                        "Checkpoint root/manifest",
                        payload["checkpoint_root_manifest"]["target_size"],
                        payload["checkpoint_root_manifest"]["cap_result"],
                    ],
                    [
                        "Individual 1e9-leaf proof",
                        f"{payload['individual_inclusion_challenge_proof']['proof_bytes_at_1e9_leaves']} bytes",
                        payload["individual_inclusion_challenge_proof"]["cap_result"],
                    ],
                    [
                        "Individual 1e12-leaf proof",
                        f"{payload['individual_inclusion_challenge_proof']['proof_bytes_at_1e12_leaves']} bytes",
                        payload["individual_inclusion_challenge_proof"]["cap_result"],
                    ],
                    [
                        "Batched 1e12-leaf proofs/frame",
                        payload["batched_proof_payload"]["max_1280_byte_proofs_with_1000_byte_overhead"],
                        payload["batched_proof_payload"]["cap_result"],
                    ],
                    [
                        "Raw receipt flood",
                        "unbounded receipt payload",
                        payload["raw_receipt_flood"]["cap_result"],
                    ],
                ],
            ),
            "",
            "### Nullifier Deduplication",
            "",
            f"A raw `10^9`-entry nullifier set is `{artifact['nullifier_analysis']['global_in_memory_set']['raw_nullifier_gib']}` GiB before data-structure overhead. A 10-bit/element Bloom filter with 7 hashes has modeled false-positive rate `{artifact['bloom_false_positive_analysis']['modeled_false_positive_rate']}`, suppressing about `{artifact['bloom_false_positive_analysis']['valid_receipts_suppressed_per_shard_per_epoch']}` valid receipts/shard/epoch if used alone. Bloom-only suppression is therefore unsafe; Bloom may only be a prefilter before exact recovery.",
            "",
            "### BLS Checkpoint Feasibility",
            "",
            f"BLS remains inactive. A checkpoint frame with one `{bls['aggregate_signature_bytes']}` byte aggregate signature, a `{bls['compact_bitmap_bytes_for_1e6_signers']}` byte bitmap, and `{FRAME_OVERHEAD_BYTES}` bytes of overhead leaves `{bls['remaining_manifest_budget_bytes_after_aggregate_bitmap_and_overhead']}` bytes. That fits, but the manifest target remains tens of KB rather than using the full budget.",
            "",
            "### Settlement Compression",
            "",
            f"Known-shard spot checks cost `{settlement['normal_path']['total_hashes_per_spot_check']}` hashes (`{settlement['normal_path']['receipt_path_hashes']}` receipt-path + `{settlement['normal_path']['shard_checkpoint_path_hashes']}` shard-path). Unknown-shard audit search is exceptional and costs `{settlement['expensive_path']['hashes_per_receipt_search']}` hashes per searched receipt across 1,000 shards. Full per-receipt settlement verification remains infeasible at the modeled scale.",
            "",
            "## Carry-Forward Gaps",
            "",
        ]
    )
    for gap in artifact["carry_forward_gaps"]:
        parts.append(f"- `{gap}`")
    parts.extend(
        [
            "",
            "## Non-Claims",
            "",
        ]
    )
    for claim in artifact["non_claims"]:
        parts.append(f"- `{claim}`")
    parts.append("")
    return "\n".join(parts)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--md-out",
        type=Path,
        default=Path("docs/sims/sim_ecu_trillion_event_batching_00_v0.1.md"),
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=Path("docs/sims/sim_ecu_trillion_event_batching_00_v0.1.json"),
    )
    parser.add_argument("--print-summary", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact = build_artifact()
    json_content = json.dumps(
        artifact,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    json_content += "\n"
    markdown_content = render_markdown(artifact)
    _atomic_write(args.json_out, json_content)
    _atomic_write(args.md_out, markdown_content)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "aggregate_verdict": artifact["aggregate_verdict"],
                    "bloom_false_positive_suppression_acceptable": artifact[
                        "bloom_false_positive_suppression_acceptable"
                    ],
                    "candidate_window_operational_memory_gib": artifact[
                        "interesting_results"
                    ]["candidate_window_operational_memory_gib"],
                    "output_token": OUTPUT_TOKEN,
                    "phase": PHASE,
                    "row_21p_may_proceed": artifact["row_21p_may_proceed"],
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
