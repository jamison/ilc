# ILC External Audit Rubric for Assistant Reviewers v0.1

Status: working audit rubric (non-normative)
Date: 2026-03-05
Purpose: raise review quality for phase execution audits (Codex, Gemini, Sonnet, other assistants)

## 1. Severity model

- Critical: security/integrity failure, constitutional violation, or silent correctness corruption.
- Moderate: architectural or operational defect that can pass tests but causes real risk.
- Low: quality, clarity, or maintainability issue with bounded risk.

Rule: every reported issue must include severity and why it matters to system behavior.

## 2. Required review lenses (always run all)

### A. Constitutional and scope compliance
- Verify phase scope boundaries are respected.
- Confirm out-of-scope files were not touched.
- Confirm decision log mutation rules were respected.

### B. Runtime mutation-scope integrity
- Confirm commit-anchored tests enforce allowed `ilc_core/` paths only.
- Confirm forbidden runtime prefixes remain untouched.

### C. Determinism and interoperability
- Reject order-sensitive dict/JSON validation contracts where semantic order is not guaranteed.
- Require set/field presence checks for schema validation and canonicalization for hashing.
- Confirm deterministic tokenized error surfaces.

### D. Operational reliability
- Check canary side-effect recovery behavior.
- Check phase scripts for explicit cleanup and clean-tree assertions.
- Flag intermittent or race-prone pass/fail behavior.

### E. Performance and baseline strategy
- Verify deep baseline caching actually reuses a shared batch key.
- Flag prompt key drift that defeats batching.
- Check cache invalidation semantics for blind spots (for example untracked files excluded from hash).

### F. Artifact and evidence quality
- Verify walkthrough commands and outputs match what actually ran.
- Verify status/backfill language is precise and not overstated.
- Verify handoff tokens are exact and complete.

## 3. Mandatory checks for phases with runtime implementation

1. Pre-commit split behavior
- Verify expected `N passed, 2 failed` commit-anchored pattern before main commit.

2. Post-commit closure
- Verify all runtime tests pass after commit.
- Verify no decision-log drift.

3. Cross-phase resilience
- Run required prior-phase regression suite.
- Confirm recovery path exists and is documented if canary contaminates worktree.

4. Interop guard
- Ensure schema validators do not require key insertion order.

## 4. Known recurring pitfalls (must explicitly inspect)

1. Key-order coupling bugs
- Example pattern: `tuple(payload.keys()) == EXPECTED_FIELDS`.
- Risk: rejects valid payloads from different runtimes/serializers.

2. Baseline cache key fragmentation
- Risk: each phase misses cache and reruns expensive deep gates.

3. Cache blind spots
- Risk: cache hit while untracked artifacts changed behavior.

4. Canary residual mutations
- Risk: false failures and long rerun cycles from dirty `ilc_core/security/*` files.

## 5. Minimum output format for each audit

For every finding, include:
- Severity
- Path and line reference
- Observed behavior
- Why it matters
- Concrete remediation
- Whether it blocks next phase execution

If no findings:
- State explicitly "No findings" and list residual risks checked.

## 6. Example finding format

- Moderate — `ilc_core/node/node_dissemination_runtime_362.py:258`
  - Observed: header validation depends on key insertion order.
  - Risk: valid cross-language payloads may be rejected.
  - Fix: validate required field set independent of order; preserve canonical hashing separately.
  - Blocker: no (should be queued for hardening window).

## 7. Audit quality bar

A review is incomplete if it only checks token presence and test pass/fail.

A complete review must assess:
- semantic correctness,
- operational robustness,
- interoperability behavior,
- and performance implications of execution policy.
