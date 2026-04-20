# ILC Antigravity Context Capsule v5.2

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.1.md
Date: 2026-04-20
Owner lane: G8 MVP-gate runtime-form and CDL-068 ratification closure

This capsule is self-contained.

## 1. Current frontier state

Capsule v5.2 supersedes v5.1.
Window 739-744 is now closed as the MVP-gate runtime-form plus CDL-068
ratification lane.
Window 745-748 is the next main-lane continuation to be defined.

New frontier state at the close of Window 739-744:

- `CDL-068` is now ratified in Phase `743`
- `CDL-068` ratified
  `k_degree_floor >= 4`,
  `push_fanout_ceiling <= 3`,
  `distinct_cluster_floor >= 4`,
  `max_cluster_share_ceiling <= 33%`,
  `shuffle_cadence_epochs = 1`,
  and `vrf_upgrade_threshold_validator_count = 10`
- `CDL-017` remains open and unratified
- row `5` remains `spec_closed_runtime_pending`
- row `5` now has a runtime evidence package and `SIM-LEAKAGE-01` commissioning
  spec, but execution is still pending
- row `7` remains `spec_closed_runtime_pending`
- row `7` censorship resistance now has a runtime evidence contract, but still
  awaits the Gemini `M-019` artifact bundle required by Phase `741` Section
  `3.2`
- row `7` strong exitability remains deferred to the Mysticeti convergence
  window
- row `8` remains an inherited criteria lock and was not advanced in Window
  `739-744`
- Gap 1 remains
  `PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE — pending Gemini M-022 for ratification`
- Option B graduation remains deferred to Window `745-748` and later actual
  row-5 / row-7 runtime closure
- Track B status: `M-018 complete; next planned phase M-019 (Adversarial Hardening and Byzantine Fault Simulation)`

## 2. Frozen inherited boundary state

The following inherited boundaries remain frozen:

- `CDL-047` treasury governance framework
- `CDL-048` ECU mandatory-conversion discipline
- `CDL-062` sovereign-substrate research lane
- `CDL-066` sender authorization
- `CDL-067` settlement-state governance vehicle
- `CDL-068` topology-shuffle authorization lane, now ratified
- `CDL-017` open and unratified
- ADR-0022 private/public and gated-use boundary
- ADR-0028 Option D active posture

Capsule v5.2 does not reopen:

- `CDL-017`
- `CDL-062`
- row `5` runtime closure by rhetoric alone
- row `7` runtime closure by rhetoric alone
- row `8` runtime confirmation
- sovereign substrate selection
- wallet widening
- final Option B production selection
- true multi-machine validator proof claims

## 3. Window 739-744 closure state

Window 739-744 is now fixed as:

- Phase 739 sequence lock complete
- Phase 740 row-5 runtime evidence package complete
- Phase 741 row-7 runtime evidence package complete
- Phase 742 `CDL-068` ratification-readiness dossier complete
- Phase 743 `CDL-068` ratification complete
- Phase 744 coherence, capsule, and closure gate complete

This window closed as honest runtime-form packaging plus narrow constitutional
ratification, without fake runtime closure, fake convergence, or runtime
mutation.

## 4. Remaining later-lane blockers and carry-forward

The surviving carry-forward items now include:

- actual execution of `SIM-LEAKAGE-01` for row `5`
- Gemini `M-019` censorship-runtime artifact bundle for row `7`, including the
  Phase `741` Section `3.2` mapping note back to the Phase `698` proof basis
- strong exitability drill execution for row `7`
- stronger public-substrate replayability proof beyond the local M-016
  extractor lane
- Gemini `M-022` before any later `CDL-017` ratification claim
- final Option B production selection after rows `5` and `7` runtime closure
- legal positioning memo carry-forward before broader public RC claims

This window did not close row `5`, did not close row `7`, did not advance row
`8`, and did not authorize Option B selection.

## 5. Window 739-744 Closure Summary

- Phase `739`: fixed Window `739-744` as the MVP-gate runtime-form plus
  `CDL-068` ratification lane and re-read the live Track B line from
  `STATUS.md`.
- Phase `740`: published the row-5 runtime evidence package and
  `SIM-LEAKAGE-01` commissioning spec, binding runtime proof obligations to the
  Phase `679` observability floor and the Phase `681` attacker model.
- Phase `741`: published the row-7 runtime evidence package, separating
  censorship-resistance runtime confirmation from the distinct strong-exitability
  drill.
- Phase `742`: published the `CDL-068` readiness dossier and explicitly checked
  all opening-checklist items plus all six Phase `736` prelock criteria.
- Phase `743`: ratified `CDL-068` and changed only the `CDL-068` row in the
  constitutional decision log.
- Phase `744`: published the coherence report, capsule v5.2, and the closure
  gate for Window `739-744`.

## 6. Next authorized continuation

The next main-lane continuation is Window `745-748` to be defined.

Until that continuation is packetized, the live carry-forward is:

- preserve the ratified `CDL-068` topology boundary exactly as written in Phase
  `743`,
- preserve row `5` as `spec_closed_runtime_pending` pending actual
  `SIM-LEAKAGE-01` execution,
- preserve row `7` as `spec_closed_runtime_pending` pending both the Gemini
  `M-019` artifact bundle and the separate strong-exitability drill,
- preserve row `8` as inherited and unchanged,
- route Option B graduation through Window `745-748` only after honest runtime
  closure on rows `5` and `7`,
- route `CDL-017` convergence through the later Gemini `M-022` handoff and the
  Mysticeti convergence window.
