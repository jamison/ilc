# ILC Row-7 Runtime Evidence Package 741 v0.1

Status: runtime-evidence package
Date: 2026-04-20
Phase: 741
Owner lane: G8 MVP-gate runtime-form lane
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`row_7_runtime_evidence_package_741_complete`
`row_7_runtime_obligations_split_censorship_and_exitability`
`row_7_censorship_runtime_confirmation_requires_m019_evidence`
`row_7_exitability_drill_deferred_to_mysticeti_convergence_window`
`row_7_status_after_phase_741=spec_closed_runtime_pending`
`row_8_inherited_criteria_lock_not_advanced_in_phase_741`

## 1. Purpose and inherited authority

This artifact formalizes what live evidence is required to move row `7` from
`spec_closed_runtime_pending` to `runtime_closed`.

It inherits the authoritative row-7 baseline from:

- `docs/specs/ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md`
- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/specs/ilc_exitability_and_replayability_threshold_674_v0.1.md`
- `docs/specs/ilc_phase_739_744_sequence_lock_v0.1.md`

Phase `698` already proved the bounded Mysticeti DAG commit rule formally for
`N=4`, `F=1`, `MaxRound=5`, and `Liveness`. This phase does not reopen that
proof. It formalizes the remaining runtime evidence bar.

## 2. The two distinct row-7 runtime obligations

Row `7` contains two distinct runtime obligations that do not share an evidence
source:

1. **Censorship-resistance runtime confirmation**
   - expected evidence source: Gemini `M-019`
   - target question: does a live multi-machine validator network preserve
     practical inclusion and eventual commit under a censoring-validator
     scenario?

2. **Strong exitability drill**
   - expected evidence source: a separate export / verify / replay / migrate
     drill
   - target question: can a participant or successor environment recover and
     continue legitimacy-relevant state without privileged original-operator
     consent?

These obligations must be treated separately in every later row-7 closure
claim.

`row_7_censorship_and_exitability_do_not_share_evidence_source`

The honest post-Phase-741 posture is:

- censorship resistance expects live Gemini `M-019` runtime evidence,
- strong exitability requires a separate drill contract and remains execution-
  deferred,
- row `7` remains `spec_closed_runtime_pending` until both obligations are
  satisfied.

## 3. Censorship-resistance runtime confirmation contract

The censorship-resistance side is the live-runtime counterpart to the formal
Phase `698` TLC proof.

### 3.1 What Phase 698 already established

Phase `698` already established:

- `N=4`
- `F=1`
- `MaxRound=5`
- `Liveness`

The formal proof therefore already shows that an honest-broadcast vertex
eventually commits despite bounded Byzantine withholding in the checked model.

### 3.2 What M-019 must demonstrate at runtime

Gemini `M-019` is the expected runtime evidence source for the censorship side.
For row-7 purposes, the `M-019` run must demonstrate all of the following:

1. a live multi-machine validator network includes an actual censoring or
   withholding validator in the bounded Byzantine role,
2. the runtime scenario is not weaker than the Phase `698` proof basis:
   it must at least cover the `N=4`, `F=1` shape or a stricter live
   configuration,
3. a well-formed participant submission or retrying participant path is not
   practically excluded by the censoring validator,
4. the honest path still reaches eventual commit under the bounded censoring
   quorum,
5. the resulting evidence bundle includes logs, timing evidence, and a verdict
   table sufficient to map the live run back to the Phase `698` formal model.

### 3.3 Minimum runtime artifacts for censorship confirmation

The minimum artifact bundle for the censorship side is:

- run manifest naming validator roles and the censoring validator,
- live logs from honest validators and the censoring validator,
- timestamped evidence showing retry or rebroadcast behavior where relevant,
- commit evidence showing that the honest path was not suppressed permanently,
- a short mapping note tying the live run back to the `N=4`, `F=1`,
  `MaxRound=5`, `Liveness` proof basis,
- explicit runtime verdict:
  censorship-resistance confirmed or not confirmed.

If `M-019` does not produce an artifact bundle at that level, the honest
result is:

- censorship-resistance runtime confirmation remains pending,
- row `7` remains `spec_closed_runtime_pending`.

## 4. Strong exitability drill contract

The strong exitability side does not come from `M-019`.

It inherits the hard threshold from Phase `674`:

- export legitimacy-relevant state,
- independently verify exported state and receipts,
- replay legitimacy-relevant history from portable data,
- migrate without privileged original-operator consent.

### 4.1 Minimum drill steps

The strong exitability drill contract requires:

1. **Export**
   - export legitimacy-relevant state in machine-legible form,
   - include admission, namespace, quorum, settlement, and continuity material
     required by Phase `674`,
2. **Independent verify**
   - verify the exported state against receipts, hashes, or lineage without
     trusting the original operator,
3. **Replay**
   - replay legitimacy-relevant history on a fresh node or successor
     environment from portable or public data,
4. **Migrate**
   - continue from the exported and replayed state without privileged
     original-operator consent,
5. **Continuity preservation**
   - show that canonical history and legitimacy continuity survive the move.

### 4.2 Required failure boundaries

The drill does not satisfy row `7` if:

- users can only read balances or receipts but cannot export legitimacy-relevant
  state,
- export exists but cannot be independently verified,
- verification exists but replay depends on one hosted API or one operator
  shell,
- migration requires privileged original-operator approval,
- continuity disappears when the original provider path disappears.

### 4.3 Deferment posture

Execution of this drill is explicitly deferred to the Mysticeti convergence
window.

`row_7_exitability_execution_explicitly_deferred`

This phase publishes the drill contract only. It does not claim that export,
verification, replay, or migration has already been executed successfully.

## 5. Current status and row-8 disposition

The post-Phase-741 status is:

- row `7` remains `spec_closed_runtime_pending`,
- censorship-resistance runtime confirmation awaits a live Gemini `M-019`
  artifact bundle,
- strong exitability awaits a separate drill execution in the Mysticeti
  convergence window,
- no row-7 runtime-closed claim is authorized by this phase.

Row `8` is unchanged in this window.

`row_8_inherited_criteria_lock_not_advanced_in_phase_741`

Its posture remains:

- inherited criteria lock,
- no runtime confirmation commissioned here,
- no advancement claimed here.
