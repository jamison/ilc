# ILC Antigravity Context Capsule v5.3

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.2.md
Date: 2026-04-20
Owner lane: G8 convergence-window commissioning and planning-surface advance

This capsule is self-contained.

## 1. Current frontier state

Capsule v5.3 supersedes v5.2.
Window 745-748 is now active through Phase `747`.
Phase `748` is the remaining in-window closure phase.

New frontier state after Phases `745-747`:

- Phase `745` sequence lock is complete
- Phase `746` convergence-window commissioning spec is complete
- the later Mysticeti convergence window is now commissioned but **not open**
- the commissioned convergence window is fixed to a bounded six-phase budget
- ADR-0031 is now accepted in Phase `746`
- `CDL-068` remains ratified from Phase `743`
- `CDL-017` remains open and unratified
- row `5` remains `spec_closed_runtime_pending`
- row `7` remains `spec_closed_runtime_pending`
- row `8` remains inherited and unchanged
- Option B graduation remains deferred to the later convergence window
- Track B status from `STATUS.md` tail remains:
  `M-019 complete; next planned phase M-020`

The convergence commissioning spec now names the currently expected artifact
carriers:

- row-7 censorship runtime bundle:
  `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
- row-5 `SIM-LEAKAGE-01` results:
  `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`

Naming the carriers does not open the convergence window. The later window
still requires all three artifact classes to exist and be re-verified together.

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

Capsule v5.3 does not reopen:

- `CDL-017`
- `CDL-062`
- row `5` runtime closure by rhetoric alone
- row `7` runtime closure by rhetoric alone
- row `8` runtime confirmation
- sovereign substrate selection
- wallet widening
- final Option B production selection
- the deferred legal positioning technical facts annex
- true multi-machine validator proof claims

## 3. Window 745-748 active state

Window 745-748 is now fixed as:

- Phase `745` sequence lock complete
- Phase `746` convergence-window commissioning spec complete
- Phase `746` ADR-0031 housekeeping acceptance complete
- Phase `747` capsule v5.3, roadmap v0.4, and planning-index advance complete
- Phase `748` coherence report and closure gate pending

This window is still an honest planning window. It has not closed row `5`, row
`7`, or row `8`. It has not ratified `CDL-017`. It has not graduated Option B.

## 4. Remaining later-lane blockers and carry-forward

The surviving carry-forward items now include:

- actual execution of `SIM-LEAKAGE-01` for row `5`
- the committed row-7 censorship-runtime bundle re-verified by the later
  convergence sequence lock
- strong exitability drill execution for row `7`
- stronger public-substrate replayability proof beyond the local M-016
  extractor lane
- Gemini `M-022` before any later `CDL-017` ratification claim
- final Option B production selection only after honest runtime closure on
  rows `5` and `7`
- legal positioning memo carry-forward before broader public RC claims

This window commissioned the later convergence lane and aligned the planning
surfaces. It did not satisfy the later-lane blockers itself.

## 5. Window 745-748 Progress Summary

- Phase `745`: opened Window `745-748` as the convergence-window commissioning
  and planning-surface advance lane and re-read the live Track B line from
  `STATUS.md`.
- Phase `746`: commissioned the later convergence window as a bounded
  six-phase lane, recorded the three artifact-gated entry conditions, and
  accepted ADR-0031 as housekeeping-only because the proto contract was already
  present.
- Phase `747`: advanced capsule v5.3, roadmap v0.4, and `PLANNING_INDEX.md`
  to the true post-746 frontier while keeping the live Track B line bound to
  `STATUS.md` tail.

## 6. Next authorized continuation

The remaining in-window continuation is Phase `748`.

Until Phase `748` closes Window `745-748`, the live carry-forward is:

- preserve row `5` as `spec_closed_runtime_pending`,
- preserve row `7` as `spec_closed_runtime_pending`,
- preserve row `8` as inherited and unchanged,
- preserve `CDL-017` as open,
- preserve ADR-0028 Option D as active,
- preserve the commissioned convergence window as **not open** until all entry
  artifacts exist and are re-verified together.
