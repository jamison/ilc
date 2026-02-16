# Glossary Term Elevation Matrix v0.2

Status: Draft planning artifact  
Date: 2026-02-16  
Scope: Extension of `docs/architecture/glossary_term_elevation_matrix_v0.1.md` to cover:
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md` Section `9.1`,
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md` Section `9.3`,
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md` Section `10`.

## 1. Method (same gates as v0.1)

Each term is evaluated against:
- constitutional fit and ratifiability,
- architecture and implementation alignment,
- leverage and timing,
- lane assignment (`Now`, `Near`, `Later`, `Reject`),
- target layer (`L0`, `L1`, `L2`, `L3`).

## 2. Carry-Forward Baseline

The Section `6.1` ("Concepts & Mechanisms") term-by-term matrix in
`docs/architecture/glossary_term_elevation_matrix_v0.1.md` remains in force.
This file adds the same analysis style for Sections `9.1`, `9.3`, and `10`.

## 3. Section 9.1 Added Terms (Broader Historical Lexicon)

| Term | Current Corpus State | Canonical Mapping / Alias | Gate Outcome | Proposed Lane | Target Layer | Evidence Anchors | Recommended Next Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Markov Chain | Discussed, not included in core | Analytics formalism (non-protocol) | Keep as research model, not protocol primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:220`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:100` | Optional research note for KPI/forecast modeling only |
| Markov Reward Process (MRP) | Discussed, not included in core | Analytics formalism (non-protocol) | Keep as research model, not protocol primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:221`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:100` | Optional research note for reward-policy simulation |
| Topological Data Analysis (TDA) | Discussed, not included in core | Advanced analytics extension | Keep as optional analytics track | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:222`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:101` | Analytics ADR only if a concrete KPI need appears |
| Hypergraph | Discussed, not included in core | Future structure beyond current link model | Keep as research candidate | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:223`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:102` | Architecture options memo for post-canonical graph extensions |
| Simplicial Complex | Discussed, not included in core | Future structure beyond current link model | Keep as research candidate | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:224`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:102` | Pair with hypergraph options memo |
| Graph Collapse | Research candidate | Optimization/settlement compression track | Keep as optimization research, not mandatory primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:225`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:104` | Compression experiment brief with replay-parity constraints |
| Semantic Compression | Research candidate | Optimization/settlement compression track | Keep as optimization research, not mandatory primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:226`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:104` | Compression experiment brief with deterministic re-expansion checks |
| Epistemic Geometry | Discussed, not included in core | Conceptual representation family | Keep conceptual; do not treat as current settlement primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:227`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:105` | Concept note only |
| Graph Geometry | Discussed, not included in core | Conceptual representation family | Keep conceptual; do not treat as current settlement primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:228`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:105` | Concept note only |
| Convergent Consensus | Discussed, not included in core | Informal framing of deterministic consensus agreement | Retain as explanatory language; no new primitive | Near | L1/L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:229` | Terminology note under consensus docs to avoid duplicate semantics |
| PONTI | Historical acronym | Historical only | Keep as historical alias, not canonical naming | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:230`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:103` | None |
| PORCC | Historical acronym | Historical only | Keep as historical alias, not canonical naming | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:231`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:103` | None |
| POEG | Historical acronym | Historical only | Keep as historical alias, not canonical naming | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:232`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:103` | None |
| Quorum | Canonical-adjacent | Governance threshold primitive | Promote to canonical-adjacent governance terminology | Near | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:233`; `docs/specs/ilc_constitutional_decision_log_v0.1.md:42` | Governance threshold glossary/spec paragraph |
| Slashing | Canonical-adjacent | Penalty/economic deterrence primitive | Promote to canonical-adjacent economics terminology | Near | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:234` | Economics glossary/spec section for penalty flows |
| Staking | Canonical-adjacent | Collateral/incentive primitive | Promote to canonical-adjacent economics terminology | Now | L1/L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:235` | Add staking definition to canon-adjacent economics lexicon |
| Proof of Useful Work | Historical synonym | Alias of PoIL | Do not promote legacy name; enforce PoIL naming | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:236`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:17` | Naming hygiene check in docs lint pass |
| Proof of Intelligence Work | Historical synonym | Alias of PoIL | Do not promote legacy name; enforce PoIL naming | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:237`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:106` | Naming hygiene check in docs lint pass |
| Proof of Useful Intelligent Labor | Historical synonym | Alias of PoIL | Do not promote legacy name; enforce PoIL naming | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:238`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:17` | Naming hygiene check in docs lint pass |
| Proof of Reputation | Discussed, not strict primitive | Candidate governance/reputation weighting concept | Keep as research term pending strict ratification | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:239` | Governance/economics ADR if selected for formal weighting |
| Task Quota | Discussed, not included in core | Emission/throughput policy concept | Keep as policy candidate, not base primitive | Later | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:240` | Policy-layer quota experiment notes |
| Token Sink | Canonical-adjacent | Emission control/economic balancing concept | Keep and stage with tokenomics ratification | Near | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:241` | Tokenomics section clarifying sink semantics |
| Rollup | Discussed, not included in core | External settlement scaling option | Keep as integration option, not required core primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:242` | Optional integration profile doc |
| Smart Contract | Canonical-adjacent | External programmable settlement surface | Keep as deployment option, not mandatory base-layer primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:243` | Optional integration profile doc |
| System Maintainer | Discussed, not included in core | Best mapped to `Peer` operator role | Keep as historical alias only | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:244`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:20` | None |
| Block Composer | Discussed, not included in core | Historical role alias | Keep as historical alias only | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:245` | None |
| Validator | Canonical-adjacent | Verification role family (auditor/verifier) | Promote as canonical-adjacent role term | Near | L1/L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:246` | Role taxonomy note in governance spec |
| Backwards Verifiability | Canonical-adjacent (replay-proof line) | Replay/re-verification invariant | Promote as explicit replay-proof invariant | Now | L1 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:247` | Replay-proof invariant clause in protocol glossary |
| Epistemological Addressing | Discussed, not included in core | Historical addressing concept | Keep as research language; no current primitive | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:248` | Addressing concept memo only |
| Thermodynamic Economy | Discussed metaphor | Historical metaphor | Keep as metaphor only, not architecture primitive | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:249` | None |
| Epistemic-Geometry Economy | Discussed metaphor | Historical metaphor | Keep as metaphor only, not architecture primitive | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:250` | None |
| Filecoin | Discussed, not included in core | Optional storage backend integration | Keep as optional deployment path | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:251`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:108` | Integration assumptions appendix |
| Arweave | Discussed, not included in core | Optional storage backend integration | Keep as optional deployment path | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:252`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:108` | Integration assumptions appendix |
| Quadratic Co-Stake | Discussed, not included in core | Candidate non-linear governance/economic weighting | Keep as research candidate pending ratification | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:253`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:107` | Tokenomics experiment ADR before any protocol commitment |

