# Phase 838i — CDL-069 Evidence Items 8, 12, and 14

**Phase:** 838i  
**Date:** 2026-04-26  
**Evidence items satisfied:** 8 (CDL-017 interaction), 12 (CDL-001 compatibility), 14 (temporal tier audit)  
**Governing spec:** CDL-069 §4 evidence checklist

---

## Item 8 — CDL-017 Interaction Resolved

**Required token:** `cdl_017_mldsa_interaction_resolved`

### 8.1 CDL-017 Scope at Ratification

CDL-017 was ratified at Phase 765 (`ratified_date: 2026-04-21`). Its
constitutional scope is:

> CDL-017 is ratified as the constitutional validator-governance framework
> covering: validator admission and ejection as governed protocol actions,
> bootstrap transition criteria, Genesis-sunset trigger design as it applies
> to validator authority, and the dynamic validator-set activation boundary.

CDL-017 is silent on signing key algorithms. It does not specify whether
validator identity root keys are BLS12-381 or ML-DSA-65. Its scope is
governance *process* (who may be admitted, under what conditions, and how
ejection works), not cryptographic algorithm selection.

### 8.2 The Interaction Question

CDL-069 mandates ML-DSA-65 as the identity root key for all agents from
Genesis forward. Validators ARE agents (established in Phase 765 / CDL-017).
Therefore: CDL-069, if ratified, imposes ML-DSA-65 as the identity root
for validator agents.

CDL-069 §2b prelock criterion 2 states:

> ML-DSA-65 (FIPS 204) is the mandatory canonical root key algorithm for all
> agents from Genesis forward. BLS12-381 is deprecated as an identity root.

The question is whether this conflicts with CDL-017 or requires CDL-017 to
be amended before CDL-069 can ratify.

### 8.3 Resolution

**No conflict exists.** CDL-017 does not specify, constrain, or name any
signing key algorithm. Its validator-governance lane is algorithm-agnostic.
CDL-069 specifying the algorithm for the identity root key is within CDL-069's
own scope and does not amend any CDL-017 provision.

**Compatibility clause (Option 3 from Phase 838g):**

Pre-Genesis validators and any validator agent already provisioned on the
testnet prior to CDL-069 ratification that uses a BLS12-381 identity root key
are subject to a migration window: such agents must re-provision with ML-DSA-65
as their canonical root key within a migration window to be specified by the
first CDL-069-compliant validator admission process. Until re-provisioned, their
BLS-rooted endorsement packets are accepted under the legacy (`derive_agent_id`)
path, which is retained for backward compatibility per CDL-069 §2b and Phase
838d.

New validators admitted from CDL-069 ratification forward must use ML-DSA-65
as their identity root key. No exceptions.

**This clause does not require CDL-017 to be amended** because CDL-017 does
not govern key algorithms. The migration window is a CDL-069 ratification
clause, not a CDL-017 clause.

### 8.4 Verdict

**Token satisfied:** `cdl_017_mldsa_interaction_resolved`

The interaction is resolved: CDL-017 and CDL-069 govern orthogonal surfaces
(governance process vs. key algorithm). No amendment to CDL-017 is required
before CDL-069 ratifies. New validators from ratification forward use ML-DSA-65;
pre-ratification validators have a migration window.

---

## Item 12 — CDL-001 Compatibility Assertion

**Required token:** `cdl_001_compatibility_asserted`

### 12.1 CDL-001 Scope (Phase 227 Remediation Boundary)

CDL-001 governs the signer lineage trust root contract. Its Phase-227
remediation boundary defines:

1. **Signer hierarchy:** `canonical_root_key` (trust root), `authority_recovery_key`
   (recovery control), `operational_signer_key` (day-to-day signing).
2. **Lifecycle states:** `active`, `rotated`, `revoked`, `recovered`.
3. **Canonical authority linkage:** canonical signer acceptance must chain to
   an active trust root; revoked lineage must be rejected for canonical authority
   decisions.
4. **Auditability:** every lineage transition is an append-only, replayable record.

CDL-001 remains open (genesis_blocker, bounded for packaging). Runtime
enforcement is deferred; the Phase-227 contract specifies the required shape
of any future implementation.

### 12.2 CDL-069 Three-Tier Key Hierarchy

