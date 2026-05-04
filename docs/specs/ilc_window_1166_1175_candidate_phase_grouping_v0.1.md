# ILC Window 1166-1175: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-04
**Status:** DRAFT — pending human review and approval before any phase executes
**Baseline:** Window 1156-1165 CLOSED (Phase 1165 verdict: PASS, commit `265e4b58`).
CDL-084 is the ratified attribution frontier. CDL-085 remains unopened and SIM-gated
(`sim_spectral_04_gate_fail`, `cdl_085_sim_gated_pending_sybil_discrimination_resolution`).
Capsule v5.41 current. Handoff: `docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md`.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1166–1171
are the hard minimum lane (sequence lock + ADR-0037 draft + SIM-SPECTRAL-05 program spec
+ two SIM tracks + disposition). Phase 1172 is a conditional CDL-085 opening slot.
Phases 1173–1174 are firm governance + coherence phases. Phase 1175 is the closure gate.
The window may run lean if Phase 1172 conditions are not met.

---

## 1. Window Identity and Scope

Window 1166-1175 runs three lanes in dependency order:

1. **Lineage Contract ADR lane** — draft ADR-0037 (Genesis Canonical Lineage Contract)
   with full scope: lineage, equivalence (Popperian Equivalence Criterion), and merge
   policy across six domains (claim, provenance, version, governance, fork, economic).
   This ADR is a prerequisite for SIM-SPECTRAL-05 (its provenance equivalence criterion
   is an explicit SIM input) and for CDL-085 reconsideration and v0.2 signing.
   ADR-0036 acceptance review runs in Phase 1173 after SIM-SPECTRAL-05 completes.

2. **SIM-SPECTRAL-05 execution lane** — three tracks executed in two phases:
   - **Track A:** structural discriminant calibration against the *actual*
     `synthetic_sybil_cluster` S3 topology (λ₂ floor sweep, λ_max, spectral_gap,
     degree_gini). Closes `sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required`.
   - **Track B:** branchial claim-state projection (build a new projection tool;
     vertices = derivation states, edges = composition/refutation/amendment/succession;
     test L3-observer path convergence for legitimate chains vs Sybil). Closes
     `sim_spectral_05_branchial_claim_state_projection_required`.
   - **Multi-slice framework:** declare the observer slice for each track; design (not
     necessarily implement) convergence tests for all six slices; produce a framework
     design document. Closes `sim_spectral_05_multi_slice_observer_convergence_framework_required`.

3. **CDL-085 conditional lane** — if SIM-SPECTRAL-05 produces positive Sybil
   discrimination evidence (gate pass) AND the human issues explicit GO, Phase 1172
   opens CDL-085 using the Popperian Equivalence Criterion from ADR-0037 as the
   equivalence policy anchor. Requires both conditions; no self-authorization.

**Key sequencing inversion from prior window planning:** The Lineage Contract ADR
(Phase 1167) must be drafted *before* SIM-SPECTRAL-05 executes (Phases 1169–1171),
because the provenance equivalence criterion defined in the ADR is an explicit input
to the SIM design. Do not run SIM-SPECTRAL-05 before the criterion is specified.

The v0.2 signing ceremony is **not** in this window. It requires both ADR-0036
acceptance (Phase 1173) and the Lineage Contract ADR's version equivalence policy.
The unsigned v0.2 candidate remains at 41 nodes; no new ADR acceptances are planned
this window.

---

## 2. Baseline and Inheritance

### Ratified CDL chain

- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- CDL-085: SIM-gated, unopened. Gate condition: positive Sybil discrimination evidence
  from SIM-SPECTRAL-05.

### Active runtime chain

- `epoch_attribution_settle_runtime_1129_fix1.v0.5` — unchanged
- No runtime semantic mutations authorized in this window.

### Genesis Atlas canonical anchors

- Signed v0.1 star map: `out/genesis_core_star_map_v0.1.json` (32 nodes, 55 edges) — **untouched**
- Signed root envelope hash: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- **Immutable:** `out/genesis_compile_coverage_diagnostic_v0.1.json` — must not be overwritten
- Unsigned v0.2 candidate: `out/genesis_core_star_map_v0.2_candidate.json` (41 nodes, 73 edges)
  — remains unsigned; no new ADR acceptances grow it this window

### SIM-SPECTRAL anchors

- SIM-SPECTRAL-04 claim-composition projection: `out/genesis_claim_composition_projection_v0.1.json`
  (56V, 125E, hash `fc1496ea12319338d10db0e63f78087b3a72c46a31507d09b35234c79a45a2ab`) — reused as S1
- SIM-SPECTRAL-04 run summary: `out/sim_spectral_04_run01_summary.json`
- SIM-SPECTRAL-04 disposition: `docs/sims/sim_spectral_04/disposition_1162_v0.1.md`
- S1 baseline slope (Phase 1161): 0.3453
- S3/S1 failure values (Phase 1162): min 0.7805, max 0.8082, threshold 0.6416 (failed)
- Phase 1164 structural perturbation research: `docs/research/sim_spectral_04_structural_perturbation_research_1164_v0.1.md`

### Research carry-forwards (Window 1156-1165 supplements)

- `docs/research/sim_spectral_wolfram_branchial_framing_1164_supplement_v0.2.md`
- `docs/research/genesis_equivalence_merge_policy_forward_planning_v0.1.md`
- `docs/research/references/wolfram_physics_project_2021_update.md`

### CDL-V7 runtime (PEC dependency)

- `CDL_V7_RUNTIME_VERSION = "cdl_v7_popperian_gate_runtime_398.v0.1"`
- CDL-V7 implements single-claim Popperian gating — SIM-SPECTRAL-05 Track B can use
  this as an input when testing the PEC relational merge extension.

### Capsule and handoff

- Capsule: `docs/specs/ilc_antigravity_context_capsule_v5.41.md`
- Handoff: `docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md`

### Next fresh CDL number

