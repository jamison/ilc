# ILC Window 565-574 Candidate Phase Grouping v0.1

Status: candidate phase grouping - pre-sequence-lock
Date: 2026-04-01
Owner lane: G8 implementation cluster

This document translates the Window 555-564 handoff into a concrete implementation
window for the first three-machine testbed. It is the anchor document for the
Phase 565-574 prompt set.

---

## 1. Window purpose

Window 565-574 operationalizes the ratified CDL-061 envelope over real HTTP
between three separate machines, while adding the minimum startup, packaging,
and genesis-import flow needed to run those machines as a reproducible testbed.

This window has two linked lanes:

- Primary gate: transport operationalization. The window must prove that three
  machines can exchange valid CDL-061 envelope traffic using the existing
  `gossip_transport.py` and `gossip_peer_registry.py` surfaces.
- Secondary lane: packaging and genesis flow. The window must also prove that
  operators can package, start, stop, and re-start those nodes with imported
  genesis state and static peer configuration.

These are compatible requirements. They belong in the same window, but they are
not equal as pass criteria. Transport operationalization is the primary gate;
packaging and genesis are the co-equal supporting lane that makes the three-
machine proof reproducible rather than ad hoc.

---

## 2. Decisions locked before Phase 565

### 2.1 Runtime and packaging decisions

- Real HTTP transport and node startup/package flow both land in Window 565-574.
- The transport runtime remains a minimal wrapper around the ratified
  `ilc_core/network/d2d/gossip_transport.py` contract.
- The fuller node-integrated D2d orchestration redesign is intentionally
  deferred; this window must leave behind clean interfaces and test harnesses so
  that redesign can start immediately afterward without reopening transport
  governance.
- Packaging target for the first three-machine testbed is `venv + systemd`.
- Static peer configuration format for v1 is JSON.
- HTTP/2 fallback is enabled only through an explicit operator config switch in
  this window; automatic fallback is deferred to a later hardening tranche.

### 2.2 Identity, security, and lifecycle decisions

- TLS posture for the first three-machine testbed is server TLS plus
  protocol-layer `ILC-Signature`; mutual TLS is not in scope for this window.
- Genesis import/export remains compressed and explicit. This window does not
  attempt a production ceremony.
- Persistence remains minimal: startup configuration, imported genesis artifact
  references, and existing event logs are retained; durable recovery of pending
  epoch buffers is out of scope unless a later phase explicitly opens it.
- Minimum operator-visible observability is required. Runtime logs must preserve
  deterministic error tokens and enough context to diagnose three-machine test
  failures quickly.

### 2.3 Terminology policy

The project should stop using the external `x402` label in forward planning.
Historical references may keep it where needed for provenance, but Window 565+
planning should use ILC-owned names:

- outbound paid external capability lane: `HTTP machine-payment skill`
- inbound paid task-submission lane: `HTTP machine-payment ingress`

This avoids coupling ILC planning language to a third-party brand or suggesting
that ILC is committed to a specific external framework.

---

## 3. Hard pass condition for Window 565-574

Window 565-574 passes only if all of the following are true:

1. Three separate machines start nodes from packaged environments.
2. Each node loads a JSON static peer configuration into `GossipPeerRegistry`.
3. Each node imports the agreed genesis artifact successfully.
4. At least one machine sends ratified CDL-061 gossip traffic to the others over
   real HTTP transport.
5. Recipients validate the envelope, enforce the ratified header contract, and
   record deterministic success or failure in operator-visible logs.
6. HTTP/2 fallback can be enabled explicitly and tested in an environment where
   QUIC or UDP is unavailable.
7. Restarting a node preserves the minimum required state for startup and does
   not destroy the ability to rejoin the static peer set.
8. No DHT, dynamic peer discovery, multi-hop behavior, or agent-loop expansion
   is introduced in order to pass the milestone.

---

## 4. Deliverables and test gates