CDL-069 introduces a three-tier key hierarchy:

| Tier | Key | Algorithm | Persistence |
|------|-----|-----------|-------------|
| Cold (identity root) | ML-DSA-65 canonical root key | FIPS 204 | Tier 3 — permanent |
| Recovery | SPHINCS+ SLH-DSA-SHA2-128s | FIPS 205 | Tier 3 — permanent |
| Operational (hot) | BLS12-381 G1 ephemeral key | BLS | Tier 1 — per-validation-epoch |

This maps directly onto CDL-001's required hierarchy:

| CDL-001 role | CDL-069 key |
|--------------|-------------|
| `canonical_root_key` | ML-DSA-65 pk (genesis record `canonical_root_pk`) |
| `authority_recovery_key` | SPHINCS+ recovery key (genesis record `recovery_commitment`) |
| `operational_signer_key` | BLS ephemeral signing key (endorsed per epoch) |

### 12.3 Compatibility Analysis

**Lifecycle state mapping:**

- `active` → agent has a valid genesis record and current endorsement packet.
- `rotated` → agent has completed a recovery transaction replacing `canonical_root_pk`
  (new ML-DSA-65 key, same agent_id — CDL-069 §2a).
- `revoked` → agent has been frozen (freeze_from_epoch set; no future
  endorsement packets accepted).
- `recovered` → agent has successfully executed a recovery transaction using
  the SPHINCS+ key; new `canonical_root_pk` is now the active trust root.

All four CDL-001 required states are representable and distinguishable in the
CDL-069 protocol.

**Canonical authority linkage:**

CDL-069 §2a specifies that the `canonical_root_pk` in the genesis record is
the trust root. Endorsement packets are signed by this key. Validators verify
the ML-DSA signature on each packet against the cached `canonical_root_pk`.
Revoked lineage is rejected via the `freeze_from_epoch` mechanism: validators
reject endorsement packets and ephemeral key transactions for epochs at or
after the freeze epoch, regardless of whether the signature is valid.

**No retroactive invalidation:** CDL-069 §2a finding I4 mandates that
`effective_freeze_epoch = max(current_epoch, freeze_from_epoch)`. This ensures
the CDL-001 auditability requirement is satisfied: a key rotation does not
retroactively invalidate any prior confirmed transaction. All lineage transitions
are forward-only, making the record append-only and replayable.

**Auditability:** The genesis record is committed on-chain (Tier 3, permanent).
Recovery transactions are on-chain events. Endorsement packets are Tier 2
(retained for the issuance epoch). The complete lineage of every key event is
replayable from the genesis record forward.

### 12.4 Compatibility Verdict

CDL-069's three-tier key hierarchy is compatible with CDL-001's Phase-227
remediation boundary:

- All four required hierarchy keys/roles are satisfied.
- All four required lifecycle states are representable.
- Canonical authority linkage chains to the genesis record `canonical_root_pk`.
- Revoked lineage is rejected via freeze_from_epoch enforcement.
- Lineage transitions are forward-only (freeze clamping) and auditable.

**No CDL-001 provision is violated or weakened by CDL-069.**

**Token satisfied:** `cdl_001_compatibility_asserted`

---

## Item 14 — Temporal Tier Framework Consistency Audit

**Required token:** `temporal_tier_framework_consistency_audit_complete`

### 14.1 CDL-069 Tier Assignments (normative)

CDL-069 §2g establishes the temporal data tier framework with three tiers:

| Tier | Data examples | Hash | Retention |
|------|--------------|------|-----------|
| Tier 3 (permanent) | genesis record fields, agent_id, ILC balances, canonical_root_pk, SHA-384 commitments | SHA-384 | Never pruned |
| Tier 2 (issuance epoch ~1 month) | endorsement packets, epoch-close attestations, ECU accumulation records, reputation snapshots, minting proof inputs | SHA-256 | Pruned after minting confirmation |
| Tier 1 (validation epoch ~1 min) | ECU deltas, ephemeral BLS signatures, gossip messages | SHA-256 | Immediate at epoch close |

### 14.2 CDL-043 Consistency

**CDL-043** (ratified Phase 395) governs storage economics and adaptive graph
pruning. Its scope: adaptive pruning with bounded retention windows for graph
claims.

