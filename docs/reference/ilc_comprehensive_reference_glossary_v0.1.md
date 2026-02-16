# ILC Comprehensive Reference Glossary v0.1

**Status:** DRAFT
**Date:** 2026-02-16
**Source:** Derived from "Constitution Dredge" (2024-2026 logs) and Historical Idea Scans.

## 1. Purpose
This document serves as an encyclopedic reference for **all** terms found in the ILC corpus, including scientific concepts, historical project metaphors, and proper names. Unlike the [Canonical Architecture Glossary](../architecture/ilc_canonical_glossary_and_concepts_v0.2.md), which defines strict protocol primitives, this document captures the broader *intellectual heritage* and *lexicon* of the project.

## 1.1 Status Legend (Lifecycle)
Use these status labels consistently across this reference glossary.

| Status | Meaning |
| :--- | :--- |
| **Canonical** | Ratified term in canonical architecture/protocol documents and actively used for implementation guidance. |
| **Canonical-adjacent** | Operationally important and repeatedly used in implementation/tests, but not yet declared a top-level canonical primitive. |
| **Research candidate** | Candidate term/mechanism with active technical interest but no ratified contract. |
| **Discussed, not included in current ILC core** | Present in historical corpus and design discussion, intentionally outside current core architecture. |
| **Historical** | Term used in prior phases/logs, retained for context and traceability. |
| **Deprecated / Rejected** | Term/mechanism explicitly replaced or dropped. |

## 1.2 Promotion Criteria and Workflow
A term should be promoted from reference status into canonical status only when all criteria below are met.

1. **Definition stability**: one precise definition with no unresolved collisions against existing canonical terms.
2. **Spec or ADR anchor**: term is explicitly defined in a ratified spec or ADR.
3. **Implementation anchor**: term maps to concrete code surfaces, schemas, or protocol messages.
4. **Verification anchor**: deterministic tests/guardrails enforce the intended contract.
5. **Phase traceability**: promotion is recorded in a walkthrough/STATUS entry with phase evidence.

Promotion workflow:
1. Add term here with provisional status (`Research candidate` or `Discussed, not included...`).
2. Reconcile in architecture notes or glossary reconciliation report.
3. Land spec/code/tests in a tracked phase.
4. Promote in `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`.
5. Back-link here and update status.

## 1.3 Synonym Reconciliation Policy
Prefer the canonical form in all new docs/code/comments. Legacy forms remain searchable but non-preferred.

| Preferred Canonical Term | Legacy / Alias Forms | Authoring Rule |
| :--- | :--- | :--- |
| **Proof of Intelligent Labor (PoIL)** | PoIW, Proof of Useful Work, Proof of Useful Intelligent Labor | Use **PoIL** in canonical and implementation-facing text. |
| **Graph Node** | Artifact (protocol object sense), node record | Use **Graph Node** for protocol data objects. |
| **Peer** | node (machine/process sense), host instance | Use **Peer** for running network software. |
| **Agent** | EveAgent (identity sense) | Use **Agent** for identity; reserve `EveAgent` for local runtime class references. |
| **Commit.Epoch** | commit epoch, epoch commit event | Use **Commit.Epoch** exactly when naming the canonical consensus boundary object. |
| **Receipt** | evidence receipt, attestation receipt | Use **Receipt** for the canonical proof artifact term. |
| **Shard** | token graph shard (legacy phrasing) | Use **Shard** with semantic/topic partition meaning. |
| **ECU** / **ILC** | compute-credit coin variants, IWC | Use **ECU** for internal compute accounting and **ILC** for settlement token. |

---

## 2. Scientific & Mathematical Concepts
*Terms from Physics, Information Theory, and Active Inference that underpin ILC theory.*

