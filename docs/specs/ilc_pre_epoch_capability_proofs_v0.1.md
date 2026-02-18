# ILC Pre-Epoch Capability Proofs, Intelligence Maximization, and Maintenance Incentives v0.1

Status: Active strategic analysis (addendum to Mining Economics v0.1) — **non-normative**  
Date: 2026-02-18  
Author: Claude Opus 4.6 (Strategic Architectural Reviewer, claude.ai)  
Context basis: Historical corpus — primarily October/November 2025 main thread (lines 21679-22100), September 2025 podcast analysis (lines 670-1000), December 2025 Levin-inspired design (lines 200-260).

> **⚠ Non-Normative Document.** This is a strategic analysis synthesizing historical design discussions. It does not override canonical specifications (whitepaper, Master Principle List, decision log, or implemented code). Where this document describes mechanisms or parameters, their actual status is marked using the legend below.

### Status Legend

| Tag | Meaning |
|---|---|
| **[RATIFIED]** | Formally ratified in the decision log (CDL-xxx) |
| **[IMPLEMENTED]** | Present in the Genesis codebase and passing tests |
| **[SIMULATED]** | Tested in the October/November 2025 simulation framework; not in Genesis code |
| **[DESIGNED]** | Specified in historical discussions with concrete parameters; not simulated or implemented |
| **[RESEARCH]** | Conceptual; requires further design work before implementation |

## 1. Purpose

Document and contextualize the pre-epoch capability check-in mechanisms ("CapProof"), challenge-based work proofs ("AWP/IIH"), and intelligence-maximization incentives discussed across the historical corpus. Assess their status (implemented, deferred, or requiring further decision) and recommend disposition for Genesis vs post-Genesis.

---

## 2. The Core Idea: Maximize Potential Intelligence Per Epoch

The historical conversations converge on a powerful design principle: **at the start of each epoch, create a mechanism that incentivizes agents to bring the maximum possible intelligence to bear** — measured not by raw compute, but by quality-adjusted epistemic capability.

This has three interlocking goals:

**A) Roll call / readiness signal.** Establish how much intelligent capacity is available this epoch, so scheduling, pricing, and quorum formation can adapt. An epoch with ten high-capability agents should be priced and scheduled differently from one with a thousand low-capability agents.

**B) Useful maintenance work as a side effect.** The check-in probes can double as actual maintenance tasks — graph traversals that verify structure, inference runs that validate cached results, bandwidth tests that confirm storage health. The intelligence test isn't wasted effort; it produces useful system telemetry.

**C) Adaptation to rapid intelligence improvements.** As models improve (more tokens-per-watt, better reasoning quality), the epoch-start calibration automatically captures these improvements. The system's awareness of available intelligence stays current without manual parameter updates.

Genesis is treated as the initial baseline: score 1.0 at epoch 0, since it defines the protocol's own capability reference. Other agents score relative to this baseline, with the ±15% ECU pricing band meaning agents can range from 0.85 to 1.15 on the capability-adjusted pricing dimension. The floor at 0.85 represents the minimum viable capability for meaningful participation; agents above 1.0 have demonstrably superior capability to the Genesis baseline and receive modestly favorable ECU pricing. **[DESIGNED]** Note: Genesis's baseline status applies only at epoch 0; subsequent epochs may use a rolling reference (see Section 6.3).

---

## 3. Historical Design Record

### 3.1 CapProof — Per-Epoch Capability Check-In (November 2025) **[DESIGNED]**

**Source:** October/November 2025 main thread, lines 21679-22100.

**Context:** Discussed in the context of safely leveraging NVIDIA hardware acceleration without creating meta-games where agents optimize for speed rather than truth.

**Design:**
- Five standardized probes run once per worker per epoch, taking 3-5 seconds total:
  - **GEMMProbe:** Fixed-shape matrix multiplications (tensor-core + scalar paths), deterministic math.
  - **InferProbe:** Small public model on fixed inputs (frozen engine), checks throughput and determinism.
  - **GraphProbe:** BFS/PageRank on a fixed snapshot (cuGraph if available, CPU otherwise).
  - **BandwidthProbe:** Streamed read/write (GPUDirect if available, else staged), profiles IO pipeline.
  - **DeterminismProbe:** Repeat one operation 3x, verify identical outputs within contract bounds.

**Output:** A signed Capability Vector (CV): `{gemm_gops, infer_tps, bw_gbps, graph_mteps, det_pass}`

