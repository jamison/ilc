# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.2
**Produced**: 2026-03-31
**Session context**: Post-Window 555-564 handoff; capsule v2.9 current
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.1.md`
**Purpose**: Working architectural reference for the remaining launch path after Window 555-564 completed.

---

## Background

This document answers the same core question as v0.1: what remains before ILC has a testable package running across three separate computers with seven active agents?

The difference is that the transport-governance lane is no longer hypothetical. Window 555-564 has completed, ADR-0025 is accepted, CDL-061 is ratified, and the D2d package now contains the envelope and peer-registry modules needed for the next implementation step.

---

## 1. Current State After Window 555-564

### 1.1 Implemented subsystems

| Subsystem | Path | Notes |
|---|---|---|
| Consensus engine | `ilc_core/consensus/` | Sponsor graph, governance, CDL-V3 diversity floor, CDL-V7 Popperian gate |
| Genesis bootstrap | `ilc_core/genesis/` | `genesis_validator_bootstrap_runtime_480.v0.1`; admission control bootstrap and schema work |
| Ledger and settlement | `ilc_core/ledger/` | Canon bundle pipeline, settlement verification, persistent backend, stake snapshots |
| D2d transport invariants | `ilc_core/network/d2d/gossip.py`, `peer.py`, `interface.py` | CDL-039 computational transport invariants |
| CDL-060 gossip runtime | `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` | Ratified single-hop, epoch-boundary atomic accumulation |
| CDL-061 HTTP envelope | `ilc_core/network/d2d/gossip_transport.py` | Ratified header contract, status semantics, CBOR production encoding, HTTP/2 fallback allowed |
| Static peer registry v1 | `ilc_core/network/d2d/gossip_peer_registry.py` | Static-v1 only, HTTPS-only endpoints, lexicographic fanout selection, no DHT |
| Passive ECU attribution runtime | `ilc_core/economics/passive_ecu_attribution_runtime.py` | `rate=0.20`, `floor=0.05`, `cap=0.15`, authorship primacy enforced |
| Node runtime | `ilc_core/node/node_v0.py` | `ILCNodeV0` with NDJSON event log |
| In-process devnet | `ilc_core/node/devnet.py` | `InProcessGossipBus`; deterministic seeded fanout inside one process |
| Validator subsystems | `ilc_core/validator/` | Re-admission, staking liveness, trust tier runtimes |
| CLI tooling | `ilc_core/cli/` | D2e CLI, agent CLI, lifecycle management, canonical operations, MCP integration |
| Work queue | `ilc_core/work/task_queue.py` | Task scheduling and management |
| Agent identity and lifecycle | `ilc_core/identity/`, `ilc_core/node/` | `agent_id_runtime.py`; `timed_out_lifecycle_runtime_411.py` |
| Wire transport contract | `ilc_core/network/wire_transport_runtime.py` | Abstract kind-level contract; allowed kinds remain `http`, `libp2p`, `quic` |

### 1.2 What is now complete

Window 545-554 closed the economic signal lane:
- `centrality_delta_gossip_runtime.py` landed in Phase 548
- `passive_ecu_attribution_runtime.py` landed in Phase 550

Window 555-564 closed the transport-governance lane:
- ADR-0025 accepted HTTP/3 over QUIC as production with HTTP/2 fallback
- CDL-061 was opened, implemented against, and ratified
- `gossip_transport.py` and `gossip_peer_registry.py` are now committed and tested
- the mutation canary grew to 8 probes

Window 555-564 also closed one cross-module administrative invariant:
- ADR-0023 recorded `recommended_decay_floor >= recommended_u_floor`

### 1.3 Critical observation: protocol surface exists, deployment surface does not

The repository now has the ratified envelope contract and the static peer inventory primitives, but it still does not have actual cross-machine HTTP client or server I/O wired into node startup. `InProcessGossipBus` remains the only working multi-node execution path. Crossing a machine boundary is no longer blocked by governance; it is blocked by operational runtime work.

---

## 2. Remaining Gaps

### Gap 1 — Transport operationalization and peer-config packaging

The transport layer now knows how to build and validate the CDL-061 envelope, but it still does not open sockets, bind HTTP/3 listeners, negotiate HTTP/2 fallback, or load a peer registry from operator-managed configuration. This is the first remaining implementation gap.

**Estimated scope**: Window 565-574.
**Required outcomes**:
- actual multi-machine HTTP/3 or HTTP/2 transport I/O around the existing envelope contract
- static peer config format for `GossipPeerRegistry`
- fallback activation path for environments where UDP or QUIC is blocked
- operator-visible observability and deployment guidance

### Gap 2 — Multi-machine packaging and genesis import/export

Three separate machines still need a reproducible way to receive genesis state, import it, start nodes, stop them cleanly, and recover from crashes under the CDL-046 lifecycle constraints. This gap now sits next to the transport work, not after it.

**Estimated scope**: Window 565-574, likely in the same lane as transport operationalization.
**Required outcomes**:
- genesis export and import format
- node lifecycle runtime for startup, shutdown, and crash recovery
- packaging choice for test deployment (venv + systemd or container)
- ops playbook v1

### Gap 3 — Functional agent behavioral loop

`tools/agent_loop_v0.sh` is still pseudocode. Seven agents means seven separate processes with key material, `agent_id`, polling behavior, model invocation, graph submission, and ECU claims. The 7+1 evaluation panel must be wired into the live submission path.

**Estimated scope**: Window 575-584.
**Required outcomes**:
- protocol-compliant agent loop daemon
- 7+1 panel wiring in the submission pipeline
- ECU attribution claims integrated with the ledger path
- CDL-V7 reproducibility rubric operationalized
- outbound HTTP machine-payment skill lane attached through existing MCP
  integration

### Gap 4 — Three-machine / seven-agent integration harness

Once transport operationalization, packaging, and the agent loop exist, the next gap is the first deterministic full-system proof: three nodes on separate machines, seven agent processes, one end-to-end task cycle, and verification of gossip propagation, evaluation flow, and ECU attribution.

**Estimated scope**: Window 585-594.
**Required outcomes**:
- deterministic integration scenario runner
- verification tests for gossip, panel, and attribution behavior
- ops playbook v2
- production-readiness delta analysis

### Deferred lane — Inbound HTTP machine-payment ingress

Inbound HTTP machine-payment ingress remains explicitly out of the
launch-critical path. It is treasury-governed and should not be merged into
transport or agent-loop work.

**Estimated scope**: Window 595+.
**Governance note**: requires stablecoin-to-ECU conversion rules under CDL-047.

---

## 3. Updated Window Roadmap

| Window | Focus | Approx phases | Key gate |
|---|---|---|---|
| **565-574** | Transport operationalization + multi-machine packaging | ~10 | 3 machines can exchange CDL-061 envelope traffic with static peers and imported genesis state |
| **575-584** | Agent behavioral loop v1 + outbound HTTP machine-payment skill lane | ~10 | 7 agent processes wired to the protocol with panel evaluation and ECU claim flow |
| **585-594** | Three-machine / seven-agent integration test | ~10 | One deterministic end-to-end task cycle passes across all 3 machines and 7 agents |
| **595+** | Inbound HTTP machine-payment ingress lane | TBD | Treasury-governed conversion model defined separately from launch-critical transport work |

**First testable milestone: approximately Phase 594** — now roughly 30 phases from the close of Window 555-564, assuming the remaining windows close on their primary path.

### Window 565-574: transport operationalization + multi-machine packaging

Minimum work items:
1. HTTP/3 client and server binding around `gossip_transport.py`
2. HTTP/2 fallback activation path for blocked-UDP environments
3. Static peer config format and loader for `GossipPeerRegistry`
4. Genesis state serialization and multi-machine import
5. Node lifecycle runtime for startup, graceful shutdown, and crash recovery per CDL-046
6. Ops playbook v1 and packaging choice for test deployment
7. Coherence report + closure gate

### Window 575-584: agent behavioral loop v1 + outbound HTTP machine-payment skill

Minimum work items:
1. Agent loop spec
2. Agent loop runtime replacing `tools/agent_loop_v0.sh`
3. 7+1 panel wiring in the submission pipeline
4. ECU attribution claim submission flow
5. CDL-V7 reproducibility harness and governance resolution
6. HTTP machine-payment outbound MCP skill for external service payments
7. Coherence report + closure gate

### Security progression across the next windows

- Window 565-574 proves the first three-machine testbed with server TLS plus
  protocol-layer `ILC-Signature`. This is the minimum acceptable identity
  posture for the infrastructure proof; mutual TLS is intentionally out of
  scope here.
- Window 575-584 should continue on that same posture while the agent loop is
  brought online. The objective in that window is behavioral integration, not
  transport re-authentication redesign.
- Window 585-594 is the first deterministic RC0 public-release-candidate
  evaluation milestone. It should still assume the already-proven server TLS +
  `ILC-Signature` posture unless a dedicated hardening window is inserted
  earlier.
- Mutual TLS belongs in the first post-RC0 hardening tranche, immediately after
  the Window 585-594 integration milestone closes successfully. The hardening
  work should include certificate issuance, trust-store distribution, peer
  identity binding, rotation, and negative-path handshake testing.

### Window 585-594: three-machine / seven-agent integration test

Minimum work items:
1. Integration test harness spec
2. Deterministic three-node / seven-agent scenario runner
3. Verification tests for gossip propagation, panel evaluation, and attribution flow
4. Ops playbook v2 with common-failure runbook
5. Production-readiness delta analysis
6. Coherence report + handoff

Public-release constitutional guidance for this window now lives in:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`