CDL-085 is reserved and SIM-gated. Next fresh CDL number after CDL-085 is CDL-086
(unassigned). Do not assign CDL-086 this window.

### Next fresh ADR number

ADR-0036 is Proposed. ADR-0037 is the next available number. Assign it to the Genesis
Canonical Lineage Contract ADR in Phase 1167.

---

## 3. Track Inventory

### 3.1 Constitutionally obligated (carry-forward from prior windows)

| Token | Routing in this window |
|-------|----------------------|
| `cdl_085_sim_gated_pending_sybil_discrimination_resolution` | Phases 1169-1171: SIM-SPECTRAL-05 execution; Phase 1172 conditional CDL-085 opening |
| `sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required` | Phase 1169: Track A |
| `sim_spectral_05_branchial_claim_state_projection_required` | Phases 1170-1171: Track B |
| `sim_spectral_05_multi_slice_observer_convergence_framework_required` | Phase 1168: program spec + framework design |
| `genesis_multi_slice_encrustation_model_required_for_lineage_contract_adr` | Phase 1167: ADR-0037 scope |
| `genesis_equivalence_and_merge_policy_required_for_lineage_contract_adr` | Phase 1167: ADR-0037 scope |
| `popperian_equivalence_criterion_required_as_merge_gate_in_lineage_contract_adr` | Phase 1167: ADR-0037 scope |
| `genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036` | Phase 1167: ADR-0037 (this is that ADR) |
| ADR-0036 acceptance review | Phase 1173 (after SIM-SPECTRAL-05) |
| `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset` | Carry-forward only |
| Contributor agreement, license, trademark | Counsel track carry-forward |
| Canon bundle signing repair | Tooling debt carry-forward |
| Tier-3 runtime linkage | ADR-0020 governance met; runtime lane — carry-forward |

### 3.2 Deferred governance

| Item | Status |
|------|--------|
| CDL-085 opening | **Conditional tail slot (Phase 1172)** — requires `sim_spectral_05_gate_pass` + human GO |
| v0.2 signing ceremony | Deferred to Window 1176+ — requires ADR-0036 + ADR-0037 acceptance first |
| ADR-0037 acceptance | Drafted Phase 1167; **acceptance review Phase 1173** |
| ADR-0036 acceptance | Proposed; **acceptance review Phase 1173** |
| Canon bundle signing repair | Carry-forward; not in scope |
| License/trademark/contributor agreement | Counsel track; not in scope |

### 3.3 Simulation-conditional

| Item | Routing |
|------|---------|
| SIM-SPECTRAL-05 Track A (structural discriminant calibration) | Phase 1169 |
| SIM-SPECTRAL-05 Track B (branchial projection) | Phases 1170-1171 |
| SIM-SPECTRAL-05 disposition | Phase 1171 |
| CDL-085 opening | Phase 1172 — conditional on Phase 1171 gate pass + human GO |

---

## 4. Genesis Canonical Lineage Contract ADR (ADR-0037) Scope

### 4.1 Designation and background

ADR-0037 is designated the **Genesis Canonical Lineage Contract**. It is a new ADR,
not a CDL amendment. Phase 1167 drafts it with `**Status:** Proposed`. Acceptance
review is Phase 1173.

Background: the Phase 1154 pre-RC obligations synthesis
(`docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md`) identified the
Canonical Lineage Contract as a pre-RC requirement. Window 1156-1165 supplements
(`docs/research/genesis_equivalence_merge_policy_forward_planning_v0.1.md`) expanded
the required scope: the ADR must address not only lineage but also equivalence and
merge policy.

### 4.2 Required ADR-0037 scope (from Window 1156-1165 research)

**Section 1 — Lineage:** How to trace any ILC claim, artifact, node, or economic event
back to the Genesis canonical root. Root envelope hash verification, Node 0 manifest
inclusion, ADR/CDL ratification chain, signed v0.1 as the canonical base object.

**Section 2 — Canonical base object:** Genesis is the canonical base object against which
all equivalence and merge policies are evaluated. This is a governance anchor, not a
mathematical identity claim. Do not use "initial object in the infinity groupoid" language.

**Section 3 — Equivalence policy (six domains):** For each domain, declare the equivalence
criterion, boundary conditions, and relationship to the multi-slice observer framework:
  - Claim equivalence (when two claims are the same canonical claim)
  - Provenance equivalence (when two derivation paths are independent vs Sybil-coordinated)
  - Version equivalence (when v0.2 is a refinement vs a new object)
  - Governance equivalence (when CDL-N supersedes vs creates a new object from CDL-M)
  - Fork equivalence (when a fork is still canonical ILC vs a separate universe)
  - Economic equivalence (when two contribution paths receive one attribution event vs two)

**Section 4 — Popperian Equivalence Criterion (PEC):** Two ILC objects are equivalent
if and only if every valid refutation that defeats one defeats the other AND the system
cannot construct a meaningful separator. Equivalence is established by failing to find
a separator (negative test), not by finding similarity. Reference CDL-V7 as the existing
single-claim Popperian gate; PEC is the relational merge extension. Sybil test: Sybil
cluster independence claims are refutable by injection-point identity without refuting
genuine independence.

**Section 5 — Merge policy:** For each equivalence domain, declare attribution consequence,
authority consequence, versioning consequence, and economic flow consequence.

**Section 6 — Multi-slice encrustation:** Genesis is a cross-slice lineage invariant.
Specify the convergence criterion for all six observer slices (authority, claim-composition,
runtime-binding, economic-flow, gossip, provenance). A fork that cannot converge through
all six slices has exited canonical ILC identity. This is the fork equivalence boundary.

**Section 7 — Fork boundary:** Formal fork equivalence criterion using multi-slice
convergence. Defines when a fork remains within canonical ILC identity vs exits to a
separate universe.

### 4.3 ADR-0037 relationship to other artifacts

