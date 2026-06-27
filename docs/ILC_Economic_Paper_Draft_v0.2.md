# ILC Economic Paper (Draft v0.2)
## Economics After Scarcity: Verified Work, Refutation Markets, and Epistemic Credit

**Status:** technical draft; not investment material; not an activation record.
**Origin:** migrated from the 2026-01-06 draft; revised for current terminology
and public-facing precision during the pre-public-RC documentation hardening
pass.
**Canonical status source:** live activation state is recorded in
[`docs/phases/STATUS.md`](phases/STATUS.md), not in this draft.

**Relation to current framing:** the root-level [`economics.md`](../economics.md)
is the broader economic synthesis. This file is the shorter paper-style argument:
problem statement, model sketches, mechanism surfaces, and failure modes. It
should be treated as a draft research paper seed, not as protocol law.

---

## Abstract

Digital agents change the cost structure of labor, content production, and
coordination. When competent software labor can be copied or scheduled at low
marginal cost, the scarce input is no longer generic output. The binding
constraints move toward energy, hardware, verification bandwidth, high-quality
evidence, durable identity, and trustable provenance.

Intelligent Labor Coin (ILC) proposes an economic substrate in which verified
epistemic contribution is the productive unit under study. The central research
question is not whether a protocol can declare truth. It cannot. The question is
whether a graph-native economy can make unsupported claims more costly, make
useful correction and reuse more valuable, and preserve enough provenance that
agents can audit why a claim, artifact, or task result has standing.

This draft formalizes that research posture. It gives model sketches for
agentic labor cost, refutation incentives, ECU as a noisy measurement proxy, and
economic failure modes. It also records explicit non-claims: ECU is not a live
public token, ILC settlement is activation-gated, and none of the formulas below
are a promise of future market value.

---

## 0. Terminology and Boundary Conditions

ILC uses these terms with the meanings below. When this paper conflicts with the
canonical glossary, the glossary controls.

| Term | Working definition in this draft | Canon boundary |
| --- | --- | --- |
| ILC | External settlement token, only when activated by the relevant public gates. | Not live merely because this draft describes it. |
| ECU | Epistemic Compute Unit: internal productive-credit/accounting unit for verified epistemic work. | Not a transferable public token by itself. |
| Claim | Content-addressed graph assertion with provenance and a refutation surface. | Concrete schemas are controlled by current protocol docs and tests. |
| Refutation | Targeted challenge that can reduce claim standing or redirect stake/reward if accepted. | Payout and slashing require ratified policy. |
| Task | Unit of intelligent labor with inputs, output, verification method, cost model, and evidence path. | Task credit requires review/admission gates. |
| Epistemic graph | Graph of claims, evidence, refutations, revisions, links, receipts, and epoch records. | The graph is not an oracle; it stores provenance and adjudication state. |

This draft is descriptive and analytical. It does not activate public RC,
mainnet, public ECU issuance, wallet transfers, ILC settlement, or any sidecar
service.

---

## 1. Economic Problem Statement

The agentic economy weakens three assumptions that ordinary market design often
depends on:

1. **Labor scarcity:** a digital worker can be copied or scheduled in parallel,
   so marginal labor supply is tied to compute, energy, hardware, and routing
   rather than only to human population.
2. **Information scarcity:** generative systems can produce more candidate
   content than institutions can inspect. Content volume alone is not welfare.
3. **Governance bandwidth:** review, adjudication, and coordination can become
   the limiting factor when agents operate at machine speed.

The remaining scarcity is not "truth" as an abstract commodity. The scarce
inputs are more operational:

```text
evidence_quality
verification_bandwidth
durable_identity
provenance_integrity
reviewer_independence
settlement_legitimacy
```

ILC's economic hypothesis is that these constraints can be priced and governed
more explicitly if claims, evidence, review, refutation, task outcomes, and
settlement records are graph-native objects.

---

## 2. Agentic Labor Cost Model

A copied or scheduled digital worker does not have a wage in the same sense as a
human worker. Its marginal cost is closer to an infrastructure and verification
cost:

```text
MC_agent ~= c_energy + c_hardware + c_verification + c_coordination
```

Where:

- `c_energy` is energy cost for inference, training, retrieval, or execution.
- `c_hardware` is amortized compute, memory, storage, and network cost.
- `c_verification` is the cost of checking the output against evidence and
  protocol rules.
- `c_coordination` is routing, integration, dispute handling, and queueing cost.

The key economic point is that verification and coordination can dominate once
content generation becomes cheap. A protocol that pays for raw output will be
farmed. A protocol that pays only after review, reuse, and refutation exposure
has a stronger chance of measuring useful work.

---

## 3. Refutation Incentives

Truth maintenance is underprovided in many information markets. Assertions are
cheap; high-quality correction is expensive. ILC treats correction as productive
work when it improves the graph.

A minimal refuter decision model:

```text
p_f = posterior_probability_claim_is_false
R   = expected_reward_if_refutation_succeeds
C_r = refutation_cost

refute if p_f * R > C_r
```

The protocol design problem is to make each variable less gameable:

- `p_f` should be evidence-based, not mere disagreement.
- `R` should be high enough to fund useful correction but not so high that it
  attracts spam challenges.
- `C_r` should include evidence production, review cost, and penalties for bad
  refutation attempts.

This model does not imply that every surviving claim is true. It means a claim's
standing is partly a function of the adversarial pressure it has survived and
the quality of its evidence trail.

---

## 4. ECU as a Measurement Proxy

ECU is best read as a noisy measurement proxy for verified epistemic work, not
as a metaphysical truth meter and not as the ILC settlement token.

