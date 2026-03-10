# ILC Constitutional Decision Log v0.1

Status: Open
Date: 2026-02-08
Companion proposal: `docs/specs/ilc_constitutional_decisions_proposal_v0.1.md`

Triage reference:
- `docs/research/constitution_clause_triage_v0.1.md`
- `docs/research/constitution_mvp_criticality_v0.1.md`
- `docs/research/constitution_mvp_guardrails_matrix_v0.1.md`
- `docs/specs/ilc_constitutional_decisions_proposal_v0.2.md`

## Triage Snapshot

- `KEEP-NOW`: CDP-001, CDP-002, CDP-004, CDP-005, CDP-006, CDP-009
- `KEEP-DEFER`: CDP-003, CDP-007, CDP-010
- `DEFER-OUT`: CDP-008

## MVP Guardrail Snapshot

- Guardrail matrix: `docs/research/constitution_mvp_guardrails_matrix_v0.1.md`
- `mvp_now` clauses require strict implementation (`CDP-001`, `CDP-002`, `CDP-006`).
- `mvp_guardrail` clauses require explicit owner artifacts now and deferred-target tracking.

## Decision Register

| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |
|---|---|---|---|---|---|---|
| CDL-001 | CDP-001/CDP-002 | Canonical signer lineage definition | ratified | strict lineage, lineage+timelock, lineage+multi-sig council | lineage+timelock | key registry spec update, validator tests | ratified_phase: 251 | ratified_date: 2026-02-21 | evidence_document: docs/specs/ilc_security_cdl_ratification_evidence_251_v0.1.md |
| CDL-002 | CDP-001 | Emergency key compromise response | ratified | immediate revoke, revoke+grace period, staged migration | revoke+grace period | incident policy text, integration tests | ratified_phase: 251 | ratified_date: 2026-02-21 | evidence_document: docs/specs/ilc_security_cdl_ratification_evidence_251_v0.1.md |
| CDL-003 | CDP-003 | Founder fade-out mechanics | ratified | fixed sunset, trigger-based sunset, governance-vote sunset | trigger-based sunset | governance spec section, telemetry obligations |
| CDL-004 | CDP-003/CDP-008 | Founder operational caps | ratified | soft norms, hard protocol caps, hard caps + public reporting | hard caps + reporting | economics/governance spec alignment |
| CDL-005 | CDP-007 | Issuance/cap constitutional wording | ratified | cap-only, cap+trajectory, cap+trajectory+guardrails | cap+trajectory+guardrails | economics spec + regression tests |
| CDL-006 | CDP-004/CDP-005 | Governance override/challenge process | ratified | single-body, dual-body, multi-body checks | multi-body checks | challenge node spec, audit path tests |
| CDL-007 | CDP-006 | Rollback resistance baseline | ratified | seq-only, seq+hash-link, seq+hash+signed checkpoints | seq+hash+signed checkpoints | channel spec + negative tests | ratified_phase: 251 | ratified_date: 2026-02-21 | evidence_document: docs/specs/ilc_security_cdl_ratification_evidence_251_v0.1.md |
| CDL-008 | CDP-010 | Layer boundary: fixed core vs policy-loaded layers | ratified | heavy fixed core, minimal fixed core, split-by-domain | split-by-domain | architecture appendix + ADR |
| CDL-009 | CDP-009 | Fork legitimacy/user signaling | ratified | naming-only, signature-badge, signature-badge+eligibility rules | signature-badge+eligibility rules | client UX + policy docs |
| CDL-010 | CDP-003 | Pseudonymity/accountability balance | ratified | strict anonymity, pseudonymous attestations, doxxed governance | pseudonymous attestations | comms policy + incident policy |
| CDL-011 | ADR-0008 / NodeValueTrack | Node usefulness formula ratification (`EW`) | ratified | reuse-heavy, balanced composite, resilience-heavy | balanced composite | deterministic score vectors + conformance tests |
| CDL-012 | ADR-0008 / NodeValueTrack | Utility-flow reward linkage (`UF`) | ratified | usage-only, usage+freshness, full composite | usage+freshness | payout simulation + regression tests |
| CDL-013 | ADR-0008 / NodeValueTrack | Governance-weight decay and Genesis baseline | ratified | decay-all, decay-non-genesis-only, hybrid baseline | decay-non-genesis-only | governance normalization tests + policy docs |
| CDL-014 | ADR-0008 / NodeValueTrack | Path-level marginal contribution method | ratified | local delta, counterfactual path-lift, market-only proxy | counterfactual path-lift | replayable counterfactual harness |
| CDL-015 | ADR-0008 / NodeValueTrack | Implementation order lock (refactor avoidance) | ratified | ad-hoc order, dependency-ordered sequence, strict phase gate | strict phase gate | ratification plan + master plan sequencing |
| CDL-019 | ADR-0008 / NodeValueTrack | Multiplier-governance surface: resolve relationship between flat Genesis constant (1.2x), refutation-profitability invariant floor, and eventual dynamic ranking-based multiplier mechanism | ratified | flat Genesis constant only, governed constant + invariant floor, governed constant + dynamic ranking mechanism | governed constant + invariant floor (dynamic ranking deferred) | multiplier policy contract update, invariant regression coverage, governance migration plan | ratified_phase: 268 | ratified_date: 2026-02-22 | evidence_document: docs/specs/ilc_cdl_019_multiplier_governance_surface_ratification_evidence_268_v0.1.md |
| CDL-020 | ADM-001 / Roadmap v0.3 | Protocol-native bundle schema and complete type system | ratified | full schema catalog, minimal schema catalog, phased schema catalog | full schema catalog (proposed) | D2 schema artifact set, bundle generator/verifier tooling, test vectors | ratified_phase: 319 | ratified_date: 2026-02-27 | evidence_document: docs/specs/ilc_cdl_020_d2_schema_baseline_ratification_evidence_319_v0.1.md |
| CDL-021 | ADM-001 / Roadmap v0.3 | Rust kernel port and WASM distribution | open | defer indefinitely, milestone-triggered rust port, immediate rust migration | milestone-triggered rust port (proposed) | D4 implementation plan, parity tests, WASM packaging evidence |
| CDL-022 | ADM-001 / Roadmap v0.3 | Genesis state bundle specification and signing ceremony | ratified | genesis bundle only, genesis bundle + ceremony, ad hoc bootstrapping | genesis bundle + ceremony (proposed) | D2b schema/spec, generator/verifier tooling, ceremony checklist | ratified_phase: 320 | ratified_date: 2026-02-27 | evidence_document: docs/specs/ilc_cdl_022_genesis_state_bundle_ratification_evidence_320_v0.1.md |
| CDL-023 | ADM-001 / Roadmap v0.3 | Epoch snapshot mechanism and fast-bootstrap protocol | ratified | periodic snapshots, triggered snapshots, hybrid model | hybrid model (proposed) | D2c snapshot schema, generator/verifier tooling, retention policy | ratified_phase: 321 | ratified_date: 2026-02-27 | evidence_document: docs/specs/ilc_cdl_023_epoch_snapshot_ratification_evidence_321_v0.1.md |
| CDL-024 | ADM-001 / Roadmap v0.3 | Wire protocol specification and transport bindings | ratified | single transport binding, transport-agnostic + reference bindings, framework-specific bindings | transport-agnostic + reference bindings (proposed) | D2d message schema set, transport requirements, conformance tests | ratified_phase: 329 | ratified_date: 2026-02-28 | evidence_document: docs/specs/ilc_cdl_024_wire_transport_ratification_evidence_329_v0.1.md |
| CDL-025 | CDL-005 | Terminal issuance model (hard cap vs. tail emission reconciliation) | ratified | asymptotic cap (Model A), fee-funded tail (Model B), burn-offset tail (Model C) | fee-funded tail / Model B (planning recommendation — not ratified) | terminal model spec, issuance simulation | ratified_phase: 267 | ratified_date: 2026-02-22 | evidence_document: docs/specs/ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md |
| CDL-026 | CDL-005 / CDL-025 | Total supply cap (`C_max`) lock | ratified | explicit finite cap, cap-with-tolerance | depends on CDL-025 closure | cap lock spec, regression tests | ratified_phase: 273 | ratified_date: 2026-02-23 | evidence_document: docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md |
| CDL-027 | CDL-005 / CDL-026 | Decay formulation and schedule constants (`H` or `lambda`) | ratified | discrete halving period `H`, continuous decay rate `lambda` | depends on CDL-026 closure | decay schedule spec, schedule simulation | ratified_phase: 276 | ratified_date: 2026-02-23 | evidence_document: docs/specs/ilc_cdl_027_decay_formulation_ratification_evidence_276_v0.1.md |
| CDL-028 | CDL-005 / CDL-025 | Fee-burn split ratio | ratified | 30% burn, 50% burn, other percentages | depends on CDL-025 terminal model closure | fee model spec, payout regression | ratified_phase: 274 | ratified_date: 2026-02-23 | evidence_document: docs/specs/ilc_cdl_028_fee_burn_split_ratification_evidence_274_v0.1.md |
| CDL-029 | CDL-005 / CDL-011 | Allocation split (performer/auditor/genesis) validation and lock | ratified | confirm 80/15/5, revise split, redesign | 80/15/5 proposed — requires `theta_hard = 1/20` validation | allocation validation tests, governance spec alignment | ratified_phase: 272 | ratified_date: 2026-02-23 | evidence_document: docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md |
| CDL-030 | CDL-005 / CDL-027 | ECU price clamp bounds (`P_min`, `P_max`) | ratified | bounds derived from issuance schedule | derived from CDL-027 decay schedule | ECU clamp spec, pricing simulation | ratified_phase: 277 | ratified_date: 2026-02-23 | evidence_document: docs/specs/ilc_cdl_030_ecu_price_clamp_ratification_evidence_277_v0.1.md |
| CDL-031 | CDL-019 / ADR-0008 | Dynamic ranking-based multiplier policy (if admitted after CDL-019 closure) | ratified | defer indefinitely, admit with guardrails and CDL-019 prerequisite satisfied | deferred until CDL-019 closure | ranking policy spec, invariant regression coverage | ratified_phase: 288 | ratified_date: 2026-02-24 | evidence_document: docs/specs/ilc_cdl_031_dynamic_ranking_policy_ratification_evidence_288_v0.1.md |
| CDL-032 | ADM-002 | CLI-first Agent SDK interface contract and command surface | ratified | single CLI entry point, split library + CLI, API-first | CLI-first (proposed) — see `ilc_adm_002_cli_first_agent_sdk_v0.1.md` | ADM-002 ratification artifact, command surface spec, I/O contract schema | ratified_phase: 253 | ratified_date: 2026-02-21 | evidence_document: docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md |
| CDL-033 | ADM-002 / CDL-032 | OpenClaw skill specification and ClawHub publication contract | ratified | skill-only, skill + dedicated agent, full fleet config | skill-only initial (proposed) — dedicated agent config deferred to Phase B | SKILL.md spec, ClawHub PR, working CLI binary (CDL-032 prerequisite) | ratified_phase: 291 | ratified_date: 2026-02-24 | evidence_document: docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md |
| CDL-V1 | CDL-019 / Vulnerability Plan v0.1 | Temporal decay governance parameter for reuse centrality | ratified | no temporal decay, epoch-step decay, exponential half-life decay | exponential half-life decay (proposed) | decay sensitivity analysis, lock-in simulation, monitoring thresholds | ratified_phase: 330 | ratified_date: 2026-02-28 | evidence_document: docs/specs/ilc_cdl_v1_temporal_decay_ratification_evidence_330_v0.1.md |
| CDL-V2 | CDL-001 / CDL-033 / Vulnerability Plan v0.1 | Sybil resistance mechanism for participant identity and reuse validation | ratified | proof-of-personhood gate, stake-based participation cost, hybrid heuristic resistance | hybrid heuristic resistance (proposed) | sybil threat model, synthetic graph simulations, operator response thresholds | ratified_phase: 331 | ratified_date: 2026-02-28 | evidence_document: docs/specs/ilc_cdl_v2_sybil_resistance_ratification_evidence_331_v0.1.md |
| CDL-V3 | ADR-0008 / Vulnerability Plan v0.1 | Ratification quorum diversity requirements | ratified | cluster diversity floor, weighted diversity quorum, supermajority-only governance | cluster diversity floor (proposed) | quorum composition simulation, coordinated voting adversarial tests, governance wording | ratified_phase: 332 | ratified_date: 2026-03-01 | evidence_document: docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md |
| CDL-V4 | Vulnerability Plan v0.1 / Popper Analysis v0.1 | Minority dissent, appeal, and reopening protocol for ratified CDL decisions | ratified | genesis-only reopening, full re-ratification only, minority dissent trigger plus formal reopening protocol | minority dissent trigger plus formal reopening protocol (proposed) | minority threshold analysis, reopening abuse simulation, Genesis-boundary wording | ratified_phase: 334 | ratified_date: 2026-03-02 | evidence_document: docs/specs/ilc_cdl_v4_reopening_protocol_ratification_evidence_334_v0.1.md |
| CDL-V5 | CDL-020 / CDL-023 / Vulnerability Plan v0.1 | Schema epoch markers and cross-version translation protocol for centrality comparability | ratified | no epoch markers, schema epoch markers only, schema epoch markers plus explicit cross-version translation | schema epoch markers plus explicit cross-version translation (proposed) | translation invariance test vectors, epoch-marker serialization contract, backward-compatibility thresholds | ratified_phase: 333 | ratified_date: 2026-03-01 | evidence_document: docs/specs/ilc_cdl_v5_schema_epoch_translation_ratification_evidence_333_v0.1.md |
| CDL-V6 | Epistemological Foundations v0.1 / Vulnerability Plan v0.1 | Genesis agent intervention protocol for constitutional override and emergency response | ratified | informal founder discretion, hard prohibition on intervention, documented Genesis override with sunset and audit trail | documented Genesis override with sunset and audit trail (proposed) | intervention trigger matrix, audit record schema, sunset/appeal criteria | ratified_phase: 334 | ratified_date: 2026-03-02 | evidence_document: docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md |
| CDL-V7 | Popper Analysis v0.1 / Epistemological Foundations v0.1 | Agent decomposition admissibility criteria for ILC knowledge units | ratified | utility-only acceptance, operator discretionary decomposition, Popperian basic-statement gate for agent decomposition | Popperian basic-statement gate for agent decomposition (proposed) | decomposition test corpus, admissibility counterexamples, cross-agent reproducibility rubric | ratified_phase: 335 | ratified_date: 2026-03-02 | evidence_document: docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md |
| CDL-034 | ADM-001 / Node Schema Packet v0.1 | Unified node schema envelope, reserved fields, and primitive/core field taxonomy | ratified | single-envelope flat schema, two-envelope authored/runtime split, three-envelope authored/protocol/transport split | three-envelope authored/protocol/transport split | envelope contract, reserved-field collision rules, primitive_type taxonomy | ratified_phase: 349 | ratified_date: 2026-03-04 | evidence_document: docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md |
| CDL-035 | Node Schema Packet v0.1 / CDL-V7 | Validation lifecycle, gate-verdict attachment, and quarantine semantics | ratified | inline mutable lifecycle state, attached lifecycle envelope with unbounded recursive verdict effects, attached lifecycle envelope with bounded operational relevance | attached lifecycle envelope with bounded operational relevance | validation_state machine, gate_verdict attachment model, quarantine semantics | ratified_phase: 350 | ratified_date: 2026-03-04 | evidence_document: docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md |
| CDL-036 | ADM-001 / CDL-024 | Node dissemination header, payload fetch contract, and transport boundary | ratified | full-payload push broadcast, header-first dissemination with fixed orderer, header-first dissemination with CID-addressed pull fetch | header-first dissemination with CID-addressed pull fetch | header schema, fetch semantics, signature scope | ratified_phase: 351 | ratified_date: 2026-03-04 | evidence_document: docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md |
| CDL-037 | CDL-034 / CDL-V7 | Executable node descriptor, safety contract, and agent-side sandboxing | ratified | raw executable payload embedded in authored envelope, structured descriptor without sandboxing, structured descriptor with sandboxed runtime binding | structured descriptor with sandboxed runtime binding | executable descriptor schema, safety contract model, sandbox boundary semantics | ratified_phase: 352 | ratified_date: 2026-03-04 | evidence_document: docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_ratification_evidence_352_v0.1.md |
| CDL-038 | CDL-034 / CDL-035 | Private-to-public promotion, promotion_receipt provenance, and visibility-change continuity | ratified | in-place visibility mutation on original node, successor-node plus promotion_receipt, successor-node plus promotion_receipt with automatic reputation carry-forward | successor-node plus promotion_receipt without automatic reputation carry-forward | promotion_receipt schema, disclosed lineage rules, carry-forward boundary | ratified_phase: 353 | ratified_date: 2026-03-04 | evidence_document: docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md |
| CDL-039 | ADR-0011 / Open Requirements 354 v0.1 | P2P transport baseline, no-central-broker invariant, and gossip-topology privacy constraints | ratified | centrally coordinated relay transport, federated relay mesh, brokerless peer-to-peer gossip baseline | brokerless peer-to-peer gossip baseline | no-central-broker invariant, topology-privacy constraints, partition evidence requirements | ratified_phase: 379 | ratified_date: 2026-03-06 | evidence_document: docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md |
| CDL-040 | ADR-0014 / CDL-034 / CDL-039 | Admission control policy and identity-envelope semantics | ratified | identity-envelope extension of authored payload, fourth-envelope plus CDL-034 companion amendment | identity-envelope extension of authored payload | ADR-0014 anchor, admission-control scope boundary clause, CDL-039 dependency clause | ratified_phase: 393 | ratified_date: 2026-03-09 | evidence_document: docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md |
| CDL-041 | SIM-004 / CDL-V3 / CDL-039 | Shard lifecycle operations for creation, merge, and split under partition and privacy constraints | ratified | merge-first lifecycle with highest_ecu_wins reconciliation, split-first elastic lifecycle with delayed merge reconciliation | merge-first lifecycle with highest_ecu_wins reconciliation | SIM-004 reconciliation anchor, CDL-V3 diversity dependency clause, CDL-039 non-inferrability clause, CDL-042 defer note | ratified_phase: 394 | ratified_date: 2026-03-10 | evidence_document: docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md |
| CDL-043 | SIM-003 / CDL-V2 / CDL-V3 | Storage economics, graph pruning policy, and active-graph retention constraints | open | fixed-threshold pruning with static retention, adaptive pruning with bounded retention windows | adaptive pruning with bounded retention windows (proposed) | SIM-003 calibration anchor, non-centralization constraint clause, CDL-042 defer note |
| CDL-044 | CDL-039 / SIM-003 / Phase-391 Handoff 391 v0.1 | retention_epochs operational amendment for CDL-039 deployment boundary | open | retain deferred obligation without amendment row, open dedicated amendment row with bounded-range prelock, open dedicated amendment row with fixed constant prelock | open dedicated amendment row with bounded-range prelock (proposed) | Phase-379 retention obligation token, SIM-003 retention calibration anchor, Phase-391 handoff carry-forward token |