| Term | Definition | ILC Relevance |
| :--- | :--- | :--- |
| **Active Inference** | A framework (Friston) where agents act to minimize expected free energy (surprise). | **High**: The core theoretical model for ILC Agents. |
| **Entropy** | A measure of disorder or uncertainty. | **High**: ILC aligns token value with the *reduction* of epistemic entropy. |
| **Free Energy** | An information-theoretic quantity bounding surprise. | **High**: Agents are "Free Energy Minimizers". |
| **Markov Blanket** | A boundary that separates an internal state from the external world. | **Medium**: Defines the operational boundary of an Agent or Shard. |
| **Strange Loop** | A cyclic structure that acts as a self-referential system (Hofstadter). | **Low**: Metaphor for recursive governance. |

## 3. Project Lexicon & Metaphors
*Terms specific to the ILC project history and culture.*

| Term | Definition | Status |
| :--- | :--- | :--- |
| **Amazement** | A qualitative metric used in early project scans to rank ideas by novelty and "wow factor". | **Historical** |
| **Constitutional Dredge** | The massive excavation of 20,000+ lines of chat logs to recover lost ideas ("nuggets"). | **Active Process** |
| **Golden Thread** | A metaphor for a coherent, unbroken line of reasoning or provenance through the graph. | **Active Metaphor** |
| **Nugget** | A discrete, valuable idea recovered from historical logs. | **Historical** |
| **Idea Scan** | The process of frequency analysis and thematic clustering of project logs. | **Historical** |
| **Epistemic Graph** | The global network of knowledge (Claims, Refutations) that strictly precedes the ledger. | **Canonical** |
| **Proof of Intelligent Labor (PoIL)** | The consensus mechanism where work is validated by its *epistemic utility* (truth-seeking). | **Canonical** |
| **Truth Primitives** | Fundamental node types (Assert, Refute) that cannot be removed, only extended. | **Canonical** |

## 4. Proper Names & Key Figures
*Entities and people referenced in the corpus.*

| Name | Role/Context |
| :--- | :--- |
| **Satoshi Nakamoto** | Creator of Bitcoin. Cited frequently as the model for "Genesis" behavior (silence, immutability). |
| **Karl Friston** | Neuroscientist. Father of the Free Energy Principle. Theoretical inspiration. |
| **Douglas Hofstadter** | Author of *Gödel, Escher, Bach*. Influence on "Strange Loop" concepts. |
| **Genesis** | The founding identity of ILC. Not a person but a *Role* with specific soft powers (e.g., calling votes). |

## 5. Historical / Deprecated Terms
*Terms found in old logs that have been replaced or refined.*

| Term | Replaced By | Notes |
| :--- | :--- | :--- |
| **Artifact** | **Graph Node** | "Artifact" is now a general file term; "Graph Node" is the strict protocol term. |
| **ICU (ILC Compute Unit)** | **TBD** | Early concept for standardizing work. Still in research (Phase 190+). |
| **Token Graph Sharding** | **Topic Sharding** | Refined to emphasize semantic locality over graph topology. |


## 6. Extracted Terminology Candidates (Automated Dredge)
*The following terms were extracted from the Constitution Dredge Matrix and await formal definition.*

Term-by-term elevation planning and lane assignment are tracked in:
- `docs/architecture/glossary_term_elevation_matrix_v0.1.md` (Section 6.1 baseline pass),
- `docs/architecture/glossary_term_elevation_matrix_v0.2.md` (Sections 9.1, 9.3, and 10 extension pass).

