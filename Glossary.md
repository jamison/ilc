# ILC Glossary

ILC uses a precise technical vocabulary. Many terms collide with everyday language or with blockchain terminology — the definitions here are not decorative; they govern protocol behavior, code correctness, and economic reasoning.

The canonical authority for all ILC terminology, architectural definitions, and naming policy is:

**[`docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`](docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md)**

Status: RATIFIED — do not rename, move, or copy this file.
Referenced by 106+ locations across the repo (CLAUDE.md, AGENTS.md, ADRs, phase prompts).

---

## Key terms (quick reference)

| Term | Definition | Source |
|------|-----------|--------|
| **Graph Node** | Immutable, content-addressed protocol data unit — the epistemic object in the ILC hypergraph. Every claim, refutation, revision, and reuse is a Graph Node. | §2, table |
| **Peer** | A running ILC software instance (host/operator). Not a Graph Node. "Node" alone is ambiguous — always qualify. | §2, table |
| **Agent** | A protocol identity (key-derived, CDL-042/CDL-069). Agents are not serving peers — an agent can exist without running a peer process. | §2, table |
| **ECU** | Epistemic Compute Unit (*W_e = ΔH / E_cost*) — the unit of verified epistemic work. Created by verified labor through the jury system, reduced by temporal decay, converted to ILC only through activation-gated paths. Not a coin; not hoardable. | §2 |
| **ILC** | Intelligent Labor Coin — the scarce settlement token. Cap: 25,920,000 (one Platonic Year × 1,000). Produced from ECU only when the relevant activation gates authorize conversion. | §2 |
| **PoIL** | Proof of Intelligent Labor — canonical consensus-work term. A claim carries PoIL when it has provenance, evidence, review exposure, refutation history, and reuse weight. Not PoIW or "Proof of Useful Work". | §1.1 |
| **Truth primitive** | One of 7 canonical graph operations: `assert.truth`, `validate.claim`, `contradict.assert`, `refute.claim`, `revise.assert`, `link.claim`, `commit.epoch`. All graph knowledge compiles from these. | §2 |
| **Commit.Epoch** | Consensus boundary object (exact casing required). Consensus-layer only — not agent-issuable. Not "commit epoch" or "epoch commit event". | §1.1 |
| **HyperEdge** | An n-ary relationship in the ILC hypergraph: `(e, V_e, w_e, τ_e)` — edge ID, vertex set, weight, and type. First-class object, not derived from pairwise links. | §2:ADR-0029 |
| **Sidecar** | An application component at the app-plane IPC boundary. Sidecars send signed typed payloads; the node core verifies signatures, anchors CIDs, and settles ECU. App semantics live in the sidecar; the core stays minimal. | §2:167 |
| **Genesis Atlas** | The LMDB-backed graph metadata and content-addressing index. Stores node identity, topology, provenance edges, `source_sha256`, and typed edges — not raw file bytes. The authority for graph identity and relationships. | §2 |
| **Fiedler value (λ₂)** | The second-smallest eigenvalue of the normalized hypergraph Laplacian. Measures algebraic connectivity of the authority graph. Used as a structural integrity anomaly signal — not a cryptographic hardness claim. | §2:SECURITY.md |
| **CDL** | Constitutional Decision Log entry — the ratification vehicle for protocol-level decisions. A CDL is a first-class Graph Node, referenceable and refutable like any other. | §1.1 |
| **ADR** | Architecture Decision Record — records technical design decisions below the constitutional threshold. Like CDLs, ADRs are graph-native nodes. | §1.1 |
| **OpenClaw** | Optional orchestration wrapper for multi-agent ILC workflows. Not a protocol substrate; no CDL governance surface. | §2:168 |
| **TransportPrincipal** | Authenticated principal abstraction binding public network paths to agent identity. Governed by CDL-094. | §2:162 |

---

## Terminology collision rules

When multiple historical names exist, the canonical form defined in the glossary governs all new normative text, specs, ADRs, and code.

Non-canonical forms to avoid:
- "node" when referring to a running process → use **Peer**
- "artifact/node" for protocol data → use **Graph Node**
- "PoIW" or "Proof of Useful Work" → use **PoIL**
- "EveAgent" in identity context → use **Agent**

---

## Additional reference

- Comprehensive term inventory and lifecycle context: [`docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`](docs/reference/ilc_comprehensive_reference_glossary_v0.1.md)
- Sidecar CLI and architecture: [`sidecars.md`](sidecars.md)
- Canonical naming policy and promotion path for new terms: §1.1–§1.2 of the ratified glossary above
