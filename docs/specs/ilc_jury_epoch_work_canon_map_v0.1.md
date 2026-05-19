# ILC Jury / Epoch Work Canon Map v0.1

**Phase:** 1391 / J-001
**Date:** 2026-05-19
**Status:** complete
**Scope:** planning and canon map only

## Required Tokens

```text
jury_epoch_work_canon_map_phase_j001
jury_participation_incentivized_not_obligatory_recorded
objective_subjective_panel_split_confirmed
```

## 1. Purpose

This document maps the current canon for ILC juries, panels, beginning-of-epoch
capability work, maintenance tasks, and incentive surfaces. It exists to prevent
context drift before the later J-series phases define eligibility, assignment,
economics, runtime quotes, shadow harnesses, and activation gates.

The governing principle recorded here is:

```text
jury participation is incentivized and opt-in; it is not obligatory for every
connected agent
```

No runtime behavior changes in this phase.

## 2. Claim Verification Table

| Claim | Source checked | Result |
|-------|----------------|--------|
| 7+1 panel is architecture / case-evaluation infrastructure | `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`; `docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md` | confirmed |
| Aesthetic panel is non-blocking and not objective truth | `docs/specs/ilc_cdl_059_aesthetic_panel_governance_ratification_evidence_531_v0.1.md`; `ilc_core/epistemic/aesthetic_panel_runtime.py` | confirmed |
| CDL-068 topology shuffle is epoch-scoped and default-off in runtime | `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`; `ilc_core/validator/topology_shuffle_runtime.py` | confirmed |
| CapProof / AWP / QATPS are planned or staged, not fully active settlement | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`; `docs/specs/ilc_capability_proof_activation_readiness_contract_231_v0.1.md`; `docs/specs/ilc_capability_proof_activation_readiness_gates_v0.1.md` | confirmed |
| General jury compensation is not fully implemented | `docs/research/ilc_jury_deliberation_research_memo_791_v0.1.md`; `docs/research/ilc_inverted_ecu_model_precanon_v0.1.md`; `ilc_core/epoch/validator_reward_pool_routing_runtime.py`; `ilc_core/economics/epoch_attribution_settle_runtime.py` | confirmed |
| Reduced 3+1 jury tier is ratified canon | committed repo and historical-chat search | not confirmed |
| 5+1 jury tier is ratified canon | committed repo and historical-chat search | not found |
| 5+2 jury tier is ratified canon | committed repo and historical-chat search | not found as jury pattern |

## 3. Source Classification

| Source | Classification | Canon Takeaway |
|--------|----------------|----------------|
| `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md` | architecture canon | Defines the 7+1 evaluation panel, `panel_size=8`, `independence_k=3`, `outsider_seat=true`, `k=5 of m=7` reviewer quorum, and L-tier quorum ladder. |
| `docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md` | phase evidence / integration boundary | Confirms seven canonical submission artifacts plus one outsider review artifact; outsider is review-only, not a passive reward recipient. |
| `docs/specs/ilc_cdl_052_epistemic_node_submission_runtime_handoff_477_v0.1.md` | ratified runtime handoff | Establishes epistemic node submission envelope and mode-routing runtime; Mode 3 auditor-review execution remains out of scope there. |
| `ilc_core/epistemic/node_submission_runtime.py` | implemented runtime surface | Implements envelope validation and deterministic mode routing, including `mode_3_boundary_detected`, but not a full jury execution engine. |
| `docs/specs/ilc_cdl_059_aesthetic_panel_governance_ratification_evidence_531_v0.1.md` | ratified governance evidence | Ratifies a narrow aesthetic panel lane as transparent, bounded, informational-only, and orthogonal to objective truth governance. |
| `ilc_core/epistemic/aesthetic_panel_runtime.py` | implemented default-off / non-blocking runtime | Confirms `BLOCKING_AUTHORITY_ACTIVE = False` and labels aesthetic outputs as not objective truth. |
| `docs/research/ilc_jury_deliberation_research_memo_791_v0.1.md` | research memo | Proposes jury petition / acknowledgment / verdict node types and sealed deliberation envelopes, but explicitly notes missing schema and economics pieces. |
| `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md` | ratified topology governance | Ratifies epoch-scoped validator topology shuffle constraints and a VRF upgrade boundary at 10 active validators. This is validator assignment infrastructure, not a general jury runtime. |
| `ilc_core/validator/topology_shuffle_runtime.py` | implemented default-off runtime | Builds deterministic topology quotes for sub-threshold validator sets; fails closed at the VRF threshold; does not activate production topology shuffle. |
| `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` | non-normative planning | Describes CapProof, AWP / IIH, QATPS / CIT, and maintenance work. It says maintenance work should be economically attractive, not mandatory. |
| `docs/specs/epoch_init_control_loop_v0.1.md` | draft | Sketches beginning-of-epoch control-loop timing and benchmark use; not an activation artifact. |
| `docs/specs/ilc_capability_proof_activation_readiness_contract_231_v0.1.md` | readiness contract | Records CapProof readiness gates and the no-direct-ILC-reward invariant. |
| `docs/specs/ilc_capability_proof_activation_readiness_gates_v0.1.md` | planning gate doc | Stages CapProof, AWP / IIH, and QATPS / CIT into separate readiness gates. |
| `ilc_core/mining/benchmark.py` | implementation scaffolding | Contains benchmark / proof-of-potential machinery, but not full economic activation. |
| `docs/research/ilc_inverted_ecu_model_precanon_v0.1.md` | precanon research | Discusses panel verification as spend-validity gate and panel compensation risks; not ratified jury economics. |
| `ilc_core/genesis/work_task.py` | implemented task model | Defines task classes such as star-map embedding, contradiction sweep, graph compression, and stability simulation. |
| `ilc_core/work/task_queue.py` | sandbox queue helper | In-memory MVP queue only; not a durable distributed scheduler. |
| `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md` | ratified narrow economics rule | Defines H-CON-02 panel quorum and REFUTATION attribution for ejected stake distribution; not a general jury-payment system. |
| `ilc_core/economics/epoch_attribution_settle_runtime.py` | implemented default-off economics runtime | Quotes ejected-stake distribution and REFUTATION attribution under CDL-083; production distribution remains not activated. |
| `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md` | ratified validator economics | Routes validator reward pool through CDL-047 treasury framework. |
| `ilc_core/epoch/validator_reward_pool_routing_runtime.py` | implemented default-off economics runtime | Provides validator reward pool quote logic; production validator reward distribution remains not activated. |

## 4. Canon Classification

### 4.1 Objective Evaluation Panels

The objective / Popperian jury line is anchored by ADM-003 and CDL-052. The
canonical panel shape is the 7+1 evaluation panel:

```text
panel_size=8
regular_reviewers=7
outsider_seat=true
reviewer_quorum=k=5 of m=7
independence_k=3
```

This panel is for knowledge-claim evaluation, task-output evaluation,
decomposition validity, and ILC attribution surfaces. It is not a validator BFT
quorum. Stated as a stable search phrase: not a validator BFT quorum. It is not
a constitutional authority above Genesis / protocol ratification.

### 4.2 Quorum Ladder

ADM-003 records the L-tier quorum ladder:

```text
L0 = 3
L1 = 5
L2 = 7
L3 = 9
appeals escalate by +2
```

The L-tiers are graph epistemic tiers. They are not agent reputation levels, not
validator BFT thresholds, and not a replacement for formal CDL ratification.

### 4.3 Reduced 3+1 / 5+1 / 5+2 Status

The committed canon supports 7+1 and the L-tier ladder. A reduced 3+1 cold-start
panel appears as a plausible later policy for low-stakes structural work, but it
is not ratified in the committed canon reviewed for this phase.

`5+1` was not found as a ratified jury tier.

`5+2` was not found as a ratified jury pattern. Historical advisory material
suggests this is likely a notation collision between `k=5` quorum and `+2`
appeal escalation.

### 4.4 Subjective / Aesthetic Panels

CDL-059 is the subjective / aesthetic lane. It is explicitly separate from
objective truth governance:

```text
layer_2_informational_only
cdl_v7_7_plus_1_panel_orthogonal
cdl_052_layer_3_orthogonal
```

The aesthetic panel may provide a transparent expressive-content quality signal.
It is non-blocking and must not be treated as objective truth.

### 4.5 Jury Deliberation and Petition Nodes

Phase 791 research proposes jury-specific node types and sealed deliberation
envelopes. Those ideas are not yet implemented as schema or runtime canon.

Open pieces:

```text
jury_petition node type
jury_acknowledgment node type
jury_verdict node type
sealed deliberation envelope
jury-specific bond / fee distribution CDL
```

### 4.6 Beginning-of-Epoch Work

Beginning-of-epoch work exists as planning and partial scaffolding, not full
settlement activation.

Canon-supported categories:

```text
CapProof capability probes
AWP / IIH heavier proof pipeline
QATPS / CIT quality-adjusted throughput research
star.map.embedding
contradiction.sweep
graph.compression
stability.simulation
```

The current policy boundary is that these tasks should be economically
attractive and useful, not mandatory. Capability results may inform routing,
queue placement, or price adjustments in later phases, but current docs preserve
the no-direct-ILC-reward invariant for CapProof.

### 4.7 Incentives and Rewards

The repository contains several adjacent economics lanes:

```text
CDL-054 validator reward-pool routing
CDL-083 ejected-stake treasury distribution and REFUTATION attribution
precanon panel verification compensation research
CapProof / AWP / QATPS readiness gates
```

None of these currently ratifies a general reviewer-payment system for all jury
work. Jury economics remain a separate J-series design obligation.

## 5. Non-Claims

This phase records the following non-claims:

```text
no mandatory jury service for every connected agent
no general production jury assignment runtime
no general reviewer-payment activation
no public graph canonicalization activation
no production ingestion activation
no production topology shuffle activation
no production validator reward distribution activation
no ejected-stake distribution activation
no CDL mutation
no runtime mutation
```

## 6. Future Phase Routing

| Future phase | Required decision |
|--------------|-------------------|
| J-002 / Phase 1392 | Jury eligibility, opt-in, assignment, and anti-capture ADR. |
| J-003 / Phase 1393 | Public node onboarding taxonomy and objective / subjective / structural review tiers. |
| J-004 / Phase 1394 | Jury and maintenance-task incentive economics without obligatory service. |
| J-005 / Phase 1395 | Beginning-of-epoch capability and maintenance-work contract. |
| J-006 / Phase 1396 | Default-off jury assignment and maintenance quote runtime. |
| J-007 / Phase 1397 | Shadow harness for jury / maintenance flow. |
| J-008 / Phase 1398 | Activation gate and public-RC boundary disposition. |

## 7. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md -> jury_epoch_work_canon
```

This artifact is load-bearing for future J-series planning. It does not mutate
signed Genesis artifacts or regenerate Atlas artifacts.

## 8. Final Disposition

Phase 1391 / J-001 completes the canon map only. It confirms the split between
objective evaluation panels and subjective / aesthetic panels, records that jury
participation is incentivized rather than obligatory, and routes unresolved
eligibility, assignment, incentive, and activation decisions to later J-series
phases.

No runtime, CDL, public ingestion, production jury, production maintenance-task,
production reward, or reviewer-payment activation occurred.
