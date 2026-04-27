# ILC Integration Coherence Report — Phase 875

Status: final
Date: 2026-04-27
Window: 873–876
Phase: 875

---

## 1. Purpose

This report verifies that Window 873–876 is internally coherent and that no
new cross-cutting concerns have been introduced by wiring the CDL-074 truth
primitive submission runtime into the ILC CLI.

---

## 2. Scope of Changes

| File | Role |
|------|------|
| `docs/specs/ilc_phase_873_876_sequence_lock_v0.1.md` | Window sequence lock (Phase 873) |
| `ilc_core/cli/d2e_submit_cli.py` | Submit command handler (Phase 874) |
| `ilc_core/cli/main.py` | Submit command routing (Phase 874) |
| `tests/test_phase_874_d2e_submit_cli.py` | 22 tests (Phase 874) |

---

## 3. Coherence Checks

### 3.1 CDL-042 framework integrity preserved

`PRIMITIVE_COMMANDS` and `OPERATIONAL_COMMANDS` in `main.py` are unchanged
except for the addition of `"submit"` to `OPERATIONAL_COMMANDS`.  No prototype
stub has been modified.  The existing command dispatch pattern (lazy import,
`_run_top_level_command`) is strictly extended.

Token: `no_prototype_stub_mutation_in_window_873_876` satisfied.

### 3.2 CDL-074 dependency locked at boundary

`d2e_submit_cli.py` declares:

```python
CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"
```

and validates this token at module import time.  Any future change to the
CDL-074 runtime contract will break this guard.

### 3.3 Graph persistence correctly deferred

`handle_submit` returns:
```python
"graph_persistence": "deferred — Phase 873+ CDL required"
```

No LMDB writes, CID generation, or network delivery occur in this window.

Token: `no_graph_persistence_in_window_873_876` satisfied.

### 3.4 No new CDL opened

This window does not open a CDL.  It is an implementation extension of
CDL-042 (Phase 420) using the CDL-074 runtime (Phase 868).

Token: `no_new_cdl_in_window_873_876` satisfied.

### 3.5 commit.epoch rejection is unconditional

`handle_submit` delegates to `validate_truth_primitive_submission`, which
rejects `commit.epoch` before any payload validation with token
`commit_epoch_agent_submission_rejected`.  Test 9 of Phase 874 confirms this.

### 3.6 Test coverage

22 tests in `test_phase_874_d2e_submit_cli.py` pass:
- All six agent-issuable primitives via `handle_submit` (6 tests)
- commit.epoch rejection (1 test)
- Malformed envelope paths: unknown primitive, missing primitive, missing
  agent_id, invalid epoch, ambiguous payload, file not found, valid file (7 tests)
- main.py structural checks (2 tests)
- Subprocess integration: no graph-state pollution (2 tests)
- Phase 874 commit scope guard (2 tests)

### 3.7 Graph-state exemption behaviour

`submit` is NOT in the graph-state exempt set
`{"query", "verify", "bundle", "agent", "node"}`, which means
`_ensure_local_graph_state` is called.  This creates (or updates) the local
graph JSON file with `last_command: "submit"` but adds NO nodes or edges.
The subprocess integration test confirms the file contains no submission data.

---

## 4. Forward Obligations Closed

| Obligation | Status |
|------------|--------|
| CLI truth primitive submission (forward-obligation from Window 863–872) | CLOSED — Phase 874 |

---

## 5. Open Forward Obligations Carried Forward

| Obligation | Next window |
|------------|-------------|
| Graph persistence for truth primitives (LMDB, CID generation) | Phase 877+ — CDL-075 required |
| Network delivery layer for submissions | Phase 877+ |

---

## 6. Coherence Verdict

Window 873–876 is coherent.  All scope boundaries observed.  All exclusion
tokens satisfied.  22 new tests pass.  No regressions introduced.

`window_873_876_coherence_verified`
