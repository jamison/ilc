# ILC Transport Hardening And Maturity Decision 669 v0.1

Status: hardening and maturity decision artifact
Date: 2026-04-15
Owner lane: G8 transport maturity strike force
Classification: sensitive decision artifact

## 1. Purpose and hardening posture

Phase 669 decides whether repo-local and operator-runbook hardening converted
the Phase 668 blocked-result set into a legitimate row-9 closure candidate.

Required decision tokens:
- `highest_value_failures_addressed_before_long_tail_polish`
- `row_9_closure_candidate_if_and_only_if_closure_tier_passes_after_hardening`
- `stretch_tier_findings_block_only_if_core_failure`
- `residual_risks_recorded_honestly`
- `dynamic_discovery_still_deferred_after_669`
- `openclaw_overlay_not_required_for_base_transport_correctness`

Hardening posture:
- closure-tier blockers first
- repo-local fixes only where they materially change the maturity claim
- no long-tail polish ahead of closure-tier truth

## 2. Failure classes addressed

`highest_value_failures_addressed_before_long_tail_polish`

Failure classes handled in this phase:
1. live operational preconditions
- restored SSH agent identity and reran remote smoke successfully
- result: the lane is no longer blocked at remote-access preconditions

2. home-node lifecycle persistence
- fixed the local launcher so the home-node service can support integrated
  exchange and drill execution
- result: integrated exchange and drill surfaces now run reliably inside the
  same command boundary

3. local interpreter determinism for live drills
- fixed testbed scripts that depended on bare `python3` instead of the repo
  interpreter
- result: negative-path and seven-agent live surfaces execute against the same
  dependency set as repo tests

4. exact-numeric public-runtime serialization
- fixed Decimal normalization at the LMDB public-runtime boundary and the
  economic-cycle hash path
- result: seven-agent economic-state materialization now completes

5. five-node closure-tier topology extension
- extended the harness from the prior three-node baseline to five transport
  nodes across the existing three machines
- result: the actual closure-tier topology now exists and is runnable

6. explicit fallback and heavy-payload evidence surfaces
- added explicit fallback markers to the exchange and drill scripts and added
  live heavy-payload rejection proof in the negative-path drill
- result: missing scenario families are now evidenced instead of inferred

7. selected `443` proof on real VPS nodes
- promoted one primary node on each DigitalOcean VPS to `TCP 443` while keeping
  colocated secondary nodes on high ports
- result: selected VPN-backed `443` proof exists without pretending QUIC or
  universal public ingress is already closed

Not addressed in this window:
- QUIC / `UDP 443` operationalization
- internet-scale or public-edge ingress proof
- dynamic discovery
- OpenClaw overlay proof as a base dependency

## 3. Changes made and why

Changes made in Phase 669:
- `tools/testbed/home_node_common.sh`
- `tools/testbed/common.sh`
- `tools/testbed/node_inventory.py`
- `tools/testbed/render_testbed_configs.py`
- `tools/testbed/render_bootstrap_peers.py`
- `tools/testbed/verify_bootstrap_peers.py`
- `tools/testbed/start_nodes.sh`
- `tools/testbed/stop_nodes.sh`
- `tools/testbed/restart_nodes.sh`
- `tools/testbed/run_remote_smoke.sh`
- `tools/testbed/check_three_node_exchange.sh`
- `tools/testbed/run_recovery_drills.sh`
- `tools/testbed/run_negative_path_drills.sh`
- `tools/testbed/run_three_node_exchange.sh`
- `tools/testbed/run_three_node_seven_agent_scenario.sh`
- `tools/testbed/run_three_node_seven_agent_scenario.py`
- `ilc_core/storage/lmdb_public_runtime.py`
- `ilc_core/rc/economic_cycle_runtime.py`
- `testbed/hosts.json`
- `testbed/bootstrap_peers.json`
- `testbed/bootstrap_distribution.json`
- `testbed/configs/ilc-node-1/node_config.json`
- `testbed/configs/ilc-node-2/node_config.json`
- `testbed/configs/ilc-node-3/node_config.json`
- `testbed/configs/ilc-node-4/node_config.json`
- `testbed/configs/ilc-node-5/node_config.json`
- targeted regression coverage in:
  - `tests/test_testbed_control_surface.py`
  - `tests/test_agent_loop_v1_runtime.py`
  - `tests/test_lmdb_public_runtime_store.py`
  - `tests/test_phase_669_transport_hardening_and_maturity_decision.py`

