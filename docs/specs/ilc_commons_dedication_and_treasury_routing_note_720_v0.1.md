# ILC Commons Dedication And Treasury Routing Note 720 v0.1

**Phase:** 720  
**Window:** 717-722  
**Date:** 2026-04-18  
**Author:** Codex

## 1. Baseline

ADR-0015 and the economic architecture both preserve a commons-dedication path
for node income rights. This phase does not reopen `CDL-047`; it states how
commons dedication fits inside the already ratified treasury-governance lane.

## 2. Dedication mechanics

Commons dedication is a voluntary dedication of income rights to the commons.
It does not move creator attribution. `dedication_does_not_move_creator_attribution`

The dedication mechanism remains irrevocable at the ordinary protocol level and
stays transfer-tax-exempt as documented in the economic architecture.

## 3. Treasury and public-goods routing boundary

Commons dedication must route through the existing `CDL-047` treasury
governance framework rather than creating a free-form sink. `commons_routing_must_layer_on_cdl_047`

The allowed routing boundary is:

- treasury as the default constitutional sink,
- public-goods routing only as a bounded layer inside the same treasury-
  governance framework,
- no silent bypass around `CDL-047`,
- no fixed constitutional commons fraction created in this phase.

## 4. Exception path

The validated IP-dispute exception path remains the only ordinary reversal of
irrevocable dedication. If `ilc contradict` plus the 7+1 evaluation process
overturns original attribution, income rights transfer to the validated true
owner while creator attribution is corrected through the existing authorship
path.

`commons_dedication_irrevocable_except_validated_ip_dispute`

## 5. Launch-bound versus deferred posture

Voluntary commons dedication under the bounded `CDL-047` routing lane is
`launch_bound`.

Any protocol-imposed commons take-rate, fixed dedication fraction, or expanded
routing taxonomy remains deferred.
