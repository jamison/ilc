# ILC Window 739-744 Guidance v0.1

**Prepared by:** Codex  
**Date:** 2026-04-20  
**For:** Codex  
**Capsule at open:** v5.1  
**Frontier at open:** Window 733-738 CLOSED; Window 739-744 is next planned continuation

---

## 1. Window purpose

Window 739-744 has two linked jobs:

1. advance **MVP gate rows 5 and 7** from `spec_closed_runtime_pending`
   into honest runtime-evidence packaging, and
2. ratify **CDL-068** now that its evidence checklist is complete.

This is not the Mysticeti convergence window. `CDL-017` remains outside scope
for ratification here, and the runtime-form work for rows 5 and 7 must remain
honest about what still depends on Gemini-side live multi-machine evidence.

The central discipline for this window is:

- do not over-claim closure on row 5 or row 7 if the live M-series evidence is
  not actually present yet,
- do not delay `CDL-068` ratification behind row-5 / row-7 work, because its
  constitutional checklist is already satisfied.

Primary source anchors:

- `docs/specs/ilc_antigravity_context_capsule_v5.1.md`
- `docs/specs/ilc_window_733_738_closure_gate_738_v0.1.md`
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md`

---

## 2. In scope

- Window `739-744` sequence lock and scope freeze
- row-5 runtime evidence package:
  live operator-path leakage measurement requirements over a multi-machine
  validator testbed
- `SIM-LEAKAGE-01` commissioning spec:
  dedicated traffic-capture and leakage-measurement requirements over the
  Gemini multi-machine validator testbed; this may reuse the `M-019` testbed,
  but it is not the same thing as the default `M-019` pass/fail artifact
- row-7 runtime evidence package:
  live censorship-resistance confirmation requirements plus a separate
  strong-exitability drill contract tied to the already-closed spec and TLC
  evidence
- row-8 disposition note:
  inherited criteria lock remains in force; no row-8 runtime confirmation work
  is commissioned in this window
- `CDL-068` ratification evidence assembly:
  single dossier that proves all opening-side checklist items are satisfied
- `CDL-068` ratification text and decision-log mutation
- coherence report, capsule v5.2, and closure gate

For rows 5 and 7, the window may close on a **commissioning / evidence-package**
posture rather than a measurement-complete posture. If the live Gemini
evidence is not present yet, `spec_closed_runtime_pending` remains the honest
status label. For row `7`, this means the censorship-resistance side may expect
Gemini `M-019` runtime evidence, while the strong-exitability side requires a
separate export / verify / replay / migrate drill and may remain explicitly
deferred if that drill is not executed in-window.

---

## 3. Hard constraints

- No `CDL-017` ratification in this window
- No sovereign substrate selection
- No wallet widening
- `CDL-068` ratification is permitted in this window
- No `ilc_core/` or `ilc_consensus/` mutation in the Codex main lane
- Do not claim row 5 runtime closure unless live operator-path leakage evidence
  actually exists
- Do not claim row 7 censorship-resistance closure unless live censoring-validator
  runtime evidence actually exists (expected from Gemini `M-019`)
- Do not claim row 7 exitability closure in this window; the strong-exitability
  drill (export / verify / replay / migrate without operator consent) is
  explicitly deferred to the Mysticeti convergence window
- No row 8 runtime confirmation work in this window; row 8 remains at its
  inherited criteria-lock posture and routes to the convergence window
- Do not conflate row-5 / row-7 runtime-form packaging with the later Mysticeti
  convergence window
- Track B wording must be re-read from `docs/phases/STATUS.md` tail at
  execution time

---

## 4. Required outputs

| Output | Form | Notes |
|---|---|---|
| Window 739-744 sequence lock | `docs/specs/ilc_phase_739_744_sequence_lock_v0.1.md` | Freezes scope, no-runtime-mutation posture, and ratification boundary |
| Row-5 runtime evidence package | `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md` | Must formalize the live operator-path leakage measurement requirements |
| `SIM-LEAKAGE-01` commissioning spec | `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md` | Must specify a dedicated leakage-measurement pass over the Gemini multi-machine testbed; `M-019` may supply the environment, but its default verdict output is not sufficient by itself |
| Row-7 runtime evidence package | `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md` | Must separate censorship-resistance runtime confirmation from the distinct strong-exitability drill contract |
| `CDL-068` ratification dossier | `docs/specs/ilc_cdl_068_ratification_readiness_dossier_742_v0.1.md` | Must consolidate all checklist evidence before ratification text is written |
| `CDL-068` ratification artifact | `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md` | Must explicitly check all six Phase 736 prelock criteria and isolate the decision-log mutation to the `CDL-068` row only |
| Coherence report | `docs/specs/ilc_coherence_report_744_v0.1.md` | Standard window closure artifact |
| Capsule v5.2 | `docs/specs/ilc_antigravity_context_capsule_v5.2.md` | Supersedes v5.1; records Track B line from `STATUS.md` tail |
| Closure gate | `docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md` | Must route carry-forward to Window 745-748 and the convergence window |

These names are the recommended canonical forms for packet drafting.

---

## 5. Suggested phase structure

| Phase | Purpose |
|---|---|
| 739 | Sequence lock — define window scope, lock no-runtime-mutation and no-`CDL-017`-ratification boundary, re-read Track B from `STATUS.md`, import `CDL-068` evidence-checklist verification |
| 740 | Row-5 runtime evidence package — formalize what the live operator-path leakage measurement must contain; publish `SIM-LEAKAGE-01` as a dedicated leakage-measurement spec that can run on the Gemini multi-machine testbed or a sibling traffic-capture pass; update row-5 status documentation |
| 741 | Row-7 runtime evidence package — formalize censorship-resistance runtime confirmation requirements separately from the strong-exitability drill; connect Phase 698 TLC proof to expected Gemini `M-019` censoring-validator evidence on the censorship side, and publish a separate export / verify / replay / migrate contract for the exitability side |
| 742 | `CDL-068` ratification evidence assembly — consolidate `SIM-TOPOLOGY-01`, `SIM-VALIDATOR-01`, `CDL-017` prelock artifact, and `CDL-039` boundary evidence into a formal dossier; publish ratification-readiness verdict |
| 743 | `CDL-068` ratification — write and publish ratification text and evidence-checklist satisfaction record in commit 1, then mutate exactly the `CDL-068` row in the decision log in commit 2; ratification text must express topology parameters as constitutional floors and ceilings (`k_degree_floor ≥ 4`, `push_fanout_ceiling ≤ 3`, `distinct_cluster_floor ≥ 4`, `max_cluster_share_ceiling ≤ 33%`) rather than hard fixed values; the VRF upgrade trigger (`vrf_upgrade_threshold_validator_count 10`) is a hard threshold, not a range |
| 744 | Coherence report, capsule v5.2, and closure gate — close the window; update frontier; route carry-forward to Window 745-748 and the Mysticeti convergence window |

These phases are a suggested skeleton. Codex may restructure within the window
as long as every required output is produced and every hard constraint is
honored.

---

## 6. Inherited evidence and governing baselines

These are inherited settled or already-closed surfaces, not reopened here:

- `CDL-066` ratified in Phase `708`
- `CDL-067` ratified in Phase `709`
- `CDL-017` remains open and unratified
- `CDL-068` opened in Phase `736`
- ADR-0019 accepted with scope-limiting amendment in Phase `737`
- ADR-0028 Option D remains the active posture

These are the load-bearing inherited evidence surfaces for Window `739-744`:

- **Row 5 proof surface:** `docs/specs/ilc_row_5_mechanism_proof_mysticeti_697_v0.1.md`
  proves the mechanism over Mysticeti at code-review level and explicitly
  leaves live operator-path leakage measurement as the remaining runtime gap
- **Row 5 observability floor:** `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`
  fixes the machine-legible receipts, receipt lineage, challengeability, and
  bounded human auditability surfaces that the runtime evidence package must
  preserve
- **Row 5 attacker model:** `docs/specs/ilc_row_5_correlation_unlinkability_simulation_packet_681_v0.1.md`
  fixes the operator-path, hosted-query, and repeated-contributor attacker
  variants that `SIM-LEAKAGE-01` must address explicitly
- **Row 5 narrowing lock:** `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
  fixes the narrowed problem statement and names the remaining gap as real
  leakage validation beyond the scenario-model packet
