# ILC Replay Nullifier And Duplicate-Claim Registry Policy 1377 v0.1

**Phase:** 1377
**Date:** 2026-05-18
**Status:** POLICY COMMITTED / NO RUNTIME ACTIVATION
**Authority basis:** CDL-088 ratification, CDL-090 ratification, CDL-027 issuance epoch cadence, Phase 1275 proof-binding boundary, Phase 1305 local verifier boundary

```text
replay_nullifier_policy_committed_phase_1377
nullifier_epoch_bounded_expiry_policy_defined
duplicate_claim_rejection_policy_defined
claim_endpoint_not_activated_phase_1377
replay_nullifier_policy_required_before_live_claim_endpoint
```

---

## 1. Policy Verdict

Phase 1377 defines the replay/nullifier and duplicate-claim registry policy
required before any future public claim endpoint may activate.

This phase is policy-only. It does not implement a nullifier runtime, does not
open a public claim endpoint, does not enable a public verifier API, does not
activate public claimability, does not authorize wallet actions, does not mint
ECU, does not settle ILC, and does not modify `ilc_core/`.

The policy may be consumed by a later implementation phase, but a later
implementation must still receive explicit activation authority before any
non-loopback or public serving path can accept public claim presentations.

---

## 2. Pre-Execution Claim Verification

| Claim | File or symbol checked | Result |
| --- | --- | --- |
| Phase 1376 completed and CDL-088 is ratified. | `docs/phases/STATUS.md`; `docs/specs/ilc_constitutional_decision_log_v0.1.md`; `docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md` | confirmed |
| CDL-090 is ratified. | `docs/specs/ilc_constitutional_decision_log_v0.1.md`; `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md` | confirmed |
| No existing current token records a completed public claim nullifier policy. | repo search for `replay_nullifier_policy_exists` and `nullifier_storage_defined` | not found |
| Existing claimability verifier is local-only and not a public API. | `ilc_core/sidecars/claimability_receipt_verifier.py`; `docs/specs/ilc_offline_claimability_receipt_verifier_sidecar_1305_v0.1.md` | confirmed |
| Existing verifier records replay/nullifier and duplicate-claim registry as public-mode blockers. | `ilc_core/sidecars/claimability_receipt_verifier.py` `_PUBLIC_MODE_BLOCKERS` | confirmed |
| No active public claim endpoint exists. | repo search for public claim endpoint activation terms, `public_claimability_activated`, and claimability API terms | confirmed |
| Epoch-bounded expiry must use protocol epochs, not wall-clock time. | `docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md`; `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md` | confirmed |
| Claimability proof bundle already includes proof, conversion, root, receipt, and epoch refs. | `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md`; `ilc_core/sidecars/claimability_receipt_verifier.py` | confirmed |

MemPalace was used only as advisory retrieval. Relevant returned paths were
direct-read before being used as authority.

---

## 3. Definitions

| Term | Policy meaning |
| --- | --- |
| `claim presentation` | A future public claimability request envelope submitted to a public API after separate activation authority. |
| `claim seed` | The canonical public input digest from which the nullifier is derived. It is not a secret seed and must not contain private graph content, wallet secrets, private lineage, or witness material. |
| `claim_nullifier_v1` | A domain-separated SHA-256 commitment proving a specific claim presentation has already entered public claim admission. |
| `duplicate claim` | A claim presentation that reuses an active nullifier or conflicts with an active conversion lot, conversion receipt, or claimability proof already admitted for the same public claim window. |
| `replay` | A duplicate, resubmitted, or semantically equivalent claim presentation that attempts to reuse the same public claim input after the admission layer has already accepted or reserved it. |
| `active nullifier` | A registry entry whose status is `pending` or `accepted` and whose `expires_at_issuance_epoch` is greater than or equal to the current issuance epoch. |
| `expired nullifier` | A registry entry past its deterministic issuance-epoch expiry. Expiry does not make an expired underlying claim valid; it only ends the active duplicate-claim block. |

---

## 4. Replay Definition

A future public claim endpoint must treat a presentation as a replay if any of
the following conditions is true at API admission time:

1. The derived `claim_nullifier_v1` already exists as an active registry entry.
2. The same `presentation_id` has already been admitted in the active window.
3. The same `claimability_proof_ref` has already been admitted in the active
   window for the same canonical agent identity.
4. The same `conversion_receipt_sha256` has already been admitted in the active
   window, regardless of wrapper or transport metadata.
