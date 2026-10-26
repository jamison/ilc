# ILC ECU Receipt-Rollup Implementation Spec - GAP-ECU-RECEIPT-ROLLUP-IMPLEMENTATION-SPEC-00 v0.1

**Phase:** GAP-ECU-RECEIPT-ROLLUP-IMPLEMENTATION-SPEC-00  
**Date:** 2026-10-14  
**Status:** Complete  
**Output token:** `ecu_receipt_rollup_implementation_spec_complete_GAP_ECU_RECEIPT_ROLLUP_IMPLEMENTATION_SPEC_00`

## 1. Purpose

This document turns the Row 21q activation-readiness blockers into concrete
implementation requirements for the ECU receipt-rollup lane. It is a spec for
future implementors, not runtime activation.

The design keeps the Row 21m conservation boundary intact: `receipt_nullifier`
is globally scoped and excludes `shard_id`; `shard_id` is provenance and proof
routing context, not a credit namespace. Bloom filters are permitted only as
performance prefilters before exact nullifier confirmation. Checkpoint roots are
candidate evidence for slow-path ILC settlement, not settlement themselves.

## 2. Canon Sources Read

- `docs/specs/ilc_ecu_fast_path_activation_readiness_00_v0.1.md`
- `docs/specs/ilc_ecu_fast_path_activation_readiness_00_v0.1.json`
- `docs/specs/ilc_ecu_sharded_receipt_rollup_spec_GAP_ECU_SHARDED_RECEIPT_ROLLUP_SPEC_00_v0.1.md`
- `docs/sims/sim_ecu_cross_shard_conservation_boundary_00_v0.1.md`
- `docs/sims/sim_ecu_trillion_event_batching_00_v0.1.md`
- `docs/sims/sim_ecu_adversarial_receipt_farming_00_v0.1.md`
- `docs/specs/ilc_cdl_066_agent_sender_authorization_ratification_evidence_708_v0.1.md`
- `docs/specs/ilc_cdl_108_backward_attribution_ratification_GAP_ECU_03_v0.1.md`
- `docs/specs/ilc_cdl_110_genesis_value_spend_guard_ratification_evidence_GAP_GENESIS_VALUE_01_v0.1.md`
- `docs/adr/ADR_0045_ILC_Native_QUIC_Submit_Frame_Format.md`

MemPalace was queried for `ECULocalReceipt receipt_nullifier challenge_window
durable queue Bloom exact nullifier store`. The useful authority came from the
direct-read artifacts above.

## 3. Non-Activation Boundary

This spec does not authorize runtime code, runtime tests, CDL mutation, CDL
opening, fast-path ECU activation, passive ECU activation, BLS signer
activation, slow-path ILC settlement changes, ECU minting, ILC minting, wallet
writes, monthly close, public mirror push, package publication, VPS mutation,
live graph/Atlas/LMDB writes, public-RC activation, mainnet activation, or epoch
transition.

`activation_authorized` remains `false`.
`fast_path_ecu_cdl_open_precondition_satisfied` remains `false`.

## S1 Durable Queue / Log Writer

**Row 21q references:** `durable_queue_log_backpressure_design`;
`durable_append_before_ack_and_idempotent_replay_gate`.

**Scope.** The durable queue accepts `ECULocalReceipt` candidates, persists them
before acknowledgement, and feeds checkpoint writers. It does not decide
economic eligibility, mint ECU, or write settlement state.

**Interface.**

- Input: canonical `ECULocalReceipt` body plus receipt bytes/hash.
- Output: durable queue record keyed by `receipt_nullifier` and
  `queue_record_id = sha256("ilc:ecu-queue-record:v1" || receipt_nullifier ||
  receipt_hash)`.
- Errors: `receipt_queue_full`, `receipt_queue_append_failed`,
  `receipt_queue_replay_conflict`, `receipt_queue_record_malformed`.

**Correctness invariants.**

1. A caller is acknowledged only after append durability is confirmed.
2. Queue capacity is bounded by explicit byte and record-count limits.
3. Overflow fails closed with `receipt_queue_full`; silent drop is forbidden.
4. Replay after restart is idempotent for the same `receipt_nullifier` and
   canonical receipt hash.
