# ILC Antigravity Context Capsule v5.34

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.33.md
Date: 2026-04-29
Owner lane: Window 1102–1109 — CDL-083 H-CON-02 Panel Quorum + REFUTATION Attribution

`capsule_v5_34_supersedes_v5_33`
`window_1102_1109_complete`
`cdl_083_ratified_phase_1105`
`h_con_02_ejected_stake_vote_runtime_implemented_phase_1106`
`h_con_02_evidence_tests_30_pass_phase_1107`

This capsule is self-contained.

---

## 1. Current Frontier State

**Window 1102–1109 complete pending closure gate Phase 1109.**

| Phase | Key work |
|-------|----------|
| 1102 | Sequence lock |
| 1103 | CDL-083 OPEN — H-CON-02 panel quorum + REFUTATION attribution |
| 1104 | CDL-083 prelock hardening + ratification evidence doc |
| 1105 | CDL-083 RATIFIED (two commits: runtime + CDL) |
| 1106 | `evaluate_ejected_stake_vote()` — CDL-083 §§5.1-5.3 |
| 1107 | 30 H-CON-02 ratification evidence tests (G1-G12) — all pass |
| 1108 | Coherence report + capsule v5.34 + hypergraph planning alignment |

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
| CDL-082 | Ratified | 950 | H-013 gossip beacon emission threshold amendment (`H013_CHANGE_THRESHOLD = 0.15`) |
| CDL-083 | **Ratified** | **1105** | **H-CON-02 panel quorum + REFUTATION attribution** |
| CDL-070 | Deferred | — | PQ migration |

Next fresh CDL number: **CDL-084** (PROVENANCE chain attribution, Window 1110+).

---

## 3. H-012 Status

**H-012 settle() implemented with CDL-083 H-CON-02 resolution.** CDL-081/CDL-083 coverage:

| Section | Content | Status |
|---------|---------|--------|
| §4.1 REUSE attribution | `attribution_ECU = REUSE_ATTRIBUTION_RATE` | Implemented |
| §4.2 CO_AUTHORSHIP split | `ECU_i = total × stake_i / Σ stake_j` | Implemented |
| §4.3 Edge type scope | REUSE + CO_AUTHORSHIP; ATTESTATION, PROVENANCE, EPOCH_BOUNDARY ignored | Implemented |
| §4.4 Buy-in decay | CDL-V1 delegation | Implemented |
| §4.5 Ejection fallback | `evaluate_ejected_stake_vote()` — CDL-083 §§5.1-5.3 | **Implemented (Phase 1106)** |
| §5.4 REFUTATION attribution | `settle_attribution_batch()` REFUTATION path — `refuting_agent_id` receives `REUSE_ATTRIBUTION_RATE` | **Implemented (Phase 1105)** |
| §4.6 Zero-member commons | Attribution suspended, commons token | Implemented |

`CDL_HCON_02_DEPENDENCY` remains as a historical marker. `CDL_083_DEPENDENCY` is the live
ratified dependency token. The Phase 1107 H-CON-02 evidence tests pass: 30/30.

---

## 4. CDL-083 Decision Record

| Question | Decision |
|----------|----------|
| Q1 Quorum floor | ≥0.50 of remaining members; hard minimum 2 voters (`HCON02_QUORUM_FLOOR`, `HCON02_QUORUM_MINIMUM_VOTERS`) |
| Q2 Vote threshold | Exact 2/3 supermajority by integer arithmetic (`approve_votes * 3 >= participating_voters * 2`) |
| Q3 Distribution | Proportional to all remaining members' stake at distribution epoch |
| Q4 REFUTATION ECU | Upheld REFUTATION → `REUSE_ATTRIBUTION_RATE` (0.20) to `refuting_agent_id`, epoch mint source |
| Q5 Irrevocability | Ejected stake irrevocable; readmission starts with zero stake |

---

## 5. Forward Obligations

| Item | Status | Window |
|------|--------|--------|
| CDL-084: PROVENANCE chain attribution | Pre-open | 1110+ |
| Werner phi-bound CDL | Needs SIM evidence | TBD |
| SIM-BEACON-01 adversary revision | Revised SIM with sealed-sender constraints | TBD |
| SIM-HYPEREDGE-01 | Gate: CDL-083 ratified; may now plan | Next planning window |
| ADR-0035 implementation CDL | Direction accepted; no CDL opened | TBD |
| H-011 patent assessment | Ongoing | — |
| Capsule v5.35 | Next coherence | Window 1110+ |

---

## 6. Phase Numbering

| Range | Status |
|-------|--------|
| 0055–0950 | Normal constitutional lane (used through Phase 950) |
| 0951–1014 | **PERMANENTLY RESERVED** — Cluster-A G8 parallel track (CLOSED) |
| 0990–1099 | **SKIP** — reserved buffer |
| 1100+ | Normal lane resumes (current position: 1108) |

Window 945–950, 1100–1101 used phases 945–950 in the normal lane, then 1100–1101 after the
reserved skip. Window 1102–1109 continues the resumed normal lane.

`phase_numbering_remediation_normal_lane_945_989_then_1100_plus`

---

## 7. Runtime Constants (CDL-083)

| Constant | Value | File |
|----------|-------|------|
| `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` | `"epoch_attribution_settle_runtime_1106.v0.2"` | `epoch_attribution_settle_runtime.py` |
| `CDL_083_DEPENDENCY` | `"cdl_083_h_con_02_ratified_1105.v0.1"` | same |
| `CDL_HCON_02_DEPENDENCY` | `"h_con_02_cdl_required_before_ejected_stake_treasury_executes"` | same (historical marker) |
| `HCON02_QUORUM_FLOOR` | `Decimal("0.50")` | same |
| `HCON02_QUORUM_MINIMUM_VOTERS` | `2` | same |
| `HCON02_VOTE_THRESHOLD_NUMERATOR` | `2` | same |
| `HCON02_VOTE_THRESHOLD_DENOMINATOR` | `3` | same |

---

## 8. Evidence and Tests

| Scope | Tests |
|-------|-------|
| H-CON-02 evidence tests (Phase 1107) | 30 |
| H-012 regression tests | 31 |
| Phase 1101 closure gate regression | 25 |
| Combined Phase 1108 verification | 86 |

---

## 9. Historical Anchors

- Prior capsule: `docs/specs/ilc_antigravity_context_capsule_v5.33.md`
- Phase 1108 coherence report: `docs/specs/ilc_integration_coherence_report_1108_v0.1.md`
- CDL-083 spec: `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md`
- CDL-083 evidence tests: `tests/test_phase_1107_h_con_02_panel_quorum_settle.py`
- Settle runtime: `ilc_core/economics/epoch_attribution_settle_runtime.py`

`capsule_v5_34_supersedes_v5_33`
`window_1102_1109_complete`
`cdl_083_ratified_phase_1105`
