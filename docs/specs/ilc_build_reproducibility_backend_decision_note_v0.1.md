# ILC Build Reproducibility Backend Decision Note v0.1

Status: Phase-230 decision note
Date: 2026-02-19
Related roadmap tasks: D1-01, D1-02, D1-03, D1-04

## 1. Decision

Retain the current backend for the D1 baseline:
- build backend: `setuptools.build_meta`
- build front-end: `python -m build`

No backend migration (for example to Hatch or Flit) is performed in Phase 230.

## 2. Rationale

1. Current backend is already wired into successful Phase-228 artifact builds and installation tests.
2. D1 objective is deterministic same-platform rebuild assurance, not backend replacement.
3. Backend migration would add uncontrolled scope and complicate root-cause attribution if reproducibility fails.
4. The deterministic-build gate provides measurable evidence independent of backend-brand preference.

## 3. Constraints and boundaries

- Determinism target in this phase is same-platform, same-commit reproducibility.
- Cross-platform bit-for-bit equivalence is explicitly out of scope for D1.
- Runtime behavior under `ilc_core/` is out of scope.

## 4. Re-evaluation triggers

Revisit backend choice if any of the following occurs:
1. deterministic rebuild gate fails under controlled same-platform conditions,
2. packaging features required by D2+ are blocked by current backend,
3. supply-chain/security policy requires backend migration.

## 5. Implementation anchor

- `tools/check_reproducible_build.sh` enforces `SOURCE_DATE_EPOCH=0` and two-build checksum comparison.
- `tests/test_reproducible_build_phase_230.py` enforces gate/script and contract/documentation shape.
