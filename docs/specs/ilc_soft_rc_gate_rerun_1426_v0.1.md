# ILC Soft RC Gate Re-Run 1426 v0.1

Status: SENSITIVE gate re-run report
Phase: 1426
Date: 2026-05-21

```text
soft_rc_gate_rerun_phase_1426
soft_rc_eligible=true_phase_1426
phase_1366_soft_rc_deferred_gate_now_closed_phase_1426
soft_rc_eligible_true_not_public_rc_activated_phase_1426
```

## Verdict

```text
soft_rc_eligible=true
soft_rc_eligible=true_phase_1426
```

The Phase 1366 historical report remains unchanged. It recorded:

```text
soft_rc_eligible=false_with_blockers: [phase_1366_treasury_epoch_budget_binding_unverified]
```

Phase 1367 fixed the only recorded blocker by replacing the caller-supplied
validator reward-pool treasury budget with an emission-derived budget binding.
Phase 1426 re-runs the soft-RC gate against the current repo state and records
that the deferred gate is now closed.

## Inputs

| Input | Purpose | Result |
| --- | --- | --- |
| `docs/specs/ilc_soft_rc_readiness_gate_report_phase_1366_v0.1.md` | Historical soft-RC gate report | confirmed false-with-one-blocker verdict |
| `docs/phases/phase_1367_pre_gate_fix_pass_walkthrough.md` | Blocker-resolution evidence | confirmed `phase_1366_treasury_epoch_budget_binding_verified` |
| `ilc_core/epoch/validator_reward_pool_routing_runtime.py` | Current CDL-054 runtime | confirmed budget now derives from `build_epoch_emission_quote(...).capped_epoch_budget_ilc` |
| `ilc_core/epoch/issuance_economics_integration_gate.py` | Current integration gate | confirmed binding-token enforcement remains present |
| `docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md` | Launch manifest dependency | confirmed Phase 1426 true verdict is expected before signing |
| `ilc_core/epistemic/jury_activation_gate.py` | Phase 1425 pre-gate state | confirmed `evaluate_jury_activation_gate()` returns `verdict="PASS"` with `production_activated=False` |

## Phase Claim Verification

| Claim | File or symbol checked | Result |
| --- | --- | --- |
| Phase 1426 prompt is schema-valid | `tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_1426_g8_soft_rc_gate_rerun.md` | confirmed |
| Phase 1366 gate report exists and shows `soft_rc_eligible=false_with_blockers` | `docs/specs/ilc_soft_rc_readiness_gate_report_phase_1366_v0.1.md` | confirmed |
| Phase 1367 records blocker fix token | `docs/phases/phase_1367_pre_gate_fix_pass_walkthrough.md`; `tests/test_phase_1367_pre_gate_fix_pass.py` | confirmed |
| No completed artifact previously recorded `soft_rc_eligible=true_phase_1426` | repo-wide token search before Phase 1426 execution | confirmed: token only appeared in prompts and future prerequisites |
| Phase 1422 launch manifest schema expects the Phase 1426 true verdict before signing | `docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md` | confirmed |
| `evaluate_jury_activation_gate()` now returns `verdict="PASS"` | live Python import of `evaluate_jury_activation_gate()` | confirmed: `blocking_not_met=[]`, `production_activated=False` |
| Production jury activation remains unauthorized | `PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED` | confirmed: `True` |

## Discovery Record

| Pass | Findings |
| --- | --- |
| Section 0a known-token audit | Required Phase 1426 tokens were present in the Phase 1426 prompt and as future prerequisites in Phase 1427/1428 prompts, but not in completed artifacts before this phase. |
| Section 0b concept-discovery search | Searches covered `soft_rc`, `soft_rc_eligible`, Phase 1366, Phase 1367, treasury epoch budget binding, Phase 1422 launch manifest dependency, and J-008 pre-gate state. |
| Section 0c contradiction and non-claim search | Confirmed existing non-claims around public RC publication, signing, activation, epoch transition, production jury activation, wallet writes, ledger writes, and production value-path operations. |
| Section 0d source expansion | Direct-read Phase 1366, 1367, 1368, 1422, and 1425 evidence plus current runtime call sites before recording this verdict. |
| MemPalace advisory recall | Tier-b planning recall confirmed the historical Phase 1366 blocker and Phase 1367 fix-without-rerun routing; direct repo reads remained controlling. |

## Gate Re-Run Table

| Gate row | Current evidence | Phase 1426 result |
| --- | --- | --- |
| CDL-025/026/027/028/029/030 issuance/emission runtimes | Phase 1345-1351 reports and runtime tokens | PASS |
| CDL-031/047/054/083 related runtime items plus treasury-budget binding | Phase 1367 token `phase_1366_treasury_epoch_budget_binding_verified`; current runtime derives budget from `capped_epoch_budget_ilc` | PASS |
| Issuance economics integration gate | Phase 1352 report plus current binding-token check | PASS |
| CDL-017 validator admission/ejection plus SEC-004 | Phase 1353 report | PASS |
| CDL-068 topology shuffle VRF | Phase 1354 report | PASS |
| CDL-V6 genesis intervention runtime | Phase 1355 report | PASS |
| CDL-013 governance weight live integration | Phase 1356 report | PASS |
| `reputation.py` H11 float-kill | Phase 1357 report | PASS |
| `ilc_core/` to `ilc_consensus/` bridge | Phase 1358 and Phase 1360 evidence; later 1386a/1386c closes TLS and persistent-connectivity paths | PASS |
| HIGH-001 log redaction | Phase 1359 report | PASS |
| Multi-operator non-loopback Mysticeti testnet | Phase 1360 reports with inherited scope caveats; later connectivity hardening recorded in Phases 1386a-1386c | PASS |
| CDL-043/044 adaptive pruning | Phase 1361 report | PASS |
| Blocking-authority ratification plus CDL-057 activation | Phase 1364 report | PASS |

## Blocker Closure

```text
phase_1366_soft_rc_deferred_gate_now_closed_phase_1426
```

The only blocker recorded by Phase 1366 was:

```text
phase_1366_treasury_epoch_budget_binding_unverified
```

Phase 1367 resolved it by recording:

```text
phase_1366_treasury_epoch_budget_binding_verified
```

No new soft-RC gate blocker was found during Phase 1426 discovery or direct
source reads.

## Non-Authorization

```text
soft_rc_eligible_true_not_public_rc_activated_phase_1426
```

This report does not authorize public RC publication, source publication, public
repository push, package upload, release signing, activation-certificate signing,
launch-readiness manifest signing, epoch 0-to-1 transition, public
installability claim, public launch claim, public verifier serving, public HTTP
claimability serving, public P2P serving, public sidecar serving, public
confidential coordination, production jury assignment, production reviewer
payment, live ECU distribution, live ILC settlement, treasury write, ledger
write, wallet write, registry write, graph write, CDL mutation, Genesis signing,
Genesis or Atlas mutation, production minting, production mining, or production
validator deployment.

Phase 1427 remains the SENSITIVE J-008 gate re-run. Phase 1428 remains the
Window 1399-1428 closure gate.
