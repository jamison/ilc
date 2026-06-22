# Fix63d CDL/ADR Lifecycle Governance Cleanup Report

- Phase: `1545p-Fix63d`
- LMDB: `out/genesis_base_graph_v0.4_unified.lmdb`
- Pre-execution queue: `120`
- Queue counts: `{'adr': 48, 'cdl': 72}`
- Node classifications updated: `120`
- Procedural edges written: `2`
- Pre-existing procedural edges observed/skipped before write plan: `37`
- Edge-write duplicate skips inside safe writer: `0`
- Source-backed direct reads: `119`
- Escalated no-source records: `1`
- `GOVERNS` edges written: `0`
- Final LMDB nodes/edges: `16451` / `90047`
- Dangling edges / edge-id debt: `0` / `0`

## Edge Types

- `RESOLVED_BY`: `2`

## Dispositions

- `adr_decision_or_lifecycle_record`: `2`
- `canonical_accepted_adr_no_concrete_governed_target`: `34`
- `canonical_ratified_cdl_no_concrete_governed_target`: `42`
- `escalated_no_source`: `1`
- `lifecycle_opening_record`: `2`
- `lifecycle_prelock_record`: `1`
- `lifecycle_ratification_record`: `1`
- `open_cdl_support_record`: `1`
- `proposed_adr_record_no_governs`: `3`
- `shadow_duplicate_same_authority`: `33`

## Non-Claims

Fix63d is local unsigned Atlas LMDB maintenance only. It does not authorize public RC, publication, runtime activation, ECU minting, ILC settlement, CDL mutation, ADR mutation, Genesis signing, or public graph upload.
