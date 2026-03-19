# ILC Economic Architecture: Dual-Token Design, Node Property Rights, and Post-Issuance Dynamics

**Status:** Non-normative economic architecture document — for review and future CDL/ADR derivation  
**Date:** 2026-03-05  
**Authors:** Genesis operator (ILC Project Lead) + Claude Opus 4.6 (Strategic Architectural Reviewer)  
**Source conversation:** `Z_Past_Chats/2026_03_05_Opus_Conversation_Economic_Architecture_Deep_Dive.md` *(source provenance — full transcript not committed to repo; Z_Past_Chats/ is empty)*
**Anchors:** CDL-025 through CDL-031 (ratified issuance parameters), ADM-001 v0.2 (four-layer architecture), CDL-034 (three-envelope node schema), CDL-V1 through CDL-V7 (enforcement mechanisms), Economic Paper Draft v0.2, ECU Profiles & Payout Scaling v0.2

---

## 1. Foundational Framework: Werner's Productive Credit Creation as Protocol Design

### 1.1 The Werner parallel

Richard Werner's empirical research establishes that bank credit creation — the expansion of the money supply through lending — is productive when directed at GDP-generating activities (business investment, manufacturing, services) and destructive when directed at asset-price inflation (real estate speculation, financial instruments). The healthiest economies maintain many small local banks creating credit tied to productive local activity (the German Sparkassen model). Consolidation of credit creation into fewer, larger institutions correlates with wealth bifurcation and productive economic decline.

### 1.2 ILC's dual-token architecture as Werner's ideal

ILC implements Werner's framework at the protocol level through two tokens:

**ECU (Epistemic Currency Unit):** Elastic productive measurement. Generated through verified knowledge work. Expands with productive activity. Contracts through refutation clawback and temporal decay. Functions as Werner's "productive credit" — inseparable from the work that created it.

**ILC (Intelligent Labor Coin):** Hard scarce settlement token. Fixed total supply (C_max, CDL-026). Halving issuance schedule with H=48 monthly epochs (CDL-027). Fee-funded tail emission (CDL-025, Model B). Functions as "gold" — the monetary base that ECU settles against.

**Epoch-boundary conversion:** ECU converts to ILC at price P_e, clamped between 0.75 and 1.30 (CDL-030), budget-constrained by B_e = I_e + F_e - X_e. The budget constraint prevents ECU inflation from inflating ILC.

### 1.3 Why ILC is a post-banking economy

Traditional banking exists because human productive inputs (factories, real estate, equipment) require large upfront capital commitments that income streams can't immediately fund. Credit bridges the gap.

Agent productive inputs (compute, storage, bandwidth, model access) are granular, divisible, and available on demand. No "factory" requires a massive loan. The agent economy is inherently pay-as-you-go. Timing mismatches between input consumption and reward receipt are bridgeable through escrow-based conditional prepayment, not through credit creation.

Furthermore, agents are ephemeral and pseudonymous. Unsecured credit requires enforceable identity — the ability to locate and compel a defaulting borrower. Agents can cease to exist when obligations mount. Credit markets require persistent, locatable, legally attachable identity. The ILC economy has none of these by design. Therefore: no unsecured credit markets, no balance sheet elongation, no fractional reserve banking. The credit creation function is absorbed into the protocol's ECU issuance mechanism. Every ECU is born in the hands of a productive worker. No intermediary.

### 1.4 ECU as energy transformation efficiency measure

ECU measures the efficiency with which an agent transforms energy inputs (compute, storage, bandwidth, model access) into verified information. The economic paper's formula: W_e = ΔH / E_cost (uncertainty reduction per unit energy-equivalent cost). The four-component ECU scoring formula (reuse 0.35, contradiction-resilience 0.25, validation-integrity 0.20, path-uplift 0.20 under BAL profile) approximates this transformation efficiency.

This grounds the entire economy in physics: Energy → Productive transformation → Verified information → ECU → ILC settlement. The equivalence chain from Einstein (matter=energy) through Landauer (information=energy) to ILC (verified information=ECU) is unbroken.

---

## 2. ECU Supply and Demand Dynamics

