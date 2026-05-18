# ILC Phase 1369 Window 1369-1390 Sequence Lock v0.1

**Status:** PASS - Window 1369-1390 is OPEN through Phase 1386a.
**Recorded:** 2026-05-16.
**Human authorization:** `GO Phase 1369`.
**Authority:** Sequence-lock and capsule phase only. This artifact authorizes the
Window 1369-1390 phase order and the non-sensitive Phase 1369 Fix1 hardening
slot. It does not authorize CDL opening, CDL mutation, `ilc_core/` runtime
mutation in Phase 1369, public activation, value-path activation, production
minting, public claimability, release signing, public source publication,
counsel approval, or legal conclusion.

```text
window_1369_1390_sequence_lock_committed_phase_1369.v0.1
capsule_v5_58_supersedes_v5_57
hardening_carry_forward_disposition_recorded_phase_1369
phase_1369_fix1_authorized_numeric_hardening
go_phase_1374_required_cdl_088_opening
go_phase_1389_required_public_claimability_gate
production_minting_activation_deferred_phase_1368
```

## 1. Verdict

Window 1343-1368 is closed by Phase 1368. Window 1369-1390 is now opened and
sequence-locked for public claimability governance, CDL-006/CDL-009 completeness,
security review scope and disposition planning, production connectivity proofing, accepted ADR/CDL
coverage review, and the eventual public-claimability gate.

The lock preserves the inherited Phase 1366 soft-RC verdict:
`soft_rc_eligible=false_with_blockers: [phase_1366_treasury_epoch_budget_binding_unverified]`.
Phase 1367 addressed that named blocker through
`phase_1366_treasury_epoch_budget_binding_verified`, but no later phase has
re-run the full gate or recorded `soft_rc_eligible=true`.

Production minting remains deferred by
`production_minting_activation_deferred_phase_1368`. CDL-088 remains unopened and
reserved for public-claimability authority. CDL-090 is the next fresh CDL number
for the identity bootstrap lane.

## 2. Source Basis

| Source | Result |
|--------|--------|
| `docs/antigravity_tasks/antigravity_prompt__phase_1369_g8_sequence_lock.md` | Phase 1369 prompt validated after moving the future Phase 1374 token into an absence check and adding Phase 1387a to the locked-order requirement. |
| `docs/specs/ilc_window_1343_1368_handoff_1368_v0.1.md` | Confirmed Window 1343-1368 closed, Window 1369 was not open before this phase, and production minting remained deferred. |
| `docs/phases/STATUS.md` | Confirmed Phase 1368 was the latest executed frontier before Phase 1369. |
| `docs/PLANNING_INDEX.md` | Confirmed pre-Phase-1369 frontier state and planning index update target. |
| `docs/specs/ilc_antigravity_context_capsule_v5.57.md` | Confirmed previous capsule baseline and supersession target. |
| `docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md` | Confirmed the candidate phase order, hardening assignments, 1387a public-economics firewall, and explicit GO gates. |
| `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md` | Confirmed forward-plan carry-forward entries for Window 1369-1390 and runtime hardening. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Confirmed CDL-089 ratified at row line 118, CDL-088 absent from the register and reserved by scoped Phase 1363 record, and CDL-090 absent as the next fresh number. |
| `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md` | Confirmed private or semi-private work does not create public ECU, public reputation, public settlement rights, public corroboration, or public claimability. |
| `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` | Confirmed "shadow economics" has been clarified as operator-local advisory scoring only, not protocol ECU generation. |

