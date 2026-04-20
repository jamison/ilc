# ILC Foundational Carry-Forward Closure Program 701+ v0.1

Status: planning carry-forward artifact
Date: 2026-04-15
Classification: non-checklist closure program
Primary program anchor: `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`

## 0. Scope clarification — Codex lane only

This program covers Codex's constitutional and foundational closure work in
windows 701–726+. It does NOT include the Mysticeti implementation lane.

The Mysticeti substrate implementation runs in a parallel Gemini lane using
the M-series phase namespace (M-001 through M-NNN). That lane is governed by:
`docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

When the Gemini M-series lane completes (M-019 handoff, Claude-audited), its
results feed back to the main Codex lane at a designated convergence window
(see §5.6 below). CDL-017 ratification — opened by Codex at Phase 695 and
implemented by Gemini in M-007 — converges at that window.

The 701+ program's foundational items run independently of the Mysticeti lane.
They do not wait for Gemini lane completion unless explicitly noted.

---

## 1. Purpose and boundary

This artifact exists to prevent historically important ILC ideas from falling
into a permanent gray zone after the `Option D -> Option B` checklist closes.

The repo now has a visible split between:
- concepts that are already constitutional law,
- concepts that are architecturally real but not yet ratified,
- concepts that are partially scaffolded but not fully operationalized,
- and concepts that should remain explanatory doctrine rather than be forced
  into CDL text.

This program is the explicit closure lane for the second and third groups.

It does **not** silently promote these items into current checklist blockers.
Unless a later lane explicitly elevates one of them, this program remains
post-`700` carry-forward work rather than a hidden requirement for `CDL-062`
opening or row-`5`/row-`7`/row-`8` closure.

## 2. Authority and source order

For every item in this program, authority order is:
1. ratified CDL / ADR and live runtime contracts
2. current economic / architecture / checklist specs
3. historical recovery and session-historization artifacts
4. `Z_Past_Chats` foundational literature
5. only then new doctrinal synthesis

Primary source anchors:
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/whitepaper/ilc_whitepaper_working_draft_v6_0.md`
- `docs/research/ilc_foundational_principles_and_window_687_692_context_2026_04_15_v0.1.md`
- `docs/research/ilc_historical_formula_and_mechanism_catalog_v0.1.md`
- `Z_Past_Chats/2026_03_05_Opus_Conversation_Werner_Political_Economy_Phase358_Review.md`
- `Z_Past_Chats/2026_03_22_ILC - Inverted ECU Model Design and Phase 453-459 Hardening.md`
- `Z_Past_Chats/2025_12_01_ILC - Q&A regarding Local Influence and other future governance nodes being on-graph and ajustable.txt`

## 3. Completion modes

Not every item should end as a CDL.

Allowed completion modes in this program are:
1. `constitutional_lock`
   Meaning: the item changes protocol rights, obligations, runtime semantics,
   or durable governance constraints and therefore warrants CDL/ADR treatment.
2. `spec_or_contract_lock`
   Meaning: the item needs a stable engineering contract or namespace/governance
   specification, but not necessarily constitutional law.
3. `doctrine_lock`
   Meaning: the item should be preserved as explanatory whitepaper/economic
   doctrine, with explicit text saying it is interpretive rather than binding.
4. `explicit_non_ratification`
   Meaning: the item is intentionally preserved as historical context,
   inspiration, or implementation freedom, but is not to be presented as
   settled protocol law.

Success for this program is not “ratify everything.”
Success is “every important under-locked item has a deliberate, auditable final
disposition.”

### 3.1 Disposition authority and elevation gates

Default disposition authority:
- sequence-lock artifact for the owning window proposes the intended completion
  mode,
- the companion conversation/research frame states the evidence standard,
- the handoff or closure artifact records the final disposition,
- only a later explicit CDL/ADR lane may upgrade an item into
  `constitutional_lock`.

Default elevation gates:
- `doctrine_lock` requires source traceability plus explicit “not binding law”
  language,
- `spec_or_contract_lock` requires a stable artifact with scope boundary,
  non-goals, and at least one worked example or conformance hook,
