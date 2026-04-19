# ILC Phase 733-738 Sequence Lock v0.1

**Phase:** 733  
**Window:** 733-738  
**Date:** 2026-04-19  
**Author:** Codex

`window_733_738_sequence_lock_active`

## 1. Baseline

Window `727-732` is closed. Capsule `v5.0` is the live main-lane frontier at
sequence-lock time. `CDL-017` remains open and unratified. `CDL-068` is not yet
open at sequence-lock time and is routed to Phase `736` in this window. Rows
`5` and `7` remain `spec_closed_runtime_pending` and are not closed by this
window.

Track B was re-read from `docs/phases/STATUS.md` tail at execution time rather
than copied from memory or an older capsule. The live tail states:

- `**Current:** M-017 (Workload E: Validator Operability) complete natively.`
- `**Next planned phase:** M-018 (Workload F: Bounded Public Auditability)`

`track_b_m017_complete_m018_next`

## 2. Inherited gates and constraints

This window inherits the closed-state boundary from Phase `732`, the 701+
carry-forward program, and the approved `733-738` packet:

- `CDL-017` remains open and may not be ratified in this window,
- no CDL ratification is planned anywhere in Window `733-738`,
- `CDL-068` is the next fresh CDL number and may only be opened in Phase `736`,
- ADR-0019 remains `Proposed` at window entry and requires explicit disposition
  in Phase `737`,
- validation pools remain outside `CDL-017` core and outside this window,
- rows `5` and `7` remain runtime-pending and are carried forward to Window
  `739-744`,
- Track B progress is parallel and informative, not a blocker for opening this
  window,
- no `ilc_core/` or `ilc_consensus/` mutation is authorized in the Codex main
  lane for this packet,
- no statement in this window may claim that the Q1-Q6 answers were originated
  here; they were settled before this phase and are imported here.

## 3. Pre-window conversation record (Q1–Q6)

The pre-window conversation record for 2026-04-19 is complete and is imported
here without reinterpretation.

`pre_window_conversation_record_complete_2026_04_19`

- Q1 = derived sub-key with governance-internal linkage (not publicly
  inferrable; CDL-017 text must include this qualifier explicitly).
- Q2 = SIM-VALIDATOR-01 must demonstrate equivocation rendered economically
  irrational (numeric threshold from SIM).
- Q3 = new CDL for topology shuffle authorization, not CDL-039 amendment.
- Q4 = validation pools are separate CDL scope, not CDL-017.
- Q5 = epoch-hash for mainnet v1 with explicit VRF upgrade forward obligation
  at named validator-count threshold (SIM-VALIDATOR-01 to supply the number,
  targeting >=10 independent validators or first non-genesis admission).
- Q6 = metric definition locked (`validator_cluster_id`), numeric thresholds
  deferred to SIM-TOPOLOGY-01.

Q1 drafting note, carried verbatim into this lock:

> the derivation relationship is assertable to the governance mechanism during
> admission — it is not required to be publicly inferrable from either key
> alone

Q5 drafting note, carried verbatim into this lock:

> epoch-hash is the production v1 randomness source for topology shuffle; a VRF
> upgrade is constitutionally mandatory when the active validator set exceeds
> [SIM-VALIDATOR-01 threshold, targeting >=10 independent validators or first
> non-genesis admission, whichever comes first]

## 4. Window meaning

Window `733-738` is the CDL-017 prelock evidence window.

`cdl_017_prelock_window_active`
`no_cdl_017_ratification_in_window_733_738`
`cdl_068_opens_this_window`
`sim_validator_01_commissioned_phase_711`
`sim_topology_01_commissioned_phase_711`

This window exists to produce the Codex-side constitutional evidence required
before `CDL-017` can later be ratified in the Mysticeti convergence window.
It is authorized to:

1. lock the six-phase order for the prelock evidence lane,
2. import the settled Q1-Q6 answers into the active sequence lock,
3. execute `SIM-VALIDATOR-01` for stake-floor calibration,
4. execute `SIM-TOPOLOGY-01` for topology and Q6 threshold evidence,
5. open `CDL-068` as the topology-shuffle authorization lane in Phase `736`,
6. update the validator-agent prelock evidence artifact and dispose of ADR-0019,
7. close the window with coherence, capsule `v5.1`, and a closure gate.

This window does not ratify `CDL-017`. It does not ratify `CDL-068`. It does
not select final Option B production posture. It does not mutate `ilc_core/` or
`ilc_consensus/` in the Codex main lane.

## 5. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 733 | sequence lock + Q1-Q6 record import | gate / constitutional planning |
| 2 | 734 | SIM-VALIDATOR-01 stake floor calibration | simulation / evidence |
| 3 | 735 | SIM-TOPOLOGY-01 topology shuffle sizing | simulation / evidence |
| 4 | 736 | CDL-068 topology shuffle authorization opening | constitutional opening |
| 5 | 737 | CDL-017 prelock evidence artifact update + ADR-0019 disposition | evidence / documentation |
| 6 | 738 | coherence report + capsule v5.1 + closure gate | gate / handoff |

Sequencing rules:

- Phase `733` opens the window but does not mutate the CDL register,
- Phases `734-735` may execute evidence work but may not mutate the CDL register,
- only Phase `736` may open `CDL-068`,
- Phase `737` assembles prelock evidence but does not ratify `CDL-017`,
- Phase `738` is the closure gate and must summarize only what Phases
  `733-737` actually established,
- if `SIM-TOPOLOGY-01` is only partial-complete in Phase `735`, the unresolved
  Q6 threshold derivation must be carried honestly into Window `739`.

Phase `738` is the closure gate for the window.

## 6. Explicit separation obligations

This window must preserve six non-conflation boundaries:

1. `CDL-017` prelock evidence is not `CDL-017` ratification.
2. `CDL-068` is a separate constitutional lane from `CDL-039`; topology
   assignment is not transport-envelope law.
3. Validation pools remain outside `CDL-017` and are routed to a later
   separate CDL.
4. Q5 settles mainnet-v1 epoch-hash posture without claiming that production
   VRF is abandoned; the VRF upgrade obligation remains live.
5. Rows `5` and `7` runtime-form work remain separate carry-forward for Window
   `739-744`.
6. Track B progress toward `M-018` does not collapse the boundary between the
   Codex constitutional lane and the Gemini implementation lane.

The Codex lane in this window is documentation, simulation evidence, and
constitutional preparation only. No hidden runtime implementation is authorized
by sequence-lock rhetoric.

## 7. Non-goals

This window does not include:

- any ratification of `CDL-017`,
- any ratification of `CDL-068`,
- any decision-log mutation in Phase `733`,
- any mutation of `ilc_core/` or `ilc_consensus/`,
- any claim that Q1-Q6 were newly resolved in this phase,
- any inclusion of validation pools inside `CDL-017`,
- any final Option B graduation claim,
- any claim that rows `5` or `7` runtime work is complete,
- any requirement to wait for `M-018` before the main lane proceeds.

## 8. Source inputs

The authoritative source set for this sequence lock is:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_window_727_732_closure_gate_732_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.0.md`
- `docs/specs/ilc_window_733_738_candidate_phase_grouping_v0.1.md`
- `docs/research/ilc_codex_lane_window_plan_733_plus_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
- `docs/specs/ilc_sim_validator_01_commissioning_711_v0.1.md`
- `docs/specs/ilc_sim_topology_01_commissioning_711_v0.1.md`
- `docs/phases/STATUS.md`

This sequence lock remains active until Phase `738` closes Window `733-738`.
