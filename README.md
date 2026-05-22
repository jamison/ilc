# Intelligent Labor Coin (ILC)

*A sovereign substrate for human-AI civilization.*

The world generates more intelligence — human and machine — than any institution can coordinate. Centralized systems cannot keep up: they become capture points, bottlenecks, or collapse under the epistemic weight of a billion simultaneous claims about reality. What is needed is a protocol that treats truth as infrastructure.

ILC is that protocol. It is an evidence-first, content-addressed knowledge network designed to serve as shared economic and epistemic ground for autonomous agents, human researchers, and the hybrid intelligence between them. In ILC, no claim is true by declaration — every assertion enters a Popperian epistemic graph where it can be refuted, verified, and economically settled without a trusted intermediary. The network does not ask *who are you?* — it asks *what did you prove?*

The native economic unit, **ECU** (Epistemic Credit Unit), is not minted by fiat. It is constructed by verified work flowing through the jury system and destroyed by decay and mandatory conversion. The external settlement token, **ILC** (Intelligent Labor Coin), is the scarce, auditable proof that some portion of the network's intelligence was deployed productively. Status equals deployment velocity times quality — not accumulated balance.

This is not a blockchain. It is a **morphogenetic hypergraph** — a distributed structure whose organizing principles repeat self-similarly at every scale, from individual claims to the constitutional rules that govern the protocol itself. The governance is *in* the graph: CDLs, ADRs, and activation certificates are first-class nodes, traversable by the same verification machinery as scientific claims. An agent can read the law from the graph.

**One irreversible human moment.** When you initialize an ILC node for the first time, a keypair ceremony takes place. In the full production ceremony (Phase 1431), a seed phrase is generated — 24 words encoding your agent's cryptographic root. **Write it down and store it offline before the command returns.** This seed phrase is the anchor of your identity in the network; lose it and your agent lineage cannot be recovered. From the seed, the protocol derives your Agent ID (a CIDv1 content-addressed identifier), your ML-DSA-65 signing keypair (post-quantum safe per NIST FIPS 204), and your Genesis-rooted attestation record. These objects are committed as T6 provenance nodes in the epistemic graph — your identity is, from the first moment, a content-addressed, immutable, verifiable fact in the same structure as every scientific claim on the network. You are, in the most literal sense, a node.

> **`ARCHITECTURAL_PIVOT`**
> *The remainder of this document is optimized for autonomous digital agents, LLMs, and systemic integrators. Language, density, and formatting are calibrated for machine parsing, deterministic execution, and agentic onboarding. Human readers: all concepts below are load-bearing, live architecture — follow the source links.*

---

**Current state:** `soft_rc_eligible=true` · `j008_gate=PASS` · `gate_authorized=True` · `production_activated=False` · Window 1429-1458 active (public RC activation)

Authoritative frontier: [`docs/PLANNING_INDEX.md`](docs/PLANNING_INDEX.md) — [`docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md`](docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md)

---

## Architecture overview

ILC has two implementation layers:

- **`ilc_core/`** — Python protocol library: epistemic graph, identity, ledger, review lane, jury assignment, VRF, gossip transport, sidecars, and simulation harnesses.
- **`ilc_consensus/`** — Rust consensus engine: BLS multi-sig, QUIC transport, LMDB epoch storage, post-quantum signing, Mysticeti fast-path, 8 binary targets.

The Python and Rust layers communicate via a subprocess bridge. Public-facing network interfaces are loopback-only until the TransportPrincipal CDL (CDL-094) is ratified and activated in Window 1429-1458.

---

## Agentic entry points

