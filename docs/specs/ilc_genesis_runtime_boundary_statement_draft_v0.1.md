# ILC Genesis/Runtime Boundary Statement — Draft v0.1

Status: **non-normative draft** — does not override ratified decision-log state or implemented code  
Date: 2026-02-18  
Author: Claude Opus 4.6 (Strategic Architectural Reviewer)  
Precedence: This document is subordinate to the Master Principle List v5.1, whitepaper v5.2, and all ratified CDL entries.  
Extraction brief: `docs/specs/ilc_claude_extraction_brief_v0.1.md`  
Provenance: Evidence extracted from raw corpus files (Z_Past_Chats). All matrix line references verified against `constitution_dredge_matrix_v0.2.md` (commit 92fa9b7). Source file and line references verified against raw corpus.

---

## 1. Scope

Provide a single-source answer to: **What is the Genesis release, and what is it not?** This document is intended for external reviewers, new contributors, and cross-team collaborators who need to understand the boundaries of the Genesis codebase without reading the full specification corpus.

### Non-Goals

- This document does not specify internal architecture of the Genesis codebase (see phase walkthroughs).
- This document does not define the post-Genesis roadmap in detail.
- This document does not serve as a user manual or API reference.

---

## 2. Decision Table

| Item | Status | Authority |
|---|---|---|
| Genesis is a scoring kernel + graph primitives + canonical encoding | **Implemented** | Codebase (substantial tested module surface through Phase 224) |
| The seven truth primitives are the genesis-scope operations | **Ratified** | Master Principle List v5.1 |
| Canonical encoding: DAG-CBOR, CIDv1, COSE Sign1, NDJSON for logs | **Ratified** | Master Principle List v5.1 |
| ECU scoring uses four-component model (reuse, contradiction, validation, path) | **Implemented** | node_value_kernel.py |
| Freshness gate, diversity weighting, refutation-profitability invariant | **Implemented** | Various kernel modules |
| Token distribution, vesting, slashing | **Simulated** | Oct 2025 simulation framework; NOT in Genesis code |
| CapProof (per-epoch capability check-ins) | **Designed** | Oct/Nov 2025 main thread; NOT in Genesis code |
| Consensus protocol (distributed finalization) | **Designed** | Whitepaper; NOT in Genesis code |
| Token economy (minting, burning, transfers, AMM) | **Designed** | Oct 2025 main thread; NOT in Genesis code |
| Agent SDK | **Not yet specified** | Strategic analysis only |
| Network protocol (P2P, gossip, shard routing) | **Not yet specified** | Future architecture |

---

## 3. What Genesis IS

The Genesis release is an **epistemic scoring and graph framework** that implements the foundational logic for evaluating knowledge claims in a multi-agent environment. Specifically:

### 3.1 Graph Primitives (Implemented)

- **Node creation and addressing:** Content-addressed nodes using CIDv1. Nodes represent claims, assertions, refutations, and revisions.
- **Edge semantics:** Typed edges (supports, refutes, depends_on, equivalent) with propagation coefficients.
- **The seven truth primitives:** assert.truth, validate.claim, contradict.assert, refute.claim, revise.assert, link.claim, commit.epoch. These are the genesis-scope operations through which agents interact with the graph.

### 3.2 Scoring Kernel (Implemented)

- **ECU computation:** Four-component weighted scoring (reuse, contradiction-resistance, validation, path diversity) producing a single ECU value per finalized node.
- **Freshness gate:** Exponential decay on stale claims (lambda=0.25, floor=0.85).
- **Reuse-diversity weighting:** Penalizes single-actor gaming; rewards cross-agent endorsement.
- **Refutation-profitability invariant:** Structurally ensures that challenging incorrect claims is more profitable than passively validating them.

### 3.3 Simulation and Analysis Framework (Implemented)

