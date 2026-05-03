# ILC Genesis Claim-Composition Projection Plan 1146 v0.1

Status: planning/spec draft; non-canonical; Phase 1146 disposition input
Date: 2026-05-04
Owner lane: SIM-SPECTRAL / Genesis Atlas / RC planning
Sensitivity: NON-SENSITIVE

## 1. Purpose

This document records the main architectural finding from SIM-SPECTRAL-03
Phases 1145 and 1145a:

> The signed 32-node Genesis star map is an authority graph. It should not be
> treated as the final knowledge-work diffusion graph for SIM-SPECTRAL metrics.
> Future spectral work should derive and test a claim-composition projection from
> the signed authority graph.

This plan is input for the Phase 1146 disposition and for any later
SIM-SPECTRAL-04 authorization. It does not mutate the signed Genesis star map.

## 2. Evidence Context

Phase 1145 ran the corrected SIM-SPECTRAL matrix with one isolated variable
change: S1 loaded `out/genesis_core_star_map_v0.1.json`, the signed 32-node
Genesis star map.

Result:

- S1 slope: `0.21355627860399237`
- S3/S1: `1.6736470076736112`
- G2/S1: `2.2539040876901315`

Phase 1145a ran a bounded 180-variant topology calibration audit without
mutating the signed star map.

Result:

- No variant passed the Phase 1145-comparable gate.
- No variant passed the matched-size 32-node gate.
- Matched-size G2 improved materially (`G2/S1 = 0.7460347870544758`).
- Matched-size S3 still failed (`S3/S1 = 0.8310911989859531`, threshold
  `0.6416011282246747`).

Interpretation:

- The Genesis authority graph is not "bad."
- The current SIM-SPECTRAL work graph is mismatched to the layer being measured.
- CDL-085 should remain SIM-gated until a claim-composition projection is tested.

## 3. Layer Separation

The current signed map is best understood as the constitutional table of
contents: durable authority nodes, proof anchors, policies, ADR/CDL surfaces,
and founding artifacts.

SIM-SPECTRAL is trying to measure knowledge-work diffusion: how claims,
validations, refutations, revisions, links, and reuse compose over time.

Those are related but not identical layers.

```text
Signed Genesis authority graph
  -> composition/classification projection
  -> claim-level work graph
  -> SIM-SPECTRAL diffusion harness
  -> CDL-085 disposition evidence
```

The claim-level work graph should be derived from the signed authority graph,
not invented independently.

## 4. Projection Classes

The first pass should classify each Genesis node into one of five projection
classes.

| Class | Meaning | Simulation treatment |
|---|---|---|
| `primitive` | Axiomatic operation or non-decomposed foundation | Stable basis node; not removed; can be invoked by composites |
| `historical_artifact` | Signed record, ceremony, identity, state bundle, or historical governance event | Provenance/attestation anchor; not a high-diffusion claim node |
| `parameterized_policy` | Governance parameter or tunable policy surface | Decompose into parameter claims and constraint claims |
| `claim_composite` | ADR/CDL/spec surface composed from primitives and subclaims | Expand into claim-level nodes and typed edges |
| `runtime_binding_pending` | Schema/runtime surface needing code-module linkage | Held as bridge node until Atlas Tier-3 runtime binding |

These classes are a starting point. They are not a final ontology.

## 5. Initial 32-Node Classification Hypothesis

This table is intentionally marked "hypothesis." It should be reviewed during
SIM-SPECTRAL-04 or a dedicated Genesis composition audit.

| Node | Initial projection class | Rationale |
|---|---|---|
| `truth_primitive:assert.truth` | `primitive` | Genesis truth primitive |
| `truth_primitive:validate.claim` | `primitive` | Genesis truth primitive |
| `truth_primitive:contradict.assert` | `primitive` | Genesis truth primitive |
| `truth_primitive:refute.claim` | `primitive` | Genesis truth primitive |
| `truth_primitive:revise.assert` | `primitive` | Genesis truth primitive |
| `truth_primitive:link.claim` | `primitive` | Genesis truth primitive |
| `truth_primitive:commit.epoch` | `primitive` | Genesis truth primitive / finalization primitive |
| `axiom:logic:01` | `primitive` | Logical foundation |
| `axiom:math:01` | `primitive` | Mathematical foundation |
| `axiom:physics:01` | `primitive` | Physical/entropy foundation |
| `adr:0004_genesis_truth_primitives` | `claim_composite` | Defines/demotes primitive set; decomposable into primitive-definition claims |
| `artifact:genesis_intent_attestation_init_authority_map` | `historical_artifact` | Node 0 / signed origin artifact |
| `artifact:genesis_state_bundle` | `historical_artifact` | Bootstrap state artifact |
| `artifact:canonical_self_describing_bootstrap_boundary` | `claim_composite` | Boundary claim surface for bootstrap/canon behavior |
| `artifact:star_map_demoted_by_adr_0004` | `historical_artifact` | Historical demotion event |
| `genesis_agent:01` | `historical_artifact` | Founder/agent identity anchor |
| `artifact:genesis_agent1_pubkey_record_838a` | `historical_artifact` | Public key record |
| `ceremony:genesis_agent1_keygen_838a` | `historical_artifact` | Key ceremony record |
| `artifact:genesis_authority_assertion_schema` | `runtime_binding_pending` | Schema surface needing runtime linkage |
| `policy:genesis_accrual_governor` | `parameterized_policy` | Policy surface |
| `policy:genesis_theta_hard_0_05` | `parameterized_policy` | Numeric policy parameter |
| `policy:genesis_theta_soft_exp_minus_3` | `parameterized_policy` | Numeric policy parameter |
| `policy:provenance_decay_alpha_0_45` | `parameterized_policy` | Numeric provenance/decay parameter |
| `policy:genesis_authority_sunset` | `parameterized_policy` | Governance/sunset policy |
| `cdl:081_hyperedge_ecu_attribution` | `claim_composite` | Ratified CDL claim surface |
| `cdl:083_panel_quorum_refutation` | `claim_composite` | Ratified CDL claim surface |
| `cdl:084_provenance_chain_attribution` | `claim_composite` | Ratified CDL claim surface |
| `adr:0029_hypergraph_substrate` | `claim_composite` | Accepted ADR claim surface |
| `adr:0030_node_embedding_substrate` | `runtime_binding_pending` | ADR surface with embedding/runtime implications |
| `adr:0032_temporal_hypergraph` | `claim_composite` | Accepted ADR claim surface |
| `adr:0033_star_map_homoiconic_entity` | `claim_composite` | Accepted ADR claim surface |
| `adr:0035_homoiconic_type_definition_system` | `runtime_binding_pending` | Draft-direction type/runtime surface |

