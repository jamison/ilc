# Fix63b Direct Source Invariant Audit Batch 001 Report

Status: batch001 direct-read complete

This report records the first corrective direct-read batch after the Fix63/Fix63a
audit. The purpose is narrow: replace weak `docs/phases/STATUS.md` evidence for
the first ten invariant rows with direct source citations and add only missing
LMDB edges supported by those reads.

## Batch Scope

- Reviewed nodes: 10
- Direct source files read: ADRs, phase walkthroughs, tests, runtime modules, SIM
  specs, and crawler source files listed in
  `docs/specs/ilc_fix63b_direct_source_invariant_audit_batch001_v0.1.json`.
- Primary correction: evidence provenance, not broad reclassification.

## Findings

1. Several Fix63a graph edges were already correct, but the ledger evidence was
   too weak. Examples: ADR-0020, ADR-0036, and ADR-0037 branchial projection.
2. The ADR-0036 stale-body conflict is resolved by Phase 1173: both ADR-0036
   and ADR-0037 were accepted, with ADR-0036 bounded to release-key mechanics
   and ADR-0037 governing lineage/equivalence semantics.
3. The refutation invariant was the main genuine gap in this batch. Direct
   source reads identify CDL-052 and CDL-083 as the relevant authority surfaces,
   but the exact legacy phrase "zeroes false claim stake and decanonicalizes"
   should not be treated as a single current ratified rule without more source
   evidence.
4. Application-number and Atlas-G rows are support/non-claim invariants. They
   should retain support-only posture and receive evidence links, not new
   authority-bearing GOVERNS edges.

## Recommended LMDB Delta

Applied only the `recommended_new_edges` rows from the JSON ledger through
`AtlasLmdbSafeWriter`:

- Add ADR-0037 `GOVERNS` for the ADR-0036/0037 lineage/PEC invariant.
- Add evidence edges to direct runtime/spec/test sources where missing.
- Add `REFERENCES_AUTHORITY` from the refutation invariant to CDL-052 and CDL-083.

Application result:

- Accepted direct-read semantic edges: 13
- Rejected direct-read semantic edges: 0
- Registered support nodes for the batch artifacts: 3
- Registered support edges for the batch artifacts: 6
- Unified LMDB post-counts: 16,349 nodes / 86,190 edges

Do not remove existing edges in this batch. Do not mutate signed Genesis
artifacts. Do not activate public RC, ECU minting, settlement, or Genesis
signing.

## Carry Forward

Continue direct reads in batches of ten. For each row, cite actual source files
or explicitly escalate if no source can be found. Do not default to STATUS.md
evidence for semantic classification.
