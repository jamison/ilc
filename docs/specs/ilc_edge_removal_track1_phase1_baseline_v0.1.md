# ILC Edge Removal Track 1 Phase 1 Baseline v0.1

## Purpose

This baseline records closure-state edge policies after Track 1 full edge-removal migration. The goal is to prevent edge debt reintroduction and keep explicit graph API usage enforceable.

## Policy

- New direct `.edges.append(` usage is forbidden.
- Concrete `Edge` import/constructor usage is forbidden everywhere in `ilc_core` and `tests`.
- Direct append compatibility has been sunset; edge writes must go through explicit graph APIs.
- Public `.edges` attribute usage is forbidden outside the explicit removal sentinel test.

## Direct Edge Append Allowlist

- None.

## Edge Usage Allowlist

- None.

## Deterministic Inventory Commands

```bash
rg -n "from\\s+[.\\w]+types\\s+import\\s+.*\\bEdge\\b|\\bEdge\\(" ilc_core tests | sort
rg -n "\\.edges\\.append\\(" ilc_core tests | sort
```

## Notes

- Guardrail enforcement is implemented by `tests/test_edge_removal_phase1_guardrails.py`.
- This baseline was reduced in phases 974 and 975, moved to zero `Edge`-symbol usage in phase 976, removed direct append compatibility in phase 977, and received closure guardrail cleanup in phase 978.