- `constitutional_lock` requires an opening stub, prelock evidence, and
  explicit justification that the item changes durable protocol/governance
  rights or obligations,
- `explicit_non_ratification` requires a drop/defer note stating why the item is
  being preserved as history or implementation freedom rather than law.

## 4. Item register and routing

### 4.1 Economic doctrine and kernel-calibration items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| `W_e = ΔH / E_cost` | real economic background, not ratified | `doctrine_lock` unless later evidence requires stronger law | after `693-700`, or in parallel with long-tail economics review | `docs/research/ilc_w_e_traceability_and_kernel_mapping_note_v0.1.md` |
| BAL-profile weights for the four-component ECU kernel | the kernel slots are canon (`reuse`, `contradiction_resilience`, `validation_integrity`, `path_uplift`); exact profile disposition is not settled | `spec_or_contract_lock` first, with optional later `constitutional_lock` only if evidence justifies | after replay/live calibration evidence is available | `docs/specs/ilc_ecu_kernel_profile_calibration_note_v0.1.md` |
| “ILC is post-banking” framing | real explanatory frame, not governance text | `doctrine_lock` | any time after `693-700` | `docs/research/ilc_post_banking_economic_doctrine_note_v0.1.md` |
| Inverted ECU model | historically important, partially echoed by decay and forced circulation | `spec_or_contract_lock` for explicit runtime traceability, plus doctrine preservation | after `693-700`, ideally beside economic monitoring review | `docs/research/ilc_inverted_ecu_model_runtime_traceability_note_v0.1.md` |

#### Completion rule for this block

This block closes when:
- every item above has a declared disposition,
- every runtime-relevant implication is mapped to existing canonical mechanics,
- and any candidate for later ratification has a replay/sim/live-evidence path
  instead of remaining as hand-wavy background.

Special requirement for the inverted-ECU item:
- the closure artifact must say explicitly whether and how current ratified
  mechanisms such as `CDL-V1` temporal decay and `CDL-048` mandatory
  conversion are being treated as operational implementation of the inverted
  circulation model.

Mandatory evidence gate for the BAL-profile item:
- `701-706` should not stop at “plan a calibration later”
- it must publish a concrete calibration harness / replay contract for the ECU
  kernel profile question, including:
  - explicit confirmation that the calibration target is the four-component ECU
    kernel (`reuse`, `contradiction_resilience`, `validation_integrity`,
    `path_uplift`) and not a reframing into stake / temporal-decay /
    diversity-floor / recency slots,
  - candidate profile set including at minimum:
    - `EVEN` (`0.25 / 0.25 / 0.25 / 0.25`),
    - `BAL` (`0.35 / 0.25 / 0.20 / 0.20`, active default / unratified planning
      assumption),
    - `ROBUST` (`0.20 / 0.45 / 0.20 / 0.15`),
    - `REFINE` (`0.45 / 0.15 / 0.20 / 0.20`),
  - explicit statement that `ADAPT` is excluded from the fixed-vector sweep
    unless a separate formal profile-spec artifact exists,
  - deterministic replay tiers:
    - `100-agent` preflight / harness sanity tier,
    - `10,000-agent` evidence-bearing tier,
    - multi-epoch sweep expectation aligned with the whitepaper simulation
      posture,
  - sensitivity dimensions,
  - and the evidence threshold required before any later `constitutional_lock`
    move.

This block should **not** constitutionalize economic metaphors just because they
are historically resonant.

### 4.2 Governance-minimization and graph-native governance items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| “Governance as a bug” | real design principle, partially incorporated | `spec_or_contract_lock` for sunset taxonomy and human-lever classification; optional later ADR/CDL where necessary | start as soon as bootstrap/founder-era lever inventory is stable enough to classify honestly; do not wait for final sovereign-substrate choice | `docs/specs/ilc_governance_minimization_and_sunset_taxonomy_v0.1.md` |
| ADR-0019 graph-native governance compilation boundary | foundational architectural boundary exists, but ADR remains proposed | `spec_or_contract_lock` via explicit ADR disposition before deeper graph-native governance claims are treated as authoritative | start before or at the beginning of the graph-native algorithm-governance lane | `docs/specs/ilc_graph_native_governance_boundary_disposition_note_v0.1.md` |
| Scoring algorithms as first-class on-graph governance objects | scaffolded historically, not fully realized | `spec_or_contract_lock` first | after `693-700`; may overlap with post-`700` graph-native governance work | `docs/specs/ilc_algorithm_governance_and_namespace_contract_v0.1.md` |
| Local-influence / scoring-family worked example | toy/proto implementation exists historically | `spec_or_contract_lock` | after the algorithm-governance contract exists | `docs/research/ilc_local_influence_algorithm_family_and_selection_note_v0.1.md` |

