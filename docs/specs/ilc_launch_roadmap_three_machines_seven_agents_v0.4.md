# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.4
**Produced**: 2026-04-20
**Session context**: Window 745-748 ACTIVE through Phase 747; capsule v5.3 current; authoritative Track B line from `STATUS.md`: M-019 complete, next planned phase M-020
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
**Purpose**: Updated launch-path reference at the post-746 frontier.

---

## Background

The core question is unchanged: what remains before ILC has a testable package
running across three separate computers with seven active agents?

The infrastructure gap from earlier roadmap versions remains mostly closed.
The surviving gaps at the post-746 frontier are:

- constitutional convergence (`CDL-017` still open),
- honest runtime-form closure on rows `5` and `7`,
- later row `8` disposition,
- true distributed-validator and replayability proof beyond local loopback,
- Option B graduation only after those runtime gates actually close.

---

## 1. What Closed Since v0.3

| Window | What closed |
|---|---|
| 745-748 (active) | Phase `745` opened the convergence-window commissioning lane; Phase `746` commissioned the later convergence window and accepted ADR-0031 as housekeeping-only; Phase `747` advanced capsule `v5.3`, roadmap `v0.4`, and `PLANNING_INDEX.md` |

---

## 2. Remaining Gaps at the Post-746 Frontier

### Gap 1 — CDL-017 convergence and activation boundary

`CDL-017` remains open and unratified.

Current Gap 1 posture:

- `PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE`
- later Gemini `M-022` handoff still required before any ratification claim

### Gap 2 — MVP gate runtime-form completion (rows 5 and 7)

Rows `5` and `7` remain `spec_closed_runtime_pending`.

- **Row 5** — still awaits committed `SIM-LEAKAGE-01` execution results
- **Row 7** — censorship-runtime artifact carrier is now named in the
  convergence commissioning spec as
  `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`, but
  strong exitability still awaits a separate export / verify / replay /
  migrate results artifact

The later convergence window is now commissioned precisely to absorb these
runtime-closure obligations. It is not open yet.

### Gap 3 — Row 8 disposition

Row `8` remains an inherited criteria lock. No runtime-confirmation or final
disposition work has occurred yet. That work is explicitly routed to the later
convergence window.

### Gap 4 — distributed validator provisioning beyond local proof

The repo still lacks the stronger distributed proof package:

- remote validator provisioning,
- multi-operator or true multi-machine evidence,
- stronger public-substrate replayability proof beyond the local M-016 lane.

### Gap 5 — Option B production selection

ADR-0028 still holds Option D as the active posture.

The later convergence window is authorized to synthesize the Option B
graduation gate, but not to claim graduation without the runtime-closure
evidence on rows `5` and `7`.

### Gap 6 — Legal positioning memo

The legal positioning memo remains not written.

It is now explicitly deferred non-gate carry-forward and does not belong in the
active Window `745-748` packet.

---

## 3. Current State Summary

| Surface | Status |
|---|---|
| 3-machine transport (CDL-061 / HTTP/3) | COMPLETE |
| Agent behavioral loop v1 (7 agents) | COMPLETE |
| MVP gate spec form (5 touchpoints) | COMPLETE |
| CDL-066 | **RATIFIED** — Phase 708 |
| CDL-067 | **RATIFIED** — Phase 709 |
| CDL-068 | **RATIFIED** — Phase 743 |
| CDL-017 | **OPEN** — later Gemini M-022 handoff still required |
| Rows 5 and 7 runtime evidence packaging lane | COMPLETE — Window 739-744 |
| Convergence-window commissioning lane | COMPLETE through Phase 746; later convergence window commissioned but not open |
| ADR-0031 | **ACCEPTED** — Phase 746 housekeeping-only status advance |
| MVP gate runtime form (rows 5 + 7) | **STILL PENDING LIVE CLOSURE** |
| Row 8 | **INHERITED / NOT ADVANCED** |
| Option B selection | **DEFERRED** — after runtime closure and later convergence synthesis |

---

## 4. Track B Note

The authoritative current/next Track B line still comes from `docs/phases/STATUS.md`:

- `M-019` complete
- `M-020` next planned phase

The convergence commissioning spec is allowed to name committed carrier docs
such as `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`,
but that does not override the `STATUS.md` authority order for the current/next
lane label.

---

## 5. Relationship to Existing Artifacts

- `docs/specs/ilc_antigravity_context_capsule_v5.3.md` — canonical current capsule
- `docs/specs/ilc_phase_745_748_sequence_lock_v0.1.md` — active sequence lock
- `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md` — later convergence lane commission
- `docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md` — latest closed-window closure
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md` — Option D / Option B route
- `docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md` — now accepted

---

*Updated 2026-04-20 to reflect the true post-746 frontier: Window 745-748 is
active, capsule v5.3 is current, the later convergence window is commissioned
but not open, ADR-0031 is accepted, rows 5 and 7 remain runtime-pending, row 8
remains inherited, and Option B remains deferred.*
