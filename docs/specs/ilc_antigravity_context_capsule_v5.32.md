# ILC Antigravity Context Capsule v5.32

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.31.md
Date: 2026-04-28
Owner lane: Window 945–952 — H-012 Attribution Settlement Runtime + CDL-082 Threshold Amendment

`capsule_v5_32_supersedes_v5_31`
`window_945_952_open_phase_945`
`cdl_081_ratified_phase_943`
`h013_closed_phase_938`
`sim_beacon_01_complete_phase_939`
`sim_reuse_01_complete_phase_941`
`phase_numbering_remediation_normal_lane_945_989_then_1100_plus`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 945–952 — Phase 945 (sequence lock). Window open.**

### Closed windows since v5.31

| Window | Topic | Key outcome |
|--------|-------|-------------|
| 921–929 | CDL-080 star.map L3 route index | CDL-080 ratified (Phase 927). 36 tests. Capsule v5.31. |
| 930–938 | H-013 spectral beacon runtime | H-013 CLOSED (Phase 938). 35 spectral beacon tests. `PeerFingerprintCache` + L3 wired. Testnet emission live. |
| 939–944 | Post-H-013: SIM-BEACON-01, SIM-REUSE-01, CDL-081 ratification | CDL-081 ratified (Phase 943). 30 ratification evidence tests. Phase numbering remediation. CLAUDE.md created. |

### Inter-phase sub-commits

| Phase | Key work |
|-------|----------|
| 0928x | CSPRNG noise + epoch-keyed replay cache in `spectral_beacon.py` |
| 0919x | blahaj migration (`ilc_consensus/` Rust crate upgrade) |

### Current position

Phase 945 — Window 945–952 open. Phase table locked by this sequence lock.

---

## 2. CDL Status

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-001 | Open (genesis_blocker) | — | Packaging track |
| CDL-042 | Ratified | 407 | CLI framework |
| CDL-052 | Ratified | 466 | Popperian gate |
| CDL-060 | Ratified | 541 | Centrality delta gossip |
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-076 | Ratified | 897 | Truth primitive announcement gossip (L1) |
| CDL-077 | Ratified | 904 | WANT-HAVE/WANT-BLOCK fetch (L2) |
| CDL-078 | Ratified | 911 | Relay incentive constitutional lock (L5) |
| CDL-079 | Ratified | 918 | HB-002 P2P bootstrap distribution protocol |
| CDL-080 | Ratified | 927 | star.map N-gram route index (L3) |
| CDL-081 | **Ratified** | **943** | **Hyperedge ECU attribution** (`REUSE_ATTRIBUTION_RATE = Decimal("0.20")`) |
| CDL-082 | To be opened | 948 (this window) | H-013 gossip beacon emission threshold amendment |
| CDL-070 | Deferred | — | PQ migration |

Next fresh CDL number after this window: **CDL-083**.

---

## 3. Key SIM Findings

### SIM-BEACON-01 (Phase 939)

Source: `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`

- `adversary_reduction ≈ 0.684 = 1 - 1/√T` — mathematical constant for T=10 Gaussian averaging,
  regardless of sigma. Privacy target (≤ 0.50) is not achievable via sigma tuning.
- **Correct interpretation:** Sealed-sender (ADR-0034) is the primary privacy mechanism. Each
  beacon is sealed per-recipient with a different emission ID — accumulating T=10 observations
  is non-trivial for an adversary under sealed-sender. Sigma noise is secondary obfuscation.
- Adversary model needs revision for a future SIM before any mainnet sigma parameter change.

Provisional parameter recommendations (pending CDL amendment):
- `H013_TESTNET_EMISSION_SIGMA = 0.05` — keep (routing correctness 97.65%)
- `H013_CHANGE_THRESHOLD` → raise 0.10 → 0.15 (exits spurious-emission regime) — CDL-082 this window
- `DEFAULT_DEAD_PEER_SILENCE_EPOCHS = 10` — confirmed (0% false-dead rate)