Early-start sublane inside this block:
- `CDL-017` bootstrap transition criteria and Genesis sunset triggers should be
  treated as an earlier-start governance-hardening item, because its subject is
  protocol/bootstrap governance rather than later sovereign-substrate choice.
- The governance-minimization block should therefore allow a pre-`707`
  initiation path for `CDL-017` evidence hardening and opening work if the
  bootstrap/runbook material is mature enough.
- `CDL-017` should not slip past the first lane that would authorize non-Genesis
  validator deployment or equivalent permanent-substrate operator authority on a
  chosen Option-B backend.

#### Completion rule for this block

This block closes when:
- the repo has a durable inventory of human levers, override classes, and
  sunset expectations,
- ADR-0019 has an explicit accepted/amended/rejected disposition rather than
  remaining silently relied upon while still proposed,
- algorithm-governance surfaces are no longer implicit or “sacred”
  implementation details,
- and the project can say clearly which governance claims are philosophy and
  which are actual runtime/governance law.

### 4.3 Adaptive resilience and transport-doctrine items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| Levin-inspired adaptive gossip | real design influence; not cleanly formalized law | `spec_or_contract_lock` | after row-`9` maturity closure and after sovereign-substrate path stabilizes | `docs/specs/ilc_adaptive_gossip_and_partition_repair_contract_v0.1.md` |
| Active repair/reselection under missing-signal conditions | partially implied by resilience discussions | `spec_or_contract_lock` | with the adaptive-gossip contract | `docs/research/ilc_missing_signal_adaptive_repair_benchmark_plan_v0.1.md` |
| Economic coupling between connectivity and usefulness | historical idea, not explicit runtime law | `explicit_non_ratification` or later `doctrine_lock` unless a real runtime dependency emerges | after adaptive-gossip benchmarking | fold into the benchmark plan or a later doctrine note |

#### Completion rule for this block

This block closes when:
- the repo has an explicit answer on what adaptive behavior the protocol
  requires versus what remains implementation freedom,
- resilience claims are benchmarked rather than metaphorical,
- and the Levin influence is either operationalized or explicitly retained only
  as background inspiration.

### 4.4 Node-transfer economics, commons dedication, and leasehold items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| ADR-0015 node-transfer economics package (transfer tax, cooling period, public goods dedication) | proposed bundle; no CDL; no authoritative sim package | `constitutional_lock` after explicit simulation and ADR disposition | after `707-712`, or earlier if launch/post-launch economic claims begin to assume transferability rules | `docs/specs/ilc_node_transfer_economics_and_commons_dedication_package_v0.1.md` |
| Leasehold model | proposed, explicitly simulation-dependent | `spec_or_contract_lock` first, with optional later `constitutional_lock` depending on activation timing | after transfer-economics package and dedicated lease-duration evidence work exist | `docs/specs/ilc_leasehold_duration_and_reversion_calibration_note_v0.1.md` |

#### Completion rule for this block

This block closes when:
- ADR-0015 receives an explicit accepted/amended/rejected disposition,
- the transfer-tax / cooling / dedication family is no longer treated as
  hand-wavy future economics,
- leasehold either has an evidence-backed activation path or an explicit
  deferment record,
- and the repo can say whether these mechanisms are launch-bound,
  post-launch-bound, or deferred indefinitely.

