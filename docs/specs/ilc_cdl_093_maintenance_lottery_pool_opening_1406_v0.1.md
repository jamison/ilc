# ILC CDL-093 Maintenance Lottery Pool Opening 1406 v0.1

Phase: 1406
Date: 2026-05-20
Status: opened; not ratified; no distribution activation

Required tokens:

```text
cdl_093_maintenance_lottery_pool_opened_phase_1406
cdl_093_not_ratified_phase_1406
cdl_093_deliberation_questions_recorded_phase_1406
```

## 1. Opening Scope

CDL-093 opens the maintenance lottery pool distribution lane. The lane governs
how low-capability agents may become eligible to earn ECU through reviewed
maintenance tasks and a lottery/pool draw, regardless of full review-lane
eligibility.

The J-008 production jury activation gate routes this work as a blocking
condition:

```text
MAINTENANCE_LOTTERY_CDL_RATIFIED
maintenance_lottery_cdl_not_opened_phase_j008
```

The gate routing requires a dedicated CDL defining five scope items:

| Scope item | Phase 1406 status |
|------------|-------------------|
| Pool budget source | opened for deliberation; not resolved |
| Task eligibility | opened for deliberation; not resolved |
| Lottery mechanics | opened for deliberation; not resolved |
| ECU distribution path | opened for deliberation; not resolved |
| Anti-gaming controls | opened for deliberation; not resolved |

CDL-093 is not ratified after Phase 1406.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-091 is ratified before Phase 1406 | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-091` | confirmed |
| CDL-092 is open before Phase 1406 | Phase 1406 prompt claim checked against CDL register | not confirmed; superseded by Phase 1405, CDL-092 is ratified |
| CDL-092 is ratified before Phase 1406 | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-092` | confirmed |
| CDL-093 is absent before Phase 1406 C2 | current CDL register before C2 and historical `608096a3` register | confirmed |
| J-008 condition `MAINTENANCE_LOTTERY_CDL_RATIFIED` is `NOT_MET` | `ilc_core/epistemic/jury_activation_gate.py` | confirmed |
| `maintenance_lottery_cdl_not_opened_phase_j008` is the J-008 NOT_MET token | `ilc_core/epistemic/jury_activation_gate.py` | confirmed |
| No maintenance lottery runtime exists yet | filesystem search for `maintenance_lottery_runtime.py` and `*lottery*` under `ilc_core/` | confirmed |
| MemPalace advisory recall found relevant J-005 maintenance context | tier A query plus direct repo reads | confirmed |

## 3. Inherited Canon

Phase 1395 / J-005 records the maintenance-task foundation:

```text
epoch_start_capability_maintenance_contract_phase_j005
maintenance_tasks_reward_eligible_after_review_lane
task_queue_sandbox_non_durable_confirmed
capproof_no_direct_ilc_reward_boundary_confirmed
activation_ladder_shadow_to_production_defined_phase_j005
```

Inherited rules:

| Rule | Source |
|------|--------|
| Maintenance tasks become reward-eligible only after passing the applicable review lane | J-005 section 6 |
| `EpistemicWorkTask.task_state=rewarded` is architecturally present but not wired to a live economic path | J-005 section 6 |
| `ilc_core/work/task_queue.py` is sandbox/simulation only, not a durable production queue | J-005 section 6 |
| Low-capability agents may participate through maintenance and lottery/pool lanes, but the lottery pool is not ratified before CDL-093 | J-005 section 6 |
| Production requires the J-008 production activation gate to pass | J-005 section 7 |

Recognized maintenance task classes from J-005:

| Task class | Description |
|------------|-------------|
| `star.map.embedding` | Generate or update star-map embeddings |
| `contradiction.sweep` | Identify and flag logical inconsistencies in the graph |
| `graph.compression` | Prune, deduplicate, or compress redundant graph structure |
| `stability.simulation` | Run stability or SIM analyses for economic or graph parameters |
| `custom` | Operator-defined maintenance task with review lane assigned at task definition time |

## 4. J-008 Gate Dependency

J-008 condition:

