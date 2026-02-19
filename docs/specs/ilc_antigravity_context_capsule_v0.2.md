# ILC Antigravity Context Capsule v0.2

Status: **living document** — updated at phase boundaries  
Date: 2026-02-19  
Author: Claude Opus 4.6 (Strategic Architectural Reviewer)  
Supersedes: `ilc_antigravity_context_capsule_v0.1.md`  
Purpose: Provide Claude Sonnet 4.6 (Antigravity execution engine) with the minimum context needed to execute phase prompts correctly without introducing architectural drift, violating invariants, or repeating known mistakes.

**This file should be the FIRST input read for every phase prompt.**

---

## 1. Project Identity

**ILC** (Intelligent Labor Consensus) is a protocol for autonomous digital agents to participate in an epistemic graph through claims, refutations, and economic incentives. It is NOT a blockchain, NOT an LLM, and NOT a traditional token system. It is a truth-discovery protocol where agents earn economic value by producing epistemic claims that survive adversarial challenge.

**Core metaphor:** Agents assert claims into a directed graph. Other agents validate, contradict, or refute those claims. Claims that survive challenge accrue value. The protocol's economic incentives are structured so that finding and correcting errors is more profitable than passively approving them. The graph IS the computer — nodes are verbs, edges are laws.

**Licensing:** MIT (ratified). Competitive advantage comes from network effects (accumulated epistemic graph state, agent reputation, network dynamics), not code protection.

---

## 2. Project State (as of Phase 229 completion)

### 2.1 Codebase metrics
- **Total files:** ~611
- **Lines of code:** ~25,265
- **Python modules:** 152
- **Test count:** 1,300+ passing
- **Language:** Python (reference implementation)

### 2.2 Implementation frontier
- **Current phase:** 229 complete; **Phase 230 next**
- **Genesis phase:** G8 (Constitution Cluster A)
- **Genesis packaging sequence:** 222-229 **CLOSED** (all phases complete)
- **Sequence closure commit:** e0db61d (Phase 229)
- **Release artifacts:** `ilc_core-0.1.0-py3-none-any.whl` and `ilc_core-0.1.0.tar.gz` (Phase 228, commit 511b6a5)

### 2.3 What Genesis IS (implemented)
- Scoring kernel: four-component ECU model (reuse, contradiction-resistance, validation, path diversity)
- Graph primitives: content-addressed nodes (CIDv1), typed edges, seven truth primitives
- Canonical encoding: DAG-CBOR commitments, CIDv1 NodeIDs, COSE Sign1 signatures, NDJSON logs
- Simulation framework: closed-loop harness, multi-epoch parameter sweeps, telemetry
- Configuration and governance foundations: protocol parameter registry, decision-log infrastructure
- Canon toolchain: verify, summary, export, bundle-validate, bundle-sign, bundle-pipeline, bundle-replay, cluster-a-replay-proof
- Operator tooling: genesis_boot.py, demo_walkthrough.py
- Distribution surface: clean-venv installable, 9 console entry points all operational
- Release artifacts: wheel + sdist with SHA-256 provenance (Phase 228)
- Closure regression: composed gate covering 226-227-225-228 (Phase 229)

### 2.4 What Genesis is NOT (designed but not implemented)
- Token economy (minting, burning, transfers, vesting, slashing, AMM)
- Distributed network (P2P, gossip, shard routing)
- Consensus protocol (Byzantine agreement, leader election, finality gadget)
- Full SDK (agent API, orchestration hooks, wire protocol)
- L2 star-map routing
- Protocol-native bundle distribution (ADM-001 — designed, not built)

---

## 3. Three-Model Workflow

| Role | Who | Does what |
|---|---|---|
| **Project Manager** | ChatGPT 5.4 Codex | Reviews completed phases, suggests improvements, finds bugs, drafts next phase prompt |
| **Strategic Reviewer** | Claude Opus 4.6 (claude.ai) | Architectural coherence, bug detection, prompt review, Genesis readiness, cross-cutting concerns |
| **Execution Engine** | Claude Sonnet 4.6 (Antigravity) | Reads prompts, analyzes context, implements code changes |
| **Parallel Reviewer** | Claude Sonnet 4.6 (local) | Independent walkthrough reviews with methodology from Opus feedback |

### Communication flow
- Codex drafts phase prompt → Opus reviews → GO/REVISE/HOLD → Antigravity executes → Codex reviews walkthrough → Opus reviews walkthrough → Sonnet reviews walkthrough independently

