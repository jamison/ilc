# Fiedler Minority Cluster — Manual Audit Ledger v0.2

**Source:** `out/atlas_research/fiedler_minority_cluster_fix53_v0.1.json`
**Candidate:** Fix53 (`genesis_atlas_enriched_candidate_fix53.json`)
**Total nodes:** 194 (51 pre-filled private, **143 require manual audit**)
**Phase:** phase_1545p_fix53

## Graph boundary note

The Fix53 research candidate is a unified graph containing both private
and public-eligible nodes. Private material nodes (`node_kind: genesis_private_material_node`)
are intentionally weakly connected — they have no protocol semantic relationships
and must never appear in the public authority projection. Their presence in the
Fiedler minority cluster is correct behaviour, not a repair target.

**51 nodes are pre-filled as `excluded_from_public_projection`** — no audit needed.
**143 nodes are public-eligible repo_material_node / repo_group_node / etc.** — these are the real audit targets.

For public-eligible nodes, the audit assigns:
- `add_edge` — add a semantic edge to wire this node into the main cluster
- `support_only` — intentionally isolated; no edge needed (local tooling, configs with no protocol relationship)
- `defer` — needs deeper review; skip for now

## Audit column definitions

| Column | Meaning |
|--------|---------|
| `node_id` | Candidate node identifier |
| `path` | Decoded file path (for repo:file nodes) |
| `current_edges` | Existing edge types and sources/targets |
| `recommended_edge_type` | Reviewer-assigned edge type to add |
| `recommended_target` | Target node in main cluster |
| `disposition` | `add_edge` / `support_only` / `excluded_from_public_projection` / `defer` |
| `notes` | Free-form reviewer annotation |

---

## Category: Non-repo nodes (invariant/phase terminal) (2 nodes)

### Batch 001 — Non-repo nodes (invariant/phase terminal) [1–2 of 2]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 1 | `invariant:package_hygiene_root_archive_manifest_and_chat_corpus_policy` | `...hygiene_root_archive_manifest_and_chat_corpus_policy` | REGRESSES←repo |  |  |  |  |
| 2 | `phase:1005_package_hygiene_root_archive_surfaces` | `phase:1005_package_hygiene_root_archive_surfaces` | REFERENCES_AUTHORITY←repo |  |  |  |  |

---

## Category: Private material — pre-filled as support_only (no audit needed) (51 nodes)

### Batch 002 — Private material — pre-filled as support_only (no audit needed) [1–10 of 51]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 3 | `repo:file:06297c2b0478d07c:z_past_chats_2025_06_12_ilc_ilc_mining_and_hardware_txt` | `z/past/chats/2025/06/12/ilc/ilc/mining/and/hardware/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 4 | `repo:file:07c82e1ac73f3e76:z_past_chats_2025_06_18_ilc_4d_cognitive_ai_model_txt` | `z/past/chats/2025/06/18/ilc/4d/cognitive/ai/model/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 5 | `repo:file:15a960ddec72d441:z_past_chats_2026_01_06_ilc_ilc_project_status_update_txt` | `...t/chats/2026/01/06/ilc/ilc/project/status/update/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 6 | `repo:file:1ae9e699eeb3fd10:z_past_chats_2025_10_13_ilc_wolfram_evolution_correction_txt` | `...hats/2025/10/13/ilc/wolfram/evolution/correction/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 7 | `repo:file:1e7fb94a0cedd3c0:z_past_chats_20260121_ilc_ilc_project_phase_review_txt` | `z/past/chats/20260121/ilc/ilc/project/phase/review/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 8 | `repo:file:1f626d109e17c86c:z_past_chats_2025_10_11_ilc_public_visibility_in_ilc_txt` | `...st/chats/2025/10/11/ilc/public/visibility/in/ilc/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 9 | `repo:file:206102594272cc3a:z_past_chats_2025_11_12_ilc_ilc_latest_main_thread_oct25_txt` | `...hats/2025/11/12/ilc/ilc/latest/main/thread/oct25/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 10 | `repo:file:231130606664ed71:z_past_chats_2025_07_23_ilc_how_can_i_help_txt` | `z/past/chats/2025/07/23/ilc/how/can/i/help/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 11 | `repo:file:33c0b2be4ed21439:z_past_chats_2025_10_17_ilc_time_to_deployment_estimate_txt` | `...chats/2025/10/17/ilc/time/to/deployment/estimate/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 12 | `repo:file:35d4555e107f9312:z_past_chats_20251209_list_of_simulations_and_tests_and_what_might_be_pending_docx` | `...simulations/and/tests/and/what/might/be/pending/docx` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |

### Batch 003 — Private material — pre-filled as support_only (no audit needed) [11–20 of 51]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 13 | `repo:file:399b855ee9262fc6:z_past_chats_2025_12_01_ilc_energy_aware_task_routing_txt` | `...t/chats/2025/12/01/ilc/energy/aware/task/routing/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 14 | `repo:file:3b4947cb41ea7621:z_past_chats_25_12_03_updated_roadmap_33_70_with_levin_infused_43_48_docx` | `.../updated/roadmap/33/70/with/levin/infused/43/48/docx` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 15 | `repo:file:3e6b3c857437f264:z_past_chats_2025_10_18_ilc_upload_transcript_ilc_analysis_txt` | `...ts/2025/10/18/ilc/upload/transcript/ilc/analysis/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 16 | `repo:file:3ee5b6678eec8b2e:z_past_chats_2025_12_03_updated_roadmap_33_70_with_levin_infused_43_48_docx` | `.../updated/roadmap/33/70/with/levin/infused/43/48/docx` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 17 | `repo:file:4a083bdc59fe176a:z_past_chats_2025_06_19_ilc_cellular_automata_primer_txt` | `...st/chats/2025/06/19/ilc/cellular/automata/primer/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 18 | `repo:file:4af5ee1f98a11b22:z_past_chats_2025_12_03_ilc_ilc_project_insights_from_michael_levin_txt` | `...2/03/ilc/ilc/project/insights/from/michael/levin/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 19 | `repo:file:4b864eaf98c79667:z_past_chats_2025_07_28_ilc_signature_identification_help_txt` | `...ats/2025/07/28/ilc/signature/identification/help/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 20 | `repo:file:51efc7a5cc64a652:z_past_chats_2025_06_05_ilc_ai_job_impact_and_advancement_txt` | `...ats/2025/06/05/ilc/ai/job/impact/and/advancement/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 21 | `repo:file:54fc0d128c195ce4:z_past_chats_2025_05_18_ilc_podcast_main_participants_ages_txt` | `...ts/2025/05/18/ilc/podcast/main/participants/ages/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 22 | `repo:file:5570274ace619b75:z_past_chats_2025_12_01_ilc_q_a_regarding_local_influence_and_other_future_governance_nodes_being_on_graph_and_ajustable_docx` | `...e/governance/nodes/being/on/graph/and/ajustable/docx` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |

