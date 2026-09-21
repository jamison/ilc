# ILC AgentID Namespace Reconciliation - GAP-AGENTID-NAMESPACE-RECONCILE-00

**Status:** Gap record. Does not open or ratify any CDL. Records the three
coexisting AgentID derivation paths, their output shapes, their operational
status, and the outstanding migration boundary between current public-RC
AgentIDs and CDL-069 identity-seed AgentIDs.

## Three Coexisting AgentID Derivation Paths

| Path | CDL authority | Derivation | Output format | Key-rotation-safe? | Status |
|------|---------------|------------|---------------|--------------------|--------|
| **Legacy CDL-042** | CDL-042, ratified Phase 407 | `"agent-" + sha256("ilc-agent-id-v1:" + BLS_pubkey_bytes)` | `"agent-{64 hex chars}"` - not 96 plain hex | No - derived from key material | **Deprecated.** Retained for pre-Genesis testnet compatibility only. |
| **Current public-RC CDL-017** | CDL-017, ratified Phase 765; implemented by current onboarding receipt field `agent_id_derivation_ref = "cdl-017-bls-g1-pubkey"` | `BLS_G1_compressed_public_key_hex` | 96 lowercase hex chars | No - the AgentID is the public key | **Active** for public-RC onboarded agents. Self-proving: invite PoP and install receipt verification use the AgentID directly as the BLS public key. |
| **CDL-069 identity-seed** | CDL-069, ratified Phase 838j; CDL-090 identity bootstrap ratified with public activation and identity artifact creation separately gated | `sha384("ilc-agent-id-v1:" + identity_seed)` | 96 lowercase hex chars | Yes - derived from permanent identity_seed, not hot key material | **Implemented in `agent_id_runtime.py`; not deployed as the current public-RC onboarding AgentID path.** Migration from CDL-017 path requires a dedicated identity migration phase. |

## Shape-Compatibility Risk

CDL-017 and CDL-069 paths both produce 96-character lowercase hex strings.
They are **shape-compatible but semantically incompatible**:

- a CDL-017 AgentID is a compressed BLS G1 public key and can verify BLS
  signatures directly;
- a CDL-069 AgentID is a SHA-384 digest of an identity seed and is not a BLS
  public key.

Code that accepts only "96 lowercase hex chars" accepts both paths without
distinguishing them. This is safe while the current public-RC onboarding path is
CDL-017 BLS-pubkey AgentID, but it becomes ambiguous if CDL-069 identity-seed
AgentIDs are later deployed without a domain-aware migration review.

## Outstanding Migration Boundary

`ilc_core/identity/agent_id_runtime.py` records:

```text
AGENT_ID_V2_DISTINCT_DOMAIN_MIGRATION_DEFERRED_TOKEN =
    "agent_id_v2_distinct_domain_migration_deferred_pending_identity_cdl"
```

The deprecated CDL-042 path and CDL-069 path both use the same domain prefix
`b"ilc-agent-id-v1:"`, with different input material. The current code comments
warn that changing the CDL-069 domain would mutate existing Genesis-forward
AgentIDs and therefore requires a dedicated CDL/migration phase rather than a
cleanup patch.

This phase does not close that token. It records that any future CDL-069
deployment must review identity-domain semantics before broad activation.

## Applicability to CDL-114

CDL-114 "distinct creator" counts are evaluated against the **current public-RC
CDL-017 BLS-pubkey AgentID domain at ratification time**. The diversity guard
must:

1. Accept only canonical 96-char lowercase hex strings matching
   `^[0-9a-f]{96}$`.
2. Treat structural uniqueness uniformly. It must not branch based on whether a
   96-hex value is believed to be CDL-017 or CDL-069.
3. Avoid a central registry, allowlist, or operator-maintained table of
   known-good AgentID paths.

The non-claim is explicit: CDL-114 does not distinguish CDL-017 BLS-pubkey
AgentIDs from CDL-069 identity-seed AgentIDs. If CDL-069 migration lands, the
diversity guard needs a fresh review to confirm it still expresses the intended
creator-diversity semantics.

## Open Carry-Forward

After CDL-069 identity-seed AgentIDs are authorized for public onboarding, the
CDL-114 guard and Phase 1602 source_refs bridge must be reviewed for
domain-aware identity semantics. That review is out of scope for
GAP-AGENTID-NAMESPACE-RECONCILE-00 and out of scope for CDL-114 ratification.
