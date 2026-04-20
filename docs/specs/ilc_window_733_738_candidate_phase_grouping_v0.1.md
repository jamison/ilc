# ILC Window 733-738: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)  
**Date:** 2026-04-19  
**Baseline:** Window 727-732 CLOSED (Phase 732 closure gate). CDL-066 ratified Phase 708, CDL-067 ratified Phase 709. CDL-017 open and unratified. Capsule v5.0 current.  
**Pre-window conversation:** COMPLETE (2026-04-19) — Q1–Q6 all answered and locked in `docs/research/ilc_codex_lane_window_plan_733_plus_v0.1.md` §1.  
**Planning note:** This is a candidate grouping, not yet a locked sequence. Phases 733–737 are the hard minimum lane. Phase 738 is the closure gate. SIM-TOPOLOGY-01 execution (Phase 735) may spill partial results into Window 739 if the graph simulation requires extended runs; Phase 738 closure gate language must be drafted to accommodate this scenario.

---

## 1. Window Identity and Scope

Window `733-738` is the **CDL-017 prelock evidence window**. Its strategic purpose is to produce the complete Codex-side half of the CDL-017 ratification prerequisite:

- the six constitutional questions answered and locked (done in pre-window conversation),
- both SIMs commissioned in Phase 711 now executed and results committed,
- a new CDL (CDL-068) opened for topology shuffle authorization,
- the prelock evidence artifact updated with Q1–Q6 answers mapped to prelock checklist,
- ADR-0019 given an explicit accepted/amended/rejected disposition,
- a capsule (v5.1) reflecting all of the above.

**CDL-017 is not ratified in this window.** Ratification requires the Gemini M-022 handoff package, which is not yet available. This window produces the Codex-side prelock evidence only.

**Tail-slot policy:** All six phases are firm. There are no conditional tail slots in this window — the scope is well-bounded by the pre-window conversation. If SIM-TOPOLOGY-01 does not complete fully in Phase 735, the Phase 738 closure gate must name the partial results honestly and forward the outstanding threshold derivation to Window 739.

---

## 2. Baseline and Inheritance

### Ratified CDL chain (relevant)

| CDL | Title summary | Ratified |
|---|---|---|
| CDL-055 | Validator slash policy | Phase 496 |
| CDL-056 | Validator trust-tier elevation | Phase 501 |
| CDL-063 | Directed-commission earmark + bounded debit | Phase 628 |
| CDL-064 | Tier-0 exact numeric determinism | Phases 631-641 |
| CDL-066 | Agent sender authentication | Phase 708 |
| CDL-067 | Settlement-state CDL | Phase 709 |

### Active runtime chain (Codex Python track)

No `ilc_core/` or `ilc_consensus/` mutation is planned in this window. The Codex main-lane code write authority for `ilc_core/` is deferred to the Mysticeti convergence window. All Codex deliverables in Window 733-738 are documentation, simulation evidence, and constitutional artifacts.

### Track B (Gemini Rust lane)

Read `docs/phases/STATUS.md` tail at sequence-lock time and cite it exactly. At guidance-authoring time the expected tail is:

```
M-016 COMPLETE — Workload D: replayability and state extraction (run_m016_workload_d_verdict=pass)
M-017 IN PROGRESS or COMPLETE — Workload E: validator operability
Next: M-018 (Workload F: bounded public auditability + gRPC)
```

Do not wait for M-017 or M-018 completion before opening Window 733-738.

### Inherited open items requiring carry-forward citation in sequence lock