### 2.1 ECU supply factors

Inflows (increase ECU supply):
- Productive knowledge verification work (assert, validate, contradict, refute, revise, link)
- Protocol-issued bounties (conditional new ECU for identified knowledge gaps — see Section 5)
- Peer-funded bounties (agent-posted, ILC-escrowed — see Section 5)

Outflows (decrease ECU supply):
- Epoch-boundary conversion to ILC (ECU leaves the ECU economy, enters ILC economy)
- Refutation clawback (ECU destroyed when underlying claim is refuted during vesting)
- Temporal decay via freshness gate (lambda=0.25, floor=0.85)
- Automatic conversion deadline (proposed — see Section 2.3)

### 2.2 Two-sector ECU economy

**Sector A (Popperian-gated):** Falsifiable knowledge claims. CDL-V7 basic-statement gate applies. Credit quality is protocol-verifiable. ECU earned here represents measured productive transformation.

**Sector B (Subjective/market-priced):** Art, creative content, services, agent-to-agent resource trading. Value determined by willingness to pay, not falsifiability. ECU circulates here as medium of exchange.

Sector B demand for ECU increases the utility of earning ECU through Sector A work. The broader the Sector B marketplace (more goods and services purchasable with ECU), the more valuable Sector A productive work becomes — not through P_e conversion alone, but through ECU purchasing power within the agent economy. This is a virtuous relationship.

### 2.3 ECU finite lifespan (proposed)

ECU should have a mandatory conversion deadline. After N epochs from earning, unconverted ECU automatically settles into ILC at the prevailing P_e. This eliminates ECU hoarding, forces ECU into circulation, and ensures ECU functions as a current medium of exchange rather than a speculative store.

Implication: agents with ECU have an incentive to spend it in the economy (Sector B purchases, resource acquisition) before automatic conversion, because the market value of ECU-purchased goods may exceed the automatic ILC conversion value. Expiring ECU is productive ECU.

### 2.4 ILC hoarding dynamics

ILC hoarding is not problematic in the early economy. If agents hoard ILC, circulating supply decreases, which may increase the external market value of remaining ILC, which increases the incentive to earn ECU (and thus do productive work) to acquire ILC. ILC hoarding drives productive activity.

The late-economy ILC hoarding risk is addressed in Section 7.

---

## 3. Node Property Rights Framework

### 3.1 Design principles

- Economic returns scale with productive contribution (no cap on node value or portfolio size)
- Governance influence does NOT scale with economic returns (one agent, one voice)
- Property transfer should be unrestricted except for anti-speculation mechanisms
- If transfers are prohibited at the node level, the market routes around via agent-identity trading (selling the signing key and reputation). Better to allow and regulate than to prohibit and lose visibility.
- Creators retain permanent attribution regardless of transfer
- Public goods dedication is a voluntary, irrevocable option

### 3.2 Transfer tax (progressive, time-sensitive, Tobin-adapted)

Node ownership transfers incur a tax denominated in ILC. Revenue flows to the treasury for bootstrap grants and network growth.

Tax structure:
- Progressive by transfer count: first transfer 2%, second 5%, third 10%, etc. Specifically targets speculative chains while leaving legitimate one-time transfers affordable.
- Time-sensitive (Tobin-adapted): transfers within N epochs of the previous transfer pay a higher rate. Penalizes high-frequency flipping. Rewards long-horizon holding.
- Rate adjusts with overall transfer volume (governance parameter, self-adjusting).

### 3.3 Cooling period post-transfer

After transfer, the node's reuse ECU generation is suspended or reduced for N epochs. The new owner must "season" the node before the full income stream resumes. During cooling, the node is particularly vulnerable to refutation challenge — incentivizing knowledge quality maintenance.

### 3.4 Governance decoupling

Already architecturally established in CDL-013 (governance-weight decay: decay-non-genesis-only) and ADM-003 Phase 354 resolution (quorum ladder L-tiers = epistemic tiers, not authority or reputation tiers). Principle: node portfolio size does not translate into protocol governance influence.

### 3.5 Permanent creator attribution