ADR-0037 is a prerequisite for:
- SIM-SPECTRAL-05 (provenance equivalence criterion from §3 is an explicit SIM input)
- v0.2 signing ceremony (version equivalence criterion from §3 governs the signing)
- CDL-085 (if opened, must be consistent with provenance equivalence defined here)
- ADR-0036 acceptance (release key binding semantics require the versioning and fork
  criteria from ADR-0037 to be established first)

ADR-0037 must NOT:
- Accept or ratify itself in Phase 1167 (Status: Proposed only)
- Require a CDL mutation pre-commit hook (it is an ADR, not a CDL)
- Change any runtime constants or signed artifacts

### 4.4 Provenance equivalence criterion as SIM-SPECTRAL-05 input

Phase 1168 (SIM-SPECTRAL-05 program spec) must consume the provenance equivalence
criterion from ADR-0037 §3.2 as an explicit, named input. The SIM must declare:
"this run tests independence criterion X using separation method Y." A SIM that runs
without a declared criterion is under-specified.

---

## 5. SIM-SPECTRAL-05 Execution Lane

### 5.1 SIM-SPECTRAL-05 program spec (Phase 1168)

Phase 1168 produces the formal program specification for SIM-SPECTRAL-05 before any
simulation code runs. This spec is the SIM-SPECTRAL-05 analog of
`docs/sims/sim_spectral_04/program.md`.

Required spec content:
1. **Observer slice declarations:** Name which observer slice each track tests (Track A =
   provenance + claim-composition slice; Track B = claim-composition + authority slice via
   L3 observer convergence).
2. **Provenance equivalence criterion:** Copy the criterion from ADR-0037 §3.2 verbatim;
   this is the named input that drives both tracks.
3. **Track A specification:** Inputs, S3 topology (`synthetic_sybil_cluster`, same as
   SIM-SPECTRAL-04), discriminants to test (λ₂ floor sweep, λ_max, spectral_gap,
   degree_gini), seeds (42/1337/2026), gate pass/fail criterion.
4. **Track B specification:** Branchial projection schema (what constitutes a
   derivation state, what constitutes a valid edge), inputs, convergence/divergence
   measurement method, gate pass/fail criterion. Gate criterion must be formulated in
   terms of the provenance equivalence criterion.
5. **Multi-slice framework design:** One-paragraph scope for each of the six slices;
   which slices are tested in this window (at minimum: authority + provenance); which
   are deferred with named carry-forward tokens.
6. **Gate criterion for SIM-SPECTRAL-05 overall pass:** Must require both Track A and
   Track B to pass; state what "pass" means for each.

### 5.2 SIM-SPECTRAL-05 Track A — structural discriminant calibration (Phase 1169)

Track A answers: "using the *actual* `synthetic_sybil_cluster` S3 topology, do the
proposed discriminants separate S1 from S3?"

This closes: `sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required`

**Critical difference from Window 1156-1165 research:** The Phase 1164 structural
perturbation research (three-path, Path 3) measured discriminants against Erdős-Rényi
random graphs. Track A must re-test against the committed `synthetic_sybil_cluster`
topology (ring + dense cluster), which is what the SIM-SPECTRAL-04 gate actually used.
The z-scores from Path 3 (λ_max at 9.8σ) are not valid against the Sybil topology
and must not be cited as gate evidence. Track A must produce new measurements.

**Inputs:**
- S1: `out/genesis_claim_composition_projection_v0.1.json` (56V, 125E) — already exists
- S3: `synthetic_sybil_cluster` — generated by `sim_spectral_02.py` (same as SIM-SPECTRAL-04)
- Seeds: 42, 1337, 2026

**Discriminants to calibrate:**
1. λ₂ floor sweep: vary `THETA_FLOOR` and measure S3/S1 separation across a range
2. λ_max: compute for both S1 and S3; measure separation and z-score vs Sybil distribution
3. spectral_gap (λ_max − λ₂): same
4. degree_gini: same

**Output:**
- `out/sim_spectral_05_track_a_calibration_summary.json`
- `docs/sims/sim_spectral_05/track_a_calibration_notes_1169.md`
- Explicit verdict per discriminant: `discriminates_against_sybil` or `insufficient_separation`

### 5.3 SIM-SPECTRAL-05 Track B — branchial projection tool build (Phase 1170)

Track B phase 1 builds the branchial claim-state projection tool. This is the Track B
analog of Phase 1160 (which built the claim-composition projection for SIM-SPECTRAL-04).

This is new infrastructure. The branchial projection is conceptually different from the
claim-composition projection:

| Property | Claim-composition (SIM-04) | Branchial claim-state (SIM-05 Track B) |
|----------|--------------------------|---------------------------------------|
| Vertices | Claims and subclaims | Derivation states (claim + history tag) |
| Edges | Derives-from, invokes-primitive, etc. | Composition, refutation, amendment, succession ops |
| Semantics | "What derives from what" (static) | "What paths exist through derivation space" (dynamic) |
| L3 frame | Bottom-up graph structure | Top-down observer trace (convergence test) |

**Design questions Phase 1170 must resolve:**
1. What is the ILC "derivation state" for a claim? Options: (claim_id, status) pairs;
   (claim_id, version, status) triples; or full claim-history-state objects. The choice
   determines the vertex schema.
2. What counts as a valid edge operation? Start with four: `compose`, `refute`, `amend`,
   `succeed`. Each must carry the provenance equivalence criterion linkage (which Genesis
   primitive does it trace back to?).
3. How is convergence measured? Proposed: a path from a derivation state back to a Genesis
   primitive is a "convergence path." Two paths converge if they terminate at the same
   primitive. A Sybil cluster's paths should converge to a non-Genesis intermediary (or
   fail to converge at all).

**Tool:** `tools/build_genesis_branchial_claim_projection.py`
**Output:** `out/genesis_branchial_claim_projection_v0.1.json`

**Determinism requirement:** Same as Phase 1160 — two runs must produce byte-identical output.

### 5.4 SIM-SPECTRAL-05 Track B run + disposition (Phase 1171)

Phase 1171 runs the branchial projection through the simulation and produces the combined
SIM-SPECTRAL-05 disposition.

