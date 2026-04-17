# Window 713-716 Guidance — Adaptive Gossip and Resilience Operationalization

**Date:** 2026-04-17  
**For:** Codex (RC main track)  
**Status:** Pre-sequence-lock guidance — Codex must produce the Window 713-716 sequence lock as Phase 713

---

## 1. Where we are

Window 707-712 closed today (`21490efa`). Capsule v4.6 is the live frontier doc.

**CDL ratification state at window open:**
- CDL-066 ✓ RATIFIED (Phase 708, `b5f3dce0`)
- CDL-067 ✓ RATIFIED (Phase 709, `bb699f73`)
- CDL-017 OPEN — prelock evidence complete (Phase 710), ratification at Mysticeti convergence window
- CDL-039 OPEN — topology shuffling authorization path published (Phase 711), not ratified

**Simulation commissioning state:**
- SIM-VALIDATOR-01 commissioned (Phase 711) — results pending
- SIM-TOPOLOGY-01 commissioned (Phase 711) — results pending (may complete in later window)

**Track B state (verify from STATUS.md tail before each phase):**
- M-012 `binary_complete` (`2086fc29`)
- M-013 next — real 4-validator liveness run, pending provisioning

**No pre-window conversation required for 713-716.** Unlike §5.2.1 which mandated
Q1-Q6 answers before the validator-agent sub-lane, §5.3 has no such gate.
Codex can begin Phase 713 without a pre-window design conversation.

---

## 2. Window 713-716 scope

**Primary closure targets (§5.3 of carry-forward program):**

1. Adaptive-gossip contract — define what is settled constitutional law vs. operator freedom in gossip behavior
2. Partition-repair benchmark pack — specify and commission evidence requirements for partition/reconnect behavior
3. Missing-signal doctrine disposition — explicit protocol behavior when expected gossip signals are absent

**Recommended outputs (§5.3):**
- Transport resilience contract
- Benchmark pack (specification + commissioning, results may extend)
- Explicit law-vs-freedom decision memo

---

## 3. Implementation baseline to read before drafting

The current gossip runtime is further along than the push-pull architecture
context doc describes. Codex must read the live runtime files, not just the
threat model doc:

| File | What it establishes |
|---|---|
| `ilc_core/network/d2d/gossip_transport.py` | `GOSSIP_TRANSPORT_RUNTIME_VERSION = "gossip_transport_runtime_558.v0.1"`, CDL-061 envelope contract, forbidden header keys, epoch header validation, `_validated_epoch_header` range guard |
| `ilc_core/network/d2d/http_gossip_transport_runtime.py` | `HTTP_GOSSIP_TRANSPORT_RUNTIME_VERSION = "http_gossip_transport_runtime_568.v0.1"`, real HTTP/3+HTTP/2 transport wrapper, `TransportRuntimeConfig` |
| `ilc_core/network/d2d/gossip_peer_registry.py` | `PEER_DISCOVERY_MODE = "static_v1"`, `MAX_PEERS = 16`, dedup via `dict.fromkeys` |
| `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` | `CDL_060_GOSSIP_RUNTIME_VERSION = "cdl_060_gossip_runtime_548.v0.1"`, bounded fanout, single-hop scope |
| `ilc_consensus/src/network.rs` | BFT validator-to-validator gossip (QUIC/mTLS); separate from the Python gossip layer |
| `docs/research/ilc_gossip_hybrid_push_pull_architecture_context_v0.1.md` | Threat model baseline: PUSH = small urgent metadata, PULL = heavy payloads (CDL-036); use for design rationale, not as current behavior description |

**Key implementation facts:**
- `PEER_DISCOVERY_MODE = "static_v1"` — no dynamic discovery yet
- `MAX_PEERS = 16` — bounded at registry level
- CDL-061 selects `http3_envelope_cbor` with `http2_cbor` fallback
- The Python gossip layer (CDL-060/061) and the Rust QUIC layer (BFT validators) are separate stacks

---

## 4. The three open questions this window must resolve

### 4.1 Law vs. freedom in gossip behavior

The central governance question for 713-716 is: which gossip behaviors are
constitutionally mandated (cannot be changed without a CDL), and which are
legitimate operator-configurable parameters?

Current settled law (do not re-open):
- CDL-060: `centrality_delta` gossip type with opaque channel, bounded fanout, single-hop scope
- CDL-061: `http3_envelope_cbor` envelope with `http2_cbor` fallback permitted
- `MAX_PEERS = 16` (runtime constant in `gossip_peer_registry.py`)
- Forbidden header keys (CDL-061 transport invariants)
- Epoch header range validation

Candidate operator-freedom territory (to be explicitly classified):
- Retry intervals and backoff parameters
- Peer selection heuristics within the bounded pool
- Fanout count within the CDL-060 bounded range
- Timeout durations for unresponsive peers
- Partition-detection sensitivity threshold

