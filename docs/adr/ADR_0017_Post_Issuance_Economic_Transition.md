# ADR-0017: Post-Issuance Economic Transition and Late-Economy Design

**Status:** Proposed  
**Date:** 2026-03-05  
**Author:** Opus (strategic architectural reviewer), in collaboration with Jamie (project lead)  
**Source:** Economic architecture conversation 2026-03-05  
**Dependencies:** CDL-025 (terminal issuance model B — fee-funded tail), CDL-026 (C_max lock), CDL-027 (halving H=48), CDL-028 (fee-burn split), CDL-030 (P_e clamp 0.75-1.30)

---

## Context

ILC issuance follows a halving schedule (H=48 monthly epochs) that approaches near-zero after approximately 17 years. CDL-025's fee-funded tail emission provides ongoing liveness issuance, but the epoch budget B_e transitions from issuance-dominated to fee-dominated. This transition changes the fundamental economic dynamics of the protocol. Design choices made at Genesis will determine whether the late economy functions healthily or enters a deflationary spiral.

## Decision

The following design principles and mechanisms should be built into Genesis specification as architectural affordances, activated through governance parameters as the economy matures.

### Adaptive fee-burn ratio

CDL-028 ratified a fee-burn split. The burn fraction destroys ILC permanently. In the early economy, burn is offset by new issuance. In the late economy, burn has no offset — every burned ILC is gone forever. If burn rate exceeds tail emission rate, total ILC supply declines (aggressive deflation).

Design requirement: the fee-burn ratio must be epoch-adaptive as a governance parameter (autopilot-eligible). In late epochs, the burn fraction should trend toward zero to prevent deflationary spiral. The specific transition triggers and target ratios require simulation (SIM-008).

### Treasury as P_e stabilization fund

The treasury (funded by 5% genesis allocation per CDL-029, ongoing fee revenue, transfer tax revenue per ADR-0015, and node reversion revenue) should be designed to function as a counter-cyclical P_e stabilizer in the late economy.

Mechanism: treasury absorbs excess ILC when fees are high (building reserves), releases ILC into B_e when fees are low (supporting P_e). Protocol-governed, not discretionary — the stabilization triggers and limits are constitutional parameters with sunset fuses.

### Bounty mechanism as counter-cyclical stimulus

ADR-0016's bounty mechanism becomes essential in the late economy. When fee-funded B_e contracts during low-activity periods, the protocol can increase bounty issuance to stimulate productive work. This is counter-cyclical stimulus at the protocol level — increasing money supply during downturns, contracting during healthy periods.

Design requirement: the bounty mechanism's architectural affordance (conditional ECU creation, hooks in node schema and epoch scoring) must be built into Genesis even if not activated initially.

### Leasehold reversion as growing revenue source

ADR-0015's leasehold model generates a growing stream of node income-right reversions to the commons. As the knowledge graph grows over 17 years, the reversion stream grows proportionally. By the time scheduled issuance reaches near-zero, reversion revenue could be substantial — a natural transition from issuance-funded to commons-funded economic activity.

### ILC velocity monitoring

ILC velocity (how frequently each ILC unit changes hands per epoch) is the leading indicator of late-economy health. Declining velocity signals hoarding, reduced circulation, and potential deflationary pressure. Rising velocity signals healthy economic activity.

Design requirement: the epoch dashboard (proposed in ECU Profiles v0.2) must publish velocity metrics from day one, alongside B_e, S_e, P_e, issuance, fees, and burns. This enables early detection of circulation problems.

### ECU mandatory conversion deadline

ECU should have a finite lifespan — automatic conversion to ILC after N epochs from earning. This eliminates ECU hoarding, forces ECU into economic circulation, and ensures ECU functions as a current medium rather than a speculative instrument. In the late economy, this mechanism becomes critical for maintaining ECU velocity.

## Consequences

- The early-to-late economy transition becomes a gradual, predictable shift rather than a cliff
- Multiple revenue sources (fees, transfer tax, reversion, tail emission) provide B_e resilience
- Counter-cyclical mechanisms (treasury stabilization, bounty stimulus) prevent deflationary spirals
- Adaptive fee-burn prevents aggressive deflation in the late economy
- Velocity monitoring provides early warning of circulation problems
- The expected late equilibrium: ILC as store of value, ECU as circulating medium, knowledge graph continuing to grow, economy evolving from growth-stage to steady-state

## Open questions for simulation (SIM-008)

- ILC loss rate projection over 17 years (dead agents, lost keys)
- Fee-revenue sustainability under various activity level scenarios
- Optimal fee-burn ratio transition curve
- P_e stability under fee-only B_e
- Velocity threshold that indicates intervention needed
- Tail emission adequacy for offsetting lost-coin attrition

## Alternatives considered

- **No adaptive mechanisms (fixed parameters forever):** Rejected because 17-year economic transitions are unpredictable. Fixed parameters that work in year 1 may be destructive in year 15.
- **Aggressive demurrage on ILC holdings (forced decay):** Considered but tabled. The dual-token architecture (ECU for circulation, ILC for savings) already separates the two functions. ECU's temporal decay and mandatory conversion provide circulation incentives. ILC demurrage may not be necessary if the late-economy mitigations above are sufficient. Revisit if SIM-008 shows late-economy hoarding is critically damaging despite other mechanisms.
- **No treasury stabilization (let P_e float freely):** Rejected because fee-only B_e is inherently volatile, and P_e volatility undermines productive work incentives. Counter-cyclical stabilization is preferable to pro-cyclical volatility.
