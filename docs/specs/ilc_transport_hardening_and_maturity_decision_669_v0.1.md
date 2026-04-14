# ILC Transport Hardening And Maturity Decision 669 v0.1

Status: hardening and maturity decision artifact
Date: 2026-04-15
Owner lane: G8 transport maturity strike force
Classification: sensitive decision artifact

## 1. Purpose and hardening posture

Phase 669 decides whether any repo-local hardening can convert the Phase 668
blocked-result set into a legitimate row-9 closure candidate.

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

Failure classes chosen for immediate handling:
1. repo-local harness ambiguity
- already addressed in Phase 667 plus the Phase 668 metrics-collector hardening
- result: the lane now emits a stable blocked-result package instead of failing
  opaquely

2. live operational preconditions
- rerun confirmed that remote smoke still fails immediately at
  `ssh_agent_identity_missing:run_ssh_add ~/.ssh/id_ed25519`
- result: no repo-local code change can honestly clear the blocker in this
  phase

Not addressed in this window:
- VPN and firewall posture verification after SSH restoration
- actual Tier B and Tier C live scenario passes
- stretch-tier expansion after closure-tier recovery

## 3. Changes made and why

Changes made in Phase 669:
- no additional runtime mutation
- no additional testbed mutation
- no additional `ilc_core/` mutation

Why:
- the remaining blocker is operational, not code-level
- further repo churn would create activity without improving the maturity truth
- the right decision is to preserve the blocked posture honestly

## 4. Closure-tier rerun results

Rerun commands:
- `python3 tools/testbed/run_transport_maturity_canary.py --plan closure_tier`
- `bash tools/testbed/run_remote_smoke.sh --mode connectivity`

Rerun result by closure-tier scenario family:
- bootstrap: not a pass, blocked by missing SSH agent identity
- steady-state dissemination: not a pass, blocked by missing SSH agent identity
- churn: not a pass, blocked by missing SSH agent identity
- partition/heal/recovery: not a pass, blocked by missing SSH agent identity
- HTTP/2 fallback activation: not a pass, blocked by missing SSH agent identity
- restart/rejoin: not a pass, blocked by missing SSH agent identity
- bounded push correctness: not a pass, blocked by missing SSH agent identity
- pull-only heavy payload correctness: not a pass, blocked by missing SSH
  agent identity

The rerun preserves the Phase 668 conclusion:
- no closure-tier live pass package exists

## 5. Maturity decision and residual risks

`row_9_closure_candidate_if_and_only_if_closure_tier_passes_after_hardening`
`residual_risks_recorded_honestly`
`dynamic_discovery_still_deferred_after_669`
`openclaw_overlay_not_required_for_base_transport_correctness`

Maturity decision:
- row 9 is not a closure candidate for Phase 670

Why:
- the closure-tier package does not pass after the available hardening work
- the blocker is still external operational access, not a resolved repo-local
  defect
- a blocked-result set cannot be promoted into a maturity closure claim

Residual risks:
- remote access preconditions remain unresolved
- VPN and firewall posture remain unverified
- row-9 timing bands remain untested under live three-machine conditions
- Tier C realism remains absent

## 6. Stretch-tier carry-forward

`stretch_tier_findings_block_only_if_core_failure`

Stretch-tier carry-forward:
- stretch-tier work stays non-blocking because the lane already failed on a
  closure-tier precondition
- no stretch-tier finding overrode the closure-tier failure
- the next useful work is to restore SSH agent identity, verify VPN posture,
  and rerun closure-tier evidence before any long-tail expansion
