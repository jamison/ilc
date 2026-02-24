# ILC Mutation Canary Gate Contract 297 v0.1

Status: Phase-297 verification infrastructure artifact  
Date: 2026-02-24  
Owner lane: G8 Constitution Cluster A

## 1. Purpose and boundary

Define a deterministic mutation-canary gate that validates test-strength invariants by injecting representative faults and confirming targeted tests fail.

This artifact is verification-only and non-ratifying.

## 2. Probe inventory and target tests

Required probes:

1. **lineage_rotated_authority_guard**
   - Mutation surface: `ilc_core/security/signer_lineage_runtime.py`
   - Injected change: authorize `ROTATED` state in canonical authority check.
   - Target test:
     - `tests/test_cdl_001_signer_lineage_runtime.py::TestVerifyCanonicalAuthorityStateGating::test_verify_canonical_authority_rejects_rotated_state`

2. **compromise_containment_sequence_order_guard**
   - Mutation surface: `ilc_core/security/key_compromise_runtime.py`
   - Injected change: swap containment action order.
   - Target test:
     - `tests/test_cdl_002_key_compromise_runtime.py::TestContainmentActionSequencing::test_containment_sequence_is_strict_and_ordered`

3. **non_target_phase_stamp_poisoning_guard**
   - Mutation surface: `docs/specs/ilc_constitutional_decision_log_v0.1.md`
   - Injected change: phase-stamp non-target row with `ratified_phase: 277`.
   - Target test:
     - `tests/test_cdl_030_ratification_277.py::test_non_target_rows_not_ratified_in_phase_277`

## 3. Mutation execution safety rules

- Probes run strictly one at a time.
- Each probe stores original file contents before mutation.
- Restoration runs in `finally` block, even if mutation execution or target test fails.
- Any restoration failure is treated as gate failure.
- Gate never commits probe mutations.

## 4. CLI contract

Script: `tools/run_mutation_canary_phase_297.py`

CLI requirements:
- `--help`: print usage and available probes, exit `0`.
- `--dry-run`: print probe plan and target test commands, do not mutate files, exit `0`.
- unknown argument: print error to stderr, exit `2`.
- full run (no args): execute all probes in deterministic order and print per-probe outcomes.

## 5. Pass/fail criteria

Pass criteria:
- all required probes report `MUTATION_KILLED`,
- all probe target tests exit non-zero under mutation,
- all mutated files are restored to original content.

Fail criteria:
- any probe reports `MUTATION_SURVIVED`,
- any probe setup/restore operation fails,
- runner receives invalid CLI input.

## 6. Non-goals

This contract does not:
- change runtime production behavior,
- mutate constitutional decision outcomes,
- replace full property-based mutation testing frameworks.

## 7. Canonical anchors

- `docs/reviews/meta_test_mutation_strength_audit_2026_02_24.md`
- `ilc_core/security/signer_lineage_runtime.py`
- `ilc_core/security/key_compromise_runtime.py`
- `tests/test_cdl_001_signer_lineage_runtime.py`
- `tests/test_cdl_002_key_compromise_runtime.py`
- `tests/test_cdl_030_ratification_277.py`
