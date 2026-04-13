# ILC Window 555-564 Candidate Phase Grouping v0.1

Status: candidate phase grouping — awaiting sequence lock
Date: 2026-03-31
Owner lane: G8 Constitution Cluster A

This document supersedes the informal carry-forward notes in the Window 545-554 handoff.
The Phase 555 sequence lock will canonicalize and may amend this grouping.

---

## 1. Window purpose

Window 555-564 binds the ratified CDL-060 gossip lane to a real D2d transport surface,
locks the gossip HTTP envelope contract under CDL-061, and carries the signal-floor
invariant into ADR-0023 without reopening the economics lane.

**Primary lane A**: CDL-061 gossip HTTP envelope governance. Open in Phase 557, ratify in
Phase 561 after implementation evidence exists (CDL-061 ratification after implementation
is the canonical ILC protocol-contract pattern).

**Primary lane B**: D2d transport runtime. Publish `gossip_transport.py` in Phase 558,
harden transport invariants in Phases 559-560, and publish `gossip_peer_registry.py`
in Phase 562.

**Documentation lane**: Carry the `recommended_decay_floor >= recommended_u_floor`
invariant into ADR-0023 in Phase 556, then close the window with coherence and closure
artifacts in Phases 563-564.

**Canary growth**: Probes 6, 7, and 8 are added in Phases 559, 560, and 561 respectively.
The canary finishes Window 555-564 at 8 probes total.

---

## 2. Carry-forward inputs from Window 545-554

| Item | Source | Window 555-564 action |
|---|---|---|
| `signal_floor_governance_adm_only` | Phase 547 | Phase 556 ADR-0023 invariant update |
| `recommended_decay_floor >= recommended_u_floor` | Phase 547 / Phase 554 handoff | Phase 556 documentation lock |
| One-epoch attribution lag is accepted | Phase 548 | Preserved; no runtime change in this window |
| Crash-recovery graceful-zero logging | Phase 548 | Preserved; no runtime change in this window |
| CDL-060 single-hop lane remains complete | Phase 552 | Preserved; no multi-hop authorization |
| `sim_multi_hop_01_insufficient` | Phase 552 | Multi-hop remains deferred |
| `phase_554_verdict=pass` | Phase 554 | Entry gate for Phase 555 |

---

## 3. Architectural decisions locked at window entry

| Decision | Status | Window impact |
|---|---|---|
| ADR-0011 Native P2P Transport Baseline | Accepted | QUIC remains the production wire requirement |
| ADR-0025 D2d HTTP Gossip Transport Binding | Accepted | HTTP/3 over QUIC is production; HTTP/2 over TCP is fallback |
| CDL-024 kind mapping | settled via ADR-0025 | `kind=quic` for HTTP/3, `kind=http` for HTTP/2 |
| CDL-039 topology privacy | ratified | enforced at the gossip HTTP header layer |
| CDL-060 single-hop centrality delta lane | ratified | carried into header contract and transport adapter |

---

## 4. CDL status at window entry

| CDL | Status | Window 555-564 action |
|---|---|---|
| CDL-036 | ratified | no mutation |
| CDL-039 | ratified | no mutation; enforced in transport/header layer |
| CDL-052 | ratified | no mutation |
| CDL-059 | ratified | no mutation |
| CDL-060 | ratified | no mutation; consumed by transport adapter |
| CDL-061 | absent | open in Phase 557 (CDL mutation); ratify in Phase 561 (CDL mutation + ilc_core/) |
| CDL-053 | reserved (unopened) | protected throughout |

---

## 5. Phase map

### Phase 555 — Window 555-564 sequence lock (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_phase_555_564_sequence_lock_v0.1.md`
- `tests/test_phase_555_window_555_564_sequence_lock.py`

