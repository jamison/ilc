# ILC Genesis Integration Smoke Contract v0.1

Status: Drafted in Phase 224
Date: 2026-02-18
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Define deterministic end-to-end smoke expectations for Genesis packaging readiness by validating that the composed node-value, reward, and governance surfaces operate coherently on one self-contained scenario.

## 2. Required smoke surfaces

The integration smoke test must execute these real surfaces together (no mocks/stubs):
- `compute_node_scores` (node-value kernel with diversity and freshness inputs)
- `allocate_rewards_with_governor` (reward allocation and refutation profitability invariant)
- `evaluate_node_value_governance_conformance` (phase-219 consolidated conformance)
- `evaluate_genesis_accrual_governor` (phase-218 taper/cap checks)

## 3. Deterministic scenario requirements

The scenario must be constructed inline in one test file and include:
- three Genesis axioms (`is_genesis = True`),
- at least four non-Genesis claims,
- at least three distinct non-Genesis agents,
- at least one refutation,
- one concentrated reuse pattern,
- one diversified reuse pattern,
- age variation with non-Genesis claims at `age >= 5` and younger peers.

No fixture imports from other test modules are allowed.

## 4. Required invariant assertions

Smoke test assertions must include:
1. Genesis axiom freshness is exactly `1.0`.
2. Diversified reuse case yields higher scored utility than concentrated reuse case under comparable base context.
3. Refuter reward exceeds validator reward for equivalent work on same pairing key.
4. Freshness gate is monotonic for comparable non-Genesis age ordering.
5. Genesis accrual governor output is bounded (`0 <= taper_multiplier <= 1`) and hard-cap respecting (`theta_hard = 1/20`).
6. Consolidated conformance report returns `overall_ok = True`.
7. Score rows match the locked phase-219 schema key set.
8. Total reward distribution does not exceed epoch budget.

## 5. Install-import smoke requirement

A separate smoke test must prove post-install API importability by:
- creating an isolated virtual environment,
- running `pip install .` from repository root,
- importing `evaluate_node_value_governance_conformance` from
  `ilc_core.analysis.node_value_governance_conformance`.

This install smoke is importability-only and does not rerun full integration assertions.

## 6. Gate command contract

`tools/check_genesis_integration_smoke_phase_224.sh` must support:
- `--dry-run`,
- `--help`/`-h`,
- unknown argument exit code `2`.

The gate executes:
1. integration smoke test,
2. install-import smoke test,
3. focused phase-219/212/218 regression subset.

## 7. Non-goals

- No new economic formula introduction.
- No governance constant changes.
- No decision-log mutations.
- No packaging/release artifact generation (covered in later phases).
