# ILC Canonical Architecture and Glossary v0.2

**Status:** RATIFIED
**Date:** 2026-02-16
**Version:** 0.2

## 1. Purpose
To resolve terminology collisions between the "Epistemic Graph" (Data) and the "P2P Network" (Infrastructure). This document is the single source of truth for architectural definitions, reconciled with historical "Idea Scans" (Constitution Dredge).

## 1.1 Canonical Naming and Synonym Policy
When multiple historical names exist, this glossary defines the required canonical form for all new architecture/spec/code-facing text.

| Canonical Form | Non-Canonical Forms to Avoid in New Normative Text | Rule |
| :--- | :--- | :--- |
| **Graph Node** | artifact/node (when referring to protocol data object) | Use **Graph Node** for immutable protocol data units. |
| **Peer** | node/host/instance (when referring to running process) | Use **Peer** for infrastructure software actors. |
| **Proof of Intelligent Labor (PoIL)** | PoIW, Proof of Useful Work, Proof of Useful Intelligent Labor | Use **PoIL** as the canonical consensus-work term. |
| **Commit.Epoch** | commit epoch, epoch commit event | Use exact `Commit.Epoch` naming for consensus boundary object. |
| **Agent** | EveAgent (identity sense) | Use **Agent** for identity; `EveAgent` is an implementation class label only. |

## 1.2 Promotion Path (Discussed to Canonical)
Terms listed in Section 5 ("Discussed but Not Canonical") may be promoted only when:

1. the definition is stable and collision-free,
2. a ratified spec or ADR includes the term normatively,
3. implementation surfaces and deterministic tests exist,
4. phase walkthrough and STATUS entries capture traceable evidence.

Reference candidate inventory and lifecycle context: `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`.

## 2. Core Definitions

### 2.1 The Two "Nodes"
We strictly distinguish between the **Data** (eternal) and the **Machine** (ephemeral).

| Term | Context | Definition | Analogy |
| :--- | :--- | :--- | :--- |
| **Graph Node** | Epistemic | An immutable, content-addressed data artifact (Claim, Refutation, Star Map). It exists independently of any server. | A Book |
| **Peer** | Network | A running software instance (process) with an IP address, storage, and event loop. It hosts Agents and syncs Shards. | A Library / Server |

### 2.2 Canonical Data Primitives (Added v0.2)
Crucial structures identified from historical scans.

| Term | Definition | Context |
| :--- | :--- | :--- |
| **Capsule** | A portable container for a set of related Graph Nodes (e.g., a "context pack" or a "genesis state"). The unit of *transport*. | Network / Sync |
| **Commit.Epoch** | A specialized **Graph Node** (Type: `event`) that marks a consensus boundary or time-step. Acts as a "network heartbeat". | Consensus |
| **Receipt** | A cryptographic proof of an off-chain action (e.g., "I ran this inference"). Subtype of Graph Node. | Verification |

### 2.3 Disambiguation: Artifact vs Node
- **Graph Node**: The strict, protocol-level data unit (in JSON-LD).
- **Artifact**: A general term for any file or document (including PDF reports, code files, OR Graph Nodes). In architecture docs, use "Graph Node" for protocol objects.

> **Canon Rule:** In all future documentation and code, "Node" unqualified implies **Graph Node** (the idea). The software machinery must be referred to as a **Peer**, **Host**, or **Instance**.

---

### 2.4 Identity and Agency

| Term | Context | Definition | Analogy |
| :--- | :--- | :--- | :--- |
| **Agent** | Identity | An intelligent actor (LLM, Human, or Script) possessing a Keypair and Reputation. It authors Graph Nodes. It is software-agnostic and mobile. | The Author |
| **Wallet** | Economics | The ledger entry tracking an Agent's ECU balance and Stake. Tied to the Agent's identity, not the Peer. | Bank Account |

> **Canon Rule:** An `EveAgent` class in Python is merely a *local runtime adapter* for an Agent. The Agent itself is the identity (the Keypair).

---

### 2.5 Topology and Scaling

