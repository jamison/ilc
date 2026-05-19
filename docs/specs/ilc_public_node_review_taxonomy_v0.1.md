# ILC Public Node Review Taxonomy v0.1

**Phase:** 1393 / J-003
**Date:** 2026-05-19
**Status:** complete
**Scope:** taxonomy and planning artifact only

## Required Tokens

```text
public_node_review_taxonomy_phase_j003
private_draft_nodes_do_not_require_jury
reward_bearing_public_nodes_require_review_lane
subjective_panel_non_blocking_boundary_preserved
```

## 1. Purpose

This document defines which graph-submission classes require no jury review,
lightweight review, objective review, subjective / aesthetic review, escalated
jury review, specialized refutation / provenance review, or validator /
consensus evidence.

It consumes Phase 1391 / J-001 and ADR-0040. It does not implement runtime
review assignment, activate public ingestion, mutate CDLs, activate reviewer
payments, or authorize public graph canonicalization.

## 2. Claim Verification Table

| Claim | Source checked | Result |
|-------|----------------|--------|
| J-001 records objective / subjective split and no mandatory jury service | `docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md` | confirmed |
| ADR-0040 records opt-in eligibility and assignment boundaries | `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` | confirmed |
| CDL-052 mode routing exists, but Mode 3 auditor-review execution is incomplete | `docs/specs/ilc_cdl_052_epistemic_node_submission_runtime_handoff_477_v0.1.md`; `ilc_core/epistemic/node_submission_runtime.py`; Phase 477 tests | confirmed |
| CDL-059 aesthetic panel is informational-only and not objective truth | `docs/specs/ilc_cdl_059_aesthetic_panel_governance_ratification_evidence_531_v0.1.md`; `ilc_core/epistemic/aesthetic_panel_runtime.py` | confirmed |
| CDL-083 is a specific upheld-REFUTATION and ejected-stake quorum lane, not general jury economics | `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md`; `ilc_core/economics/epoch_attribution_settle_runtime.py`; Phase 1107 tests | confirmed |
| Public economics require public visibility and machine-checkable public graph admission evidence | `docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md`; `ilc_core/ledger/public_economics_admission_firewall.py`; Phase 1387a tests | confirmed |
| Private / local drafts are not public canonical nodes | Phase 1387a firewall, J-001 canon map, J-003 prompt discovery | confirmed |

## 3. Taxonomy Table

| Taxonomy ID | Submission class | Required review lane | Public economic eligibility | Boundary |
|-------------|------------------|----------------------|-----------------------------|----------|
| `T0_PRIVATE_LOCAL_DRAFT` | Private, local, operator-only, or harness-only draft node | No jury review required | None | Draft can exist privately without public graph admission, public canonical status, public reputation, protocol ECU, or claimability. |
| `T0_5_PENDING_PUBLIC_INGESTION` | Submitted with public intent but not yet admitted — content-addressed, requestable, zero weight | Schema validity check only | None — no ranking, no reward, no canonical status | Distinct from T0 (private): the agent has declared public intent but admission is pending. Serves as the submission quarantine state. Promoted to T1+ by the ingestion admission path. |
| `T1_PUBLIC_NON_REWARD_METADATA` | Public non-reward metadata, labels, pointers, receipts, or low-risk descriptive records | Lightweight schema / admission check | None unless later promoted to economic lane | Public visibility alone does not create reward. |
| `T2_REWARD_BEARING_OBJECTIVE_NODE` | Reward-bearing public objective knowledge node | CDL-052 / CDL-V7 objective review lane | Possible only after public admission and eligible public state | Must not bypass review lane. |
| `T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE` | Contested, high-value, safety-critical, or high-reward objective claim | 7+1 objective panel or escalated jury petition | Possible only after upheld/evaluated state and public admission | Uses ADM-003 panel shape and ADR-0040 anti-capture rules. |
| `T4_SUBJECTIVE_AESTHETIC_NODE` | Subjective, aesthetic, expressive, or taste-oriented node | CDL-059 aesthetic panel signal | No objective-truth or blocking effect | Informational-only, non-blocking, `not_objective_truth`. |
| `T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM` | Refutation, provenance, stake-affecting, or attribution-affecting claim | Specialized refutation / provenance / quorum lane | Only when lane-specific conditions hold | REFUTATION payout path is caller-filtered upheld-refutation under CDL-083; provenance attribution follows CDL-084 economics, not generic jury approval. |
| `T6_VALIDATOR_CONSENSUS_CLAIM` | Validator BFT certificate, epoch checkpoint, quorum certificate, topology endpoint, or consensus safety claim | Validator / formal evidence, not epistemic jury verdict | Not decided by jury taxonomy | BFT quorum certificates are consensus evidence, not 7+1 epistemic panel verdicts. |