Scope:
- Freeze 10-phase program for Window 555-564.
- Lock ADR-0025 HTTP/3 production binding and ADR-0011 QUIC wire requirement.
- Commit CDL-061 opening target for Phase 557 with ordering token `cdl_061_ratification_after_implementation`.
- Bind four carry-forwards from Window 545-554 (Phase 547 ADR-0023 obligation, 1-epoch lag,
  crash-recovery graceful-zero, CDL-061 prelock dep token for Phase 558).
- State CDL-053 reserved throughout window.
- No CDL mutation. No ilc_core/ mutation.

Required verbatim tokens in sequence lock:
- `gossip_transport_http3_binding_selected`
- `cdl_061_gossip_http_envelope_to_open_phase_557`
- `adr_023_invariant_update_phase_556`
- `kind_quic_http3_production_kind_http_http2_fallback`
- `cdl_061_ratification_after_implementation`
- `static_peer_config_no_dht_v1`

Phase 555 commit: touches exactly `{seq_lock_path, test_path}` (2 paths).
Test count: 6 tests (4+2 commit-anchored).

---

### Phase 556 — ADR-0023 signal floor invariant update (NON-SENSITIVE)

Deliverables:
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` (updated: new section appended)
- `tests/test_phase_556_adr_023_signal_floor_invariant.py`

Entry criteria:
- Phase 555 sequence lock contains `adr_023_invariant_update_phase_556` token.

Scope:
- Close Phase 547 forward obligation by appending section
  `## Signal Floor Cross-Module Invariant (Phase 556 addition)` to ADR-0023.
- Document `recommended_decay_floor >= recommended_u_floor` invariant with current values
  (both 0.05); cite `signal_floor_governance_adm_only` governance basis (Phase 547 disposition).
- No other ADR-0023 sections modified. No CDL mutation. No ilc_core/ mutation.

Required verbatim token:
- `signal_floor_cross_module_invariant_documented_phase_556`

Phase 556 commit: touches exactly `{adr_023_path, test_path}` (2 paths).
Test count: 6 tests (4+2 commit-anchored).

---

### Phase 557 — CDL-061 open + prelock (SENSITIVE — CDL mutation)

Deliverables:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (CDL-061 row added)
- `docs/specs/ilc_cdl_061_gossip_http_envelope_prelock_557_v0.1.md`
- `tests/test_phase_557_cdl_061_prelock.py`

Entry criteria:
- CDL-061 does NOT yet exist in the decision log.
- ADR-0025 confirmed Accepted.
- Phase 556 6 tests passing.

Scope:
- Open CDL-061 with `status: open`,
  `candidate_forms: http3_envelope_cbor | http2_fallback_envelope_cbor`.
- Commit prelock artifact with 10 sections (scope, candidate forms, invariants, header field
  set, CDL-039 exclusions, CDL-060 hop-count enforcement, HTTP status code semantics, payload
  encoding, CDL-024 kind canonical representation, prelock governance tokens).
- Ratification explicitly deferred to Phase 561.
- CDL mutation required: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=557`.
- No ilc_core/ changes.

CDL-061 row fields:
- `related_clauses`: CDL-024 / CDL-039 / CDL-060 / ADR-0025
- `candidate_forms`: `http3_envelope_cbor | http2_fallback_envelope_cbor`

Required prelock governance tokens:
- `cdl_061_gossip_http_envelope_prelock`
- `cdl_061_ratification_deferred_to_phase_561`
- `gossip_http_envelope_invariants_locked_at_prelock`
- `cdl_039_exclusions_enforced_at_header_layer`

Phase 557 commit: touches exactly `{cdl_log_path, prelock_path, test_path}` (3 paths).
Test count: 7 tests (5+2 commit-anchored).

---

### Phase 558 — HTTP gossip transport adapter (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/network/d2d/gossip_transport.py` (new file)
- `tests/test_phase_558_gossip_transport_adapter.py`

Entry criteria:
- CDL-061 row present with `status: open`.
- Prelock artifact `ilc_cdl_061_gossip_http_envelope_prelock_557_v0.1.md` exists.
- Phase 557 7 tests passing.