## 3. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1368 closed Window 1343-1368 and required `GO Phase 1369` before opening the next window | `docs/specs/ilc_window_1343_1368_handoff_1368_v0.1.md`; `docs/phases/STATUS.md` tail | confirmed |
| Production minting remains deferred | `production_minting_activation_deferred_phase_1368` in Phase 1368 handoff, STATUS, PLANNING_INDEX, and Phase 1369 prompt | confirmed |
| Soft RC eligibility remains false-with-blockers as the last full gate verdict | Phase 1366 report, Phase 1367 walkthrough, Phase 1368 handoff | confirmed; Phase 1367 fixed the named blocker but did not re-run the full gate |
| Capsule v5.57 is the previous context capsule | `docs/specs/ilc_antigravity_context_capsule_v5.57.md` | confirmed |
| CDL-089 is ratified | CDL register line 118 and scoped ratification record lines 180-188 | confirmed |
| CDL-088 is not open or ratified | Fixed-string register search for `| CDL-088 |`; scoped Phase 1363 record line 143 | confirmed absent from register; reserved for public-claimability authority |
| CDL-090 is the next fresh CDL number | Fixed-string register search for `| CDL-090 |`; CDL-089 last numbered row | confirmed absent |
| `cdl_088_not_ratified_phase_1374` is not a pre-existing Phase 1369 status token | Phase 1369 prompt and Phase 1374/1375 planned prompts | confirmed as a future Phase 1374 output or prerequisite for Phase 1375, not current canon |
| Phase 1360 gRPC proof did not exercise production TLS path | Phase 1360 Fix2a carry-forward in forward plan and candidate grouping | confirmed; Phase 1386a owns TLS proof |
| Phase 1360 Fix2 proof is injected-checkpoint/local-commit only | Phase 1360 Fix2a scope qualifier token and candidate grouping | confirmed |
| Runtime hardening item 1 has actual code targets | `_require_decimal_amount`, `_quantize_*`, and `_quantize_payout` in listed epoch/economic runtimes | confirmed |
| Runtime hardening items 2 and 4 have actual code targets | `genesis_intervention_runtime.py` line 321 append and line 427 read/evaluate/write | confirmed |
| Runtime hardening item 3 has actual code target | `ilc_core/analysis/governance_weight.py` lines 73, 109, 198 | confirmed |
| Runtime hardening items 5 and 6 have actual code target | `ilc_core/storage/lmdb_graph_pruning_runtime.py` line 154 and surrounding cursor loop | confirmed |
| Runtime hardening item 7 has actual code target | `ilc_core/consensus/production_bridge.py` lines 520-528 | confirmed |
| Runtime hardening item 8 has actual code targets | `_decimal_to_string()` dead branches in epoch/economic runtimes | confirmed |
| Private-node "shadow economics" cannot mean protocol ECU generation | ADR-0022 and node-schema synthesis clarification | confirmed; Phase 1387a must enforce public-only economic admission before activation |

## 4. Discovery Record

| Pass | Findings |
|------|----------|
| §0a Known-token audit | Required inherited tokens were found in Phase 1368 handoff, STATUS, PLANNING_INDEX, prompts, tests, and forward planning. The Phase 1374 non-ratification token was correctly classified as a future output, not a Phase 1369 prerequisite. |
| §0b Concept-discovery search | Broad search covered production minting, CDL-088, CDL-090, identity bootstrap, agent birth attestation, public claimability, replay nullifier, FastAPI public routes, sidecar query, CDL-048, CDL-006, CDL-009, external audit, TLA+ SafetyNoDualCert, genesis key ceremony, TLS gRPC, QUIC endpoint registry, hardening carry-forward, Decimal magnitude, shadow economics, and private ECU. |
| §0c Contradiction and non-claim search | Confirmed no public RC, public claimability, production minting, value-path activation, CDL-088 opening, CDL-090 opening, counsel approval, or legal conclusion is authorized by Phase 1369. |
| §0d Source expansion | Direct-read the Phase 1369 prompt, Phase 1368 handoff, STATUS, PLANNING_INDEX, capsule v5.57, CDL register, candidate grouping, forward plan, ADR-0022, node schema synthesis, and targeted runtime files referenced by the hardening table. |
| MemPalace | Not refreshed or relied on for this execution. Current-worktree direct reads are controlling; MemPalace remains advisory only for future historical retrieval. |

Phase 1385 addendum: SafetyNoDualCert wording now has an explicit scope split. The owned-object
fast-path Spec B invariant has bounded TLC evidence. The epoch-checkpoint/shared-object dual-cert
property was initially deferred with authority by `safetynodualcert_deferred_with_authority_phase_1385`.

