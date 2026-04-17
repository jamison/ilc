# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.3
**Produced**: 2026-04-17
**Session context**: Window 575-584 in progress; capsule v4.5 current; M-series M-011 complete
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`
**Purpose**: Updated launch path reference reflecting Windows 565-574 closure and 575-584 progress.

---

## Background

Same core question as v0.1/v0.2: what remains before ILC has a testable package running
across three separate computers with seven active agents?

The gap structure has materially compressed since v0.2:
- **Window 565-574 CLOSED** — three-machine transport operationalized, `three_machine_testbed_primary_gate_passed`
- **Window 575-584 IN PROGRESS** — agent behavioral loop v1, Phase 580 complete (7+1 panel + live submission integration)
- **M-series parallel track: M-009/M-010/M-011 COMPLETE** — Rust/Mysticeti validator cluster
  has keygen, testnet_client, and 4-validator harness tooling; real liveness run pending provisioning

---

## 1. Current State (2026-04-17)

### 1.1 Subsystems added since v0.2

| Subsystem | Path | Notes |
|---|---|---|
| HTTP gossip transport | `ilc_core/network/d2d/http_gossip_transport_runtime.py` | Real HTTP/3 client+server I/O, HTTP/2 fallback config (Phase 568-569) |
| Static peer config loader | `ilc_core/node/node_startup_runtime.py` | JSON static peers, genesis import, CDL-046 startup sequencing (Phase 570) |
| Node service packaging | `run_ilc_node_service_v1.py` + `deploy/systemd/ilc-node-v1.service` | venv + systemd unit (Phase 571) |
| Agent behavioral loop v1 | `tools/agent_loop_v1.py` | Replaced `agent_loop_v0.sh` pseudocode; protocol-compliant loop (Phase 579) |
| 7+1 panel + submission integration | _(panel wiring in submission pipeline)_ | Live submission path with diversity-floor and Popperian gate (Phase 580) |
| Rust validator harness | `ilc_consensus/` | M-009: BFT core; M-010: `validator_harness` binary; M-011: `keygen` + `testnet_client` (Phase M-009/M-010/M-011) |

### 1.2 Completed subsystems (unchanged from v0.2)

| Subsystem | Path | Notes |
|---|---|---|
| Consensus engine | `ilc_core/consensus/` | Sponsor graph, governance, CDL-V3 diversity floor, CDL-V7 Popperian gate |
| Genesis bootstrap | `ilc_core/genesis/` | `genesis_validator_bootstrap_runtime_480.v0.1` |
| Ledger and settlement | `ilc_core/ledger/` | Canon bundle pipeline, settlement verification, persistent backend |
| D2d transport invariants | `ilc_core/network/d2d/` | CDL-039, CDL-060 gossip, CDL-061 HTTP envelope, static peer registry |
| Passive ECU attribution | `ilc_core/economics/passive_ecu_attribution_runtime.py` | `rate=0.20`, `floor=0.05`, `cap=0.15` |
| Validator subsystems | `ilc_core/validator/` | Re-admission, staking liveness, trust tier runtimes |
| CLI tooling | `ilc_core/cli/` | D2e CLI, agent CLI, lifecycle management |

### 1.3 Window 565-574 closure summary

Gap 1 (transport operationalization) and Gap 2 (multi-machine packaging) from v0.2 are **CLOSED**.

Closure evidence:
- Real HTTP gossip transport wrapper wraps `gossip_transport.py` with actual socket I/O
- JSON static peer config loader wires `GossipPeerRegistry` at startup
- `venv + systemd` packaging validated
- Three-machine smoke harness `run_three_machine_smoke_phase_572.sh` passed all 8 criteria including CDL-061 envelope traffic over real HTTP, genesis import, and kind=http fallback proof
- Gate token: `three_machine_testbed_primary_gate_passed`

TLS posture: server TLS + `ILC-Signature` header. mTLS explicitly deferred to post-RC0 hardening.

---

## 2. Remaining Gaps

### Gap 3 — Agent behavioral loop completion (Window 575-584, IN PROGRESS)

Agent loop v1 (`tools/agent_loop_v1.py`) is running. The 7+1 evaluation panel is wired into
the live submission path (Phase 580). Remaining work in this window:

**Still needed before 575-584 closes:**
- ECU attribution into settlement path (Phase 581)
- Wallet query integration — visibility-only, no write authority (Phase 581)
- CDL-V7 reproducibility disposition (Phase 582)
- Outbound HTTP machine-payment skill: defer-or-attach decision (Phase 582)
- Coherence report + capsule v3.2 (Phase 583)
- Closure gate (Phase 584)

**Pass condition (7 criteria):**
- Live agent loop on 3-machine substrate with 7 agents and bounded 7+1 panel
- Durable persisted graph
- ECU attribution into settlement path
- Wallet visibility-only (no write authority)
- Negative-path drills completed
- Bounded CDL-V7 reproducibility disposition before Phase 584
- No public genesis-governance or public minting claim

### Gap 4 — Three-machine / seven-agent integration harness (Window 585-594)

The deterministic full-system proof: three nodes on separate machines, seven agent
processes, one end-to-end task cycle, gossip propagation verification, evaluation flow,
and ECU attribution.

**Estimated scope**: Window 585-594 (sequence lock exists: `docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`).
**Required outcomes**:
- deterministic integration scenario runner
- verification tests for gossip propagation, panel evaluation, and attribution flow
- ops playbook v2 with common-failure runbook
- production-readiness delta analysis

### M-series parallel track — Rust consensus real liveness run (M-012+)

M-011 tooling (keygen + testnet_client + 4-validator harness) is committed with
`run_m011_workload_a_verdict=binary_complete`. The real 4-validator run requires
provisioning (running `--keygen`, `--gen-tls`, distributing binaries to VPS nodes).

**M-012**: Full BFT ECUTransfer round-trip — client-side AckFor collection, certificate
formation, broadcast. Completes owned-object fast path end-to-end across real machines.

**M-013**: Workload A real liveness run (4-validator live, epochs 1-12, silent-validator test).

### Deferred lane — Inbound HTTP machine-payment ingress (Window 595+)

Treasury-governed. Requires stablecoin-to-ECU conversion rules under CDL-047. Not on the
launch-critical path.

---

## 3. Window Roadmap (updated)

| Window | Focus | Status | Key gate |
|---|---|---|---|
| **555-564** | Transport governance (CDL-061, ADR-0025) | **CLOSED** | CDL-061 ratified; 8-probe canary |
| **565-574** | Transport operationalization + multi-machine packaging | **CLOSED** | `three_machine_testbed_primary_gate_passed` |
| **575-584** | Agent behavioral loop v1 + ECU attribution + settlement | **IN PROGRESS** (Phase 580 complete) | 7 agents live on 3-machine substrate, ECU attribution into settlement |
| **585-594** | Three-machine / seven-agent integration test | Planned | Deterministic end-to-end task cycle across 3 machines, 7 agents |
| **595+** | Inbound HTTP machine-payment ingress | Deferred | Treasury-governed conversion model |

**First testable milestone: approximately Phase 594** — now roughly 14 phases from 2026-04-17,
assuming Windows 575-584 and 585-594 close on primary path.

### Window 575-584: remaining phases

| Phase | Work item |
|---|---|
| 575-580 | COMPLETE (seq lock, RC0.1 constitutional locks, agent loop cutover, panel+submission integration) |
| 581 | ECU attribution, settlement, wallet query integration |
| 582 | CDL-V7 reproducibility disposition + outbound HTTP machine-payment skill decision |
| 583 | Coherence report + capsule v3.2 |
| 584 | Closure gate |

### Window 585-594: minimum work items

1. Integration test harness spec
2. Deterministic three-node / seven-agent scenario runner
3. Verification tests for gossip propagation, panel evaluation, and attribution flow
4. Ops playbook v2 with common-failure runbook
5. Production-readiness delta analysis
6. Coherence report + handoff

Public-release constitutional guidance: `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`

---

## 4. Security Posture Progression

| Window | Posture | Notes |
|---|---|---|
| 565-574 | Server TLS + `ILC-Signature` | Minimum acceptable for infrastructure proof; mTLS deferred |
| 575-584 | Same as 565-574 | Behavioral integration window; no transport re-authentication |
| 585-594 | Same (RC0 evaluation) | First public-readiness milestone assumes proven posture |
| Post-RC0 | mTLS hardening tranche | Certificate issuance, trust-store distribution, peer identity binding, rotation, negative-path |

---

## 5. Risk Register (updated)

| Risk | Severity | Window affected | Notes |
|---|---|---|---|
| CDL-V7 reproducibility rubric governance resolution | MODERATE | 575-584 | Must close before Phase 584; disposition due Phase 582 |
| Outbound HTTP machine-payment skill scope | LOW | 575-584 | Defer-or-attach decision at Phase 582 |
| M-series / Python-track convergence | LOW | 585-594 | Two separate transport stacks (Mysticeti QUIC vs Python HTTP); integration boundary TBD |
| Inbound payment pressures bleed into launch planning | LOW | 595+ | Keep treasury-governed inbound payments separate |

---

## 6. Relationship to Existing Artifacts

- `docs/specs/ilc_window_565_574_handoff_574_v0.1.md` — Window 565-574 canonical closure
- `docs/specs/ilc_window_575_584_candidate_phase_grouping_v0.1.md` — current window grouping
- `docs/specs/ilc_phase_575_584_sequence_lock_v0.1.md` — current window sequence lock
- `docs/specs/ilc_antigravity_context_capsule_v4.5.md` — current context capsule
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` — M-series Rust track
- `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md` — canonical transport decision
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md` — prior planning snapshot

---

*Updated 2026-04-17 to reflect Window 565-574 closure (`three_machine_testbed_primary_gate_passed`),
Window 575-584 progress through Phase 580, and M-series M-009/M-010/M-011 completion.*
*Next update recommended after Window 575-584 closes or when integration test harness scope is locked.*