5. A replay with the same nullifier but different receipt hash is routed to
   challenge/adjudication rather than admitted as a second event.

**Implementation guidance.** Use an append-only write-ahead log segmented by
epoch and shard namespace. A checkpoint writer advances a durable offset only
after the receipt is either included, rejected with a stable reason, or routed
to challenge. Startup recovery scans unapplied records from the last durable
offset and replays them through exact nullifier reservation. Backpressure is an
explicit operator state, not a memory-growth accident.

## S2 Exact Global Nullifier Store With Atomic Reservation

**Row 21q references:** `exact_nullifier_store_false_positive_recovery_design`;
`atomic_nullifier_reservation_gate`.

**Scope.** The exact nullifier store is the value-bearing duplicate-suppression
authority for receipt admission. It is global across shards for a network and
projection family; it is not shard-local.

**Interface.**

- Input: `receipt_nullifier`, `projection_family`, source receipt hash,
  checkpoint/shard context.
- Output: one of `reserved`, `already_reserved_same_receipt`,
  `duplicate_conflict`, or `reservation_failed`.
- Errors: `nullifier_store_unavailable`, `nullifier_reservation_conflict`,
  `nullifier_record_malformed`, `nullifier_scope_mismatch`.

**Correctness invariants.**

1. Reservation is atomic check-and-insert, not check-then-insert.
2. `shard_id` is excluded from the uniqueness key.
3. A duplicate same receipt may feed availability diagnostics but never a second
   close-facing projection.
4. A same nullifier with conflicting receipt hash is challenge-routed.
5. Reservation commits before checkpoint inclusion.

**Implementation guidance.** The minimum shape is a transactional key-value
store keyed by `(network_id, projection_family, receipt_nullifier)`. A future
implementation may shard the physical database, but the logical keyspace
remains global. Use compare-and-swap, LMDB `put(nooverwrite=True)`, SQL
`INSERT ... ON CONFLICT`, or equivalent atomic semantics. Do not use a Bloom
filter, cache, or in-memory set as final authority.

## S3 Bloom Prefilter + Exact Recovery Boundary

**Row 21q references:** `bloom_prefilter_only_with_exact_recovery_gate`;
`exact_nullifier_store_false_positive_recovery_design`.

**Scope.** Bloom filters may reduce exact-store reads at high volume. They do
not decide admission, rejection, or credit.

**Interface.**

- Input: candidate `receipt_nullifier`.
- Output: `probably_seen` or `definitely_not_seen`, followed by exact-store
  confirmation in both cases.
- Errors: `bloom_prefilter_unavailable`, `bloom_exact_recovery_missing`,
  `bloom_used_as_authority`.

**Correctness invariants.**

1. Bloom hit always triggers exact-store lookup.
2. Bloom miss still triggers exact-store reservation before admission.
3. False positives cannot suppress valid receipts permanently.
4. Filter resets are not allowed to erase exact nullifier history.
5. Any code path treating Bloom membership as value authority fails closed with
   `bloom_used_as_authority`.

**Implementation guidance.** Row 21o modeled roughly `8193723` valid receipts
suppressed per shard/epoch at the modeled false-positive rate if Bloom were
used alone. Therefore Bloom is only a routing hint. The exact store is the
recovery path and must be available for all close-facing receipt admission.

## S4 Canonical Checkpoint Tree and Inclusion-Proof Verifier

**Row 21q references:** `canonical_checkpoint_tree_and_inclusion_proof_verifier_binding`;
`inclusion_proof_verifier_binding_gap`; `OQ1_canonical_hash_tree_choice`.

**Scope.** V1 uses a binary Merkle tree over ordered canonical receipt leaves:
`merkle_sha256_canonical_json_v1`. This section binds checkpoint roots to proof
verification. It does not activate settlement consumption.

**Interface.**

- Input: `ECUReceiptInclusionProof`, canonical receipt leaf bytes,
  `ECUShardCheckpoint.checkpoint_root`.
