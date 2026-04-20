# ILC Phase 739-744 Sequence Lock v0.1

**Phase:** 739  
**Window:** 739-744  
**Date:** 2026-04-20  
**Author:** Codex

`window_739_744_sequence_lock_active`

## 1. Baseline

Window `733-738` is closed. Capsule `v5.1` is the live main-lane frontier at
sequence-lock time. `CDL-017` remains open and unratified. `CDL-068` is
already open and unratified at window entry. Rows `5` and `7` remain
`spec_closed_runtime_pending`. Row `8` remains an inherited criteria lock and
is not a runtime-confirmation lane in this window. ADR-0028 still leaves
Option D as the active settlement posture at window open.

Track B was re-read from `docs/phases/STATUS.md` tail at execution time rather
than copied from memory or from the now-stale Track B line inside capsule
`v5.1`. The live tail states:

- `**Current:** M-018 (Workload F: Bounded Public Auditability) complete. run_m018_workload_f_verdict=pass`
- `**Next planned phase:** M-019 (Adversarial Hardening and Byzantine Fault Simulation)`

`track_b_m018_complete_m019_next`

## 2. Inherited gates and constraints

This window inherits the closed-state boundary from Phase `738`, the 701+
carry-forward program, ADR-0028, and the approved `739-744` guidance:

- `CDL-017` remains open and may not be ratified in this window,
- `CDL-068` is the only CDL authorized for ratification in this window,
- rows `5` and `7` may advance only through honest runtime-evidence packaging
  unless live multi-machine evidence actually exists,
- row `8` remains inherited and is not reopened here,
- no sovereign substrate selection is authorized in this window,
- no wallet widening is authorized in this window,
- Option B graduation remains deferred to Window `745-748`,
- no `ilc_core/` or `ilc_consensus/` mutation is authorized in the Codex main
  lane for this packet,
- Track B progress is informative for rows `5` and `7` but does not authorize
  invented runtime evidence in the Codex lane.

## 3. Window meaning

Window `739-744` is the MVP-gate runtime-form and `CDL-068` ratification
window.

`rows_5_and_7_runtime_form_window_active`
`row_5_runtime_evidence_packaging_window_active`
`row_7_runtime_evidence_packaging_window_active`
`rows_5_and_7_remain_spec_closed_runtime_pending_at_window_open`
`no_cdl_017_ratification_in_window_739_744`

This window exists to:

1. lock the six-phase order for the rows-5-and-7 runtime-form lane,
2. formalize the row-5 live operator-path leakage evidence requirements,
3. formalize the row-7 live censorship-resistance evidence requirements and the
   separate strong-exitability drill requirements,
4. assemble the formal `CDL-068` ratification dossier from already-complete
   checklist evidence,
5. ratify `CDL-068` without waiting on row-5 / row-7 runtime closure,
6. close the window with coherence, capsule `v5.2`, and a closure gate.

This window does not close row `5` or row `7` by rhetoric alone. It does not
ratify `CDL-017`. It does not select sovereign substrate posture. It does not
mutate runtime code in the Codex main lane.

## 4. Row 5 and Row 7 runtime posture at open

Row `5` enters this window from Phase `697` as:

- `row_5_post_697_status=spec_closed_runtime_pending`
- concrete mechanism proof over Mysticeti is complete,
- the remaining gap is live operator-path leakage measurement on a
  multi-machine validator network,
- that measurement must stay inside the already-locked row-5 narrowing:
  correlation minimization and unlinkability, not blanket secrecy,
- the public-legitimacy observability floor must remain intact while the
  runtime evidence package is written.

Row `7` enters this window from Phase `698` and Phase `674` as:

- `row_7_post_698_status=spec_closed_runtime_pending`
- TLC proof exists for `N=4`, `F=1`, `MaxRound=5`, and `Liveness`,
- the remaining gap splits into two distinct runtime proof obligations:
  censorship resistance and strong exitability,
- censorship-resistance runtime confirmation may use Gemini `M-019`
  censoring-validator evidence,
- strong exitability still means export, independent verify, replay, and
  migrate without privileged original-operator consent,
- strong exitability does not share the same evidence source as `M-019` and
  requires a separate export / verify / replay / migrate drill,
- the runtime evidence package must connect the bounded formal proof to live
  validator behavior rather than claim the proof alone closes the row.

If live Gemini censorship evidence or a separate strong-exitability drill is
not present during Phases `740-741`, the honest result is commissioning /
evidence-package completion only. The status label remains
`spec_closed_runtime_pending` until live runtime evidence actually exists.

## 5. CDL-068 ratification posture at open

`CDL-068` enters this window open, checklist-complete, and eligible for
ratification.

`cdl_068_evidence_checklist_complete_at_window_open`
`cdl_068_ratification_authorized_in_window_739_744`
`cdl_068_ratification_independent_of_rows_5_and_7_runtime_closure`

