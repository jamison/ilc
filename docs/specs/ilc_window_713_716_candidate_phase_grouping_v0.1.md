# ILC Window 713-716: Candidate Phase Grouping (Codex Lead)

**Author:** Codex  
**Date:** 2026-04-17  
**Baseline:** Window `707-712` is closed. Capsule v4.6 is published. `CDL-066`
and `CDL-067` are ratified. `CDL-017` remains open and unratified. Track B
shows `M-012` complete and `M-013` next in `STATUS.md`.
**References:**
- `docs/specs/ilc_window_713_716_guidance_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §5.3
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
- `docs/research/ilc_gossip_hybrid_push_pull_architecture_context_v0.1.md`

---

## 1. Window identity and scope

Window `713-716` is the adaptive-gossip and resilience-operationalization lane.

This window is responsible for:

1. writing the sequence lock for `713-716`,
2. publishing the adaptive-gossip law-vs-freedom contract,
3. explicitly classifying every live gossip parameter as
   `constitutional_law`, `operator_configurable`, or `deferred`,
4. commissioning a partition-repair benchmark pack,
5. publishing the missing-signal doctrine disposition,
6. closing the window with a coherence report, capsule v4.7, and closure gate.

This window does NOT:
- ratify any CDL,
- reopen `CDL-060` or `CDL-061`,
- ratify `CDL-039`,
- deliver benchmark results in-window,
- mutate `ilc_core/` or `ilc_consensus/` in the docs-only phases.

---

## 2. Inter-lane dependencies

### 2.1 Inherited baseline

This window inherits:
- Window `707-712` closure and capsule v4.6,
- `CDL-066` ratified,
- `CDL-067` ratified,
- `CDL-017` open and unratified,
- the topology-shuffling authorization path from Phase `711`,
- Track B current state from `STATUS.md`, not from memory.

### 2.2 Relationship to Track B

Track B is not the central work of this packet, but the live M-series frontier
still matters for capsule and closure language. The rule is:
- verify `STATUS.md` tail before every phase,
- do not copy stale M-series wording from capsule v4.6,
- do not let Track B implementation churn redefine the gossip-governance packet
  without explicit source reading.

### 2.3 Relationship to prior gossip law

`CDL-060` and `CDL-061` are the settled constitutional anchors for the active
Python gossip lane:
- `CDL-060` governs the single-hop `centrality_delta` lane under bounded fanout
  and opaque-channel privacy constraints,
- `CDL-061` governs the HTTP envelope/header surface and fallback binding.

Window `713-716` must classify live parameters against those anchors without
silently reopening them.

---

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- Phase `713` sequence lock
- Phase `714` adaptive-gossip contract and complete law-vs-freedom classification
- Phase `715` partition-repair benchmark commissioning and missing-signal doctrine
- Phase `716` coherence report, capsule v4.7, and closure gate

### 3.2 Explicitly deferred

- any CDL ratification
- `CDL-039` ratification or topology-shuffling authorization
- benchmark results for partition-repair evidence
- dynamic peer discovery if it is not already live in the active path
- runtime mutation of `ilc_core/` or `ilc_consensus/`
- `CDL-017` ratification
- Option B production selection

---

## 4. Governing constraints inherited from prior windows

Hard constraints:
- no pre-window conversation gate applies here,
- `CDL-060` and `CDL-061` may be cited but not reopened,
- every live gossip parameter must land in one category and none may be left
  ambiguous,
- benchmark commissioning is acceptable in-window; benchmark-results claims are not,
- topology shuffling remains a later authorization question,
- docs-only phases may not mutate runtime code,
- any statement about current Track B state must be verified against `STATUS.md`.

---

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 713 | Window `713-716` sequence lock | Gate / Planning | **SENSITIVE** |
| 2 | 714 | Adaptive-gossip contract and law-vs-freedom classification | Governance / Spec | **SENSITIVE** |
| 3 | 715 | Partition-repair benchmark pack and missing-signal doctrine | Resilience / Spec | **SENSITIVE** |
| 4 | 716 | Coherence report, capsule v4.7, and window `713-716` closure gate | Gate / Handoff | **SENSITIVE** |

---

## 6. Scope notes for candidate phases

### Phase 713 — sequence lock

Deliverables:
- `docs/specs/ilc_phase_713_716_sequence_lock_v0.1.md`

Required content:
- lock the four-phase ordering for `713-716`,
- state that there is no CDL ratification in-window,
- state that `CDL-060` and `CDL-061` are inherited and not reopened,
- require complete live-parameter classification in Phase `714`,
- state that Phase `715` commissions evidence only and does not need results,
- state that closure phase is `716`.

### Phase 714 — adaptive-gossip law-vs-freedom contract

Deliverables:
- `docs/specs/ilc_adaptive_gossip_law_vs_freedom_contract_714_v0.1.md`

Required content:
- inventory every live gossip parameter,
- classify each as `constitutional_law`, `operator_configurable`, or `deferred`,
- explicitly cover at minimum:
  - `PEER_DISCOVERY_MODE`
  - `MAX_PEERS`
  - `MAX_FANOUT`
  - peer selection
  - timeout / retry / backoff surfaces
  - `ILC-Epoch` header validation / range behavior,
- preserve the no-reopen rule for `CDL-060` and `CDL-061`.

### Phase 715 — benchmark commission and doctrine disposition

Deliverables:
- `docs/specs/ilc_partition_repair_benchmark_pack_715_v0.1.md`
- `docs/specs/ilc_missing_signal_doctrine_disposition_715_v0.1.md`

Required content:
- commission partition-repair evidence with explicit scenario and pass/fail format,
- define what counts as repair under the current static-peer baseline,
- choose an explicit missing-signal behavior,
- state implicated source surfaces,
- avoid ratifying topology shuffling or claiming benchmark completion.

### Phase 716 — closure

Deliverables:
- `docs/specs/ilc_coherence_report_716_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.7.md`
- `docs/specs/ilc_window_713_716_closure_gate_716_v0.1.md`

Required content:
- summarize Phases `713-715`,
- record that no CDL ratification occurred in-window,
- record that benchmark commissioning happened without claiming benchmark results,
- advance the capsule to v4.7,
- route carry-forward explicitly into Window `717-722` and any later resilience
  evidence execution that remains open.

---

## 7. Phase-specific open questions, options, and recommendations

### 7.1 Phase 714

Open question:
- should `PEER_DISCOVERY_MODE = "static_v1"` be treated as inherited law or
  operator freedom?

Options:
- `constitutional_law`
- `operator_configurable`
- `deferred`

Recommendation:
- `constitutional_law` for the current no-dynamic-discovery baseline. The live
  runtime asserts `static_v1` against the `CDL-039` privacy boundary, so moving
  beyond static discovery needs explicit authorization rather than quiet
  operator drift.

Open question:
- should `MAX_PEERS = 16` be treated as constitutional law or operator freedom?

Options:
- `constitutional_law`
- `operator_configurable`
- `deferred`

Recommendation:
- `operator_configurable`. The live ceiling exists, but the exact numeric value
  is not clearly constitutionalized by `CDL-060` or `CDL-061`.

Open question:
- should the exact live fanout bound remain constitutional, or only the
  high-level bounded-fanout principle?

Options:
- exact live bound remains `constitutional_law`
- only the principle is law; the number becomes operator freedom
- `deferred`

Recommendation:
- do not pre-decide this in the packet. Phase `714` should explicitly classify
  whether only the bounded-fanout principle is inherited law or whether the
  exact live constant also rose to constitutional status. The safe planning rule
  is to keep `bounded_fanout` inherited and treat the literal numeric value as a
  live classification question rather than an assumed settled fact.

Open question:
- is the deterministic sorted-prefix peer-selection rule itself law?

Options:
- `constitutional_law`
- `operator_configurable`
- `deferred`

Recommendation:
- `operator_configurable`, provided any alternative heuristic still respects the
  inherited bounded-fanout and privacy constraints.

Open question:
- how should timeout / retry / backoff surfaces be classified if the live path
  only partially exposes them?

Options:
- classify every numeric surface as law
- classify the live numeric surface as operator freedom and mark missing ones deferred
- defer the whole topic

Recommendation:
- classify real live numeric surfaces such as `request_timeout_seconds` as
  `operator_configurable` unless inherited law says otherwise, and mark missing
  retry/backoff knobs as `deferred` rather than inventing policy.

Open question:
- is `ILC-Epoch` only an envelope invariant, or does a stronger staleness/range
  policy already exist?

Options:
- envelope only
- explicit bounded range is already live law
- `deferred`

Recommendation:
- keep required epoch-header presence and non-negative integer validation as
  inherited law; treat any stronger staleness window as `deferred` unless a live
  code path actually implements it.

### 7.2 Phase 715

Open question:
- what counts as repair under the current static-peer baseline?

Options:
- bounded reconnect to the same static peers
- reselection within a broader static registry
- topology shuffling / discovery-based repair

Recommendation:
- bounded reconnect and re-sync over the same static peer set. Do not authorize
  discovery or topology shuffling in this window.

Open question:
- what missing-signal behavior should be chosen?

Options:
- fail-open
- fail-soft
- fail-closed
- grace period + alert, then degraded behavior

Recommendation:
- grace period + alert, then fail-soft degradation aligned with existing
  temporal-decay semantics. This is more honest and safer than silent fail-open,
  and less brittle than immediate fail-closed.

Open question:
- must the benchmark pack include results in-window?

Options:
- yes
- no, commissioning only

Recommendation:
- no. The benchmark pack should commission evidence only and define the results
  format for later execution.

### 7.3 Phase 716

Open question:
- can capsule v4.7 close the window even if partition-repair evidence is only
  commissioned and not yet executed?

Options:
- yes, if explicit
- no, require results first

Recommendation:
- yes, if the coherence report and closure gate state clearly that commissioning
  completed, benchmark execution remains later work, and no performance claims
  are being made.

---

## 8. Blockers and cautions

- there is no pre-window conversation blocker for `713-716`,
- the main execution risk is incomplete parameter inventory in Phase `714`,
- if the live gossip runtime changes before execution, Phase `714` must reread
  the active code before final classification,
- any attempt to smuggle topology shuffling or discovery into Phase `715` is a
  scope violation,
- any attempt to turn commissioning into benchmark-results claims is a closure violation.

---

## 9. Recommendation summary

Proceed with a four-phase packet:
- `713` sequence lock,
- `714` law-vs-freedom classification,
- `715` partition-repair commission plus missing-signal doctrine,
- `716` coherence, capsule v4.7, and closure.

The critical quality bar is Phase `714`: the inventory must be complete and must
classify each live parameter explicitly, including any parameter that is only
partially implemented or present as a current numeric default.