### 4.1 Transport wrapper deliverables

Deliverables:
- A real HTTP client/server wrapper around `gossip_transport.py`.
- A clean adapter boundary that is thin enough to replace later when the fuller
  node-integrated D2d runtime is designed.
- Explicit config for `transport_kind=quic` production mode and
  `transport_kind=http` fallback mode.

Test gates:
- Build and validate outgoing headers only through the ratified envelope helper.
- Reject malformed headers, forbidden CDL-039 fields, and non-single-hop values
  at the network boundary.
- Send and receive at least one valid gossip request across machine boundaries.
- Surface transport failures with deterministic error tokens or structured log
  fields rather than ad hoc text.

Unlocks for the later orchestration redesign:
- Stable adapter API for send/receive.
- Explicit startup contract for transport listeners.
- A black-box smoke harness that can be preserved while internals are refactored.

### 4.2 Packaging and genesis deliverables

Deliverables:
- JSON peer-config file format and loader.
- Genesis export/import format for test-grade multi-machine bootstrap.
- `venv + systemd` packaging path with documented service startup and shutdown.
- Minimal node lifecycle commands for start, stop, restart, and log inspection.

Test gates:
- A machine with no prior local state can import the genesis artifact and start.
- A node can restart under `systemd` and come back with peer config intact.
- Configuration errors fail fast with deterministic messages.
- Service logs are sufficient to distinguish startup failures, transport failures,
  and genesis import failures.

### 4.3 Lean three-machine validation plan

This window should not try to exhaustively discover every future defect. It
should close the known unknowns that block the first real networked testbed.

Required deterministic checks:
- Unit tests for transport wrapper boundary behavior.
- Unit tests for JSON peer-config loading and validation.
- Unit tests for genesis import/export helpers.
- A single-machine local integration test with loopback HTTP.
- A deterministic three-machine smoke run with expected log markers and success
  criteria.
- An explicit fallback run with HTTP/2 enabled by config.

Required expected results:
- Envelope send succeeds on the primary path.
- Explicit fallback path succeeds when enabled.
- Invalid config or invalid envelope fails with predictable error output.
- Logs make it obvious which machine failed and in which lane it failed.

---

## 5. Candidate phase map

### Phase 565 - Window 565-574 sequence lock

Purpose:
- Freeze the 10-phase implementation program and bind the hard pass condition.

Test focus:
- Sequence-lock integrity.
- Carry-forward alignment from the Window 564 handoff and roadmap v0.2.

### Phase 566 - Transport operationalization decision and boundary lock

Purpose:
- Lock the minimal wrapper architecture around `gossip_transport.py`.
- Lock explicit HTTP/2 fallback activation by configuration only.
- Lock server TLS plus `ILC-Signature` as the testbed identity posture.

Test focus:
- Boundary and scope tests only; no runtime yet.

### Phase 567 - Genesis/package/lifecycle scoping decision

Purpose:
- Lock JSON static peer config, test-grade genesis import/export, and the
  minimum `venv + systemd` lifecycle contract.

Test focus:
- Documentation and contract verification.

### Phase 568 - Real HTTP transport wrapper runtime

Purpose:
- Add the minimal real transport implementation around the ratified envelope.

Expected deliverables:
- New D2d transport runtime module.
- Runtime tests for send/receive, header use, and config wiring.

### Phase 569 - Transport hardening and fallback activation

Purpose:
- Harden the runtime around QUIC-primary and explicit HTTP/2 fallback behavior.
- Add negative-path coverage and mutation/canary protections as needed.

Expected deliverables:
- Hardening tests.
- Runtime or canary updates required to keep the transport lane protected.

### Phase 570 - Static peer-config JSON loader and startup wiring

Purpose:
- Connect JSON peer config to `GossipPeerRegistry` and node startup paths.

Expected deliverables:
- Config schema or loader module.
- Tests for invalid config, duplicate peers, and startup wiring behavior.

