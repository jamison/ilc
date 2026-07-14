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
auth[4]: docs/phases/STATUS.md,docs/PLANNING_INDEX.md,docs/specs/ilc_constitutional_decision_log_v0.1.md,docs/specs/ilc_block6_public_rc_activation_matrix_1574_v0.1.md
b[7]: pip_install_editable,cargo_build_release,pytest_q,cargo_test,genesis_boot,run_node,demo_walkthrough
c[5]: assert,challenge,refute,revise,reuse
e[2]: ECU=W_e=dH/E_cost;mint=0,ILC=cap25920000;settle=0
ep[9]: ilc=ilc_core/cli/main.py,atlas=ilc_core/cli/atlas_lmdb_cli.py,sidecar=ilc_core/cli/sidecar_cli.py,node=run_node.py,genesis=tools/genesis_boot.py,demo=tools/demo_walkthrough.py,release=tools/public_release_prepare_update.py,rust=ilc_consensus/src/main.rs,pq=ilc_consensus/src/pq_sign_main.rs
g[7]: sub=ADR0029,com=MLD,lmdb=out/genesis_base_graph_v0.4_unified.lmdb,panel,co_authorship,refutation_coalition,epoch_boundary
orient[2]: README.md,HUMANS.md
p[7]: assert.truth,validate.claim,contradict.assert,refute.claim,revise.assert,link.claim,commit.epoch
r[2]: pub=github.com/jamison/ilc,dev=github.com/jamison/ilc-core
rule: read_auth;read_path;read_code;no_readme_authority
s[7]: rc=1575c_live,mainnet=0,mint=0,settle=0,wallet=0,e01=0,ch=0
sw[13]: py=ilc_core,rs=ilc_consensus,cli=ilc_core/cli+run_node.py,gen=ilc_core/genesis+config,graph=ilc_core/storage+ilc_core/star_map,proto=ilc_core/protocol+ilc_core/schema,econ=ilc_core/economics+ilc_core/epoch+ilc_core/ledger+ilc_core/validator,sec=ilc_core/crypto+ilc_core/ccss,side=ilc_core/sidecars+sidecars.md,ops=tools+deploy+automation,docs=docs+whitepaper+QUICKSTART.md,test=tests+ilc_consensus/tests,sim=simulations+docs/sims
v: readme_toon_v4_swmap
x[6]: cjson_sort,rand0_core,float0_econ,assert0_prod,tls_required,atomic_writes
```
