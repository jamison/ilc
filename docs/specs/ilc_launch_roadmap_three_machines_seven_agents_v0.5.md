# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.5
**Produced**: 2026-04-23
**Session context**: Window 811-822 CLOSED; capsule v5.12 current; all M-phases
complete; convergence window closed (Phase 762); CDL-017 ratified (Phase 765);
Option B selected by human authorization on 2026-04-23; row 7 runtime_closed;
row 8 pass; row 5 remains a pre-public-RC obligation.
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.4.md`
**Purpose**: Updated launch-path reference at the post-822 frontier.

---

## Background

The core question is unchanged: what remains before ILC has a production-ready
package running across three separate computers with seven active agents?

Significant ground has been covered since v0.4. The major convergence,
constitutional, and implementation milestones are now closed. What remains
is a bounded set of activation tasks, one unresolved technical problem (row 5
privacy), and the post-selection hardening/deployment sequencing.

---

## 1. What Closed Since v0.4

| Window / Milestone | What closed |
|---|---|
| M-022 complete (2026-04-21) | Exitability drill (export/verify/replay/migrate all pass); Gemini handoff package complete; `run_m022_exitability_drill_verdict=pass`; M-series COMPLETE |
| Convergence window CW-1 to CW-6 (Phase 762) | Row 7 `runtime_closed` (censorship + strong-exitability both pass); row 5 honest non-closure; row 8 criteria-locked + candidate-evaluated |
| CDL-017 ratification window (Phase 765-766) | CDL-017 **RATIFIED** — validator governance framework in force; activation boundary preserved (Genesis-only authority, human gate for first deployment, M-007 local helpers activated, SEC-004 deferred pending live wiring) |
| Window 767-774 | SEC-004 acceptance scope closed; M-007 hooks activated as local `ValidatorSet` mutation helpers |
| Window 775-782 | Row 5 privacy remediation: honest non-closure recorded; two-layer carry-forward fixed (log hygiene + transfer privacy) |
| Window 783-790 | Row 8 evaluation: `mysticeti_sovereign_row_8_combined_status=conditional` pending verification tooling |
| Window 791-800 | Hypergraph research (H-series): H-013 ADR accepted, H-014/H-015 complete, Tier 3 deferred |
| Window 801-804 | DAG audit design: `ilc_dag_audit` CLI design spec complete; Tier-1 confirmed implementable |
| Phase 805 | `ilc_dag_audit` Tier-1 delivered; `dag_audit_tier1_pass`; `verification_tooling_tier1_condition_discharged` |
| Window 806-810 | Post-805 Option B re-synthesis: row 8 combined status = `pass`; `option_b_gate_conditions=none`; `option_b_gate_synthesis_verdict=go_pending_human_authorization` |
| Window 811-822 | ADR-0028 amended; checklist v0.2/v0.3 published; Option B selected; Spec C TLC clean; SEC-007a protoc vendored; SEC-007b rand disposition closed |

---

## 2. Current Gap Inventory

The v0.4 gaps are substantially resolved. The surviving gaps are:

### Gap 1 — Mysticeti activation sequencing

**Status: Open post-selection.** Option B is now selected and ADR-0028 posture
has shifted to Option B. The remaining gap is execution sequencing:

- live settlement-path rotation wiring,
- first non-Genesis validator deployment under the separate human gate,
- post-rotation three-machine smoke proof,
- HIGH-002 production disposition.

### Gap 2 — Row 5 privacy (unresolved technical problem)

**Status: Open.** Row 5 (`privacy-preserving public legitimacy mechanism`) is
the only MVP gate condition that is not closed.

The CW-2 verdict is `row_5_runtime_closure_verdict=fail`. Two concrete
requirements are fixed:

1. **Log hygiene** — AgentID redaction from validator operational logs.
2. **Transfer privacy** — a privacy layer sufficient to drive contribution-flow
   linkage below the Phase 740 closure bands (0.45 / 0.60).

**Open decisions before scoping can proceed:**

- *Which privacy mechanism?* Three candidates: H-013 sealed-sender
  (ADR-0034 accepted, implementation incomplete), k-anonymity-style protection
  (lower complexity, unclear if it clears the bands), or a mixing layer
  (gold-standard, higher complexity). Human judgment needed.
- *Is the Phase 740 closure bar still the right bar?* Not revisited since CW-2.

Row 5 non-closure no longer blocks Option B selection, but it remains a
parallel obligation on the path to full production legitimacy.

### Gap 3 — Settlement-path rotation wiring and first validator deployment

**Status: Scoped but not implemented.**

SEC-004 acceptance scope is closed and the live wiring scope has now been named
in Window 811-822. What remains is the actual implementation and live test.

First non-Genesis validator deployment is an explicit second human gate
(separate from Option B selection).

True multi-machine validator provisioning and stronger public-substrate
replayability proof (beyond local M-016/M-022 loopback) remain post-deployment
obligations.

### Gap 4 — TLA+ pre-RC hardening follow-through

**Status: Mostly delivered, with one honest environment-bound remainder.**

Three TLA+ items are pre-RC obligations:

| Item | Effort | What it hardens |
|---|---|---|
| TLA-PRE-1: Widen Spec A MaxRound 5→12 | Delivered; default 6GB TLC gate is memory-bound at the deeper horizon | Row-7 liveness claim under a materially wider bounded search |
| TLA-PRE-2: Spec C — partition/heal recovery | Delivered cleanly | M-015 recovery behavior |
| TLA-PRE-3: Informal refinement notes | Delivered | Audit credibility; closes the Rust↔TLA+ gap claim |
| Shared-object SafetyNoDualCert | Honest deferral to later Spec D | Avoids misusing Spec A for the wrong property |

### Gap 5 — Legal positioning memo

**Status: Not written; deferred non-gate.**

A counsel-facing memo on the passive ECU attribution/decay/treasury/validator-
parameter facts package is needed before broader public RC claims. It is not
a gate for Option B selection or Mysticeti activation.

---

## 3. Current State Summary

| Surface | Status |
|---|---|
| 3-machine transport (CDL-061 / HTTP/3) | COMPLETE |
| Agent behavioral loop v1 (7 agents) | COMPLETE |
| MVP gate spec form (all 9 touchpoints) | All rows have criteria locks |
| CDL-066, CDL-067, CDL-068 | RATIFIED |
| CDL-017 | **RATIFIED** — Phase 765 |
| Row 1 (public init/admission) | `runtime_closed` |
| Row 2 (machine-legible receipts) | `runtime_closed` |
| Row 3 (ECU-to-ILC lifecycle) | `runtime_closed` |
| Row 4 (public wallet surface) | `runtime_closed` |
| Row 5 (privacy mechanism) | **`spec_closed_runtime_pending`** — honest fail at CW-2 |
| Row 6 (coupling invariants) | `closed` — CDL-065 ratified |
| Row 7 (censorship resistance) | **`runtime_closed`** — CW-3 + CW-4 both pass |
| Row 8 (external constitutional independence) | **`pass`** — Phase 809 post-805 re-synthesis |
| Row 9 (transport maturity) | `closed` — Phase 669 |
| M-series (M-001–M-022) | **COMPLETE** — 2026-04-21 |
| Convergence window (CW-1 through CW-6) | **CLOSED** — Phase 762 |
| `ilc_dag_audit` Tier-1 verifier | **DELIVERED** — Phase 805 |
| Option B gate | **CONSUMED** — human authorization exercised |
| Option B selection | **SELECTED** — Window 811-822 |
| Settlement-path rotation wiring | **SCOPED** — implementation still pending |
| First non-Genesis validator deployment | **DEFERRED** — second human gate, post-selection |
| TLA+ pre-RC hardening | **DELIVERED WITH HONEST BOUNDARIES** |
| Legal positioning memo | **DEFERRED** — non-gate carry-forward |
| External security audit | **NOT ENGAGED** — post-RC trigger |

---

## 4. Proposed Window Sequence

The following is the indicative sequencing. Items marked `[HG]` require a human
gate in conversation first. Items with no `[HG]` can open on Codex authorization.

### Near-term (independent of Option B decision)

**TLA+ Pre-RC Hardening** (~4 phases, no HG)
- Widen MaxRound, re-run TLC (TLA-PRE-1)
- Write Spec C partition/heal, run TLC, disposition SafetyNoDualCert (TLA-PRE-2)
- Write refinement notes for Spec A and B (TLA-PRE-3)

**Row 5 Mechanism Scoping** (~5 phases, HG on mechanism choice)
- Privacy mechanism family analysis: H-013 sealed-sender vs k-anonymity vs mixing
- SIM-LEAKAGE-02 pre-implementation simulation against candidate(s)
- Mechanism selection lock with linkage-reduction projection
- **Human gate required**: mechanism choice and closure bar confirmation

### After Window 811-822

**Mysticeti Implementation Activation** (~4-6 phases, HG for first deployment)
- Settlement-path rotation wiring implementation
- First non-Genesis validator deployment (second human gate)
- Multi-machine provisioning and stronger replayability proof
- **Human gate required**: first deployment authorization

### After row 5 mechanism selected

**Row 5 Implementation** (~6-8 phases, no additional HG)
- Log hygiene implementation (AgentID redaction)
- Privacy layer implementation per selected mechanism
- SIM-LEAKAGE-03 execution
- Row 5 runtime-closure evaluation (pass or honest fail)

### Non-blocking, any time

**Legal Memo** (~2-3 phases)

---

## 5. Track B note

The M-series is complete. Track B is closed. There is no "next M-phase." The
authoritative source for completed phases and their evidence is:
`docs/phases/STATUS.md` and `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`.

The authoritative source for the current main-lane frontier is:
`docs/specs/ilc_antigravity_context_capsule_v5.12.md` and
`docs/phases/STATUS.md` tail.

---

## 6. Relationship to current artifacts

| Artifact | Path | Role |
|---|---|---|
| Context Capsule v5.12 | `docs/specs/ilc_antigravity_context_capsule_v5.12.md` | Live frontier posture |
| Master Completion Roadmap v0.2 | `docs/specs/ilc_master_completion_roadmap_v0.2.md` | Detailed category breakdown |
| Phase STATUS | `docs/phases/STATUS.md` | Authoritative phase record |
| Phase 822 closure gate | `docs/phases/phase_822_window_811_822_closure_gate.md` | Latest closed window gate |
| Phase 814 selection record | `docs/phases/phase_814_option_b_selection_record.md` | Live Option B selection record |
| CW-2 Row 5 evaluation | `docs/specs/ilc_row_5_runtime_closure_evaluation_cw2_v0.1.md` | Row 5 honest fail record |
| CW-4 Row 7 exitability | `docs/specs/ilc_row_7_exitability_closure_evaluation_cw4_v0.1.md` | Row 7 runtime_closed record |
| ADR-0028 | `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md` | Option D/B governance route |
| TLA+ gap analysis | `docs/research/ilc_tla_plus_gap_analysis_v0.1.md` | Pre-RC TLA+ obligations |
| DAG Audit CLI design | `docs/specs/ilc_dag_audit_cli_design_803_v0.1.md` | Tier-1 delivered; Tier-2 design for later |

---

*Updated 2026-04-23 to reflect the true post-822 frontier: M-series complete,
convergence and CDL-017 ratification windows closed, row 7 runtime_closed,
row 8 pass, Option B selected by human authorization, and the TLA+/SEC-007a/b
pre-RC hardening tranche closed with honest boundaries. Remaining gaps: row 5
privacy mechanism and implementation, post-selection Mysticeti activation
sequencing, and the environment-bound default Spec A TLC gate.*
