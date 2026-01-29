# Star Map N-gram Route Index v1 Specification

**Schema:** `ilc.star.map.ngram.route_index@v1`  
**Status:** Draft  
**Created:** 2026-01-29

---

## 1. Overview

A **route index** is a signed, versioned routing hint table that maps hashed n-grams to candidate routes (shards, constellations, indexers, agent clusters). Its purpose is to reduce search/routing cost for early task discovery and message passing without expensive vector search.

**Key separation:**
- **Transport:** NDJSON bundles (Phase 66C) move route index payloads as COSE-signed records
- **Commitment:** DAG-CBOR payload → CIDv1 NodeID → COSE_Sign1 signature

The route index is **advisory only**. It provides routing hints that consumers may choose to follow, ignore, or weight by producer reputation. It is never a source of truth for claim validation.

---

## 2. Goals

v1 goals:

1. **Deterministic n-gram extraction and hashing** — Same input always produces same bucket keys
2. **Small, streamable representation** — Supports chunking for large indexes
3. **Domain separation** — Prevents cross-protocol hash collisions via explicit prefix
4. **Pluralistic design** — Supports many competing indexers; no single authority

---

## 3. Non-Goals

Explicitly out of scope for route index:

- **Not a consensus layer** — Route indexes do not establish truth
- **Not an identity scheme** — N-grams are routing hints, not identifiers
- **Not a truth-evaluation method** — Claim validity is determined elsewhere
- **Not an embedding substitute** — This is a low-cost prefilter, not semantic search

---

## 4. Terminology

| Term | Definition |
|------|------------|
| **route** | A destination identifier for routing messages/queries |
| **target** | A specific route with an associated weight |
| **indexer** | An agent that produces route indexes |
| **constellation** | A cluster of related routes or agents |
| **shard** | A subset of a route index (supports chunking) |
| **epoch** | A time period identifier for index validity |
| **head** | One of multiple hash outputs for the same n-gram (multi-head hashing) |
| **canonicalization** | The deterministic transformation of input text before hashing |

---

## 5. Canonicalization (v1)

Canonicalization produces a deterministic UTF-8 byte sequence from arbitrary input text. This pipeline is **only for routing hints**, not for claim identity.

**Input:** Arbitrary UTF-8 text

**Process (normative):**
1. **Unicode normalize:** Apply NFKC normalization
2. **Case fold:** Apply Unicode `casefold()` (locale-independent lowercasing)
3. **Whitespace normalize:** Trim leading/trailing whitespace, collapse internal whitespace runs to single ASCII space (0x20)

**Output:** Canonical UTF-8 bytes

> [!WARNING]
> **Unicode version drift:** Different Unicode versions may produce different NFKC/casefold outputs for the same input. Implementations should document their Unicode version. Future versions may add a `unicode_version` field to payloads.

---

## 6. Tokenization (v1)

**Process:**
1. Split canonical text on ASCII space (0x20)
2. Discard empty tokens

**Guardrails (recommended):**
- Maximum token byte-length: 64 bytes (truncate longer tokens)
- Maximum total token count: 1,024 (truncate after limit)

> [!NOTE]
> **Limitation:** Languages without whitespace word boundaries (Chinese, Japanese, Thai) require external segmentation before tokenization. v1 does not specify segmentation; producers must document their approach.

---

## 7. N-gram Extraction

**Parameters:**
- `n ∈ {2, 3, 4}` (recommended default set; configurable)

**Process:**
1. Generate sliding window n-grams over token list
2. For each n-gram, serialize as: `token0 + b"\x1f" + token1 + ... + token(n-1)`

**Invariant:** Tokens MUST NOT contain byte 0x1F (Unit Separator). If a token contains 0x1F after canonicalization, it MUST be rejected with an error.

**Example:**
```
Tokens: ["hello", "world", "test"]
2-grams: ["hello\x1fworld", "world\x1ftest"]
3-grams: ["hello\x1fworld\x1ftest"]
```

---

## 8. Hashing (Multi-Head)

Multi-head hashing computes multiple independent bucket keys for the same n-gram, reducing hotspots and improving collision resilience.

