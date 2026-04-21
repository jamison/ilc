# ILC Mysticeti Convergence Window Guidance v0.1

Status: PRE-DRAFT — convergence window is not open.  
This guidance becomes active only when all three entry artifact classes exist
and are re-verified by the convergence sequence lock (`CW-1`).

**Phase:** 754  
**Window:** 753-756  
**Date:** 2026-04-21  
**Author:** Codex

`convergence_window_guidance_pre_draft_only`
`cw1_artifact_reverification_hard_gate`
`cw2_row5_runtime_closure_evaluation_defined`
`cw3_row7_censorship_runtime_closure_defined`
`cw4_row7_exitability_closure_defined`
`cw5_row8_and_option_b_gate_synthesis_defined`
`cw6_convergence_window_closure_defined`
`artifact_paths_authoritative_not_phase_labels`
`no_cdl_017_ratification_inside_convergence_window`
`epochcheckpointmsg_path_carries_row7_evidence_weight_post_crit_001`

## 1. Status and boundary

This document is execution guidance for a later six-phase convergence window.
It is not the convergence sequence lock itself and it does not open the window.

The later convergence window is the point where:

- the Gemini runtime-evidence lane,
- the Codex constitutional / planning lane, and
- the ADR-0028 Option B graduation route

first become one bounded decision surface.

That bounded surface remains closed until `CW-1` re-verifies every required
artifact class against its governing contract.

## 2. Window purpose

The later convergence window exists to do five things and only those five
things:

1. re-verify the committed entry artifacts,
2. evaluate row `5` against the Phase `740` runtime-closure bar,
3. evaluate row `7` against the Phase `741` censorship and strong-exitability
   contracts,
4. record the row `8` disposition and synthesize the Option B graduation gate
   under ADR-0028,
5. close honestly with a coherence report, successor capsule, and closure
   gate.

The convergence window does **not** ratify `CDL-017`. That is a separate later
window which consumes the convergence outputs after this window closes.

## 3. Entry conditions and authority order

Authority for entry conditions remains
`docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`.
This pre-draft does not rewrite those conditions from scratch. It translates
them into the concrete `CW-1` verification checklist.

The three required artifact classes are:

1. **Row-7 censorship runtime bundle**
   `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
2. **SIM-LEAKAGE-01 results**
   `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`
3. **Strong-exitability drill evidence**
   within `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`

The artifact path and contract are authoritative. The Gemini phase label is
descriptive only. If a carrier path changes later, the later sequence lock
must bind the new path explicitly rather than assuming that the old label
still applies.

`CW-1` is a hard gate. If any artifact class is absent or fails contract
re-verification, the convergence window does not proceed to any row-closure
phase.

## 4. Hard constraints

These constraints apply verbatim throughout the later convergence window:

- No row closure may be claimed before the relevant evidence is re-verified at
  `CW-1`
- No `CDL-017` ratification occurs inside the convergence window
- No `ilc_core/` or `ilc_consensus/` mutation in the Codex convergence lane
- Option B graduation-gate synthesis is not the same as Option B selection
- Row `8` disposition is descriptive and evidence-bound, not a ratification act
- Artifact-class verification failure at `CW-1` stops the window honestly
- Track B current/next wording must be re-read from `docs/phases/STATUS.md`
  tail at `CW-1`, not copied from memory or older capsules

## 5. Six-phase structure

### CW-1 — Convergence sequence lock and artifact re-verification

**Purpose:** verify all three artifact classes against their governing
contracts before any row-closure work begins.

**Primary inputs:**

- `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
- `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`
- `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`
- `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
- `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
- `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
- `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`

**Required output:**
`ilc_mysticeti_convergence_window_sequence_lock_vX.Y.md`

**Pass condition:** all three artifact classes are present and satisfy their
governing contracts:

- the row-7 bundle includes the live censoring-validator evidence and the
  short mapping note back to `N=4`, `F=1`, `MaxRound=5`, `Liveness`,
- the `SIM-LEAKAGE-01` results include methodology plus raw numbers for all
  three attacker variants rather than a verdict token alone,
- the M-022 handoff includes physical strong-exitability drill evidence:
  actual export path, actual replay-log epoch numbers, and fresh-node startup
  log.

**May not claim:** any row closure, any `CDL-017` action, or any Option B
selection claim.

### CW-2 — Row 5 runtime-closure evaluation

**Purpose:** evaluate whether `SIM-LEAKAGE-01` actually satisfies the row-5
runtime closure bar.

**Primary inputs:**

- `CW-1` verified `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`
- `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
- `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`

**Required output:**
`ilc_row_5_runtime_closure_evaluation_vX.Y.md`

**Pass condition:** the evaluation shows, from the committed results artifact
itself:

- ordinary-observer / hosted-query same-contributor linkage recall `<= 0.45`,
- operator-path same-contributor linkage recall `<= 0.60`,
- observability-floor mapping preserved per Phase `679`.

