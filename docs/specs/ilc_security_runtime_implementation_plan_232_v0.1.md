# ILC Security Runtime Implementation Plan 232 v0.1

Status: Phase-232 planning artifact (no runtime implementation)
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact locks the runtime implementation plan for `CDL-001`, `CDL-002`, and `CDL-007` after Phase-227 contract bounding. It defines dependency ordering, implementation targets, test strategy, risk/rollback plans, and entry criteria for later runtime phases.

This document is planning-only:
- no `ilc_core/` runtime behavior is implemented here,
- no CDL status fields are mutated,
- no ratification is performed in this phase.

## 2. CDL implementation sequence

| Order | CDL | Runtime objective | Dependency rule | Target implementation window |
| --- | --- | --- | --- | --- |
| 1 | `CDL-001` | Runtime signer-lineage trust-root enforcement (hierarchy, lifecycle, canonical authority linkage, audit record emission). | Foundation lane. Must complete baseline runtime trust-root enforcement before dependent lanes are allowed to close. | Post-239 security runtime window (`Phase 240-241` target). |
| 2 | `CDL-002` | Runtime key-compromise detection, containment, revocation, replacement, and incident recording. | Must start only after `CDL-001` trust-root runtime is active because revocation/replacement must target an established lineage model. | Post-239 security runtime window (`Phase 241-242` target). |
| 3 | `CDL-007` | Runtime rollback supersession, clawback declaration enforcement, and replay/conflict rejection across protocol paths. | Partial parallelism allowed for event-shape scaffolding. Final closure must occur after `CDL-001` runtime establishment so supersession authority attribution is trust-root anchored. | Post-239 security runtime window (`Phase 241-243` target). |

## 3. Deferred-from-Phase-227 mapping per CDL

### 3.1 `CDL-001` deferred mapping

Phase-227 deferred runtime items:
- key-registry schema migration and runtime validator enforcement,
- key custody and rotation automation,
- distributed recovery quorum tooling and incident orchestration,
- hardware-backed signer controls.

Runtime implementation lane must deliver:
- authoritative signer-lineage registry with lifecycle-state transitions (`active`, `rotated`, `revoked`, `recovered`),
- canonical verification path that rejects revoked or non-anchored lineage,
- append-only lineage transition log with replayable records.

### 3.2 `CDL-002` deferred mapping

Phase-227 deferred runtime items:
- compromise detectors and responder automation,
- custody telemetry and alert pipeline,
- production recovery drills with signing quorum infrastructure,
- emergency command controls.

Runtime implementation lane must deliver:
- deterministic compromise trigger pipeline (`suspected`, `confirmed`),
- ordered containment sequence (`freeze_authority`, `quarantine_lineage`, `suspend_new_canonical_signatures`),
- deterministic revoke-and-replace flow with incident record emission.

### 3.3 `CDL-007` deferred mapping

Phase-227 deferred runtime items:
- protocol-level rollback orchestration hooks,
- negative-path supersession/replay enforcement beyond partial channel checks,
- clawback settlement runner integration.

Runtime implementation lane must deliver:
- strict supersession event validation with required rollback tokens,
- runtime rejection of conflicting supersession chains,
- runtime rejection of replayed supersession identifiers,
- runtime enforcement that every rollback declares clawback treatment.

## 4. Test strategy per CDL

### 4.1 `CDL-001` runtime tests

Required test classes:
- lineage chain validation across trust-root and operational signers,
- revoked-lineage signer rejection in canonical authority paths,
- lifecycle transition tests covering `active -> rotated -> revoked -> recovered`.

### 4.2 `CDL-002` runtime tests

Required test classes:
- compromise trigger detection tests for anomaly, custody-loss, coercion, and crypto-compromise signals,
- containment action sequencing tests proving strict ordered execution,
- recovery sequence integrity tests proving replacement lineage validity,
- incident audit record emission tests with deterministic reason-code validation.

### 4.3 `CDL-007` runtime tests

Required test classes:
- rollback supersession event format validation tests,
- clawback declaration token presence and allowed-value tests,
- negative-path replay rejection tests,
- negative-path conflict rejection tests.

## 5. Risk and rollback plan per CDL

### 5.1 `CDL-001` risk and rollback

Risk statement:
- incorrect trust-root migration could reject valid signers or accept invalid lineage.

Rollback mode:
- must support reversible migration checkpoints for lineage-registry writes,
- must include deterministic fallback to last known-valid lineage snapshot,
- must block promotion to dependent `CDL-002` runtime lane until post-rollback verification passes.

### 5.2 `CDL-002` risk and rollback

Risk statement:
- false-positive compromise handling could over-revoke authority; false negatives could preserve compromised keys.

Rollback mode:
- must keep containment actions auditable and reversible where policy allows,
- must support controlled recovery to prior non-compromised lineage when incident classification is corrected,
- must require post-rollback integrity checks on trigger and containment sequencing before lane re-entry.

### 5.3 `CDL-007` risk and rollback

Risk statement:
- rollback-event validation defects could permit replay/state corruption or mismatched clawback semantics.

Rollback mode:
- must preserve immutable supersession audit history while disabling defective enforcement paths,
- must revert to last verified rollback-validation ruleset,
- must require replay/conflict negative-path tests to pass before enforcement is re-enabled.

## 6. Entry criteria for implementation phases

### 6.1 `CDL-001` entry criteria

The following must be true before `CDL-001` runtime implementation begins:
- signer-lineage trust-root contract (`docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`) must exist and remain `open` in decision log,
- implementation-phase prompt and contract tests must pass prompt validation and targeted test gates,
- canonical event schema for lineage lifecycle transitions must exist and must be test-anchored.

### 6.2 `CDL-002` entry criteria

The following must be true before `CDL-002` runtime implementation begins:
- `CDL-001` runtime trust-root enforcement must be implemented and must pass its gate suite,
- compromise-response contract (`docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md`) must remain authoritative for response ordering,
- incident audit record schema must exist and must be deterministic under regression tests.

### 6.3 `CDL-007` entry criteria

The following must be true before `CDL-007` runtime implementation closes:
- protocol supersession/clawback schema must exist and must encode required tokens,
- replay/conflict negative-path tests must exist and must pass,
- trust-root authority mapping from `CDL-001` runtime must exist before final `CDL-007` closure is accepted.

## 7. Non-goals and canonical anchors

Non-goals for Phase 232:
- does not implement `ilc_core/` runtime behavior,
- does not ratify `CDL-001`, `CDL-002`, or `CDL-007`,
- does not mutate CDL status fields,
- does not choose cryptographic algorithms or key sizes,
- does not set governance quorum or economic policy constants.

Canonical anchors:
- `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`
- `docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md`
- `docs/specs/ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md`
- `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
- `docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.2.md`
