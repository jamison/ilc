# ILC Phase 1432 Rehearsal Infrastructure Validation Evidence v0.1

PUBLIC_RC_EXCLUDE: private_rehearsal_evidence
PUBLIC_RC_EXCLUDE_REASON: contains private testbed topology, rehearsal-only runtime paths, and non-public operator infrastructure evidence.
PUBLIC_RC_INCLUDE_REQUIRES: public_rc_rehearsal_evidence_allowlist_review

## Result

Phase 1432 private rehearsal infrastructure validation is complete.

```text
rehearsal_infra_validation_complete_phase_1432
rehearsal_epoch_cycling_confirmed_phase_1432
rehearsal_review_lane_vrf_panel_confirmed_phase_1432
openclaw_p2p_path_tested_phase_1432
no_live_llm_api_phase_1432
```

## Claim Verification

| Claim | File/symbol checked | Result |
|---|---|---|
| Phase 1423 defines private rehearsal criteria and 3-machine / 7-agent topology | `docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md` | confirmed |
| Phase 1431 identity manifest exists before infra validation | `docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md` | confirmed |
| FINDING-9 was dispositioned before Phase 1432 | `docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md`, `docs/phases/phase_1431_rehearsal_identity_ceremony_walkthrough.md` | confirmed |
| Production jury assignment gate is authorized after Phase 1429 | `ilc_core/epistemic/jury_assignment_runtime.py` | confirmed: `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = False` |
| VRF jury assignment path is integrated | `ilc_core/epistemic/jury_assignment_runtime.py`, token `vrf_verifier_integrated_jury_assignment_phase_1412` | confirmed |
| Review lane admission runtime exists | `ilc_core/epistemic/review_lane_admission_runtime.py` | confirmed |
| Prompt claim that `ilc_core/network/d2d/gossip_transport.py` was modified in git status | `git status --short`, `ilc_core/network/d2d/gossip_transport.py` | stale prompt claim; file was not dirty at execution start |
| Live LLM API calls are absent from scripted rehearsal runtime | `tools/agent_loop_v1.py`, `tools/testbed/`, `testbed/scenarios/seven_agent_cycle_v1.json` | confirmed by search for OpenAI/Anthropic/API-key/LLM terms |

## Topology

The private rehearsal topology used the Phase 1431 seven-agent public identity
manifest and the Phase 1432 private testbed endpoints.

| Role | Machine / endpoint | Evidence |
|---|---|---|
| M1 / home | `ilc-node-1`, local home node | `out/testbed/phase1432/seven-agent/submissions/submission_1.json`, `submission_4.json` |
| M2 | `ilc-node-2`, Tailscale `100.112.32.42`, systemd port 443 | service active; exchange returned 202 |
| M2 manual endpoint | `ilc-node-4`, Tailscale `100.112.32.42`, port 19574 | service ready; exchange returned 202 |
| M3 | `ilc-node-3`, Tailscale `100.91.33.46`, systemd port 443 | service active; exchange returned 202 |
| M3 manual endpoint | `ilc-node-5`, Tailscale `100.91.33.46`, port 19575 | service ready; exchange returned 202 |
| Harness node | `ilc-node-6`, Tailscale `100.72.17.38`, systemd port 443 | service active; exchange returned 202 |

Transport evidence:

```text
three_node_exchange_ok
home_to_https://100.112.32.42:19574=202
home_to_https://100.112.32.42:443=202
home_to_https://100.72.17.38:443=202
home_to_https://100.91.33.46:19575=202
home_to_https://100.91.33.46:443=202
ilc-node-2_to_home=202
ilc-node-3_to_home=202
ilc-node-4_to_home=202
ilc-node-5_to_home=202
ilc-node-6_to_home=202
```

Scope correction: current testbed D2D transport exercised the explicit
private-rehearsal HTTP/HTTPS gossip fallback over Tailscale. Native Rust/QUIC
P2P remains deferred and was not activated by this phase.
Native Rust/QUIC P2P remains deferred.

## Epoch And Review Cycle Evidence

Scenario artifact:

```text
path=out/testbed/phase1432/seven-agent/scenario_manifest.json
sha256=97559166246746ce9c1a0f7fc416f0d54cd0fdc8f0c4e3e899c11357b1adc4c3
scenario_runtime_version=agent_loop_v1_runtime_575.v0.1
epoch=574
submission_count=7
panel_verdict_token=panel_quorum_passed
yes_votes=7
no_votes=1
agreement_score=0.875
ecu_claim_count=6
economic_distribution_check_ok=true
economic_wallet_count=8
economic_reward_total=5.8173828125
```

