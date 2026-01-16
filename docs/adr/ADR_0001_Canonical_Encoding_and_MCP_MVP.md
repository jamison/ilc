# ADR-0001: Canonical Commitment Encoding, NodeID, and Agent Interface (MVP)

**Status:** Accepted  
**Date:** 2026-01-14  
**Scope:** Genesis + MVP consensus and agent interoperability surface

## Context

ILC needs a commitment layer that is:
- Deterministic across languages (stable bytes for hashing/signing)
- Upgrade-friendly (new codecs/hashes without rewriting history)
- Graph-native (first-class links between content-addressed nodes)
- Friendly for agent participation (simple API surface; streaming compatible)

## Decision

### 1) Consensus object codec: DAG-CBOR

All consensus-critical objects (claims, refutations, link-edges, tasks, etc.) MUST serialize to **DAG-CBOR** bytes.

Rationale:
- DAG-CBOR is a restricted CBOR profile designed for deterministic, content-addressed DAGs.
- It reduces consensus ambiguity by restricting tags and key types while retaining compact binary encoding.

**Notes (ILC profile constraints):**
- Map keys are strings only.
- Disallow indefinite-length items.
- Avoid floats in consensus payloads (use integers / fixed-point / explicit string/bytes forms).
- Use explicit domain encodings for timestamps, money, big integers, field elements.

### 2) NodeID: CIDv1 (codec + multihash)

**NodeID MUST be a CIDv1**, computed as:

`NodeID = CIDv1(multicodec="dag-cbor", multihash=H(dag_cbor_bytes))`

Hash function policy:
- MVP default: `sha2-256` (widely supported).
- Allowed (optional): `blake3-256` (highly parallelizable).
- Hash function MUST be expressed via multihash to preserve algorithm agility.

Schema/versioning:
- The payload MUST include a schema identifier (e.g., `schema: "ilc.genesis.node_structure@v1"`).
- Schema identifiers are NOT required to be in the NodeID, but MUST be included in payload and enforced by validators.

### 3) Attestations & signatures: COSE blocks (non-DAG-CBOR)

Signatures and encrypted envelopes MUST be represented as **separate blocks** encoded using CBOR/COSE
(e.g., COSE_Sign1 / COSE_Sign). These blocks are content-addressed and linked from DAG-CBOR nodes
via CID links.

Rationale:
- DAG-CBOR restricts tags and map key types; COSE uses integer-labeled header maps.
- Keeping attestations as separate blocks avoids violating DAG-CBOR rules while keeping verification clean.

Post-quantum crypto (PQC):
- MVP policy: PQ signatures are OPTIONAL and may be included alongside classical signatures (“hybrid”).
- PQ algorithm registries/IDs in COSE may evolve; decouple from consensus payloads by keeping signatures as separate blocks.

### 4) Agent control-plane: MCP (minimal tool surface)

Expose a minimal MCP tool set for agents (JSON-RPC control plane), where agents mostly exchange **CIDs**.
Large data moves as content-addressed blocks/bundles rather than giant JSON blobs.

**MVP MCP tools:**
1. `ilc.capabilities.get`
2. `ilc.task.get`
3. `ilc.block.get`
4. `ilc.bundle.submit`

### 5) Transport formats: NDJSON is allowed (non-consensus)

NDJSON is allowed for:
- event streaming (SSE / WebSocket)
- logs, fixtures, audit replay
- debugging and operational tooling

NDJSON MUST NOT be used as the canonical commitment bytes for NodeID/signatures.

## Consequences

- Implementations must include: DAG-CBOR encode/decode, CIDv1 + multihash, COSE handling (as separate blocks).
- Validation is simplified: consensus objects are deterministic; attestations are linkable and verifiable independently.
- Future codecs can be introduced without breaking old NodeIDs by minting new CIDs for new blocks.

## MVP Test Plan (acceptance checks)

- Cross-language determinism fixtures: same object → identical DAG-CBOR bytes → identical CID.
- Round-trip: DAG-CBOR decode/encode remains stable under canonical rules.
- Graph-link tests: CID links resolve and validate across nodes.
- Attestation tests: COSE blocks verify against referenced DAG-CBOR bytes and/or referenced CIDs.
- MCP contract tests: tool input/output validate against JSON Schemas.

