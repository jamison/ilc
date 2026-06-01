<!-- PUBLIC_RC_EXCLUDE -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Internal pre-public governance classification. Patent filing remains pending; no public disclosure is authorized. -->

# ILC Backward Attribution Classification Spec - Phase 1492p

**Date:** 2026-06-01  
**Window:** 1489p-1497p  
**Phase:** 1492p  
**Status:** Internal classification complete  
**Sensitivity:** NON-SENSITIVE, private pre-public  
**Obligation closed:** OBL-010  

```text
backward_attribution_classification_committed_phase_1492p
```

---

## 1. Context and Identification

Backward attribution is the candidate mechanism by which verified downstream
work creates credit that propagates backward through a typed provenance graph or
typed provenance hypergraph to upstream claims, evidence, methods, datasets,
models, software artifacts, review artifacts, revision chains, or other
graph-native artifacts that enabled the downstream work.

The canonical research description for this phase is:

```text
typed-hypergraph backward credit propagation
```

The important distinction is that this is not generic citation tracking. The
candidate mechanism computes provenance distance over protocol-recognized edge
and hyperedge semantics, including provenance, reuse, validation,
contradiction, refutation, revision, evidence, method dependency, dataset
dependency, model dependency, and epoch commitment. That lets the credit rule
condition on epistemic state, not merely on the existence of a link.

The mechanism appears in the current research and planning record at three
levels:

| Source | Status |
|---|---|
| Opus 4.7 economics / Atlas of Cliffs intake | Identified as a novel research contribution and distinct from inverted ECU |
| `docs/research/patent_pending/filing_3_ecu_metered_verified_epistemic_work_us_provisional_specification_v0.1.md` | Draft-level patent coverage added as a typed-hypergraph backward credit propagation embodiment |
| `docs/specs/ilc_window_1489p_1497p_candidate_phase_grouping_v0.1.md` | Routed to Phase 1492p to classify as research-only or candidate CDL |

The local Filing 3 draft describes:

- upstream artifact eligibility;
- provenance-distance scoring;
- hop, epoch-age, edge-type, claim-status, validation-state,
  refutation-survival, revision-lineage, reuse-depth, confidence,
  centrality, impedance, spectral, and governance-weight factors;
- geometric, exponential, linear, capped, thresholded, piecewise,
  context-dependent, governance-controlled, or simulation-derived decay;
- bidirectional coefficients separating forward contributor credit from
  backward foundational credit;
- optional privacy-preserving attribution using a commitment, proof, receipt,
  or bounded disclosure.

Filing 2 has also been updated so the truth-primitive state-machine filing
points attribution decay functions, depth caps, provenance-distance scoring,
and bidirectional attribution coefficients to the companion ECU metering filing
rather than to an unresolved separate filing.

---

## 2. Patent Coverage Status (OBL-001 Disposition)

OBL-001 is resolved only at the draft-coverage level. The local patent-pending
Filing 3 draft now covers typed-hypergraph backward credit propagation as an
embodiment of the ECU metering pipeline, and it describes the optional
privacy-preserving structural-commitment embodiment without making the
Merkle-Laplacian filing a required dependency.

This does not mean a patent filing has been submitted. The hard public
disclosure gate remains in force:

```text
patent filing submission or later filing/counsel disposition required before public disclosure
```

This classification spec is internal only and carries `PUBLIC_RC_EXCLUDE`. It
does not authorize public publication, public repository export, public RC
publication, patent-filing claims, or any removal of the existing public path
block.

---

## 3. Classification Decision

**Decision:** Option B - Candidate CDL pre-deliberation spec.

Backward attribution is mature enough to be treated as a future candidate CDL,
but it is not current protocol law. The mechanism has a coherent technical
substrate, local draft patent coverage, related prior canon in provenance and
refutation economics, and clear open parameter surfaces. That is enough to
preserve it as a CDL candidate rather than leave it as research-only non-canon.

It is not mature enough for activation. No current CDL authorizes backward
attribution as a live economic rule, no runtime implements it, and no phase in
Window 1489p opens or mutates a CDL. A future CDL opening would require a
separate SENSITIVE phase after the filing/public-disclosure disposition is
recorded and after calibration evidence exists.

### 3.1 Candidate CDL Scope

A future backward-attribution CDL would need to decide at least:

| Decision surface | Candidate question |
|---|---|
| Triggering events | Which downstream verified-work events create backward attribution eligibility? |
| Eligible upstream artifacts | Which upstream artifact types may receive credit: claims, evidence, methods, datasets, models, software, reviews, revision chains, or hyperedge entities? |
| Typed path semantics | Which edge and hyperedge types count, and which are excluded? |
| Provenance-distance score | Which variables are included: hyperpath distance, hop count, protocol age, edge type, claim status, refutation survival, reuse depth, confidence, centrality, or graph-structural impedance? |
| Decay rule | Whether decay is geometric, exponential, linear, capped, thresholded, context-dependent, simulation-derived, or governance-controlled. |
| Bidirectional coefficients | How forward contributor credit and backward foundational credit are separated and bounded. |
| Depth and dominance bounds | Maximum depth, anti-dominance caps, cluster caps, novelty gates, and reuse-diversity guards. |
| Refutation interaction | Whether refuted, contradicted, revised, or pending upstream artifacts are excluded, discounted, escrowed, or clawed back. |
| Audit surface | Whether public traversal is required or whether private/sidecar computation with bounded disclosure is allowed. |