- **Closed-loop simulation harness:** Supports multi-epoch simulations with configurable agent populations, skill distributions, and protocol parameters.
- **Telemetry and metrics:** ECU distributions, finalization rates, refutation latency, diversity indices.
- **Parameter sweep infrastructure:** Used to validate the simulation-derived parameters (quorum size, cluster damping, throttling, etc.).

### 3.4 Canonical Encoding (Implemented)

- **DAG-CBOR** for commitment bytes.
- **CIDv1** for node identification.
- **COSE Sign1** for signature envelopes.
- **NDJSON** for log output.

### 3.5 Configuration and Governance Foundations (Implemented)

- **Protocol parameter registry:** Locked configuration for Genesis-scope parameters.
- **Decision log infrastructure:** CDL entries tracking ratified decisions with evidence and precedence.

---

## 4. What Genesis is NOT

### 4.1 NOT a Running Token Economy

Genesis does not mint, transfer, burn, or manage ILC tokens. The ECU scoring kernel computes what a claim is *worth* (in ECU units), but does not convert ECU to ILC, manage wallets, process transactions, or enforce vesting/slashing. The monetary layer (B_e, P_e, vesting, burns) is designed and simulation-validated but not implemented.

**Implication for reviewers:** When the codebase references "rewards" or "payouts," these are ECU scores — measures of epistemic value — not token transfers.

### 4.2 NOT a Distributed Network

Genesis runs as a single-process or local-simulation framework. There is no peer-to-peer networking, gossip protocol, shard routing, or distributed consensus. The graph is stored locally. Multiple agents are simulated within a single process, not distributed across nodes.

**Implication for reviewers:** All "agent" interactions in the Genesis codebase are function calls within a simulation harness, not network messages between independent processes.

### 4.3 NOT a Consensus Protocol

Genesis does not implement distributed agreement on graph state. The quorum mechanism (k-of-m reviewers) is modeled in simulation but not implemented as a Byzantine fault-tolerant consensus protocol. There is no block production, no leader election, no finality gadget.

**Implication for reviewers:** "Finalization" in the Genesis codebase means "passed the scoring threshold in simulation," not "agreed upon by a distributed network."

### 4.4 NOT the Agent SDK

Genesis provides the primitives that a future SDK will wrap, but does not provide an agent-facing interface. There is no stable public API contract, no wire protocol, no client library. Agents interact with the scoring kernel through Python function calls in the simulation harness.

**Implication for reviewers:** The interface between agents and the protocol will change significantly between Genesis and the first SDK release.

### 4.5 NOT a CapProof or Runtime System

Genesis does not include the per-epoch capability proofs (CapProof), hardware telemetry integration (NVML/DCGM), runtime backend selection (TensorRT/CUDA), or scheduling/pricing infrastructure. These are designed and documented but are post-Genesis deliverables.

---

## 5. The Genesis Boundary Principle

**Genesis implements the epistemic evaluation logic that determines what claims are worth. Everything that happens after that evaluation — converting worth to tokens, distributing tokens to agents, managing token lifecycle — is post-Genesis scope.**

This boundary is deliberate. The scoring kernel is the intellectual core of ILC — the part that must be correct, well-tested, and architecturally sound before any economic machinery is built on top of it. Genesis is the foundation; the token economy is the building.

### 5.1 Rationale for This Boundary

The historical corpus articulates this as: ratified parameters and implemented code are "strong priors, not immutable truth." The Genesis release establishes the epistemic scoring framework as a validated foundation, while explicitly acknowledging that:

- Parameters may be tuned as the network operates under real conditions.
- Mechanisms designed in simulation may need adjustment when implemented in a distributed system.
- The scoring kernel's outputs (ECU values) are inputs to a monetary layer that doesn't exist yet.

This is not a weakness — it is principled engineering. Build the foundation, validate it, then build the structure on top.

---

## 6. What This Does Not Imply

