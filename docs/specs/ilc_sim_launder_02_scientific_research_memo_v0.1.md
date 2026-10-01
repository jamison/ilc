# SIM-LAUNDER-02 Scientific Research Memo v0.1

**Status:** Research synthesis
**Phase:** GAP-ADVERSARIAL-EPISTEMICS-REPORT-00
**Date:** 2026-10-01
**Corpus:** `research/adversarial_epistemics/`

## 1. Research Program Overview

The adversarial epistemics program tests a central ILC design claim: the graph is
the primary epistemic object, and the jury is one observation operator over that
graph. A binary jury verdict can be operationally useful while still losing
structure that the graph needs to retain for provenance, refutation, and
context-sensitive interpretation.

All results in this memo are model results under the voter error distributions
implemented in the research harness. They are not empirical measurements of the
live ILC protocol, do not activate IEC/K tracking in `ilc_core/`, and do not
claim that real validators or LLM agents follow the simulated distributions.

The harness records SHA-384 self-certification notes for generated result
records. Those notes bind the scripted artifact emitted by the simulation run;
file-level hashes of final Markdown reports are separate repository facts.

## 2. Formal Model Specification

Core variables:

| Variable | Meaning |
|---|---|
| `N` | Total validator or observer population. |
| `E(x)` | Relevant-expertise population for claim `x`. |
| `alpha(x)` | Adversarial fraction within `E(x)`, not global population share. |
| `rho` | Pairwise epistemic error correlation. |
| `d(x)` | Evidence independence coefficient for the dominant edge type. |
| `R` | Reputation-to-selection or refutation-resistance amplification. |
| `delta` | Reputation decay rate in the Werner family of models. |
| `A(x)` | Epistemic attention allocated to claim `x`. |
| `I(x)` | Downstream influence or reuse reach of claim `x`. |

The Phase 1 harness uses explicit Beta-distribution voter models by claim type.
Objective and laundered claims can have similar binary vote fractions despite
different provenance; contextual and subjective claims can have similar binary
vote fractions despite different within/between-context structure; contested and
Popperian claims can have similar binary vote fractions despite different
refutation-resistance profiles.

The staged compression model is:

```text
Observer layer: 4D profile
  (vote_fraction_context_A, vote_fraction_context_B,
   normalized_cluster_count, within_cluster_agreement)

Graph layer: 3D profile
  (within_ctx, between_ctx, cluster_diversity_norm)

Jury layer: 1D profile
  vote_fraction
```

The six claim types in the SIM-LAUNDER-02D through 02H synthesis are:
`OBJECTIVE`, `CONTESTED`, `CONTEXTUAL`, `SUBJECTIVE`, `LAUNDERED`, and
`POPPERIAN`.

## 3. Experiment Chronology

### SIM-LAUNDER-02A

**Question:** Does Epistemic Laundering Factor separate propagation from
corroboration across refutation environments?

**Design:** Five graph populations crossed with four refutation rates and
repeated runs.

**Predictions:** ELF should expose propagation-heavy claims; laundering gain
should remain stable; refutation should not fully erase provenance differences.

**Result:** Laundering gain stayed near 10x in ordinary refutation regimes.
At extreme refutation, all-propagation populations collapsed because every
descendant was refuted.

**Verdict:** Three of four predictions confirmed; one rate-dependence prediction
was refuted.

**Finding:** IEC/ELF detects a provenance risk that raw reuse does not.

### SIM-LAUNDER-02B

**Question:** Can context separation distinguish contextual claims from contested
claims?

**Design:** Four claim types with observer/context triples.

**Predictions:** Contextual claims should show high context separation while
contested claims should not.

**Result:** The measurement sampled the first 30 observers, which all came from
one context. The resulting `ctx_sep=0` readings were a measurement confound.

**Verdict:** Invalidated; P2 verdicts from this run are not usable.

**Finding:** Failed experiments remain evidence: the graph-level metric is
sensitive to sampling design and must specify observer selection.

### SIM-LAUNDER-02B-R1

**Question:** Does corrected sampling recover the intended context signal?

**Design:** Same claim family as 02B, with randomized observer sampling and a
full `n_obs_used` sweep.

**Predictions:** Contextual claims should have high `ctx_sep`; subjective and
contextual claims should remain hard for a binary jury; corrected graph metrics
should recover within/between-context asymmetry.

**Result:** `ctx_sep(CONTEXTUAL)=0.797` and `ctx_sep(CONTESTED)=0.000`; the
context signal was stable from `n_obs=7` to `n_obs=100`.

**Verdict:** P1 refuted due inherited inversion; P2, P3, P4, and P5 confirmed.

**Finding:** Context-preserving graph metrics recover information that the binary
jury discards.

### SIM-LAUNDER-02C

**Question:** Does raw reuse rank a popular falsehood above a contested truth?

**Design:** Popular Falsehood versus Contested Truth across refutation rates,
plus an underspecified proposition context split.

**Predictions:** RRW should over-rank the popular falsehood; IEC/ELF should
separate it; cartel behavior should suppress refutation.

**Result:** ELF ratio was 52-59x. RRW ranked the popular falsehood above the
contested truth despite the latter having far more independent evidence.

**Verdict:** All four predictions confirmed.

**Finding:** RRW is not an independence metric.

### SIM-LAUNDER-02D

**Question:** Does a 4D epistemic profile separate claim types better than a
binary jury?

**Design:** Six claim types and 60,000 trials; compared jury separability with
the 4D observer profile.

**Predictions:** Laundered/objective, Popperian/contested, and
contextual/subjective pairs should be separable in graph/observer dimensions
even when jury fractions are close.

