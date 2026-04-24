# ILC Codex Model Transition Supplement B5 v0.1

**Date:** 2026-04-24
**Use:** first-entry brief for the incoming GPT-5.5 instance
**Capsule:** `docs/specs/ilc_antigravity_context_capsule_v5.13.md`

## 1. Critical Correction Record

The last committed B-4 recommendation from Codex is superseded.

Do not use the old conclusion:

- mixing family
- `A<=0.30`, `B<=0.45`, `C<=0.40`

That result came from the original formula-based simulation and is no longer the
live Row-5 basis.

The correction chain is:

- FIX-1: real Monte Carlo replaced formula functions and reversed the family ranking
- FIX-2: rolling-threshold k-anonymity exposed Variant C under non-uniform timing
- FIX-3: `release_jitter_epochs=3` resolved the Variant C exposure
- FIX-4: `k=20 + jitter=3` confirmed as the fallback

Locked Row-5 mechanism:

- primary: `k=30`, `rolling_threshold`, `release_jitter_epochs=3`, `bounded_hold`
- fallback: `k=20`, `rolling_threshold`, `release_jitter_epochs=3`, `bounded_hold`
- simulation-derived B-Impl target: `A<=0.15`, `B<=0.15`, `C<=0.05`

## 2. Current Constitutional Posture

| Item | Status |
|---|---|
| Row 5 | `spec_closed_runtime_pending` — B-Scope closed, mechanism locked, runtime still pending |
| Row 7 | `runtime_closed` |
| Row 8 | `pass` |
| ADR-0028 | `option_b` posture active; Option B was selected by human authorization on 2026-04-23 |
| CDL-017 | `ratified` in Phase 765; do not reopen as pending work |
| Capsule | `v5.13` |

Two stale assumptions must be ignored by GPT-5.5:

- older draft language that reverts `ADR-0028` to a pre-selection posture and
  gate-no-go framing
- older draft language saying `CDL-017` ratification is still pending

Both are false in the live canon.

## 3. Current Frontier

What just closed in B-5:

- the B-4 human hold point is closed
- Row-5 mechanism selection is locked
- Row-5 B-Impl is commissioned to the local reviewer
- `TransferClass` and `ExpressConsent` groundwork already exists in
  [`types.rs`](/Users/jamstar/Documents/ILC_Main/01_Current/ilc_consensus/src/types.rs)

What has not happened:

- no Row-5 runtime closure claim
- no `SIM-LEAKAGE-03`
- no CDL mutation
- no Option B graduation claim

## 4. GPT-5.5 Operating Boundary

Do not spend time re-litigating closed constitutional items.

- `CDL-017` is already ratified
- Option B is already selected
- Row 5 is the remaining legitimacy lane, but it is now in runtime-pending state

The Row-5 runtime closure window does not open until:

1. the local reviewer completes B-Impl Phases 1–3, and
2. `SIM-LEAKAGE-03` runs on the M-009 testbed

Until then, GPT-5.5 should treat Row 5 as implementation-follow-through and
evaluation-prep, not as an already-open runtime-closure proof window.

## 5. Read Order

1. `AGENTS.md`
2. `docs/PLANNING_INDEX.md`
3. `docs/specs/ilc_antigravity_context_capsule_v5.13.md`
4. `docs/phases/STATUS.md` tail
5. `docs/specs/ilc_row5_mechanism_selection_lock_b5_v0.1.md`
6. `docs/specs/ilc_row5_b_impl_commissioning_spec_v0.1.md`
