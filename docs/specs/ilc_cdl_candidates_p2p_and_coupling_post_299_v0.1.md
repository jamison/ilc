# ILC Proposed CDL Candidates: P2P and Coupling Post-299 v0.1

Status: Planning artifact  
Date: 2026-02-25  
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Translate recently agreed architecture constraints (independence, low-latency native P2P, utility-first economics) into concrete governance candidates for upcoming phase windows.

## 2. Candidate register (proposed, not yet created)

| Proposed CDL | Subject | Dependency | Suggested lane |
|---|---|---|---|
| CDL-034 | Communication plane separation contract (hot/dissemination/coordination/settlement) | ADR-0010 | post-300 planning lane |
| CDL-035 | Native P2P transport baseline and no-central-broker dependency rule | ADR-0011 | post-300 planning lane |
| CDL-036 | ECU-ILC-Graph coupling and anti-reflexivity invariants | ADR-0012 | economic monitoring window |
| CDL-037 | External payment boundary (perimeter-only adapter policy) | ADR-0013 | d2e/payment boundary lane |
| CDL-038 | Identity/sybil envelope contract for write-path admission and mesh abuse controls | ADR-0014 | security/runtime planning lane |
| CDL-039 | ECU epoch anchoring policy (1/2/3/adaptive epoch settlement window) | `ilc_ecu_epoch_anchoring_options_and_test_plan_v0.1.md` | Phase-305+ simulation + policy lane |

## 3. Creation guardrails

Before creating any CDL above:
- include explicit non-goals,
- include implementation boundary (docs-only vs runtime lane),
- include deterministic test contract requirements,
- include phase-scoped mutation protections for non-target CDLs.

## 4. Why this ordering

1. Plane and transport semantics first (`CDL-034`, `CDL-035`) avoid implementation drift in D2e runtime lanes.
2. Coupling and settlement policy (`CDL-036`, `CDL-039`) should follow with simulation evidence.
3. Boundary and abuse controls (`CDL-037`, `CDL-038`) lock external exposure and adversarial resilience before scaling.

## 5. Canonical anchors

- `docs/adr/ADR_0010_Communication_Plane_Separation_and_Performance_Boundaries.md`
- `docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md`
- `docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md`
- `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`
- `docs/specs/ilc_phase_298_307_sequence_lock_v0.1.md`