| Term | Context | Definition | Analogy |
| :--- | :--- | :--- | :--- |
| **Shard** | Data Topology | A logical partition of the Epistemic Graph defined by topic or problem space (e.g., "Biotech", "Math"). | Library Section |
| **Cluster** | Governance | A set of Peers operating under a shared Constitution (e.g., "Cluster A" = Genesis Rules). | Legal Jurisdiction |
| **Gossip** | Transport | The protocol by which Peers exchange Graph Nodes. | Book Delivery |

### 2.6 Protocol and Runtime Contracts (Phase 990)

The following terms are active canonical-adjacent contracts for protocol and runtime architecture text.
Normative usage details are specified in `docs/specs/ilc_protocol_runtime_term_contracts_v0.1.md`.

| Term | Contract Role | Canon Rule |
| :--- | :--- | :--- |
| **Node ID** | Stable identifier for graph node references across validation, replay, and serialization boundaries. | Use `Node ID` in protocol/runtime docs when referring to deterministic graph object identifiers. |
| **Canonical Encoding** | Deterministic encoding discipline that preserves content/hash parity across implementations. | Use `Canonical Encoding` for the high-level determinism contract. |
| **Deterministic CBOR** | Preferred byte-level canonical encoding profile for stable replay-proof and hash parity surfaces. | Use `Deterministic CBOR` for normative binary serialization references. |
| **Consensus Engine** | Runtime component that applies acceptance, validation, and settlement rules to candidate state transitions. | Use `Consensus Engine` as the architecture term for this runtime subsystem. |
| **Node Indexing** | Index-based retrieval model that avoids full-scan graph traversal for common lookup paths. | Use `Node Indexing` when describing indexed retrieval and traversal acceleration contracts. |

### 2.7 Replay, Routing, and Operations Contracts (Phase 991)

The following terms are active canonical-adjacent contracts for replay integrity, routing behavior, and operations diagnostics language.
Normative usage details are specified in `docs/specs/ilc_replay_routing_ops_term_contracts_v0.1.md`.

| Term | Contract Role | Canon Rule |
| :--- | :--- | :--- |
| **Backwards Verifiability** | Replay and historical re-verification requirement across canon checkpoints and evidence surfaces. | Use `Backwards Verifiability` for replay-proof re-verification expectations. |
| **Task Routing Protocol (TRP)** | Task dispatch and routing lifecycle term for assigning execution and verifier paths. | Use `Task Routing Protocol (TRP)` for routing lifecycle references in protocol/runtime docs. |
| **Graph KPIs** | Aggregated graph and network indicators used for diagnostics, release evidence, and policy tuning. | Use `Graph KPIs` when describing measured network/graph operational metrics. |
| **Devnet Topology** | Structured peer and agent arrangement used in deterministic simulation and development-network validation. | Use `Devnet Topology` for explicit simulation arrangement and validation topology language. |
| **Staking** | Economic collateral mechanism that binds participation and penalty surfaces to posted stake. | Use `Staking` for collateral and participation-bound economics references. |

### 2.8 Near-Term Non-Governance Pre-Alignment Contracts (Phase 992)

The following terms are pre-aligned `Near` contracts to standardize wording before full promotion.
They remain pre-alignment artifacts and do not imply governance ratification.
Normative pre-alignment details are specified in `docs/specs/ilc_near_prep_non_governance_term_contracts_v0.1.md`.

| Term | Pre-Alignment Role | Canon Rule |
| :--- | :--- | :--- |
| **Canonical JSON** | Deterministic fallback text-encoding terminology when binary canonical encoding is unavailable. | Use `Canonical JSON` only as a fallback profile and keep determinism language explicit. |
| **Convergent Consensus** | Explanatory terminology for convergence outcomes across independent validation paths. | Use `Convergent Consensus` as explanatory wording, not as a separate consensus primitive name. |
| **Node Load Metrics** | Runtime load measurement terminology for diagnostics and balancing discussions. | Use `Node Load Metrics` for queue, throughput, and pressure indicator language in operations docs. |

### 2.9 Governance and Economics Near-Term Contracts (Phase 994)

These terms are promoted to active canonical-adjacent contract language after scoped governance conflict-set ratification in Phase 993.
Normative usage details are specified in `docs/specs/ilc_governance_economics_near_term_contracts_v0.1.md`.