- Output: `inclusion_valid` or deterministic rejection.
- Errors: `invalid_inclusion_proof`, `unsupported_tree_algorithm`,
  `checkpoint_root_mismatch`, `leaf_hash_mismatch`, `proof_depth_exceeded`.

**Correctness invariants.**

1. Leaves are `sha256(canonical_json(ECULocalReceipt))`.
2. Leaf ordering is ascending `(receipt_nullifier, leaf_hash)` with bytewise
   comparison of lowercase hex strings.
3. Parent nodes are `sha256("ilc:ecu-merkle-node:v1" || left || right)`.
4. Odd leaves duplicate the final hash only at that level.
5. Verification is required before projection eligibility.

**Implementation guidance.** Binary Merkle is selected for v1 because Row 21o
showed individual proofs fit the ADR-0045 payload cap. Sparse Merkle and Verkle
remain future optimization candidates. Root construction over an ordered batch
is O(N) hash work; sorting and dynamic authenticated updates may be O(N log N).

## S5 Manifest Completeness and Root Binding

**Row 21q reference:** `manifest_root_completeness_and_receipt_root_binding_gate`.

**Scope.** The checkpoint manifest commits to the complete receipt/nullifier set
included in a checkpoint. It prevents selective omission of receipts relevant
to challenge or settlement consumption.

**Interface.**

- Input: checkpoint manifest, receipt root, nullifier root, status root,
  checkpoint root.
- Output: `manifest_complete` or deterministic rejection.
- Errors: `manifest_root_mismatch`, `manifest_receipt_count_mismatch`,
  `manifest_nullifier_count_mismatch`, `manifest_incomplete`.

**Correctness invariants.**

1. `receipt_count`, `unique_nullifier_count`, and status counts are root-bound.
2. Manifest entry order matches the tree leaf order.
3. A checkpoint root commits to receipt root, nullifier root, projection-claim
   root, source-evidence root, status root, and manifest hash.
4. A missing manifest or incomplete manifest makes the checkpoint ineligible.
5. Manifest validation precedes settlement-consumer proof selection.

**Implementation guidance.** Define
`checkpoint_root = sha256(canonical_json(checkpoint_root_preimage_v1))` where
the preimage includes all child roots and manifest metadata. Store large
manifests by CID if needed, but the manifest CID/hash must be root-bound.

## S6 Challenge-Window State Machine

**Row 21q references:** `challenge_window_state_machine_and_proof_protocol`;
`challenge_window_state_machine_gap`;
`challenge_rate_limit_deposit_and_priority_gate`;
`proof_availability_timeout_and_checkpoint_ineligibility_gate`;
`OQ5_exact_challenge_window_durations`.

**Scope.** The challenge state machine decides when a checkpoint is eligible
for downstream consumption. It does not mint, settle, or adjudicate wallets.

**Interface.**

- Input: `ECURollupChallenge`, checkpoint metadata, proof availability events.
- Output states: `open`, `response_submitted`, `upheld`, `dismissed`,
  `expired_unanswered`, `expired_resolved`.
- Errors: `challenge_window_closed`, `challenge_rate_limited`,
  `challenge_priority_invalid`, `challenge_proof_timeout`,
  `checkpoint_ineligible_open_challenge`.

**Correctness invariants.**

1. Candidate v1 duration is `16` issuance epochs from checkpoint publication.
2. The duration is a candidate spec value only; activation still requires the
   future fast-path CDL to cite this spec.
3. Open challenges block the affected receipt and may block the checkpoint
   segment referenced by the proof index.
4. Missing proof after timeout makes the affected checkpoint segment ineligible.
5. Challenge priority is deterministic: duplicate/nullifier conservation,
   invalid inclusion proof, proof unavailability, sender/Genesis missing,
   status misclassification, then private-boundary failures.
6. Deposits or cost controls are parameterized policy values, but zero-cost
   unbounded challenge flooding is forbidden.

