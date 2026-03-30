# ILC Window 515-524 Candidate Phase Grouping v0.1

Status: candidate phase grouping — awaiting sequence lock
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

This document supersedes any informal carry-forward notes from Window 505-514.
The Phase 515 sequence lock will canonicalize and may amend this grouping.

---

## 1. Window purpose

Window 515-524 implements the CDL-057 epoch-boundary witness runtime, runs SIM-011 to calibrate
the re_admission_boundary, and advances CDL-058 through its full lifecycle (opening → prelock →
ratification → runtime). An ADR-0023 quality signal CDL scoping analysis closes the research
carry-forward from Window 505-514.

Three primary deliverables:
1. CDL-057 epoch-boundary witness runtime implementation (provenance-only scope; blocking authority
   deferred per ratification),
2. CDL-058 re_admission_boundary full lifecycle (SIM-011 calibration → opening → ratification →
   runtime), and
3. ADR-0023 quality signal CDL scoping analysis (recommendation: open CDL-059 or defer).

---

## 2. Carry-forward inputs (from Window 505-514)

| Item | Source | Window 515-524 action |
|---|---|---|
| CDL-057 runtime deferred | Capsule v2.4 §4 | Phase 516 |
| CDL-058 opening deferred; SIM-011 required | Phase 512 scoping (`sim_011_required`) | Phase 517 → Phase 518 |
| CDL-058 opening prerequisites documented | Capsule v2.4 §4 | Phase 518-521 |
| ADR-0023 research carry-forward | Capsule v2.4 §4 | Phase 522 |
| CDL-053 reserved and separate | Capsule v2.4 §5 | protected throughout window |

---

## 3. CDL status at window entry

| CDL | Status | Action |
|---|---|---|
| CDL-055 | ratified (Phase 496) | consumed by Phase 516 + Phase 521 dep chain |
| CDL-056 | ratified (Phase 501) | consumed by Phase 516 dep chain |
| CDL-057 | ratified (Phase 511) | runtime implementation Phase 516 |
| CDL-058 (re_admission_boundary) | not yet opened | SIM-011 (Phase 517) → open Phase 518 |
| CDL-053 | reserved (unopened) | protected throughout window |

---

## 4. Phase map

### Phase 515 — Sequence lock and carry-forward intake (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_phase_515_524_sequence_lock_v0.1.md`

Scope:
- Freeze 10-phase program for Window 515-524.
- Authorize CDL-057 runtime implementation in Phase 516.
- Authorize SIM-011 execution in Phase 517.
- State CDL-058 opening requires SIM-011 synthesis with `sim_011_sufficient`.
- State CDL-053 reserved throughout window.
- No CDL mutation. No ilc_core/ mutation.

Required tokens in sequence lock:
- `CDL-057 runtime implementation is authorized for Window 515-524.`
- `SIM-011 is required before CDL-058 can be opened.`
- `CDL-053 remains reserved and unopened throughout Window 515-524.`
- `Phase 524 is the closure gate.`

---

### Phase 516 — CDL-057 epoch-boundary witness runtime (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/epoch/epoch_boundary_witness_runtime.py`
- `tests/test_phase_516_epoch_boundary_witness_runtime.py`

Scope:
- New module in existing `ilc_core/epoch/` subpackage (additive only; `epoch_snapshot_runtime.py`
  must not be modified).
- Runtime module exports:
  - `EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION = "epoch_boundary_witness_runtime_516.v0.1"`
  - `CDL_057_DEPENDENCY = "cdl_057_ratified_511.v0.1"`
  - `CDL_055_STAKING_DEPENDENCY` — must equal `staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION`
  - `BLOCKING_AUTHORITY_DEFERRED = True` (constitutional boundary marker per CDL-057 provenance-only scope)
  - `record_epoch_boundary_witness(validator_id, epoch_id, batch_cid)` → dict with `status` and `provenance_tag`
  - `is_blocking_authority_active()` → always False
- CRITICAL: `is_blocking_authority_active()` must always return False; tested explicitly as
  constitutional boundary assertion.
- `ilc_core/epoch/` mutations only. No CDL mutation.
- Test count: 12 tests.

---

### Phase 517 — SIM-011 re_admission_boundary calibration (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_sim_011_re_admission_boundary_calibration_517_v0.1.md`
- `tests/test_phase_517_sim_011_re_admission_calibration.py`

Scope:
- Simulation synthesis document modeling validator re-admission scenarios.
- Required outputs: `recommended_cooldown_epochs_liveness_miss`,
  `recommended_cooldown_epochs_equivocation`, `recommended_cooldown_epochs_voluntary_exit`.