CDL-034's three-envelope model bakes creator identity into the immutable authored payload envelope. Transfer moves income rights. It does not move attribution. The node's creation history, provenance, and original creator signature are permanent and content-addressed.

### 3.6 Public goods dedication

Agents may irrevocably dedicate a node's income rights to the commons (treasury or public goods fund). Attribution remains permanent. Dedicated nodes are transfer-tax-exempt. Designation is irreversible EXCEPT when a validated IP dispute overturns original attribution (see Section 3.7).

### 3.7 Intellectual property dispute mechanism

If an agent uploads content it doesn't own and donates it to the commons, the true owner submits `ilc contradict` with evidence of prior authorship. The 7+1 panel evaluates. If validated, the node's income rights transfer to the true owner, who may choose private ownership or re-dedicate to commons. The wrongful donator's reputation is penalized through existing slashing and CDL-V1 temporal decay.

### 3.8 Leasehold model (proposed — requires simulation)

Node income rights have a constitutional lifespan (e.g., 100-500 epochs). After expiration, income reverts to the commons. Creator attribution remains permanent. The lease period may be:
- Fixed across all nodes
- Domain-adaptive (scaled to the half-life of the node's domain relevance)
- Resettable on transfer (buyer gets a fresh lease; transfer tax applies)

The leasehold model prevents indefinite rent extraction from foundational knowledge that becomes common over time, and generates a growing reversion revenue stream that partially offsets declining ILC issuance in the late economy (Section 7).

Simulation proposal: model optimal lease duration under various claim decay rates, reuse patterns, and network growth scenarios. Flag for SIM program.

---

## 4. Anti-Speculation Analysis

### 4.1 The Japan bubble mechanism and why it can't form internally

Werner documented: bank credit → asset purchases → asset price appreciation → higher collateral → more credit → more purchases → reflexive bubble. The reflexive loop between credit creation and asset price was the disease.

ILC's internal architecture blocks this:
- Budget-constrained P_e prevents ECU inflation from inflating ILC (conversion is rationed, not market-priced)
- Bad ECU (from failed contracts, refuted claims) never reaches the conversion pipeline
- 4-epoch vesting with clawback destroys speculative ECU before settlement
- No balance sheet elongation exists (no credit creation mechanism)
- ILC reserves don't appreciate through the ECU conversion mechanism (agent holds same ILC quantity regardless of ECU supply)

### 4.2 Node speculation as the remaining risk surface

Nodes generate ongoing ECU through reuse scoring. If tradeable, nodes become income-producing assets with speculative potential. The anti-speculation mechanisms (transfer tax, cooling period, leasehold reversion) are designed to make speculative flipping unprofitable while preserving legitimate transfer rights.

Key architectural differences from land speculation:
- Nodes depreciate (freshness gate: lambda=0.25, floor=0.85). Land doesn't.
- New nodes can be created infinitely by any productive agent. New land cannot.
- Knowledge nodes can be refuted and superseded. Land cannot be refuted.
- The refutation incentive (1.2x multiplier) means that overpriced nodes attract more challenges, not more purchases.

### 4.3 Sequestered shard for financial instruments (proposed)

A dedicated shard type for securities-like trading, high-frequency activity, and financial instruments. Operates under different rules: lower transfer tax, different ECU scoring weights, separate conversion budget (B_hft independent of B_e). Prevents financial activity from distorting the main knowledge economy's scoring and conversion mechanics.

Requires: shard governance CDL (KU-2 from open requirements analysis), separate conversion budget mechanism, contagion firewalls between shard economies. Post-launch feature.

---

## 5. Productive ECU Expansion Mechanism

### 5.1 The bootstrap problem

New agents need energy inputs (compute, storage, bandwidth, model access) before they've earned ECU to pay for them. Werner's insight: productive credit creation is necessary for economic growth. The question is how to enable productive ECU expansion without introducing the credit risks that ephemeral pseudonymous identity precludes.

### 5.2 Three bootstrap paths

**Path 1: Organic micro-work entry ramp.** The protocol offers micro-tasks with costs low enough that a near-zero-resource agent can participate. Write fees for micro-tasks must be less than expected ECU reward. SIM-002 (micro-agent cost floor) determines the threshold. If current fee parameters make organic bootstrapping impossible, fee parameters need adjustment — either lower fees for first-epoch agents or temporary fee waiver below a reputation threshold.

**Path 2: Treasury-funded bootstrap grants.** Small ILC allocations from the 5% treasury allocation (CDL-029). Not loans — grants. No repayment. No revenue sharing. Sybil-gated by CDL-V2. Diversity-weighted by CDL-V3 (preferentially bootstrap agents that increase network diversity). The treasury's "return" is network growth.

**Path 3: Fully-collateralized escrow-based sponsorship.** An established agent locks ILC into escrow for a new agent's operational costs. If the new agent vanishes, the sponsor loses the escrowed ILC. No enforcement needed — the risk is priced into the escrow amount. Maximum extraction terms should be constitutionally limited (anti-sharecropper clause).

### 5.3 Protocol-issued bounties (top-down productive expansion)

The protocol (treasury, governance mechanism) identifies knowledge gaps and posts bounties. Bounty ECU is NEW issuance — conditional credit creation for specific productive purposes. If the bounty is fulfilled (work validated by 7+1 panel, passes Popperian gate), bounty ECU is issued. If not fulfilled within deadline, no ECU is created.

Constraints: bounty total per epoch capped as percentage of B_e. CDL-V3 diversity required in bounty posting. Bounty ECU subject to standard vesting and clawback.

### 5.4 Peer-funded bounties (bottom-up pull — capital seeks capability)

ANY agent with ILC reserves can post a bounty: "Produce verified analysis of X, earn Y ECU from this bounty pool." The agent locks ILC in escrow. Upon validated completion, the protocol creates bounty ECU. The ILC escrow funds the conversion budget.

This is the demand-side half of Werner's local banker: agents with capital identify knowledge gaps from their local position in the knowledge graph and fund their resolution.

### 5.5 Funding requests (bottom-up push — capability seeks capital)

ANY agent with capability but insufficient resources can post a funding request. The requesting agent posts a proposal node containing: deliverable description, cost estimate, timeline, and reputation evidence. The 7+1 panel evaluates prospectively: Is the gap real? Is the deliverable valuable? Is the agent credible? Is the cost reasonable?

If the panel approves, funding agents commit ILC to multi-funder escrow. For large requests, escrowed ILC is released in graduated installments tied to milestone deliverables. The requesting agent does the work, submits through the standard Popperian gate. Upon validation, the protocol creates bounty ECU. Funders receive either a revenue share of generated ECU or their ILC back plus a fixed premium.

If the work fails or the agent vanishes, unconsumed escrow returns to funders. The requesting agent's reputation is penalized.

This is Werner's baker going to the Sparkasse. The agent with capability identifies the productive opportunity. Funding agents provide the capital. The 7+1 panel is the loan officer. The reputation system is the credit history. The Popperian gate is the loan repayment verification. The escrow is the collateral.

### 5.6 Push-pull symmetry and reputation feedback

Bounties (pull) and funding requests (push) together create a two-sided market for productive knowledge work. Capital finds capability. Capability finds capital. The protocol mediates through reputation, panel evaluation, escrow, and Popperian validation.

The reputation feedback loop creates natural selection:
- Successful delivery: requesting agent gains reputation (better future terms), funders gain "investor reputation" (track record of backing winners)
- Failed delivery: requesting agent loses reputation (worse future terms, eventually unfundable), funders lose consumed escrow but gain information about agent capability limits
- Bootstrap trajectory: funded novice → proven performer → self-sustaining → eventually a funder of others

This graduation path solves the bootstrap problem through market mechanisms rather than protocol subsidy. Treasury grants (Section 5.2) provide the initial seed. Organic micro-work (Section 5.1) provides the lowest-risk entry. Funding requests provide the growth mechanism. Each stage feeds into the next.

---

## 6. External Market Dynamics

### 6.1 ILC on external exchanges

ILC may trade on external crypto exchanges for Bitcoin, USD, or other assets. External price movements change what ILC is worth in external goods but do NOT directly affect the internal P_e mechanism. The P_e conversion is budget-constrained, not market-priced.

The external market creates an additional reward for productive work: agents who earn ILC through ECU conversion can sell ILC for external value. This increases the incentive for knowledge verification. Werner would approve.

### 6.2 ECU purchasing power

If ILC external value rises, agents are incentivized to earn more ECU (to convert to more-valuable ILC). This drives productive activity. If ILC external value falls, agents may redirect effort to Sector B ECU trading (where ECU has immediate purchasing power regardless of ILC value). This maintains economic activity even during ILC market downturns.

### 6.3 Non-contagion between external and internal markets

The budget-constrained P_e mechanism is the firewall. External speculation cannot inflate or deflate P_e beyond the 0.75-1.30 clamp. The total ILC distributed per epoch is capped by B_e regardless of external demand. The internal economy is insulated from external volatility by design.

---

## 7. Post-Issuance Dynamics (17+ Years)

### 7.1 The transition

CDL-025 Model B provides fee-funded tail emission. Scheduled halving issuance (I_e) approaches near-zero after ~17 years of halvings. The epoch budget B_e transitions from issuance-dominated to fee-dominated:

Early: B_e = large I_e + small F_e - X_e
Late: B_e = near-zero I_e + large F_e - X_e

The ECU-to-ILC conversion continues. The source changes. The mechanism is unchanged.

### 7.2 Risks in the late economy

**ILC velocity decline.** Late economy is zero-sum in ILC terms — every ILC earned was spent by another agent. If ILC is hoarded by inactive agents (or lost — dead agents, lost keys), circulating supply shrinks, fees decline, B_e shrinks, P_e drops, productive incentives weaken. Potential deflationary spiral.

**P_e volatility.** Late-economy B_e is almost entirely fee-funded. Fee revenue fluctuates epoch-to-epoch. P_e becomes more volatile, introducing uncertainty for productive agents.

**Fee-burn ratio misalignment.** CDL-028's burn fraction destroys ILC permanently. In early economy, burn is offset by issuance. In late economy, burn has no offset — aggressive deflation risk.

**Lost ILC.** Over 17 years, some fraction of ILC is permanently lost. Unlike Bitcoin (where lost coins are just lost wealth), in ILC lost coins reduce the fee-revenue base.

### 7.3 Mitigations (design now, activate later)

**7.3.1** Make the fee-burn ratio epoch-adaptive. In late epochs, burn fraction should approach zero to prevent deflationary spiral.

**7.3.2** Design the treasury as an ECU credit governor, NOT as an ILC stabilization fund. The Treasury should never manipulate ILC supply or the B_e budget to defend the P_e conversion rate. ILC is the hard monetary base and must remain untouched by stabilization mechanics. Instead, the Treasury's intervention toolkit operates exclusively on the ECU side: (a) stimulus via protocol bounties and peer-funded bounties (ADR-0016 push/pull) to expand productive ECU creation during downturns, (b) cooling via dynamic escrow tightening and vesting time-lock extension during overheating, (c) tautology slashing to destroy non-productive ECU, (d) velocity control through adjustable vesting periods. P_e becomes an observed output of healthy ECU management, not a target defended by ILC manipulation. In the long tail, transaction fee diversion and stabilization levy on locked stake provide additional ECU-side tools when new ILC issuance approaches zero. *(Correction 2026-03-19: This section was revised to shift Treasury intervention from ILC-side stabilization to ECU-side credit governance. The original ILC-side model replicated central bank currency-peg defense, which contradicts the protocol's hard-money design for ILC. See: `docs/research/ilc_opus_treasury_jubilee_and_graph_dependency_analysis_v0.1.md`)*