**Result:** 4D separability was 1.287 versus jury separability 0.754, a 71%
advantage. Refutation resistance captured signal rather than cluster
correlation.

**Verdict:** Four of five prediction checks confirmed; one R-specific check
revealed a model limitation.

**Finding:** The graph needs provenance, refutation, and context dimensions; no
single binary vote fraction preserves them.

### SIM-LAUNDER-02E

**Question:** How much accuracy is lost by collapsing graph structure to a jury
fraction?

**Design:** Six claim types and architecture comparison between jury and
context-preserving graph features.

**Predictions:** Graph features should outperform binary jury features and
recover the three collapsed pairs.

**Result:** Graph classifier accuracy was 82.4%; jury classifier accuracy was
33.9%. OBJECTIVE versus LAUNDERED had a graph separation about 2400x the jury
separation.

**Verdict:** Four of five predictions confirmed; one variance prediction was
refuted in an informative direction.

**Finding:** Graph-layer features preserve practical discriminative power that
binary jury output does not.

### SIM-LAUNDER-02F

**Question:** Can matched-RRW populations be separated without adding IEC, R, and
K dimensions?

**Design:** Five populations tuned toward the same mean RRW and then classified
using RRW alone versus a full `(I, R, K)` profile.

**Predictions:** RRW-only classification should be near random; `(I, R, K)`
should separate the matched populations; K should separate the A/D pair; R
should separate fragile versus robust populations.

**Result:** RRW-only accuracy was 0.411 and full 3D accuracy was 0.911.
The A/D pair had `rrw_sep=0.001` and `full_sep=0.241`.

**Verdict:** Three of five prediction checks confirmed; the matching procedure
did not make all RRW values as close as intended, so two checks were refuted or
conditional.

**Finding:** K is a necessary dimension, and RRW by itself is structurally
underspecified.

### SIM-LAUNDER-02G

**Question:** Are IEC, Popperian resistance, and K independent dimensions?

**Design:** Sixteen factorial conditions over IEC level, refutation resistance,
and context mode.

**Predictions:** ELF should decrease with IEC; R should not alter laundering;
K should be orthogonal to IEC and ELF; low IEC should remain high-risk.

**Result:** IEC controlled ELF, but R inflated ELF for low-IEC claims under
moderate refutation. Max K effect on IEC was 0.165 on a 20-origin scale.

**Verdict:** Five of six predictions confirmed; P2 was refuted in the important
direction that R can inflate laundering risk.

**Finding:** IEC, Popperian resistance, and K must not be collapsed into one
score.

### SIM-LAUNDER-02H

**Question:** How much observer information does the graph preserve compared
with the binary jury?

**Design:** Six claim types, 5,000 trials each, staged
Observer -> Graph -> Jury compression.

**Predictions:** Graph accuracy should beat jury accuracy; graph should recover
the three jury-collapsed pairs; graph rank correlation with observer structure
should exceed jury rank correlation.

**Result:** Graph preservation ratio was 0.884 and jury preservation ratio was
0.262. Observer accuracy was 0.8200, graph accuracy 0.8242, and jury accuracy
0.3391.

**Verdict:** All five predictions confirmed.

**Finding:** The graph's within/between-context decomposition is
information-preserving for this model; the binary jury is the lossy projection.

## 4. Cross-Experiment Synthesis

The staged compression cascade observed in 02H is:

```text
Observer structure
  -> Graph layer: about 12% compression loss, rank preservation 0.9536
  -> Jury verdict: about 66% additional loss, rank preservation 0.7464
```

Three pairs collapse in the jury but survive in the graph:

| Pair | Graph separation | Jury separation | What survives to graph |
|---|---:|---:|---|
| OBJECTIVE vs LAUNDERED | 0.7222 | 0.0003 | Cluster diversity/provenance structure |
| CONTEXTUAL vs SUBJECTIVE | 0.1247 | 0.0013 | Within/between context asymmetry |
| CONTESTED vs POPPERIAN | 0.1581 | 0.0228 | Refutation-resistance and cluster structure |

The unexpected finding is that observer 4D accuracy and graph 3D accuracy are
essentially equal in this harness: `0.8200` versus `0.8242`. That does not mean
the live protocol already has these features; it means the proposed graph
features are sufficient under the model to preserve most observer information.

## 5. Protocol Implications

IEC addresses the OBJECTIVE versus LAUNDERED collapse by counting independent
origins rather than descendants. K addresses the CONTEXTUAL versus SUBJECTIVE
collapse by retaining context structure. Popperian weight addresses the
CONTESTED versus POPPERIAN distinction by preserving survived refutation
attempts.

The minimal protocol addition suggested by this research is to record
`origin_id` and `context_id` per vote or attribution event. The IEC+K CDL has
not been opened by this phase; this memo is only supporting evidence and scope.

Three simulations remain explicitly post-RC: SIM-REPUTATION-01 for the Werner
phase boundary, SIM-CAMOUFLAGE-01 for adversarial attention allocation, and
SIM-EVOLVE-01 for adaptive attackers.

## 6. Limitations and Open Questions

The model cannot establish that real-world claims have measurable signal
strength. It also does not prove real LLM-agent independence, because Phase 3
calibration has not run.

The circularity concern remains: a confused jury produces some of the ambiguity
signals used to route hard claims. That may be acceptable if the graph stores
the ambiguity explicitly, but it requires governance and runtime treatment.

Fiedler behavioral partitioning is a hypothesis for detecting multi-cluster
cartel coordination. It is not a confirmed trust metric and is not needed for
basic IEC computation.

Phase 3 real LLM calibration and Phase 4 adversarial tournament work are needed
before any deployment claim about real-world robustness can be made.