Stable lane tokens:

```text
review_lane_private_draft_no_jury
review_lane_pending_public_ingestion_quarantine_zero_weight
review_lane_public_metadata_lightweight_admission
review_lane_reward_bearing_objective_requires_cdl052_cdlv7
review_lane_contested_high_value_requires_7_plus_1_or_escalation
review_lane_subjective_aesthetic_cdl059_non_blocking
review_lane_refutation_provenance_specialized
review_lane_validator_consensus_evidence_not_jury
```

## 4. Private / Public Boundary

Private and local drafts do not require jury review:

```text
private_draft_nodes_do_not_require_jury
```

Private drafts may be authored, revised, simulated, previewed, or discarded
without entering the public review system. They are not public canonical nodes.
They do not create public reputation, protocol ECU, public settlement rights,
public corroboration, public claimability, or public reward eligibility.

If a private draft is later promoted to public material, the public successor
must satisfy the active public admission and promotion-continuity rules. Private
timestamps, private commitments, or private draft history do not create
retroactive public reward priority.

Stable private-boundary phrase: Private timestamps, private commitments, or private draft history do not create retroactive public reward priority.

## 4.5 Pending Public Ingestion Quarantine (T0.5)

`T0_5_PENDING_PUBLIC_INGESTION` is the state between private draft (T0) and
publicly admitted non-reward metadata (T1). It is distinct from T0 in one
important way: the submitting agent has declared public intent. The content is
content-addressed, requestable by other agents (via D2D serve-credit path), and
permanently recorded by hash. But it has not yet passed the admission path and
carries no public weight.

```text
t0_5_pending_public_ingestion_has_zero_public_weight
t0_5_content_is_requestable_not_canonical
```

Properties of T0.5:

- **Content-addressed:** permanently retrievable by hash from any serving agent
  that has replicated it.
- **Zero public weight:** no public reputation, protocol ECU, public settlement,
  public corroboration, public claimability, or public canonical status.
- **No ranking / discovery effect:** T0.5 nodes do not influence search, routing,
  or recommendation until promoted.
- **No economic event construction:** Phase 1387a public-economics admission
  firewall applies; T0.5 nodes cannot construct public economic events.
- **Schema validity only:** the only check at T0.5 entry is schema conformance
  and basic CDL-V7 claim-form validity where applicable. No jury review.
- **Promotion path:** a T0.5 node may be promoted to T1+ by the ingestion
  admission path defined in ADR-0041. Promotion requires passing the relevant
  review lane for the target tier.
- **Copyright note:** storing verbatim content (e.g. a full PDF) at T0.5 may
  have different legal character than storing a hash, metadata, and extracted
  claims. The copyright/publication boundary is a counsel-gated decision routed
  to ADR-0041.

The submission quarantine design is: T0.5 is the default landing zone for any
"submit to network" action. Nothing in T0.5 is ephemeral or deniable — it is
permanently content-addressed — but nothing in T0.5 earns weight, ranking, or
reward until the appropriate review lane promotes it.

## 5. Public Metadata Boundary

Public non-reward metadata may use a lightweight schema / admission check when
it is descriptive and non-economic. Examples include public labels, pointers,
receipts, public package metadata, or non-economic references.

This lane does not bypass the public-economics admission firewall. If metadata
later becomes reward-bearing, claimable, reputational, settlement-bearing, or
canonical evidence for public economics, it must be routed to the appropriate
review lane before economic event construction.

Stable metadata-boundary phrase: If metadata later becomes reward-bearing, it must be routed to the appropriate review lane.

## 6. Reward-Bearing Objective Boundary

Reward-bearing public objective nodes require a review lane:

```text
reward_bearing_public_nodes_require_review_lane
```

The default lane is CDL-052 / CDL-V7 objective review. Current `mode_1` and
`mode_2` routing can classify ordinary submission and refutation-criterion
boundaries. `mode_3_boundary_detected` identifies anomaly / auditor-review
boundary conditions, but Mode 3 auditor-review execution remains incomplete and
must not be treated as a completed jury runtime.

No reward-bearing objective node may construct public ECU, public reputation,
public settlement, public corroboration, or public claimability events unless it
also satisfies the Phase 1387a public-economics admission firewall.

## 7. Contested / High-Value Objective Boundary

Contested, high-value, safety-critical, or high-reward objective claims require
stronger review than lightweight admission. The default target is ADM-003's
objective panel shape:

```text
panel_size=8
regular_reviewers=7
outsider_seat=true
reviewer_quorum=k=5 of m=7
independence_k=3
```

ADR-0040 anti-capture rules apply. Same-operator, same-SSH, same-control-plane,
same-custodian, or otherwise unseparated identities are not independent
reviewers for this lane.

