# ILC Antigravity Context Capsule v0.7

Status: living document — updated at phase boundaries  
Date: 2026-02-28  
Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.6.md`

Purpose: provide the minimum current architectural and constitutional context needed to execute post-Phase-326 work without reintroducing known defects or creating V-series ratification drift.

## 1. Project Identity

ILC remains a protocol for autonomous digital agents to participate in an epistemic graph through claims, refutations, and economic incentives.

Core identity preserved from v0.6:
- the graph is the computer,
- nodes are content-addressed and typed,
- protocol value depends on epistemic challenge and reuse rather than passive approval,
- ILC is not a generic blockchain substitute and not a traditional token network.

## 2. Core Architectural Invariants

The following remain unchanged from v0.6 and continue to govern all future phases:
- the New Seven truth primitives remain authoritative,
- canonical encoding remains DAG-CBOR + CIDv1 + COSE Sign1 + NDJSON,
- ECU remains a four-component model: reuse, contradiction-resistance, validation, path diversity,
- document precedence remains: principles -> whitepaper -> ratified CDL -> implemented code -> simulations -> draft analysis.

## 3. Project State (as of Phase 326 completion)

Current phase state:
- Phase 326 complete,
- Phase 327 next,
- Window 318-327 closure lane remains pending.

Constitutional state:
- `CDL-020`, `CDL-022`, and `CDL-023` are ratified,
- `CDL-024` remains open,
- `CDL-V1` through `CDL-V7` are open,
- no additional constitutional mutations occurred in Phase 326.

## 4. Window 318-325 Constitutional State

Window summary:
- Phase 319 ratified `CDL-020`.
- Phase 320 ratified `CDL-022`.
- Phase 321 ratified `CDL-023`.
- Phase 322 and Phase 323 carried `CDL-024` to contract/runtime readiness while leaving it open.
- Phase 324 opened `CDL-V1`, `CDL-V2`, and `CDL-V3`.
- Phase 325 opened `CDL-V4`, `CDL-V5`, `CDL-V6`, and `CDL-V7`.

## 5. CDL-V Ratification Authority Rule

Normative rule:
- future CDL-V ratification prompts must treat Section 3 of the corresponding evidence-prelock artifact as authoritative when it is more specific than the compressed `required_artifacts` column in the CDL row,
- the CDL row `required_artifacts` field is shorthand and does not override more specific Section-3 evidence obligations.

Operational implication:
- future ratification prompts must cite the prelock artifact directly and derive their evidence checklist from that artifact,
- prompt authors must not rely on CDL-row shorthand alone.

## 6. CDL-V Ratification Sequencing

Locked sequencing summary:
- `CDL-V2 -> CDL-V3 -> CDL-V4`
- `CDL-V4 <-> CDL-V6`
- `CDL-V5 -> CDL-V7`
- `CDL-V1 has no V-series ordering constraint`

Carry-forward implications:
- `CDL-V5` ratification must include explicit `non-comparable by design` handling,
- `CDL-V7` ratification must include tested graph-entry and reuse-value tie-back requirements,
- `CDL-V7` reproducibility must use a concrete evaluation protocol with explicit tolerance bounds.

## 7. Phase-317 Snapshot Isolation Remediation

Closure-gate state after Phase 326:
- `tools/check_window_308_317_closure_gate_phase_317.sh` is no-write by default for the canonical Phase-316 snapshot,
- explicit snapshot regeneration requires `ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE=1`,
- ordinary validation runs must not mutate canonical snapshot files under `out/monitoring/`.

This rule exists because the old gate behavior wrote `out/monitoring/infrastructure_risk_snapshot_phase_316.json` as a side effect during later-phase entry checks.

## 8. Implementation Frontier

Current near-term work:
- Phase 327 closure gate and 328+ handoff,
- future CDL-024 ratification sequencing,
- future V-series ratification lanes under the locked ordering and evidence-authority rules.

## 9. Key Canonical Anchors

Primary references after Phase 326:
- `docs/specs/ilc_phase_318_327_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_308_317_handoff_317_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_326_v0.1.md`
- `docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v3_quorum_diversity_evidence_prelock_324_v0.1.md`
- `docs/specs/ilc_cdl_v4_reopening_protocol_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_cdl_v5_schema_epoch_translation_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_evidence_prelock_325_v0.1.md`
- `docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md`