**Track B run:**
- S1: `out/genesis_branchial_claim_projection_v0.1.json` (new)
- S3: generated Sybil cluster in branchial topology form (must design how to represent
  a Sybil cluster as a branchial projection — this is a Phase 1171 design question)
- Convergence metric: fraction of paths that terminate at Genesis primitives (S1) vs
  at non-canonical intermediaries or infinity (S3)
- Seeds: 42, 1337, 2026

**Combined disposition must:**
- State Track A verdict per discriminant
- State Track B convergence verdict
- Declare overall `sim_spectral_05_gate_pass` or `sim_spectral_05_gate_fail`
- If PASS: "CDL-085 reconsideration supported pending human GO for Phase 1172"
- If FAIL: specific diagnosis per track + new carry-forward obligations for Window 1176+
- Record the provenance equivalence criterion used as input (from ADR-0037)
- Record which observer slices were tested and which are deferred

**Output:**
- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md`
- `out/sim_spectral_05_track_b_run_summary.json`

---

## 6. CDL-085 Conditional Lane

### 6.1 CDL-085 opening (Phase 1172, conditional)

**Conditional on:** `sim_spectral_05_gate_pass` AND explicit human GO token `GO Phase 1172`.

Phase 1172 opens CDL-085 (Werner φ-bound / spectral efficiency / provenance attribution
limit — exact scope to be confirmed from prior planning refs when Phase 1172 executes).

Phase 1172 must:
1. Confirm `sim_spectral_05_gate_pass` is present in Phase 1171 disposition
2. Confirm CDL-085 number is still unused (check CDL index)
3. Create the CDL-085 pre-opening spec, synthesized from:
   - Phase 1171 pass evidence (SIM-SPECTRAL-05 disposition)
   - ADR-0037 provenance equivalence criterion (the SIM's named input)
   - `docs/sims/sim_spectral_04/program.md` §5 (prior gate criterion)
   - `docs/sims/sim_spectral_04/disposition_1162_v0.1.md` (prior diagnosis)
   - Phase 1164 structural perturbation research
   - Any prior `EDGE_MINT_PHI_BOUND` or φ-bound mentions
4. Open CDL-085 in the CDL file using the standard opening format

**Pre-commit hook required (if Phase 1172 executes):**
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1172
```

If Phase 1171 produces `sim_spectral_05_gate_fail`, Phase 1172 does not execute.
The window closes at Phase 1174 (coherence/capsule) then Phase 1175.

---

## 7. CDL Number Assignments

| CDL | Status | Notes |
|-----|--------|-------|
| CDL-085 | **Conditional opening in Phase 1172** | Only if `sim_spectral_05_gate_pass` + human GO `GO Phase 1172` |
| CDL-086 | Unassigned | Do not use this window |

---

## 8. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1166 | Window sequence lock | Foundation / Constitutional | NON-SENSITIVE |
| 2 | 1167 | ADR-0037 Genesis Canonical Lineage Contract draft | Governance review | NON-SENSITIVE |
| 3 | 1168 | SIM-SPECTRAL-05 program spec + multi-slice framework design | Synthesis / Simulation | NON-SENSITIVE |
| 4 | 1169 | SIM-SPECTRAL-05 Track A — structural discriminant calibration vs Sybil | Simulation | NON-SENSITIVE |
| 5 | 1170 | SIM-SPECTRAL-05 Track B — branchial projection design + tool build | Simulation | NON-SENSITIVE |
| 6 | 1171 | SIM-SPECTRAL-05 Track B run + combined disposition + gate verdict | Simulation / Synthesis | NON-SENSITIVE |
| — | 1172 | CDL-085 opening (conditional on Phase 1171 gate pass) | Constitutional | **conditional** |
| 7 | 1173 | ADR-0036 + ADR-0037 acceptance reviews | Governance review | NON-SENSITIVE |
| 8 | 1174 | Coherence report + capsule v5.42 | Synthesis | NON-SENSITIVE |
| 9 | 1175 | Closure gate | Gate | **SENSITIVE** |

### Conditional note on Phase 1172

Two scenarios:

**Scenario PASS:** Phase 1171 produces `sim_spectral_05_gate_pass`. Human issues GO token
`GO Phase 1172`. Phase 1172 opens CDL-085 using
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1172`. Phase 1173 then runs ADR
acceptance reviews. Phase 1174 (coherence) records CDL-085 as opened.

**Scenario FAIL:** Phase 1171 produces `sim_spectral_05_gate_fail`. Phase 1172 does not
execute. Window closes at Phase 1174 then 1175. CDL-085 routing carries into Window 1176+
with new per-track diagnosis tokens.

Before executing Phase 1172 under PASS scenario, confirm:
- CDL-085 pre-opening scope and title from prior planning references
- CDL number not previously used
- Human has issued explicit GO token `GO Phase 1172`

### Note on Phase 1167 — Lineage Contract ADR

ADR-0037 is a prerequisite for Phase 1168. Phase 1168 must consume the provenance
equivalence criterion from ADR-0037 §3 as an explicit named input to the SIM spec.
If Phase 1167 cannot produce a well-formed ADR-0037 (because some scope question is
unresolved), Phase 1168 must not run until it is resolved. Do not proceed to SIM-SPECTRAL-05
with an under-specified equivalence criterion.

ADR-0037 is drafted as Proposed; it is not accepted in Phase 1167. Acceptance is Phase 1173.

### Note on Phase 1168 — SIM-SPECTRAL-05 program spec

The program spec is the gate for the Track A and Track B phases. Phase 1169 and Phase 1170
must not begin until the program spec is approved. This is analogous to how Phase 1160
(projection tool build) waited for the Phase 1146 disposition and SIM-SPECTRAL-04 program
spec before building the tool.

### Note on Phase 1169 — Track A: actual Sybil topology required

Track A must use the `synthetic_sybil_cluster` topology as S3, not Erdős-Rényi random
graphs. The Window 1156-1165 Path 3 research used random graphs. Those results are
directional only and may not hold against the actual Sybil topology. Every discriminant
result in Track A must be labeled with the S3 topology used: `s3_topology=synthetic_sybil_cluster`.

### Note on Phase 1170 — branchial projection design

Phase 1170 is design-heavy. The branchial projection schema (what is a derivation state?
what is a valid edge?) may require multiple candidate schemas before one is selected. The
phase may need more time than a typical tool-build phase. If the design question cannot
be resolved within the phase, an intermediate design doc must be committed and the tool
build deferred to a Phase 1170b or extended into Phase 1171. Do not run Track B without
a committed design document.

### Note on Phase 1173 — two ADR acceptance reviews

Phase 1173 reviews both ADR-0036 (Operational Release Key) and ADR-0037 (Lineage Contract).
ADR-0037 acceptance is sequenced after ADR-0036 acceptance because the release key binding
semantics in ADR-0036 must be consistent with the versioning and fork criteria in ADR-0037.
Review ADR-0037 first to establish the criteria, then confirm ADR-0036 is consistent before
accepting both. Per-ADR outcomes are independent — one failing does not block the other.

ADR-0037 acceptance criteria:
1. The six equivalence domains are specified with criterion, boundary, and merge consequence.
2. The PEC is formally stated as the operational test.
3. Multi-slice encrustation and fork boundary are specified.
4. The ADR is consistent with SIM-SPECTRAL-05 results (if Phase 1171 ran before acceptance).

---

## 9. Sensitivity Classification

### SENSITIVE phases

- **Phase 1172 (conditional — CDL-085 opening):** CDL mutation. Requires
  `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1172` and explicit human GO
  `GO Phase 1172`. Only executes if `sim_spectral_05_gate_pass`.
- **Phase 1175 (closure gate):** Structural window boundary. Requires human GO token.
  No CDL mutation if Phase 1172 did not execute.

### NON-SENSITIVE phases

- **Phase 1166:** Sequence lock. No CDL, no star-map mutation.
- **Phase 1167:** ADR-0037 draft. New document, no CDL mutation. No signed artifact change.
- **Phase 1168:** SIM-SPECTRAL-05 program spec. Document only.
- **Phase 1169:** Track A calibration. Simulation output only.
- **Phase 1170:** Track B projection tool build. New tool + output artifact.
- **Phase 1171:** Track B run + disposition. Simulation output + document. No CDL mutation.
- **Phase 1173:** ADR acceptance reviews. No CDL mutation; signed v0.1 untouched;
  v0.2 candidate is an unsigned artifact (acceptance does not change it in this window).
- **Phase 1174:** Coherence + capsule. No CDL mutation.

### Conditional phases rule

Phase 1172: before executing, confirm Phase 1171 produced `sim_spectral_05_gate_pass`.
Confirm human GO token `GO Phase 1172`. If either condition is not met, Phase 1172 does
not execute — no GO token needed for non-execution.

### Pre-commit hook

Required only for Phase 1172 (if it executes):
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1172
```

No CDL mutation pre-commit hook needed for Phases 1166–1171, 1173–1175.

---

## 10. Scope Notes for Fixed Phases

### Phase 1166 — Window sequence lock

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_phase_1166_1175_sequence_lock_v0.1.md` — sequence lock
- `docs/phases/phase_1166_window_sequence_lock_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1166 entry

**Required content:**
- Window token: `window_1166_1175_sequence_lock_committed`
- Carry-forward intake: consume all 13 carry-forward tokens from capsule v5.41 §7
- Record the sequencing inversion: Lineage Contract ADR (Phase 1167) before SIM-SPECTRAL-05
  (Phases 1169-1171); neither SIM track may run before the provenance equivalence criterion
  is specified
- Record CDL-085 current state: `cdl_085_sim_gated_pending_sybil_discrimination_resolution`
- Record SIM-SPECTRAL-04 diagnosis: λ₂-based structural impedance inactive (THETA_FLOOR
  calibration issue); λ_max/spectral_gap require testing against actual Sybil topology

**Commit subject:** `feat(g8): phase 1166 window 1166-1175 sequence lock`

---

### Phase 1167 — ADR-0037 Genesis Canonical Lineage Contract draft

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` — Status: Proposed
- `docs/phases/phase_1167_adr_0037_lineage_contract_draft_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1167 entry

**Required ADR content:** (see Section 4.2 for full scope)
- Seven sections covering: lineage, canonical base object, six equivalence domains,
  Popperian Equivalence Criterion, merge policy, multi-slice encrustation, fork boundary
- Must declare provenance equivalence criterion in §3 in a form that can be directly
  used as a SIM input parameter

**Must not:**
- Accept ADR-0037 in this phase (Status: Proposed only)
- Require CDL mutation pre-commit hook

**Gate token:** `adr_0037_lineage_contract_draft_committed_phase_1167`

**Commit subject:** `docs(adr): phase 1167 adr-0037 genesis canonical lineage contract draft`

---

### Phase 1168 — SIM-SPECTRAL-05 program spec + multi-slice framework design

NON-SENSITIVE. No GO token required.

**Prerequisite:** `adr_0037_lineage_contract_draft_committed_phase_1167` must be present.

**Deliverables:**
- `docs/sims/sim_spectral_05/program.md` — SIM-SPECTRAL-05 program spec
- `docs/sims/sim_spectral_05/multi_slice_framework_design_1168_v0.1.md` — slice framework
- `docs/phases/phase_1168_sim_spectral_05_program_spec_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1168 entry

**Required program spec content:** (see Section 5.1 for full scope)
- Observer slice declarations per track
- Provenance equivalence criterion verbatim from ADR-0037 §3.2
- Track A specification (S3 topology, discriminants, gate criterion)
- Track B specification (projection schema, convergence metric, gate criterion)
- Multi-slice framework design (all six slices scoped; at least authority + provenance tested)
- Overall SIM-SPECTRAL-05 gate criterion (requires both Track A and Track B to pass)

**Gate token:** `sim_spectral_05_program_spec_committed_phase_1168`

**Commit subject:** `docs(sim): phase 1168 sim-spectral-05 program spec multi-slice framework`

---

### Phase 1169 — SIM-SPECTRAL-05 Track A

NON-SENSITIVE. No GO token required.

**Prerequisite:** `sim_spectral_05_program_spec_committed_phase_1168` must be present.

**Deliverables:**
- `out/sim_spectral_05_track_a_calibration_summary.json`
- `docs/sims/sim_spectral_05/track_a_calibration_notes_1169.md`
- `tests/test_phase_1169_sim_spectral_05_track_a.py` — minimum 5 tests
- `docs/phases/phase_1169_sim_spectral_05_track_a_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1169 entry