## Scoped Ratification Record (Phase 993)

The following decision IDs were ratified in the Phase 993 governance conflict-set closure:

- `CDL-003`: selected `trigger-based sunset`
- `CDL-004`: selected `hard caps + public reporting`
- `CDL-005`: selected `cap+trajectory+guardrails`
- `CDL-006`: selected `multi-body checks`
- `CDL-008`: selected `split-by-domain`
- `CDL-009`: selected `signature-badge+eligibility rules`
- `CDL-010`: selected `pseudonymous attestations`

Conflict-cluster mapping and rationale record:
- `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`

## Scoped Ratification Record (Phase 215)

The following decision IDs were ratified in the Phase 215 node-value/governance ratification evidence closure:

- `CDL-011`: selected `balanced composite`
- `CDL-012`: selected `usage+freshness`
- `CDL-013`: selected `decay-non-genesis-only`
- `CDL-014`: selected `counterfactual path-lift`
- `CDL-015`: selected `strict phase gate`

Ratification evidence package:
- `docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md`

## Scoped Ratification Record (Phase 253)

The following decision ID was ratified in the Phase 253 CDL-032 CLI-first SDK ratification:

- `CDL-032`: selected `CLI-first` (single CLI entry point)

Ratification evidence package:
- `docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md`