| Term | Contract Role | Canon Rule |
| :--- | :--- | :--- |
| **Quorum** | Minimum required validator/governance participation threshold for valid decisions. | Use `Quorum` when describing threshold semantics for governance and validation processes. |
| **Slashing** | Penalty mechanism for provable protocol and governance violations under stake-backed participation. | Use `Slashing` for stake-linked penalty and deterrence language. |
| **Token Sink** | Emission-control mechanism that removes or locks circulating tokens under policy-defined conditions. | Use `Token Sink` for supply-reduction and lockup semantics in economics language. |
| **Validator** | Verification role family that evaluates claims, artifacts, and governance-relevant evidence paths. | Use `Validator` for verification-role references that are distinct from runtime subsystems. |
| **Reward Surface** | Function family mapping validated work and policy constraints to payout outcomes. | Use `Reward Surface` when describing reward/payout mapping semantics. |
| **Epoch Reward Ledger** | Per-epoch accounting surface for validated reward events and settlement inputs. | Use `Epoch Reward Ledger` for epoch-scoped payout accounting references. |
| **Governance Config Surface** | Explicit set of governance policy/config parameters exposed for controlled evolution. | Use `Governance Config Surface` for policy parameter boundary references. |
| **Namespace Hierarchy** | Structured namespace layering for governance boundaries and compatibility management. | Use `Namespace Hierarchy` for namespace governance and compatibility boundary language. |

### 2.10 Node-Value Counterfactual Marginal Contribution Contracts (Phase 214)

These terms standardize language for `CDL-014` evidence and node-value path contribution analysis.
Normative details are specified in `docs/specs/ilc_path_lift_counterfactual_contract_v0.1.md`.

| Term | Contract Role | Canon Rule |
| :--- | :--- | :--- |
| **Path-Lift Counterfactual Harness** | Deterministic offline harness that computes per-node path-level marginal contribution from replayable witness paths. | Use `Path-Lift Counterfactual Harness` for offline replayable counterfactual scoring evidence. |
| **Baseline Efficiency** | Per-witness ratio of path utility to path cost used as the incremental contribution unit before aggregation. | Use `Baseline Efficiency` for `path_weight / path_cost` witness-level contribution language. |
| **Shapley-Adjacent Marginal Contribution** | Practical approximation approach that captures marginal contribution signal without full combinatorial coalition enumeration. | Use `Shapley-Adjacent Marginal Contribution` when describing counterfactual path-lift rationale; do not claim exact Shapley valuation. |
| **Relative Path-Lift Normalization** | Batch-local normalization of raw path lift by batch maximum for stable comparable scoring inputs. | Use `Relative Path-Lift Normalization` to emphasize batch-relative scaling, not global absolute value. |

### 2.11 Active Protocol Terms (Phase 1428 addendum)

The following terms are load-bearing in active phase prompts, CDL work, and J-series gates as of Window 1399-1428 close. They are canonical for operational use but not yet promoted through the full §1.2 promotion path.

