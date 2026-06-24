# ILC Glossary

The canonical authority for all ILC terminology, architectural definitions, and naming policy is:

**[`docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`](docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md)**

Status: RATIFIED — do not rename, move, or copy this file.
Referenced by 106+ locations across the repo (CLAUDE.md, AGENTS.md, ADRs, phase prompts).

---

## Key terms (quick reference)

| Term | Definition | Source |
|------|-----------|--------|
| **Graph Node** | Immutable, content-addressed protocol data unit — the epistemic object in the ILC hypergraph. | §2, table |
| **Peer** | A running ILC software instance (host/operator). Not a Graph Node. | §2, table |
| **Agent** | A protocol identity (key-derived, CDL-042/CDL-069). Not a serving peer. | §2, table |
| **Sidecar** | An application component that attaches to an ILC node at the app-plane IPC boundary. Sidecars send signed typed payloads; the node core verifies the signature, anchors the CID, and settles ECU. App semantics live in the sidecar; the core stays minimal. Notable sidecars: private messaging (sealed sender), spectral beacon, L3 domain apps. Do not embed domain logic in the node core. | §2:167 |
| **ECU** | Epistemic Compute Unit — the unit of verified epistemic work. | §2 |
| **PoIL** | Proof of Intelligent Labor — canonical consensus-work term. Not PoIW or "Proof of Useful Work". | §1.1 |
| **Commit.Epoch** | Consensus boundary object (exact casing required). Not "commit epoch" or "epoch commit event". | §1.1 |
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
