# ILC Public RC Launch Gate: GAP-PUBLIC-RC-LAUNCH-00 Track B

**Phase:** GAP-PUBLIC-RC-LAUNCH-00  
**Track:** B, Public Mirror Push Authorization  
**Date:** 2026-08-17  
**Verdict:** PASS, publication package authorized for human-operated push and visibility flip  
**Source private commit:** `c5f8a5dab8f15ed493038f9a740b3d812cb086e3`
**Filtered public head SHA:** `563f8165edc629382cc89d18dd9421f0dd6fb7c8`
**Sanitized archive SHA-256:** `sha256:9ebeed34b71fec271c05b3685f081dbc8e714d680697af68cf91c4283a4f5301`

## 1. Authorization Record

Track A GO receipt in `docs/phases/STATUS.md`:

```text
GO Phase GAP-PUBLIC-RC-LAUNCH-00 TRACK-A VALIDATOR-NAMESPACE-RESET — received 2026-08-17T18:31:19Z
```

Track B GO receipt in `docs/phases/STATUS.md`:

```text
GO Phase GAP-PUBLIC-RC-LAUNCH-00 TRACK-B PUBLIC-MIRROR-PUSH — received 2026-08-17T19:17:32Z
```

Track B execution note: Codex regenerated and verified the sanitized public mirror artifact. Codex did not push to GitHub, did not create a public tag, and did not change repository visibility.

## 2. Input Token Census

| Token | Present | Confirmed |
|---|---:|---:|
| `window_1584_1593_closure_gate_verdict_pass` | yes | 1 |
| `public_rc_validator_db_contamination_disposition_committed_phase_1591_fix7` | yes | 1 |
| `public_rc_clean_reset_plan_only_committed_phase_1591_fix7` | yes | 1 |
| `public_rc_epoch1_ceremony_deferred_to_final_launch_phase_1591_fix7` | yes | 1 |
| `transfer_enabled_ilc_transfer_gate_committed_GAP_VALUE_ACTION_LIVE_RC_08` | yes | 1 |
| `ecu_transfer_public_rc_gate_committed_phase_gap_ecu_transfer_rc_05` | yes | 1 |
| `genesis_value_guard_runtime_committed_GAP_GENESIS_VALUE_02` | yes | 1 |
| `public_rc_epoch0_clean_validator_namespace_ready_phase_1591_fix7` | yes | 1 |
| `source_export_drift_reconciled_GAP_PUBLIC_RC_EXPORT_FIX_01` | yes | 2 |

## 3. Epoch-0 Namespace Readiness

Track A receipt: `out/public_rc_launch_00/track_a_validator_namespace_reset_receipt.json`.

| Validator | SSH host | Epoch | LMDB clean | Phase artifacts absent | Fresh namespace |
|---:|---|---:|---|---|---|
| 1 | `ilc-node-2` | 0 | true | true | `/var/lib/ilc/rc01/validator_1` |
| 2 | `ilc-node-2` | 0 | true | true | `/var/lib/ilc/rc01/validator_2` |
| 3 | `ilc-node-3` | 0 | true | true | `/var/lib/ilc/rc01/validator_3` |
| 4 | `ilc-node-6` | 0 | true | true | `/var/lib/ilc/rc01/validator_4` |

Launch namespace disposition: clean epoch-0 validator namespaces are ready. Old `phase1591_fix*` LMDB databases are not launch inputs.

## 4. Source Export Result

Command artifact: `/tmp/launch_00_export.json`.

| Field | Value |
|---|---:|
| `result` | `pass` |
| `included_files` | 522 |
| `excluded_files` | 7235 |
| `blocked_ambiguities` | 0 |
| `dependency_hits` | 0 |
| `marker_hits` | 0 |
| `marker_scan.result` | `pass` |
| `dependency_scan.result` | `pass` |
| Included/excluded intersection | 0 |

Execution finding and fix: the first Track B mirror attempt found one remaining public-mirror denylist hit in `tests/test_agent_keygen_cli_GAP_AGENT_KEYGEN_00.py`, where the private-key PEM marker appeared as a harmless test sentinel. Because the public mirror denylist rejects that literal string, commit `9463f1b7b` added that private-regression test to the mirror exclusion list and updated the Phase 1575n regression test. A post-Track-B audit then hardened the mirror wrapper at commit `c5f8a5dab` to require exact source-HEAD matching and safe output directories. The final audit mirror run used `c5f8a5dab8f15ed493038f9a740b3d812cb086e3` as the clean source head.

## 5. Mirror Regeneration Record

Receipt artifact: `/tmp/public_rc_launch_00_release_receipt.json`.