**Run requirements:**
- S1: `out/genesis_claim_composition_projection_v0.1.json` (existing)
- S3: `synthetic_sybil_cluster` topology (MUST be labeled in output; not random graph)
- Seeds: 42, 1337, 2026
- Discriminants: λ₂ floor sweep (5–10 THETA_FLOOR values), λ_max, spectral_gap, degree_gini

**Required tests:**

| ID | Test | Gate |
|----|------|------|
| T1A-1 | Calibration summary exists and S3 topology is labeled `synthetic_sybil_cluster` | Topology |
| T1A-2 | λ₂ floor sweep table present with at least 5 THETA_FLOOR values | Coverage |
| T1A-3 | λ_max, spectral_gap, degree_gini each reported with z-score vs Sybil distribution | Discriminants |
| T1A-4 | Each discriminant has explicit verdict: `discriminates_against_sybil` or `insufficient_separation` | Verdict |
| T1A-5 | Signed v0.1 star map unchanged | Immutability |

**Gate token:** `sim_spectral_05_track_a_completed_phase_1169`

**Commit subject:** `sim(spectral-05): phase 1169 track-a structural discriminant calibration vs sybil`

---

### Phase 1170 — SIM-SPECTRAL-05 Track B projection design + tool build

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_05/branchial_projection_design_1170_v0.1.md` — schema design
- `tools/build_genesis_branchial_claim_projection.py` — projection tool
- `out/genesis_branchial_claim_projection_v0.1.json` — output artifact
- `tests/test_phase_1170_branchial_projection_build.py` — minimum 5 tests
- `docs/phases/phase_1170_sim_spectral_05_track_b_build_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1170 entry

**Design doc must resolve** (see Section 5.3):
1. Vertex schema: what constitutes a derivation state?
2. Edge schema: which operations are valid? (propose: compose, refute, amend, succeed)
3. Convergence metric: what constitutes a path terminating at a Genesis primitive?
4. Sybil representation: how is a Sybil cluster represented in branchial topology?

**Required tests:**

| ID | Test | Gate |
|----|------|------|
| T1B-1 | Projection file exists and is valid JSON | Existence |
| T1B-2 | Vertex schema matches design doc: each vertex has `derivation_state_type` and `genesis_anchor` | Schema |
| T1B-3 | Edge schema matches design doc: each edge has `operation_type` in allowed set | Schema |
| T1B-4 | Tool is deterministic: two runs produce identical sha256 output | Determinism |
| T1B-5 | Signed v0.1 star map unchanged | Immutability |

**Gate token:** `sim_spectral_05_track_b_projection_built_phase_1170`

**Commit subject:** `sim(spectral-05): phase 1170 track-b branchial claim projection design and tool`

---

### Phase 1171 — SIM-SPECTRAL-05 Track B run + combined disposition

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `out/sim_spectral_05_track_b_run_summary.json`
- `docs/sims/sim_spectral_05/disposition_1171_v0.1.md` — combined disposition + gate verdict
- `tests/test_phase_1171_sim_spectral_05_disposition.py` — minimum 5 tests
- `docs/phases/phase_1171_sim_spectral_05_disposition_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1171 entry

**Disposition must contain:**
- Track A verdict table (per discriminant)
- Track B convergence verdict (legitimate chains vs Sybil paths)
- Provenance equivalence criterion used (verbatim reference to ADR-0037 §3.2)
- Observer slices tested + slices deferred with tokens
- Overall gate verdict: `sim_spectral_05_gate_pass` or `sim_spectral_05_gate_fail`
- If PASS: "CDL-085 reconsideration supported pending human GO `GO Phase 1172`"
- If FAIL: per-track diagnosis + new carry-forward tokens for each failed track

**Required tests:**

| ID | Test | Gate |
|----|------|------|
| T1C-1 | Disposition file exists with Track A and Track B verdict sections | Coverage |
| T1C-2 | Provenance equivalence criterion citation present (ADR-0037 §3 reference) | Criterion |
| T1C-3 | Gate verdict token present: `sim_spectral_05_gate_pass` or `sim_spectral_05_gate_fail` | Verdict |
| T1C-4 | Observer slices tested are listed; deferred slices have named carry-forward tokens | Slices |
| T1C-5 | Signed v0.1 star map unchanged | Immutability |

**Commit subject:** `sim(spectral-05): phase 1171 track-b run combined disposition gate verdict`

---

### Phase 1173 — ADR-0036 + ADR-0037 acceptance reviews

NON-SENSITIVE. No GO token required.

**Deliverables:**
- Updated `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` (if accepted: `**Status:** Accepted`)
- Updated `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` (if accepted: `**Status:** Accepted`)
- `docs/adr/adr_0037_acceptance_review_1173_v0.1.md` — ADR-0037 review record
- `docs/adr/adr_0036_acceptance_review_1173_v0.1.md` — ADR-0036 review record
- `tests/test_phase_1173_adr_0036_0037_acceptance.py` — minimum 4 tests
- `docs/phases/phase_1173_adr_0036_0037_acceptance_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1173 entry

**ADR-0037 acceptance criteria:**
1. Six equivalence domains specified with criterion, boundary, and merge consequence
2. PEC formally stated as the operational test
3. Multi-slice encrustation and fork boundary specified
4. ADR is consistent with SIM-SPECTRAL-05 results (if Phase 1171 has run)

