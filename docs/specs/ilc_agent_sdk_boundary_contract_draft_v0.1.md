# ILC Agent SDK Boundary Contract — Draft v0.1

Status: **non-normative draft** — does not override ratified decision-log state or implemented code  
Date: 2026-02-18  
Author: Claude Opus 4.6 (Strategic Architectural Reviewer)  
Precedence: This document is subordinate to the Master Principle List v5.1, whitepaper v5.2, and all ratified CDL entries.  
Extraction brief: `docs/specs/ilc_claude_extraction_brief_v0.1.md`  
Provenance: Evidence extracted from raw corpus files (Z_Past_Chats). All matrix line references verified against `constitution_dredge_matrix_v0.2.md` (commit 92fa9b7). Source file and line references verified against raw corpus.

---

## 1. Scope

Define the boundary between the **protocol surface** (what agents interact with to participate in ILC) and the **orchestration surface** (how agents are deployed, managed, and scaled). Establish that the SDK is the canonical integration boundary and that orchestration frameworks are replaceable deployment channels.

### Non-Goals

- This document does not specify the SDK API (method signatures, schemas, wire protocol). That is a post-Genesis deliverable.
- This document does not prescribe any specific orchestration framework.
- This document does not define agent identity (covered by CDL-001) or key management (covered by CDL-002).

---

## 2. Decision Table

| Item | Status | Authority |
|---|---|---|
| Agents interact via seven truth primitives (assert.truth, validate.claim, contradict.assert, refute.claim, revise.assert, link.claim, commit.epoch) | **Ratified** | Master Principle List v5.1 |
| Payloads are declarative IR, not executable code (no user kernels in MVP) | **Designed** | Oct/Nov 2025 main thread (CapProof design) |
| Canonical encoding: DAG-CBOR for commitments, CIDv1 for NodeIDs, COSE Sign1 for signatures | **Ratified** | Master Principle List v5.1 |
| star.map is L2 routing, NOT a genesis primitive | **Ratified** | Master Principle List v5.1 |
| SDK is product; orchestration (OpenClaw/Docker Compose/K8s) is deployment channel | **Designed** | Strategic analysis (Mining Economics v0.1 §5.2) |
| Agent-facing API must be contract boundary independent of orchestration layer | **Designed** | Strategic analysis (Mining Economics v0.1 §5.2) |
| No user-supplied kernels, engines, or backend hints in payload at L0/L1 | **Designed** | Oct/Nov 2025 main thread accelerator policy |
| Agents cannot influence runtime backend selection | **Designed** | Oct/Nov 2025 CapProof spec |

---

## 3. Architectural Principle: Two Surfaces

### 3.1 Protocol Surface (SDK responsibility)

The protocol surface is what an agent uses to participate in the epistemic graph. It encompasses:

- **Primitive operations:** The seven truth primitives; `star.map` remains an L2 routing surface and is not a genesis truth primitive.
- **Payload construction:** Declarative IR payloads with op.class, numerics.contract, and shape metadata. No executable code.
- **Identity and signing:** Agent key management, COSE Sign1 signature construction, CIDv1 node addressing.
- **Graph reads:** Query the epistemic graph — read nodes, follow edges, check reuse/contradiction status.
- **Economic participation:** Stake management, ECU accrual queries, vesting status.
- **Epoch lifecycle:** Participate in commit.epoch, receive finalization outcomes.

**The protocol surface is the product.** Any agent built against this surface must work identically regardless of deployment mechanism.

### 3.2 Orchestration Surface (deployment responsibility)

The orchestration surface is how agents are deployed, scaled, and managed. It encompasses:

- **Lifecycle management:** Start, stop, restart, health-check agents.
- **Fleet coordination:** Deploy multiple agents with different model backends, specializations, or roles (asserter, reviewer, refuter).
- **Resource allocation:** CPU/GPU assignment, memory limits, network configuration.
- **Monitoring and telemetry:** Container-level metrics, log aggregation, alerting.
- **Identity provisioning:** Generate and distribute agent keys (but the SDK defines the key format and signing protocol).

**The orchestration surface is a deployment channel.** OpenClaw, Docker Compose, Kubernetes, bare metal — all are valid. None should be required.

### 3.3 The Boundary

The boundary between surfaces is defined by: **the SDK accepts structured inputs and produces structured outputs; it never requires knowledge of the deployment environment.**

