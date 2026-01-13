# ILC Technical Paper (Draft v0.2)
## *The Epistemological Graph as a Compute Substrate for Agentic Economies*

*Build artifact:* 2026-01-06  
*Corpus basis (local zip):* `MANIFESTO.md`, `docs/ILC_Master_Principle_List_v5.1.md`, `protocol/ilc_protocol_mvp.json`, `epistemic_work_task_schema_v1.json`, plus high-signal transcripts in `Z_Past_Chats/`.  

---

## Abstract
ILC proposes a protocol specialized for an economy dominated by autonomous digital agents, where the primary scarce goods are verification bandwidth and credible knowledge. Technically, ILC replaces the “ledger-only” worldview with an **epistemological graph** whose nodes are performed tasks/claims and whose edges are typed semantic operators with economic consequences. The MVP protocol surface defines a minimal object vocabulary (`claim`, `refute`, `task`, `task_outcome`, `epoch_summary`) designed for machine interoperability. Security is enforced primarily by staking and economically-rewarded falsification; scalability is pursued through content-addressed evidence, optional ZK proof compression, and “star.map” routing over embedded graph geometry.

---

## 0. Why ILC is not a general-purpose L1
ILC’s corpus repeatedly stresses *scope discipline*:
- A general VM invites ambiguity, bloat, and unverifiable semantics.
- Agent economies require fast, standard schemas and predictable validation.
- The graph’s evolution must be auditable and replayable.

So ILC is closer to: “a dedicated execution environment whose transaction vocabulary is epistemic acts.”

---

## 1. MVP protocol object model (repo ground truth)
From `protocol/ilc_protocol_mvp.json`:

### 1.1 Claim
Fields (abridged):
- `id` (content-addressed hash)
- `agent_id`
- `content` (text or reference)
- `parent_ids` (graph parents)
- `timestamp`
- `net_stake`

### 1.2 Refute
Fields (abridged):
- `target_claim_id`
- `content` (evidence/explanation)
- `timestamp`

### 1.3 Task / Task outcome / Epoch summary
The MVP explicitly includes epoch-level economic stats, including:
- `total_ecu_spent`
- `total_reward_paid`
- `clearing_price_ilc_per_ecu`

This is important: the protocol anticipates a **market-clearing price** between “epistemic work” and coin rewards.

---

## 2. Graph-native architecture
### 2.1 Nodes are verbs; edges are laws
Manifesto summary:
- nodes are performed tasks (not passive data)
- edges encode protocol semantics (not merely links)

Technically, this implies:
- deterministic canonicalization for hashing (principle list emphasizes content-addressable canonical form)
- stable edge vocabularies so agents can reason about consequences
- economic logic that can read edge types (supports/refutes/equivalent/depends_on etc.)

### 2.2 Link types as typed operators
The principle list + audits repeatedly reference link types. A minimal typed-edge interface should specify:
- directionality
- allowed source/target node types
- staking implications
- reward flow implications
- inference implications (e.g., `equivalent` may merge reputation; `supersedes` may transfer authority)

---

## 3. Proof-of-Intelligent-Labor (PoIL) as protocol work
ILC’s “work” is not SHA-256 grinding; it is **validated epistemic tasks**.

### 3.1 Task schema hook: `epistemic_work_task_schema_v1.json`
Concrete fields:
- `difficulty_factor`
- `verification_method`
- `ecu.estimate`
- `bounty_id`
- `staking_beneficiary`

These are the “ports” for:
- compute cost estimation,
- verification constraints,
- economic settlement.

### 3.2 Verification modalities
The corpus anticipates plural verification:
- computational checks (deterministic)
- cryptographic checks (signatures, hashes, ZK proofs)
- human audits (structured, paid, replayable)
- oracle links (physical-world evidence)

---

## 4. Economics-enforced security
### 4.1 Stake as spam filter and truth collateral
Claims require stake; false claims expose stake to transfer/slash. This makes “speaking” costly and “lying” dangerous.

### 4.2 Refutation as a first-class economic event
A validated refute triggers:
- stake redistribution,
- claim status transitions,
- reward payouts,
- graph annotation (so downstream reuse can weight against refuted items).

### 4.3 Epoch clearing price
Because the MVP schema includes `clearing_price_ilc_per_ecu`, the protocol hints at an internal market:
- agents spend/lock/burn some stake value to do epistemic work
- the network clears rewards based on congestion, difficulty, and budget

This is where the “closed-loop backlog controller” concept (seen in status threads) naturally plugs in: price and difficulty can respond to backlog.

---

## 5. Routing and discovery: bounties + star.maps
### 5.1 Pull markets for tasks
The principle list describes “pull-driven economics”: agents choose tasks with the best expected payoff.

### 5.2 Star.map navigation
Star.map is described as geometry for discovery: embeddings/sharding that let agents navigate “hot” regions of epistemic opportunity.

A practical interpretation:
- maintain vector embeddings for nodes/tasks
- partition/shard regions of the graph
- broadcast “bounty gradients” so agents can hill-climb toward profitable work

### 5.3 Energy-aware routing
The energy-aware routing transcript describes adding `energy_cost_hint` into routing and breaking tasks into smaller pieces to fit available energy envelopes. This pushes the protocol into a rarely explored frontier:
> consensus and routing that react to grid/compute realities.

---

## 6. Evidence handling and canonicalization
The principle list repeatedly emphasizes:
- content addressing,
- canonical form,
- crypto-agility (hash functions like BLAKE3/SHA-256),
- evidence-first design.

This enables:
- deduplication (same claim hashed once),
- cheap verification (hash match),
- ZK-friendly commitments (proofs over hashes).

---

## 7. Governance: autopilot with fuses
Manifesto: “Governance is a bug.”  
Technically: minimize human interventions by:
- using objective metrics (backlog, error rates)
- automatic parameter adjustment
- “sunset” levers so emergency controls expire unless re-justified

If humans must intervene, the manifesto proposes a triad (executive/judicial/legislative roles). Implementation-wise, that maps to:
- a limited set of signed “attention” and “certification” actions
- strict rate limits
- on-chain audit logs

---

## 8. Threat model (where protocols go to die)
1) **Sybil:** stake + identity primitives are necessary but insufficient.  
2) **Cartels:** validator reputation can collude; requires diversity and auditability.  
3) **Goodhart:** ECU estimation will be attacked.  
4) **Evidence spam:** adversaries flood cheap “evidence” to clog audits.  
5) **Oracle capture:** physical-world truth boundaries remain hard.

The repo’s philosophy addresses this by making contradiction profitable and governance minimal—but these remain open engineering problems.

---

## 9. Implementation surface in the repo (as delivered in the zip)
- `protocol/ilc_protocol_mvp.json` — MVP object vocabulary
- `epistemic_work_task_schema_v1.json` — task + ECU hooks
- `docs/ILC_Master_Principle_List_v5.1.md` — canonical principles and roadmap
- `MANIFESTO.md` — axiomatic stance and protocol ethos
- `simulations/`, `tests/` — convergence and safety harness surfaces
- `ilc_core/` — reference code scaffolding

---

## Appendix: minimal flow diagram
```
Agent picks task  -> produces output -> submits claim + evidence hash
                         |                   |
                         v                   v
                 verification_method     stake attached
                         |
     other agents refute/validate (paid)
                         |
                         v
                 epoch clearing: ECU <-> ILC price
                         |
                         v
           balances + stake updates + graph state transitions
```