**Implementation guidance.** Use a bounded challenge queue per checkpoint and a
global per-agent/per-nullifier opening cap. Deposit amounts, if economic, must
be exact integer or Decimal strings and must be ratified before activation.
Reputation can rank service order only after the mandatory sampling floor in
S12; it cannot suppress challenge eligibility.

## S7 Settlement-Consumer Proof Selection Rules

**Row 21q reference:** `settlement_consumer_proof_selection_rules`.

**Scope.** These rules describe what slow-path ILC settlement may consume from
the fast-path evidence lane once separately authorized. They do not change the
current settlement runtime.

**Interface.**

- Input: eligible `ECUShardCheckpoint`, manifest, inclusion proof samples,
  challenge-state snapshot.
- Output: `settlement_input_candidate` or rejection token.
- Errors: `settlement_checkpoint_not_final`, `settlement_open_challenge`,
  `settlement_manifest_missing`, `settlement_raw_receipt_flood_rejected`.

**Correctness invariants.**

1. Root-only trust is insufficient for close-facing settlement.
2. Raw receipt flood is rejected as an ADR-0045 anti-pattern.
3. Normal path consumes checkpoint root, manifest commitment, challenge closure,
   and sampled inclusion proofs.
4. Challenge path consumes targeted inclusion proofs and challenge outcomes.
5. Any open or unanswered proof-availability challenge excludes the affected
   segment from settlement consumption.

**Implementation guidance.** Settlement consumers should verify proofs in this
order: checkpoint identity and authority label, manifest/root binding,
challenge-window closure, nullifier uniqueness, inclusion proof, status
eligibility, sender/Genesis gates, and projection-family admissibility.

## S8 Sender-Authorization Proof Binding

**Row 21q references:** `sender_authorization_projection_gate_gap`;
`sender_authorization_and_genesis_policy_reference_proof_binding`.

**Scope.** Transfer-like or sender-intent receipts must reference
CDL-066-compatible sender authorization before projection eligibility.

**Interface.**

- Input: `sender_authorization_ref`, receipt canonical body, signer identity.
- Output: `sender_authorization_valid`.
- Errors: `sender_authorization_missing`,
  `sender_authorization_invalid`, `sender_authorization_scope_mismatch`.

**Correctness invariants.**

1. Sender authorization verification precedes quorum, execution, and projection
   eligibility.
2. Missing or invalid authorization rejects the receipt for close-facing use.
3. Authorization scope binds source event, subject, amount/weight commitment,
   epoch/window, and signer identity.
4. Authorization validity does not prove Sybil diversity or service quality.

**Implementation guidance.** The receipt stores `sender_authorization_ref` as a
CID/hash reference to the authorization artifact or proof receipt. A verifier
must fetch or receive the artifact during challenge/audit and recompute the
authorization preimage. Unknown sender-auth formats fail closed.

## S9 Genesis Policy-Reference Verification

**Row 21q references:** `genesis_policy_reference_projection_gate_gap`;
`sender_authorization_and_genesis_policy_reference_proof_binding`.

**Scope.** Genesis-sourced value receipts require a
`GenesisValueActionPolicyCertificate` reference per CDL-110.

**Interface.**

- Input: `genesis_value_policy_ref`, receipt body, policy certificate.
- Output: `genesis_policy_valid`.
- Errors: `genesis_policy_missing`, `genesis_policy_invalid`,
  `genesis_policy_window_mismatch`, `genesis_policy_recipient_mismatch`.

**Correctness invariants.**

1. Genesis-sourced value movement is projection-ineligible without a certificate.
2. Certificate policy window is bounded; CDL-110 records a maximum four-epoch
   inclusive policy window.
3. Recipient policy must satisfy the certificate's graph-context requirement.
4. Certificate verification is cached only by content hash and never by mutable
   path or operator memory.

**Implementation guidance.** Treat the policy reference as an immutable
content-addressed artifact. Cache hits must still compare certificate digest,
policy id, epoch window, action class, and recipient/subject constraints.

## S10 Receipt-Status Commitment and Transition Proof

**Row 21q references:** `receipt_status_integrity_gate_gap`;
`receipt_status_commitment_and_transition_proof_gate`.

