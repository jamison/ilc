# ILC Window 745-748 Guidance v0.1

**Prepared by:** Codex  
**Date:** 2026-04-20  
**For:** Codex  
**Capsule at open:** v5.2  
**Frontier at open:** Window 739-744 CLOSED; Window 745-748 is the next main-lane continuation

---

## 1. Window purpose

Window 745-748 has three linked jobs:

1. define and commission the **Mysticeti convergence window** as a later
   bounded window with explicit artifact-gated entry conditions,
2. advance **ADR-0031** from `Proposed` to `Accepted` as housekeeping because
   the proto fields it required are already present in `ilc_app.proto`, and
3. advance the **planning surfaces** to the live post-744 frontier.

The legal positioning technical facts annex (passive ECU attribution, validator
staking Howey analysis inputs) is deferred. It remains on the non-gate
carry-forward list and will be written before broader public RC claims, but it
does not belong in this window.

This window is not the convergence window itself. It does not close row `5`,
does not close row `7`, does not ratify `CDL-017`, and does not graduate
Option B.

The central discipline for this window is:

- commission the next honest closure lane without pretending it has opened,
- advance planning surfaces to the live frontier without smuggling runtime or
  constitutional claims that the evidence base does not support.

Primary source anchors:

- `docs/specs/ilc_antigravity_context_capsule_v5.2.md`
- `docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md`
- `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
- `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`

---

## 2. In scope

- Window `745-748` sequence lock and live-frontier recheck
- Mysticeti convergence window commissioning spec:
  artifact-gated entry conditions, bounded phase budget, authorized outputs,
  explicit exclusions, and honest carry-forward route
- ADR-0031 housekeeping acceptance:
  status change from `Proposed` to `Accepted` if the repo still shows the
  required proto contract already landed without further implementation work
- planning-surface advance:
  capsule `v5.3`, launch roadmap `v0.4`, and `docs/PLANNING_INDEX.md`
- coherence report and closure gate

The convergence window commissioned here must define a later bounded window
that may close:

- row `5` runtime closure,
- row `7` censorship-resistance runtime closure,
- row `7` strong-exitability closure,
- row `8` disposition,
- Option B graduation gate synthesis under ADR-0028.

This window may define those later outputs, but it does not claim them now.

---

## 3. Hard constraints

- No `CDL-017` ratification in this window
- No row `5` move to `runtime_closed`
- No row `7` move to `runtime_closed`
- No Option B graduation claim in this window
- ADR-0028 Option D remains the active posture
- No `ilc_core/` or `ilc_consensus/` mutation in the Codex lane
- Track B wording must be re-read from `docs/phases/STATUS.md` tail at
  execution time; capsule `v5.2` is frozen at Window `744` close and does not
  control the live M-series line
- Convergence-window entry conditions must bind to **committed artifacts**, not
  to assumed Gemini phase labels; the current M-series lane still labels
  `M-020` as audit preparation, `M-021` as audit remediation, and `M-022` as
  handoff, so the gating authority is the artifact bundle, not the phase number
- ADR-0031 acceptance is housekeeping-only in this window; if accepted, the
  change is limited to the ADR file and any strictly necessary doc-only
  cross-reference alignment
- Do not represent planning-surface advancement as evidence that row `5`, row
  `7`, row `8`, `CDL-017`, or Option B have crossed their actual gates

---

## 4. Required outputs

| Output | Form | Notes |
|---|---|---|
| Window 745-748 sequence lock | `docs/specs/ilc_phase_745_748_sequence_lock_v0.1.md` | Freezes non-goals and records the live Track B line from `STATUS.md` |
| Mysticeti convergence window commissioning spec | `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md` | Must define entry conditions, phase budget, authorized outputs, and exclusions for the later convergence window |
| ADR-0031 status advance | `docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md` | Change `Status: Proposed` to `Status: Accepted` if the required proto contract is already landed |
| Capsule v5.3 | `docs/specs/ilc_antigravity_context_capsule_v5.3.md` | Supersedes v5.2; records live Track B line from `STATUS.md` tail |
| Launch roadmap v0.4 | `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.4.md` | Must reflect M-019 complete, M-020 next, and convergence-window commissioning |
| Planning index advance | `docs/PLANNING_INDEX.md` | Must point to the live guidance/capsule/roadmap frontier |
| Coherence report | `docs/specs/ilc_coherence_report_748_v0.1.md` | Standard window-close synthesis artifact |
| Closure gate | `docs/specs/ilc_window_745_748_closure_gate_748_v0.1.md` | Must route carry-forward to the convergence window and preserve all non-closures honestly |

These names are the recommended canonical forms for packet drafting.

---

## 5. Suggested phase structure

| Phase | Purpose |
|---|---|
| 745 | Sequence lock — re-read the live frontier, freeze the non-goals (`no row closure`, `no CDL-017 ratification`, `no Option B graduation`), and record the authoritative Track B line from `STATUS.md` |
| 746 | Commissioning tranche — publish the Mysticeti convergence window commissioning spec and advance ADR-0031 from `Proposed` to `Accepted` as housekeeping if the proto contract is already present |
| 747 | Planning-surface advance — publish capsule `v5.3`, launch roadmap `v0.4`, and the `PLANNING_INDEX` update to reflect `M-019` complete, `M-020` next, convergence-window commissioning published, and ADR-0031 accepted |
| 748 | Coherence report and closure gate — close Window `745-748`, record what was commissioned versus what remains blocked, and route carry-forward explicitly to the later convergence window |

The commissioned convergence window defined in Phase `746` should itself be a
bounded **six-phase** lane:

1. convergence sequence lock and artifact-entry verification,
2. row `5` runtime closure lane using committed `SIM-LEAKAGE-01` results,
3. row `7` censorship-resistance runtime closure lane using the committed live
   artifact bundle that satisfies the Phase `741` Section `3.2` contract,
4. row `7` strong-exitability closure lane using committed export / verify /
   replay / migrate evidence,
5. row `8` disposition plus Option B graduation-gate synthesis under ADR-0028,
6. coherence report, capsule, and closure gate.

That later window does not open until every entry artifact exists.

---

## 6. Inherited evidence and governing baselines

These are inherited settled or already-closed surfaces, not reopened here:

- `CDL-066`, `CDL-067`, and `CDL-068` are ratified
- `CDL-017` remains open and unratified
- row `5` remains `spec_closed_runtime_pending`
- row `7` remains `spec_closed_runtime_pending`
- row `8` remains inherited and not runtime-advanced
- ADR-0028 Option D remains active

These are the load-bearing inherited evidence surfaces for Window `745-748`:

- **Window-close authority:** `docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md`
  fixes the inherited post-744 frontier and the carry-forward posture
- **Row 5 runtime package:** `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
  defines the exact row-5 runtime evidence bar
