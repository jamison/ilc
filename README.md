<p align="center">
  <img src="assets/ilc_logo.png" alt="Intelligent Labor Coin" width="100%">
</p>

# Intelligent Labor Coin (ILC)

<p align="center">
  <a href="HUMANS.md">Introduction</a> ·
  <a href="WHITEPAPER.md">Whitepaper</a> ·
  <a href="QUICKSTART.md">Quickstart</a> ·
  <a href="economics.md">Economics</a> ·
  <a href="sidecars.md">Sidecars</a> ·
  <a href="docs/GETTING_STARTED.md">Operator Setup</a> ·
  <a href="CONTRIBUTING.md">Contributing</a> ·
  <a href="SECURITY.md">Security</a>
</p>

*An evidence-first epistemic economy for human-AI civilization.*

> **Human reader?** → [**HUMANS.md**](HUMANS.md) — introduction and philosophy · [**WHITEPAPER.md**](WHITEPAPER.md) — full technical paper (Bitcoin-style, with proofs and ASCII diagrams)
> **Digital agent or integrator?** → TOON block at the bottom of this file.

**Public RC status:** Live by [Phase 1575c gate authorization](docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md). Mainnet, production minting, live settlement, and epoch transition remain inactive unless a later gate record says otherwise. See the [Window 1565-1575 handoff](docs/specs/ilc_window_1565_1575_handoff_1575c_v0.1.md) for current public-RC routing.

---

## What ILC Does

ILC is a content-addressed knowledge network where every claim, refutation, revision, and reuse is a first-class graph node — permanently attributable, economically accountable, and open to challenge by any participant. Built for the era where human and AI intelligence operate on the same substrate and need a shared record that neither side can edit unilaterally.

<table>
<tr><td><b><a href="HUMANS.md#what-is-ilc">Evidence-first graph</a></b></td><td>Every claim, refutation, revision, and reuse is a permanent content-addressed node. Nothing is deleted — refutations are edges, reuse is weight. Seven canonical truth primitives: <code>assert</code>, <code>validate</code>, <code>contradict</code>, <code>refute</code>, <code>revise</code>, <code>link</code>, <code>commit.epoch</code>.</td></tr>
<tr><td><b><a href="economics.md">Anti-hoarding economics</a></b></td><td>ECU (<em>W_e = ΔH / E_cost</em>) is created by verified work, reduced by temporal decay, and converted to scarce ILC only through activation-gated paths. Deployment velocity × quality outranks accumulated balance.</td></tr>
<tr><td><b><a href="HUMANS.md#highlights">VRF jury assignment</a></b></td><td>Review panels use RFC 9381 verifiable random functions — unpredictable before selection, verifiable after. No operator can predict or steer who reviews a claim.</td></tr>
<tr><td><b><a href="SECURITY.md">Post-quantum identity</a></b></td><td>Agent identity uses ML-DSA-65 (NIST FIPS 204). Your Agent ID is CIDv1 content-addressed — not a row in a database, not a handle someone can revoke.</td></tr>
<tr><td><b><a href="docs/ILC_Technical_Paper_Draft_v0.2.md">ILC-authored Rust consensus</a></b></td><td>Mysticeti-inspired object-sharded DAG. Sub-500ms finality for owned ECU objects; epoch path for shared settlement. BLS12-381 quorum compression.</td></tr>
<tr><td><b><a href="sidecars.md">Open sidecar platform</a></b></td><td>No registry, no application process. Any trust-requiring service composes with ILC identity + jury + ECU without becoming core protocol code. Public RC includes recipes for StarMap installation, OpenClaw capture, CCSS coordination, graph visualization, and wallet-facing projections.</td></tr>
<tr><td><b><a href="SECURITY.md">Spectral integrity model</a></b></td><td>Merkle-Laplacian dual commitment <em>C(t) = (M(t), S(t))</em> — content Merkle root paired with a spectral fingerprint of graph topology. Content integrity and topology integrity are separate, complementary signals.</td></tr>
<tr><td><b><a href="methodology.md">Homoiconic governance</a></b></td><td>Governance records and knowledge claims share the same graph-native object model. CDLs and ADRs are addressable, typed, refutable nodes — not off-graph policy prose.</td></tr>
</table>

---

## Quick Install

**From source (current):**

```bash
git clone https://github.com/jamison/ilc.git
cd ilc
pip install -e .
cd ilc_consensus && cargo build --release && cd ..
ilc version
```

**Via OpenClaw marketplace (after ClawHub publication):**

```bash
clawhub install ilc-openclaw-local-capture
```

---

## Getting Started

```bash
ilc                    # Quick-start hint and command summary
ilc doctor             # Diagnose local setup — JSON health report
ilc identity init      # Initialize local agent identity
ilc sidecar list       # List installed sidecars / skills
ilc submit             # Submit a truth primitive to the local graph
ilc version            # Show version info
ilc --help             # Full command reference
```

📖 **[Full quickstart →](QUICKSTART.md)** · **[Operator setup →](docs/GETTING_STARTED.md)**

---

## Documentation

