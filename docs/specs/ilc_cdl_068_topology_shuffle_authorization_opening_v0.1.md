# ILC CDL-068 Topology Shuffle Authorization Opening v0.1

Status: opening artifact
Date: 2026-04-20
Decision vehicle: CDL-068
Phase: 736
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`cdl_068_opens_phase_736`
`new_cdl_not_cdl_039_amendment`
`topology_shuffle_authorization_separated_from_transport_contract`
`cdl_068_evidence_checklist_requires_sim_topology_01_results`
`cdl_068_not_ratified_in_window_733_738`
`epoch_hash_v1_production_posture_cdl_068_scope`
`vrf_upgrade_forward_obligation_in_cdl_068`
`q3_settled_2026_04_19_new_cdl_not_cdl_039_amendment`

## 1. Motivation and governing question

CDL-068 opens because the project now has an evidence-backed topology-shuffle
question that cannot remain implied across CDL-017 prelock notes, CDL-039
privacy language, and simulation artifacts.

The governing constitutional question is:

Which validator-topology assignment rules are authorized for production-facing
topology shuffle once validators are already admitted?

The opening is required because the 2026-04-19 Q3 settlement fixed the vehicle
choice cleanly:

- validator topology shuffle authorization is a new CDL,
- it is not a CDL-039 amendment,
- it is not part of CDL-017 admission law.

This phase therefore opens the constitutional lane for topology assignment
without ratifying it.

## 2. Scope: what CDL-068 governs

CDL-068 governs the validator-topology assignment surface after admission.

The opening scope includes:

- randomness source for topology shuffle:
  epoch-hash v1 remains the production v1 posture,
- mandatory VRF upgrade trigger:
  `vrf_upgrade_threshold_validator_count 10` from Phase 734,
- k-regular topology sizing:
  `recommended_k_degree 4` from Phase 735,
- shuffle cadence:
  per-epoch-boundary shuffle cadence, with Phase 735 recommending `1` epoch,
- bounded push budget for the authorized topology:
  Phase 735 recommends fanout `3`,
- validator diversity metric:
  `validator_cluster_id` remains the metric definition,
- Q6 numeric thresholds from the full-pass Phase 735 result:
  `distinct_cluster_floor_recommendation 4` and
  `max_cluster_share_ceiling_recommendation 33`.

CDL-068 therefore governs:

- which validators are assigned to communicate with each other,
- how dense the authorized validator shuffle graph may be,
- what diversity floor and cluster-share ceiling constrain committee
  composition,
- what randomness posture and upgrade trigger apply to the shuffle surface.

## 3. Scope: what CDL-068 does not govern (boundary with CDL-039 and CDL-017)

CDL-068 does not govern:

- transport envelope format,
- opaque-channel routing or hop semantics,
- cluster-membership-non-inferrable transport constraints,
- validator admission, stake-floor law, or validation-pool law,
- runtime implementation details in `ilc_core/` or `ilc_consensus/`.

CDL-039 governs how validators communicate (transport envelope, opaque channel, cluster-membership-non-inferrable). CDL-068 governs which validators are assigned to communicate with each other (topology, diversity, randomness). These are complementary and non-overlapping. A future reader of CDL-039 seeking topology shuffle authorization is in error - the correct reference is CDL-068.

CDL-017 remains the validator-admission lane. It decides:

- admission identity linkage,
- stake-floor evidence gate,
- threshold-gated eligibility posture,
- validation-pool exclusion from core validator law.

CDL-068 begins only after that admission surface exists. It is therefore
separated from transport contract law and from validator-admission law.

## 4. Evidence checklist

The following evidence checklist must be satisfied before CDL-068 can be
ratified:

1. SIM-TOPOLOGY-01 full results:
   complete in Phase 735.
   `sim_topology_01_results_complete`
   `sim_topology_01_verdict=pass`
   The opening cites `recommended_k_degree 4`, cadence `1`, fanout `3`,
   `distinct_cluster_floor_recommendation 4`, and
   `max_cluster_share_ceiling_recommendation 33`.

2. SIM-VALIDATOR-01 VRF threshold:
   complete in Phase 734.
   `sim_validator_01_results_complete`
   `sim_validator_01_verdict=pass`
   `vrf_upgrade_threshold_validator_count 10`

3. CDL-017 prelock evidence artifact:
   not complete yet at Phase 736.
   Phase 737 must update `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
   so CDL-068 opening has a direct prelock citation path.

4. CDL-039 boundary satisfaction:
   opening-side boundary satisfied.
   No transport-scope overlap is introduced here, and no CDL-039 mutation is
   required for CDL-068 opening.

Because the Phase 735 result is a full pass, the SIM-TOPOLOGY-01 checklist item
is complete at opening time rather than marked partial or deferred.

## 5. Prelock criteria

The candidate prelock criteria opened here are:

1. topology shuffle remains a separate constitutional lane from both CDL-039
   and CDL-017,
2. epoch-hash v1 remains acceptable for production v1 only with an explicit
   forward obligation to adopt VRF at `10` active validators,
3. any production-facing topology authorization must stay within the Phase 735
   bounded path: `k=4`, per-epoch cadence, bounded push fanout `3`,
4. validator composition must use the explicit `validator_cluster_id` metric
   rather than an implied diversity notion,
5. the Q6 numeric floor and ceiling must remain tied to the Phase 735 evidence:
   `distinct_cluster_floor >= 4` and `max_cluster_share_ceiling <= 33%`,
6. CDL-068 cannot be ratified until the Phase 737 CDL-017 prelock evidence
   artifact update is in place.

These are prelock criteria only. They are not ratification text yet.

## 6. Non-goals

This opening does not do any of the following:

- ratify CDL-068,
- ratify CDL-017,
- amend CDL-039,
- authorize validation pools or delegation,
- authorize a final production VRF design beyond the upgrade obligation,
- disclose global validator adjacency,
- mutate `ilc_core/` or `ilc_consensus/`,
- claim that Window 733-738 completed final convergence.

`cdl_068_not_ratified_in_window_733_738`

CDL-068 opens the lane only. Ratification belongs in Window 739 or the later
convergence window after the remaining prelock evidence assembly is complete.
