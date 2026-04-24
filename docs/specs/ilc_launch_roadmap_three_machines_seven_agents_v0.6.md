# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.6
**Produced**: 2026-04-24
**Session context**: Window 811-822 closed; Option B selected; CDL-017 ratified;
Row-5 B-Scope closed at B-5; k-anonymity `k=30 + jitter=3` locked with
`k=20 + jitter=3` fallback; Row 5 remains `spec_closed_runtime_pending`;
B-Impl commissioned to the local reviewer.
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.5.md`
**Purpose**: Updated launch-path reference at the post-B-5 frontier.

---

## 1. Current Gap Inventory

### Gap 1 — Mysticeti activation sequencing

**Status: open post-selection.**

Option B is selected. Remaining work is execution sequencing:

- live settlement-path rotation wiring,
- first non-Genesis validator deployment under the preserved human gate,
- post-rotation three-machine smoke proof,
- HIGH-002 production disposition.

### Gap 2 — Row 5 privacy runtime delivery

**Status: spec closed, runtime pending.**

The Row-5 mechanism lock is complete.

The open design question is resolved. The open runtime question is not.

Locked mechanism:

- primary: `k=30`, `rolling_threshold`, `release_jitter_epochs=3`,
  `bounded_hold`
- fallback: `k=20`, `rolling_threshold`, `release_jitter_epochs=3`,
  `bounded_hold`

Locked simulation-derived B-Impl target:

- `A<=0.15`
- `B<=0.15`
- `C<=0.05`

What remains:

- B-Impl delivery in the runtime
- `SIM-LEAKAGE-03` on the M-009 testbed
- honest Row-5 runtime closure evaluation

### Gap 3 — First validator deployment and stronger replayability proof

**Status: still separately human-gated.**

The constitutional and selection work is done. The live deployment gate is not.

### Gap 4 — TLA+ pre-RC follow-through

**Status: delivered with honest boundaries.**

- Spec A widened, default 6GB gate memory-bound
- Spec C clean
- refinement notes published
- SafetyNoDualCert deferred honestly to later Spec D

### Gap 5 — Legal positioning memo

**Status: deferred non-gate.**

Still useful before broader public RC claims, but not a blocker to the current
technical frontier.

---

## 2. Current State Summary

| Surface | Status |
|---|---|
| Option B selection | **SELECTED** |
| CDL-017 | **RATIFIED** |
| Row 5 | **`spec_closed_runtime_pending`** — B-Scope closed, mechanism locked, runtime still pending |
| Row 7 | **`runtime_closed`** |
| Row 8 | **`pass`** |
| `ilc_dag_audit` Tier-1 | **DELIVERED** |
| TLA+ pre-RC hardening | **DELIVERED WITH HONEST BOUNDARIES** |
| Transfer privacy mechanism | **LOCKED** — `k=30 + jitter=3`, fallback `k=20 + jitter=3` |
| B-Impl | **COMMISSIONED** — local reviewer lane |
| `SIM-LEAKAGE-03` | **NOT RUN** |
| First non-Genesis validator deployment | **DEFERRED** — human gate preserved |

---

## 3. Proposed Next Sequence

### Near-term

**Row-5 B-Impl** (local reviewer lane)

- rolling-group runtime integration
- deferred jitter queue
- bounded-hold enforcement
- fallback activation
- degraded-anonymity notification
- live instrumentation

**Row-5 runtime closure evaluation** (opens only after B-Impl + `SIM-LEAKAGE-03`)

- live evaluation against the locked `A/B/C` target
- honest pass/fail closure record

### Parallel / subsequent

**Mysticeti activation implementation** (human-gated for first deployment)

- settlement-path rotation wiring
- first non-Genesis validator deployment
- stronger multi-machine proof

---

## 4. Relationship to Current Canon

| Artifact | Path | Role |
|---|---|---|
| Capsule v5.13 | `docs/specs/ilc_antigravity_context_capsule_v5.13.md` | live frontier posture |
| Row-5 lock B5 | `docs/specs/ilc_row5_mechanism_selection_lock_b5_v0.1.md` | mechanism lock |
| Row-5 B-Impl commissioning spec | `docs/specs/ilc_row5_b_impl_commissioning_spec_v0.1.md` | runtime obligations |
| B-5 closure gate | `docs/phases/phase_b5_row5_b_scope_closure_gate.md` | B-Scope close |
| Phase STATUS | `docs/phases/STATUS.md` | authoritative phase record |

---

This roadmap does not claim Row 5 runtime closure, Option B graduation, or
first-validator deployment. It records the post-B-5 state only.