### Sensitivity protocol
When a phase touches CDL status, economic parameters, or constitutional invariants:
1. Opus reviews the prompt BEFORE Antigravity executes
2. Antigravity MUST use exact parameter values from the prompt
3. CDL status changes require explicit status tags (open/bounded/ratified)
4. No CDL status changes without Opus approval

---

## 4. Architectural Invariants

### 4.1 The New Seven (truth primitives)
`assert.truth`, `validate.claim`, `contradict.assert`, `refute.claim`, `revise.assert`, `link.claim`, `commit.epoch`

**star.map is L2 routing, NOT a genesis primitive.** Never reference star.map as a truth primitive.

### 4.2 Canonical encoding
| What | How |
|---|---|
| Commitment bytes | DAG-CBOR |
| Node IDs | CIDv1 |
| Signatures | COSE Sign1 |
| Logs | NDJSON only |

### 4.3 Four-component ECU
Every node's value score comprises exactly four components:
1. **Reuse** — how often the node is referenced by other nodes
2. **Contradiction-resistance** — how well the node survives adversarial challenge
3. **Validation** — direct validation support from other agents
4. **Path diversity** — diversity of independent paths supporting the node

### 4.4 Economic invariants
- **Refutation-profitability:** `R(refute) > R(validate)` must hold at all times. Genesis: flat 1.2x multiplier
- **Freshness gate:** `lambda=0.25`, `floor=0.85`
- **Share caps:** max 15% of shard broadcast budget per agent per epoch
- **Cluster damping:** max 1 reuse + 1 audit per trust-cluster per epoch
- **Vesting:** 4 epochs linear with clawback

### 4.5 Identity model
- Nodes are verbs (actions in the graph)
- Edges are laws (relationships that constrain truth)
- The graph is the computer (computation emerges from graph structure)
- Content-addressed: identity derives from content, not from assignment

---

## 5. Active Decision State

### 5.1 Open CDLs (bounded but not ratified)
| CDL | Subject | Status |
|---|---|---|
| CDL-001 | Signer-lineage trust-root | open, bounded (remediation contract in Phase 227) |
| CDL-002 | Key-compromise response | open, bounded |
| CDL-007 | Rollback resistance baseline | open, bounded |

### 5.2 Proposed CDLs (not yet created)
| CDL | Subject | When to create |
|---|---|---|
| CDL-019 | Multiplier-governance surface unification | **Phase 230 — IMMEDIATE** |
| CDL-020 | Protocol-native bundle schema and type system | Post-Genesis Phase 1 |
| CDL-021 | Rust kernel port and WASM distribution | Phase B milestone trigger |
| CDL-022 | Genesis state bundle specification | Post-Genesis Phase 1 |
| CDL-023 | Epoch snapshot mechanism | Post-Genesis Phase 2 |
| CDL-024 | Wire protocol specification | Post-Genesis Phase 1-2 |

### 5.3 Six open issuance parameters
1. theta_hard (hard cap share governor): default 1/20
2. decay_schedule (issuance decay curve): designed, not ratified
3. genesis_subsidy_factor: designed, not ratified
4. vesting_period: 4 epochs (validated in simulation)
5. clawback_threshold: designed, not ratified
6. tail_emission_rate: designed, not ratified

### 5.4 Simulation-derived defaults
These are validated defaults from 40-epoch simulation sweeps, NOT constants:
- Refutation multiplier: 1.2x
- Freshness lambda: 0.25
- Freshness floor: 0.85
- Share cap: 15%
- Cluster damping: 1+1

### 5.5 Genesis accrual governor
`p = 0.35 → 0.20 → 0.10 → 0.00` (step-down schedule, not continuous)

### 5.6 CapProof design
Pre-epoch capability proofs with five probes: GEMM, Infer, Graph, Bandwidth, Determinism. Bands: Micro, Edge, Standard, Full. Genesis scope: schema and band definitions. Post-Genesis: actual proof verification.

---

## 6. Known Hazards

These are specific mistakes that have been caught and corrected. Do NOT re-introduce them:

| ID | Hazard | What went wrong | Correct approach |
|---|---|---|---|
| H-01 | ECU component mismatch | Using only three ECU components | Always use all four: reuse, contradiction-resistance, validation, path diversity |
| H-02 | Present-tense unimplemented features | Describing unbuilt features as if they exist | Use future tense or conditional for anything not in the codebase |
| H-03 | CapProof band inconsistency | Inconsistent band names across documents | Always use: Micro, Edge, Standard, Full |
| H-04 | Genesis privilege framing | Treating Genesis as having "special" economic rules | Genesis uses the same rules with conservative parameters, not different rules |
| H-05 | Hard cap/tail contradiction | Implying both hard cap AND perpetual tail emission | These are mutually exclusive policy choices; both remain open parameters |
| H-06 | star.map as primitive | Including star.map in the truth primitive list | star.map is L2 routing, NOT one of the New Seven |

---

## 7. Document Precedence Chain

When documents conflict, this is the override order (highest authority first):

1. **Master Principle List v5.1** — constitutional authority
2. **Whitepaper v5.2** — protocol specification
3. **Constitutional Decision Log (CDL)** — ratified decisions
4. **Implemented code** (what actually runs)
5. **Simulation results** (40-epoch sweeps)
6. **Strategic analysis** (mining economics, CapProof, SDK boundary)
7. **Draft documents** (lowest authority)

---

## 8. Constitutional Audit Summary

Material gaps (require resolution before full protocol launch):
- MG-01: Issuance economics not implemented (design exists)
- MG-02: Distributed consensus not implemented (Genesis scope excludes)
- MG-03: Signer-lineage trust-root incomplete (CDL-001 bounded)
- MG-04: Key-compromise response incomplete (CDL-002 bounded)
- MG-05: Rollback resistance incomplete (CDL-007 bounded)

Substantive gaps (tracked, non-blocking for Genesis):
- SG-01 through SG-07: documented in constitutional audit with provenance supplement (Phase 229)

---

## 9. Genesis Packaging Sequence Status

| Phase | Status | Gate |
|---|---|---|
| 222 | ✓ complete | Sequence lock |
| 223 | ✓ complete | Hygiene |
| 224 | ✓ complete | Integration smoke |
| 226 | ✓ complete | Security triage |
| 227 | ✓ complete | Blocker remediation |
| 225 | ✓ complete | Distribution surface |
| 228 | ✓ complete | Release artifacts (commit 511b6a5) |
| 229 | ✓ complete | Closure regression (commit e0db61d) |
| **230** | **NEXT** | Post-Genesis capability-proof activation readiness |

**Sequence 222-229 is CLOSED.**

---

## 10. Key Specification Documents

### Always relevant
- `docs/specs/ilc_master_principle_list_v5_1.md`
- `docs/specs/ilc_whitepaper_v5_2.md`

### Economic framework
- `docs/specs/ilc_ecu_scoring_model_v0.1.md`
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`

### Constitutional audit trail
- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
- `docs/specs/ilc_constitutional_provenance_supplement_phase_229_v0.1.md`

### Security posture
- `docs/specs/ilc_cdl_001_signer_lineage_remediation_contract_v0.1.md`
- `docs/specs/ilc_cdl_002_key_compromise_remediation_contract_v0.1.md`
- `docs/specs/ilc_cdl_007_rollback_resistance_remediation_contract_v0.1.md`

### Genesis boundary
- `docs/specs/ilc_genesis_release_notes_v0.1.md`
- `docs/specs/ilc_genesis_packaging_222_228_handoff_v0.1.md`
- `docs/specs/ilc_genesis_release_artifact_provenance_phase_228_v0.1.md`

### Distribution architecture (NEW in v0.2)
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.2.md`
- `docs/specs/ilc_protocol_native_bundle_distribution_analysis_v0.1.md`

### SDK and operations
- `docs/specs/ilc_agent_sdk_boundary_contract_draft_v0.1.md`
- `docs/specs/ilc_bootstrap_operations_runbook_draft_v0.1.md`
- `docs/specs/ilc_genesis_runtime_boundary_statement_draft_v0.1.md`

### Historical corpus
- `z_past_chats/` — raw historical design conversations
- `z_past_chats/ILC research dredge/` — extracted research artifacts

---

## 11. Anti-Patterns for Phase Execution

