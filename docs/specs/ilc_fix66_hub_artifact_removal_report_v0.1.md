# ILC Fix66 Hub Artifact Removal Report

PUBLIC_RC_EXCLUDE: fix66_hub_artifact_removal_research_only

## Summary

- Hub artifact: `policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22`
- Pre-removal LMDB: `16810` nodes / `93909` edges
- Hub incident edges removed: `4304`
- Hub node removed: `1`
- Residual audit queue entries: `10`
- Post-repair LMDB before phase-file registration: `16809` nodes / `89605` edges
- Governance export after repair: `9776` nodes / `48298` edges

## Hub Edge Breakdown

```json
{
  "in:CLASSIFIED_BY": 4300,
  "in:GOVERNS": 1,
  "out:REFERENCES_AUTHORITY": 2,
  "self:CLASSIFIED_BY": 1
}
```

## Boundary

This phase repairs the local unsigned Atlas LMDB candidate topology only. It does
not sign Genesis, publish the graph, activate public serving, mint ECU, settle
ILC, clear a public path gate, or mutate canonical protocol authority.
