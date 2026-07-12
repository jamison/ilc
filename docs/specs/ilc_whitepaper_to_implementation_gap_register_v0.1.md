# ILC Whitepaper-to-Implementation Gap Register

**Version:** v0.1
**Date:** 2026-06-29
**Status:** Internal engineering gap register. Not part of the whitepaper. Not a
ratified CDL or ADR.

## Purpose

The whitepaper is allowed to describe the ideal ILC architecture: the final
math, science, threat model, and protocol shape the project is building toward.
This register is the separate engineering document that tracks the gap between
that ideal description and current implementation or ratification state.

This document must not be used to soften the whitepaper text. Its job is to
route implementation, simulation, governance, and activation work so no
whitepaper-critical concept is orphaned.

## Classification

| Status | Meaning |
| --- | --- |
| `implemented_default_off` | Code exists, but activation or public use is blocked by a guard or phase gate. |
| `implemented_partial` | Some code or documents exist, but the full protocol path is incomplete. |
| `diagnostic_only` | Calculation or report exists, but it has no settlement or authority effect. |
| `research_or_sim_required` | The concept is scientifically plausible but needs SIM, adversarial analysis, or parameter ratification. |
| `cdl_or_adr_required` | A governance artifact must authorize the behavior before runtime or settlement use. |
| `post_rc_target` | Correctly deferred until after the first public RC unless a later sequence lock pulls it forward. |

## Gap Matrix

| Whitepaper claim family | Current implementation anchor | Gap | Route |
| --- | --- | --- | --- |
| Directed morphogenetic hypergraph | ADR-0029, current Atlas typed nodes/edges, `HyperEdge` planning, CDL-099/100 plan | The public Atlas is still mostly binary typed edges plus metadata. First-class hyperedge definition nodes and runtime type-registry activation are not public-live at scale. | CDL-099/100, then ADR-0035 type-registry activation. Keep public-RC graph tooling honest about current edge representation. |
| Merkle-Laplacian and PoSK | Research/spec docs, spectral diagnostics, Fix72-style measurements | PoSK is not live consensus or admission machinery. Spectral metrics are useful diagnostics but not a standalone security guarantee or settlement gate. | Fix2h routing matrix; post-RC SIM/CDL lane before any consensus, eligibility, or settlement use. |
| PoIL → ECU → ILC conversion | OBL-020/021/022/027 paths, Fix2d ECU/PoIL production-path audit, CDL-048 conversion concepts | The live soft-RC path still needs exact production wiring for node submission, jury/review acceptance, ECU lot creation, conversion, allocation, and settlement-root verification. | Phase 1568 Fix2b-3, Fix2c, Fix2d, plus any follow-up fix prompts from the live rehearsal. |
| Jury privacy, discoverability, and notification | CDL-036/076/077 pull pattern, Fix2g minimal announcements, ADR-0040, candidate private-assignment CDL | The narrow push/pull mechanism exists, but blind jury assignment, sealed task handles, switch-out privacy, non-response recovery, and jury-as-node semantics need integrated authority and testing. | Fix2i SIM/amendment, then Fix2j candidate CDL for private assignment/deliberation channel. |
| Runtime-memory-substrate custody and representational independence | New whitepaper threat-model work; Engram/CXL external memory papers; no existing ILC runtime control | Model-family diversity and weight hashes do not prove epistemic independence if jurors rely on shared mutable memory pools or the same external substrate operator. | Fix2h gap-routing row, Fix2i SIM C.5 design, Fix2j substrate-custody authority, and post-RC harness H2 implementation route. |
| Harness sidecar and model-router last-mile execution | `ilc_core/harness/` local modules, `PUBLIC_RC_EXCLUDE_PRIVATE_AGENTIC_HARNESS`, sidecar registry concepts | Model-router, endpoint adapters, compliance-capture CLI, multi-model endorsement, GAIA-X/sovereign adapters, and Werner-credit wiring are not active public-RC protocol surfaces. | Harness sidecar forward plan, H1/H2 prompt drafts after valid sequence-lock slot, H3 only with sensitive GO and production-path authority. |
| Sidecars as typed subgraphs | Sidecar architecture docs, registry manifest, package profiles | Sidecar nodes can be represented with current binary edges, but contributor sidecar registry, init-node schema, recipe/package lifecycle, and activation lifecycle need formalization. | Post-RC sidecar typed-subgraph schema; pre-RC only preserve fields needed to avoid later schema refactor. |
| Inverted ECU / spend-to-keep | Design language, temporal decay, CDL-048 conversion pressure | Not a live debit, slash, burn, or wallet rule. Must not be confused with inverse/backward attribution. | Fix2h distinction row; post-RC economic behavior spec before any settlement claim. |
| Werner systolic/diastolic pressure | Werner diagnostics and planning docs | Current use is diagnostic/review-lane only. No settlement use is authorized. | Keep indicative calculation allowed only if non-prescriptive; settlement influence requires CDL authority and adversarial tests. |
| Subjective/aesthetic juries | Whitepaper and planning material | Subjective/aesthetic lanes can govern curation, resonance, reuse, and taste-like work, but must not silently promote into objective truth or settlement authority. | Fix2h routing row; later CDL/spec for bounded subjective settlement if desired. |
| Protocol-native content store / fuller homoiconicity | Fix83 materialization path, file hashes, package profiles | Current graph carries cryptographic identity and materialization receipts; content bytes are not stored inline in LMDB. | Post-RC content-addressed blob/content layer. |
| Implementation-agnostic behavioral graph | Post-RC architectural targets | v0.4 signs a reference implementation and materialization path. Language-neutral behavioral spec nodes and conformance receipts remain future work. | v0.5 behavioral surface audit, behavioral spec node schema, economic behavior spec, conformance receipt schema. |

