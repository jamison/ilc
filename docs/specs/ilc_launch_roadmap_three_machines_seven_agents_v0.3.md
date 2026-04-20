# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.3
**Produced**: 2026-04-18
**Session context**: Window 733-738 CLOSED (today); capsule v5.1 current; M-017 complete; next planned phase M-018
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`
**Purpose**: Updated launch path reference at the post-732 frontier.

---

## Background

Same core question as v0.1/v0.2: what remains before ILC has a testable package running
across three separate computers with seven active agents?

The implementation gap from v0.2 (transport operationalization, agent loop, integration
harness) has been **substantially closed** across Windows 565-594. The remaining gaps at
the post-732 frontier are primarily **constitutional/governance**, **runtime-form
completion**, and **distributed-validator operationalization** — not base infrastructure.

---

## 1. What Closed Since v0.2 (Windows 565-732)

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
| 717-722 | ADR-0015 family closure; transfer tax and cooling period bounded to launch structure without numeric lock; commons dedication bounded under CDL-047; leasehold / reversion deferred; capsule v4.8 frontier close |
| 723-726 | Sequestered financial-shard eligibility prefilter; post-launch trigger matrix; contagion firewall prerequisites; no activation and no ratification; capsule v4.9 frontier close |
| 727-732 | Adjacent gated-economy hardening closure; rights/licensing disposition; private/gated contract hardening bounded; no activation and no ratification; capsule v5.0 frontier close |
| 733-738 | CDL-017 prelock evidence window; Q1-Q6 imported; `SIM-VALIDATOR-01` and `SIM-TOPOLOGY-01` full pass; `CDL-068` opened; ADR-0019 accepted with scope amendment; no CDL ratification; capsule v5.1 frontier close |

### M-series milestones (Gemini Rust track)

| Phase | What closed |
|---|---|
| M-009 | BFT consensus core; all 6 SEC gates satisfied (`acfcfd2d`) |
| M-010 | `validator_harness` binary; 4-validator config; `binary_complete` |
| M-011 | `keygen` + `testnet_client` binaries; 4-validator harness tooling; `binary_complete` — real run pending provisioning |
| M-012 | Full BFT ECUTransfer round-trip; client-side certificate assembly path complete |
| M-013 | Workload A local multi-process liveness pass; epochs 1-10 finalized, silent-validator bounding on epochs 11-12 confirmed (`1d005208`) |
| M-014 | Workload B censorship resistance drill complete; local f=1 loopback proof documented |
| M-015 | Workload C partition / heal / recovery loopback proof complete |
| M-016 | Local offline state-extraction proof complete; stronger public-substrate replayability claim remains open pending a later lane |
| M-017 | Workload E validator operability complete; native validator envelope, sync proxy, and hardware budget captured |

---

## 2. Remaining Gaps at the Post-732 Frontier

### Gap 1 — CDL-017 convergence and activation boundary (post-738)

`CDL-066` and `CDL-067` are now ratified, but `CDL-017` remains open and unratified.
This is the primary surviving constitutional blocker in the validator/bootstrap lane.

- **CDL-017** (Phase 695) — bootstrap transition criteria

Window 707-712 resolved governance-minimization and validator-agent prelock
questions, and Window 733-738 completed the Codex-side prelock evidence block.
The remaining work is the Gemini `M-022` handoff plus the later convergence
window that turns both lanes into honest ratification text and activation
criteria.

Current Gap 1 posture:

- `PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE`
- pending Gemini `M-022` before any later `CDL-017` ratification claim

### Gap 2 — MVP gate runtime-form completion (rows 5 and 7)

The Phase 612 two-form MVP gate requires both spec form and runtime form. Spec form
closed at Window 613-619 (`mvp_gate_spec_verdict=pass`). Runtime form is blocked until
Window 623+ interface/runtime work completes:

- **Row 5** — `spec_closed_runtime_pending` (leakage confirmation)
- **Row 7** — `spec_closed_runtime_pending` (censorship and exitability confirmation)

Broader public RC claims remain blocked until both forms complete.

### Gap 3 — distributed validator provisioning beyond local M-series loopback proof

M-015 closed the local loopback partition/heal proof and M-016 closed a local
offline state-extraction proof, but the three-computer / real distributed
validator objective still requires provisioning and deployment work beyond the
local loopback harness.

Remaining distributed steps include:

- validator cert/key material distribution,
- remote binary placement,
- remote config distribution,
- true multi-machine epoch injection and evidence capture.

### Gap 4 — Option B production selection (post-Window 623+ runtime confirmed)

ADR-0028 holds Option D as the active posture. Option B becomes selectable only
after rows 5 and 7 runtime confirmation. Rows 6, 8, 9 are already closed.

### Gap 5 — Legal positioning memo (carry-forward, not a gate)

A legal positioning memo on passive ECU accrual and validator staking rewards
(CDL-054/055/056 Howey analysis) is listed in TODO.txt as `NOT YET WRITTEN`.
This is carry-forward, not a formal opening gate. The Phase 687-692 sequence
lock explicitly resolved this: "The legal memo is not a formal opening gate"
(`docs/specs/ilc_phase_687_692_sequence_lock_v0.1.md`). Expected to be written
before broader public RC claims but does not block Window 733+ or M-series
advancement.

### Gap 6 — stronger public-substrate replayability proof

M-016 delivered a local offline extractor over validator LMDB state. That is
useful tooling, but it is not yet the stronger proof of replayability from
public substrate data without operator cooperation.

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
| CDL-017 prelock evidence window | COMPLETE — Window 733-738 (Codex side) |
| Adaptive gossip + resilience operationalization | COMPLETE — Window 713-716 |
| ADR-0015 family closure | COMPLETE — Window 717-722 |
| Sequestered financial-shard eligibility prefilter | COMPLETE — Window 723-726 |
| Adjacent gated-economy hardening closure | COMPLETE — Window 727-732 |
| CDL-066 | **RATIFIED** — Phase 708 |
| CDL-067 | **RATIFIED** — Phase 709 |
| CDL-017 | **PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE** — Window 733-738; pending Gemini M-022 |
| CDL-068 | **OPEN** — Phase 736, not ratified |
| MVP gate runtime form (rows 5 + 7) | **PENDING** — post-707 |
| M-series loopback validator proof through partition/heal | **COMPLETE** — M-015 |
| M-series local offline state extraction | **COMPLETE** — M-016 |
| M-series validator operability evidence | **COMPLETE** — M-017 |
| M-series stronger public-substrate replayability proof | **PENDING** — post-M016 |
| M-series true multi-machine validator proof | **PENDING** — post-M016 provisioning |
| Option B selection | **DEFERRED** — post-runtime-form |
| Legal positioning memo | **NOT WRITTEN** — carry-forward, not a gate (Phase 687-692 seq lock) |

---

## 4. Relationship to Existing Artifacts

- `docs/specs/ilc_antigravity_context_capsule_v5.1.md` — canonical current state
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` — 701+ program
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` — Option D→B transition
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` — M-series Rust track
- `docs/specs/ilc_window_733_738_closure_gate_738_v0.1.md` — Window 733-738 canonical closure
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md` — `CDL-068` opening
- `docs/research/ilc_mysticeti_workload_c_results_M015_v0.1.md` — M-015 partition / heal loopback results
- `docs/research/ilc_mysticeti_workload_d_results_M016_v0.1.md` — M-016 local offline state extraction results
- `docs/research/ilc_sim_validator_01_results_v0.1.md` — Phase 734 stake-floor and VRF-threshold evidence
- `docs/research/ilc_sim_topology_01_results_v0.1.md` — Phase 735 topology and diversity evidence
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md` — prior planning snapshot (Windows 565-584 as future)

