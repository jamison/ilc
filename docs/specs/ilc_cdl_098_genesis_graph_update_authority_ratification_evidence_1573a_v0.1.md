# ILC CDL-098 Genesis Graph Update Authority Ratification Evidence 1573a v0.1

**Status:** ratification evidence artifact  
**Date:** 2026-07-06  
**Decision vehicle:** CDL-098  
**Phase:** 1573a  
**Owner lane:** Block 6 / Genesis graph authority  
**Sensitivity:** SENSITIVE governance artifact  
**Ratification token:** `cdl_098_ratified_phase_1573a`

## 1. Opening And Ratification Record

Phase 1573a opens, deliberates, and ratifies CDL-098 as the Genesis Graph
Update Authority lane.

The live CDL register previously carried only a historical metadata note in the
CDL-096 row: `cdl_098_status: unconsumed`. Phase 1573a creates the first-class
pipe-delimited CDL-098 row and records it as ratified.

Ratification facts:

- Opening phase: `1573a`
- Opening token: `cdl_098_opened_phase_1573a`
- Ratification phase: `1573a`
- Ratification token: `cdl_098_ratified_phase_1573a`
- Authority token: `genesis_graph_update_authority_ratified_phase_1573a`
- Per-node provenance token: `per_node_provenance_metadata_schema_ratified_phase_1573a`
- Sunset token: `cdl_098_sunset_condition_defined_phase_1573a`
- Base-graph signing authority token: `genesis_base_graph_signing_authority_unlocked_phase_1573a`
- Section architecture token: `cdl_098_section_architecture_types_ratified_phase_1573a`

This phase ratifies authority and schema only. It does not produce, mutate, or
sign `out/genesis_base_graph_v0.4.json`. Phase 1573 remains the signing phase.

## 2a. Authorized Scope

CDL-098 grants Genesis Agent edge-fabric authority over the Genesis-signed base
graph during the bounded genesis period.

Genesis may:

- Sign the full Genesis base graph as a separate signed artifact under CDL-098
  authority. The full base graph is distinct from the 57-node canonical core.
- Issue `SUPERSEDES` edges where a new node annotates or supersedes a prior node
  without deleting or mutating the prior node.
- Issue `REFUTES` edges against community-proposed edges within the
  Genesis-signed subgraph.
- Add new nodes with updated `annotation_method` or corrected edge types.
- Issue versioned graph updates such as `v0.4.1` and `v0.4.2` under this
  authority without per-change governance ratification.
- Preserve all updates as append-only and permanently auditable graph material.
- Apply the per-node provenance metadata schema ratified in Section 2d.
- Use the section architecture object types ratified in Section 2g under the
  limits stated there.

## 2b. Prohibited Scope

Genesis may not:

- Modify truth primitives, ratified CDL parameters, or accepted ADR
  architecture through graph updates.
- Claim governance effects, economic authority, eligibility, or claimability
  through graph updates.
- Delete any node or edge.
- Rewrite content-addressed nodes.
- Use CDL-098 to override community governance on protocol-layer questions.
- Change the 57-node canonical core artifact
  `genesis_core_star_map_v0.4.json`; that artifact remains governed by the full
  CDL/ADR process and the Phase 1573 signing decision.
- Treat a Genesis economic tranche, fee-burn surface, or emergency guardrail
  limit as a standalone graph-authority sunset trigger.
- Sign `AtlasSliceManifest` records for `excluded_private_material` sections.
- Activate the ADR-0035 type registry or create CDL-099 definition-node
  instances through section architecture language.

## 2c. Mechanism

The Genesis base graph remains content-addressed and append-only.

Operational meaning:

1. "Modification" always means a new node plus an explicit relationship edge.
2. A prior node remains present and auditable.
3. A `SUPERSEDES` edge records replacement or correction.
4. A `REFUTES` edge records Genesis disagreement with a proposed edge.
5. Community proposals persist even if Genesis refutes them in the
   Genesis-signed subgraph.
6. Every Genesis-signed node in the base graph carries the provenance metadata
   schema in Section 2d.
7. After Genesis graph-authority sunset, community governance takes over
   curation under the successor process; Genesis-signed content is not deleted.

## 2d. Per-Node Provenance Metadata Schema

Every node in the Genesis base graph must carry the following metadata fields:

```json
{
  "annotation_method": "manual_reviewed | scripted_extractor | manual_reviewed_over_scripted",
  "annotation_phase": "<fix_batch_id, e.g. fix33 | fix38_batch_001>",
  "annotation_reviewer": "genesis_agent:01 | codex | sonnet",
  "genesis_signature_version": "v0.4",
  "update_authority": "genesis_until_sunset",
  "update_authority_cdl": "cdl_098",
  "graph_trace_status": "candidate | trace_declared | trace_missing"
}
```

This schema is ratified as a protocol requirement for the Genesis base graph.
It exists because the graph contains multiple evidence-quality strata:
manual-reviewed annotations, scripted extractor annotations, and
manual-over-scripted corrections. The network must be able to distinguish those
sources instead of treating all signed graph material as uniformly reviewed.

## 2e. Sunset Condition

CDL-098 graph authority sunsets only when all of the following are satisfied:

1. CDL-017 bootstrap transition criteria are satisfied. This is the floor
   condition because CDL-017 governs validator participation and bootstrap
   transition criteria.
2. The homoiconic test registry is live.
3. The graph can self-validate without Genesis curation as a required
   authority source.

The CDL-098 sunset condition is separate from validator participation sunset.
Validator governance can advance under CDL-017 while graph curation remains
Genesis-guided until the graph has the tools to validate itself.