- Must contain `sim_011_sufficient` (Phase 518 entry criteria require this token).
- No CDL mutation. No ilc_core/ mutation.
- Test count: 7 tests.

---

### Phase 518 — CDL-058 opening (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_058_re_admission_boundary_opening_stub_518_v0.1.md`
- `tests/test_phase_518_cdl_058_opening_stub.py`
- historicalization patch to `tests/test_phase_517_sim_011_re_admission_calibration.py`
- CDL log mutation (additive CDL-058 row only)

Scope:
- Opens CDL-058 (re_admission_boundary) using Phase 512 scoping + Phase 517 SIM-011 evidence.
- Selected option: cooldown period per exit-reason type, anchored to SIM-011 constants.
- Entry criteria require `sim_011_sufficient` in the Phase 517 synthesis document.
- Must preserve the pre-hardened historical CDL-058 absence checks already landed in the
  Phase 505 / Phase 512 / Phase 513 test suites.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 519 — CDL-058 prelock hardening (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_cdl_058_re_admission_boundary_prelock_hardening_519_v0.1.md`
- `tests/test_phase_519_cdl_058_prelock_hardening.py`

Scope:
- Hardens the CDL-058 lane against scope creep.
- Patches Phase 518 test to use historical CDL-058 open-state read (via commit-anchored git show).
- Locks: three exit-reason types (liveness_miss, equivocation, voluntary_exit), CDL-046
  timed_out orthogonality, CDL-055 dep chain integrity.
- No CDL mutation in Phase 519.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 520 — CDL-058 ratification (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_cdl_058_re_admission_boundary_ratification_evidence_520_v0.1.md`
- `tests/test_phase_520_cdl_058_ratification_evidence.py`
- historicalization patch to `tests/test_phase_519_cdl_058_prelock_hardening.py`
- CDL log mutation (CDL-058 only: open → ratified)

Scope:
- Ratifies the re_admission_boundary lane per evidence ladder.
- CDL-058 moves `open -> ratified`.
- Evidence section 6 heading: `## 6. Section-5 ratification readiness evidence checklist satisfaction`
- Governance tokens: `cdl_058_governs_re_admission_boundary`, `cdl_046_timed_out_orthogonal`,
  `cdl_053_reserved`, `sim_011_calibrated_cooldown_constants`.
- CDL mutation: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=520`.
- Pre-commit split: 5 passed / 2 failed. Post-commit: 7 passed.

---

### Phase 521 — CDL-058 re_admission_boundary runtime (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/validator/re_admission_runtime.py`
- `tests/test_phase_521_re_admission_runtime.py`

Scope:
- New module in existing `ilc_core/validator/` subpackage (additive only).
- `ilc_core/validator/__init__.py`, `staking_liveness_runtime.py`, and `trust_tier_runtime.py`
  must remain unchanged.
- Runtime module exports:
  - `RE_ADMISSION_RUNTIME_VERSION = "re_admission_runtime_521.v0.1"`
  - `CDL_058_DEPENDENCY = "cdl_058_ratified_520.v0.1"`
  - `CDL_055_STAKING_DEPENDENCY` — must equal `staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION`
  - `COOLDOWN_EPOCHS_LIVENESS_MISS` (from SIM-011 recommended constant)
  - `COOLDOWN_EPOCHS_EQUIVOCATION` (from SIM-011 recommended constant)
  - `COOLDOWN_EPOCHS_VOLUNTARY_EXIT` (from SIM-011 recommended constant)
  - `EXIT_REASONS` — frozenset containing exactly `"liveness_miss"`, `"equivocation"`, `"voluntary_exit"`
  - `evaluate_re_admission_eligibility(exit_reason, epochs_since_exit)` → dict with `eligible` and
    `cooldown_remaining`; raises `ValueError` for unrecognized `exit_reason`
- `ilc_core/validator/` mutations only. No CDL mutation.
- Test count: 12 tests.

CRITICAL guard: `EXIT_REASONS` boundary: unrecognized `exit_reason` raises `ValueError` — tested
explicitly as constitutional boundary assertion (mirrors CDL-056 `CONSENSUS_DISPUTE_TYPES` pattern).

---

### Phase 522 — ADR-0023 quality signal CDL scoping analysis (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_adr_0023_cdl_scoping_analysis_522_v0.1.md`
- `tests/test_phase_522_adr_0023_cdl_scoping_analysis.py`

Scope:
- Analytical phase only. No CDL mutation (CDL-059 opening, if recommended, is Window 525+).
- Evaluates whether ADR-0023 quality signal architecture requires constitutional protection or
  can remain ADR/research guidance outside the CDL inventory.
- Output: explicit recommendation — either open CDL-059 (Window 525+) or maintain ADR-0023 as
  research guidance.
- Test count: 7 tests.

---

### Phase 523 — Integration coherence report and capsule v2.5 (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_integration_coherence_report_523_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.5.md`
- `tests/test_phase_523_coherence_report_and_capsule_v2_5.py`

Scope:
- Coherence report covers: CDL-057 runtime integration, SIM-011 calibration, CDL-058 lifecycle,
  ADR-0023 scoping disposition, snapshot isolation.
- Capsule v2.5 supersedes v2.4. §1 required text: "Window 515-524 remains active at Phase 523."
- CDL-058 state handling must remain scenario-aware: either ratified with Phase 521 runtime
  implemented, or deferred as a Window 525+ constitutional/runtime carry-forward.
- No CDL mutation. No ilc_core/ mutation.

---

### Phase 524 — Closure gate and handoff (SENSITIVE — gate + tests)

Deliverables:
- `tools/check_window_515_524_closure_gate_phase_524.sh`
- `docs/specs/ilc_window_515_524_handoff_524_v0.1.md`
- `tests/test_window_515_524_closure_gate_524.py`

Scope:
- 6-category gate: prompt_contract_validation, lane_contract_tests, cross_window_regression,
  mutation_canary, closure_gate_cli_contract, walkthrough_hygiene.
- Lane contract tests: Phases 515-523 (9 tests).
- Cross-window regression: all prior closure gate tests from 307 through 514.
- Selftest chain must include `ILC_PHASE_514_GATE_SELFTEST=1`; verify by reading actual test files.
- Window states: success_path (CDL-057 runtime + CDL-058 ratified + Phase 521 runtime),
  blocked_path (CDL-058 not ratified = deferred carry-forward), invalid
  (CDL-057 runtime absent = fail).
- Snapshot isolation: `ILC_PHASE_524_SNAPSHOT_PATH` override; no canonical `out/monitoring/` mutation.

---

## 5. CDL mutation summary for Window 515-524

| Phase | CDL action |
|---|---|
| 515 | None |
| 516 | None |
| 517 | None |
| 518 | add new CDL-058 row (status: open) |
| 519 | None |
| 520 | CDL-058 status: open → ratified |
| 521 | None |
| 522 | None |
| 523 | None |
| 524 | None |

---

## 6. ilc_core/ mutation summary for Window 515-524

| Phase | ilc_core/ action |
|---|---|
| 515 | None |
| 516 | `ilc_core/epoch/epoch_boundary_witness_runtime.py` (NEW, additive to existing epoch subpackage) |
| 517–520 | None |
| 521 | `ilc_core/validator/re_admission_runtime.py` (NEW, additive to existing validator subpackage) |
| 522–524 | None |

---

## 7. Protected boundaries

The following boundaries must remain intact throughout Window 515-524:

- CDL-053 reserved and unopened.
- CDL-059 (ADR-0023) not opened until Window 525+ (Phase 522 is scoping only).
- CDL-V3 diversity floor protections unchanged.
- 7+1 quorum ladder unchanged.
- ADR-0022 private/gated boundary separate from validator and epoch-boundary work.
- Werner credit lane (CDL-053) separate from re_admission_boundary work.
- `epoch_snapshot_runtime.py` must not be modified by Phase 516.
- `ilc_core/epoch/__init__.py` must not be modified by Phase 516.
- `ilc_core/validator/__init__.py`, `staking_liveness_runtime.py`, and `trust_tier_runtime.py`
  must not be modified by Phase 521.
- Blocking authority for epoch-boundary witnesses remains deferred (CDL-057 provenance-only scope).

---

## 8. Predecessor references

- `docs/specs/ilc_window_505_514_handoff_514_v0.1.md` — Window 505-514 closure (must exist before Phase 515)
- `docs/specs/ilc_antigravity_context_capsule_v2.4.md` — current capsule (superseded by v2.5 at Phase 523)
- `docs/specs/ilc_cdl_058_re_admission_boundary_scoping_512_v0.1.md` — Phase 512 scoping (CDL-058 prerequisites and `sim_011_required` declaration)
- `docs/specs/ilc_epoch_boundary_witness_ratification_evidence_511_v0.1.md` — CDL-057 ratification evidence (provenance-only scope and blocking-authority deferral confirmed)
- `docs/specs/ilc_sim_010_validator_incentive_economics_synthesis_487_v0.1.md` — SIM-010 (staking constants; SIM-011 extends this for re-admission calibration)
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` — ADR-0023 (Phase 522 input)
- `docs/research/ilc_phase_495_504_deep_audit_v0.1.md` — audit M-1 through M-4 findings (Window 505-514 drivers)
