# ILC CDL-068 Topology Shuffle Authorization Ratification Evidence 743 v0.1

Status: ratification evidence artifact
Date: 2026-04-20
Decision vehicle: CDL-068
Phase: 743
Owner lane: G8 MVP-gate runtime-form and topology-shuffle ratification lane
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`cdl_068_ratification_evidence_complete`
`cdl_068_ratified_topology_shuffle_authorization_lane`
`cdl_068_topology_parameters_ratified_as_floors_and_ceilings`
`cdl_068_vrf_upgrade_threshold_fixed_at_10_active_validators`
`cdl_068_commit_1_does_not_mutate_decision_log`
`cdl_068_commit_2_mutates_only_cdl_068_row`
`cdl_017_remains_open_after_cdl_068_ratification`

## 1. Phase 742 dossier verdict re-read

This ratification phase re-reads the explicit verdict from
`docs/specs/ilc_cdl_068_ratification_readiness_dossier_742_v0.1.md`
Section `5` verbatim:

> all checklist items satisfied - `CDL-068` is ready for ratification in
> Phase `743`

Verbatim verdict string:
all checklist items satisfied - `CDL-068` is ready for ratification in
Phase `743`

That dossier already checked:

- all four opening-checklist items from Phase `736`,
- all six Phase `736` prelock criteria individually,
- the non-ratification boundary for Phase `742`.

Phase `743` therefore does not reopen checklist satisfaction. It consumes the
Phase `742` dossier as the explicit ratification-readiness authority.

## 2. Ratified constitutional decision

The constitutional lane opened in Phase `736` is now ratified.

`CDL-068` is ratified as the narrow constitutional lane governing:

- topology-shuffle authorization for validator assignment,
- validator diversity constraints for committee composition,
- the randomness-source boundary for the topology-shuffle surface.

This ratification remains narrow:

- it ratifies topology-assignment law rather than transport-envelope law,
- it ratifies a bounded authorization surface rather than a generalized
  validator-committee redesign,
- it does not ratify `CDL-017`,
- it does not amend `CDL-039`,
- it does not authorize sovereign substrate selection or wallet widening.

## 3. Ratified topology floors, ceilings, cadence, and VRF threshold

The ratified constitutional parameters are:

- `shuffle_cadence_epochs = 1`
- `k_degree_floor >= 4`
- `push_fanout_ceiling <= 3`
- `distinct_cluster_floor >= 4`
- `max_cluster_share_ceiling <= 33%`
- `vrf_upgrade_threshold_validator_count = 10`

Constitutional reading:

- the topology surface is ratified through floors and ceilings rather than as a
  claim that one exact runtime graph is the only lawful configuration,
- `k_degree_floor >= 4` means the ratified lane may not authorize a weaker
  graph than the Phase `735` evidence floor,
- `push_fanout_ceiling <= 3` means the ratified lane may not authorize a
  larger bounded-push budget than the evidence-supported ceiling without later
  constitutional change,
- `distinct_cluster_floor >= 4` and
  `max_cluster_share_ceiling <= 33%` ratify the diversity metric as an
  evidence-derived floor/ceiling pair rather than as a conversational target,
- `vrf_upgrade_threshold_validator_count = 10` is a hard threshold, not a
  range and not an indefinite future question.

This ratification does not constitutionalize a single fixed runtime adjacency
map. It constitutionalizes the minimum and maximum admissible topology
authorization bounds named above.

## 4. Phase 736 prelock criteria re-read as satisfied

### 4.1 Criterion 1 satisfied

Criterion:

> `topology shuffle remains a separate constitutional lane from both CDL-039 and CDL-017`

Dossier citation:

- Phase `742` dossier Section `4.1`

Status: satisfied.

### 4.2 Criterion 2 satisfied

Criterion:

> `epoch-hash v1 remains acceptable for production v1 only with an explicit forward obligation to adopt VRF at 10 active validators`

Dossier citation:

- Phase `742` dossier Section `4.2`

Status: satisfied.

### 4.3 Criterion 3 satisfied

Criterion:

> `any production-facing topology authorization must stay within the Phase 735 bounded path: k=4, per-epoch cadence, bounded push fanout 3`

Dossier citation:

- Phase `742` dossier Section `4.3`

Status: satisfied.

### 4.4 Criterion 4 satisfied

Criterion:

> `validator composition must use the explicit validator_cluster_id metric rather than an implied diversity notion`

Dossier citation:

- Phase `742` dossier Section `4.4`

Status: satisfied.

### 4.5 Criterion 5 satisfied

Criterion:

> `the Q6 numeric floor and ceiling must remain tied to the Phase 735 evidence: distinct_cluster_floor >= 4 and max_cluster_share_ceiling <= 33%`

Dossier citation:

- Phase `742` dossier Section `4.5`

Status: satisfied.

### 4.6 Criterion 6 satisfied

Criterion:

> `CDL-068 cannot be ratified until the Phase 737 CDL-017 prelock evidence artifact update is in place`

Dossier citation:

- Phase `742` dossier Section `4.6`

Status: satisfied.

The prelock criteria therefore remain satisfied at ratification time.

## 5. Two-commit mutation discipline and decision-log consequence

This phase uses a two-commit constitutional mutation pattern.

Commit `1`:

- publishes this ratification artifact,
- re-states the satisfied checklist and prelock burden using the Phase `742`
  dossier,
- publishes the phase test and `STATUS.md` backfill,
- does not mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

Commit `2`:

- mutates exactly the `CDL-068` row in
  `docs/specs/ilc_constitutional_decision_log_v0.1.md`,
- changes `status: open` to `status: ratified`,
- appends `ratified_phase: 743`,
- appends `ratified_date: 2026-04-20`,
- appends
  `evidence_document: docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`.

No other decision-log row may change in commit `2`.

## 6. Preserved exclusions and non-goals

This ratification does not do any of the following:

- ratify `CDL-017`,
- amend `CDL-039`,
- authorize validation pools or delegation,
- freeze every runtime implementation detail of topology shuffling,
- authorize a weaker graph than the evidence floor,
- authorize a larger bounded push budget than the evidence ceiling,
- mutate `ilc_core/` or `ilc_consensus/`,
- claim row `5`, row `7`, or row `8` runtime closure,
- select sovereign substrate or graduate Option B.

`CDL-017` remains open after this phase.
