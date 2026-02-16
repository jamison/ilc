# ILC Near-Prep Non-Governance Term Contracts v0.1

Status: Draft
Date: 2026-02-16
Phase Anchor: Phase 992 (Near pre-alignment, non-governance terms)

## 1. Purpose

Provide pre-alignment contract language for selected non-governance `Near` terms before full promotion steps.

This document is pre-alignment only and does not ratify governance decisions or introduce runtime behavior changes.

## 2. In-Scope Terms

- `Canonical JSON`
- `Convergent Consensus`
- `Node Load Metrics`

## 3. Pre-Alignment Contracts

### 3.1 Canonical JSON

Definition:
- Deterministic JSON normalization profile used as a fallback when deterministic binary encoding is unavailable.

Pre-alignment contract:
- Documentation must clearly label `Canonical JSON` as fallback rather than primary binary canonical encoding.
- Determinism expectations must be explicit when this term is used.

Non-goals:
- No change to existing binary canonical encoding preference.

### 3.2 Convergent Consensus

Definition:
- Explanatory term describing validator convergence to equivalent outcomes.

Pre-alignment contract:
- Use as descriptive language in architecture and analysis text.
- Do not present `Convergent Consensus` as a separate consensus primitive or new protocol subsystem.

Non-goals:
- No changes to consensus implementation naming or algorithms.

### 3.3 Node Load Metrics

Definition:
- Runtime load indicators such as queue pressure, throughput pressure, and operational balancing signals.

Pre-alignment contract:
- Use the term `Node Load Metrics` for runtime diagnostics and balancing discussions.
- Keep metric naming tied to deterministic report surfaces where those reports exist.

Non-goals:
- No new metric formula definitions or runtime metric collectors are introduced.

## 4. Constraints

- This phase is non-governance pre-alignment only.
- Governance-coupled near terms remain deferred for dedicated governance conflict resolution phases.
- No runtime behavior changes are in scope.

## 5. Traceability

- `docs/architecture/glossary_term_elevation_matrix_v0.2.md`
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`

