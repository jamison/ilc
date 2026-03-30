# ILC Window 505-514 Candidate Phase Grouping v0.1

Status: candidate phase grouping — awaiting sequence lock
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

This document supersedes any informal carry-forward notes from Window 495-504.
The Phase 505 sequence lock will canonicalize and may amend this grouping.

---

## 1. Window purpose

Window 505-514 completes the validator lane runtime tranche and advances the epoch-boundary
witness CDL. The three primary deliverables are:
1. CDL-055 validator staking and liveness runtime implementation,
2. CDL-056 validator trust-tier runtime implementation,
3. Epoch-boundary witness CDL (vehicle selection → opening → prelock → ratification).

A fourth scoping deliverable (re_admission_boundary CDL analysis) closes the CDL-055 forward
obligation. CDL-058 opening is deferred to Window 515+.

---

## 2. Carry-forward inputs (from Window 495-504)

| Item | Source | Window 505-514 action |
|---|---|---|
| CDL-055 runtime implementation | Handoff §3 | Phase 506 |
| CDL-056 runtime implementation | Handoff §4 | Phase 507 |
| Epoch-boundary CDL amendment | Handoff §6 | Phases 508-511 |
| re_admission_boundary CDL scoping | Audit M-1 + evidence governance token | Phase 512 |
| Capsule v2.3 state stale after Phase 504 | Audit M-2 | Phase 513 (capsule v2.4) |
| CDL-056 tiebreaker category enumeration | Audit M-4 | Phase 507 test contract |
| ADR-0023 carry-forward reference | Audit L-2 | Phase 513 (capsule v2.4) |

---

## 3. CDL status at window entry

| CDL | Status | Action |
|---|---|---|
| CDL-055 | ratified (Phase 496) | runtime implementation Phase 506 |
| CDL-056 | ratified (Phase 501) | runtime implementation Phase 507 |
| CDL-053 | reserved (unopened) | protected throughout window |
| CDL-057 (or CDL-030/051 amendment) | not yet opened | vehicle selection Phase 508; open Phase 509 |
| CDL-058 (re_admission_boundary) | not yet opened | scoping only Phase 512; open Window 515+ |

---

## 4. Phase map

### Phase 505 — Sequence lock and carry-forward intake (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_phase_505_514_sequence_lock_v0.1.md`

Scope:
- Freeze 10-phase program for Window 505-514.
- Enumerate CDL-055/056 runtime scope and explicitly declare `re_admission_boundary` out of scope
  for CDL-055 runtime in this window.
- Enumerate epoch-boundary CDL vehicle decision obligation for Phase 508.
- No CDL mutation. No ilc_core/ mutation.

---

### Phase 506 — CDL-055 validator staking and liveness runtime (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/validator/__init__.py` (new subpackage)
- `ilc_core/validator/staking_liveness_runtime.py`
- `tests/test_phase_506_validator_staking_liveness_runtime.py`

Scope:
- New `ilc_core/validator/` subpackage.
- Runtime module exports:
  - `STAKING_LIVENESS_RUNTIME_VERSION = "staking_liveness_runtime_506.v0.1"`
  - `CDL_055_DEPENDENCY = "cdl_055_ratified_496.v0.1"`
  - `GENESIS_STAKE_AMOUNT` (anchored to SIM-010 recommended value)
  - `LIVENESS_MISS_THRESHOLD` (anchored to SIM-010 recommended value)
  - `EQUIVOCATION_FULL_SLASH` constant
  - `validate_staking_and_liveness_state()` enforcement function
- Explicit exclusion: `re_admission_boundary` is NOT defined in this module.
- No CDL mutation. `ilc_core/validator/` mutations only.
- Test count: 12 tests.

CRITICAL guard: `re_admission_boundary` must NOT appear in the runtime module as a constant,
parameter, or function argument. The test suite must assert its absence by name.

---

### Phase 507 — CDL-056 validator trust-tier runtime (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/validator/trust_tier_runtime.py`
- `tests/test_phase_507_validator_trust_tier_runtime.py`

