# ILC Node Transfer Economics And Cooling Period Governance Package 719 v0.1

**Phase:** 719  
**Window:** 717-722  
**Date:** 2026-04-18  
**Author:** Codex

## 1. Baseline

ADR-0015 already establishes why protocol-visible transfer economics exist at
all: if node transfers are banned in-protocol, the market routes around the
rule through agent-identity sales and invisible portfolio conveyance. That
would preserve the economic reality of transfer while removing taxation,
auditing, and anti-speculation guardrails from protocol view.

Off-protocol transfer evasion is unacceptable because it recreates node trading
outside protocol visibility, taxation, and audit.

This phase therefore packages the transfer-tax and cooling-period mechanisms as
the visible-transfer baseline for the ADR-0015 family.

## 2. Transfer-tax structure

The preserved transfer-tax structure is:

- transfer remains protocol-visible rather than informally hidden,
- tax is charged at transfer time,
- tax is progressive by transfer count,
- tax is time-sensitive so rapid flipping is disfavored,
- tax revenue remains a treasury-routed economic input rather than private
  bypass.

The phase does not freeze a numeric rate or a fixed schedule. It locks the
structure and anti-speculation purpose only.

`visible_taxed_transfer_principle_preserved`
`numeric_tax_and_cooling_constants_not_constitutionalized_here`

## 3. Cooling-period duration class

Cooling period is expressed in epochs, not issuance cycles and not wall-clock
time.

Epochs are the right duration class because the protocol already measures
economic and validation time in epoch law. A post-transfer cooling window tied
to epochs preserves challengeability, aligns with the ECU-time architecture,
and avoids wall-clock ambiguity.

The phase locks the duration class, not the exact count. Cooling remains an
anti-speculation and refutation-window mechanism whose final numeric duration
still depends on evidence.

`cooling_period_duration_class_selected`

## 4. Launch-bound versus deferred posture

Transfer tax is `launch_bound` at the principle-and-structure level.

Cooling period is `launch_bound` at the duration-class level because the node
transfer lane is not honest without an explicit anti-flipping and challenge
window.

numeric tax brackets, exact cooling duration, and any adaptive calibration
curve remain deferred to later evidence and simulation rather than being
constitutionalized here.

## 5. Preserved invariants and non-goals

Creator attribution remains permanent and is not transferred by sale, lease, or
portfolio movement. `creator_attribution_not_transferred`

Node portfolio size does not become protocol governance influence.
`governance_influence_not_purchased`

This phase does not:

- mutate the constitutional decision log,
- ratify a new CDL,
- define commons-dedication routing in final detail,
- activate leasehold / reversion,
- mutate `ilc_core/` or `ilc_consensus/`.