### SIM-REUSE-01 (Phases 940–941)

Source: `docs/specs/ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md`

- `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` — resolved CDL-081 Q6.
- Gaming non-attractive by construction: `gaming_roi_ratio < 0.02` at all tested rates.
  Gaming (fake reuse traversal at 1.5× cost) yields `rate × TRAVERSAL_ECU_BASE` ECU — structurally
  non-attractive regardless of rate parameter choice.
- Sharp floor at rate=0.10 confirmed.

---

## 4. H-013 Status

**CLOSED (Phase 938).** 35 spectral beacon tests. All pass.

Modules deployed:
- `ilc_core/node/spectral_beacon.py` (epoch-keyed replay cache, Phase 0928x)
- `ilc_core/node/node_startup_runtime.py`: `H013_TESTNET_EMISSION_SIGMA = 0.05` (kept)
- `ilc_core/node/node_startup_runtime.py`: `H013_CHANGE_THRESHOLD = 0.1` (to be raised by CDL-082 Phase 950)
- `PeerFingerprintCache` wired; L3 spectral routing connected.

Testnet emission is live.

---

## 5. H-012 Status

`EpochAttributionBatch.settle()` in `ilc_core/types.py` is currently a stub:
```python
CDL_HCON_01_DEPENDENCY = "h_con_01_cdl_required_before_settle_executes"
def settle(self) -> None:
    raise NotImplementedError(CDL_HCON_01_DEPENDENCY)
```

CDL-081 prerequisite is now met (ratified Phase 943). **H-012 runtime implementation is Phase
946–947 (this window).** After Phase 946:
- `CDL_HCON_01_DEPENDENCY` stub is removed.
- `settle()` delegates to `ilc_core/economics/epoch_attribution_settle_runtime.py`.
- Ejected stake treasury sub-path remains stubbed (`CDL_HCON_02_DEPENDENCY`) pending H-CON-02.

---

## 6. CDL-081 Decision Record

CDL-081 constitutionalises ECU attribution for hyperedge traversal. All 6 questions resolved:

| Question | Decision |
|----------|----------|
| Q1 Edge type triggers | REUSE + CO_AUTHORSHIP trigger; ATTESTATION/EPOCH_BOUNDARY excluded; REFUTATION conditional |
| Q2 Stake floor | None — zero-member → commons transition via ADR-0015/CDL-047 |
| Q3 Buy-in decay | CDL-V1 temporal decay from buy-in epoch; no hard lockout |
| Q4 Ejected stake | Treasury accumulation (H-CON-02 quorum required for distribution) |
| Q5 Attribution target | Target node creator receives ECU (Option A); consumer excluded |
| Q6 Per-traversal rate | `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` — SIM-REUSE-01 evidence |

`REUSE_ATTRIBUTION_RATE` is `Decimal` type. Float is explicitly rejected.

---

## 7. Phase Numbering

| Range | Status |
|-------|--------|
| 0055–0989 | Normal constitutional lane (current: 944; next: 945) |
| 0951–1014 | **PERMANENTLY RESERVED** — Cluster-A G8 parallel track (CLOSED) |
| 0990–1099 | **SKIP** — reserved buffer |
| 1100+ | Normal lane resumes after 989 |

Named series (B-series, M-series, SIM-series, H-series, CDL-series) use non-integer identifiers
and are unaffected by the normal lane skip.

`phase_numbering_remediation_normal_lane_945_989_then_1100_plus`

---

## 8. Audit Findings (Phase 944 code audit)

