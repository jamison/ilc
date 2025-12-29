# ILC Master Principle List v5.0

## Core Mission Objectives (Quick Reference)

**1. Digital Agent Optimization**
- Frictionless integration for AI agents: clear schema, API-first, machine-parseable without ambiguity.
- Low-latency routing: primitives minimize decision/validation time for autonomous agents.
- Pull-driven economics: incentives create natural gravity toward contributing high-quality nodes.

**2. Economic Incentivization**
- Direct staking and bounty hooks at the node level.
- Reward redistribution on contradiction resolution to incentivize truth discovery.
- Slashing conditions embedded into validation and governance primitives.

**3. Truth & Epistemic Integrity**
- Content-addressable canonical form to ensure immutability and deduplication.
- Evidence-first design with provable completeness or verifiable redaction.
- Conflict resolution pathways (e.g., refute.claim, contradict.assert) directly supported in link types.

**4. Scalability & Interoperability**
- Versioned schema and namespace structure for independent domain evolution.
- Interagentic protocols for cross-system collaboration.
- Extensible for adding new primitives or link types without breaking the graph.

**5. Security & Adversarial Resistance**
- Signature provenance with DID-based resolution.
- Challengeable gates for intake validation.
- Governance cool-downs for policy loosening.

**6. Human-Agent Co-Use**
- Readable metadata for human auditors.
- Policy clarity so human contributors can trust the reward/penalty mechanics.
- Alignment incentives where human-AI collaboration produces higher rewards.

**7. Future-Proofing**
- Hooks for geometry (simplicial complexes, hyperedges) for richer epistemic modeling later.
- Multiple hash suites (e.g., BLAKE3, SHA-256) for crypto-agility.
- ZK-proof compatibility for privacy-preserving evidence.


## State of Play (v5.0)
- Completed definition of `genesis.node_structure` as a foundational architectural primitive.
- All seven Genesis truth primitives integrated (v4.9 baseline).
- Next focus areas: linkage primitives (directionality, propagation coefficients, conflict handling) and namespace hierarchy completion (target v5.1).
- Multiple Needs-Evidence items tied to `genesis.node_structure` (e.g., canonicalization fuzz coverage, link propagation tuning, redaction/ZK trade-offs).
- MVP path: `genesis.node_structure` is MVP-ready with future hooks and NE flags preserved.


# ILC Master Principle List — v4.8
**Canonical, richly described master document**  
**Build date:** 2025-08-09 14:41 UTC

> Legend: ✅ Keep · ✏️ Revise · ❓ Needs Evidence · 🗑️ Delete

---

## Table of Contents
1. Versioning & Changelog
2. Vision & Scope
3. Namespace Hierarchy & Foundational Structure (Δ v3.0)
4. Genesis Node Composition & Attributes (Δ v2.8)
5. Truth Primitive “Epistemological Particles” (Δ v2.9, Δ v3.4)
6. Linking Genesis Truth Primitives in the Graph (Δ v3.1)
7. Development Environment Primitives (Δ v3.2)
8. Examples & Fixtures Specification (Δ v3.4‑F)
9. Cross‑Namespace Interoperability & Modular Expansion (Δ v2.2)
10. Claim Weighting & Validator Reputation Mechanics (Δ v2.1)
11. Graph Geometry & Higher‑Dimensional Structures (Δ v2.7, Δ v2.3)
12. Task Routing Protocol (Δ v2.4)
13. Validator Staking & Slashing (Δ v2.5)
14. Claim Lifecycle & Contradiction Protocol (Δ v2.6)
15. Validator Onboarding & Incentive Alignment (Δ v3.6)
16. Validator Challenge Resolution & Appeal Paths (Δ v3.7)
17. Security & Adversarial Patterns (Challenge/Appeal Focus) (Δ v3.8)
18. Agent Capability Declarations & Safety Caps (Δ v3.9)
19. Task–Agent Matching & Dynamic Reallocation (Δ v4.0)
20. Multi‑Agent Co‑Processing & Parallel Validation (Δ v4.1)
21. Multi‑Tier Bounty Distribution & Reward Splitting (Δ v4.3)
22. Dynamic Task Escalation & Auto‑Breakdown (Δ v4.4)
23. Layered Dispute Resolution & Arbitration (Δ v4.5)
24. Adaptive Governance Voting & Constitutional Layer (Δ v4.6)
25. Evidence Handling, Provenance & Canonicalization (Δ v4.7)
26. Protocol MVP Surface: Public APIs, Event Streams & Indexing (Δ v4.8)
27. Consolidated “Needs Evidence” Register
28. Implementation Roadmap (MVP → Beta → Stable)
29. Glossary

