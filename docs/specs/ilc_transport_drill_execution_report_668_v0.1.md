# ILC Transport Drill Execution Report 668 v0.1

Status: failure-harvest report
Date: 2026-04-15
Owner lane: G8 transport maturity strike force
Classification: sensitive execution report

## 1. Purpose and execution posture

Phase 668 attempted the row-9 closure-tier drill surface and records the actual
operational blockers instead of simulating success.

Required execution tokens:
- `vpn_firewall_posture_recorded_before_live_runs`
- `row_9_not_closed_in_668`

Execution posture:
- topology manifest rendered locally
- closure-tier canary plan rendered locally
- live remote smoke attempted before any maturity claim
- failure evidence recorded when the live path blocked

## 2. Scenario matrix and environment notes

Required execution tokens:
- `tier_b_three_machine_evidence_present_or_honest_gap_recorded`
- `tier_c_vpn_evidence_present_or_honest_gap_recorded`
- `push_path_boundedness_checked`
- `pull_only_heavy_payload_checked`
- `fallback_activation_checked`
- `partition_and_recovery_checked`
- `restart_and_rejoin_checked`

Scenario families in scope:
- bootstrap
- steady-state dissemination
- churn
- partition/heal/recovery
- HTTP/2 fallback activation
- restart/rejoin
- bounded push correctness
- pull-only heavy payload correctness

Environment notes:
- `python3 tools/testbed/render_transport_maturity_topologies.py --output out/testbed/transport_maturity_topologies.json` succeeded
- `python3 tools/testbed/run_transport_maturity_canary.py --plan closure_tier` succeeded
- `bash tools/testbed/run_remote_smoke.sh --mode connectivity` failed immediately with `ssh_agent_identity_missing:run_ssh_add ~/.ssh/id_ed25519`
- no verified VPN port-posture artifact existed after the failed smoke attempt

Interpretation:
- `tier_b_three_machine_evidence_present_or_honest_gap_recorded` means an
  honest Tier B evidence gap was recorded
- `tier_c_vpn_evidence_present_or_honest_gap_recorded` means an honest Tier C
  evidence gap was recorded
- `push_path_boundedness_checked`, `pull_only_heavy_payload_checked`,
  `fallback_activation_checked`, `partition_and_recovery_checked`, and
  `restart_and_rejoin_checked` were all retained in the blocked scenario matrix
  and metrics set, but none reached live pass status in this phase

## 3. Closure-tier results

Closure-tier result summary:
- Tier B baseline: blocked before live execution
- Tier C selected VPN-backed scenarios: blocked before live execution
- root blocker: SSH agent identity unavailable for remote access
- secondary blocker: VPN and firewall posture remained unverified after the SSH
  blocker

The metrics artifact records blocked closure-tier rows for:
- all eight Tier B scenario families
- selected Tier C scenarios for bootstrap, partition/heal/recovery, HTTP/2
  fallback activation, and restart/rejoin

No closure-tier scenario passed in Phase 668.

## 4. Stretch-tier results

Stretch-tier work was intentionally downgraded after the closure-tier blocker
surfaced.

Recorded stretch-tier posture:
- Tier A local-only stretch rows were deferred
- extra Tier C bounded-push and pull-only-heavy checks were deferred
- the deferred rows remain useful because they preserve the scenario envelope
  for later reruns without claiming evidence we do not have

## 5. Failure taxonomy and operator notes

Failure taxonomy:
1. access and control-plane blocker
- `ssh_agent_identity_missing:run_ssh_add ~/.ssh/id_ed25519`

2. live evidence blocker
- VPN and firewall posture unverified after the failed SSH step

3. resulting maturity blocker
- no closure-tier remote evidence
- honest Tier C evidence gap after the failed SSH step

Operator notes:
- the harness behaved correctly by failing closed
- the lane did not silently collapse Tier C into local-only reassurance
- the next step is to restore SSH agent identity and then rerun smoke plus
  port-posture verification before making any live maturity claim

## 6. Provisional maturity posture

`row_9_not_closed_in_668`

Provisional posture:
- row 9 remains open in this phase
- the current evidence package is an honest blocked-result set, not closure
  evidence
- Phase 669 may only produce a row-9 closure candidate if the live blockers are
  cleared and the closure-tier reruns actually pass
