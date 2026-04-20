# ILC Window 753-756 Guidance v0.1

**Prepared by:** Claude (architectural review lane)
**Date:** 2026-04-20
**For:** Codex
**Capsule at open:** v5.3 (or successor if 749-752 produces v5.4)
**Frontier at open:** Window 749-752 CLOSED; Window 753-756 is the next
main-lane continuation

---

## 1. Window purpose

Window 753-756 produces two pre-draft artifacts that must exist and be
reviewed before the convergence window opens, but which do not themselves
open it:

1. **Convergence window guidance pre-draft** — the phase-by-phase execution
   guidance for each of the six convergence phases, so the convergence window
   can open and execute immediately on M-022 approval without a separate
   guidance-writing lag.

2. **CDL-017 ratification text pre-work** — the ratification readiness
   dossier assembling the constitutional text, Codex-side prelock evidence
   summary, what M-022 must confirm on the implementation side, and the
   exact SEC-004 activation scope. This is preparation, not ratification.

Both are clearly labeled as pre-drafts. Neither opens the convergence window.
Neither ratifies CDL-017. Both are planning and documentation work only.

This window has no dependency on M-021 or M-022 completing first. It runs in
parallel with the M-track. The pre-draft artifacts may reference expected M-022
deliverables by artifact class (not by Gemini phase label) as placeholders.

Primary source anchors:

- `docs/specs/ilc_antigravity_context_capsule_v5.3.md` (or successor)
- `docs/specs/ilc_window_749_752_closure_gate_752_v0.1.md`
- `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`
- `docs/specs/ilc_master_completion_roadmap_v0.1.md`
- `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
- `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
- `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
  (archived; §5.6 and §6 still useful as historical reference for convergence
  window original scoping intent)
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` §4
  (Convergence with main Codex lane)

---

## 2. Role context

Same as Window 749-752. Gemini executes M-021 and M-022. Claude audits.
Operator gates. Codex produces all main-lane planning and constitutional work.
This window's outputs are Codex lane artifacts only.

---

## 3. In scope

### 3.1 Convergence window guidance pre-draft

Create `docs/specs/ilc_mysticeti_convergence_window_guidance_v0.1.md`.

This document is the execution guidance for the six-phase convergence window.
It is analogous to the Window 745-748 guidance (`ilc_window_745_748_guidance_v0.1.md`)
but for the convergence window.

**Label clearly at the top:**

```
Status: PRE-DRAFT — convergence window is not open.
This guidance becomes active only when all three entry artifact classes
exist and are re-verified by the convergence sequence lock (CW-1).
```

**Required sections:**

**§1 — Window purpose**

The convergence window is the only point where the Gemini and Codex lanes
formally merge. It closes rows 5 and 7, dispositions row 8, and synthesizes
the Option B graduation gate under ADR-0028. It does not open until all
three artifact classes exist and are re-verified.

**§2 — Entry conditions (from commissioning spec)**

Do not re-specify from scratch. Reference
`ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md` as the
authority. Summarize the three artifact classes:

