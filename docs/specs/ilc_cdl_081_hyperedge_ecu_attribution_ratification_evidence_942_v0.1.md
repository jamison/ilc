# CDL-081: Hyperedge ECU Attribution — Ratification Evidence

**Phase:** 942
**CDL-ID:** CDL-081
**Status:** Evidence complete — awaiting human ratification authorization
**Date:** 2026-04-28
**Evidence file:** `tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py`

---

## 1. Ratification Gate Checklist

| Gate item | Status |
|-----------|--------|
| SIM-REUSE-01 calibration complete | DONE — Phase 941 |
| CDL-081 Q6 locked in spec | DONE — Phase 941 (ec01b1e0) |
| Ratification evidence document (≥20 tests) | DONE — 30 tests, Phase 942 |
| H-012 attribution runtime implemented and tested | DEFERRED — post-ratification obligation |
| H-CON-02 opened or deferred with forward obligation | DEFERRED — forward obligation recorded in §5 |
| Human ratification authorization | PENDING |

---

## 2. Test Coverage (30 tests)

### Q1 — Edge type attribution triggers (Tests 01–06)
| Test | Coverage |
|------|----------|
| 01 | All 6 CDL-081 edge types present in EdgeType enum |
| 02 | EdgeType string values stable (serialization safety) |
| 03 | REUSE is in attribution-triggering set |
| 04 | CO_AUTHORSHIP is in attribution-triggering set |
| 05 | ATTESTATION excluded from attribution |
| 06 | EPOCH_BOUNDARY excluded from attribution |

### Q6 — Per-traversal ECU rate (Tests 07–08)
| Test | Coverage |
|------|----------|
| 07 | REUSE_ATTRIBUTION_RATE=None pre-ratification (constitutional state guard) |
| 08 | EDGE_MINT_PHI_BOUND=None pending Werner CDL |

### Provisional constants (Test 09–10)
| Test | Coverage |
|------|----------|
| 09 | PROVENANCE_MAX_DEPTH=3, PROVENANCE_DECAY_ALPHA=0.5 (alpha<1 convergence) |
| 10 | STAR_NODE_MIN_STAKE_ECU is positive Decimal |

### EpochAttributionBatch invariants (Tests 11–16, 30)
| Test | Coverage |
|------|----------|
| 11 | Version token present |
| 12 | CDL gate dependency token (h_con_01 + cdl_required) |
| 13 | Basic instantiation (epoch, events=[], sealed=False) |
| 14 | add_event before seal |
| 15 | seal() prevents further events (ValueError) |
| 16 | settle() raises NotImplementedError (CDL gate) |
| 30 | Multiple events, correct count |

### §4.2 CO_AUTHORSHIP stake-proportional split (Tests 17–18)
| Test | Coverage |
|------|----------|
| 17 | Stake-proportional split formula: ECU_i = total × (stake_i / Σ_j stake_j) |
| 18 | Zero-member denominator must NOT execute attribution |

### §4.6 Commons transition (Test 19)
| Test | Coverage |
|------|----------|
| 19 | Node survives commons transition; attribution suspended |

### Q5 — Attribution target (Test 20)
| Test | Coverage |
|------|----------|
| 20 | ECU flows to creator of target node, not consuming agent |

### Q3 — Buy-in decay (Test 21)
| Test | Coverage |
|------|----------|
| 21 | CDL-V1 temporal decay from buy-in epoch; no hard lockout |

### Q4 — Ejected stake (Test 22)
| Test | Coverage |
|------|----------|
| 22 | Ejected stake to treasury; remaining members unchanged |

### §4.3 Refutation conditional (Test 23)
| Test | Coverage |
|------|----------|
| 23 | REFUTATION attribution gated on CDL-V7 Popperian gate upholding it |

### HyperEdge substrate (Tests 24–25)
| Test | Coverage |
|------|----------|
| 24 | HyperEdge.edge_type accepts EdgeType.REUSE |
| 25 | HyperEdge.edge_type=None valid (backwards compatible) |

### SIM-REUSE-01 evidence anchoring (Tests 26–29)
| Test | Coverage |
|------|----------|
| 26 | SIM-REUSE-01 evidence document exists at expected path |
| 27 | Rate=0.20 disposition token and Q6 resolved token present |
| 28 | Gaming non-attractive token present |
| 29 | CDL-081 spec Q6 locked token present; deferred token absent |

---

## 3. SIM-REUSE-01 Summary

Evidence: `docs/specs/ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md`

| Finding | Result |
|---------|--------|
| Attribution floor | rate=0.10 (rate=0.05 fails creation_rate and Gini targets) |
| Recommended rate | 0.20 (creation_rate=82.3%, Gini=0.197, quality signal preserved) |
| Gaming resistance | Structural — gaming_roi_ratio <0.02 at all rates; not parameter-dependent |
| Over-attribution risk | Gini <0.11 at rate≥0.25 risks erasing epistemic quality gradient |

---

## 4. Post-Ratification Obligations

1. **`REUSE_ATTRIBUTION_RATE`**: update `ilc_core/types.py` from `None` to `Decimal("0.20")`
   (requires ILC_CDL_MUTATION_AUTHORIZED=1 in ratification commit environment)
2. **H-012 attribution runtime**: `EpochAttributionBatch.settle()` implementation
   (currently raises NotImplementedError; CDL_HCON_01_DEPENDENCY gate)
3. **H-CON-02**: Panel hyperedge quorum rules (PROVENANCE, treasury distribution)

---

## 5. H-CON-02 Forward Obligation (Deferred)

H-CON-02 is not opened in this phase. Forward obligation recorded:
- PROVENANCE chain attribution rules (depth cap, α-decay governance)
- Panel hyperedge quorum rules for treasury ECU distribution
- `PROVENANCE_MAX_DEPTH` and `PROVENANCE_DECAY_ALPHA` may not be changed without CDL

---

`cdl_081_ratification_evidence_complete_phase_942`
`30_tests_pass_all_q1_q6_s41_s42_s43_s46_batch_invariants`
`sim_reuse_01_evidence_anchored`
`human_ratification_authorization_pending`
`post_ratification_types_py_update_required`
`h_con_02_forward_obligation_recorded`