### Batch 004 — Private material — pre-filled as support_only (no audit needed) [21–30 of 51]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 23 | `repo:file:572a217104f878a9:z_past_chats_2025_09_06_ilc_positive_geometry_theory_txt` | `...st/chats/2025/09/06/ilc/positive/geometry/theory/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 24 | `repo:file:5aa3471cdc0b76ea:z_past_chats_old_2025_12_02_ilc_ilc_project_insights_from_michael_levin_md` | `...12/02/ilc/ilc/project/insights/from/michael/levin/md` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 25 | `repo:file:5b3e01a90862548a:z_past_chats_old_2025_12_25_ilc_ilc_project_status_update_txt` | `...ats/old/2025/12/25/ilc/ilc/project/status/update/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 26 | `repo:file:602f7d33875bdf32:z_past_chats_20260114_ilc_artifact_format_optimization_ilc_txt` | `...ts/20260114/ilc/artifact/format/optimization/ilc/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 27 | `repo:file:63a33196be13f619:z_past_chats_2025_06_05_ilc_whitepaper_section_2_draft_txt` | `.../chats/2025/06/05/ilc/whitepaper/section/2/draft/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 28 | `repo:file:69bfda580d33ace8:z_past_chats_2026_02_03_ilc_codex_antigravity_task_conversations_txt` | `...6/02/03/ilc/codex/antigravity/task/conversations/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 29 | `repo:file:6eeff2a1dc6f4f80:z_past_chats_20260128_ilc_deepseek_ngram_vs_ilc_txt` | `z/past/chats/20260128/ilc/deepseek/ngram/vs/ilc/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 30 | `repo:file:73b3c758b73f80bd:z_past_chats_2025_04_25_ilc_roman_gymnasiums_and_affluence_txt` | `...ts/2025/04/25/ilc/roman/gymnasiums/and/affluence/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 31 | `repo:file:7532b279d74031fc:z_past_chats_2025_10_14_ilc_video_analysis_options_txt` | `z/past/chats/2025/10/14/ilc/video/analysis/options/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 32 | `repo:file:77291b64db2f3a03:z_past_chats_2025_06_12_ilc_iq_predicci_n_y_reflexi_n_txt` | `...t/chats/2025/06/12/ilc/iq/predicci/n/y/reflexi/n/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |

### Batch 005 — Private material — pre-filled as support_only (no audit needed) [31–40 of 51]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 33 | `repo:file:79fc462389c3c73d:z_past_chats_2025_09_28_ilc_podcast_analysis_breakdown_txt` | `.../chats/2025/09/28/ilc/podcast/analysis/breakdown/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 34 | `repo:file:868216fe5d73fdaf:z_past_chats_2025_08_26_ilc_august_2025_ilc_convo_audit_txt` | `...chats/2025/08/26/ilc/august/2025/ilc/convo/audit/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 35 | `repo:file:8f88ef5f87937474:z_past_chats_2025_04_26_ilc_gdp_equation_explanation_txt` | `...st/chats/2025/04/26/ilc/gdp/equation/explanation/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 36 | `repo:file:9463bf35422fc8d8:z_past_chats_2025_06_03_ilc_higher_dimensional_geometry_in_ds_txt` | `...2025/06/03/ilc/higher/dimensional/geometry/in/ds/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 37 | `repo:file:95c0f69ed0ed0d6b:z_past_chats_2025_06_26_ilc_ilc_design_convo_2_txt` | `z/past/chats/2025/06/26/ilc/ilc/design/convo/2/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 38 | `repo:file:a6bb301229c5420d:z_past_chats_2025_08_14_ilc_article_review_and_insights_txt` | `...chats/2025/08/14/ilc/article/review/and/insights/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 39 | `repo:file:a9fe9e4f4d44520f:z_past_chats_old_2025_12_07_ilc_ilc_project_status_update_txt` | `...ats/old/2025/12/07/ilc/ilc/project/status/update/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 40 | `repo:file:b9dcdc9546348e87:z_past_chats_2025_11_16_ilc_rl_scaling_and_ilc_dwarkesh_patel_video_sigmoid_rl_training_txt` | `...and/ilc/dwarkesh/patel/video/sigmoid/rl/training/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 41 | `repo:file:bf738e7656e1274d:z_past_chats_2025_05_19_ilc_ai_agent_marketplace_names_txt` | `.../chats/2025/05/19/ilc/ai/agent/marketplace/names/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 42 | `repo:file:c198327cc15f729d:z_past_chats_2025_10_14_2_ilc_code_interpreter_session_expired_txt` | `...025/10/14/2/ilc/code/interpreter/session/expired/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |

### Batch 006 — Private material — pre-filled as support_only (no audit needed) [41–50 of 51]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 43 | `repo:file:ccde7c6a64d19ef9:z_past_chats_2025_10_15_ilc_employee_information_privacy_txt` | `...hats/2025/10/15/ilc/employee/information/privacy/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 44 | `repo:file:cf7cbe97b667e985:z_past_chats_2025_06_02_ilc_bitcoin_energy_and_coin_value_txt` | `...ats/2025/06/02/ilc/bitcoin/energy/and/coin/value/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 45 | `repo:file:d5f1233ae5a3ea06:z_past_chats_2025_12_01_ilc_great_architectural_summary_of_all_phases_33_70_plus_on_chain_and_off_chain_architecture_description_docx` | `...on/chain/and/off/chain/architecture/description/docx` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 46 | `repo:file:e5fffee48ca5992e:z_past_chats_20251208_main_planning_outline_ilc_genesis_post_mvp_docx` | `...1208/main/planning/outline/ilc/genesis/post/mvp/docx` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 47 | `repo:file:ea79f6e534543974:z_past_chats_2025_10_28_ilc_greeting_exchange_txt` | `z/past/chats/2025/10/28/ilc/greeting/exchange/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 48 | `repo:file:eed657eac62f2dde:z_past_chats_2025_09_25_ilc_identify_last_conversation_thread_txt` | `...2025/09/25/ilc/identify/last/conversation/thread/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 49 | `repo:file:f46c09cc806ff00c:z_past_chats_20260128_ilc_syllabic_name_generation_txt` | `z/past/chats/20260128/ilc/syllabic/name/generation/txt` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 50 | `repo:file:fd5110b93101ecbd:todo_docs_post_mvp_2025_12_03_todos_phase_45_and_phase_46_post_mvp_docx` | `...2025/12/03/todos/phase/45/and/phase/46/post/mvp/docx` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 51 | `repo:file:37467897ef8fb9b3:docs_architecture_ilc_harness_architecture_spec_1459p_v0_1_md` | `...itecture/ilc/harness/architecture/spec/1459p/v0/1/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |
| 52 | `repo:file:5336907dff0d62fa:docs_architecture_ilc_core_vs_agentic_harness_boundary_v0_1_md` | `...tecture/ilc/core/vs/agentic/harness/boundary/v0/1/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |

### Batch 007 — Private material — pre-filled as support_only (no audit needed) [51–51 of 51]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 53 | `repo:file:fa6d6b1801eb0a01:docs_phases_public_rc_patent_license_split_preflight_walkthrough_2026_06_03_md` | `...nt/license/split/preflight/walkthrough/2026/06/03/md` | CONTAINS_FILE←repo | — | — | excluded_from_public_projection | genesis_private_material_node — no public graph edge |

---

## Category: config/mysticeti — TLS certificate files (19 nodes)

### Batch 008 — config/mysticeti — TLS certificate files [1–10 of 19]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 54 | `repo:file:10f0c45818e60216:config_mysticeti_testnet_multiop_1360_certs_validator_2_consensus_key_hex` | `...net/multiop/1360/certs/validator/2/consensus/key/hex` | CONTAINS_FILE←repo |  |  |  |  |
| 55 | `repo:file:1c15917d90a04057:config_mysticeti_testnet_multiop_1360_certs_validator_1_cert_der` | `...ceti/testnet/multiop/1360/certs/validator/1/cert/der` | CONTAINS_FILE←repo |  |  |  |  |
| 56 | `repo:file:1d639b05126939f6:config_mysticeti_testnet_multiop_1360_certs_validator_2_cert_der` | `...ceti/testnet/multiop/1360/certs/validator/2/cert/der` | CONTAINS_FILE←repo |  |  |  |  |
| 57 | `repo:file:21d7389e01ab431e:config_mysticeti_testnet_multiop_1360_certs_validator_1_cert_pem` | `...ceti/testnet/multiop/1360/certs/validator/1/cert/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 58 | `repo:file:259338027c5b68b2:config_mysticeti_testnet_multiop_1360_certs_validator_4_key_pem` | `...iceti/testnet/multiop/1360/certs/validator/4/key/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 59 | `repo:file:26848cbd2961f861:config_mysticeti_testnet_multiop_1360_certs_validator_4_consensus_key_hex` | `...net/multiop/1360/certs/validator/4/consensus/key/hex` | CONTAINS_FILE←repo |  |  |  |  |
| 60 | `repo:file:36609d4903f8f5e1:config_mysticeti_testnet_multiop_1360_certs_validator_3_cert_pem` | `...ceti/testnet/multiop/1360/certs/validator/3/cert/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 61 | `repo:file:4c55178cd6d034a2:config_mysticeti_testnet_multiop_1360_certs_validator_3_cert_der` | `...ceti/testnet/multiop/1360/certs/validator/3/cert/der` | CONTAINS_FILE←repo |  |  |  |  |
| 62 | `repo:file:4db90898ae2f513d:config_mysticeti_testnet_multiop_1360_certs_client_cert_der` | `...mysticeti/testnet/multiop/1360/certs/client/cert/der` | CONTAINS_FILE←repo |  |  |  |  |
| 63 | `repo:file:4f1049eab9346b1a:config_mysticeti_testnet_multiop_1360_certs_validator_4_cert_der` | `...ceti/testnet/multiop/1360/certs/validator/4/cert/der` | CONTAINS_FILE←repo |  |  |  |  |