5. The same `conversion_lot_id` has already been admitted in the active window
   for the same canonical agent identity.
6. A modified presentation changes non-semantic envelope fields but preserves
   the same claim seed.
7. A presentation reuses claim material after its conversion or claim window is
   closed.

Replay means duplicate public claim admission. It does not mean packet
retransmission, local verifier re-run, local preview, rate limiting, or a user
retry that never reaches public admission.

---

## 5. Nullifier Construction

Nullifiers use the following versioned construction:

```text
nullifier_version = claim_nullifier_v1
nullifier_domain = ilc-public-claim-nullifier-v1
nullifier_ref = claim_nullifier_sha256:<64 lowercase hex sha256>
```

The hash input is canonical JSON over this exact public-safe object shape:

```json
{
  "canonical_agent_identity": "<agent_id>",
  "claim_epoch": "<issuance_epoch>",
  "claim_window_end_epoch": "<issuance_epoch>",
  "claim_window_start_epoch": "<issuance_epoch>",
  "claimability_proof_ref": "claimability_proof_sha256:<sha256>",
  "conversion_deadline_epoch": "<issuance_epoch>",
  "conversion_issuance_epoch": "<issuance_epoch>",
  "conversion_lot_id": "<lot-id>",
  "conversion_receipt_sha256": "<sha256>",
  "domain": "ilc-public-claim-nullifier-v1",
  "latest_balance_receipt_ref": "balance_receipt_sha256:<sha256>",
  "presentation_id": "claimability_presentation_sha256:<sha256>",
  "public_economics_admission_ref": "<phase-1387a-or-successor-ref>",
  "settled_runtime_root": "settled_runtime_sha256:<sha256>",
  "transport_principal_ref": "<public-transport-principal-ref>",
  "version": "claim_nullifier_v1",
  "wallet_state_root": "wallet_state_sha256:<sha256>"
}
```

The canonical JSON serializer must use deterministic key ordering, compact
separators, and non-finite numeric rejection:

```text
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

All epoch fields are protocol issuance-epoch integers or canonical
issuance-epoch identifiers. The nullifier object must not use wall-clock time,
timestamps, random nonces, private graph payloads, private lineage material,
wallet secrets, private keys, mnemonics, recovery shares, ZK witnesses, or
operator-local advisory scores.

---

## 6. Nullifier Storage Policy

The future public claim endpoint must persist nullifiers in a logical public
claim nullifier registry:

```text
claim_nullifier_registry_v1
```

The registry is a protocol admission state surface. A later implementation may
use LMDB, a registry table, or an append-only graph/admission projection, but
the logical record shape must preserve these fields:

| Field | Requirement |
| --- | --- |
| `claim_nullifier_ref` | Required `claim_nullifier_sha256:<64 lowercase hex sha256>`. |
| `claim_seed_ref` | Required hash ref over the canonical nullifier input object. |
| `canonical_agent_identity` | Required public agent identity governed by CDL-090. |
| `presentation_id` | Required public-safe presentation id. |
| `claimability_proof_ref` | Required proof ref. |
| `conversion_receipt_sha256` | Required conversion receipt hash. |
| `conversion_lot_id` | Required conversion lot id. |
| `claim_window_start_epoch` | Required issuance epoch. |
| `claim_window_end_epoch` | Required issuance epoch. |
| `first_seen_issuance_epoch` | Required issuance epoch when API admission reserved the nullifier. |
| `expires_at_issuance_epoch` | Required issuance epoch computed by this policy. |
| `status` | One of `pending`, `accepted`, `rejected_nonblocking`, or `expired`. |
| `decision_ref` | Optional public-safe decision ref after processing completes. |

The registry must be updated by an atomic insert-if-absent operation before any
expensive verifier, wallet, ECU, ILC, or settlement processing. The atomic
operation must reject an already-active nullifier at the API layer.

Invalid unauthenticated garbage must not create a blocking nullifier. A future
implementation must authenticate the transport principal and canonical agent
identity, parse a bounded public-safe envelope, and derive the nullifier before
reservation. Failed presentations that do not pass that minimum admission shape
may be logged or rate-limited, but they must not reserve a duplicate-claim
nullifier.

---

## 7. Epoch-Bounded Expiry

Nullifier expiry is issuance-epoch based and never wall-clock based.

CDL-027 ratifies monthly issuance epochs with:

```text
issuance_epoch_cadence_cdl_027_one_month
H = 48
```

Phase 1377 defines:

```text
CLAIM_NULLIFIER_POST_WINDOW_RETENTION_EPOCHS = 1
```

The expiry rule is:

```text
expires_at_issuance_epoch =
  max(claim_window_end_epoch, conversion_deadline_epoch)
  + CLAIM_NULLIFIER_POST_WINDOW_RETENTION_EPOCHS