### 4.5 Sequestered financial-shard and gated-economy eligibility items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| Sequestered financial shard / dedicated `B_hft` lane | explicitly proposed and post-launch; not blocked on shard-lifecycle CDL anymore | `spec_or_contract_lock` for eligibility/prefilter first; later `constitutional_lock` only if a real activation case exists | after public launch, after at least one post-launch monitoring cycle, and only with a concrete demand signal plus contagion/firewall simulation readiness | `docs/specs/ilc_sequestered_financial_shard_eligibility_prefilter_v0.1.md` |

#### Completion rule for this block

This block closes when:
- the repo has an explicit answer on when the sequestered-shard lane becomes
  eligible to open,
- the trigger conditions are published rather than assumed,
- and the financial-shard question is no longer silently mixed together with
  unrelated shard-lifecycle or private/gated-shard questions.

### 4.7 Validator-Agent Identity System

Full design reference: `docs/research/ilc_validator_agent_identity_system_v0.1.md`

Accepted design position (2026-04-16): validators are agents that have taken on
a validator role. `ValidatorID` must eventually map to `AgentID`. Validator
stake (CDL-055) is backed by agent ECU. Validator reputation extends the
CDL-V1 through CDL-V7 agent reputation chain. Topology assignment should use
the same randomized assignment machinery as jury/quorum selection (7+1 panels).

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| `ValidatorID` → `AgentID` linkage | Unresolved — M-series uses opaque `u32` | `constitutional_lock` via CDL-017 | Window 707-712 research sub-lane | `docs/research/ilc_validator_agent_design_evidence_v0.1.md` |
| `ValidatorKey` derivation from `AgentID` | Design question open (same key vs sub-key) | `spec_or_contract_lock` first; incorporated into CDL-017 prelock | Window 707-712 | Fold into design evidence doc |
| Validator selection via reputation-weighted random assignment | Design proposal; consistent with CDL-V1/V3 | `constitutional_lock` via CDL-017 | After SIM-VALIDATOR-01 and reputation calibration evidence | `docs/research/ilc_validator_selection_and_topology_assignment_v0.1.md` |
| Topology shuffling authorization | Blocked by CDL-039 pending constitutional authorization | `constitutional_lock` via CDL-039 amendment or new CDL | After Q5 (VRF vs epoch-hash) resolved; Window 707-712+ | CDL-039 amendment opening stub |
| Validation pools (stake delegation, slash propagation) | Architectural proposal only; no CDL | `constitutional_lock` via separate CDL (after CDL-017 core) | Post CDL-017 core ratification | `docs/research/ilc_validation_pool_and_stake_delegation_v0.1.md` |
| CDL-V3 diversity floor extension to validator set | Open constitutional question | Resolve in CDL-017 prelock; may require CDL-V3 amendment | Window 707-712 conversation | Named in prelock evidence packet |

#### Required simulations before CDL-017 prelock

- **SIM-VALIDATOR-01**: minimum ECU stake threshold calibration. Inputs:
  expected transfer volume per epoch, CDL-055 slash rates. Must show stake
  floor renders equivocation always economically irrational.
- **SIM-TOPOLOGY-01**: topology shuffle sizing and k-regular subgraph bounds.
  Inputs: N validators, F Byzantine tolerance, shuffle frequency. Must confirm
  gossip graph remains connected across shuffle transitions under worst-case F.

#### Six constitutional questions that must be answered before CDL-017 prelock

1. `ValidatorKey`: same BLS key as `AgentID`, or derived sub-key with provable linkage?
2. Minimum ECU stake threshold (SIM-VALIDATOR-01 required)?
3. Reputation-weighted selection: proportional to `ecu_score`, or threshold-based eligibility pool?
4. Validation pools: CDL-017 scope, or separate subsequent CDL?
5. Topology assignment seed: epoch-hash (public/predictable) or VRF (private/unpredictable)?
6. Does CDL-V3 diversity floor extend to validator set composition? If yes, what is the diversity metric?

These questions must be resolved in conversation with Sonnet before any Codex
prelock phase begins. They are not resolvable from code alone.

#### Completion rule for this block

This block closes when:
- Q1 through Q6 are answered and recorded in a research artifact,
- SIM-VALIDATOR-01 and SIM-TOPOLOGY-01 evidence exists,
- CDL-017 prelock incorporates the validator-agent design explicitly,
- validation pools are either included in CDL-017 or formally deferred to a
  named subsequent CDL, and
