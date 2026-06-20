# ILC Fix62d Authority Normalization Report v0.1

## Summary

- Phase: `1545p-Fix62d`
- Canonical authority selections: `137`
- New authority nodes materialized: `25`
- Existing authority nodes updated: `112`
- Root authority semantics present: `137`
- Priority-1 token reference semantics present: `148`
- Next queue entries: `4402`
- Next queue priority counts: `{"1": 1159, "2": 190, "3": 3053}`
- Final LMDB nodes: `16106`
- Final LMDB edges: `77130`
- Final preimages: `93236`

## Interpretation

Fix62d normalizes accepted ADR and ratified CDL authority targets from
source canon, then applies deterministic semantic references only where a
priority-1 invariant/policy node explicitly names one of those accepted or
ratified identifiers. Open/proposed rows are not promoted.

## Non-Claims

- No Genesis signing occurred.
- No public graph upload occurred.
- No public RC activation occurred.
- No ECU minting, settlement, or entitlement was authorized.
- No proposed/open ADR or CDL was promoted.