Phase 1385a addendum (Strike Force, same session): The Phase 1385 deferral is CLOSED. Spec D
(`docs/specs/tla/ilc_epoch_checkpoint_safety.tla`) delivers a TLA+ model of the epoch-checkpoint
BFT round and was verified by TLC to full state-space exhaustion (67M states, 0 left on queue,
no violations). Token `safetynodualcert_spec_d_proven_epoch_checkpoint` supersedes the deferral.

Phase 1386 addendum: The old multi-operator ceremony slot was executed as a Genesis validator
bootstrap exception record after explicit `GO Phase 1386` and human acceptance of the exception.
`genesis_controlled_single_custodian_bootstrap_exception_phase_1386` is recorded, single-operator-compromise resistance is not confirmed, and
`production_split_custody_ceremony_required_before_mainnet_launch` is carried forward to
mainnet launch planning rather than inserted as a new Phase 1387/1388/1389 public-RC gate.

Phase 1386a addendum: The production TLS gRPC path proof is complete. The Rust optional
gRPC server now uses tonic TLS identity, Python `build_secure_grpc_read_stub()` uses
TLS roots plus a receive-size channel cap, `GetEpochChain(0,0)` is reconciled at genesis,
and hardening item 7 is closed by `get_epoch_chain_channel_limit_added_phase_1386a`.

## 5. Locked Phase Order

