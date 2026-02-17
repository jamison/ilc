# ILC Path-Lift Counterfactual Contract v0.1

Status: Draft
Date: 2026-02-17
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Define a deterministic offline contract for replayable path-lift computation used by node-value scoring as evidence for path-level marginal contribution (`CDL-014`).

## 2. Scope

This contract covers:
- path witness input shape,
- deterministic counterfactual lift computation,
- provenance-preserving output rows for downstream anti-Sybil checks,
- deterministic ranking tie-break rules.

This contract does not change runtime consensus, governance vote-share formulas, or reward issuance semantics.

## 3. Input Contract

Each path witness must contain exactly these fields:

- `witness_id: str` (non-empty, unique across batch)
- `source_id: str` (non-empty)
- `target_id: str` (non-empty)
- `nodes: list[PathWitnessNode]` (non-empty, no duplicate `node_id` within one witness)
- `path_weight: float` (`>= 0`)
- `path_cost: float` (`> 0`)

Each `PathWitnessNode` must contain exactly:

- `node_id: str` (non-empty)
- `agent_id: str` (non-empty)

`agent_id` is mandatory provenance metadata and must be preserved in outputs.

## 4. Counterfactual Method

For each witness:

1. Compute baseline efficiency:

`baseline_efficiency = path_weight / path_cost`

2. For each node in the witness path, treat node removal as path break for this witness contribution.

3. Add `baseline_efficiency` to that node's `raw_path_lift`.

Across all witnesses:

- `max_raw_path_lift = max(raw_path_lift)`
- `normalized_path_lift = raw_path_lift / max_raw_path_lift` when `max_raw_path_lift > 0`, else `0`.

## 5. Output Contract

Each output row contains:

- `node_id: str`
- `raw_path_lift: float`
- `normalized_path_lift: float`
- `witness_count: int`
- `supporting_agents: list[str]` (sorted unique agent IDs from paths containing node)
- `unique_agent_count: int`

Rows are sorted by `node_id` for canonical serialization.

## 6. Ranking Tie-Break Contract

When ranked for analysis displays:

1. descending `normalized_path_lift`
2. descending `raw_path_lift`
3. ascending `node_id`

This ordering is deterministic and host-independent.

## 7. Guardrail Requirements

1. Reject invalid witness keys and invalid node keys.
2. Reject duplicate `witness_id` values in batch.
3. Reject duplicate `node_id` inside one witness.
4. Reject negative `path_weight` and non-positive `path_cost`.
5. Preserve provenance (`agent_id`) in output so self-referential hub-and-spoke patterns are externally detectable.

## 8. Bridge to Node Value Kernel

The node-value kernel may consume `normalized_path_lift` as `path_component` input. If path witnesses are not supplied, legacy fallback path behavior is retained.

## 9. Non-Goals

- This contract does not define economic multipliers.
- This contract does not define governance policy ratification decisions.
- This contract does not define runtime ingestion of path witnesses.
