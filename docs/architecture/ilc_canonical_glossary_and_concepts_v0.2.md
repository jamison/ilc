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

Reference list for broader historical lexicon: `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`.
