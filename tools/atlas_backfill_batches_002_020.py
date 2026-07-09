#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""One-shot Atlas ledger backfill: batches 002–020 (190 ilc_core/ runtime modules).

Writes 190 annotation entries to the Fix38 ledger atomically, then exits.
Run from the repo root: python3 tools/atlas_backfill_batches_002_020.py
"""
from __future__ import annotations

import json
import os
import tempfile

LEDGER = "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json"

GENESIS_EDGE = {"edge_type": "SOURCE_TREE_MEMBER", "target": "genesis:genesis_root_v0.4"}


def _entry(
    batch: str,
    repo_path: str,
    summary: str,
    authority_edges: list[dict],
    extra_semantic_edges: list[dict] | None = None,
) -> dict:
    semantic_edges = [GENESIS_EDGE] + (extra_semantic_edges or [])
    trace_roles = ["SOURCE_TREE_MEMBER"] + [e["edge_type"] for e in authority_edges] + [
        e["edge_type"] for e in (extra_semantic_edges or []) if e["edge_type"] not in ("SOURCE_TREE_MEMBER",)
    ]
    # deduplicate trace_roles preserving order
    seen: set[str] = set()
    deduped_roles: list[str] = []
    for r in trace_roles:
        if r not in seen:
            seen.add(r)
            deduped_roles.append(r)
    return {
        "annotation_batch": batch,
        "chronology_note": "2026-07-09 phase_backfill_batches_002_020 — historical ilc_core/ runtime module",
        "manual_read_summary": summary,
        "proposed_authority_trace_edges": authority_edges,
        "proposed_semantic_edges": semantic_edges,
        "proposed_trace_roles": deduped_roles,
        "recommended_graph_action": "load_bearing_artifact_added:ilc_core/ -> genesis:genesis_root_v0.4",
        "repo_path": repo_path,
    }


def _impl(cdl: str, target: str) -> dict:
    return {"edge_type": "IMPLEMENTS", "target": target}


def _ref(target: str) -> dict:
    return {"edge_type": "REFERENCES_AUTHORITY", "review_status": "candidate_authority_trace", "target": target}


NEW_ENTRIES: list[dict] = [
    # ── batch 002 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/epoch_report_export.py",
        "Exports per-agent epoch reports combining namespace health and agent dossier data to CSV or JSON files, creating parent directories automatically.",
        [_ref("ilc_core/analysis/namespace_health.py")],
        [{"edge_type": "DEPENDS_ON", "target": "ilc_core/analysis/namespace_health.py"}],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/fairness_metrics.py",
        "SIM-63A offline analysis module computing Gini coefficients, Pearson correlation, β/θ ECU payout reweighting, and PB farming gating simulations over agent payout distributions.",
        [],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/freshness_gate.py",
        "Computes exponential decay freshness gate scores bounded by a configurable floor, with a Genesis node exemption that bypasses decay.",
        [],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/genesis_accrual_governor.py",
        "Enforces the Genesis cumulative accrual cap using a sigmoid taper (theta_hard=1/20, theta_soft=exp(-3)) with monotonicity invariants and bounded Decimal arithmetic.",
        [],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/governance_weight.py",
        "Implements CDL-013 Decimal-arithmetic governance weight and vote-share computation with a decay-non-genesis-only rule.",
        [_ref("cdl:013")],
        [_impl("CDL-013", "cdl:013")],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/graph_kpis.py",
        "Computes per-claim link statistics (supports_in, refutes_in, equivalent_in, depends_on_in) and local influence scores dispatched by protocol algorithm ID.",
        [],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/laplacian_analytics.py",
        "Full hypergraph Laplacian analytics pipeline implementing ADR-0029 and SIM-SPECTRAL-01: builds the normalized Laplacian, computes the Fiedler value (lambda2/v2), and evaluates partition risk with bootstrap mode for small graphs below N=44.",
        [_ref("docs/adr/ADR_0029_Hypergraph_Laplacian_Analytics.md")],
        [_impl("ADR-0029", "adr:0029")],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/light_cone_kpis.py",
        "Computes the epistemic light cone composite score (reach × horizon × domain_span) per agent from graph adjacency and task row aggregation.",
        [],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/local_spectral_analytics.py",
        "Computes induced-subgraph local lambda2 per content_type cluster (H-006b Part 2+4, ADR-0032 §2.5), excluding partial-membership hyperedges.",
        [_ref("docs/adr/ADR_0032_Multiscale_Spectral_Analysis.md")],
        [_impl("ADR-0032", "adr:0032")],
    ),
    _entry(
        "catchup_batch_002_phase_backfill",
        "ilc_core/analysis/namespace_health.py",
        "Builds NamespaceHealthSnapshot combining epistemic stress and cohesion metrics for a namespace at one epoch.",
        [],
    ),
    # ── batch 003 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/node_value_conformance.py",
        "Builds conformance reports with SHA-256 over sorted score rows and anti-sybil invariant checks (sybil_low_diversity_reuse, inconsistent_agent_reuse).",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/node_value_extraction.py",
        "Extracts NodeValueInputEvents from dict rows or NDJSON files and constructs replay fixtures with SHA-256 integrity checksums.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/node_value_governance_conformance.py",
        "Produces comprehensive multi-check governance conformance reports covering score vector schema, anti-sybil, reuse diversity, freshness, refutation profitability, and genesis accrual governor invariants.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/node_value_input_canon.py",
        "Validates and normalizes four node value input event kinds (task_outcome, claim, refutation, commit.epoch) into canonical TypedDict structures with telemetry.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/node_value_kernel.py",
        "Core epistemic weight kernel: builds NodeEvidenceVectors from events, computes weighted Decimal scores (reuse, contradiction, validation, path) and utility flow.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/node_value_policy_migration.py",
        "Normalizes policy bundles in strict (v0.1) or legacy-bridge mode, mapping legacy field aliases to canonical keys.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/path_lift_counterfactual.py",
        "Computes normalized path lift scores per node from path witnesses using baseline efficiency (weight/cost ratio), with agent diversity tracking.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/problem_space_kpis.py",
        "Aggregates task counts per agent across six problem space categories (LOCAL_CONSISTENCY, GLOBAL_EXPLANATION, etc.) with heuristic inference from task fields.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/reuse_diversity_invariants.py",
        "Validates reuse diversity policy (min_distinct_agents, max_single_agent_share, penalty_floor) and computes a diversity multiplier with refutation-safe floor.",
        [],
    ),
    _entry(
        "catchup_batch_003_phase_backfill",
        "ilc_core/analysis/routed_tasks.py",
        "Materializes TaskRoutingSuggestions into concrete RoutedTaskRows with QA gating, κ-parameterized reward calculation, and competence multiplier logic.",
        [],
    ),
    # ── batch 004 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/analysis/routed_tasks_export.py",
        "Exports RoutedTaskRow dict lists to CSV (alphabetical header) or JSON files, creating parent directories automatically.",
        [],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/analysis/spectral_trajectory.py",
        "H-006b Part 3 temporal spectral trajectory analytics: produces SpectralEpochRecord with lambda2_delta and lambda2_accel from a single LAPACK eigenvalue call.",
        [],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/analysis/spectral_utils.py",
        "ADR-0029 spectral utility functions: L2 spectral_distance routing metric, provisional edge weight computation (SIM-REUSE-01 pending), v0.2 fixed-point eigenvalue hashing, and CSPRNG Gaussian noise injection for beacon emission.",
        [_ref("docs/adr/ADR_0029_Hypergraph_Laplacian_Analytics.md")],
        [_impl("ADR-0029", "adr:0029")],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/analysis/stress_and_cohesion.py",
        "Computes EpistemicStress (validation depth, contradiction, crosslink error terms) and CohesionMetrics (support ratio, controversy ratio, mean absolute influence).",
        [],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/analysis/stress_response_kpis.py",
        "Aggregates per-agent stress response metrics (low/high bucket task counts and success rates) from task samples that include a stress field.",
        [],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/analysis/task_routing_suggestions.py",
        "Generates prioritized TaskRoutingSuggestion lists combining regime classification, agent competency, stress preference, and light cone tie-breaking.",
        [],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/analysis/utility_flow_rewards.py",
        "Utility flow reward allocation governor: applies action-kind multipliers (refutation=1.2×), diversity/freshness multipliers, budget cap, genesis share cap, and refutation profitability invariant.",
        [],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/asgi.py",
        "Thin ASGI adapter creating the ilc_core FastAPI application via create_app() for uvicorn and module-import serving surfaces.",
        [],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/bundle/__init__.py",
        "PUBLIC_RC_EXCLUDE package marker for the private ADR-0009 bundle tooling; exports no symbols.",
        [_ref("docs/adr/ADR_0009_Protocol_Bundle_Architecture.md")],
    ),
    _entry(
        "catchup_batch_004_phase_backfill",
        "ilc_core/bundle/bundle_verifier.py",
        "Independent four-layer ADR-0009 bundle verifier: validates CIDv1 content-addressing, DAG-CBOR canonicality, COSE-Sign1 signatures, and the cross-layer CID chain.",
        [_ref("docs/adr/ADR_0009_Protocol_Bundle_Architecture.md")],
        [_impl("ADR-0009", "adr:0009")],
    ),
    # ── batch 005 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/bundle/layer0_protocol_bundle.py",
        "ADR-0009 Layer 0 generator: embeds CDL-073 truth primitive schemas as DAG-CBOR bundles with optional COSE-Sign1 attestation.",
        [_ref("docs/adr/ADR_0009_Protocol_Bundle_Architecture.md"), _ref("cdl:073")],
        [_impl("ADR-0009 Layer 0", "adr:0009")],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/bundle/layer1_genesis_bundle.py",
        "ADR-0009 Layer 1 generator: links Layer 0 by SHA-256/CIDv1, stores seed claims, initial agent roster, shard topology, and genesis signing key references as DAG-CBOR.",
        [_ref("docs/adr/ADR_0009_Protocol_Bundle_Architecture.md")],
        [_impl("ADR-0009 Layer 1", "adr:0009")],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/bundle/layer2_epoch_snapshot.py",
        "ADR-0009 Layer 2 generator: commits epoch state with graph, agent, and contract digests, linking back to Layer 0 and Layer 1 by CIDv1.",
        [_ref("docs/adr/ADR_0009_Protocol_Bundle_Architecture.md")],
        [_impl("ADR-0009 Layer 2", "adr:0009")],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/bundle/layer3_wire_binding.py",
        "ADR-0009 Layer 3 generator: wire binding descriptor linking a Layer 2 snapshot CIDv1 to message type, agent, epoch, payload digest, and signature reference.",
        [_ref("docs/adr/ADR_0009_Protocol_Bundle_Architecture.md")],
        [_impl("ADR-0009 Layer 3", "adr:0009")],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/bundle/type_registry.py",
        "ADR-0035 type definition registry (default-off): parses and verifies type definition records with CIDv1 identity; CDL-097 ratification token present.",
        [_ref("docs/adr/ADR_0035_Type_Registry.md"), _ref("cdl:097")],
        [_impl("ADR-0035", "adr:0035")],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/ccss/runtime.py",
        "CCSS local runtime implementing X25519+ChaCha20Poly1305 double-layer envelope encryption, contact/identity management, SOCKS5 Tor transport, and prompt injection detection with L2 Unicode obfuscation checks.",
        [],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/ccss/safe_message.py",
        "SafeCCSSMessage frozen dataclass enforcing content-vs-instruction isolation with an as_user_input() JSON wrapper and a pluggable MessageSafetyClassifier Protocol for LLM-backed safety passes.",
        [],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/cli/_cli_error.py",
        "Shared CLI error helpers: emit_cli_error() prints a JSON error payload and exits 2.",
        [],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/cli/_key_utils.py",
        "Key loading utility: base64-decodes key material with a raw-byte fallback for CLI key-registry tools.",
        [],
    ),
    _entry(
        "catchup_batch_005_phase_backfill",
        "ilc_core/cli/atlas_lmdb_cli.py",
        "Read-first Atlas LMDB CLI providing status, validate, node, edges, register-phase-files, apply-edge-batch, and apply-node-edge-plan subcommands with an authority edge gate.",
        [],
    ),
    # ── batch 006 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/d2e_agent_cli.py",
        "Phase 420 agent identity derive CLI; routes derive-agent-id and verify-agent-id subcommands against CDL-042 runtime.",
        [_ref("cdl:042")],
        [_impl("CDL-042", "cdl:042")],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/d2e_lifecycle_cli.py",
        "Phase 421 lifecycle CLI routing timed-out-lifecycle commands against CDL-046 and D2D gossip dependency tokens.",
        [_ref("cdl:046")],
        [_impl("CDL-046", "cdl:046")],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/d2e_query_truth_cli.py",
        "Phase 888 CDL-075 truth store query CLI routing query-truth subcommands against the CDL-075 truth primitive graph store.",
        [_ref("cdl:075")],
        [_impl("CDL-075", "cdl:075")],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/d2e_submit_cli.py",
        "Phase 874/882 CDL-074/075 truth primitive submit CLI routing submit-truth subcommands that validate and record truth primitive submissions.",
        [_ref("cdl:074"), _ref("cdl:075")],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/ep_task_cli.py",
        "HTTP CLI adapter for epistemic task operations with 2-second connect and 30-second read timeouts enforced on all outbound requests.",
        [],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/main.py",
        "Main JSON-first ILC CLI (Phase 264) routing all primitive and operational subcommands and enforcing structured error output.",
        [],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/mcp_cli.py",
        "MCP CLI adapter dispatching ILC tool calls through NodeMCPToolService.",
        [],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/sidecar_cli.py",
        "Sidecar and recipe discovery CLI providing list and run subcommands, including the confidential-contact recipe.",
        [],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/canon_bundle_sign.py",
        "Canon export bundle signing CLI: signs a canon export bundle using an Ed25519 key loaded from the key registry.",
        [],
    ),
    _entry(
        "catchup_batch_006_phase_backfill",
        "ilc_core/cli/canon_bundle_validate.py",
        "Canon export bundle validation CLI: validates the structure and signature chain of a canon export bundle file.",
        [],
    ),
    # ── batch 007 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/config.py",
        "Governance config loader: reads YAML or JSON configuration files with defaults from governance_mvp.json.",
        [],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/__init__.py",
        "Exports CDL-V3 diversity floor and CDL-V7 Popperian gate consensus package symbols.",
        [_ref("cdl:v3"), _ref("cdl:v7")],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/accepted_work_lineage_adapter.py",
        "Phase 1568-Fix2t lineage adapter mapping accepted agent-loop ECU claim payloads to provenance chain records for attribution downstream.",
        [],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/attribution_batch_bridge.py",
        "Phase 1568-Fix2b-3 Python-to-Rust attribution batch bridge converting accepted agent-loop ECU claims to the JSON shape consumed by the Rust attribution_batch_ingest binary.",
        [],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/circuit_breaker_interface.py",
        "CDL-045 circuit-breaker validator: validates breaker activation parameters and evaluates CDL-V3 diversity-quorum trigger conditions.",
        [_ref("cdl:045")],
        [_impl("CDL-045", "cdl:045")],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/clustering.py",
        "SponsorGraph union-find data structure for computing capital cluster diversity across validator sponsor relationships.",
        [],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/diversity_floor_runtime.py",
        "CDL-V3 diversity floor runtime: deterministic cluster-diversity helpers computing max_cluster_share and distinct-cluster floor with bounded penalty scoring.",
        [_ref("cdl:v3")],
        [_impl("CDL-V3", "cdl:v3")],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/engine.py",
        "Core consensus engine coordinating stake governance, ECU fee structure, and validator quorum logic.",
        [],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/epoch_state_runtime.py",
        "Phase 444 epoch-state and quorum-record runtime implementing CDL-051 constitutional consensus and epoch finality.",
        [_ref("cdl:051")],
        [_impl("CDL-051", "cdl:051")],
    ),
    _entry(
        "catchup_batch_007_phase_backfill",
        "ilc_core/consensus/finality_evaluator.py",
        "Phase 445 finality evaluator with CDL-V3 diversity-aware extension that checks whether a quorum record satisfies finality conditions.",
        [_ref("cdl:v3"), _ref("cdl:051")],
        [_impl("CDL-V3 finality", "cdl:v3")],
    ),
    # ── batch 008 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/consensus/governance.py",
        "ECU-anchored congestion-aware fee governance: BacklogMetrics and Governance class computing dynamic fee floors from queue depth and stake utilization.",
        [],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/consensus/popperian_gate_runtime.py",
        "CDL-V7 Popperian gate runtime: evaluates decomposition admissibility and falsifiability criteria for epistemic node submissions.",
        [_ref("cdl:v7")],
        [_impl("CDL-V7", "cdl:v7")],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/consensus/production_bridge.py",
        "Phase 1358 Python-to-ilc_consensus gRPC production bridge referencing ADR-0028 for the language-boundary contract.",
        [_ref("docs/adr/ADR_0028_Python_Rust_Language_Split.md")],
        [_ref("docs/adr/ADR_0028_Python_Rust_Language_Split.md")],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/consensus/reputation.py",
        "Phase 1357 H-011 Decimal reputation runtime: computes per-agent reputation scores from validation, refutation, and consistency history using exact Decimal arithmetic.",
        [],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/crypto/__init__.py",
        "Exports COSE-Sign1 cryptographic primitives (cose_sign1_sign, cose_sign1_verify, cose_sign1_decode).",
        [],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/crypto/cbor_canonical.py",
        "Canonical CBOR encoding/decoding utilities using cbor2 with canonical=True and a 1 MiB input size cap; validates round-trip canonicality.",
        [],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/crypto/cose_sign1.py",
        "Minimal RFC 8152 COSE_Sign1 implementation using Ed25519 (algorithm -8, EdDSA) with canonical CBOR and ILC DAG-CBOR payload validation.",
        [],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/crypto/pq_signature_verify.py",
        "ML-DSA-65 signature verification utility for CDL-101 signed gossip envelopes; fails closed on any import, format, or verification error.",
        [_ref("cdl:101")],
        [_impl("CDL-101 PQ verify", "cdl:101")],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/distribution/__init__.py",
        "Distribution profile constants package marker; exports no protocol symbols.",
        [],
    ),
    _entry(
        "catchup_batch_008_phase_backfill",
        "ilc_core/economics/entropy.py",
        "Economics sandbox entropy helpers: learning_signal() and entropy_weight() compute mid-entropy upweighting over empirical success rates using exact Decimal arithmetic.",
        [],
    ),
    # ── batch 009 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/passive_ecu_attribution_runtime.py",
        "Phase 550 passive ECU attribution runtime computing centrality-weighted, quality-adjusted passive payouts for reuse paths with CDL-060 dependency verification.",
        [_ref("cdl:060")],
        [_impl("CDL-060 passive attribution", "cdl:060")],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/onboarding.py",
        "OnboardingVault: issues 0.02 ECU starter credits per agent and intercepts 50% of earnings as repayment until the debt is cleared.",
        [],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/epoch_attribution_settle_runtime.py",
        "Phase 946 EpochAttributionBatch.settle() runtime implementing CDL-081 attribution settlement (REUSE, CO_AUTHORSHIP, REFUTATION, PROVENANCE) and CDL-083 H-CON-02 ejected-stake treasury distribution.",
        [_ref("cdl:081"), _ref("cdl:083"), _ref("cdl:084"), _ref("cdl:085")],
        [_impl("CDL-081/083/084/085 settlement", "cdl:081")],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/reward.py",
        "Economics sandbox reward helper: simple_claim_reward() computes entropy-weighted reward from stake_spent, hardware potential, and optional success_rate using exact Decimal arithmetic.",
        [],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/telemetry.py",
        "EconomicTelemetry façade wrapping SimpleEpochLedger and OutcomeLogger; RLHook defines a no-op observer interface for RL agents to receive per-task and per-epoch signals.",
        [],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/epoch_ledger.py",
        "SimpleEpochLedger: minimal per-epoch Decimal ledger tracking task counts, ECU spent, and rewards paid with a clearing-price computation.",
        [],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/outcome.py",
        "TaskOutcome dataclass and OutcomeLogger for accumulating sandbox task economic outcomes (stake_spent, reward_paid, success, domain) in memory.",
        [],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/dynamic_ranking_multiplier_runtime.py",
        "CDL-031 dynamic ranking multiplier runtime (guarded, not activated): computes log-shaped multiplier f(w) ∈ [0.80, 1.65] from epistemic weight with anti-dominance cap.",
        [_ref("cdl:031")],
        [_impl("CDL-031", "cdl:031")],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/productive_ecu_expansion_bounty_runtime.py",
        "Productive ECU Expansion Bounty scaffold (Phase 1542p, OBL-027): builds non-activating issuance quotes, delivery stubs, and settlement roots under ADR-0016 proposed authority with 15% cap enforced.",
        [_ref("adr:0016")],
        [_ref("adr:0016")],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/economics/rl_agents.py",
        "Sandbox RL agent: SimpleBanditHook implements epsilon-greedy domain selection using secrets.SystemRandom() and incremental mean updates over TaskOutcome reward_paid signals.",
        [],
    ),
    _entry(
        "catchup_batch_009_phase_backfill",
        "ilc_core/epoch/epoch_emission_production_path.py",
        "Phase 1532p default-off emission production path composing CDL-025/026/027/028/029 quote runtimes into a guarded result with SHA-256 settlement root; PRODUCTION_EMISSION_NOT_ACTIVATED=True.",
        [_ref("cdl:025"), _ref("cdl:026"), _ref("cdl:027"), _ref("cdl:028"), _ref("cdl:029")],
        [_impl("CDL-025/026/027/028/029 production path", "cdl:025")],
    ),
    # ── batch 010 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/epoch_emission_runtime.py",
        "Phase 1345 non-activating epoch emission quote runtime implementing CDL-025 halving schedule, CDL-026 C_MAX=25,920,000 cap, and CDL-027 epoch length constants.",
        [_ref("cdl:025"), _ref("cdl:026"), _ref("cdl:027")],
        [_impl("CDL-025/026/027 emission", "cdl:025")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/ecu_price_clamp_runtime.py",
        "Phase 1351 default-off CDL-030 ECU price clamp quote runtime enforcing P_MIN=0.75 and P_MAX=1.30 bounds derived from CDL-027 parameters.",
        [_ref("cdl:030")],
        [_impl("CDL-030", "cdl:030")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/allocation_distributor_runtime.py",
        "Phase 1347 default-off CDL-029 allocation split quote runtime distributing epoch emission across the 80/15/5 agent/validator/Genesis-overhead pools.",
        [_ref("cdl:029")],
        [_impl("CDL-029", "cdl:029")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/fee_burn_split_runtime.py",
        "Phase 1346 default-off CDL-028 fee-burn split quote runtime burning 10% of fees to the genesis burn pool with non-activating Decimal arithmetic.",
        [_ref("cdl:028")],
        [_impl("CDL-028", "cdl:028")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/treasury_governance_runtime.py",
        "Phase 1348 default-off CDL-047 treasury governance quote runtime enforcing 15% bounty cap, 5% burn floor, and 91% velocity alert threshold.",
        [_ref("cdl:047")],
        [_impl("CDL-047", "cdl:047")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/validator_reward_pool_routing_runtime.py",
        "Phase 1349 default-off CDL-054 validator reward-pool routing runtime computing per-epoch validator share from the CDL-029 allocation pool.",
        [_ref("cdl:054")],
        [_impl("CDL-054", "cdl:054")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/issuance_economics_integration_gate.py",
        "Phase 1352 non-activating issuance economics integration gate composing the Phase 1345–1351a quote runtimes and verifying quote-level debit/credit conservation.",
        [],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/canonical_economic_event.py",
        "Phase 1534p canonical economic event record schema and emitter: builds typed CanonicalEconomicEventRecord structs from CDL-025/027/028/029 emission path output.",
        [_ref("cdl:025"), _ref("cdl:029")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/epoch_boundary_witness_runtime.py",
        "Epoch-boundary witness runtime implementing CDL-057 epoch boundary attestation with CDL-055 staking liveness dependency.",
        [_ref("cdl:057"), _ref("cdl:055")],
        [_impl("CDL-057", "cdl:057")],
    ),
    _entry(
        "catchup_batch_010_phase_backfill",
        "ilc_core/epoch/epoch_snapshot_runtime.py",
        "Phase-314 epoch snapshot generator/verifier runtime with canonical test vectors for snapshot creation, bootstrap, and epoch retention.",
        [],
    ),
    # ── batch 011 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/epoch/genesis_tranche_reconciliation_runtime.py",
        "Phase 1568-Fix2q Genesis tranche reconciliation runtime separating three Genesis-related value surfaces (genesis burn pool, CDL-029 overhead, CDL-048 tranche) without activating any wallet or settlement path.",
        [_ref("cdl:029"), _ref("cdl:048")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/epoch/ejected_stake_distribution_production_path.py",
        "Phase 1541p default-off ejected-stake distribution production path wrapping CDL-083/H-CON-02 quote runtimes with SHA-256 settlement root; no stake liquidation or wallet write activated.",
        [_ref("cdl:083")],
        [_impl("CDL-083 ejected stake", "cdl:083")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/epoch/treasury_validator_reward_production_path.py",
        "Phase 1540p default-off treasury and validator reward production path wrapping CDL-047 and CDL-054 quote runtimes; no treasury transfer or payout activated.",
        [_ref("cdl:047"), _ref("cdl:054")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/eve/capsule_builder.py",
        "EVE capsule builder and signing utilities per ADR-0006: builds capsule manifests from entries and signs them using COSE-Sign1 with Ed25519.",
        [_ref("docs/specs/eve_capsule_format_v0.1.md")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/eve/capsule.py",
        "EVE capsule verification utilities per ADR-0006: loads and validates capsule manifests and verifies COSE-Sign1 signatures.",
        [_ref("docs/specs/eve_capsule_format_v0.1.md")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/exceptions.py",
        "Centralized ILC domain exception hierarchy defining typed exception classes for stake, epoch, graph, gossip, ledger, protocol, and CLI error conditions.",
        [],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/genesis/assertion_schema.py",
        "Phase 858 HB-001 genesis assertion schema: GenesisAssertionContent, GenesisValidatorEntry, canonical JSON payload encoding for ML-DSA-65 signing, and structural validation.",
        [_ref("cdl:073")],
        [_impl("CDL-073 genesis assertion", "cdl:073")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/genesis/genesis_intervention_runtime.py",
        "Phase 1355 default-off CDL-V6 Genesis intervention guardrail runtime: records and audits extraordinary intervention decisions within three-lifetime and epoch-60 outer-sunset bounds.",
        [_ref("cdl:v6")],
        [_impl("CDL-V6", "cdl:v6")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/genesis/validator_bootstrap_runtime.py",
        "Genesis validator bootstrap runtime: verifies epoch-zero state, enrollment records, and derives agent IDs from CDL-042 derivation rules.",
        [_ref("cdl:042"), _ref("cdl:051")],
    ),
    _entry(
        "catchup_batch_011_phase_backfill",
        "ilc_core/genesis/admission_control_bootstrap.py",
        "Genesis validator bootstrap admission-control runtime (Phase 481): builds admission control bundles from enrollment records and epoch-zero state against CDL-040.",
        [_ref("cdl:040")],
        [_impl("CDL-040 admission", "cdl:040")],
    ),
    # ── batch 012 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/genesis/genesis_state_bundle_runtime.py",
        "Phase-312 genesis state bundle generator/verifier runtime with canonical ceremony step validation and test vectors for mainnet genesis bundle construction.",
        [],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/genesis/genesis_authority_assertion.py",
        "Phase 1557 HB-001 genesis-authority assertion builder wiring caller-facing helpers over the Phase 858 assertion schema to produce unsigned assert.truth envelopes.",
        [_ref("cdl:073")],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/genesis/serving_receipt.py",
        "Phase 1559 HB-002 known-peer serving receipts: builds, fetches, and verifies serving receipts over HTTPS with 30-second timeout and 1 MiB response cap.",
        [],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/genesis/invitation_provenance_record.py",
        "Phase 1562 invitation provenance records: builds and atomically persists InvitationProvenanceRecord structs linking inviter, invitee, serving receipt, depth, and parent invite.",
        [],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/genesis/schema.py",
        "Loads the canonical EpistemicWorkTask JSON schema from the ilc_core.genesis package resource epistemic_work_task_schema_v1.json.",
        [],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/genesis/work_task.py",
        "EpistemicWorkTask Pydantic model with five task classes, six task states, Decimal ecu_estimate, and five verification methods.",
        [],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/governance/challenge_node_runtime.py",
        "CDL-006 challenge-node runtime (Phase 1382): validates schema, verifies 3-body affirmative quorum, and writes deterministic audit-path records.",
        [_ref("cdl:006")],
        [_impl("CDL-006", "cdl:006")],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/governance/fork_legitimacy_runtime.py",
        "CDL-009 fork-legitimacy operator inspection runtime (Phase 1383): validates badge schema and eligibility rules for fork-signal artifacts.",
        [_ref("cdl:009")],
        [_impl("CDL-009", "cdl:009")],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/graph/agent_graph_projection_runtime.py",
        "Phase 1229 read-only deterministic graph projection runtime for digital agents: produces projection dicts for authority, claim, provenance, economic, and branchial convergence views.",
        [],
    ),
    _entry(
        "catchup_batch_012_phase_backfill",
        "ilc_core/graph/sidecar_query_runtime.py",
        "Phase 1237 read-only sidecar query runtime performing ego-graph, centrality-metrics, and convergence-trace queries over Phase 1229 graph projection dictionaries.",
        [],
    ),
    # ── batch 013 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/graph/sidecar_public_path_preflight.py",
        "Phase 1278 sidecar public-path authorization preflight: records fail-closed checks required before a future non-loopback projection endpoint, but does not bind any socket or serve data.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/hardware.py",
        "HardwareArchetype dataclass and YAML/JSON loader for hardware capability profiles used in economics sandbox simulations.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/harness/idle_capacity_scheduler.py",
        "Private idle capacity scheduler stub (not activated): selects up to MAX_TASKS_PER_WINDOW maintenance candidates from scored agent nodes using Decimal epistemic weight.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/harness/local_node_capture.py",
        "Private local node capture helper: builds deterministic LocalNodeSnapshot objects for private graph-shaped artifacts with consent gate enforcement.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/harness/maintenance_task_executor.py",
        "Private deterministic maintenance task executor: converts scheduled fixtures into QueryResponseArtifact objects with canonical JSON and SHA-256 content addressing.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/harness/provider_usage_adapter.py",
        "Private local token-budget tracker: accumulates ProviderBudgetSnapshot records from LLM provider usage telemetry (not protocol truth).",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/harness/co_attestation_receipt.py",
        "Private local co-attestation fixture: builds CoAttestationReceipt from up to 16 attestation signatures with canonical JSON and receipt SHA-256.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/harness/consent_gate.py",
        "Private local capture consent gate: evaluates ConsentDecision records per subject_id/purpose pair before allowing private artifact transitions.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/harness/local_immutable_store.py",
        "Private file-backed immutable store (Phase 1485p): persists LocalLedgerEntry records for ConsentGate-approved harness artifacts with mkstemp+os.replace atomic writes.",
        [],
    ),
    _entry(
        "catchup_batch_013_phase_backfill",
        "ilc_core/identity/endorsement_packet_schema.py",
        "CDL-069 epoch endorsement packet schema: field validation, COSE_Sign1 signing payload construction, and agent_state_root specification.",
        [_ref("cdl:069")],
        [_impl("CDL-069 endorsement schema", "cdl:069")],
    ),
    # ── batch 014 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/identity/agent_id_runtime.py",
        "CDL-042 agent identity derivation runtime: deterministically derives 96-char hex agent IDs from identity seeds.",
        [_ref("cdl:042")],
        [_impl("CDL-042", "cdl:042")],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/identity/epoch_endorsement_runtime.py",
        "CDL-069 epoch endorsement protocol runtime: EpochEndorsementPacket dataclass, EndorsementCache validator-side state, liveness assertion and ecu_commitment derivation.",
        [_ref("cdl:069")],
        [_impl("CDL-069 endorsement runtime", "cdl:069")],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/identity/log_redaction_runtime.py",
        "HIGH-001 AgentID log redaction helpers: produces deterministic epoch-scoped redaction tokens from AgentID material before passing to logging sinks.",
        [],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/identity/genesis_record_schema.py",
        "CDL-069 genesis record schema runtime: four-field SHA-384 commitment structure, blinding factor derivation, and recovery transaction protocol.",
        [_ref("cdl:069")],
        [_impl("CDL-069 genesis record", "cdl:069")],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/identity/pq_agent_sign_bridge.py",
        "Private rehearsal bridge to the Rust pq_agent_sign binary: prompts for seed via TTY-hidden getpass and pipes it to the signer without exposing it as an argument or env var.",
        [],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/identity/sybil_resistance_runtime.py",
        "CDL-V2 Sybil resistance runtime: validates sponsor diversity, cluster diversity, and invitation-chain depth constraints.",
        [_ref("cdl:v2")],
        [_impl("CDL-V2", "cdl:v2")],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/ledger/exact_numeric.py",
        "Exact numeric helpers: to_decimal(), decimal_to_canonical_string(), and parse_non_negative_decimal() with NaN/Infinity rejection for all ECU boundary inputs.",
        [],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/ledger/backend.py",
        "In-memory settlement ledger backend: EpochRecord, InMemoryLedgerBackend, StakeSnapshot-based reward distribution, and abstract LedgerBackend interface.",
        [],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/ledger/stake_snapshot.py",
        "StakeSnapshot frozen dataclass capturing per-epoch agent stake distribution with invariant checking that the sum of per-agent stakes equals total_stake.",
        [],
    ),
    _entry(
        "catchup_batch_014_phase_backfill",
        "ilc_core/ledger/settlement_metrics.py",
        "Computes aggregate settlement metrics from the ledger (total epochs, settled/rolled-back/superseded counts, total rewards distributed and stubbed).",
        [],
    ),
    # ── batch 015 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/ledger/ledger_export.py",
        "Exports ledger state to LedgerStateExport JSON/CSV, optionally including stake distribution checks per epoch.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/ledger/canon_export.py",
        "Exports canonical ledger state as canon_state.json with SHA-256 hash commitment over sorted-key JSON.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/ledger/persistent_backend.py",
        "FileLedgerBackend: persistent file-based ledger backend storing epoch records, stake snapshots, and balances as JSON files with atomic writes.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/ledger/lmdb_backend.py",
        "LmdbLedgerBackend: LMDB-backed ledger backend storing epoch records, stake snapshots, and balances with 256 MiB default map size.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/distribution/package_profiles.py",
        "ILC package profile constants (Gap 14, Phases 1436a-1436b): defines five canonical Python package profile names (protocol-core, operator-node, openclaw-hosted, public-rc, dev).",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/distribution/genesis_package_manifest.py",
        "Deterministic Genesis package membership manifest helpers: scans Atlas nodes to build a Merkle root over public-protocol-graph file members for local verification.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/distribution/materialization.py",
        "Public-RC reference implementation materialization helpers (Fix83): generates manifests, fetches files from cache/repo/tarball/HTTP, verifies SHA-256 hashes, and produces reconstruction receipts.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/encoding/__init__.py",
        "ILC encoding package exports: DAG-CBOR encode/decode, CIDv1 node ID generation, and strict profile validation primitives.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/encoding/cidv1.py",
        "CIDv1 generation and parsing: derives content-addressed NodeIDs using DAG-CBOR codec (0x71), SHA2-256 multihash (0x12), and base32 lowercase multibase encoding.",
        [],
    ),
    _entry(
        "catchup_batch_015_phase_backfill",
        "ilc_core/encoding/dag_cbor.py",
        "Deterministic DAG-CBOR subset encoder/decoder: definite-length CBOR with canonical map key ordering, minimal integer encoding, no floats, no tags, and 64-level nesting cap.",
        [],
    ),
    # ── batch 016 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/encoding/varint.py",
        "LEB128-style unsigned variable-length integer encoder/decoder for CIDv1 multihash prefix construction.",
        [],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/__init__.py",
        "CDL-052 epistemic runtime package exports: jury gate, shadow ingestion harness, jury assignment, acceptance authority classification, incentives, review lane, maintenance lottery, VRF verifier, and novelty/refutation/reuse centrality runtimes.",
        [_ref("cdl:052")],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/vrf_proof_verifier.py",
        "RFC 9381 ECVRF-EDWARDS25519-SHA512-ELL2 verifier for ADR-0042 jury assignment (Phase 1411): verifies proofs using liboqs/nacl and returns the 64-byte VRF beta output.",
        [_ref("adr:0042")],
        [_impl("ADR-0042 VRF verify", "adr:0042")],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/jury_activation_gate.py",
        "Phase 1398/J-008 production jury activation gate: defines and evaluates ten blocking conditions required before production jury assignment, with Phase 1427 re-run issuing the explicit GO.",
        [],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/jury_incentive_runtime.py",
        "Phase 1401 CDL-091 jury incentive runtime stub: exposes CDL-091 ratification evidence, reviewer payment parameters, and REVIEWER_PAYMENT_NOT_ACTIVATED guard.",
        [_ref("cdl:091")],
        [_impl("CDL-091", "cdl:091")],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/maintenance_lottery_runtime.py",
        "Phase 1409 CDL-093 maintenance lottery runtime stub: exposes CDL-093 ratification evidence, pool funding parameters, and MAINTENANCE_LOTTERY_NOT_ACTIVATED guard.",
        [_ref("cdl:093")],
        [_impl("CDL-093", "cdl:093")],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/review_lane_admission_runtime.py",
        "Phase 1415 ADR-0043 review lane admission runtime: pure, default-off evaluator producing T0.5→T1+ admission quotes with dedup, payment stub, and REVIEW_LANE_PRODUCTION_NOT_ACTIVATED guard.",
        [_ref("adr:0043")],
        [_impl("ADR-0043", "adr:0043")],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/refutation_runtime.py",
        "CDL-052 refutation submission runtime (Phase 478): validates refutation envelope fields and returns RefutationSubmissionResult with reputation event.",
        [_ref("cdl:052")],
        [_impl("CDL-052 refutation", "cdl:052")],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/jury_assignment_runtime.py",
        "Phase 1396/J-006 default-off jury assignment quote runtime: deterministic panel quoting via epoch-hash shadow assignment with VRF integration and CDL-V3 cluster diversity wiring.",
        [_ref("adr:0040")],
        [_impl("ADR-0040 jury assignment", "adr:0040")],
    ),
    _entry(
        "catchup_batch_016_phase_backfill",
        "ilc_core/epistemic/truth_primitive_graph_store.py",
        "CDL-075 truth primitive graph persistence (Phases 879–881): derives CIDv1 node records from validated submissions and writes them through the graph persistence contract with idempotency guards.",
        [_ref("cdl:075"), _ref("cdl:074")],
        [_impl("CDL-075 graph store", "cdl:075")],
    ),
    # ── batch 017 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/novelty_check_runtime.py",
        "CDL-052 novelty-check runtime: validates query fields and returns NoveltyCheckResult indicating whether a CID is novel or a known duplicate.",
        [_ref("cdl:052")],
        [_impl("CDL-052 novelty", "cdl:052")],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/reuse_centrality_runtime.py",
        "CDL-052 reuse-centrality runtime (Phase 537): computes bounded centrality scores using incremental direct-use ratio with a 5% floor.",
        [_ref("cdl:052")],
        [_impl("CDL-052 reuse centrality", "cdl:052")],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/ingestion_shadow_harness.py",
        "Phase 1397/J-007 shadow public-ingestion jury harness: exercises T0.5 quarantine, external-identifier deduplication, J-003 taxonomy classification, and maintenance task lifecycle without activating production ingestion or ECU distribution.",
        [_ref("adr:0041")],
        [_impl("ADR-0041 shadow harness", "adr:0041")],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/aesthetic_panel_runtime.py",
        "CDL-059 aesthetic panel runtime (Phase 532): composes deterministic diverse panels from agent_pool by model_type buckets using SHA-256-keyed ordering.",
        [_ref("cdl:059")],
        [_impl("CDL-059", "cdl:059")],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/truth_primitive_submission_runtime.py",
        "CDL-074 truth primitive submission runtime (Phases 865–868): validates CDL-073 wire-format submissions for six agent-issuable primitives and returns graph-output contracts.",
        [_ref("cdl:074"), _ref("cdl:073")],
        [_impl("CDL-074", "cdl:074")],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/node_submission_runtime.py",
        "CDL-052 epistemic node-submission runtime (Phase 477): validates node submission envelopes and routes to appropriate mode handler.",
        [_ref("cdl:052")],
        [_impl("CDL-052 node submission", "cdl:052")],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/jury_assignment_announcement_runtime.py",
        "Phase 1568-Fix2g jury assignment announcement and recovery runtime: defines push signal, reviewer self-match/ack contract, and missing-assignment recovery receipt without starting a listener or issuing ECU.",
        [],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/jury_finality_evaluator.py",
        "CDL-095 jury verdict finality evaluator (Phase 1494p): evaluates local finality under 2/3 approval threshold with 5-reviewer participation floor; JURY_FINALITY_EVALUATOR_NOT_PRODUCTION guard retained.",
        [_ref("cdl:095")],
        [_impl("CDL-095", "cdl:095")],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/epistemic/jury_acceptance_authority_classification.py",
        "Phase 1568-Fix2u classification-only module naming six current acceptance-authority surfaces without empaneling juries, evaluating finality, or authorizing settlement.",
        [],
    ),
    _entry(
        "catchup_batch_017_phase_backfill",
        "ilc_core/ledger/settlement_verification.py",
        "Verifies ledger settlement by comparing per-agent computed reward shares against epoch summaries with configurable tolerance.",
        [],
    ),
    # ── batch 018 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_bundle_utils.py",
        "Canon bundle utilities: shared helpers for canon export bundle file naming, path construction, and bundle manifest parsing.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_export_format.py",
        "Defines the v0.1 canon export format schema: EpochRecord serialization structure and field ordering for canonical JSON output.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_export_validate.py",
        "Validates canon state JSON against the expected schema, checking fields, types, and hash commitment.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_export_bundle.py",
        "Builds and persists canon export bundles: packages canon state JSON and supporting files into a versioned archive with manifest and content hashes.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_export_bundle_sign.py",
        "Signs a canon export bundle using an Ed25519 private key and writes the detached COSE-Sign1 signature file atomically.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_export_bundle_validate.py",
        "Validates the structural integrity of a canon export bundle, checking manifest completeness and file hash correctness.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_export_bundle_verify_sig.py",
        "Verifies a COSE-Sign1 signature over a canon export bundle manifest using an Ed25519 public key.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_export_bundle_report.py",
        "Produces a structured summary report of a canon export bundle including file count, total size, and verification status.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_loader.py",
        "Loads and validates canon state JSON from file, checking schema version and hash commitment before returning the parsed state.",
        [],
    ),
    _entry(
        "catchup_batch_018_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry.py",
        "Canon bundle key registry: stores, retrieves, and validates named Ed25519 public keys for signing canon export bundles.",
        [],
    ),
    # ── batch 019 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry_sync.py",
        "Syncs canon bundle key registry entries between operator instances by exchanging signed registry manifests.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry_sync_state.py",
        "Persists and loads canon bundle key registry sync state (last-sync timestamps and remote peer registry manifests) atomically.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry_fetch.py",
        "Fetches remote canon bundle key registry manifests over HTTPS with timeout enforcement and SHA-256 content verification.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry_promotion.py",
        "Promotes a key from the staging registry to the active registry after policy review and threshold approvals.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry_channel.py",
        "Manages the CCSS-encrypted channel for canon bundle key registry communications between operators.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry_channel_signing.py",
        "Produces and verifies COSE-Sign1 attestations over canon bundle key registry channel messages.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_key_registry_bundle.py",
        "Packages the current canon bundle key registry into a signed manifest artifact for distribution to peer operators.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_replay_verify.py",
        "Replays a canon export bundle and verifies that all epoch records re-hash to their stored commitments.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_replay_report.py",
        "Produces a structured replay report summarizing epoch re-hash verification results across a canon export bundle.",
        [],
    ),
    _entry(
        "catchup_batch_019_phase_backfill",
        "ilc_core/ledger/canon_bundle_pipeline_report.py",
        "Aggregates pipeline-level status reports across sign, validate, verify, and replay canon bundle workflow steps.",
        [],
    ),
    # ── batch 020 ──────────────────────────────────────────────────────────────
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/canon_bundle_audit_artifact.py",
        "Builds and persists canon bundle audit artifacts capturing operator attestation and review decisions over a bundle manifest.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/ecu_active_layer_runtime.py",
        "ECU active-layer runtime: validates and tracks active ECU balance entries across agent accounts with non-negative Decimal invariants.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/ecu_ilc_lifecycle_runtime.py",
        "ECU/ILC lifecycle runtime: manages the ECU-to-ILC conversion pipeline state, activation gates, and lifecycle event emission.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/public_economics_admission_firewall.py",
        "Public economics admission firewall: enforces the J-008 gate boundary before any public-economics path is activated.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/claimability_proof_binding_runtime.py",
        "Claimability proof binding runtime: validates and records proof-of-eligibility bindings for ECU claimability events.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
        "CDL-048 conversion sweeper runtime: identifies and processes expired ECU-to-ILC conversion candidates within the sweeper epoch window.",
        [_ref("cdl:048")],
        [_impl("CDL-048", "cdl:048")],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/distributed_conversion_schema.py",
        "Distributed conversion schema: defines the canonical field structure and validation rules for distributed ECU-to-ILC conversion artifacts.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/fix2s_activation_packet_verifier.py",
        "Phase 1568-Fix2s activation packet verifier: validates the cryptographic activation packet format and CCSS-SPECTRAL route token before authorizing a conversion activation.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/conversion_candidate_runtime.py",
        "Conversion candidate runtime: identifies ECU balances eligible for ILC conversion based on epoch expiry and claimability proof status.",
        [],
    ),
    _entry(
        "catchup_batch_020_phase_backfill",
        "ilc_core/ledger/__init__.py",
        "Ledger package init: exports LedgerBackend, InMemoryLedgerBackend, and key ledger model types.",
        [],
    ),
]

print(f"Constructed {len(NEW_ENTRIES)} entries")

# Atomic write
with open(LEDGER) as f:
    data = json.load(f)

prev_count = len(data["annotations"])
data["annotations"].extend(NEW_ENTRIES)

tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(LEDGER), suffix=".tmp")
try:
    with os.fdopen(tmp_fd, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    os.replace(tmp_path, LEDGER)
except Exception:
    try:
        os.unlink(tmp_path)
    except FileNotFoundError:
        pass
    raise

print(f"Wrote {len(data['annotations'])} total entries ({prev_count} + {len(NEW_ENTRIES)} new) to {LEDGER}")
