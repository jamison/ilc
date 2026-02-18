# ILC Reviewer Context Pack v0.1

Status: active reviewer pack
Date: 2026-02-18
Scope: constitutional, architecture, economics, and anti-gaming review context

Delta supplement:
- `docs/specs/ilc_reviewer_context_pack_v0.2_delta.md` (gap-focused reviewer update + historical/canon backtrace map)

## 1. Purpose

Provide one deterministic orientation pack for architectural reviewers so feedback is anchored to ratified artifacts, not fragmented memory.

## 2. Authoritative source precedence

When sources conflict, use this precedence order:

1. Ratified constitutional decisions and ratification bundles:
   - `docs/specs/ilc_constitutional_decision_log_v0.1.md`
   - `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`
   - `docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md`
2. Accepted ADRs:
   - `docs/adr/ADR_0007_Constitutional_Baseline_and_Ratification_Process.md`
   - `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
3. Locked sequence and handoff artifacts:
   - `docs/specs/ilc_main_track_return_sequence_213_221_v0.1.md`
   - `docs/specs/ilc_main_track_return_213_220_handoff_v0.1.md`
   - `docs/specs/ilc_genesis_packaging_distribution_sequence_222_229_v0.1.md`
4. Contract specs and gate scripts tied to implemented phases.
5. Research corpus and historical literature (`docs/research/*`, `Z_Past_Chats/*`) for rationale and provenance.

## 3. Corpus lineage for historical context

Primary source inventory and extraction chain:
- File inventory and hashes: `docs/research/constitution_dredge_inventory_v0.1.md`
- Scan totals and pending conversions: `docs/research/constitution_dredge_meta_v0.1.md`
- Raw extracted ledger: `docs/research/constitution_dredge_raw_v0.1.jsonl`
- Refined candidate matrix: `docs/research/constitution_dredge_matrix_v0.2.md`
- Clause gates and triage: `docs/research/constitution_clause_triage_v0.1.md`
- MVP criticality and guardrails: `docs/research/constitution_mvp_criticality_v0.1.md`, `docs/research/constitution_mvp_guardrails_matrix_v0.1.md`
- Dropped clause memorialization: `docs/research/constitution_drop_ledger_v0.1.md`

Discovery and hardening walkthrough anchors:
- `docs/phases/constitutional_discovery_dredge_walkthrough.md`
- `docs/phases/constitutional_hardening_phase_001_walkthrough.md`

## 4. Current project-state snapshot (through Phase 224)

Implemented and locked in active code/test surfaces:
- Refutation profitability invariant and gate (Phase 212)
- Path-lift counterfactual harness (Phase 214)
- CDL-011 to CDL-015 ratification closure (Phase 215)
- Reuse-diversity anti-Sybil weighting invariants (Phase 216)
- Freshness gate shape, bounds, and Genesis exemption (Phase 217)
- Genesis accrual governor constants and taper simulation checks (Phase 218)
- Consolidated conformance and telemetry schema lock (Phase 219)
- Preflight and closure gate composition for 214-220 (Phases 220-221)
- Sequence lock for Genesis packaging/distribution line 222-229 (Phase 222)
- Scope-capped hygiene backfill (`math.isfinite` in reuse-diversity module) (Phase 223)
- End-to-end integration smoke and install-import contract (Phase 224)

## 5. Canonical invariant map for reviewers

| Invariant surface | Canonical implementation anchor | Contract or gate anchor | Primary regression anchor |
| --- | --- | --- | --- |
| Refutation profitability is structurally enforced | `ilc_core/analysis/utility_flow_rewards.py` | `tools/check_refutation_profitability_invariant_phase_212.sh` | `tests/test_refutation_profitability_invariant_phase_212.py` |
| Reuse-diversity anti-Sybil weighting | `ilc_core/analysis/reuse_diversity_invariants.py` | `tools/check_reuse_diversity_invariants_phase_216.sh` | `tests/test_reuse_diversity_invariants_phase_216.py` |
| Freshness decay with Genesis exemption | `ilc_core/analysis/freshness_gate.py` | `tools/check_freshness_gate_invariants_phase_217.sh` | `tests/test_freshness_gate_phase_217.py` |
| Genesis accrual hard cap and taper | `ilc_core/analysis/genesis_accrual_governor.py` | `tools/check_genesis_accrual_governor_phase_218.sh` | `tests/test_genesis_accrual_governor_phase_218.py` |
| Consolidated conformance schema lock | `ilc_core/analysis/node_value_governance_conformance.py` | `tools/check_node_value_governance_conformance_phase_219.sh` | `tests/test_node_value_governance_conformance_phase_219.py` |
| End-to-end composition and install importability | Integration test and install smoke | `tools/check_genesis_integration_smoke_phase_224.sh` | `tests/test_genesis_integration_smoke_phase_224.py`, `tests/test_genesis_install_smoke_phase_224.py` |

## 6. Open constitutional decisions reviewers must not treat as closed

Still open in decision log:
- `CDL-001` (canonical signer lineage definition)
- `CDL-002` (emergency key compromise response)
- `CDL-007` (rollback resistance baseline)

Anchor: `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 7. Reviewer operating protocol

For architecture reviews:
1. Verify claim against precedence order in Section 2.
2. Confirm whether claim is ratified, open, deferred, or research-only.
3. Cite exact file anchors for both proposed change and constitutional authority.
4. Distinguish code-level bug from policy-level disagreement.
5. If policy-level, route to decision-log workflow rather than ad hoc implementation change.

## 8. Fast-start reading list (minimum)

1. `docs/specs/ilc_constitutional_decision_log_v0.1.md`
2. `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`
3. `docs/specs/ilc_main_track_return_213_220_handoff_v0.1.md`
4. `docs/specs/ilc_genesis_packaging_distribution_sequence_222_229_v0.1.md`
5. `docs/specs/ilc_anti_gaming_simulation_findings_v0.1.md`
6. `docs/specs/ilc_constitutional_context_audit_v0.1.md`
7. `docs/specs/ilc_constitutional_context_audit_response_v0.1.md`
8. `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md` (non-normative strategic supplement)
9. `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` (non-normative strategic supplement)
10. `docs/specs/ilc_reviewer_context_pack_v0.2_delta.md`

## 9. Companion document

This pack is paired with:
- `docs/specs/ilc_anti_gaming_simulation_findings_v0.1.md`
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `docs/specs/ilc_reviewer_context_pack_v0.2_delta.md`

These companion specs summarize anti-gaming rationale, mining economics framing, and pre-epoch capability strategy for reviewer context.