**Scope.** Receipt status is committed in the checkpoint and later transitions
must be proof-bearing. Status relabeling cannot create credit.

**Interface.**

- Input: current receipt status, status root entry, optional transition proof.
- Output: `status_eligible` or rejection token.
- Errors: `receipt_status_mismatch`, `receipt_status_transition_missing`,
  `receipt_status_projection_ineligible`.

**Correctness invariants.**

1. `failed`, `partial`, `replayed`, and `superseded` are zero close-facing
   projection by default.
2. `succeeded` is candidate-only and still requires all other gates.
3. Status counts are manifest/root-bound.
4. Any post-checkpoint status change requires a transition proof referencing
   the prior committed status.
5. Relabeling without proof makes the receipt projection-ineligible.

**Implementation guidance.** Transition proofs should include previous status,
new status, reason, source evidence, actor key/ref, and prior checkpoint
context. They update eligibility through a new immutable node or sidecar proof,
not by mutating the original receipt.

## S11 Projection-Family Adjudication Hooks

**Row 21q reference:** `projection_family_adjudication_gap`.

**Scope.** Projection-family rules decide whether one source event may feed one
family, multiple composed families, or zero close-facing projection.

**Interface.**

- Input: `projection_family`, `economic_projection_class`,
  `projection_claim_id`, source event id, nullifier.
- Output: `projection_family_admitted`, `projection_family_composed`, or
  `projection_family_unresolved`.
- Errors: `projection_family_unknown`, `projection_family_collision`,
  `projection_family_governance_required`.

**Correctness invariants.**

1. Same source event plus same projection family has at most one
   `projection_claim_id`.
2. Cross-family claims require registry/adjudication before close-facing use.
3. Unknown or colliding families default to zero close-facing projection.
4. Composition rules must cite a ratified registry or later SENSITIVE CDL.

**Implementation guidance.** V1 defines the hook, not all thresholds. A
registry entry should name allowed source classes, composition behavior, caps,
and governing authority. Until the registry exists, unresolved families are
diagnostic/routing evidence only.

## S12 Economic Admissibility, Quality, Caps, Diversity, Novelty/Quality

**Row 21q references:** `receipt_economic_admissibility_and_service_quality_gate`;
`service_receipt_attempt_cap_and_value_evidence_gate`;
`sybil_diversity_and_independent_origin_gate`;
`root_committed_novelty_and_quality_evidence_gate`;
`global_nullifier_cap_and_admission_accounting_gate`;
`challenge_sampling_floor_independent_of_reputation_gate`.

**Scope.** This section prevents receipt volume from becoming value by itself.
It defines mandatory gates before close-facing projection.

**Interface.**

- Input: receipt, source/value evidence, diversity evidence, novelty/quality
  evidence root, admission counters, challenge sampling policy.
- Output: `economic_admissibility_candidate` or rejection token.
- Errors: `receipt_quality_evidence_missing`, `attempt_cap_exceeded`,
  `diversity_floor_unmet`, `novelty_quality_root_missing`,
  `global_nullifier_cap_exceeded`, `challenge_sampling_floor_missing`.

**Correctness invariants.**

1. Volume alone is never close-facing value evidence.
2. Service receipts require attempt caps and value-evidence thresholds.
3. Sybil diversity must require independent origin evidence beyond signatures.
4. Novelty/quality evidence must be root-committed and compatible with
   CDL-108 `hybrid_merkle_proof`.
5. Global caps count nullifiers across shards, not shard-local copies.
6. Every checkpoint has a reputation-independent challenge sampling floor.

**Implementation guidance.** Threshold values that affect economics are policy
parameters and should be exact integer or Decimal strings. If they cannot be
ratified in implementation, route them to a named governance phase before any
activation attempt. Challenge sampling should combine deterministic random seed
inputs from checkpoint roots with fixed minimum coverage.

## S13 Private/Public Proof Boundary and Shard-Membership Privacy

**Row 21q references:** `private_public_proof_boundary_gap`;
`private_public_proof_boundary_from_rows_21l_21n`;
`OQ3_private_topology_preserving_shard_membership`;
`OQ4_privacy_preserving_proof_eligibility`.