- **Row 7 formal surface:** `docs/specs/ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md`
  gives the bounded TLC proof (`N=4`, `F=1`, `MaxRound=5`, `Liveness`)
  and explicitly leaves live runtime confirmation pending
- **Row 7 and row 8 criteria lock:** `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
  fixes the row-7 censorship and exitability bar and preserves row 8 as an
  inherited selection criterion not advanced by this window
- **Row 7 hard threshold:** `docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md`
  fixes export / verify / replay / migrate without operator consent as the
  non-negotiable bar
- **CDL-068 checklist anchors:**
  - `docs/research/ilc_sim_validator_01_results_v0.1.md`
  - `docs/research/ilc_sim_topology_01_results_v0.1.md`
  - `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
  - `docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md`
  - `docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md`

The window inherits the Window `733-738` closure reading exactly:

- rows `5` and `7` remain `spec_closed_runtime_pending`
- row `8` remains inherited as a closed criteria lock rather than a runtime
  closure lane
- `CDL-068` is open and checklist-complete
- Option B graduation remains deferred to Window `745-748`

---

## 7. Key questions this window must answer honestly

1. What exact live evidence would be sufficient to move row 5 from
   `spec_closed_runtime_pending` to runtime-closed, and which parts of that
   evidence must come from a dedicated leakage-measurement pass on the Gemini
   multi-machine testbed rather than Codex docs work?
