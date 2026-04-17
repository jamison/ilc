# Window 713-716 Guidance — Adaptive Gossip and Resilience Operationalization

**Date:** 2026-04-17  
**For:** Codex (RC main track)  
**Status:** Pre-sequence-lock guidance — Codex must produce the Window 713-716 sequence lock as Phase 713

---

## 1. Where we are

Window 707-712 is closed (`21490efa`). Capsule v4.6 is the live frontier doc.

**Constitutional state at window open:**
- `CDL-066` ratified in Phase `708`
- `CDL-067` ratified in Phase `709`
- `CDL-017` remains open and unratified; prelock evidence exists from Phases `710-711`
- topology-shuffling authorization remains later-scope only; no new `CDL-039`
  ratification occurs in this window

**Simulation / evidence state inherited from Window 707-712:**
- `SIM-VALIDATOR-01` commissioned; results pending
- `SIM-TOPOLOGY-01` commissioned; results pending

**Track B state (verify from `STATUS.md` tail before each phase):**
- `M-012` complete (`2086fc29`)
- `M-013` next

**No pre-window conversation is required for 713-716.** Unlike the validator-agent
sub-lane in §5.2.1, this window has no pre-execution conversation gate.

---

## 2. Window 713-716 scope

**Primary closure targets (§5.3 of carry-forward program):**

1. adaptive-gossip contract
2. partition-repair benchmark pack
3. missing-signal doctrine disposition

**Load-bearing rule for this window:**

Every live gossip parameter must be explicitly sorted into one of:
- `constitutional_law`
- `operator_configurable`
- `deferred`

This is the central governance task of the window. `CDL-060` and `CDL-061`
remain settled source law and must not be reopened while this sorting work is
done.

**Recommended outputs (§5.3):**
- transport resilience contract
- benchmark pack
- explicit law-vs-freedom decision memo

---

## 3. Implementation baseline to read before drafting

The active gossip runtime is the Python D2d stack, not the Rust validator QUIC
stack. Codex must read the live runtime files before drafting any classification
memo:

| File | What it establishes |
|---|---|
| `ilc_core/network/d2d/gossip_peer_registry.py` | `PEER_DISCOVERY_MODE = "static_v1"`, `MAX_PEERS = 16`, deterministic dedup, deterministic prefix peer selection |
| `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` | `MAX_FANOUT = 3`, single-hop validation, bounded fanout runtime |
| `ilc_core/network/d2d/gossip_transport.py` | CDL-061 envelope helper surface, required headers, forbidden headers, `ILC-Epoch` validation |
| `ilc_core/network/d2d/http_gossip_transport_runtime.py` | real HTTP wrapper, `request_timeout_seconds`, payload-size/read timeout surfaces |
| `docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md` | settled CDL-060 lane: single-hop `centrality_delta`, opaque channel, bounded fanout |
| `docs/specs/ilc_cdl_061_gossip_http_envelope_ratification_evidence_561_v0.1.md` | settled CDL-061 lane: envelope form, required/fallback transport binding, header restrictions |
| `docs/specs/ilc_cdl_v1_temporal_decay_runtime_handoff_388_v0.1.md` | existing decay semantics relevant to missing-signal handling |
| `docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md` | earlier partition evidence baseline; use as prior art, not current closure |
| `docs/research/ilc_gossip_hybrid_push_pull_architecture_context_v0.1.md` | original push-pull threat-model rationale; use for context, not as current behavior description |

**Key implementation facts at window open:**
- dynamic peer discovery is not operationalized in the live Python runtime
- `select_fanout_peers()` currently does deterministic sorted-prefix selection
- the live HTTP wrapper has a numeric `request_timeout_seconds` but no full
  adaptive retry/backoff policy
- `ILC-Epoch` is validated as an integer, non-negative header field; wider
  staleness/range policy is not separately formalized in the live code

---

## 4. The three decisions this window must make

### 4.1 Law-vs-freedom classification

The window must publish an explicit classification of every live gossip
parameter. At minimum the inventory must address:

- `PEER_DISCOVERY_MODE`
- `MAX_PEERS`
- `MAX_FANOUT`
- peer-selection behavior in `select_fanout_peers()`
- `request_timeout_seconds`
- `ILC-Epoch` header validation / range behavior
- any live retry or backoff rule if one actually exists in the active path

If a parameter surface is not actually live in the current code path, the
artifact must say so explicitly and classify it as `deferred` rather than
inventing a fake runtime knob.

