# ILC Integration Coherence Report — Phase 897

Status: final
Date: 2026-04-27
Window: 892–898
Phase: 897

---

## 1. Purpose

This report verifies that Window 892–898 is internally coherent and that CDL-076 truth
primitive announcement gossip connects cleanly to the CDL-075 LMDB graph store and the
CDL-061 gossip transport without disturbing existing handlers.

---

## 2. Scope of Changes

| File | Role |
|------|------|
| `docs/specs/ilc_phase_892_898_sequence_lock_v0.1.md` | Window sequence lock (Phase 892) |
| `docs/specs/ilc_cdl_076_truth_primitive_announcement_gossip_opening_893_v0.1.md` | CDL-076 opening (Phase 893) |
| `ilc_core/network/d2d/truth_primitive_gossip_runtime.py` | Gossip runtime (Phase 894) |
| `ilc_core/cli/d2e_submit_cli.py` | Submit CLI wiring (Phase 895) |
| `tests/test_phase_894_898_truth_primitive_gossip.py` | 26 tests (Phase 896) |
| `docs/specs/ilc_cdl_076_truth_primitive_announcement_gossip_ratification_evidence_897_v0.1.md` | Ratification evidence (Phase 897) |

---

## 3. Coherence Checks

### 3.1 CDL-075 store untouched by gossip path

`truth_primitive_gossip_runtime.py` does not open or read the LMDB store.
The announcement payload is derived entirely from the `write_receipt` dict returned by
`write_truth_primitive_result()`. No `TruthPrimitiveGraphStore` call is made in the gossip path.

Token: `no_lmdb_read_or_write_in_gossip_path` satisfied.

### 3.2 CDL-061 gossip header contract respected

The gossip runtime uses `gossip_transport.build_gossip_headers()` directly, producing the
exact CDL-061 required header set: `ILC-Gossip-Type`, `ILC-Channel`, `ILC-Epoch`,
`ILC-Hop-Count`, `ILC-Signature`, `Content-Type`. No forbidden headers included.
`HOP_COUNT_SINGLE` enforced per CDL-039 single-hop scope.

Token: `no_cdl_061_header_contract_violation` satisfied.

### 3.3 Existing submit CLI result contract preserved

The submit CLI result dict gains one new field (`gossip_delivery`) and is otherwise
unchanged. The `D2E_SUBMIT_CLI_VERSION` token remains `"d2e_submit_cli_874.v0.1"` —
this is a wiring extension, not a new module version. Existing tests for Phases 874 and
882 continue to pass.

Token: `no_existing_submit_handler_mutation_in_window_892_898` satisfied.

### 3.4 CDL-036 dissemination contract honoured

The announcement payload is exactly `{node_id, primitive, agent_id, epoch, cdl_version}`.
No full node record content is transmitted. This is the "soft push-signal" defined by
CDL-036: `"pull-dominant with soft push-signals"`, `"header-first dissemination does not
authorize full-payload push as the default transport rule."`

Token: `no_full_payload_push_in_window_892_898` satisfied.

### 3.5 Activation gate follows CDL-075 pattern

`ILC_D2D_GOSSIP_PEERS` absent → gossip silently skipped with descriptive receipt field.
This mirrors the CDL-075 pattern (`ILC_TRUTH_GRAPH_STORE_PATH` absent → persist skipped).
No crash, no stack trace in either absent case.

### 3.6 No new CDL beyond CDL-076

CDL-076 is the only CDL opened and ratified in this window.

Token: `no_new_cdl_beyond_076_in_window_892_898` satisfied.

### 3.7 Dep-chain guard in gossip runtime

`truth_primitive_gossip_runtime.py` verifies `gossip_transport.GOSSIP_TRANSPORT_RUNTIME_VERSION`
at import time and raises `RuntimeError` on mismatch. Same pattern as existing dep-chain guards
in `http_gossip_transport_runtime.py`.

---

## 4. Forward Obligations Opened by This Window

| Obligation | Vehicle |
|------------|---------|
| CID-addressed pull fetch (WANT-HAVE / WANT-BLOCK) | CDL-077 — Phase 899+ |

---

## 5. Open Forward Obligations Carried Forward

| Obligation | Next window |
|------------|-------------|
| CDL-077: WANT-HAVE/WANT-BLOCK fetch + DoS prevention | Phase 899+ |
| star.map L3 routing (N-gram index, spectral) | H-series, post-RC1 |
| Multi-hop centrality attribution CDL | Future (SIM-MULTI-HOP-01 evidence Phase 552) |
| Relay fee / two-sided ECU routing market | Future CDL |
| HB-002 P2P bootstrap distribution | Re-evaluate each window closure |
| CDL-070 PQ migration ceremony | Deep audit window; SIM-MONETARY-01 prerequisite |
| Cross-epoch compaction / snapshot export | Deferred |

---

## 6. Coherence Verdict

Window 892–898 is coherent. All scope boundaries observed. All exclusion tokens satisfied.
26 new tests pass. No regressions. CDL-076 ratified.

`window_892_898_coherence_verified`
