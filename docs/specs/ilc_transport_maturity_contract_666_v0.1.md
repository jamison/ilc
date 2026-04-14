# ILC Transport Maturity Contract 666 v0.1

Status: row-9 maturity contract
Date: 2026-04-15
Owner lane: G8 transport maturity strike force
Classification: planning contract artifact

## 1. Purpose and row-9 decision rule

This artifact writes the threshold contract for Window 665-670.

Required contract tokens:
- `row_9_target_bounded_public_participant_maturity`
- `row_9_closure_tier_and_stretch_tier_defined`

The row-9 target is:
- bounded public-participant maturity for the current D2d transport posture
- not internet-scale proof
- not dynamic-discovery authorization

Row 9 becomes a legitimate closure candidate only if:
- the closure-tier evidence package is complete
- the closure-tier scenarios pass within the broad timing bands below
- ordinary operator actions remain runbook-grade rather than heroic
- the Phase 670 closure gate passes

## 2. Inherited transport posture

Required contract tokens:
- `static_peer_registry_v1_acceptable_for_row_9`
- `dynamic_discovery_not_required_for_row_9`
- `openclaw_overlay_harness_allowed_not_required_for_transport_correctness`

Inherited posture:
- static peer registry v1 remains acceptable for row 9
- curated bootstrap remains acceptable
- explicit promotion remains required before runtime peer use
- dynamic discovery is not required for row 9
- HTTP/3 over QUIC remains preferred where available
- HTTP/2 fallback remains the approved degraded path where QUIC or UDP is
  blocked
- OpenClaw may support operator or agent overlay checks, but it is not part of
  the base transport-correctness dependency set

## 3. Closure tier

Required contract tokens:
- `five_node_three_machine_minimum`
- `selected_vpn_backed_evidence_required`
- `three_clean_repetitions_plus_one_soak_run`

Closure-tier evidence is the minimum package that may close row 9 honestly.

Closure-tier requirements:
- topology minimum: five nodes across three machines
- required baseline: Tier B three-machine baseline evidence
- required realism: selected Tier C VPN-backed evidence where feasible
- repeatability bar: three clean repetitions plus one soak run
- evidence must cover the required scenario families from Section 5

If the VPNs are unavailable or blocked, the lane must record an honest evidence
gap rather than inflate maturity claims.

## 4. Stretch tier

Stretch-tier evidence improves confidence but does not block row-9 closure
unless it reveals a core failure that invalidates closure-tier claims.

Stretch-tier goals:
- seven or more nodes if resource limits allow
- more complete Tier C VPN-backed coverage
- longer soak periods
- broader operator-rotation or restart-path evidence
- richer artifact capture for reuse by later rows

## 5. Scenario families and evidence schema

Required contract token:
- `row_9_closure_tier_and_stretch_tier_defined`

Required scenario families:
- bootstrap
- steady-state dissemination
- churn
- partition/heal/recovery
- HTTP/2 fallback activation
- restart/rejoin
- bounded push correctness
- pull-only heavy payload correctness

The machine-readable evidence schema for later phases must record at least:
- `scenario_id`
- `topology_tier`
- `run_id`
- `counts_toward`
- `pass`
- `timing_measurements`
- `operator_intervention`
- `notes`

`counts_toward` must be either:
- `closure_tier`
- `stretch_tier`

## 6. Operator burden contract

Required contract token:
- `documented_manual_bootstrap_allowed_but_heroics_forbidden`

Operator-burden categories:

1. Initial curated control-plane setup
- documented manual bootstrap is allowed
- inventory preparation, certificate placement, and approved-peer distribution
  are allowed here

2. Ordinary join, restart, rejoin, and fallback
- must be runbook-grade
- must be repeatable by a disciplined operator
- must not depend on code edits, ad hoc database surgery, or undocumented
  rituals

3. Pathological rescue or heroics
- heroics are forbidden for row-9 closure
- bespoke debugging, live code edits, internal-state patching, or hidden
  operator folklore disqualify normal-operation maturity claims

## 7. Broad timing bands and deferred long-tail work

Required contract token:
- `threshold_bands_broad_not_slo_theater`

Broad timing bands:
- bootstrap: healthy if normally within 120 seconds, degraded if beyond 300
  seconds
- rejoin: healthy if normally within 90 seconds, degraded if beyond 240 seconds
- partition-heal recovery: healthy if normally within 180 seconds, degraded if
  beyond 420 seconds
- fallback activation: healthy if normally within 60 seconds, degraded if
  beyond 180 seconds

These bands are intentionally broad and are not service-level theater.

Deferred long-tail work:
- internet-scale discovery
- autonomous peer-set expansion
- anonymity-overlay ambitions
- deep long-tail performance tuning after closure-tier proof
- non-essential OpenClaw overlay polish

## 8. What this phase does not claim

This phase does not:
- close row 9
- mutate the decision log
- mutate any ADR
- authorize dynamic discovery
- mutate `ilc_core/`
- claim that the VPN-backed evidence already exists

The contract only fixes what later live phases must prove.
