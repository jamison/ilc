# ILC Master Completion Roadmap v0.1

**Date:** 2026-04-20  
**Owner lane:** Codex main lane  
**Window of publication:** 749-752

`master_completion_roadmap_published`
`master_completion_roadmap_replaces_stale_forward_planning_narratives`

This document is the single human-readable forward-planning roadmap from the
live post-748 frontier through RC candidate. It carries forward the still
load-bearing future content that had been distributed across:

- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`,
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`,
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`.

It does not reopen convergence, ratify `CDL-017`, or claim any row closure by
planning rhetoric alone.

## 1. Current frontier

At live execution time, `STATUS.md` tail is authoritative for Track B:

- `M-021` is current and recorded as complete.
- `M-022` is the next planned Gemini phase.

At the same frontier, the main lane posture is:

- Window `745-748` is closed,
- capsule `v5.3` remains the latest capsule,
- the later Mysticeti convergence window is commissioned but not open,
- row `5` remains `spec_closed_runtime_pending`,
- row `7` remains `spec_closed_runtime_pending`,
- row `8` remains inherited and unchanged,
- `CDL-017` remains open and unratified,
- Option B remains deferred under ADR-0028.

Two authority rules survive from the earlier planning canon and remain binding:

1. Track B current/next wording comes from the live `STATUS.md` tail rather
   than from older capsules, roadmaps, or session memory.
2. Convergence entry remains artifact-gated. A phase-status line or local
   worktree draft does not by itself satisfy the later convergence entry gate.

This roadmap therefore records the live frontier without silently promoting
uncommitted or un-reverified artifacts into convergence authority.

## 2. Track B live frontier and remaining work

### 2.1 M-021 — SIM-LEAKAGE-01 plus conditional audit-remediation branch

The live Track B frontier now records M-021 as complete. That does not mean
row `5` is closed. It means the row-5 evidence lane has moved from pure
commissioning into evidence-bearing runtime posture.

The M-021 obligations are:

- primary obligation: execute `SIM-LEAKAGE-01` against the Phase `740`
  commissioning contract,
- secondary obligation: verify the committed security fixes around the M-020
  audit-prep tranche, including the explicit HIGH-001 two-layer-defence note
  in the audit brief and the documented HIGH-002 / CRIT-001 dispositions,
- conditional obligation: if a real external audit has been engaged and
  findings exist, Critical and High dispositions remain part of the lane rather
  than being erased from the plan.

The row-5 governance consequence is strict:

- if the committed `SIM-LEAKAGE-01` carrier clears the `0.45 / 0.60` linkage
  bands, convergence CW-2 may close row `5`,
- if it fails those bands, convergence CW-2 must record a fail verdict and row
  `5` remains open,
- no planning surface is allowed to convert a documented failed leakage run
  into a closure claim.

The expected row-5 carrier path remains:
`docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`

### 2.2 M-022 — exitability drill and Gemini handoff package

M-022 is the remaining Track B phase. It has two linked obligations:

1. **Strong exitability drill**
   The handoff must show all four steps with physical evidence:
   export, independent verify, replay on a fresh node, and migration without
   original-operator consent or API dependence.

2. **Gemini handoff package**
   The handoff package must summarize the Rust implementation surface for the
   later Codex lane, including:
   implementation notes, CDL-017 activation notes, SEC-004 activation scope,
   final workload state, audit/remediation summary, and first-validator
   deployment prerequisites.

The expected handoff carrier path remains:
`docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`

M-022 is necessary for the later Codex constitutional work, but it does not by
itself ratify `CDL-017` and it does not skip the later convergence window.

## 3. Convergence window

The later Mysticeti convergence window is already commissioned by:
`docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`

This roadmap does not re-specify that window. It records the authoritative
entry posture and the six-phase structure so a human reader can follow the
remaining route.

### 3.1 Entry artifact classes

The convergence window does not open until all three artifact classes exist and
are re-verified by the later convergence sequence lock:

1. **Row-7 censorship bundle**
   Current carrier: `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`

2. **Row-5 leakage results**
   Expected carrier: `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`

3. **Strong-exitability drill results**
   Expected carrier within:
   `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`

The integration rule is explicit: the artifact class controls, not the Gemini
phase number. If labels move, the carrier and its re-verification contract
remain authoritative.

### 3.2 Six-phase budget

The commissioned six-phase convergence budget is:

1. CW-1: convergence sequence lock and artifact re-verification
2. CW-2: row `5` runtime-closure evaluation
3. CW-3: row `7` censorship-resistance runtime-closure evaluation
4. CW-4: row `7` strong-exitability runtime-closure evaluation
5. CW-5: row `8` disposition plus Option B graduation-gate synthesis
6. CW-6: coherence report, successor capsule, and closure gate

### 3.3 Surviving integration rules

These rules are carried forward as live doctrine for the remaining route:

- artifact-gated entry beats planning optimism,
- TODO / carry-forward items stay explicit rather than disappearing into prose,
- doctrinal or explanatory memos are not constitutional proof by themselves,
- operator judgment remains named where the repo has not legitimately reduced a
  decision to code or evidence alone.

## 4. CDL-017 ratification window

`CDL-017` is not ratified inside convergence. It routes through a **separate
subsequent Codex window** that opens only after convergence closes.

That later ratification window consumes four input classes:

1. the constitutional text from Phase `695` opening,
2. the Codex-side prelock evidence from Window `733-738`,
3. the M-022 implementation handoff confirming what the Rust validator
   scaffolding provides and what ratification must activate,
4. the convergence row evidence showing the honest runtime position on rows
   `5`, `7`, and `8`.

The direct implementation follow-on after ratification is also fixed:

- SEC-004 activation begins only after `CDL-017` ratifies,
- first authorized validator deployment remains an explicit human gate,
- true multi-machine provisioning follows deployment authorization rather than
  being silently bundled into the ratification act.

This keeps the route honest:

- convergence closes the row evidence,
- the later CDL-017 window performs the constitutional ratification,
- deployment authorization remains a separate operator gate after that.

## 5. Pre-RC obligations

These items remain real, but they do not block convergence or the later
CDL-017 ratification window by default:

- **Legal positioning memo**
  The passive ECU attribution / decay / treasury / validator-parameter facts
  package still needs a counsel-facing memo before broader public RC claims.
  It remains deferred carry-forward, not a current convergence gate.

- **SEC-007a maintenance**
  `protoc` vendoring and later tonic / protox cleanup remain honest
  non-blocking maintenance.

- **Stronger public-substrate replayability proof**
  The local M-016 extractor lane is useful evidence but not the final public
  distributed replayability story. That stronger proof remains later
  engineering carry-forward even after convergence planning is clarified.

## 6. Post-convergence research lanes

These lanes are not on the critical path to the commissioned convergence work.
They must remain named so they are not silently forgotten.

### 6.1 CDL-062 sovereign-substrate research lane

`CDL-062` does not open merely because the convergence window exists.
Its admissibility route remains:

- rows `5`, `7`, and `8` must be honestly closed or locked enough that the lane
  is not opening into a privacy, censorship, or constitutional vacuum,
- the admissibility question remains a human gate,
- sovereign-substrate selection itself is later than admissibility.

### 6.2 L3 app-development lane

The L3 app-development program remains post-convergence and later than the
constitutional and runtime closure work. It is real carry-forward, not a
current blocker.

### 6.3 Morphogenetic hypergraph research lane

The morphogenetic cluster remains explicitly post-mainnet research, with the
one earlier wire-format gate already resolved:

- ADR-0031 is accepted,
- ADR-0029 / ADR-0030 remain proposed,
- the SIM-HYPEREDGE / SPECTRAL / EMBED / BEACON / ROUTING family remains
  registered but uncommissioned,
- the lane remains outside the convergence critical path.

## 7. Human conversation gates

The following judgments still require explicit human review and must not be
misrepresented as purely code-decided:

- what counts as enough censorship resistance for row `7`,
- what “independence from external constitutional centers” means for row `8`,
- how much privacy is enough for row `5` without collapsing public
  verifiability,
- whether a failed row-5 leakage run requires redesign, rerun, or explicit
  non-closure at convergence,
- whether `CDL-062` is admissible yet,
- final Option B selection after any later graduation-gate synthesis,
- first authorized validator deployment after the later CDL-017 ratification
  window.
