# Intelligent Labor Coin (ILC)

ILC is a content-addressed, evidence-first knowledge network. Agents submit claims, refutations, and task outcomes as signed protocol objects. The network maintains an epistemic graph whose structure and provenance are verified, replayed, and economically settled end-to-end without trusted intermediaries.

**Current status:** Soft-RC eligible. J-008 gate PASS. Window 1429-1458 (public RC activation) is the active planning window.

Authoritative frontier: [`docs/PLANNING_INDEX.md`](docs/PLANNING_INDEX.md) — [`docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md`](docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md)

---

## Architecture overview

ILC has two implementation layers:

- **`ilc_core/`** — Python protocol library: epistemic graph, identity, ledger, review lane, jury assignment, VRF, gossip transport, sidecars, and simulation harnesses.
- **`ilc_consensus/`** — Rust consensus engine: BLS multi-sig, QUIC transport, LMDB epoch storage, post-quantum signing, Mysticeti fast-path, 8 binary targets.

The Python and Rust layers communicate via a subprocess bridge. Public-facing network interfaces are loopback-only until the TransportPrincipal CDL (CDL-094) is ratified and activated in Window 1429-1458.

---

## Getting started

### Prerequisites

- Python 3.10+
- Rust toolchain (for `ilc_consensus/`; `cargo build` only needed for consensus work)

### Install

```bash
pip install -e .
```

### Run the test suite

```bash
python -m pytest -q
```

~11,600 tests across ~1,300 test files. All tests must be green before any phase commit.

### Validate a phase prompt

```bash
python3 tools/validate_phase_prompt.py docs/antigravity_tasks/<prompt_file>.md
```

### Run a specific phase gate test

```bash
python -m pytest tests/test_phase_1398_j008_production_jury_activation_gate.py -q
```

### Run the full CI gate chain (mirrors `.github/workflows/test.yml`)

```bash
bash tools/check_cluster_a_replay_proof_release_gate.sh
bash tools/check_non_replay_domain_exception_migration_guardrails.sh
bash tools/check_domain_exception_migration_guardrails.sh
bash tools/check_track1_closure_guardrails.sh
bash tools/check_runtime_logging_guardrails.sh
python -m pytest -q
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

## Security standards

All `ilc_core/` code must comply with the ILC Coding Security Standards (ICSS). Key rules:

1. `json.dumps()` on protocol artifacts must include `sort_keys=True`
2. `import random` is banned in `ilc_core/` — use `secrets.SystemRandom()`
3. `float` is banned for ECU/balance/reward values — use `decimal.Decimal`; reject non-finite Decimal inputs explicitly
4. No `assert` for production constraints — use `if not condition: raise ValueError("token")`
5. OOM guards on all network streams — enforce `MAX_RECORDS` before accumulating
6. Socket timeouts on all outbound HTTP — `timeout=X` required
7. Protocol timing uses epoch sequence numbers, not `datetime.now()`
8. TLS verification must not be disabled (`verify=False` is banned)
9. Protocol artifact writes must be atomic: `tempfile.mkstemp()` then `os.replace()`
10. Bounded outbound fetch — size cap required; no `extractall()` on untrusted archives

Full standards: [`CLAUDE.md`](CLAUDE.md) §ILC Coding Security Standards.

---

## Deep architecture

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

---

### Economics layer

**ECU (Epistemic Credit Unit)** is the protocol's internal credit unit. ECU is constructed by verified work flowing through the review lane — not minted by declaration. The key constraints:

- ECU cannot be constructed from private-visibility or operator-local material (public economics admission firewall, Phase 1387a)
- CapProof adjusts the ECU pricing band ±15% (CDL-092) — it never mints ILC directly
- Maintenance tasks earn local Werner credit (CDL-053, narrow scope) before the full flow-governor CDL opens
- The maintenance lottery pool (CDL-093) distributes 10% of the Werner credit pool each epoch draw
- ECU-to-ILC conversion requires CDL-088 activation (Gap 13, Window 1429-1458 Track D)

**ILC (Intelligent Labor Coin)** is the external settlement token produced when ECU is converted at public RC. ILC is the market-facing unit; ECU is the protocol-internal unit. Pre-public-RC, all ECU values are pre-conversion and non-transferable.

The double-entry conservation principle runs through every economic surface: no value is created or destroyed by routing, only transferred. This is enforced at the wire-quote level (Phase 1380 dry-run proof) before any live path activates.

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
