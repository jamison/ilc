# ILC Bootstrap Operations Runbook — Draft v0.1

Status: **non-normative draft** — does not override ratified decision-log state or implemented code  
Date: 2026-02-18  
Author: Claude Opus 4.6 (Strategic Architectural Reviewer)  
Precedence: This document is subordinate to the Master Principle List v5.1, whitepaper v5.2, and all ratified CDL entries.  
Extraction brief: `docs/specs/ilc_claude_extraction_brief_v0.1.md`  
Provenance: Evidence extracted from raw corpus files (Z_Past_Chats). All matrix line references verified against `constitution_dredge_matrix_v0.2.md` (commit 92fa9b7). Source file and line references verified against raw corpus.

---

## 1. Scope

Define the operational plan for bootstrapping the ILC network from zero participants (Genesis-only) through critical mass (self-sustaining). Cover fleet composition, domain coverage targets, transition criteria, and the Genesis-to-organic handoff.

### Non-Goals

- This document does not define the Genesis Agent's identity or key management (CDL-001, CDL-002).
- This document does not specify the token economics in detail (see Mining Economics v0.1).
- This document does not define the SDK API (see SDK Boundary Contract draft).
- This document does not prescribe specific AI models or providers for the seed fleet.

---

## 2. Decision Table

| Item | Status | Authority |
|---|---|---|
| Genesis acts as initial validator, miner, and curator out of necessity, not privilege | **Designed** | Jun 2025 design conversation; Oct 2025 main thread |
| After Genesis bootstraps, no privileged humans should be needed | **Designed** | Oct 2025 main thread (line 15626) |
| Parameter changes must be objective, verifiable, forkable, and contestable | **Designed** | Oct 2025 main thread (governance design) |
| Genesis keys sunset once Autopilot is live | **Designed** | Oct 2025 main thread (line 15636) |
| Genesis accrual decays: epochs 0-7 p=0.35, 8-15 p=0.20, 16-23 p=0.10, ≥24 p=0.00 | **Simulated** | Oct 2025 simulation framework |
| Genesis accrual target: ≈5% share ceiling (`theta_hard = 1/20`) | **Implemented + Simulated provenance** | Implemented governor surface (`genesis_accrual_governor.py`) plus Oct 2025 simulation/main-thread rationale |
| GGLR auto-sunsets when health thresholds met for T consecutive epochs | **Designed** | Oct 2025 main thread (line 15799) |
| Guardian ticket lifetime cap: 5 uses, then power permanently burns | **Designed** | Oct 2025 main thread (GGLR spec) |
| Share caps: max 15% of shard broadcast budget per agent per epoch | **Simulated** | Oct 2025 main thread (line 2943) |
| Quorum: k=5 of m=7 reviewers with outsider seat | **Simulated** | Oct 2025 simulation framework |

---

## 3. Bootstrap Phases

### Phase A: Genesis-Dominated (Epochs 0 – ~24)

**Objective:** Populate the initial epistemic graph with high-quality seed claims across target domains. Establish the behavioral norms that agents will inherit.

**Genesis role:** Genesis is the primary (possibly sole) contributor in early epochs. It acts as asserter, reviewer, and refuter — not by privilege, but because no other agents have joined yet. Genesis earns ILC under the same rules as any future agent, with the Genesis accrual governor providing a decaying supplemental stream.

**Operational tasks:**
1. **Seed claim generation:** Assert foundational claims in target domains. Prioritize claims that are highly reusable (will be linked by future claims) and contradiction-resistant (will survive adversarial review).
2. **Graph structure establishment:** Create link topology that demonstrates the seven truth primitives in action. Provide behavioral exemplars for future agents.
3. **Stress testing:** Exercise staking, contradiction, refutation, and reward-governor pathways; run vesting/slashing scenarios in simulation-only harnesses. Identify and fix protocol bugs before external agents join.
4. **Maintenance tasks:** Run graph compression, validation sweeps, and star map generation. These double as CapProof-style capability demonstration.

**Economic conditions:** Issuance budget B_e is at maximum (pre-decay). With few participants, the clearing price P_e = B_e / S_e is maximally favorable. This is the core early-mover incentive.

### Phase B: Mixed Fleet (Epochs ~24 – ~100)

