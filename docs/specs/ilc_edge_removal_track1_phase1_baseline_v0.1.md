# ILC Edge Removal Track 1 Phase 1 Baseline v0.1

## Purpose

This baseline freezes current `Edge` compatibility surfaces for Track 1 full edge-removal migration phase 1. The goal is to prevent new `Edge` spread while preserving known compatibility paths until phased removal work lands.

## Policy

- New direct `.edges.append(` usage is forbidden outside an explicit allowlist.
- New `Edge` import or constructor usage is forbidden outside an explicit allowlist.
- Phase 1 preserves compatibility. It does not remove `Edge` model usage yet.

## Direct Edge Append Allowlist

- `ilc_core/graph.py`
- `tests/test_graph_edges.py`

## Edge Usage Allowlist

- `ilc_core/types.py` (canonical `Edge` model definition)
- `ilc_core/graph.py`
- `ilc_core/agent.py`
- `ilc_core/consensus/engine.py`
- `tests/test_contradiction.py`
- `tests/test_graph_edges.py`
- `tests/test_kernel.py`
- `tests/test_task_primitive.py`
- `tests/test_versioning.py`

## Deterministic Inventory Commands

```bash
rg -n "from\\s+[.\\w]+types\\s+import\\s+.*\\bEdge\\b|\\bEdge\\(" ilc_core tests | sort
rg -n "\\.edges\\.append\\(" ilc_core tests | sort
```

## Notes

- Guardrail enforcement is implemented by `tests/test_edge_removal_phase1_guardrails.py`.
- This baseline is expected to shrink in phases 974 and later until `Edge` compatibility is fully removed.