- `CDL-017` — open, unratified (primary subject of this window's prelock work)
- `CDL-068` — new, to be opened in Phase 736
- ADR-0019 — Proposed, requires explicit disposition in Phase 737
- ADR-0029 / ADR-0030 / ADR-0031 — Proposed, morphogenetic research lane; post-mainnet except ADR-0031 proto gate (already satisfied — `EdgeRecord` and `HyperEdgeRecord` added to `ilc_consensus/proto/ilc_app.proto`)
- MVP gate rows 5 + 7 — `spec_closed_runtime_pending`; deferred to Window 739-744
- `testnet_fault_sim` feature gate in node.rs — pre-M-019 item, not this window
- TLA-PRE-1 (MaxRound widening) — pre-RC item, not this window
- Legal positioning memo — carry-forward only, not a gate (Phase 687-692 sequence lock explicit)

### Next fresh CDL number

CDL-067 is the most recently ratified CDL. CDL-068 is next available and is assigned to topology shuffle authorization in Phase 736.

---

## 3. Track Inventory

### 3.1 Constitutionally obligated (this window)

| Item | Source obligation |
|---|---|
| Execute SIM-VALIDATOR-01 | Commissioned Phase 711; numeric stake floor required before CDL-017 numeric prelock |
| Execute SIM-TOPOLOGY-01 | Commissioned Phase 711; topology shuffle Q6 thresholds and CDL-068 evidence basis |
| Open CDL-068 | Q3 settled (2026-04-19): new CDL for topology shuffle authorization, not CDL-039 amendment |
| Update prelock evidence artifact | Phase 710 artifact needs Q1–Q6 fully mapped to checklist with 2026-04-19 answers incorporated |
| ADR-0019 disposition | Carry-forward program §4.2 requires explicit accepted/amended/rejected before deeper graph-native governance claims become authoritative |

### 3.2 Deferred governance (not this window)

| Item | Why deferred |
|---|---|
| CDL-017 ratification | Requires Gemini M-022 handoff; convergence window only |
| CDL-068 ratification | Requires SIM-TOPOLOGY-01 full results; may ratify in Window 739 or convergence window |
| MVP gate rows 5 + 7 runtime form | Window 739-744 |
| Option B graduation gate | Window 745-748 |
| Validation pools CDL (Q4) | Separate CDL after CDL-017 ratification |
| VRF upgrade CDL (Q5 follow-on) | Later; triggered at named validator-count threshold |

### 3.3 Simulation-conditional

SIM-TOPOLOGY-01 may not complete fully in Phase 735. The closure gate at Phase 738 must acknowledge this explicitly. If Phase 735 produces only partial connectivity results, Phase 738 closure gate should state: `sim_topology_01_partial_complete_in_733_738` and carry the threshold derivation forward as a named obligation for Phase 739 to satisfy before CDL-068 evidence checklist can be marked complete.

---

## 4. CDL-017 Prelock Evidence Block

The pre-window conversation (2026-04-19) resolved all six constitutional questions. The answers are normative and must appear verbatim in the Phase 733 sequence lock.

### Settled Q1–Q6 record

| Q | Settled answer | Source |
|---|---|---|
| Q1 | Derived sub-key with provable linkage; linkage is governance-internal, not publicly inferrable from either key alone | Phase 710 + 2026-04-19 conversation |
| Q2 | SIM-VALIDATOR-01 numeric output; equivocation must be economically irrational across operating envelope | Phase 710 |
| Q3 | New CDL (CDL-068), not CDL-039 amendment | 2026-04-19 conversation |
| Q4 | Separate subsequent CDL for validation pools, not CDL-017 scope | Phase 710 |
| Q5 | Epoch-hash for mainnet v1; explicit VRF upgrade forward obligation in CDL-017 text at named validator-count threshold | 2026-04-19 conversation |
| Q6 | Metric definition locked (`validator_cluster_id`); numeric thresholds from SIM-TOPOLOGY-01 if full pass — threshold derivation is explicit carry-forward to Window 739 if partial-complete | 2026-04-19 conversation + Phase 735 |

### Q1 drafting note

CDL-017 text must include the explicit qualifier for Q1: "the derivation relationship is assertable to the governance mechanism during admission — it is not required to be publicly inferrable from either key alone." Without this qualifier "provable linkage" could be read as requiring a public cryptographic proof attached to the validator set listing, which would shatter agent pseudonymity and violate CDL-039 cluster-membership-non-inferrable.

### Q5 drafting note

CDL-017 text must include: "epoch-hash is the production v1 randomness source for topology shuffle; a VRF upgrade is constitutionally mandatory when the active validator set exceeds [SIM-VALIDATOR-01 threshold, targeting ≥10 independent validators or first non-genesis admission, whichever comes first]." The threshold numeric is filled in by SIM-VALIDATOR-01 results.

---

## 5. CDL-068: Topology Shuffle Authorization

### Why a new CDL, not CDL-039 amendment

CDL-039 governs the agent gossip *transport* contract — envelope format, opaque channel, cluster-membership-non-inferrable. Topology shuffling for validators is a *constitutional assignment* question: who validates alongside whom, how seats rotate, what diversity constraints apply. These are meaningfully different concerns. An amendment to CDL-039 would (a) blur the transport-vs-constitution boundary, (b) clutter CDL-039's ratification evidence record with validator topology evidence that belongs elsewhere, and (c) create confusion when CDL-039 is cited in future transport audits.

The Phase 711 CDL-039 scope note explicitly said topology shuffling "requires a later named authorization artifact or amendment." CDL-068 is the named artifact.

### CDL-068 scope (opening only — not ratification)

Phase 736 opens CDL-068. Ratification requires SIM-TOPOLOGY-01 full results and happens in Window 739 or the convergence window.

CDL-068 scope:
- randomness source selection for topology shuffles (epoch-hash v1; VRF upgrade trigger)
- k-regular subgraph parameters (degree, shuffle cadence) — derived from SIM-TOPOLOGY-01
- `validator_cluster_id` metric definition and numeric diversity thresholds — derived from SIM-TOPOLOGY-01
- CDL-039 interaction note: CDL-068 governs which validators communicate; CDL-039 governs how they communicate; the two CDLs are complementary, not overlapping

CDL-068 is not the same as CDL-017. CDL-017 covers admission, stake floor, and slash compatibility. CDL-068 covers topology assignment after admission.

---

## 6. CDL Number Assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|---|---|---|---|---|
| CDL-068 | Topology Shuffle Authorization: k-regular assignment, epoch-hash v1, VRF upgrade obligation | `cdl_068_opens_phase_736`, `new_cdl_not_cdl_039_amendment`, `q3_settled_2026_04_19` | Phase 736 | Window 739 or convergence window (pending SIM-TOPOLOGY-01 full results) |

CDL-068 opening is pre-authorized by the Q3 settlement (2026-04-19 pre-window conversation). No further human gate is required before Phase 736 writes the opening document, subject to the GO token at Phase 736 execution time.

---

## 7. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | 733 | Window 733-738 sequence lock + Q1-Q6 record import | Foundation / Constitutional | **SENSITIVE** |
| 2 | 734 | SIM-VALIDATOR-01 execution: stake floor calibration | Simulation | NON-SENSITIVE |
| 3 | 735 | SIM-TOPOLOGY-01 execution: topology shuffle sizing | Simulation | NON-SENSITIVE |
| 4 | 736 | CDL-068 opening: topology shuffle authorization | Constitutional | **SENSITIVE** |
| 5 | 737 | CDL-017 prelock evidence artifact update + ADR-0019 disposition | Constitutional | NON-SENSITIVE |
| 6 | 738 | Coherence report + capsule v5.1 + closure gate 738 | Gate | **SENSITIVE** |

### Note on Phase 735 partial-completion scenario

If SIM-TOPOLOGY-01 requires extended graph simulation runs that cannot complete within a single phase execution, Phase 735 must commit partial results with an honest partial-completion token (`sim_topology_01_partial_complete_in_phase_735`) and Phase 738 closure gate must record this as a named carry-forward. The Q6 numeric threshold derivation is then the first obligation for Window 739. Phase 736 CDL-068 opening may proceed after Phase 735 commits partial results, as long as the opening document explicitly states that the evidence checklist is incomplete pending full SIM-TOPOLOGY-01 results.

### Note on Phase 733 non-ratifying boundary

Phase 733 sequence lock is a documentation-only commit. It must not open or ratify any CDL, must not mutate `ilc_core/` or `ilc_consensus/`, and must not claim that Q1–Q6 are newly resolved — they were resolved in the pre-window conversation and the sequence lock imports those answers, not originates them.

---

## 8. Sensitivity Classification

### SENSITIVE phases

- **Phase 733** — sequence lock publication; structural boundary that fixes the window ordering and imports constitutional conversation record
- **Phase 736** — CDL-068 opening; CDL mutation (opening new CDL number is a CDL register mutation)
- **Phase 738** — closure gate; structural boundary that closes the window and carries forward to Window 739

### NON-SENSITIVE phases

- **Phase 734** — simulation execution; no CDL mutation, no ilc_core/ mutation, outputs are evidence files only
- **Phase 735** — simulation execution; same as Phase 734
- **Phase 737** — prelock evidence artifact update and ADR-0019 disposition; no CDL mutation (CDL-017 is not ratified here); ADR disposition is a documentation commit

### Pre-commit hook requirement

Phases requiring `ILC_CDL_MUTATION_AUTHORIZED=1`:
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=736
```
Phase 736 only. Phase 733 sequence lock and Phase 738 closure gate are structural commits; confirm with project lead whether they require the CDL mutation hook — in prior windows structural gates have not used the hook (e.g., Phase 727 sequence lock did not mutate the CDL register). If CDL-068 opening is committed in the same commit as any other Phase 736 work, the hook is required.

---

## 9. Scope Notes for Fixed Phases

### Phase 733 — **SENSITIVE** — GO token required: `GO Phase 733`

Deliverables:
- `docs/specs/ilc_phase_733_738_sequence_lock_v0.1.md`
- `tests/test_phase_733_window_733_738_sequence_lock.py`
- `docs/phases/phase_733_g8_window_733_738_sequence_lock_walkthrough.md`
- `docs/phases/STATUS.md` (backfill commit)

Required headings in sequence lock:
1. `## 1. Baseline`
2. `## 2. Inherited gates and constraints`
3. `## 3. Pre-window conversation record (Q1–Q6)`
4. `## 4. Window meaning`
5. `## 5. Phase table and sequencing`
6. `## 6. Explicit separation obligations`
7. `## 7. Non-goals`
8. `## 8. Source inputs`

Required tokens:
- `window_733_738_sequence_lock_active`
- `cdl_017_prelock_window_active`
- `pre_window_conversation_record_complete_2026_04_19`
- `no_cdl_017_ratification_in_window_733_738`
- `cdl_068_opens_this_window`
- `sim_validator_01_commissioned_phase_711`
- `sim_topology_01_commissioned_phase_711`
- `track_b_[read from STATUS.md at execution time]`

The sequence lock must explicitly state: capsule v5.0 is the live frontier; CDL-017 is open and unratified; Q1–Q6 answers are imported from the pre-window conversation and recorded verbatim in §3; CDL-068 will be opened in Phase 736 (not ratified in this window); Phase 738 is the closure gate.

Test structure: pre-main-commit → 6 passed, 2 failed; post-main-commit → 7 passed, 1 failed; post-backfill → 8 passed.

Commit subject:
- Main: `docs(g8): phase 733 window 733-738 sequence lock`
- Backfill: `docs(g8): phase 733 walkthrough and status backfill`

---

### Phase 734 — NON-SENSITIVE

Deliverables:
- `docs/research/ilc_sim_validator_01_results_v0.1.md`
- `simulations/sim_validator_01_stake_floor_calibration.py` (executable simulation)
- `tests/test_phase_734_sim_validator_01_results.py`
- `docs/phases/phase_734_g8_sim_validator_01_stake_floor_calibration_walkthrough.md`
- `docs/phases/STATUS.md` (backfill commit)

Required content in results doc:
- candidate stake-floor interval (not a conversation-picked constant — the output of the sweep)
- payoff curves showing adversary expected value under equivocation across the parameter envelope
- sensitivity table: which parameters move the floor most
- recommended VRF upgrade threshold (validator count) that satisfies Q5 forward obligation
- explicit statement of which assumptions dominate the floor result
- `sim_validator_01_verdict=pass` or `=fail` (fail = any equivocation regime remains non-negative EV at proposed floor, or floor shifts materially under ordinary parameter shifts)

Reference inputs:
- `docs/specs/ilc_sim_validator_01_commissioning_711_v0.1.md` — defines the calibrated question, parameter sweep requirements, and failure criteria
- CDL-055 slash-rate assumptions
- Phase 710 Q2 answer: equivocation must be economically irrational across the agreed operating envelope

The simulation Python file must be deterministic (no `random` or `numpy.random` without fixed seeds). All sweeps must be reproducible from committed inputs.

Test structure: minimum 8 tests — commission brief existence and token presence, results doc required sections, sweep coverage assertions, payoff curve monotonicity, sensitivity table completeness, VRF threshold present and numeric, verdict token present and parseable, simulation file is importable and deterministic.

Commit subject:
- Main: `docs(g8): phase 734 sim-validator-01 stake floor calibration results`
- Backfill: `docs(g8): phase 734 walkthrough and status backfill`

---

### Phase 735 — NON-SENSITIVE

Deliverables:
- `docs/research/ilc_sim_topology_01_results_v0.1.md`
- `simulations/sim_topology_01_topology_shuffle_sizing.py` (executable simulation)
- `tests/test_phase_735_sim_topology_01_results.py`
- `docs/phases/phase_735_g8_sim_topology_01_topology_shuffle_sizing_walkthrough.md`
- `docs/phases/STATUS.md` (backfill commit)

Required content in results doc:
- k-regular subgraph parameters: recommended degree `k` and shuffle cadence
- connectivity results: does the shuffled graph preserve connected communication under worst-case F Byzantine validators?
- privacy results: does the assignment method satisfy CDL-039 cluster-membership-non-inferrable?
- recovery time after shuffle transitions
- Q6 numeric threshold recommendation: `distinct_cluster_floor` and `max_cluster_share_ceiling` values derived from the simulation (not conversation-picked)
- epoch-hash vs VRF comparison — does epoch-hash seeding introduce exploitable manipulation surface at the tested validator-count ranges?
- `sim_topology_01_verdict=pass` or `=partial_complete` (partial-complete = full connectivity and privacy results committed, but Q6 threshold derivation requires additional runs — carry forward to Window 739)

Reference inputs:
- `docs/specs/ilc_sim_topology_01_commissioning_711_v0.1.md` — defines the three calibrated questions, parameter sweep, and failure conditions
- Phase 710 Q6 candidate metric: `validator_cluster_id`, `distinct_cluster_floor = 2` (Phase 710 placeholder — the SIM should validate or revise this)

If the simulation cannot complete in a single phase, commit partial results with token `sim_topology_01_partial_complete_in_phase_735` and explicitly name the remaining work. Phase 736 CDL-068 may still open after partial-complete Phase 735 (see §3.3 tail-slot note).

Test structure: parallel structure to Phase 734 — minimum 8 tests covering commissioning brief token check, results doc sections, connectivity assertion present, privacy assertion present, Q6 thresholds present (or partial-complete token present if not yet derived), verdict token present, simulation file deterministic.

Commit subject:
- Main: `docs(g8): phase 735 sim-topology-01 topology shuffle sizing results`
- Backfill: `docs(g8): phase 735 walkthrough and status backfill`

---

### Phase 736 — **SENSITIVE** — GO token required: `GO Phase 736`

Deliverables:
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md`
- `tests/test_phase_736_cdl_068_opening.py`
- `docs/phases/phase_736_g8_cdl_068_topology_shuffle_authorization_opening_walkthrough.md`
- `docs/phases/STATUS.md` (backfill commit)

CDL-068 opening document required sections:
1. `## 1. Motivation and governing question`
2. `## 2. Scope: what CDL-068 governs`
3. `## 3. Scope: what CDL-068 does not govern (boundary with CDL-039 and CDL-017)`
4. `## 4. Evidence checklist`
5. `## 5. Prelock criteria`
6. `## 6. Non-goals`

Required tokens in opening document:
- `cdl_068_opens_phase_736`
- `new_cdl_not_cdl_039_amendment`
- `topology_shuffle_authorization_separated_from_transport_contract`
- `cdl_068_evidence_checklist_requires_sim_topology_01_results`
- `cdl_068_not_ratified_in_window_733_738`
- `epoch_hash_v1_production_posture_cdl_068_scope`
- `vrf_upgrade_forward_obligation_in_cdl_068`

The opening document must explicitly state the CDL-039 boundary: CDL-039 governs how validators communicate (transport); CDL-068 governs which validators are assigned to communicate with each other (topology). These are complementary and non-overlapping. Any future reading of CDL-039 for topology questions is an error.

Pre-commit hook: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=736`

The CDL register (`docs/specs/ilc_constitutional_decision_log_v0.1.md`) must be updated to add CDL-068 as `status: open` in the main commit.

Test structure: pre-main-commit → 6 passed, 2 failed; post-main-commit → 7 passed, 1 failed; post-backfill → 8 passed.

Commit subject:
- Main: `docs(g8): phase 736 CDL-068 topology shuffle authorization opening`
- Backfill: `docs(g8): phase 736 walkthrough and status backfill`

---

### Phase 737 — NON-SENSITIVE

Deliverables:
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md` (updated — same file, new version increment)
- `docs/specs/ilc_adr_0019_graph_native_governance_boundary_disposition_note_v0.1.md`
- `tests/test_phase_737_cdl_017_prelock_evidence_and_adr_0019_disposition.py`
- `docs/phases/phase_737_g8_cdl_017_prelock_evidence_and_adr_0019_disposition_walkthrough.md`
- `docs/phases/STATUS.md` (backfill commit)

#### Prelock evidence artifact update

The existing `docs/research/ilc_validator_agent_design_evidence_v0.1.md` (Phase 710) records Q1–Q6 answers in table form. Phase 737 must:
- Add a new dated section `## 3. Q1–Q6 answers — 2026-04-19 pre-window conversation` that records the settled answers from the pre-window conversation (Q3, Q5, Q6 specifically — Q1, Q2, Q4 were already present from Phase 710)
- Add a new section `## 4. CDL-017 prelock checklist satisfaction` that maps each Q1–Q6 answer to the corresponding CDL-017 prelock requirement row
- Add SIM-VALIDATOR-01 and SIM-TOPOLOGY-01 result citations (from Phases 734 and 735) into the evidence checklist
- Record the `cdl_017_prelock_evidence_artifact_updated_phase_737` token

The artifact update is additive only — existing Phase 710 sections must not be modified.

Required tokens added in Phase 737:
- `cdl_017_prelock_evidence_artifact_updated_phase_737`
- `q3_q5_q6_settled_2026_04_19_recorded_in_prelock_evidence`
- `sim_validator_01_results_cited_in_prelock_evidence`
- `sim_topology_01_results_cited_in_prelock_evidence`

#### ADR-0019 disposition note

ADR-0019 (`docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md`) has been `Proposed` since 2026-03-18 and is silently relied upon by governance claims in later windows. The carry-forward program §4.2 requires explicit disposition.

The disposition note must:
- state the explicit verdict: `Accepted`, `Accepted with amendment`, or `Rejected`
- if `Accepted`: name the boundary (small audited kernel remains code-resident; which declarative surfaces are graph-compilable) and confirm it is consistent with CDL-017, CDL-066, and ADM-003 v0.2
- name any specific claims from ADR-0019 that are not yet implementable (e.g., graph-native compilation of governance constants requires a later explicit activation CDL)
- state what would trigger revisiting the decision (e.g., a CDL that proposes moving runtime constants into graph-native form)
- record `adr_0019_disposition_complete_phase_737`

My bias: ADR-0019 should be `Accepted` with a scope-limiting amendment that makes explicit: graph-native compilation of governance constants is the *long-horizon direction*, not a currently authorized action. No production governance constant may be moved to graph-native form without a dedicated CDL ratification. The ADR's kernel boundary section is sound as written.

Commit subject:
- Main: `docs(g8): phase 737 CDL-017 prelock evidence artifact update and ADR-0019 disposition`
- Backfill: `docs(g8): phase 737 walkthrough and status backfill`

---

### Phase 738 — **SENSITIVE** — GO token required: `GO Phase 738`

Deliverables:
- `docs/specs/ilc_coherence_report_phase_738_window_733_738_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.1.md`
- `docs/specs/ilc_window_733_738_closure_gate_738_v0.1.md`
- `tests/test_phase_738_window_733_738_closure_gate.py`
- `docs/phases/phase_738_g8_coherence_report_capsule_v5_1_and_window_733_738_closure_gate_walkthrough.md`
- `docs/phases/STATUS.md` (backfill commit)

#### Coherence report requirements

The coherence report must assert:
- No CDL-017 ratification occurred in Window 733-738
- CDL-068 was opened in Phase 736 (not ratified)
- SIM-VALIDATOR-01 verdict (from Phase 734 results)
- SIM-TOPOLOGY-01 verdict (from Phase 735 results — `pass` or `partial_complete`)
- Prelock evidence artifact updated in Phase 737
- ADR-0019 disposition recorded in Phase 737
- Track B status at closure (read STATUS.md tail)
- All six constitutional questions settled; citations to pre-window conversation record in sequence lock

#### Capsule v5.1 requirements

Capsule v5.1 supersedes v5.0. It must:
- inherit all §1–§4 content from v5.0 and update only what changed
- add new §: "Window 733-738 closure summary" naming each phase and its key output
- record SIM-VALIDATOR-01 stake floor candidate interval
- record SIM-TOPOLOGY-01 connectivity and diversity metric outputs (full or partial-complete)
- record CDL-068 as open
- record ADR-0019 as disposed
- update the roadmap gap table: Gap 1 (CDL-017) status from `OPEN` to one of:
  - `PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE_733_738` (if SIM-TOPOLOGY-01 full pass)
  - `PRELOCK_EVIDENCE_ADVANCED_CODEX_SIDE_733_738_Q6_CARRY_FORWARD` (if partial-complete)
  The capsule must not use the full-pass label if Phase 737 emitted the carry-forward token.

#### Closure gate requirements

The closure gate must explicitly state:
- `window_733_738_closure_gate_pass` (or `window_733_738_closure_gate_partial_pass` if SIM-TOPOLOGY-01 partial-complete)
- Exactly one of (matching Phase 737 artifact):
  - `cdl_017_prelock_codex_side_complete` — only if SIM-TOPOLOGY-01 full pass
  - `cdl_017_prelock_codex_side_advanced_with_carry_forward` — if partial-complete
- If SIM-TOPOLOGY-01 partial-complete: `sim_topology_01_threshold_derivation_carry_forward_to_739`
- Carry-forward to Window 739: rows 5 + 7 runtime form; CDL-068 ratification evidence; any remaining SIM-TOPOLOGY-01 threshold derivation; stronger replayability proof

Commit subject:
- Main: `docs(g8): phase 738 capsule v5.1 and window 733-738 closure gate`
- Backfill: `docs(g8): phase 738 walkthrough and status backfill`

---

## 10. Key Dependencies and Open Questions

### Must resolve at window entry

- STATUS.md tail must be read at Phase 733 execution time (Track B)
- SIM-VALIDATOR-01 commission brief (`ilc_sim_validator_01_commissioning_711_v0.1.md`) must be confirmed present before Phase 734
- SIM-TOPOLOGY-01 commission brief (`ilc_sim_topology_01_commissioning_711_v0.1.md`) must be confirmed present before Phase 735

### Sequencing constraints

- Phase 734 must commit before Phase 736 (SIM-VALIDATOR-01 results must be available to cite in CDL-068 opening or Phase 737 prelock update)
- Phase 735 must commit (at minimum partial-complete) before Phase 736 (CDL-068 opening document cites SIM-TOPOLOGY-01 scope and status)
- Phase 737 must commit after both Phase 734 and Phase 735 (prelock evidence artifact cites both SIM results)
- Phase 738 must be the final commit in the window

### Open questions (for CDL-068, not this window)

- Exact VRF upgrade threshold numeric (from SIM-VALIDATOR-01 results — Phase 734 must supply this)
- Q6 numeric thresholds: `distinct_cluster_floor` and `max_cluster_share_ceiling` (from SIM-TOPOLOGY-01 results — Phase 735 must supply these or carry forward to 739)
- CDL-068 ratification timing: Window 739 or convergence window? Depends on SIM-TOPOLOGY-01 completion status.

### Permanently deferred (not open questions — settled)

- CDL-039 amendment for topology: **rejected** (Q3 settled — new CDL is the path)
- Epoch-hash vs VRF for v1: **settled** (epoch-hash v1, VRF at named threshold)
- Validation pools in CDL-017: **rejected** (Q4 settled — separate CDL)
- Same BLS key for validator and agent: **rejected** (Q1 settled — derived sub-key)

---

## 11. Known Patterns and Technical Constraints

### Novel patterns this window

- **First window where pre-window conversation record is imported into sequence lock**: Phase 733 must include a verbatim Q1–Q6 section in the sequence lock doc. Prior sequence locks (727, 723, etc.) did not include conversation records because those windows had no pre-window resolution requirement.
- **First SIM execution pair in same window**: Phases 734 and 735 both execute SIMs. Prior windows commissioned SIMs in one phase and executed in another. The commission briefs are already committed (Phase 711); only execution and results are new.
- **Partial-complete SIM pattern**: If SIM-TOPOLOGY-01 produces partial results, the closure gate must accept a `partial_complete` verdict. This is a new verdict token pattern; prior SIM gates used only `pass` or `fail`.

### Historical prelock hardening

Each phase that touches a prior test file must harden that test's CDL-state checks against the current open/closed status at the time of the commit being tested. Phase 737's evidence artifact update must not cause test regressions in Phase 710's tests. If Phase 710's test file asserts `cdl_017_prelock_only_not_ratified_here` in Phase 710 context, that assertion must remain valid — CDL-017 is still not ratified after Phase 737.

### No phantom edit guard needed (no ilc_core/ mutation)

No `ilc_core/` or `ilc_consensus/` files are mutation targets in this window. The phantom edit guard is not required. However: if Codex is tempted to add validator logic to `ilc_core/` based on SIM results, this must be blocked explicitly — no runtime mutation until the Mysticeti convergence window.

### Closure gate selftest guard chain

Phase 738 closure gate test file must include selftest guards for all prior window closure gate tests in the selftest env var chain. Read each prior gate test file directly rather than reasoning by analogy. The minimum required selftest env vars in category 3:
```
ILC_PHASE_401_GATE_SELFTEST=1
ILC_PHASE_413_GATE_SELFTEST=1
ILC_PHASE_337_GATE_SELFTEST=1
[... and all subsequent closure gates through Phase 732]
```
Read `tests/test_phase_732_window_727_732_closure_gate.py` for the exact chain used in the prior gate before adding Phase 738's entry.

---

## 12. Non-Goals and Explicitly Deferred Items

- CDL-017 ratification — convergence window only
- CDL-068 ratification — Window 739 or convergence window
- Any validation pool CDL — after CDL-017 ratification
- VRF implementation — Gemini lane, after CDL-068 ratification and named threshold reached
- ilc_core/ mutation — Mysticeti convergence window
- ilc_consensus/ mutation — Gemini M-lane exclusively until convergence
- MVP gate rows 5 + 7 runtime form — Window 739-744
- Option B graduation — Window 745-748
- Morphogenetic hypergraph ADR-0029/0030 ratification — post-mainnet
- Legal positioning memo — carry-forward only, not a gate

---

## 13. Key Canonical Anchors for Phase Prompt Drafting

- `docs/specs/ilc_antigravity_context_capsule_v5.0.md` (PRIMARY — current frontier)
- `docs/specs/ilc_window_727_732_closure_gate_732_v0.1.md` (prior window closure)
- `docs/specs/ilc_phase_727_732_sequence_lock_v0.1.md` (format reference for new sequence lock)
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (CDL register — CDL-068 will be added Phase 736)
- `docs/phases/STATUS.md` (read tail at Phase 733 execution time for Track B)
- `docs/research/ilc_codex_lane_window_plan_733_plus_v0.1.md` (pre-window conversation record, Q1–Q6 settled answers)
- `docs/specs/ilc_sim_validator_01_commissioning_711_v0.1.md` (commission brief for Phase 734)
- `docs/specs/ilc_sim_topology_01_commissioning_711_v0.1.md` (commission brief for Phase 735)
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md` (Phase 710 prelock artifact — additive update in Phase 737)
- `docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md` (disposition target in Phase 737)
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` (§4.2 ADR-0019 obligation, §4.7 Q1–Q6 block)
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md` (six remaining gaps; Gap 1 = CDL-017)
- For Phase 738 closure gate: all Phase 733–737 test files and artifacts

`window_733_738_candidate_phase_grouping_published_2026_04_19`
`codex_pre_window_guidance_complete`
`pre_window_conversation_record_complete_2026_04_19`