1. Row-7 censorship bundle — `ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
   (committed; must be re-verified by CW-1 against Phase 741 §3.2 contract)
2. SIM-LEAKAGE-01 results — `ilc_sim_leakage_01_results_M021_v0.1.md`
   (M-021 obligation; must include methodology + raw numbers, not just verdict)
3. Exitability drill results — within `ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`
   (M-022 obligation; physical evidence required: exported file path, replay
   log with epoch numbers, fresh-node startup log)

State explicitly: if any artifact class is absent or fails re-verification
at CW-1, the convergence window does not proceed. CW-1 is a hard gate, not
a formality.

**§3 — Hard constraints for the convergence window**

These must appear verbatim so every convergence phase can inherit them:

- No row closure may be claimed before the relevant evidence is re-verified
  at the convergence sequence lock (CW-1)
- No CDL-017 ratification occurs inside the convergence window — CDL-017
  ratification is a separate subsequent window
- No ilc_core/ or ilc_consensus/ mutation in the Codex convergence lane
- Option B graduation-gate synthesis (CW-5) is not the same as Option B
  selection — gate synthesis is the artifact that records whether evidence
  supports selection; selection is an operator decision
- Row 8 disposition is descriptive; row 8 is an inherited criteria lock
  and its disposition records what the evidence says, not a ratification act

**§4 — Six-phase structure with per-phase guidance**

For each of the six phases, provide:
- purpose (one sentence)
- primary inputs (which artifact classes and which prior-phase outputs)
- required outputs (artifact name and content scope)
- pass condition (what must be true for this phase to close)
- what may NOT be claimed in this phase

**CW-1: Convergence sequence lock + artifact re-verification**

Purpose: Verify all three artifact classes exist and satisfy their governing
contracts before any row-closure work begins.

Inputs:
- `ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md` — verify against
  Phase 741 §3.2 contract: explicit N=4, F=1, MaxRound=5, Liveness mapping
  to Phase 698 proof, live censoring-validator evidence
- `ilc_sim_leakage_01_results_M021_v0.1.md` — verify against Phase 740
  commissioning spec: all three attacker variants present, linkage recall
  numbers stated with methodology, observability-floor mapping present
- Exitability drill results within M-022 handoff — verify: four steps
  executed (export, independent verify, fresh-node replay, migrate without
  operator API), physical evidence present (not assertion only)

Required output: `ilc_mysticeti_convergence_window_sequence_lock_vX.Y.md`
containing explicit go/no-go verdict for each artifact class.

Pass condition: all three artifact classes verified against their governing
contracts. Any single failure stops the window.

May not claim: any row closure, any CDL action, any Option B claim.

**CW-2: Row 5 runtime closure evaluation**

Purpose: Evaluate whether SIM-LEAKAGE-01 results satisfy the row 5 runtime
closure bar.

Inputs: CW-1 verified SIM-LEAKAGE-01 results + Phase 740 commissioning spec
pass criteria (0.45 / 0.60 linkage recall bands).

Required output: `ilc_row_5_runtime_closure_evaluation_vX.Y.md` — explicit
verdict (pass / fail / conditional) against the Phase 740 pass criteria, with
the actual measurement figures from M-021 results cited verbatim.

Pass condition: ordinary-observer / hosted-query recall ≤ 0.45 AND
operator-path recall ≤ 0.60 AND observability-floor mapping confirmed. If
any band is exceeded, the verdict is fail and row 5 does not close.

May not claim: row 5 is closed if either band is missed. A conditional pass
requires explicit statement of what remediation is required.

**CW-3: Row 7 censorship-resistance runtime closure evaluation**

Purpose: Evaluate whether the M-020 censoring-validator evidence satisfies
the Phase 741 §3.2 censorship-resistance contract.

Inputs: CW-1 verified `ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
+ Phase 741 §3.2 contract + Phase 698 TLC proof (N=4, F=1, MaxRound=5,
Liveness).

Required output: `ilc_row_7_censorship_runtime_closure_evaluation_vX.Y.md` —
explicit verdict. Must confirm: N=4/F=1 configuration, four validators
participating, censor scenario correctly executed (V4 dropped
EpochCheckpointMsg from V1; redundant path via V2/V3 delivered epoch; all
four validators committed epoch_record_committed:epoch=1), mapping to
Phase 698 Liveness proof basis.

Pass condition: all Phase 741 §3.2 evidence requirements confirmed from
the committed artifact. Row 7 censorship-resistance obligation discharged.
Row 7 exitability obligation is separate (CW-4).

Note: post-CRIT-001 fix, production builds no longer accept EpochSettlementTx.
The censoring scenario evidence was recorded pre-fix and included
EpochSettlementTx references. The evaluation must note this context and
confirm that the redundant-path liveness property (via EpochCheckpointMsg)
is what carries the row-7 evidence weight, not the EpochSettlementTx path.

**CW-4: Row 7 strong-exitability closure evaluation**

Purpose: Evaluate whether the M-022 exitability drill results satisfy the
Phase 741 §4 strong-exitability contract.

Inputs: CW-1 verified exitability drill evidence from M-022 handoff package
+ Phase 741 §4 contract.

The Phase 741 §4 contract requires all four of:
1. Export: legitimacy-relevant state exported from a running validator
2. Independent verify: exported state verified using only the exported data —
   no calls to the original validator or original-operator APIs
3. Replay: exported state replayed on a fresh node that achieves consensus
4. Migrate: migration completed without original-operator consent or API access

Required output: `ilc_row_7_exitability_closure_evaluation_vX.Y.md` — explicit
verdict against all four steps. Physical evidence must be cited (actual file
paths, epoch numbers, fresh-node logs). Assertion without evidence is a fail.

Pass condition: all four drill steps confirmed with physical evidence. If any
step lacks physical evidence, verdict is fail.

**CW-5: Row 8 disposition + Option B graduation-gate synthesis**

Purpose: Record the row 8 disposition and synthesize whether the Option B
graduation gate is satisfied under ADR-0028.

Inputs: CW-2/CW-3/CW-4 verdicts + ADR-0028 graduation checklist + row 8
criteria lock.