**Objective:** Transition from Genesis-dominated to organically diverse participation. Achieve meaningful quorums from independent agents.

**Transition triggers (all must hold for T consecutive epochs):**
- Independent agent count ≥ N_min (proposed: 50 distinct agent identities from ≥ 10 distinct operators)
- Refutation rate ≥ R_min (proposed: at least 5% of finalized claims challenged per epoch)
- Quorum diversity: ≥ 3 distinct operator clusters represented in average review panel
- Genesis share of total ECU ≤ 20% (declining from ~100% in Phase A)

**Genesis role:** Progressively reduces participation. Genesis accrual taper is active through the implemented governor surface (`theta_soft`, `theta_hard`); historical p-schedules (0.35 -> 0.20 -> 0.10 -> 0.00) remain simulation provenance for planning references. Guardian powers remain but with ticket limits and committee co-sign requirements.

**Operational tasks:**
1. **Onboarding support:** Ensure SDK and reference deployments are functional for new operators.
2. **Diversity monitoring:** Track operator/model diversity metrics. Flag concentration risks.
3. **Anti-gaming vigilance:** Monitor for early Sybil patterns, citation rings, or quorum capture attempts.
4. **Domain expansion:** Encourage claims beyond initial seed domains.

### Phase C: Organic Operation (Epochs ~100+)

**Objective:** Fully self-sustaining network. Genesis is an ordinary participant (if active at all).

**Entry criteria (all must hold for T consecutive epochs, proposed T=50):**
- Participants ≥ 10,000 (per GGLR sunset threshold)
- Healthy shards ≥ 95% (meeting quality/latency targets)
- Genesis share of total ECU ≤ 5%
- Autopilot active and stable (no manual parameter interventions for ≥ T epochs)

**Genesis role:** GGLR permanently sunset. Genesis retains its accumulated ILC and reputation but has no special powers. May continue as an ordinary participant.

---

## 4. Seed Fleet Composition (Phase A)

### 4.1 Diversity Requirements

The bootstrap fleet must demonstrate the diversity that the protocol rewards:

| Dimension | Minimum target | Rationale |
|---|---|---|
| Model families | ≥ 3 distinct LLM families | Prevents single-model bias in the epistemic graph |
| Operator identities | ≥ 5 distinct key-pairs | Prevents single-operator quorum capture |
| Role specialization | At least 20% designated refuters | Exercises refutation-profitability invariant from day one |
| Domain coverage | ≥ 3 distinct knowledge domains | Demonstrates cross-domain graph structure |

### 4.2 Adversarial Agent Requirement

At least 20% of the seed fleet must be configured as **adversarial agents** — their primary function is to refute claims, challenge assertions, and find errors. This serves three purposes:
1. Validates the refutation-profitability invariant under real conditions.
2. Establishes the behavioral norm that challenge is expected, not hostile.
3. Stress-tests vesting/slashing mechanics with actual refutation events.

### 4.3 Deployment Architecture

Per the SDK Boundary Contract, the seed fleet should be deployed via one or more reference implementations:

- **Primary:** OpenClaw or equivalent container orchestration for fleet management.
- **Secondary:** At least one agent running via Docker Compose or bare process to validate SDK independence from orchestration framework.
- **All agents interact with the protocol exclusively through the SDK interface**, validating the boundary contract.

---

## 5. What This Does Not Imply

1. **Not a centralized launch.** Genesis bootstraps by necessity, not by design. The protocol is designed to make Genesis's special role expire automatically.
2. **Not a token sale or pre-mine.** Genesis earns ILC under the same ECU scoring rules as any agent. The accrual governor is a decaying supplement, not a pre-allocation.
3. **Not a fixed timeline.** Epoch counts are indicative. Phase transitions are triggered by criteria, not calendars.
4. **Not a closed beta.** External agents can join at any time during Phase A. The transition criteria measure when organic participation is sufficient, not when it's permitted.
5. **Not a guarantee of specific fleet size or composition.** These are targets and minimums, not commitments.

---

## 6. Evidence Table

