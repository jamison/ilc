# ILC Test Inventory

Status: Phase 1545p-Fix2 support inventory.

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