| Order | Phase | Scope | Authority after Phase 1369 |
|-------|-------|-------|----------------------------|
| 1 | 1369 | Sequence lock + Capsule v5.58; record hardening carry-forward disposition | COMPLETE by this artifact; SENSITIVE; no runtime or CDL mutation. |
| 2 | 1369 Fix1 | Numeric hardening pass: Decimal magnitude, genesis counter/audit log, governance bounds, LMDB pruning, dead branch cleanup | Authorized as NON-SENSITIVE hardening slot; prompt must be drafted and validated before execution; no public surface or value-path activation. |
| 3 | 1370 | Agent birth attestation ADR-0038 | NON-SENSITIVE ADR/spec work; prerequisite for CDL-090 deliberation. |
| 4 | 1371 | Identity bootstrap CDL-090 opening | SENSITIVE CDL mutation; requires explicit phase execution and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1371`. |
| 5 | 1372 | Identity bootstrap CDL-090 deliberation/prelock | SENSITIVE constitutional deliberation record. |
| 6 | 1373 | Identity bootstrap CDL-090 ratification | SENSITIVE CDL mutation; requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1373`. |
| 7 | 1374 | CDL-088 opening | SENSITIVE CDL mutation; requires separate explicit `GO Phase 1374` and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1374`. |
| 8 | 1375 | CDL-088 deliberation/prelock | SENSITIVE constitutional deliberation record. |
| 9 | 1376 | CDL-088 ratification | SENSITIVE CDL mutation; requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1376`. |
| 10 | 1377 | Replay/nullifier + duplicate-claim registry policy ADR | SENSITIVE claim-endpoint policy. |
| 11 | 1378 | Legacy `/v1/public/*` FastAPI route cleanup | SENSITIVE public-surface runtime cleanup. |
| 12 | 1379 | ADR-0031 sidecar query runtime completeness | SENSITIVE public-query runtime completion. |
| 13 | 1380 | CDL-048 ECU-to-ILC dry-run wiring | COMPLETE; gate-closed value-path dry-run wiring; records `cdl_048_dry_run_wiring_phase_1380`, `cdl_048_not_activated_phase_1380`, `gate_closed_state_confirmed_phase_1380`, and `double_entry_conservation_proven_wire_level_phase_1380`; no live activation. |
| 14 | 1381 | CDL-006 challenge node spec + stub | COMPLETE; records `cdl_006_challenge_node_spec_phase_1381`, `cdl_006_challenge_node_runtime_stub_phase_1381`, and `cdl_006_multi_body_3_body_quorum_spec_committed`; no production quorum verification, audit-path write, CDL mutation, or public activation. |
| 15 | 1382 | CDL-006 challenge node runtime + tests | COMPLETE; records `cdl_006_challenge_node_runtime_phase_1382.v0.1`, `cdl_006_3_body_quorum_verification_implemented`, and `cdl_006_audit_path_record_writer_implemented`; no challenge triggering, governance decision execution, graph state write, CDL mutation, public serving, or public activation. |
| 16 | 1383 | CDL-009 fork legitimacy UX | COMPLETE; records `cdl_009_fork_legitimacy_ux_phase_1383.v0.1`, `cdl_009_signature_badge_schema_implemented`, and `cdl_009_eligibility_rules_contract_committed`; CLI/operator-only inspection helper, no public API, graph write, CDL mutation, public serving, or governance activation. |
| 17 | 1384 | Security review scope record | COMPLETE; records `security_review_scope_recorded_phase_1384`, `audit_scope_bft_safety_economic_surfaces_high_001`, and `phase_1387_requires_project_authority_security_disposition`; commercial audit firm engagement is not required; Phase 1387 still requires project-authority disposition for every known HIGH finding. |
| 18 | 1385 | TLA+ SafetyNoDualCert disposition | COMPLETE; records `tla_plus_safetynodualcert_disposed_phase_1385`, `safetynodualcert_deferred_with_authority_phase_1385`, and `phase_1385_epoch_checkpoint_safetynodualcert_deferred_to_spec_d`; owned-object Spec B remains bounded TLC evidence, epoch-checkpoint/shared-object proof deferred — DEFERRAL CLOSED by Phase 1385a. |
| 18a | 1385a | Spec D epoch-checkpoint SafetyNoDualCert (Strike Force) | COMPLETE; `safetynodualcert_spec_d_proven_epoch_checkpoint`; TLC 67M states exhaustive, no violations; closes Phase 1385 deferral. |
| 19 | 1386 | Genesis validator bootstrap exception record | COMPLETE; SENSITIVE Genesis authority surface; records `genesis_validator_bootstrap_record_committed_phase_1386`, `genesis_controlled_single_custodian_bootstrap_exception_phase_1386`, `single_operator_compromise_resistance_not_confirmed_phase_1386`, and `production_split_custody_ceremony_required_before_mainnet_launch`; no split-custody claim, no private key material, no activation. |
| 20 | 1386a | Production TLS gRPC path proof | COMPLETE; records `production_tls_grpc_path_proven_phase_1386a`, `epoch_0_sentinel_reconciliation_verified_phase_1386a`, and `get_epoch_chain_channel_limit_added_phase_1386a`; no production activation. |
| 21 | 1386b | Validator endpoint registry ADR | NON-SENSITIVE ADR/spec; defines epoch-scoped `QUIC_ENDPOINT` graph edges and projection contract. |
| 22 | 1386c | Persistent QUIC connectivity proof | SENSITIVE consensus connectivity proof with direct + relay fallback. |
| 23 | 1387 | Pre-activation hardening gate | SENSITIVE gate; fails closed if audit/key/connectivity/hardening prerequisites are incomplete. |
| 24 | 1387a | Accepted ADR/CDL coverage audit + public-economics admission firewall | SENSITIVE gate/runtime phase; blocks Phase 1388/1389 unless public-only economics and accepted-functionality coverage are proven. |
| 25 | 1388 | CDL-048 activation + counsel clearance | SENSITIVE value-path/counsel phase; fails closed without Phase 1387a pass. |
| 26 | 1389 | Public claimability / API activation gate | SENSITIVE public-RC gate; requires explicit `GO Phase 1389`; `result=public_claimability_activated` may first appear here only if all blockers close. |
| 27 | 1390 | Window closure handoff | SENSITIVE closure handoff; records final window verdict. |

## 6. Runtime Hardening Carry-Forward Disposition

```text
hardening_carry_forward_disposition_recorded_phase_1369
phase_1369_fix1_authorized_numeric_hardening
```