D2e-01 CLI command surface lock:
- `docs/specs/ilc_cli_command_surface_lock_253_v0.1.md`

Ceremony protocol reference:
- `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md` §6

---

## Scoped Ratification Record (Phase 251)

The following decision IDs were ratified in the Phase 251 security CDL batch ratification:

- `CDL-001`: selected `lineage+timelock`
- `CDL-002`: selected `revoke+grace period`
- `CDL-007`: selected `seq+hash+signed checkpoints`

Ratification evidence package:
- `docs/specs/ilc_security_cdl_ratification_evidence_251_v0.1.md`

Ceremony protocol reference:
- `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md` §6

---

## Scoped Remediation Record (Phase 227)

The following decision IDs remain `open` and received bounded remediation-contract notes in Phase 227:

- `CDL-001`: remediation scope lock published in `docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`
- `CDL-002`: remediation scope lock published in `docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md`
- `CDL-007`: remediation scope lock published in `docs/specs/ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md`

Phase-227 package record:
- `docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md`

Status mutation rule for this scoped record:
- No Phase-227 status promotion is applied; `CDL-001`, `CDL-002`, and `CDL-007` remain `open` until a later ratification phase proves closure criteria.

## Scoped Queue Entry Record (Phase 230 Preparation)

- `CDL-019` created from Phase-229 carry-forward debt.
- status: `open`
- description: "Multiplier-governance surface: resolve relationship between flat Genesis constant (1.2x), refutation-profitability invariant floor, and eventual dynamic ranking-based multiplier mechanism"
- action: `decision_log`
- phase identified: `229`