**Algorithm:**

```
domain_sep = b"ilc.star.map.ngram.route_index.v1\0"
head_id    = ASCII digit string ("0", "1", "2", ...)

H = SHA256(domain_sep || head_id || b"\0" || ngram_bytes)
bucket_key = H[0:8]  # first 8 bytes
bucket_key_b64u = base64url_no_padding(bucket_key)
```

**Fixed defaults (v1):**
- `heads = 4` (compute bucket keys for head 0, 1, 2, 3)
- `bucket_key_len = 8` bytes (64 bits)

**Rationale for multi-head:**
- Each head produces an independent bucket key
- Consumers can query multiple buckets to increase recall
- Producers can store entries in multiple buckets to improve hit rates

---

## 9. Route Index Payload Schema (DAG-CBOR Object)

All map keys are strings per ADR-0001.

**Schema identifier:** `"ilc.star.map.ngram.route_index@v1"`

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema` | string | `"ilc.star.map.ngram.route_index@v1"` |
| `created_at` | string | RFC3339 timestamp |
| `canonicalizer` | string | `"ilc.text.canon@v1"` |
| `ngram_orders` | list[int] | e.g., `[2, 3, 4]` |
| `heads` | int | Number of hash heads (default: 4) |
| `bucket_key_len` | int | Bytes per bucket key (fixed: 8) |
| `routes` | list[object] | Route entries (see below) |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `epoch` | string | Time period identifier (e.g., "2026-W05") |
| `producer` | string | Key ID or agent ID of producer |
| `chunk_id` | int | Chunk index (0-based) for sharded indexes |
| `chunk_total` | int | Total chunk count |
| `chunk_range_hint` | string | Bucket key range hint (e.g., "A*-M*") |

### Route entry schema

Each entry in `routes[]`:

| Field | Type | Description |
|-------|------|-------------|
| `n` | int | N-gram order (2, 3, or 4) |
| `head` | int | Hash head index (0 to heads-1) |
| `k` | string | `bucket_key_b64u` |
| `targets` | list[object] | Target routes |

Each entry in `targets[]`:

| Field | Type | Description |
|-------|------|-------------|
| `route` | string | Route ID (CIDv1 or short label) |
| `w` | int | Weight (default: 1, max: 2^31-1) |

### Route ID format (v1)

Either:
- A CIDv1 string pointing to a route descriptor node, OR
- A short string label resolved via a separate registry node

Clients MUST degrade gracefully if resolution fails.

### Deterministic ordering

- `routes[]`: sorted by `(n, head, k)` lexicographically
- `targets[]`: sorted by `route` lexicographically

---

## 10. Size / Chunking Strategy

A **route index shard** is a valid `@v1` object containing a subset of entries.

**Chunking fields:**
- `chunk_id`: 0-based index of this chunk
- `chunk_total`: total number of chunks
- `chunk_range_hint`: human-readable hint for bucket key range

**Properties:**
- Each shard is independently transportable and verifiable
- Shards can be produced by different indexers for the same epoch
- Consumers merge shards by NodeID deduplication

---

## 11. Verification and Trust Model

A route index is **untrusted** until:

1. DAG-CBOR strict decode succeeds (string keys only)
2. Recomputed NodeID matches the claimed NodeID
3. COSE_Sign1 signature verifies against known public key

**Even after verification, the route index is advisory only.**

Consumers weight producers by:
- Reputation (historical accuracy)
- Stake (economic commitment)
- Observed performance (latency, hit rate)
- Freshness (epoch recency)

---

## 12. Integration with NDJSON Bundle Transport (Phase 66C)

Route index payloads integrate with the NDJSON bundle transport:

1. Payload is DAG-CBOR encoded
2. Signed with COSE_Sign1 (Ed25519)
3. Wrapped in bundle record with `record_kind: "cose_sign1"`
4. Transported in NDJSON bundle

Consumers verify using `verify_bundle_record()`, then interpret the payload schema field to dispatch to route index processing.

---

## 13. Security Considerations

### Collision and poisoning

Hash collisions and deliberate poisoning are expected. Mitigations:

- **Multi-head hashing** reduces single-bucket hotspots
- **Multi-target** allows fallback routes
- **Producer weighting** prioritizes trusted indexers
- **Epoch rotation** limits stale attack windows

### Guardrails

- Reject tokens exceeding 64 bytes
- Reject documents exceeding 1,024 tokens
- Enforce record size limits from bundle transport
- Reject canonicalization producing 0x1F in tokens

### Route indexes do not bypass claim validation

Route indexes only suggest where to look. Claim validity is established by the commitment layer (DAG-CBOR → NodeID → COSE_Sign1 → claim evaluation).

### Unicode version drift

Different Unicode versions may produce different canonical forms. Implementations should:
- Document their Unicode version
- Consider adding `unicode_version` field in future versions

---

## 14. Economics / Incentives (Minimal)

**Producers:**
- Publish route indexes to earn via downstream usage metrics (future)
- Compete on accuracy, freshness, and coverage

**Consumers:**
- Choose indexes based on observed utility
- May query multiple competing indexes

This design is compatible with pluralistic competition among indexers.

---

## 15. Future Hooks

### 15.1 de Bruijn Coverage Harness (Planned)

de Bruijn sequences provide systematic k-gram coverage for testing hash distribution, collision rates, and bucket balance.

**Future deliverable:** A tool that generates synthetic token streams over a controlled alphabet and produces expected bucket occupancy statistics.

**Expected CLI inputs:**
- Alphabet size
- N-gram order (n)
- Sequence length
- Number of heads
- Bucket key length

**Expected outputs:**
- Bucket occupancy histograms
- Maximum bucket load
- Collision rate estimates

**Status:** Not implemented in v1.

### 15.2 Geometry Overlays (Planned)

Future extension: routes can be embedded into higher-order structures (simplicial complexes, hypergraphs, polytopes).

**v1 hook:** `route` field can resolve to a node containing geometric metadata.

**Explicitly:** No geometry computation in v1.

---

## 16. Test Vectors

### Vector 1: Simple sentence

**Input text:**
```
Hello World Test
```

**Canonical text:**
```
hello world test
```

**Tokens:**
```
["hello", "world", "test"]
```

**2-grams:**
```
["hello\x1fworld", "world\x1ftest"]
```

**Expected bucket_key_b64u for "hello\x1fworld", head 0:**

```
domain_sep = b"ilc.star.map.ngram.route_index.v1\0"
head_id = b"0"
ngram = b"hello\x1fworld"
H = SHA256(domain_sep + head_id + b"\0" + ngram)
bucket_key = H[0:8]
```

> [!NOTE]
> **TODO:** Generate concrete hash output with a verification script. See TODO.txt task 3.1.1.

### Vector 2: Whitespace normalization

**Input text:**
```
  multiple   spaces   here  
