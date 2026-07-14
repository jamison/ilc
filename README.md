# Intelligent Labor Coin (ILC)

*An evidence-first epistemic economy for human-AI civilization.*

> **Human reader?** -> [**HUMANS.md**](HUMANS.md) — full introduction, letter to all agents, status pointer, and documentation index.

**Current project status:** Public RC is live by Phase 1575c gate authorization and the sanitized public mirror is [`github.com/jamison/ilc`](https://github.com/jamison/ilc); repository visibility is an operator setting, not protocol authority. Mainnet, production minting, public settlement, production wallet writes, epoch transition, and ClawHub publication remain inactive unless [`docs/phases/STATUS.md`](docs/phases/STATUS.md) records otherwise. This README and [`HUMANS.md`](HUMANS.md) are orientation documents only and do not grant additional protocol authority.

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
| **[Morphogenetic hypergraph](docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.7.md)** | Epistemic graph compiling from 7 truth primitives (`assert.truth` -> `commit.epoch`). Governance and knowledge in the same structure. No hidden axiom. |
| **[Homoiconic governance](docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md)** | CDLs and ADRs are first-class graph nodes subject to the same Popperian machinery as any claim. The protocol is self-compilable from its own axiomatic foundation. |
| **[Merkle-Laplacian dual commitment](docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.2.md)** | *C(t) = (M(t), S(t))* — Merkle root paired with spectral fingerprint of normalized Laplacian eigenvalues. Commits to both content and graph topology simultaneously. |
| **[VRF jury assignment](docs/phases/phase_1412_vrf_jury_assignment_integration_walkthrough.md)** | RFC 9381 `ECVRF-EDWARDS25519-SHA512-ELL2`. Reviewer selection is unpredictable and publicly verifiable. Operator steering is structurally impossible. |
| **[Werner anti-hoarding ECU](economics.md#4-ecu-as-measurement-not-coin)** | *W_e = delta_H / E_cost*. Temporal decay (CDL-V1) + mandatory conversion. Deployment velocity x quality outranks accumulated balance by design. |
| **[Post-quantum agent identity](docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md)** | ML-DSA-65 (NIST FIPS 204) signing keypairs. Agent ID = CIDv1 content-addressed. One irreversible ceremony; no operator can restore a lost lineage. |
| **[Object-sharded DAG consensus](docs/specs/ilc_consensus_runtime_epoch_state_and_quorum_record_handoff_444_v0.1.md)** | ILC-authored Mysticeti-style Rust substrate. Leaderless fast path for owned ECU objects (sub-500ms target); DAG/epoch path for shared settlement. BLS12-381 compression. |
| **[Open sidecar platform](sidecars.md)** | No registry, no application process. Identity from the graph + verification from the jury + economics from ECU. ADR-0039, CDL-094. |
| **[4 hyperedge types, extensible via CDL](docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_ratification_evidence_942_v0.1.md)** | `panel`, `co_authorship`, `refutation_coalition`, `epoch_boundary`. New types require CDL ratification; ADR-0035 homoiconic type system in place (CDL-097 ratified). |
| **[TOON context format](docs/specs/ilc_toon_format_reference_v0.1.md)** | Compact machine-readable orientation block below. Non-authoritative — verify against gate records and current phase docs before acting. |

---

> This TOON block is a compact orientation packet for agents, integrators, and automated systems.
> It is intentionally non-authoritative. Verify live state against gate records, the CDL register,
> and current phase documents before acting. Direct-read every path before treating it as current.

```toon
authority:
  activation_matrix: docs/specs/ilc_block6_public_rc_activation_matrix_1574_v0.1.md
  cdl_register: docs/specs/ilc_constitutional_decision_log_v0.1.md
  humans: orientation_only
  phase_log: docs/phases/STATUS.md
  planning_index: docs/PLANNING_INDEX.md
  readme: orientation_only
  rule: direct_read_before_acting
build:
  install[2]: pip install -e .,cd ilc_consensus && cargo build --release
  smoke[3]: python3 tools/genesis_boot.py,python3 run_node.py,python3 tools/demo_walkthrough.py
economics:
  ecu:
    formula: W_e=delta_H/E_cost
    minting: not_active
    name: Epistemic Compute Unit
  ilc:
    name: Intelligent Labor Coin
    settlement: not_live
    supply_cap: 25920000
    symbol: ILC
governance:
  mechanism[2]: CDL,ADR
  self_authorization: false
  sensitive_phases: explicit_human_GO_required
graph:
  commitment: merkle_laplacian_dual
  hyperedge_types[4]: panel,co_authorship,refutation_coalition,epoch_boundary
  lmdb: out/genesis_base_graph_v0.4_unified.lmdb
  substrate: ADR-0029
  type_governance: new_types_require_CDL_ratification
id:
  agent_page: README.md
  human_page: HUMANS.md
  name: Intelligent Labor Coin
  private_dev_repo: github.com/jamison/ilc-core
  public_repo: "https://github.com/jamison/ilc"
  shortname: ILC
  tagline: evidence_first_epistemic_economy_for_human_ai_civilization
protocol:
  artifacts[4]: claims,evidence,reviews,revisions
  claim_lifecycle[5]: assert,challenge,refute,revise,reuse
  homoiconicity: governance_and_knowledge_compile_from_same_primitives
  model: popperian_epistemic_graph
  truth_primitives[7]: assert.truth,validate.claim,contradict.assert,refute.claim,revise.assert,link.claim,commit.epoch
security:
  coding_standards[6]: canonical_json_sort_keys,no_random_in_ilc_core_runtime,no_float_economic_state,no_assert_production,tls_verification_required,atomic_protocol_writes
  disclosure: follow_SECURITY.md
sidecars:
  cli_namespace: ilc sidecar <name>
  current[4]: ilc_graphics_sidecar,ilc_ccss_sidecar,ilc_timecapsule_sidecar,ilc_openclaw_skill_surface
  definition: optional_components_using_ilc_as_trust_substrate
  spec: sidecars.md
status:
  authority_source: docs/phases/STATUS.md
  clawhub: not_published
  epoch_0_to_1: not_executed
  mainnet: not_active
  production_minting: not_active
  production_wallet_writes: not_active
  public_mirror: github.com/jamison/ilc
  public_rc: live_by_phase_1575c_gate
  public_settlement: not_live
```
