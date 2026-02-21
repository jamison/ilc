# ILC D2 Schema Test Vectors Specification 257 v0.1

Status: Phase-257 specification artifact (non-ratifying)
Date: 2026-02-21
Lane: D2 schema test-vector specification
Anchor: `docs/specs/ilc_d2_minimal_schema_specification_255_v0.1.md`

## 1. Purpose and scope

Define test-vector contracts for the three Phase-255 schemas:
- Node schema,
- Edge schema,
- Epoch Record schema.

This document specifies deterministic fixtures and invariants for future runtime implementation testing.

## 2. Node schema vectors

### 2.1 Golden input object

```json
{
  "node_id": "bafy-node-001",
  "payload": {"claim": "example"},
  "primitive_type": "assert",
  "creator_agent_id": "bafy-agent-001",
  "epoch_created": "epoch-0421",
  "parent_edges": ["bafy-edge-001"],
  "signature": "cose-sign1-node"
}
```

### 2.2 Expected canonical encoding path

- Build canonical map using Phase-255 field ordering.
- Serialize deterministically using the future canonical codec.
- Reject inputs missing required fields.

### 2.3 Expected CIDv1 derivation path

- Compute content digest over canonical bytes.
- Build CIDv1 from codec identifier and digest.
- Validate repeat derivation produces identical CID for identical object.

### 2.4 Round-trip invariants

- decode(encode(node)) equals canonical node object.
- encode(decode(bytes)) equals original canonical bytes.

## 3. Edge schema vectors

### 3.1 Golden input object

```json
{
  "edge_id": "bafy-edge-001",
  "source_node_id": "bafy-node-001",
  "target_node_id": "bafy-node-002",
  "edge_type": "supports",
  "weight": 0.75,
  "epoch_created": "epoch-0421",
  "creator_agent_id": "bafy-agent-001"
}
```

### 3.2 Expected canonical encoding path

- Use Phase-255 canonical ordering for edge fields.
- Serialize with deterministic map semantics.
- Reject unknown or missing mandatory edge fields.

### 3.3 Expected CIDv1 derivation path

- Hash canonical edge bytes.
- Build CIDv1 from hash digest.
- Assert stable CID across repeated deterministic encodings.

### 3.4 Round-trip invariants

- decode(encode(edge)) preserves required fields and values.
- encode(decode(bytes)) yields byte-identical canonical form.

## 4. Epoch Record schema vectors

### 4.1 Golden input object

```json
{
  "epoch_id": "epoch-0421",
  "participating_agents": ["bafy-agent-001", "bafy-agent-002"],
  "scoring_results": {"bafy-agent-001": 0.9, "bafy-agent-002": 0.8},
  "reward_distribution": {"bafy-agent-001": 60, "bafy-agent-002": 40},
  "finalization_hash": "sha256:epoch-0421",
  "previous_epoch_hash": "sha256:epoch-0420",
  "timestamp": "2026-02-21T00:00:00Z"
}
```

### 4.2 Expected canonical encoding path

- Canonical map ordering from Phase-255 section for Epoch Record.
- Deterministic serialization with no runtime-dependent ordering.
- Reject records with missing chain fields (`finalization_hash`, `previous_epoch_hash`).

### 4.3 Expected CIDv1 derivation path

- Compute digest over canonical Epoch Record bytes.
- Use digest and codec identifier to derive CIDv1.
- Validate deterministic regeneration for identical inputs.

### 4.4 Round-trip invariants

- decode(encode(epoch_record)) preserves all required fields.
- encode(decode(bytes)) equals original canonical bytes.

## 5. Negative-path vectors (applies to all three schemas)

Required invalid fixtures for future implementation tests:
- missing required field,
- wrong field type,
- extra unknown field when strict mode is enabled,
- non-canonical field ordering input that must normalize or reject deterministically.

## 6. Non-goals

This phase does not define codec implementation bytes, only path-level expectations and deterministic invariants.
