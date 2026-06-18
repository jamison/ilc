# ILC Epistemic Gap Node Schema v0.1

## Purpose

This document defines the unsigned candidate-only `epistemic_gap` node kind for
Genesis Atlas research/frontier projections. An epistemic gap node represents a
known semantic hole: an expected relation, authority target, policy target, or
resolution terminus that is not yet identified or materialized as a definitive
graph node.

An epistemic gap is not a dangling edge and is not a missing-target stub. It is
a first-class, traversable research/frontier node that allows agents to discover,
rank, discuss, and eventually resolve graph incompleteness without granting
authority to the gap itself.

## Authority Boundary

`epistemic_gap` nodes are never authority-bearing.

Required fields enforce this boundary:

- `authority_effect: "none_until_resolved"`
- `signing_posture: "not_atlas_signing_ready"`
- `projection_policy.authority_projection: "excluded"`
- `candidate_status: "fix51_support_only_not_canonical"`
- `signature_status: "unsigned_candidate_preimage"`
- `authority_boundary: "not_authority_promotion"`

No `epistemic_gap` node may receive or emit a `GOVERNS` edge. A later resolution
must create a new resolving node or edge, then add a `RESOLVED_BY` edge from the
gap node to that resolver. The gap node itself remains an audit record.

## Lifecycle Edges

| Edge type | Source | Target | Meaning |
|---|---|---|---|
| `EXPECTS_RESOLUTION` | Existing non-gap source node | `epistemic_gap` node | The source records an expected relation or target that is unresolved. |
| `RESOLVED_BY` | `epistemic_gap` node | Resolving node | A later node or target resolves the gap. |
| `EXPIRED_UNRESOLVED` | Sequence/authority expiry actor | `epistemic_gap` node | The gap expired without resolution and remains as audit evidence. |

## Projection Model

| Projection | Gap inclusion | Use |
|---|---|---|
| `authority_projection` | Excluded | Signing batch selection, authority traces, governance eligibility. |
| `frontier_projection` | Included | Gap discovery, coverage dashboards, work queues. |
| `research_projection` | Included | Knowledge graph completion, PageRank/Fiedler exploration, SIM work. |

## KGC Scores

`candidate_targets[].kgc_score` is a decimal string, not a float. This prevents
float drift in any artifact that may later become a signing preimage. KGC scores
are advisory research signals only and never grant authority, eligibility,
claimability, public economic weight, or governance effect.

## Gossip Boundary

Gap gossip may publish only:

- `gossip_hash`
- `status`
- `target_prefix_hint`
- `expiry_epochs`

The private source node, full target schema hint, local graph position, and
candidate target list remain local unless a later phase explicitly authorizes
publication.

## Non-Claims

- This schema does not add an eighth truth primitive.
- This schema does not backfill all unresolved Atlas gaps.
- This schema does not authorize Genesis signing or Atlas promotion.
- This schema does not mutate ADRs, CDLs, LMDB stores, star-map signing packets,
  runtime state, economic state, network state, public graph state, or public RC
  state.