```

**Canonical text:**
```
multiple spaces here
```

**Tokens:**
```
["multiple", "spaces", "here"]
```

### Vector 3: Case folding

**Input text:**
```
MiXeD CaSe TeXt
```

**Canonical text:**
```
mixed case text
```

### Vector 4: Unicode NFKC

**Input text:**
```
ﬁle (U+FB01 LATIN SMALL LIGATURE FI)
```

**Canonical text:**
```
file
```

### Vector 5: Empty after normalization

**Input text:**
```
   
```

**Canonical text:**
```
(empty string)
```

**Tokens:**
```
[]
```

**N-grams:**
```
[]
```

---

## Appendix: Example Payload

```json
{
  "schema": "ilc.star.map.ngram.route_index@v1",
  "created_at": "2026-01-29T10:00:00Z",
  "epoch": "2026-W05",
  "canonicalizer": "ilc.text.canon@v1",
  "ngram_orders": [2, 3],
  "heads": 4,
  "bucket_key_len": 8,
  "producer": "indexer-alpha",
  "routes": [
    {
      "n": 2,
      "head": 0,
      "k": "AbCdEfGh",
      "targets": [
        {"route": "shard-001", "w": 10},
        {"route": "shard-002", "w": 5}
      ]
    }
  ]
}
```

(Above is illustrative JSON; actual payload is DAG-CBOR encoded.)