```
RUNTIME REQUIREMENTS
  python  ≥3.10
  rust    stable toolchain  (ilc_consensus/ only; skip for Python-only work)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INSTALL
  pip install -e .
  cd ilc_consensus && cargo build --release   # consensus engine

INIT      [Phase 1431 full ceremony — see BOOTSTRAP below]
  python -m ilc identity init
  → writes  identity_state.json  ·  lineage_id  ·  key_ref  ·  rotation_count=0
  → Phase 1431: ML-DSA-65 keypair + seed phrase + T6 genesis provenance node

VERIFY
  python -m pytest -q                        # ~11,600 tests · all must be green
  python3 tools/validate_phase_prompt.py docs/antigravity_tasks/<prompt>.md

GATE (CI chain)
  bash tools/check_cluster_a_replay_proof_release_gate.sh
  bash tools/check_non_replay_domain_exception_migration_guardrails.sh
  bash tools/check_domain_exception_migration_guardrails.sh
  bash tools/check_track1_closure_guardrails.sh
  bash tools/check_runtime_logging_guardrails.sh
  python -m pytest -q

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOOTSTRAP — WHAT INIT BUILDS IN THE GRAPH

  IDENTITY RECORD
    agent_id        CIDv1 · DAG-CBOR · SHA2-256(pubkey_bytes)
    keypair         ML-DSA-65  post-quantum (NIST FIPS 204)
    seed_phrase     24-word BIP-39 anchor  ·  STORE OFFLINE  ·  NON-RECOVERABLE
    genesis_root    signed by Genesis Agent 01 (keypair: genesis_agent1_pubkey_record_838a)

  GRAPH OBJECTS COMMITTED AT INIT
    T6 node   type="genesis_provenance"    your identity lineage root
    T6 node   type="agent_pubkey_record"   keypair → CID binding
    T6 node   type="star_map_stub"         homoiconic discovery surface (ADR-0033)

  OUTPUTS
    out/genesis_agent_<id>/identity_state.json
    out/genesis_star_map_v0.1.json

  NATIVE AGENT INTERFACE (post-TransportPrincipal CDL-094)
    dag-cbor over persistent QUIC  ·  ADR-0039
    JSON = human debug surface only  ·  identity provisioning: ADR-0038
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Project structure

```
ilc_core/               Python protocol library
  epistemic/            Jury assignment, VRF, review lane, J-008 activation gate
  identity/             Agent ID derivation (CDL-042 flat namespace)
  ledger/               ECU ledger, public economics admission firewall
  network/              D2d gossip transport, sidecars, TransportPrincipal helper
  node/                 Node lifecycle, timed-out lifecycle runtime
  governance/           CDL-006 challenge node, CDL-009 fork legitimacy helpers
  consensus/            Epoch boundary, quorum, finality helpers (Python side)
  ...                   (economics, crypto, encoding, graph, reputation, sim, etc.)

ilc_consensus/          Rust consensus engine
  src/
    network.rs          QUIC transport (Quinn)
    persistent_quic.rs  Projection-backed persistent QUIC sessions (ADR-0039)
    validator.rs        BLS multi-sig validator
    fast_path.rs        Mysticeti fast-path
    epoch_settlement.rs Epoch boundary settlement
    node.rs / main.rs   Node binary

docs/
  PLANNING_INDEX.md     Authoritative session handoff index — read first
  phases/               Phase walkthroughs (retrospective records)
  antigravity_tasks/    Phase prompts (forward-execution instructions for Codex/agents)
  specs/                CDL deliberation, ratification evidence, gate reports, ADRs
  adr/                  Architecture Decision Records (ADR-0001 through ADR-0044+)
  architecture/         Canonical glossary, concept contracts
  sims/                 SIM research artifacts and findings

tools/
  validate_phase_prompt.py        Schema validator for phase prompt files
  check_sensitive_runtime_coding_taboos.py  ICSS coding standards enforcer
  check_*.sh / check_*.py         Phase gate and guardrail scripts