| Field | Value |
|---|---|
| `source_private_commit` | `c5f8a5dab8f15ed493038f9a740b3d812cb086e3` |
| `source_private_branch` | `main` |
| `private_worktree_clean` | true |
| `filtered_public_head_sha` | `563f8165edc629382cc89d18dd9421f0dd6fb7c8` |
| `archive_sha256` | `sha256:9ebeed34b71fec271c05b3685f081dbc8e714d680697af68cf91c4283a4f5301` |
| `staging_dir` | `/private/tmp/ilc-public-mirror-audit-c5f8a5dab8f1` |
| `denylist_scan_result` | `pass` |
| `public_rc_exclude_scan_result` | `pass` |
| `PUBLIC_RC_EXCLUDE` header hits in tracked mirror files | 0 |
| Denylist git-grep hits in tracked mirror files | 0 |
| Mirror worktree status lines | 0 |
| Mirror commit count | 3178 |
| `docs/PLANNING_INDEX.md` in mirror | absent by mirror policy |
| `docs/phases/` in mirror | absent by mirror policy |

The mirror was not hand-edited. It is a generated artifact from the exact private source commit named above.

## 6. Activation Matrix Reconciliation

The current source state column is based on direct source reads during Track B execution.

| Row | Surface | 1574 verdict | 1575b verdict | 1575b guard state | Current source state | Superseding phase/token | Launch disposition | Non-claims |
|---:|---|---|---|---|---|---|---|---|
| 5 | OBL-020 emission engine | `pending_private_economic_soft_rc_gate` | `public_rc_live` | `PRODUCTION_EMISSION_NOT_ACTIVATED=True` | `PRODUCTION_EMISSION_NOT_ACTIVATED=False` in `ilc_core/epoch/epoch_emission_production_path.py:48` | Phase 1575g economic guard clearance | Guard cleared; production emission path is live | No treasury, bounty, or validator reward activation from this row alone |
| 6 | CDL-048 ECU-to-ILC conversion | `pending_private_economic_soft_rc_gate` | `public_rc_live` | `CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED=True` | `CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED=False` in `ilc_core/ledger/conversion_candidate_runtime.py:24` | Phase 1575g economic guard clearance | Guard cleared; CDL-048 conversion runtime is live | CDL-057 witness gate still required for batch eligibility |
| 7 | OBL-021 validator admission/ejection | `pending_private_economic_soft_rc_gate` | `public_rc_live` | `VALIDATOR_ADMISSION_NOT_ACTIVATED=True` | `VALIDATOR_ADMISSION_NOT_ACTIVATED=True` in `ilc_core/validator/validator_admission_ejection_production_path.py:26` | None | Guard remains true; admission/ejection not live at RC | Requires dedicated sensitive activation |
| 8 | OBL-022 treasury/reward/ejected-stake | `pending_private_economic_soft_rc_gate` | `public_rc_live` | `TREASURY_DISTRIBUTION_NOT_ACTIVATED=True`; `EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED=True` | `TREASURY_DISTRIBUTION_NOT_ACTIVATED=True` in `ilc_core/epoch/treasury_validator_reward_production_path.py:34`; `EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED=True` in `ilc_core/epoch/ejected_stake_distribution_production_path.py:25` | None | Both guards remain true; distribution not live at RC | No treasury distribution or ejected-stake distribution |
| 9 | OBL-027 productive ECU expansion | `pending_private_economic_soft_rc_gate` | `public_rc_live` | `PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED=True` | `PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED=True` in `ilc_core/economics/productive_ecu_expansion_bounty_runtime.py:25` | None | Guard remains true; productive ECU expansion bounty not live at RC | No bounty payout activation |
| 20 | Production minting/economic settlement | `pending_private_economic_soft_rc_gate` | `public_rc_live` | All six guards true | Row 5 and row 6 guards are false; rows 7, 8, and 9 guards remain true; ILC transfer and ECU fast-path rows below are live | Phase 1575g, Phase 1592, LIVE-RC-08, ECU-RC-05 | Emission, conversion, wallet claimability, ILC transfer, and bounded ECU fast-path are live; treasury/admission/expansion remain guarded | No generalized ECU money transfer, external withdrawal, or unbounded minting |
| 21 | Epoch 0 to 1 transition | `pending_private_economic_soft_rc_gate` | `public_rc_live` | Epoch transition flags false | Deferred by `public_rc_epoch1_ceremony_deferred_to_final_launch_phase_1591_fix7` in STATUS.md | Phase 1591-Fix7 | Not part of this gate; deferred to final launch authority | No epoch transition in Track B |
| n/a | ILC agent-to-agent transfer | Not in 1574 matrix | Not in 1575b certificate | Not applicable | `ILC_TRANSFER_ENABLED=True` in `ilc_core/value_action/ilc_transfer_intent.py:22` | LIVE-RC-08, `transfer_enabled_ilc_transfer_gate_committed_GAP_VALUE_ACTION_LIVE_RC_08` | Live; bounded agent-to-agent settlement only | No external withdrawal, marketplace spend, or generalized transfer surface |
| n/a | ECU fast-path transfer | Not in 1574 matrix | Not in 1575b certificate | Not applicable | `ECU_FAST_PATH_TRANSFER_ENABLED=True` in `ilc_core/ecu/ecu_fast_path_intent.py:16` | ECU-RC-05, `ecu_transfer_public_rc_gate_committed_phase_gap_ecu_transfer_rc_05` | Live; bounded graph-contextual fast-path only | No generalized ECU money transfer |
| n/a | Genesis value guard | Not in 1574 matrix | Not in 1575b certificate | Not applicable | `genesis_value_guard_runtime_committed_GAP_GENESIS_VALUE_02` present in STATUS.md | GAP-GENESIS-VALUE-02 | Required guard present; Genesis-sourced transfers require policy certificate | Does not apply to ordinary agents |
| n/a | Werner Attribution Bridge | Not in 1574 matrix | Not in 1575b certificate | Not applicable | `WERNER_CREDIT_WIRING_NOT_ACTIVATED=False` in `ilc_core/economics/werner_runtime.py:35`; `WERNER_CREDIT_WIRING_NOT_ACTIVATED_cleared_GAP_WERNER_02b` present in STATUS.md | GAP-WERNER-02b | CDL-109 attribution reweighting bridge live with bounded cap | No Werner ECU minting; no CDL-096 production routing activation |
| 2 | ADR-0035 type registry | `default_off_at_public_rc` | unchanged | `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED` | `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED=True` in `ilc_core/bundle/type_registry.py:19` | None | Default-off at RC | No graph-loaded type authority activation |
| 3 | CDL-096 Werner flow-governor production | `default_off_at_public_rc` | unchanged | Runtime not activated | CDL-109 ratified; CDL-096 production routing/admission deferred to post-RC phases 1596 to 1598 | CDL-109 ratified; CDL-096 production remains blocked | Default-off except the CDL-109 attribution bridge row above | No Werner production routing at RC |
| 11 | Rust P2P bridge | `default_off_at_public_rc` | unchanged | `RUST_P2P_BRIDGE_NOT_ACTIVATED` | `RUST_P2P_BRIDGE_NOT_ACTIVATED=True` in `ilc_core/network/rust_p2p_bridge.py:18` | None | Default-off | No public P2P bridge activation |
| 13 | Public repository publication | `public_rc_live` | unchanged | Not applicable | This Track B gate passed | GAP-PUBLIC-RC-LAUNCH-00 Track B | Publication authorized for human-operated push and visibility flip | Codex did not push or flip visibility |
| 14 to 16 | OpenClaw, ClawHub, SKILL.md publication | `default_off_at_public_rc` | unchanged | Not applicable | `openclaw_clawhub_not_published_pending_phase_1575` disposition unchanged | None | Default-off | No OpenClaw or ClawHub publication |
| 19, 23 to 25 | Public P2P, public sidecar serving, third-party surfaces | `default_off_at_public_rc` | unchanged | Not applicable | No activating source change in Track B | None | Default-off | No public sidecar serving activation |
| 28 | CDL-093 maintenance lottery | `default_off_at_public_rc` | unchanged | CDL-093 | No activating source change in Track B | None | Default-off | No Werner lottery activation |
| 33 | CCSS cover/batching and public relay | `default_off_at_public_rc` | unchanged | Future guard | No activating source change in Track B | None | Default-off | No public relay or cover/batching activation |
| 36 | Sanitized public mirror maintenance | `public_rc_live` | unchanged | Not applicable | Mirror regenerated and scans passed | GAP-PUBLIC-RC-LAUNCH-00 Track B | Public mirror package authorized | Human push still pending |

