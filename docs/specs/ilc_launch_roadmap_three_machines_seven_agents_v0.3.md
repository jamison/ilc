# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.3
**Produced**: 2026-04-17
**Session context**: Window 701-706 CLOSED (today); capsule v4.5 current; M-011 binary_complete
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`
**Purpose**: Updated launch path reference at the Window 707+ frontier.

---

## Background

Same core question as v0.1/v0.2: what remains before ILC has a testable package running
across three separate computers with seven active agents?

The implementation gap from v0.2 (transport operationalization, agent loop, integration
harness) has been **substantially closed** across Windows 565-594. The remaining gaps at
the Window 707+ frontier are primarily **constitutional/governance** and
**runtime-form completion** — not infrastructure.

---

## 1. What Closed Since v0.2 (Windows 565-706)

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

### M-series milestones (Gemini Rust track)

| Phase | What closed |
|---|---|
| M-009 | BFT consensus core; all 6 SEC gates satisfied (`acfcfd2d`) |
| M-010 | `validator_harness` binary; 4-validator config; `binary_complete` |
| M-011 | `keygen` + `testnet_client` binaries; 4-validator harness tooling; `binary_complete` — real run pending provisioning |

---

## 2. Remaining Gaps at the Window 707+ Frontier

### Gap 1 — CDL-066 / CDL-017 / CDL-067 ratification (Window 707+, active)

Three CDLs are open and unratified. These are the primary constitutional blockers
for the Window 707-712 lane:

- **CDL-066** (Phase 694) — agent sender authorization (SEC-001 Track A)
- **CDL-017** (Phase 695) — bootstrap transition criteria
- **CDL-067** (Phase 696) — related governance vehicle

Window 707-712 carries governance-minimization and validator-agent identity design
alongside these ratification items.

### Gap 2 — MVP gate runtime-form completion (post-707, rows 5 and 7)

The Phase 612 two-form MVP gate requires both spec form and runtime form. Spec form
closed at Window 613-619 (`mvp_gate_spec_verdict=pass`). Runtime form is blocked until
Window 623+ interface/runtime work completes:

- **Row 5** — `spec_closed_runtime_pending` (leakage confirmation)
- **Row 7** — `spec_closed_runtime_pending` (censorship and exitability confirmation)

Broader public RC claims remain blocked until both forms complete.

### Gap 3 — M-series real liveness run (M-012 / M-013)

M-011 tooling is committed (`binary_complete`). The real 4-validator testnet run
requires provisioning: `--keygen`, `--gen-tls`, binary distribution to VPS nodes,
epoch injection 1-10, silent-validator test.

- **M-012**: Full BFT ECUTransfer round-trip — client-side AckFor collection,
  certificate formation, broadcast. Completes owned-object fast path.
- **M-013**: Workload A real liveness run (verdict target: `pass`).

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
| CDL-066/017/067 ratification | **OPEN** — Window 707+ |
| MVP gate runtime form (rows 5 + 7) | **PENDING** — post-707 |
| M-series real liveness run | **PENDING** — M-013 |
| Option B selection | **DEFERRED** — post-runtime-form |
| Legal positioning memo | **NOT WRITTEN** — pre-RC prerequisite |

---

## 4. Relationship to Existing Artifacts

- `docs/specs/ilc_antigravity_context_capsule_v4.5.md` — canonical current state
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` — 701+ program
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` — Option D→B transition
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` — M-series Rust track
- `docs/specs/ilc_window_701_706_closure_gate_706_v0.1.md` — Window 701-706 canonical closure
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md` — prior planning snapshot (Windows 565-584 as future)

---

*Updated 2026-04-17 to reflect true current frontier: Window 701-706 closed, Window 707-712 next.
Infrastructure gaps from v0.2 (transport, packaging, agent loop, integration harness) are closed.
Remaining work is constitutional ratification, runtime-form MVP gate closure, M-series liveness, and legal positioning.*
