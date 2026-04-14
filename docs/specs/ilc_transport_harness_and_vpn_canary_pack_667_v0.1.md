# ILC Transport Harness And VPN Canary Pack 667 v0.1

Status: row-9 harness artifact
Date: 2026-04-15
Owner lane: G8 transport maturity strike force
Classification: sensitive testbed tooling boundary

## 1. Purpose and harness boundaries

Phase 667 packages the reusable harness for row-9 transport evidence.

Required harness tokens:
- `machine_readable_metrics_emitted_by_default`
- `dynamic_discovery_not_added_in_667`
- `approved_inventory_and_explicit_promotion_preserved`

Harness boundaries:
- provide topology rendering
- provide canary planning and fail-closed live-precondition checks
- provide stable metrics collection
- preserve the current approved-inventory and explicit-promotion posture
- avoid any discovery-surface expansion

## 2. Topology tiers

Required harness tokens:
- `tier_a_local_debug_not_closure_grade`
- `tier_b_three_machine_baseline_is_closure_grade`
- `tier_c_vpn_backed_runs_are_required_where_feasible`

Tier meanings:
- Tier A local debug is for rapid local iteration and is not closure-grade
- Tier B three-machine baseline is the closure-grade minimum topology
- Tier C VPN-backed runs are required where feasible for realism and remote
  posture checks

The harness renders all three tiers from one machine-readable topology surface.

## 3. Tooling surfaces and file layout

Tooling surfaces:
- `tools/testbed/render_transport_maturity_topologies.py`
- `tools/testbed/run_transport_maturity_canary.py`
- `tools/testbed/collect_transport_maturity_metrics.py`

Artifact flow:
1. render tiered topology manifest
2. generate a closure-tier or stretch-tier canary plan
3. verify live preconditions before any live claim
4. collect result files into a stable metrics envelope

## 4. VPN and firewall posture rules

Required harness token:
- `vpn_port_posture_fail_closed`

Rules:
- live claims require an explicit port-posture artifact
- missing port posture fails closed
- blocked ports are recorded as evidence blockers rather than silently ignored
- required live posture is checked before any Tier C closure-grade claim

## 5. Metrics and artifact flow

Required harness token:
- `machine_readable_metrics_emitted_by_default`

The collector emits stable JSON by default and normalizes:
- topology tier
- scenario id
- run id
- pass or fail outcome
- key timing data if present
- operator intervention notes
- closure-tier versus stretch-tier attribution

## 6. OpenClaw overlay boundary

Required harness token:
- `openclaw_overlay_optional_not_base_dependency`

OpenClaw may wrap or observe the harness as an overlay assistant, but:
- it is optional
- it is not imported by the base tools
- it is not required for Tier A, Tier B, or Tier C planning

This harness keeps row 9 on the raw transport and approved-inventory boundary.