Scope:
- New file only; must not modify `gossip.py`, `peer.py`, `interface.py`, or any non-D2d
  ilc_core/ package.
- Implements `gossip_request_path`, `build_gossip_headers`, `validate_gossip_headers`.
- Uses prelock dep string (`cdl_061_prelock_557.v0.1`); dep string updated to ratified
  form in Phase 561 Commit 1.
- Enforces CDL-039 forbidden header keys (`creator_agent_id`, `node_id`, `ILC-Creator-Agent-Id`,
  `ILC-Node-Id`) at validation layer.
- Enforces CDL-060 `ILC-Hop-Count: 1` requirement.
- No CDL mutation. Forbidden ilc_core/ paths: `gossip.py`, `peer.py`, `interface.py`,
  and all non-D2d ilc_core/ packages (consensus/, security/, ledger/, issuance/, schema/,
  genesis/, epoch/, identity/, cli/, economics/).

Required constants (exact strings):
- `GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v0.1"`
- `CDL_061_DEPENDENCY = "cdl_061_prelock_557.v0.1"` (updated to ratified form at Phase 561)
- `CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"`
- `CDL_060_GOSSIP_RUNTIME_DEPENDENCY = "cdl_060_gossip_runtime_548.v0.1"`

Phase 558 commit: touches exactly `{transport_path, test_path}` (2 paths).
Test count: 12 tests (10+2 commit-anchored).

---

### Phase 559 — Gossip transport adapter hardening (NON-SENSITIVE)

Deliverables:
- `tests/test_phase_559_gossip_transport_hardening.py`
- `tools/run_mutation_canary_phase_297.py` (Probe 6 added)

Entry criteria:
- Phase 558 12 tests passing.
- `gossip_transport.py` contains
  `GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v0.1"`.

Scope:
- Add CDL-039 boundary tests: all 4 forbidden keys verified, forbidden-key rejection
  for each, CDL-039/CDL-060 enforcement tested at boundary.
- Add CBOR/JSON encoding coverage: default CBOR, JSON permitted, text/plain rejected.
- Add Probe 6 to mutation canary: `gossip_transport_cdl_039_forbidden_key_guard`
  (targets removal of `"creator_agent_id"` from `FORBIDDEN_HEADER_KEYS`).
- No modification of `gossip_transport.py`. No CDL mutation. No ilc_core/ changes.

Phase 559 commit: touches exactly `{canary_path, test_path}` (2 paths).
Test count: 8 tests (6+2 commit-anchored).
Canary probe count after Phase 559: 6 probes.

---

### Phase 560 — Canary probes for transport-layer invariants (NON-SENSITIVE)

Deliverables:
- `tools/run_mutation_canary_phase_297.py` (Probe 7 added)
- `tests/test_phase_560_canary_transport_probes.py`

Entry criteria:
- Phase 559 8 tests passing.
- Canary dry-run shows exactly 6 probes.

Scope:
- Add Probe 7 to mutation canary: `gossip_transport_version_guard`
  (targets `GOSSIP_TRANSPORT_RUNTIME_VERSION` constant — stable target, not the CDL dep string).
- No modification of `gossip_transport.py`. No CDL mutation. No ilc_core/ changes.
- Note: Probe 8 (CDL-061 dep chain guard) is deferred to Phase 561 because the dep string
  changes at ratification and must target the ratified form `"cdl_061_ratified_561.v0.1"`.

Phase 560 commit: touches exactly `{canary_path, test_path}` (2 paths).
Test count: 6 tests (4+2 commit-anchored).
Canary probe count after Phase 560: 7 probes.

---

### Phase 561 — CDL-061 ratification (SENSITIVE — CDL mutation + ilc_core/)

