# ILC Fix62f Runtime Source Trace Report

PUBLIC_RC_EXCLUDE: fix62f_runtime_source_trace_research_only

## Summary

- Phase: `1545p-Fix62f`
- Input priority-2 runtime/source entries: `190`
- Resolved priority-2 entries: `190`
- Carry-forward priority-2 entries: `0`
- Accepted edges: `1145`
- Skipped duplicate edges: `0`
- Rejected edges: `0`
- Final LMDB nodes: `16120`
- Final LMDB edges: `78311`
- Final LMDB preimages: `94434`

## Boundary

This phase updates the local unsigned Genesis Atlas LMDB candidate only. It does
not sign Genesis, publish the graph, activate public serving, mint ECU, settle
ILC, or mutate canonical protocol authority. No ECU minting, production
emission, wallet settlement, or public claimability activation occurred.

## Method

Each priority-2 `public_protocol_graph` file was direct-read from disk in
work-family ordered batches of ten. The evaluator recorded source evidence,
added source-tree membership, derived import edges to existing repo-file nodes,
and added path/content-derived semantic edges only to existing ADR/CDL/policy
targets. Missing targets were rejected rather than stubbed.