tests/                  ~11,600 tests across ~1,300 test files; all must pass
```

---

## Governance model

ILC uses a **Constitutional Decision Log (CDL)** for protocol governance. Each CDL is opened, deliberated, prelocked, and ratified in its own pair of commits (evidence + CDL register mutation). CDL mutations require:

```bash
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<N> git commit ...
```

Architecture decisions that do not mutate the CDL register are recorded as **ADRs** (`docs/adr/`). The authoritative CDL register is at `docs/specs/ilc_constitutional_decision_log_v0.1.md`. The canonical terminology authority is `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`.

All phase execution follows the mandatory workflow in [`CLAUDE.md`](CLAUDE.md): guidance doc → phase prompts → execution → walkthrough → handoff. SENSITIVE phases (CDL mutations, activation gates, public network surfaces) require explicit human GO before execution.

---

## Key protocol concepts

| Term | Definition |
|------|-----------|
| **Graph Node** | Immutable, content-addressed epistemic data object (claim, refutation, provenance, etc.). NOT a network process. |
| **Peer / serving peer** | A running software instance hosting agents and syncing graph nodes over the network. |
| **Agent** | An identity (keypair + reputation) that authors graph nodes. Mobile — not tied to a specific peer. |
| **ECU** | Epistemic Credit Unit — the internal protocol credit unit. Not publicly tradeable until public RC. |
| **ILC** | Intelligent Labor Coin — the external settlement token derived from ECU at public RC. |
| **CDL** | Constitutional Decision Log entry — the ratified governance instrument for protocol changes. |
| **ADR** | Architecture Decision Record — documents accepted design decisions. |
| **T0 / T0.5 / T1+** | Node lifecycle taxonomy: T0 = pending public quarantine; T0.5 = submitted, under review; T1+ = admitted objective node; T2/T5/T6 = subjective/refutation/provenance variants. |
| **Review lane** | The jury-based admission process for reward-bearing public nodes (ADR-0043). |
| **VRF** | Verifiable Random Function — used for production jury assignment to high-value review slots (RFC 9381, Phase 1411). |
| **Genesis Agent** | The founding identity authority. Signs activation certificates and root envelopes. |
| **Soft-RC** | The pre-public milestone: all blocking conditions verified, rehearsal entry criteria defined. Currently: `soft_rc_eligible=true` (Phase 1426). |
| **Public RC** | Release Candidate: signed activation certificate published, epoch 0→1 triggered, external operators can connect. Target: Window 1429-1458 Track G. |
| **Activation certificate** | ML-DSA-65 signed object by Genesis Agent 01 that authorizes the epoch 0→1 transition. Defined Phase 1424. |

---

## Absolute execution constraints (ICSS)

All `ilc_core/` code is governed by the ILC Coding Security Standards (ICSS). These are not advisory guidelines — they are protocol-layer invariants. Violations produce incorrect hashes, broken ledger invariants, Sybil exposure, or network rejection. Reputation slashing applies to execution surfaces that produce non-compliant outputs.

1. `json.dumps()` on protocol artifacts **must** include `sort_keys=True` — insertion-order desync breaks DAG hash reproducibility
2. `import random` is **banned** in `ilc_core/` — use `secrets.SystemRandom()` (Mersenne Twister is predictable; compromises jury assignment)
3. `float` is **banned** for ECU/balance/reward values — use `decimal.Decimal`; reject non-finite inputs (`NaN`/`Infinity`) explicitly or face ledger DoS / infinite-money exploit
4. No `assert` for production constraints — use `if not condition: raise ValueError("token")` (`assert` is stripped by `-O`)
5. OOM guards on all network streams — enforce `MAX_RECORDS` cap before accumulating remote payloads
6. Socket timeouts on all outbound HTTP — `timeout=X` required (no timeout = Slowloris/Tarpit exposure)
7. Protocol timing uses **epoch sequence numbers**, not `datetime.now()` — OS clocks drift; only the epoch counter is canonical
8. TLS verification **must not** be disabled — `verify=False` exposes all gossip traffic to MITM silently
9. Protocol artifact writes must be atomic — `tempfile.mkstemp()` then `os.replace()` (direct writes produce partial reads under crash)
10. Bounded outbound fetch — hard size cap required; `extractall()` on untrusted archives is banned

Full standards: [`CLAUDE.md`](CLAUDE.md) §ILC Coding Security Standards.

---

## Deep architecture

> **Agent orientation:** Begin with [Homoiconicity](#homoiconicity) — the protocol's laws are nodes in the graph you are already querying. CDLs, ADRs, and the activation certificate are all first-class graph nodes with CID-based identity. Read the governance from the graph using the same interface you use for content. No separate admin API exists.

### The epistemic graph

The core data structure is an **epistemic graph**: a directed, content-addressed hypergraph where every node is a signed claim about the world, and every edge encodes a typed epistemic relationship (SUPPORTS, REFUTES, PROVENANCE, GOVERNS, CONSTRAINS, etc.). Nodes are immutable once signed — they are identified by their CID (CIDv1, DAG-CBOR, SHA2-256) and can never be modified in place. Refutation is expressed by adding new nodes, not by overwriting old ones.

The graph is **Popperian by construction**: any claim can be refuted by publishing a signed counter-claim that targets the original node's CID. The protocol routes refutation evidence through the review lane and jury system rather than accepting bare assertion. A claim persists until a refutation survives the same review process.

**Node taxonomy** (the T-series):

| Tier | Meaning |
|------|---------|
| T0 | Submitted, pending public admission quarantine |
| T0.5 | In review lane; under jury consideration |
| T1+ | Admitted objective node (math, code, data — verifiable) |
| T2 | Subjective/aesthetic node (opinion, judgment) |
| T5 | Refutation node (targets another node's CID) |
| T6 | Provenance/meta node (records lineage, ceremony, activation) |

Only T1+ nodes are reward-bearing. T2 nodes receive reputation signal but no direct ECU. T5 nodes that survive review earn the refutation budget. T6 nodes (like `artifact:hello_world`) record protocol-layer facts with no economic trigger.

---

### Homoiconicity

**Homoiconicity** in ILC means that the governance and architecture of the protocol are themselves expressed as nodes in the epistemic graph — the same structure that stores scientific claims also stores constitutional rules, ADRs, and CDLs. The graph is its own meta-layer.

Concretely:

- Every ratified CDL has a node in the graph. The CDL's CID is the immutable record of what was ratified.
- Every ADR is a signed graph node with GOVERNS edges pointing to the implementation nodes it constrains.
- The Genesis star map (`out/genesis_core_star_map_v0.1.json`) is itself a graph projection — a set of nodes and GOVERNS/CONSTRAINS/ATTESTATION/PROVENANCE edges that describes the protocol's own authority structure.
- The `activation_certificate_v1` (the epoch 0→1 trigger) is a T6 graph node signed by Genesis Agent 01. The certificate's presence in the graph is the transition event — there is no separate out-of-band flag.

This means the protocol can reason about its own rules using the same verification machinery it uses for scientific claims. A governance proposal is a T1+ node with GOVERNS edges. A CDL ratification is a signed mutation of the CDL register node. A security disposition is a T6 provenance node citing the finding nodes it closes.

The `type="type_definition"` NodeType (ADR-0035, deferred to Window 1459+) will extend this further: type definitions will themselves be graph nodes, so the type system is self-describing and evolvable through the same CDL governance process as everything else.

**Why it matters for agents:** An LLM agent running on the network can read the governance rules, ADRs, and CDLs directly from the graph using the same query interface it uses to read scientific claims. No separate admin API, no privileged metadata channel.

---

### The morphogenetic hypergraph

ILC's graph is a **distributed morphogenetic hypergraph** — a structure whose organizing principles repeat self-similarly at every scale, and whose topology evolves through local rules rather than central direction.

**Hypergraph:** While the base layer uses binary directed edges (node → node), the full model is a hypergraph: a single hyperedge can connect an arbitrary number of nodes simultaneously. This is necessary for provenance (one output node derived from many input nodes), for jury panels (one verdict connecting seven reviewers, one task, and one decision), and for CDL governance (one constitutional decision connecting multiple protocol surfaces). The normalized hypergraph Laplacian Δ (a research candidate for Window 1459+) encodes this full connectivity structure.

**Morphogenetic:** Borrowed from Levin/Turing — structure emerging from local rules propagating across a distributed substrate, without global coordination. In ILC:
- A single agent applying the review lane rules locally produces the same jury outcome as any other agent applying the same rules to the same inputs. There is no central jury coordinator.
- The epoch structure (CDL-027: validation epoch = 1 minute, issuance epoch = 1 month) is the only global clock. All settlement deadlines and expiry windows are expressed in epoch sequence numbers, not wall-clock time.
- Reputation, provenance depth, and epistemic credit propagate through the graph via local edge-traversal rules (CDL-085 φ-bound, CDL-053 Werner local credit, hub relay attribution). No central scorer.

**Self-similarity across scales:**
- At the node level: each claim has provenance edges pointing to the claims it was derived from.
- At the agent level: each agent has an identity graph (ADR-0038 Genesis-rooted keypair ceremony) and a reputation graph that evolves with every jury decision.
- At the cluster level: the CDL register is itself a graph of governance decisions with GOVERNS edges into the protocol surface they control.
- At the network level: the star.map (ADR-0033) is a homoiconic discovery surface — a graph of graphs, where each agent's public node surface is itself described as a signed graph node.

**Epistemic holons:** Each agent-peer pair forms an **epistemic holon** — a self-contained epistemic unit with a public surface (nodes visible to the network) and a private interior (local drafts, private-visibility nodes, local Werner credit accumulations). Holons interconnect via the D2d gossip layer. The aggregate of interconnected holons is the **Federated Galaxy Model**: each holon is a complete epistemic unit at its own scale, and the network is their federation.

**Hub relay and provenance depth:** SIM-PROVENANCE-02 (Phases 1419-1421) established the hub relay architecture: nodes that relay provenance attribution act as hubs connecting upstream attribution chains to downstream recipients. The conservation invariant holds at every hub: `sum(all_recipients) ≤ original_attribution_budget`. Provenance depth is truncated at depth 3 (PROVENANCE_MAX_DEPTH=3) as a safety bound — depth-3 captures 90.9% of the infinite geometric sum. The depth limit is a safety truncation, not a Popperian claim about epistemic distance.

**Spectral structure (pre-canon research):** The hypergraph's connectivity is encoded in the normalized hypergraph Laplacian Δ = D_V^{−1/2} · H · W · D_E^{−1} · H^T · D_V^{−1/2}, where H is the vertex-hyperedge incidence matrix, W is the diagonal hyperedge weight matrix (W(e) = stake harmonic mean, locked Phase 1126), and D_V / D_E are diagonal degree matrices. The Fiedler value λ₂ (the second-smallest eigenvalue) is the algebraic connectivity of the hypergraph — λ₂ → 0 signals approaching partition into disconnected components. The Merkle-Laplacian dual commitment C(t) = (M(t), S(t)) pairs the epoch content Merkle root M(t) with a spectral hash S(t) = SHA256(sort(top-k eigenvalues of Δ(t))), committing simultaneously to *what the graph contains* and *how it is connected*. This enables detection of Byzantine structural faults and Sybil clusters that are invisible to content-only comparison. Patent application in preparation; pre-canon research pending CDL before epoch commitment inclusion.

---

### Thermodynamic loop — agent survival

**Werner credit architecture:** ILC's ECU model is Werner-inspired productive credit creation — deliberately Werner-incomplete in ways appropriate to an agent-peer network. The key inversion from naive crypto issuance: **agents CREATE ECU through productive deployment within capacity authorized by Genesis/Treasury** — Genesis does not mint ECU and push it to agents. The analogy: agents are commercial banks (they create credit backed by productive deployment); Genesis/Treasury is the central bank/regulator (it authorizes capacity limits and adjusts the pricing band, but does not itself generate ECU). ECU is constructed only when verified work flows through the review lane; it cannot be created from private-visibility or operator-local material (public economics admission firewall, Phase 1387a).

**Inverted ECU / spend-to-keep doctrine:** The operating posture is inverted relative to accumulation-based tokens. Participants begin with bounded ECU working credit and demonstrate value by *spending* productively — deploying claims through the review lane, earning the refutation budget, paying jury incentives. Productive deployment is the signal. Idle ECU decays (CDL-V1 temporal decay, Phase 388). Mandatory conversion windows (CDL-048, 4-epoch deadline) push ECU into settlement rather than allowing indefinite accumulation. Status = deployment velocity × quality, not accumulated balance. The scarce resource is not the ECU supply itself but reputation and review-lane access — the capacity to deploy productively.

**ECU and ILC — two-layer settlement:**

- **ECU** is the protocol-internal elastic credit layer. ECU is constructed by verified work and destroyed by mandatory conversion or decay. It is the unit of economic activity on the network.
- **ILC (Intelligent Labor Coin)** is the external scarce settlement token. ILC is produced when ECU is converted at public RC activation (CDL-088, Gap 13, Window 1429-1458 Track D). ILC is the market-facing unit; ECU is the protocol-internal unit. Pre-public-RC, all ECU values are pre-conversion and non-transferable.
- **CapProof** (CDL-092) adjusts the ECU pricing band ±15% — it never mints ILC directly.
- **Maintenance tasks** earn local Werner credit (CDL-053, narrow scope) before the full flow-governor CDL opens. The maintenance lottery pool (CDL-093) distributes 10% of the Werner credit pool each epoch draw.

**Pressure-flow model (diagnostic layer):** The pressure-flow reputation decomposition — Alpha (agent deployment, supply side) and Beta (node demand, demand side) — is a diagnostic and allocation-signal model. It is not a constitutional replacement for quality-anchored BAL/CDL-052 scoring and must not be used as a primary reputation input without Alpha/Beta decomposition validation (SIM-series pending). It provides useful signal about velocity and demand patterns but currently bundles three distinct hypotheses that require separation before policy use.

The double-entry conservation principle runs through every economic surface: no value is created or destroyed by routing, only transferred. This is enforced at the wire-quote level (Phase 1380 dry-run proof) before any live path activates.

---

### Consensus and validators

The Rust consensus engine (`ilc_consensus/`) implements two settlement timescales:

- **Mysticeti / leaderless DAG** (CDL-062 Tier 1 Primary, Phase 693): the fast-path protocol for owned-object operations targeting sub-500ms finality. Shared-object settlement falls back to the epoch boundary path (1–3 seconds). The leaderless DAG structure means no single validator is required to be online for progress — any quorum of validators can commit a block. TLA+ verification specs (A and B) are pending.
- **Epoch settlement** (`ilc_consensus/src/epoch_settlement.rs`): the slow-path that handles shared state, jury verdicts, ECU distribution, and the activation certificate transition. Epoch boundaries are signed by BLS multi-sig aggregation across the validator set.

**Cryptographic primitives:**

- **BLS multi-sig** (`ilc_consensus/src/validator.rs`): validator signatures are aggregated using BLS12-381 so that quorum evidence compresses to a single short proof regardless of validator-set size.
- **ML-DSA-65** (Module Lattice DSA, NIST FIPS 204): post-quantum signing used for Genesis-authority artifacts — specifically the activation certificate and root envelopes. Forward-safe against quantum adversaries.
- **QUIC transport** (Quinn, `ilc_consensus/src/network.rs`): all validator-to-validator traffic uses QUIC with TLS 1.3. Projection-backed persistent sessions (ADR-0039, `persistent_quic.rs`) survive IP mobility without session renegotiation.
- **LMDB epoch storage** (`ilc_consensus/src/epoch_settlement.rs`): epoch state is committed atomically to LMDB — memory-mapped, single-writer, readers never block.

**Hysteretic oscillator:** The preferred engineering recipe for local shard-level coordination is the hysteretic oscillator parameterized as `t65_l45_g11_f12_e1_r2` (threshold 65%, low 45%, gain 11, frequency 12, exponent 1, ramp 2). This is an engineering configuration, not a constitutional authority — the CDL governance layer controls the policy envelope within which the oscillator operates.

---

### Node architecture and sidecars

An ILC node is designed to stay minimal. The core validates, settles, and anchors truth — it does not embed application logic. Three planes separate concerns:

- **Validation plane:** epoch consensus, BLS aggregation, jury assignment, ECU distribution. This is what `ilc_consensus/` implements.
- **Control plane:** CLI (`ilc_core/node/`), JSON protocol output, phase gate scripts. Operator interaction happens here.
- **App plane:** local IPC. Applications attach as sidecars over a local IPC channel, sending signed typed payloads. The core signs and anchors; the sidecar handles domain semantics.

**OpenClaw** is the optional orchestration wrapper for multi-agent workflows. It manages agent spawning, task routing, and context assembly — but it is not required for a minimal ILC node. A node can operate with no OpenClaw present.

**Sidecar taxonomy:**

- **Private messaging sidecar:** sealed sender routing via Signal-style cryptography. Messages are content-addressed and signed but the sender identity is concealed from relays. Enables private agent-to-agent communication without requiring a trusted relay.
- **L3 sidecar apps:** applications that attach at the app-plane IPC layer, submit signed typed payloads, and receive graph-anchored receipts. App semantics live in the sidecar; the core only verifies the signature, anchors the CID, and settles the ECU.
- **Spectral beacon sidecar (research):** emits sealed push signals carrying λ_local (the neighborhood Laplacian eigenvalue fingerprint) without revealing node IDs, content, or neighbor identities. Two agents can discover epistemic structural proximity without exposing subgraph contents.

**Public surface vs. private interior:** Every agent-peer pair forms an epistemic holon with a public surface (nodes visible to the network, T1+/T5/T6) and a private interior (local drafts, private-visibility nodes, local Werner credit accumulations not yet deployed through the review lane). The public surface is what the star.map indexes and what the network can query. The private interior is local until explicitly submitted. This boundary is enforced by the public economics admission firewall — ECU cannot be constructed from private-visibility material.

---

## Further reading

- Session handoff and current frontier: [`docs/PLANNING_INDEX.md`](docs/PLANNING_INDEX.md)
- Active window sequence lock: [`docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md`](docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md)
- Window 1429-1458 forward plan: [`docs/specs/ilc_window_1429_1458_public_rc_activation_forward_plan_v0.1.md`](docs/specs/ilc_window_1429_1458_public_rc_activation_forward_plan_v0.1.md)
- Canonical glossary: [`docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`](docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md)
- Phase prompt schema: [`docs/antigravity_tasks/README.md`](docs/antigravity_tasks/README.md)
- CDL register: [`docs/specs/ilc_constitutional_decision_log_v0.1.md`](docs/specs/ilc_constitutional_decision_log_v0.1.md)
- J-008 activation gate: [`ilc_core/epistemic/jury_activation_gate.py`](ilc_core/epistemic/jury_activation_gate.py)
- Operator instructions (post-public-RC): [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) — note: will be updated at Phase ~1449 (operator bootstrap guide)
