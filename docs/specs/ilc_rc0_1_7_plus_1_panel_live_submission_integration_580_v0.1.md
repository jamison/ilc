# ILC RC0.1 7+1 Panel and Live Submission Integration 580 v0.1

Status: locked
Date: 2026-04-03
Phase: 580
Owner lane: G8 implementation cluster

## 1. Bounded RC target

Phase 580 hardens the already-landed live submission and bounded 7+1 panel path
into one authoritative runtime integration surface for the RC0.1 curated
testnet.

Required governance tokens:
- `phase_580_panel_submission_path_authoritative`
- `phase_580_replay_agreement_required`
- `phase_580_outsider_review_only_boundary`
- `phase_580_panel_claim_alignment_required`
- `phase_580_broadcasts_must_reflect_live_artifacts`
- `phase_580_keeps_576_577_578_semantics_unchanged`

This packet does not introduce new settlement, wallet, graph, or lineage
meaning. It proves the live panel/submission path conforms to the already
locked semantic boundaries.

## 2. Authoritative runtime surfaces

The authoritative Phase 580 runtime surfaces are:
- `tools/agent_loop_v1.py`
- `tools/testbed/run_three_node_seven_agent_scenario.py`
- `tools/testbed/replay_three_node_seven_agent_scenario.py`
- `tools/testbed/check_phase_580_panel_live_submission_integration.py`
- `tools/testbed/run_phase_580_panel_live_submission_integration.py`

The authoritative artifact set for the integration check is:
- seven live submission artifacts
- one outsider review artifact
- one live panel artifact with embedded claim batch
- one standalone claim artifact
- one replay manifest with replay result
- live panel and claim broadcast artifacts
- one machine-legible Phase 580 integration manifest

## 3. Deterministic integration contract

`phase_580_panel_submission_path_authoritative`.

A passing Phase 580 integration requires all of the following:
- the Phase 579 cutover manifest exists and remains valid for the same scenario
  root
- exactly seven canonical submission artifacts feed the panel path
- exactly one outsider review artifact feeds the 7+1 panel path
- the panel vote set aligns with the seven canonical submission identities plus
  the outsider review identity
- the direct author selected by the panel is one of the canonical submissions,
  not the outsider reviewer
- the standalone claim artifact matches the panel-embedded claim batch
- the outsider reviewer remains review-only and does not receive a passive claim
- replay over the saved live artifacts produces `agent_loop_replay_ok`
- replay agrees with the saved panel and claim artifacts without drift
- broadcast artifacts point to the live panel and claim files and all broadcast
  statuses are `202`

`phase_580_replay_agreement_required`.

`phase_580_panel_claim_alignment_required`.

`phase_580_broadcasts_must_reflect_live_artifacts`.

## 4. Outsider boundary and live broadcast rule

`phase_580_outsider_review_only_boundary`.

The outsider reviewer exists only to satisfy the bounded 7+1 review path. The
outsider reviewer must remain outside the rewarded passive-recipient set.

The outsider review artifact must:
- remain `variant = outsider`
- remain review-only rather than submission-authoritative
- align with the outsider vote row in the panel result
- not widen the curated lineage or rewarded submission set

Live panel and claim broadcasts must remain broadcasts of the saved live runtime
artifacts rather than synthetic helper payloads.

## 5. Carry-forward into Phase 581

Phase 580 is complete when live submission, panel, replay, and broadcast
surfaces are deterministically aligned.

This packet does not by itself authorize:
- wallet write authority
- public claimability
- spend, transfer, or withdrawal semantics
- new persisted-graph roles beyond the Phase 577 minimum contract
- lineage widening beyond the Phase 578 curated boundary

`phase_580_keeps_576_577_578_semantics_unchanged`.