## 6. Projection Rules

The projection should be deterministic and reproducible.

Minimum candidate rules:

1. Preserve all 32 signed Genesis nodes as authority anchors.
2. Do not remove Node 0 or any Genesis truth primitive.
3. For `primitive` nodes, emit one stable basis vertex per primitive.
4. For `historical_artifact` nodes, emit low-diffusion provenance/attestation
   anchors rather than high-work claim vertices.
5. For `parameterized_policy` nodes, emit:
   - one policy claim vertex;
   - one parameter vertex for each locked numeric constant;
   - one constraint edge from policy to governed surface.
6. For `claim_composite` nodes, emit subclaim vertices extracted from ADR/CDL/spec
   structure where the source has stable headings or explicit claims.
7. For `runtime_binding_pending` nodes, emit bridge vertices that remain flagged
   until Atlas Tier-3 adds runtime module edges.
8. Every projected vertex must carry `authority_source_ref` back to a signed
   Genesis node.
9. Every projected edge must carry a typed reason:
   `invokes_primitive`, `defines_claim`, `constrains_policy`, `attests_history`,
   `implements_runtime`, or `derives_from`.
10. Output JSON must use deterministic canonicalization for any hashable artifact:
    `sort_keys=True`, stable separators, and `allow_nan=False`.

## 7. Proposed SIM-SPECTRAL-04 Scope

SIM-SPECTRAL-04 should test whether the claim-composition projection, not the
raw authority graph, produces the expected S1 discrimination.

Minimum run plan:

1. Build projection artifact:
   `out/genesis_claim_composition_projection_v0.1.json`.
2. Run S1 against the claim-composition projection.
3. Run matched-size S3 and G2 controls by default.
4. Keep raw 100-node S3/G2 comparisons as secondary historical continuity only.
5. Report both:
   - raw authority-graph result from SIM-SPECTRAL-03;
   - claim-composition result from SIM-SPECTRAL-04.

CDL-085 should not be reconsidered until this projection or an equivalent
model-level fix has been tested.

## 8. Phase 1146 Disposition Language

Phase 1146 should include the following named finding:

```text
raw_authority_graph_is_not_the_right_spectral_work_graph
```

Required interpretation:

- SIM-SPECTRAL-03 did not invalidate the signed Genesis graph.
- SIM-SPECTRAL-03 showed that raw authority topology is not a sufficient
  substrate for the current spectral efficiency metric.
- CDL-085 remains SIM-gated.
- Future work should test the claim-composition projection and require matched-size
  controls.

## 9. Related Forward Obligations

Carry these forward to Phase 1147 or Window 1148+ planning:

1. `sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration`
2. `genesis_32_node_composability_audit_required`
3. `matched_size_controls_required_for_future_spectral_sims`
4. `genesis_canonical_lineage_contract_required_before_public_rc`
5. `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`
6. `public_rc_envelope_hash_transition_policy_required`
7. `contributor_agreement_required_before_public_repo`

## 10. Public Versioning Note

Internal signed envelopes may remain custody artifacts. The first public RC graph
may start its own public version sequence, but any transition from the current
signed root envelope hash
`ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
to a later public envelope must be explicit.

Future tests and docs should distinguish:

- historical internal envelope assertions;
- current public canonical envelope assertions;
- successor-envelope lineage assertions.

This decision must not happen silently during a future phase.

## 11. Genesis Veto Terminology Note

Avoid the phrase "Genesis veto" unless a future CDL explicitly ratifies it.

Current canon supports CDL-V6 extraordinary intervention only:

- capture;
- constitutional violation;
- time-critical emergency;
- mandatory audit;
- sunset/challenge criteria;
- post-hoc CDL-V4 review.

That is not an ordinary governance veto.