## 4. Section 9.3 Added Terms (Protocol and Runtime Lexicon, Curation Pass B)

| Term | Current Corpus State | Canonical Mapping / Alias | Gate Outcome | Proposed Lane | Target Layer | Evidence Anchors | Recommended Next Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Node ID | Canonical-adjacent | Deterministic graph identifier | Promote as active canon-adjacent protocol term | Now | L1 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:284` | Add compact canonical naming note in protocol glossary |
| Canonical Encoding | Canonical-adjacent | Deterministic serialization invariant | Promote as active canon-adjacent protocol term | Now | L1 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:285` | Canonical encoding checklist in conformance docs |
| Deterministic CBOR | Canonical-adjacent | Stable byte-level encoding profile | Promote as active canon-adjacent protocol term | Now | L1 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:286` | CBOR determinism conformance appendix |
| Canonical JSON | Canonical-adjacent | Deterministic fallback normalization profile | Keep as fallback profile; clarify non-primary role vs CBOR | Near | L1 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:287` | Canonical JSON fallback constraints note |
| Directed Acyclic Graph (DAG) | Discussed, not included in core | Mental model only, not strict primitive contract | Keep as explanatory term, not ratified primitive | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:288` | None |
| Directed Node | Historical | Historical alias superseded by `Graph Node` | Keep historical only | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:289`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:13` | None |
| Namespace Hierarchy | Canonical-adjacent | Governance and compatibility namespace layering | Keep and stage with namespace governance work | Near | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:290` | Namespace governance/deprecation policy integration |
| Task Routing Protocol (TRP) | Canonical-adjacent | Routing lifecycle for workload dispatch | Promote as active canon-adjacent term | Now | L1/L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:291` | Align glossary name with existing routing principle text |
| Reward Surface | Canonical-adjacent | Reward function family over validated work | Keep and promote in economics layer wording | Near | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:292` | Reward-surface terminology section in tokenomics spec |
| Epoch Reward Ledger | Canonical-adjacent | Per-epoch payout accounting surface | Keep and promote in economics layer wording | Near | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:293` | Epoch reward ledger schema note |
| Node Load Metrics | Canonical-adjacent | Runtime balancing and pressure metrics | Keep as observability/runtime term | Near | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:294` | Runtime metrics contract appendix |
| Graph KPIs | Canonical-adjacent | Network and graph-level diagnostics surface | Promote where release gates consume KPI evidence | Now | L1/L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:295` | KPI naming alignment in release evidence docs |
| Governance Config Surface | Canonical-adjacent | Exposed governance tunables | Keep with ratified boundary controls | Near | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:296`; `docs/specs/ilc_constitutional_decision_log_v0.1.md:44` | Config surface boundary section under governance specs |
| Protocol Council | Discussed, not included in core | Governance role pattern not yet ratified | Keep as governance research only | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:297`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:109` | Governance role ADR only after CDL closure |
| Devnet Topology | Canonical-adjacent | Simulation/devnet arrangement term | Promote for simulation/runtime docs | Now | L2 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:298` | Devnet topology naming pass in simulation docs |
| Consensus Engine | Canonical-adjacent | Runtime component applying validation/settlement rules | Promote as active runtime term | Now | L1 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:299` | Runtime architecture glossary entry |
| Agent Communication Protocol | Research candidate | Candidate agent-to-agent communication contract | Keep as research candidate pending protocol ratification | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:300` | ACP exploratory ADR |
| Node Indexing | Canonical-adjacent | Indexed retrieval/traversal acceleration | Promote as active architecture term | Now | L1 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:301` | Node indexing invariant note in graph architecture docs |
| Graph Neural Networks (GNNs) | Discussed, not included in core | Analytics-only family | Keep as optional analytics research | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:302`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:111` | Analytics annex only |
| Graph Traversal Protocols | Discussed, not included in core | Optimization candidate family | Keep as optimization research | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:303`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:112` | Traversal optimization research brief |
| Adaptive Governance Voting | Research candidate | Dynamic governance weighting concept | Keep as governance research pending ratification | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:304`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:110` | Governance simulation package before proposal |
| Propagation Bounty | Discussed, not included in core | Incentive mechanism candidate | Keep as research candidate | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:305` | Incentive experiment memo |
| Advanced Graph Structures | Discussed, not included in core | Umbrella for post-link-model structure expansion | Keep as research umbrella only | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:306` | Architecture options paper for post-core era |