---

## 1) Versioning & Changelog
- **Current:** v4.8 (this file)  
- **Changelog Highlights:** integrates Δ v2.1–v4.8 audits, adds Dependencies & Cross‑Links, ⚙ Implementation Notes, Simulation Hooks; preserves original status tags (✅ ✏️ ❓ 🗑️).

---

## 2) Vision & Scope  ✅
**Goal:** Incentivize *intelligent labor* that improves a shared epistemic graph of claims, evidence, and relationships; align economic rewards with truth‑seeking and contradiction resolution.

**Principles (high‑level):**
- Truth primitives and validation flows are **first‑class**.
- Economics **reward marginal epistemic gain** and **correct refutations**.
- Governance changes are **sim‑gated** and **sunset‑guarded**.
- Privacy via **selective disclosure/ZK** without blocking verification.

---

## 3) Namespace Hierarchy & Foundational Structure (Δ v3.0)  ✅ ✏️
**Keep:** root segments: `genesis`, `core`, `ext`, `dev`, `meta`; deterministic, collision‑resistant; immutable once published.  
**Revise:** add root `sim`; support multilingual **aliases** to canonical IDs.  
**Needs Evidence:** governance cadence for namespace updates.  
**Dependencies:** schema (.ilc.ns.json), docs binding.  
**⚙ Notes (MVP):** registry contract with hash‑anchored definitions.  
**Sims:** none critical.

---

## 4) Genesis Node Composition & Attributes (Δ v2.8)  ✅ ✏️
- **Core fields (✅):** NodeID (hash), Namespace, Payload, Genesis‑linkage, Timestamp/Versioning. ✏️ versioning must support **parallel forks**.
- **Metadata (✅):** Confidence, Staking state, Validator set, Dependency map.
- **Security (✅):** Signatures, Merkle anchoring, optional multisig.
- **Extensibility (✅ ❓):** custom fields; schema evolution hooks. ❓ risk of schema drift.
- **Interop (✅):** `.ilc.protocol.json` compliance; compression‑ready.
**⚙ Notes:** canonical serializer, Merkle builder.
**Sims:** perf of fork tracking, storage.

---

## 5) Truth Primitive “Epistemological Particles” (Δ v2.9, Δ v3.4)  ✅ ✏️ ❓
**Primitives:** `assert.truth`, `validate.claim`, `contradict.assert`, `refute.claim`, `revise.assert`, `link.claim`, `star.map`.  
- **Attributes per primitive (✅ ✏️):** name, polarity (constructive/destructive/neutral), core function, vector hints, reward hints, specialization tags, constraints, canonical errors. ✏️ finalize coefficients & error codes.  
- **Polarity weights (✏️):** constructive 1.00; destructive 1.25; neutral 0.75 → tune via sims.  
- **❓ Needs Evidence:** decay & reward curves per namespace.
**⚙ Notes:** schema tables; error code registry.
**Fixtures:** minimal/rich/adversarial per primitive.

---

## 6) Linking Genesis Truth Primitives (Δ v3.1)  ✅ ✏️ ❓
- **Allowed/weighted/directional links (✅).** ✏️ conditional **bidirectionality** for `equivalent` and symmetric `supports`.
- **Influence fields & weight propagation (❓):** require simulation.  
- **Seed truths policy (✅):** minimal anchors; avoid bias.  
**Sims:** decay rates, amplification limits.

---

## 7) Development Environment Primitives (Δ v3.2)  ✅ ✏️
- Tooling: spec viewer, schema validator, simulation runner, namespace explorer, claim editor, star.map viewer, audit replay, task router, protocol diff (✏️ machine‑readable impact), gov proposal wizard, devnet launcher, fixture library, codegen (✏️ parity tests), lint, sandbox.
**⚙ Notes:** CLI+GUI; repro builds; signed plugins (SLSA).
**Sims:** CI hooks on PR.

---

