# ILC Edge Removal Track 1 Phase 1 Baseline v0.1

## Purpose

This baseline freezes current edge compatibility surfaces for Track 1 full edge-removal migration phase 1. The goal is to prevent edge debt spread while preserving known compatibility paths until phased removal work lands.

## Policy

- New direct `.edges.append(` usage is forbidden outside an explicit allowlist.
- Concrete `Edge` import/constructor usage is forbidden everywhere in `ilc_core` and `tests`.
- Phase 1 compatibility now preserves only temporary direct append behavior in bounded surfaces.

## Direct Edge Append Allowlist

- `ilc_core/graph.py`
- `tests/test_graph_edges.py`

## Edge Usage Allowlist

- None (`Edge` symbol fully evicted from `ilc_core` and `tests`).

## Deterministic Inventory Commands

```bash
rg -n "from\\s+[.\\w]+types\\s+import\\s+.*\\bEdge\\b|\\bEdge\\(" ilc_core tests | sort
rg -n "\\.edges\\.append\\(" ilc_core tests | sort
```

## Notes

- Guardrail enforcement is implemented by `tests/test_edge_removal_phase1_guardrails.py`.
- This baseline was reduced in phases 974 and 975 and moved to zero `Edge`-symbol usage in phase 976.
