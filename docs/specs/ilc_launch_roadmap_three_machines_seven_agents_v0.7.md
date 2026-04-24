# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.7
**Produced**: 2026-04-24
**Session context**: Window 823-829 closed; Option B selected; CDL-017
ratified; Row-5 B-Scope closed; B-Impl commissioned to the local reviewer;
H-013 sealed spectral beacon implemented locally and post-audit hardened;
HIGH-002 disposition, settlement-path rotation wiring design, and
first-validator entry conditions published.
**Supersedes**:
`docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.6.md`
**Purpose**: Updated launch-path reference at the post-823-829 frontier.

---

## 1. Current Gap Inventory

### Gap 1 — Mysticeti activation sequencing

**Status: partially designed, implementation still gated.**

Completed:

- HIGH-002 production disposition,
- settlement-path rotation wiring design,
- first-validator deployment entry conditions,
- H-013 local sealed-beacon implementation with post-audit hardening for
  relay-origin opacity, authenticated beacon identity, replay detection, and
  SIM-BEACON bounds.

Remaining:

- settlement-path rotation Rust implementation,
- three-machine smoke proof,
- explicit human authorization for first non-Genesis validator deployment,
- first deployment execution and rollback verification.

### Gap 2 — Row 5 privacy runtime delivery

**Status: spec closed, runtime pending.**

Locked mechanism:

- primary: `k=30`, `rolling_threshold`, `release_jitter_epochs=3`,
  `bounded_hold`
- fallback: `k=20`, `rolling_threshold`, `release_jitter_epochs=3`,
  `bounded_hold`

Locked simulation-derived B-Impl target:

- `A<=0.15`
- `B<=0.15`
- `C<=0.05`

Remaining:

- B-Impl delivery in the runtime,
- `SIM-LEAKAGE-03` on the M-009 testbed,
- honest Row-5 runtime closure evaluation.

### Gap 3 — First validator deployment and stronger replayability proof

**Status: entry conditions published, gate not pulled.**

The operator checklist exists. The deployment authorization itself remains
separate and must name validator IDs, machines, network state, rollback, and
the fact that Row 5 and HIGH-002 remain bounded carry-forward obligations.

### Gap 4 — TLA+ pre-RC follow-through

**Status: delivered with honest boundaries.**

- Spec A widened, default 6GB gate memory-bound,
- Spec C clean,
- refinement notes published,
- SafetyNoDualCert deferred honestly to later Spec D.

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
| Row 5 | **`spec_closed_runtime_pending`** |
| Row 7 | **`runtime_closed`** |
| Row 8 | **`pass`** |
| H-013 | **IMPLEMENTED LOCALLY** — post-audit hardened; no production gossip activation |
| H-015 | **PRIMITIVE COMPLETE** — can consume H-013 later |
| HIGH-002 | **DISPOSITIONED** — production-hardening item |
| Settlement-path rotation | **DESIGNED ONLY** — Rust implementation gated |
| First non-Genesis validator deployment | **DEFERRED** — human gate preserved |
| B-Impl | **COMMISSIONED** — local reviewer lane |
| `SIM-LEAKAGE-03` | **NOT RUN** |

---

## 3. Proposed Next Sequence

### Near-term Mysticeti activation implementation

- implement the settlement-path rotation gate from Phase 825,
- run the three-machine smoke proof,
- produce the deployment authorization packet,
- only then ask the operator to pull the first-validator human gate.

### Parallel Row-5 runtime work

- local reviewer delivers B-Impl obligations,
- run `SIM-LEAKAGE-03`,
- open a Row-5 runtime closure evaluation only after live evidence exists.

### Later hardening

- implement HIGH-002 signer-subset verification before independently operated
  production validator sets, and no later than `N >= 4`, `F >= 1`.

---

## 4. Relationship to Current Canon

| Artifact | Path | Role |
|---|---|---|
| Capsule v5.14 | `docs/specs/ilc_antigravity_context_capsule_v5.14.md` | live frontier posture |
| Phase 829 closure gate | `docs/phases/phase_829_window_823_829_closure_gate.md` | latest closed activation sequencing gate |
| HIGH-002 disposition | `docs/specs/ilc_high_002_production_disposition_824_v0.1.md` | liveness limitation and hardening trigger |
| Rotation wiring design | `docs/specs/ilc_settlement_path_rotation_wiring_design_825_v0.1.md` | later Rust implementation basis |
| First-validator entry conditions | `docs/specs/ilc_first_validator_deployment_entry_conditions_826_v0.1.md` | operator gate checklist |
| Row-5 B-Impl commissioning spec | `docs/specs/ilc_row5_b_impl_commissioning_spec_v0.1.md` | runtime obligations |

---

This roadmap does not claim Row 5 runtime closure, Option B graduation,
first-validator deployment, settlement-path Rust activation, or production D2d
gossip activation.