## Homoiconicity Gap Register (added 2026-07-11)

These rows track the six identified gaps preventing full graph homoiconicity.
They are separate from the whitepaper science-claim rows above because they are
internal structural completeness gaps, not claims about external architecture.
Ordered easiest → hardest.

| Gap | Description | Current anchor | Route | Status |
| --- | --- | --- | --- | --- |
| G1 — Duplicate repo:file nodes | `repo:file_ref:*` nodes without `source_sha256` / `SAME_SOURCE` edges to `repo:file:*` counterparts | Fix64 prompt: `antigravity_prompt__phase_1545p_fix64_g10_file_ref_content_hash_resolution.md`; resolves via SHA-256 hash + SAME_SOURCE edge write using `AtlasLmdbSafeWriter` | **Tier 1 COMPLETE** (`48ebffaa`). **Tier 2 COMPLETE** (`1eec1a5d` — actual live count was 4,002 not 179; original estimate stale due to graph growth; result: 4,008 total file_refs, 0 missing source_path/sha256/SAME_SOURCE, 2 non-file identities exempted, 7 stale Fix84/Fix85 rollback refs removed; edges now 89,367). **Tier 3 = Fix64c** (nodes resolvable via `label` only; original estimate 3,117 but MUST recount from live LMDB at execution time; token: `fix64c_tier3_complete`; must complete before Phase 1573 signing scope review). | `implemented_partial` |
| G2 — Content-layer edge types lack recipe annotations | The 13 output edge types of the 6 agent-issuable truth primitives (asserted_by, extends, validated_by, contradicts, refuted_by, supported_by, cites, elaborates, contrasts, instantiates, generalizes, revision_of, revised_by) — `supported_by` is the evidence-loop edge from `refute.claim`, confirmed by runtime preflight | Fix86 committed `7508f265`; 13 invariant nodes in LMDB; token: `content_layer_edge_type_recipe_annotation_committed_fix86` | **COMPLETE** | `implemented_partial` |
| G3 — Remaining edge-type definition node instances not yet written; type-registry runtime default-off | CDL-097 (ratified Phase 1528p) established type-definition node authority. CDL-099 (ratified Phase 1573b) ratified 5 hyperedge type definition nodes: `panel`, `co_authorship`, `refutation_coalition`, `epoch_boundary`, `jury_verdict`. CDL-100 (ratified Phase 1573c) ratified the type-dispute procedure. What remains: (a) content-layer and governance-layer edge types (asserted_by, extends, GOVERNS, CONSTRAINS, etc.) have no definition-node instances; (b) `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True`; `HyperEdge.hyperedge_type` is still a string literal, not graph-loaded from definition nodes | `docs/specs/ilc_constitutional_decision_log_v0.1.md` rows CDL-097/099/100; `docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md` §7; `ilc_core/types.py:378` HyperEdge dataclass | (a) Add definition-node instances for content-layer and governance edge types under CDL-097 authority — **NON-SENSITIVE only if the instances register already-authorized semantics without changing protocol behavior, economic attribution, settlement, public-RC authority, or reserved edge namespace meaning.** Any proposed instance that touches those surfaces requires a CDL/ADR/governance action before writing. Window 1577+. (b) SENSITIVE runtime activation phase: clear `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED`, migrate `HyperEdge.hyperedge_type` from string to graph-loaded node ID, cache invalidation, migration tests — separate from (a). | `implemented_default_off` |
| G4 — Protocol invariants are Python constants, not graph nodes | Key protocol invariants (AGENT_ISSUABLE_PRIMITIVES, ALLOWED_PRIMITIVE_TYPES, k_min=128, D_max=8, cover_ratio=8) are frozen Python sets/constants in `ilc_core/`, not content-addressed graph nodes traversable by the same query path as epistemic content. The CDL-097 authority schema applies here — invariant values could be definition-node instances under existing authority. | `ilc_core/epistemic/truth_primitive_submission_runtime.py`, `ilc_core/protocol/primitive_type_registry.py`; CDL-097 ratified (Phase 1528p) provides the definition-node schema authority | Phase A: annotation pass creating LMDB invariant nodes for each constant — can use CDL-097 authority, no new CDL opening needed (NON-SENSITIVE); Phase B: runtime integration threading invariant node IDs through validation paths, requires separate sensitive activation gate; Window 1577+; see PLANNING_INDEX.md addendum | `implemented_partial` |
| G5 — commit.epoch epoch-seal CIDs not threaded through truth primitive LMDB records; first-class temporal nodes needed if economics activates | Phase 855 wire format spec defines commit.epoch node schema (`previous_epoch_hash` CID chain, `finalizes` edge, `epoch_record_node`). CDL-099 ratified `epoch_boundary` as an irreducible hyperedge type definition (its `commit.epoch` temporal anchor status is recorded). The Python truth primitive LMDB adapter does not receive or record epoch seal CIDs from the Rust consensus layer (`ilc_consensus/`). | `docs/specs/ilc_phase_855_truth_primitive_wire_format_spec_v0.1.md` §4.7; CDL-099 `epoch_boundary` definition node; `ilc_core/epistemic/truth_primitive_graph_lmdb_adapter.py` | This is launch-sensitive: if economic soft-RC activates (Phase 1575a/b), commit.epoch boundary records need a concrete epoch-boundary graph record in the economic activation chain. Route belongs in the economic soft-RC/public-RC activation path, not as abstract graph cleanup. Codex input required on cross-language threading (Python/Rust bridge). Defer detailed phase planning. | `implemented_partial` |
| G6 — ADR-0029 hyperedge substrate implemented but unpopulated; star expansion not automatic; attribution/jury/settlement sensitive | ADR-0029 `HyperEdge` dataclass and sparse incidence index are implemented (`ilc_core/types.py:378`, `ilc_core/graph/__init__.py:48`); star expansion (hyperedge → hyperedge_entity node + binary member edges) is defined but not automatic; no real panel/co_authorship/refutation_coalition/epoch_boundary/jury_verdict instances are populated. CDL-099 ratified the five type definition nodes; CDL-100 ratified the type-dispute procedure. Population is sensitive because star-expanded hyperedges affect attribution, jury semantics, and settlement accounting. | `ilc_core/types.py:378`; `ilc_core/graph/__init__.py:48`; CDL-099 definition nodes; CDL-100 type dispute procedure | Pre-RC: AtlasSliceManifest (Fix61/Fix61c) should reference CDL-099/ADR-0029 governance basis; no standalone population action required before RC. Full population: SENSITIVE, Window 1578+, after G3 type-registry activation. **Before any star-expanded hyperedge may affect ECU or jury output, explicitly verify:** (1) CDL-081/083 attribution/quorum authority covers the hyperedge kind; (2) CDL-099/100 type definitions and dispute procedure are confirmed; (3) any settlement/value-path authority gate governing the specific kind passes. Do not activate panel, jury_verdict, or co_authorship star expansion before all three checks pass. | `post_rc_target` |