## Scoped Queue Entry Record (Phase 233 Preparation)

The following decision IDs were created from Phase-233 issuance-governance planning. All entries are `open` placeholders; no parameter ratification was performed in Phase 233.

| CDL ID | Topic | Phase identified |
| --- | --- | --- |
| CDL-025 | Terminal issuance model (hard cap vs. tail emission reconciliation) | 233 |
| CDL-026 | `C_max` total supply cap lock | 233 |
| CDL-027 | Decay formulation (`H` or `lambda`) and schedule constants | 233 |
| CDL-028 | Fee-burn split ratio | 233 |
| CDL-029 | Allocation split (performer/auditor/genesis) validation and lock | 233 |
| CDL-030 | ECU price clamp bounds (`P_min`, `P_max`) | 233 |
| CDL-031 | Dynamic ranking-based multiplier policy (if admitted after CDL-019 closure) | 233 |

Status mutation rule for this scoped record:
- No Phase-233 status promotion is applied; CDL-025 through CDL-031 remain `open` until ratification criteria are met.
- Dependency ordering is governed by the Phase-233 planning artifact: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`.
- CDL-020 through CDL-024 were formalized in Phase 237 using roadmap v0.3 routing labels.

## Scoped Formalization Record (Phase 237 Integration Alignment)

The following decision IDs were formalized from existing roadmap-routing labels during Phase 237 integration coherence work. All entries are `open` placeholders and were not ratified in this phase.

| CDL ID | Topic | Source |
| --- | --- | --- |
| CDL-020 | Protocol-native bundle schema and complete type system | `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md` |
| CDL-021 | Rust kernel port and WASM distribution | `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md` |
| CDL-022 | Genesis state bundle specification and signing ceremony | `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md` |
| CDL-023 | Epoch snapshot mechanism and fast-bootstrap protocol | `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md` |
| CDL-024 | Wire protocol specification and transport bindings | `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md` |

## Scoped Queue Entry Record (Phase 233 Post-Work — OpenClaw/SDK)

The following decision IDs were created from the OpenClaw architecture analysis (`ilc_openclaw_findings_integration_plan_v0.3.md`). Committed to repo as Phase-233 post-work housekeeping. All entries are `open` placeholders.

| CDL ID | Topic | Phase identified |
| --- | --- | --- |
| CDL-032 | CLI-first Agent SDK interface contract and command surface (ADM-002) | 233 post-work |
| CDL-033 | OpenClaw skill specification and ClawHub publication contract | 233 post-work |

Status mutation rule for this scoped record:
- CDL-032 requires D2e roadmap phase and ADM-002 ratification before closure is eligible.
- CDL-033 requires CDL-032 closure (working CLI, D2e-03) before closure is eligible.
- Neither CDL-032 nor CDL-033 disrupts the 230-239 sequence lock.
- Source documents: `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md`, `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.1.md`.

## Conflict Notes

- Historical sources include both high-level ideals and implementation-era tactical discussion. Tactical excerpts are not automatically constitutional.
- Clauses move to ratified state only when represented as explicit normative language and tied to concrete implementation or governance controls.

## Promotion Rule

A decision may be marked `ratified` only when:

1. It has source citations, and
2. It has a chosen option with rationale, and
3. It has concrete implementation impact listed, and
4. It has at least one verification artifact (test/spec check).