- **Row 5 commissioned measurement:** `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
  defines the dedicated future leakage-measurement pass
- **Row 7 runtime package:** `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
  splits censorship-runtime confirmation from the separate strong-exitability
  drill contract
- **Option D / Option B route:** `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
  keeps Option D active and binds Option B graduation to the checklist route
- **Option D / Option B planning context:** `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
  remains a reference-tier planning memo; use it for historical route context,
  not as the live authority over the current frontier
- **701+ carry-forward backbone:** `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
  remains the live multi-window carry-forward program for foundational closure
- **ADR-0031 housekeeping target:** `docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md`
  is still `Proposed`, but the required `EdgeRecord` / `HyperEdgeRecord`
  contract is already present in `ilc_consensus/proto/ilc_app.proto`

Convergence-window entry is blocked until **all three** committed artifact
classes exist:

1. a committed Gemini runtime artifact bundle satisfying the Phase `741`
   Section `3.2` censorship-resistance contract,
2. a committed `SIM-LEAKAGE-01` results artifact for row `5`, and
3. a committed Gemini strong-exitability drill results artifact.

If Gemini later packages these as `M-020`, `M-021`, `M-022`, or under different
phase numbers, the artifact bundle controls. The numeric label does not.

---

## 7. Key questions this window must answer honestly

1. What exact committed artifacts are required before the convergence window can
   open, and how should those artifact checks be written so they survive future
   Gemini renumbering?
2. What is the bounded phase budget for the convergence window, and which row
   closures or graduation outputs belong inside it versus outside it?
3. Is ADR-0031 acceptance truly housekeeping-only, or does the repo reveal any
   still-missing proto or documentation dependency that must be addressed
   before status can advance?
4. Which planning surfaces must move in Phase `747` so future sessions stop
   inheriting the stale `M-018 -> M-019` frontier line?
5. What exactly remains blocked at window close so that no reader mistakes
   commissioning work for runtime closure, `CDL-017` ratification, or Option B
   graduation?

This window does not need to pretend that Codex can manufacture Gemini runtime
artifacts. It needs to commission the honest next lane and tighten the planning
canon around the live frontier.

---

## 8. Required reading before Phase 745 begins

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.2.md`
3. `docs/phases/STATUS.md` (tail)
4. `docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md`
5. `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
6. `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
7. `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
8. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
9. `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
10. `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
11. `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
12. `docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md`
13. `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

---

## 9. No special pre-window conversation gate

Window 745-748 contains no CDL ratification and no runtime mutation. No special
pre-window conversation gate is required before packet drafting begins.

Standard review still applies. The live authority order remains:

1. `STATUS.md` tail for Track B,
2. the most recent closed capsule and closure gate for main-lane frontier,
3. this guidance doc for Window `745-748` scope and drafting intent.

---

## 10. Track B line at window open

From `docs/phases/STATUS.md` tail (verified 2026-04-20):

> **Current:** M-019 (Adversarial Hardening and Byzantine Fault Simulation) complete. `run_m019_adversarial_hardening_verdict=pass`  
> **Next planned phase:** M-020 (External Security Audit Preparation)

This live Track B line supersedes the stale `M-018 -> M-019` line frozen inside
capsule `v5.2` and launch roadmap `v0.3`.

---

## 11. Closure-gate selftest chain note

The closure-gate selftest chain for this window should extend from:

- `ILC_PHASE_744_GATE_SELFTEST=1`

to:

- `ILC_PHASE_748_GATE_SELFTEST=1`

When drafting the closure-gate test, read the actual prior closure-gate test
file rather than reasoning by analogy from memory.
