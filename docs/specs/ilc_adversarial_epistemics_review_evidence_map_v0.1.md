# Adversarial Epistemics Review Evidence Map v0.1

**Status:** Reviewer evidence map
**Phase:** GAP-ADVERSARIAL-EPISTEMICS-REPORT-00
**Date:** 2026-10-01

This document is a pre-report assessment framework for an independent reviewer.
It is not the final external report and is not an advocacy brief.

## 1. Evidence Map Table

| Claim | Primary source | Experimental support | Model confidence | Reviewer assessment column |
|---|---|---|---|---|
| IEC measures provenance independence | Part 12g and SIM-LAUNDER-02C/02F | 02C ELF ratio 52-59x; 02F A/D `rrw_sep=0.001`, `full_sep=0.241` | High within model | [To be filled by reviewer] |
| R, or Popperian weight, is epistemically distinct from IEC | SIM-LAUNDER-02G | P2 refuted: R inflates ELF for low-IEC claims | Medium-high within model | [To be filled by reviewer] |
| K is orthogonal to IEC | SIM-LAUNDER-02G | Max K effect on IEC is 0.165 on a 20-origin scale | Medium-high within model | [To be filled by reviewer] |
| Binary jury loses graph-layer information | SIM-LAUNDER-02H | Graph 88.4% preservation; jury 26.2%; three collapsed pairs | High within model | [To be filled by reviewer] |
| Graph preserves about 88% of observer structure | SIM-LAUNDER-02H | Mean Graph/Observer ratio 0.884 across 15 pairs | Method-dependent; ratio depends on normalization | [To be filled by reviewer] |
| IEC should enter CDL as secondary signal | SIM-LAUNDER-02F/02G/02H | Demonstrates RRW insufficiency, not IEC sufficiency | Medium | [To be filled by reviewer] |
| RRW is insufficient as a standalone metric | SIM-LAUNDER-02C/02F/02G/02H | 52-59x ELF gap; matched-RRW populations with different epistemic profiles | High within model | [To be filled by reviewer] |
| ILC epistemic guarantees hold for high-signal claims | SIM-CORR-02 | Under the Phase 1 voter model only | Medium; model result only | [To be filled by reviewer] |
| ILC is ready for deployment | None | Not established by this research program | Not assessed | [To be filled by reviewer] |
| Three-tier state is needed | SIM-SIGNAL-01 | AUC 0.615 at probe=5 and 0.889 at probe=15; circularity unresolved | Medium | [To be filled by reviewer] |

## 2. Reviewer Scorecard

| Dimension | Astra initial score | Revised after simulation program | Reviewer final score |
|---|---:|---|---|
| Conceptual novelty | 8/10 | Not assigned here | [To be filled by reviewer] |
| Protocol specification completeness | 6/10 | Not assigned here | [To be filled by reviewer] |
| Epistemic mechanism rigor | 5/10 | Not assigned here | [To be filled by reviewer] |
| Adversarial robustness | 4/10 | Not assigned here | [To be filled by reviewer] |
| Economic mechanism rigor | 5/10 | Not assigned here | [To be filled by reviewer] |
| Implementation maturity | 6/10 | Not assigned here | [To be filled by reviewer] |
| Research methodology | N/A | To be assessed | [To be filled by reviewer] |
| Deployment readiness | Not established | Not established | [To be filled by reviewer] |

## 3. Withdrawn Criticisms

The review package should not repeat criticisms already corrected by repo/canon
checks:

- ML-DSA-65 is not the general live identity mechanism. It is used for Genesis
  authority artifacts.
- Stale codebase size and test count claims must not be reused.
- Merkle-Laplacian dual commitment is not live architecture. It remains
  research-only and excluded from public-RC claims.
- Fiedler value is not a trust signal. It is an observability and anomaly signal
  unless and until a separate governance action changes that status.

## 4. Retained and Reinforced Findings

- Epistemic minority and domain-expertise capture remain real concerns. The
  relevant threat variable is `alpha(x)` within `E(x)`, not global attacker
  population share.
- Correlated reasoning remains independent of identity diversity. The jury
  effectiveness function is `f(n, rho, E(x), alpha(x))`.
- Graph laundering is now quantified through ELF and matched-RRW tests.
- Reputation lock-in remains unmeasured in this corpus; SIM-REPUTATION-01 has
  not run.
- Epistemic camouflage remains unmeasured in this corpus; SIM-CAMOUFLAGE-01 has
  not run.
- Identity diversity, epistemic diversity, and evidential independence are
  distinct and should not be collapsed in protocol language.

## 5. Reviewer Package Index

| Artifact | Status | Notes |
|---|---|---|
| Public repository snapshot | Derived outside this phase | Mirror update is not authorized here. |
| `research/adversarial_epistemics/` corpus | Present in private repo | Committed earlier at `58931cb46`; verified in this phase. |
| Simulation result documents | Present | Seven `RESULTS_*.md` files from 2026-09-07 through 2026-09-08f. |
| Scientific memo | Produced by this phase | `docs/specs/ilc_sim_launder_02_scientific_research_memo_v0.1.md`. |
| IEC+K scope document | Produced by this phase | Scoping only; no CDL opening. |
| Forward plan Part 12g | Updated by this phase | Completed SIM table plus remaining work. |

## 6. Non-Claims

- This evidence map does not open, prelock, or ratify any CDL.
- IEC, K, and Popperian weight are not implemented in live runtime by this phase.
- The research results are model results, not empirical live-protocol evidence.
- Public mirror push and package publication are out of scope.
