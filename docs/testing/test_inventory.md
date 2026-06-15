# ILC Test Inventory

Status: Phase 1545p-Fix3 support inventory.

This document describes the current test suite at a broad operational level. It
is not a per-test-function catalog. The authoritative executable policy is in
`tests/conftest.py`; the package-level marker declarations are in
`pyproject.toml`.

## Default Current Regression Suite

Run:

```bash
.venv/bin/python -m pytest tests/ -q
```

The default suite is intended to cover current runtime behavior, current
planning-frontier checks, current guardrails, and current integration scaffolds.
As of Phase 1545p-Fix2, default collection skips two opt-in categories:
historical phase snapshots and expensive release-artifact proofs.

Default-suite files include these broad families:

- Runtime unit tests for `ilc_core/` economics, validator, graph, bundle,
  sidecar, network, privacy, governance, and schema modules.
- Current phase and window tests for the active pre-public-RC frontier.
- Static guardrail tests for sensitive runtime coding taboos.
- Integration and rehearsal tests that are deterministic and cheap enough for
  normal local execution.
- Planning and obligation-register tests that assert current frontier state.

## Historical Phase-Snapshot Tests

Marker: `historical_phase_snapshot`

Opt-in:

```bash
ILC_RUN_HISTORICAL_PHASE_SNAPSHOT_TESTS=1 .venv/bin/python -m pytest tests/ -q
```

These files assert old phase/window state, old planning-index text, old capsule
frontiers, or old closure-gate snapshots. They remain useful as archival
evidence, but they are not reliable current-regression signals after later
windows intentionally supersede the same docs and tokens.

Default behavior: skipped unless
`ILC_RUN_HISTORICAL_PHASE_SNAPSHOT_TESTS=1`.

The file allowlist lives in
`tests.conftest.HISTORICAL_PHASE_SNAPSHOT_TEST_FILES`.

## Expensive Release-Artifact Tests

Marker: `expensive_release_artifact`

Opt-in:

```bash
ILC_RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS=1 .venv/bin/python -m pytest tests/ -q
```

These files perform release-artifact build, install, or reproducibility proofs
that are useful but too expensive or environment-sensitive for routine default
regression. They stay runnable under explicit operator intent.

Default behavior: skipped unless
`ILC_RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS=1`.

The file allowlist lives in
`tests.conftest.EXPENSIVE_RELEASE_ARTIFACT_TEST_FILES`.

## Sensitive Closure Selftests

Some sensitive closure gates require an explicit phase-local selftest
environment variable such as `ILC_PHASE_1545P_GATE_SELFTEST=1`. These tests may
also be historical snapshots if the phase has closed and later windows have
advanced. The phase prompt or walkthrough is the authoritative source for each
selftest variable.

Default behavior: usually skipped or inactive unless the phase-specific
selftest variable is set.

## Security And Coding-Taboo Guardrails

Run:

```bash
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
```

The checker enforces the repo-local AGENTS.md guardrails on selected sensitive
runtime surfaces: no wall-clock protocol time, no predictable PRNG in runtime
paths, no production `assert` enforcement, mandatory network timeouts, TLS
verification defaults, bounded fetch/archive behavior, atomic-write patterns,
and canonical JSON requirements on machine-verifiable surfaces.

The pytest wrapper for the same policy is
`tests/test_sensitive_runtime_coding_taboos.py`.

## Phase Prompt Validation

Run a specific prompt validation with:

```bash
.venv/bin/python tools/validate_phase_prompt.py docs/antigravity_tasks/<prompt>.md
```

These checks validate phase-prompt schema discipline. They are not runtime
correctness tests; they prevent prompt drift before implementation.

## Idea-Descent Rehearsal Tests

Run:

```bash
.venv/bin/python -m pytest tests/test_phase_1546p_idea_descent_rehearsal_sidecar.py tests/test_idea_descent_phase_prompt_loop.py tests/test_idea_descent_genesis_star_map_loop.py -q
```

These tests cover the local-only protocol-governed refinement sidecar, the
phase-prompt schema demonstration loop, and the Genesis star-map candidate
refinement loop. The Genesis evaluator checks the v0.3 star-map candidate
against required Genesis Agent 1 authority nodes, the seven truth primitives,
edge endpoint closure, decomposition recipes, and signed-candidate hash
discipline. These tests do not authorize graph writes, signing, public serving,
Window 1546p opening, or public RC publication.

## Rust Consensus Tests

Rust consensus tests are separate from the Python `pytest tests/` suite. Run
them from the Rust workspace or with the phase-specific command named in the
current prompt/walkthrough, for example:

```bash
cd ilc_consensus
cargo test
```

Rust tests cover validator/session-pool, relay-routing, QUIC smoke, and related
consensus substrate behavior when the relevant crates and toolchain are present.

## Simulations And Research Harnesses

Simulation files under `simulations/`, `docs/sims/`, and selected `tests/`
modules validate parameter studies, topology-pressure evidence, economic
calibration, or research-support claims. Whether a simulation is part of the
default current suite depends on runtime cost and whether the result is current
evidence or historical evidence.

## Policy Rule

If a test is always skipped on purpose, keep it only when all three are true:

- It has evidentiary or regression value.
- It has a clear opt-in path.
- Its skip reason names the gate or historical boundary.

Remove or rewrite tests that are dead, permanently unrunnable, or asserting
superseded state without archival value.

## Future Homoiconic Test Registry

Forward plan:
`docs/specs/ilc_homoiconic_test_registry_forward_plan_v0.1.md`

Implementation guidance:
`docs/specs/ilc_homoiconic_test_registry_implementation_guidance_v0.1.md`

Phase 1545p-Fix32 contract:
`docs/specs/ilc_homoiconic_test_registry_contract_1545p_fix32_v0.1.md`

Phase 1545p-Fix32 implementation route:
`docs/specs/ilc_homoiconic_test_registry_implementation_route_1545p_fix32_v0.1.md`

The current test suite is still organized around local `pytest` execution.
The planned homoiconic model keeps `pytest` as an executor, but moves test
discovery and evidence semantics into graph nodes and typed edges.

The intended transition is:

- test files become graph nodes with `TESTS` edges;
- test functions become graph nodes with `pytest_nodeid`, marks, executor
  profile, fixture dependencies, expected invariants, and target coverage;
- test runs emit canonical evidence nodes;
- graph queries answer which tests validate a runtime, spec, ADR, CDL, or Atlas
  node;
- `pytest <path>::<test_name>` remains one concrete executor command resolved
  from the graph.

The planned pytest sidecar has two implementation modes before any native pytest
plugin work:

- registry mode resolves graph-selected test nodes to local pytest commands;
- graph-hydrated workspace mode verifies graph/source-tree digests before
  executing pytest in a temporary workspace.

This future registry is planning-only until a later phase implements a
collector, evidence envelope, and graph-derived test frontier report.
