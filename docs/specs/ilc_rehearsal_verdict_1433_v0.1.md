# ILC Rehearsal Verdict - Phase 1433

PUBLIC_RC_EXCLUDE: private_rehearsal_evidence
PUBLIC_RC_EXCLUDE_REASON: contains private testbed topology, rehearsal-only runtime evidence, and non-public operator infrastructure evidence.
PUBLIC_RC_INCLUDE_REQUIRES: public_rc_rehearsal_evidence_allowlist_review

**Status:** PASS - private soft-RC rehearsal complete; wipe right exercised
**Phase:** 1433
**Date:** 2026-05-22
**Scope:** Private rehearsal verdict and Phase 2 Lean Mathlib dataset

```text
rehearsal_verdict_phase_1433
rehearsal_phase_2_complete_phase_1433
rehearsal_lean_mathlib_dataset_complete_phase_1433
rehearsal_verdict=pass_phase_1433
wipe_right_exercised_phase_1433
rehearsal_state_wiped_phase_1433
production_keypairs_preserved_off_machine_phase_1433
no_live_llm_api_phase_1433
phase_1433_no_public_serving
phase_1433_no_public_rc_publication
phase_1433_no_epoch_0_to_1_transition
phase_1433_no_cdl_mutation
phase_1433_no_production_graph_write
phase_1433_no_wallet_write
phase_1433_no_treasury_write
phase_1433_native_rust_p2p_not_activated
phase_1433_openclaw_gateway_not_publicly_activated
```

## Verdict

```text
verdict=PASS
phase_1_status=PASS_BY_PHASE_1432
phase_2_status=PASS_BY_PHASE_1433
remediation_required=false
next_phase=1434
next_phase_sensitivity=SENSITIVE
next_phase_go_required=GO Phase 1434
```

Phase 1433 completes the private soft-RC rehearsal by adding the rights-safe
Lean Mathlib Phase 2 dataset, running seven deterministic scripted agents
against that dataset, recording a passing panel verdict, materializing
rehearsal-only economic evidence, and exercising the Phase 1423 wipe right.

This PASS does not publish public RC artifacts, activate public serving,
trigger epoch 1, mutate the CDL register, write production graph state, mutate
wallets, or authorize any public network surface.

## Pre-Execution Claim Verification

| Claim | File or symbol checked | Result |
|---|---|---|
| Phase 1432 evidence confirms epoch cycling and VRF panel evidence | `docs/specs/ilc_rehearsal_infra_validation_evidence_1432_v0.1.md` | confirmed: `rehearsal_epoch_cycling_confirmed_phase_1432`, `rehearsal_review_lane_vrf_panel_confirmed_phase_1432` |
| Phase 2 dataset must be Lean Mathlib, Apache-2.0 licensed, at most 5 theorems | `docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md` | confirmed |
| Wipe right scope is defined before verdict execution | `docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md` | confirmed |
| Phase 1420 copyright disposition allows metadata, extracted claims, hashes, source spans, and explicitly licensed bytes | `docs/specs/ilc_copyright_counsel_disposition_1420_v0.1.md` | confirmed |
| Lean Mathlib upstream HEAD and license were checked during execution | `git ls-remote https://github.com/leanprover-community/mathlib4.git HEAD`, `curl https://raw.githubusercontent.com/leanprover-community/mathlib4/master/LICENSE` | confirmed: commit `b115fc31f3f5cf2ea5991fcc01a7d7772c0324bb`; license first line `Apache License Version 2.0, January 2004` |

## Phase 1 Evidence Summary

Phase 1 is inherited from Phase 1432:

```text
rehearsal_infra_validation_complete_phase_1432
rehearsal_epoch_cycling_confirmed_phase_1432
rehearsal_review_lane_vrf_panel_confirmed_phase_1432
openclaw_p2p_path_tested_phase_1432
no_live_llm_api_phase_1432
```

Phase 1432 records:

```text
scenario_runtime_version=agent_loop_v1_runtime_575.v0.1
epoch=574
submission_count=7
panel_verdict_token=panel_quorum_passed
yes_votes=7
no_votes=1
agreement_score=0.875
ecu_claim_count=6
economic_distribution_check_ok=true
synthetic_math_truth_primitive_count=64
review_lane_decision_count=64
review_lane_admitted_count=64
```

Transport scope correction: Phase 1432 proved the explicit private HTTP/HTTPS
gossip fallback over Tailscale. It did not prove or activate native Rust/QUIC
P2P. Native Rust/QUIC P2P remains deferred, and the public OpenClaw gateway
remains not activated.

## Phase 2 Dataset

The Phase 2 dataset is a deterministic Lean Mathlib metadata and extracted
claim subset. It contains no verbatim theorem source text.

```text
dataset_marker=phase_1433_lean_mathlib_phase2_dataset
dataset_id=lean_mathlib_phase2_subset_v1
source_repo=https://github.com/leanprover-community/mathlib4
source_commit=b115fc31f3f5cf2ea5991fcc01a7d7772c0324bb
license=Apache-2.0
license_evidence_url=https://raw.githubusercontent.com/leanprover-community/mathlib4/master/LICENSE
theorem_count=5
no_verbatim_source=true
rights_profile=metadata_extracted_claims_source_span_only_phase_1420
taxonomy_targets=TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE, TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM, TaxonomyClass.T6_VALIDATOR_CONSENSUS_CLAIM
```

Selected theorem identifiers and source spans:

| Theorem ID | Source path | Source line | Taxonomy target |
|---|---|---:|---|
| `one_le_div` | `Mathlib/Algebra/Order/Field/Basic.lean` | 41 | `TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE` |
| `div_le_one` | `Mathlib/Algebra/Order/Field/Basic.lean` | 43 | `TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE` |
| `one_lt_div` | `Mathlib/Algebra/Order/Field/Basic.lean` | 45 | `TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM` |
| `div_lt_one` | `Mathlib/Algebra/Order/Field/Basic.lean` | 47 | `TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM` |
| `tsub_le_iff_left` | `Mathlib/Algebra/Order/Sub/Defs.lean` | 92 | `TaxonomyClass.T6_VALIDATOR_CONSENSUS_CLAIM` |

Dataset evidence:

```text
path=out/testbed/phase1433/lean-mathlib/lean_mathlib_phase2_dataset.json
file_sha256=c49a41482706c13df748a2c263ed7e636494c97901337a65ac8d2c6b3655e185
manifest_sha256=d9b055d98d7f1e491b0977c821fd17dbdd39526f39717bef8f1c8e0780ce68d2
```

## Phase 2 Execution Evidence

The seven deterministic scripted agents ran against the Lean Mathlib Phase 2
dataset using `agent_loop_v1_runtime_575.v0.1`.

```text
path=out/testbed/phase1433/lean-mathlib/scenario_manifest.json
sha256=baae765e6041e174d278a23264aab8907115329c7c01471d48f37a0a80ba103d
scenario_runtime_version=agent_loop_v1_runtime_575.v0.1
epoch=575
submission_count=7
panel_verdict_token=panel_quorum_passed
panel_passed=true
yes_votes=7
no_votes=1
agreement_score=0.875
ecu_claim_count=6
economic_distribution_check_ok=true
economic_wallet_count=8
economic_reward_total=5.8173828125
live_llm_api_calls=false
production_graph_write_authorized=false
public_serving_authorized=false
transport_scope_correction=private_http_https_gossip_fallback_over_tailscale_not_native_rust_quic
transport_scope_human_phrase=private HTTP/HTTPS gossip fallback over Tailscale
```

Supporting artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `out/testbed/phase1433/lean-mathlib/panel/panel_result.json` | `03fc2ace7ba52578652365c2e26cdd40e062b875bef06b7ab34d77094ebe1ed7` |
| `out/testbed/phase1433/lean-mathlib/panel/ecu_claims.json` | `8e8c255eb8f60cecc392a189721c208ec911bada7b12c01b9c4178eb520475ee` |
| `out/testbed/phase1433/lean-mathlib/economic-state/manifest.json` | `9a21cd223e93bdff9250e841e5764ab965c8801a839ddba04130b23c20242e3e` |
| `out/testbed/phase1433/lean-mathlib/diagnostics/manifest.json` | `6abd5498bcee7dece2b2b7fc2cb174a3f397b71ac8a6e87e60f6a6e378e4921d` |

The initial Phase 2 task payload attempted a more specific task class and
verification method, but `EpistemicWorkTask` failed closed because only the
current literal enums are accepted. The successful run used the existing
`task_class=custom` and `verification_method=replayable-simulation` literals,
while preserving the Lean Mathlib dataset manifest as task payload evidence.

## Wipe Right Exercise

Because the verdict is PASS, the Phase 1423 wipe right was exercised before
proceeding to Track C.

```text
path=out/testbed/phase1433/wipe_right_evidence.json
sha256=b598bd7ff4d4148543b158cb7f7186a6967dad43f8add1cf1e41167c6d45231f
wipe_right_exercised_phase_1433=true
rehearsal_state_wiped_phase_1433=true
topology_torn_down_phase_1433=true
production_keypairs_preserved_off_machine_phase_1433=true
key_material_touched_by_wipe=false
private_key_material_paths_accessed=[]
failed_labels=[]
```

Wipe scope:

```text
rehearsal runtime services stopped
manual temp/log/pid paths cleared
home-node pid/log lifecycle cleared
out/testbed phase evidence retained for hash provenance
/etc/ilc reusable testbed config retained
production keypairs not touched
```

The seven production keypairs generated in Phase 1431 remain off-machine with
the human operator per Q1. No private key material, mnemonics, recovery seeds,
Shamir shares, or private plates were touched by the wipe.

## Criteria Mapping

| Phase 1423 criterion | Evidence | Result |
|---|---|---|
| 3-machine / 7-agent topology | Phase 1431 manifest, Phase 1432 infra evidence, Phase 1433 scenario manifest | PASS |
| Synthetic Phase 1 corpus at least 10 nodes | Phase 1432: 64 synthetic math truth primitives | PASS |
| Phase 2 Lean Mathlib subset at most 5 theorems | Phase 1433 dataset: 5 theorem metadata/extracted-claim records | PASS |
| Taxonomy coverage at least 3 classes | Phase 1433 dataset targets three `TaxonomyClass.*` enums | PASS |
| Rights-safe external content boundary | Apache-2.0 upstream license checked; no verbatim source included | PASS |
| Deterministic scripted agents only | `agent_loop_v1_runtime_575.v0.1`; no live LLM API calls | PASS |
| Panel/verdict path completes | `panel_quorum_passed`, 7 yes / 1 no, agreement 0.875 | PASS |
| Rehearsal economic materialization only | 6 claim records, distribution check true, production graph/write flags false | PASS |
| Wipe right after PASS | `wipe_right_evidence.json`, failed labels empty | PASS |

## Non-Activation Claims

```text
no_live_llm_api_phase_1433
phase_1433_no_public_serving
phase_1433_no_public_rc_publication
phase_1433_no_epoch_0_to_1_transition
phase_1433_no_cdl_mutation
phase_1433_no_production_graph_write
phase_1433_no_wallet_write
phase_1433_no_treasury_write
phase_1433_native_rust_p2p_not_activated
phase_1433_openclaw_gateway_not_publicly_activated
```

## Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_rehearsal_verdict_1433_v0.1.md
```
