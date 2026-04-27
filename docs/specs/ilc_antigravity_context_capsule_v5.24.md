# ILC Antigravity Context Capsule v5.24

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.23.md
Date: 2026-04-27
Owner lane: Window 873–876 — CLI truth primitive submission

`capsule_v5_24_supersedes_v5_23`
`window_873_876_closed_recorded_in_capsule_v5_24`
`cli_submit_command_window_commissioned_recorded_in_capsule_v5_24`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 873–876 — COMPLETE.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 873 | Sequence lock | Window 873–876 commissioned |
| 874 | `d2e_submit_cli.py` + `main.py` wiring + tests | Working `submit` command; 22 tests |
| 875 | Coherence report + capsule v5.24 | This phase |
| 876 | Closure gate | Gate document; window closed |

**Previous windows:**
- Window 863–872 COMPLETE. CDL-074 ratified (Phase 870). 229 tests.
- Window 853–862 COMPLETE. CDL-073 ratified. HB-001/003 CLOSED.

---

## 2. Option B Status (unchanged from v5.23)

`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`

Graduation checklist: v0.3 — `all_rows_satisfied=true`.

---

## 3. CDL Status

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-017 | Ratified | 765 | — |
| CDL-042 | Ratified | 407 | CLI framework — extended by Window 873–876 |
| CDL-043 | Ratified | 395 | **Tier 2 (CDL-071)** |
| CDL-044 | Ratified | 399 | **Tier 2 (CDL-071)** |
| CDL-052 | Ratified | 466 | Epistemic mode routing — intact, unchanged |
| CDL-068 | Ratified | 743 | — |
| CDL-069 | Ratified | 838j | — |
| CDL-070 | Deferred | — | PQ migration; SIM-MONETARY-01 prerequisite |
| CDL-071 | Ratified | 851 | Temporal tier reconciliation |
| CDL-072 | Ratified | 846 | Bound B formula amendment |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime — six agent-issuable primitives |
| CDL-V1 | Ratified | 330 | **Tier 2 (CDL-071)** |

CDL-070 remains the only deferred CDL with defined scope.
No new CDL was opened in Window 873–876.

---

## 4. Window 873–876 Deliverable

**New module:** `ilc_core/cli/d2e_submit_cli.py`

```python
D2E_SUBMIT_CLI_VERSION = "d2e_submit_cli_874.v0.1"
CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"

def handle_submit(args: argparse.Namespace) -> dict[str, Any]:
    # builds CDL-073 envelope {v:1, primitive, agent_id, epoch, payload, sig}
    # calls validate_truth_primitive_submission(envelope)
    # returns: {subcommand, primitive, creates_node, node_primitive_type,
    #           edges, graph_persistence, version}
```

**main.py extension:**
- `"submit"` added to `OPERATIONAL_COMMANDS`
- Submit subparser: `--primitive`, `--payload-json`/`--payload-file` (mutex),
  `--agent-id`, `--epoch`, `--sig`
- Dispatch branch: `command == "submit"` → lazy import `d2e_submit_cli`

**Test coverage:** 22 tests in `tests/test_phase_874_d2e_submit_cli.py`
- All six agent-issuable primitives via `handle_submit`
- `commit.epoch` rejection
- Malformed envelope paths (7 variants)
- main.py structural checks
- Subprocess integration (no graph-state pollution)
- Phase 874 commit scope guard

---

## 5. CDL-074 Runtime (unchanged from v5.23)

**Module:** `ilc_core/epistemic/truth_primitive_submission_runtime.py`

```python
CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"
TRUTH_PRIMITIVE_RUNTIME_VERSION = "truth_primitive_submission_runtime_868.v0.1"

AGENT_ISSUABLE_PRIMITIVES = frozenset({
    "assert.truth", "validate.claim", "contradict.assert",
    "refute.claim", "revise.assert", "link.claim",
})
```

---

## 6. HB Obligation Status (unchanged from v5.23)

| Obligation | Status |
|------------|--------|
| HB-001 | **CLOSED** (CDL-073, Phase 860) |
| HB-002 | RC2+ — enabled |
| HB-003 | **CLOSED** (CDL-073, Phase 860) |

---

## 7. Row Status (unchanged from v5.23)

| Row | Status |
|-----|--------|
| Row 5 (Privacy Lane) | `runtime_closed` ✅ |
| Row 7 | `runtime_closed` ✅ |
| Row 8 | `evaluation_complete` — ILC Native Minimal L1 |

---

## 8. First-Validator Deployment (unchanged from v5.23)

Gate pulled 2026-04-26 (commit `a1e2c21b`). Four validators live on M-009.

---

## 9. Window 873–876 Scope Boundaries (DID NOT)

- Implement graph persistence, CIDv1 generation, or LMDB storage.
- Implement network-layer delivery of truth primitive submissions.
- Open a new CDL.
- Modify prototype primitive stubs (`assert`, `validate`, etc. in PRIMITIVE_COMMANDS).
- Change M-009.

---

## 10. Test Count

| Scope | Tests |
|-------|-------|
| Window 873–876 (Phase 874) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **251** |

---

## 11. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| Truth primitive graph persistence (CIDv1 + LMDB) | Phase 877+ | CDL-075 required |
| Network-layer delivery of truth primitive bundles | Phase 877+ | Separate CDL required |
| HB-002 (P2P bootstrap distribution) | RC2+ | Enabled after CDL-073 |
| CDL-070 (PQ migration ceremony) | Deferred | SIM-MONETARY-01 prerequisite |