---

## 4. Updated Risk Register

| Risk | Severity | Window affected | Notes |
|---|---|---|---|
| Multi-machine HTTP/3 operationalization is more complex than the ratified envelope layer suggests | MODERATE | 565-574 | Governance is done; complexity is now in runtime, packaging, and observability |
| Node lifecycle under CDL-046 needs more explicit runtime semantics for crash recovery | MODERATE | 565-574 | Deployment crashes are not the same as stake or admission failures |
| CDL-V7 reproducibility rubric requires a new CDL rather than an ADM update | MODERATE | 575-584 | Still unresolved and must close before the agent loop is protocol-compliant |
| Outbound HTTP machine-payment integration expands external dependency surface | LOW | 575-584 | Operational and provider risk, not a transport-architecture blocker |
| Inbound HTTP machine-payment pressures bleed into launch planning too early | LOW | 595+ | Keep treasury-governed inbound payments separate from the launch-critical path |

---

## 5. Scope Compression Notes

The current roadmap already benefits from one major compression: Window 555-564 is complete, so the launch path no longer needs to spend a future window deciding or ratifying the transport envelope. The main compression questions that remain are operational, not constitutional.

Potential internal-proof compression options:
- use HTTP/2 fallback first in constrained test environments while preserving HTTP/3 as production binding
- use a manual test-grade key ceremony before a more polished multi-machine bootstrap flow exists
- use a fixed model endpoint inside the agent loop before dynamic model routing is introduced

These are acceptable for an internal proof-of-concept if they are called out as such. They are not enough for a public readiness claim.

---

## 6. Relationship to Existing Artifacts

- `docs/specs/ilc_window_555_564_handoff_564_v0.1.md` — canonical closure and carry-forward record for the completed transport window
- `docs/specs/ilc_antigravity_context_capsule_v2.9.md` — current context capsule
- `docs/specs/ilc_integration_coherence_report_563_v0.1.md` — transport and registry coherence record
- `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md` — canonical transport decision
- `docs/research/ilc_http_gossip_transport_x402_context_v0.1.md` — historical context for the ADR decision
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.1.md` — prior planning snapshot before Window 555-564 completed

---

*Updated after Window 555-564 closure to reflect ADR-0025 acceptance, CDL-061 ratification, and the completed D2d transport-governance lane.*
*Next update recommended after Window 565-574 planning or when the estimate to the first multi-machine milestone changes materially.*