2. What exact live evidence would be sufficient to move row 7 from
   `spec_closed_runtime_pending` to runtime-closed, given that the TLC proof
   already exists and that censorship resistance and strong exitability do not
   share the same evidence source?
3. What count as the minimum measurable operator-path leakage surfaces for row 5:
   timing, packet size, validator-host vantage, hosted-query traces, or a
   narrower subset?
4. What count as the minimum runtime scenarios for row 7:
   censoring validator for censorship resistance, export / verify / replay /
   migrate drill for strong exitability, or a stronger bundle?
5. Does this window advance row 8 beyond its inherited criteria-lock posture?
   The default answer in this window should be no.
6. Is `CDL-068` ready for ratification independently of rows 5 and 7?
   The default answer in this window should be yes, provided the Phase 742
   dossier checks every inherited checklist item explicitly.

The window does not need to pretend that Codex alone can generate live
multi-machine evidence. It needs to make the remaining evidence bar explicit
and ratify `CDL-068` honestly.

---

## 8. Required reading before Phase 739 begins

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.1.md`
3. `docs/phases/STATUS.md` (tail)
4. `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
5. `docs/specs/ilc_window_733_738_closure_gate_738_v0.1.md`
6. `docs/specs/ilc_row_5_mechanism_proof_mysticeti_697_v0.1.md`
7. `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`
8. `docs/specs/ilc_row_5_correlation_unlinkability_simulation_packet_681_v0.1.md`
9. `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
10. `docs/specs/ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md`
11. `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
12. `docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md`
13. `docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md`
14. `docs/research/ilc_sim_validator_01_results_v0.1.md`
15. `docs/research/ilc_sim_topology_01_results_v0.1.md`
16. `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
17. `docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md`
18. `docs/specs/ilc_m_series_test_coverage_and_hardening_plan_v0.1.md`
19. `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

---

## 9. GO Phase 739 required

Window 739-744 includes CDL-068 ratification (Phase 743), which mutates the
constitutional decision log. An explicit GO Phase 739 from the architectural
reviewer is required before packet drafting begins.

This guidance doc is the basis for that review. The GO gate is satisfied when
the reviewer confirms the window scope, hard constraints, and Q1-Q5
resolutions above are acceptable.

---

## 10. Track B line at window open

From `docs/phases/STATUS.md` tail (verified 2026-04-20):

> **Current:** M-018 (Workload F: Bounded Public Auditability) complete. `run_m018_workload_f_verdict=pass`  
> **Next planned phase:** M-019 (Adversarial Hardening and Byzantine Fault Simulation)

---

## 11. Closure-gate selftest chain note

The closure-gate selftest chain extends from:

- `ILC_PHASE_738_GATE_SELFTEST=1`

to:

- `ILC_PHASE_744_GATE_SELFTEST=1`

As with Phase 738, the Phase 744 packet should read the actual prior closure
gate test file and extend the chain directly rather than reasoning by analogy.