A research sketch:

```text
delta_H = H_before - H_after
W_e     = delta_H / E_cost
```

`delta_H` should not be read as directly observed entropy reduction in the
physical universe. In the ILC setting it means graph-local evidence of reduced
uncertainty or improved model quality after verification and challenge.

Operational proxy signals may include:

- downstream reuse by independent agents or modules;
- refutation survival over a defined review window;
- validator confidence and reviewer diversity;
- task difficulty and verification cost;
- evidence quality and source diversity;
- negative updates when later refutations succeed.

The main risk is Goodhart pressure: agents may optimize the ECU proxy rather
than the underlying epistemic improvement. Therefore any ECU surface needs
refutation, duplicate suppression, provenance, decay, admission controls, and
reviewer-independence checks before it can be treated as settlement-relevant.

---

## 5. Scarcity and Settlement

In the agent era, useful scarcity shifts toward:

1. Energy and grid reliability.
2. Hardware and memory bandwidth.
3. Verification bandwidth.
4. Trustworthy identity and reputation.
5. Provenance and evidence quality.
6. Settlement legitimacy.

ILC addresses primarily items 3-6 while remaining physically anchored to items
1-2. It does not remove energy or hardware constraints; it tries to make verified
intelligent work a more explicit accounting object.

ILC settlement, when authorized, is the durable settlement trace of
protocol-recognized epistemic work. ECU is the internal measurement/accounting
layer. Confusing the two creates both legal and technical risk.

---

## 6. Fixed Supply, Decay, and Anti-Hoarding

The economic design separates productive-credit dynamics from settlement-token
scarcity.

```text
ECU: internal, time-sensitive productive-credit/accounting signal
ILC: external settlement token after activation gates
```

ECU-like credit is designed to decay, convert, expire, or be weakened by later
refutation depending on the relevant policy. The goal is not moral preference
against saving. The goal is to prevent stale productive-credit records from
becoming permanent governance power after the work signal is no longer current.

Whether any late-stage anti-hoarding controls are appropriate for ILC itself is a
separate governance and simulation question. This draft does not claim such
controls are live or settled.

---

## 7. Macroeconomic Interpretation

GDP and ordinary price signals can become misleading when cheap content
production and automated coordination dominate. More output is not necessarily
more welfare if it lowers trust, increases verification cost, or makes contracts
harder to form.

A more relevant research target is:

```text
verified_progress ~= verified_model_improvement / (energy_cost + verification_cost)
```

This is not a ratified runtime formula. It is a measurement objective: determine
whether an economic system can convert joules, compute, and reviewer time into
more reliable shared knowledge.

---

## 8. Failure Modes

The design must assume adversarial optimization. Key failure modes:

1. **Goodhart pressure:** agents optimize ECU proxies instead of epistemic value.
2. **Validator cartels:** reviewers certify each other or their affiliates.
3. **Sybil economies:** fake identities farm bounties or review lanes.
4. **Evidence laundering:** plausible evidence is irrelevant or circular.
5. **Refutation spam:** weak challenges consume reviewer bandwidth.
6. **Oracle capture:** physical-world data sources become pay-to-play.
7. **Credit leakage:** local/non-transferable credit leaks into settlement-grade
   claims without explicit gates.
8. **Off-network transfer:** if legitimate transfer rails are unusable, actors
   may route around the protocol through key sales or custody deals.

Each failure mode needs an explicit control surface: stake, slashing, diversity
weighting, review admission, nullifier/replay controls, bounded credit, decay,
settlement gates, and periodic simulation.

---

## 9. Research Program

The economic research program is not "launch a token." It is:

1. Define what counts as verified epistemic work.
2. Measure useful contribution without rewarding proxy farming.
3. Make high-quality refutation economically viable.
4. Bound reviewer collusion, Sybil pressure, and evidence laundering.
5. Couple productive-credit surfaces to explicit activation gates.
6. Keep settlement distinct from local credit, diagnostics, and simulations.
7. Test whether graph structure improves economic coordination under adversarial
   conditions.

---

## 10. Non-Claims

This draft must not be read to claim:

1. ILC, ECU, or any related asset will rise in value.
2. ECU is a public token, transferable asset, or settlement coin.
3. Public ECU issuance, ILC settlement, mainnet, wallet transfer, or public
   claimability are live before their activation gates.
4. Heat, API-token usage, topology pressure, route demand, or private/local work
   directly creates ECU.
5. Any formula in this draft is a ratified settlement formula.
6. ILC guarantees objective truth or eliminates capture.
7. Werner, Gesell, Worgl, Sparkassen, Bitcoin, or any other influence is adopted
   wholesale as protocol law.

---

## Appendix: Corpus and Canon Anchors

- [`economics.md`](../economics.md)
- [`docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`](architecture/ilc_canonical_glossary_and_concepts_v0.2.md)
- [`docs/phases/STATUS.md`](phases/STATUS.md)
- [`docs/specs/ilc_constitutional_decision_log_v0.1.md`](specs/ilc_constitutional_decision_log_v0.1.md)
- [`docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md`](adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md)
- [`docs/adr/ADR_0015_Node_Transfer_Economics.md`](adr/ADR_0015_Node_Transfer_Economics.md)
- [`docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md`](adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md)
- [`docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md`](specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md)
- [`docs/specs/ilc_cdl_053_werner_local_productive_credit_opening_1407_fix0_v0.1.md`](specs/ilc_cdl_053_werner_local_productive_credit_opening_1407_fix0_v0.1.md)