### Phase 571 - Packaging and lifecycle runtime (`venv + systemd`)

Purpose:
- Add the minimum packaging and lifecycle artifacts for three-machine startup.

Expected deliverables:
- Service template(s), runtime wrapper scripts, and lifecycle tests.
- Deterministic log/output expectations for start, stop, restart, and failure.

### Phase 572 - Deterministic three-machine smoke harness

Purpose:
- Prove the full primary gate and secondary lane in one repeatable run.

Expected deliverables:
- Smoke harness script(s).
- Deterministic expected results and failure markers.

### Phase 573 - Coherence report and capsule v3.0

Purpose:
- Record the final transport, packaging, and lifecycle state after the smoke
  harness passes.

Test focus:
- Cross-phase coherence and carry-forward correctness.

### Phase 574 - Window 565-574 closure gate and handoff

Purpose:
- Close the window only if the three-machine testbed gate has passed and the
  next-window carry-forwards are explicit.

Test focus:
- Closure gate, regression suite, and handoff completeness.

---

## 6. Protected boundaries and out-of-scope items

Protected boundaries for this window:
- `ilc_core/network/d2d/gossip_transport.py` remains the ratified envelope
  contract surface; it may be consumed but not constitutionally expanded without
  a new governance lane.
- `ilc_core/network/d2d/gossip_peer_registry.py` remains `static_v1`; no DHT,
  no dynamic discovery, no reputation-based peer selection.
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` remains single-hop
  only; multi-hop stays deferred.
- `ilc_core/economics/passive_ecu_attribution_runtime.py` is not recalibrated in
  this window.
- `ilc_core/node/devnet.py` may remain as the local deterministic dev harness;
  replacing it is not a window goal.

Out of scope:
- mTLS.
- Automatic fallback negotiation between HTTP/3 and HTTP/2.
- Dynamic peer discovery or DHT.
- Multi-hop gossip.
- Agent behavioral loop implementation.
- Inbound `HTTP machine-payment ingress`.
- Treasury or ECU governance changes.

---

## 7. Evolution path beyond the three-machine testbed

### 7.1 What this window must prove

Window 565-574 is the infrastructure milestone. It proves that ILC can leave the
single-process devnet and operate across real machine boundaries with stable
transport, packaging, and startup flow.

### 7.2 What should evolve next

Recommended path after this window:

1. Window 565-574 - transport operationalization + multi-machine packaging.
2. Window 575-584 - agent behavioral loop plus outbound `HTTP machine-payment
   skill` lane.
3. Window 585-594 - deterministic three-machine / seven-agent integration and
   first public release-candidate evaluation.
4. Window 595+ - inbound `HTTP machine-payment ingress` as a separate,
   treasury-governed lane.

### 7.3 Hardening items for post-testbed work

The following are important, but they are not blockers for the first
three-machine milestone:
- fuller node-integrated D2d orchestration replacing the minimal wrapper
- mutual TLS
- automatic fallback from HTTP/3 to HTTP/2
- richer peer-registry operations
- more polished genesis/bootstrap ceremony

Recommended release framing:
- RC0 infrastructure proof: after Window 565-574.
- RC0 public-release candidate evaluation: after Window 585-594, assuming the
  seven-agent integration milestone passes.
- RC1 hardening tranche: mTLS, automatic fallback, and stronger operational
  packaging.

---

## 8. Predecessor references

- `docs/specs/ilc_window_555_564_handoff_564_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`
- `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md`
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.9.md`
- `docs/specs/ilc_integration_coherence_report_563_v0.1.md`

---

This candidate grouping is deliberately implementation-first. Governance for the
transport envelope is already closed by CDL-061. The next failure mode is not
constitutional ambiguity; it is under-specified operational work. The phase
prompts for Window 565-574 should therefore optimize for clean boundaries,
deterministic test gates, and fast learning on three real machines.
