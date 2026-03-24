# ILC Private/Gated Shard, Rights, and Access Hardening Placeholder v0.1

Author: GPT-5 Codex (planning carry-forward)
Date: 2026-03-24
Status: planning placeholder only. Not a CDL. Does not pre-authorize execution or amend any
active sequence lock.

Purpose: preserve a distinct future lane for hardening private/gated shard headers, access
rights surfaces, rights/licensing metadata, and promotion-lineage continuity without folding
that work into minimum-scope `CDL-053`.

---

## 1. Why this placeholder exists

Recent architecture work clarified that ILC should support:

- local/private memory infrastructure,
- gated shard access patterns,
- rights/licensing overlays,
- paywalled or subscription-gated knowledge services,
- and public-anchor / private-interior designs,

but the current canon does not yet harden the necessary contract surfaces.

The project now has:

- `ADR-0022` for the local-first/private-use boundary,
- a candidate contract for private/gated shard headers and capability-token access,
- and a rights / licenses / gated-access research memo.

What is still missing is a named future lane that prevents these surfaces from being
forgotten or incorrectly collapsed into unrelated windows.

---

## 2. Scope

This future lane should be responsible for hardening the following surfaces:

1. private/gated shard header schema
2. public anchor / root commitment / pointer-root rules
3. gate-control and access-model declaration surfaces
4. capability-token or access-right reference model
5. subscription / contract-linked access hooks
6. rights/licensing metadata surface
7. rights-dispute / usage-condition dispute surface
8. promotion-lineage references from private/gated origins

This lane should not be responsible for:

- Werner credit architecture,
- pressure-based reputation as a constitutional replacement,
- long-tail post-issuance economics,
- `Option C+`,
- or sequestered market-shard economics in full generality.

Those belong to separate lanes.

---

## 3. Dependencies and anchors

This future lane should read as its primary anchors:

- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`
- `docs/specs/ilc_window_469_plus_cdl_053_and_long_tail_research_placeholder_v0.1.md`
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md`

This lane should treat the above as staging inputs, not as already-ratified final law on
all points.

---

## 4. Planning posture

Recommended posture:

- keep current Treasury and epistemic windows narrow,
- do not backflow this work into `CDL-050` closure or `CDL-052` ratification,
- keep this lane separate from minimum-scope `CDL-053`,
- treat this lane as adjacent to, but not a subset of, the `469+` minimum-scope
  `CDL-053` placeholder,
- and carry it forward as a named candidate lane until a future window can absorb it cleanly.

This placeholder should be read as:

- a future hardening lane for private/gated access surfaces,
- not a near-term command to constitutionalize all business logic around licensing,
  subscriptions, or markets.

---

## 5. Candidate obligations

If this lane opens later, the candidate obligations are:

### A. Header and anchor hardening

- define what minimum header information must remain public for private/gated shards,
- define acceptable root commitment / pointer-root forms,
- define anchor relationships between agent anchors, node anchors, and shard anchors.

### B. Access-right hardening

- define whether access grants are first-class protocol objects or contract-linked references,
- define minimum fields for grant scope, duration, revocation, and payment linkage,
- define snapshot and lineage treatment for access-right state.

### C. Rights/licensing hardening

- define how rights/licensing metadata is attached to public authored nodes,
- define what is public metadata versus gated/private metadata,
- define the dispute/adjudication surface for usage-condition conflicts.

### D. Promotion continuity hardening

- define how private/gated shard origin is referenced in promotion lineage,
- preserve provenance continuity without laundering private legitimacy into public status.

---

## 6. Non-goals and boundary rules

This lane must not:

- force all licensing/business logic into L1,
- collapse rights disputes into purely epistemic refutation,
- treat gated/private usage as automatic public corroboration,
- or turn a private node into an implicit full shard lifecycle event without explicit shard
  formation semantics.

Core boundary rule:

- L1 should provide the minimum protocol surfaces for identity, provenance, visibility,
  promotion, and access references,
- while richer business logic should remain available to L2/L3 systems unless and until a
  specific piece is worth hardening into protocol law.

---

## 7. Carry-forward rule

Future planning artifacts should explicitly disposition this placeholder as one of:

- deferred
- partially activated
- opened

Suggested carry-forward surfaces:

- next context capsule refresh,
- future candidate phase grouping documents,
- future sequence locks,
- roadmap / TODO artifacts.

---

## 8. Practical next action

At the next capsule refresh, include a short carry-forward note that:

- `ADR-0022` is active as the local-first/private-use architecture boundary,
- minimum-scope `CDL-053` remains separate,
- and private/gated shard + rights/access hardening remains a distinct future lane rather
  than an implicit side effect of unrelated windows.