Deliverables (Commit 1 — no CDL env required):
- `ilc_core/network/d2d/gossip_transport.py` (dep constant update only)
- `tools/run_mutation_canary_phase_297.py` (Probe 8 added)
- `tests/test_phase_557_cdl_061_prelock.py` (historicalization patch)
- `tests/test_phase_558_gossip_transport_adapter.py` (constant value update)
- `tests/test_phase_561_cdl_061_ratification.py` (new)
- `docs/specs/ilc_cdl_061_gossip_http_envelope_ratification_evidence_561_v0.1.md` (new)

Deliverables (Commit 2 — CDL mutation):
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
  (CDL-061 row: `status: open → ratified`, `ratified_date`, `ratified_phase: 561`,
  `candidate_forms` updated to selected form)

Entry criteria:
- Phase 560 6 tests passing; canary PASS (7 probes).
- CDL-061 `status: open` in decision log.
- `gossip_transport.py` contains `CDL_061_DEPENDENCY = "cdl_061_prelock_557.v0.1"`.

Scope (Commit 1):
- Update `CDL_061_DEPENDENCY` from `"cdl_061_prelock_557.v0.1"` to
  `"cdl_061_ratified_561.v0.1"` — this is the only change to `gossip_transport.py`.
- Add Probe 8: `gossip_transport_cdl_061_dep_guard`
  (targets CDL-061 dep constant; mutant kills at import via dep chain assertion).
- Historicalize Phase 557 prelock test (live CDL-061 open-state check → historical
  prelock reference with comment: `# The Phase-557 CDL-061 open-state check is a historical prelock reference.`).
- Update Phase 558 constant value test to expect `"cdl_061_ratified_561.v0.1"`.
- CDL mutation required for Commit 2: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=561`.

Selected candidate form: `http3_envelope_cbor` with `http2_fallback_envelope_cbor` as permitted fallback.

Required ratification evidence token: `cdl_061_ratification_evidence_complete`

Commit 1: touches exactly 6 paths. No CDL env.
Commit 2: touches 1 path (CDL log only). CDL env required.
Test count: 7 tests (5+2 commit-anchored).
Canary probe count after Phase 561: 8 probes.

---

### Phase 562 — Static gossip peer registry (SENSITIVE — ilc_core/)

Deliverables:
- `ilc_core/network/d2d/gossip_peer_registry.py` (new file)
- `tests/test_phase_562_gossip_peer_registry.py`

Entry criteria:
- CDL-061 `status: ratified`.
- Canary PASS (8 probes).
- Phase 561 7 tests passing.

Scope:
- New file only; must not modify `gossip_transport.py`, `gossip.py`, `peer.py`,
  `interface.py`, or any non-D2d ilc_core/ package.
- Implements v1 static peer configuration (no DHT, no dynamic discovery) per ADR-0025.
- Implements `validate_peer_endpoint` (HTTPS-only), `GossipPeerRegistry` class with
  `peer_count`, `get_peers` (copy semantics), `select_fanout_peers` (lexicographically
  sorted, CDL-039 topology non-inferrability).
- CDL-039 topology invariant as module-level assert on `PEER_DISCOVERY_MODE`.
- No CDL mutation. Forbidden ilc_core/ paths: `gossip_transport.py`, `gossip.py`,
  `peer.py`, `interface.py`, and all non-D2d ilc_core/ packages.

Required constants (exact strings):
- `GOSSIP_PEER_REGISTRY_VERSION = "gossip_peer_registry_562.v0.1"`
- `CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"`
- `CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"`
- `GOSSIP_TRANSPORT_DEPENDENCY = "gossip_transport_runtime_558.v0.1"`
- `PEER_DISCOVERY_MODE = "static_v1"`
- `MAX_PEERS = 16`

Phase 562 commit: touches exactly `{registry_path, test_path}` (2 paths).
Test count: 12 tests (10+2 commit-anchored).

---

### Phase 563 — Coherence report and capsule v2.9 (NON-SENSITIVE)

Deliverables:
- `docs/specs/ilc_integration_coherence_report_563_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v2.9.md`
- `tests/test_phase_563_coherence_report_and_capsule.py`

