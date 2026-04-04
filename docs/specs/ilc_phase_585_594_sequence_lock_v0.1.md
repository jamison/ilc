# ILC Phase 585-594 Sequence Lock v0.1

Status: locked
Date: 2026-04-04
Phase: 585
Owner lane: G8 public-release constitutional closure

## 1. Window summary

Window 585-594 is the first explicit RC0.1+ public-release constitutional
closure lane.

It is not a generic continuation of the bounded RC0.1 testnet runtime lane. It
exists to close the missing public legitimacy surfaces around Genesis,
identity, quorum, settlement, and public-release honesty while preserving the
already-locked RC0.1 runtime and economic boundaries.

Required lock tokens:
- `rc0_1_plus_public_release_window_585_594_primary_gate`
- `public_release_not_equivalent_to_testnet_closure`
- `receipt_representation_cluster_precedes_public_runtime_integration`
- `genesis_authority_and_sunset_dependency_mandatory`
- `genesis_not_informal_founder_discretion`
- `cdl_v6_extraordinary_authority_only`
- `canonical_public_legitimacy_must_flow_through_genesis_rooted_lineage`
- `canonical_vs_fork_genesis_consequence_explicit`
- `public_namespace_receipt_disposition_must_be_explicit`
- `supporting_context_not_equal_canon`
- `no_public_release_claim_without_receipt_boundary_closure`
- `no_quota_miner_or_onboarding_inside_public_release_constitutional_lane`

## 2. Hard pass condition

Window 585-594 passes only if all of the following are true:
1. The public receipt and proof representation discipline is explicit and
   frozen before public-runtime integration is treated as authoritative.
2. Public identity activation authority is receipt-bound and canonical-lineage-
   bound.
3. Public quorum authority is receipt-bound and canonical-lineage-bound.
4. Settlement-linked public legitimacy is explicit, receipt-backed, and
   auditable.
5. Genesis authority and sunset posture are explicit, bounded,
   non-informal, and consistent with the Genesis-rooted public legitimacy
   lineage.
6. The public release-claim package states what remains non-mainnet-safe,
   curated, or constitutionally deferred.

`rc0_1_plus_public_release_window_585_594_primary_gate`.
`public_release_not_equivalent_to_testnet_closure`.
`receipt_representation_cluster_precedes_public_runtime_integration`.
`genesis_authority_and_sunset_dependency_mandatory`.
`canonical_public_legitimacy_must_flow_through_genesis_rooted_lineage`.
`no_public_release_claim_without_receipt_boundary_closure`.

## 3. Mandatory dependency bundle

Every Phase 585-594 artifact must carry the mandatory dependency bundle from
`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`.

Binding references for the window:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Minimum decision-log cluster for the window:
- `CDL-001`
- `CDL-002`
- `CDL-003`
- `CDL-004`
- `CDL-007`
- `CDL-009`
- `CDL-013`
- `CDL-022`
- `CDL-023`
- `CDL-040`
- `CDL-042`
- `CDL-045`
- `CDL-V6`

Supporting context bundle for the window, never equal canon by silence:
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
- `docs/specs/ilc_freshness_gate_contract_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.1.md`
- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `whitepaper/02_design_principles.md`

Supporting context may inform this window only when it is explicitly labeled as
supporting context or unresolved carry-forward. `supporting_context_not_equal_canon`.

## 4. Pre-lock blockers

The following blockers are mandatory before any public-release execution lock or
public release-claim may pass:
- receipt representation CDL cluster required before execution lock
- Genesis authority and sunset dependency note required before execution lock
- canonical-vs-fork Genesis consequence must be explicit before any public
  release-claim
- public operator honesty boundary must be explicit before closure
- supporting context may inform the window but may not be treated as equal
  canon by silence

`receipt_representation_cluster_precedes_public_runtime_integration`.
`genesis_authority_and_sunset_dependency_mandatory`.
`canonical_vs_fork_genesis_consequence_explicit`.
`public_namespace_receipt_disposition_must_be_explicit`.

## 5. Phase table

| Phase | Description | Primary output | Sensitive? |
|---|---|---|---|
| 585 | Window 585-594 sequence lock and dependency freeze | `ilc_phase_585_594_sequence_lock_v0.1.md` | No |
| 586 | Receipt representation CDL cluster | receipt-format CDL cluster | YES |
| 587 | Public identity activation and namespace authority boundary | public identity and namespace boundary lock | YES |
| 588 | Public quorum eligibility and Genesis-lineage authority boundary | public quorum authority boundary lock | YES |
| 589 | Settlement-linked public legitimacy and payout traceability | public settlement legitimacy lock | YES |
| 590 | Genesis authority, sunset, and fork-legitimacy coherence lock | Genesis/sunset coherence lock | YES |
| 591 | Public-runtime integration over the receipt boundary | public-runtime integration proof | YES |
| 592 | Public release-claim and operator honesty package | public RC package | YES |
| 593 | Coherence report and public-RC capsule update | report + capsule | No |
| 594 | Window 585-594 closure gate and handoff | gate script + handoff | YES |

## 6. Locked implementation decisions

The following decisions are locked for the full public-release window:
- Window 585-594 is the first public-release constitutional closure lane, not a
  generic continuation of testnet runtime work.
- public participation inseparability is the operative architectural target.
- Genesis-signed bootstrap artifacts remain the recursive self-anchor for
  public identity, public economic activation, and consensus bootstrap lineage.
- ordinary governance and `CDL-V6` extraordinary intervention remain distinct.
- `genesis_not_informal_founder_discretion`.
- `cdl_v6_extraordinary_authority_only`.
- local/private ILC use remains permitted outside public legitimacy.
- protocol-vs-harness boundary remains intact; post-582 harness/operator work
  is not part of public-release constitutional closure.
- the receipt-format cluster and namespace receipt disposition are top blockers
  before public-runtime integration may be treated as authoritative.
- non-equal-canon sources may be used only if labeled as supporting context or
  analysis.
- `canonical_public_legitimacy_must_flow_through_genesis_rooted_lineage`.
- `no_quota_miner_or_onboarding_inside_public_release_constitutional_lane`.

## 7. Protected boundaries and anti-pattern exclusions

The following exclusions are mandatory for Window 585-594:
- treating Genesis authority as informal founder discretion
- treating supporting-context artifacts as equal canon
- reopening the protocol-vs-harness boundary
- embedding a moving ledger root into every graph object
- deriving identity from transaction hashes
- pushing QuotaMiner, onboarding UX, or dashboard work into protocol closure
- treating RC0.1 testnet success as equivalent to public-release legitimacy
  closure

`genesis_not_informal_founder_discretion`.
`supporting_context_not_equal_canon`.
`no_quota_miner_or_onboarding_inside_public_release_constitutional_lane`.

## 8. Sequence integrity rule

Window 585-594 must execute in this order:
1. Phase 585 sequence lock and dependency freeze.
2. Phase 586 receipt representation CDL cluster.
3. Phase 587 public identity activation and namespace authority boundary.
4. Phase 588 public quorum eligibility and Genesis-lineage authority boundary.
5. Phase 589 settlement-linked public legitimacy and payout traceability.
6. Phase 590 Genesis authority, sunset, and fork-legitimacy coherence lock.
7. Phase 591 public-runtime integration over the receipt boundary.
8. Phase 592 public release-claim and operator honesty package.
9. Phase 593 coherence report and public-RC capsule update.
10. Phase 594 closure gate and handoff.

This ordering prevents public-runtime integration or public-release claims from
hardening against vague receipt semantics, silent Genesis privilege, or unclear
canonical-vs-fork legitimacy boundaries.