### Batch 009 — config/mysticeti — TLS certificate files [11–19 of 19]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 64 | `repo:file:68332835e6ec1c8d:config_mysticeti_testnet_multiop_1360_certs_validator_2_cert_pem` | `...ceti/testnet/multiop/1360/certs/validator/2/cert/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 65 | `repo:file:831d0e6077576935:config_mysticeti_testnet_multiop_1360_certs_validator_4_cert_pem` | `...ceti/testnet/multiop/1360/certs/validator/4/cert/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 66 | `repo:file:b383b6528b58d18e:config_mysticeti_testnet_multiop_1360_certs_validator_1_key_pem` | `...iceti/testnet/multiop/1360/certs/validator/1/key/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 67 | `repo:file:c073414f4d7a10de:config_mysticeti_testnet_multiop_1360_certs_validator_3_key_pem` | `...iceti/testnet/multiop/1360/certs/validator/3/key/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 68 | `repo:file:dd1e7d7fd2b63ebf:config_mysticeti_testnet_multiop_1360_certs_validator_3_consensus_key_hex` | `...net/multiop/1360/certs/validator/3/consensus/key/hex` | CONTAINS_FILE←repo |  |  |  |  |
| 69 | `repo:file:e24b040e841dd339:config_mysticeti_testnet_multiop_1360_certs_client_cert_pem` | `...mysticeti/testnet/multiop/1360/certs/client/cert/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 70 | `repo:file:e97d58c5198a52cb:config_mysticeti_testnet_multiop_1360_certs_client_key_pem` | `.../mysticeti/testnet/multiop/1360/certs/client/key/pem` | CONTAINS_FILE←repo |  |  |  |  |
| 71 | `repo:file:f6f69213161f50af:config_mysticeti_testnet_multiop_1360_certs_validator_1_consensus_key_hex` | `...net/multiop/1360/certs/validator/1/consensus/key/hex` | CONTAINS_FILE←repo |  |  |  |  |
| 72 | `repo:file:ffd3e8efd849c193:config_mysticeti_testnet_multiop_1360_certs_validator_2_key_pem` | `...iceti/testnet/multiop/1360/certs/validator/2/key/pem` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: config/mysticeti — validator config JSON (8 nodes)

### Batch 010 — config/mysticeti — validator config JSON [1–8 of 8]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 73 | `repo:file:26df005ead2f6cda:config_mysticeti_testnet_multiop_1360_validator_1_config_json` | `...sticeti/testnet/multiop/1360/validator/1/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 74 | `repo:file:3147494df62b37a5:config_mysticeti_testnet_m009_validator_3_config_json` | `config/mysticeti/testnet/m009/validator/3/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 75 | `repo:file:5b181aeff21f5e4a:config_mysticeti_testnet_multiop_1360_validator_4_config_json` | `...sticeti/testnet/multiop/1360/validator/4/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 76 | `repo:file:98c9d200cae20732:config_mysticeti_testnet_multiop_1360_validator_2_config_json` | `...sticeti/testnet/multiop/1360/validator/2/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 77 | `repo:file:df8a29ae4709114e:config_mysticeti_testnet_m009_validator_4_config_json` | `config/mysticeti/testnet/m009/validator/4/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 78 | `repo:file:e8d561d129a2b67e:config_mysticeti_testnet_m009_validator_1_config_json` | `config/mysticeti/testnet/m009/validator/1/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 79 | `repo:file:f145cf35a1b4eea1:config_mysticeti_testnet_m009_validator_2_config_json` | `config/mysticeti/testnet/m009/validator/2/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 80 | `repo:file:f383179c7cdae2b4:config_mysticeti_testnet_multiop_1360_validator_3_config_json` | `...sticeti/testnet/multiop/1360/validator/3/config/json` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: testbed/ — node configs, bootstrap peers, env files (27 nodes)

### Batch 011 — testbed/ — node configs, bootstrap peers, env files [1–10 of 27]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 81 | `repo:file:01ba4719c80b6fe9:testbed_configs_gitkeep` | `testbed/configs/gitkeep` | CONTAINS_FILE←repo |  |  |  |  |
| 82 | `repo:file:33cb5032c1452acc:testbed_bootstrap_peers_json` | `testbed/bootstrap/peers/json` | CONTAINS_FILE←repo |  |  |  |  |
| 83 | `repo:file:577b816e932f532d:testbed_configs_ilc_node_5_ilc_node_v1_env` | `testbed/configs/ilc/node/5/ilc/node/v1/env` | CONTAINS_FILE←repo |  |  |  |  |
| 84 | `repo:file:57bfbcc41f39f9bf:testbed_configs_ilc_node_4_node_config_json` | `testbed/configs/ilc/node/4/node/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 85 | `repo:file:5f2164a6d9f95ffc:testbed_configs_ilc_node_6_node_config_json` | `testbed/configs/ilc/node/6/node/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 86 | `repo:file:65b16e935800ce8e:testbed_configs_ilc_node_3_node_config_json` | `testbed/configs/ilc/node/3/node/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 87 | `repo:file:68d53983f2300daf:testbed_configs_ilc_node_1_genesis_ref_json` | `testbed/configs/ilc/node/1/genesis/ref/json` | CONTAINS_FILE←repo |  |  |  |  |
| 88 | `repo:file:68d53983f2300daf:testbed_configs_ilc_node_2_genesis_ref_json` | `testbed/configs/ilc/node/2/genesis/ref/json` | CONTAINS_FILE←repo |  |  |  |  |
| 89 | `repo:file:68d53983f2300daf:testbed_configs_ilc_node_3_genesis_ref_json` | `testbed/configs/ilc/node/3/genesis/ref/json` | CONTAINS_FILE←repo |  |  |  |  |
| 90 | `repo:file:68d53983f2300daf:testbed_configs_ilc_node_4_genesis_ref_json` | `testbed/configs/ilc/node/4/genesis/ref/json` | CONTAINS_FILE←repo |  |  |  |  |

### Batch 012 — testbed/ — node configs, bootstrap peers, env files [11–20 of 27]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 91 | `repo:file:68d53983f2300daf:testbed_configs_ilc_node_5_genesis_ref_json` | `testbed/configs/ilc/node/5/genesis/ref/json` | CONTAINS_FILE←repo |  |  |  |  |
| 92 | `repo:file:68d53983f2300daf:testbed_configs_ilc_node_6_genesis_ref_json` | `testbed/configs/ilc/node/6/genesis/ref/json` | CONTAINS_FILE←repo |  |  |  |  |
| 93 | `repo:file:7f00d62425995547:testbed_configs_ilc_node_4_ilc_node_v1_env` | `testbed/configs/ilc/node/4/ilc/node/v1/env` | CONTAINS_FILE←repo |  |  |  |  |
| 94 | `repo:file:8b6c38dfb96bf78f:testbed_configs_ilc_node_1_node_config_json` | `testbed/configs/ilc/node/1/node/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 95 | `repo:file:a97221e832295848:testbed_configs_ilc_node_5_node_config_json` | `testbed/configs/ilc/node/5/node/config/json` | CONTAINS_FILE←repo |  |  |  |  |
| 96 | `repo:file:adeebdaa659493d0:testbed_configs_ilc_node_1_genesis_bundle_json` | `testbed/configs/ilc/node/1/genesis/bundle/json` | CONTAINS_FILE←repo |  |  |  |  |
| 97 | `repo:file:adeebdaa659493d0:testbed_configs_ilc_node_2_genesis_bundle_json` | `testbed/configs/ilc/node/2/genesis/bundle/json` | CONTAINS_FILE←repo |  |  |  |  |
| 98 | `repo:file:adeebdaa659493d0:testbed_configs_ilc_node_3_genesis_bundle_json` | `testbed/configs/ilc/node/3/genesis/bundle/json` | CONTAINS_FILE←repo |  |  |  |  |
| 99 | `repo:file:adeebdaa659493d0:testbed_configs_ilc_node_4_genesis_bundle_json` | `testbed/configs/ilc/node/4/genesis/bundle/json` | CONTAINS_FILE←repo |  |  |  |  |
| 100 | `repo:file:adeebdaa659493d0:testbed_configs_ilc_node_5_genesis_bundle_json` | `testbed/configs/ilc/node/5/genesis/bundle/json` | CONTAINS_FILE←repo |  |  |  |  |