Row 8 disposition: Row 8 is an inherited criteria lock ("independence from
external constitutional centers"). This phase records what the current
evidence says about row 8, not a ratification act. If the evidence is
insufficient, row 8 remains inherited and that is the honest disposition.

Option B graduation-gate synthesis: Re-read the ADR-0028 graduation checklist.
Synthesize a go/no-go verdict based on the CW-2/CW-3/CW-4 outcomes and the
row 8 disposition. If rows 5 and 7 are both closed and row 8 disposition is
satisfactory, the gate synthesizes positive and Option B becomes selectable.
Option B selection itself is an operator decision, not a Codex act.

Required output: `ilc_row_8_disposition_and_option_b_gate_synthesis_vX.Y.md`

Pass condition: honest disposition of all inputs. A negative gate synthesis
is an honest pass — it records what the evidence actually supports.

**CW-6: Coherence report + successor capsule + closure gate**

Purpose: Close the convergence window honestly.

Required outputs:
- `ilc_coherence_report_CWX_vX.Y.md`
- Successor capsule (v5.4 or next in sequence)
- `ilc_mysticeti_convergence_window_closure_gate_vX.Y.md`
- Updated `docs/PLANNING_INDEX.md` and `docs/phases/STATUS.md`

Pass condition: closure gate records what actually closed (which rows,
whether Option B gate synthesized, row 8 disposition) versus what remains
open (CDL-017 ratification, first validator deployment, legal memo). No
inflation of outcomes.

**§5 — Inherited constraints throughout the convergence window**

These apply to every phase:
- Track B current/next line re-read from STATUS.md tail at CW-1; not copied
  from memory or older capsules
- No decision-log mutation except as authorized (CW-5 row 8 disposition and
  Option B gate are documentation, not CDL ratification)
- No ilc_core/ or ilc_consensus/ mutation
- Artifact-class verification at CW-1 is authoritative; if any class fails,
  stop and record failure honestly rather than proceeding on weakened evidence
- Convergence window does not ratify CDL-017 — that is the subsequent window

**§6 — Required reading before CW-1**

1. `docs/PLANNING_INDEX.md`
2. Current capsule
3. `docs/phases/STATUS.md` tail
4. `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`
5. `docs/specs/ilc_master_completion_roadmap_v0.1.md`
6. `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
7. `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
8. `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
9. `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
10. `docs/research/ilc_external_security_audit_brief_M020_v0.1.md`
11. `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md` (M-022 artifact)
12. `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md` (M-021 artifact)
13. `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`

---

### 3.2 CDL-017 ratification readiness dossier

Create `docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md`.

**Label clearly at the top:**

```
Status: PRE-WORK — CDL-017 is not ratified and will not be ratified in
this window. This dossier assembles the ratification inputs so the
CDL-017 ratification window can execute immediately when M-022 is approved.
```

**Required sections:**

**§1 — What CDL-017 covers**

Re-read CDL-017 from the CDL register. Summarize:
- Opened Phase 695
- Bootstrap transition criteria: the conditions under which the validator
  set transitions from the genesis configuration to the first dynamically
  authorized validator set
- Current status: OPEN, unratified
- Codex-side prelock evidence: COMPLETE (Window 733-738)
- Implementation side: Gemini M-007 implemented the BLS key management and
  CDL-017 hooks (unimplemented! guards); full activation awaits ratification

**§2 — Codex-side prelock evidence summary**

Summarize what the Window 733-738 prelock evidence established. Do not
re-derive — cite the committed artifacts. State clearly what constitutional
text and evidence already exists on the Codex side.

**§3 — What M-022 must confirm (implementation side)**

List exactly what the M-022 handoff package must establish before CDL-017
ratification can proceed. Do not assume M-022 has been approved — write this
as a checklist against which M-022 will be evaluated:

1. The Rust validator governance scaffolding: what the M-007 `unimplemented!`
   hooks provide and what is still a stub
2. BLS key ceremony protocol: what M-007 implemented, what a real multi-operator
   key ceremony requires beyond the testnet config
3. SEC-004 activation scope: `TransferCertificate` must gain `epoch: EpochSeq`
   field; `execute_certificate` must resolve the historically active
   `ValidatorSet` per epoch from LMDB epoch record store. This implementation
   work happens after CDL-017 ratification, not before it, but must be
   documented as an activation-scope item in M-022.
4. First validator deployment prerequisites: what the Rust implementation
   requires before a real (non-testnet) validator can be deployed.

**§4 — CDL-017 ratification window scope**

What the CDL-017 ratification window (a separate bounded Codex window,
separate from the convergence window) will execute:

1. CDL-017 ratification — Codex executes the ratification using:
   - The constitutional text from Phase 695 (opening stub)
   - The M-007 key ceremony protocol as implementation evidence
   - The M-009+ testnet results as operational evidence
   - M-022 handoff package as the implementation completeness confirmation
2. Explicit human gate: first authorized validator deployment. This gate
   is not satisfied by CDL-017 ratification alone. It requires explicit
   operator sign-off and is separate from the ratification act.
3. True multi-machine provisioning: the engineering work that follows
   deployment authorization (cert/key distribution, remote binary placement,
   multi-operator evidence capture).

**§5 — SEC-004 disposition**

SEC-004 (epoch/validator-set historical binding) is dormant until CDL-017
activates. Document precisely:
- The gap: `TransferCertificate`s currently carry no epoch reference. When
  the validator set changes (CDL-017 activation), certificates from prior
  epochs would be evaluated against the current validator set incorrectly.
- The fix scope: `TransferCertificate` gains `epoch: EpochSeq`; 
  `execute_certificate` resolves the historically active `ValidatorSet`
  from LMDB for that epoch before verifying signatures.
- Acceptance condition: `test_ejected_validator_sig_rejected_after_epoch_boundary`
  passes (per M-series doc §6 SEC-004 entry).
- Ownership: M-track implementation task, starts after CDL-017 is ratified.
  Not a Codex coding task.

**§6 — What this dossier is NOT**

State explicitly:
- This dossier does not ratify CDL-017
- This dossier does not open the CDL-017 ratification window
- This dossier does not assume M-022 has been approved
- This dossier does not contain the final ratification text — it contains
  the inputs and the checklist for the ratification window to use

---

## 4. Hard constraints

- No opening of the Mysticeti convergence window
- No CDL-017 ratification
- No row closure claims
- No Option B graduation
- No ilc_core/ or ilc_consensus/ mutation
- No decision-log mutation
- The convergence window guidance must be clearly labeled PRE-DRAFT
- The CDL-017 dossier must be clearly labeled PRE-WORK
- Neither document may claim that M-022 has been approved or that the
  convergence window entry conditions are satisfied — they are not yet
- Artifact classes referenced as expected placeholders (M-021 results,
  M-022 drill evidence) must be named by artifact path, not by Gemini
  phase label, so the guidance survives any M-track renumbering
- Do not write the CDL-017 ratification constitutional text itself in this
  window — the dossier assembles inputs and checklists only

---

## 5. Required outputs

| Output | File | Notes |
|---|---|---|
| Window 753-756 sequence lock | `docs/specs/ilc_phase_753_756_sequence_lock_v0.1.md` | Re-read Track B from STATUS.md tail |
| Convergence window guidance pre-draft | `docs/specs/ilc_mysticeti_convergence_window_guidance_v0.1.md` | Labeled PRE-DRAFT; six-phase structure per §3.1 |
| CDL-017 ratification readiness dossier | `docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md` | Labeled PRE-WORK; inputs and checklist only, no ratification text |
| Planning index update | `docs/PLANNING_INDEX.md` | Point to both new pre-draft artifacts |
| Coherence report | `docs/specs/ilc_coherence_report_756_v0.1.md` | Standard window-close synthesis |
| Closure gate | `docs/specs/ilc_window_753_756_closure_gate_756_v0.1.md` | Selftest chain: ILC_PHASE_752_GATE_SELFTEST=1 → ILC_PHASE_756_GATE_SELFTEST=1 |

---

## 6. Suggested phase structure

| Phase | Purpose |
|---|---|
| 753 | Sequence lock |
| 754 | Convergence window guidance pre-draft |
| 755 | CDL-017 ratification readiness dossier |
| 756 | Coherence report + closure gate |

---

## 7. Key questions this window must answer honestly

1. Does the convergence window guidance CW-1 re-verification checklist
   correctly catch a fabricated SIM-LEAKAGE-01 artifact — i.e., does it
   require methodology and raw numbers, not just a verdict statement?
2. Does the convergence window guidance correctly distinguish CW-5 Option B
   graduation-gate synthesis from operator Option B selection?
3. Does the CDL-017 dossier §3 checklist correctly scope what M-022 must
   confirm versus what ratification must add — specifically that SEC-004
   activation is post-ratification implementation, not a pre-ratification
   requirement?
4. Are both pre-draft artifacts clearly labeled so no future reader mistakes
   them for open-window documents or ratification acts?

---

## 8. Closure-gate selftest chain note

The closure gate for this window should extend from:

- `ILC_PHASE_752_GATE_SELFTEST=1`

to:

- `ILC_PHASE_756_GATE_SELFTEST=1`

Read the actual Phase 752 closure gate file before drafting the test.

---

## 9. No special pre-window gate

This window contains no CDL ratification and no runtime mutation. No special
pre-window conversation gate is required.

Standard review applies. Live authority order:
1. STATUS.md tail for Track B
2. Current capsule and Phase 752 closure gate for main-lane frontier
3. This guidance doc for Window 753-756 scope and drafting intent