Entry criteria:
- CDL-061 `status: ratified`.
- Phase 562 12 tests passing.

Scope:
- Coherence report covers 7 sections: window summary, CDL-061 ratification coherence,
  transport adapter dep chain, signal floor invariant closure (Phase 556), CDL-039
  topology privacy enforcement surface, static peer registry scope and Window 565+ forward
  obligations, open items.
- Capsule v2.9 supersedes v2.8: add CDL-061 ratification entry (`http3_envelope_cbor +
  http2_fallback`), update D2d sub-package status (gossip_transport.py Phase 558,
  gossip_peer_registry.py Phase 562), ADR-0025 Accepted note, signal floor invariant closure
  note (Phase 556), canary probe count updated (5 → 8), next window pointer to
  Window 565-574.
- No CDL mutation. No ilc_core/ mutation.

Required coherence tokens:
- `cdl_061_ratified_phase_561`
- `gossip_transport_dep_chain_cdl_060_to_cdl_061_complete`
- `signal_floor_invariant_documented_and_closed_phase_556`
- `static_peer_registry_v1_scope_no_dht`
- `cdl_039_topology_privacy_enforced_at_header_layer`
- `window_565_multi_machine_packaging_carry_forward`

Phase 563 commit: touches exactly `{coherence_path, capsule_path, test_path}` (3 paths).
Test count: 6 tests (4+2 commit-anchored).

---

### Phase 564 — Window 555-564 closure gate and handoff (SENSITIVE — gate + tests)

Deliverables:
- `tools/check_window_555_564_closure_gate_phase_564.sh`
- `tests/test_window_555_564_closure_gate_564.py`
- `docs/specs/ilc_window_555_564_handoff_564_v0.1.md`

Scope:
- 6-category gate: prompt_contract_validation (all 10 phase prompts for 555-564),
  lane_contract_tests (all 9 phase test files for 555-563), cross_phase_regression
  (all prior window closure gate tests from Phase 317 through Phase 554),
  mutation_canary (8 probes, all killed), closure_gate_cli_contract (selftest guard),
  walkthrough_hygiene.
- Selftest chain for category 3: `ILC_PHASE_554_GATE_SELFTEST=1`, `ILC_PHASE_544_GATE_SELFTEST=1`,
  and all prior confirmed guards from Phase 317 through Phase 534. CRITICAL: read each prior
  gate test to verify selftest guard presence before omitting.
- Selftest guard for category 5: `ILC_PHASE_564_GATE_SELFTEST=1`.
- Snapshot isolation: `ILC_PHASE_564_SNAPSHOT_PATH` env override; no canonical
  `out/monitoring/` mutation without `ILC_PHASE_564_ALLOW_SNAPSHOT_WRITE=1`.
- Handoff document: 7 sections including module inventory (gossip_transport.py Phase 558,
  gossip_peer_registry.py Phase 562), canary probe inventory (8 probes), Window 565-574
  carry-forwards (5 items minimum: static peer config format, HTTP/2 fallback activation,
  genesis state serialization, node lifecycle runtime, ops playbook v1).
- Handoff tokens: `phase_564_verdict=pass`, `window_555_564_complete`,
  `cdl_061_ratified_561_gossip_http_envelope_contract`,
  `gossip_transport_dep_chain_complete_through_562`,
  `window_565_574_ready_to_plan`.

No CDL mutation. No ilc_core/ mutation.
Test count: 8 gate tests.

---

## 6. CDL mutation summary for Window 555-564

| Phase | CDL action |
|---|---|
| 555 | None (sequence lock only) |
| 556 | None (ADR-0023 update; no CDL row change) |
| 557 | CDL-061 row opened (`status: open`) — `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=557` |
| 558 | None |
| 559 | None |
| 560 | None |
| 561 — Commit 2 | CDL-061 row ratified (`status: open → ratified`, `ratified_date`, `ratified_phase: 561`, `candidate_forms` updated to selected form) — `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=561` |
| 562-564 | None |