`CDL-060` and `CDL-061` are settled and may be cited, but not reopened. The
task is classification of inherited live behavior, not new ratification.

### 4.2 Partition-repair benchmark commission

The partition-repair phase commissions evidence. It does not need to deliver
benchmark results in-window.

The benchmark pack must define:
- scenario family
- pass/fail criteria
- evidence format
- what counts as repair
- what remains out of scope because topology shuffling and dynamic discovery are
  still not authorized here

The pack must stay honest about the current `static_v1` peer-registry baseline.
If repair would require dynamic discovery or topology shuffling, that must be
recorded as deferred rather than smuggled in as a present behavior.

### 4.3 Missing-signal doctrine disposition

If expected gossip signals do not arrive, the protocol needs an explicit
behavioral doctrine. The disposition must choose a concrete behavior rather than
leaving the runtime in an implied gray zone.

Candidate behaviors include:
- fail-open
- fail-soft
- fail-closed
- grace period + alert, then degraded behavior

The doctrine artifact must name the selected behavior, the escalation path, and
the implicated source surfaces such as `CDL-V1`, `CDL-060`, and `CDL-061`. It
must not pretend to ratify a new CDL by rhetoric alone.

---

## 5. Candidate phase structure

| Phase | Topic | Character | Key deliverable |
|---|---|---|---|
| 713 | Window 713-716 sequence lock | Gate / Planning | `docs/specs/ilc_phase_713_716_sequence_lock_v0.1.md` |
| 714 | Adaptive-gossip contract and law-vs-freedom classification | Governance / Spec | `docs/specs/ilc_adaptive_gossip_law_vs_freedom_contract_714_v0.1.md` |
| 715 | Partition-repair benchmark pack and missing-signal doctrine | Resilience / Spec | commissioning pack + doctrine disposition |
| 716 | Coherence report, capsule v4.7, and closure gate | Window closure | capsule v4.7, coherence, gate |

This is a four-phase docs/spec window. There is:
- no pre-window conversation gate
- no CDL ratification in-window
- no `CDL-039` ratification in-window
- no benchmark-results requirement in-window

---

## 6. Hard constraints

- Do NOT reopen `CDL-060` or `CDL-061`
- Do NOT ratify any CDL in this window
- Do NOT ratify `CDL-039` or topology shuffling in this window
- Do NOT treat benchmark commissioning as benchmark results
- Do NOT silently classify only some live parameters; the inventory must be complete
- Do NOT mutate `ilc_core/` or `ilc_consensus/` in the docs-only phases (`713-716`)
  unless the sequence lock explicitly adds a runtime phase
- Track B state must be re-read from `docs/phases/STATUS.md` tail at execution time
- Do NOT copy stale Track B wording forward from capsule v4.6 without verifying it

---

## 7. Docs to read at session start

Required reading before Phase 713 begins:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v4.6.md`
3. `docs/phases/STATUS.md` (tail)
4. `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §5.3
5. `docs/specs/ilc_window_707_712_closure_gate_712_v0.1.md`
6. `docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md`
7. `docs/specs/ilc_cdl_061_gossip_http_envelope_ratification_evidence_561_v0.1.md`
8. `docs/specs/ilc_cdl_v1_temporal_decay_runtime_handoff_388_v0.1.md`
9. `docs/specs/ilc_sim_004_partition_resilience_commissioning_results_369_v0.1.md`
10. `docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md`
11. `ilc_core/network/d2d/gossip_peer_registry.py`
12. `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`
13. `ilc_core/network/d2d/gossip_transport.py`
14. `ilc_core/network/d2d/http_gossip_transport_runtime.py`
15. `docs/research/ilc_gossip_hybrid_push_pull_architecture_context_v0.1.md`

---

## 8. Local reviewer responsibilities

- Confirm the Phase 714 classification covers every live gossip parameter and
  explicitly marks any non-live surface as `deferred`
- Confirm `CDL-060` and `CDL-061` are cited but not reopened
- Confirm the partition-repair artifact is commissioning-only and makes no
  benchmark-results claim
- Confirm the missing-signal doctrine names a concrete behavior and escalation path
- Confirm there is no `CDL-039` ratification in the packet
- Confirm capsule v4.7 Track B wording is taken from `STATUS.md`, not memory
- Confirm docs-only phases do not mutate `ilc_core/` or `ilc_consensus/`