## Pre-RC Handling Rule

Before public RC, do not attempt to finish every whitepaper target. Instead:

1. Close any gap that can affect live rehearsal safety, economic settlement, or signing integrity.
2. Route any gap that affects a public claim into a prompt, planning document, or activation matrix row.
3. Preserve schema fields needed to avoid obvious post-RC refactors.
4. Keep non-activated research, SIM, and sidecar work default-off unless a sensitive GO explicitly changes that boundary.

## Immediate Routing

| Route | Scope |
| --- | --- |
| Phase 1568-Fix2e | Guard census must include harness and future Werner-credit guards. |
| Phase 1568-Fix2h | Produce the machine-readable whitepaper science routing matrix from this register. |
| Phase 1568-Fix2i | Add substrate-custody and Engram/CXL independence questions to the jury switch-out SIM/amendment lane. |
| Phase 1568-Fix2j | Open the candidate CDL scope for blind jury assignment, sealed delivery, jury-as-node, and substrate-custody independence. |
| H1/H2/H3 sidecar drafts | Preserve harness sidecar implementation tasks as prompt drafts until a valid sequence-lock slot exists. |

## Phase 1568-Fix2h Execution Note

Phase 1568-Fix2h created
`docs/specs/ilc_whitepaper_science_claim_routing_matrix_v0.1.json` as the
machine-readable routing matrix for this register and
`docs/specs/ilc_native_sidecar_typed_subgraph_anchor_v0.1.md` as the v0.4
sidecar anchor vocabulary. The whitepaper itself remains untouched by this
register; this document and the JSON matrix carry the implementation-gap and
activation-boundary tracking.
