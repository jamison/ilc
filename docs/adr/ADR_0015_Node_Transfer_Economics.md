# ADR-0015: Node Transfer Economics and Knowledge Property Rights

**Status:** Proposed  
**Date:** 2026-03-05  
**Author:** Opus (strategic architectural reviewer), in collaboration with Genesis operator (project lead)  
**Source:** Economic architecture conversation 2026-03-05  
**Dependencies:** CDL-034 (three-envelope node schema), CDL-035 (validation lifecycle), CDL-V1 (temporal decay), CDL-V7 (Popperian gate), CDL-029 (allocation split)

---

## Context

Nodes in the ILC epistemic graph generate ongoing ECU value through the reuse component of the scoring formula (35% weight under BAL profile). This makes high-value nodes income-producing assets. Without a node transfer framework, the market will route around any restriction by trading agent identities off-protocol — selling signing keys, reputation, and accumulated node portfolios as going concerns. This produces identical economic outcomes to node trading but invisible to the protocol and therefore unregulatable. It is preferable to allow node transfers within protocol-visible, taxable, regulatable mechanisms.

## Decision

Node ownership transfers are permitted under the following constraints:

### Transfer tax (progressive, time-sensitive)

- Tax is denominated in ILC and paid at transfer time
- Progressive by transfer count: increasing rate for nodes that have been transferred more frequently
- Time-sensitive (Tobin-adapted): higher rate for transfers occurring within N epochs of the previous transfer
- Tax rate adjusts with overall transfer volume (governance parameter, autopilot-eligible)
- Revenue flows to the treasury for bootstrap grants and productive network growth

### Cooling period

- Post-transfer, the node's reuse ECU generation is suspended or reduced for N epochs
- New owner must demonstrate productive engagement before full income resumes
- Cooling period doubles as a refutation opportunity window — the node is explicitly challengeable during cooling

### Creator attribution permanence

- CDL-034's authored payload envelope (containing creator identity and signature) is immutable
- Transfer moves income rights only, never attribution
- Full provenance chain (creation, all transfers, tax paid at each step) is content-addressed and auditable

### Governance decoupling

- Node portfolio size does not translate into protocol governance influence
- Consistent with CDL-013 (governance-weight decay) and ADM-003 Phase 354 (L-tiers = epistemic tiers)
- Principle: economic returns scale with contribution; governance does not scale with economic returns

### Public goods dedication

- Agents may irrevocably dedicate a node's income rights to the commons (treasury or public goods fund)
- Attribution remains permanent. Dedication is transfer-tax-exempt.
- Irrevocable EXCEPT when a validated IP dispute (via `ilc contradict` and 7+1 panel evaluation) overturns original attribution, in which case income rights transfer to the validated true owner

### Leasehold model (proposed — requires simulation)

- Node income rights have a constitutional lifespan (specific duration to be determined by simulation)
- After expiration, income reverts to the commons
- Lease resets on transfer (buyer gets a fresh lease period)
- Generates growing reversion revenue stream that partially offsets declining ILC issuance in late economy

## Consequences

- Prevents off-protocol agent-identity trading market from forming
- Generates treasury revenue proportional to market activity (hot markets fund more bootstrap grants)
- Progressive tax specifically targets speculative chains while preserving legitimate transfers
- Cooling period maintains knowledge quality by creating refutation windows at ownership transitions
- Governance decoupling prevents economic concentration from becoming governance concentration
- Public goods dedication creates a growing corpus of freely available knowledge

## Open questions for simulation

- Optimal transfer tax rates (SIM-010)
- Optimal cooling period duration
- Optimal lease duration (SIM-009)
- Interaction between transfer tax revenue and bootstrap grant funding levels

## Alternatives considered

- **No transfers allowed:** Rejected because the market routes around via agent-identity trading, producing identical outcomes outside protocol visibility.
- **Unrestricted transfers (no tax):** Rejected because it enables speculative node flipping and concentration.
- **Cap on node portfolio size:** Rejected because it infringes on productive property rights. Economic returns should scale with contribution without artificial caps.
