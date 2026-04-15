# ILC Exitability and Replayability Threshold 674 v0.1

Status: threshold artifact
Date: 2026-04-15
Phase: 674
Owner lane: G8 censorship-resistance and independence strike force

## 1. Purpose and threshold target

Phase 674 fixes the minimum row-7 exitability and replayability bar that later
substrate candidates must satisfy before they can claim row-7 compliance.

`strong_exitability_requires_export_verify_replay_and_migrate_without_operator_consent`
`row_7_future_substrate_proof_obligations_are_hard_gate`

## 2. Strong exitability definition

The strong bar requires all of the following:
- export of legitimacy-relevant state
- independent verification of exported state and receipts
- replay of legitimacy-relevant history from portable data
- migration without privileged original-operator consent

The relevant state includes, at minimum:
- admission and activation lineage
- namespace and handle authority lineage
- quorum or evaluation eligibility lineage
- settlement-linked public legitimacy receipts
- reputation continuity material needed to preserve canonical history

## 3. Minimum proof obligations

Later substrate candidates must demonstrate:

1. **Exportability**
   - legitimacy-relevant state can be exported in machine-legible form
   - export is not trapped behind one dashboard or one provider shell

2. **Verifiability**
   - exported state can be checked against receipts, hashes, or protocol
     lineage without trusting the original operator

3. **Replayability**
   - a participant or successor environment can reconstruct legitimacy-relevant
     history from exported or public data
   - replay does not depend on one hosted API staying alive

4. **Migratability**
   - participants can move to a successor environment or alternative operator
     path without needing privileged approval from the original operator

5. **Continuity preservation**
   - admission, namespace, quorum, settlement, and reputation continuity do not
     disappear merely because the original provider path disappears

## 4. Failure cases that do not satisfy row 7

`read_only_observation_is_insufficient_for_row_7`
`state_export_without_replayability_is_insufficient_for_row_7`
`privileged_original_operator_consent_may_not_be_required_for_exit`

The following do not satisfy the threshold:
- users can read balances but cannot export legitimacy-relevant state
- users can export state but cannot verify or replay it
- users can verify state but cannot migrate without operator permission
- users can migrate only through one hosted dashboard or provider shell
- users can observe a chain or portal but cannot preserve protocol continuity

## 5. Evidence forms for later substrate candidates

Later substrate candidates should prove compliance through a combination of:
- architecture-level state/export mapping
- proof and receipt lineage description
- migration / replay scenario drills
- operator-agnostic walkthrough or reference implementation evidence

This lane does not require that evidence now. It requires that the proof burden
be explicit now.

## 6. Enforcement posture

The threshold fixed here is a hard admissibility gate:
- later substrate candidates may not claim row-7 compliance without satisfying
  these obligations
- later substrate lanes may not soften this threshold by convenience argument
  alone
- if a candidate cannot satisfy export, verification, replay, and migration, it
  remains non-compliant regardless of branding or throughput

## 7. What this artifact does not claim

This artifact does not claim:
- any current substrate candidate has already passed the threshold
- row 7 runtime proof is complete in Phase 674
- row 8 is decided here
- `CDL-062` is opened here
