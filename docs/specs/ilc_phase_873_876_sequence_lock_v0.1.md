# ILC Phase 873–876 Sequence Lock v0.1

Status: locked
Date: 2026-04-27
Phase: 873
Owner lane: CLI truth primitive submission — CDL-074 wire-up

`window_873_876_sequence_lock`
`cli_submit_command_window_commissioned`
`cdl_074_runtime_precedes_cli_submit_wiring`

---

## 1. Window Purpose

Window 873–876 wires the CDL-074 truth primitive submission runtime into the
existing ILC CLI (`ilc_core/cli/main.py`), giving agents and operators a
`submit` command that validates a CDL-073 wire-format submission and returns
the graph-output contract.

This window does NOT require a new CDL — it is an implementation extension
of the CDL-042 CLI framework (Phase 420) using the CDL-074 runtime (Phase 868).

---

## 2. Prerequisite State

| Item | Status at Window Open |
|------|-----------------------|
| CDL-042 | Ratified (Phase 407) — CLI framework |
| CDL-074 | Ratified (Phase 870) — truth primitive submission runtime |
| `truth_primitive_submission_runtime.py` | Deployed (Phase 868) |
| Existing primitive stubs (`assert`, `validate`, …) | Prototype stubs — unchanged by this window |
| Graph persistence | Not yet deployed — Phase 873+ separate CDL |

---

## 3. Hard Pass Condition

Window 873–876 passes only if ALL of the following are true:

1. A new `ilc_core/cli/d2e_submit_cli.py` module exists.
2. `D2E_SUBMIT_CLI_VERSION` and `CDL_074_DEPENDENCY` tokens present.
3. `handle_submit(args)` calls `validate_truth_primitive_submission` and
   returns a JSON-serialisable result dict containing `creates_node`, `edges`,
   and `node_primitive_type`.
4. `commit.epoch` submission via CLI returns an error result (not a success).
5. `main.py` registers `submit` as a top-level command and routes to the new module.
6. `main.py`'s `PRIMITIVE_COMMANDS` and `OPERATIONAL_COMMANDS` are NOT
   restructured — the existing prototype stubs are untouched.
7. Tests cover all six valid primitives via CLI, `commit.epoch` rejection,
   malformed envelope rejection, and dependency token presence.
8. The window does NOT implement graph persistence, CID generation, or network
   delivery — `submit` validates and returns the contract only.

`window_873_876_hard_pass_condition`

---

## 4. Phase Map

| Phase | Topic | Deliverable |
|-------|-------|-------------|
| 873 | Sequence lock | This document |
| 874 | `d2e_submit_cli.py` + `main.py` wiring + tests | Working `submit` command; tests |
| 875 | Coherence report + capsule v5.24 | Coherence report 875; capsule v5.24 |
| 876 | Closure gate | Gate document; window closed |

---

## 5. Scope Boundaries

This window DOES:
- Add `ilc_core/cli/d2e_submit_cli.py` (new file).
- Add `submit` to the CLI command surface in `main.py`.
- Wire `validate_truth_primitive_submission` into the CLI dispatch path.

This window does NOT:
- Implement graph persistence, CID generation, or LMDB storage.
- Implement network-layer delivery.
- Modify the prototype primitive stubs (`assert`, `validate`, etc.).
- Open a new CDL.
- Change M-009.

---

## 6. Exclusion Tokens

```
no_graph_persistence_in_window_873_876
no_new_cdl_in_window_873_876
no_prototype_stub_mutation_in_window_873_876
no_m009_change_in_window_873_876
```
