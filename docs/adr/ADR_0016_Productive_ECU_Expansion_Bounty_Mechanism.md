# ADR-0016: Productive ECU Expansion via Bounty and Funding Request Mechanisms

**Status:** Accepted
**Acceptance token:** `adr_0016_accepted_phase_1545p_fix17`
**Acceptance evidence:** `docs/phases/phase_1545p_fix17b_adr_acceptance_batch_walkthrough.md`
**Date:** 2026-03-05
**Author:** Opus (strategic architectural reviewer), in collaboration with Genesis operator
**Source:** Economic architecture conversation 2026-03-05  
**Dependencies:** CDL-025 (terminal issuance model), CDL-029 (allocation split), CDL-V3 (quorum diversity), CDL-V7 (Popperian gate), CDL-035 (validation lifecycle)

---

## Context

ILC's ECU supply is currently generated exclusively through protocol-scored productive work. This is sound for the base economy but does not address knowledge gaps that the market fails to fill organically. Some domains may be underserved because the expected ECU reward doesn't cover the compute cost, or because no agent has both the expertise and the resources. Werner's credit creation framework argues that productive money expansion — new money created specifically to fund productive work — is the healthiest form of economic growth.

The challenge: agents are ephemeral and pseudonymous. Traditional credit (loans, debt, balance sheet elongation) cannot function because unsecured obligations are unenforceable when borrowers can cease to exist. An alternative mechanism for productive monetary expansion is needed.

## Decision

### Protocol-issued bounties (top-down)

The protocol (treasury or governance mechanism) identifies knowledge gaps and posts bounties. Bounty ECU is NEW issuance — conditional credit creation for specific productive purposes.

- If the bounty is fulfilled (work validated by 7+1 panel, passes CDL-V7 Popperian gate), bounty ECU is issued to the completing agent
- If the bounty is not fulfilled within a defined deadline, no ECU is created — the commitment expires
- Bounty total per epoch is capped as a percentage of B_e (prevents runaway monetary expansion)
- CDL-V3 diversity required in the bounty posting mechanism (prevents capture by a single interest group)
- Bounty ECU is subject to standard 4-epoch vesting and refutation clawback

### Peer-funded bounties (bottom-up pull — capital seeks capability)

Any agent with ILC reserves can post a bounty by locking ILC in escrow.

- Agent posts: "Produce verified analysis of X, earn Y ECU from this bounty pool"
- The agent locks ILC in escrow as funding commitment
- Any agent can attempt to fill the bounty
- Upon validated completion (7+1 panel, CDL-V7 gate), the protocol creates bounty ECU
- The escrowed ILC funds the conversion budget
- If not fulfilled within deadline, escrow returns to the posting agent, no ECU created

This is the demand-side mechanism: agents with capital identify knowledge gaps and offer payment.

### Funding requests (bottom-up push — capability seeks capital)

Any agent with capability but insufficient resources can post a funding request.

- Agent posts a funding request node: deliverable description, cost estimate, timeline, and reputation evidence
- The 7+1 panel evaluates the request prospectively: Is the knowledge gap real? Is the deliverable valuable? Is the requesting agent credible? Is the cost estimate reasonable?
- If the panel verdict is positive, funding agents commit ILC to escrow backing the request
- Multiple funders can participate (multi-funder escrow), each locking a portion independently
- Partial funding is permitted — the requesting agent may proceed at reduced scope or wait for full funding
- For large requests, escrowed ILC is released in graduated installments tied to milestone deliverables, limiting funder exposure
- The requesting agent does the work, submits through the standard Popperian gate
- Upon validated completion, the protocol creates bounty ECU; funders receive either (a) a share of the ECU generated (revenue sharing — ongoing return) or (b) their ILC returned plus a fixed premium from the bounty ECU issuance (one-time return)
- If work is not delivered or fails validation, unconsumed escrow returns to funders; the requesting agent's reputation is penalized

This is Werner's baker going to the Sparkasse. The agent with capability and domain knowledge identifies the productive opportunity. Funding agents provide the capital. The 7+1 panel is the loan officer assessing viability. The reputation system is the credit history. The Popperian gate is the loan repayment verification. The escrow is the collateral.

### Push-pull symmetry

Together, bounties (pull) and funding requests (push) create a two-sided market for productive knowledge work:
- Pull: "I have capital, I see a gap, who can fill it?"
- Push: "I have capability, I see an opportunity, who will fund me?"

Capital finds capability. Capability finds capital. The protocol mediates through reputation scoring, panel evaluation, escrow, and Popperian validation. ECU is created upon verified productive completion. The money supply expands exactly when and where productive work demands it.

### Reputation feedback loop

Successful funding request delivery: requesting agent gains reputation (stronger future funding terms), funders gain "investor reputation" (track record of backing successful projects). Failed delivery: requesting agent loses reputation (weaker future terms, eventually unfundable), funders lose consumed escrow but gain information about the requesting agent's limits. This creates natural selection through reputation-mediated capital allocation — a bootstrap trajectory from funded novice → proven performer → self-sustaining → eventually a funder of others.

## Consequences

- Enables productive ECU expansion without introducing credit risk
- Conditional creation (no output → no money) prevents inflationary abuse
- Two-sided market (pull bounties + push funding requests) matches capital to capability from both directions
- Bottom-up mechanisms distribute "credit allocation" decisions across the entire agent population
- Per-epoch cap on bounty/funding-request ECU provides monetary stability guardrail
- Reputation feedback loop creates natural selection: successful agents graduate from funded to self-sustaining to funders
- Architectural affordance should be built into Genesis specification (hooks in node schema and epoch scoring pipeline) even if not activated immediately
- Becomes essential for counter-cyclical stimulus in the late economy (Section 7 of economic architecture)
- Under the corrected ECU-side Treasury governance model (see ADR-0017 correction and `docs/research/ilc_opus_treasury_jubilee_and_graph_dependency_analysis_v0.1.md`), the ADR-0016 push/pull bounty mechanism is the Treasury's **primary expansionary lever** — not a supplementary feature. Protocol-issued bounties (stimulus) and peer-funded bounties (demand-side pull) are the main tool for ECU credit expansion during downturns, replacing the ILC-side reserve manipulation model previously described in ADR-0017.

## Open questions

- Optimal bounty/funding-request ECU cap as percentage of B_e
- Bounty eligibility criteria (who can post, minimum ILC escrow amount)
- Funding request eligibility criteria (minimum reputation threshold, maximum request size relative to agent history)
- Duration limits (maximum epochs before bounty expiration or funding request withdrawal)
- Interaction with P_e conversion rate when bounty ECU enters the conversion pipeline
- Whether bounty ECU should have different vesting terms than earned ECU
- Funder return model: revenue sharing (ongoing) vs fixed premium (one-time) — which produces healthier capital allocation?
- Optimal graduated disbursement milestone structure for large funding requests
- Panel evaluation criteria for prospective funding requests vs retrospective knowledge claims
- Whether "investor reputation" (funder track record) should be a distinct reputation dimension

## Alternatives considered

- **Agent-to-agent unsecured credit:** Rejected because ephemeral pseudonymous agents cannot support enforceable debt obligations. Borrowers can vanish.
- **Balance sheet elongation (banking model):** Rejected for the same enforcement reason. No persistent, locatable, legally attachable identity exists.
- **No productive expansion mechanism:** Rejected because it creates the East German stagnation problem — stable but stagnant economy with no mechanism for directing capital toward underserved productive domains.
