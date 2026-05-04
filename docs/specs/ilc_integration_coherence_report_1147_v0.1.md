# ILC Integration Coherence Report — Phase 1147

**Date:** 2026-05-04
**Window:** 1139–1147
**Phase:** 1147
**Status:** SENSITIVE closure report

`coherence_report_1147_verdict=pass`

---

## §1 Purpose

This coherence report closes Window 1139-1147. The window corrected the SIM-SPECTRAL-02
Run 02 baseline, signed the 32-node Genesis star map v0.1, ran SIM-SPECTRAL-03 against
that signed topology, and disposed of CDL-085 as DEFER.

No CDL was opened or ratified in this window. No settlement rule changed. Runtime
semantics are unchanged.

---

## §2 Run02 Fix2

Phases 1140 and 1141 established `out/sim_spectral_02_run02_fix2_summary.json` as the
corrected quantitative baseline.

- Matrix size: 333 entries.
- Corrected Track A S3/S1 ratio: `0.6416011282246747`.
- Corrected Track A G2/S1 ratio: `0.8640456434014127`.
- Addendum token: `run02_fix2_disposition_addendum_committed_phase_1141`.

This corrected baseline is the comparison target for SIM-SPECTRAL-03 and supersedes the
pre-fix Run 02 numeric values where the normalized-lambda2 harness matters.

---

## §3 Atlas Tier-1 / GENESIS-COMPILE Checkpoint

The signed Genesis star map v0.1 is now the Tier-1 authority baseline.

- `out/genesis_core_star_map_v0.1.json`: 32 nodes, 55 edges.
- Signed root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`.
- Public verification token: `signature_verified`.
- Checkpoint #1 token: `genesis_compile_checkpoint_1_pass`.
- Human-facing authority grounding: 32/32 nodes included in the signed package.
- Traversal metric: 31 downstream nodes reached from Node 0 by authority-path BFS.

The 31/32 traversal metric is not a defect. Node 0 is the authority origin and is
included in the signed manifest.

---

## §4 SIM-SPECTRAL-03 / CDL-085 Recommendation

SIM-SPECTRAL-03 did not support opening CDL-085.

Key values:

| Metric | Corrected Run 02 | SIM-SPECTRAL-03 |
|--------|------------------|-----------------|
| S1 mean slope | `0.557071692882566` | `0.21355627860399237` |
| S3/S1 | `0.6416011282246747` | `1.6736470076736112` |
| G2/S1 | `0.8640456434014127` | `2.2539040876901315` |

Phase 1145a found no passing topology-overlay variant. Matched-size controls partly
mitigated G2 but not S3. The Phase 1146 disposition therefore correctly declares:

`CDL-085 recommendation: DEFER`

Named architectural finding:

`raw_authority_graph_is_not_the_right_spectral_work_graph`

---

## §5 CDL Chain

The CDL chain is unchanged.

| CDL | Status | Note |
|-----|--------|------|
| CDL-084 | Ratified | Frontier attribution CDL; `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` locked |
| CDL-085 | Deferred / SIM-gated | Not opened; requires SIM-SPECTRAL-04 claim-composition evidence before reconsideration |

No prelock, opening, ratification, or constitutional mutation occurred in Window
1139-1147.

---

## §6 Runtime Chain

Runtime semantics are unchanged.

| Item | Status |
|------|--------|
| `epoch_attribution_settle_runtime.py` | `epoch_attribution_settle_runtime_1129_fix1.v0.5` |
| `CDL_084_DEPENDENCY` | `"cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` |
| `PROVENANCE_DECAY_ALPHA` | `Decimal("0.45")` |

Audit nuance: commit `102ed6f2` added a comment-only broad-except justification to
`ilc_core/analysis/embedding_pipeline.py`. This is not a runtime semantic mutation and
does not change the active runtime version.

---

## §7 Audit Findings

Findings and carry-forward:

- Phase 1147 closure gate passes with targeted evidence tests.
- Dirty monitoring snapshots remain unrelated and pre-existing:
  `out/monitoring/d2e_risk_snapshot_phase_306.json` and
  `out/monitoring/infrastructure_risk_snapshot_phase_316.json`.
- User-provided transcript `docs/research/last_turns_for_review.md` remains untracked and
  outside this closure commit.
- Canon bundle tests are known pre-existing failures and carry forward from the canon
  bundle signing step:
  `test_canon_bundle_audit_artifact.py` and `test_canon_bundle_pipeline_report.py`.
- `102ed6f2` fixed Phase 1145a audit hazards by fail-closing zero/non-finite ratio
  denominators and documenting assumptions.
- `out/genesis_compile_coverage_diagnostic_v0.1.json` is restored to the signed Phase
  1142s content because it is covered by the Genesis bootstrap toolchain manifest.

---

`coherence_report_1147_verdict=pass`