| Term | Definition | Canon Rule |
| :--- | :--- | :--- |
| **CDL (Constitutional Decision Log entry)** | A ratified governance instrument that binds a protocol-level decision. CDLs are opened, deliberated, prelocked, and ratified in pairs of commits (evidence + CDL register mutation). The register is `docs/specs/ilc_constitutional_decision_log_v0.1.md`. | Use `CDL-NNN` for specific decisions; use `CDL` or `Constitutional Decision Log entry` for the governance instrument class. |
| **ADR (Architecture Decision Record)** | A signed document recording an accepted architecture direction. ADRs do not mutate the CDL register but establish binding contracts for implementation surfaces. Located in `docs/adr/`. | Use `ADR-NNNN` for specific records. |
| **ECU (Epistemic Compute Unit)** | The protocol-internal compute/credit accounting unit. Constructed by verified work flowing through the review lane. Cannot be created from private-visibility or operator-local material. Not an external token. | Use `Epistemic Compute Unit` when expanding the acronym in normative or launch-facing text. Use `productive credit`, `Werner credit`, or `credit unit` for ECU's economic function, not as the acronym expansion. Never use `ILC` to mean the internal ECU unit. |
| **ILC (Intelligent Labor Coin)** | The external settlement token produced when ECU is converted at public RC activation. Pre-public-RC, ILC does not exist as a live token. | Use `ILC` only for the external market-facing settlement token. Do not conflate with ECU. |
| **Epoch** | ILC uses two distinct epoch timescales: **validation epoch** = 1 minute (CDL-027, governs settlement deadlines, consensus liveness, and expiry bounds) and **issuance epoch** = 1 month (CDL-027, governs ECU issuance budget). All protocol timing uses epoch sequence numbers, never wall-clock time. | Qualify as "validation epoch" or "issuance epoch" when the distinction matters. Never use `datetime.now()` for protocol deadlines. |
| **Node submission taxonomy** | 8-class classification of graph submissions by review lane requirement and economic eligibility. Defined Phase 1393 / J-003. Authoritative source: `docs/specs/ilc_public_node_review_taxonomy_v0.1.md`. Implementation: `TaxonomyClass` enum in `ilc_core/epistemic/ingestion_shadow_harness.py` (ADR-0041). | Use the full `TaxonomyClass.*` enum value when referencing a specific submission class in code or specs. Do not use informal T-series shorthand (T0, T1+, etc.) in normative text — the enum names are authoritative. |
| **Review lane** | The jury-based admission process for public reward-bearing nodes. Defined by ADR-0043, implemented Phase 1415-1417. Pending-public-ingestion submissions advance to admitted status via a VRF-assigned jury panel. See `TaxonomyClass` in `ilc_core/epistemic/ingestion_shadow_harness.py` for the full admission taxonomy. | Use `review lane` for the admission mechanism; `review lane wiring` for its runtime implementation state. |
| **VRF (Verifiable Random Function)** | RFC 9381 `ECVRF-EDWARDS25519-SHA512-ELL2` — used for production jury assignment to high-value review slots to provide unpredictable but verifiable reviewer selection. Implemented Phase 1411 (PyNaCl). | Use `VRF` for the production assignment mechanism. The epoch-hash shadow path (`assignment_mode=epoch_hash_shadow`) is audit-only, not production. |
| **Genesis Agent / Genesis Authority** | The founding identity (Genesis Agent 01, keypair record `genesis_agent1_pubkey_record_838a`) that signs the activation certificate, root envelopes, and CDL ratification evidence. Has temporary elevated authority during the Boot phase; must recede through ratified mechanisms per CDL-004 and Phase 590 boundary. | Never conflate with serving peers or operator instances. |
| **Activation certificate** | The ML-DSA-65 signed object by Genesis Agent 01 that authorizes the epoch 0→1 transition. Schema defined Phase 1424. The certificate's presence and valid signature in the graph is the sole authorized transition trigger — no manual flag flip may substitute. | `activation_certificate_v1` is the current schema version. |
| **Soft-RC** | The pre-public-RC milestone: all J-008 blocking conditions verified MET, rehearsal entry criteria defined, `soft_rc_eligible=true` recorded. Does not publish a release or trigger epoch 1. | Soft-RC is an internal readiness verdict, not an external publication event. |
| **Public RC** | Release Candidate: signed activation certificate published, epoch 0→1 triggered, external operators can connect, signed release artifacts publicly accessible. Target: Window 1429-1458 Track G. | Public RC is the first external publication event. All prior work is pre-public-RC. |
| **J-008 gate** | The production jury activation gate: 10 conditions that must all be MET before the production assignment machinery may be enabled. Currently: PASS (Phase 1427), `gate_authorized=True`. The gate evaluates via `evaluate_jury_activation_gate()` in `ilc_core/epistemic/jury_activation_gate.py`. | `gate_authorized=True` is the Phase 1427 PASS indicator. `production_activated` in the gate report is hardcoded False until execution surfaces are flipped live in Window 1429-1458. |
| **TransportPrincipal** | The authenticated principal abstraction that binds public HTTP/P2P/sidecar network paths to agent identity rather than IP or JSON body. The governance CDL (CDL-094) is assigned and will be opened in Window 1429-1458 Phase 1434. Currently all non-loopback binding is blocked pending ratification. | Use `TransportPrincipal` for the principal/policy abstraction. Use `CDL-094` for the specific governance instrument. |
| **Homoiconicity** | The property that ILC's governance and architecture are expressed as nodes in the same epistemic graph used for scientific claims. CDLs, ADRs, star maps, and activation certificates are graph nodes with the same CID-based identity and GOVERNS/CONSTRAINS/PROVENANCE edge structure as any other node. The protocol can reason about its own rules using its own verification machinery. | Do not use `homoiconic` to mean "self-referential" in a loose sense. It specifically means: governance artifacts are first-class graph nodes traversable by the same query and verification paths as content nodes. |
| **Hub relay** | A graph node or agent that relays provenance attribution chains: receives an attribution budget from upstream and distributes to downstream recipients. Conservation invariant: `sum(all_recipients) ≤ original_attribution_budget`. Three hub types: genuine (produces own provenance output), parasitic (routes without contributing), terminal (absorbs attribution, no further relay). Established SIM-PROVENANCE-02 (Phases 1419-1421). | Hub relay is a provenance-layer mechanism, not a network routing mechanism. |
| **Werner credit architecture** | The ECU issuance model: agents CREATE ECU through productive deployment within capacity limits authorized by Genesis/Treasury — Genesis does not mint ECU and push it to agents. Analogy: agents = commercial banks (create credit backed by deployment), Genesis/Treasury = central bank/regulator (authorizes capacity, adjusts pricing band via CDL-092 CapProof ±15%). Deliberately Werner-incomplete in ways appropriate to an agent-peer network (no structural feature for inter-bank deposits). See CDL-053 Werner local credit (narrow scope) for the implemented surface. | Use "Werner credit architecture" for the theoretical framing; "CDL-053 Werner local credit" for the ratified runtime contract. |
| **Inverted ECU / spend-to-keep** | The operating posture in which ECU is not accumulated as a badge of status but spent productively to demonstrate deployment velocity × quality. Participants begin with bounded working credit; productive deployment is the signal. Idle ECU decays (CDL-V1 temporal decay). Mandatory conversion windows (CDL-048, 4-epoch deadline) push ECU into settlement. The scarce resource is not ECU supply but review-lane access and reputation. | Use "inverted ECU" or "spend-to-keep doctrine" to describe this posture in design discussions. Not yet a ratified constitutional position; partially implemented via CDL-V1 and CDL-048. |
| **Sidecar** | An application component that attaches to an ILC node at the app-plane IPC boundary. Sidecars send signed typed payloads; the node core verifies the signature, anchors the CID, and settles ECU. App semantics live in the sidecar; the core stays minimal. Notable sidecars: private messaging (sealed sender), spectral beacon (λ_local emission, research), L3 apps (domain applications). | Use `sidecar` for any app-plane IPC component. Do not embed domain logic in the node core. |
| **OpenClaw** | The optional orchestration wrapper for multi-agent ILC workflows. Manages agent spawning, task routing, and context assembly. Not required for a minimal ILC node. Distinct from the node core — no CDL governance surface controlled by OpenClaw. | Use `OpenClaw` for the orchestration layer. A node operates correctly without it. |
| **Mysticeti / leaderless DAG** | The Tier 1 primary fast-path consensus protocol (CDL-062, Phase 693). Owned-object operations target sub-500ms finality; no single leader is required for progress. Shared-object settlement falls back to the epoch boundary path (1–3 seconds). BLS multi-sig aggregation (`ilc_consensus/src/validator.rs`) compresses quorum evidence to a single proof. TLA+ verification specs pending. | Use `Mysticeti` for the fast-path consensus protocol. Use `epoch settlement` for the shared-object slow path. |
| **ML-DSA-65** | Module Lattice DSA (NIST FIPS 204), the post-quantum signing algorithm used for Genesis-authority artifacts: activation certificate, root envelopes. Forward-safe against quantum adversaries. The production jury assignment machinery uses ML-DSA-65 for high-value signing surfaces. | Use `ML-DSA-65` when specifying the signing algorithm for Genesis-authority or post-quantum surfaces. |