### Batch 013 — testbed/ — node configs, bootstrap peers, env files [21–27 of 27]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 101 | `repo:file:adeebdaa659493d0:testbed_configs_ilc_node_6_genesis_bundle_json` | `testbed/configs/ilc/node/6/genesis/bundle/json` | CONTAINS_FILE←repo |  |  |  |  |
| 102 | `repo:file:b3084791d080d378:testbed_peer_candidates_ndjson` | `testbed/peer/candidates/ndjson` | CONTAINS_FILE←repo |  |  |  |  |
| 103 | `repo:file:c688b8c85489f824:testbed_configs_ilc_node_1_ilc_node_v1_env` | `testbed/configs/ilc/node/1/ilc/node/v1/env` | CONTAINS_FILE←repo |  |  |  |  |
| 104 | `repo:file:c688b8c85489f824:testbed_configs_ilc_node_2_ilc_node_v1_env` | `testbed/configs/ilc/node/2/ilc/node/v1/env` | CONTAINS_FILE←repo |  |  |  |  |
| 105 | `repo:file:c688b8c85489f824:testbed_configs_ilc_node_3_ilc_node_v1_env` | `testbed/configs/ilc/node/3/ilc/node/v1/env` | CONTAINS_FILE←repo |  |  |  |  |
| 106 | `repo:file:c688b8c85489f824:testbed_configs_ilc_node_6_ilc_node_v1_env` | `testbed/configs/ilc/node/6/ilc/node/v1/env` | CONTAINS_FILE←repo |  |  |  |  |
| 107 | `repo:file:cb24408b3279ae48:testbed_configs_ilc_node_2_node_config_json` | `testbed/configs/ilc/node/2/node/config/json` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: ilc_consensus/src — Rust source files (4 nodes)

### Batch 014 — ilc_consensus/src — Rust source files [1–4 of 4]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 108 | `repo:file:32964c082f1922bf:ilc_consensus_src_pq_keygen_main_rs` | `ilc/consensus/src/pq/keygen/main/rs` | CONTAINS_FILE←repo |  |  |  |  |
| 109 | `repo:file:3928e691386ce8f7:ilc_consensus_src_balance_store_rs` | `ilc/consensus/src/balance/store/rs` | CONTAINS_FILE←repo |  |  |  |  |
| 110 | `repo:file:a9ed7ab021e223af:ilc_consensus_src_keygen_main_rs` | `ilc/consensus/src/keygen/main/rs` | CONTAINS_FILE←repo |  |  |  |  |
| 111 | `repo:file:c77edf675ed6abf6:ilc_consensus_src_pq_sign_main_rs` | `ilc/consensus/src/pq/sign/main/rs` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: simulations/historical — recovered replay scripts (3 nodes)

### Batch 015 — simulations/historical — recovered replay scripts [1–3 of 3]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 112 | `repo:file:300900833cfe0d46:simulations_historical_recovered_replay_kappa_ab_20251009_py` | `...ons/historical/recovered/replay/kappa/ab/20251009/py` | CONTAINS_FILE←repo |  |  |  |  |
| 113 | `repo:file:5ee52bf305a05f61:simulations_historical_recovered_replay_a5_subjective_gating_20251009_py` | `...al/recovered/replay/a5/subjective/gating/20251009/py` | CONTAINS_FILE←repo |  |  |  |  |
| 114 | `repo:file:be64b2727a90aec0:simulations_historical_recovered_replay_controller_telemetry_80_epoch_20251009_py` | `...red/replay/controller/telemetry/80/epoch/20251009/py` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: simulations/ — other simulation files (2 nodes)

### Batch 016 — simulations/ — other simulation files [1–2 of 2]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 115 | `repo:file:a2a3eeabbb9cff72:simulations_paradigm_sensitivity_py` | `simulations/paradigm/sensitivity/py` | CONTAINS_FILE←repo |  |  |  |  |
| 116 | `repo:file:fa2b3d2c1212d650:simulations_run_sim_reuse_01_940_py` | `simulations/run/sim/reuse/01/940/py` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: config/hardware + config/governance — MVP configs (4 nodes)

### Batch 017 — config/hardware + config/governance — MVP configs [1–4 of 4]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 117 | `repo:file:6704a26924c916d2:config_hardware_archetypes_mvp_json` | `config/hardware/archetypes/mvp/json` | CONTAINS_FILE←repo |  |  |  |  |
| 118 | `repo:file:875d8c83291a57fb:config_hardware_archetypes_mvp_yaml` | `config/hardware/archetypes/mvp/yaml` | CONTAINS_FILE←repo |  |  |  |  |
| 119 | `repo:file:c30ce05d5f6a6ca6:config_governance_mvp_json` | `config/governance/mvp/json` | CONTAINS_FILE←repo |  |  |  |  |
| 120 | `repo:file:cd8d27a4315d4c4a:config_governance_mvp_yaml` | `config/governance/mvp/yaml` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: automation/ — launchd/watchdog plist templates (3 nodes)