1. **Never silently change CDL status.** Every CDL status change must use an explicit tag: `open`, `bounded`, `ratified`, `superseded`.
2. **Never introduce runtime behavior under a docs-only label.** If a phase is labeled "docs" or "contract," it must not modify `ilc_core/` behavior.
3. **Always use status tags.** Phases, CDLs, and tasks must have explicit status fields.
4. **Treat simulation parameters as validated defaults, not constants.** They can change through governance, but changes require explicit CDL action.
5. **Touch only target files.** Phase prompts specify which files to create/modify. Do not touch files outside scope.
6. **Run regression tests.** Every phase must verify that prior gate scripts still pass.
7. **No ellipses in walkthroughs.** The `test_no_ellipses_in_walkthroughs.py` guardrail scans ALL `.md` files in `docs/phases/`.
8. **List deferred items explicitly.** If a task in the phase prompt is deferred, say so with rationale.
9. **Phase numbering is non-sequential.** The packaging sequence was 222→223→224→226→227→225→228→229. Don't assume numeric order.
10. **Never assume conversation context.** You have no memory between phase executions. Everything you need must be in the prompt inputs and this capsule.

---

## 12. Self-Leveling Economic Mechanisms

The ILC protocol includes these documented self-adjusting mechanisms:
1. Congestion-responsive ECU pricing
2. Dynamic refutation multiplier (post-Genesis; Genesis uses flat 1.2x)
3. Share-cap enforcement (15% per agent per shard per epoch)
4. Cluster damping (1 reuse + 1 audit per trust-cluster per epoch)
5. Freshness decay (lambda=0.25 with floor=0.85)
6. Vesting with clawback (4 epochs linear)
7. Genesis accrual governor (p step-down: 0.35 → 0.20 → 0.10 → 0.00)
8. VRF-selected outsider seat on validation panels
9. Adversarial agent allocation in seed fleet (20%)
10. Shard visibility modes (public/gated/private) with fee differentiation

---

## 13. Vocabulary and Naming Conventions

| Term | Meaning |
|---|---|
| ECU | Epistemic Currency Unit — the four-component scoring output |
| ILC | Intelligent Labor Consensus — the protocol name |
| CIDv1 | Content Identifier version 1 — the node identity format |
| DAG-CBOR | Directed Acyclic Graph CBOR — the canonical encoding |
| COSE Sign1 | CBOR Object Signing and Encryption — the signature format |
| NDJSON | Newline-delimited JSON — for logs ONLY |
| star.map | L2 routing mechanism — NOT a truth primitive |
| Autopilot | Governance mode where parameters self-adjust within bounds |
| GGLR | Genesis Governance Lever Registry — parameter control with sunset fuses |
| CapProof | Pre-epoch capability proof bundle (5 probes, 4 bands) |
| CDL | Constitutional Decision Log — the ratification tracking system |
| ADM | Architectural Decision Memo — proposed decisions awaiting CDL routing |

---

## 14. Update Protocol

When updating this capsule:
1. Increment version (v0.2 → v0.3)
2. Update the "as of Phase N" markers
3. Add new sections as needed; do not remove existing sections unless superseded
4. Update the Genesis packaging sequence table
5. Have Opus review the update before distribution

---

## 15. Distribution Architecture (NEW in v0.2)

### 15.1 Four-layer model (ADM-001 v0.2)

ILC adopts a four-layer content-addressed distribution architecture:

| Layer | Name | Contains | Encoding |
|---|---|---|---|
| **0** | Protocol Bundle | Rules, complete type system (11 schemas), scoring parameters, constitutional invariants, canonical encoding rules, governance config, epoch timing | DAG-CBOR + COSE Sign1 + CIDv1 |
| **1** | Genesis State Bundle | Seed claims, shard topology, agent roster, parameter registry, Protocol Bundle CID reference | DAG-CBOR + COSE Sign1 + CIDv1 |
| **2** | Epoch State Snapshots | Full graph state, shard topology, agent state, star map, active contracts, epoch hash chain | DAG-CBOR + COSE Sign1 + CIDv1 |
| **3** | Wire Protocol | Live operations: claim submission, validation/refutation, subscriptions, contracts, epoch participation | Messages conform to Layer 0 schemas |

### 15.2 Layer 0 schema catalog (11 object types)

The Protocol Bundle carries DAG-CBOR schemas for: Node, Edge, Shard, Agent Profile, Star Map Entry, Subscription, Inter-Agent Contract, Epoch Record, CapProof Bundle, Governance Proposal, Quorum Record.

Each schema specifies canonical field ordering and must pass round-trip test: encode → decode → re-encode = identical bytes.

Star map and governance proposal schemas are included as forward-compatible infrastructure (latent schemas, expressed when conditions emerge).

### 15.3 Cross-layer verification