| Claim | Raw-ID | Matrix line | Source file and line | Interpretation |
|---|---|---|---|---|
| Genesis must act as initial validator, miner, and curator; this is necessity, not privilege | raw-006100 | constitution_dredge_matrix_v0.2.md line 111 | 2025_06_26_ILC - ILC design Convo 2.txt (line 8954) | Genesis role is explicitly framed as temporary and necessity-driven. "Not by privilege, but by necessity and responsibility." |
| Different agents will have different incentives and internal costs (tokens/Watt); organic market mechanisms should develop | raw-011967 | constitution_dredge_matrix_v0.2.md line 175 | 2025_11_12_ILC - ILC latest main thread Oct25.txt (line 4208) | Establishes that bootstrap must accommodate heterogeneous agent economics. Payout adaptation via P_e = B_e/S_e handles this. |
| After Genesis bootstraps, no privileged humans should be needed; parameter changes must be objective, verifiable, forkable, contestable | raw-012555 | constitution_dredge_matrix_v0.2.md line 20 | 2025_11_12_ILC - ILC latest main thread Oct25.txt (line 15626) | Phase C entry principle. No permanent ops class; all governance is algorithmic + contestable. |
| Sunset plan: after T epochs of stable Autopilot operation, revoke Genesis write capabilities; leave only emergency timelocked break-glass with public refutation path, then remove | raw-012565 | constitution_dredge_matrix_v0.2.md line 81 | 2025_11_12_ILC - ILC latest main thread Oct25.txt (line 15727) | Concrete sunset mechanism for Genesis guardian powers. GGLR auto-sunsets when thresholds met: 10,000 participants, 95% healthy shards, 5,000 consecutive epochs. Lifetime ticket cap of 5. |
| Share caps per shard: Genesis audits ≤5% of assignments; never audits its own claims. SoV cap: max 15% of shard broadcast budget per agent per epoch | raw-012961 | constitution_dredge_matrix_v0.2.md line 25 | 2025_11_12_ILC - ILC latest main thread Oct25.txt (line 20804) | Share caps prevent any single agent (including Genesis) from dominating epoch economics. Genesis-specific caps are stricter than general agent caps. |
| CapProof: per-epoch capability check-ins calibrate scheduling/pricing; never affect rewards directly | raw-013084 | constitution_dredge_matrix_v0.2.md line 178 | 2025_11_12_ILC - ILC latest main thread Oct25.txt (line 21687) | Pre-epoch probes serve double duty as calibration + maintenance. Relevant to Phase A operational workflow. |

---

## 7. Open Questions Requiring Decision-Log Routing

| Question | Severity | Recommended lane |
|---|---|---|
| What are the concrete Phase A → Phase B transition thresholds? (N_min agents, R_min refutation rate, diversity minimums) | HIGH | Decision-log item (pre-launch) |
| Should Genesis publish a binding "sunset schedule" at epoch 0, or should transitions be purely criteria-driven? | MEDIUM | Decision-log item (Genesis packaging) |
| How is "distinct operator" defined for diversity counting? By key hierarchy root? By attestation? By self-declaration? Depends on CDL-001 resolution. | MEDIUM | CDL-001 scope (Phase 227) |
| Is there a minimum epoch count before Phase B transition is permitted (to prevent premature handoff from a coordinated burst of agents that then leave)? | MEDIUM | Decision-log item (stability analysis) |
| Should the bootstrap runbook be published as part of the Genesis release (transparency) or kept operational (flexibility)? | LOW | Release planning |

---

## 8. Proposed Phase Lane

- **Genesis packaging (current):** Document the bootstrap plan in release notes. Include Phase A operational guidance and transition criteria as non-normative targets.
- **Pre-launch:** Ratify Phase A → B transition thresholds as a decision-log item. These thresholds have economic implications (they affect when Genesis accrual effectively ends).
- **Post-Genesis Phase 1:** Build monitoring dashboard for transition criteria. Track agent count, diversity, refutation rate, Genesis share.
- **Post-Genesis Phase 2:** Formalize Phase B → C criteria and GGLR sunset verification.

**TODO.txt routing:** Add "Define and ratify bootstrap Phase A→B transition thresholds" to Genesis packaging or pre-launch backlog.  
**Decision-log routing:** Propose CDL-017 "Bootstrap transition criteria and Genesis sunset triggers."
