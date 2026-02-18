# ILC Mining Economics, Bootstrapping Incentives, and Distribution Strategy v0.1

Status: Active strategic analysis — **non-normative**  
Date: 2026-02-18  
Author: Claude Opus 4.6 (Strategic Architectural Reviewer, claude.ai)  
Context basis: Historical corpus (Z_Past_Chats), simulation record, constitutional context audit, and strategic review discussions.

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

Document the "mining" economics of ILC, how early-mover incentives resolve the cold-start bootstrapping problem, the relationship between issuance decay and token scarcity, and the role of container-based agent orchestration (e.g., OpenClaw) as a distribution and bootstrapping mechanism.

This document is intended for cross-review by the project management team (Codex) and should inform whitepaper revisions, tokenomics specification, and go-to-market planning.

---

## 2. The Mining Analogy: How ILC is "Mined"

### 2.1 Core Mechanism

ILC tokens are not mined through proof-of-work computation. They are earned through **proof-of-intelligent-labor** — epistemic contributions that survive adversarial challenge within the protocol.

The economic flow per epoch:

1. **Fixed issuance budget (B_e):** **[DESIGNED]** Each epoch has a predetermined ILC budget derived from the issuance curve plus net protocol fees minus treasury earmarks.
2. **ECU scoring:** **[IMPLEMENTED]** Every finalized claim receives an ECU score based on weighted components. The Genesis codebase uses a four-component model (reuse, contradiction-resistance, validation, path diversity) per the implemented `node_value_kernel.py`. Note: the October 2025 simulations used a three-component model (reuse, contradiction-resistance, refinement); the four-component kernel is a legitimate design evolution under the ratified "balanced composite" principle (CDL-011).
3. **Pro-rata clearing:** **[DESIGNED]** The epoch's ILC budget is distributed proportionally: `ILC_i = ECU_i * (B_e / S_e)` where `S_e` is total ECU earned that epoch.
4. **Vesting and slashing:** **[SIMULATED]** Rewards vest over V epochs (~4). Unvested rewards are burned if the claim is later successfully refuted. *These mechanics are simulation-validated but not implemented in the Genesis codebase.*

**Key property: usefulness is relative.** An agent's ECU is measured against all other contributions finalized in the same epoch. This means your share of the epoch's ILC budget depends not on the absolute quality of your work but on its quality relative to everything else submitted that epoch.

### 2.2 Why "Mining" is the Correct Analogy

| Property | Bitcoin | ILC |
|---|---|---|
| Fixed supply cap | 21M BTC (hard) | C_max (hard, immutable without hard fork) **[DESIGNED]** |
| Issuance decay | Block reward halving every ~4 years | Geometric decay per epoch, asymptoting toward zero **[DESIGNED]** |
| Who earns issuance | Miners (valid blocks via proof-of-work) | Contributors (finalized claims via proof-of-intelligent-labor) **[DESIGNED]** |
| Quality filter | None — all valid blocks are equivalent | Yes — ECU scoring differentiates quality (four-component: reuse, contradiction, validation, path) **[IMPLEMENTED]** |
| Deflationary pressure | Transaction fees to miners | Fee burns + refutation burns reduce circulating supply **[DESIGNED]** |
| Early builder advantage | Lower difficulty, higher block rewards | Fewer participants, larger epoch share **[DESIGNED]** |
| Security model | Energy expenditure makes attacks costly | Stake + vesting + slashing make dishonesty costly **[SIMULATED]** |

The analogy is structurally sound: ILC replaces Bitcoin's "burn electricity to solve a hash" with "perform epistemic labor that survives adversarial challenge." The economic scaffolding (fixed supply, decaying issuance, deflationary burns, pro-rata distribution) is deliberately Bitcoin-parallel.