### 3.2 Relationship to Existing CDLs

Backward attribution must be designed as an extension around existing canon,
not a silent override.

| Existing canon | Relationship |
|---|---|
| CDL-083 refutation attribution | Upheld refutation rewards already have a ratified path. Backward attribution must not double-pay or bypass caller-filtered upheld-refutation semantics. |
| CDL-084 provenance chain attribution | CDL-084 already ratifies caller-only PROVENANCE chain attribution with geometric decay and max depth. Backward attribution must specify whether it is a successor, a distinct economic layer, or a higher-order redistribution rule over verified downstream value. |
| CDL-091 jury incentive economics | Reviewer compensation remains inactive and separately governed. Backward attribution must not activate reviewer payment or jury incentives by implication. |
| ADR-0029 / ADR-0030 hypergraph substrate | Star-expanded hyperedges and hyperedge entities are relevant substrate, but economic attribution over those entities remains gated on CDL alignment. |

### 3.3 Required Evidence Before CDL Opening

A future opening should not proceed without:

- patent filing submission or later filing/counsel disposition;
- a simulation contract covering backward-attribution parameter sweeps;
- adversarial analysis for self-referential dependency loops, citation rings,
  dense early-node capture, Sybil reuse amplification, and stale-founder
  dominance;
- a no-double-counting proof or test plan against CDL-083 and CDL-084;
- a privacy/audit boundary decision for optional structural commitments;
- a clear non-activation statement for public RC unless separately authorized.

---

## 4. Terminology Resolution

**Canonical term for this mechanism:** `backward attribution`.

**Canonical technical description:** `typed-hypergraph backward credit propagation`.

**Retired usage:** Do not use `inverted ECU` as a synonym for backward
attribution.

The Phase 1492p prompt expected "inverted ECU" to have no canonical glossary
entry. Direct source verification found the opposite: the canonical glossary
does contain `Inverted ECU / spend-to-keep`, but it means a different doctrine.
Inverted ECU describes the operating posture where ECU is treated as working
credit deployed productively, with status measured by deployment velocity and
quality rather than accumulated balance. Historical MemPalace retrieval also
points to the March 2026 inverted-ECU conversation where the central question
was whether success should be measured by how much ECU an agent spends
productively, not by how much ECU it accumulates.

Therefore the correction is not to retire the term `inverted ECU` globally. The
term remains available for the spend-to-keep doctrine. What is retired is the
informal use of `inverted ECU` to mean backward attribution.

| Term | Phase 1492p disposition |
|---|---|
| `backward attribution` | Canonical short name for this candidate mechanism |
| `typed-hypergraph backward credit propagation` | Canonical technical description |
| `retroactive dependency-chain attribution` | Acceptable research-paper synonym if explicitly mapped to backward attribution |
| `inverted ECU` | Reserved for spend-to-keep / working-credit doctrine; not a synonym for backward attribution |

Future prompts, specs, and CDL drafts should use `backward attribution` when
discussing upstream credit propagation from downstream verified work. They
should use `inverted ECU` only for the spend-first working-credit posture.

---

## 5. Forward Path

Backward attribution moves forward on a candidate-CDL path, not a runtime path.

### 5.1 Minimum Future Sequence

1. Record patent filing submission or later filing/counsel disposition for the
   relevant Filing 3 coverage.
2. Produce a backward-attribution simulation contract that names the candidate
   parameter grid and adversarial cases.
3. Run the simulation and record whether any parameter region is viable.
4. Draft a future SENSITIVE CDL opening prompt only if the evidence is
   sufficient.
5. If opened, prelock the parameter surfaces and non-authorizations.
6. Only after ratification and separate runtime authorization may code be
   written for live backward-attribution economics.

### 5.2 Non-Authorizations

This phase does not:

- open a CDL;
- mutate the CDL register;
- ratify backward attribution;
- activate ECU credit, ECU minting, ILC settlement, reviewer payment, public
  bundle-serving incentives, or invitation economics;
- implement runtime code;
- alter Filing 3 or any patent draft;
- claim that any provisional filing has been submitted;
- authorize public disclosure or public RC publication;
- remove `PUBLIC_RC_EXCLUDE` from any patent-sensitive or private planning
  artifact.

### 5.3 Carry-Forward

Phase 1493p may proceed to the invitation provenance chain spec. That phase
should treat invitation/service-chain attribution as a narrower future design
surface and must not collapse it into this backward-attribution CDL candidate.
The two mechanisms may eventually interact, but Phase 1492p does not authorize
that merger.
