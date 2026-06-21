# ILC Fix63a Procedural Support Edge Manual Audit Report

PUBLIC_RC_EXCLUDE: fix63a_procedural_support_edge_manual_audit_research_only

## Summary

- Rows reviewed: `373`
- Manual batches: `38`
- Accepted edges: `309`
- Materialized support endpoint nodes: `191`
- Rejected edges: `0`
- Final LMDB: `16346` nodes / `86171` edges / `102520` preimages

## Edge Types

```json
{
  "CLASSIFIED_BY": 373,
  "DERIVED_FROM": 227,
  "GOVERNS": 6,
  "OPENED_FOR": 2,
  "PRELOCK_FOR": 1,
  "RATIFICATION_EVIDENCE_FOR": 1,
  "SAME_AUTHORITY": 25
}
```

## Boundary

This phase updates local unsigned Atlas LMDB support and procedural traces only.
It does not sign Genesis, publish a public graph, activate runtime flags,
perform ECU minting, settle ILC, mutate CDL/ADR source documents, or authorize
public RC.
