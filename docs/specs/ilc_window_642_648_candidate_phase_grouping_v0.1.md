# ILC Window 642-648 Candidate Phase Grouping v0.1

Status: planning artifact
Date: 2026-04-14
Classification: candidate phase grouping
Owner lane: G8 security boundary and remaining-float strike force

## 1. Window identity

Window 642-648 is the bounded security strike-force lane that follows:
- Window 624-630 ECU active-layer strike force
- Window 631-636 Tier-0 exact numeric determinism strike force
- Window 637-641 residual `R2/R3` numeric cleanup

This window does not open a new constitutional vehicle. It exists to:
- inventory remaining float surfaces after Window 637-641
- register follow-on float cleanup in durable carry-forward form
- close the live Gemini-identified security/runtime issues that still remain in
  bounded `ilc_core/` implementation surfaces
- harden the code against fix-induced regressions introduced by those fixes

## 2. Window-level constraints

Hard constraints for this window:
- no decision-log mutation
- no ADR mutation
- no wallet widening
- no generalized ECU transfer
- no ILC transferability
- no `Option B` selection claim
- no `CDL-062` opening
- no repo-wide simulation cleanup
- no epoch-liveness fallback architecture opening in this lane

This is an implementation/security hardening lane, not a new governance lane.

## 3. Primary targets

Primary live targets:
- `ilc_core/ledger/canon_bundle_replay_report.py`
- `ilc_core/ledger/canon_export_bundle_sign.py`
- `ilc_core/cli/canon_bundle_sign.py`
- `ilc_core/cli/canon_bundle_validate.py`
- `ilc_core/cli/canon_bundle_replay.py`
- `ilc_core/cli/canon_bundle_pipeline.py`
- `ilc_core/ledger/canon_bundle_pipeline_report.py`
- `ilc_core/network/peer.py`
- `ilc_core/epistemic/aesthetic_panel_runtime.py`
- `ilc_core/economics/passive_ecu_attribution_runtime.py`
- `ilc_core/protocol/ndjson_bundle.py`
- `ilc_core/cli/ep_task_cli.py`

Residual-inventory targets for carry-forward:
- `ilc_core/server.py`
- `ilc_core/config.py`
- `ilc_core/types.py`
- runtime-adjacent consensus / analysis / devnet float surfaces still outside the
  bounded 642-648 security lane

## 4. Second-order guardrails

The window must front-run likely fix-induced vulnerabilities:
- canonical JSON must use `sort_keys=True` with `separators=(",", ":")`
- any JSON intended for cross-language or hash/signature stability must reject
  `NaN` / `Infinity` / `-Infinity`
- deterministic or secure selection must not fall back to predictable Mersenne
  Twister in runtime/security-sensitive paths
- timeout hardening must use bifurcated connect/read timeouts where HTTP IO
  remains operator-facing or network-facing
- bounded-stream fixes must cap both line size and aggregate bundle scale; this
  lane must prefer bounded in-memory iteration over temporary-disk spooling
- assert-removal must not be replaced by silent broad exception swallowing
- any later integer/minor-unit migration must serialize large numeric amounts as
  canonical strings over JSON

## 5. Phase map

### Phase 642 — Window sequence lock

Type: sensitive sequence lock

Deliverables:
- `docs/specs/ilc_phase_642_648_sequence_lock_v0.1.md`
- `tests/test_phase_642_window_642_648_sequence_lock.py`

Mission:
- lock the security lane
- keep it non-constitutional
- preserve Window 623+ as the broader continuation
- require explicit second-order guardrails in later phases

### Phase 643 — Remaining float and security inventory

Type: non-sensitive inventory / carry-forward phase

Deliverables:
- `docs/specs/ilc_remaining_float_and_security_follow_on_inventory_643_v0.1.md`
- `TODO.txt`
- `tests/test_phase_643_remaining_float_and_security_inventory.py`

Mission:
- inventory remaining float surfaces after Window 637-641
- classify which are still open, which are deferred, and which are now lower tier
- register durable TODO carry-forward items

### Phase 644 — Canonical JSON and signature boundary hardening

Type: runtime/security hardening

Deliverables:
- `docs/specs/ilc_canonical_json_and_signature_boundary_hardening_644_v0.1.md`
- runtime/test mutations in canonical JSON / bundle signing / reporting surfaces
- `tests/test_phase_644_canonical_json_and_signature_boundary_hardening.py`

Mission:
- remove remaining `sort_keys=False` / whitespace drift from hash/signature or
  machine-verifiable bundle/report surfaces
- ensure compact separators are locked
- prevent non-finite JSON constants on those paths

### Phase 645 — PRNG, timeout, and invariant enforcement hardening

Type: runtime/security hardening

Deliverables:
- `docs/specs/ilc_prng_timeout_and_invariant_enforcement_hardening_645_v0.1.md`
- runtime/test mutations in peer, panel, and passive-attribution surfaces
- `tests/test_phase_645_prng_timeout_and_invariant_enforcement_hardening.py`

Mission:
- remove predictable PRNG from touched runtime/security-sensitive paths
- harden peer HTTP timeouts with bifurcated connect/read behavior
- replace production `assert` enforcement in touched runtime with explicit checks

### Phase 646 — Bounded NDJSON ingress and operational boundary hardening

Type: runtime/security hardening

Deliverables:
- `docs/specs/ilc_ndjson_ingress_and_operational_boundary_hardening_646_v0.1.md`
- runtime/test mutations in `ndjson_bundle.py` and `ep_task_cli.py`
- `tests/test_phase_646_ndjson_ingress_and_operational_boundary_hardening.py`

Mission:
- bound bundle scale in memory without introducing temp-disk exhaustion behavior
- harden CLI HTTP operations with explicit timeout contracts and narrower catches
- state the touched wall-clock boundary precisely: metadata timestamps may remain,
  protocol-state triggers may not be introduced

### Phase 647 — Security hardening gate and fix-induced regression audit

Type: sensitive hardening gate

Deliverables:
- `docs/specs/ilc_security_hardening_gate_and_fix_induced_regression_audit_647_v0.1.md`
- `tools/run_window_642_648_security_hardening_gate_phase_647.sh`
- `tests/test_phase_647_security_hardening_gate_and_fix_induced_regression_audit.py`

Mission:
- prove the bounded security fixes hold together
- test second-order regressions explicitly
- verify remaining float inventory and TODO carry-forward are in place

### Phase 648 — Closure, capsule, and handoff

Type: closure / carry-forward handoff

Deliverables:
- `docs/specs/ilc_window_642_648_handoff_648_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v3.7.md`
- `tests/test_phase_648_window_642_648_closure_and_handoff.py`

Mission:
- close the security lane cleanly
- route back into the broader runtime roadmap
- keep remaining deferred float/security work visible

## 6. Success criteria

This window succeeds only if:
1. a durable remaining-float inventory and TODO carry-forward are published
2. canonical JSON/signature drift is closed on the touched bundle surfaces
3. touched PRNG/runtime selection no longer depends on predictable `random`
4. touched HTTP/network clients use explicit timeout contracts
5. touched production invariants no longer depend on `assert`
6. NDJSON bundle ingestion is bounded by aggregate scale, not only line size
7. no new fix-induced vulnerability is opened in the touched code

## 7. Routing after closure

After Window 642-648:
- Window 623+ remains the broader priority continuation
- remaining lower-tier float cleanup stays visible through the new inventory/TODO
- no new constitutional or settlement posture is claimed