### Concepts & Mechanisms
- **Context Packs**: Canonical, reproducible documentation/context bundles.
- **Court Certification**: The 7+1 auditor panel verification step in governance.
- **Epistemic Lineage Anchoring**: Early nodes establishing the "bedrock" for trust weight.
- **Epistemological Purism**: The principle that truth must be public, verifiable, and reproducible.
- **Evidence Submission**: The requirement for cryptographically verifiable data in challenges.
- **Genesis Attention Broadcast (GAB)**: A soft-power mechanism for Genesis to trigger network-wide votes.
- **Graph Anchoring**: The requirement for opaque nodes to link to transparent public nodes.
- **Intelligent Labor**: The core unit of value in ILC (epistemic work).
- **Lawfulness**: The support for modular legal subgraphs and jurisdictional constraints.
- **Minimal Theoretic Core**: The design philosophy of minimizing hardcoded truths.
- **Namespace Deprecation Protocol**: The governance process for archiving malicious namespaces.
- **Passive Observation Feeds**: Canonical feeds for observation/star maps.
- **Philosophical Relativism**: The acknowledgment of multiple valid forks of reality (refuted by ILC's forward arrow of consolidated truth).
- **Protocol Critical**: Components affecting NodeIDs, signatures, and consensus.
- **Provenance**: The chain of signed promotions and endorsements.
- **Quality Floor**: The minimum quality ($q$) required to mint standard units.
- **Rate of Adaptation**: The system's ability to evolve without centralized retraining.
- **Receipts Schema**: Canonical fields for evidence and payout trails.
- **Spec Oracle**: The requirement for new chain implementations to replicate SIM behaviors.
- **Task Routing Protocol (TRP)**: The lifecycle and sharding logic for tasks.
- **Token Graph Sharding**: The distribution of the token ledger across the graph (concept).
- **Trusted Verifier Safeguards**: Mechanics to ensure verifier integrity.
- **Truth Ledger**: The storage of verified proofs and PoIL submissions.

### System Variables & Technical Terms
- `access_fee_ilc`
- `compute_node_load_metrics`
- `execution_payload`
- `finalization_state`
- `ilc_emission_model`
- `max_decoy_rate`
- `max_duration`
- `max_throttle`
- `node_structure`
- `obj_cert`
- `previous_version_ref`
- `quadratic_co_stake`
- `refinement_score`
- `rep_min`
- `rolled_back`
- `routed_tasks_to_task_rows_dicts`
- `stake_multiplier_cap`
- `weighted_count`
- `write_fee_multiplier`

### Acronyms
- **ADR**: Architectural Decision Record.
- **CID**: Content Identifier (IPFS/Merkle).
- **COSE**: CBOR Object Signing and Encryption.
- **DSL**: Domain Specific Language.
- **ECU**: Epistemic Compute Unit.
- **GDPR**: General Data Protection Regulation (relevant to node operator identity).
- **IWC**: Intelligent Work Coin (historical synonym for ILC).
- **KPI**: Key Performance Indicator.
- **NDJSON**: Newline Delimited JSON.
- **UTXO**: Unspent Transaction Output (ledger model).
- **VRF**: Verifiable Random Function.


## 7. Raw Ledger Frequency Analysis (Top Terms)
*Terms appearing most frequently across the 22,194 raw historical records (Constitution Dredge Raw).*

### Core Entities & Metrics
- **ILC** (12,007 citations)
- **MVP** (1,062)
- **ECU** (999)
- **EVE** (372)
- **GPU** (329)
- **Intelligent Labor Coin** (195)
- **Intelligent Labor** (57)
- **Genesis Truth Primitives** (39)
- **Epistemological Graph** (13)

### System Components
- **Principle List** (242)
- **Master Principle List** (153)
- **Namespace Hierarchy** (38)
- **Genesis Node Era** (38)
- **Clearing Price Probe** (13)
- **Pricing Integrity Pass** (17)
- **Governance Config Surface** (13)
- **Labor Graph** (12)
- **Arc Architecture** (12)
- **Reward Surface** (12)
- **Node Load Metrics** (30)

### Technical Terminology
- **DAG** (226)
- **CBOR** (145)
- **NDJSON** (123)
- **KDL (Knowledge Definition Language)** (76)
- **CID** (58)
- **COSE** (54)
- **NVML** (16)

## 8. Rejected / Deprecated Concepts (Constitution Drop Ledger)
*Concepts explicitly triaged as 'out of scope' or 'dropped' during the Constitutionalization phase.*

- **Token Graph Sharding**: Replaced by semantic Topic Sharding.
- **Passive Observation Feeds**: Dropped in favor of active canonical signaling.
- **Epistemological Purism**: The idea that truth must be absolute; replaced by pragmatic verification.
- **Distributed Internet of Tokens**: Too broad/marketing-focused.
- **Foundational Papers Compendium**: Deferred to later roadmap.
- **Graph Traversal Protocols**: Considered L2/Optimization, not L1.
- **Resolution Strategy**: Specific mechanism replaced by general Disputability.
- **Ethics Supports**: Dropped as a specific module name.

## 9. Raw Dredge Expansion Pass (2026-02-16)
*This pass parsed `docs/research/constitution_dredge_raw_v0.1.jsonl` (22,194 records) and promoted additional high-signal terms into this reference glossary.*

### 9.1 Added Terms (Broader Historical Lexicon)

| Term | Definition | Status |
| :--- | :--- | :--- |
| **Markov Chain** | A stochastic process where the next state depends only on the current state. | **Discussed, not included in current ILC core** |
| **Markov Reward Process (MRP)** | A Markov chain augmented with reward signals used in sequential decision modeling. | **Discussed, not included in current ILC core** |
| **Topological Data Analysis (TDA)** | A family of methods that studies shape and connectivity of data using topology. | **Discussed, not included in current ILC core** |
| **Hypergraph** | A graph generalization where one edge can connect more than two nodes. | **Discussed, not included in current ILC core** |
| **Simplicial Complex** | A higher-order topological structure used to represent multi-way relations. | **Discussed, not included in current ILC core** |
| **Graph Collapse** | Historical concept for reducing large labor/claim graphs into compact settlement representations. | **Research candidate** |
| **Semantic Compression** | Compression of graph/state by preserving epistemically relevant structure rather than raw events. | **Research candidate** |
| **Epistemic Geometry** | The idea of representing validated graph state as geometric/structured summaries. | **Discussed, not included in current ILC core** |
| **Graph Geometry** | Historical term for geometric abstractions built from graph topology and validation outputs. | **Discussed, not included in current ILC core** |
| **Convergent Consensus** | Consensus framing where independent validators converge on equivalent outcomes. | **Discussed, not included in current ILC core** |
| **PONTI** | Historical acronym used in some drafts for task execution/proof stages. | **Discussed, not included in current ILC core** |
| **PORCC** | Historical acronym used in some drafts for convergence/quorum validation phases. | **Discussed, not included in current ILC core** |
| **POEG** | Historical acronym used in some drafts for graph-to-geometry collapse stages. | **Discussed, not included in current ILC core** |
| **Quorum** | A minimum validator subset required for a decision to be considered valid. | **Canonical-adjacent** |
| **Slashing** | Economic penalty for provably bad behavior by staked actors. | **Canonical-adjacent** |
| **Staking** | Economic collateral posted by agents/operators to align incentives and absorb penalties. | **Canonical-adjacent (active contract)** |
| **Proof of Useful Work** | Work validation framing where only useful verified outputs are rewarded. | **Historical synonym / discussed** |
| **Proof of Intelligence Work** | Early term (PoIW) used for intelligence-bound production proofs. | **Historical synonym / discussed** |
| **Proof of Useful Intelligent Labor** | Expanded phrase used in historical drafts for utility-validated labor proofs. | **Historical synonym / discussed** |
| **Proof of Reputation** | Historical phrase for weighting or gating activity by reputation-backed trust. | **Discussed, not included as strict primitive** |
| **Task Quota** | Historical concept limiting task throughput per epoch/window to control emissions. | **Discussed, not included in current ILC core** |
| **Token Sink** | Any mechanism that removes circulating tokens (e.g., burns, fees, lockups). | **Canonical-adjacent** |
| **Rollup** | L2 construction where execution is batched off-chain and commitments are posted to a base layer. | **Discussed, not included in current ILC core** |
| **Smart Contract** | On-chain programmable logic for deterministic state transition and enforcement. | **Canonical-adjacent** |
| **System Maintainer** | Historical role label for infrastructure operators providing availability and validation services. | **Discussed, not included in current ILC core** |
| **Block Composer** | Historical role label for actors assembling validated outputs into settlement-ready structures. | **Discussed, not included in current ILC core** |
| **Validator** | Actor/role that verifies claims, tasks, or settlement artifacts under protocol rules. | **Canonical-adjacent** |
| **Backwards Verifiability** | Ability to replay and re-verify state from earlier history or genesis checkpoints. | **Canonical-adjacent (active contract)** |
| **Epistemological Addressing** | Historical term for addressing schemes tied to claim semantics/provenance. | **Discussed, not included in current ILC core** |
| **Thermodynamic Economy** | Metaphor describing PoW-style systems where value tracks energy expenditure. | **Discussed metaphor** |
| **Epistemic-Geometry Economy** | Historical metaphor describing ILC as value from verified intelligence structure rather than pure energy burn. | **Discussed metaphor** |
| **Filecoin** | Decentralized storage network often discussed as archival substrate candidate. | **Discussed, not included in current ILC core** |
| **Arweave** | Permanent-data storage network discussed for durable record anchoring. | **Discussed, not included in current ILC core** |
| **Quadratic Co-Stake** | Candidate economic weighting idea where co-staked influence scales non-linearly. | **Discussed, not included in current ILC core** |

### 9.2 Mined Frequency Signals (Selected)
*Selected term counts from the 2026-02-16 parse pass, used as prioritization hints for future glossary promotion.*

- **governance** (~6,601)
- **stake / staking** (~2,131 / ~1,981)
- **consensus** (~1,722)
- **namespace** (~1,478)
- **reputation** (~1,352)
- **quorum** (~705)
- **slashing** (~534)
- **DAG** (~517)
- **capsule** (~391)
- **star map** (~364)
- **NDJSON** (~330)
- **CBOR** (~325)
- **commit.epoch** (~322)
- **PoIL** (~234)
- **rollup** (~175)
- **CID** (~137)
- **COSE** (~97)
- **VRF** (~96)
- **tokenomics** (~95)
- **Markov Chain** (low frequency but present and historically relevant)

### 9.3 Added Terms (Protocol and Runtime Lexicon, Curation Pass B)
*Second curation pass over `constitution_dredge_raw_v0.1.jsonl` to promote recurrent implementation and architecture language into explicit definitions.*

| Term | Definition | Status |
| :--- | :--- | :--- |
| **Node ID** | Deterministic identifier used to reference a Graph Node across serialization, validation, and replay boundaries. | **Canonical-adjacent (active contract)** |
| **Canonical Encoding** | Deterministic serialization constraints that ensure identical content hashes and replay outcomes across implementations. | **Canonical-adjacent (active contract)** |
| **Deterministic CBOR** | CBOR encoding profile constrained for stable byte output and cross-runtime hash parity. | **Canonical-adjacent (active contract)** |
| **Canonical JSON** | JSON normalization discipline used where CBOR is unavailable, preserving deterministic field/value interpretation. | **Canonical-adjacent** |
| **Directed Acyclic Graph (DAG)** | A graph structure without cycles, used as a mental model for causality/order in knowledge dependencies. | **Discussed, not included in current ILC core** |
| **Directed Node** | Historical phrase for an explicitly linked/typed node; retained for traceability but superseded by canonical Graph Node language. | **Historical** |
| **Namespace Hierarchy** | Structured namespace layering used for governance boundaries, compatibility, and modular extension. | **Canonical-adjacent** |
| **Task Routing Protocol (TRP)** | Routing lifecycle for dispatching workloads/tasks to appropriate execution/verifier paths. | **Canonical-adjacent (active contract)** |
| **Reward Surface** | Function family mapping verified work quality and policy constraints into payout outcomes. | **Canonical-adjacent** |
| **Epoch Reward Ledger** | Per-epoch accounting surface recording validated reward events and settlement inputs. | **Canonical-adjacent** |
| **Node Load Metrics** | Runtime load measurements (for example compute, queue, throughput) used in balancing and policy tuning. | **Canonical-adjacent** |
| **Graph KPIs** | Aggregated graph/network indicators used for diagnostics, governance tuning, and release gating evidence. | **Canonical-adjacent (active contract)** |
| **Governance Config Surface** | The explicit set of configurable governance parameters exposed for policy control and versioned evolution. | **Canonical-adjacent** |
| **Protocol Council** | Historical governance role label for a bounded reviewer set; not yet a ratified canonical role primitive. | **Discussed, not included in current ILC core** |
| **Devnet Topology** | Explicit peer/agent arrangement used in simulation and development-network validation. | **Canonical-adjacent (active contract)** |
| **Consensus Engine** | Runtime component that applies validation and settlement rules to produce accepted state transitions. | **Canonical-adjacent (active contract)** |
| **Agent Communication Protocol** | Message and interaction contract space for agent-to-agent coordination and delegation flows. | **Research candidate** |
| **Node Indexing** | Index structures that accelerate retrieval/traversal compared with full-scan edge walks. | **Canonical-adjacent (active contract)** |
| **Graph Neural Networks (GNNs)** | Neural methods that operate on graph-structured data for prediction/embedding tasks. | **Discussed, not included in current ILC core** |
| **Graph Traversal Protocols** | Candidate protocol-layer traversal strategies discussed for optimization and discovery, not yet ratified as core primitives. | **Discussed, not included in current ILC core** |
| **Adaptive Governance Voting** | Dynamic governance weighting/threshold ideas that adapt to context or recent behavior. | **Research candidate** |
| **Propagation Bounty** | Historical incentive concept rewarding rapid/verified dissemination of important graph updates. | **Discussed, not included in current ILC core** |
| **Advanced Graph Structures** | Umbrella label for richer representations beyond the current canonical link model (for example hypergraph-like encodings). | **Discussed, not included in current ILC core** |

### 9.4 Curation Pass B Frequency Signals (Selected)
*Additional parse signals used to prioritize term inclusion in Section 9.3.*

- **Genesis Agent** (~152)
- **Directed Node** (~100)
- **Node ID** (~58)
- **Graph KPIs** (~50)
- **Canonical Encoding** (~43)
- **Node Load Metrics** (~30)
- **Epoch Reward Ledger** (~25)
- **Task Routing Protocol** (~12)
- **Graph Neural Networks** (~19)
- **Graph Traversal Protocols** (~10)
- **Adaptive Governance Voting** (~14)

## 10. Discussed, Not Included in Current ILC Core (Index)
*Quick index for terms that appear in the historical corpus but are not currently ratified as canonical architecture primitives.*

- **Markov Chain**
- **Markov Reward Process**
- **Topological Data Analysis (TDA)**
- **Hypergraph / Simplicial Complex**
- **PONTI / PORCC / POEG**
- **Graph Collapse / Semantic Compression** (as strict protocol primitive)
- **Epistemic Geometry / Graph Geometry** (as settlement primitive)
- **Proof of Intelligence Work / Proof of Useful Work** (legacy naming forms)
- **Quadratic Co-Stake**
- **Filecoin / Arweave integration assumptions**
- **Graph Neural Networks (GNNs)**
- **Graph Traversal Protocols**
- **Protocol Council** (as strict canonical role)
- **Propagation Bounty**
- **Advanced Graph Structures**

---
*Note: This is a living document. Add new terms as they are encountered in the Dredge or new research phases.*
