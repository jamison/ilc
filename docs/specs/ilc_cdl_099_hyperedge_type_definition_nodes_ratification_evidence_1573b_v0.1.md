# ILC CDL-099 Hyperedge Type Definition Nodes Ratification Evidence 1573b v0.1

**Phase:** 1573b
**Date:** 2026-07-07
**Status:** ratified
**Ratification token:** `cdl_099_ratified`
**Definition-node token:** `definition_node_instances_s8_ratified`

## 1. Identity And Dependency Chain

CDL-099 ratifies the initial hyperedge type definition-node instances required
by ADR-0035 forward obligation S8.

Dependency chain:

| Layer | Status | Evidence |
| --- | --- | --- |
| ADR-0035 | Accepted homoiconic type-definition system | `docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md` |
| CDL-097 | Ratified type-definition node authority | `cdl_097_ratified_phase_1528p` |
| CDL-099 | Ratified initial hyperedge type definition-node instances | `cdl_099_ratified` |

The Phase 1573b prompt referenced `docs/adr/ADR_0004_Truth_Primitives.md`, but
that path does not exist in the live repository. The live ADR-0004 source is
`docs/adr/ADR_0004_Genesis_Primitive_Commit_Epoch.md`; it defines the New Seven
truth primitives, including `commit.epoch`. This evidence also direct-read
`docs/specs/ilc_truth_primitive_permanence_ratification_packet_1211_v0.1.md`,
which records the same primitive set and the consensus-only status of
`commit.epoch`.

## 2. Definition-Node Records

CDL-099 ratifies exactly five definition-node records:

| Type | Record path | Recipe | Irreducible | Governing CDLs |
| --- | --- | --- | --- | --- |
| `panel` | `docs/specs/ilc_cdl_099_definition_node_panel_v0.1.json` | `validate.claim compose link.claim` | false | CDL-081, CDL-083 |
| `co_authorship` | `docs/specs/ilc_cdl_099_definition_node_co_authorship_v0.1.json` | `assert.truth compose link.claim` | false | CDL-081 |
| `refutation_coalition` | `docs/specs/ilc_cdl_099_definition_node_refutation_coalition_v0.1.json` | `contradict.assert compose link.claim` | false | CDL-081, CDL-083 |
| `epoch_boundary` | `docs/specs/ilc_cdl_099_definition_node_epoch_boundary_v0.1.json` | `commit.epoch` | true | CDL-027 |
| `jury_verdict` | `docs/specs/ilc_cdl_099_definition_node_jury_verdict_v0.1.json` | `validate.claim compose link.claim compose commit.epoch` | false | CDL-095, CDL-096 |

Each record has:

- `node_type: "type_definition"`
- `content_type: "type_definition"`
- `target_surface: "HyperEdge.hyperedge_type"`
- `authority_ref: {"cdl": "CDL-097", "ratification_token": "cdl_097_ratified_phase_1528p"}`
- `attribution_policy: "non_attributable"`
- `snapshot_semantics: true`
- `phase: "1573b"`

The records include deterministic `definition_id` values computed by
`ilc_core.bundle.type_registry.compute_type_definition_id`. The runtime registry
remains default-off.

## 3. Jury Verdict Decomposition Resolution

The forward plan left `jury_verdict` as `CANDIDATE_ONLY` with an open question:
whether verdict finality is reducible to truth-primitive composition or
partially irreducible as constitutional resolution machinery.

Phase 1573b resolves the minimum viable CDL-099 type record as reducible:

`validate.claim compose link.claim compose commit.epoch`

Reasoning:

- `validate.claim` covers the jury's adjudicative validation or rejection of the
  claim under review.
- `link.claim` binds the claim node, jury panel, verdict outcome, finality path,
  and governing CDL references into one hyperedge entity.
- `commit.epoch` supplies the snapshot/finality anchor required for a verdict to
  be cited later without changing its meaning.

The constitutional and procedural machinery for type disputes is not smuggled
into the `jury_verdict` type record. It remains open as ADR-0035 forward
obligation S9 and is routed to Phase 1573c / CDL-100.

## 4. Guard Status

`ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED` remains `True` in
`ilc_core/bundle/type_registry.py`.

`HyperEdge.hyperedge_type` remains annotated as `str` in `ilc_core/types.py`.

CDL-099 does not authorize either guard clearance or runtime migration. Any
future graph-loaded type registry activation requires a separate SENSITIVE
activation phase.

## 5. ADR-0035 Forward Obligation S8

ADR-0035 section 7 item 2 requires ratification of definition-node instances for
existing `hyperedge_type` values. CDL-097 explicitly excluded initial
definition-node instances from its own ratification scope.

CDL-099 closes S8 for the five initial pre-RC types listed in this evidence.

Closure token:

`definition_node_instances_s8_ratified`

## 6. ADR-0035 Forward Obligation S9

ADR-0035 section 7 item 5 requires a jury procedure for type disputes.

This remains open. CDL-099 defines the first type records, but it does not
ratify the type-level and instance-level dispute procedure. That work is routed
to Phase 1573c / CDL-100.

Carry-forward:

`cdl_100_type_dispute_procedure_required_phase_1573c`

## 7. Ratification Verdict

CDL-099 is ratified in Phase 1573b under the human GO authorization for
`GO Phase 1573b`.

Verdict token:

`cdl_099_ratified`

## 8. Non-Claims

This phase does not:

- clear `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED`
- migrate `HyperEdge.hyperedge_type` from string to node ID reference
- implement a type-registry cache loader
- activate graph-loaded type definitions
- ratify CDL-100
- add `reuse`, `carry_forward`, or any sixth hyperedge type
- alter wallet, treasury, settlement, minting, production emission, public P2P,
  public repository publication, public RC, Genesis signing, or epoch transition
  state