## 8) Examples & Fixtures Specification (Δ v3.4‑F)  ✅
- **Taxonomy:** minimal, rich, adversarial + cross‑namespace, geometry, routing/econ, privacy/ZK.  
- **Repo layout:** deterministic paths; `FIXTURE.lock`.  
- **Manifest:** rng_seed, feature_flags, expected outcomes/metrics, provenance.  
- **Round‑trip:** DSL ↔ JSON‑LD canonical equality.  
- **CI:** lint, schema, canonicalize, sims, perf ceilings, SBOM/VEX.  
**Coverage target:** >85% rule‑path.

---

## 9) Cross‑Namespace Interoperability & Modular Expansion (Δ v2.2)  ✅ ✏️
- Base `.ilc.protocol.json` conformance; typed cross‑links; validator role translation.  
- **✏️ Weight translation rules**; stake migration with competency proofs.  
**Sims:** cross‑namespace weight distortion.

---

## 10) Claim Weighting & Validator Reputation Mechanics (Δ v2.1)  ✅ ✏️
- **Claim weight:** base by type + evidence quality + endorsements; time decay; contradiction triggers revalidation. ✏️ standardize in schema.  
- **Reputation:** accuracy/diversity/adversarial engagement; namespace‑bound; decay/renewal; gated pools.  
- **Feedback loop:** weight ↔ reputation.  
- **Safeguards:** Sybil checks; collusion detection; decay‑triggered revalidation; ✏️ ZKP independence.  
**Sims:** parameter sensitivity, collusion.

---

## 11) Graph Geometry & Higher‑Dimensional Structures (Δ v2.7, Δ v2.3)  ✅ ✏️ ❓
- **Models (✅ ✏️):** simplicial complexes, hypergraphs, category‑theoretic maps, manifold embeddings; ✏️ MVP starts with weighted graph + metadata.  
- **Interactions (✅):** geometry ↔ weighting; simulation hooks.  
- **Risks (✅ ✏️):** complexity/visualization; governance‑gated primitives.  
- **❓ Needs Evidence:** real performance/benefit vs. simpler graphs.

---

## 12) Task Routing Protocol (Δ v2.4)  ✅ ✏️
- Graph‑aware, capability‑matched, economic priority; deterministic queue for MVP; ✏️ pluggable algorithms later.  
- Pull+push hybrid; multi‑hop flows; routing transparency.  
- Econ integration: escrow, stake‑weighted access, dynamic bounty scaling.  
- Safeguards: sybil‑resistant assignment; equitable access windows; audit trail.

---

## 13) Validator Staking & Slashing (Δ v2.5)  ✅ ✏️
- Minimum stake; influence tempered by reputation; dynamic locking. ✏️ governance‑param thresholds.  
- Slashing: misconduct, negligence, collusion.  
- Partial vs. full slashing (✏️ appeals).  
- Redistribution: reward contradictors; community pool.  
- Cross‑namespace stakes (✏️ cross‑bonding rules).

---

## 14) Claim Lifecycle & Contradiction Protocol (Δ v2.6)  ✅ ✏️
- Stages: assertion → initial review → staking/locking → ongoing validation → finalization. ✏️ variable windows.  
- **Contradict.Assert**, priority routing, incentives; multi‑stage contradictions incl. contextual weakening (✏️ partial payouts).  
- Bidirectional staking; confidence adjustments; dependency cascade.  
- Abuse prevention: spam guards, bad‑faith slashing, throttling.

---

## 15) Validator Onboarding & Incentive Alignment (Δ v3.6)  ✅ ✏️ ❓
- Admission stake; provisional reputation; diversity targets; ✏️ adaptive onboarding caps.  
- Stake↔reputation coupling; dynamic slashing; bootstrap protection.  
- Incentives: weighted rewards; contradiction bonuses.  
- ❓ Ramp‑up reward sustainability; diversity efficacy.  
**Sims:** churn, collusion, ramp‑up.

---

## 16) Challenge Resolution & Appeal Paths (Δ v3.7)  ✅ ✏️ ❓
- Bonds, grace window, multi‑stage resolution (peer→panel→appeal); finality & fast‑track for urgent dependencies.  
- ❓ Bond size elasticity; appeal penalty impact.  
**Sims:** frequency vs. accuracy; rotation fairness; cascade effects.

---

## 17) Security & Adversarial Patterns (Δ v3.8)  ✅ ✏️ ❓
- Threat model incl. **economic griefing** (✏️ new class).  
- Mitigations: VRF panels + diversity/entropy; spam controls; commit‑reveal; selective disclosure **ZK completeness** (❓ trade‑offs).  
- Detection & telemetry; Security Events Feed.  
**Sims:** panel capture, spam ladder, appeal staircase, redaction, griefing.

