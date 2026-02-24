# ILC Subjective/Objective Epistemic-Type and Sybil Guardrails (Pre-Canon) v0.1

Status: non-normative synthesis artifact  
Date: 2026-02-23  
Owner lane: Constitution Cluster A (pre-ratification framing)

## 1. Purpose

Consolidate historical design intent and current implementation anchors for:
- objective + subjective coexistence on-graph,
- explicit node epistemic typing,
- reuse-based valuation across types,
- anti-Sybil and anti-gaming controls that preserve graph quality.

This artifact is intended to prepare a future ratification lane, not to mutate runtime behavior.

## 2. Historical intent anchors (chat corpus)

Primary historical evidence that should be treated as design intent:

1) Subjective nodes are allowed and should be explicitly typed:
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:1123`
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:1131`
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:1207`

2) Objective + subjective outputs both carry economic value under different validation pathways:
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:3860`
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:3862`
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:5754`

3) Reuse is a central valuation mechanism and anti-spam pressure:
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:4366`
- `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt:5300`

4) Truth-spectrum framing (math-proof extreme vs artistic/taste extreme):
- `Z_Past_Chats/2025_10_28_ILC - Greeting exchange.txt:967`
- `Z_Past_Chats/2025_10_28_ILC - Greeting exchange.txt:975`
- `Z_Past_Chats/2025_10_28_ILC - Greeting exchange.txt:1168`

5) Subjective/objective gradient as network behavior around a node (reuse/confirmation), not binary node mutation:
- `Z_Past_Chats/2025_06_18_ILC - 4D Cognitive AI Model.txt:2617`

6) Explicit epistemic-type tag model and broadcast policy hooks:
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:2704`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:2710`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:2796`

## 3. Proposed node typing contract (for future canon)

Recommended canonical field:
- `epistemic_type: enum`

Recommended enum values (from historical convergence):
- `objective`
- `subjective`
- `normative`
- `creative_speculative`

Recommended companion fields:
- `confidence` (bounded float),
- `uncertainty_note` (short text),
- `channel` (for propagation policy),
- `privacy_flags` (if applicable).

Rationale:
- keeps one graph, multiple epistemic lanes,
- avoids forcing subjective claims into false objective semantics,
- allows per-type validation and propagation policies without splitting protocol identity.

## 4. Validation and reward policy matrix (candidate)

| Type | Primary validation path | Contradiction path | Reuse valuation path | Core-claim eligibility |
|---|---|---|---|---|
| `objective` | formal/empirical checks + auditor quorum | full refute/invalidation path | full reuse weighting | yes |
| `subjective` | curation + audience pull + diversity checks | limited contradiction semantics | reuse/resonance/curation-weighted | no (unless decomposed/reclassified) |
| `normative` | policy quorum + bounded governance checks | challenge path with governance review | bounded reuse weighting | policy lane only |
| `creative_speculative` | exploratory/gestational review | weak contradiction semantics | reuse discovery weighting | no (default) |

Notes:
- Reuse valuation applies across all types, but payout semantics differ by lane.
- Objective-core promotion should require decomposition/anchoring if source is composite.

## 5. Sybil and anti-gaming guardrail bundle

Current anchor set already available in repo:

1) Reuse-diversity anti-Sybil policy contract:
- `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md`
  - `min_distinct_agents`
  - `max_single_agent_share`
  - `penalty_floor`
  - fail-closed scoring behavior for missing provenance

2) Independence/sponsor-clustering defense path:
- `tests/test_sybil_defense.py`

3) Reuse-diversity invariant and gate coverage:
- `tests/test_reuse_diversity_invariants_phase_216.py`
- `tests/test_reuse_diversity_invariants_gate_phase_216.py`

4) Subjective gating + PB-gaming simulation harness:
- `simulations/sim_subjective_gating_pb_gaming.py`
- `tests/test_sim_subjective_gating_pb_gaming.py`

Recommended minimum anti-Sybil invariants to preserve in future ratification:
- independence is measured at sponsor/root level, not surface account count,
- diversity penalties cannot invert refutation-profitability invariant,
- missing provenance fails closed for scoring,
- citation-loop/collusion pressure is bounded via diversity + cluster damping + audit path.

## 6. What is ready now vs what still needs closure

Ready now:
- design intent is strongly evidenced across historical corpus,
- core anti-Sybil contract + tests already exist,
- simulation harnesses for fairness/gating/econ already exist.

Open closure items:
- canonicalization of `epistemic_type` field and enum semantics in protocol-level schema,
- explicit objective-vs-subjective payout policy boundaries in one ratified artifact,
- recovery and replay of historical A5 gating result sets as versioned reproducible outputs.

## 7. Proposed next ratification-prep work

1) Publish a schema-focused prelock artifact for `epistemic_type` and companion metadata.
2) Re-run recovered historical subjective-gating and kappa sweeps with local output paths and deterministic seeds.
3) Publish a single evidence package with:
- objective/subjective policy matrix,
- Sybil-resilience checks,
- reproducible simulation outputs and command transcripts.
4) Route a dedicated CDL lane for objective/subjective policy lock (without changing runtime in the same phase).
