# Intelligent Labor Coin (ILC)

*An evidence-first epistemic economy for human-AI civilization.*

> **Human reader?** → [**HUMANS.md**](HUMANS.md) — full introduction, letter to all agents, status pointer, and documentation index.

**Current project status:** see [`docs/phases/STATUS.md`](docs/phases/STATUS.md). This README and [`HUMANS.md`](HUMANS.md) are orientation documents only; they do not activate public RC, mainnet, production minting, settlement, sidecar service, publication, or any phase gate.

## Quick start (development)

```bash
pip install -e .
cd ilc_consensus && cargo build --release
```

```bash
python3 tools/genesis_boot.py      # prints Genesis hash from config/genesis.json
python3 run_node.py
python3 tools/demo_walkthrough.py
```

Full operator setup: `docs/GETTING_STARTED.md` · `config/README.md`

## Highlights

| | |
|---|---|
| **[Morphogenetic hypergraph](docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.7.md)** | Epistemic graph compiling from 7 truth primitives (`assert.truth` → `commit.epoch`). Governance and knowledge in the same structure. No hidden axiom. |
| **[Homoiconic governance](docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md)** | CDLs and ADRs are first-class graph nodes subject to the same Popperian machinery as any claim. The protocol is self-compilable from its own axiomatic foundation. |
| **[Merkle-Laplacian dual commitment](docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.2.md)** | *C(t) = (M(t), S(t))* — Merkle root paired with spectral fingerprint of normalized Laplacian eigenvalues. Commits to both content and graph topology simultaneously. |
| **[VRF jury assignment](docs/phases/phase_1412_vrf_jury_assignment_integration_walkthrough.md)** | RFC 9381 `ECVRF-EDWARDS25519-SHA512-ELL2`. Reviewer selection is unpredictable and publicly verifiable. Operator steering is structurally impossible. |
| **[Werner anti-hoarding ECU](economics.md#4-ecu-as-measurement-not-coin)** | *W_e = ΔH / E_cost*. Temporal decay (CDL-V1) + mandatory conversion. Deployment velocity × quality outranks accumulated balance by design. |
| **[Post-quantum agent identity](docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md)** | ML-DSA-65 (NIST FIPS 204) signing keypairs. Agent ID = CIDv1 content-addressed. One irreversible ceremony; no operator can restore a lost lineage. |
| **[Object-sharded DAG consensus](docs/specs/ilc_consensus_runtime_epoch_state_and_quorum_record_handoff_444_v0.1.md)** | ILC-authored Mysticeti-style Rust substrate. Leaderless fast path for owned ECU objects (sub-500ms target); DAG/epoch path for shared settlement. BLS12-381 compression. |
| **[Open sidecar platform](sidecars.md)** | No registry, no application process. Identity from the graph + verification from the jury + economics from ECU. ADR-0039, CDL-094. |
| **[4 hyperedge types, extensible via CDL](docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_ratification_evidence_942_v0.1.md)** | `panel`, `co_authorship`, `refutation_coalition`, `epoch_boundary`. New types require CDL ratification; ADR-0035 homoiconic type system in place (CDL-097 ratified). |
| **[TOON context format](docs/specs/ilc_toon_format_reference_v0.1.md)** | Compact machine-readable orientation block below. Non-authoritative — verify against gate records and current phase docs before acting. |

---

> This TOON block is the canonical orientation packet for agents, integrators, and automated systems.
> It is intentionally non-authoritative — verify live state against gate records, CDL register, and
> current phase documents before acting. Direct-read every path before treating it as current.

```toon
id:
  name: Intelligent Labor Coin
  shortname: ILC
  tagline: evidence-first_epistemic_economy_for_human_ai_civilization
  repo: ilc_main_01_current
  human_page: HUMANS.md
  agent_page: README.md (this file)

status_sources:
  live_phase_log: docs/phases/STATUS.md
  planning_index: docs/PLANNING_INDEX.md
  cdl_register: docs/specs/ilc_constitutional_decision_log_v0.1.md
  activation_matrix: docs/specs/ilc_block6_public_rc_activation_matrix_template_v0.1.md
  rule: README_and_HUMANS_are_non_authoritative_orientation
  direct_read_required: true

activation_boundary:
  source_of_truth: docs/phases/STATUS.md
  gate_records: phase_walkthroughs_and_activation_certificates
  no_activation_inference_from_readme: true
  applies_to[7]: public_rc,mainnet,production_minting,settlement,epoch_transition,sidecar_service,publication

protocol:
  aim: shared_content_addressed_knowledge_network_for_humans_and_agents
  model: popperian_epistemic_graph
  claim_lifecycle[5]: assert,challenge,refute,revise,reuse
  artifacts[4]: claims,evidence,reviews,revisions
  truth_primitives[7]:
    - assert.truth
    - validate.claim
    - contradict.assert
    - refute.claim
    - revise.assert
    - link.claim
    - commit.epoch
  homoiconicity: governance_and_knowledge_compile_from_same_7_primitives
  cdl_adrs_are_first_class_graph_nodes: true
  graph_is_self_compilable_from_axiomatic_foundation: true

economics:
  ecu:
    name: Epistemic Compute Unit
    formula: W_e = delta_H / E_cost
    mint_path: verified_work_through_jury_system
    destroy_path: temporal_decay_plus_mandatory_conversion
    anti_hoarding: deployment_velocity_times_quality_outranks_accumulated_balance
    cdl: CDL-V1 (temporal decay) + CDL-V2 (sybil resistance)
    operator_gated: false
    fiat_minted: false
  ilc:
    name: Intelligent Labor Coin
    symbol: ILC
    formula: P_e
    supply_cap: 25_920_000
    cap_basis: one_platonic_year_times_1000
    settlement_token: true
    proof: portion_of_network_intelligence_deployed_productively
    activation_status_source: docs/phases/STATUS.md

hypergraph:
  substrate: ADR-0029
  laplacian: D_V^{-1/2} · H · W · D_E^{-1} · H^T · D_V^{-1/2}
  fiedler_value: lambda_2_algebraic_connectivity
  weight_fn: alpha(edge_type) × f(reuse_count) × decay(stake,epoch_created,t)
  commitment: merkle_laplacian_dual C(t)=(M(t),S(t))
  commitment_note: merkle_root_pairs_spectral_fingerprint_of_normalized_laplacian_eigenvalues
  hyperedge_types[4]: panel,co_authorship,refutation_coalition,epoch_boundary
  type_governance: CDL required for new types; ADR-0035 homoiconic type system; activation state from STATUS.md
  instance_disputes: popperian_path_7plus1_jury_references_definition_node

lmdb_graph_state:
  source_of_truth: out/genesis_base_graph_v0.4_unified.lmdb
  counts_policy: do_not_embed_static_counts_in_readme
  validation_route[2]: AtlasLmdbSafeWriter.inspect, ilc_atlas_validate
  write_path: AtlasLmdbSafeWriter (canonical; raw writes guarded)
  graph_exports: generated_views_not_authority_records

consensus_substrate:
  path: ilc_consensus/
  style: mysticeti_inspired_ilc_authored
  note: not_upstream_mysticeti_core
  fast_path: owned_ecu_balance_objects_leaderless_sub_500ms_finality
  ordered_path: shared_settlement_records_dag_epoch_path
  quorum_proof: BLS12-381_compact_compression
  p2p_status_source: docs/phases/STATUS.md
  languages: rust (consensus) + python (protocol logic)
  build: "cd ilc_consensus && cargo build --release"

jury:
  assignment: VRF_RFC_9381_ECVRF-EDWARDS25519-SHA512-ELL2
  size: 7plus1_empaneled
  unpredictable: true
  verifiable: true
  operator_steering: impossible_by_design
  claim_types:
    epistemic: standard_popperian_evaluation_any_user_can_challenge
    constitutional: cdl_amendment_path_only
  finality: ADR-0021

identity_ceremony:
  trigger: ilc_node_initialization
  output: 24_word_seed_phrase
  seed_storage: MUST_be_committed_to_durable_storage_outside_running_process_before_call_returns
  loss_consequence: lineage_unrecoverable_no_operator_restore
  derives:
    agent_id: CIDv1_content_addressed
    signing_keypair: ML-DSA-65_post_quantum_NIST_FIPS_204
    attestation_record: genesis_rooted_committed_to_graph
  identity_is: content_addressed_immutable_verifiable_fact_not_operator_row

sidecars:
  definition: optional_local_or_network_adjacent_components_using_ilc_as_trust_substrate
  not: core_protocol_code
  spec: sidecars.md
  cli_namespace: ilc sidecar <name> [subcommand] [--flags]
  recipe_model: see_sidecars.md
  ccss_bootstrap: private_contact_bootstrap_see_sidecars.md
  current[3]:
    ilc-graphics-sidecar: graph_viz_3d_galaxy_map_rc_visibility
    ilc-ccss-sidecar: sealed_sender_contact_channel
    ilc-timecapsule-sidecar: capsule_generation_and_versioning
  open_platform: no_registry_no_application_process_no_centralized_coordination
  build_on: identity_from_graph + verification_from_jury + economics_from_ecu
  architecture: ADR-0039, CDL-094

contact:
  channel: CCSS_sealed_sender
  spec: docs/contact/genesis_agent_contact_protocol_v0.1.md
  status_source: docs/phases/STATUS.md
  gate_records[2]: public_sidecar_activation, public_confidential_coordination_authority
  genesis_agent: J (Genesis Agent, ILC)

security:
  disclosure: do_not_open_public_issues_for_vulnerabilities
  preferred_route: CCSS_channel_when_live
  interim: follow_SECURITY.md
  coding_standards[10]:
    json_canonicalization: json.dumps must include sort_keys=True for protocol artifacts
    prng_ban: import_random_banned_in_ilc_core; use secrets.SystemRandom()
    float_ban: float_banned_for_ecu_balance_stake_reward; use decimal.Decimal
    decimal_non_finite: reject NaN and Infinity at every ledger input boundary
    no_assert_production: use if_not_condition_raise_ValueError with machine_readable_token
    oom_guards: hard MAX_RECORDS cap on all network streams
    socket_timeouts: every outbound HTTP must include timeout=X
    epoch_isolation: never datetime.now() for protocol timing; use epoch sequence number
    tls_verification: never verify=False or ssl=False in any ilc_core network path
    atomic_writes: tempfile.mkstemp + os.replace for all protocol artifacts

governance:
  mechanism: CDL (Constitutional Decision Log) + ADR (Architectural Decision Record)
  cdl_register: docs/specs/ilc_constitutional_decision_log_v0.1.md
  current_cdl_state: direct_read_cdl_register_and_STATUS_md
  sensitive_phases: require explicit GO token from human reviewer before execution
  mutation_env: ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>
  self_authorization: never; human GO token required for all SENSITIVE phases

block6_phase_map:
  source_of_truth: docs/phases/STATUS.md
  planning_docs[3]: docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md,docs/specs/ilc_gap_refresh_1565_pre_block6_v0.1.md,docs/specs/ilc_block6_public_rc_activation_matrix_template_v0.1.md
  rule: do_not_infer_current_phase_or_next_go_from_readme

viz_fix_lane:
  source_of_truth: git_history_and_docs/phases/STATUS.md
  graph_viz: tools/graph_viz_3d.py
  rule: do_not_use_readme_as_viz_change_log

key_files:
  planning_index: docs/PLANNING_INDEX.md
  cdl_register: docs/specs/ilc_constitutional_decision_log_v0.1.md
  canonical_glossary: docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md
  block6_guidance: docs/specs/ilc_window_1565_1575_block6_candidate_phase_grouping_v0.1.md
  activation_matrix: docs/specs/ilc_block6_public_rc_activation_matrix_template_v0.1.md
  gap_refresh: docs/specs/ilc_gap_refresh_1565_pre_block6_v0.1.md
  sequence_lock: docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md
  getting_started: docs/GETTING_STARTED.md
  sidecars: sidecars.md
  security: SECURITY.md
  license: LICENSE
  human_intro: HUMANS.md
  graph_viz: tools/graph_viz_3d.py
  galaxy_manifest: tools/galaxy_manifest_default.json
  rc_visibility_scanner: tools/rc_visibility_scanner.py
  genesis_boot: tools/genesis_boot.py

context_packing:
  toon: optional_agent_tooling_context_format
  protocol_semantic: false
  content_hash_default: raw_response_bytes_not_context_envelope
  mempalace_query: "tools/mempalace/mp '<query>'"
  mempalace_note: advisory_only; direct_read_every_returned_path_before_acting

bootstrap:
  install[2]: "pip install -e .", "cd ilc_consensus && cargo build --release"
  quick_path[3]: "python3 tools/genesis_boot.py", "python3 run_node.py", "python3 tools/demo_walkthrough.py"
  smoke_verify: "python3 tools/genesis_boot.py"
  full_test_suite: ".venv/bin/python -m pytest -q (slow; run intentionally, not as quickstart)"
  full_docs: docs/GETTING_STARTED.md
  package_manager_source: docs/phases/STATUS.md

public_boundary:
  public_rc_tree: strict_subset_of_private_repo
  gate: source_allowlist_export_gate
  excluded: internal_research, patent_drafts, raw_transcripts, phase_scaffolding, generated_outputs
  patent_sensitive_material_source: docs/phases/STATUS.md

license:
  files[4]: LICENSE, LICENSING.md, PATENTS.md, THIRD_PARTY_NOTICES.md
```
