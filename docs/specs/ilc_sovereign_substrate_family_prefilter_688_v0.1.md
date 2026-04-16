# ILC Sovereign Substrate-Family Prefilter 688 v0.1

Status: prefilter and exclusion packet
Date: 2026-04-16
Phase: 688
Owner lane: G8 sovereign-substrate research

`sovereign_substrate_family_prefilter_688_complete`
`external_chain_families_are_inadmissible_bucket_not_comparators`
`live_research_lane_is_sovereign_bft_and_minimal_l1_only`

---

## 1. Purpose and method

This phase applies the closed constitutional gates from rows 6-8 and the
compatibility filter from row 5 to the full candidate family space.

The purpose is disposal, not comparison shopping.

Most families fail quickly. The research time in Phases 689-691 goes only to
families that survive all four filters.

Filters applied in order:
1. Row-6 filter: does this family allow ILC to remain the upstream legitimacy
   source? (CDL-065)
2. Row-8 filter: does this family avoid placing ILC under an external
   constitutional center? (Phase 673/675)
3. Row-7 filter: does this family support strong exitability, replayability,
   and censorship resistance? (Phase 674/675)
4. Row-5 filter: does this family foreclose the near-term tractable privacy
   mechanism families from Phase 680?

A family that fails filter 1 or 2 is out before filters 3 and 4 are applied.

---

## 2. Full candidate family inventory

### 2.1 External public L1s (Ethereum, Solana, Avalanche, Cosmos hub)

**Row-6 result: FAIL**
These chains have their own state machines, governance processes, and canonical
authority structures. Using one as a settlement substrate would make ILC
epoch-state canonical only relative to that chain's own finality rules. The
chain's validator set would be the practical author of ILC settlement finality.
CDL-065 forbids a backend that authors legitimacy. Settlement finality
authored by Ethereum's validator set is not ILC-native legitimacy.

**Row-8 result: FAIL (independently)**
Ethereum Foundation, Solana Foundation, Cosmos Hub governance — each is a
named governance body with de facto veto authority over protocol upgrades,
validator set composition, and chain-level decisions. Each constitutes an
external constitutional center by the Phase 673 definition. The Phase 675 lock
is explicit: no candidate may be treated as compliant merely because it is
popular, performant, or easy to operate.

**Disposition: PRESUMPTIVELY INADMISSIBLE**
These families appear in this register as the reference inadmissible bucket.
Phase 689-691 analysis will not revisit them as live candidates. They may be
cited in Phase 691 exclusion reasoning to sharpen the admissibility argument
for sovereign families.

---

### 2.2 External L2 rollups and delegated-security systems (Optimism, Arbitrum, Polygon zkEVM, StarkNet)

**Row-6 result: FAIL**
Rollups derive finality from their L1 base layer. An Optimism rollup posting
to Ethereum derives settlement finality from Ethereum's validator set. ILC
epoch state would be canonical only relative to Ethereum's finality. Same
CDL-065 failure as the L1 case.

**Row-8 result: FAIL (independently)**
Rollup governance (Optimism Foundation, Arbitrum DAO, Polygon Foundation)
constitutes an external constitutional center. Even if ILC operated its own
rollup, the sequencer set, the fraud/validity proof verifier, and the L1
bridge contracts are all subject to rollup governance authority.

**Row-7 consideration (moot given prior failures):**
Exit from a rollup requires the base L1 to be live and cooperative. Forced
exit paths exist but depend on L1 liveness and censorship resistance — both
outside ILC's control.

**Disposition: PRESUMPTIVELY INADMISSIBLE**
The "external rollup with credible export" conditional from Phase 610 was
already marginal and is now closed in practical terms by row-8 and row-6
locks. No extraordinary showing has been made.

---

### 2.3 Shared sequencer networks and managed settlement services (Espresso, Astria, Radius)

**Row-6 result: FAIL**
Shared sequencer networks impose an ordering layer between ILC and finality.
The sequencer set authors the ordering of ILC epoch records. Ordering is not
neutral — the sequencer that orders ILC state is the practical author of
finality sequence.

**Row-8 result: FAIL (independently)**
Shared sequencer networks are operated by distinct organizations with their
own governance. The sequencer operator is an external constitutional center
by the Phase 673 definition.

**Row-7 result: FAIL (independently)**
If the shared sequencer is the ordinary submission path, censorship by the
sequencer operator constitutes censorship of ILC's public legitimacy surface.
The row-7 lock requires that one operator or dashboard not be the ordinary
path.

**Disposition: PRESUMPTIVELY INADMISSIBLE**

---

### 2.4 Appchain frameworks on external L1 security (Cosmos SDK / ICS, Polkadot parachains, Avalanche subnets)

**Analysis:**
These frameworks offer sovereignty at the application layer while relying on
external security (Cosmos Hub validators via ICS, Polkadot relay chain, etc.)
for finality security.