Two CDL mutations total: Phase 557 (open) and Phase 561 Commit 2 (ratify).

---

## 7. ilc_core/ mutation summary for Window 555-564

| Phase | ilc_core/ action |
|---|---|
| 555-557 | None |
| 558 | `ilc_core/network/d2d/gossip_transport.py` (new file — HTTP envelope builder, header validator, status code constants) |
| 559-560 | None |
| 561 — Commit 1 | `ilc_core/network/d2d/gossip_transport.py` (one-line dep constant update: `cdl_061_prelock_557.v0.1` → `cdl_061_ratified_561.v0.1`) |
| 562 | `ilc_core/network/d2d/gossip_peer_registry.py` (new file — static peer config, CDL-039 topology invariant, dep chain from gossip_transport.py) |
| 563-564 | None |

Three total ilc_core/ touches: one new file (Phase 558), one one-line update (Phase 561
Commit 1), one new file (Phase 562). Both new files in `ilc_core/network/d2d/`. All
existing D2d files (`gossip.py`, `peer.py`, `interface.py`, `centrality_delta_gossip_runtime.py`)
remain untouched throughout.

---

## 8. Protected boundaries

The following boundaries must remain intact throughout Window 555-564:

- CDL-053 remains reserved and unopened.
- CDL-039 topology privacy: cluster membership must not be inferrable from gossip HTTP
  headers; `creator_agent_id` and `node_id` are forbidden header keys enforced at the
  envelope layer (not left to runtime discretion).
- CDL-060 row must not be modified (ratified; single-hop lane remains in force).
- CDL-036 row must not be modified.
- Multi-hop centrality: `sim_multi_hop_01_insufficient` disposition stands; no CDL opening
  for multi-hop within this window.
- `ilc_core/network/d2d/gossip.py` must not be modified.
- `ilc_core/network/d2d/peer.py` must not be modified.
- `ilc_core/network/d2d/interface.py` must not be modified.
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` must not be modified.
- `ilc_core/economics/passive_ecu_attribution_runtime.py` must not be modified.
- `ilc_core/epistemic/reuse_centrality_runtime.py` must not be modified.
- No dynamic peer discovery (DHT, mDNS, or similar): `PEER_DISCOVERY_MODE = "static_v1"`
  is the permanent v1 scope per ADR-0025; DHT authorization requires a future CDL.
- ADR-0025 transport selection is locked at window entry; libp2p evaluation is not reopened.
- `out/monitoring/infrastructure_risk_snapshot_phase_316.json` must not be written by any
  gate script run without the explicit `ILC_PHASE_564_ALLOW_SNAPSHOT_WRITE=1` env variable.
- CDL-V3 diversity floor protections unchanged.
- 7+1 quorum ladder unchanged.

---

## 9. Predecessor references

- `docs/specs/ilc_window_545_554_handoff_554_v0.1.md` — Window 545-554 closure
- `docs/specs/ilc_antigravity_context_capsule_v2.8.md` — current capsule at window entry
- `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md` — HTTP/3 production binding (Accepted)
- `docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md` — QUIC wire requirement (Accepted)
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` — signal floor basis (Phase 556 addition target)
- `docs/specs/ilc_signal_floor_policy_consistency_scoping_547_v0.1.md` — Phase 547 governance disposition
- `docs/specs/ilc_sim_multi_hop_01_centrality_calibration_552_v0.1.md` — multi-hop SNR analysis (`sim_multi_hop_01_insufficient`)
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` — Phase 548 gossip runtime (must not modify)
- `ilc_core/economics/passive_ecu_attribution_runtime.py` — Phase 550 ECU attribution runtime (must not modify)
- `tools/run_mutation_canary_phase_297.py` — mutation canary (Probes 6/7/8 added in Phases 559/560/561)
