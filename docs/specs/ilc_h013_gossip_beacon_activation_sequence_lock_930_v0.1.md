# H-013: Gossip Beacon Activation — Sequence Lock

**Window:** 930–938
**Sequence lock phase:** 930 (2026-04-28)
**Status:** CLOSED — Phase 938 verdict PASS (2026-04-28)
**Supersedes authorization queue:** `docs/specs/ilc_h013_gossip_beacon_activation_authorization_queue_v0.1.md`
**ADR basis:** ADR-0034 (sealed sender, accepted)
**CDL basis:** CDL-080 (star.map L3 routing, ratified Phase 927)

---

## 1. What Is Already Done (No Implementation Needed)

| Item | Status | Commit |
|------|--------|--------|
| X25519 ECDH ephemeral key exchange | Done | 65b51025 |
| ChaCha20Poly1305 AEAD encryption | Done | 65b51025 |
| Ed25519 signing and verification | Done | 65b51025 |
| Fixed-size padded envelopes (INNER=2048, OUTER=4096) | Done | 65b51025 |
| MIN_NOISE_SIGMA = 0.005 floor | Done | 65b51025 |
| BEACON_EMISSION_MODE_TESTNET/MAINNET constants | Done | d40c458a |
| SpectralBeaconReplayCache keyed by (emission_id, epoch) | Done | 65b51025 |
| `add_noise()` via Box-Muller + os.urandom (CSPRNG) | Done | 65b51025 |
| `spectral_hash()` SHA-256 of sorted big-endian doubles | Done | 65b51025 |
| `spectral_distance()` routing metric | Done | f69a87da |
| ADR-0034 accepted (sealed sender protocol) | Done | Prior window |
| CDL-080 L3 route index runtime | Done | Phase 923–926 |
| `gossip_transport.py` CDL-061 envelope | Done | Phase 558+ |

---

## 2. Authorization Queue Decisions (Applied Phase 930)

### Q1 — H-013 before/after/parallel to SIM-BEACON-01
**Decision: Option C** — testnet-only flag. Implement and emit on testnet only.
Gate mainnet emission on SIM-BEACON-01 noise calibration completion.
`BEACON_EMISSION_MODE_TESTNET` constant already committed (d40c458a).
`h013_q1_option_c_testnet_flag_selected`

### Q2 — Provisional noise sigma for testnet emission
**Decision: sigma = 0.05** (10× more conservative than CDL-080 planning figure of 0.005).
More noise → less information leaked per beacon → safer testnet posture.
SIM-BEACON-01 will calibrate the real figure.
MIN_NOISE_SIGMA = 0.005 floor is enforced at construction boundary; testnet default = 0.05.
`h013_q2_testnet_sigma_0_05`

### Q3 — Peer fingerprint cache eviction policy
**Decision: Option D** — overwrite-only. A cached fingerprint is overwritten only when a
newer beacon from the same peer arrives. No epoch-based eviction. Add `last_seen_epoch`
field to detect dead peers separately from fingerprint staleness. A silent peer keeps its
last-known fingerprint as a routing hint — better than no hint at all.
`h013_q3_option_d_overwrite_only_last_seen_epoch`

### Q4 — Beacon emission frequency
**Decision: Option D** — once per validation epoch, but only if spectral fingerprint has
changed by more than the change threshold. Change gate:
`spectral_distance(lambda_prev, lambda_curr) > 0.1` (provisional; SIM-BEACON-01 calibrates).
Stable nodes emit infrequently — reducing bandwidth and structural information leakage.
`h013_q4_option_d_epoch_cadence_change_threshold_0_1_provisional`

### Q5 — Sealed sender scope
**Decision: Option A** — sealed sender for beacon messages only. Beacon messages are the
specific use case ADR-0034 was designed for. Applying sealed sender to all gossip is a
larger trust model change requiring its own deliberation.
`h013_q5_option_a_sealed_sender_beacon_only`

---

## 3. Phase Plan

```
Phase 930 (this): H-013 sequence lock
Phase 931: PeerFingerprintCache dataclass + population logic stub
Phase 932–933: ≥20 tests for spectral_beacon.py
             (seal/peel/open roundtrip, replay detection, sigma floor,
              fixed-size invariants, epoch-keyed replay cache, AAD binding,
              header sanitization, BEACON_EMISSION_MODE constants)
Phase 934: node_startup_runtime.py peer fingerprint cache integration
           (PeerFingerprintCache keyed by peer_endpoint; populated on beacon receipt)
Phase 935: node_startup_runtime.py L3 wiring
           (live peer fingerprint cache → query_route_index_spectral())
Phase 936: Testnet emission wiring (BEACON_EMISSION_MODE_TESTNET; sigma=0.05;
           change-threshold gate; validation epoch cadence)
Phase 937: Coherence report + ratification evidence (≥20 tests confirmed passing)
Phase 938: Closure gate
```

Window size: 9 phases (930–938).

---

## 4. Hard Pass Conditions

- [x] ≥20 tests for spectral_beacon.py passing (Phase 932–933) — 35 passing
- [x] PeerFingerprintCache dataclass implemented and tested (Phase 931)
- [x] node_startup_runtime.py wired to peer fingerprint cache (Phase 934)
- [x] `query_route_index_spectral()` receiving live fingerprints (Phase 935)
- [x] Testnet emission wiring with BEACON_EMISSION_MODE_TESTNET guard (Phase 936)
- [x] SIM-BEACON-01 commissioning prepared (Phase 937 coherence report §7)
- [x] No mainnet emission path opened (BEACON_EMISSION_MODE_MAINNET unreachable)
- [x] Coherence report confirms no gossip_transport.py behavioral change for non-beacon messages

---

## 5. Scope Boundaries

**In scope:**
- Tests for the already-implemented spectral_beacon.py crypto
- PeerFingerprintCache dataclass and population from incoming beacon messages
- L3 wiring: live fingerprints feeding `query_route_index_spectral()`
- Testnet emission with BEACON_EMISSION_MODE_TESTNET flag and sigma=0.05

**Out of scope (deferred):**
- Mainnet emission (gated on SIM-BEACON-01)
- SIM-BEACON-01 execution (commissioned in this window; executed separately)
- SIM-ROUTING-01 (spectral routing convergence validation)
- Sealed sender extension to non-beacon gossip (requires separate deliberation)
- Beacon relay implementation (bounded one-relay model is implemented; relay node runtime wiring is separate)

---

## 6. Dependency Token Chain

```
H013_SEQUENCE_LOCK = "h013_gossip_beacon_activation_sequence_lock_930.v0.1"
H013_ADR_0034_DEPENDENCY = "run_h013_d2d_sealed_sender_adr_verdict=accepted"
H013_CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index_ratified_927.v0.1"
```

`h013_window_930_938_open`
`spectral_beacon_crypto_complete_tests_pending`
`peer_fingerprint_cache_is_missing_link_for_l3_live_routing`
`testnet_emission_authorized_mainnet_gated_on_sim_beacon_01`
