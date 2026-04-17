# ILC CDL-066 Agent Sender Authorization Ratification Evidence 708 v0.1

Status: ratification evidence artifact
Date: 2026-04-17
Decision vehicle: CDL-066
Phase: 708

`cdl_066_ratified_narrow_sender_authorization_lane`
`sec_001_implementation_closed_before_cdl_066_ratification`
`sender_auth_verification_precedes_quorum_and_execution`
`cdl_066_remains_orthogonal_to_cdl_017_and_cdl_039`
`cdl_066_does_not_broaden_into_generalized_transfer_redesign`

## 1. Evidence basis

CDL-066 ratification rests on three already-established anchors:

- the Phase 694 opening stub that fixed the narrow constitutional question
- the M-series implementation evidence showing SEC-001 is already closed in
  code
- the carry-forward planning state that explicitly separates SEC-001
  implementation closure from later constitutional ratification

This means the question in Phase 708 is not whether sender authorization exists
in code. It is whether the narrow constitutional lane should now be ratified.

## 2. Narrow ratified rule

The ratified rule is narrow:

- fast-path ECU transfers require sender authorization
- sender authorization must be verified before quorum success is accepted
- sender authorization must be verified before certificate execution succeeds
- missing or invalid sender authorization must cause deterministic rejection

This ratification governs the constitutional boundary for who is allowed to
initiate a fast-path transfer. It does not reopen generalized transferability.

## 3. Implementation closure and runtime basis

SEC-001 is already implementation-closed.

Current code and planning state record that:

- `ECUTransfer` carries `sender_sig: AgentSig`
- sender verification happens before quorum in the fast path
- invalid sender authorization causes rejection rather than post-hoc cleanup
- Track B no longer treats CDL-066 as a blocker on M-series execution

Phase 708 therefore ratifies the governing constitutional surface for an
already-implemented invariant.

## 4. Preserved exclusions and orthogonality

CDL-066 remains orthogonal to:

- `CDL-017` validator admission / ejection governance
- `CDL-039` transport invariants and topology privacy
- broader wallet redesign or generalized transfer-auth architecture

It also remains narrow with respect to representation details:

- this ratification does not freeze every future wire-format choice
- this ratification does not reopen the signature-scheme debate unless later
  evidence shows incompatibility with the ratified rule

## 5. Decision-log consequence

Because the narrow sender-authorization rule is now both implemented and
constitutionally justified, the Phase 708 decision-log mutation is:

- `CDL-066` changes from `open` to `ratified`
- its evidence document becomes this artifact
- `CDL-017` and `CDL-067` remain open after this phase