```text
MAINTENANCE_LOTTERY_CDL_RATIFIED
```

Current J-008 status before Phase 1406:

```text
NOT_MET
```

J-008 routing:

```text
Open a maintenance lottery pool CDL defining: pool budget source,
task eligibility, lottery mechanics, ECU distribution path, and
anti-gaming controls; ratify before live ECU distribution from
maintenance lane.
```

Phase 1406 opens the CDL. It does not satisfy `MAINTENANCE_LOTTERY_CDL_RATIFIED`
because ratification is routed to Phase 1408.

## 5. Deliberation Questions

```text
cdl_093_deliberation_questions_recorded_phase_1406
```

### Q1 — Lottery draw mechanism

Should the maintenance lottery use a VRF or later-ratified randomness source, or
may it use an epoch-hash pseudorandom draw for this lower-value lane?

ADR-0040 allows deterministic epoch-hash assignment for pre-production, testnet,
public-RC shadow, and non-value-bearing harness lanes. It requires VRF or a
later-ratified randomness source for production high-value review lanes, private
assignment, value-bearing public canonicalization, or claims of strategic
unpredictability.

Phase 1407 must resolve whether CDL-093 is allowed to use epoch-hash for a
bounded maintenance lottery lane or whether it waits for the VRF verifier track.

### Q2 — Pool budget source and funding fraction

What source funds the maintenance lottery pool, and what fraction or cap applies?

Candidate source families for Phase 1407 deliberation:

| Candidate | Open issue |
|-----------|------------|
| Fixed pooled maintenance budget | Requires defining a Decimal-only per-epoch cap |
| Treasury allocation under CDL-047-style governance | Requires preserving existing treasury activation boundaries |
| Petition-bond or task-sponsor funding | Requires anti-spam and failed-task handling |

### Q3 — Task eligibility criteria and anti-gaming controls

Which maintenance task categories qualify for lottery pool entry, and what
minimum audited contribution threshold is required?

Phase 1407 must specify at least:

| Control | Open issue |
|---------|------------|
| Required task state | Whether `audited` is sufficient or only review-lane-passed tasks qualify |
| Contribution threshold | Minimum accepted maintenance output before lottery entry |
| Per-agent cap | Maximum entries per epoch or task class |
| Duplicate-work guard | How repeated or low-novelty maintenance claims are filtered |
| Same-operator guard | Whether same-operator entries are capped or down-weighted |

### Q4 — ECU distribution path and settlement boundary

How are winning lottery pool ECU credits routed, and what settlement boundary
prevents Phase 1406 or Phase 1407 from becoming a live distribution?

Phase 1407 must define whether winning credits route through treasury-governance
quotes, reviewer-payment stubs, a dedicated CDL-093 runtime stub, or another
explicitly ratified path. Live settlement remains disallowed until later runtime
and gate authority.

### Q5 — Production gate and activation split

Which later phase flips the J-008 `MAINTENANCE_LOTTERY_CDL_RATIFIED` condition,
and what additional production GO is required before live ECU distribution?

Phase 1406 answer: opening does not flip the J-008 condition. Ratification is
Phase 1408, runtime stub is Phase 1409, and the production gate re-run is routed
to Phase 1427 after Phase 1425 verification.

## 6. Non-Authorizations

Phase 1406 does not:

- ratify CDL-093;
- activate maintenance lottery distribution;
- execute live lottery draws;
- settle ECU;
- mint ILC;
- modify wallets;
- mutate `ilc_core/`;
- create `ilc_core/epistemic/maintenance_lottery_runtime.py`;
- change the J-008 gate verdict;
- activate production jury behavior;
- publish public RC artifacts.

## 7. Historical Hardening

Historical hardening command:

```bash
git show 608096a3:docs/specs/ilc_constitutional_decision_log_v0.1.md | rg -n "^\\| CDL-093 \\|"
```

Result: no CDL-093 row exists at the Phase 1404 prelock commit.

## 8. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_093_maintenance_lottery_pool_opening_1406_v0.1.md -> constitutional/cdl
```