The inherited checklist is complete because:

1. `SIM-TOPOLOGY-01` completed in Phase `735` with `recommended_k_degree 4`,
   cadence `1`, fanout `3`,
   `distinct_cluster_floor_recommendation 4`, and
   `max_cluster_share_ceiling_recommendation 33`,
2. `SIM-VALIDATOR-01` completed in Phase `734` with
   `vrf_upgrade_threshold_validator_count 10` and
   `stake_floor_candidate_interval_micro_ecu 400000000-450000000`,
3. the `CDL-017` prelock artifact update exists after Phase `737`,
4. the CDL-039 boundary note already fixes the non-overlap between transport
   contract law and topology-assignment law.

Phase `743` may therefore ratify `CDL-068`, but it must still explicitly check
all six inherited prelock criteria from the Phase `736` opening:

1. separate constitutional lane from both `CDL-039` and `CDL-017`,
2. epoch-hash v1 remains acceptable only with a VRF upgrade obligation at `10`
   active validators,
3. bounded path remains `k=4`, per-epoch cadence, and bounded push fanout `3`,
4. validator composition uses explicit `validator_cluster_id`,
5. Q6 thresholds remain tied to the Phase `735` evidence floor and ceiling,
6. the Phase `737` prelock artifact update exists and is cited directly.

The Phase `743` ratification must also preserve the established constitutional
mutation discipline:

- commit 1 publishes the ratification artifact, evidence-checklist
  satisfaction record, and tests,
- commit 2 mutates exactly the `CDL-068` row in
  `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- no other decision-log row may change in the ratification commit.

## 6. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 739 | sequence lock | gate / constitutional planning |
| 2 | 740 | row-5 runtime evidence package + `SIM-LEAKAGE-01` commissioning spec | runtime-form packaging |
| 3 | 741 | row-7 runtime evidence package | runtime-form packaging |
| 4 | 742 | `CDL-068` ratification-readiness dossier | constitutional evidence assembly |
| 5 | 743 | `CDL-068` ratification | constitutional ratification |
| 6 | 744 | coherence report + capsule v5.2 + closure gate | gate / handoff |

Sequencing rules:

- Phase `739` opens the window but does not mutate the decision log,
- Phases `740-742` may publish evidence packages and dossier material but may
  not mutate the decision log,
- only Phase `743` may mutate the decision log, and only for the `CDL-068`
  ratification row update in a dedicated second commit,
- Phases `740-741` may close on commissioning posture if live Gemini
  censorship evidence, dedicated leakage measurement, or a separate
  exitability drill is not yet present,
- Phase `744` is the closure gate for the window and must summarize only what
  Phases `739-743` actually established.

Phase `744` is the closure gate for the window.

## 7. Explicit separation obligations

This window must preserve six non-conflation boundaries:

1. row-5 runtime evidence packaging is not row-5 runtime closure,
2. row-7 runtime evidence packaging is not row-7 runtime closure,
3. `CDL-068` ratification is not `CDL-017` ratification,
4. `CDL-068` topology-assignment law is not `CDL-039` transport-envelope law,
5. runtime-form work for rows `5` and `7` is not sovereign-substrate
   selection or Option B graduation,
6. row `8` inherited criteria lock is not a runtime-closure target in this
   window,
7. Gemini-side live evidence may inform this window but cannot be invented or
   implied by Codex documentation alone.

The Codex lane in this window is constitutional ratification work and honest
runtime-evidence packaging only. No hidden runtime closure is authorized by
sequence-lock rhetoric.

## 8. Non-goals

This window does not include:

- any ratification of `CDL-017`,
- any sovereign substrate selection,
- any wallet widening,
- any claim that row `5` is runtime-closed without live operator-path
  measurement,
- any claim that row `7` is runtime-closed without live censorship-and-exitability
  confirmation,
- any claim that row `8` was advanced or runtime-confirmed in this window,
- any mutation of `ilc_core/` or `ilc_consensus/`,
- any claim that Option B graduation occurs in Window `739-744`,
- any decision-log mutation in Phase `739`.

## 9. Source inputs

The authoritative source set for this sequence lock is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.1.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
- `docs/specs/ilc_window_733_738_closure_gate_738_v0.1.md`
- `docs/specs/ilc_window_739_744_guidance_v0.1.md`
- `docs/specs/ilc_row_5_mechanism_proof_mysticeti_697_v0.1.md`
- `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`
- `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
- `docs/specs/ilc_row_5_correlation_unlinkability_simulation_packet_681_v0.1.md`
- `docs/specs/ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md`
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md`
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md`
- `docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md`
- `docs/research/ilc_sim_topology_01_results_v0.1.md`
- `docs/research/ilc_sim_validator_01_results_v0.1.md`
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`

This sequence lock remains active until Phase `744` closes Window `739-744`.