| Severity | Finding | Location | Assignment |
|----------|---------|----------|------------|
| M | Huge finite `Decimal` values escape tokenized validation and can raise raw quantize exceptions at economic boundaries | `fee_burn_split_runtime.py:87`, `allocation_distributor_runtime.py:197`, `treasury_governance_runtime.py:107`, `ecu_price_clamp_runtime.py:105`, `validator_reward_pool_routing_runtime.py:168`, `epoch_attribution_settle_runtime.py:61` | Phase 1369 Fix1; add finite magnitude cap with stable error token before quantize. |
| M | Genesis intervention counter TOCTOU around read/evaluate/write | `genesis_intervention_runtime.py:427` | Phase 1369 Fix1; lock full read/evaluate/write critical section. |
| M | Governance weight accepts unbounded `quality_score`, `base_weight`, `contribution_bonus`, and `genesis_baseline_weight` | `ilc_core/analysis/governance_weight.py:73`, `:109`, `:198` | Phase 1369 Fix1; document trusted pre-normalization contract or add bounds, including at minimum `quality_score <= 1`. |
| L/M | Genesis intervention audit log append is non-atomic | `genesis_intervention_runtime.py:321` | Phase 1369 Fix1; pair with counter lock so audit append cannot interleave. |
| L/M | LMDB pruning batch cap counts total scanned cursor entries instead of eligible tier-2 records | `lmdb_graph_pruning_runtime.py:154` | Phase 1369 Fix1; adjust cap semantics or add prunable-record counter. |
| L | LMDB pruning opens a write transaction in `dry_run=True` | `lmdb_graph_pruning_runtime.py:154` | Phase 1369 Fix1; use read transaction for dry run. |
| L | `get_epoch_chain()` materializes response records before enforcing `max_epoch_chain_records` | `production_bridge.py:526` | CLOSED by Phase 1386a; added gRPC receive-size channel limit and bounded response iteration. |
| L | `_decimal_to_string()` contains identical return branches in seven epoch/economic runtimes | Seven epoch/economic runtimes | Phase 1369 Fix1; clean up as behavior-preserving maintenance. |

## 7. Public-Only Economics and Private-Shard Boundary

Historical "shadow economics" phrasing is clarified as operator-local advisory
scoring only. It is not protocol ECU, does not create public reputation, does not
settle publicly, does not count as public corroboration, and does not create
public claimability.

Phase 1387a must prove or implement a fail-closed public-economics admission
firewall before Phase 1388 or Phase 1389 can unlock public value-path or public
claimability behavior. Public economic events must require public node
visibility, public graph admission evidence, eligible evaluation or promotion
state, and no carry-forward of private reputation or corroboration reuse.

## 8. Gate Requirements

```text
go_phase_1374_required_cdl_088_opening
go_phase_1389_required_public_claimability_gate
```

Phase 1374 requires an explicit future `GO Phase 1374` even though this sequence
lock schedules it. CDL-088 must not open in any earlier phase.

Phase 1389 requires an explicit future `GO Phase 1389`. The token
`result=public_claimability_activated` may first appear in Phase 1389 only, and
only if all predecessor blockers and Phase 1387a public-economics/coverage tokens
are confirmed.

## 9. Stop Conditions

Any later phase in this window must stop and route to human review if any of the
following is discovered:

- A phase attempts CDL-088 opening before Phase 1374 or without explicit `GO Phase 1374`.
- A phase attempts public claimability activation before Phase 1389 or without explicit `GO Phase 1389`.
- A phase treats private, semi-private, or operator-local advisory scores as protocol ECU, public reputation, public settlement, public corroboration, or public claimability.
- A phase treats Phase 1360 Fix2 as durable peer-to-peer BFT proof rather than injected-checkpoint/local-commit proof.
- A phase treats public gRPC serving or production validator deployment as activated by Phase 1386a.
- A phase opens production minting, production mining, live ECU transfer routing, public RC publication, release signing, public source publication, or value-path activation without a later explicit gate.
- A phase claims `soft_rc_eligible=true` without re-running and passing the full gate after Phase 1367 evidence.
- A phase treats a commercial signed audit report as required after Phase 1384 rather than the project-authority security disposition gate.
- A phase treats the Phase 1384 scope record as satisfying the Phase 1387 disposition requirement.
- A phase finds any accepted ADR or ratified CDL public-RC obligation without implementation, explicit public-RC deferral authority, or a routed phase before Phase 1389.

## 10. Non-Authorization Floor

Phase 1369 did not modify runtime source, open any CDL, ratify any CDL, activate
production minting, activate public claimability, activate wallet/ECU/ILC value
paths, approve counsel/legal conclusions, publish source publicly, sign release
artifacts, or run a public RC gate.

Graph delta:
`graph_delta=support_only:docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md -> planning/frontier`.