```

The endpoint must reject a claim if the underlying conversion or claim window is
closed, regardless of whether a historical nullifier has expired. Nullifier
expiry only bounds duplicate-claim registry retention. It does not reopen public
claimability after the claim window closes.

A later implementation may keep compacted hash-only audit records after expiry,
but active duplicate-claim rejection must be governed only by protocol issuance
epochs.

This records:

```text
nullifier_epoch_bounded_expiry_policy_defined
```

---

## 8. API-Layer Duplicate-Claim Rejection

Duplicate-claim rejection must happen at the public API admission layer before deeper claim verification or economic processing.

A future endpoint must process a public claim presentation in this order:

1. Enforce request size, shape, and public-safe disclosure bounds.
2. Authenticate the public transport principal and bind it to the canonical
   agent identity.
3. Verify that public claimability activation authority is present.
4. Verify that the Phase 1387a or successor public-only economics admission
   evidence is present.
5. Canonicalize the nullifier input and derive `claim_nullifier_v1`.
6. Check `claim_nullifier_registry_v1` for active nullifier, presentation,
   proof, conversion receipt, and conversion lot conflicts.
7. Atomically reserve the nullifier with status `pending`.
8. Only then run claimability verifier, wallet, ECU, ILC, or settlement-adjacent
   processing.
9. Mark the nullifier `accepted` if the claim is accepted, or
   `rejected_nonblocking` if the authenticated claim fails verification and
   should not block a later valid presentation.

If any active conflict exists at step 6, the endpoint must reject the request
with a stable duplicate-claim reason before any wallet, ECU, ILC, settlement, or
value-path processing:

```text
duplicate_claim_rejection_policy_defined
duplicate_claim_rejected_at_api_layer
```

Storage-only duplicate detection is insufficient. A future implementation must
not rely on a later database uniqueness violation or settlement-layer rejection
as the primary duplicate-claim control.

---

## 9. Non-Activation Boundary

Phase 1377 does not authorize or perform:

1. Claim endpoint activation.
2. Public verifier API activation.
3. Public claimability activation.
4. Public HTTP route activation.
5. Public socket listener or non-loopback bind.
6. Wallet-facing withdrawal, transfer, or spend.
7. Wallet-provider signing.
8. Wallet-provider ledger writes.
9. ECU minting.
10. ILC settlement.
11. Value-path behavior.
12. Runtime implementation in `ilc_core/`.
13. CDL mutation.
14. Public RC publication.
15. Public launch.

This records:

```text
claim_endpoint_not_activated_phase_1377
```

---

## 10. Implementation Requirements For Later Phases

A later runtime phase that implements this policy must prove:

1. The nullifier hash uses canonical JSON with deterministic key ordering,
   compact separators, and non-finite numeric rejection.
2. Nullifier input contains only public-safe refs and no private payload,
   private lineage, wallet secret, private key, mnemonic, recovery share,
   ZK witness, random nonce, or wall-clock timestamp.
3. Epoch fields are protocol issuance epochs.
4. The registry insert is atomic and fail-closed under concurrent submissions.
5. Active duplicate rejection occurs at API admission before verifier or
   economic processing.
6. Pending reservations cannot be weaponized by unauthenticated garbage.
7. Expiry uses the deterministic issuance-epoch formula in this policy.
8. Expired nullifiers do not reopen expired claim windows.
9. The public endpoint remains closed unless Phase 1389 or a later explicit
   activation gate records activation.

---

## 11. Phase 1378 Handoff

Phase 1378 may proceed to legacy FastAPI route cleanup. This policy is now an
available prerequisite for future public claimability activation, but activation
remains blocked until the later gate.

Carry-forward:

```text
phase_1378_legacy_fastapi_route_cleanup_next
phase_1389_claim_endpoint_requires_replay_nullifier_policy_phase_1377
phase_1389_claim_endpoint_requires_duplicate_claim_registry_phase_1377
```

Graph delta:

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md -> public-claimability/replay-nullifier-policy
```
