# ILC Protocol and Runtime Term Contracts v0.1

Status: Draft
Date: 2026-02-16
Phase Anchor: Phase 990 (Now-track protocol and runtime term elevation)

## 1. Purpose

Define explicit architecture-facing contracts for selected `Now` terms promoted from the glossary elevation matrix into active canonical-adjacent use.

This document is terminology-contract only. It does not introduce runtime behavior changes.

## 2. In-Scope Terms

- `Node ID`
- `Canonical Encoding`
- `Deterministic CBOR`
- `Consensus Engine`
- `Node Indexing`

## 3. Contract Definitions

### 3.1 Node ID

Definition:
- Deterministic identifier for graph nodes used across validation, replay, serialization, and reporting boundaries.

Contract:
- Any protocol-facing artifact that references a graph node must use stable `Node ID` values.
- `Node ID` naming must not be replaced by ambiguous alternatives such as `artifact id` in normative protocol/runtime text.

Non-goals:
- This contract does not define a new ID generation algorithm.

### 3.2 Canonical Encoding

Definition:
- Deterministic serialization discipline that preserves byte-level parity and hash parity across implementations.

Contract:
- Protocol/runtime docs must use `Canonical Encoding` to describe the determinism requirement for serialized payloads.
- Determinism requirements must be stated independently from transport and storage details.

Non-goals:
- This contract does not mandate a specific wire transport.

### 3.3 Deterministic CBOR

Definition:
- Preferred binary encoding profile for deterministic serialization in replay-proof and hash-sensitive surfaces.

Contract:
- When binary canonical encoding is referenced for protocol/runtime consistency, use `Deterministic CBOR` terminology.
- Any fallback encoding must be explicitly named as fallback and must not dilute deterministic requirements.

Non-goals:
- This contract does not remove existing JSON fallback pathways.

### 3.4 Consensus Engine

Definition:
- Runtime subsystem that evaluates candidate transitions under acceptance, validation, and settlement rules.

Contract:
- Architecture and runtime docs should use `Consensus Engine` as the canonical subsystem label.
- Avoid role-name collisions between `Consensus Engine`, validators, and policy/governance bodies.

Non-goals:
- This contract does not alter current consensus algorithms or settlement policy.

### 3.5 Node Indexing

Definition:
- Indexed lookup/traversal acceleration model used to avoid full-scan retrieval paths.

Contract:
- Use `Node Indexing` terminology in architecture/runtime docs when discussing indexed retrieval paths.
- Avoid mixing indexing terminology with deprecated full edge-list traversal language in normative text.

Non-goals:
- This contract does not prescribe a single index implementation or storage backend.

## 4. Constraints

- This phase is documentation/spec contract hardening only.
- Governance and economics term ratification is out of scope for this contract.
- This contract does not supersede constitutional decision-log governance entries.

## 5. Traceability

- `docs/architecture/glossary_term_elevation_matrix_v0.2.md`
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`

