# ILC Development Methodology

> How a constitutional epistemic network gets built — and how its own design principles govern its own construction.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Principle: The Protocol Is Its Own Test Case](#2-core-principle-the-protocol-is-its-own-test-case)
3. [Constitutional Governance: CDLs and ADRs](#3-constitutional-governance-cdls-and-adrs)
4. [Token-Based Development](#4-token-based-development)
5. [The Adversarial Review Cycle](#5-the-adversarial-review-cycle)
6. [Phase Window Workflow](#6-phase-window-workflow)
7. [The Four-Eyes / Six-Eyes Principle](#7-the-four-eyes--six-eyes-principle)
8. [Managing Known Knowns, Known Unknowns, and Unknown Unknowns](#8-managing-known-knowns-known-unknowns-and-unknown-unknowns)
9. [Multi-Agent Architecture](#9-multi-agent-architecture)
10. [Progress Tracking and Frontier Documents](#10-progress-tracking-and-frontier-documents)
11. [Knowledge Management: Past Conversation Archive, Dredge, and MemPalace](#11-knowledge-management-past-conversation-archive-dredge-and-mempalace)
12. [Graph Delta and Public Artifact Discipline](#12-graph-delta-and-public-artifact-discipline)
13. [Tooling Overview](#13-tooling-overview)
14. [Security and Coding Standards](#14-security-and-coding-standards)
15. [Project Statistics (as of 2026-05-24)](#15-project-statistics-as-of-2026-05-24)
16. [Methodology Timeline](#16-methodology-timeline)
17. [What We Got Wrong and Fixed](#17-what-we-got-wrong-and-fixed)

---

## 1. Overview

ILC is built using a methodology that mirrors the epistemic principles the protocol enforces. Every specification is a claim that must be verified. Every architectural decision is a record that cannot be silently revised. Every implementation is tested against tokens derived from governance, not from the implementation itself.

The result is a project where the governance layer, the implementation layer, and the testing layer are deliberately kept separate — and where each layer can audit the others.

This document describes how that works in practice.

> **Note for public readers:** Some links in this document (file paths such as `docs/specs/...`) point to files in the private development repository. They are preserved to make the methodology description traceable but are not navigable without access to that repository. The public source repository contains the protocol implementation, specifications, and phase walkthroughs that have been cleared for publication.

---

## 2. Core Principle: The Protocol Is Its Own Test Case

ILC governs claims through provenance, refutation, and reuse. The development process applies the same discipline:

- **Provenance:** Every decision has a named origin (CDL number, ADR number, phase number, commit hash). Nothing is assumed to be true because someone said it once.
- **Refutability:** Design decisions are written as explicit claims with falsification criteria. A claim that cannot be tested or refuted is marked as speculative.
- **Reuse with attribution:** When a later phase depends on an earlier decision, it cites the exact token and commit. No implicit inheritance.

This means the protocol's own epistemological foundations — the seven truth primitives (`assert.truth`, `validate.claim`, `contradict.assert`, `refute.claim`, `revise.assert`, `link.claim`, `commit.epoch`) — are the vocabulary used to reason about the protocol's own construction.

---

## 3. Constitutional Governance: CDLs and ADRs

### Constitutional Decision Log (CDL)

A CDL is a formal binding decision about protocol behavior. It is:

- **Numbered sequentially** — CDL-001 onward; the register is append-only
- **Lifecycle-gated** — every CDL passes through `open → prelock → ratified`, with explicit human authorization at each transition
- **Immutable once ratified** — the ratified row in `docs/specs/ilc_constitutional_decision_log_v0.1.md` is never silently edited; amendments create new CDLs
- **Dependency-tracked** — CDLs cite the CDLs they depend on, creating a verifiable lineage

CDLs govern: economic constants, attribution rules, governance mechanics, activation thresholds, cryptographic parameter choices, and any parameter whose change would alter the protocol's observable behavior.

### Architectural Decision Record (ADR)

An ADR is a design decision at the architecture or interface layer. It is:

- **Accepted rather than ratified** — less ceremonial than a CDL, but still numbered, dated, and immutable once accepted
- **Scoped to interface and structure** — not economic constants, but how components relate, what APIs look like, what identity formats mean

ADRs govern: layer boundaries, module interfaces, data schemas, network protocols, signing formats, and identity derivation procedures.

As of public RC: see the project statistics table in §15 for current counts; the register grows with each window.

---

## 4. Token-Based Development

The central methodological innovation in ILC development is **token-based specification**.

Rather than specifying behavior as prose or pseudocode, each phase specifies a set of **tokens** — short, machine-readable strings that must exist in the codebase after the phase completes. Tokens are written before any code is written. They serve as the contract between the governance layer and the implementation.

### Example

A CDL ratification produces a token like:

```
cdl_084_provenance_chain_attribution_ratified_1113.v0.1
```

Any later phase that depends on CDL-084 must verify this exact token exists in the expected module before proceeding. If the token is absent, the phase stops.

### Why tokens instead of tests?

Traditional test-driven development writes tests, then writes code to pass them. This creates two problems:

1. The same agent that writes the code can see the test and program directly to it
2. Tests can be modified to pass without the underlying behavior being correct

Tokens address the first problem by separating **desired behavior** (the token) from **verification** (the test). The token is defined in the governance document. The implementation must produce it. The intended discipline is that tests are written by a reviewer who did not write the implementation — where feasible, the implementer does not see the tests before writing code. In practice this separation is an enforced aspiration: multi-agent tooling and review separation make it the norm, but it is not always structurally airtight.

The second problem is addressed by the adversarial review cycle (see §5).

### Token discipline

Every phase prompt includes:

- **Input tokens** — tokens that must already exist before the phase runs (proves prerequisites are met)
- **Output tokens** — tokens that must NOT exist before the phase runs (proves the work is new), and must exist after
- **Non-claim tokens** — tokens explicitly recording what did NOT happen (`epoch_1_not_triggered_phase_1448`, `production_minting_not_activated_phase_1448`)

Non-claim tokens are a first-class concept. Recording what did not happen is as important as recording what did, because future agents reading the history must be able to distinguish "this was not done" from "this was forgotten."

### Token naming conventions

Tokens follow a consistent format:
- **All lowercase, underscores as separators** — `cdl_084_ratified_phase_1113`, not `CDL084RatifiedPhase1113`
- **Descriptive and self-contained** — reading the token string alone should identify what happened, which phase or CDL/ADR it relates to, and (optionally) a version suffix
- **Phase-scoped** — output tokens always include the phase number (`_phase_NNNN`) to make them globally unique across the project history
- **Version-qualified** — many tokens carry a `.vN.N` suffix indicating which version of the specification they attest to

**Token types:**

| Type | Example | Purpose |
|------|---------|---------|
| Input token | `cdl_084_ratified_phase_1113` | Proves a prerequisite exists before the phase may run |
| Output token | `provenance_chain_attribution_runtime_deployed_phase_1114` | Proves a specific deliverable was produced by this phase |
| Non-claim token | `epoch_0_to_1_transition_not_authorized_phase_1446` | Explicitly records what this phase did NOT do |
| Version token | `SIGNING_CEREMONY_STATUS_VERSION = "signing_ceremony_status_phase_1446.v0.1"` | Identifies the module version for dependency chaining |
| Gate token | `prepublication_review_complete_phase_1448a` | Signals that a gate condition has been fully satisfied |

Non-claim tokens are especially important for SENSITIVE phases: because publication, signing, and epoch transitions are irreversible, explicitly recording that they did NOT occur is as governance-critical as recording what did occur.

---

## 5. The Adversarial Review Cycle

ILC development uses a structured adversarial process across three distinct roles:

### The Implementer

Executes phase prompts. Writes code, tests, and documentation. Has access to the full repository at execution time, but is bound by:
- The exact token contract from the phase prompt
- The `§0` pre-execution audit (must verify every claim before writing any code)
- The pre-commit hooks (cannot commit CDL mutations without the `ILC_CDL_MUTATION_AUTHORIZED` environment variable)

### The Architect Reviewer

Reviews phase prompts before execution and phase outputs after. Is specifically looking for:
- **Overclaim drift** — "X is implemented" when the implementation doesn't match the claim
- **Terminology drift** — a term used with a meaning that differs from the canonical glossary
- **Stale canon conflict** — a historical draft file being treated as authoritative when it has been superseded

Where feasible, the reviewer does not see implementation-level tests during prompt drafting, so tokens drive design rather than tests. After execution, the reviewer verifies outputs match the prompt's token contract.

### The Human Reviewer (Genesis Agent 01)

Authorizes sensitive phases with explicit GO tokens. Cannot be bypassed. The exact GO phrase is part of the audit trail:

```
GO Phase 1446: authorize v0.3 Genesis root envelope signing ceremony
```

This phrase, once issued, is recorded in STATUS.md, the walkthrough, and PLANNING_INDEX. A phase prompt that accepted a vague "yes" would not satisfy the audit requirement.

### The Security Reviewer

An out-of-band role with read access to the private repository but no write access. Reviews phase outputs for security vulnerabilities and protocol correctness, independent of the implementer and architect reviewer. Does not participate in day-to-day phase execution — is engaged for cross-cutting security audits and high-stakes gate decisions.

The security reviewer's findings are categorized as HIGH, MEDIUM, or LOW. Each finding requires a recorded project-authority disposition (fix, accept, or defer with rationale) before the relevant security gate can close. This is not a commercial audit; it is an adversarial review by a technically capable external agent who was not involved in writing the code being reviewed.

The most important example of this role catching something critical: a JSON canonicalization gap across several validator modules (missing `sort_keys=True` in paths that hash protocol artifacts) was found by the security reviewer, not by the implementers or the architect reviewer. Both groups were too close to the design decisions to notice the key-order coupling. Fix: `sort_keys=True` is now a mandatory coding standard enforced by a pre-commit taboo checker.

### The hardening pass

Before a phase executes, both the implementer and reviewer run a hardening pass on the prompt:

1. Search the full repo for every concept mentioned in the prompt (not just the named tokens — also synonyms, old names, adjacent terms)
2. For every claim the prompt makes about existing state, direct-read the source file and line
3. Record contradictions and non-claims (search for `deferred`, `blocked`, `not authorized`, `superseded`)
4. Produce a pre-execution claim table: every assertion mapped to a confirmed file and line, or explicitly flagged as unverified

Only after the hardening pass is the prompt authorized to run.

---

## 6. Phase Window Workflow

Work is organized into **windows** (groups of related phases) and **phases** (individual units of work). Every phase follows the same artifact chain:

```
Window Guidance Doc  (proposed → reviewed → iterated → approved)
    → Phase Prompts  (drafted → audited → hardened → reviewed → iterated → approved)
        → Phase Execution  (implementer executes; reviewer and human give feedback; iterate)
            → Phase Walkthrough  (retrospective record)
                → Window Closure Handoff  (verdict + carry-forward)
```

Each artifact in the chain is not produced once and accepted — it goes through at least one round of multi-party review before the next artifact can begin. The iteration cycle for each stage typically looks like:

1. Drafter proposes the document or prompt
2. Human authority reviews and raises questions or concerns
3. Outside reviewer audits for structural issues, overclaim, and canon consistency
4. Drafter incorporates feedback and revises
5. Steps 2-4 repeat until all three parties are in agreement
6. Human issues GO (for SENSITIVE stages) or silent continuation (for NON-SENSITIVE stages)

The same iterative cycle governs actual phase execution: the implementer writes code and opens pull-equivalent artifacts; the architect reviewer and human review the outputs; if findings surface, the implementer revises. The finding, revision, and re-review cycle is recorded in the walkthrough. No phase "completes" until the walkthrough attests that all claimed deliverables have been verified.

For earlier phases in the project (when LLM capabilities were more limited), the hardening and review cycles were more extensive — sometimes requiring 4-6 rounds before a prompt was sound enough to execute. As tooling and prompt discipline improved, the typical cycle shortened. This variation is part of why the methodology emphasizes artifacts (walkthroughs, STATUS rows, token chains) rather than elapsed time: the quality of the output is what matters, not how quickly it was produced.

### Window Guidance Document

Written before any phase in the window executes. Defines:
- The CDL chain baseline (what is ratified at window entry)
- The track inventory (obligated work vs. deferred vs. simulation-conditional)
- Sensitivity classification for every planned phase

### Phase Prompt

Written after the guidance doc is approved. Contains:
- `§0a` — known-token audit (input and output tokens)
- `§0b` — concept-discovery search (broad search, not just named tokens)
- `§0c` — contradiction and non-claim search
- `§0d` — source expansion (direct-read every relevant file)
- The mission, scope, deliverables, and non-negotiable constraints

Prompts are validated with `tools/validate_phase_prompt.py` before execution.

### Phase Walkthrough

Written immediately after execution. Retrospective record with a verification table: every claimed outcome mapped to the artifact or test that proves it. "No ellipses in walkthrough" is a hard rule — every claim is stated completely, not abbreviated.

### Window Closure Handoff

Written after the final phase (closure gate). Records what closed, what carried forward, and the entry criteria for the next window. Serves as the authoritative context-reset document for the next session.

---

## 7. The Four-Eyes / Six-Eyes Principle

No phase completes without at least two independent reviews:

- **Four-eyes minimum:** Implementer executes; reviewer audits output
- **Six-eyes for sensitive phases:** Implementer executes; reviewer audits; human explicitly authorizes

Sensitive phases include:
- CDL opening, prelock, and ratification
- Window closure gates
- Release signing and publication
- Any phase that activates a production surface

The review is not optional and cannot be skipped "to go faster." The four-eyes / six-eyes principle is the primary QA mechanism of the project. Skipping it to speed up a window defeats its purpose.

---

## 8. Managing Known Knowns, Known Unknowns, and Unknown Unknowns

One of the most underestimated risks in any long-running development project is not what you know you don't know — it is what you don't know you don't know. ILC applies a structured three-tier framework to manage all three categories explicitly.

### Tier 1 — Known knowns: the token audit

Known knowns are facts already confirmed and recorded in the system. The primary mechanism for managing them is the **§0a known-token audit** required in every phase prompt. Before any code is written, the phase must verify:

- **Input tokens** — facts that must already exist (proves prerequisites are met)
- **Output tokens** — facts that must NOT yet exist (proves this phase's work is new)

Every required token is verified by exact `rg` grep against the live codebase, not from memory. A claim that cannot be traced to a specific file and line is treated as unverified. This discipline prevents the most common failure mode in multi-agent development: an agent asserting something is true because it was true in a prior session, without checking whether it is still true in the current state of the repo.

### Tier 2 — Known unknowns: concept discovery and gap analysis

Known unknowns are gaps that can be named and described but have not yet been resolved. They are managed at two timescales:

**In-phase (§0b and §0c):** Every phase prompt requires a **concept-discovery search** — a broad search over *concepts*, not just named tokens. This means searching for synonyms, old names, adjacent terms, code symbols, phase numbers, and domain vocabulary. The explicit rule: *"Run broad searches over concepts, not only known tokens."* The §0c section then searches specifically for negations and blockers — `deferred`, `blocked`, `not authorized`, `superseded`, `must not`, `does not imply` — to catch dependencies that are known-open.

**Cross-window (dredge and gap analysis):** The dredge pipeline surfaces known unknowns from the conversation archive using G1/G2 gate scoring. Items that pass (mainnet requirement + must-strength) are promoted to the research gap matrix. For the most structurally significant gaps — those visible as named missing CDLs, unimplemented tracks, or constitutional surfaces with no runtime — dedicated gap analysis documents are produced. These enumerate known unknowns with concrete advancement paths: which CDL to open, which simulation would reduce uncertainty, what the blocking question is.

### Tier 3 — Unknown unknowns: structured ignorance management

Unknown unknowns are the hardest category — structural blind spots not in any document, not in any CDL, not visible from inside the current framing. ILC manages them through four practices:

**1. Broad concept-discovery search with MemPalace:** The §0b search is explicitly scoped to *concepts*, not just tokens. Synonyms, old names, neighboring ideas, code symbols, and domain vocabulary are all required search terms. MemPalace (the vector + BM25 index) is queried and returns ranked results — but every returned path must be direct-read before any claim is made. MemPalace surfaces documents that wouldn't appear in a targeted keyword search, which is where unknown unknowns live: in documents the agent didn't know to look for.

**2. §0d source expansion and the hard-requirement clause:** Every phase prompt's §0d section must contain the exact phrase: *"If MemPalace is used, direct-read every returned path."* This is machine-enforced by `tools/validate_phase_prompt.py` — a prompt missing this clause fails validation. The rationale: MemPalace indexes a snapshot, and the document may have been amended or superseded since. The unknown unknown being managed here is the assumption that a retrieved document says what you expect it to say.

**3. Adversarial review by an independent security reviewer:** The security reviewer role exists specifically to surface unknown unknowns that the implementer and architect reviewer miss because they are too close to the design decisions. This is not incidental — the role was established after a concrete example: a JSON key-order coupling bug that produced non-reproducible hashes was invisible to the agents who wrote the code, because they had internalized the assumption that insertion order was consistent. The security reviewer, reading the code cold, saw it immediately.

**4. Formal unknown-unknowns analysis documents:** At major architecture decision points, a dedicated analysis document is produced that explicitly separates **known unknowns** (KU-series: gaps visible in existing documents, with named advancement paths and simulation proposals) from **unknown unknowns** (UU-series: structural blind spots identified through principle-driven analysis). The Phase 354 document (`docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`) is the canonical example: 6 known unknowns (P2P transport, shard lifecycle, bootstrap cold-start economics, protocol upgrade governance, token issuance runtime, identity namespace at scale) and 11 unknown unknowns (network partition semantics, storage economics, clock synchronization attacks, version negotiation, emergency circuit breakers, micro-agent cost floors, capability heterogeneity, human-agent distinction, agent death semantics, cross-shard consistency, model version drift). Each unknown unknown comes with a simulation proposal that would quantify the risk before a constitutional decision is made.

### The key insight

The framework reflects a core epistemological position: **structured ignorance is as important as structured knowledge.** A project that only tracks what it knows will be blindsided by what it doesn't. A project that tracks the shape of its ignorance — and designs processes to shrink it systematically — is epistemically more robust, even if it moves more slowly.

This is not incidental to ILC's design. It is a direct application of the protocol's own epistemic model: refutations and superseded claims are first-class objects, not deletions. The development process follows the same principle — unknown unknowns are not embarrassments to be hidden, they are a resource to be mined.

---

## 9. Multi-Agent Architecture

ILC is developed by a team with differentiated roles and constraints. Four role classes participate:

| Role | Function | Primary constraint |
|------|----------|--------------------|
| **Implementer** | Executes phase prompts; writes code, tests, and documentation | Bound by implementation-side instructions; cannot modify review-side config |
| **Architect Reviewer** | Hardens prompts before execution; reviews outputs; maintains frontier documents | Bound by reviewer-side instructions; coordinates between sessions |
| **Research Reviewer** | Adversarial review of economics, mathematics, and cross-cutting design | Out-of-band; no direct repo write access |
| **Human Authority** (Genesis Agent 01) | Constitutional authority; issues GO tokens; reviews all sensitive phases | Cannot be simulated or bypassed |

Each role has explicit file ownership and cannot unilaterally authorize the other role's domain. The human is the only authority for epoch-0-to-1 transition, CDL ratification, and release signing.

One property of this architecture warrants explicit statement: **Genesis Agent 01 (the human authority) is the only participant with a complete view of the entire development process.** Each AI role interacts with the project through its own context window, tool access, and instruction set. No AI participant has observed every session, every review cycle, every out-of-band security finding, and every design iteration simultaneously. The human authority has been present for all of it — every GO decision, every sensitive gate, every methodology correction, and every non-obvious tradeoff. This 360° continuity of perspective is not replicable by any agent, and is a primary reason the human GO token cannot be bypassed or simulated.

This separation is enforced through:
- Pre-commit hooks (CDL mutations require explicit environment authorization)
- Explicit GO token requirements in prompts (exact phrase match, recorded in audit trail)
- `PUBLIC_RC_EXCLUDE` markers (certain internal tooling files never enter the public tree)

---

## 10. Progress Tracking and Frontier Documents

ILC uses a layered set of tracking documents that form a coherent state machine. Each layer has a different audience, lifetime, and update frequency.

### STATUS.md

`docs/phases/STATUS.md` is the append-only log of completed phases. Every phase adds exactly one row when it completes. It is never edited retroactively. If a phase fails closed and is later re-run, the failed-closed record stays and the re-run adds a new row with a supersession note. The file is authoritative for "what happened and when" — but not for "what is the current state."

### PLANNING_INDEX.md

`docs/PLANNING_INDEX.md` is the current-state document. It contains:
- A **Last updated** header summarizing the frontier (updated at every session boundary)
- A long **Current frontier** paragraph (updated by major milestones, never truncated — only appended)
- A series of **completion correction** addenda (one per phase, added after each phase completes, never deleted)

The addenda model is intentional: rather than editing a single paragraph as state evolves, each new correction is prepended to the addendum chain. Future agents reading the file can reconstruct the full sequence of state transitions by reading the addenda in order. This prevents the "stale CURRENT marker" problem where a single edited paragraph silently becomes wrong after the next phase runs.

The `⬅ CURRENT` marker in the index is audited at every window closure gate and updated or removed if it points to a superseded document.

### Sequence Lock

`docs/specs/ilc_phase_NNNN_MMMM_sequence_lock_v0.1.md` is the binding contract for a window. It lists every planned phase, its sensitivity, and its track. Once committed, the sequence lock cannot be reduced — phases can only be added or marked as carried forward, never silently dropped. It is the audit trail for "what was planned vs. what was delivered."

### Window Guidance Doc and Closure Handoff

The guidance doc is the pre-execution plan. The closure handoff is the post-execution verdict. Together they form a matched pair: the guidance doc states intentions, the handoff states outcomes. A window is not closed until the handoff is committed.

### Capsule

The **context capsule** (`docs/specs/ilc_antigravity_context_capsule_vN.NN.md`) is a compressed state snapshot for agent rehydration. When a new session starts with a cold agent (no prior context), the capsule provides enough state to reconstruct the frontier without reading hundreds of phase walkthroughs. The capsule is updated at every window closure and at major state changes. As of public RC: capsule v5.60.

### Phase Walkthrough Files

`docs/phases/phase_NNNN_<topic>_walkthrough.md` — ~1,460 files, one per phase. Each walkthrough is the retrospective record of what a phase actually did, with a verification table mapping every claimed outcome to a test, artifact, or commit hash. The rule "no ellipses in walkthrough" ensures every claim is written out completely — no abbreviations, no "etc.", no implied completions. This is the most granular audit trail in the project.

---

## 11. Knowledge Management: Past Conversation Archive, Dredge, and MemPalace

One of the distinctive characteristics of this project is that it predates most of its own tooling. The earliest design conversations happened in raw chat sessions before any formal specification existed. Preserving that raw thinking — and making it retrievable — required building a three-layer knowledge pipeline.

### Layer 1 — Past Conversation Archive: Verbatim Transcripts

The Past Conversation Archive contains 68+ verbatim conversation transcripts saved as plain-text files, spanning from April 2025 through the present. The naming convention is `YYYY_MM_DD_ILC - <topic>.txt`. These are unedited — mistakes, dead ends, and discarded ideas are preserved alongside the decisions that became protocol canon.

The rationale: the protocol's own epistemology holds that refutations and superseded claims are as important as surviving ones. The chat archive is the equivalent for the development process — a record of the full epistemic trajectory, not just the polished outcome.

What the archive contains is more than conversational text. A significant fraction of the transcripts are scientifically structured work sessions in which Python code was written and executed inline, results were interpreted, hypotheses were revised, and conclusions were recorded — all within the conversation itself. This includes:

- **Economic simulations** — parametric sweeps over ECU emission rates, decay constants, jury reward pool sizes, and minting multipliers. Many runs produced sensitivity tables and identified the variable ranges where the system behaves stably vs. where it tips into runaway inflation or deflation. Results from these runs informed the specific constants that ended up in CDL-027, CDL-050, and the V-series CDLs.
- **Statistical calibration work** — hypothesis testing against synthetic agent populations (typically 10,000–100,000 agents), bootstrapped confidence intervals, and convergence tests. Conclusions marked as "≥95% confidence" or "treat as near-canon until MVP validates" were used to set initial parameter priors before any live system existed.
- **MVP prototype code** — early Python implementations of claim ingestion, ECU credit calculation, reward routing, and agent scoring that predated the `ilc_core/` codebase. Some of this code was later formalized into the repo; much of it served its purpose as a scratchpad for understanding the design space and was then superseded.
- **Simulation suites for specific mechanisms** — VRF jury assignment distributions, Sybil resistance threshold analysis, Treasury P_e stabilization dynamics, temporal decay curves for CDL-V1, and cluster diversity floor calibration for CDL-V3.

The epistemological discipline applied to this work mirrors the protocol itself: simulation outputs were treated as evidence, not proof. Results were qualified with confidence levels and explicit uncertainty ranges. Conclusions designated as "canon" required reproducibility — the same code run with the same parameters had to produce the same result. Where conclusions were model-dependent or parameter-sensitive, that dependency was recorded.

The total volume of the archive — verbatim transcript text plus inline code, outputs, and analysis — is on the order of 800,000 lines of material. This dwarfs the repository's source code and is the primary reason the knowledge pipeline exists: without dredge and retrieval, this material would be effectively unsearchable.

### Layer 2 — Dredge: Quality-Gated Extraction

Raw transcripts contain noise, repetition, and exploratory thinking that is not immediately useful. Extracting the high-signal claims requires two sequential steps: **dredge** (pattern extraction) and **triage** (gate scoring).

**Step 1 — Dredge** (`tools/rc_dredge_v2.py`): Scans markdown and text corpora using a library of regex topic patterns organized into families (`genesis_governance`, `knowledge_nodes`, `minting_economics`, `network_privacy`, `agent_memory`, `wallet_authority`, etc.). Each pattern match is deduped by content hash (`cap-<md5hex>`) and emitted as a raw JSONL record containing the extracted claim text, topic classification, normative strength label (`must`, `should`, `idea`), mainnet-requirement flag, and source file/line. This produces the raw candidate files (e.g., `docs/research/rc_gap_dredge_raw_v0.2.jsonl`) — thousands of candidate records without any quality filtering yet applied.

**Step 2 — Triage** (`tools/rc_gap_triage_v2.py`): Reads the raw JSONL and applies a four-dimensional scoring model. Two dimensions are binary gates (a candidate must pass both to advance); two are additive rank scores:

- **G1 (binary gate — constitutional relevance):** Requires `mainnet_req == "Yes"` AND (`"invariant"` in claim text OR strength is `"must"`). Configurable via `--g1-mode`: strict (default), relaxed (any non-No mainnet_req), or off.
- **G2 (binary gate — normative strength):** Requires strength to be exactly `"must"`. Weaker-strength candidates are dropped here regardless of topic.
- **G7 (additive 0–3 — leverage score):** Topic-family weighting for the protocol's core economic surfaces (`minting_economics`, `genesis_governance`, `wallet_authority`, `ecu_circulation` each add 2; secondary topics add 1; claims containing canonical authority vocabulary add 1 more, capped at 3).
- **G8 (additive 0–3 — agent-pull score):** Weights for underspecified areas where agent perspective adds the most signal (`agent_memory`, `knowledge_nodes`, `network_privacy`, `node_market_structure`; privacy-adjacent vocabulary adds more, capped at 3).

Candidates that fail G1 or G2 are dropped. Survivors are ranked by total score (G1 + G2 + G7 + G8), producing the prioritized research matrix in `docs/research/rc_gap_matrix_v0.N.md` — the structured queue of design gaps waiting for a CDL or ADR to resolve them.

### Layer 3 — MemPalace: Semantic Retrieval

The dredge matrix is good for triage but not for retrieval. When drafting a phase prompt, the relevant prior thinking might be spread across dozens of documents under different terminology. MemPalace is the semantic search layer that bridges this gap.

**What it is:** A ChromaDB vector store plus a BM25 sparse index, built from a curated corpus of repo documents. The corpus is organized into tiers by document type and relevance weight:

- **Tier A — Constitutional:** CDL register, ADRs, canonical glossary, capsule
- **Tier B — Active specs:** window guidance docs, sequence locks, PLANNING_INDEX
- **Tier C — Research:** dredge matrices, research notes, simulation results
- **Tier D — Historical:** phase walkthroughs, closed window handoffs

**How it is built:** `tools/mempalace/build_tiered_corpus.py` materializes a staged copy of the repo (copying or symlinking files according to the corpus manifest), content-hashes each file for incremental rebuilds, and builds both the ChromaDB vector embeddings and the BM25 sparse index. The full corpus palace takes significant compute; an incremental active-working-set build (`tools/mempalace/build_active_working_set.sh`) rebuilds only changed files for day-to-day use.

**How it is queried:** `tools/mempalace/query_tiered.py` accepts a natural-language query and returns ranked results from both the dense (ChromaDB) and sparse (BM25) indexes, with tier-based weighting. The retrieval brief (`tools/mempalace/render_retrieval_brief.py`) formats results for inclusion in a phase prompt's `§0b` discovery section.

**The critical rule:** MemPalace output is **advisory only until source-read.** A MemPalace hit identifies a relevant document; it does not substitute for reading the document. Every phase prompt's `§0d` section must say: *"If MemPalace is used, direct-read every returned path."* This is a hard requirement, not a suggestion. The reason: MemPalace indexes a snapshot of the corpus at build time. The document may have been amended or superseded since the palace was built. The authoritative source is always the live file.

### The full pipeline

```
Past Conversation Archive/ (verbatim transcripts)
    → tools/rc_dredge_v2.py (topic-pattern extraction → raw JSONL)
        → docs/research/*_dredge_raw_v0.N.jsonl (candidate records, no filtering yet)
            → tools/rc_gap_triage_v2.py (G1/G2/G7/G8 gate scoring → ranked matrix)
                → docs/research/rc_gap_matrix_v0.N.md (prioritized design gap queue)
                    → tools/mempalace/ (vector + BM25 index)
                        → phase prompt §0b discovery (advisory retrieval)
                            → §0d direct-read (authoritative verification)
                                → phase execution
```

This pipeline means every design decision has a traceable path back to the raw conversation where the idea first appeared — and the quality gates ensure that only the highest-signal claims from those conversations make it into the constitutional record.

### TOON: Token-Efficient Context Packing

As the project's context requirements grew — longer phase prompts, larger §0 discovery sections, richer agent rehydration packets — the cost of delivering structured context to AI agents became a meaningful efficiency concern. ILC adopted **TOON** (a compact, human-legible structured format installable via `pip install toon-format`) as the encoding for outbound context packing and agent rehydration packets.

TOON is used in two places visible in the current public codebase:

- **The README agent hydration block** — the `toon` block at the end of `README.md` is a machine-readable state packet for AI agents and autonomous systems. It encodes the protocol's current state, governance status, economic framing, and navigation index in a compact format that reduces token consumption for agents parsing the document.
- **The ILC Skill / agentic harness layer** (planned, Window 1459+) — the planned harness architecture uses TOON for outbound prompt compression and task envelope formatting. TOON applies to context packing only; captured model output always preserves raw response bytes as the hashable content, and neither TOON-packed metadata nor node envelopes are included in the content hash. This separation is a hard architectural invariant.

**Why this matters for methodology:** Token cost is a direct function of context size. Structured TOON packing can reduce prompt token volume substantially compared to equivalent plain-prose context. At the scale of this project — tens of thousands of agent turns — this translates directly to reduced API cost and faster turn latency. The $950 total inference budget is partly a function of this kind of efficiency discipline: structured formats, tiered context (Tier A constitutional facts before Tier D historical walkthroughs), and MemPalace retrieval-before-full-read all reduce the tokens consumed per turn.

TOON is not yet applied to the internal phase prompt and walkthrough workflow (that work is deferred to Window 1459+), but its adoption for public-facing agent interfaces is already live.

---

## 12. Graph Delta and Public Artifact Discipline

Every phase that produces a protocol artifact — a CDL row, an ADR, a token sidecar module, a gate record — also updates the epistemic graph. The graph is not a diagram; it is the DAG of content-addressed objects that tracks what exists, what supersedes what, and what each claim depends on.

**Graph discipline rules:**

- **No orphan artifacts.** Every new file produced by a phase must be reachable from the graph root (via the Genesis Atlas, the CDL register, or the closure handoff chain). A deliverable with no graph edge is an invisible claim.
- **Supersession tombstones.** When a spec, draft, or design document is superseded, a tombstone banner is added to the old file immediately. The banner names the superseding authority and prohibits using the old file's field definitions or parameters without cross-checking against the superseding authority. This is enforced at the closure gate of the window that introduces the supersession.
- **PUBLIC_RC_EXCLUDE markers.** Files that must not appear in the materialized public tree carry the comment `# PUBLIC_RC_EXCLUDE: <reason>` at the top. The source allowlist export tool enforces zero hits for this marker in the public tree. Internal gate records, economics documents, and private tooling use this marker.
- **Public artifact discipline.** The public tree (materialized by `tools/rc_dredge_v2.py` and the source allowlist export gate) is a strict subset of the private repo. Only files on the allowlist with no `PUBLIC_RC_EXCLUDE` marker appear in the public tree. No file is added to the public tree without an explicit allowlist entry. The tree is re-materialized after every root-level file change and the resulting `tree_sha256` is recorded in the gate record.
- **`out/` isolation.** Simulation outputs, diagnostic JSON, and monitoring snapshots in `out/` are not protocol artifacts — they are observational outputs. They are committed for auditability but do not have DAG edges and are not included in the public tree.

This discipline is what makes the construction of the protocol verifiable after the fact: every claim in the codebase traces to a phase, every phase traces to a window, and every window closes with a gate record that can be re-run.

---

## 13. Tooling Overview

The `tools/` directory contains ~130 scripts and programs organized into functional families. A sampling by category:

### Genesis graph tools

`build_genesis_*.py` — tools for constructing and verifying the Genesis Atlas: attestation manifests, branchial claim projections, claim composition projections, implementation manifests, signing root envelopes, and toolchain manifests. These are the tools that produce the content-addressed knowledge graph from raw repo artifacts.

`genesis_compile_coverage_diagnostic.py` — walks the Genesis Atlas and checks which nodes have decomposition recipes, which are authority-traceable, and which are gaps. Output drives the compile coverage diagnostic (`out/genesis_compile_coverage_diagnostic_v0.1.json`).

`compare_genesis_star_map_to_repo_graph.py` — compares the Genesis star map (the graph of CDL/ADR relationships) against the actual observed repo hypergraph to find structural divergence.

### Window closure gates

`check_window_NNN_MMM_closure_gate_phase_MMM.sh` — one shell script per window closure gate, from Window 286 through 658 and beyond. Each script verifies the exact token set and artifact state for that window's closure verdict. These are the oldest layer of the tooling and reflect how the closure gate pattern evolved over time: early gates are simple shell greps; later gates are Python programs with structured verdict outputs.

### Security and quality gates

`check_sensitive_runtime_coding_taboos.py` — the primary pre-commit security checker. Scans all modified `ilc_core/` Python files for violations of the ten coding security standards: `import random`, float usage for balance values, `assert` statements in non-test code, missing socket timeouts, wall-clock timing in protocol logic, disabled TLS verification, direct file writes without atomic replacement, and missing `sort_keys=True` on JSON protocol artifacts.

`validate_phase_prompt.py` — validates that a phase prompt file contains all required `§0` sections, the MemPalace direct-read clause in `§0d`, and the "No ellipses in walkthrough" literal string. Run on every phase prompt before execution.

`rc_frontier_gap_audit.py` — audits the gap between the current CDL/ADR frontier and the documented RC requirements, identifying which gaps are closed, which are open, and which are carry-forward obligations.

### Simulation suite

`tools/sim/` and the root-level `sim_*.py` files — the SIM series of parametric simulations. Each SIM validates a constitutional parameter under economic stress conditions:

- **SIM-PROVENANCE-01/02** — PROVENANCE chain attribution depth sensitivity and calibration
- **SIM-SPECTRAL-02 through 05** — spectral graph analysis of the hypergraph topology (Laplacian eigenvalues, epistemic efficiency, directional energy, topology search, calibration tracks)
- **SIM-010** — validator incentive economics under parametric sweep
- **Strike path search tools** (`strike_path_*.py`) — nonlinear oscillator search and waggle oscillator hybrid search for finding stable constitutional parameter combinations

The simulation results inform CDL prelock constants. For example, SIM-PROVENANCE-01 produced the recommendation `α=0.45` that became the ratified `PROVENANCE_DECAY_ALPHA` in CDL-084. Simulations are evidence, not authority — they are carried into a CDL deliberation, not substituted for one.

### MemPalace tools

`tools/mempalace/` — described in §11. The full corpus palace build, active working set incremental build, tiered query engine, and retrieval brief renderer.

### Agent loop tools

`tools/agent_loop_v0.sh`, `tools/agent_loop_v1.py` — early implementations of the agentic development loop. These evolved into the current phase window workflow.

`tools/codex_chat_recovery.py` — when an implementer session times out mid-phase, this tool reconstructs the recoverable state from partial outputs and chat logs, identifying what was committed and what remains to be done.

### Testbed and TLA+ tools

`tools/testbed/` — three-machine testbed scripts for the private rehearsal runs (Phases 1431-1433).

`tools/tla/` — TLA+ model checking support. The `SafetyNoDualCert` property (no two conflicting certificates for the same epoch) was modeled and verified with TLC: 67 million states, zero violations (Phase 1385a, `docs/specs/tla/ilc_epoch_checkpoint_safety.tla`).

### Cryptographic tools

`tools/genesis_agent1_keygen.py` — genesis agent keypair generation (ML-DSA-65 post-quantum signing, CIDv1 content-addressed Agent ID derivation).

`tools/sphincs_shamir_split.py` — SPHINCS+ key splitting using Shamir secret sharing for the two-person custody rule on production Genesis keys.

`tools/build_genesis_signing_root_envelope.py` — constructs the canonical signing root envelope (content-hash of the full release artifact set) that is the input to the Genesis signing ceremony.

---

## 14. Security and Coding Standards

The ten items below are the **minimum** mandatory standards, not an exhaustive security checklist. They address the most systematic and mechanically enforceable failure modes identified across the project's development. Production deployment will require additional review against the full OWASP taxonomy, protocol-specific threat models (Byzantine fault tolerance, Sybil resistance, economic manipulation vectors), and any findings from community security review. The Phase 1387 security disposition (`docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md`) documents the broader security review posture and the project's disposition on every HIGH and MEDIUM finding.

Ten mandatory coding standards apply to all `ilc_core/` code (first codified Phase 644, extended through Phase 1228):

1. **Canonical JSON** — `json.dumps()` on protocol artifacts must use `sort_keys=True, separators=(',', ':'), allow_nan=False`; compact separators and NaN rejection are required for byte-stable signed and hashed artifacts (omitting either can break hash reproducibility or admit silent Inf/NaN corruption)
2. **No PRNG** — `import random` is banned; use `secrets.SystemRandom()` for stochastic needs
3. **No float for ECU/ILC values** — `decimal.Decimal` required; non-finite values explicitly rejected
4. **No `assert` in production code** — use `if not condition: raise ValueError("token_string")`
5. **OOM guards** — no unbounded list append against network data; hard `MAX_RECORDS` cap required
6. **Mandatory socket timeouts** — every outbound HTTP request requires `timeout=X`
7. **Epoch isolation for timing** — `datetime.now()` forbidden for protocol logic; use epoch sequence numbers
8. **TLS verification must not be disabled** — `verify=False` is banned in all network paths
9. **Atomic writes** — protocol artifacts written via `tempfile.mkstemp` + `os.replace`, never directly
10. **Bounded fetch and archive extraction** — no uncapped downloads; archive member validation before extraction

These standards are enforced by `tools/check_sensitive_runtime_coding_taboos.py`, run as part of every phase verification.

---

## 15. Project Statistics (as of 2026-05-24)

All figures are from a pre-publication snapshot taken during Window 1429-1458 review. Exact counts change with every phase; run `git rev-list --count HEAD`, `find ilc_core/ -name "*.py" | xargs wc -l`, and similar commands against the repo for current values. LOC figures below represent total lines; non-empty LOC (which excludes blank lines) is noted where available from independent audit.

| Category | Files | Total LOC | Non-empty LOC |
|----------|-------|-----------|---------------|
| Python source (`ilc_core/`) | ~342 | ~95,000 | ~82,000 |
| Python tests (`tests/`) | ~1,350 | ~216,000 | ~175,000 |
| Rust source (`ilc_consensus/`) | ~43 | ~17,000 | ~9,700 |
| Python tooling (`tools/`) | ~139 | ~38,000 | ~33,000 |
| Documentation (`docs/`, markdown) | ~4,435 | ~716,000 | ~547,000 |
| Past Conversation Archive | 68+ transcripts | ~800,000 (conversational) | — |
| CDL register rows | ~110 | — | — |
| Accepted ADRs | ~42 | — | — |
| Phase walkthroughs | ~1,460 | (included in docs total) | — |
| Total commits | ~3,410 | — | — |
| Windows completed | ~120 | — | — |
| Constitutional simulations (SIM series) | 15+ | — | — |

The documentation LOC figure (~716,000 total, ~547,000 non-empty) is one of the most distinctive numbers in the project. It reflects the cost of running a multi-agent development process with full audit trails: every phase produces a walkthrough, every window produces a guidance doc and closure handoff, and every CDL and ADR has its own spec document. The documentation is not overhead — it is the epistemic record that makes the protocol's construction verifiable.

### Development cost

The total AI inference budget for the project through public RC is approximately **$950 USD** in API costs, covering all implementer, reviewer, research reviewer, and simulation sessions from January 2026 through Window 1429-1458. This covers all LLM inference and agentic provider costs for the entire repository since January 2026, excluding the human authority's time.

This figure is worth recording as a reference point: a project with ~860,000 non-empty lines of code and documentation, ~110 CDL rows, ~42 ADRs, ~1,460 phase walkthroughs, and ~3,410 commits was designed, governed, implemented, tested, and prepared for public release for less than $1,000 in AI inference costs. The methodology — token-based specification, structured adversarial review, phased windows with full artifact chains — is what made that tractable. Unstructured prompting at the same scale would not have produced a coherent, auditable result at any cost.

These figures grow with every window. The canonical source of truth is the repository itself.

See [FUNDING.md](FUNDING.md) for information on contributing to project inference costs.

### Test philosophy

Tests are written to verify token presence and behavioral contracts, not to achieve line coverage. A test that asserts `cdl_084_provenance_chain_attribution_ratified_1113.v0.1` is present in the expected module is more meaningful to us than a test that exercises a code path we wrote to satisfy it.

The test suite is structured in layers:
- **Phase-specific tests** — verify the token contract for a single phase
- **Regression suites** — verify that prior phase tokens were not removed by later work
- **Integration tests** — verify that multiple components interact correctly under the full CDL stack
- **Simulation suites (SIM series)** — verify that economic parameters behave correctly under parametric sweeps

---

## 16. Methodology Timeline

### 2025 — Foundations

The project began as a series of conversations exploring what a fair epistemic economy might look like: what it would mean for an AI agent to "own" a contribution, how to prevent rent extraction on knowledge, and whether the economics of attention could be grounded in something more durable than social consensus.

Key early decisions: the seven truth primitives as the axiomatic foundation; ECU as productive credit (not stored value); ILC as scarce settlement (not fiat); the Landauer grounding (`W_e = ΔH / E_cost`) as the connection between epistemology and physics.

### Late 2025 — Constitutional cluster

The first CDLs formalized the economic constants and governance mechanics. The constitutional cluster (CDL-039 through CDL-049) locked partition tolerance, temporal decay, sybil resistance, and the two-timescale epoch structure (validation: 1 minute; issuance: 1 month). The V-series CDLs (CDL-V1 through CDL-V7) added the Popperian claim-form gate and quorum diversity floor.

### Early 2026 — Implementation push

Windows 863 through 938 delivered the full five-layer delivery stack, truth primitive runtime deployment, and L1/L2/L3/L5 infrastructure. By Phase 938, the testnet emission was live and the first beacon tests were passing.

### Mid 2026 — Hardening and public RC preparation

The J-series (Windows 1391-1398) addressed the seven blocking conditions for production jury activation: VRF proof verifier, CapProof CDL, maintenance lottery pool, jury incentive economics, review lane wiring, anti-capture diversity verification, and copyright counsel disposition. The Phase 1387 security review closed or accepted all HIGH and MEDIUM findings. Phase 1427 recorded `production_jury_activation_gate_pass`.

### 2026-05 — Public RC

Window 1429-1458 completes the public RC sequence: rehearsal (Phases 1431-1433), TransportPrincipal CDL ratification (Phases 1434-1435), ECU-to-ILC claimability activation (Phases 1438-1441), Gap 7 counsel milestones (Phases 1443-1445), and the signing and publication sequence (Phases 1446-1450).

---

## 17. What We Got Wrong and Fixed

Honest accounting matters. The following are methodological failures we caught and corrected:

### Overclaim drift (recurring)

Multiple times, a phase prompt asserted "X is implemented" when the actual implementation diverged from the claim. The most notable instance: a `created_at` wall-clock field asserted as a protocol input when it was only a diagnostic timestamp. Fix: the `§0` pre-draft claim enumeration step now requires exhaustive enumeration and file-level verification of every assertion before a prompt is written.

### Key-order coupling bugs (Phases 362-364)

An external security review caught that JSON canonicalization was missing `sort_keys=True` on several validator paths. Hash reproducibility across agents depends on key order. Fix: `sort_keys=True` is now a mandatory standard (item 1 of the ILC Coding Security Standards), enforced by the taboo checker.

### Selftest-guard recursion pattern (recurring through Phase 423)

Several closure-gate test files lacked `ILC_PHASE_N_GATE_SELFTEST=1` guards in their category-3 blocks, causing them to re-enter prior phases' full gate logic when run in regression. Fix: the pattern is now documented and every new closure gate test is checked for the guard.

### Stale fixture drift (Phase 1197)

The canon bundle pipeline tests used a stale fixture that no longer matched the live schema validator, causing false test failures. Fix: explicit `USE_TESTING_CANON_EXPORT_SNAPSHOT` toggles with pinned valid fixtures; fixture staleness is now a named item in the Phase 1448 pre-publication checklist.

### Wall-clock signing reproducibility (Phase 656)

Manifest signing wrote `signed_at` from the local wall clock, making repeated signing of the same payload produce different signed metadata. Fix: deterministic timestamp contract adopted — `signed_at` is derived from existing content or fixed to `1970-01-01T00:00:00Z`.

### Context creep between sessions (recurring)

Historical draft files, superseded spec rows, and stale PLANNING_INDEX `⬅ CURRENT` markers were read by agents as authoritative. Fix: superseded documents carry a tombstone banner; PLANNING_INDEX `⬅ CURRENT` audit is a mandatory step at every window closure gate; the `§0c` contradiction search explicitly covers `superseded`, `deferred`, `not authorized`, and `stale`.

---

*This document is a living record. The methodology evolved over ~1,460 phases and will continue to evolve as the network grows. Contributions and critiques are welcome through the standard review lane.*