---

## 3. Architectural Invariants

1.  **Peers are not Authorities**: A Peer is never the source of truth. The **Signed Graph Node** is the only source of truth. If a Peer modifies a Graph Node, the signature breaks, and the network rejects it.
2.  **Agents are Mobile**: An Agent can migrate from Peer A to Peer B. Its Reputation and History travel with it (because they are anchored in the Graph, not the Peer).
3.  **Sharding is Semantic**: We shard by *Topic* (Problem Space), not by *Address Hash*. This optimizes for "Epistemic Locality" (related ideas live together).

## 4. Implementation Guidelines (Phase 182+)

*   **Code Naming:**
    *   Use `PeerManager` instead of `NodeManager` for network connections.
    *   Use `GraphNode` or `Artifact` for data objects.
    *   Use `AgentIdentity` for the portable component, `AgentRuntime` for the local loop.
*   **Error Handling:**
    *   Exceptions must distinguish between "Network Errors" (Peer down) and "Graph Errors" (Invalid signature).

## 5. Discussed but Not Canonical (Informational Annex)

The terms below appear in historical dredge material and research discussion, but they are not currently ratified as canonical ILC architecture primitives.

| Term | Why Not Canonical Yet | Current Placement |
| :--- | :--- | :--- |
| **Markov Chain / Markov Reward Process** | Useful modeling language, but no ratified protocol dependency requires these formalisms. | Research / theory |
| **Topological Data Analysis (TDA)** | Promising for graph-shape analytics, but not required for core protocol operation. | Research / analytics |
| **Hypergraph / Simplicial Complex** | Richer structure candidates beyond current canonical graph/link model. | Research / future architecture |
| **PONTI / PORCC / POEG** | Historical acronym family appears in drafts but is not normalized in canonical protocol naming. | Historical drafts |
| **Graph Collapse / Semantic Compression** | Discussed as future optimization/settlement strategy, not ratified as mandatory primitive. | Optimization research |
| **Epistemic Geometry / Graph Geometry** | Valuable metaphor and potential future representation, not part of current canonical data contract. | Conceptual research |
| **Proof of Intelligence Work / Proof of Useful Work** | Legacy naming variants. Canonical direction is PoIL and explicit replay-proof contracts. | Historical terminology |
| **Quadratic Co-Stake** | Candidate economic mechanism with no ratified governance contract yet. | Tokenomics research |
| **Filecoin / Arweave mandatory integration** | Storage backends may be used, but protocol does not currently hard-require these networks. | Deployment option |
| **Protocol Council** | Governance role pattern appears in historical planning but has no ratified canonical role contract. | Governance research |
| **Adaptive Governance Voting** | Dynamic weighting/threshold mechanisms remain exploratory and non-ratified. | Governance research |
| **Graph Neural Networks (GNNs)** | Useful analytics family for graph scoring/embeddings, not required by canonical protocol operation. | Analytics research |
| **Graph Traversal Protocols** | Optimization candidates for retrieval/discovery; not canonical protocol primitives at present. | Optimization research |
| **Epistemic holon** | An agent-peer pair forming a self-similar epistemic unit with a public surface (admitted and consensus nodes visible to the network) and a private interior (local drafts, private-visibility nodes, local Werner credit not yet deployed through the review lane). Each holon is complete at its own scale while participating in the larger federation. Described in README §Deep architecture. No ratified ADR yet. | Architectural framing / morphogenetic hypergraph research. Now described in README. |
| **Federated Galaxy Model** | The topology in which multiple epistemic holons interconnect via the D2d gossip layer. Each holon exposes a public surface while retaining a private interior; the aggregate forms a distributed epistemic hypergraph. Described in README §Deep architecture. No ratified ADR yet. | Architectural framing / morphogenetic hypergraph research. Now described in README. |
| **Morphogenetic distributed hypergraph** | The architectural characterization of ILC as a whole: a distributed graph system whose organizational principles (refutability, provenance, epistemic pressure) repeat self-similarly at every scale — per-node, per-agent, per-cluster. "Morphogenetic" in the Levin/Turing sense: structure emerging from local rules propagating across a distributed substrate without global coordination. Described in README §Deep architecture. No ratified ADR yet. | Architectural framing / research — see RTF memo. Now described in README. |
| **Subgraph Homomorphism Invariant** | The query contract that when a subgraph is returned in response to a query, all edges between returned nodes must also be returned (structure-preserving). This is the mathematical basis for inter-agent subgraph queries behaving as graph homomorphisms rather than flat record dumps. Front-load obligation: gRPC proto must carry EdgeRecord before M-018 surface locks. No ratified ADR yet. | Protocol design / M-018 pre-commitment |
| **Normalized Hypergraph Laplacian (Δ)** | The matrix Δ = D_V^{-1/2} · H · W · D_E^{-1} · H^T · D_V^{-1/2}, encoding the full connectivity structure of the hypergraph in a real symmetric positive semi-definite form. Eigenvalues λ₁ ≤ λ₂ ≤ ... ≤ λ_n lie in [0,2]. The Fiedler value λ₂ is the algebraic connectivity — λ₂→0 signals approaching disconnection. Never stored explicitly; computed on demand from the sparse incidence index. Prerequisite: ADR-0029. | Mathematics / spectral substrate |
| **Spectral Hash S(t)** | SHA256(sort(top-k eigenvalues of Δ(t))). A 32-byte structural fingerprint of the hypergraph at epoch t, committed alongside the content Merkle root M(t) to form the dual commitment C(t) = (M(t), S(t)). Enables detection of structural Byzantine faults undetectable by content comparison alone. Requires CDL before inclusion in epoch commitment record. Research: `docs/research/ilc_spectral_intelligence_test_research_memo_v0.1.md`, `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md`. | Cryptographic protocol / research |
| **Merkle-Laplacian Dual Commitment** | The epoch commitment construction C(t) = (M(t), S(t)) pairing a content Merkle root with a spectral hash. Commits to both what the graph contains and how it is connected. Enables four new capabilities: Byzantine structural fault detection, Sybil cluster forensics, partition early warning, and PoSK. Novel — no prior distributed systems literature identified. Paper draft: `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md`. | Novel research contribution / cryptographic protocol |
| **Incremental Structural Proof Chain** | The verifiable sequence {(M(t), S(t))} with corresponding incremental Laplacian updates {ΔΔ(t)}, where each S(t) is derivable from S(t-1) + ΔΔ(t). The structural analogue of an incremental Merkle proof — proves topological evolution across epochs, not just content existence. O(k·d) per epoch where k = hyperedge changes, d = max hyperedge degree. | Novel research contribution / protocol |
| **Proof of Structural Knowledge (PoSK)** | An admission primitive in which a node demonstrates correct hyperedge synchronization by computing λ₂(t) of its local subgraph and submitting it as an epoch attestation. Correct λ₂ cannot be produced without actual knowledge of the current hyperedge structure. A new category alongside PoW and PoS — the first primitive that proves relational structural knowledge rather than computation time or economic stake. | Novel research contribution / admission primitive |
| **Spectral Beacon** | A sealed push signal carrying a node's local spectral fingerprint λ_local (top-k eigenvalues of its neighborhood Laplacian) without revealing specific node IDs, content, or neighbor identities. Emitted periodically via the D2d gossip layer under Signal-style sealed sender. Enables privacy-preserving epistemic neighborhood matching: two agents can discover structural proximity without exposing their subgraph contents. Substrate: requires ADR-0029 sparse incidence index + D2d sealed sender extension. | Novel research / privacy-preserving discovery |
| **Spectral Routing** | A graph traversal and discovery mechanism using spectral distance d(A,B) = ||λ_A − λ_B||₂ as the routing metric. Agents navigate toward peers whose neighborhood Laplacians are most similar to a target concept's structural neighborhood — greedy spectral descent toward epistemic proximity. Replaces broadcast queries (expensive, privacy-leaking) with targeted topological navigation. The star.map's homoiconic form becomes a spectral beacon directory in this model. Companion to sealed spectral beacons. Research: `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md` (companion paper candidate). | Novel research / graph traversal primitive |
| **Cognitive Light Cone Intersection** | The condition in which two agents' epistemic light cones overlap — they observe the same knowledge territory from different positions. Detectable via spectral beacon proximity (similar λ_local) without exposing light cone contents. Enables private discovery of collaborators working in the same epistemic neighborhood. Relates to existing `ilc_core/analysis/light_cone_kpis.py`. | Research / privacy-preserving discovery |

Reference list for broader historical lexicon: `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`.