Why:
- these mutations materially changed the row-9 maturity claim
- the lane moved from blocked remote access to live five-node closure evidence
- the remaining realism gaps are now honestly bounded rather than lane-blocking

## 4. Closure-tier rerun results

Rerun commands and proof surfaces:
- `bash tools/testbed/run_remote_smoke.sh --mode connectivity`
- `bash tools/testbed/run_remote_smoke.sh --mode service`
- `bash tools/testbed/run_three_node_exchange.sh`
- `bash tools/testbed/run_three_node_exchange.sh --soak-seconds 300`
- `bash tools/testbed/run_recovery_drills.sh --skip-diagnostics`
- `bash tools/testbed/run_negative_path_drills.sh --skip-diagnostics`
- `bash tools/testbed/run_three_node_seven_agent_scenario.sh`

Closure-tier scenario family result:
- bootstrap: satisfied on the five-node / three-machine topology
- steady-state dissemination: satisfied on the five-node / three-machine
  topology
- churn: satisfied through five-node reruns and the seven-agent runtime surface
- partition/heal/recovery: satisfied on the five-node / three-machine topology
- HTTP/2 fallback activation: satisfied through explicit `transport_kind=http`
  fallback proof markers on all active nodes
- restart/rejoin: satisfied on the five-node / three-machine topology
- bounded push correctness: satisfied on the five-node / three-machine topology
- pull-only heavy payload correctness: satisfied through explicit live rejection
  proof in the negative-path drill

Repeatability and soak:
- three clean closure-tier repetitions completed
- one soak run completed at 300 seconds before live exchange

selected Tier C VPN-backed realism proof:
- both DigitalOcean VPS hosts now run one selected primary node on `TCP 443`
- `100.109.27.59:443` is open and participates in the live network
- `100.108.3.57:443` is open and participates in the live network
- colocated secondary nodes remain on `19574` and `19575`
- dual-`443` exchange passed
- dual-`443` negative-path drill passed
- dual-`443` recovery rerun passed

Evidence roots:
- `out/testbed/transport_maturity/live_fix_loop_20260415/three_node_exchange.log`
- `out/testbed/transport_maturity/live_fix_loop_20260415/recovery_drill.log`
- `out/testbed/transport_maturity/live_fix_loop_20260415/negative_path_drill.log`
- `out/testbed/seven-agent/20260415_071813/scenario_manifest.json`
- `out/testbed/seven-agent/20260415_071813/economic-state/manifest.json`

The maturity picture changed materially:
- the five-node / three-machine minimum is now instantiated and passing
- required scenario families are now evidenced rather than assumed
- selected Tier C VPN-backed evidence exists on the actual remote infrastructure

## 5. Maturity decision and residual risks

`row_9_closure_candidate_if_and_only_if_closure_tier_passes_after_hardening`
`residual_risks_recorded_honestly`
`dynamic_discovery_still_deferred_after_669`
`openclaw_overlay_not_required_for_base_transport_correctness`

Maturity decision:
- row 9 is a closure candidate for Phase 670

Why:
- the closure-tier contract is met after hardening
- the five-node / three-machine topology passes the required scenario families
- the repeatability bar is met with three clean repetitions plus one soak run
- ordinary operator actions remained runbook-grade rather than heroic
- selected Tier C VPN-backed evidence now exists on the live VPS pair

Residual risks:
- QUIC remains unoperationalized in the current runtime, so `UDP 443` is still
  not a live proof surface
- selected `TCP 443` proof exists, but universal public-edge ingress posture is
  still not claimed
- DigitalOcean is not the blocker here; the remaining gap is runtime and
  deployment scope, not provider prohibition
- row-9 closure remains bounded public-participant maturity, not internet-scale
  proof

## 6. Stretch-tier carry-forward

`stretch_tier_findings_block_only_if_core_failure`

Stretch-tier carry-forward:
- stretch-tier work remains non-blocking because the closure-tier package now
  passes
- no stretch-tier finding in this window invalidated the closure-tier claim
- useful carry-forward items are:
  - operationalize real QUIC / `UDP 443`
  - extend soak time beyond 300 seconds
  - broaden public-edge or non-Tailscale ingress proof if a later lane wants it
  - reuse the five-node harness for rows 7 and 8 rather than rebuilding it