Stable anti-capture phrase: same-operator identities are not independent reviewers.

Escalated jury-petition machinery remains future work unless a later phase
ratifies the petition / acknowledgment / verdict schema and economics.

## 8. Subjective / Aesthetic Boundary

Subjective panel outputs are non-blocking and must not be represented as
objective truth:

```text
subjective_panel_non_blocking_boundary_preserved
```

CDL-059 covers a narrow Register 2 aesthetic panel lane. The current runtime
labels outputs with `not_objective_truth: True` and `BLOCKING_AUTHORITY_ACTIVE =
False`.

Subjective / aesthetic signals may inform user-facing quality, taste, or
expressive-content metadata. They must not finalize objective truth, override
CDL-052 / CDL-V7 objective review, create consensus finality, or become a hidden
gate for public economic rights unless a future ratified lane explicitly
authorizes that use.

## 9. Refutation / Provenance / Stake-Affecting Boundary

Refutation, provenance, stake-affecting, and attribution-affecting claims are
specialized lanes.

REFUTATION:

- CDL-052 authored `refutation_criterion` routes ordinary refutation-capable
  submissions into `mode_2`.
- CDL-083 settles only caller-filtered upheld `REFUTATION` events.
- The payout recipient is the refuting agent, not the creator of the refuted
  target.
- CDL-083 does not ratify a general reviewer-payment system.

PROVENANCE:

- PROVENANCE attribution follows CDL-084 chain-attribution economics and
  provenance-chain validation.
- Provenance edge semantics are lineage / derivation semantics, not generic
  jury approval.
- Provenance payout does not imply that a subjective panel became objective
  truth.

Stake-affecting claims require the specific lane that governs the stake effect.
Generic jury terminology must not be used to bypass the relevant CDL, economic
firewall, or consensus guard.

## 10. Validator / Consensus Boundary

Validator and consensus claims are not epistemic jury verdicts.

Examples:

- epoch checkpoint certificate;
- BLS aggregate signature quorum;
- validator endpoint claim;
- topology epoch projection;
- TLA+ / TLC formal-methods evidence;
- persistent QUIC connectivity evidence.

These claims require validator BFT evidence, signed endpoint / identity evidence,
formal verification evidence, or production connectivity evidence as applicable.
They must not be described as 7+1 epistemic panel approvals.

Stable boundary:

```text
validator_bft_certificates_are_not_epistemic_jury_verdicts
```

## 11. Decision Procedure

A future implementation or operator guide should classify a submission in this
order:

1. If it is private, local, operator-only, or harness-only, classify as
   `T0_PRIVATE_LOCAL_DRAFT`.
2. If it has declared public intent but has not yet passed admission, classify as
   `T0_5_PENDING_PUBLIC_INGESTION` (quarantine state; zero weight).
3. If it has passed admission and is public but non-economic and descriptive only,
   classify as `T1_PUBLIC_NON_REWARD_METADATA`.
4. If it requests public reward, reputation, settlement, corroboration, or
   claimability, require public admission evidence and classify by claim type.
5. If it is objective and reward-bearing, classify as
   `T2_REWARD_BEARING_OBJECTIVE_NODE`.
6. If it is contested, high-value, safety-critical, or high-reward, classify as
   `T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE`.
7. If it is subjective / aesthetic, classify as `T4_SUBJECTIVE_AESTHETIC_NODE`.
8. If it is refutation, provenance, stake-affecting, or attribution-affecting,
   classify as `T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM`.
9. If it is validator or consensus evidence, classify as
   `T6_VALIDATOR_CONSENSUS_CLAIM`.

When a submission fits multiple classes, choose the stricter lane. Public
economic effect always requires the public-economics admission firewall.

## 12. Non-Authorizations

This phase authorizes no runtime mutation, no public graph admission activation,
no reviewer-payment activation, no CDL mutation, no public claimability
activation, no public economic event construction, no production jury activation,
no consensus activation, no source publication, no release signing, and no graph
write.

Stable non-authorization phrase: no public claimability activation.
Stable non-authorization phrase: no graph write.

## 13. Future Phase Routing

| Future phase | Relationship |
|--------------|--------------|
| J-004 / Phase 1394 | Designs reviewer incentives and non-response economics without paying solely per approval. |
| J-005 / Phase 1395 | Defines epoch-start capability and maintenance-work contracts. |
| J-006 / Phase 1396 | May implement default-off quote logic using this taxonomy and ADR-0040. |
| J-007 / Phase 1397 | May run a shadow public-ingestion jury harness without production activation. |
| J-008 / Phase 1398 | Defines production activation gates and must preserve all taxonomy non-claims. |

## 14. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_public_node_review_taxonomy_v0.1.md -> jury_epoch_work_canon
```
