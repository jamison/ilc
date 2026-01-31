# ADR-0006: EVE Canonical Capsule Integrity

**Status:** Accepted  
**Date:** 2026-01-31  
**Authors:** ILC Core Team

---

## Context

EVE (External Vector Environment) is the knowledge substrate for ILC agents. As agents consume and operate on EVE data, there is a need for unambiguous integrity guarantees:

1. Which version of EVE is authoritative?
2. How can agents verify they have untampered knowledge?
3. How are forks and alternative knowledge sources distinguished?

Without a formal integrity model, agents risk operating on corrupted or adversarial knowledge bases.

---

## Decision

We define the **EVE Canonical Capsule** as the authoritative packaging format for EVE knowledge:

### Core Properties

1. **Content-Addressed**: Each capsule is identified by its CID (content identifier) over DAG-CBOR serialized contents.
2. **Genesis-Signed**: The canonical capsule is signed by the Genesis publisher key (the ILC operator's root key).
3. **Versioned**: Each capsule includes a monotonic version number and predecessor CID.
4. **Immutable**: Any change produces a new capsule with a new CID; in-place mutation is not permitted.

### EVE Fork Definition

An **EVE Fork** is any capsule signed by a non-Genesis key:
- Valid: signature verification passes
- Non-canonical: signer is not the Genesis publisher
- Explicit: clients can distinguish forks from canonical capsules by checking the signer key

### Embeddings as Derived Caches

Vector embeddings and indexes are **derived caches**, not ground truth:
- The capsule content is authoritative
- Embeddings can be regenerated from capsule content
- Agents should not trust embeddings without capsule provenance

### Verification Protocol

1. Fetch capsule by CID
2. Verify CID matches content hash
3. Verify COSE signature over capsule bytes
4. Check signer key against known Genesis key
5. If signer differs, treat as fork (warn user)

---

## Consequences

### Positive

- Clear canonical/fork distinction
- Cryptographic integrity verification
- Version history via predecessor chain
- Agents can detect tampering or substitution

### Negative

- Genesis key management becomes critical infrastructure
- Fork warning UX needs design
- Capsule size may require chunking strategy

---

## Non-Goals

This ADR does **not** cover:

- Network distribution protocol for capsules
- Capsule chunking or delta updates
- Multi-party signing or quorum schemes
- Embedding generation algorithms

These may be addressed in future phases.

---

## Alternatives Considered

### 1. Unsigned Content-Addressed Only

**Rejected.** Without signatures, any party can publish capsules claiming to be authoritative.

### 2. Central Server Authority

**Rejected.** Creates single point of failure and trust dependency.

### 3. Multi-Sig Consortium

**Deferred.** Adds complexity. Single Genesis key is sufficient for initial deployment; multi-sig can be added later.

---

## References

- [ADR-0001: Canonical Encoding and MCP MVP](ADR_0001_Canonical_Encoding_and_MCP_MVP.md)
- `ilc_core/crypto/` - COSE signing utilities
