# Dynamic Epistemic Traversal Engine — Forward Planning

**Phase originated:** 1233-1240 (design discussion, human + Codex)
**Earliest implementation window:** 1241+
**Status:** Pre-planning only. No spec-open or CDL-open decision has been made.
**Sequence gate:** Must not precede Phase 1236 (commit.epoch connector),
Phase 1237 (L3 sidecar spec), or Phase 1238 (SIM-FETCH-01).
**Current planning status:** Not yet scheduled as a locked phase in Window 1233-1240.
This artifact is a citeable planning record for Window 1241+ consideration, not an
authorization to implement or wire economics.

```text
dynamic_epistemic_traversal_engine_forward_planning_recorded_phase_1233_1240
```

---

## 1. Motivation

ILC's epistemic substrate is a time-indexed evolving hypergraph, not a static
matrix. The system already has deterministic nonlinear or nonlinear-adjacent
primitives:

- Geometric provenance decay (α = 0.45, CDL-084)
- CDL-V1 temporal reputation decay
- CDL-V3 diversity floor (lateral inhibition analog)
- CDL-V7 Popperian gate (threshold activation)
- CDL-077 circuit breaker (refractory period analog)
- CDL-060 centrality-delta gossip (bounded signal propagation)
- CDL-081 hyperedge ECU attribution (generalized multi-party connectivity)
- Phase 1229 deterministic graph projection (read-only traversal layer)

What is **not yet implemented** is a unified versioned traversal/evaluation
engine that composes these primitives into a single runtime that can answer
the question: *for this epoch, agent, and query context, which paths are
active, discounted, amplified, or suppressed?*

This document records the proposed answer from the Phase 1233-1240 design
discussion: implement the first version as a **read-only deterministic graph
evaluation layer** over existing projections, then SIM it before any routing or
settlement integration.

---

## 2. Architectural Framing

The key engineering boundary:

> **Nonlinear dynamics can inspire the system architecture, but
> consensus-critical protocol state must remain deterministic, replayable,
> and exact.** Adaptive behavior lives in versioned traversal rules,
> projection layers, economic weights, and epoch-indexed state — not in
> hidden mutable code inside knowledge nodes.

Knowledge **Graph Nodes are immutable artifacts.** Time variation comes from
changing edge weights, activation state, reputation, centrality, decay, reuse
frequency, quorum status, and epoch context. Dynamics emerge from repeated
agent interactions across epochs.

"Turn a vertex on or off" is not the right frame. The correct frame is:
**contextual edge activation and projection gating**. The underlying graph
history is never rewritten. A traversal rule says: for this epoch, agent,
and authority context, these edges are active / discounted / suppressed.

---

## 3. Proposed Module

```
ilc_core/graph/dynamic_traversal_runtime.py
```

Version token format (not yet assigned):
```
dynamic_traversal_runtime_phase_NNNN.v0.1
```

Suggested paired test file:

```
tests/test_phase_NNNN_dynamic_epistemic_traversal_runtime.py
```

Suggested future spec file:

```
docs/specs/ilc_dynamic_epistemic_traversal_engine_spec_NNNN_v0.1.md
```

---

## 4. Inputs

| Input | Type | Notes |
|-------|------|-------|
| `nodes` | canonical Graph Node artifacts | content-addressed, immutable |
| `edges` | typed relations | REUSE, PROVENANCE, REFUTATION, VALIDATION, SERVE, ATTESTATION, etc. |
| `hyperedges` | quorum / co-authorship / CDL bundles | multi-party relations |
| `epoch_context` | current, query, and finalized epoch frontier | epoch sequence number, not wall-clock |
| `agent_context` | requesting agent, reputation tier, permissions, perspective | |
| `projection_context` | provenance view / economic view / refutation view / bootstrap view / fetch-incentive view | |
| `policy_version` | explicit version token | required for deterministic replay |

---

## 5. Core Math

All arithmetic must use `Decimal`. No `float`. No `math.exp`, no sigmoid.
Use Decimal-safe rational curves or bounded piecewise functions for
nonlinear saturation.

### Edge Activation Score (multiplicative)

```
edge_score =
    base_edge_weight
  × edge_type_coefficient
  × temporal_decay_multiplier        # CDL-V1 style epoch decay
  × centrality_multiplier            # high-centrality artifacts stay visible
  × reputation_multiplier            # serving-peer / agent reputation
  × refutation_multiplier            # upheld refutations suppress or reroute
  × provenance_multiplier            # CDL-084 hop decay, α = Decimal("0.45")
  × policy_gate                      # hard 0 if invalid lineage / quorum / φ-bound
```

All coefficients are `Decimal`. `policy_gate` is `Decimal("0")` or `Decimal("1")`.

### Edge Status

Every evaluated edge receives one of these canonical statuses:

| Status | Meaning | Score behavior |
|--------|---------|----------------|
| `active` | Edge participates normally in the projection context | computed score |
| `discounted` | Edge remains usable but weakened by decay, refutation risk, low centrality, or reputation context | computed score in `(0, 1)` |
| `suppressed` | Edge is visible for audit but not traversable for this query | `0` |
| `amplified` | Edge remains bounded but receives a positive multiplier from centrality, reputation, or quorum confidence | capped computed score |
| `ignored` | Edge is outside projection context or depth bounds | omitted from path search, optionally listed in audit output |

### Nonlinear Saturation (Decimal-safe)

Preferred: **bounded piecewise rational**

```python
# Example: centrality multiplier
if x < floor: result = Decimal("0")
elif x > ceiling: result = Decimal("1")
else: result = (x - floor) / (ceiling - floor)  # linear in range; Decimal
```

Or Hill function using integer exponents:

```
hill(x) = x^n / (k^n + x^n)
```

where `n` is a small integer (2 or 3) and all values are `Decimal`.

### Path Scoring

First version (less brittle for long paths):

```
path_score = min(edge_scores) × average(edge_scores)
```

vs pure product (which collapses too aggressively over long paths).

### Hyperedge Activation

```
hyperedge_active = required_member_count_met AND quorum_or_policy_condition_met
hyperedge_score = min(member_edge_scores) × quorum_confidence
```

### Determinism Requirements

- No `float`, no `math.exp`, no wall-clock time, no PRNG.
- All external numeric inputs normalize through `Decimal` and reject non-finite values.
- All output scores serialize as canonical Decimal strings.
- Traversal order is deterministic: sort by canonical ID before expansion.
- Ties are resolved lexicographically by canonical ID unless a later CDL ratifies another rule.

---

## 6. API Shape (v0.1 target)

```python
@dataclass(frozen=True)
class TraversalContext:
    epoch: int
    projection_type: str
    requesting_agent_id: str | None
    max_depth: int

@dataclass(frozen=True)
class TraversalPolicy:
    version: str                              # explicit version token
    edge_type_coefficients: Mapping[str, Decimal]
    decay_alpha: Decimal                      # CDL-084 α; currently Decimal("0.45")
    centrality_floor: Decimal
    max_paths: int

def evaluate_dynamic_projection(
    projection: Mapping[str, Any],
    context: TraversalContext,
    policy: TraversalPolicy,
) -> dict[str, Any]:
    ...
```

### Internal Function Decomposition

Expected implementation pieces:

```python
def normalize_traversal_policy(raw: Mapping[str, Any]) -> TraversalPolicy:
    ...

def normalize_traversal_context(raw: Mapping[str, Any]) -> TraversalContext:
    ...

def evaluate_edge(
    edge: Mapping[str, Any],
    *,
    context: TraversalContext,
    policy: TraversalPolicy,
    node_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    ...

def evaluate_hyperedge(
    hyperedge: Mapping[str, Any],
    *,
    evaluated_edges: Mapping[str, Mapping[str, Any]],
    context: TraversalContext,
    policy: TraversalPolicy,
) -> dict[str, Any]:
    ...

def score_paths(
    *,
    start_ids: Sequence[str],
    target_ids: Sequence[str] | None,
    evaluated_edges: Sequence[Mapping[str, Any]],
    context: TraversalContext,
    policy: TraversalPolicy,
) -> list[dict[str, Any]]:
    ...
```

The v0.1 runtime should consume the Phase 1229 projection shape directly. It
should not query LMDB, the network, or consensus state itself. Callers provide
already materialized projection records.

### Output format

Machine-auditable reason tokens required per edge:

```json
{
  "edge_id": "edge:a->b:provenance",
  "active": true,
  "score": "0.18225",
  "reason_tokens": [
    "edge_type_provenance",
    "temporal_decay_applied",
    "refutation_not_upheld",
    "lineage_valid"
  ]
}
```

- All ratio/score fields serialized as canonical Decimal strings (`str`)
- `sort_keys=True, allow_nan=False` on all JSON output
- Deterministic across two calls with identical inputs + policy version

---

## 7. Implementation Sequence

| Step | Phase range | Description |
|------|-------------|-------------|
| 1 | 1241+ | Spec phase: Dynamic Epistemic Traversal Engine Spec (NON-SENSITIVE) |
| 2 | 1241+ | v0.1 implementation: read-only, deterministic, projection-layer only |
| 3 | Later | SIM: run traversal over historical epoch data; measure emergent behavior |
| 4 | Later | Connect traversal output to routing decisions (CDL required) |
| 5 | Later | Connect traversal output to ECU settlement path (CDL required — high sensitivity) |

**Steps 4 and 5 require separate CDL openings.** Connecting traversal output
directly to economic settlement before SIM evidence is available would wire
an untested engine into consensus-critical protocol state. The safe first
version is read-only evaluation only.

