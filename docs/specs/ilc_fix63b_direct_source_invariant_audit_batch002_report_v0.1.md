# ILC Fix63b Direct Source Invariant Audit Batch 002 Report v0.1

Status: applied_to_unified_lmdb  
Phase: 1545p-Fix63b  
Batch: 002  

## Scope

This batch direct-read the second ten `confirmed_support_stub` invariant rows
from the Fix63 ledger. The purpose is to replace weak proxy evidence, usually
`docs/phases/STATUS.md`, with concrete source, test, spec, and runtime evidence.

## Invariants Reviewed

| # | Invariant | Disposition |
|---:|---|---|
| 11 | `invariant:bridge_realism_exercise_no_native_p2p_implementation` | confirmed support trace |
| 12 | `invariant:bundle_and_registry_signature_fingerprint_mismatch_fails_closed` | confirmed support trace |
| 13 | `invariant:candidate_scoring_not_authority_human_objective_selection_boundary` | confirmed support trace |
| 14 | `invariant:canon_bundle_key_registry_empty_default_unknown` | confirmed support trace |
| 15 | `invariant:canon_bundle_sign_fails_closed_on_missing_or_invalid_key` | confirmed support trace |
| 16 | `invariant:canon_bundle_sign_no_overwrite_without_flag` | confirmed support trace |
| 17 | `invariant:canon_bundle_signing_repair_testing_snapshot_explicit_toggle_and_guardrails` | confirmed support trace |
| 18 | `invariant:canon_cli_output_deterministic` | confirmed support trace |
| 19 | `invariant:canon_cli_rejects_tampered_hash` | confirmed support trace |
| 20 | `invariant:canon_cluster_a_replay_proof_uses_shared_cli_error_module` | confirmed support trace |

## Direct Read Findings

1. Phase 472 bridge realism is an exercise/non-goal boundary. The source spec
   states no native P2P implementation and no decision-log mutation occurred.
   The test and tool evidence support a deterministic exercise, not a new
   authority-bearing rule.

2. The bundle and registry fingerprint invariant is governed by ADR-0009 and
   evidenced by Phase 284 handoff material, regression tests, and runtime
   signer/verifier/key-registry code.

3. The Fix9 candidate-scoring invariant is a non-authority boundary: candidate
   scoring is explicitly not authority, humans select objectives, and the
   evaluator rejects activation/economic claims.

4. The canon-bundle key registry, signing, CLI, and replay-proof invariants are
   support evidence under the ADR-0009 bundle/distribution stack. They should
   not be promoted to independent Genesis authority nodes.

## LMDB Recommendation

Apply the `recommended_new_edges` from
`docs/specs/ilc_fix63b_direct_source_invariant_audit_batch002_v0.1.json` via
`AtlasLmdbSafeWriter`. The edges are all `EVIDENCES` support edges from the
reviewed invariant node to the direct-read source/test/spec/runtime file node.

No new `GOVERNS` edge is recommended in this batch.

## LMDB Application

Applied via `AtlasLmdbSafeWriter` with safe-writer phase
`1545p-Fix63b-batch002`.

| Field | Value |
|---|---:|
| Semantic edges accepted | 28 |
| Semantic edges rejected | 0 |
| Phase/file nodes registered | 3 |
| File registration edges accepted | 6 |
| Post-application LMDB nodes | 16,352 |
| Post-application LMDB edges | 86,224 |
| Dangling edges after application | 0 |

## Non-Claims

This report does not authorize public RC, public publication, signing,
production minting, ECU settlement, or mutation of signed Genesis artifacts. It
is a support-trace evidence repair for the local Genesis Atlas LMDB.
