# ILC Track 1 Edge Removal Closure Handoff Plan v0.1

## Context

Track 1 completed a controlled migration from legacy edge-list usage to canonical link/indexed graph surfaces and then enforced closure guardrails across production and test code. This handoff plan records what is now closed, what remains guarded, and how follow-on phases should sequence work without reopening Track 1 debt.

## Closed Guarantees

- No direct `.edges.append(` usage in `ilc_core` or `tests`.
- No `Edge` symbol import or constructor usage in `ilc_core` or `tests`.
- Public `.edges` attribute surface remains removed from runtime graph access paths.
- Track 1 closure is backed by full-suite green regression evidence and dedicated guardrail tests.

## Active Guardrails

- `tests/test_edge_removal_phase1_guardrails.py`
  - forbids direct append usage via deterministic pattern checks.
  - forbids `Edge` symbol usage via deterministic pattern checks.
  - enforces `.edges` attribute allowlist constraints.
- `tests/test_graph_edges.py`
  - contains the explicit closure sentinel asserting public `graph.edges` access is removed.
- `docs/specs/ilc_edge_removal_track1_phase1_baseline_v0.1.md`
  - defines active closure policy and deterministic inventory commands.

## Residual Sentinels

- `.edges` literal strings may appear in guardrail tests for detection messaging.
- One explicit sentinel access in `tests/test_graph_edges.py` is intentionally retained to prove the removal contract remains enforced.
- Guardrail allowlists should remain minimal and explicit.

## Reopen Conditions

Track 1 should be reopened only if one or more of the following is required:

- a protocol or persistence requirement demands reintroducing a public edge-list runtime API,
- compatibility with an external consumer requires an edge-list surface that cannot be represented by current link/indexed APIs,
- measurable performance regressions require controlled data-structure redesign that touches link/index internals.

If reopened, require:

- a versioned phase prompt with explicit rollback criteria,
- guardrail updates first,
- deterministic regression and closure evidence before merge.

## Next-Phase Ordering

Immediate recommended next phase:

- Phase 982: post-Track-1 handoff execution for non-Track-1 workstreams, starting with typed contract sustainment and residual consolidation in modules actively under change.

Dependency constraints:

- keep Track 1 guardrail tests in the mandatory regression subset for every follow-on phase touching graph or replay-proof flows,
- do not weaken allowlists without an explicit migration phase and approval,
- preserve sentinel assertions in `tests/test_graph_edges.py` until a deliberate policy update lands.

Do-not-break inherited contracts:

- no direct `.edges.append(` usage,
- no `Edge` symbol usage,
- no public runtime `.edges` attribute surface.

## Risk Notes

- Risk: accidental reintroduction through test helpers or utility modules.
  - Mitigation: retain guardrail scans and AST-based attribute checks.
- Risk: broad refactors that bypass closure checks by narrowing test subsets.
  - Mitigation: keep full `python3 -m pytest -q` as the closure-level gate for track-adjacent changes.
- Risk: policy drift between docs and tests.
  - Mitigation: update baseline and guardrail wording together in the same phase commit.