The law-vs-freedom decision memo must explicitly sort every live gossip parameter
into one of: `constitutional_law`, `operator_configurable`, or `deferred`.

### 4.2 Partition-repair behavior

The current implementation has no explicit partition-detection or repair protocol.
The `static_v1` peer registry means disconnected peers are not replaced.

The window must specify:
- At which layer is partition detected? (gossip layer, application layer, or not at all in this window?)
- What is the protocol behavior during partition? (degrade gracefully, fail-open, or bounded retry?)
- What constitutes "repair" evidence? (reconnection, re-sync, or explicit re-registration?)

The partition-repair benchmark pack commissions evidence — it does not need to
deliver results in-window. The commissioning artifact defines the test scenario,
pass criteria, and evidence format. Results may carry into Window 717+.

### 4.3 Missing-signal doctrine

If a node stops receiving `centrality_delta` gossip signals it expects, what
should it do? Options:

- **Fail-open (current implicit behavior):** continue operating with stale centrality scores
- **Fail-soft:** apply a decay function to stale centrality scores (consistent with CDL-V1 temporal decay)
- **Fail-closed:** halt gossip participation pending signal recovery
- **Grace period + alert:** operate normally for N epochs, then emit a diagnostic signal

The missing-signal doctrine disposition must explicitly name the chosen behavior
and state which CDLs it implicates (CDL-V1 temporal decay, CDL-060 bounded
fanout). It must not silently create new executable law by rhetoric alone.

---

## 5. Candidate phase structure

| Phase | Topic | Character | Key deliverable |
|---|---|---|---|
| 713 | Window 713-716 sequence lock | Gate / Planning | `docs/specs/ilc_phase_713_716_sequence_lock_v0.1.md` |
| 714 | Adaptive-gossip contract + law-vs-freedom memo | Governance / Spec | Contract + classification memo |
| 715 | Partition-repair benchmark commission + missing-signal doctrine | Resilience / Spec | Benchmark commissioning + doctrine disposition |
| 716 | Coherence report + capsule v4.7 + closure gate | Window closure | Capsule v4.7, coherence, gate |

Four phases. No CDL ratification in this window (CDL-039 topology shuffling
is not ratified here — it remains later-authorized). No `ilc_core/` mutation
unless a specific runtime phase is explicitly added to the sequence lock.

---

## 6. Hard constraints

- Do NOT ratify CDL-039 in this window — the Phase 711 scope note explicitly
  deferred topology shuffling ratification to a later window with more evidence
- Do NOT select final production VRF — SIM-TOPOLOGY-01 results may not be available
- Do NOT reopen CDL-060 or CDL-061 scope — those are settled law
- Do NOT reopen CDL-017 or CDL-066 or CDL-067 — ratification states are fixed
- Do NOT treat the partition-repair benchmark commission as benchmark results —
  commissioning and results are separate artifacts
- Do NOT mutate `ilc_core/` or `ilc_consensus/` in the docs-only phases (713, 714, 715, 716)
  unless the sequence lock explicitly adds a runtime phase
- Track B must be verified from `STATUS.md` tail at every phase — do not copy
  M-series state from capsule v4.6 (its Track B line predates M-012 binary_complete)

---

## 7. Docs to read at session start

Required reading before Phase 713 begins:

1. `docs/PLANNING_INDEX.md` — verify current window entry
2. `docs/specs/ilc_antigravity_context_capsule_v4.6.md` — canonical frontier
3. `docs/phases/STATUS.md` (tail) — confirm Phase 712 is the last G8 entry and M-012 is binary_complete
4. `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §5.3 — window scope
5. `docs/specs/ilc_window_707_712_closure_gate_712_v0.1.md` — inherited baseline from previous window
6. `ilc_core/network/d2d/gossip_transport.py` — live gossip transport constants and contract
7. `ilc_core/network/d2d/gossip_peer_registry.py` — peer discovery mode and MAX_PEERS
8. `docs/research/ilc_gossip_hybrid_push_pull_architecture_context_v0.1.md` — threat model (for rationale only)

---

## 8. Local reviewer (Sonnet) responsibilities

- Confirm the law-vs-freedom classification is complete — every live parameter
  must land in one category, not left ambiguous
- Verify partition-repair benchmark commission is scoped as commissioning only —
  no premature results claims
- Verify missing-signal doctrine names a specific behavior and cites the CDLs it implicates
- Verify CDL-039 is NOT ratified
- Verify capsule v4.7 Track B line is read from STATUS.md tail, not copied from v4.6
- Check that no `ilc_core/` or `ilc_consensus/` mutation occurred in docs-only phases