**Row-8 result: BORDERLINE to FAIL**
Under ICS (Interchain Security), Cosmos Hub validators validate the consumer
chain. Cosmos Hub governance can remove a consumer chain. This places ILC
under Cosmos Hub governance authority — an external constitutional center.
Polkadot parachains similarly inherit relay-chain governance.
Avalanche subnets with primary network validation have a dependency on the
primary network's validator set composition rules.

**Row-6 result: BORDERLINE to FAIL**
If the external validator set determines which epoch records are finalized,
legitimacy authorship is partially delegated to that set.

**Disposition: CONDITIONAL EXCLUSION**
These families are excluded as-used under standard ICS/parachain/subnet
configurations. A fully isolated sovereign instantiation of the Cosmos SDK
(own validator set, no ICS dependency, no relay-chain dependency) is a
different question — that is the minimal sovereign L1 case addressed below.
The framework code may be relevant; the security-delegation model is not.

---

### 2.5 Internal-ledger-final (current Option D posture elevated)

**Row-6 result: PASS** (trivially — there is no external backend)

**Row-8 result: PASS** (trivially — there is no external constitutional center)

**Phase 610 result: REJECTED**
Phase 610 explicitly rejected this path because it collapses bounded current
runtime truth into forever-substrate closure without constitutional
authorization. That rejection stands. This is listed for completeness only.

**Disposition: REJECTED BY PHASE 610 — NOT A LIVE CANDIDATE**

---

### 2.6 Custom minimal sovereign L1 with own BFT validator set

**Row-6 result: PASS**
ILC controls the canonical state machine. The validator set finalizes
already-legitimate protocol state; it does not author it. CDL-065 is
satisfied.

**Row-8 result: PASS**
ILC is the constitutional center. No external governance body holds veto
authority over the validator set, the protocol rules, or the state finality
semantics. The Protocol's own governance (CDL process) governs parameter
changes.

**Row-7 result: CONDITIONAL PASS — proof obligations apply**
Strong exitability and replayability are achievable: the full state history is
anchored on-chain, no external operator can prevent state reconstruction, and
the settlement record is public. Censorship resistance depends on validator
set composition and governance — honest-majority assumptions must be validated.
The row-7 proof obligations from Phase 675 must be satisfied in Phase 691.

**Row-5 result: PASS (conditional)**
A sovereign L1 does not structurally foreclose any of the three near-term
tractable mechanism families from Phase 680. Privacy mechanism compatibility
is substrate-architecture-dependent and must be evaluated per BFT family in
Phase 689. No structural incompatibility is present at the family level.

**Disposition: PRIMARY LIVE CANDIDATE LINE**
This is the effectively sole serious candidate direction. The entire Phase 689
research focus is on the design space within this family — specifically, which
BFT protocol variant, validator-set shape, and implementation approach is most
suited to ILC's settlement-state model.

---

## 3. Summary classification table

| Family | Row-6 | Row-8 | Row-7 | Row-5 | Disposition |
|---|---|---|---|---|---|
| External public L1 (ETH, SOL, AVAX, ATOM) | FAIL | FAIL | — | — | PRESUMPTIVELY INADMISSIBLE |
| External L2 rollup (OP, ARB, MATIC, STARK) | FAIL | FAIL | — | — | PRESUMPTIVELY INADMISSIBLE |
| Shared sequencer / managed settlement | FAIL | FAIL | FAIL | — | PRESUMPTIVELY INADMISSIBLE |
| Appchain with external security (ICS, DOT, AVAX subnet) | BORDERLINE FAIL | BORDERLINE FAIL | — | — | CONDITIONAL EXCLUSION |
| Internal-ledger-final | PASS | PASS | — | — | REJECTED (Phase 610) |
| Custom minimal sovereign L1 / sovereign BFT | PASS | PASS | CONDITIONAL | PASS | **PRIMARY LIVE CANDIDATE** |

---

## 4. Implications for Phase 689

Phase 689 research is bounded to the primary live candidate family.

The comparison work in Phase 689 is not between ILC-native and Ethereum.

It is between BFT protocol families within the sovereign design space:
- PBFT-lineage variants
- Tendermint / CometBFT (extractable from Cosmos SDK without ICS)
- HotStuff / Jolteon / Fast HotStuff
- Narwhal-Bullshark (DAG-based mempool + BFT ordering)
- Snowball / Avalanche-native (probabilistic — flagged for row-7 scrutiny)

The evaluation criteria for Phase 689 are constitutional admissibility first,
then finality semantics, then censorship resistance, then operability and
tractability. Performance is a tiebreaker inside the surviving set only.

---

## 5. What this phase does not decide

This phase does not decide:
- which BFT family wins
- what the validator set size or composition is
- what the implementation language or framework is
- whether any appchain SDK code is reused (the code may be useful even if the
  security model is inadmissible)
- final row-5 mechanism closure