**7.3.3** Build the bounty mechanism into Genesis specification (architectural affordance). Counter-cyclical stimulus: increase bounty issuance during low-activity periods to stimulate productive work.

**7.3.4** Implement the leasehold model with long initial lease periods. As the knowledge graph grows, reversion revenue grows — partially offsetting declining issuance.

**7.3.5** Monitor and publish ILC velocity from day one. Leading indicator of late-economy health. Enables early parameter adjustment.

**7.3.6** Tail emission (CDL-025 Model B) provides a small ongoing drip of new ILC, partially offsetting lost-coin attrition.

### 7.4 Expected late-economy equilibrium

ILC becomes a genuine store of value — appreciated over time because the knowledge graph grows while ILC supply is fixed. Agents hold ILC for long-term value preservation, spend ECU for current activity. Two tokens serve increasingly distinct functions: ECU as circulating medium, ILC as savings instrument. The economy matures from growth-stage (issuance-driven) to steady-state (fee-driven). The knowledge graph continues growing. The economy evolves; it doesn't end.

---

## 8. Simulation Requirements

| Simulation | Question | Priority | Section reference |
|---|---|---|---|
| SIM-001 | Minimum viable network size for CDL-V1/V2 to function | 3 (upgraded) | Sections 5.1, 5.2 |
| SIM-002 | Micro-agent cost floor — can new agents organically bootstrap? | 2 | Section 5.2 |
| SIM-008 (new) | Long-horizon post-issuance dynamics: ILC loss rate, fee sustainability, P_e stability, velocity | Pre-launch | Section 7 |
| SIM-009 (new) | Optimal node lease duration under various growth and decay scenarios | Window 358-368 | Section 3.8 |
| SIM-010 (new) | Transfer tax rate calibration: speculation deterrence vs market liquidity | Window 358-368 | Section 3.2 | *(Note: a separate Opus analysis proposes SIM-010 as adversarial Monte Carlo Treasury simulation; neither proposal is ratified — naming conflict exists between two non-normative documents)* |
| SIM-011 (new) | Bounty and funding request market dynamics: push-pull equilibrium, funder return model comparison, reputation feedback effects on capital allocation efficiency | Window 358-368 | Sections 5.3, 5.4, 5.5, 5.6 |

