# CDL-102 Inviter-Chaining Economics Opening 1573ad v0.1

Status: open
Date: 2026-07-10
Phase: 1573ad
Decision ID: CDL-102
Opening token: `cdl_102_inviter_chaining_economics_opened_phase_1573ad`

## 1. Scope

CDL-102 opens the constitutional lane for inviter-chaining economics: economic credit to inviters when invited agents complete work on the graph.

The attribution chain under deliberation is:

```text
InviteBatchRecord.inviter_cid
  -> InviteRedemptionRecord.inviter_cid
  -> redeemed agent identity / attributed work
  -> possible inviter credit rule
```

The Phase 1573z invite runtime provides the local/default-off record substrate for `InviteBatchRecord` and `InviteRedemptionRecord`. CDL-102 does not activate that substrate for production economic credit.

## 2. CDL-091 Disambiguation

CDL-091 is already ratified as Jury Incentive Economics from Phase 1400. CDL-091 is not the inviter-chaining economics CDL and must not be reused for inviter-chaining.

Older planning language that described inviter-chaining as a “CDL-091 successor” is interpreted as historical shorthand for a later, separate CDL surface. The separate surface opened by this phase is CDL-102.

## 3. Open Questions

Q1: What fraction of an invited agent's initial ECU earnings routes to the inviter?

Q2: Does inviter credit decay with invite depth, distinguishing direct invitees from second-generation or deeper invitees?

Q3: Does Genesis receive inviter credit for directly invited agents, or is Genesis' invite-service contribution covered by the fixed Genesis tranche?

Q4: How many epochs does inviter attribution persist before expiry?

Q5: What fraud, duplicate-redemption, clawback, or withheld-reward review path applies when invitation provenance is valid but the invited agent's work is later rejected?

Q6: Which evidence is required before ratification: local rehearsal evidence, 3-VPS / 7-agent evidence, or post-public-RC live network evidence?

## 4. Carry-Forward Dependencies

- ADR-0038 provenance edge semantics are required for inviter-chain attribution.
- ADR-0041 Agent INIT semantics are required for binding invite redemption to a new agent identity.
- CDL-042 flat agent namespace means the economic rule must bind to explicit provenance records rather than assuming agent IDs alone are sufficient.
- ADR-0009 bundle and snapshot serving evidence remains relevant where inviter-chain credit covers protocol-native bootstrap service rather than ordinary referral.
- Phase 1573z `InviteBatchRecord` and `InviteRedemptionRecord` are implementation evidence, not activation authority.

## 5. Non-Claims

This CDL opening does not:

- activate inviter credit;
- ratify any inviter-credit percentage;
- ratify invite-depth decay;
- ratify Genesis inviter-credit treatment;
- ratify an attribution expiry period;
- modify CDL-029 allocation fractions;
- modify CDL-091 Jury Incentive Economics;
- activate production invite distribution;
- write wallet state, treasury state, settlement state, or production graph state;
- mint ECU or settle ILC;
- authorize public RC, public serving, public P2P, or Genesis signing.

## 6. Future Ratification Boundary

Ratification is deferred. Any future ratification must resolve the open questions above, preserve CDL-091 separation, and carry explicit non-activation or activation language. If activation is proposed, it must include separate runtime authority, tests, and economic safety evidence.
