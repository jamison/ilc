# ILC CDL-066 Agent Sender Authorization Opening Stub 694 v0.1

Status: opening stub
Date: 2026-04-16
Decision vehicle: CDL-066
Phase: 694
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

## 1. Lane identity

`cdl_066_governs_agent_sender_authorization_for_ecu_fast_path_transfers`
`sec_001_agent_sender_auth_cdl_066_required_before_m009`

CDL-066 opens in Phase 694 as the numbered constitutional lane for agent
sender authorization on ECU fast-path transfers.

Earlier planning text named this lane `CDL-063`, but `CDL-063`, `CDL-064`,
and `CDL-065` are already occupied in the constitutional decision log.
The correct vehicle for SEC-001 is therefore `CDL-066`.

## 2. Problem statement

Track B security review identified SEC-001:
- `ECUTransfer` carries no sender authorization surface
- validators can approve a structurally valid transfer without any proof that
  the sending agent authorized it
- a multi-machine testnet that accepts unsigned sender intent is not a safe
  test environment

This problem is constitutional in scope because the protocol needs a narrow,
durable boundary for who is authorized to initiate a fast-path ECU transfer.

## 3. Opening scope

CDL-066 opens the narrow authorization lane only.

In scope:
- authorizing a sender-authorization field on `ECUTransfer`
- requiring sender verification before validator quorum check or certificate
  execution succeeds
- requiring deterministic rejection of missing or invalid sender
  authorization
- defining the compatibility boundary with CDL-042 agent-key derivation

Out of scope:
- final signature-scheme selection
- final sender-signature wire format
- transport-level redesign
- validator admission / ejection governance
- generalized ECU transferability beyond the fast-path surface at issue

## 4. Inherited interactions and exclusions

### 4.1 CDL-042 interaction

Sender verification under CDL-066 must be consistent with the CDL-042
identity model:
- globally flat namespace
- key-derived `agent_id`

CDL-066 may require compatibility with that model, but it does not reopen or
replace the CDL-042 identity boundary.

### 4.2 CDL-039 interaction

CDL-066 does not reopen CDL-039 transport invariants.

The authorization question is:
- who is allowed to initiate a transfer,

not:
- how transport topology, relay privacy, or channel invariants are governed.

### 4.3 CDL-017 interaction

CDL-066 is orthogonal to CDL-017.

- CDL-017 governs validator-set admission and ejection
- CDL-066 governs sender authorization for transfer initiation

Opening CDL-066 must not be silently blocked by CDL-017 timing.

## 5. Candidate opening rule set

The candidate rule set opened here is:
- fast-path ECU transfers require sender authorization
- sender authorization must be verified before quorum success is accepted
- missing or invalid sender authorization must cause deterministic rejection
- the authorization check must bind to the sending agent's CDL-042-compatible
  key material

This opening deliberately leaves undecided:
- whether the sender signature is BLS, Ed25519, or another compatible scheme
- the exact serialized field layout
- the final domain-separation encoding

Those are ratification and implementation questions, not opening-scope facts.

## 6. Evidence anchors

Required anchors:
- `docs/specs/ilc_phase_694_700_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_694_700_track_a_candidate_phase_grouping_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md`

## 7. Forward obligations

Before M-009 approval:
- CDL-066 must be open
- Track B must wire sender verification into the fast-path execution path
- the hard gate token
  `sec_001_agent_sender_auth_cdl_066_required_before_m009`
  must remain visible in planning and handoff artifacts

Later phases must still provide:
- prelock hardening / ratification vehicle
- final signature and field-format decision
- runtime evidence that unsigned transfers are rejected