**Scope.** Private-local evidence may remain private until it is used for
public close-facing claims. At that boundary it needs disclosure, a public
anchor, or a named privacy-preserving proof class.

**Interface.**

- Input: evidence classification, shard id, public anchor/proof reference.
- Output: `public_proof_eligible`, `private_local_only`, or rejection token.
- Errors: `private_boundary_missing`, `private_proof_class_unknown`,
  `shard_id_topology_leak`, `public_anchor_missing`.

**Correctness invariants.**

1. Private-local evidence is not public evidence by assertion.
2. `shard_id` must be deterministic and opaque; it must not leak private
   topology, raw membership lists, or wallet balances.
3. Public close-facing use requires disclosure, content-addressed public anchor,
   or ratified privacy-preserving proof class.
4. Unknown privacy classes are projection-ineligible.

**Implementation guidance.** Use opaque shard keys derived from governed
namespace, epoch/window, and private salt/commitment where needed. Publish only
the shard id and proof commitments required for verification. Route unresolved
privacy-preserving proof classes to a later governance phase.

## S14 BLS Roster-Reference Format and Inactive Activation Boundary

**Row 21q references:** `bls_signer_roster_reference_and_activation_boundary`;
`OQ2_minimal_registered_fast_signer_scheme`.

**Scope.** This section defines the placeholder format for future shard-boundary
aggregate signatures. It does not activate BLS or threshold verification.

**Interface.**

- Input: checkpoint authority label, signer roster reference, aggregate
  signature reference if activated later.
- Output: `bls_roster_reference_well_formed` or rejection token.
- Errors: `bls_not_activated`, `bls_roster_ref_missing`,
  `bls_roster_bitmap_mismatch`, `fast_signer_scheme_unknown`.

**Correctness invariants.**

1. Current local receipt signer baseline remains registered Ed25519 where
   already authorized by surrounding lanes.
2. `threshold_bls_v1` and `bls_checkpoint_v1_planned_inactive` are labels only.
3. A roster reference is a content-addressed roster plus compact bitmap or
   equivalent inclusion set, not a full key list in every frame.
4. Any BLS verification path requires a later SENSITIVE activation phase.
5. Unknown signer schemes fail closed.

**Implementation guidance.** A roster reference should include roster CID,
roster epoch/window, signer count, threshold, compact participation bitmap,
aggregate signature ref, and governing activation token. Row 21o's payload
model prefers compact bitmap/reference shapes rather than large repeated key
lists.

## 4. Row 21q Coverage Summary

All 14 Row 21q scope items are covered by S1-S14:

1. durable queue/log writer and overflow recovery - S1
2. exact global nullifier store with atomic reservation - S2
3. Bloom prefilter plus exact recovery boundary - S3
4. canonical checkpoint tree and inclusion-proof verifier - S4
5. manifest completeness and root binding - S5
6. challenge-window state machine, proof availability, rate limits, and priority - S6
7. settlement-consumer proof selection rules - S7
8. sender authorization and Genesis policy-reference proof binding - S8 and S9
9. receipt status commitment and transition proof - S10
10. projection-family adjudication hooks - S11
11. economic admissibility, service quality, attempt caps, diversity floors,
    novelty/quality roots, and cap accounting - S12
12. private/public proof boundary and shard-membership privacy constraints - S13
13. BLS roster-reference format and inactive activation boundary - S14
14. exact challenge-window duration candidate - S6

## 5. Fast-Path CDL Preconditions

A future `GAP-ECU-FAST-PATH-CDL-OPEN-00` may cite this spec only after:

1. this output token is present;
2. the future implementation artifacts for S1-S14 exist or unresolved policy
   items are routed to a named SENSITIVE governance/CDL phase;
3. BLS activation remains false unless separately authorized;
4. settlement, wallet, minting, monthly close, public-RC, mainnet, and epoch
   claims remain absent unless their own gates are satisfied.

`fast_path_ecu_cdl_open_precondition_satisfied` remains `false` after this
phase.
