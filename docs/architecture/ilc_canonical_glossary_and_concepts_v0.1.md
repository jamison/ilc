# ILC Canonical Architecture and Glossary v0.1

**Status:** RATIFIED
**Date:** 2026-02-16
**Version:** 0.1

## 1. Purpose
To resolve terminology collisions between the "Epistemic Graph" (Data) and the "P2P Network" (Infrastructure). This document is the single source of truth for architectural definitions.

## 2. Core Definitions

### 2.1 The Two "Nodes"
We strictly distinguish between the **Data** (eternal) and the **Machine** (ephemeral).

| Term | Context | Definition | Analogy |
| :--- | :--- | :--- | :--- |
| **Graph Node** | Epistemic | An immutable, content-addressed data artifact (Claim, Refutation, Star Map). It exists independently of any server. | A Book |
| **Peer** | Network | A running software instance (process) with an IP address, storage, and event loop. It hosts Agents and syncs Shards. | A Library / Server |

> **Canon Rule:** In all future documentation and code, "Node" unqualified implies **Graph Node** (the idea). The software machinery must be referred to as a **Peer**, **Host**, or **Instance**.

---

### 2.2 Identity and Agency

| Term | Context | Definition | Analogy |
| :--- | :--- | :--- | :--- |
| **Agent** | Identity | An intelligent actor (LLM, Human, or Script) possessing a Keypair and Reputation. It authors Graph Nodes. It is software-agnostic and mobile. | The Author |
| **Wallet** | Economics | The ledger entry tracking an Agent's ECU balance and Stake. Tied to the Agent's identity, not the Peer. | Bank Account |

> **Canon Rule:** An `EveAgent` class in Python is merely a *local runtime adapter* for an Agent. The Agent itself is the identity (the Keypair).

---

### 2.3 Topology and Scaling

| Term | Context | Definition | Analogy |
| :--- | :--- | :--- | :--- |
| **Shard** | Data Topology | A logical partition of the Epistemic Graph defined by topic or problem space (e.g., "Biotech", "Math"). | Library Section |
| **Cluster** | Governance | A set of Peers operating under a shared Constitution (e.g., "Cluster A" = Genesis Rules). | Legal Jurisdiction |
| **Gossip** | Transport | The protocol by which Peers exchange Graph Nodes. | Book Delivery |

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
