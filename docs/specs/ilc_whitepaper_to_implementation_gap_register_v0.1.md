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