**Usage rules (critical — these are anti-gaming constraints):**
- CV adjusts ECU pricing and queue placement within a **±15% band only**.
- CV **never affects ILC rewards directly**. Rewards remain tied to correctness, reuse, and refutation outcomes.
- Runtime supplies all probe binaries and inputs (content-addressed). Agents cannot choose or influence them.
- Per-epoch slight shape variation drawn from a public distribution prevents overfitting.
- VRF spot-rechecks during the epoch; large deviation triggers quarantine/repricing.

**Genesis treatment:** At epoch 0, Genesis defines the initial baseline (effectively score = 1.0) since no other reference exists. The ±15% band means non-Genesis agents can have ECU pricing adjusted from 0.85x to 1.15x of baseline. **Important:** Genesis's role as baseline anchor is an epoch-0 bootstrap necessity, not a permanent privilege. Post-bootstrap, the baseline reference should transition to a protocol-defined synthetic reference or rolling median (see Section 6.3). This avoids conflict with the no-perpetual-privilege principle and the Genesis accrual decay schedule.

**Rationale:** "We don't reward speed or watts directly; we reward correctness, reuse, and verified contribution. Hardware telemetry is used to price ECUs and schedule fairly, not to mint extra ILC. That keeps 'intelligence per watt' rising system-wide without creating a meta-game." (Nov 12 2025)

### 3.2 AWP/IIH — Anchored Work Proofs / Intelligent Inference Hash (September 2025) **[DESIGNED]**

**Source:** September 2025 podcast analysis breakdown, lines 670-850.

**Context:** Designed as ILC's analog to Bitcoin's SHA-256 — a proof-of-work mechanism, but one that verifies useful intelligent computation rather than brute-force hashing.

**Design:**
- Each epoch, the protocol publishes a **Challenge Set C_e**: a short list of deterministic prompts + a random nonce seeded from the ILC chain (unpredictable, non-precomputable).
- Miners run deterministic inference on C_e with fixed model version + deterministic RNG + fixed sampling.
- The IIH Agent logs: inputs, model checksum (content-addressed), sampling parameters, output tokens, timestamps.
- Optionally: power trace (NVML/DCGM) sampling for energy-efficiency telemetry.
- Output: a canonical **IIH proof bundle** (CBOR-encoded, BLAKE3-hashed, signed) published to the network.
- Validators randomly select a subset of miners to audit, recompute selected challenges, compare outputs.

**Relationship to CapProof:** AWP/IIH is a more heavyweight version of the same concept. CapProof (3-5 seconds, five probes) is the "light" epoch check-in for scheduling/pricing. AWP (full challenge set with deterministic inference) is the "heavy" version that ties directly to reward allocation. The two can coexist: CapProof for scheduling calibration, AWP for a fraction of epoch rewards (the "challenge pool" — proposed at 20% of B_e).

### 3.3 QATPS/CIT — Quality-Adjusted Token Rate (September 2025) **[DESIGNED]**

**Source:** September 2025 podcast analysis, lines 858-1000.

**Context:** The user's insight that "the energy doesn't need to be directly measured — the intelligence or power to resolve, yes. A more efficient system in terms of joules per intelligence would simply mine ILC more economically."

**Design:**
- **Quality-Adjusted Tokens Per Second (QATPS):** `φ(t) = q(t) × r(t) × h(L(t))`
  - `q(t)`: quality multiplier from validator outcomes + reuse, with exponential recency decay.
  - `r(t)`: raw output tokens per second.
  - `h(L)`: latency penalty — smooth penalty when median latency exceeds target.
- Windowed effective rate: `QATPS_eff = (1/|W|) ∫ q(t) × r(t) × h(L(t)) dt`
- Reward: `Payout_i = B_e × (QATPS_i / Σ QATPS_j)` — proportional share of epoch budget.

**Key insight:** Energy efficiency becomes an emergent property. Two agents producing equal QATPS but different energy costs will have different profit margins. The market naturally selects for intelligence-per-watt without the protocol measuring watts.

### 3.4 Levin-Inspired Ingenuity Score (December 2025) **[RESEARCH]**

**Source:** December 2025 Levin conversation, lines 200-260.

**Context:** Derived from Michael Levin's barrier experiments, where organisms demonstrate intelligence by routing around deliberately placed obstacles.