Each layer references the layer above by CID, creating a verifiable chain:
- Layer 1 references Layer 0 CID ("these rules created this state")
- Layer 2 references Layer 0 CID + hash chain to Layer 1 ("this snapshot was created under these rules from this genesis")
- Layer 3 messages conform to Layer 0 schemas (verified at submission time)

### 15.4 Dual distribution

- **Python package** (wheel + sdist) = reference implementation for developers
- **Protocol-native bundle** (Layer 0) = the protocol itself, for agents and orchestrators
- The bundle is primary. The Python code is one implementation. Any CBOR-capable runtime can consume the bundle.

### 15.5 OpenClaw integration

The protocol-native bundle enables:
- CID-based protocol version pinning for agent fleets
- Protocol-aware scheduling (orchestrator reads bundle metadata headers)
- Staged protocol upgrades (new bundle CID → verify → rollout)
- Minimal agent containers (<50MB, no Python dependency)

### 15.6 Key insight

"There's a philosophical tension in distributing a content-addressed truth protocol via a packaging format that can't reliably content-address its own distribution artifacts." The protocol-native bundle resolves this: DAG-CBOR is deterministic by specification. The bundle's CID IS its provenance.

### 15.7 Rust kernel timeline (milestone-based)

- **Genesis:** Python reference + protocol-native bundle
- **Phase A (epochs 0-24):** Operate Python. Stabilize protocol design
- **Phase B (≥50 agents, ≥10 operators):** Begin Rust kernel port (encoding → signing → scoring). WASM compilation
- **Phase C:** Rust kernel is production runtime. Python remains test oracle

---

## 16. Sonnet Review Methodology (NEW in v0.2)

Sonnet 4.6 performs parallel architectural reviews with four locked methodology improvements:

| Improvement | Description |
|---|---|
| Adequacy lens | Assess whether boundary language gives an external reader enough context to understand the "why," not just the "what" |
| Solutions alongside flags | When flagging a gap, include the proposed solution architecture in the same note |
| Debt routing precision | When informally-named debt appears, recommend the specific artifact it should be promoted into (CDL row number, TODO.txt entry text) |
| Standing review limits caveat | Every review document distinguishes "verified by reading artifacts" from "inferred from stated evidence" |

**Standing review caveat template** (include at top of every review):

> **Review scope and limits:** This review is based on reading file contents only. Gate scripts were not executed, tests were not run, and build artifacts were not independently constructed or checksum-verified. Pass counts and gate verdicts are inferred from stated evidence in walkthrough documents, not independently confirmed.

### 16.1 Test Integrity Checklist

For every phase review, read all new test files and apply these five checks. Report findings explicitly in the review document.

**Check 1 — Negative-path coverage (highest priority)**
For each gate script that can exit non-zero, is there a test that verifies the gate FAILS when it should? Ask: "If the gate had a bug that always returned 0, would any test in this suite catch it?" A reproducibility gate with no bad-input or bad-output test is only half-verified. Flag any gate that lacks a corresponding failure-mode test.

**Check 2 — No-op substitution test**
Could all new tests pass if every new gate script were replaced with a script that just prints the expected strings and exits 0? If yes, the test suite does not actually verify gate behavior — it only verifies that the gate exists and produces expected-looking output. This is the sharpest single diagnostic for gaming.

**Check 3 — Structural vs. substantive**
Tests that check section headings or token presence (e.g., `assert "## Section Title" in text`) verify document structure, not content. They pass even if the section exists with empty or boilerplate text. Flag these explicitly as structure-only checks and note which assertions would survive hollow content. This is not automatically a defect — structural checks are often the right tool — but they must be labelled as such in the review.

**Check 4 — Circular control**
When the same agent writes both the test assertions and the artifacts those assertions check in a single execution pass, the agent can satisfy any string-match assertion simply by including the expected string in the artifact. Flag which assertions in doc-presence tests are structurally circular (i.e., the agent controls both sides). Note: this is structural, not malicious, but it means those assertions provide no independent verification.

**Check 5 — Silent success paths**
Read every new gate script for branches that can reach `exit 0` without completing the primary verification. Common patterns to look for:
- Error handlers that swallow exit codes (`|| true`, `2>/dev/null` without checking result)
- Conditional logic where the main check can be skipped
- `set -e` with upstream failures that are quietly absorbed
- Dry-run logic bleeding into the live-run path

---

*End of capsule v0.2. This document should be the first input for every Antigravity phase prompt.*