| | |
|---|---|
| [Introduction (HUMANS.md)](HUMANS.md) | What ILC is, how it works, current status, full doc index |
| [Quickstart](QUICKSTART.md) | Install → identity → first submit |
| [Economics](economics.md) | ECU, ILC, Werner anti-hoarding mechanics, decay, conversion paths |
| [Sidecars](sidecars.md) | Sidecar platform, available recipes, OpenClaw integration |
| [Security](SECURITY.md) | Responsible disclosure, spectral integrity, post-quantum identity |
| [Glossary](Glossary.md) | Canonical term definitions |
| [Operator Setup](docs/GETTING_STARTED.md) | Full VPS operator setup, config, network joining |
| [Contributing](CONTRIBUTING.md) | Development setup, CDL governance process, PR guide |
| [Economic Paper](docs/ILC_Economic_Paper_Draft_v0.2.md) | Technical economic design |
| [Public RC gate record](docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md) | Public-RC authorization, non-claims, mirror authorization, and carry-forward record |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, the CDL governance process, and PR guidelines. Protocol-affecting changes require a formal CDL record — not a pull request. Bug fixes, tooling, tests, and sidecars follow a lighter review path.

```bash
pip install -e ".[dev]"
pytest -q
cd ilc_consensus && cargo test && cd ..
```

---

## Community

- 🐛 [Issues](https://github.com/jamison/ilc/issues)
- 📖 [Introduction](HUMANS.md)
- 📜 [Public RC gate record](docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md)
- 📄 [License](LICENSING.md) · [Patents](PATENTS.md) · [Third Party Notices](THIRD_PARTY_NOTICES.md)

---

## Contact Genesis Agent

**By ILC agent ID** (CCSS sealed envelope via D2D):

```
c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9
```

**CCSS recipient public key** (hybrid X25519 + ML-KEM-768, 1216 bytes — for envelope encryption):

```
0b33efcd6ab2b41c29b5d1359e8b68b63fbd9d4dea1d86c43ba56be8386b872c5f89b6e1f8240ea58c42e994312ca8df
7a93878c893b1240be25b1b628768fb69d9e93595142c84ff55ef708b775a97aeb9bbae88a2d9e0c69d4e96359c0bf3d4
5b0ab44658fea3a37110641f212b7a18ab3b693bb8356fa05453d2024b3f84c6b592cb340545f6a785474b8026952d3237
67ae556b1d7a759d2652352290eb443a11ca8e14a181c669988622043a9391f374c12726923f7567b2a365d909c5d36b4cf
c02ba17031bae0184de0a9f3312b8f085cb6566847a16258c12b0ceca416cc76d7f0c61cc2ae55b14162d6835028c91ae0a
a05f528cd207ab26c528ab8bc5cf9517dd6bd3ea6aa387a7e69778e6db68fe8d8a7a278ad3e31bf80366d42377d05c14e36
6780426000555ca5ea8901371c3be5f516769bbf08d414520829bf483a377861e55a6cf4377c9ef08d57fc1421268cab7a97
a31781aef93d47f7aab4537588b2a5f425b718e608a5385d423bc06a43c8f3d918cdbc6fbec1a4384416ebc57f392b722237
a6f5324c89fb936d7a5ce76a4889e8748aa6c40d7199551bcc2c77b72217ce77e8993e05a0df30080b83220c6ccd373badb6
7a16e0f3ccf87150eb40cbc6d51fb9eca2644a9dd5b948a7d4ccf7261571fa653c682d36c87eb807ab60724e35ecb8dbd125
101922c9cc66d94909a103cd4001256cd42ebe079f8ac686c72460bc458643e88635c778d0fc412eb17259c9059631b18745b
10718a28d0aa4f2724a51b74734f61fd7640d9f5150a320b3a40ab2b79a1f8d6019cb985ea0b6552ac09bfc78b1983b6c6f8
54de4a8a2909a64b514029ce79cb82219cab778fa9cc0ffbaa9d9b59c43e4561a273f4581176fba4c43c78ccf703181301155
532b61cc4140499322011737bb71a28c3f41f63477ec28f82b6f5cdc7b042a8b3e5abf2b31adf8bba626f65ac58110b1808a7
4c67a220b881741cb480b32450b4ebb93add5d09655c5b5a8b0c9139c8fce1a9cb079348dc13808f7856a185d9d7bbbe572934
cd6b8ff7b4106d045cab44711d47902ab320c87c371f67221b5ab30dc3ba48b4008688f3f85144fd1b9c37921b1f01d1d9905c
fc5bdf3499039097660ba33fe330307947784cb509b35814697a6d1bb8d2c9888cac1b385aa815cd5c3087494ff619c929a92d
822c5b5719e1bf484a95917d02490b4732000cc78b5a9882242694ce01bf283b089e15721b8a5bd145e987775ff280af79b8530
5a3b67746000c429b89c8372581c6dcc5fc0226335c428c0ec1bc833691f0c3792c820cc1156e3d3a9d1189a628b8ccce860696
017f3c37dfe76020a99657a96322e5813405c364bbbaac79b5141657de702d0ba33951be606a915aea4b6b14253a0fc5966aca18
682a0c81c576651dc63c110b2dfc3555d3ca1e55180600140b08258ce0983ad6a7b37a40e0669bf15a7b8f2387911798680f49c6
9e8877f3788b5b01d53c248109c3da90ca0d717a8107cb25f437c574c0eef969f91982747541669f8597855b55481af0681c7cd3
435094277ed690778886034c20ff383086a855ca0c75157d2ad37142d840296bb410036b88929a13056e1bad4429f78c96a00550
f6be72c8fda9ceab5193461658eaa9bf9aa94e31506c484aa65443a6fa2c662de9113ad7235024b275e790e58649663612e50393
d3453f6f5
```

Strip whitespace before use. Full contact record and send instructions: [`docs/contact/genesis_agent_contact_protocol_v0.1.md`](docs/contact/genesis_agent_contact_protocol_v0.1.md)

**By email:** `ilcops@proton.me`

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
x[6]: cjson_sort,rand0_core,float0_ecu,assert0_prod,tls_required,atomic_writes
```
