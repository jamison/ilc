# ILC Antigravity Context Capsule v5.33

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.32.md
Date: 2026-04-28
Owner lane: Window 945–950, 1100–1101 — H-012 Attribution Settlement Runtime + CDL-082 Threshold Amendment

`capsule_v5_33_supersedes_v5_32`
`window_945_1101_complete`
`cdl_082_ratified_phase_950`
`h013_change_threshold_0_15_constitutional_lock`
`h012_partial_settle_implemented_hcon02_stub_active`
`audit_m1_resolved_passive_ecu_decimal_fix`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 945–950, 1100–1101 — Phase 1100 (coherence report). Window 1101 (closure gate) pending.**

### Closed windows since v5.32

| Window | Topic | Key outcome |
|--------|-------|-------------|
| 945–950, 1100–1101 | H-012 attribution settle + CDL-082 + capsule | CDL-082 ratified (Phase 950). H-012 partial settle() implemented (Phase 946). 31 ratification evidence tests. Audit M1 resolved. Phase numbering corrected (951/952 → 1100/1101). |

### What changed this window

| Phase | Key work |
|-------|----------|
| 945 | Sequence lock + capsule v5.32 |
| 946 | H-012 `settle()` runtime + M1 Decimal precision fix |
| 947 | 31 H-012 ratification evidence tests |
| 948 | CDL-082 open — H-013 threshold amendment |
| 949 | CDL-082 prelock hardening + ratification evidence doc |
| 950 | CDL-082 ratification (two-commit: runtime + CDL) |
| 1100 | Phase numbering correction + coherence report + capsule v5.33 |

### Current position

Phase 1100 — Window 945–950, 1100–1101 coherence complete. Closure gate (Phase 1101) pending
human GO token.

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
| CDL-081 | Ratified | 943 | Hyperedge ECU attribution (`REUSE_ATTRIBUTION_RATE = Decimal("0.20")`) |
| CDL-082 | **Ratified** | **950** | **H-013 gossip beacon emission threshold amendment (`H013_CHANGE_THRESHOLD = 0.15`)** |
| CDL-070 | Deferred | — | PQ migration |

Next fresh CDL number: **CDL-083**.

---

## 3. Key SIM Findings

### SIM-BEACON-01 (Phase 939)

Source: `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`

- `adversary_reduction ≈ 0.684 = 1 - 1/√T` — mathematical constant for T=10 Gaussian averaging,
  regardless of sigma. Privacy target (≤ 0.50) is not achievable via sigma tuning alone.
- **Correct interpretation:** Sealed-sender (ADR-0034) is the primary privacy mechanism. Sigma
  noise is secondary obfuscation.
- `H013_CHANGE_THRESHOLD = 0.15` exits spurious-emission regime. Routing correctness: 97.65%
  at sigma=0.05 (unchanged). Adversary model revision is a separate future SIM.

### SIM-REUSE-01 (Phases 940–941)

Source: `docs/specs/ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md`

- `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` — resolved CDL-081 Q6.
- Gaming non-attractive by construction: `gaming_roi_ratio < 0.02` at all tested rates.

---

## 4. H-013 Status

**CLOSED (Phase 938).** 35 spectral beacon tests. All pass. `H013_CHANGE_THRESHOLD = 0.15`
(CDL-082 ratified Phase 950). `H013_TESTNET_EMISSION_SIGMA = 0.05` (unchanged — SIM-BEACON-01
confirmed). Testnet emission is live.

---

## 5. H-012 Status

**Partial settle() implemented (Phase 946).** CDL-081 §§4.1–4.6 coverage:

| Section | Content | Status |
|---------|---------|--------|
| §4.1 REUSE attribution | `attribution_ECU = REUSE_ATTRIBUTION_RATE` | Implemented |
| §4.2 CO_AUTHORSHIP split | `ECU_i = total × stake_i / Σ stake_j` | Implemented |
| §4.3 Edge type scope | REUSE + CO_AUTHORSHIP; others ignored | Implemented |
| §4.4 Buy-in decay | CDL-V1 delegation | Implemented |
| §4.5 Ejection fallback | CDL_HCON_02_DEPENDENCY stub | **Stubbed — H-CON-02 required** |
| §4.6 Zero-member commons | Attribution suspended, commons token | Implemented |

`CDL_HCON_01_DEPENDENCY` stub removed from `ilc_core/types.py`. `EPOCH_ATTRIBUTION_BATCH_VERSION`
updated to v0.2. `settle()` delegates to `ilc_core/economics/epoch_attribution_settle_runtime.py`.

31 ratification evidence tests (Phase 947) — all pass.

---

## 6. CDL-081 Decision Record

| Question | Decision |
|----------|----------|
| Q1 Edge type triggers | REUSE + CO_AUTHORSHIP trigger; ATTESTATION/EPOCH_BOUNDARY excluded; REFUTATION conditional |
| Q2 Stake floor | None — zero-member → commons transition via ADR-0015/CDL-047 |
| Q3 Buy-in decay | CDL-V1 temporal decay from buy-in epoch; no hard lockout |
| Q4 Ejected stake | Treasury accumulation (H-CON-02 quorum required for distribution) |
| Q5 Attribution target | Target node creator receives ECU (Option A); consumer excluded |
| Q6 Per-traversal rate | `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` — SIM-REUSE-01 evidence |

