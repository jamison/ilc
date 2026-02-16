# Glossary Candidate Reconciliation Report

**Source**: `docs/research/constitution_dredge_matrix_v0.2.md` (Constitutional Dredge)
**Target**: `docs/architecture/ilc_canonical_glossary_and_concepts_v0.1.md`
**Date**: 2026-02-16

## 1. Executive Summary
This report analyzes 300+ historical "nuggets" to reconcile architectural terminology.
- **Alignment**: Historical use of "Shard" and "Agent" basics aligns with the new "Topological" and "Identity" definitions.
- **Gaps**: Several crucial data structures ("Capsule", "Commit.Epoch") are well-defined in history but missing from the current Glossary v0.1.
- **Conflicts**: The term "Artifact" is used loosely in history; we must formally define it to avoid confusion with "Graph Node".

## 2. Reconciled Terms (Existing in v0.1)

| Term | Historical Context (Dredge) | Current Canon (v0.1) | Status |
| :--- | :--- | :--- | :--- |
| **Shard** | "Private/Gated Shard", "Client chooses shard_id" | **Topology**: A logical partition of the Graph. | ✅ **Aligned**. Retain "Topic/Community Partition" definition. |
| **Agent** | "Genesis Agent", "Agent ID" | **Identity**: An actor with keys/reputation. | ✅ **Aligned**. |
| **Graph Node** | "Claim Node", "Refutation Node" | **Data**: Immutable data unit. | ✅ **Aligned**. |

## 3. New Candidates (To Add to v0.2)

These terms appear frequently in the "Idea Scans" as critical primitives but are currently absent from the Glossary.

### 3.1 Capsule
- **Dredge ref**: "Capsule must be valid and test-signed" (Rank #1 Idea), "Context Packs must be small, canonical capsules".
- **Proposed Definition**: A **Portable Container** for a set of related Graph Nodes (e.g., a "context pack" or a "genesis state"). It is the unit of *transport* between Peers, whereas a "Graph Node" is the unit of *linking*.
- **Action**: **Promote to Glossary**.

### 3.2 Commit.Epoch
- **Dredge ref**: "Settlement must be canonical at commit.epoch", "commit.epoch is a truth primitive".
- **Proposed Definition**: A specialized **Graph Node** (Type: `event`) that marks a consensus boundary or time-step. It acts as a "heartbeat" for the network.
- **Action**: **Promote to Glossary**.

### 3.3 Receipt
- **Dredge ref**: "Receipts schema: canonical fields for evidence...".
- **Proposed Definition**: A cryptographic proof of an off-chain action (e.g., "I ran this inference"). It is a subtype of **Graph Node** (or a payload within one).
- **Action**: **Promote to Glossary** (as `Evidence/Receipt`).

## 4. Conflict Resolution: "Artifact" vs "Node"

- **Historical Use**: "Artifact Format Optimization", "Genesis-signed artifacts". Used generically to mean "files" or "data objects".
- **Current Ambiguity**: Is an "Artifact" a *file* (like this report) or a *Graph Node*?
- **Resolution**:
    - **Graph Node**: The strict, protocol-level data unit (in JSON-LD).
    - **Artifact**: A *general* term for any file or document (including PDF reports, code files, OR Graph Nodes).
    - **Constraint**: In *Architecture* docs, distinctively use **"Graph Node"** for protocol objects. Use "Artifact" only for generic file management.

## 5. Implementation Path
1.  **Approve** this report.
2.  **Edit** `docs/architecture/ilc_canonical_glossary_and_concepts_v0.1.md`:
    - Add "Capsule", "Commit.Epoch", "Receipt".
    - Add a "Disambiguation" note for "Artifact".
    - Bump version to **v0.2**.

## 6. Follow-up Curation Pass (Raw Dredge, 2026-02-16)

After the initial reconciliation, a second parse/curation pass over
`docs/research/constitution_dredge_raw_v0.1.jsonl` promoted additional
high-signal terms into the reference glossary.

### 6.1 Newly Elevated Reference Terms
- `Node ID`
- `Canonical Encoding`
- `Deterministic CBOR`
- `Task Routing Protocol (TRP)`
- `Reward Surface`
- `Epoch Reward Ledger`
- `Node Load Metrics`
- `Graph KPIs`
- `Governance Config Surface`

These are now treated as **canonical-adjacent** in
`docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`.

### 6.2 Explicitly Non-Canonical (Still Research/Historical)
- `Graph Neural Networks (GNNs)`
- `Graph Traversal Protocols`
- `Protocol Council` (as a strict role primitive)
- `Adaptive Governance Voting`
- `Propagation Bounty`

These are kept in the "Discussed, not included in current ILC core" lane
until ratified by spec/ADR + implementation + deterministic tests.