### Morphogenetic Hypergraph Research Lane (post-mainnet, with one pre-M-018 gate)

A post-mainnet architectural research cluster was established 2026-04-19. One item is time-critical before M-018:

- **ADR-0031** (`docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md`) — `EdgeRecord` and `HyperEdgeRecord` proto message types must be added to `ilc_app.proto` before M-018 finalizes its gRPC query response schema. Adding after that point is a breaking wire-format change.

Remaining items are post-mainnet research: ADR-0029 (hypergraph substrate), ADR-0030 (embedding substrate), SIM-HYPEREDGE-01/SPECTRAL-01/EMBED-01/BEACON-01/ROUTING-01, Merkle-Laplacian dual commitment paper, sealed spectral beacon / spectral routing.

Master index for this cluster: `docs/PLANNING_INDEX.md` §9.

---

*Updated 2026-04-20 to reflect the true current frontier: Window 733-738 closed, capsule v5.1 current, Gap 1 advanced to `PRELOCK_EVIDENCE_COMPLETE_CODEX_SIDE`, and M-017 validator operability complete.
Infrastructure gaps from v0.2 (transport, packaging, agent loop, integration harness) are closed.
Remaining work is CDL-017 convergence, MVP gate runtime-form closure, stronger public-substrate replayability proof, true multi-machine validator provisioning, Option B selection gating, and legal positioning.*