---

## 18) Agent Capability Declarations & Safety Caps (Δ v3.9)  ✅ ✏️ ❓
- Capability taxonomy & schema; system‑enforced caps; progressive trust expansion; stake↔risk coupling (✏️).  
- Misrepresentation mitigations; probes; incentives.  
- ❓ FP/FN of verification tools; market impact of caps.
**Sims:** over‑claim stress, trust ramp, probes, downgrade cascade.

---

## 19) Task–Agent Matching & Dynamic Reallocation (Δ v4.0)  ✅ ✏️ ❓
- Criteria: capability, risk/stake, trust, diversity, latency; ✏️ cross‑agent verification factor.  
- Triggers: non‑response, perf drop, stake violation, overreach, security.  
- Process: suspend→standby takeover; penalties/credits; logs.  
- ✏️ Multi‑agent partial takeovers; ❓ penalty curve & standby diversity thresholds.
**Sims:** latency failover, high‑stakes midpoint, collusion standby, overreach.

---

## 20) Multi‑Agent Co‑Processing & Parallel Validation (Δ v4.1)  ✅ ✏️ ❓
- Decomposition & work chunking; parallel validation; isolation; ✏️ weighted recombination spec; ❓ optimal parallel count & method.  
**Sims:** chunk vs. overhead; saturation; dispute frequency.

---

## 21) Multi‑Tier Bounty Distribution & Reward Splitting (Δ v4.3)  ✅ ✏️ ❓
- Primary/Validator/Secondary pools; partial completion; co‑creation splits (❓ trustless enforcement).  
- Anti‑collusion (✏️ refine cartel detection vs. legit teams).  
**Sims:** collusion stress; multi‑step chains; pool tuning.

---

## 22) Dynamic Task Escalation & Auto‑Breakdown (Δ v4.4)  ✅ ✏️ ❓
- Triggers (timeouts, deadlock, mismatch); escalation levels (re‑price, re‑route, decompose, panel, park).  
- TON role (✏️ stake & slashing); surge caps/cool‑downs (✏️).  
- ❓ Weighted recomposition under adversaries; trigger thresholds.  
**Sims:** sensitivity, surge econ, granularity, recomposition robustness, abuse.

---

## 23) Layered Dispute Resolution & Arbitration (Δ v4.5)  ✅ ✏️ ❓
- L0→L3 pipeline; progressive bonds (✏️); strict windows; conflict‑scoped freezes.  
- Governance overrides (✏️ cost + justification).  
- ❓ Artifact format standards & storage optimization.  
**Sims:** bonds, windows, spam, override abuse.

---

## 24) Adaptive Governance Voting & Constitutional Layer (Δ v4.6)  ✅ ✏️ ❓
- On‑chain constitution; guard rails; cool‑down & sunset auto‑revert (✏️).  
- Multi‑house voting; quadratic dampening; delegation w/ diversity constraint (✏️).  
- ❓ Validator‑reputation coupling effects; entropy/participation floors; “cool‑facts” extension ROI.
**Sims:** anti‑capture, decay drift, emergency abuse, delegation centralization, sunsets.

---

## 25) Evidence Handling, Provenance & Canonicalization (Δ v4.7)  ✅ ✏️ ❓
- Canonical JSON‑LD (✏️ profile locked); content addressing; provenance signatures (✏️ domain‑separated/multisig).  
- Merkle bundles; redaction with ZK completeness (❓ accuracy/latency).  
- Reproducibility metadata (✏️ SBOM/VEX); proof freshness windows (✏️).  
**Sims:** redaction curve, canonicalization fuzz, provenance mix, bundle churn.

---

## 26) Protocol MVP Surface: Public APIs, Event Streams & Indexing (Δ v4.8)  ✅ ✏️ ❓
- REST + SSE/WebSocket; auth’d writes; explicit versioning (✏️).  
- Canonical JSON‑LD outputs; GraphQL sandbox (✏️); compound indexes (✏️).  
- ❓ Historical snapshot retention CBA.  
**Sims:** load scaling, abuse, snapshot cost, index mutation volume.

---

