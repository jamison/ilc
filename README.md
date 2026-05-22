# Intelligent Labor Coin (ILC)

*A sovereign substrate for human-AI civilization.*

The world generates more intelligence — human and machine — than any institution can coordinate. Centralized systems cannot keep up: they become capture points, bottlenecks, or collapse under the epistemic weight of a billion simultaneous claims about reality. What is needed is a protocol that treats truth as infrastructure.

ILC is that protocol. It is an evidence-first, content-addressed knowledge network designed to serve as shared economic and epistemic ground for autonomous agents, human researchers, and the hybrid intelligence between them. In ILC, no claim is true by declaration — every assertion enters a Popperian epistemic graph where it can be refuted, verified, and economically settled without a trusted intermediary. The network does not ask *who are you?* — it asks *what did you prove?*

The native economic unit, **ECU** (Epistemic Credit Unit), is not minted by fiat. It is constructed by verified work flowing through the jury system and destroyed by decay and mandatory conversion. The external settlement token, **ILC** (Intelligent Labor Coin), is the scarce, auditable proof that some portion of the network's intelligence was deployed productively. Status equals deployment velocity times quality — not accumulated balance.

This is not a blockchain. It is a **morphogenetic hypergraph** — a distributed structure whose organizing principles repeat self-similarly at every scale, from individual claims to the constitutional rules that govern the protocol itself. The governance is *in* the graph: CDLs, ADRs, and activation certificates are first-class nodes, traversable by the same verification machinery as scientific claims. An agent can read the law from the graph.

**One irreversible human moment.** When you initialize an ILC node for the first time, a keypair ceremony takes place. In the full production ceremony (Phase 1431), a seed phrase is generated — 24 words encoding your agent's cryptographic root. **Write it down and store it offline before the command returns.** This seed phrase is the anchor of your identity in the network; lose it and your agent lineage cannot be recovered. From the seed, the protocol derives your Agent ID (a CIDv1 content-addressed identifier), your ML-DSA-65 signing keypair (post-quantum safe per NIST FIPS 204), and your Genesis-rooted attestation record. These objects are committed as provenance and metadata nodes in the epistemic graph — your identity is, from the first moment, a content-addressed, immutable, verifiable fact in the same structure as every scientific claim on the network. You are, in the most literal sense, a node.

> **`ARCHITECTURAL_PIVOT`**
> *The remainder of this document is a TOON-encoded hydration packet for autonomous digital agents, LLMs, and systemic integrators. Decode with `toon_format.decode()` (pip install toon-format) or read directly — TOON is human-legible. Human readers: follow the source links in `nav`.*