**ADR-0036 acceptance criteria:**
1. Operational release key scope correctly bounded (not conflated with Lineage Contract)
2. Genesis binding semantics are consistent with ADR-0037 versioning + fork criteria
3. Key rotation policy specified

**Review ADR-0037 first.** Confirm ADR-0036's binding semantics are consistent before accepting.

**Per-ADR independence:** failing one does not block the other. Produce explicit
accept or defer token for each.

**Required tests:**

| ID | Test | Gate |
|----|------|------|
| T3-1 | ADR-0037 review record exists with explicit accept/defer verdict | Coverage |
| T3-2 | ADR-0036 review record exists with explicit accept/defer verdict | Coverage |
| T3-3 | If ADR-0036 accepted, status field reads "Accepted" | Status |
| T3-4 | Signed v0.1 star map unchanged | Immutability |

**Commit subject:** `docs(adr): phase 1173 adr-0036 adr-0037 acceptance reviews`

---

### Phase 1174 — Coherence report + capsule v5.42

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_integration_coherence_report_1174_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.42.md`
- `docs/phases/phase_1174_coherence_capsule_v5_42_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1174 entry

**Capsule v5.42 must record:**
- SIM-SPECTRAL-05 gate verdict (pass or fail; per-track results)
- CDL-085 state (opened if Phase 1172 executed; still SIM-gated if Phase 1172 skipped)
- ADR-0037 status (Accepted or Proposed; with acceptance token if accepted)
- ADR-0036 status (Accepted or Proposed; with acceptance token if accepted)
- Signed v0.1 immutability (confirmed unchanged)
- v0.2 candidate state (41 nodes; signing deferred if ADRs not yet accepted)
- All carry-forwards resolved or deferred with tokens

**Commit subject:** `docs(coherence): phase 1174 coherence report capsule v5.42`

---

### Phase 1175 — Closure gate

**SENSITIVE.** Requires explicit human GO token.

**Deliverables:**
- `docs/specs/ilc_window_1166_1175_handoff_1175_v0.1.md`
- `tests/test_phase_1175_window_1166_1175_closure_gate.py` — minimum 16 tests
- `docs/phases/phase_1175_window_1166_1175_closure_gate_walkthrough.md`
- `docs/PLANNING_INDEX.md` — mark Window 1166-1175 closed
- `docs/phases/STATUS.md` — Phase 1175 entry + window closure

**Selftest guard:** `ILC_PHASE_1175_GATE_SELFTEST=1`

**Closure gate must verify (minimum checks):**
1. Sequence lock committed (Phase 1166) + `window_1166_1175_sequence_lock_committed`
2. ADR-0037 draft committed (Phase 1167) + `adr_0037_lineage_contract_draft_committed_phase_1167`
3. SIM-SPECTRAL-05 program spec committed (Phase 1168) + `sim_spectral_05_program_spec_committed_phase_1168`
4. Track A calibration summary exists + S3 topology labeled `synthetic_sybil_cluster` (Phase 1169)
5. `sim_spectral_05_track_a_completed_phase_1169` token present
6. Branchial projection tool + artifact exist (Phase 1170) + determinism tested
7. `sim_spectral_05_track_b_projection_built_phase_1170` token present
8. Track B run summary + combined disposition exist (Phase 1171)
9. Gate verdict token present: `sim_spectral_05_gate_pass` or `sim_spectral_05_gate_fail`
10. Phase 1172: either CDL-085 opened with pre-commit hook evidence OR `sim_spectral_05_gate_fail` token present (Phase 1172 correctly skipped)
11. ADR-0036 review record exists with explicit verdict (Phase 1173)
12. ADR-0037 review record exists with explicit verdict (Phase 1173)
13. Signed v0.1 star map unchanged (32 nodes, hash unchanged)
14. `out/genesis_compile_coverage_diagnostic_v0.1.json` not regenerated
15. Runtime chain unchanged (`epoch_attribution_settle_runtime_1129_fix1.v0.5`)
16. Capsule v5.42 exists and contains `capsule_v5_42_supersedes_v5_41` token

**Closure token:** `window_1166_1175_closed_phase_1175`

**Commit subject:** `docs(phase): close window 1166-1175`

---

## 11. Key Dependencies and Open Questions

### Must-resolve at window entry

1. **ADR-0037 scope boundary with ADR-0036:** ADR-0036 covers the operational release key;
   ADR-0037 covers lineage + equivalence + merge policy. Phase 1167 must confirm these
   are genuinely non-overlapping. The release-key binding semantics in ADR-0036 reference
   Genesis-binding — this is where the two ADRs touch. Phase 1167 must specify exactly
   how ADR-0037's versioning criterion (§3.3) governs the release-key's Genesis-binding
   semantics, so Phase 1173 can confirm consistency.

2. **Branchial projection tractability:** The conceptual design of the branchial
   claim-state projection is new and may surface unexpected complexity in Phase 1170.
   If the derivation-state vertex schema cannot be cleanly constructed from existing
   ILC claim artifacts, Phase 1170 may need to produce a design doc first, then build
   the tool in a Phase 1170b. Flag this as a risk at sequence-lock time.

3. **SIM-SPECTRAL-05 Track B Sybil representation:** How does a Sybil cluster look in
   branchial topology form? This is an open design question for Phase 1170. A Sybil
   cluster in the static topology is a ring + dense cluster. In branchial topology,
   it would need to be represented as a set of derivation states whose paths converge
   at a non-Genesis intermediary. Phase 1168 should sketch this in the program spec.

### Sequencing constraints

- Phase 1167 must complete before Phase 1168 (program spec needs ADR-0037 §3.2 criterion)
- Phase 1168 must complete before Phase 1169 and Phase 1170
- Phase 1169 (Track A) should complete before Phase 1170 (Track A results may inform branchial design)
- Phase 1170 must complete before Phase 1171 (Track B run needs the tool)
- Phase 1171 must complete before Phase 1172 evaluation (gate verdict required)
- Phase 1172 (if executing) must complete before Phase 1173 acceptance reviews
- Phase 1173 must complete before Phase 1174 (capsule must reflect ADR outcomes)