If either band is missed, the honest verdict is fail and row `5` remains
pending.

**May not claim:** row `5` closure if either linkage band is exceeded or if
the observability-floor mapping is missing.

### CW-3 — Row 7 censorship-resistance runtime-closure evaluation

**Purpose:** evaluate whether the row-7 censorship-resistance obligation is
discharged by the committed live runtime bundle.

**Primary inputs:**

- `CW-1` verified
  `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
- `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
- `docs/specs/ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md`

**Required output:**
`ilc_row_7_censorship_runtime_closure_evaluation_vX.Y.md`

**Pass condition:** the committed bundle confirms every Phase `741` Section
`3.2` requirement, including:

- live censoring-validator scenario,
- `N=4`, `F=1` shape or stricter live configuration,
- practical inclusion not suppressed permanently,
- eventual commit under bounded censoring quorum,
- explicit mapping note to the Phase `698` proof basis.

Post-CRIT-001 context must be stated explicitly: pre-fix evidence may contain
`EpochSettlementTx` references, but the row-7 evidence weight is carried by the
redundant-path liveness property via `EpochCheckpointMsg`, not by the rejected
`EpochSettlementTx` path.

**May not claim:** full row-7 closure. `CW-3` discharges only the
censorship-resistance side.

### CW-4 — Row 7 strong-exitability closure evaluation

**Purpose:** evaluate whether the M-022 strong-exitability drill satisfies the
Phase `741` Section `4` contract.

**Primary inputs:**

- `CW-1` verified `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`
- `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
- `docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md`

**Required output:**
`ilc_row_7_exitability_closure_evaluation_vX.Y.md`

**Pass condition:** all four drill steps are confirmed with physical evidence:

1. export,
2. independent verify,
3. replay on a fresh node,
4. migrate without original-operator consent or API dependence.

Actual exported file paths, actual replay-log epoch numbers, and a fresh-node
startup log are mandatory.

**May not claim:** row `7` closure if any step lacks physical evidence or if
verification / replay depends on the original operator.

### CW-5 — Row 8 disposition and Option B graduation-gate synthesis

**Purpose:** record what the current evidence says about row `8` and synthesize
the Option B graduation gate under ADR-0028.

**Primary inputs:**

- `CW-2` row-5 verdict
- `CW-3` row-7 censorship verdict
- `CW-4` row-7 exitability verdict
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`

**Required output:**
`ilc_row_8_disposition_and_option_b_gate_synthesis_vX.Y.md`

**Pass condition:** the artifact records the evidence honestly:

- row `8` disposition is descriptive and bounded by the evidence actually in
  hand,
- Option B gate synthesis is a go / no-go record under ADR-0028,
- a negative gate synthesis is still an honest pass if that is what the
  evidence supports.

**May not claim:** Option B selection. Gate synthesis records whether Option B
becomes selectable; operator selection remains separate.

### CW-6 — Coherence report, successor capsule, and convergence closure gate

**Purpose:** close the convergence window honestly.

**Primary inputs:**

- `CW-1` through `CW-5` outputs
- current capsule and `docs/phases/STATUS.md` tail
- `docs/PLANNING_INDEX.md`

**Required outputs:**

- `ilc_coherence_report_CWX_vX.Y.md`
- successor capsule
- `ilc_mysticeti_convergence_window_closure_gate_vX.Y.md`
- updated `docs/PLANNING_INDEX.md`
- updated `docs/phases/STATUS.md`

**Pass condition:** the closure gate states exactly what closed and what did
not. If row `5`, row `7`, row `8`, or the Option B gate do not all land
positively, the closure must say so without inflation.

**May not claim:** `CDL-017` ratification. That remains a later separate window.

## 6. Inherited constraints throughout convergence

The later convergence window inherits these constraints from the commissioning
spec and from Phases `740` and `741`:

- artifact-class verification at `CW-1` is authoritative,
- row `5` closure is governed by the Phase `740` leakage bands and
  observability-floor mapping,
- row `7` censorship and exitability remain separate obligations,
- no decision-log mutation occurs unless a later dedicated authorization opens
  one; row `8` and Option B gate work are documentation, not CDL acts,
- the later convergence window still does not ratify `CDL-017`.

## 7. Required reading before CW-1

1. `docs/PLANNING_INDEX.md`
2. current capsule
3. `docs/phases/STATUS.md` tail
4. `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`
5. `docs/specs/ilc_master_completion_roadmap_v0.1.md`
6. `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
7. `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
8. `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
9. `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
10. `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
11. `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`
12. `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`

## 8. What this pre-draft is not

This pre-draft is not:

- an open convergence window,
- a substitute for `CW-1` artifact re-verification,
- a row-5 closure claim,
- a row-7 closure claim,
- a row-8 ratification act,
- an Option B selection act,
- a `CDL-017` ratification artifact.
