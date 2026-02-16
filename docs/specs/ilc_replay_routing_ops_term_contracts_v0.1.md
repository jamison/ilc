# ILC Replay Routing and Operations Term Contracts v0.1

Status: Draft
Date: 2026-02-16
Phase Anchor: Phase 991 (Now-track replay, routing, and operations term elevation)

## 1. Purpose

Define explicit contract language for selected replay, routing, and operations terms promoted from glossary matrix `Now` lane into active canonical-adjacent use.

This document is terminology-contract only. It does not introduce runtime behavior changes.

## 2. In-Scope Terms

- `Backwards Verifiability`
- `Task Routing Protocol (TRP)`
- `Graph KPIs`
- `Devnet Topology`
- `Staking`

## 3. Contract Definitions

### 3.1 Backwards Verifiability

Definition:
- Ability to replay and re-verify state and evidence from historical checkpoints.

Contract:
- Replay-facing protocol/runtime documentation must use `Backwards Verifiability` for re-verification expectations.
- Replay and evidence surfaces should be documented with deterministic re-check semantics.

Non-goals:
- No new replay engine behavior is introduced by this contract.

### 3.2 Task Routing Protocol (TRP)

Definition:
- Routing lifecycle framework for dispatching tasks to execution and verifier paths.

Contract:
- Routing lifecycle language in protocol/runtime docs should use `Task Routing Protocol (TRP)` consistently.
- Avoid parallel naming that creates duplicate routing primitives.

Non-goals:
- This contract does not alter routing algorithms or scheduling policy.

### 3.3 Graph KPIs

Definition:
- Aggregated graph and network indicators used for diagnostics, gating evidence, and tuning discussions.

Contract:
- Operations and release-gating docs should use `Graph KPIs` for aggregated metric surfaces.
- KPI references should be tied to deterministic report surfaces where available.

Non-goals:
- This contract does not define a new KPI formula set.

### 3.4 Devnet Topology

Definition:
- Structured peer and agent arrangement for simulation and development-network validation.

Contract:
- Simulation topology descriptions should use `Devnet Topology` terminology.
- Topology references should distinguish deterministic dev/test layout from production deployment assumptions.

Non-goals:
- This contract does not define production topology constraints.

### 3.5 Staking

Definition:
- Economic collateral posted by participating actors to bind incentives and penalty surfaces.

Contract:
- Documentation must use `Staking` for collateral semantics in participation and risk-binding contexts.
- Staking language should avoid introducing governance ratification claims that are still unresolved.

Non-goals:
- This contract does not ratify unresolved governance/economics decision-log entries.

## 4. Constraints

- This phase is documentation/spec hardening only.
- Governance-linked ratification remains deferred to dedicated governance conflict resolution phases.
- No implementation behavior or consensus economics code changes are in scope.

## 5. Traceability

- `docs/architecture/glossary_term_elevation_matrix_v0.2.md`
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`

