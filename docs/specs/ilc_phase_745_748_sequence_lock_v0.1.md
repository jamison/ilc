# ILC Phase 745-748 Sequence Lock v0.1

**Phase:** 745  
**Window:** 745-748  
**Date:** 2026-04-20  
**Author:** Codex

`window_745_748_sequence_lock_active`

## 1. Baseline

Window `739-744` is closed. Capsule `v5.2` is the frozen main-lane frontier at
sequence-lock time. `CDL-017` remains open and unratified. Rows `5` and `7`
remain `spec_closed_runtime_pending`. Row `8` remains an inherited criteria
lock and is not a runtime-confirmation lane in this window. ADR-0028 still
leaves Option D as the active settlement posture at window open.

Track B was re-read from `docs/phases/STATUS.md` tail at execution time rather
than copied from memory or from the now-stale Track B line inside capsule
`v5.2`. The live tail states:

- `**Current:** M-019 (Adversarial Hardening and Byzantine Fault Simulation) complete. run_m019_adversarial_hardening_verdict=pass`
- `**Next planned phase:** M-020 (External Security Audit Preparation)`

`track_b_m019_complete_m020_next`

## 2. Inherited gates and constraints

This window inherits the closed-state boundary from Phase `744`, the 701+
carry-forward program, ADR-0028, and the approved `745-748` guidance:

- `CDL-017` remains open and may not be ratified in this window,
- rows `5` and `7` may not move to `runtime_closed` in this window,
- row `8` remains inherited and is not reopened here,
- Option B graduation remains deferred until the later convergence window,
- no sovereign substrate selection is authorized in this window,
- no `ilc_core/` or `ilc_consensus/` mutation is authorized in the Codex main
  lane for this packet,
- Track B progress is informative for convergence-window entry conditions but
  does not authorize invented runtime evidence in the Codex lane,
- convergence-window entry conditions must bind to committed artifacts rather
  than assumed Gemini phase labels,
- uncommitted working-tree drafts do not satisfy any convergence-window entry
  condition.

## 3. Window meaning

Window `745-748` is the convergence-window commissioning and planning-surface
advance window.

`convergence_window_commissioning_window_active`
`convergence_window_artifact_gated_entry_required`
`adr_0031_housekeeping_acceptance_authorized_in_window_745_748`
`rows_5_and_7_remain_spec_closed_runtime_pending_at_window_open`
`no_cdl_017_ratification_in_window_745_748`
`no_option_b_graduation_in_window_745_748`
`no_legal_facts_annex_in_window_745_748`

This window exists to:

1. lock the four-phase order for the convergence-window commissioning lane,
2. publish the bounded commissioning spec for the later Mysticeti convergence
   window,
3. advance ADR-0031 from `Proposed` to `Accepted` if the repo still supports
   the housekeeping-only reading,
4. publish the planning-surface advance to capsule `v5.3`, roadmap `v0.4`,
   and an updated `PLANNING_INDEX.md`,
5. close the window with coherence and a closure gate that preserves every
   non-closure honestly.

This window does not close row `5`, row `7`, or row `8`. It does not ratify
`CDL-017`. It does not graduate Option B. It does not publish the deferred
legal positioning technical facts annex.

## 4. Convergence-window commissioning posture at open

The convergence window commissioned by this packet is a later bounded window.
It does not open at Phase `745`; it is only defined here.

`convergence_window_not_open_at_phase_745`
`convergence_window_requires_three_committed_artifact_classes`

The convergence window may close:

- row `5` runtime closure using committed `SIM-LEAKAGE-01` results,
- row `7` censorship-resistance runtime closure using a committed Gemini live
  artifact bundle that satisfies the Phase `741` Section `3.2` contract,
- row `7` strong-exitability closure using committed export / verify / replay /
  migrate evidence,
- row `8` disposition,
- Option B graduation-gate synthesis under ADR-0028.

The convergence window does not open until **all three** committed artifact
classes exist:

