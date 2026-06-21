# ILC Fix63 Manual GOVERNS Audit Report

PUBLIC_RC_EXCLUDE: fix63_manual_governs_audit_research_only

## Summary

- Total reviewed: `497`
- Accepted edges: `124`
- Node updates: `497`
- Escalations: `0`
- Final LMDB: `16148` nodes / `85842` edges / `101993` preimages

## Dispositions

```json
{
  "add_governs_from_adr": 1,
  "add_governs_from_cdl": 114,
  "add_governs_from_genesis": 9,
  "adr_decision_record": 2,
  "cdl_lifecycle_record": 4,
  "confirmed_support_stub": 336,
  "open_cdl_stub": 2,
  "proposed_adr_stub": 4,
  "shadow_duplicate_deduped": 25
}
```

## Boundary

This phase updates the local unsigned Genesis Atlas LMDB candidate only. It does
not sign Genesis, publish the graph, activate public serving, perform ECU minting,
settle ILC, mutate the CDL register, open or ratify a CDL, or authorize public RC.

## Carry-Forward

Lifecycle and proposal records are not false or disposable nodes. They should be
enriched in a follow-on pass with non-authority procedural edges such as
`OPENED_FOR`, `PRELOCK_FOR`, `RATIFICATION_EVIDENCE_FOR`, `PROPOSES_CHANGE_TO`,
`RESOLVED_BY`, `SUPERSEDES`, `SAME_AUTHORITY`, or `DERIVED_FROM`. Fix63 only
prevents false authority by avoiding independent root `GOVERNS` edges for those
records.
