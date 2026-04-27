# ILC Window 873–876 Closure Gate — Phase 876

Status: PASS
Date: 2026-04-27
Phase: 876
Window: 873–876

`window_873_876_closed`
`capsule_v5_24_is_current_frontier`

---

## 1. Hard Pass Condition Verification

From `docs/specs/ilc_phase_873_876_sequence_lock_v0.1.md` §3:

| # | Condition | Status |
|---|-----------|--------|
| 1 | `ilc_core/cli/d2e_submit_cli.py` module exists | ✅ PASS |
| 2 | `D2E_SUBMIT_CLI_VERSION` and `CDL_074_DEPENDENCY` tokens present | ✅ PASS |
| 3 | `handle_submit(args)` calls `validate_truth_primitive_submission` and returns `creates_node`, `edges`, `node_primitive_type` | ✅ PASS |
| 4 | `commit.epoch` submission via CLI returns an error result (not a success) | ✅ PASS |
| 5 | `main.py` registers `submit` as a top-level command and routes to the new module | ✅ PASS |
| 6 | `main.py`'s `PRIMITIVE_COMMANDS` and `OPERATIONAL_COMMANDS` are NOT restructured — existing prototype stubs untouched | ✅ PASS |
| 7 | Tests cover all six valid primitives via CLI, `commit.epoch` rejection, malformed envelope rejection, and dependency token presence | ✅ PASS |
| 8 | Window does NOT implement graph persistence, CID generation, or network delivery | ✅ PASS |

All 8 hard pass conditions satisfied.

---

## 2. Evidence

### 2.1 Module existence and version token

File: `ilc_core/cli/d2e_submit_cli.py`

```python
D2E_SUBMIT_CLI_VERSION = "d2e_submit_cli_874.v0.1"
CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"
```

Import guard validates at module load:
```python
if CDL_074_DEPENDENCY != "cdl_074_truth_primitive_runtime_ratified.v0.1":
    raise ValueError("submit_cli_dependency_mismatch")
```

### 2.2 handle_submit returns graph-output contract

Return structure:
```python
{
    "subcommand": "submit",
    "primitive": result.primitive,          # str
    "creates_node": result.creates_node,    # bool
    "node_primitive_type": result.node_primitive_type,  # str | None
    "edges": [{edge_type, source, target}, ...],
    "graph_persistence": "deferred — Phase 873+ CDL required",
    "version": D2E_SUBMIT_CLI_VERSION,
}
```

### 2.3 commit.epoch rejection

Test `test_handle_submit_commit_epoch_rejected` confirms token
`commit_epoch_agent_submission_rejected` is raised as `SubmitCommandError`.

Subprocess test `test_submit_commit_epoch_via_subprocess_returns_error`
confirms exit code 1 and `ok: false` JSON output.

### 2.4 main.py submit routing

```python
OPERATIONAL_COMMANDS = (
    ...
    "node",
    "submit",    # ← added Phase 874
    "version",
)
```

Dispatch branch:
```python
if command == "submit":
    from ilc_core.cli.d2e_submit_cli import handle_submit, SubmitCommandError
    try:
        data = handle_submit(args)
    except SubmitCommandError as exc:
        raise ValueError(exc.message) from exc
    return _success_payload(command, data)
```

Subparser: `--primitive`, `--payload-json`/`--payload-file` (mutually
exclusive, required), `--agent-id`, `--epoch`, `--sig`.

### 2.5 PRIMITIVE_COMMANDS unchanged

```python
PRIMITIVE_COMMANDS = (
    "assert", "validate", "contradict", "refute", "revise", "link", "epoch",
)
```

No prototype stub modified.  Token: `no_prototype_stub_mutation_in_window_873_876`.

### 2.6 Test count and coverage

22 tests in `tests/test_phase_874_d2e_submit_cli.py` — all pass.

Coverage:
- Six primitives (assert.truth, validate.claim, contradict.assert, link.claim,
  refute.claim, revise.assert): tests 3–8
- commit.epoch rejection: test 9
- Malformed envelope: tests 10–16
- main.py structural: tests 17–18
- Subprocess integration: tests 19–20
- Commit scope guard: tests 21–22

### 2.7 Graph persistence deferred

`handle_submit` performs no LMDB writes, CID generation, or network calls.
`graph_persistence` field in result is explicitly:
`"deferred — Phase 873+ CDL required"`.

Token: `no_graph_persistence_in_window_873_876`.

---

## 3. Snapshot Isolation

No CDL mutation occurred in Window 873–876.  CDL master log is unchanged.

No new CDL was opened.  Token: `no_new_cdl_in_window_873_876`.

---

## 4. Exclusion Token Satisfaction

```
no_graph_persistence_in_window_873_876         SATISFIED
no_new_cdl_in_window_873_876                   SATISFIED
no_prototype_stub_mutation_in_window_873_876   SATISFIED
no_m009_change_in_window_873_876               SATISFIED
```

---

## 5. Window Closure Declaration

Window 873–876 is hereby **CLOSED**.

Capsule v5.24 is the current frontier capsule.

`window_873_876_hard_pass_condition` — ALL SATISFIED
`window_873_876_closed`
`capsule_v5_24_is_current_frontier`