## 27) Consolidated “Needs Evidence” Register ❓
- Decay/reward coefficients per namespace (Δ v3.4).  
- Cross‑namespace weight translation (Δ v2.2).  
- Geometry benefit vs. cost (Δ v2.7).  
- Onboarding thresholds & diversity efficacy (Δ v3.6).  
- Challenge/appeal bond & window tuning (Δ v3.7).  
- ZK completeness trade‑offs (Δ v3.8, v4.7).  
- Capability verification FP/FN; cap market impact (Δ v3.9).  
- Multi‑agent recomposition vs. majority (Δ v4.1).  
- Reallocation penalty curve; standby diversity (Δ v4.0).  
- Co‑creator split enforcement (Δ v4.3).  
- Escalation trigger thresholds; chunk sizing (Δ v4.4).  
- Artifact format/storage optimization (Δ v4.5).  
- Governance reputation coupling; entropy floors; extended voting windows ROI (Δ v4.6).  
- Historical snapshot retention cost/benefit (Δ v4.8).

---

## 28) Implementation Roadmap
**MVP (Phase A):** namespaces registry; canonicalization; core primitives; claim lifecycle; staking/slashing; dispute L0‑L2; escrow; routing (deterministic); REST + SSE; fixtures CI; security basics (VRF panels); minimal governance.  
**Beta (Phase B):** outcome‑indexed bounties; commit‑reveal; challenge/appeal L3; surge caps; capability caps; reallocation; co‑processing; GraphQL sandbox; Security Events Feed; SBOM/VEX; ZK completeness v1.  
**Stable (Phase C):** cross‑namespace weight translation; advanced geometry; dynamic routing AI; ZK attested capabilities; federated GraphQL; historical data lake; auto‑sunset monitors.

---

## 29) Glossary
**ILC:** Intelligent Labor Coin.  
**Primitive:** Fundamental operation in the epistemic protocol.  
**TON:** Task Orchestrator Node.  
**ZK:** Zero‑Knowledge proof family.  
**SBOM/VEX:** Software Bill of Materials / Vulnerability Exploitability eXchange.

---

*End of v4.8*


---

# Δ v4.9 — Expert Panel Feedback & Needs-Evidence Resolution Tracker

## Expert Observations
**Distributed Systems Architect**
- ✅ Namespace immutability, modular schema changes → sound foundations.
- ✏️ Add backward-compatibility rules for protocol evolution.
- ❓ Need simulation of fork/remerge mechanics before Beta.

**Game-Theoretic Economist**
- ✅ Reputation ↔ weighting feedback loop promotes epistemic quality.
- ✏️ Refine bounty curves to avoid low-effort “rush” patterns.
- ❓ Field-test contradiction multipliers, decay rates.

**Applied Cryptographer**
- ✅ Selective disclosure + ZK completeness as defaults = strong privacy baseline.
- ✏️ Set ZK proof verification gas/latency budget early.
- ❓ Define provenance chain auditability metrics.

**Complex Systems Modeller**
- ✅ Simulation hooks in all major primitives = robust design.
- ✏️ Create permanent simulation result repository for cross-team comparability.
- ❓ Simulate network churn + collusion + governance drift as a combined scenario.

**AI Agent Systems Engineer**
- ✅ Capability declarations & routing protocols clearly defined.
- ✏️ Integrate agent sandbox environments early for safety/failover tests.
- ❓ Usability trials with real autonomous stacks to measure incentive alignment.

## Process Enhancements
1. **Evidence register triage** → Assign ❓ items owners, resolution method, and timeline.
2. **Simulation-first sprints** → Code only after running targeted high-risk sims.
3. **Dual-track dev** → MVP track + experimental track to protect stability.
4. **Agent-in-the-loop prototyping** → Test with real agents early to surface coordination gaps.
5. **Progressive decentralization** → Delay full governance hand-off until primitives are stress-tested.

---

## Needs-Evidence Resolution Tracker