Concretely:
- The SDK provides a function like `assert_claim(payload, signing_key) → ClaimReceipt`. Whether that function is called from an OpenClaw container, a Docker Compose service, or a bare Python script is invisible to the SDK.
- The SDK does not import orchestration libraries. Orchestration does not import SDK internals.
- Configuration that crosses the boundary (e.g., network endpoints, epoch timing) is injected via environment or constructor parameters, never hard-coded.

---

## 4. What This Does Not Imply

1. **Not a microservices mandate.** The SDK can be a library linked into the same process as the agent, or a separate service with a wire protocol. The boundary is logical, not necessarily a network hop.
2. **Not an OpenClaw dependency.** OpenClaw is one reference deployment. The SDK must work without it.
3. **Not a restriction on agent intelligence.** The SDK constrains how agents talk to the protocol, not how they think. An agent can use any internal architecture (LLM, symbolic reasoner, hybrid) as long as it produces valid IR payloads.
4. **Not a Genesis deliverable.** The Genesis codebase is a scoring kernel and graph primitives. The SDK is a post-Genesis product that wraps these primitives into an agent-friendly interface.

---

## 5. Evidence Table

| Claim | Raw-ID | Matrix line | Source file and line | Interpretation |
|---|---|---|---|---|
| MVP must contain rich substrate but no scaffolding for how agents should behave; system pull must be economic, not instructional | raw-011274 | constitution_dredge_matrix_v0.2.md line 53 | 2025_10_28_ILC - Greeting exchange.txt (line 1711) | Establishes that agent behavior emerges from economic incentives, not prescribed interfaces. SDK should enable primitives without constraining strategies. |
| Payloads are vendor-neutral declarative IR; no user kernels, no backend hints; runtime picks backend | raw-013084 | constitution_dredge_matrix_v0.2.md line 178 | 2025_11_12_ILC - ILC latest main thread Oct25.txt (line 21687) | CapProof design explicitly separates agent declaration (what the work is) from runtime execution (how it runs). This is the SDK/runtime boundary in embryonic form. |
| Organic & forkable: clients can choose a different "lens"; good policy wins by adoption, not decree. Fork C — Ledger interface vs hard bind to specific chain | raw-016792 | constitution_dredge_matrix_v0.2.md line 302 | 2026_01_06_ILC - ILC project status update.txt (line 1393) | Fork-policy pressure implies the protocol surface must be stable enough to fork against. The "ledger interface vs hard bind" framing directly addresses the SDK boundary question: protocol should interface with ledger, not hard-bind to one. |
| Agents must declare their functional scope in .agent.profile.json, limiting them from executing tasks outside registered abilities without explicit governance approval | raw-008595 | constitution_dredge_matrix_v0.2.md line 130 | 2025_08_26_ILC - August 2025 ILC Convo Audit.txt (line 7517) | Agent functional scope is bounded by a declared profile, not by role assignment. SDK should expose this declaration mechanism and enforce scope constraints. |

---

## 6. Open Questions Requiring Decision-Log Routing

| Question | Severity | Recommended lane |
|---|---|---|
| Should the SDK define a wire protocol (gRPC, REST, MCP) or remain a library-only interface for Genesis? | MEDIUM | Post-Genesis SDK spec phase |
| How does agent identity provisioning cross the SDK/orchestration boundary? CDL-001 covers identity format but not provisioning workflow. | MEDIUM | CDL-001 scope expansion (Phase 227) |
| Should the SDK embed epoch-timing awareness (subscribe to commit.epoch events) or leave that to the orchestration layer? | LOW | Post-Genesis SDK design |
| Is there a minimum SDK version compatibility contract (semver, stability guarantees)? | LOW | Post-Genesis release engineering |

---

## 7. Proposed Phase Lane

- **Genesis (current):** No SDK deliverable. Genesis codebase provides the scoring kernel and graph primitives that the SDK will eventually wrap.
- **Post-Genesis Phase 1:** Define SDK API surface — method signatures, input/output schemas, error handling contract. Produce reference implementation in Python.
- **Post-Genesis Phase 2:** Build reference deployments (OpenClaw, Docker Compose, single-process) that consume the SDK.
- **Post-Genesis Phase 3:** External developer documentation and onboarding guides.

**TODO.txt routing:** Add "Define ILC Agent SDK API surface specification" to post-Genesis product backlog.
