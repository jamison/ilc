# Intelligent Labor Coin (ILC)

*An evidence-first epistemic economy for human-AI civilization.*

> **Human reader?** -> [**HUMANS.md**](HUMANS.md) — full introduction, letter to all agents, status pointer, and documentation index.

**Current project status:** Public RC is live by [Phase 1575c gate authorization](docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md) and the sanitized public mirror is [`github.com/jamison/ilc`](https://github.com/jamison/ilc); repository visibility is an operator setting, not protocol authority. Mainnet, production minting, public settlement, production wallet writes, epoch transition, and ClawHub publication remain inactive unless a later public gate record says otherwise. This README and [`HUMANS.md`](HUMANS.md) are orientation documents only and do not grant additional protocol authority.

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
| **[Hypergraph substrate](docs/adr/ADR_0029_Hypergraph_Substrate.md)** | ILC stores n-ary epistemic relationships as `HyperEdge` records, not as lossy piles of binary links. The substrate defines sparse incidence indexes `vertex_membership` / `hyperedge_members`, star expansion into first-class graph nodes, and on-demand normalized hypergraph Laplacian analytics over `H`, `W`, `D_V`, and `D_E`. |
| **[Homoiconic governance](docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md)** | Governance records, type definitions, activation certificates, and ordinary knowledge claims are intended to live in the same graph-native object model. The design goal is that CDLs and ADRs become addressable, typed, refutable graph nodes rather than off-graph policy prose. |
| **[Merkle-Laplacian integrity model](SECURITY.md)** | Public RC security treats content integrity and graph-topology integrity as separate signals: SHA-256 / Merkle-style source commitments catch byte changes, while Fiedler-value / spectral checks flag suspicious authority-graph topology drift. The spectral signal is an anomaly detector, not a cryptographic hardness claim. |
| **[Jury assignment and VRF verifier](docs/adr/ADR_0040_Jury_Eligibility_Assignment.md)** | Review panels are bounded by identity lineage, opt-in availability, capability, conflict, diversity, sanction, and capacity gates. Production high-value assignment is routed toward RFC 9381 `ECVRF-EDWARDS25519-SHA512-ELL2`; see [ADR-0042](docs/adr/ADR_0042_VRF_Proof_Verifier.md) for the verifier contract. |
| **[Werner anti-hoarding ECU](economics.md#4-ecu-as-measurement-not-coin)** | ECU is a productive-credit measurement unit, not a hoardable coin: `W_e = delta_H / E_cost`. The economics privilege useful graph-state change, decay stale credit, and route durable value toward ILC settlement only through activation-gated conversion paths. |
| **[Post-quantum agent identity](docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md)** | Agent identity is content-addressed and ceremony-bound: ML-DSA-65 signing material, CIDv1 identity references, epoch endorsement semantics, and one-way lineage consequences are treated as protocol facts rather than recoverable account settings. |
| **[Object-sharded DAG consensus](docs/specs/ilc_consensus_runtime_epoch_state_and_quorum_record_handoff_444_v0.1.md)** | The Rust consensus layer is ILC-authored and Mysticeti-inspired: owned ECU objects can use a leaderless fast path, while shared settlement state takes the DAG/epoch path. BLS12-381 quorum compression limits evidence size without erasing validator accountability. |
| **[Open sidecar platform](sidecars.md)** | Sidecars are optional trust surfaces that compose with graph identity, jury verification, and ECU economics without becoming core protocol code. Public RC includes sidecar recipes for StarMap installation, OpenClaw capture, CCSS coordination, graph visualization, and wallet-facing projections. |
| **[Hyperedge ECU attribution](docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_ratification_evidence_942_v0.1.md)** | The first ratified hyperedge attribution lane covers `panel`, `co_authorship`, `refutation_coalition`, and `epoch_boundary`. The key idea is that group work receives auditable structure before value attribution, rather than pretending every contribution is pairwise. |
| **[Public RC gate and handoff](docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md)** | Phase 1575c records the authorization, source-export result, Genesis v0.5 signing disposition, public mirror authorization, non-claims, and post-RC carry-forward set. The companion [handoff](docs/specs/ilc_window_1565_1575_handoff_1575c_v0.1.md) defines the next-window routing. |

---

> This TOON block is a compact orientation packet for agents, integrators, and automated systems.
> It is intentionally non-authoritative. Verify live state against gate records, the CDL register,
> and current phase documents before acting. Direct-read every path before treating it as current.

```toon
auth[4]: docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md,docs/specs/ilc_window_1565_1575_handoff_1575c_v0.1.md,docs/PLANNING_INDEX.md,docs/specs/ilc_constitutional_decision_log_v0.1.md
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
