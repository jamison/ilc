# ILC Window 649-654 Candidate Phase Grouping v0.1

Status: planning artifact
Date: 2026-04-14
Classification: candidate phase grouping
Owner lane: G8 MVP touchpoints runtime/interface closure

## 1. Window identity

Window 649-654 is the concrete execution form of the long-carried `Window 623+`
roadmap label.

This window follows:
- Window 613-619 MVP gate spec closure
- Window 624-630 bounded ECU active-layer runtime and hardening
- Window 631-636 Tier-0 exact-numeric foundation
- Window 637-641 bounded residual numeric cleanup
- Window 642-648 bounded security boundary hardening

This window exists to:
- close the interface/runtime form of the five MVP touchpoints
- move Phase 611 graduation checklist rows 1-4 from
  `spec_closed_runtime_pending` to `runtime_closed`
- preserve the active `Option D` posture while removing the runtime-form blocker
  beneath later Option-B routing

## 2. Authorization basis and current state

Current inherited state before this window:
- public init/admission is closed in spec form by Phase 614
- public receipt schema and bounded query are closed in spec form by Phase 616
- visible ECU and delayed visible ILC lifecycle are closed in spec form by
  Phase 615
- public wallet surface is closed in spec form by Phase 617
- Window 613-619 handoff records rows 1-4 as `spec_closed_runtime_pending`
- bounded ECU active-layer runtime is live and hardened
- exact-numeric and non-finite ingress rules are live in the migrated runtime
  surfaces
- bounded touched security issues on canonical JSON, PRNG, timeout, and NDJSON
  ingress are closed

No 623+ prompt pack previously existed in the repo. Window 649-654 is the first
concrete runtime packet for that deferred lane.

## 3. Window-level constraints

Hard constraints for this window:
- no decision-log mutation
- no ADR mutation
- no `CDL-062` opening
- no sovereign substrate selection claim
- no `Option B` selection claim
- no generalized ECU transfer
- no ILC transferability
- no wallet write, spend, transfer, or withdrawal widening
- `claimability_state` remains `deferred`
- all new numeric/public runtime boundaries must follow exact-numeric,
  canonical-string, and non-finite rejection rules
- any machine-verifiable JSON surface must remain canonicalized with sorted
  keys, compact separators, and `allow_nan=False`

This is a bounded runtime/interface closure lane, not a new constitutional lane.

## 4. Touchpoint map and likely runtime target surface

The five MVP touchpoints are closed across four runtime phases:
- public init/admission runtime
- public receipt issuance and query runtime
- visible ECU runtime surface
- delayed visible ILC settlement runtime surface
- public wallet runtime integration

Primary likely runtime surface families:
- `ilc_core/server.py`
- `ilc_core/storage/lmdb_public_runtime.py`
- `ilc_core/rc/economic_cycle_runtime.py`
- `ilc_core/protocol/ilc_receipt_validate.py`
- `ilc_core/protocol/schemas/ilc_receipt_schema_v0.1.json`
- `ilc_core/identity/agent_id_runtime.py`

Execution may introduce a small new helper module if needed, but the lane should
stay inside bounded public-runtime, storage, receipt-validation, and lifecycle
integration surfaces rather than widening into unrelated protocol work.

## 5. Phase map

### Phase 649 — Window sequence lock

Type: sensitive sequence lock

Deliverables:
- `docs/specs/ilc_phase_649_654_sequence_lock_v0.1.md`
- `tests/test_phase_649_window_649_654_sequence_lock.py`

Mission:
- lock Window 649-654 as the concrete 623+ runtime lane
- preserve all inherited wallet, lifecycle, and settlement boundaries
- explicitly target rows 1-4 for runtime closure while leaving rows 5-9 open

### Phase 650 — Public init/admission runtime

Type: sensitive runtime phase

Deliverables:
- `docs/specs/ilc_public_init_admission_runtime_650_v0.1.md`
- runtime/test mutations in the bounded init/admission runtime surface
- `tests/test_phase_650_public_init_admission_runtime.py`