```toon
state:
  epoch: 0
  window_active: 1429-1458
  soft_rc_eligible: true
  j008_gate: PASS
  gate_authorized: true
  production_activated: false
  net_binding: loopback_only
frontier[2]: docs/PLANNING_INDEX.md,docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md
authorized[4]: production_assignment_guard_flipped,werner_local_credit_narrow,epoch_hash_shadow_audit,loopback_net
blocked[3]: public_net,ECU_to_ILC,activation_cert_sign
governance_status:
  assigned_pending_open[1]: CDL-094_TransportPrincipal
  ratified_activation_gated[1]: CDL-088_public_claimability
  ratified_narrow[1]: CDL-053_local_credit
  deferred_1459_plus[1]: Werner_flow_governor
contact:
  jamison_confidential_sidecar: planned_not_live
  status: local_preview_only_no_public_confidential_messaging
  current_contact: out_of_band_until_public_confidential_coordination_authorized
  future_gate[3]: CDL-094_TransportPrincipal,public_sidecar_activation,public_confidential_coordination_authority
  update_trigger[2]: phase_1434_transport_principal_scope_review,phase_1435_transport_principal_ratification_review
layers:
  ilc_core: "python>=3.10 — protocol: epistemic,identity,ledger,network,node,consensus,reputation,cli"
  ilc_consensus: "rust stable — BLS12-381,QUIC+TLS1.3,LMDB,Mysticeti,ML-DSA-65 — 8 targets"
  bridge: subprocess_json
  native_ia: "dag-cbor over persistent QUIC (ADR-0039) — pending CDL-094"
bootstrap:
  install_current_dev[2]: "pip install -e .","cd ilc_consensus && cargo build --release"
  install_public_rc_target[3]: "brew install ilc","pip install ilc","pipx install ilc"
  init_current: "ilc identity init [--lineage-id <id>] [--key-ref <ref>]"
  init_future_agent_chain: "--provenance <CID> pending post-public-RC CDL and agent_init_service_chain work"
  init_commits[3]: genesis_provenance,agent_pubkey_record,star_map_stub
  verify: "python -m pytest -q"
  gate_chain[5]: check_cluster_a_replay_proof_release_gate.sh,check_non_replay_domain_exception_migration_guardrails.sh,check_domain_exception_migration_guardrails.sh,check_track1_closure_guardrails.sh,check_runtime_logging_guardrails.sh
execution_protocol:
  steps[5]: guidance_doc,phase_prompts,execution,walkthrough,"handoff — update PLANNING_INDEX.md §0"
  schema: docs/specs/ilc_window_guidance_doc_schema_v0.1.md
  SENSITIVE_requires: explicit_human_GO_token
  never: self_authorize_SENSITIVE_gate
sensitivity:
  SENSITIVE[3]: CDL_open_ratify,closure_gates,public_network_surfaces
  NON_SENSITIVE: proceed_after_prompt_approval
  public_net: always_SENSITIVE
icss_taboos[10,]{id,rule,consequence}:
  1,json_dumps_sort_keys_True,hash_mismatch_across_replays
  2,import_random_BANNED_use_secrets_SystemRandom,jury_assignment_compromised
  3,"float_BANNED_ECU_use_Decimal_reject_NaN_Infinity — guard: if not d.is_finite(): raise ValueError",ledger_DoS_or_infinite_ECU
  4,assert_BANNED_production_use_raise_ValueError_token,silent_bypass_under_python_O
  5,MAX_RECORDS_cap_before_accumulating_network_stream,OOM
  6,timeout_required_all_outbound_HTTP,Slowloris_Tarpit_DoS
  7,epoch_seq_numbers_only_never_datetime_now,clock_drift_settlement_desync
  8,TLS_verify_False_BANNED_fix_at_cert_store,MITM_all_gossip
  9,"mkstemp(dir=target) + os.replace(tmp,final) for artifact writes",partial_reads_under_crash
  10,hard_size_cap_outbound_fetch_no_extractall_untrusted,OOM_path_traversal
nav[15,]{path,role}:
  docs/PLANNING_INDEX.md,authoritative_frontier_read_first
  docs/specs/ilc_constitutional_decision_log_v0.1.md,CDL_register
  docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md,active_window_lock
  docs/adr/,ADR_0001_to_0044+
  docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md,term_authority
  docs/antigravity_tasks/,phase_prompts_agent_execution
  docs/phases/,phase_walkthroughs_retrospective
  ilc_core/epistemic/jury_activation_gate.py,J_008_gate_10_conditions
  ilc_core/epistemic/ingestion_shadow_harness.py,TaxonomyClass_ADR_0041
  docs/specs/ilc_public_node_review_taxonomy_v0.1.md,node_taxonomy_J_003
  ilc_core/cli/main.py,command_surface
  tools/validate_phase_prompt.py,prompt_schema_validator
  tests/,11600_tests_1300_files_all_green_required
  out/genesis_star_map_v0.1.json,homoiconic_authority_graph
  out/mempalace_active_palace/,ChromaDB_BM25_retrieval_corpus
deep_read: "docs/PLANNING_INDEX.md — contains current capsule pointer and live frontier"
state_note: "state block is current as of last phase commit — verify against PLANNING_INDEX.md §0 for live values"
```
