# ILC Epoch-Start Capability and Maintenance Work Contract v0.1

**Phase:** 1395 / J-005
**Date:** 2026-05-19
**Status:** complete
**Scope:** planning and contract artifact only

## Required Tokens

```text
epoch_start_capability_maintenance_contract_phase_j005
capproof_no_direct_ilc_reward_boundary_confirmed
maintenance_tasks_reward_eligible_after_review_lane
awp_iih_depends_on_capproof_infrastructure_confirmed
qatps_cit_post_genesis_supplement_confirmed
task_queue_sandbox_non_durable_confirmed
```

## 1. Purpose

This document converts the CapProof / AWP / QATPS / maintenance-task design memory
into a staged, binding contract for the J-series. It does not ratify new CDLs,
mutate runtime code, activate production economics, or require any agent to perform
epoch-start work before activation gates are passed.

The three-layer architecture from `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
is confirmed as the organizing principle:

| Layer | Mechanism | Phase | Function |
|-------|-----------|-------|----------|
| L0 — hardware readiness | CapProof (5 probes, signed CV) | Per-epoch start | ECU pricing ±15%, scheduling, quorum formation |
| L1 — throughput/quality | QATPS/CIT | Continuous within epoch | Main reward pool share |
| L2 — maintenance | Civic / maintenance tasks | Continuous | System upkeep + lottery pool |

## 2. Claim Verification Table

| Claim | File checked | Result |
|-------|-------------|--------|
| CapProof is DESIGNED, not ratified or implemented | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` §3.1, §6 disposition table | confirmed — marked [DESIGNED]; post-Genesis L2 disposition |
| CapProof never mints extra ILC — affects ECU pricing ±15% only | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` §6.1 | confirmed — settled design decision |
| AWP/IIH is DESIGNED, depends on CapProof infrastructure | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` §3.2, §6 disposition table | confirmed — marked [DESIGNED]; post-Genesis L2 |
| QATPS/CIT is DESIGNED; ECU scoring partially present; throughput dimension not measured | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` §3.3, §6 disposition table | confirmed — marked [DESIGNED]; supplement in Genesis docs |
| Maintenance tasks are partially present; task infrastructure exists | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` §6 disposition table | confirmed |
| `EpistemicWorkTask` task_class enum exists with star.map.embedding, contradiction.sweep, graph.compression, stability.simulation, custom | `ilc_core/genesis/work_task.py` | confirmed |
| `EpistemicWorkTask.task_state` includes "rewarded" as a valid terminal state | `ilc_core/genesis/work_task.py` | confirmed |
| `ilc_core/work/task_queue.py` is sandbox/simulation only — not a durable protocol queue | `ilc_core/work/task_queue.py` docstring and import structure | confirmed — economics sandbox; not production queue |
| `epoch_init_control_loop_v0.1.md` is DRAFT, not ratified | `docs/specs/epoch_init_control_loop_v0.1.md` status header | confirmed — DRAFT |
| `EpistemicWorkTask.difficulty_factor` is `Optional[float]` — note: not a reward value; float is not banned for this field | `ilc_core/genesis/work_task.py` line 16 | confirmed — difficulty_factor is a routing/scheduling input, not an ECU or reward value; CODING-SECURITY-STANDARD §3 float ban applies to ECU/balance/reward values only; `ecu_estimate` is already `Decimal` |

## 3. Decision 1 — CapProof Boundary

### Rule

CapProof is a **readiness, routing, and ECU pricing signal**. It is not a direct
ILC reward path.

```text
capproof_no_direct_ilc_reward_boundary_confirmed
```

The five standardized probes (GEMMProbe, InferProbe, GraphProbe, BandwidthProbe,
DeterminismProbe) produce a signed Capability Vector (CV). The CV adjusts ECU
pricing and queue placement within a **±15% band only**. It never directly affects
ILC reward allocation.

Rationale from the historical corpus (November 2025): "We don't reward speed or
watts directly; we reward correctness, reuse, and verified contribution. Hardware
telemetry is used to price ECUs and schedule fairly, not to mint extra ILC."

Implementation prerequisites before CapProof can be deployed:
- runtime infrastructure for deterministic probe execution (not in current Genesis codebase)
- content-addressed probe binary supply chain
- per-epoch slight shape variation drawn from a public distribution
- VRF-based spot-recheck mechanism

CapProof remains post-Genesis (L2). Genesis defines the initial baseline
(score = 1.0) at epoch 0 as a bootstrap anchor only. After the Genesis accrual
taper (nominally around epoch 24), the baseline must transition to a rolling median
or protocol-defined synthetic reference via a ratified CDL. The permanent-Genesis-
baseline posture conflicts with the no-perpetual-privilege principle.

## 4. Decision 2 — AWP/IIH Dependency

### Rule

AWP/IIH (Anchored Work Proofs / Intelligent Inference Hash) is the heavyweight
counterpart to CapProof. It depends on CapProof infrastructure.

```text
awp_iih_depends_on_capproof_infrastructure_confirmed
```

AWP cannot be deployed before CapProof infrastructure exists. The proposed split
(λ = 0.80 QATPS/CIT, 0.20 AWP challenge pool) is not simulation-validated.
If AWP is implemented, the split must be validated against the Phase 1118-1123
simulation framework before any production reward allocation claim.

AWP remains post-Genesis. No production reward activation is authorized by this
contract.

