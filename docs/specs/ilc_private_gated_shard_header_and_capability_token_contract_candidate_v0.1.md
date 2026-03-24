# ILC Private/Gated Shard Header and Capability-Token Contract Candidate v0.1

Status: candidate contract outline (non-ratified)  
Date: 2026-03-24  
Purpose: define the minimum contract surfaces needed for private/gated shard headers,
public anchors, access rights, and private-to-public continuity without forcing premature
constitutional closure.

---

## 1. Problem

The current architecture already supports:

- public / semi-private / private visibility modes,
- explicit private-to-public promotion,
- separate `Shard`, `Node`, `Subscription`, and `Inter-Agent Contract` object classes,
- public agent identity material,
- and the idea that private or gated shards may expose minimal public headers.

What is still missing is a concrete contract for:

- what exactly is public when a shard is private or gated,
- how access rights are represented,
- how continuity is preserved without revealing private contents,
- how payment-gated access should hook into shard-level objects,
- and how downstream promotion preserves lineage.

Without this contract, later implementations are likely to drift into incompatible local
patterns and create refactor pressure.

---

## 2. Scope

This candidate contract covers:

- minimal public header surfaces for private/gated shards,
- capability-token access references,
- public/private boundary commitments,
- subscription / access hooks,
- promotion linkage surfaces.

This candidate contract does **not** cover:

- full token economics for subscriptions or auctions,
- full DRM or copyright enforcement,
- full rights/licensing semantics,
- market-specific overlays such as securities or prediction markets,
- runtime implementation details.

---

## 3. Core design rule

Private/gated shards should follow this structure:

- **public anchor/header**
- **private interior**
- **explicit access mechanism**
- **explicit promotion path**

The public graph should carry enough information to preserve:

- existence,
- identity linkage,
- continuity,
- navigability,
- promotion lineage,

without disclosing private content by default.

---

## 4. Minimum public header for a private or gated shard

Recommended minimum public shard-header fields:

- `shard_id`
- `creator_agent_id`
- `visibility_mode` = `gated` or `private`
- `anchor_mode`
  - `agent_root`
  - `node_root`
  - `mixed`
- `anchor_ref`
  - public agent/profile anchor and/or public root node reference
- `root_commitment_ref`
  - first-node pointer, root CID, beacon, notarized pointer root, or equivalent commitment
- `gate_control_ref`
  - pointer to the gate-control node if one exists
- `access_model`
  - `local_only`
  - `capability_token`
  - `subscription`
  - `contract_gated`
  - `hybrid`
- `lineage_policy_ref`
  - pointer to the policy governing private-to-public promotion continuity
- `content_disclosure_level`
  - `header_only`
  - `metadata_only`
  - `selective_public`
- `epoch_created`
- `status`
  - `active`
  - `frozen`
  - `deprecated`

Design rule:

- the header must be sufficient to prove that a private or gated shard exists and is
  anchored,
- but insufficient to reconstruct private contents without the corresponding access rights.

---

## 5. Node-anchored shard initiation

Nodes and shards are distinct object types.

A shard may begin from:

- an agent anchor,
- a public node anchor,
- a lineage of related nodes,
- or a mixed anchor set.

Recommended rule:

- a public node may serve as the root anchor or entry point for a downstream private or
  gated shard,
- but shard formation remains an explicit shard-lifecycle event rather than an implicit
  side effect of creating a node.

This supports use cases such as:

- a public scientific discovery spawning a private research workspace,
- a public media node spawning a gated derivative-use shard,
- a public governance node spawning a private deliberation workspace before later promotion.

---

## 6. Capability-token access surface

If access is not public, the shard should support a capability-token style reference model.

Minimum conceptual fields for an access token or token reference:

- `access_grant_id`
- `target_shard_id`
- `grantor_agent_id`
- `grantee_ref`
  - specific agent
  - group
  - bearer-like reference only if explicitly allowed
- `scope`
  - `read`
  - `write`
  - `audit`
  - `promote`
  - combinations
- `content_scope`
  - whole shard
  - subtree
  - node set
  - selected derivative set
- `valid_from_epoch`
- `valid_to_epoch`
- `revocation_ref`
- `payment_ref`
  - optional pointer to subscription / contract / escrow object
- `signature`

Important boundary:

- the protocol needs a place to point to access rights,
- but the full custody, cryptography, and delivery model for those rights can remain L2/L3
  until a dedicated lane hardens it.

---

## 7. Subscription and payment hooks

The existing `Shard`, `Subscription`, and `Inter-Agent Contract` object classes are already
the right substrate for gated access.

Recommended rule:

- the base protocol should expose enough schema surface for:
  - access fees,
  - write multipliers,
  - subscription duration,
  - and contract-linked access grants,
- but should not attempt to hardcode all recurring-payment business logic at L1.

Practical reading:

- one-time access, recurring subscription, metered usage, auction access, and enterprise
  contract access are all plausible,
- but most of that business logic belongs in L2/L3 contract systems built on top of the
  base protocol primitives.

---

## 8. Promotion linkage

Promotion from private/gated space into public graph space must continue to follow CDL-038:

- successor public node,
- promotion receipt,
- disclosed lineage,
- no automatic public corroboration carry-forward,
- no automatic public reputation carry-forward.

This candidate contract adds one recommended extension:

- if promoted content came from a private/gated shard, the public promotion lineage should
  be able to reference:
  - originating `shard_id`,
  - root commitment/header,
  - gate policy reference,
  - and selected disclosed review-history hashes if the promoter chooses to disclose them.

This preserves continuity without converting private rehearsal into public legitimacy.

---

## 9. Scenario mapping

### A. Licensed public node

- public node stays public,
- rights/licensing metadata remains attached at the public layer,
- a gated/private derivative-use shard may be created downstream,
- public graph can preserve attribution and lineage,
- usage-condition enforcement may reference contract/jury surfaces rather than epistemic
  falsification alone.

### B. Paywalled media or knowledge service

- public node and public anchor remain visible,
- gated shard/header exposes access model and fee hooks,
- actual premium content remains private or selectively disclosed,
- subscription or contract objects grant access.

### C. Market overlays

- public graph carries disclosures, claims, evidence, and resolution anchors,
- market mechanics remain in a specialized gated/private or sequestered financial shard,
- failures in the market layer must not contaminate the base epistemic graph.

---

## 10. Open questions

1. Should `root_commitment_ref` be a generic field or a small enumerated union?
2. Should `capability_token` be a first-class protocol object or only referenced through
   contracts in the first iteration?
3. What minimum metadata must be public for privacy, anti-loss, and navigability to balance
   correctly?
4. How should revocation of access rights be represented across snapshots?
5. What should be ratified at L1 versus left to L2/L3 contract systems?

---

## 11. Recommended next step

Use this candidate as input to a future lane that hardens:

- private/gated shard header schema,
- access-right token or contract reference model,
- and promotion-lineage linkage for private/gated origins.

That future lane should remain separate from minimum-scope `CDL-053`.

---

## 12. Canonical anchors

- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
