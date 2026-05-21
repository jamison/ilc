# ADR-0044: Anti-Capture Diversity Verification

**Status:** Accepted
**Date:** 2026-05-21
**Phase:** 1418
**Author:** Jamison and Codex
**Dependencies:** ADR-0040, ADR-0042, ADR-0043, CDL-V3, Phase 397, Phase 1412, Phase 1413, Phase 1417, Phase 1398/J-008

`anti_capture_diversity_adr_accepted_phase_1418`
`cdl_v3_jury_assignment_wiring_defined_phase_1418`
`vrf_outsider_selection_contract_defined_phase_1418`
`anti_capture_diversity_not_verified_phase_1418`

---

## Context

J-008 records `ANTI_CAPTURE_DIVERSITY_VERIFIED` as a blocking `NOT_MET`
condition. At J-008 time, the gate source correctly said the VRF verifier was
not implemented and that CDL-V3 cluster diversity was not wired into jury
assignment. Since then, Phases 1411-1413 implemented the VRF proof verifier,
integrated audit-only high-value VRF ordering into `jury_assignment_runtime.py`,
and tested that integration without production activation.

The remaining anti-capture gap is therefore narrower:

1. `jury_assignment_runtime.py` already enforces same-operator-domain
   independence through `_INDEPENDENCE_K = 3` and `_MAX_PER_OPERATOR_DOMAIN = 4`.
2. `jury_assignment_runtime.py` already carries `cluster_id` on each
   `EligibleAgent`.
3. `jury_assignment_runtime.py` already verifies externally supplied VRF proof
   material for high-value audit quotes and orders candidates by
   `(beta_bytes, agent_id)`.
4. CDL-V3 cluster-share enforcement exists in
   `ilc_core/consensus/diversity_floor_runtime.py`, but it is not yet wired into
   the jury assignment path.

Phase 1418 is design-only. Runtime wiring and the verification evidence token
belong to Phase 1419.

## Claim Verification Table

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-V3 diversity runtime exists | `ilc_core/consensus/diversity_floor_runtime.py` | confirmed: `CDL_V3_RUNTIME_VERSION = "cdl_v3_diversity_floor_runtime_397.v0.1"` |
| CDL-V3 exposes max-cluster-share helper | `ilc_core/consensus/diversity_floor_runtime.py` | confirmed: `compute_max_cluster_share(...)` |
| `EligibleAgent` carries `cluster_id` | `ilc_core/epistemic/jury_assignment_runtime.py` | confirmed |
| Same-operator independence is already enforced | `ilc_core/epistemic/jury_assignment_runtime.py` | confirmed: `_INDEPENDENCE_K = 3`, `_MAX_PER_OPERATOR_DOMAIN = 4`, `same_operator_domain_not_independent` |
| VRF verifier is integrated into high-value audit assignment | `ilc_core/epistemic/jury_assignment_runtime.py` and `tests/test_phase_1413_vrf_integration.py` | confirmed: `vrf_verifier_integrated_jury_assignment_phase_1412`, `assignment_mode="vrf_verified"` |
| J-008 anti-capture gate source remains static NOT_MET | `ilc_core/epistemic/jury_activation_gate.py` | confirmed: `ANTI_CAPTURE_DIVERSITY_VERIFIED` remains `NOT_MET` |

## Decision

Production anti-capture diversity verification requires three independent checks
to pass together before Phase 1425 may mark J-008
`ANTI_CAPTURE_DIVERSITY_VERIFIED` as satisfied:

1. Same-operator-domain independence is enforced for the selected regular panel.
2. High-value assignment uses externally supplied RFC 9381 VRF proof material
   and visible exclusion reasons for missing or invalid proofs.
3. CDL-V3 cluster diversity is enforced against `EligibleAgent.cluster_id` using
   the Phase 397 diversity-floor runtime helpers.

The Phase 1419 runtime target is:

```text
ilc_core/epistemic/jury_assignment_runtime.py
```

The Phase 1419 evidence token is:

```text
anti_capture_diversity_verified_phase_1419
```

## Already-Wired Invariants

`jury_assignment_runtime.py` already contains these anti-capture surfaces:

| Surface | Current behavior |
|---------|------------------|
| Panel shape | `7` regular reviewers plus `1` outsider reviewer |
| Same-operator independence | no more than `_MAX_PER_OPERATOR_DOMAIN = 4` regular reviewers from one operator domain |
| Independence target | `_INDEPENDENCE_K = 3` distinct operator-domain contribution guarantee |
| Author conflict exclusion | author `agent_id` and author `operator_domain` are removed from the pool |
| Outsider seat | selected from `outsider_candidate_flag=True` candidates outside author domain and preferably outside regular-panel domains |
| VRF high-value path | externally supplied proof material is verified by `vrf_beta_from_proof(...)`; invalid proof material excludes the candidate visibly |
| Production default-off guard | `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = True`; non-audit high-value calls fail closed |