Scope:
- Runtime module exports:
  - `TRUST_TIER_RUNTIME_VERSION = "trust_tier_runtime_507.v0.1"`
  - `CDL_056_DEPENDENCY = "cdl_056_ratified_501.v0.1"`
  - `CDL_055_STAKING_DEPENDENCY = "staking_liveness_runtime_506.v0.1"` (dep chain)
  - `is_trust_tier_eligible(validator_liveness_score, equivocation_state)` function
  - `revoke_trust_tier_if_below_threshold(validator_state)` function
  - `apply_consensus_dispute_tiebreaker(dispute_type, candidates)` function
- `dispute_type` must be validated against an explicit enumeration of consensus-related dispute
  categories (block-proposal dispute, equivocation dispute, fork-choice dispute). Non-consensus
  dispute types must raise `ValueError`.
- No CDL mutation. `ilc_core/validator/` mutations only (adding to existing subpackage).
- Test count: 12 tests.

CRITICAL guard: The dispute-type enumeration must be tested as a boundary assertion — non-consensus
dispute types must be rejected by the runtime, not silently accepted.

---

### Phase 508 — Epoch-boundary CDL vehicle selection (NON-SENSITIVE, analytical)

Deliverables:
- `docs/specs/ilc_epoch_boundary_cdl_vehicle_selection_508_v0.1.md`
- `tests/test_phase_508_epoch_boundary_cdl_vehicle_selection.py`

Scope:
- Analytical phase only. No CDL mutation. No ilc_core/ mutation.
- Evaluate three candidate vehicles:
  1. CDL-030 extension (P_e conversion surface amendment)
  2. CDL-051 extension (epoch transition amendment)
  3. New CDL-057 (narrow epoch-boundary witness lane)
- Output: explicit written selection of one vehicle with rationale, OR explicit deferral with
  stated blocking conditions.
- Phase 498 scoping document is a required input.
- Recommendation must state whether the selected vehicle supports only provenance tagging (no CDL
  required per Phase 498) or also includes future blocking-quorum authority (CDL required).

---

### Phase 509 — Epoch-boundary CDL opening (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_057_epoch_boundary_witness_opening_stub_509_v0.1.md`
  (or CDL-030/CDL-051 amendment opening artifact, per Phase 508 decision)
- `tests/test_phase_509_epoch_boundary_cdl_opening_stub.py`
- CDL log mutation (additive only — new row)

