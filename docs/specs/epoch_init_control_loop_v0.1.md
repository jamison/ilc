# Epoch Init Control Loop v0.1

**Version:** 0.1  
**Status:** DRAFT  
**Date:** 2026-02-03

---

## 1. Overview

The epoch-init control loop executes at the start of each epoch before any tasks are processed. It updates control-plane parameters (trust vectors, routing caps, congestion policy) based on benchmark results and prior epoch state.

**Key principle:** Control-plane updates are non-ledger operations. No balance mutations occur until `commit.epoch`.

---

## 2. Inputs

| Input | Source | Description |
|-------|--------|-------------|
| `epoch_index` | Prior `commit.epoch` | Current epoch number (E = prior + 1) |
| `seed` | Protocol RNG or beacon | Randomness for benchmark selection (placeholder: deterministic seed) |
| `benchmark_suite_id` | Config | Identifier for the benchmark suite to run |
| `prior_trust_vectors` | Trust store | Agent trust vectors from epoch E-1 |
| `baseline_params` | Protocol config | Default routing caps, congestion thresholds |

---

## 3. Actions

The control loop executes these actions in order:

1. **Benchmark Run (MVP)**
   - Execute benchmark suite for eligible agents
   - Record per-agent results (latency, throughput, correctness)
   - MVP: minimal synthetic benchmark, no hardware attestation

2. **Update Trust Vectors**
   - Adjust `trust_vector.potential` based on benchmark results
   - Recalculate tier eligibility (e.g., tier 0/1/2)
   - Apply decay to stale trust scores

3. **Refresh Routing Parameters**
   - Update per-agent routing caps based on new trust tier
   - Adjust congestion policy thresholds
   - Apply any protocol-level parameter changes

4. **Form Epoch Config**
   - Construct `epoch_config` payload with updated parameters
   - Emit `epoch_config` event to protocol log

---

## 4. Outputs

### 4.1 epoch_config Payload (Informal v0.1)

```json
{
  "event_kind": "epoch_config",
  "epoch_index": 42,
  "namespace_id": "QmNodeID",
  "created_at": "2026-02-03T08:00:00Z",
  "benchmark_suite_id": "benchmark_suite_v0.1",
  "trust_updates": {
    "agent_1": {"tier": 1, "potential": 0.85},
    "agent_2": {"tier": 2, "potential": 0.72}
  },
  "routing_caps": {
    "tier_0": 100,
    "tier_1": 50,
    "tier_2": 20
  },
  "congestion_policy": {
    "threshold": 0.8,
    "backoff_factor": 1.5
  }
}
```

### 4.2 Per-Agent Benchmark Results (Optional)

Individual benchmark results may be logged as `task_outcome` events with `task_class="benchmark"` or via a future dedicated event kind. Decision deferred to Phase 69D.

---

## 5. Binding vs Non-Binding Rules

| Rule | Binding? | Scope |
|------|----------|-------|
| Trust tier determines routing eligibility | **Binding** | Epoch E |
| Routing caps limit task assignment | **Binding** | Epoch E |
| Congestion policy affects scheduling | **Binding** | Epoch E |
| Benchmark results | Non-binding (informational) | Epoch E |
| Balance mutations | **Prohibited** until `commit.epoch` | Always |

---

## 6. Threat Model and Mitigations (Brief)

| Threat | Mitigation |
|--------|------------|
| Spoofed benchmarks | Require signed results; future: hardware attestation |
| Replayed results | Include epoch_index in benchmark payload; reject stale |
| Sybil farms | Rate-limit new agent registration; stake requirements |
| Benchmark overfitting | Rotate benchmark suite; randomize test selection |

---

## 7. Determinism and Reproducibility Expectations

- **Seed determinism:** Given the same seed and prior state, the control loop must produce identical outputs
- **Benchmark reproducibility:** MVP benchmarks are synthetic and deterministic; hardware benchmarks may vary
- **State isolation:** Control loop reads from prior epoch state only; no mid-epoch state access

---

## 8. Non-Goals

This specification does **not** cover:
- Hardware attestation or TEE integration
- Benchmark suite design or selection criteria
- Trust vector decay formulas (covered in trust tier spec)
- Slashing or penalty mechanics
- Cross-namespace control-plane synchronization
