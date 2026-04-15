# ILC Transport Open Questions and Historical Recovery 665 v0.1

Status: historical planning recovery artifact for the closed row-9 lane
Date: 2026-04-15
Owner lane: G8 transport maturity strike force
Classification: authority-ordered recovery register

Audit note, 2026-04-15:
- Window `665-670` is closed
- this artifact remains a durable record of how row-9 transport questions were
  authority-classified during that lane
- it should be cited as historical recovery for the closed row-9 window, not as
  a live planning artifact for `687-692`

## 1. Purpose and authority order

This artifact exists to prevent Window 665-670 from re-arguing transport
questions from memory.

Required recovery token:
- `row_9_open_questions_classified_by_authority_not_by_memory`

Authority order in this lane:
1. ratified ADR/CDL and runtime contracts
2. phase handoffs and checklist-state artifacts
3. session historization and recovery notes
4. fresh sim/live evidence
5. only then unresolved human judgment

## 2. Questions already settled by canon

Settled by canon:
- `static_peer_registry_v1_remains_row_9_baseline`
- `github_bootstrap_and_explicit_promotion_preserved`

Already settled answers:
- static peer registry v1 remains the active row-9 discovery posture
- curated bootstrap is allowed, but it is not active-peer admission by itself
- explicit promotion remains required before runtime peer use
- preferred binding is HTTP/3 over QUIC with HTTP/2 fallback where blocked
- heavy canon/graph payloads remain pull-only and receiver-controlled
- bounded metadata/topology PUSH remains acceptable under the current doctrine

## 3. Questions directionally settled but not operationalized

Directionally settled but not yet operationalized:
- `openclaw_sidecar_investigation_allowed_not_required`

These questions are directionally settled but not yet operationalized.

These are not open design questions, but they still need concrete machinery:
- how to package closure-tier versus stretch-tier evidence in a stable format
- how to verify live VPN/port posture in a fail-closed way
- how to use OpenClaw as an overlay harness without making it a base
  dependency
- how to make transport evidence reusable for later rows rather than a one-off
  report

## 4. Questions that require sim or live drills

Require sim or live drills:
- `vpn_port_matrix_needed_before_live_claims`

These cannot be answered by prose alone:
- whether the current three-machine testbed plus VPN posture actually supports
  closure-tier row-9 evidence
- whether HTTP/2 fallback activates and recovers correctly under constrained
  conditions
- whether partition/heal and restart/rejoin behavior remains runbook-grade
- whether bounded PUSH and pull-only heavy-payload discipline is observable in
  practice

## 5. Questions that require human decision

Require human decision:
- whether the available live infra is good enough to attempt VPN-backed closure
  claims now
- whether any firewall or port changes should be authorized on the remote hosts
- whether stretch-tier evidence beyond the minimum closure-tier package is
  worth the live cost in this window

## 6. Immediate easy wins for later lanes

Required recovery token:
- `transport_evidence_infrastructure_should_be_reusable_beyond_row_9`

Immediate easy wins:
1. define a stable scenario catalog so rows 7 and 8 can reuse transport
   evidence rather than restating it
2. define a stable metrics schema so future drills compare like with like
3. keep the remote/topology posture machine-readable so later RC and launch
   lanes inherit the same evidence infrastructure
4. preserve the OpenClaw overlay boundary so later app/agent-operability work
   does not contaminate base transport correctness

Explicit carry-forward answers:
- dynamic discovery remains deferred
- the two external VPNs are available, but their firewall/port posture is an early gating question
- OpenClaw remains an overlay harness for internal RC testing rather than the
  base correctness layer
- stronger adaptive-gossip / partition-repair doctrine is a later carry-forward
  lane, not part of row-9 closure, and now routes through
  `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