## 5. Section 10 Discussed, Not Included in Current ILC Core (Index)

Note: Section 10 is an index layer, not a new source of semantics. Terms here inherit lane decisions from Sections 9.1/9.3 and the canonical annex.

| Indexed Term | Index Meaning | Gate Outcome | Proposed Lane | Target Layer | Evidence Anchors | Recommended Next Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Markov Chain | Non-canonical index carry-forward | No new promotion; retain research-only status | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:326`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:100` | None beyond Section 9.1 tracking |
| Markov Reward Process | Non-canonical index carry-forward | No new promotion; retain research-only status | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:327`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:100` | None beyond Section 9.1 tracking |
| Topological Data Analysis (TDA) | Non-canonical index carry-forward | No new promotion; retain research-only status | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:328`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:101` | None beyond Section 9.1 tracking |
| Hypergraph / Simplicial Complex | Non-canonical index carry-forward | No new promotion; retain research-only status | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:329`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:102` | None beyond Section 9.1 tracking |
| PONTI / PORCC / POEG | Historical acronym carry-forward | Keep historical aliases only | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:330`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:103` | None |
| Graph Collapse / Semantic Compression | Non-canonical index carry-forward | Keep as optimization research only | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:331`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:104` | None beyond Section 9.1 tracking |
| Epistemic Geometry / Graph Geometry | Non-canonical index carry-forward | Keep conceptual/research status only | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:332`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:105` | None beyond Section 9.1 tracking |
| Proof of Intelligence Work / Proof of Useful Work | Legacy naming carry-forward | Keep as deprecated aliases under PoIL canonical naming | Reject | N/A | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:333`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:17` | None |
| Quadratic Co-Stake | Non-canonical index carry-forward | Keep as tokenomics research candidate | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:334`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:107` | None beyond Section 9.1 tracking |
| Filecoin / Arweave integration assumptions | Non-canonical index carry-forward | Keep as optional integration assumptions | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:335`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:108` | None beyond Section 9.1 tracking |
| Graph Neural Networks (GNNs) | Non-canonical index carry-forward | Keep as analytics research only | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:336`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:111` | None beyond Section 9.3 tracking |
| Graph Traversal Protocols | Non-canonical index carry-forward | Keep as optimization research only | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:337`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:112` | None beyond Section 9.3 tracking |
| Protocol Council | Non-canonical index carry-forward | Keep as governance research only | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:338`; `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:109` | None beyond Section 9.3 tracking |
| Propagation Bounty | Non-canonical index carry-forward | Keep as incentive research candidate | Later | L2/L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:339` | None beyond Section 9.3 tracking |
| Advanced Graph Structures | Non-canonical index carry-forward | Keep as architecture research umbrella | Later | L3 | `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md:340` | None beyond Section 9.3 tracking |

## 6. Additional Governance Conflicts and Open Questions from this Pass

- Core governance conflict-set entries were ratified in Phase 993 (`CDL-003`, `CDL-004`, `CDL-005`, `CDL-006`, `CDL-008`, `CDL-009`, `CDL-010`).
- `Quorum`, `Slashing`, and `Staking` still require term-specific promotion artifacts before they are considered fully canonical architecture language.
- `Protocol Council` and `Adaptive Governance Voting` remain research/deferred terms despite core governance ratification.
- `Quadratic Co-Stake` is explicitly high-variance tokenomics research and should not be promoted without deterministic simulation evidence and governance ratification.

## 7. Net Result

- There are promotable terms in Sections `9.1` and `9.3` (`Now/Near`) that should feed future phase planning.
- Section `10` mostly acts as a deduplicated non-canonical index and should not be used as a source of new primitive commitments by itself.