### Minimum v0.1 Deliverables

The first implementation phase should produce:

1. `ilc_core/graph/dynamic_traversal_runtime.py`
2. `DYNAMIC_TRAVERSAL_RUNTIME_VERSION = "dynamic_traversal_runtime_phase_NNNN.v0.1"`
3. `TraversalContext` and `TraversalPolicy` dataclasses
4. Decimal-only normalization helpers
5. `evaluate_dynamic_projection`
6. deterministic edge evaluation with status + reason tokens
7. deterministic hyperedge evaluation
8. bounded path scoring with `max_depth` and `max_paths`
9. canonical JSON export helper or reuse of Phase 1229 export helpers
10. focused tests with at least 12 cases

### Minimum Test Coverage

Tests should cover:

1. version token exported;
2. float inputs rejected at all numeric policy/context boundaries;
3. non-finite Decimal inputs rejected;
4. deterministic output across two identical calls;
5. canonical JSON uses `sort_keys=True` and `allow_nan=False`;
6. edge statuses: `active`, `discounted`, `suppressed`, `amplified`, `ignored`;
7. temporal decay lowers score as epoch distance grows;
8. refutation context suppresses or discounts the target edge;
9. provenance hop decay uses Decimal and the configured alpha;
10. hyperedge activation requires member/quorum condition;
11. path scoring is deterministic and bounded by `max_depth` / `max_paths`;
12. Phase 1229 projection compatibility: output can be built from `project_graph(...)`.

---

## 8. What This Is NOT

- This is NOT "logic inside knowledge nodes." Graph Nodes remain immutable artifacts.
- This is NOT an LLM or matrix-multiply engine added to ILC.
- This is NOT authorization for CDL-088 or any economic settlement change.
- This is NOT a public-launch act or production wiring decision.
- The `cdl_087_ratification_authorized` flag remains `false` until the six
  Phase 1228 ratification conditions are satisfied independently.
- This is NOT a replacement for `commit.epoch`; epoch/finality remains governed
  by CDL-051 and the Phase 1226/1235 `commit.epoch` path.

---

## 9. Relationship to Existing Primitives

| Primitive | Where | Relationship to traversal engine |
|-----------|-------|----------------------------------|
| Provenance decay α | `epoch_attribution_settle_runtime.py` | `provenance_multiplier` in edge activation |
| CDL-V1 temporal decay | `temporal_decay_runtime.py` | `temporal_decay_multiplier` |
| CDL-V3 diversity floor | `diversity_floor_runtime.py` | `policy_gate` (hard suppression) |
| CDL-V7 Popperian gate | `popperian_gate_runtime.py` | `policy_gate` (threshold activation) |
| CDL-060 centrality delta | `centrality_delta_gossip_runtime.py` | feeds `centrality_multiplier` |
| Phase 1229 projection | `agent_graph_projection_runtime.py` | traversal engine consumes projection as input |
| CDL-077 circuit breaker | `circuit_breaker_interface.py` | `policy_gate` at serving-peer level |
| φ-bound (CDL-085) | `types.py:EDGE_MINT_PHI_BOUND` | `policy_gate` for payout suppression |

---

## 10. Open Design Questions Before Implementation

1. **Projection input contract:** should v0.1 consume only the generic Phase 1229
   projection, or should it define a stricter dynamic-traversal projection schema?
   Recommendation: consume the Phase 1229 shape first, then tighten if tests expose ambiguity.
2. **Refutation semantics:** should an upheld refutation always suppress a target
   edge, or can it reroute value to the refuting path? Recommendation: expose both
   as policy modes but default to discount/suppress only in v0.1.
3. **Centrality source:** should v0.1 accept centrality as caller-supplied node
   metadata or read from CDL-060 state? Recommendation: caller-supplied only in v0.1.
4. **Agent context:** should requesting-agent reputation affect read-only projection?
   Recommendation: include the field but default to neutral multiplier; avoid access-control
   semantics until a later CDL.
5. **Economic integration:** when should traversal scores affect ECU settlement?
   Recommendation: only after a SIM phase and a separate CDL, because this crosses into
   settlement policy.

---

## 11. Recommended Next Planning Action

After Phase 1236, Phase 1237, and Phase 1238 close, add a Window 1241+ candidate
phase:

```text
Phase NNNN — Dynamic Epistemic Traversal Engine Spec
Sensitivity: NON-SENSITIVE if spec-only
Scope: define v0.1 read-only traversal/evaluation runtime contract, tests, and SIM plan
Non-goals: no settlement wiring, no routing authority, no CDL-087 ratification
```

Implementation should follow in a separate phase only after that spec is reviewed.

`dynamic_epistemic_traversal_engine_forward_planning_recorded_phase_1233_1240`
