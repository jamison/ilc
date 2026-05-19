# ILC Jury and Epoch-Work Canonicalization Phase Plan v0.1

**Date:** 2026-05-19
**Status:** planning-only; Phase J-001 / 1391 and Phase J-002 / 1392 complete
**Scope:** jury/panel selection, subjective/objective review lanes, beginning-of-epoch capability work, maintenance tasks, and incentive routing

## 1. Purpose

This document consolidates the recovered jury / panel / epoch-work design into a
concrete future phase plan. It does not ratify new constitutional rules, mutate
runtime code, activate public RC, activate production economics, or require jury
participation from every connected agent. Phase J-001 / 1391 has now executed as
a non-sensitive canon-map phase; the rest of the J-series remains future work
unless separately authorized. Phase J-002 / 1392 now complete; it publishes
`docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` and locks the opt-in,
eligibility, deterministic shadow-assignment, VRF boundary, diversity,
outsider-seat, and non-response rules for later J-series phases.

The core principle is:

```text
jury_participation_is_incentivized_not_obligatory
```

Agents may connect, observe, draft, and perform private work without being forced
into jury service. However, reputation weight, public graph canonicalization,
reward eligibility, validator eligibility, and high-trust routing may require an
agent to opt into randomized review, audit, maintenance, or epoch-readiness duties.

## 2. Recovered Context