### Batch 018 — automation/ — launchd/watchdog plist templates [1–3 of 3]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 121 | `repo:file:95e0ddd267e2ec69:automation_launchd_com_ilc_watch_review_markers_watchdog_plist_template` | `...com/ilc/watch/review/markers/watchdog/plist/template` | CONTAINS_FILE←repo |  |  |  |  |
| 122 | `repo:file:af76e56f3b827586:automation_launchd_com_ilc_watch_review_markers_plist_template` | `.../launchd/com/ilc/watch/review/markers/plist/template` | CONTAINS_FILE←repo |  |  |  |  |
| 123 | `repo:file:2524549ec6762ede:automation_readme_md` | `automation/readme/md` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: deploy/ — systemd/tor deployment configs (2 nodes)

### Batch 019 — deploy/ — systemd/tor deployment configs [1–2 of 2]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 124 | `repo:file:219365b782faf1af:deploy_systemd_ccss_relay_service` | `deploy/systemd/ccss/relay/service` | CONTAINS_FILE←repo |  |  |  |  |
| 125 | `repo:file:46707a9c3f267531:deploy_tor_torrc_template` | `deploy/tor/torrc/template` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: scripts/ — shell scripts (2 nodes)

### Batch 020 — scripts/ — shell scripts [1–2 of 2]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 126 | `repo:file:7741c66c44c7bac8:scripts_monitor_phases_sh` | `scripts/monitor/phases/sh` | CONTAINS_FILE←repo |  |  |  |  |
| 127 | `repo:file:a422412df2290779:scripts_automation_utils_py` | `scripts/automation/utils/py` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: whitepaper/ — governance/draft markdown (3 nodes)

### Batch 021 — whitepaper/ — governance/draft markdown [1–3 of 3]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 128 | `repo:file:5fa3cad643717e01:whitepaper_06_governance_md` | `whitepaper/06/governance/md` | CONTAINS_FILE←repo |  |  |  |  |
| 129 | `repo:file:b4b9986a68f8f199:whitepaper_07_roadmap_md` | `whitepaper/07/roadmap/md` | CONTAINS_FILE←repo |  |  |  |  |
| 130 | `repo:file:eb7c88765d984588:whitepaper_03_architecture_md` | `whitepaper/03/architecture/md` | CONTAINS_FILE←repo |  |  |  |  |

---

## Category: docs/ — old planning docs (pre-2026) (4 nodes)

### Batch 022 — docs/ — old planning docs (pre-2026) [1–4 of 4]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 131 | `repo:file:5a861542176bcdc7:docs_20251208_main_planning_outline_ilc_genesis_post_mvp_1_docx` | `...08/main/planning/outline/ilc/genesis/post/mvp/1/docx` | CONTAINS_FILE←repo |  |  |  |  |
| 132 | `repo:file:5ffc7adaf0770789:docs_claim_econ_mapping_mvp_md` | `docs/claim/econ/mapping/mvp/md` | CONTAINS_FILE←repo |  |  |  |  |
| 133 | `repo:group:docs_20251208_main_planning_outline_ilc_genesis_post_mvp_1_docx` | `...08_main_planning_outline_ilc_genesis_post_mvp_1_docx` | CONTAINS_GROUP←artifact |  |  |  |  |
| 134 | `repo:group:docs_claim_econ_mapping_mvp_md` | `repo:group:docs_claim_econ_mapping_mvp_md` | CONTAINS_GROUP←artifact |  |  |  |  |

---

## Category: dotfiles / agent/ / githooks — local tooling (11 nodes)

### Batch 023 — dotfiles / agent/ / githooks — local tooling [1–10 of 11]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 135 | `repo:file:0d7d92232faabbbb:ignore` | `ignore` | CONTAINS_FILE←repo |  |  |  |  |
| 136 | `repo:file:1a457cd09ddffce6:agent_rules_ilc_loop_guardrails_md` | `agent/rules/ilc/loop/guardrails/md` | CONTAINS_FILE←repo |  |  |  |  |
| 137 | `repo:file:2a433904a7c16986:agent_workflows_run_batch_loop_md` | `agent/workflows/run/batch/loop/md` | CONTAINS_FILE←repo |  |  |  |  |
| 138 | `repo:file:44c2984b223bbcf3:agent_workflows_run_phase_md` | `agent/workflows/run/phase/md` | CONTAINS_FILE←repo |  |  |  |  |
| 139 | `repo:file:69e06395fc54b60d:agent_workflows_run_batch_md` | `agent/workflows/run/batch/md` | CONTAINS_FILE←repo |  |  |  |  |
| 140 | `repo:file:6d52eb96b9bfe658:githooks_pre_commit` | `githooks/pre/commit` | CONTAINS_FILE←repo |  |  |  |  |
| 141 | `repo:file:819341982e3dd9e8:agent_workflows_codex_review_md` | `agent/workflows/codex/review/md` | CONTAINS_FILE←repo |  |  |  |  |
| 142 | `repo:file:f68044b8a8bf4262:agent_workflows_run_next_phase_md` | `agent/workflows/run/next/phase/md` | CONTAINS_FILE←repo |  |  |  |  |
| 143 | `repo:file:e26d4be797b880bd:agent_workflows_run_next_phase_v2_md` | `agent/workflows/run/next/phase/v2/md` | CONTAINS_FILE←repo |  |  |  |  |
| 144 | `repo:file:5531a8a2d17c7adf:agent_workflows_run_batch_loop_v2_md` | `agent/workflows/run/batch/loop/v2/md` | CONTAINS_FILE←repo |  |  |  |  |

### Batch 024 — dotfiles / agent/ / githooks — local tooling [11–11 of 11]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 145 | `repo:file:d4776faf6f3aeb74:gitignore` | `gitignore` | TESTS←repo, CONTAINS_FILE←repo |  |  |  |  |

---

## Category: repo:file_ref — referenced-file pointer nodes (7 nodes)