These surfaces are necessary but not sufficient. They do not yet enforce the
CDL-V3 cluster-level diversity floor.

## Phase 1419 CDL-V3 Wiring Contract

Phase 1419 must add cluster-diversity evidence without activating production.
The implementation must use `EligibleAgent.cluster_id` and Phase 397 helpers.

Required default jury-diversity constants for Phase 1419:

```python
JURY_CLUSTER_DIVERSITY_FLOOR = 4
JURY_MAX_CLUSTER_SHARE_CEILING = 0.40
```

Rationale:

1. The ADM-003 panel has 8 total seats.
2. A floor of 4 distinct clusters prevents a two-cluster or three-cluster
   capture from satisfying production diversity evidence.
3. A ceiling of `0.40` permits at most 3 of 8 seats from one cluster, because
   `compute_max_cluster_share(largest_cluster_slots=3, total_panel_slots=8)`
   returns `0.375`, while 4 of 8 returns `0.5` and fails.
4. This is a jury-panel anti-capture ceiling, not a validator-topology ceiling.
   CDL-068 validator topology thresholds remain separate.

Phase 1419 must compute diversity evidence over the final selected panel:

```text
selected_panel = regular_panel + outsider_panel
distinct_clusters = count(distinct cluster_id among selected_panel)
largest_cluster_slots = max(counts by cluster_id among selected_panel)
max_cluster_share = compute_max_cluster_share(
    largest_cluster_slots=largest_cluster_slots,
    total_panel_slots=len(selected_panel),
)
```

The selected panel satisfies the Phase 1419 contract only when:

```text
distinct_clusters >= JURY_CLUSTER_DIVERSITY_FLOOR
max_cluster_share <= JURY_MAX_CLUSTER_SHARE_CEILING
```

The quote or verification response must expose the measured values and stable
failure tokens. Recommended tokens:

```text
anti_capture_cluster_diversity_passed_phase_1419
jury_cluster_diversity_floor_not_met
jury_max_cluster_share_ceiling_exceeded
anti_capture_diversity_verified_phase_1419
```

If Phase 1419 discovers that greedy score-order selection can produce a panel
that fails the cluster ceiling while an alternate score-respecting panel could
pass, Phase 1419 must fail closed and document the selector limitation instead
of silently reordering beyond the ADR-0042 VRF ordering contract. A later ADR may
authorize a diversity-constrained VRF selector if needed.

## VRF Outsider Selection Contract

For high-value audit and later production assignment, outsider selection must
use the same VRF-derived score basis as regular selection. The outsider is not a
separate random draw from an unverified source. It is selected from candidates
with `outsider_candidate_flag=True` after proof verification and candidate
exclusion handling.

Missing or invalid proof material must exclude the outsider candidate visibly in
the quote or verification evidence.

Stable boundary: must not silently fall back to epoch-hash shadow assignment for
high-value slots.

Epoch-hash shadow remains permitted only for non-high-value, shadow,
non-production assignment.

## Phase 1419 Verification Evidence

Phase 1419 may record `anti_capture_diversity_verified_phase_1419` only after
focused tests prove all of the following:

1. Non-audit high-value assignment still fails closed while
   `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = True`.
2. Audit-only high-value VRF assignment returns `assignment_mode="vrf_verified"`.
3. Invalid or missing proof material excludes affected candidates visibly.
4. Selected panel evidence reports at least 4 distinct clusters.
5. Selected panel evidence reports max cluster share no greater than `0.40`.
6. A one-cluster or two-cluster candidate pool cannot produce a verified panel.
7. A panel with 4 of 8 selected seats in one cluster fails closed.
8. J-008 gate source remains unchanged until Phase 1425.

## Non-Activation

`anti_capture_diversity_not_verified_phase_1418`

This ADR does not:

- modify `jury_assignment_runtime.py`;
- run the Phase 1419 verification pass;
- mark `ANTI_CAPTURE_DIVERSITY_VERIFIED` as MET;
- modify `jury_activation_gate.py`;
- activate production jury assignment;
- activate public graph admission;
- execute reviewer payment;
- distribute ECU;
- mutate ledger, treasury, wallet, graph, or CDL state.

## Consequences

Phase 1419 has a bounded runtime/audit task: wire selected-panel cluster
diversity evidence into jury assignment, test it with VRF high-value audit
quotes, and record the evidence token while preserving default-off production
guards. Phase 1425 remains responsible for re-verifying all J-008 blocking
tracks and updating the static gate source if the evidence is complete.

Graph delta:
`graph_delta=load_bearing_artifact_added:docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md -> adr/anti_capture_diversity`.