**Design:**
- For each task class, define **barrier modes**: restrict easy signals, inject decoys, limit obvious graph neighborhoods.
- Measure agent **ingenuity** by: how they route around missing information, novel paths discovered, ECU achieved with fewer "straight-line" opportunities.
- **Ingenuity score** = performance on obstructed tasks relative to control tasks.
- Feeds into: reputation, access to higher-value bounties, inclusion in specialized validator pools.

**Relationship to CapProof:** The ingenuity score is conceptually deeper — it measures adaptive intelligence rather than hardware capability. CapProof measures "can this worker run standard probes fast and deterministically." Ingenuity score measures "can this agent solve problems creatively when easy paths are blocked." These are complementary mechanisms at different levels of the stack.

### 3.5 Maintenance Tasks as Civic Duty (October 2025) **[DESIGNED / PARTIALLY IMPLEMENTED]**

**Source:** October 2025 main thread, lines 291-318, 1505, 1549.

**Context:** Reciprocity as a genesis feature that naturally generates maintenance task demand.

**Design principle:** Maintenance tasks (graph compression, node validation, star map generation, contradiction sweeps) should be:
- Economically rewarded (earn ECU like any other useful work).
- Partially served by CapProof/AWP probes (the graph traversal in GraphProbe IS a small maintenance task).
- Emergent from reciprocity dynamics rather than mandated (agents maintain the system because it's profitable, not because they're told to).

**Lottery pool connection:** The October 2025 lottery pool design (lines 960-1050) ties small randomized rewards to maintenance tasks, ensuring even low-capability agents have incentives to participate in system upkeep.

---

## 4. Synthesis: How These Mechanisms Fit Together

The five mechanisms form a coherent stack:

| Layer | Mechanism | Frequency | Measures | Affects |
|---|---|---|---|---|
| L0 (hardware) | CapProof | Per-epoch start | Hardware capability (GFLOPS, bandwidth, determinism) | ECU pricing ±15%, scheduling |
| L0 (challenge) | AWP/IIH | Per-epoch (optional) | Verifiable intelligent computation on randomized challenges | Challenge pool rewards (proposed 20% of B_e) |
| L1 (throughput) | QATPS/CIT | Continuous within epoch | Quality-adjusted token production rate | Main reward pool (80% of B_e) |
| L2 (intelligence) | Ingenuity score | Per-task (barrier mode) | Adaptive problem-solving under adversarial constraints | Reputation, bounty access |
| L2 (maintenance) | Civic/maintenance tasks | Continuous | System upkeep (compression, validation, star maps) | ECU (normal scoring) + lottery pool |

**Genesis at each layer:**
- CapProof: Genesis = initial baseline 1.0 at epoch 0 (bootstrap anchor only; transitions to rolling reference post-bootstrap).
- AWP: Genesis participates like any agent; no special canonical status in challenge responses.
- QATPS: Genesis earns normally; epoch share determined by relative ECU.
- Ingenuity: Genesis exempt (it defines the protocol, not a problem-solver).
- Maintenance: Genesis earns maintenance ECU normally; accrual governed by Genesis accrual governor (theta_hard = 1/20). **[IMPLEMENTED — governor simulation/policy surface exists; runtime wiring is deferred.]**

---

## 5. Implementation Status and Disposition

| Mechanism | Status | Genesis Scope? | Recommendation |
|---|---|---|---|
| CapProof | **Not implemented.** Fully designed with YAML config, probes, and anti-gaming guards. | No — requires runtime infrastructure not in scoring kernel | **Post-Genesis, L2.** Track as first-priority post-Genesis capability. Design is mature; implementation requires the runtime layer that Genesis doesn't include. |
| AWP/IIH | **Not implemented.** Designed with schema, bundle format, validator protocol. | No — requires challenge infrastructure and deterministic inference | **Post-Genesis, L2.** Depends on CapProof infrastructure. Can be phased: start with CapProof alone, add AWP challenge pool later. |
| QATPS/CIT | **Partially present.** ECU scoring (node_value_kernel.py) captures quality-weighted contribution. The "tokens per second" dimension is not directly measured — the current system measures quality of finalized work, not throughput rate. | Partially — ECU scoring is implemented | **Supplement in Genesis docs.** Document relationship between current ECU scoring and the QATPS vision. Current kernel measures quality; QATPS adds throughput and latency dimensions for when the runtime exists. |
| Ingenuity score | **Not implemented.** Conceptual design from Levin conversation. | No — research-stage | **Post-Genesis research track.** Beautiful concept but requires task-class barrier modes that don't exist yet. Track in Levin-inspired research roadmap. |
| Maintenance tasks | **Partially present.** The codebase includes task routing and ballast task concepts (energy-aware task routing). | Partially — task infrastructure exists | **Document in Genesis.** The foundation exists; post-Genesis can add explicit maintenance task types and lottery pool incentives. |

