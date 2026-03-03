# ILC ADM-003 Reference Agent Architecture v0.1

Status: Phase-292 architecture lock artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Define the canonical reference-agent architecture boundaries for post-ratification implementation planning.

Scope:
- architecture-level decomposition,
- signing and key-isolation boundary definition,
- dependency and phased rollout mapping.

## 2. Architecture layers and responsibilities

Layer model:
1. Interface layer: CLI/SDK command surfaces and JSON contract adaptation.
2. Orchestration layer: workflow coordination, policy-gated execution planning.
3. Protocol layer: canonical validation, ratification-aware policy evaluation.
4. Runtime integration layer: storage/network adapters and environment bindings.

Responsibility split:
- policy interpretation remains separated from transport/runtime adapters,
- deterministic protocol behavior remains isolated from UI concerns.

Role decomposition:
- `Evaluation Panel Member`
- `Graph Observation / Schema Evolution Analyst`

The 7+1 evaluation panel is case-evaluation infrastructure, not a standing constitutional authority.

Evaluation Panel Member evaluates task outputs, decomposition validity, and ILC attribution; it does not continuously survey the whole graph.

Graph Observation / Schema Evolution Analyst monitors public-graph patterns, surfaces candidate field-elevation proposals, and publishes evidence summaries for governance lanes; it does not directly ratify schema changes.

## 3. Signing and key-isolation boundaries

Signing boundary principles:
- wallet-agnostic signing is mandatory,
- signing provider interface remains abstracted from protocol logic,
- private key material must remain outside protocol-state payloads.

Key-isolation boundary:
- signing requests use detached payload digest contracts,
- provider isolation is required for local, hardware, and external wallet backends.

`kid` privacy boundary:
- COSE `kid` must not contain raw public key material,
- `kid` values are opaque routing identifiers only.
- kid values are opaque routing identifiers only.

## 4. Protocol/SDK/runtime dependency map

Dependency map:
- protocol invariants and CDL states feed SDK command-level affordances,
- SDK command contracts feed runtime adapters,
- runtime adapters must not bypass protocol validation boundaries.

Governance-preparation boundary:
- Continuous graph observation and schema-evolution preparation are analytics/governance-preparation functions, not ratification authority.
- ADM-003 defines role boundaries; a separate governance artifact defines schema-evolution workflow.
- The graph-observation role may prepare evidence summaries for future CDL lanes but may not open or ratify CDL rows by itself.
- Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.
- This role resolution authorizes Window 340-344 schema-opening work but does not itself open a CDL row.

Carry-forward dependencies:
- `CDL-032` and `CDL-033` ratification state,
- wallet-agnostic signing strategy handoff,
- D2e identity contract lane (phase 293),
- `docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md`,
- `docs/specs/ilc_integration_coherence_report_336_v0.1.md`,
- `docs/specs/ilc_antigravity_context_capsule_v0.8.md`,
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md`.

## 5. Security and privacy invariants

Invariants:
1. no unsigned state transitions in canonical protocol path,
2. signer identity metadata must preserve privacy boundary constraints,
3. provider compromise must be containable without protocol-layer secret leakage,
4. protocol validation must remain deterministic across replay contexts.
5. Custom-field elevation and validation-lifecycle governance remain blocked until this role split is explicit.
6. Private or semi-private graph activity is not sufficient input for schema-elevation monitoring; the graph-observation role monitors public-graph patterns only.

## 6. Non-goals and phased rollout

Non-goals in this phase:
- no runtime implementation in `ilc_core/`,
- no decision-log mutation,
- no direct CLI feature implementation,
- no opening of `CDL-034` through `CDL-038`,
- no execution of custom-field elevation,
- no reputation threshold locking.

Phased rollout boundary:
- implementation is deferred to D2e identity lanes after contract lock.

## 7. Canonical anchors

- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `docs/specs/ilc_signing_provider_interface_262_v0.1.md`
- `docs/specs/ilc_phase_286_295_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md`

Boundary statement:
- no runtime changes in `ilc_core/` and no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md` in this artifact lane.
