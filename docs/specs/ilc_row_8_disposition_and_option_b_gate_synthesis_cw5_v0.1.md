# ILC Row-8 Disposition and Option B Gate Synthesis CW-5 v0.1

**Phase:** 761  
**Window:** Mysticeti convergence window  
**Date:** 2026-04-21  
**Author:** Codex

`option_b_gate_synthesis_verdict=no_go`
`option_b_gate_blockers=row_8_candidate_evaluation_pending|cdl_017_ratification_pending`
`row_7_runtime_closed_milestone_recorded`
`option_d_posture_active_per_adr_0028`
`row_8_posture=criteria_locked_candidate_evaluation_pending`
`row_5_parallel_privacy_carry_forward_recorded`

## 1. Baseline and governing posture

`CW-2`, `CW-3`, and `CW-4` are committed and authoritative:

- row `5`: `row_5_runtime_closure_verdict=fail`
- row `7` censorship: `row_7_censorship_resistance_runtime_closure_verdict=pass`
- row `7` exitability: `row_7_strong_exitability_runtime_closure_verdict=pass`
- combined row `7`: `row_7_combined_runtime_status=runtime_closed`

ADR-0028 remains the governing route for Option D / Option B posture:

- `Option D` remains the active architectural posture until explicit graduation
  criteria are met,
- future substrate choice must preserve protocol-first legitimacy,
- censorship-resistance and independence from external constitutional centers
  remain named future-substrate criteria,
- this phase synthesizes whether Option B becomes selectable; it does not select
  Option B.

The human-reviewed framing fixed before this commission remains controlling:

1. `CDL-017` ratification is a constitutional gate blocker for sovereign public
   substrate activation.
2. Row `8` candidate evaluation is the second gate blocker.
3. Row `5` privacy failure is a parallel legitimacy obligation, not an
   ADR-0028 substrate-selection criterion.
4. Row `7` runtime closure is the positive convergence milestone.

## 2. Row-8 disposition

Phase `673` defines the row-8 exclusion matrix and Phase `675` locks those
criteria as binding for later substrate admissibility.

The exclusion matrix fixes the disqualifying dependency patterns:

- outside veto authority over legitimacy-relevant public state,
- de facto source-of-truth drift for admission, namespace, settlement
  legitimacy, auditability, or continuity,
- hosted control-plane chokepoints as the only practical audit or exit path,
- migration dependence on privileged operator or provider consent.

Phase `675` then locks the row-8 rule:

- later substrate families may not make protocol legitimacy subordinate to an
  outside veto authority,
- outside systems may carry already-legitimate protocol state but may not become
  the constitutional center that authors legitimacy,
- the Phase `673` exclusion matrix is binding for later substrate admissibility.

Current row-8 posture:

- criteria locked: yes,
- specific substrate candidate named: no,
- candidate evaluation against the Phase `673` matrix: not yet performed.

Row-8 disposition:

- `row_8_posture=criteria_locked_candidate_evaluation_pending`

This is a descriptive posture only. No hypothetical substrate is evaluated here.

## 3. Option B graduation-gate synthesis

ADR-0028 requires that `Option D` remain the active posture until the published
graduation criteria are honestly satisfied. Evaluated against the current
committed evidence:

| Gate condition | Status | Evidence source |
|---|---|---|
| Row-7 proof obligations satisfied | **PASS** | `CW-3` and `CW-4` runtime-closure verdicts |
| Row-8 exclusion-matrix evaluation against a specific candidate | **PENDING** | Phase `673` exclusion matrix is binding; Phase `675` criteria lock is active; no candidate has been evaluated |
| `CDL-017` ratification | **PENDING** | Phase `755` dossier §4 fixes the sequence `M-022 approval -> convergence window -> CDL-017 ratification window`; `CDL-017` remains open and constitutional validator activation has not occurred |

Overall gate verdict:

- `option_b_gate_synthesis_verdict=no_go`
- `option_b_gate_blockers=row_8_candidate_evaluation_pending|cdl_017_ratification_pending`

Honest synthesis:

- Option B does **not** become selectable at `CW-5`,
- `Option D` remains the active posture under ADR-0028,
- the blocker list is short, explicit, and bounded rather than open-ended.

## 4. Positive convergence milestone

The positive finding of the convergence window is row `7` runtime closure.

