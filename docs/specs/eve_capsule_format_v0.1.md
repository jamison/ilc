# EVE Capsule Format v0.1

**Status:** Draft  
**Date:** 2026-01-31  
**ADR Reference:** [ADR-0006: EVE Canonical Capsule Integrity](../adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md)

---

## Overview

This specification defines the packaging format for EVE Canonical Capsules: content-addressed, Genesis-signed knowledge bundles.

---

## Capsule Structure

A capsule consists of two parts:

1. **Manifest**: Metadata describing the capsule and its entries
2. **Entries**: The actual content blocks (stored separately or inline)

### Encoding

- **Manifest**: DAG-CBOR encoded
- **Entries**: DAG-CBOR encoded (content-addressed by CID)
- **Signature**: COSE Sign1 over manifest bytes

Human readability is not required; tooling provides inspection.

---

## Manifest Schema

```yaml
capsule_id: CID           # CID computed from manifest with capsule_id=""
version: int              # Monotonic version number (1, 2, 3, ...)
predecessor: CID | null   # CID of previous version (null for v1)
publisher_key_id: string  # Key identifier (e.g., DID or key fingerprint)
created_at: string        # ISO 8601 timestamp
entries: Entry[]          # Array of entry descriptors
```

### Entry Schema

```yaml
kind: string              # Entry type: "document", "index", "config", "embedding"
cid: CID                  # Content identifier for the entry data
content_type: string      # MIME type or custom type (e.g., "text/markdown", "application/cbor")
summary: string           # Human-readable summary (max 256 chars)
tags: string[]            # Optional classification tags
```

---

## Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| capsule_id | Yes | CID of signed manifest |
| version | Yes | Positive integer |
| predecessor | Yes | null for first version |
| publisher_key_id | Yes | Identifies signing key |
| created_at | Yes | ISO 8601 |
| entries | Yes | Non-empty array |

### Entry Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| kind | Yes | Entry type |
| cid | Yes | Content CID |
| content_type | Yes | MIME or custom |
| summary | No | Optional description |
| tags | No | Optional tags |

---

## Capsule ID Derivation

To avoid self-referential hashing, `capsule_id` is computed from a canonical
manifest where `capsule_id` is the empty string:

1. Set `capsule_id` = "" (empty string)
2. Serialize manifest to DAG-CBOR bytes
3. Compute CID over those bytes
4. Write computed CID into `capsule_id`
5. Re-serialize and sign the manifest bytes (now containing the CID)

This binds the signature to the final manifest while keeping CID derivation deterministic.

---

## Signature

The manifest is signed using COSE Sign1:

1. Serialize manifest (with computed `capsule_id`) to DAG-CBOR bytes
2. Sign bytes with publisher private key
3. Encode signature as COSE Sign1 structure
4. Store signature alongside manifest (e.g., `manifest.sig`)

### Verification

1. Fetch manifest and signature
2. Decode COSE Sign1 structure
3. Verify signature against known public key
4. Check `publisher_key_id` matches expected Genesis key

---

## Redaction Model

Capsules are immutable. To redact content:

1. Create new manifest without redacted entries
2. Increment version number
3. Set predecessor to previous capsule CID
4. Re-sign with publisher key

The predecessor chain provides audit trail.

---

## Example Manifest (JSON representation)

```json
{
  "capsule_id": "bafyreif...",
  "version": 1,
  "predecessor": null,
  "publisher_key_id": "did:key:z6Mk...",
  "created_at": "2026-01-31T22:00:00Z",
  "entries": [
    {
      "kind": "document",
      "cid": "bafyreig...",
      "content_type": "text/markdown",
      "summary": "ILC Protocol Overview",
      "tags": ["core", "documentation"]
    },
    {
      "kind": "index",
      "cid": "bafyreih...",
      "content_type": "application/cbor",
      "summary": "N-gram route index",
      "tags": ["index", "routing"]
    }
  ]
}
```

---

## Non-Goals

This specification does **not** cover:

- Network distribution protocol
- Delta updates or streaming
- Entry content format (only descriptors)
- Embedding generation

---

## References

- [ADR-0006: EVE Canonical Capsule Integrity](../adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md)
- [DAG-CBOR Specification](https://ipld.io/specs/codecs/dag-cbor/)
- [COSE Sign1 (RFC 9052)](https://www.rfc-editor.org/rfc/rfc9052)
