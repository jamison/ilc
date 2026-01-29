# ADR-0003: Star Map N-gram Route Index

**Status:** Accepted  
**Date:** 2026-01-29  
**Context:** Phase 66+ (Star Map infrastructure)

---

## Summary

Define a signed, versioned **route index** artifact that maps hashed n-grams to candidate routes for low-cost task discovery and message routing.

---

## Context

ILC needs efficient routing hints for:
- Task discovery across distributed shards/constellations
- Message passing before expensive vector search
- Pluralistic indexer competition

Vector embeddings are powerful but computationally expensive. N-gram hashing provides a fast prefilter.

---

## Decision

Adopt `ilc.star.map.ngram.route_index@v1` as the route index format with:

### Canonicalization
- Unicode NFKC normalization
- Case folding via `casefold()`
- Whitespace normalization (trim + collapse)

### Tokenization
- Split on ASCII space
- Token byte-length cap: 64 bytes (reject if exceeded)
- Token count cap: 1,024 (reject if exceeded)

### Hashing
- Multi-head SHA-256 with domain separation
- Domain prefix: `b"ilc.star.map.ngram.route_index.v1\0"`
- Default: 4 heads, 8-byte bucket keys

### Payload
- DAG-CBOR with string-only keys (per ADR-0001)
- Deterministic ordering of routes and targets
- Supports chunking via `chunk_id`, `chunk_total`

### Trust Model
- Route indexes are **advisory only**
- Untrusted until COSE signature verifies
- Consumers weight producers by reputation

---

## Non-Goals (Explicit)

> [!CAUTION]
> The route index is explicitly NOT:

1. **A consensus layer** — Does not establish truth
2. **An identity scheme** — N-grams are not identifiers
3. **A truth-evaluation method** — Claim validity is separate
4. **An embedding substitute** — Low-cost prefilter only
5. **A syllabic-name identity scheme** — Not the routing mechanism

---

## Consequences

### Positive
- Fast O(1) lookup by bucket key
- Deterministic and reproducible
- Compatible with chunked transport
- Supports pluralistic indexer competition

### Negative
- Collisions expected (mitigated by multi-head + multi-target)
- Unicode version drift affects canonicalization
- Languages without whitespace need external segmentation

### Future Hooks
- de Bruijn coverage harness for testing
- Geometry overlays for higher-order route structures

---

## References

- [Spec: star.map.ngram.route_index.v1](../specs/star.map.ngram.route_index.v1.md)
- [ADR-0001: Canonical Encoding and MCP MVP](ADR_0001_Canonical_Encoding_and_MCP_MVP.md)
- [ADR-0002: NDJSON Bundle Transport](ADR_0002_NDJSON_Bundle_Transport.md)