### Open questions

1. **CDL-085 exact scope:** The SIM-SPECTRAL-04 program spec references "Werner φ-bound /
   spectral efficiency." What is the exact CDL-085 scope, title, and affected parameters?
   Phase 1166 sequence lock should locate all prior planning references and record them.

2. **PEC formalization:** Is the Popperian Equivalence Criterion as stated in ADR-0037 §4
   precise enough to be tested in a simulation? Or does it require further formalization
   (e.g., formal definition of "valid refutation" in ILC terms)? Phase 1167 must produce
   an operationalizable criterion, not just a philosophical statement.

3. **Multi-slice framework scope for this window:** Phases 1168-1171 can realistically
   test at most two slices (authority + provenance). Phase 1168 program spec should
   explicitly name which four slices are deferred and with what tokens.

### Permanently deferred from this window

- v0.2 signing ceremony (requires ADR-0036 + ADR-0037 acceptance; deferred to Window 1176+)
- Tier-3 runtime linkage implementation
- Canon bundle signing repair
- License, trademark, contributor agreement
- SIM-BEACON-01, SIM-HYPEREDGE-01, SIM-ECU-STABILITY-01
- Merkle-Laplacian paper finalization

---

## 12. Known Patterns and Technical Constraints

### Branchial projection — first instance (novel pattern)

Phase 1170 introduces the first branchial/multiway projection in ILC simulation history.
Unlike prior projections (raw star map, claim-composition), this projection has a
dynamic semantics: vertices are derivation states, not static nodes. The design decisions
in Phase 1170 establish a new projection class. Document the design decisions explicitly
in the design doc — they will be referenced by future SIM-SPECTRAL-06+ windows.

### Track A must not reuse Path 3 results

The λ_max (9.8σ) and spectral_gap (8.9σ) z-scores from the Window 1156-1165 Path 3 research
were measured against Erdős-Rényi random graphs. They are NOT valid evidence against the
`synthetic_sybil_cluster` topology. Do not cite them as Track A gate evidence. Track A must
produce new measurements specifically against the Sybil topology.

### PEC operationalization check

The Popperian Equivalence Criterion as stated is philosophical. Before Track B can test
it in a simulation, it must be operationalized: "what exactly constitutes a 'valid
refutation' in ILC derivation terms?" Phase 1167 must provide this operationalization
in ADR-0037 §4. Phase 1168 must confirm the operationalization is testable before
writing the Track B specification.

### CDL-V7 as substrate for Track B

CDL-V7's Popperian gate runtime is already deployed. Track B's PEC test is the relational
extension of CDL-V7. Phase 1170's tool build should consider whether the branchial
projection can be built *on top of* CDL-V7's falsifiability infrastructure rather than
from scratch. This may significantly reduce Track B implementation complexity.

### Signed v0.1 immutability

Any phase that touches the v0.2 candidate or runs a simulation must include a test:
- `out/genesis_core_star_map_v0.1.json` node count == 32
- Root envelope hash unchanged: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- `out/genesis_compile_coverage_diagnostic_v0.1.json` not regenerated

### Selftest guard chain (Phase 1175)

Phase 1175 closure gate test must include `ILC_PHASE_1175_GATE_SELFTEST=1` guard.

---

## 13. Non-Goals and Explicitly Deferred Items

- v0.2 signing ceremony
- Tier-3 runtime linkage (`schema:*`/`runtime:*` node class)
- New ADR acceptance batch (no new ADRs are queued for acceptance beyond ADR-0036/0037)
- SIM-SPECTRAL-01 for Merkle-Laplacian paper
- Canon bundle signing failure repair
- License, trademark, or contributor agreement drafting
- Multi-agent testnet / RC substrate changes
- Runtime semantic changes

---

## 14. Key Canonical Anchors for Prompt Drafting

- `docs/specs/ilc_window_1166_1175_candidate_phase_grouping_v0.1.md` — this document
- `docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md` — incoming handoff (CURRENT)
- `docs/specs/ilc_antigravity_context_capsule_v5.41.md` — current capsule (CURRENT)
- `docs/research/genesis_equivalence_merge_policy_forward_planning_v0.1.md` — ADR-0037 scope source
- `docs/research/sim_spectral_wolfram_branchial_framing_1164_supplement_v0.2.md` — SIM-SPECTRAL-05 framing
- `docs/research/sim_spectral_04_structural_perturbation_research_1164_v0.1.md` — Track A baseline
- `out/genesis_claim_composition_projection_v0.1.json` — S1 for Track A (existing)
- `docs/sims/sim_spectral_04/disposition_1162_v0.1.md` — prior gate fail diagnosis
- `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` — Phase 1173 target
- `docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md` — Lineage Contract background
- `ilc_constitutional_decision_log_v0.1.md` — CDL register (confirm CDL-085 number unused)
- For closure gate (Phase 1175): all Phase 1166–1174 test files and artifacts.

---

## 15. Rationale for Single-Window Scope

1. ADR-0037 (Phase 1167) is a prerequisite for SIM-SPECTRAL-05 and must precede it —
   keeping both in one window avoids a round-trip window solely for the ADR draft.
2. SIM-SPECTRAL-05 has three tracks but two are closely related (Track A calibration
   informs Track B branchial design); splitting them across two windows would force
   re-specification work.
3. ADR-0036 acceptance has been deferred two windows; it is ready for review and should
   proceed in the same window as ADR-0037 acceptance (Phase 1173), since the two ADRs
   need consistency review anyway.
4. CDL-085 conditional opening (Phase 1172) is retained in this window so that if the
   SIM passes, CDL-085 can proceed without an additional window gap.
5. If Phase 1172 fails (SIM gate fail), the window closes cleanly at Phase 1175 with
   all other phases valuable regardless of the CDL-085 outcome.
