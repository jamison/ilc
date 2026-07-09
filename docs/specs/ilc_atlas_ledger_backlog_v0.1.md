# Atlas Ledger Backlog — Coverage Gap Progress Tracker

**Total historical gap (pre-protocol files):** 4,982 files  
**Protocol start:** 2026-06-16 (Graph Intake Protocol established)  
**Last audit:** 2026-07-09  
**Ledger file:** `docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json`  
**Future queue file:** `docs/specs/ilc_atlas_ledger_backlog_queue_v0.1.json` (not yet materialized)

> Run the coverage audit script from the taxonomy spec §9 to regenerate the true current gap.  
> This file tracks batch-level progress until a machine-readable queue file is materialized.

---

## Priority Order

1. **`ilc_core/` runtime modules** — load-bearing; benefit from `IMPLEMENTS`, `TESTS` edges (417 files)
2. **`docs/specs/`** — governance docs, CDL evidence, ADR specs; mix of load-bearing and support (1,878 files)
3. **`tests/`** — support_only but adds `TESTS` → module edges (877 files)
4. **`tools/`** — mostly support_only (422 files)
5. **`docs/antigravity_tasks/`** — support_only, lowest priority (1,388 files)

---

## Batch Progress

| Batch | Files | Directory range | Status | Annotator |
|-------|-------|-----------------|--------|-----------|
| catchup_batch_001 | #001–010 | ilc_core/agent.py … ilc_core/analysis/epistemic_code.py | complete — fd371d8df | sonnet |
| catchup_batch_002 | #011–020 | ilc_core/analysis/epoch_report_export.py … ilc_core/analysis/namespace_health.py | pending | — |
| catchup_batch_003 | #021–030 | ilc_core/analysis/node_value_conformance.py … ilc_core/analysis/utility_flow_rewards.py | pending | — |
| catchup_batch_004 | #031–040 | ilc_core/asgi.py … ilc_core/bundle/type_registry.py | pending | — |
| catchup_batch_005 | #041–050 | ilc_core/ccss/runtime.py … ilc_core/cli/ccss_cli.py | pending | — |
| catchup_batch_006 | #051–060 | ilc_core/cli/d2e_agent_cli.py … ilc_core/cli/sidecar_cli.py | pending | — |
| catchup_batch_007 | #061–070 | ilc_core/config.py … ilc_core/consensus/production_bridge.py | pending | — |
| catchup_batch_008 | #071–080 | ilc_core/consensus/reputation.py … ilc_core/economics/outcome.py | pending | — |
| catchup_batch_009 | #081–090 | ilc_core/economics/passive_ecu_attribution_runtime.py … ilc_core/epoch/epoch_emission_production_path.py | pending | — |
| catchup_batch_010 | #091–100 | ilc_core/epoch/epoch_emission_runtime.py … ilc_core/genesis/genesis_state_bundle_runtime.py | pending | — |
| catchup_batch_011 | #101–110 | ilc_core/genesis/genesis_state_bundle_runtime.py … ilc_core/identity/sybil_resistance_runtime.py | pending | — |
| catchup_batch_012 | #111–120 | ilc_core/ledger/__init__.py … ilc_core/ledger/claimability_proof_binding_runtime.py | pending | — |
| catchup_batch_013 | #121–130 | ilc_core/ledger/distributed_conversion_schema.py … ilc_core/ledger/settlement_verification.py | pending | — |
| catchup_batch_014 | #131–140 | ilc_core/ledger/stake_snapshot.py … ilc_core/network/wire_transport_runtime.py | pending | — |
| catchup_batch_015 | #141–150 | ilc_core/node/__init__.py … ilc_core/protocol/commit_epoch_emission_runtime.py | pending | — |
| catchup_batch_016 | #151–160 | ilc_core/protocol/event_export.py … ilc_core/protocol/ilc_cluster_a_conformance.py | pending | — |
| catchup_batch_017 | #161–170 | ilc_core/protocol/ilc_cluster_a_ingest.py … ilc_core/rc/gap_7_closure_status.py | pending | — |
| catchup_batch_018 | #171–180 | ilc_core/rc/genesis_v0_2_signing_ceremony_gate.py … ilc_core/sidecars/idea_descent_rehearsal.py | pending | — |
| catchup_batch_019 | #181–190 | ilc_core/sidecars/local_graph_memory_projection.py … ilc_core/storage/lmdb_public_runtime.py | pending | — |
| catchup_batch_020 | #191–200 | ilc_core/storage/truth_primitive_graph_lmdb_adapter.py … ilc_core/validator/trust_tier_runtime.py | pending | — |

---

## Remaining Queue Summary (after catchup batch 020)

| Priority group | Files remaining after batch 100 |
|---|---|
| `ilc_core/` (remainder) | ~217 |
| `docs/specs/` | 1,878 |
| `tests/` | 877 |
| `tools/` | 422 |
| `docs/antigravity_tasks/` | 1,388 |
| **Total remaining** | **~4,782** |

---

## How to Run a Batch

Each batch is 10 files. For each file:
1. Read the file in full
2. Write a `manual_read_summary` (1 sentence — must describe actual content, not the filename)
3. Classify `node_kind` (see taxonomy spec §3)
4. Choose edges (see taxonomy spec §4 and §5 decision tree)
5. Add the annotation record to the ledger JSON atomically (mkstemp + os.replace)
6. Mark the batch row above as `complete — <commit_hash>`

**Taxonomy reference:** `docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md`  
**Audit script:** run §9 from the taxonomy spec to confirm the batch was registered.

---

## Completed Batches

*(none yet — catch-up batches are pending)*

Previously completed (in-protocol):

| Batch | Files | Phase | Commit |
|-------|-------|-------|--------|
| manual_batch_001 through manual_batch_078 | 760 files | Various phases (pre-1573) | various |
| manual_batch_079 | 19 retroactive (1573e–1573i) | Phase 1573u | 40ad8888d |
| manual_batch_080 | 45 files (1573j–current) | Phase 1573u | 40ad8888d |

---

## Notes

- The ~5,000-file historical gap predates the Graph Intake Protocol (established 2026-06-16).
- Batching at 10 files each allows meaningful read-and-classify work without context overflow.
- `ilc_core/` modules are the highest priority because they are load-bearing and benefit most
  from `IMPLEMENTS → cdl:CDL-NNN` and `REFERENCES_AUTHORITY → adr:ADR-NNNN` edges.
- `docs/antigravity_tasks/` phase prompts are lowest priority — they are all `support_only`
  with `SOURCE_TREE_MEMBER` only and do not add semantic graph value.
- Do NOT use boilerplate summaries ("Registers X as a source-tree member…"). Read the file.
- Catch-up batch numbering uses `catchup_batch_NNN` and must not consume
  `manual_batch_NNN` identifiers, which are reserved for current phase ledger
  records.
