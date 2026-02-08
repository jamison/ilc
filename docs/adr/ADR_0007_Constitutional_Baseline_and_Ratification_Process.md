# ADR-0007: Constitutional Baseline and Ratification Process

**Status:** Accepted  
**Date:** 2026-02-08  
**Context:** Governance and architectural continuity

---

## Summary

Establish a formal constitutional baseline workflow for ILC that is evidence-backed, triage-driven, and ratified through explicit conformance hooks rather than informal chat memory.

---

## Context

ILC governance and architecture intent has accumulated across many historical conversations and phase documents. That creates continuity risk:

1. Important principles may be lost or misremembered.
2. Tactical implementation discussion can be mistaken for constitutional commitments.
3. Future phases may drift from foundational constraints without an explicit ratification pipeline.

The project needs a repeatable method to extract, evaluate, and ratify constitutional-level decisions.

---

## Decision

Adopt a three-stage constitutional process:

1. **Discovery Dredge**
   - Build inventory, raw claim ledger, and reconciliation matrix from historical sources.
2. **Clause Triage**
   - Evaluate candidate clauses via logic gates (scope, evidence, conflict, alignment, ratifiability, MVP criticality).
3. **Ratification Hardening**
   - Convert retained clauses into normative (`MUST`/`SHALL`) language and attach conformance hooks.

### Canonical artifacts for this process

- Discovery and matrices under `docs/research/constitution_*`.
- Draft proposals under `docs/specs/ilc_constitutional_decisions_proposal_v*.md`.
- Open decision register under `docs/specs/ilc_constitutional_decision_log_v*.md`.

### MVP criticality policy

Each retained clause must be labeled:
- `mvp_now`
- `mvp_guardrail`
- `post_mvp`

No clause can be considered “ratified” without an explicit conformance artifact.

---

## Consequences

### Positive

- Architectural and governance intent becomes auditable and reproducible.
- Drift risk drops because ratified clauses require conformance hooks.
- Future phases can distinguish constitutional commitments from policy-layer preferences.

### Tradeoffs

- Additional documentation overhead.
- Requires periodic reconciliation when new high-signal sources appear.

---

## Non-Goals

- This ADR does not ratify any specific constitutional clause by itself.
- This ADR does not define final economics or governance body composition.

---

## References

- `docs/phases/constitutional_discovery_dredge_walkthrough.md`
- `docs/phases/constitutional_hardening_phase_001_walkthrough.md`
- `docs/specs/ilc_constitutional_decisions_proposal_v0.3.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/research/constitution_clause_triage_v0.1.md`
- `docs/research/constitution_mvp_criticality_v0.1.md`