## 5. Decision 3 — QATPS/CIT Status

### Rule

QATPS/CIT (Quality-Adjusted Token Rate / Continuous Intelligence Test) is
partially present via the existing ECU scoring kernel. The throughput and latency
dimensions are not yet measured.

```text
qatps_cit_post_genesis_supplement_confirmed
```

The current ECU scoring (`ilc_core/` economic surfaces) measures quality of
finalized work. The QATPS vision adds throughput and latency dimensions when the
corresponding runtime layer exists. These are additive, not conflicting.

No QATPS-specific reward distribution or throughput measurement is activated by
this contract.

## 6. Decision 4 — Maintenance Task Reward Eligibility

### Rule

Maintenance tasks become reward-eligible only after passing a reviewed task outcome
via the applicable review lane.

```text
maintenance_tasks_reward_eligible_after_review_lane
```

The existing `EpistemicWorkTask` schema in `ilc_core/genesis/work_task.py` provides
the task class foundation. The recognized maintenance task classes are:

| Task class | Description | Review lane (J-003 taxonomy) |
|-----------|-------------|------------------------------|
| `star.map.embedding` | Generate or update star-map embeddings | T2 (reward-bearing objective) or T1 (metadata) depending on scope |
| `contradiction.sweep` | Identify and flag logical inconsistencies in the graph | T2 or T5 (refutation/provenance) depending on finding |
| `graph.compression` | Prune, deduplicate, or compress redundant graph structure | T1 (structural metadata) |
| `stability.simulation` | Run stability/SIM analyses for economic or graph parameters | T1 or T2 depending on whether result is reward-bearing |
| `custom` | Operator-defined maintenance task | Review lane assigned at task definition time |

The task lifecycle (`proposed` → `claimed` → `completed` → `audited` → `rewarded`
or `expired`) in `EpistemicWorkTask.task_state` models the intended path. The
`rewarded` terminal state is architecturally present but not yet wired to a live
economic path.

The `ilc_core/work/task_queue.py` `TaskQueue` is a sandbox/simulation primitive
only — it is not a durable production queue.

```text
task_queue_sandbox_non_durable_confirmed
```

A durable production maintenance task queue is a post-J-005 implementation
obligation. It must:
- be content-addressed (task_id derivable from canonical task descriptor hash)
- enforce `Decimal`-only ECU estimates (already satisfied in `EpistemicWorkTask`)
- not accept `difficulty_factor` as an ECU or reward input (it is a
  routing/scheduling signal only)
- be gated behind the applicable review lane before emitting `task_state=rewarded`

The lottery pool connection (low-capability agents participate through maintenance
and lottery/pool lanes, earning ECU through system upkeep regardless of full review
lane eligibility) is noted from the historical corpus as architecturally intended.
It is not ratified as a CDL and must route through J-008 production activation gate
before any live ECU distribution from a maintenance lottery pool.

## 7. Decision 5 — Activation Ladder

### Rule

Epoch-start capability work and maintenance task economics follow a staged
activation ladder. No layer may claim the next stage without passing its gate.

| Stage | Activation criteria | Authorized by |
|-------|--------------------|----|
| Shadow / spec-only | Spec complete; no runtime required | This document |
| Bounded testnet | CapProof runtime implemented; probes content-addressed; CV signing wired; deterministic probe variation implemented | Future CDL + explicit GO |
| Public RC shadow | Shadow harness validates maintenance task lifecycle end-to-end; no live ECU distribution; J-007 harness passes | J-007 / Phase 1397 |
| Production candidate | J-008 production activation gate passes; VRF or approved randomness for CapProof spot-recheck confirmed; maintenance lottery pool CDL ratified; review lane wiring complete | J-008 / Phase 1398 |

```text
activation_ladder_shadow_to_production_defined_phase_j005
```

The `epoch_init_control_loop_v0.1.md` draft describes the benchmark run, trust
vector update, routing parameter refresh, and epoch_config emission sequence. It
is DRAFT and non-normative. It is not activated by this contract.

## 8. Non-Authorizations

This phase authorizes no runtime mutation, no CDL mutation, no CDL opening, no
production CapProof deployment, no AWP challenge pool activation, no QATPS
throughput measurement activation, no maintenance lottery pool activation, no
reviewer payment activation, no public economics activation, no live ECU
distribution from any maintenance or capability lane, no production jury activation,
no public graph admission activation, no public RC claim, no source publication,
no release signing, no wallet/ECU/ILC value-path activation, no Genesis
intervention execution, and no legal conclusion.

## 9. Future Phase Routing

| Future phase | Relationship |
|--------------|--------------|
| J-006 / Phase 1396 | Default-off jury assignment quote runtime; consumes J-003 taxonomy and ADR-0040 |
| J-007 / Phase 1397 | Shadow public-ingestion harness; ADR-0041 (J-003a) hard prerequisite; exercises T0.5 quarantine and maintenance task lifecycle without production activation |
| J-008 / Phase 1398 | Production jury activation gate; must resolve: CapProof CDL, maintenance lottery pool CDL, VRF production assignment, anti-capture diversity checks |
| CapProof CDL (TBD) | New CDL for CapProof deployment; must include: probe content-addressing, CV signing contract, ±15% band enforcement, Genesis baseline transition rule |

## 10. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md -> jury_epoch_work_canon
```
