# ILC CCSS-004 Gossip Jitter Cover Policy Tests

**Phase:** 1327
**Status:** Implemented as a private/local contract and focused test suite
**Version token:** `ccss_004_gossip_jitter_cover_policy_tests_phase_1327.v0.1`

## Purpose

Phase 1327 records the CCSS-004 private/local boundary for gossip announce/pull coordination, bounded jitter, bounded batching, cover-policy enforcement, and traffic-analysis negative tests.

This is not a public transport activation. It does not create public P2P, public relay serving, public confidential coordination serving, public confidential messaging, public peer discovery, or an anonymity guarantee.

## Implemented Surface

The implementation lives at `ilc_core/sidecars/confidential_coordination_gossip_policy.py`.

It defines three local record shapes:

| Record | Role |
|---|---|
| `traffic_analysis_matrix_ref` | Records the adversary-observation matrix, tested mitigation, evidence artifact, residual risk, and exact non-claim for each row. |
| `gossip_announce_pull_policy_ref` | Records private/local bounded announce metadata, receiver-controlled pull, bounded jitter, bounded batching, required cover policy, and no-anonymity boundary. |
| `gossip_cover_policy_decision` | Records fail-closed local decisions for allowed private/local announce or pull states and rejected public-network, deterministic-runtime-seed, participant-metadata, disabled-cover, and unbounded-batch attempts. |

All records use canonical JSON with sorted keys, `allow_nan=False`, bounded payload depth, bounded payload nodes, a pre-serialization byte budget, positive epochs, positive sequences where applicable, hash-bound references, false authorization flags, and private-field disclosure rejection.

## Announce/Pull Policy

The private/local policy records:

| Field | Required value |
|---|---|
| `announce_scope` | `private_local_opaque_availability_only` |
| `push_payload_class` | `bounded_metadata_ref_only` |
| `pull_payload_class` | `heavy_payload_receiver_controlled` |
| `receiver_controlled_pull` | `True` |
| `batching_mode` | `bounded_epoch_batch` |
| `cover_policy_mode` | `idle_cover_required` |
| `min_jitter_epochs` | `0` |
| `max_jitter_epochs` | `3` |
| `runtime_jitter_source` | `secure_random_or_ratified_vrf_required` |
| `test_fixture_jitter_derivation` | `sha256_domain_separated_epoch_ref_fixture_only` |

The deterministic jitter helper is explicitly a test fixture. It is not a runtime scheduling source and does not import or use predictable PRNG.

## Traffic-Analysis Matrix

The required matrix rows are:

| Adversary observation | Tested mitigation | Residual risk | Exact non-claim |
|---|---|---|---|
| `sender_timing_correlation_against_local_enqueue_time` | `bounded_release_jitter_epochs` | `metadata_correlation_reduced_not_eliminated` | `does_not_claim_anonymity_or_unlinkability` |
| `receiver_timing_correlation_against_local_delivery_time` | `receiver_controlled_pull_window` | `metadata_correlation_reduced_not_eliminated` | `does_not_claim_anonymity_or_unlinkability` |
| `batch_size_leakage_across_shards` | `bounded_epoch_batching` | `metadata_correlation_reduced_not_eliminated` | `does_not_claim_anonymity_or_unlinkability` |
| `cover_message_absence_during_idle_periods` | `idle_cover_messages_required` | `metadata_correlation_reduced_not_eliminated` | `does_not_claim_anonymity_or_unlinkability` |
| `retry_burst_correlation_after_failed_delivery` | `retry_burst_coalescing_required` | `metadata_correlation_reduced_not_eliminated` | `does_not_claim_anonymity_or_unlinkability` |
| `shard_header_correlation_across_announce_pull_cycles` | `opaque_shard_header_ref_only` | `metadata_correlation_reduced_not_eliminated` | `does_not_claim_anonymity_or_unlinkability` |
| `harness_identity_leakage_through_adapter_metadata` | `adapter_identity_metadata_forbidden` | `metadata_correlation_reduced_not_eliminated` | `does_not_claim_anonymity_or_unlinkability` |

A row can be marked `not_tested_carry_forward` when needed, but Phase 1327's focused tests record every required row as `tested_local_negative`.

## Negative Boundaries

The tests reject or fail closed for:

| Condition | Result |
|---|---|
| Zero max jitter | `ccss_004_zero_jitter_forbidden_phase_1327` |
| Disabled cover policy | `ccss_004_cover_policy_disabled_phase_1327` |
| Deterministic runtime jitter seed | `ccss_004_runtime_jitter_seed_forbidden_phase_1327` or rejected decision state |
| Unbounded batch growth | `ccss_004_unbounded_batch_forbidden_phase_1327` or rejected decision state |
| Public network configuration | `ccss_004_public_network_forbidden_phase_1327` or rejected decision state |
| Participant-identifying metadata fields | `ccss_004_private_key_field_forbidden_phase_1327`, `ccss_004_private_value_disclosure_forbidden_phase_1327`, or rejected decision state |

## Registry Integration

The sidecar registry now records `confidential_coordination_gossip_jitter_cover_policy` under `phase_1327_private_local_contract_only`.

The confidential coordination local-preview profile now requires CCSS-001, CCSS-002, CCSS-003, and CCSS-004.

## Required Tokens

```text
ccss_004_gossip_jitter_cover_policy_tests_phase_1327.v0.1
gossip_announce_pull_jitter_policy_recorded_phase_1327
traffic_analysis_negative_tests_recorded_phase_1327
anonymity_guarantee_not_claimed_phase_1327
phase_1328_ccss_private_droplet_reproducibility_next
public_rc_remains_blocked_after_phase_1327
```

## Non-Authorization

Phase 1327 does not authorize public RC, public source export, public repository publication, package publication, release artifact production, release keys, signing, Genesis/Atlas mutation or signing, CDL mutation, identity artifacts, seed commitments, wallet writes, ECU minting, ILC settlement, value-path activation, public P2P, public fetch serving, public listener, peer discovery, public relays, public sidecar/projection serving, public confidential messaging, public confidential coordination serving, anonymity, unlinkability, Signal-equivalent claims, or public bootstrap claims.

## Next Phase

`phase_1328_ccss_private_droplet_reproducibility_next`
