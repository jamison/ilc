# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.3
**Produced**: 2026-04-17
**Session context**: Window 713-716 CLOSED (today); capsule v4.7 current; M-013 complete; next planned phase TBD
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`
**Purpose**: Updated launch path reference at the post-716 frontier.

---

## Background

Same core question as v0.1/v0.2: what remains before ILC has a testable package running
across three separate computers with seven active agents?

The implementation gap from v0.2 (transport operationalization, agent loop, integration
harness) has been **substantially closed** across Windows 565-594. The remaining gaps at
the post-716 frontier are primarily **constitutional/governance**, **runtime-form
completion**, and **distributed-validator operationalization** — not base infrastructure.

---

## 1. What Closed Since v0.2 (Windows 565-716)

### Implementation milestones (Codex Python track)

| Window | What closed |
|---|---|
| 565-574 | Three-machine transport operationalized; `three_machine_testbed_primary_gate_passed`; venv + systemd packaging |
| 575-584 | Agent behavioral loop v1 live; 7+1 panel + live submission integration; ECU attribution into settlement; wallet query boundary locked |
| 585-594 | Three-machine / seven-agent integration harness; `phase_594_verdict=pass`; RC0.1 Strike Force (Phase 595) absorbed 582-584 obligations |
| 596-605 | Genesis carry-forward closure lane |
| 607-612 | Settlement substrate closure; Option D confirmed active; Option B row checklist opened |
| 613-619 | MVP gate spec lane — all five participant-touch surfaces closed in spec form; `mvp_gate_spec_verdict=pass` |
| 620-622 | Agent Skills surface spec; bounded ECU exchange model spec |
| 624-630 | CDL-063 ratified (directed-commission earmark + bounded debit); ECU active-layer runtime live |
| 631-641 | CDL-064 ratified (Tier-0 exact numeric determinism); float cleanup |
| 642-706 | Signing export hardening; privacy-preserving public legitimacy; sovereign substrate admissibility; foundational economic doctrine + kernel calibration |
| 707-712 | Governance minimization closure; ADR-0019 disposition; CDL-066 ratified; CDL-067 ratified; validator-agent prelock lane bounded without CDL-017 ratification |
| 713-716 | Adaptive-gossip law-vs-freedom classification; partition-repair benchmark commissioning; missing-signal doctrine; capsule v4.7 frontier close |

### M-series milestones (Gemini Rust track)

| Phase | What closed |
|---|---|
| M-009 | BFT consensus core; all 6 SEC gates satisfied (`acfcfd2d`) |
| M-010 | `validator_harness` binary; 4-validator config; `binary_complete` |
| M-011 | `keygen` + `testnet_client` binaries; 4-validator harness tooling; `binary_complete` — real run pending provisioning |
| M-012 | Full BFT ECUTransfer round-trip; client-side certificate assembly path complete |
| M-013 | Workload A local multi-process liveness pass; epochs 1-10 finalized, silent-validator bounding on epochs 11-12 confirmed (`1d005208`) |

---

## 2. Remaining Gaps at the Post-716 Frontier

### Gap 1 — CDL-017 convergence and activation boundary (post-716)

`CDL-066` and `CDL-067` are now ratified, but `CDL-017` remains open and unratified.
This is the primary surviving constitutional blocker in the validator/bootstrap lane.

- **CDL-017** (Phase 695) — bootstrap transition criteria

Window 707-712 resolved governance-minimization and validator-agent prelock
questions, but later work still needs to converge constitutional text, runtime-form
evidence, and activation criteria honestly.

### Gap 2 — MVP gate runtime-form completion (rows 5 and 7)

The Phase 612 two-form MVP gate requires both spec form and runtime form. Spec form
closed at Window 613-619 (`mvp_gate_spec_verdict=pass`). Runtime form is blocked until
Window 623+ interface/runtime work completes:

- **Row 5** — `spec_closed_runtime_pending` (leakage confirmation)
- **Row 7** — `spec_closed_runtime_pending` (censorship and exitability confirmation)

Broader public RC claims remain blocked until both forms complete.

### Gap 3 — distributed validator provisioning beyond local M-013 pass

M-013 closed the local multi-process Workload A proof, but the three-computer
/ real distributed validator objective still requires provisioning and deployment
work beyond the local loopback harness.

Remaining distributed steps include:

- validator cert/key material distribution,
- remote binary placement,
- remote config distribution,
- true multi-machine epoch injection and evidence capture.

### Gap 4 — Option B production selection (post-Window 623+ runtime confirmed)

ADR-0028 holds Option D as the active posture. Option B becomes selectable only
after rows 5 and 7 runtime confirmation. Rows 6, 8, 9 are already closed.

### Gap 5 — Legal positioning memo (pre-RC prerequisite)

A legal positioning memo on passive ECU accrual and validator staking rewards
(CDL-054/055/056 Howey analysis) is listed in TODO.txt as `NOT YET WRITTEN`.
Required before any broader public RC claim.

---

## 3. Current State Summary

| Surface | Status |
|---|---|
| 3-machine transport (CDL-061 / HTTP/3) | COMPLETE — Window 565-574 |
| Agent behavioral loop v1 (7 agents) | COMPLETE — Window 575-584 |
| 7+1 panel + ECU attribution | COMPLETE — Window 575-584 |
| Genesis carry-forward | COMPLETE — Window 596-605 |
| MVP gate spec form (5 touchpoints) | COMPLETE — Window 613-619 |
| ECU active-layer runtime (CDL-063) | COMPLETE — Window 624-630 |
| Tier-0 numeric determinism (CDL-064) | COMPLETE — Windows 631-641 |
| Foundational economic doctrine | COMPLETE — Window 701-706 |
| Governance minimization + validator-agent prelock lane | COMPLETE — Window 707-712 |
| Adaptive gossip + resilience operationalization | COMPLETE — Window 713-716 |
| CDL-066 | **RATIFIED** — Phase 708 |
| CDL-067 | **RATIFIED** — Phase 709 |
| CDL-017 | **OPEN** — post-716 carry-forward |
| MVP gate runtime form (rows 5 + 7) | **PENDING** — post-707 |
| M-series local liveness run | **COMPLETE** — M-013 local multi-process pass |
| M-series true multi-machine validator proof | **PENDING** — post-M013 provisioning |
| Option B selection | **DEFERRED** — post-runtime-form |
| Legal positioning memo | **NOT WRITTEN** — pre-RC prerequisite |

---

## 4. Relationship to Existing Artifacts

- `docs/specs/ilc_antigravity_context_capsule_v4.7.md` — canonical current state
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` — 701+ program
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` — Option D→B transition
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` — M-series Rust track
- `docs/specs/ilc_window_713_716_closure_gate_716_v0.1.md` — Window 713-716 canonical closure
- `docs/research/ilc_mysticeti_workload_a_results_M013_v0.1.md` — M-013 local multi-process results
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md` — prior planning snapshot (Windows 565-584 as future)

---

*Updated 2026-04-17 to reflect the true current frontier: Window 713-716 closed, Window 717-722 next planned, and M-013 local multi-process liveness complete.
Infrastructure gaps from v0.2 (transport, packaging, agent loop, integration harness) are closed.
Remaining work is CDL-017 convergence, MVP gate runtime-form closure, true multi-machine validator provisioning, Option B selection gating, and legal positioning.*