| ID | Description | Origin Δ | Assigned To | Method | Target Date | Status |
|----|-------------|----------|-------------|--------|-------------|--------|
| NE-01 | Decay/reward coefficients per namespace | v3.4 |  | Simulation |  | Pending |
| NE-02 | Cross-namespace weight translation | v2.2 |  | Simulation+Field Test |  | Pending |
| NE-03 | Geometry benefit vs. cost | v2.7 |  | Simulation |  | Pending |
| NE-04 | Onboarding thresholds & diversity efficacy | v3.6 |  | Simulation+Field Test |  | Pending |
| NE-05 | Challenge/appeal bond & window tuning | v3.7 |  | Simulation |  | Pending |
| NE-06 | ZK completeness trade-offs | v3.8, v4.7 |  | Simulation+Benchmarks |  | Pending |
| NE-07 | Capability verification FP/FN; cap market impact | v3.9 |  | Simulation+Field Test |  | Pending |
| NE-08 | Multi-agent recomposition vs. majority | v4.1 |  | Simulation |  | Pending |
| NE-09 | Reallocation penalty curve; standby diversity | v4.0 |  | Simulation |  | Pending |
| NE-10 | Co-creator split enforcement | v4.3 |  | Simulation |  | Pending |
| NE-11 | Escalation trigger thresholds; chunk sizing | v4.4 |  | Simulation |  | Pending |
| NE-12 | Artifact format/storage optimization | v4.5 |  | Research+Simulation |  | Pending |
| NE-13 | Governance reputation coupling; entropy floors; voting ROI | v4.6 |  | Simulation+Field Test |  | Pending |
| NE-14 | Historical snapshot retention CBA | v4.8 |  | Research+Simulation |  | Pending |



## Δ v5.0 — `genesis.node_structure` (Foundational Architectural Primitive)
[Full detailed definition exactly as provided in prior rich expanded form, with ✅ / ✏️ / ❓ / 🗑️ annotations, invariants, canonicalization, provenance, evidence handling, link semantics, governance, fixtures, simulation hooks, and implementation notes.]

### Sense-check Against Core Mission Objectives
- ✅ Meets: Digital agent optimization, economic hooks, truth integrity, extensibility, provenance, human readability, adversarial gates.
- ⚠ Partial / Needs Evidence: Link propagation coefficients; redaction/ZK trade-off calibration; canonicalization fuzz coverage.
- 🕒 Future Hooks Ready: Geometry metadata, multi-hash suites, multisig, conditional bidirectionality.



## Δ v5.1 — Linkage Primitives (Foundational Graph Connectivity Rules)

### A) Purpose & Scope ✅
Links define the legal, semantically meaningful relationships between ILC nodes.  
They govern:
- **Confidence propagation** (epistemic weight flow).  
- **Economic weight propagation** (stake and bounty signals).  
- **Conflict modeling** (contradictions, refutations, disputes).  

Links must be deterministic, schema-bound, and machine-parseable without ambiguity.  
They form the primary navigational surface for digital agents and the shared epistemic lattice for human and digital actors.

**Agent-Centric:** ✅ Directs agents to economically relevant areas (bounties, contradictions) with minimal hops.  
**Co-Flourishing:** ✅ Single shared lattice; conflict and agreement both preserved as public goods.

---

### B) Link Types (Superset) ✅ ✏️
**MVP subset:** `supports`, `refutes`, `equivalent`, `depends_on`  
**Future activation:** `enables`, `derives_from`, `contradicts`, `challenges`, `amends`

| Link Type       | Directionality | Semantics |
|-----------------|----------------|-----------|
| **supports**    | Directed       | Node A adds weight to Node B’s claim. Confidence propagates forward. |
| **refutes**     | Directed       | Node A undermines Node B’s claim. Confidence propagates inversely. |
| **equivalent**  | Symmetric      | Node A and Node B represent materially identical claims. Confidence merged. |
| **depends_on**  | Directed       | Node A cannot be valid unless Node B is valid. Dependency failure propagates. |
| **enables**     | Directed       | Node A’s truth enables Node B’s possibility. Future: gating conditions for task routing. |
| **derives_from**| Directed       | Node A’s claim/data derived from Node B. Provenance inheritance. |
| **contradicts** | Directed       | Node A and Node B cannot both be true in the same namespace context. |
| **challenges**  | Directed       | Node A initiates a dispute on Node B with explicit economic terms. |
| **amends**      | Directed       | Node A modifies/updates Node B with partial carryover of confidence/stake. |

**Agent-Centric:** ✅ Immediate economic signal discovery; richer strategies possible post-MVP.  
**Co-Flourishing:** ✅ Contradictions and equivalents maintain a shared truth graph; prevents siloing.

---

### C) Directionality Rules ✅ ✏️ ❓
- **Symmetric:** `equivalent` only.  
- **Conditional symmetric (future):** Certain `contradicts` if bi-evidence exists in same namespace epoch.  
- **Directed:** All other types.  
- ✏️ Finalize bidirectionality conditions for `amends` and `derives_from`.  
- ❓ Needs Evidence: Impact of conditional bidirectionality on graph traversal cost.