Committed convergence evidence now records:

- censorship-resistance runtime closure: pass,
- strong-exitability runtime closure: pass,
- combined row-7 runtime status: `runtime_closed`.

Milestone token:

- `row_7_runtime_closed_milestone_recorded`

This matters for the Option B route because ADR-0028 names censorship-resistance
as a future-substrate criterion. The criterion is now runtime-backed rather than
only criteria-locked.

## 5. Carry-forward obligations

### 5.1 Row-5 privacy carry-forward

Row `5` remains `spec_closed_runtime_pending`. `CW-2` recorded an honest fail
against the Phase `740` closure bar with raw linkage recall still at `1.0`.

Required carry-forward:

1. log hygiene: AgentID redaction or equivalent removal of direct sender
   identity from validator operational logs,
2. transfer privacy: mixing or k-anonymity-style protection sufficient to drive
   the linkage numbers below the inherited closure bands (`<= 0.45` /
   `<= 0.60`).

Governing documents:

- `docs/specs/ilc_row_5_runtime_closure_evaluation_cw2_v0.1.md`
- `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`

### 5.2 CDL-017 ratification carry-forward

`CDL-017` remains open and unratified. The later ratification window remains
pending reviewer approval at `CW-5` close and may open only after `CW-6` review
passes.

The Phase `755` dossier fixes the governing sequence:

- `M-022 approval -> convergence window -> CDL-017 ratification window`

SEC-004 remains post-ratification M-track work rather than a pre-ratification
obligation.

Governing document:

- `docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md`

### 5.3 Row-8 substrate evaluation carry-forward

Before the Option B gate can be re-synthesized as go:

- a specific substrate candidate must be named,
- that candidate must be classified against the Phase `673` exclusion matrix,
- that classification must satisfy the Phase `675` locked independence and
  exclusion criteria.

Governing documents:

- `docs/specs/ilc_external_constitutional_center_and_exclusion_matrix_673_v0.1.md`
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`

### 5.4 Hypergraph Tier 2 carry-forward

Tier `1` substrate additions are complete in commit `1c027054`:

- `HyperEdge` dataclass,
- sparse incidence index,
- Node embedding fields,
- `spectral_distance()` utility,
- `SpectralBeacon` stub.

Tier `2` remains SIM-gated. Positive results are still required before the
corresponding implementations proceed:

- `SIM-HYPEREDGE-01` for stable hyperedge-weight calibration,
- `SIM-EMBED-01` for content-type-specific embedding model selection,
- `SIM-SPECTRAL-01` for λ₂ signal quality, compute feasibility, and spoofability.

Governing documents:

- `docs/adr/ADR_0029_Hypergraph_Substrate.md`
- `docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md`
- `docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md`

### 5.5 Hypergraph Tier 3 carry-forward

The following remain gated on positive SIM results plus governance / patent
decisions before implementation:

- star expansion for hyperedge entities,
- Proof of Structural Knowledge (`PoSK`),
- sealed spectral beacon emission,
- spectral routing,
- Merkle-Laplacian paper publication.

The gating posture remains:

- positive SIM results first,
- CDL ratification where governance surfaces are implicated,
- patent assessment before publication-sensitive lanes proceed.

Governing documents:

- `docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md`
- `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md`

### 5.6 Incremental structural proof chain carry-forward

The incremental structural proof chain remains deferred:

- `compute_laplacian_delta()` is deferred pending `SIM-SPECTRAL-01`,
- `perturbation_norm` storage is deferred pending the same signal validation,
- CDL ratification is required before `spectral_hash` enters the epoch
  commitment record.

Governing document:

- `docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md`

## 6. Forward path and non-claims

The forward path to Option B gate satisfaction is visible and bounded:

1. keep row `7` closed and preserve that runtime evidence in the planning canon,
2. complete `CW-6` closure and pass reviewer audit,
3. open the later `CDL-017` ratification window if the reviewer approves,
4. name a specific substrate candidate and evaluate it against the Phase `673`
   / Phase `675` row-8 rules,
5. re-synthesize the Option B gate after both blockers are actually discharged.

This artifact does **not** claim:

- Option B selection,
- `CDL-017` ratification,
- row `5` closure,
- that the no-go verdict means Option B is unachievable.