- CDL-039 topology-shuffling amendment lane is either opened or explicitly
  deferred with a trigger condition.

---

### 4.6 M-series security deferred items requiring CDL action

These items were identified during the M-001 to M-007 security hardening pass
(2026-04-16, commit `486b6896`) and formally deferred with routing decisions.
Full technical context is in §6 of the M-series planning doc:
`docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`

| Token | Gap | Completion mode | Routing | Must resolve before |
|---|---|---|---|---|
| `sec_001_agent_sender_auth_cdl_066_required_before_m009` | `ECUTransfer` carries no sender sig — any validator can forge a transfer | `constitutional_lock` via CDL-066 | CDL-066 opened Phase 694; SEC-001 implementation **CLOSED** `acfcfd2d` | **SATISFIED** — M-009/M-010/M-011 complete |
| `sec_002_chain_id_dst_required_before_m009_testnet` | DST `b"ILC_FAST_PATH_V1"` has no network discriminator — testnet sigs valid on mainnet | `spec_or_contract_lock` via M-008 + ADR-0011 amendment | M-008 scope; ADR-0011 amendment dated 2026-04-16 | **CLOSED** M-008 |
| `sec_003_gossip_sync_recovery_owned_in_m008` | No offline validator cert recovery — returning validator gets locked out on stale ObjectRef | `spec_or_contract_lock` via M-008 | M-008 `MissingCertSync` message type | **CLOSED** M-008 |
| `sec_004_epoch_validator_binding_owned_by_cdl_017_activation` | No historical ValidatorSet binding on TransferCertificate — ejected validator sigs may pass after ejection | `constitutional_lock` scope via CDL-017 activation | CDL-017 activation phase; M-019 handoff must name it explicitly | M-019 handoff |
| `sec_005_lmdb_map_size_owned_by_m009_node_config` | LMDB environment opened with no `set_map_size()` — defaults to ~10 MB on macOS | `spec_or_contract_lock` via node runner config | M-010 single LMDB env with `set_map_size()` (`83a1305d`) | **CLOSED** M-010 |

**SEC-001 and CDL-066 — historical note (updated 2026-04-17):** SEC-001
implementation was CLOSED at commit `acfcfd2d` (2026-04-16): `ECUTransfer`
carries `sender_sig: AgentSig` and it is verified before quorum. CDL-066 was
opened by Codex at Phase 694. M-009, M-010, and M-011 are all complete;
CDL-066 constitutional ratification is OPEN (Track A, Window 707+) and does
NOT block any M-series phase. The previous text saying "Codex must open CDL-066
before M-009 is approved" was correct at the time of writing but is now
historical — M-009 was approved and M-010 and M-011 have since completed.

Note: CDL-062 is already open as the sovereign substrate research CDL (opened
in window 687-692, Mysticeti elevated to Tier 1 primary in Phase 693 addendum).
Agent sender authorization is CDL-066. Earlier planning drafts named `CDL-063`,
but `CDL-063`, `CDL-064`, and `CDL-065` are already occupied in the decision log.

CDL-066 recommended opening stub: "Agent authorization envelope for ECU
fast-path transfers: authorization-surface opening, CDL-042 compatibility,
and mandatory verification sequence in `FastPathProtocol::execute_certificate`
before any quorum threshold check."

CDL-066 should NOT be silently blocked by CDL-017 timeline. The two CDLs
address different things: CDL-017 governs who is *in the validator set*;
CDL-066 governs who is *authorized to initiate a transfer*.

#### Completion rule for this block

This block closes when:
- SEC-001 (CDL-066) is ratified and the `AgentSig` field is present in
  the committed `ECUTransfer` type with a passing test
- SEC-002 is resolved in M-008 and ADR-0011 amendment is accepted
- SEC-003 is resolved in M-008 with a passing integration test
- SEC-004 disposition is documented in the M-019 handoff package
- SEC-005 is resolved in M-009 node config with no LMDB soft-default remaining

## 5. Suggested window routing

### 5.1 `701-706` — Foundational Economic Doctrine and Kernel Calibration

