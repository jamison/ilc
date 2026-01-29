# ADR 0002: NDJSON Bundle Transport

**Status:** Accepted  
**Phase:** 66C  
**Date:** 2026-01-24

## Context

ILC needs a transport format for moving large numbers of COSE-signed artifacts between agents/nodes with:
- Streaming I/O (line-by-line, no "read whole file" assumption)
- Deterministic output for diffs and reproducibility
- Strong guardrails (ordering, size limits, strict schemas)
- Binding to commitment layer (COSE_Sign1 + NodeID verification)

## Decision

We adopt **NDJSON (Newline Delimited JSON)** as the streaming transport format for COSE_Sign1 attestation bundles.

### Transport vs Commitment Separation

| Layer | Format | Trust |
|-------|--------|-------|
| Commitment | DAG-CBOR + CIDv1 NodeID + COSE_Sign1 | Canonical, verified |
| Transport | NDJSON bundle | Untrusted until verified |

NDJSON is **untrusted** until each record is verified by:
1. COSE_Sign1 signature verification (Ed25519)
2. Canonical CBOR validation
3. NodeID recomputation and match

### Bundle Structure

Each bundle is a sequence of JSON lines (`\n` terminated):

```
┌─────────────────────────────────────┐
│ {"type":"ilc.bundle.header",...}    │  Line 1: Header (exactly 1)
├─────────────────────────────────────┤
│ {"type":"ilc.bundle.record",...}    │  Line 2..N: Records (0..N)
│ {"type":"ilc.bundle.record",...}    │
│ ...                                 │
├─────────────────────────────────────┤
│ {"type":"ilc.bundle.footer",...}    │  Last line: Footer (optional)
└─────────────────────────────────────┘
```

### Line Schemas

**Header** (first line, required):
```json
{
  "type": "ilc.bundle.header",
  "bundle_version": 1,
  "bundle_id": "uuid4-string",
  "created_at": "RFC3339 timestamp",
  "ilc_phase": "66C",
  "record_kind": "cose_sign1",
  "cose_encoding": "base64url",
  "notes": "optional string"
}
```

**Record** (0 or more):
```json
{
  "type": "ilc.bundle.record",
  "seq": 1,
  "node_id": "bafyrei...",
  "cose_sign1_b64u": "base64url(COSE_Sign1 bytes, no padding)",
  "meta": {"optional": "metadata dict"}
}
```

**Footer** (optional, must be last):
```json
{
  "type": "ilc.bundle.footer",
  "record_count": 123,
  "sha256_b64u": "base64url(sha256(record_lines))"
}
```

### Footer Digest Rule

If footer is present:
1. Compute SHA-256 over exact UTF-8 bytes of each record line (including `\n`)
2. Concatenate record line bytes in emission order
3. Exclude header and footer from digest input
4. `sha256_b64u = base64url_no_padding(digest_bytes)`

### Invariants

| Rule | Enforcement |
|------|-------------|
| bundle_version = 1 | Reject other versions |
| record_kind = "cose_sign1" | Only COSE_Sign1 supported |
| cose_encoding = "base64url" | No padding in encoding |
| seq strictly increasing | Reject out-of-order records |
| node_id = valid CIDv1 | Parse validation on read |
| max line size | Default 1 MiB, configurable |

## Security Notes

1. **NDJSON is untrusted** - Bundle contents are arbitrary until verified
2. **Line size limits** - Prevents memory/DoS attacks (default 1 MiB)
3. **Strict ordering** - Prevents parsing ambiguity exploits
4. **Footer digest = integrity, not authenticity** - Auth comes from COSE signatures
5. **NodeID binding** - Each record must verify against recomputed NodeID from payload

## Implementation

```
ilc_core/protocol/ndjson_bundle.py   # Writer, reader, validators
ilc_core/protocol/bundle_verify.py   # Transport-to-commitment binding
ilc_core/protocol/__init__.py        # Public exports
tools/make_ndjson_bundle.py          # Demo/smoke test tool
```

## Consequences

- Agents can stream large artifact bundles without loading all into memory
- Footer digest provides end-to-end integrity (but not authenticity)
- Each record can be independently verified via COSE + NodeID
- Deterministic JSON output enables diff-based debugging
- Future phases can add compression, chunking, or network transport

**Concrete use-case:** Route index shards (ADR-0003) are transported as COSE-signed records in NDJSON bundles.

## References

- NDJSON: https://ndjson.org/
- RFC 8259: JSON
- Phase 66B: COSE_Sign1 attestation blocks
- [ADR-0003: Star Map N-gram Route Index](ADR_0003_Star_Map_Ngram_Route_Index.md)