Supporting artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `out/testbed/phase1432/seven-agent/panel/panel_result.json` | `f9645188311df3f700444509d95bd9e2eab77a5fbba660e350250d546de12f32` |
| `out/testbed/phase1432/seven-agent/panel/ecu_claims.json` | `3d5f4a9debc24324789bd5f7f98115d2b1f47ccfadd362a77f21dcbc44df8a59` |
| `out/testbed/phase1432/seven-agent/economic-state/manifest.json` | `7cb7778965c47e0046da52993cb48f0c5417dbf6598b629f2856d64bfbd86267` |
| `out/testbed/phase1432/seven-agent/diagnostics/manifest.json` | `24d546ec92c580841b14bfb1f0fabe28965b16d0871b26512fb9619da7d17c55` |

Execution anomaly: the full scenario wrapper wrote all seven submissions, then
blocked in a captured subprocess path. The deterministic remaining steps
`evaluate-panel`, `broadcast-artifact`, diagnostics collection, and economic
materialization were run directly with the same `agent_loop_v1_runtime_575.v0.1`
runtime and persisted artifacts. This anomaly is recorded in the scenario
manifest as `manual_close_after_wrapper_inherited_pipe_hang`.

## Synthetic Math Dataset

The Phase 1 synthetic dataset was generated as 64 deterministic mathematical
truth primitives.

```text
path=out/testbed/phase1432/synthetic_math_truth_primitives.json
sha256=4a2541b2b9b04b5aefcded2adb774614e1fd9b1a737c043468bd795839019206
manifest_sha256=af90de30a4ed74fdfb9376db8bb5b1290a2cd4c6ac1e7a289e4f431d3bc8daa0
node_count=64
taxonomy_classes=TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA, TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE, TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE, TaxonomyClass.T4_SUBJECTIVE_AESTHETIC_NODE
visibility=private_rehearsal_only
```

The synthetic dataset was not a production graph write and did not enter public
RC artifacts.

## VRF Panel And Review Lane Evidence

VRF-integrated jury assignment evidence:

```text
path=out/testbed/phase1432/vrf_panel_quote.json
sha256=4da36ba5aca9543a63d287def37e85d9447963c448d95df3488f9081d5725b1a
assignment_mode=vrf_verified
review_epoch=574
regular_panel_size=7
outsider_panel_size=1
panel_size=8
reviewer_quorum_k=5
cluster_diversity_verified=true
production_activated=false
```

The VRF quote used RFC 9381 B.4 public fixtures in audit mode. No Phase 1431
private identity key material, VRF private key, or production proof-generation
material entered the repository. No Phase 1431 private identity key material
was used for the VRF fixture quote.

Review lane synthetic decision evidence:

```text
path=out/testbed/phase1432/review_lane_synthetic_decisions.json
sha256=b4117fc0e4afddd52f16fee2361650628fa52e75d94595b016bb1094f9213ee7
manifest_sha256=352ee6e13505ba9364d81fa2c225bf2c21fd24ee0c6ad649e8486bd00fc93c81
review_lane_decision_count=64
admitted_count=64
source_taxonomy_class=TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION
graph_write_authorized=false
public_economics_authorized=false
reviewer_payment_authorized=false
```

## OpenClaw Harness-Assisted P2P Path

OpenClaw was present on `ilc-node-6`:

```text
OpenClaw 2026.5.7 (eeef486)
```

The local ILC OpenClaw profile was present and ready:

```text
ilc-local Ready
Local-only ILC profile preview and sidecar verification guide for private OpenClaw rehearsal.
```

No OpenClaw gateway listener was active on `:18789` or `:19001` after the check.
This phase tested the harness path by verifying the installed OpenClaw CLI,
profile visibility, local skill readiness, and absence of an externally exposed
OpenClaw gateway. Public OpenClaw P2P activation remains Phase 1437 and remains
SENSITIVE.

## Werner Diagnostic

Track H1 Werner diagnostic runtime was not yet wired at Phase 1432 execution.
No pressure-flow or Werner flow-governor metric is recorded by this phase.

## Non-Activation Claims

```text
no_live_llm_api_phase_1432
phase_1432_no_public_serving
phase_1432_no_public_rc_publication
phase_1432_no_epoch_0_to_1_transition
phase_1432_no_cdl_mutation
phase_1432_no_production_graph_write
phase_1432_no_wallet_write
phase_1432_no_treasury_write
phase_1432_no_live_llm_api_call
phase_1432_native_rust_p2p_not_activated
phase_1432_openclaw_gateway_not_publicly_activated
```

## Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_rehearsal_infra_validation_evidence_1432_v0.1.md
```