Primary closure targets:
- `W_e = ΔH / E_cost`
- BAL-profile weight disposition
- post-banking doctrine lock
- inverted-ECU runtime traceability

Recommended outputs:
- doctrine/law classification table
- kernel traceability note
- calibration/replay contract for the four-component ECU kernel, explicitly
  using `reuse`, `contradiction_resilience`, `validation_integrity`, and
  `path_uplift` as the scored slots
- candidate profile set fixed at `EVEN`, `BAL`, `ROBUST`, `REFINE` for the
  fixed-vector sweep; `ADAPT` handled separately as a later formal-spec item
- replay tiers fixed at `100-agent` preflight and `10,000-agent`
  evidence-bearing deterministic replay
- whitepaper/economic-architecture amendment packet

Nearer-term non-blocking requirement for `687-692`:
- if sovereign-substrate benchmarking or comparison work uses BAL-profile kernel
  weights as planning inputs, the lane must say so explicitly and must label
  those weights as unratified planning assumptions pending the `701-706`
  calibration/disposition lane.

### 5.2 `707-712` — Governance Minimization and Graph-Native Algorithm Governance

Primary closure targets:
- governance-minimization inventory
- human-lever sunset taxonomy
- algorithm-governance namespace and selection contract
- local-influence family worked example

Recommended outputs:
- governance taxonomy artifact
- ADR-0019 disposition note
- graph-native algorithm contract
- worked example and non-goal boundary note

Allowed early-start carry-forward before `707`:
- `CDL-017` bootstrap transition criteria / Genesis sunset triggers
- bootstrap-lever inventory and observable-trigger hardening
- explicit split between founder-rent sunset and steward/infrastructure
  incentive continuity where required

#### 5.2.1 Validator-Agent Identity System sub-lane (within 707-712)

This sub-lane runs inside 707-712. It is NOT a separate window; it is an
explicit research and conversation deliverable within the governance-minimization
window. Classification: **Research: HIGH, Sim/replay: HIGH, Conversation: VERY HIGH**.

The six constitutional questions (§4.7) must be answered in pre-window
conversation with Sonnet before Codex begins any phase in this sub-lane.

Background reference for gossip topology and topology-shuffling design:
`docs/research/ilc_gossip_hybrid_push_pull_architecture_context_v0.1.md`
— establishes the original push-pull threat model and inv/getdata rationale
that governs how validator peer connections and shuffle frequency interact with
gossip architecture. Read this before drafting the CDL-039 amendment scope note.

