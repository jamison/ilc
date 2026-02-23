# ILC Phase 270-279 Sequence Lock v0.1

Status: Locked (Phase 270)
Date: 2026-02-22
Owner lane: G8 Constitution Cluster A

## 1. Purpose and sequence scope

Lock the dependency-ordered sequence for phases 270 through 279 for the issuance-governance closure window.

This lock governs ordering, dependencies, sensitivity classification, and mandatory gate composition.
It does not mutate Constitutional Decision Log rows and does not change runtime behavior.

## 2. Entry state from Phase 269 handoff

Entry baseline from `docs/specs/ilc_cdl_ratification_window_260_269_handoff_v0.1.md`:
- ratified CDLs: `CDL-001`, `CDL-002`, `CDL-007`, `CDL-032`, `CDL-025`, `CDL-019`,
- open issuance queue: `CDL-026`, `CDL-027`, `CDL-028`, `CDL-029`, `CDL-030`, `CDL-031`,
- `CDL-031` is unblocked by `CDL-019` closure and remains deferred,
- cross-window gate continuity anchor: `tools/check_cdl_ratification_verification_gate_phase_269.sh`,
- carry-forward regression files:
  - `tests/test_cdl_032_ratification_253.py`
  - `tests/test_security_cdl_ratification_251.py`
  - `tests/test_cdl_025_ratification_267.py`
  - `tests/test_cdl_019_ratification_268.py`

## 3. Locked phase table (270-279)

| Step | Phase | Lane type | Objective | Dependencies | Exit gate |
| --- | --- | --- | --- | --- | --- |
| 1 | 270 | `sequence-lock` | Lock 270-279 ordering and sensitivity map. | Phase 269 closure complete. | Sequence lock artifact + tests pass. |
| 2 | 271 | `issuance-evidence-closure-B` | Evidence closure for CDL-029, CDL-026, CDL-028. | Phase 270 complete. | Evidence-closure tests pass. |
| 3 | 272 | `cdl-ratification` | CDL-029 allocation split ratification. | Phases 270, 271 complete. | Ratification tests + mutation-scope checks pass. |
| 4 | 273 | `cdl-ratification` | CDL-026 C_max lock ratification. | Phase 272 complete. | Ratification tests + mutation-scope checks pass. |
| 5 | 274 | `cdl-ratification` | CDL-028 fee-burn split ratification. | Phase 273 complete. | Ratification tests + mutation-scope checks pass. |
| 6 | 275 | `issuance-evidence-closure-C` | Evidence closure for CDL-027 and CDL-030 methodology. | Phase 274 complete. | Evidence-closure tests pass. |
| 7 | 276 | `cdl-ratification` | CDL-027 decay formulation ratification. | Phase 275 complete. | Ratification tests + mutation-scope checks pass. |
| 8 | 277 | `cdl-ratification` | CDL-030 ECU price clamp ratification. | Phase 276 complete. | Ratification tests + mutation-scope checks pass. |
| 9 | 278 | `integration-doc` | Coherence report and context capsule v0.6. | Phase 277 complete. | Integration coherence tests pass. |
| 10 | 279 | `ratification-verification-gate + handoff` | Compose verification for phases 272-277 and publish 280+ handoff. | Phase 278 complete. | Verification gate dry-run/full-run pass. |

Fix-pack dependency inside Step 5:
- before executing sensitive Phase 274 ratification, complete `Phase 274-fix1` (non-sensitive) candidate simulation prelock and produce:
  - `docs/specs/ilc_cdl_028_fee_burn_split_candidate_lock_274_fix1_v0.1.md`,
  - `tests/test_cdl_028_fee_burn_candidate_lock_274_fix1.py`.

## 4. Per-phase sensitivity classification

| Phase | Classification |
| --- | --- |
| 270 | non_sensitive |
| 271 | non_sensitive |
| 272 | sensitive |
| 273 | sensitive |
| 274 | sensitive |
| 275 | non_sensitive |
| 276 | sensitive |
| 277 | sensitive |
| 278 | non_sensitive |
| 279 | sensitive |

## 5. CDL dependency map and ratification ordering

Dependency map:
- `CDL-029` is unblocked and can be ratified first,
- `CDL-026` depends on `CDL-025` (already closed),
- `CDL-028` depends on `CDL-025` (already closed),
- `CDL-027` depends on `CDL-026`,
- `CDL-030` depends on `CDL-027`,
- `CDL-031` is unblocked by `CDL-019` but deferred to Phase 280+.

Locked ordering in this window:
1. `CDL-029`
2. `CDL-026`
3. `CDL-028`
4. `CDL-027`
5. `CDL-030`

`CDL-031` is explicitly excluded from ratification in phases 270-279.

## 6. Mandatory entry/exit gates per phase lane

- all sensitive lanes (272, 273, 274, 276, 277, 279) must begin with:
  - `bash tools/check_cdl_ratification_verification_gate_phase_269.sh`,
  - `python3 -m pytest tests/test_ratification_mutation_scope_261.py -q`,
  - cross-phase regression suites from 251/253/267/268.
- sensitive Phase 274 ratification must additionally require Phase 274-fix1 candidate lock test:
  - `python3 -m pytest tests/test_cdl_028_fee_burn_candidate_lock_274_fix1.py -q`.
- ratification lanes must use phase-scoped non-target assertions (`ratified_phase != <phase>`),
  not `status == open` checks.
- evidence-closure lanes (271, 275) are non-ratifying and must include explicit decision-log non-mutation boundaries.
- phase 279 gate must compose prior-window gate and current-window ratification tests.

## 7. Non-goals and out-of-scope boundaries

- no decision-log row status changes are performed in Phase 270,
- no runtime implementation changes in `ilc_core/`,
- no issuance policy values are ratified in Phase 270,
- `CDL-031` ratification is out of scope for phases 270-279 and deferred to Phase 280+.

## 8. Forward pointer

Next-window opening target (Phase 280+):
- dedicated `CDL-031` ranking-policy evidence and ratification lane,
- `CDL-033` OpenClaw skill contract lane,
- ADM-003 reference architecture lane,
- D2e-04+ implementation lanes.