---

## 7. CDL-082 Decision Record

**Ratified Phase 950. SIM-BEACON-01 evidence (Phase 939).**

- `H013_CHANGE_THRESHOLD: float = 0.15` — constitutional lock. Value 0.10 retired.
- No deployment may set this to a value other than 0.15 without a subsequent CDL amendment.
- Runtime mutation: `ilc_core/node/node_startup_runtime.py` (Phase 950 Commit 1).
- CDL mutation: spec OPEN → RATIFIED + log row updated (Phase 950 Commit 2).

Out of scope: `H013_TESTNET_EMISSION_SIGMA` (unchanged), `DEFAULT_DEAD_PEER_SILENCE_EPOCHS`
(unchanged), sealed-sender adversary model revision (separate future SIM).

---

## 8. Audit Findings (Phase 944 code audit)

| Finding | Severity | Status |
|---------|----------|--------|
| M1 — PASSIVE_ATTRIBUTION_RATE float (4 constants) | MEDIUM | **Resolved Phase 946** |
| H1 — SSL cert verification disabled | HIGH | Tracked — mainnet concern |
| H2 — Bootstrap exception swallowing | HIGH | Tracked — mainnet concern |
| M2 — requester_id hardcoded "local" | MEDIUM | Tracked — pre-multi-node |
| M3 — EndorsementCache not thread-safe | MEDIUM | Tracked |
| M4 — PeerFingerprintCache NaN validation | MEDIUM | Tracked |
| M5 — star_map private field mutation | MEDIUM | Tracked |
| L1 — Unsigned gossip announcements | LOW | By design (CDL-036); documented |
| L2 — assert in agent_id_runtime | LOW | Tracked |
| L3 — Equivocation forensic log | LOW | Tracked |

---

## 9. Phase Numbering

| Range | Status |
|-------|--------|
| 0055–0950 | Normal constitutional lane (used through Phase 950) |
| 0951–1014 | **PERMANENTLY RESERVED** — Cluster-A G8 parallel track (CLOSED) |
| 0990–1099 | **SKIP** — reserved buffer |
| 1100+ | Normal lane resumes (current position: 1100) |

Window 945–950, 1100–1101: phases 945–950 in the normal lane, then 1100–1101 after the
reserved skip. Next window: 1102+.

`phase_numbering_remediation_normal_lane_945_989_then_1100_plus`

---

## 10. Forward Obligations

| Item | Status | Window |
|------|--------|--------|
| H-CON-02 panel quorum rules | **Primary next obligation** | 1102+ |
| Werner φ-bound CDL | Needs SIM evidence | TBD |
| SIM-BEACON-01 adversary revision | Revised SIM with sealed-sender constraints | TBD |
| H-011 patent assessment | Ongoing | — |
| Capsule v5.34 | Next coherence | Window 1102+ |
| Audit M2–M5 | Tracked — not this window | TBD |
| Audit H1–H2 (SSL/bootstrap) | Tracked — mainnet concern | TBD |

---

## 11. 5-Layer Network Delivery Architecture

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| **L1** | Announcement gossip | CDL-076 | **Ratified (Phase 897)** |
| **L2** | WANT-HAVE/WANT-BLOCK fetch | CDL-077 | **Ratified (Phase 904)** |
| **L3** | star.map N-gram route index | CDL-080 | **Ratified (Phase 927)** |
| L4 | Onion routing + SURB | Future CDL | Post-L3 |
| **L5** | Relay incentives | CDL-078 | **Ratified (Phase 911)** |

`l1_l2_l3_l5_constitutional_stack_complete`

---

## 12. Test Count

| Scope | Tests |
|-------|-------|
| H-012 ratification evidence (Phase 947) | 31 |
| CDL-081 ratification evidence (Phase 943) | 30 |
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
| **Full regression (Phase 949 boundary)** | **7,644** |

---

## 13. Historical Anchors

- Prior capsule: `docs/specs/ilc_antigravity_context_capsule_v5.32.md` (Window 945 open)
- Phase 1100 coherence report: `docs/specs/ilc_integration_coherence_report_1100_v0.1.md`
- CDL-082 spec: `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md`
- CDL-081 spec: `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md`
- Settle runtime: `ilc_core/economics/epoch_attribution_settle_runtime.py`
  (`EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_946.v0.1"`)
- SIM-BEACON-01 results: `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`
- Passive ECU formula: `passive_ecu = min(base_reward × 0.20 × centrality_score × m_i, base_reward × 0.15)`
- star.map primitive: `docs/specs/star.map.ngram.route_index.v1.md`
- ADR-0034 sealed-sender: primary privacy mechanism; T=10 Gaussian averaging yields constant
  `adversary_reduction ≈ 0.684` regardless of sigma

`capsule_v5_33_supersedes_v5_32`
`window_945_1101_complete`
`cdl_082_ratified_phase_950`
`h013_change_threshold_0_15_constitutional_lock`