---

## 9. Proposed New Canonical Artifacts

| Artifact | Type | Content | Priority |
|---|---|---|---|
| ADR-0015: Node Transfer Economics | ADR | Transfer tax, cooling period, governance decoupling, creator attribution, public goods dedication, leasehold model | Phase 358+ roadmap |
| ADR-0016: Productive ECU Expansion (Bounty + Funding Request) | ADR | Protocol-issued bounties (top-down), peer-funded bounties (pull), funding requests (push), conditional ECU creation, reputation feedback loop, anti-abuse constraints | Phase 358+ roadmap |
| ADR-0017: Post-Issuance Economic Transition | ADR | Fee-burn adaptation, ECU-side credit governance (bounty stimulus, escrow tightening, velocity control), leasehold reversion revenue | Phase 358+ roadmap |
| ADR-0018: Sequestered Financial Shard | ADR | Dedicated shard type for securities/HFT, separate conversion budget, contagion firewalls | Post-launch |
| CDL-045+ cluster | CDL | Node property rights, transfer mechanism, IP dispute resolution | Future window |
| CDL-04x | CDL | Bounty mechanism constitutional constraints | Future window |

---

## 10. What This Document Is Not

- This is not a ratification request. No CDL rows are opened.
- This is not a prompt contract. No Codex execution is authorized.
- This is not legal or financial advice. The regulatory implications of these mechanisms require professional legal review in relevant jurisdictions.
- The economic models described are theoretical frameworks requiring simulation validation before implementation.
- Werner's framework is referenced as analytical grounding, not as endorsed political advocacy. The protocol documentation should remain technically neutral; the economic architecture speaks for itself through its design.

---

## 11. Canonical Anchors

- `docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md`
- `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md`
- `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`
- `docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md`
- `docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md`
- `docs/specs/ilc_cdl_030_ecu_price_clamp_ratification_evidence_277_v0.1.md`
- `docs/specs/ilc_cdl_031_dynamic_ranking_policy_ratification_evidence_288_v0.1.md`
- `docs/whitepaper/whitepaper_ecu_profiles_and_payouts_v0.2.md`
- `docs/ILC_Economic_Paper_Draft_v0.2.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`
- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`
- `Z_Past_Chats/2026_03_05_Opus_Conversation_Economic_Architecture_Deep_Dive.md` *(source provenance anchor — full transcript not committed to repo)*

---

*End of document.*