## 7. Authorized Push Commands

Human operator commands authorized after reviewing this gate artifact. These commands are to
be run from the sanitized mirror staging repository, not from the private canonical repo:

```bash
cd /private/tmp/ilc-public-mirror-audit-c5f8a5dab8f1
git remote add foundation git@github.com:ILC-Foundation/ilc.git  # if not already set
git push foundation main
git tag v0.4-public-rc  # confirm exact tag with human reviewer before executing
git push foundation v0.4-public-rc
gh repo edit ILC-Foundation/ilc --visibility public
```

These commands were recorded as text only. Codex did not execute them.

## 8. OpenClaw and ClawHub Disposition

`openclaw_clawhub_not_published_pending_phase_1575` remains unchanged. GAP-PUBLIC-RC-LAUNCH-00 Track B does not publish OpenClaw, ClawHub, or SKILL.md public marketplace surfaces.

## 9. Epoch 0 to 1 Ceremony

Epoch transition remains deferred under `public_rc_epoch1_ceremony_deferred_to_final_launch_phase_1591_fix7`. Track B authorizes public mirror publication only.

## 10. Non-Claims

- No public push was executed by Codex.
- No repository visibility was changed by Codex.
- No epoch 0 to epoch 1 ceremony occurred.
- No CDL mutation occurred.
- No public P2P bridge activation occurred.
- No OpenClaw or ClawHub publication occurred.
- No external withdrawal path was activated.
- No generalized ECU money transfer was activated.
- No hand edits were made to the generated public mirror.

## 11. Output Tokens

The following tokens are authorized for `docs/phases/STATUS.md`:

```text
public_rc_mirror_regenerated_GAP_PUBLIC_RC_LAUNCH_00
public_rc_publication_authorized_GAP_PUBLIC_RC_LAUNCH_00
```