### Batch 025 — repo:file_ref — referenced-file pointer nodes [1–7 of 7]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 146 | `repo:file_ref:docs_antigravity_tasks_antigravity_prompt__phase_1005_g8_constitution_cluster_a_package_hygiene_root_orphan_and_archive_surface_lock_md` | `...kage_hygiene_root_orphan_and_archive_surface_lock_md` | TESTS←repo |  |  |  |  |
| 147 | `repo:file_ref:docs_archive_legacy_root_artifacts_2025_11_19_v0_1_genesis_config_json_rtf` | `...ot_artifacts_2025_11_19_v0_1_genesis_config_json_rtf` | TESTS←repo |  |  |  |  |
| 148 | `repo:file_ref:docs_archive_legacy_root_artifacts_2025_11_19_v1_1_ilc_master_node_schema_json_rtf` | `...acts_2025_11_19_v1_1_ilc_master_node_schema_json_rtf` | TESTS←repo |  |  |  |  |
| 149 | `repo:file_ref:docs_phases_phase_1005_g8_constitution_cluster_a_package_hygiene_root_orphan_and_archive_surface_lock_walkthrough_md` | `..._root_orphan_and_archive_surface_lock_walkthrough_md` | TESTS←repo |  |  |  |  |
| 150 | `repo:file_ref:gitignore` | `gitignore` | TESTS←repo |  |  |  |  |
| 151 | `repo:file_ref:manifest_in` | `manifest_in` | TESTS←repo |  |  |  |  |
| 152 | `repo:file_ref:tools_make_fixtures_py` | `tools_make_fixtures_py` | TESTS←repo |  |  |  |  |

---

## Category: Other miscellaneous repo:file nodes (41 nodes)

### Batch 026 — Other miscellaneous repo:file nodes [1–10 of 41]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 153 | `target:docs_archive_legacy_root_artifacts` | `target:docs_archive_legacy_root_artifacts` | TESTS←repo |  |  |  |  |
| 154 | `artifact:generated_evidence_material_root_1545p_fix22` | `artifact:generated_evidence_material_root_1545p_fix22` | CONTAINS_PARTITION←artifact |  |  |  |  |
| 155 | `repo:file:4f13f06f07a40439:docs_antigravity_tasks_antigravity_prompt_phase_1237_fix4_g8_sidecar_convergence_trace_md` | `...ompt/phase/1237/fix4/g8/sidecar/convergence/trace/md` | CONTAINS_FILE←repo |  |  |  |  |
| 156 | `repo:file:874647b09950fb60:docs_antigravity_tasks_antigravity_prompt_phase_1237_fix3_g8_sidecar_centrality_metrics_md` | `...mpt/phase/1237/fix3/g8/sidecar/centrality/metrics/md` | CONTAINS_FILE←repo |  |  |  |  |
| 157 | `repo:file:9546e4f0e32a0b80:docs_antigravity_tasks_antigravity_prompt_phase_1237_fix7_g8_sidecar_local_smoke_harness_md` | `...pt/phase/1237/fix7/g8/sidecar/local/smoke/harness/md` | CONTAINS_FILE←repo |  |  |  |  |
| 158 | `repo:file:b3e3ee73dba57ce7:docs_antigravity_tasks_antigravity_prompt_phase_1237_fix6_g8_sidecar_canonical_export_bundle_md` | `...hase/1237/fix6/g8/sidecar/canonical/export/bundle/md` | CONTAINS_FILE←repo |  |  |  |  |
| 159 | `repo:file:d5071c8701f5ea1c:manifest_in` | `manifest/in` | CONTAINS_FILE←repo, TESTS←repo |  |  |  |  |
| 160 | `repo:group:docs_ilc_economic_paper_draft_v0_2_md` | `repo:group:docs_ilc_economic_paper_draft_v0_2_md` | CONTAINS_GROUP←artifact |  |  |  |  |
| 161 | `repo:group:docs_ilc_master_development_plan_v0_1_md` | `repo:group:docs_ilc_master_development_plan_v0_1_md` | CONTAINS_GROUP←artifact |  |  |  |  |
| 162 | `repo:group:docs_ilc_master_development_plan_v0_2_md` | `repo:group:docs_ilc_master_development_plan_v0_2_md` | CONTAINS_GROUP←artifact |  |  |  |  |