1. a committed Gemini runtime artifact bundle satisfying the Phase `741`
   Section `3.2` censorship-resistance contract,
2. a committed `SIM-LEAKAGE-01` results artifact for row `5`, and
3. a committed Gemini strong-exitability drill results artifact.

If Gemini later packages these as `M-020`, `M-021`, `M-022`, or under different
phase numbers, the artifact bundle controls. The numeric label does not.

At sequence-lock time, none of those entry classes are yet authoritative for
main-lane use because the live authority order still points to `STATUS.md`
tail, capsule `v5.2`, and the Phase `744` closure gate. Any uncommitted
Gemini worktree draft remains below that authority threshold and therefore does
not satisfy convergence entry.

## 5. ADR-0031 housekeeping posture at open

ADR-0031 enters this window as a housekeeping-only candidate rather than as a
live implementation gate.

`adr_0031_proto_contract_already_present`
`adr_0031_acceptance_requires_no_new_runtime_work`

The repo already contains the required proto contract in
`ilc_consensus/proto/ilc_app.proto`:

- `repeated EdgeRecord edges = 2;`
- `repeated HyperEdgeRecord hyperedges = 3;`
- `message EdgeRecord { ... }`
- `message HyperEdgeRecord { ... }`

Phase `746` may therefore accept ADR-0031 only if re-reading the ADR confirms
that no additional implementation work, wire-format change, or runtime mutation
is still missing. If that re-read reveals a residual implementation gap, the
honest result is to preserve `Status: Proposed`.

## 6. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 745 | sequence lock | gate / planning |
| 2 | 746 | convergence-window commissioning spec + ADR-0031 housekeeping check | planning + ADR housekeeping |
| 3 | 747 | capsule v5.3 + roadmap v0.4 + planning index advance | planning-surface advance |
| 4 | 748 | coherence report + closure gate | gate / handoff |

Sequencing rules:

- Phase `745` opens the window but does not mutate the decision log,
- Phase `746` may publish the commissioning spec and may mutate ADR-0031 only
  if the change is doc-only housekeeping,
- Phase `747` advances planning surfaces but may not claim any row closure,
  `CDL-017` ratification, or Option B graduation,
- Phase `748` is the closure gate for the window and must summarize only what
  Phases `745-747` actually established.

Phase `748` is the closure gate for the window.

## 7. Explicit separation obligations

This window must preserve seven non-conflation boundaries:

1. convergence-window commissioning is not convergence-window execution,
2. row `5` still pending `SIM-LEAKAGE-01` execution is not row `5`
   runtime-closure,
3. row `7` still pending censorship and exitability artifacts is not row `7`
   runtime-closure,
4. planning-surface advance is not constitutional ratification,
5. ADR-0031 housekeeping acceptance is not new runtime or wire-format work,
6. Option B graduation-gate planning is not Option B graduation,
7. uncommitted Gemini drafts are not authoritative convergence-entry
   artifacts.

The Codex lane in this window is planning and ADR housekeeping only. No hidden
runtime closure or hidden constitutional ratification is authorized by
sequence-lock rhetoric.

## 8. Non-goals

This window does not include:

- any ratification of `CDL-017`,
- any move of row `5` to `runtime_closed`,
- any move of row `7` to `runtime_closed`,
- any runtime confirmation or advancement of row `8`,
- any sovereign substrate selection,
- any Option B graduation claim,
- the deferred legal positioning technical facts annex,
- any mutation of `ilc_core/` or `ilc_consensus/`,
- any attempt to treat uncommitted Gemini `M-020+` drafts as authoritative
  entry artifacts,
- any decision-log mutation in Phase `745`.

## 9. Source inputs

The authoritative source set for this sequence lock is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.2.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md`
- `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
- `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
- `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `ilc_consensus/proto/ilc_app.proto`
- `docs/specs/ilc_window_745_748_guidance_v0.1.md`

This sequence lock remains active until Phase `748` closes Window `745-748`.