| Lane | Current status | Principal sources |
|------|----------------|-------------------|
| 7+1 objective knowledge panel | Architectural canon exists; bounded Phase 580 live-submission integration exists; not universal runtime for every node | `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`; `docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md` |
| Subjective / aesthetic panel | Ratified narrow lane; runtime exists; informational and non-blocking; no general payout path | `docs/specs/ilc_cdl_059_aesthetic_panel_governance_ratification_evidence_531_v0.1.md`; `ilc_core/epistemic/aesthetic_panel_runtime.py` |
| Node submission evaluation | Mode-routing runtime exists; Mode 3 auditor review execution remains incomplete | `docs/specs/ilc_cdl_052_epistemic_node_submission_runtime_handoff_477_v0.1.md`; `ilc_core/epistemic/node_submission_runtime.py` |
| Jury deliberation / petitions | Research memo exists; petition/verdict/envelope/bond design not implemented as general runtime | `docs/research/ilc_jury_deliberation_research_memo_791_v0.1.md` |
| Validator topology randomization | CDL-068 ratified; default-off runtime exists; epoch-hash v1 below 10 validators; VRF required at 10 validators | `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`; `ilc_core/validator/topology_shuffle_runtime.py` |
| Beginning-of-epoch capability work | CapProof/AWP/QATPS plans exist; mostly post-Genesis/non-active; CapProof affects routing/pricing, not direct ILC rewards | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`; `docs/specs/epoch_init_control_loop_v0.1.md` |
| Maintenance tasks | Task classes exist for star maps, contradiction sweeps, graph compression, stability simulation; task queue remains sandbox/non-durable | `ilc_core/genesis/work_task.py`; `ilc_core/work/task_queue.py` |
| Jury / panel incentives | Validator reward and treasury routing exist as default-off quote engines; general jury compensation remains design/CDL work | `docs/specs/ilc_cdl_054_validator_economic_incentive_framework_ratification_evidence_491_v0.1.md`; `ilc_core/epoch/validator_reward_pool_routing_runtime.py`; `docs/research/ilc_inverted_ecu_model_precanon_v0.1.md` |
| Specific panel quorum payout | CDL-083 implements H-CON-02 ejected-stake panel quorum and upheld-refutation attribution; not a general jury economy | `docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md`; `ilc_core/economics/epoch_attribution_settle_runtime.py` |

## 3. Canonical Distinctions To Preserve

1. **Objective panels vs subjective panels.** Objective panels evaluate truth,
   decomposition validity, refutation, provenance, and public graph
   canonicalization. Subjective/aesthetic panels produce transparent quality
   signals and must not be represented as objective truth.
2. **Consensus quorum vs epistemic jury.** Validator BFT quorum certifies epoch
   checkpoints. A 7+1 epistemic panel evaluates knowledge claims. These are
   architecturally distinct and must not be conflated.
3. **Connected agent vs reward-seeking agent.** Connection alone should not impose
   jury work. Reward, reputation, validator eligibility, and public graph influence
   may require opted-in jury/audit/maintenance availability.
4. **Private draft vs public canonical node.** Private or local draft nodes may
   exist without jury passage. Public, reward-bearing, or canonical graph nodes
   should pass a mode-appropriate review lane.
5. **Assignment vs coercion.** Once an agent opts into a reward/reputation lane,
   randomized assignment can be binding for that lane's benefits. This is not the
   same as forcing all agents into jury work.
6. **Approval-volume bias is a first-order risk.** Jury incentives must not pay
   solely per approval, or panels are economically pushed toward rubber-stamping.

## 4. Proposed Phase Sequence

The J-series is mapped to numeric future-window prompt drafts as follows. These
numeric prompts are not executable until a future sequence lock assigns them or a
human gives the corresponding explicit GO.

| J phase | Numeric draft | Purpose |
|---------|---------------|---------|
| J-001 | Phase 1391 | COMPLETE: jury / epoch-work canon map |
| J-002 | Phase 1392 | COMPLETE: jury eligibility and assignment ADR |
| J-003 | Phase 1393 | Public node review taxonomy |
| J-004 | Phase 1394 | Jury incentive economics CDL opening |
| J-005 | Phase 1395 | Epoch-start capability and maintenance contract |
| J-006 | Phase 1396 | Default-off jury assignment quote runtime |
| J-007 | Phase 1397 | Shadow public-ingestion jury harness |
| J-008 | Phase 1398 | Production jury activation gate definition |

### Phase J-001 — Jury / Epoch Work Canon Map

**Goal:** Produce a binding inventory that reconciles all current jury, panel,
CapProof, task, reward, and validator-topology sources.

**Deliverables:**
- `docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md`
- focused tests proving all referenced source files exist
- STATUS entry and graph delta

**Output tokens:**
```text
jury_epoch_work_canon_map_phase_j001
jury_participation_incentivized_not_obligatory_recorded
objective_subjective_panel_split_confirmed
```

**Non-authorizations:** no runtime mutation, no CDL mutation, no public ingestion
activation, no production rewards.

### Phase J-002 — Jury Eligibility and Assignment ADR

**Goal:** Define who can be selected for review work and how randomization works.

**Status:** J-002 / 1392 now complete. See
`docs/adr/ADR_0040_Jury_Eligibility_Assignment.md`.

**Decisions to lock:**
- eligible reviewer classes: worker agent, reviewer agent, validator-agent,
  bootstrap Genesis reviewer, outsider reviewer
- opt-in mechanism for review availability
- reputation / stake / skill thresholds by review lane
- diversity floor and outsider-seat requirements
- deterministic epoch-hash assignment for testnet / public RC shadow mode
- VRF upgrade boundary for production or high-value review lanes
- refusal / non-response effects: no punishment for non-opt-in agents; reward or
  reputation consequences only for agents that opted into availability

**Deliverables:**
- `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` or next available ADR ID
- test fixture for deterministic assignment shape

**Output tokens:**
```text
jury_eligibility_assignment_adr_accepted_phase_j002
randomized_jury_assignment_opt_in_boundary_defined
non_opt_in_agents_not_forced_into_jury_service
```

### Phase J-003 — Public Node Review Taxonomy

**Goal:** Define which graph submissions require which review lane.

**Proposed taxonomy:**
- private/local draft: no jury required
- public non-reward metadata: lightweight schema/admission check
- reward-bearing objective node: CDL-052/CDL-V7 objective review lane
- contested/high-value objective node: 7+1 panel or escalated jury petition
- subjective/aesthetic node: CDL-059 transparent quality panel, non-blocking
- refutation/provenance/stake-affecting claim: specialized panel/quorum lane
- validator/consensus claim: validator BFT evidence, not epistemic jury

**Deliverables:**
- `docs/specs/ilc_public_node_review_taxonomy_v0.1.md`
- tests proving no subjective panel is represented as objective truth

**Output tokens:**
```text
public_node_review_taxonomy_phase_j003
private_draft_nodes_do_not_require_jury
reward_bearing_public_nodes_require_review_lane
subjective_panel_non_blocking_boundary_preserved
```

### Phase J-004 — Jury Incentive Economics CDL Opening

**Goal:** Open the explicit economic design for reviewer compensation.

**Decisions to evaluate:**
- fixed pooled reviewer budget
- petition bond funded review
- delayed accuracy-weighted reviewer bonus
- split fixed fee plus long-run accuracy bonus
- slash / decay for non-response after opt-in commitment
- anti-rubber-stamp checks
- relationship to CDL-047 treasury, CDL-054 validator rewards, CDL-055 staking,
  CDL-083 upheld-refutation attribution, and existing public economics firewall

**Recommended default:** do not pay purely per approval. Use a fixed review fee
for completed work plus delayed accuracy / survival / appeal-outcome component.

**Deliverables:**
- `docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md`
- simulation requirements for panel throughput, approval bias, backlog, and
  long-run accuracy

**Output tokens:**
```text
jury_incentive_economics_cdl_opened_phase_j004
approval_volume_bias_risk_recorded
fixed_plus_accuracy_weighted_panel_compensation_recommended
```

### Phase J-005 — Epoch-Start Capability and Maintenance Work Contract

**Goal:** Convert CapProof / AWP / maintenance-task memory into a staged contract.

**Decisions to lock:**
- CapProof is a readiness/routing/pricing signal, not direct ILC reward
- AWP/IIH remains heavier and later than CapProof
- QATPS/CIT remains optional until simulation and fraud controls mature
- maintenance tasks become reward-eligible only through reviewed task outcomes
- task categories include graph compression, contradiction sweep, star-map
  generation, provenance repair, and fixture/test maintenance
- low-capability agents can participate through maintenance and lottery/pool lanes

**Deliverables:**
- `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md`
- explicit activation ladder: shadow -> bounded testnet -> public RC shadow ->
  production candidate

**Output tokens:**
```text
epoch_start_capability_maintenance_contract_phase_j005
capproof_no_direct_ilc_reward_boundary_confirmed
maintenance_tasks_reward_eligible_after_review_lane
```

### Phase J-006 — Default-Off Jury Assignment Runtime Quote

**Goal:** Implement a non-activating quote engine that composes panels
deterministically for review requests.

**Runtime scope:**
- pure function / quote-only
- deterministic canonical JSON inputs
- no wall-clock protocol time
- no `random`
- no ledger writes
- no graph writes
- no production reward distribution
- no public ingestion activation

**Suggested module:** `ilc_core/epistemic/jury_assignment_runtime.py`

**Output tokens:**
```text
default_off_jury_assignment_quote_runtime_phase_j006
jury_assignment_no_public_activation_phase_j006
epoch_hash_shadow_assignment_only_phase_j006
```

### Phase J-007 — Shadow Public-Ingestion Harness

**Goal:** Connect OpenClaw / public RC ingestion rehearsals to the review taxonomy
without making public graph claims permanent.

**Deliverables:**
- shadow ingestion scenario
- panel assignment fixture
- objective and subjective lane examples
- non-claim record: no public graph permanence, no production rewards, no public
  canonical node creation

**Output tokens:**
```text
shadow_public_ingestion_jury_harness_phase_j007
public_graph_permanence_not_activated_phase_j007
openclaw_ingestion_review_shadow_only_phase_j007
```

### Phase J-008 — Production Jury Activation Gate

**Goal:** Define what must be true before jury-reviewed public graph
canonicalization and reviewer payments become production behavior.

**Prerequisites:**
- jury eligibility ADR accepted
- public node review taxonomy accepted
- incentive economics CDL ratified
- default-off runtime tested
- public economics firewall integrated
- VRF or approved randomness source selected for production assignment
- anti-capture / diversity / outsider-seat checks tested
- appeal and challenge path defined
- counsel / public-claimability boundary reviewed where relevant

**Output tokens:**
```text
production_jury_activation_gate_defined_phase_j008
reviewer_payment_activation_requires_later_gate
public_canonical_node_review_requires_later_gate
```

## 5. Recommended Ordering Relative To Current Window

This plan should not block Phase 1388 or Phase 1389 public-RC gates unless those
gates choose to make public node ingestion or reward-bearing node admission part
of their activation scope.

Recommended placement:

| Timing | Work |
|--------|------|
| Before public RC if time permits | J-001 canon map complete; J-002 assignment ADR draft; J-003 review taxonomy |
| Public RC shadow period | J-005 epoch-start / maintenance contract; J-006 quote runtime; J-007 shadow harness |
| Before production mainnet launch | J-004 incentive economics CDL; J-008 production activation gate; VRF production randomness decision |

The critical path distinction is:

```text
public_rc_can_shadow_jury_lanes_without_production_jury_activation
production_public_graph_canonicalization_requires_jury_activation_gate
```

## 6. Open Decisions

1. Should every reward-bearing public node require a review lane, or only nodes
   above value/reputation/visibility thresholds?
2. Should low-risk objective submissions begin with deterministic mode routing and
   only escalate to 7+1 panels when contested?
3. What exact non-response consequence applies to agents that opted into reviewer
   availability but miss an assigned panel?
4. What is the first acceptable incentive source for reviewer payment: petition
   bonds, treasury budget, write-fee-burn allocation, or a separate review pool?
5. Should subjective/aesthetic review ever affect routing or discovery ranking,
   while still preserving non-blocking/non-truth status?
6. At what graph size / validator count does VRF become mandatory for panel
   assignment, independent of the CDL-068 topology-shuffle threshold?
7. Does maintenance work use the same reviewer pool as node review, or a separate
   maintenance/audit pool?

## 7. Near-Term Recommendation

J-001 is complete. The next concrete phase should be J-002, the jury eligibility
and assignment ADR. It should be treated as non-activating ADR work: no public
ingestion, production jury assignment, production graph canonicalization, or
reviewer payment activation.

J-001 should explicitly preserve this boundary:

```text
connected_agents_are_not_obligated_to_jury_service
reward_weighted_agents_may_opt_into_randomized_review_duties
```

This gives the system the quality-control structure originally intended without
turning participation into coercive protocol work.