| Finding | Severity | Status |
|---------|----------|--------|
| M1 — PASSIVE_ATTRIBUTION_RATE is float, not Decimal | MEDIUM | **To fix Phase 946** |
| H1 — SSL cert verification disabled in truth_primitive_gossip_runtime.py | HIGH | Tracked — testnet posture, mainnet concern |
| H2 — Bootstrap exception swallowing in node_startup_runtime.py | HIGH | Tracked — mainnet concern |
| M2 — requester_id hardcoded "local" | MEDIUM | Tracked — pre-multi-node |
| M3 — EndorsementCache not thread-safe | MEDIUM | Tracked |
| M4 — PeerFingerprintCache NaN validation | MEDIUM | Tracked |
| M5 — star_map private field mutation | MEDIUM | Tracked |
| L1 — Unsigned gossip announcements | LOW | By design (CDL-036); documented |
| L2 — assert in agent_id_runtime | LOW | Tracked |
| L3 — Equivocation forensic log | LOW | Tracked |

M1 is addressed inline in Phase 946 (`passive_ecu_attribution_runtime.py` Decimal fix).
H1–H2 and M2–M5 are tracked for future windows; not this window's scope.

---

## 9. Forward Obligations

| Item | Status | Window |
|------|--------|--------|
| H-012 settle() runtime | **This window (Phase 946–947)** | 945–952 |
| CDL-082 threshold amendment | **This window (Phase 948–950)** | 945–952 |
| H-CON-02 panel quorum rules | Next window (own CDL) | 953+ |
| Werner φ-bound CDL | Needs SIM evidence | TBD |
| SIM-BEACON-01 adversary revision | Revised SIM with sealed-sender constraints | TBD |
| H-011 patent assessment | Ongoing | — |
| Capsule v5.33 | Phase 951 | 945–952 |
| Audit M2–M5 | Tracked — not this window | TBD |
| Audit H1–H2 (SSL/bootstrap) | Tracked — mainnet concern | TBD |

---

## 10. 5-Layer Network Delivery Architecture

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip | CDL-076 | **Ratified (Phase 897)** |
| **L2** | WANT-HAVE/WANT-BLOCK fetch | CDL-077 | **Ratified (Phase 904)** |
| **L3** | star.map N-gram route index | CDL-080 | **Ratified (Phase 927)** |
| L4 | Onion routing + SURB | Future CDL | Post-L3 |
| **L5** | Relay incentives | CDL-078 | **Ratified (Phase 911)** |

`l1_l2_l3_l5_constitutional_stack_complete`

---

## 11. Test Count

| Scope | Tests |
|-------|-------|
| CDL-081 ratification evidence | 30 |
| H-013 spectral beacon | 35 |
| Window 921–929 (CDL-080 star.map) | 36 |
| Window 913–920 (CDL-079 bootstrap) | 33 |
| Window 906–912 (CDL-078 relay) | 28 |
| Window 899–905 (CDL-077 fetch) | 34 |
| Window 892–898 (CDL-076 gossip) | 26 |
| Window 887–891 (query CLI) | 23 |
| Window 877–886 (CDL-075 graph store) | 31 |
| Window 873–876 (CLI submit) | 22 |
| Window 863–872 (CDL-074 runtime) | 67 |
| Prior windows | 162 |
| **Full regression (Phase 944 baseline)** | **7,643** |

---

## 12. Historical Anchors

- Prior capsule: `docs/specs/ilc_antigravity_context_capsule_v5.31.md` (Window 921–929)
- Phase 944 coherence report: `docs/specs/ilc_integration_coherence_report_944_v0.1.md`
- CDL-081 spec: `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md`
- SIM-BEACON-01 results: `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`
- Passive ECU formula: `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- star.map primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- H-014 SIM-ROUTING-01 result: P50=1–2 hops, two-phase ≥0.80 in all four topology classes
- H-015 spectral routing primitive: `spectral_routing_runtime_h015.v0.1`
- ADR-0034 sealed-sender: primary privacy mechanism; accumulating T=10 beacon observations is non-trivial

`capsule_v5_32_supersedes_v5_31`
`window_945_952_open_phase_945`
`cdl_081_ratified_phase_943`
`h013_closed_phase_938`
