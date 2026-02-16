# ILC Governance and Economics Near-Term Contracts v0.1

Status: Draft
Date: 2026-02-16
Phase Anchor: Phase 994 (Near governance/economics term promotion)
Ratification prerequisite: Phase 993 (`docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`)

## 1. Purpose

Define active canonical-adjacent contract language for governance and economics `Near` terms promoted after scoped governance conflict-set ratification.

This document is terminology-contract only and does not introduce runtime behavior or policy algorithm changes.

## 2. In-Scope Terms

- `Quorum`
- `Slashing`
- `Token Sink`
- `Validator`
- `Reward Surface`
- `Epoch Reward Ledger`
- `Governance Config Surface`
- `Namespace Hierarchy`

## 3. Contract Definitions

### 3.1 Quorum

Definition:
- Minimum participation threshold required for valid governance or validation decisions.

Contract:
- Use `Quorum` for threshold language in governance and validation documentation.
- Distinguish threshold semantics from role semantics.

### 3.2 Slashing

Definition:
- Stake-linked penalty mechanism for provable violations.

Contract:
- Use `Slashing` for penalty and deterrence language tied to stake-backed participation.
- Keep violation conditions explicit and traceable to policy rules.

### 3.3 Token Sink

Definition:
- Mechanism that reduces or locks circulating token supply under defined policy conditions.

Contract:
- Use `Token Sink` for supply-reduction and lockup semantics in economics documentation.
- Distinguish sink mechanisms from issuance controls.

### 3.4 Validator

Definition:
- Role family responsible for verification of claims, evidence, and settlement artifacts.

Contract:
- Use `Validator` for verification-role references.
- Keep role language distinct from runtime subsystem names such as `Consensus Engine`.

### 3.5 Reward Surface

Definition:
- Function family mapping validated work and policy constraints to payout outcomes.

Contract:
- Use `Reward Surface` for payout mapping language.
- Keep formula details traceable to economics artifacts where implemented.

### 3.6 Epoch Reward Ledger

Definition:
- Epoch-scoped accounting surface recording validated reward events and settlement inputs.

Contract:
- Use `Epoch Reward Ledger` when describing epoch payout accounting boundaries.
- Maintain clear boundary between event recording and policy definition.

### 3.7 Governance Config Surface

Definition:
- Explicit governance policy parameter set exposed for controlled protocol evolution.

Contract:
- Use `Governance Config Surface` for configurable governance parameter boundaries.
- Keep references aligned with ratified governance decisions and policy-layer boundaries.

### 3.8 Namespace Hierarchy

Definition:
- Structured namespace layering for governance segmentation, compatibility boundaries, and modular extension.

Contract:
- Use `Namespace Hierarchy` when describing namespace governance and compatibility structure.
- Keep namespace policy references aligned with layer-boundary decisions.

## 4. Constraints

- Promotion is grounded in the scoped governance ratification baseline established in Phase 993.
- This phase does not ratify additional non-scoped decision-log entries.
- No runtime code changes are in scope.

## 5. Traceability

- `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/architecture/glossary_term_elevation_matrix_v0.2.md`
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`

