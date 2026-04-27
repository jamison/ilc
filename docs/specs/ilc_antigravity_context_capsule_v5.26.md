# ILC Antigravity Context Capsule v5.26

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.25.md
Date: 2026-04-27
Owner lane: Window 887–891 — Truth primitive read-path query integration

`capsule_v5_26_supersedes_v5_25`
`window_887_891_closed_recorded_in_capsule_v5_26`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 887–891 — COMPLETE.**

| Phase | Topic | Key outcome |
|-------|-------|-------------|
| 887 | Sequence lock | Window 887–891 commissioned |
| 888 | `d2e_query_truth_cli.py` | `handle_query_truth_node` + `handle_query_truth_edges` |
| 889 | `main.py` wiring | `truth-node` + `truth-edges` subcommands of `query` |
| 890 | Tests + coherence report + capsule v5.26 | 23 tests; this phase |
| 891 | Closure gate | Gate document; window closed |

**Previous windows:**
- Window 877–886 COMPLETE. CDL-075 ratified (Phase 884). 282 tests.
- Window 873–876 COMPLETE. CLI `submit` command. 251 tests.
- Window 863–872 COMPLETE. CDL-074 ratified (Phase 870). 229 tests.

---

## 2. Option B Status (unchanged)

`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`

---

## 3. CDL Status (unchanged from v5.25)

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-042 | Ratified | 407 | CLI framework — extended again by Window 887–891 |
| CDL-052 | Ratified | 466 | Popperian gate — intact |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-070 | Deferred | — | PQ migration |

(Full CDL table in v5.25 — unchanged.)

---

## 4. Window 887–891 Deliverable

**New module:** `ilc_core/cli/d2e_query_truth_cli.py`

```python
D2E_QUERY_TRUTH_CLI_VERSION = "d2e_query_truth_cli_888.v0.1"
CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"

def handle_query_truth_node(node_id: str) -> dict:
    # Opens CDL-075 store, get_node(node_id), raises if not found

def handle_query_truth_edges(node_id: str) -> dict:
    # Opens CDL-075 store, iter_edges(), filters by source or target
```

**CLI:** `ilc query truth-node --node-id <cid>` and
`ilc query truth-edges --node-id <cid>` now available.

**No new CDL** — extension of CDL-042 framework.

**Test coverage:** 23 tests in `tests/test_phase_888_891_query_truth_cli.py`

---

## 5. Submit → Persist → Query Loop

The full loop is now operational locally:

```
ilc submit --primitive assert.truth --payload-json '...' \
           --agent-id agent-001 --epoch 1
# → node_id: bafyreicbeey...   graph_persistence: persisted

ilc query truth-node --node-id bafyreicbeey...
# → node_record: {primitive: "assert.truth", agent_id: "agent-001", ...}

ilc query truth-edges --node-id bafyreicbeey...
# → edges: [{edge_type: "asserted_by", source: "bafyreicbeey...", target: "agent-001"}]
```

Both `ILC_TRUTH_GRAPH_STORE_PATH` must be set.

---

## 6. Test Count

| Scope | Tests |
|-------|-------|
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Total** | **305** |

---

## 7. Forward Obligations

| Item | Priority | Status |
|------|----------|--------|
| Network-layer delivery of persisted truth primitive records | Phase 892+ | CDL-076 required |
| Cross-epoch compaction / snapshot export | Deferred | — |
| HB-002 (P2P bootstrap distribution) | RC2+ | Enabled after CDL-073 |
| CDL-070 (PQ migration ceremony) | Deferred | SIM-MONETARY-01 prerequisite |