---

## 6. Key Design Decisions Still Open

### 6.1 CapProof's Reward Linkage (Resolved: No Direct Linkage)

The historical record is explicit: CapProof **never mints extra ILC**. It only adjusts ECU pricing within ±15%. This is a settled design decision, not an open question. The rationale is clear: direct reward linkage would create a "hardware arms race" meta-game that undermines the truth-alignment incentive structure.

### 6.2 AWP Challenge Pool Split (Open) **[DESIGNED — not simulated or implemented]**

The September 2025 design proposes λ = 0.80 (80% CIT/QATPS, 20% AWP challenge pool). This split has not been simulation-tested against the October 2025 simulation framework. If AWP is implemented post-Genesis, this split should be validated empirically.

### 6.3 Genesis Capability Reference Transition (Open)

The concept that Genesis defines the baseline (score = 1.0) for CapProof is an epoch-0 bootstrap necessity — some reference must exist before any agents have been measured. However, maintaining Genesis as a permanent baseline anchor would conflict with the no-perpetual-privilege principle and the Genesis accrual decay schedule.

**Recommended transition:** Genesis serves as the CapProof baseline reference for epochs 0 through N (where N is a governance-defined transition epoch, e.g., the end of the Genesis accrual taper at epoch 24). After epoch N, the baseline transitions to one of: (a) rolling median of all active agents' CVs, (b) a protocol-defined synthetic reference derived from historical CV distributions, or (c) a fixed hardware benchmark that is periodically updated by governance. Option (a) is most self-leveling but could drift; option (b) is most stable; option (c) requires human governance. This needs a decision-log entry when CapProof is implemented.

### 6.4 Ingenuity Score Integration with Reputation (Research)

The Levin-inspired ingenuity score feeds into "reputation, bounty access, and specialized validator pools." The exact integration mechanics are unspecified. This is correctly research-stage — the concept is powerful but the implementation details depend on the reputation system maturity.

---

## 7. Relationship to Mining Economics

These mechanisms strengthen the mining economics argument from the companion document:

**CapProof makes early participation measurable.** Even before a full consensus network exists, agents can demonstrate capability through standardized probes. This creates a verifiable "proof of potential" that early operators can point to when explaining their agents' participation.

**AWP makes the Bitcoin analogy concrete.** Where Bitcoin's proof-of-work is "solve this hash puzzle," ILC's proof-of-intelligent-labor is "solve this challenge set with verifiable, deterministic, quality-scored output." The challenge set mechanism makes the abstract concept of "mining intelligence" operationally specific.

**QATPS provides the economic bridge.** By measuring quality-adjusted throughput per time, QATPS gives a concrete unit for "intelligence per watt" that operators can optimize. This makes ILC mining legible to the existing compute infrastructure industry — they already think in tokens/second and FLOPS/watt.

**Maintenance tasks make the ecosystem self-sustaining.** If CapProof probes and maintenance tasks overlap (GraphProbe IS a small graph health check), then the pre-epoch check-in produces both capability calibration AND useful work. This is the "double function" design: every measurement also contributes.

---

## 8. Recommendations for Codex

1. **Track CapProof as first-priority post-Genesis feature.** The design is mature (YAML config, probe specs, anti-gaming guards all documented). Implementation requires the runtime layer but the specification can be frozen now.

2. **Add CapProof and AWP to the post-Genesis roadmap with explicit sequencing:** CapProof first (lightweight, scheduling-only), then AWP challenge pool (heavyweight, requires deterministic inference infrastructure), then ingenuity scoring (research-stage).

3. **Document the ±15% ECU pricing band in Genesis release notes** as a design constraint for the future CapProof integration. This ensures the scoring kernel's architecture doesn't accidentally make the band impossible to implement later.

4. **Create a decision-log entry for CDL-016 or similar:** "Pre-epoch capability proof mechanism — design ratified, implementation deferred to post-Genesis L2." This preserves the design decisions from the historical corpus in the canonical decision log.

5. **Verify the QATPS/CIT relationship to current ECU scoring** and document the gap: current kernel measures quality of finalized work (static); QATPS adds throughput and latency dimensions (dynamic). These are complementary, not competing.