Mission:
- implement the bounded public init/admission runtime form of Phase 614
- issue/persist admission-shaped receipts tied to canonical lineage
- keep init/admission fail-closed and non-authoritative beyond the locked scope

### Phase 651 — Public receipt issuance and query runtime

Type: sensitive runtime phase

Deliverables:
- `docs/specs/ilc_public_receipt_runtime_651_v0.1.md`
- runtime/test mutations in receipt issuance, validation, persistence, and
  bounded query surfaces
- `tests/test_phase_651_public_receipt_runtime.py`

Mission:
- implement the runtime form of Phase 616
- support exactly the locked receipt classes and bounded read-only query modes
- fail closed with machine tokens rather than widening into mutation/revocation

### Phase 652 — ECU/ILC lifecycle runtime

Type: sensitive runtime phase

Deliverables:
- `docs/specs/ilc_ecu_ilc_lifecycle_runtime_652_v0.1.md`
- runtime/test mutations in lifecycle visibility and epoch-settled accounting
  surfaces
- `tests/test_phase_652_ecu_ilc_lifecycle_runtime.py`

Mission:
- implement the runtime form of Phase 615
- expose read-only visible ECU and delayed visible ILC settlement state
- add a bounded read-only coupling-invariants diagnostic surface that makes the
  graph-truth-to-settlement ordering visible without claiming the governance
  lock is already closed
- preserve exact-numeric, non-finite rejection, and no-transfer/no-claimability
  boundaries

### Phase 653 — Public wallet runtime integration

Type: sensitive runtime phase

Deliverables:
- `docs/specs/ilc_public_wallet_runtime_integration_653_v0.1.md`
- runtime/test mutations in read-only wallet query/history/export surfaces
- `tests/test_phase_653_public_wallet_runtime_integration.py`

Mission:
- implement the runtime form of Phase 617
- wire `wallet_status`, `wallet_history`, `wallet_export`, and `ledger_summary`
  to the settled runtime root
- keep the wallet surface strictly read-only and accounting-only

### Phase 654 — Runtime coherence, checklist delta, and closure

Type: sensitive closure gate

Deliverables:
- `docs/specs/ilc_window_649_654_runtime_coherence_report_654_v0.1.md`
- `docs/specs/ilc_option_b_graduation_checklist_state_654_v0.1.json`
- `tools/run_window_649_654_runtime_closure_gate_phase_654.sh`
- `tests/test_phase_654_window_649_654_closure_and_handoff.py`
- `docs/specs/ilc_antigravity_context_capsule_v3.8.md`
- `docs/specs/ilc_window_649_654_handoff_654_v0.1.md`

Mission:
- prove the runtime lane is coherent
- record rows 1-4 as `runtime_closed` if and only if the runtime phases pass
- emit a machine-legible nine-row checklist-state artifact with evidence basis
  for each row
- name the coupling-invariants governance lock as the next constitutional target
  after this runtime lane without reserving a CDL number
- preserve rows 5-9 as open and keep `Option D` active

## 6. Success criteria

This window succeeds only if:
1. all five MVP touchpoints are live in bounded runtime/interface form
2. rows 1-4 in the Phase 611 checklist move to `runtime_closed`
3. rows 5-9 remain honestly open
4. no wallet widening or public claimability widening occurs
5. no generalized ECU transfer or ILC transferability is introduced
6. all newly touched runtime/public numeric surfaces obey exact-numeric,
   canonical-string, and non-finite rejection rules
7. all touched machine surfaces preserve canonical JSON and fail-closed
   discipline where applicable
8. the runtime lane leaves behind a machine-legible checklist artifact and an
   explicit forward pointer to the coupling-invariants governance lane

## 7. Routing after closure

After Window 649-654:
- the MVP runtime/interface blocker beneath rows 1-4 is removed
- `Option D` remains active until later checklist rows are materially closed and
  explicitly authorized
- the next major blocker remains the later-lane governance/privacy/substrate
  route, especially the coupling-invariants governance lock
- the closure packet should leave a machine-legible checklist state and a clear
  handoff pointer into that coupling-invariants governance lane
- this window does not by itself authorize broader public RC claims that depend
  on still-open rows 5-9
