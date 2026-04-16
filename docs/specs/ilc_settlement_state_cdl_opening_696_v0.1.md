# ILC Settlement-State CDL Opening 696 v0.1

Status: opening artifact
Date: 2026-04-16
Decision vehicle: CDL-067
Phase: 696
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`cdl_067_opened_for_settlement_state_scope`
`settlement_state_is_constitutional_surface_not_backend_convenience`
`backend_carries_already_legitimate_state_only`

## 1. Decision target and why a constitutional vehicle is needed

Phase 687 already produced the planning enumeration:
`docs/specs/ilc_settlement_state_enumeration_and_submission_model_687_v0.1.md`

That artifact answered the research question. It did not create a
constitutional lane.

CDL-067 opens in Phase 696 because the project now needs an explicit protocol
vehicle for the question:

What counts as durable ILC protocol state for Option-B settlement purposes?

This needs constitutional treatment because:
- settlement-state scope determines what the later backend is allowed to carry,
- settlement-state scope defines the public replay and audit surface,
- settlement-state scope cannot be left as a moving benchmark assumption once
  the chosen-substrate lane is active.

## 2. Inherited legitimacy boundary

CDL-067 inherits CDL-065 without modification.

The locked boundary remains:
- a later backend may carry, order, anchor, finalize, or settle already
  legitimate protocol state,
- a later backend may not author, override, or inherit protocol legitimacy on
  its own.

CDL-067 therefore governs the downstream settlement-state surface only. It does
not reopen the upstream legitimacy boundary.

## 3. Opening scope

### In scope

- defining what categories of protocol state qualify as durable settlement
  state for Option-B purposes
- defining the canonical epoch-boundary submission unit at the level required
  for constitutional scope
- defining which public legitimacy surfaces must be carried downstream
- defining which categories remain off-chain and hash-anchored only

### Out of scope

- final substrate-family selection
- final serialization or wire-format lock for every field
- row-5 closure
- row-7 closure
- row-8 closure
- public launch or production deployment authorization

## 4. Candidate settlement-state rule set opened here

The candidate constitutional rule set opened in CDL-067 is:

### 4.1 Durable on-settlement categories

The settlement substrate must be able to carry:
- epoch-boundary commit records
- public node-linkage graph anchors
- namespace and schema registry events
- sparse economic and governance events
- genesis lineage anchor material

### 4.2 Off-chain preserved categories

The settlement substrate must not require direct carriage of:
- raw claim and evidence payloads
- individual COSE Sign1 bytes for authored nodes
- private or gated shard content
- per-agent detailed ECU balance ledgers
- raw panel deliberation records

These remain off-chain, content-addressed, and replay-linked through the
anchored settlement record.

### 4.3 Epoch-boundary submission discipline

The canonical settlement-state submission unit is the epoch settlement record
described in the Phase 687 enumeration artifact, including:
- epoch sequence / close time
- prior epoch linkage
- canonical state root
- node / edge deltas
- namespace events
- economic events
- governance events

CDL-067 opening does not yet ratify every field or encoding detail. It opens
the constitutional lane that says this class of state is real, durable, and
bounded.

## 5. Evidence anchors

Required anchors:
- `docs/specs/ilc_phase_694_700_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_694_700_track_a_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_settlement_state_enumeration_and_submission_model_687_v0.1.md`
- `docs/specs/ilc_coupling_invariants_governance_lock_663_v0.1.md`
- `docs/specs/ilc_cdl_062_mysticeti_survivor_set_addendum_693_v0.1.md`

## 6. Forward obligations

Later phases must still do the following:
- ratify the settlement-state lane explicitly if the current scope remains
  correct after Track-B spike evidence
- ensure row-5 mechanism proof over Mysticeti remains compatible with the
  settlement-state surface opened here
- ensure row-7 and row-8 closure artifacts evaluate the real carried state
  rather than an abstract substrate target
- make any later change to this state surface through explicit amendment, not
  by benchmark drift

This opening is therefore a constitutional scope declaration, not a final
backend schema freeze.