**Check:** Does CDL-043 pruning ever apply to Tier 3 data?

CDL-043 pruning applies to graph claim data — specifically to claims that fall
below the `ecu_score_floor` retention threshold. Genesis record fields
(Tier 3) are not graph claims; they are identity anchors stored in the genesis
record, not in the prunable claim graph. The identity commitment fields are
indexed separately and are not subject to CDL-043 pruning rules.

**Verdict:** No conflict. CDL-043 pruning operates on the claim graph (Tier 1/2
data). Tier 3 identity data is outside CDL-043's pruning scope.

### 14.3 CDL-044 Consistency

**CDL-044** (ratified Phase 399) governs the `retention_epochs` operational
parameter for CDL-039 transport data.

**Check:** Does the CDL-044 retention epoch parameter conflict with Tier 2
retention?

CDL-044 specifies `retention_epochs` for CDL-039 gossip/transport envelopes.
These are Tier 1 transport layer objects (ephemeral per validation epoch) or
at most Tier 2 (cached endorsement packets retained across validation epochs
within an issuance epoch). The CDL-044 retention_epochs parameter is a
lower-bound floor on how long transport data is cached, not an upper bound.
It does not override CDL-069 Tier 2 retention policy.

**Verdict:** No conflict. CDL-044 retention_epochs applies to transport-layer
caching (Tier 1/2). CDL-069 Tier 2 retention (pruned after minting confirmation)
operates at a higher semantic layer and a longer timescale. The two policies
are compatible by layer separation.

### 14.4 CDL-V1 Consistency

**CDL-V1** (ratified Phase 330) governs temporal decay for reuse centrality
scores: exponential half-life decay applied to reputation values.

**Check:** Does CDL-V1 temporal decay conflict with CDL-069 tier assignments?

CDL-V1 applies decay to reputation scores and reuse centrality values. Per
CDL-069 §2g, reputation snapshots are Tier 2 data (retained for issuance epoch,
pruned after minting). CDL-V1's decay function operates within the issuance
epoch cadence: the decay parameter governs how much historical centrality weight
is retained across issuance epochs.

The CDL-V1 decay function reads centrality history and outputs a decayed score.
This is a computation over Tier 2 snapshots — it does not change the tier
assignment of those snapshots. The input (centrality score at prior epoch) is
Tier 2; the output (decayed score for current epoch) is also Tier 2. CDL-069
does not change either input or output.

**Verdict:** No conflict. CDL-V1 temporal decay is a computation over Tier 2
reputation data. CDL-069 Tier 2 retention policy preserves reputation snapshots
for the issuance epoch, which is exactly the window over which CDL-V1 decay is
applied. The policies are consistent.

### 14.5 Forward Obligation (CDL-071)

CDL-069 §2g establishes a forward obligation:

> CDL-071 will formally reconcile CDL-043, CDL-044, and CDL-V1 under this
> framework, amending each where needed and taking constitutional precedence
> on tiering questions.

This audit confirms that no conflicts require immediate amendment. CDL-071's
reconciliation work is normative consolidation, not emergency conflict
resolution. Until CDL-071 is ratified, each CDL governs its specific domain
as before; CDL-069 governs identity and endorsement only.

### 14.6 Audit Verdict

No conflicts found between CDL-069's temporal tier framework and:
- CDL-043: pruning operates on claim graph (Tier 1/2); Tier 3 identity data exempt.
- CDL-044: retention_epochs applies at transport layer; layer-separated from Tier 2 semantics.
- CDL-V1: decay operates on Tier 2 reputation snapshots within issuance epoch cadence.

**Token satisfied:** `temporal_tier_framework_consistency_audit_complete`

---

## Summary

All three evidence items are satisfied by this document:

| Token | Status |
|-------|--------|
| `cdl_017_mldsa_interaction_resolved` | **SATISFIED** — Phase 838i |
| `cdl_001_compatibility_asserted` | **SATISFIED** — Phase 838i |
| `temporal_tier_framework_consistency_audit_complete` | **SATISFIED** — Phase 838i |

**All 14 CDL-069 evidence checklist items are now satisfied.**

Updated checklist: **14/14 tokens satisfied**. Phase 838j (prelock + ratification) may now proceed.