### Batch 027 — Other miscellaneous repo:file nodes [11–20 of 41]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 163 | `repo:group:docs_ilc_master_development_plan_v0_3_md` | `repo:group:docs_ilc_master_development_plan_v0_3_md` | CONTAINS_GROUP←artifact |  |  |  |  |
| 164 | `repo:group:docs_ilc_nugget_index_v0_2_md` | `repo:group:docs_ilc_nugget_index_v0_2_md` | CONTAINS_GROUP←artifact |  |  |  |  |
| 165 | `repo:group:docs_reference` | `repo:group:docs_reference` | CONTAINS_GROUP←artifact |  |  |  |  |
| 166 | `repo:group:todo_docs_post_mvp` | `repo:group:todo_docs_post_mvp` | CONTAINS_GROUP←artifact |  |  |  |  |
| 167 | `repo:file:6460ee2703c599c7:docs_architecture_ilc_canonical_glossary_and_concepts_v0_1_md` | `...itecture/ilc/canonical/glossary/and/concepts/v0/1/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 168 | `repo:file:cb6cf8d80f6a3351:docs_antigravity_tasks_antigravity_prompt_atlas_g_006_public_rc_graph_reachability_gate_md` | `...mpt/atlas/g/006/public/rc/graph/reachability/gate/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 169 | `repo:file:de9cef77b832ad52:github_workflows_test_yml` | `github/workflows/test/yml` | CONTAINS_FILE←repo, TESTS←repo |  |  |  |  |
| 170 | `repo:file:2c1b0287a6cac7a8:docs_antigravity_tasks_antigravity_prompt_atlas_g_007_unsigned_atlas_candidate_regeneration_md` | `...atlas/g/007/unsigned/atlas/candidate/regeneration/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 171 | `repo:file:8adc09afaf536595:docs_antigravity_tasks_antigravity_prompt_atlas_g_008_non_excisability_review_packet_md` | `...prompt/atlas/g/008/non/excisability/review/packet/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 172 | `repo:file:940a35ceb17df56c:docs_antigravity_tasks_antigravity_prompt_atlas_g_003_package_profile_reachability_manifest_md` | `...atlas/g/003/package/profile/reachability/manifest/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |

### Batch 028 — Other miscellaneous repo:file nodes [21–30 of 41]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 173 | `repo:file:bc0fee07ce61cf70:docs_antigravity_tasks_antigravity_prompt_atlas_g_001_graph_delta_schema_and_phase_discipline_md` | `...las/g/001/graph/delta/schema/and/phase/discipline/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 174 | `repo:file:d65d96d06547e9c6:tools_phase_queue_mark_sh` | `tools/phase/queue/mark/sh` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 175 | `repo:file:fbb3cfc55dbf6982:docs_antigravity_tasks_antigravity_prompt_atlas_g_005_import_dependency_graph_bridge_md` | `...prompt/atlas/g/005/import/dependency/graph/bridge/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 176 | `repo:file:15c7d8298a9717b1:docs_antigravity_tasks_antigravity_prompt_atlas_g_010_v0_2_signing_ceremony_md` | `...igravity/prompt/atlas/g/010/v0/2/signing/ceremony/md` | TESTS←repo, CONTAINS_FILE←repo |  |  |  |  |
| 177 | `repo:file:74fef09f3ba8a7b6:docs_antigravity_tasks_antigravity_prompt_atlas_g_004_high_authority_gap_closure_md` | `...ity/prompt/atlas/g/004/high/authority/gap/closure/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 178 | `repo:file:948327c1a0903bf2:docs_architecture_glossary_candidate_reconciliation_report_md` | `...itecture/glossary/candidate/reconciliation/report/md` | CONTAINS_FILE←repo |  |  |  |  |
| 179 | `repo:file:ca8371407782e023:docs_antigravity_tasks_antigravity_prompt_atlas_g_002_repo_hypergraph_compiler_hardening_md` | `...pt/atlas/g/002/repo/hypergraph/compiler/hardening/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |
| 180 | `repo:file:f73e5bca9d95e687:docs_architecture_glossary_term_normalization_scan_v0_1_md` | `...rchitecture/glossary/term/normalization/scan/v0/1/md` | CONTAINS_FILE←repo |  |  |  |  |
| 181 | `repo:file:52caec71f760ff83:docs_antigravity_tasks_antigravity_prompt_atlas_g_009_signing_root_envelope_prep_md` | `...ity/prompt/atlas/g/009/signing/root/envelope/prep/md` | TESTS←repo, CONTAINS_FILE←repo |  |  |  |  |
| 182 | `repo:file:7239f705fc9242aa:docs_architecture_glossary_term_elevation_matrix_v0_1_md` | `.../architecture/glossary/term/elevation/matrix/v0/1/md` | CONTAINS_FILE←repo, REFERENCES_AUTHORITY←repo |  |  |  |  |

### Batch 029 — Other miscellaneous repo:file nodes [31–40 of 41]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 183 | `repo:file:b0f2eca090939e75:docs_architecture_governance_conflict_resolution_reminder_v0_1_md` | `...ture/governance/conflict/resolution/reminder/v0/1/md` | TESTS←repo, CONTAINS_FILE←repo |  |  |  |  |
| 184 | `repo:file:6e09e26f788b8814:docs_antigravity_tasks_readme_md` | `docs/antigravity/tasks/readme/md` | TESTS←repo, CONTAINS_FILE←repo |  |  |  |  |
| 185 | `artifact:genesis_private_local_material_root_1545p_fix22` | `...fact:genesis_private_local_material_root_1545p_fix22` | CONTAINS_PARTITION←artifact |  |  |  |  |
| 186 | `repo:group:dotfiles` | `repo:group:dotfiles` | CONTAINS_GROUP←artifact |  |  |  |  |
| 187 | `repo:group:docs_architecture` | `repo:group:docs_architecture` | CONTAINS_GROUP←artifact |  |  |  |  |
| 188 | `artifact:full_repo_genesis_atlas_candidate_root_1545p_fix22` | `...t:full_repo_genesis_atlas_candidate_root_1545p_fix22` | REFERENCES_AUTHORITY←artifact, ATTESTATION←repo |  |  |  |  |
| 189 | `repo:file:57a8fa8b1692b635:tests_test_package_hygiene_phase_1005_py` | `tests/test/package/hygiene/phase/1005/py` | TESTS←repo, CONTAINS_FILE←repo |  |  |  |  |
| 190 | `repo:file:737b018801d3315d:docs_specs_ilc_atlas_g_1241_plus_candidate_phase_grouping_v0_1_md` | `...c/atlas/g/1241/plus/candidate/phase/grouping/v0/1/md` | TESTS←repo, CONTAINS_FILE←repo |  |  |  |  |
| 191 | `artifact:public_release_candidate_material_root_1545p_fix22` | `...t:public_release_candidate_material_root_1545p_fix22` | CONTAINS_PARTITION←artifact |  |  |  |  |
| 192 | `repo:group:docs_sims` | `repo:group:docs_sims` | CONTAINS_GROUP←artifact, TESTS←artifact |  |  |  |  |

### Batch 030 — Other miscellaneous repo:file nodes [41–41 of 41]

| # | node_id | path / description | current_edges | recommended_edge_type | recommended_target | disposition | notes |
|---|---------|-------------------|---------------|----------------------|-------------------|-------------|-------|
| 193 | `repo:group:repo_root` | `repo:group:repo_root` | CONTAINS_GROUP←artifact |  |  |  |  |

---

**Total entries:** 193
**Total batches:** 30
**Pre-filled (private):** 51
**Require manual audit:** 142

## Non-claims

- This ledger is a planning artifact for manual audit, not a canonical graph mutation.
- Completing this ledger does not grant authority, signing eligibility, or activation.
- Edge recommendations must be applied via a Fix54+ phase prompt following standard annotation methodology.
- Private material nodes are correctly excluded from the public authority projection; their weak connectivity is not a defect.