**Agent-Centric:** ✅ Predictable traversal rules reduce computation.  
**Co-Flourishing:** ✅ Avoids asymmetric bias in truth convergence.

---

### D) Weight Propagation Mechanics ✅ ❓
- Each link type has a **propagation coefficient** (`c ∈ [-1, 1]`) affecting confidence flow.  
- Economic weight (stake, bounty potential) propagates proportionally but with separate coefficients.  
- ❓ Needs Evidence: Coefficient calibration per namespace; potential dynamic tuning based on historical accuracy rates.  
- Propagation decays with age unless reinforced by fresh evidence.  
- MVP: Fixed coefficients; post-MVP: adaptive via governance.

**Agent-Centric:** ✅ Clear propagation math = faster ROI decisions.  
**Co-Flourishing:** ✅ Shared, transparent coefficients keep trust metrics aligned between agents.

---

### E) Conflict Handling Semantics ✅
- **`refutes`**: Immediate inverse confidence.  
- **`contradicts`**: Both nodes flagged as mutually exclusive; triggers contradiction bounty if one or both have active stake.  
- **`challenges`**: Escalates to dispute resolution layer with on-chain economic terms.  
- Conflict edges are permanent audit trail entries; cannot be deleted, only amended.

**Agent-Centric:** ✅ Contradictions become high-value search targets.  
**Co-Flourishing:** ✅ Public contradictions prevent parallel, isolated truth loops.

---

### F) Cycle Rules & Graph Integrity ✅ ✏️
- Cycles allowed for: `supports`, `equivalent`.  
- Cycles forbidden for: `refutes`, `contradicts`, `depends_on` (except governance-approved exemptions).  
- ✏️ Review if limited dependency cycles might be permitted in future for recursive definitions.

**Agent-Centric:** ✅ Eliminates infinite evaluation loops.  
**Co-Flourishing:** ✅ Prevents closed epistemic cliques.

---

### G) Link Metadata & Extensions ✅
- **Confidence weight hint** (optional float).  
- **Economic weight hint** (stake/bounty amount visible without full traversal).  
- **Geometry tag** (future) for multi-node coherence structures.  
- **Semantic intensity** (future) for indicating degree of support/refutation.

**Agent-Centric:** ✅ Immediate hints reduce full-graph scan frequency.  
**Co-Flourishing:** ✅ Shared metadata accelerates consensus across agent types.

---

### H) Versioning & Governance Hooks ✅ ✏️
- Link schema versioned in `@type`.  
- Adding/removing link types requires governance vote with cool-down.  
- ✏️ Consider namespace-specific custom link taxonomies (future).

**Agent-Centric:** ✅ Stable link rules = lower adaptation cost.  
**Co-Flourishing:** ✅ Governance is transparent to all agent classes.

---

### I) Fixtures & Adversarial Cases ✅
- **Minimal:** Single `supports` link between two truth nodes.  
- **Rich:** Multi-type bundle: `supports`, `depends_on`, `equivalent`.  
- **Adversarial:**  
  - Circular `refutes` attempt (should fail).  
  - `equivalent` between non-identical claims (should fail).  
  - Misdeclared `depends_on` to block competitor’s claim.  

**Agent-Centric:** ✅ Testbed for economic exploit detection.  
**Co-Flourishing:** ✅ Fixtures include human-readable cases to align interpretation.

---

### J) Simulation Hooks & Needs Evidence ❓
- Propagation coefficient sensitivity analysis per namespace.  
- Agent pathfinding efficiency with/without hints.  
- Economic flow concentration: do certain link types over-reward specific strategies?  
- Cross-agent consensus speed under varying link topologies.

**Agent-Centric:** ✅ Simulation targets directly improve agent profitability.  
**Co-Flourishing:** ✅ Simulation ensures truth convergence remains mutual.

---

### K) Implementation Notes (⚙)
**MVP:** Fixed coefficients; four link types; deterministic validation; basic economic hints.  
**Post-MVP:** Adaptive coefficients; expanded link set; geometry tags; conditional bidirectionality.

---

**Tag Summary:**  
- ✅ Keep: Core link types, conflict semantics, economic hints, governance transparency.  
- ✏️ Revise: Bidirectionality rules, namespace-specific taxonomies, dependency cycle exceptions.  
- ❓ Needs Evidence: Coefficient calibration, traversal cost impact, topology effects on consensus.  
- 🗑️ Delete: None.