Scope:
- Opens CDL-057 (or amends existing CDL row) per Phase 508 vehicle selection.
- Opening stub must cite Phase 508 vehicle selection document as a required anchor.
- Must preserve CDL-053 reserved status.
- Must distinguish the provenance-tagging scope (no CDL required) from the future
  blocking-authority scope (requires this CDL) as governance tokens in the stub.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 510 — Epoch-boundary CDL prelock hardening (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_cdl_057_epoch_boundary_witness_prelock_hardening_510_v0.1.md`
- `tests/test_phase_510_epoch_boundary_cdl_prelock_hardening.py`

Scope:
- Hardens the epoch-boundary witness lane against scope creep.
- Must lock: witness-only vs blocking distinction, CDL-030/051 non-interference, CDL-V3 quorum
  applicability if any quorum is introduced.
- No CDL mutation in Phase 510.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 511 — Epoch-boundary CDL ratification (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_057_epoch_boundary_witness_ratification_evidence_511_v0.1.md`
- `tests/test_phase_511_epoch_boundary_cdl_ratification_evidence.py`
- CDL log mutation (status: open → ratified)

Scope:
- Ratifies CDL-057 (or CDL-030/051 amendment) per evidence ladder.
- 3-path commit resolver (CDL + evidence + test).
- Evidence section heading: `## 6. Section-5 ratification readiness evidence checklist satisfaction`
- Governance tokens must include: `epoch_boundary_witness_scope`, `provenance_tag_only`,
  `blocking_authority_deferred` (if applicable).
- CDL mutation: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=511`.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 512 — re_admission_boundary CDL scoping (NON-SENSITIVE, analytical)

Deliverables:
- `docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md`
- `tests/test_phase_512_re_admission_boundary_cdl_scoping.py`

Scope:
- Closes the CDL-055 forward obligation on `re_admission_boundary`.
- Analytical phase only. No CDL mutation (CDL-058 opening is Window 515+).
- Required inputs: CDL-055 ratification evidence §5 governance token, CDL-046 (timed_out
  orphan policy for context), SIM-010 synthesis.
- Output: scoping document enumerating: what re_admission_boundary governs (validator re-entry
  after liveness miss, after equivocation recovery, after timed_out), candidate options (cool-down
  period, stake re-deposit, reputation floor), and Window 515+ CDL-058 opening prerequisites.
- Must assert that CDL-058 opening is a Window 515+ action; no CDL mutation occurs in Phase 512.

---

### Phase 513 — Integration coherence report and capsule v2.4 (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_integration_coherence_report_513_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.4.md`
- `tests/test_phase_513_coherence_report_and_capsule_v2_4.py`

Scope:
- Coherence report covers: CDL-055/056 runtime integration, epoch-boundary CDL ratification,
  re_admission_boundary scoping, ADR-0023 carry-forward.
- Capsule v2.4 required content:
  - §1: "Window 505-514 is closed. Window 515+ requires a new sequence lock."
    (OR "Window 505-514 is active." if written mid-window before Phase 514)
  - Must reference ADR-0023 as a research carry-forward, not a ratified CDL.
  - Must explicitly state CDL-058 opening is Window 515+.
  - Must supersede capsule v2.3.
- No CDL mutation. No ilc_core/ mutation.

---

### Phase 514 — Closure gate and handoff (SENSITIVE — gate + tests)

Deliverables:
- `tools/check_window_505_514_closure_gate_phase_514.sh`
- `docs/specs/ilc_window_505_514_handoff_514_v0.1.md`
- `tests/test_window_505_514_closure_gate_514.py`

Scope:
- 6-category gate: prompt_contract_validation, lane_contract_tests, cross_window_regression,
  mutation_canary, closure_gate_cli_contract, walkthrough_hygiene.
- Lane contract tests: Phases 505-513.
- Cross-window regression: all prior closure gate tests (307, 317, 327, 337, 347, 357, 367, 377,
  391, 401, 413, 423, 433, 440, 449, 459, 468, 474 (no selftest guard), 484 (no selftest guard),
  494, 504, 514).
- Selftest chain: must include ILC_PHASE_NNN_GATE_SELFTEST=1 for every prior gate with a
  `test_gate_full_run_*` function. Verify by reading each test file — do not copy by analogy.
- Snapshot isolation: gate must write to `ILC_PHASE_514_SNAPSHOT_PATH` override; never to
  canonical `out/monitoring/`.
- Handoff §7 next-window controls must state CDL-058 opening is Window 515+.

---

## 5. CDL mutation summary for Window 505-514

| Phase | CDL action |
|---|---|
| 505 | None |
| 506 | None |
| 507 | None |
| 508 | None |
| 509 | CDL-057 (or CDL-030/051 amendment) row addition |
| 510 | None |
| 511 | CDL-057 status: open → ratified |
| 512 | None |
| 513 | None |
| 514 | None |

---

## 6. ilc_core/ mutation summary for Window 505-514

| Phase | ilc_core/ action |
|---|---|
| 505 | None |
| 506 | `ilc_core/validator/__init__.py` + `staking_liveness_runtime.py` (NEW subpackage) |
| 507 | `ilc_core/validator/trust_tier_runtime.py` |
| 508–514 | None |

---

## 7. Protected boundaries

The following boundaries must remain intact throughout Window 505-514:

- CDL-053 reserved and unopened.
- CDL-058 scoped but not opened until Window 515+.
- CDL-V3 diversity floor protections unchanged.
- 7+1 quorum ladder unchanged.
- ADR-0022 private/gated boundary separate from validator work.
- Werner credit lane separate from CDL-057 epoch-boundary lane.
- `re_admission_boundary` excluded from CDL-055 runtime implementation.

---

## 8. Predecessor references

- `docs/specs/ilc_window_495_504_handoff_504_v0.1.md` — Window 495-504 closure
- `docs/specs/ilc_antigravity_context_capsule_v2.3.md` — superseded by capsule v2.4 (Phase 513)
- `docs/specs/ilc_epoch_boundary_enforcement_architectural_scoping_498_v0.1.md` — required input
  for Phase 508
- `docs/specs/ilc_cdl_055_validator_staking_and_liveness_enforcement_ratification_evidence_496_v0.1.md`
- `docs/specs/ilc_cdl_056_validator_trust_tier_elevation_ratification_evidence_501_v0.1.md`
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` — carry-forward reference
- `docs/research/ilc_phase_495_504_deep_audit_v0.1.md` — audit findings driving this grouping