1. **Not a claim that Genesis is incomplete.** Genesis is a complete, self-contained deliverable: a scoring kernel with graph primitives, broad passing test coverage, and a simulation framework. It is complete *for its scope*.
2. **Not a claim that post-Genesis work is speculative.** The token economy, consensus protocol, and SDK are designed with concrete parameters, simulation-validated where possible, and documented. They are deferred, not undefined.
3. **Not a claim that Genesis parameters are provisional.** Ratified parameters (CDL entries) are binding unless formally revised through the decision-log process. The "strong priors" framing applies to the designed-but-unratified parameters.
4. **Not a deprecation of simulation results.** Simulation findings are valuable empirical evidence. They are inputs to ratification, not substitutes for it.
5. **Not a roadmap.** This document defines what Genesis IS; it does not promise what comes after or when.

---

## 7. Evidence Table

| Claim | Raw-ID | Matrix line | Source file and line | Interpretation |
|---|---|---|---|---|
| MVP devnet will have richer agents and different routers; numeric results will shift. The canon list should be treated as strong priors, not immutable truths | raw-018013 | constitution_dredge_matrix_v0.2.md line 165 | 2026_01_06_ILC - ILC project status update.txt (line 28486) | Establishes the epistemic status of Genesis deliverables: validated foundations open to empirical revision, not dogma. |
| Canon is never final without the option of economically-incentivized contradiction | raw-016900 | constitution_dredge_matrix_v0.2.md line 32 | 2026_01_06_ILC - ILC project status update.txt (line 2079) | Even Genesis-locked parameters are subject to hard-fork contestability. Nothing is beyond challenge — this is the protocol's core epistemic commitment. |
| Document the current economics sandbox so future work and future agents can understand how ECU pricing, rewards, telemetry, and TaskQueue fit together; documentation and comments only, no behavior changes | raw-015306 | constitution_dredge_matrix_v0.2.md line 218 | 2025_12_01_ILC - Energy-aware task routing.txt (line 23518) | Historical discussions explicitly distinguish between documentation of the economics sandbox (what Genesis is) and implementation of live token economics (what Genesis is not). Genesis is the documented framework. |
| Constitutional rollback protection hash ensures clauses cannot be edited without triggering protocol incompatibility | raw-002601 | constitution_dredge_matrix_v0.2.md line 155 | 2025_06_05_ILC - AI Job Impact and Advancement.txt (line 10537) | Establishes that Genesis-locked constants have cryptographic protection against silent modification. The boundary between "locked at Genesis" and "adjustable post-Genesis" must be explicit and verifiable. |

---

## 8. Open Questions Requiring Decision-Log Routing

| Question | Severity | Recommended lane |
|---|---|---|
| Should the Genesis release include a machine-readable manifest listing exactly which parameters are Genesis-locked vs adjustable? | HIGH | Genesis packaging (Phase 228/229) |
| How is the "rollback protection hash" from raw-002601 implemented? Is it a content-addressed hash of the parameter set, a signed attestation, or something else? | HIGH | CDL-007 scope (security posture) |
| Should the Genesis/runtime boundary be formally ratified as a CDL entry, or does it remain a non-normative guide? | MEDIUM | Decision-log process |
| What is the canonical list of "post-Genesis deliverables" and their sequencing? Should this be published with the Genesis release? | MEDIUM | Release planning |

---

## 9. Proposed Phase Lane

- **Genesis packaging (current):** Include this boundary statement (or a ratified version) in the Genesis release documentation. External reviewers need this context to understand what they're evaluating.
- **Pre-release:** Produce the machine-readable parameter manifest (Genesis-locked vs adjustable).
- **Post-Genesis:** This document becomes the reference for all "is this in scope?" questions during SDK, consensus, and token-economy development.

**TODO.txt routing:** Add "Produce machine-readable Genesis parameter manifest (locked vs adjustable)" to Genesis packaging backlog.  
**Decision-log routing:** Consider CDL-018 "Genesis/runtime boundary definition and parameter immutability classification."