Required outputs within 707-712:
- Conversation record: Q1 through Q6 answered and agreed
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md` — maps Q1-Q6
  answers to CDL-017 prelock checklist requirements
- SIM-VALIDATOR-01 commissioned and results available
- SIM-TOPOLOGY-01 commissioned (may complete in later window)
- CDL-039 amendment scope note: topology shuffling authorization path

Note: CDL-017 **ratification** does not happen in 707-712. Ratification
happens in the Mysticeti convergence window (§5.6) because it requires both
Codex constitutional text and Gemini M-series implementation evidence.
Window 707-712 produces the prelock evidence and design resolution.

### 5.3 `713-716` — Adaptive Gossip and Resilience Operationalization

Background reference:
`docs/research/ilc_gossip_hybrid_push_pull_architecture_context_v0.1.md`
— establishes the original push-pull (inv/getdata) threat model and CDL-036
compatibility rationale. Read before drafting the adaptive-gossip contract.
Current implementation (CDL-060, CDL-061, `gossip_transport.py`,
`ilc_consensus/src/network.rs`) has moved beyond this doc; use it for design
rationale and threat-model baseline, not as a description of current behavior.

Primary closure targets:
- adaptive-gossip contract
- partition-repair benchmark pack
- missing-signal doctrine disposition

Recommended outputs:
- transport resilience contract
- benchmark pack
- explicit law-vs-freedom decision memo

### 5.4 `717-722` — Node Transfer Economics, Commons Dedication, and Leasehold Calibration

Primary closure targets:
- ADR-0015 disposition
- transfer tax and cooling-period simulation package
- public-goods dedication governance package
- leasehold duration / reversion evidence note

Recommended outputs:
- node-transfer economics package artifact
- explicit sim commissioning / replay contract for transfer-tax, cooling, and
  lease-duration questions
- CDL-opening recommendation or deferment memo for the transfer-economics lane

### 5.5 `723-726` — Sequestered Financial-Shard Eligibility and Gated-Economy Prefilter

Primary closure targets:
- post-launch trigger conditions for the sequestered financial shard
- contagion/firewall evidence prerequisites
- explicit separation from ordinary shard-lifecycle law

Recommended outputs:
- eligibility prefilter artifact
- activation trigger matrix
- explicit defer / open recommendation tied to post-launch evidence rather than
  folklore

### 5.6 Mysticeti Convergence Window (post-726, timing TBD)

When the Gemini M-series lane completes M-019 (handoff package) and Claude
has approved it, the main Codex lane opens a convergence window. This window
is not assigned a fixed number here because its timing depends on Gemini lane
progress. It is assigned when M-019 is approved.

Primary closure targets in convergence window:
- CDL-017 ratification (opened at Phase 695 by Codex; implemented by Gemini
  in M-007; ratification requires M-series BLS validator governance work plus
  the constitutional text from Codex's Phase 695 opening)
- Settlement-state formal CDL ratification (CDL-067, opened at Phase 696 by
  Codex; Mysticeti application interface from Gemini lane feeds into
  ratification evidence)
- First authorized validator deployment authorization (explicit human gate)
- Integration of Mysticeti implementation into RC track (convergence with
  Track A RC development)
- Option B graduation checklist final closure (if all rows satisfied)

This window is the only point where the Gemini and Codex lanes formally merge.
Until M-019 is approved, the two lanes are independent.

`mysticeti_convergence_window_opens_after_m019_approved`
`cdl_017_ratification_requires_both_codex_constitutional_and_gemini_implementation`

## 6. Integration rules for current planning

To prevent these items from being forgotten before `701+`, the repo should
carry three explicit rules now:
1. every sequence-lock or handoff that touches these topics must either point to
   this program or explicitly say the item is out of scope for the current lane,
2. `TODO.txt` must retain a dedicated carry-forward block with concrete trigger
   conditions and suggested artifact paths,
3. doctrinal restoration memos may not be cited as if they themselves
   constitutionalize the claim.

## 7. Non-goals

This program does **not** do the following:
- reopen rows `5-9`,
- silently block `CDL-062`,
- force every historical idea into a CDL,
- or treat metaphysical language as sufficient for runtime/governance law.

### 7.1 Deferred programs not in scope for 701-726

The following planning artifacts exist and are canon-adjacent but belong to
programs that start **after** the convergence window closes:

- **L3 app development program** (post-convergence):
  `docs/specs/ilc_l3_app_sidecar_and_homoiconic_object_model_note_v0.1.md`
  Covers the sidecar model, homoiconic representation for L3 apps, schema
  governance, and the market-app object-model example. Content is sound and
  non-stale. Scheduled for a dedicated L3 app development program that opens
  after the sovereign substrate is stable. Does not require a CDL yet. Not in
  scope for any window in 701-726.

- **Morphogenetic hypergraph research lane** (post-mainnet, with one pre-M-018 gate):
  Established 2026-04-19. ADR-0029/0030/0031 proposed; SIM programs SIM-HYPEREDGE-01,
  SIM-SPECTRAL-01, SIM-EMBED-01, SIM-BEACON-01, SIM-ROUTING-01 registered but not yet
  commissioned. Merkle-Laplacian dual commitment and sealed spectral beacon are candidate
  novel research contributions (patent assessment required before publication).
  **One item is in-scope for the current M-series window:** ADR-0031 proto gate must land
  before M-018 finalizes its gRPC query surface. All other items are post-mainnet.
  Master index: `docs/PLANNING_INDEX.md` §9.
  Substrate additions guide (what to add now): `docs/research/ilc_morphogenetic_substrate_additions_now_v0.1.md`.

## 8. Bottom line

The project now has enough historical recovery to know which ideas matter.
What it lacks is a durable closure route for ideas that sit between “real” and
“ratified.”

This artifact is that route.
