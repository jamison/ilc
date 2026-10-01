# Adversarial Epistemics Executive Summary v0.1

**Status:** One-page reviewer summary
**Phase:** GAP-ADVERSARIAL-EPISTEMICS-REPORT-00
**Date:** 2026-10-01

The adversarial epistemics simulation program tested whether ILC's graph can
retain epistemically important structure that a binary jury verdict loses. It
used lightweight probabilistic agents to stress correlated voting, expertise
capture, raw reuse weighting, refutation resistance, and context-dependent
observer disagreement.

The headline result is that, in SIM-LAUNDER-02H, the graph representation
preserved about 88% of observer structure while the binary jury preserved about
26%. Graph classification accuracy was 0.8242, essentially equal to the
observer-layer accuracy of 0.8200; jury classification accuracy was 0.3391.

Three pairs explain why this matters:

- OBJECTIVE vs LAUNDERED: the jury sees nearly identical vote fractions, while
  the graph preserves cluster/provenance structure.
- CONTEXTUAL vs SUBJECTIVE: the jury collapses context-sensitive disagreement,
  while the graph preserves within-context and between-context asymmetry.
- CONTESTED vs POPPERIAN: the jury compresses both into weak agreement, while
  the graph preserves refutation-resistance and cluster-diversity differences.

The protocol implication is narrow but important: ILC should track `origin_id`
and `context_id` at the vote or attribution layer. `origin_id` enables
Independent Evidence Count (IEC), which distinguishes independent corroboration
from copied propagation. `context_id` enables K, the within/between-context
agreement profile that prevents contextual claims from being flattened into
ordinary disagreement.

The program did not establish deployment readiness. SIM-REPUTATION-01,
SIM-CAMOUFLAGE-01, and SIM-EVOLVE-01 remain unrun. Real LLM-agent calibration
has not measured actual pairwise error correlation, and no adversarial
tournament against a live RC has occurred.

All findings here are model results under the simulation harness's assumed
voter error distributions. They are not empirical measurements of the live ILC
protocol, and this phase does not implement IEC, K, or Popperian tracking in
runtime code.
