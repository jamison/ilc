# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.1
**Produced**: March 2026
**Session context**: Window 545-554 planning; capsule v2.7
**Purpose**: Working architectural reference for coordinating between local review (Claude Code) and Codex — not a formal phase artifact or sequence-locked document.

---

## Background

This document answers the question: **what remains before ILC has a testable package running across three separate computers with seven active agents?**

It synthesizes findings from a full filesystem audit of `ilc_core/` conducted at the close of Window 544 (Phase 544 complete; capsule v2.7 current).

---

## 1. What Is Already Implemented

The core protocol is substantially more complete than the phase number might suggest. The G8 constitutional track (CDL ratifications, simulation calibrations, coherence reports) has been running in parallel with a significant amount of runtime implementation work.

### 1.1 Implemented subsystems

| Subsystem | Path | Notes |
|---|---|---|
| Consensus engine | `ilc_core/consensus/` | Full implementation — sponsor graph, governance, CDL-V3 diversity floor, CDL-V7 Popperian gate |
| Genesis bootstrap | `ilc_core/genesis/` | `genesis_validator_bootstrap_runtime_480.v0.1`; admission control bootstrap; schema and work task |
| Ledger and settlement | `ilc_core/ledger/` | `settlement_verification.py`, canon bundle pipeline, persistent backend, stake snapshots |
| D2d gossip layer | `ilc_core/network/d2d/` | Phase 382 — `gossip.py`, `peer.py`, `interface.py`; CDL-039 transport invariants computationally enforced |
| Node runtime | `ilc_core/node/node_v0.py` | `ILCNodeV0` with NDJSON event log |
| In-process devnet | `ilc_core/node/devnet.py` | `InProcessGossipBus` — multi-node simulation, single process, deterministic seeded fanout |
| Validator subsystems | `ilc_core/validator/` | Re-admission, staking liveness, and trust tier runtimes |
| CLI tooling | `ilc_core/cli/` | D2e CLI, agent CLI, lifecycle management, canonical operations, MCP integration |
| Work queue | `ilc_core/work/task_queue.py` | Task scheduling and management |
| Agent identity and lifecycle | `ilc_core/identity/`, `ilc_core/node/` | Phase 410: `agent_id_runtime.py`; Phase 411: `timed_out_lifecycle_runtime_411.py` |
| Wire transport spec | `ilc_core/network/wire_transport_runtime.py` | Abstract contract; allowed kinds: `http`, `libp2p`, `quic`; **no actual socket binding** |
| Mining benchmark | `ilc_core/mining/benchmark.py` | Performance benchmarking tooling |

### 1.2 What Window 545-554 will add (in progress at Phase 547)

- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` — CDL-060 centrality-delta gossip runtime (planned Phase 548)
- `ilc_core/economics/passive_ecu_attribution_runtime.py` — passive ECU attribution runtime (planned Phase 550)

These will be the economic signal layer on top of the gossip infrastructure: centrality propagation and the passive attribution formula (`rate=0.20`, `decay_floor=0.05`, `attribution_cap=0.15`). Phases 545-547 are complete; Phases 548-554 are planned.

### 1.3 Critical observation: in-process vs. distributed

The devnet (`InProcessGossipBus`) runs all nodes in a single Python process. `wire_transport_runtime.py` defines an abstract transport contract but nothing binds to actual TCP/IP sockets. Everything works end-to-end — but only within one machine, one process. **Crossing a machine boundary is the primary unresolved gap.**

---

## 2. The Four Remaining Gaps

### Gap 1 — Real network transport binding

`wire_transport_runtime.py` specifies three allowed transport kinds (`http`, `libp2p`, `quic`) but nothing binds to actual sockets. `InProcessGossipBus` routes all gossip messages in-memory. Crossing a machine boundary requires binding the D2d gossip layer to a real transport. ADR-0025 (Accepted) selects HTTP/3 over QUIC (`kind=quic` under CDL-024) as the production binding, with HTTP/2 over TCP (`kind=http`) as the fallback. CDL-039 topology privacy constraints must hold at the network layer, not just in-process.

**Estimated scope**: 1 full window.
**CDL track**: one new CDL covering the ILC gossip HTTP envelope contract (header field set, CDL-039 exclusions, status code semantics, CDL-060 hop enforcement). See ADR-0025.

### Gap 2 — Multi-machine packaging and genesis bootstrap

Three separate machines need: a way to export/import the genesis state, a minimal key ceremony (test-grade is acceptable), and scripts to bring up `ILCNodeV0` on each. The node currently starts in-process with no startup/shutdown lifecycle outside of devnet. Genesis state serialization and node lifecycle management (startup, graceful shutdown, crash recovery per CDL-046) are not yet implemented for distributed operation.

**Estimated scope**: 1 full window.
**CDL track**: possibly one CDL covering node packaging and deployment contracts.

### Gap 3 — Functional agent behavioral loop

`tools/agent_loop_v0.sh` is explicitly labeled pseudocode with TODO placeholders for actual Antigravity/Codex triggering. Seven agents means seven separate processes, each with its own keypair and `agent_id`, each: polling for task prompts, calling an AI model (Antigravity/Codex), submitting output back to the protocol graph, and collecting ECU attribution. The 7+1 evaluation panel (CDL-V7 Popperian gate) needs to be wired into the submission pipeline.

This is also where the **CDL-V7 cross-agent reproducibility rubric** — the MODERATE finding deferred from Phase 325 — becomes concrete. That rubric requires a tolerance-bound evaluation protocol demonstrating that different agent instances produce comparable outputs on equivalent inputs. Whether this requires a new CDL or can be resolved via an ADM update is an open governance question for Window 575-584.

**Estimated scope**: 1 full window.
**CDL track**: CDL-V7 reproducibility rubric resolution; possibly no new CDL if ADM update suffices.

### Gap 4 — Integration test harness

A deterministic end-to-end test that: starts 3 nodes across machines, spawns 7 agent processes, drives a task through the full pipeline, and verifies gossip propagation, CDL replication, and ECU attribution flow. This is the first real proof-of-concept milestone where all four prior gaps are demonstrated working together.

**Estimated scope**: 1 full window.
**Deliverable**: Ops playbook v2 with runbook for common failure modes; handoff for any production-readiness gaps identified.

---

## 3. Approximate Window Roadmap

| Window | Focus | Approx phases | Key gate |
|---|---|---|---|
| **545-554** | CDL-060 gossip runtime + passive ECU attribution | 10 | *(current window)* |
| **555-564** | D2d real transport binding | ~10 | D2d gossip over sockets; CDL-039 enforced end-to-end |
| **565-574** | Multi-machine packaging + genesis export/import | ~10 | Genesis export/import; node lifecycle on 3 machines |
| **575-584** | Agent behavioral loop v1 | ~10 | 7 agent processes wired to protocol; 7+1 panel live |
| **585-594** | Three-machine / seven-agent integration test | ~10 | Full-pipeline end-to-end test passes |

**First testable milestone: approximately Phase 594** — roughly 40 phases from the close of Window 545-554.

### Window 555-564: D2d real transport binding

~6 substantive phases + coherence + closure gate.

**Transport binding decision** (see ADR-0025): HTTP/3 over QUIC is the selected binding. This satisfies ADR-0011's QUIC requirement (HTTP/3 IS QUIC at the transport layer) while enabling a lightweight HTTP envelope design for the gossip protocol. HTTP/2 over TLS/TCP is the development/test-environment fallback where UDP/QUIC may be blocked. No libp2p dependency introduced at v1.

The gossip envelope uses standard HTTP headers for ILC-specific protocol semantics, inspired by the architectural pattern demonstrated by Coinbase's x402 protocol — custom protocol semantics layered on standard HTTP headers without a bespoke wire format.

Work items:
1. ILC gossip HTTP envelope spec (header field set, CBOR payload schema, CDL-039 exclusions, status code semantics)
2. One new CDL locking the gossip HTTP envelope contract (CDL-061 or next available)
3. HTTP/3 transport adapter for `ilc_core/network/d2d/` (static peer config; no DHT)
4. CDL-039 enforcement at the header layer (opaque channel, no `creator_agent_id`, non-inferrable topology)
5. Hardening + canary update (new probes for transport-layer invariants)
6. Coherence report + closure gate

CDL track: one new CDL covering the ILC gossip HTTP envelope contract (analogous to CDL-024 for wire transport, scoped to the gossip sub-layer).

### Window 565-574: Multi-machine packaging + genesis export/import

~6 substantive phases + coherence + closure gate.

Work items:
1. Packaging spec — Python venv + systemd unit or container (protocol-neutral; either is acceptable for the test milestone)
2. Genesis state serialization for multi-machine import
3. Test-grade key ceremony (abbreviated CDL-040/042 admission flow)
4. Node lifecycle runtime (startup, graceful shutdown, crash recovery per CDL-046)
5. Ops playbook v1
6. Coherence report + closure gate

CDL track: possibly one CDL covering node packaging and deployment contracts.

### Window 575-584: Agent behavioral loop v1

~6 substantive phases + coherence + closure gate.

Work items:
1. Agent loop spec
2. Agent loop runtime — replaces `tools/agent_loop_v0.sh` pseudocode with a protocol-compliant daemon
3. 7+1 panel wiring (CDL-V7 gate in the submission pipeline)
4. ECU attribution claim submission (connects agent output to the ledger pipeline)
5. Cross-agent reproducibility test against the CDL-V7 rubric (operationalizes the MODERATE finding from Phase 325)
6. x402 outbound skill — ILC agent pays external AI services via x402 MCP skill; attaches to existing `ilc_core/cli/` MCP integration; ADR-level decision only, no CDL required
7. Coherence report + closure gate

CDL track: CDL-V7 reproducibility rubric — ADM update or new CDL depending on governance review.

### Window 585-594: Three-machine / seven-agent integration test

~6 substantive phases + coherence + closure gate.

Work items:
1. Integration test harness spec
2. Deterministic scenario runner (bring up 3 nodes + 7 agents, drive one full task cycle end-to-end)
3. Verification tests: gossip propagation, ECU attribution flow, panel evaluation
4. Ops playbook v2 with runbook for common failure modes
5. Gap analysis: what remains for production readiness beyond the test milestone
6. Coherence report + handoff

---

## 4. Risk Register

| Risk | Severity | Window affected | Notes |
|---|---|---|---|
| CDL-V7 cross-agent reproducibility rubric requires a new CDL rather than ADM update | MODERATE | 575-584 or parallel track | Deferred since Phase 325; must be resolved before agent loop is considered protocol-compliant |
| D2d transport adapter requires more CDL governance than one CDL | LOW | 555-564 | Unlikely; CDL-024 analogy is a clean precedent. ADR-0025 selects HTTP/3; one envelope CDL is sufficient |
| Node lifecycle / crash recovery under CDL-046 requires scope extension to CDL-046 | LOW | 565-574 | CDL-046 covers `timed_out` with `stake_full_release`; a deployment crash is a different scenario and may need explicit handling |
| Agent loop AI-model integration has external dependency (Antigravity/Codex API surface) | LOW | 575-584 | API surface is controlled; risk is to scheduling, not architecture |

**The CDL governance load in Windows 555-594 is significantly lighter than Windows 328-413.** The V-series and node-schema CDL cluster are complete. Most remaining work is implementation rather than constitutional deliberation.

---

## 5. Notes on Scope Compression

The estimate above targets correctness and protocol compliance at each step. If the goal is the earliest possible three-machine / seven-agent demonstration, some compression is feasible:

- **Transport (555-564)**: HTTP/3 is the selected binding per ADR-0025. HTTP/2 over TCP is the permitted fallback for test environments where UDP/QUIC is blocked. Static peer config is already the v1 design; no compression needed here.
- **Packaging (565-574)**: Use a manual key ceremony rather than a full CDL-compliant one, with explicit acknowledgment that the production ceremony is a Window 565-574 follow-on.
- **Agent loop (575-584)**: Stub the AI-model call to a fixed endpoint rather than dynamic Antigravity routing. Demonstrates the pipeline without the full model-selection infrastructure.

These compressions would demonstrate the three-machine architecture earlier but leave protocol gaps that require subsequent CDL work before any mainnet readiness claim. The compression path is viable for an internal proof-of-concept; it is not viable for a public testnet.

---

## 6. Relationship to Existing Roadmap Artifacts

- `docs/ILC_Master_Development_Plan_v0.4.md` — overarching master plan (this document is more specific to the final integration gap)
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md` — 91-task roadmap (earlier scope; this document supersedes its cross-machine section)
- `docs/specs/ilc_antigravity_context_capsule_v2.7.md` — current primary context doc; CDL-052/059/060 ratified; CDL-053 reserved
- `docs/specs/ilc_window_545_554_candidate_phase_grouping_v0.1.md` — Window 545-554 phase guidance (current window)
- `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md` — formal decision record for HTTP/3 as D2d gossip transport
- `docs/research/ilc_http_gossip_transport_x402_context_v0.1.md` — conversation context and design rationale for ADR-0025

---

*Based on filesystem audit of `ilc_core/` at Window 544 close and Window 545-554 planning session.*
*Updated March 2026 post-Phase 547 to reflect ADR-0025 (HTTP/3 gossip transport) and x402 agent skill track.*
*Next update recommended at Window 554 handoff or when any gap estimate changes significantly.*