At sunset:

- Genesis-signed content remains in the graph.
- Community governance takes over curation.
- No Genesis-signed content is deleted.
- Later updates continue through append-only graph mechanisms.

## 2f. Relationship To Prior Governance

| Prior instrument | What it covers | What CDL-098 adds |
|---|---|---|
| Phase 590 coherence lock | Genesis authority is bounded, must recede, and is not permanent sovereign override | CDL-098 operates inside that bound and defines the graph-update authority surface |
| CDL-017 | Validator participation governance, bootstrap transition criteria, and validator-authority Genesis sunset floor | CDL-098 covers graph curation and edge-fabric authority, a separate surface |
| CDL-V6 | Extraordinary Genesis intervention for capture, constitutional violation, or time-critical emergency | CDL-098 is ordinary genesis-period graph curation, not emergency intervention |
| Phase 599/600/602 Genesis tranche closure | Fixed 5 percent economic target-plus-cap surface and evidence bounds | No graph-update authority sunset; economic tranche realization is not a CDL-098 sunset trigger |
| ADR-0020 | Knowledge-node-first design principle and migration discipline | CDL-098 supplies a ratified graph-authority lane for base-graph curation and later graph-native migration |
| ADR-0033 | Published star-map result nodes as advisory navigation artifacts | CDL-098 covers base-graph curation and slice/section schemas, not star-map advisory semantics |
| ADR-0035/CDL-097 | Type-definition node authority and default-off type registry scaffold | CDL-098 section architecture schemas are not ADR-0035 type-definition nodes |

## 2g. Section Architecture Object Types Authorized Under CDL-098

These types are CDL-098-governed graph curation/export schemas. They are NOT
ADR-0035 type definition nodes and are NOT CDL-099 definition-node instances.
Machine-readable non-claim: GraphSection, CROSS_SECTION_REF, and
AtlasSliceManifest are NOT ADR-0035 type definition nodes.
No runtime activation, export tooling, or signing pipeline is authorized by
this section.

Genesis may:

- Classify nodes into `GraphSection` regions using the Fix55
  `graph_projection` vocabulary during genesis-period graph curation passes.
- Issue `CROSS_SECTION_REF` edges, stub or resolved, within the Genesis-signed
  base graph.
- Sign `AtlasSliceManifest` records for public sections:
  `genesis_core_star_map`, `public_protocol_graph`, and
  `support_candidate_graph`, under the same append-only content-addressed
  invariants as other CDL-098 operations.

Genesis may not:

- Sign `AtlasSliceManifest` records for `excluded_private_material` sections.
  Those are owner-signed, per `docs/specs/ilc_private_layer_policy_v0.1.md`.
- Change the section label of a committed node in place. Section label changes
  require a new node plus a `SUPERSEDES` edge.
- Activate export tooling, public slice distribution, or any signing pipeline
  under Section 2g. Those are separate implementation phases.
- Treat `GraphSection`, `CROSS_SECTION_REF`, or `AtlasSliceManifest` as
  ADR-0035 type definition nodes or as CDL-099 definition-node instances.

Section 2g emits
`cdl_098_section_architecture_types_ratified_phase_1573a`.

## 3. Reconciliation Note

CDL-098 graph authority is separate from adjacent Genesis-related surfaces.

The Phase 599/600/602 Genesis economic tranche records the fixed 5 percent
target-plus-cap surface: `theta_hard = 0.05`, `1,296,000 ILC` of
`C_max = 25,920,000`. Reaching, preserving, or realizing that economic tranche
does not sunset CDL-098 graph update authority by itself.

The CDL-V6 emergency guardrail has its own bounds: one-epoch suspension,
maximum three lifetime invocations, and an epoch-60 outer ceiling. That
emergency guardrail is not the CDL-098 graph update authority sunset condition.

The older design language about "5-6% mined" is not a standalone graph-update
sunset trigger. Machine-readable non-claim: "5-6% mined" is not a standalone graph-update sunset trigger.

## 4. Non-Claims Of CDL-098

CDL-098 does not:

- Sign any graph artifact.
- Produce `out/genesis_base_graph_v0.4.json`.
- Push any public repository.
- Activate public RC.
- Activate public P2P or public relay serving.
- Clear any `NOT_ACTIVATED` guard.
- Write wallet, treasury, mint, settlement, or ledger state.
- Delete or rewrite graph content.
- Override Phase 590, CDL-017, CDL-V6, ADR-0020, ADR-0033, or ADR-0035.
- Activate the ADR-0035 type registry; `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED`
  remains `True`. CDL-098 does NOT activate the ADR-0035 type registry.
- Create CDL-099 definition-node instances.
- Authorize export tooling, public slice distribution, or section signing
  pipelines beyond the schema authority in Section 2g.

## 5. Carry-Forward To Phase 1573

Phase 1573 may use CDL-098 as the authority basis for the full Genesis base
graph signing path.

Carry-forward facts:

- `genesis_core_star_map_v0.4.json` remains the 57-node core signing artifact
  and is CDL-098-independent.
- `out/genesis_base_graph_v0.4.json` is the full-repo base graph artifact and
  is CDL-098-gated.
- Phase 1573 must verify the per-node provenance metadata schema before signing
  the base graph.
- Phase 1573 must not treat CDL-098 ratification as public RC activation.

## 6. Ratification Verdict

CDL-098 is ratified at Phase 1573a.

**Verdict token:** `cdl_098_ratified_phase_1573a`  
**Public path:** blocked  
**Runtime activation:** none  
**Graph update execution:** none  
**Genesis signing:** deferred to Phase 1573