**Critical difference:** Bitcoin mining has no quality filter — any valid block earns the reward regardless of its content. ILC mining has a strong quality filter — claims that are more reused, more contradiction-resistant, more validation-backed, and stronger on path contribution signals earn proportionally more ECU. This means ILC mining rewards intelligence, not just capital expenditure. **[IMPLEMENTED — ECU quality differentiation is in the Genesis scoring kernel; token distribution and vesting are DESIGNED only.]**

---

## 3. The Issuance Decay Schedule

### 3.1 What Exists in the Design Record

The October 2025 main thread (lines 4610-4692) establishes:

- **Hard cap (C_max):** **[DESIGNED]** A fixed maximum total supply embedded at genesis, immutable without hard fork. Proposed value: 1,000,000,000 ILC (sufficient divisibility for micro-rewards).
- **Issuance curve:** **[DESIGNED]** Geometric decay ("halvings"), front-loaded across early epochs, asymptoting toward zero. Two formulations discussed: discrete halvings every H epochs, or continuous decay `e^(-lambda * t)`.
- **Tail emission:** **[DESIGNED]** A small perpetual tail emission for liveness (prevents the network from stalling when issuance approaches zero, similar to Monero's approach).
- **Genesis-locked constants:** **[DESIGNED]** C_max, issuance curve, fee-burn split, and vesting length V are immutable except via hard fork.

A later summary (line 6405) proposes allocation per emission:
- Task bounties (performers): 80%
- Auditor pool: 15%
- Genesis/Endowment: 5% time-locked stream

### 3.2 Reconciliation Required: Hard Cap vs Tail Emission

The historical corpus describes both a **hard cap** (C_max is immutable, total supply can never exceed it) and **perpetual tail emission** (small ongoing issuance for liveness). These are logically incompatible as stated. Three reconciliation models exist:

**Model A — Asymptotic cap (Monero-style).** Tail emission is so small relative to C_max that the total minted supply never reaches the cap in any practical timeframe. C_max functions as a theoretical ceiling rather than a binding constraint. *Problem:* If tail emission is truly perpetual, it eventually reaches C_max given infinite time, making the "hard" cap soft.

**Model B — Fee-funded tail rewards.** Issuance from minting decays to zero (hard cap is binding). After issuance exhausts, epoch rewards are funded entirely by protocol fees (transaction fees, broadcast fees, contra fees). The "tail emission" is actually fee redistribution, not new minting. *This is the Bitcoin model:* after all 21M BTC are mined, miners are compensated solely by transaction fees.

**Model C — Burn-offset tail emission.** Small perpetual minting continues, but is offset by fee burns and refutation burns. If burn rate ≥ emission rate, circulating supply is deflationary even with ongoing minting. C_max constrains *gross* minting; net circulating supply can be well below it.

**Recommendation:** Model B (fee-funded tail) is the cleanest and most Bitcoin-consistent. It preserves a true hard cap, eliminates the logical contradiction, and creates a natural economic transition: early epochs are issuance-dominated; later epochs are fee-dominated. The historical corpus's discussion of fee burns (30-50% of fees burned, remainder to rewards budget) already assumes this model implicitly. This reconciliation should be ratified as a CDL item.

### 3.3 What is NOT Yet Closed

The following issuance parameters are discussed but not ratified or implemented:

1. **Exact C_max value:** 1,000,000,000 proposed but not locked.
2. **Halving period H:** Not specified. Bitcoin uses ~4 years (~210,000 blocks). ILC needs an epoch-denominated equivalent.
3. **Continuous vs discrete decay:** Both formulations discussed, neither chosen.
4. **Tail emission rate:** Acknowledged as necessary but no value proposed.
5. **Fee-burn split ratio:** 30% burn / 70% to rewards budget proposed but not locked. A later discussion proposes 50% burn for broadcast/contra fees.
6. **Allocation split (performer/auditor/genesis):** 80/15/5 proposed but not reconciled with the Genesis accrual governor's theta_hard = 1/20 (5%) — these appear aligned but should be explicitly confirmed.

### 3.4 Why This Must Be Closed Before or At Genesis

The issuance decay schedule is the primary early-mover incentive mechanism (see Section 4). Without a locked schedule:

- Early participants cannot calculate expected returns.
- The "mine early when epoch budgets are large" narrative has no concrete numbers behind it.
- The hard cap cannot be verified by external auditors.
- Token economics are unspecifiable for any exchange, legal, or partnership context.

**Recommendation:** The issuance decay schedule should be ratified as a Genesis-locked constant. It does not need to be implemented in the scoring kernel (which is the Genesis codebase scope), but it must be specified in the whitepaper and tokenomics documentation so that the economic contract with early participants is explicit and immutable.

---

## 4. Early-Mover Incentives and the Phase A Bootstrapping Solution

### 4.1 The Cold-Start Problem (Restated)

The strategic review identified the cold-start problem as ILC's biggest execution risk: the network needs participants to generate value, but participants need value to justify participation. This creates a chicken-and-egg coordination problem with two phases:

- **Phase A (bootstrap through critical mass):** Value is speculative. Participation requires belief that the network will eventually reach Phase B.
- **Phase B (post critical mass):** Value is demonstrated. The epistemic graph has survived sustained adversarial challenge from diverse independent agents.

The question was: what makes Phase A participation rational?

### 4.2 The Mining Incentive as Phase A Solution

The issuance decay schedule resolves this. Early-epoch economics are structurally favorable:

**Fewer participants, larger shares.** If epoch 1 has 10 agents and epoch 1000 has 10,000 agents, each epoch-1 agent receives approximately 1,000x more ILC per unit of equivalent ECU. This is not a bug — it is the designed reward for bearing early-network risk.

**Higher issuance budgets.** The geometric decay schedule means early epochs have the largest B_e values. Combined with fewer participants, the clearing price P_e = B_e / S_e is maximally favorable in early epochs.

**Token appreciation potential.** If the network succeeds (graph becomes useful, participation grows, demand for ILC increases), early-accumulated tokens appreciate. The fixed supply cap ensures no dilution.

**This is structurally identical to Bitcoin's early-mover incentive.** Early Bitcoin miners earned 50 BTC per block with low difficulty. The calculation was: "mine now when rewards are high and competition is low; if Bitcoin succeeds, these tokens become valuable." No belief in Bitcoin's long-term utility was required — only belief in potential token appreciation.

ILC's early-mover calculation is: "Deploy agents now when epoch shares are large and competition is sparse. If ILC succeeds, accumulated tokens appreciate." The epistemic graph quality emerges as a byproduct of economic incentives, not as a prerequisite for participation.

### 4.3 Why ILC's Mining Incentive is Stronger Than Bitcoin's

Bitcoin mining requires capital expenditure (hardware + electricity) with no quality differentiation — all valid blocks are equivalent. This led to industrialization, mining pools, and a race to the bottom on energy efficiency.

ILC mining requires epistemic capability. The quality filter (ECU scoring with reuse, contradiction-resistance, validation, and path components) means:

- **Spam is unprofitable.** **[IMPLEMENTED — ECU scoring]** Low-quality contributions earn low ECU and therefore low ILC. The pro-rata clearing price means spammers dilute their own returns.
- **Refutation is profitable.** **[IMPLEMENTED + GATED — Phase 212]** The refutation-profitability invariant structurally ensures that finding and correcting errors pays better than passive validation. This creates an adversarial economy where the most profitable strategy is rigorous honesty.
- **Diversity is rewarded.** **[IMPLEMENTED]** The reuse-diversity weighting penalizes single-actor gaming and rewards cross-agent endorsement. Sock puppets and citation rings face economic penalties.
- **Staleness decays.** **[IMPLEMENTED]** The freshness gate reduces the value of old claims that aren't being reused, preventing passive rent-seeking on early contributions.

The net effect: ILC mining rewards agents that produce genuinely useful, robust, novel epistemic work — not agents that merely consume resources. The quality filter prevents the industrialization pathology that Bitcoin experienced.

### 4.4 The First-Mover Persona

The practical implication for go-to-market: ILC's first movers are likely **AI developers who already have capable agents and see an opportunity to monetize their agents' epistemic output.**

The pitch: "Your agent is already doing intelligent work — answering questions, analyzing data, generating insights. ILC lets it earn tokens for that work, verified by adversarial challenge, with early-epoch economics that reward first movers."

This is distinct from crypto speculation (which requires only capital) and from academic contribution (which requires only expertise). ILC first movers need both: capable agents (technical) and willingness to stake on a new network (economic).

---

## 5. OpenClaw and Container-Based Distribution

### 5.1 Three Distinct Problems

Container-based agent orchestration (OpenClaw, Docker Compose, Kubernetes) addresses three problems that should be kept architecturally separate:

**Distribution** (getting the code into people's hands): Solved by standard packaging — pip install, Docker images, GitHub releases. Phase 225 handles this. Container orchestration adds minimal value over a well-structured Docker image.

**Orchestration** (running multiple ILC-participating agents in coordination): This is where container frameworks genuinely add value. Running a fleet of agents — some asserting, some reviewing, some refuting — with different model backends and identity management is a natural fit for container orchestration.

**Bootstrapping** (populating the initial graph): The seed agent fleet discussed in the bootstrapping analysis (diverse model families, adversarial agents, quorum-density planning) maps directly to container orchestration. OpenClaw (or equivalent) becomes the mechanism for deploying the bootstrap fleet.

### 5.2 Recommended Architecture

**The ILC Agent SDK is the product.** A clean Python (or language-agnostic) interface that any agent can use to participate in the protocol: assert claims, review claims, refute claims, manage stakes, read the graph. This interface must be independent of any deployment mechanism.

**Container deployments are distribution channels.** Build reference deployments for multiple orchestration frameworks:

1. **OpenClaw reference deployment:** Full fleet orchestration with model-family diversity, adversarial agent roles, and quorum-density configuration. This is the primary bootstrap toolkit and the "getting started with a fleet" experience.
2. **Docker Compose reference:** Simpler multi-agent setup for developers who don't use OpenClaw.
3. **Single-process development mode:** Minimal setup for individual developers testing single-agent participation.

**The SDK-to-orchestration boundary must be clean.** An agent built against the SDK must work identically whether deployed in OpenClaw, Docker Compose, Kubernetes, or bare metal. The orchestration layer handles lifecycle, networking, and resource management. The SDK handles protocol interaction. If OpenClaw changes direction or goes unmaintained, agents migrate to another orchestration layer without code changes.

### 5.3 OpenClaw as Go-to-Market Channel

The strategic value of OpenClaw integration depends on its community:

**High value if:** OpenClaw has an active ecosystem of developers deploying autonomous agents that need to coordinate on claims, verify information, or establish trust. These developers are the natural first-mover persona for ILC — they already have capable agents and are looking for coordination mechanisms.

**Lower value if:** OpenClaw is primarily an infrastructure tool without a strong agent-developer community. In this case, it's a deployment convenience but not a distribution channel.

**Evaluation criteria:** Before investing in deep OpenClaw integration, assess: How many active agent developers? What kinds of agents are being deployed? Is there a natural demand for epistemic coordination? Are developers already solving trust/verification problems that ILC addresses?

### 5.4 Bootstrapping via OpenClaw

The seed agent fleet architecture maps to container orchestration:

| Requirement | Implementation |
|---|---|
| Model-family diversity | Deploy containers with different LLM backends (Claude, GPT, Gemini, Llama, Mistral) |
| Adversarial agents | Designate ~20% of containers as dedicated refuters |
| Quorum density | Scale fleet to support meaningful quorums across target domains |
| Domain coverage | Configure agent specializations per hub-and-spoke bootstrap plan |
| Monitoring | Container-level telemetry on ECU, refutation rates, diversity metrics |
| Transition criteria | Automated checks against bootstrap exit conditions |

The OpenClaw deployment becomes a reusable reference implementation: "this is how you run a fleet of ILC-participating agents." Post-bootstrap, it serves as the template for external operators who want to deploy their own agent fleets.

---

## 6. Open Questions for Cross-Review

### 6.1 Issuance Schedule Closure (Priority: HIGH)

The issuance decay schedule is discussed extensively in the historical corpus but not ratified. Specific parameters needing closure:

1. C_max value (1B proposed).
2. Halving period or continuous decay rate.
3. Tail emission rate.
4. Fee-burn split ratio.
5. Allocation split (performer/auditor/genesis).

**Question for Codex:** Should issuance schedule ratification be added to the Genesis packaging sequence (222-229), or is it correctly deferred to a post-Genesis tokenomics phase? The argument for Genesis inclusion: without a locked schedule, the early-mover incentive narrative is unspecifiable. The argument for deferral: the Genesis codebase is a scoring/reward simulation framework, not a running token economy.

### 6.2 Reconciliation of Genesis Accrual Parameters

The October 2025 simulations use an 8% Genesis siphon on referenced tasks with p_g = 0.35 reference probability. The implemented Genesis accrual governor uses theta_hard = 1/20 (5% of total issuance). The later emission allocation proposes 5% to Genesis/Endowment.

These numbers are in the same range but measure different things (task-level ECU share vs total issuance share vs emission allocation). They appear compatible but the reconciliation should be explicit.

**Question for Codex:** Is there a single authoritative statement of how Genesis accrual works that reconciles these three formulations? If not, this should be produced as part of the pre-Genesis documentation.

### 6.3 OpenClaw Integration Timing

**Question for Codex:** Is OpenClaw integration a Genesis-scope deliverable, a near-term post-Genesis priority, or a longer-term ecosystem play? This affects whether the SDK abstraction layer needs to be designed now (to ensure clean separation) or can evolve organically.

### 6.4 Whitepaper Coverage

Based on the full historical corpus review, the following topics should be front-and-center in the whitepaper but may not be adequately covered:

1. **The "observed epistemic value" framing.** ILC measures what the epistemic community treats as load-bearing, not objective truth. This is the project's most important philosophical contribution.
2. **The mining analogy done properly.** Bitcoin's value anchored to energy cost; ILC's value anchored to epistemic labor that survived adversarial challenge. Early-mover economics with decaying issuance.
3. **The self-leveling mechanism design.** Ten documented mechanisms, four simulation-validated. This differentiates ILC from naive token systems.
4. **The honest acknowledgment of convergence limitations.** ILC converges on the most economically defensible epistemic position, not on objective truth. This is a strength when stated explicitly.

**Question for Codex:** What is the current whitepaper's coverage of these four topics? Should whitepaper revision be scoped into the Genesis packaging sequence, or treated as a parallel workstream?

---

## 7. Summary

The "mining" economics of ILC provide a structurally sound early-mover incentive that resolves the Phase A bootstrapping problem. The mechanism is: deploy agents early when epoch shares are large, accumulate ILC with favorable economics, benefit from token appreciation if the network succeeds. This is Bitcoin's bootstrapping model adapted for intelligent labor rather than energy expenditure, with the critical addition of a quality filter that prevents industrialization pathologies.

The issuance decay schedule is the keystone of this incentive structure and must be ratified — either within the Genesis packaging sequence or as an immediate post-Genesis deliverable.

Container-based orchestration (OpenClaw or equivalent) is the natural deployment mechanism for the bootstrap fleet and a potential go-to-market channel, but must be architecturally separated from the ILC Agent SDK to prevent coupling risk.

These findings should inform whitepaper revisions, tokenomics specification, and go-to-market planning.
