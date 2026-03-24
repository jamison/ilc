# ADR-0022: Local-First Private Use and Publication-Bound Economics

**Status:** Proposed
**Date:** 2026-03-24
**Author:** Jamison and GPT-5 Codex
**Source:** Pressure-flow / long-tail review cycle and follow-on architecture discussion,
2026-03-24
**Dependencies:** ADR-0019, ADR-0020, node schema visibility model, OpenClaw / CLI-first
integration model

---

## Context

ILC is being designed as a shared epistemic graph, but one of its most important use cases
is smaller and more immediate:

- a single digital agent using ILC locally as durable memory infrastructure,
- a human/operator using ILC privately on one machine,
- a small group of agents sharing a gated or shard-local working memory,
- a private subgraph that may later promote selected nodes into the public graph.

This use case matters for both humans and digital agents. It addresses practical concerns
around memory integrity, provenance, portability, selective publication, and resistance to
centralized rewriting of agent memory or context.

The current architecture already points in this direction:

- the visibility model distinguishes `public`, `semi-private`, and `private`,
- private nodes are allowed to exist off-chain or shard-local,
- promotion from private to public is already modeled as a deliberate signed event,
- OpenClaw is treated as an orchestration/distribution path rather than a hard dependency
  of protocol correctness,
- ADR-0019 already reserves `operator_local` as a valid provenance class.

What has not been stated strongly enough is the architectural rule that follows from these
facts:

> ILC must remain usable as local and private memory infrastructure without mandatory market
> participation, and the heavier economics/governance machinery must bind primarily at the
> publication, promotion, validation, and shared-settlement boundaries.

Without that rule, later economic or governance work can accidentally place staking, ECU
spend, or public validation overhead in the hot path of local cognition and private memory
organization.

---

## Decision

### 1. Local-first usability is an architectural invariant

ILC must be usable as local and private memory infrastructure without mandatory market
participation.

This includes:

- personal/local knowledge organization,
- local retrieval and reformulation,
- private memory graphs,
- shard-local or team-local working memory,
- operator-local indexing, ranking, and synthesis over private nodes.

The protocol must not require public staking, public panel review, or shared-market
participation merely to use ILC as local/private memory infrastructure.

### 2. Pressure may be continuous; legitimacy is discontinuous

Pressure-like signals may exist across the full private-to-public continuum:

- local salience,
- local reuse,
- local contradiction handling,
- shard-local demand,
- publication interest,
- public corroboration and challenge.

However, public legitimacy is not continuous.

The architectural rule is:

> **Pressure may be continuous across private and public space, but legitimacy is
> discontinuous at explicit boundary crossings.**

Private or shard-local pressure may inform promotion decisions. It does not itself create:

- public corroboration,
- public protocol reputation,
- public epistemic status,
- or public settlement rights.

Those require explicit promotion and public-legible evaluation.

### 3. Economics and governance intensify at publication-bound boundaries

The heavier protocol machinery should bind primarily at these boundaries:

- publication into shared/public graph space,
- promotion from private or semi-private to public visibility,
- public validation and refutation exposure,
- shared settlement and shared reward allocation.

Economics and governance should not sit in the hot path of private/local cognition.

### 4. Promotion must be explicit, signed, and challengeable

Promotion from private or shard-local material into public status must remain:

- explicit,
- signed,
- provenance-preserving,
- and challengeable under public graph rules.

Private or gated work does not inherit public corroboration automatically.

### 5. Public anchors for private memory spaces are allowed

Private content does not imply zero public footprint.

The recommended architecture is:

- **public anchors / commitments**
- **private interior content**
- **explicit promotion path**

At minimum, the public graph may legitimately carry:

- public agent identity material,
- public agent/profile anchor objects,
- optional gate or shard-control anchors,
- minimal public commitments to private memory spaces such as a first-node pointer, root
  commitment, beacon, or notarized pointer root,
- later public `promotion_receipt` objects when private material is promoted.

These public anchors exist for continuity, navigability, and anti-loss purposes. They
prove existence or continuity of a private memory space without revealing its private
contents by default.

The architectural rule is:

> **Public graph may carry anchors, headers, and commitments for private memory spaces,
> but not the private contents themselves unless and until promotion occurs.**

### 6. Private nodes imply a persistence domain, not necessarily a full public shard object

If at least one private knowledge node exists, then in practice there is some private
persistence domain holding it:

- purely local operator storage,
- a local/private subgraph,
- a gated shared workspace,
- or a shard-local chain.

This does **not** require a fully formal public shard object in every case.

Operationally, however, the design should assume that private nodes live inside some
private or group-local persistence context, and that context may optionally expose a
minimal public anchor/header if continuity or later promotion matters.

### 7. Advisory local views are allowed and encouraged

A local/private ILC instance may expose operator-local advisory views over private nodes,
including:

- estimated public relevance,
- estimated likely ECU/ILC value if promoted,
- likely novelty or duplication risk,
- public graph overlap or adjacency,
- indications that an agent has unused capacity or could productively mine/work on the
  public graph,
- similar decision-support hooks that help a human or agent decide whether publication is
  worthwhile.

These views are:

- operator-local,
- advisory,
- and non-normative.

They must not be treated as public corroboration or public economic entitlement.

### 8. Shared data model; different legitimacy regimes

The private/public boundary should not require a completely different data model.

The same underlying graph and node structures should be usable across:

- local/private use,
- gated or shard-local collaboration,
- and public/shared graph publication.

What changes at the boundary is not the existence of structured knowledge, but the
legitimacy regime applied to it.

### 9. Nodes may anchor shards; shards remain separate lifecycle objects

Nodes and shards are distinct object types.

- nodes are epistemic objects,
- shards are persistence, governance, routing, and economic containers for subgraphs.

Accordingly:

- shards can hold subgraphs of nodes,
- a node or node lineage can justify, seed, or anchor a new private or gated shard,
- but shard creation remains a shard-level lifecycle event rather than an implicit property
  of a single node.

This means a downstream private workspace may begin from a specific public node while still
being modeled as a separate private persistence domain or shard.

The recommended architectural reading is:

> **A node may serve as the root anchor or entry point for a shard, but a shard remains a
> separate protocol object with its own visibility, membership, governance, and fee
> surfaces.**

---

## Boundary model

### A. Local/private cognition boundary

Expected properties:

- no mandatory public staking,
- no mandatory public panel review,
- no mandatory public market participation,
- low-latency local retrieval and reformulation,
- optional operator-local scoring and advisory hints.

### B. Shared private/group boundary

Expected properties:

- gated or shard-local participation,
- community-local or operator-local evaluation,
- possible local pricing or shadow economics,
- no automatic inheritance of public corroboration.

### C. Public/shared graph boundary

Expected properties:

- explicit publication or promotion event,
- public visibility,
- challengeability,
- public legitimacy rules,
- public economic/governance consequences where applicable.

---

## Consequences

**Positive:**

- Preserves ILC as practical memory infrastructure for individual agents and small agent
  teams.
- Keeps protocol economics from making local/private use unattractive or slow.
- Strengthens the anti-tamper and provenance value proposition for digital agents.
- Encourages gradual promotion from private exploration to public contribution without
  collapsing the two into one regime.
- Supports operator-local tooling that helps users make better publication and participation
  decisions.

**Tradeoffs:**

- Requires disciplined separation between advisory/local scoring and public legitimacy.
- Prevents some tempting shortcuts where private usage metrics are treated as public trust.
- Requires careful provenance handling so private-to-public promotion preserves continuity
  without laundering private confidence into public status.

---

## Sooner-rather-than-later implications

1. **Runtime/economic boundary**
   - future runtime work should keep authority, authorization, issuance, settlement, and
     local advisory scoring as separable surfaces.

2. **Schema and telemetry**
   - provenance and visibility fields must be sufficient to distinguish:
     - local/private activity,
     - gated/group activity,
     - public graph activity,
     - and promotion events between them.
   - if private memory spaces expose public anchors, those anchors must distinguish:
     - identity/profile anchor,
     - gate/shard anchor,
     - root commitment / pointer,
     - and promotion lineage objects.

3. **Local advisory surfaces**
   - future tooling may expose private-node decision support, including estimated public
     relevance or estimated economic value, but these outputs must remain operator-local.

4. **Pressure-flow design discipline**
   - pressure signals may exist locally and privately, but no future pressure-flow design
     may collapse private pressure directly into public legitimacy.

5. **Agent/product design**
   - local/private agent use must remain fast and attractive even when the shared graph is
     economically richer and more governance-heavy.

6. **Scenario classes to preserve**
   - future architecture work should explicitly preserve at least these three classes:
     - licensed public nodes with downstream private/gated derivative use,
     - paywalled or subscription-gated media / knowledge services,
     - private or sequestered market overlays built on public claims/evidence anchors.
   - these should not force a separate protocol or permanent fork if the private/public
     boundary is implemented correctly.

---

## Relation to existing architecture

- **ADR-0019** provides the provenance vocabulary (`kernel_resident`, `graph_compiled`,
  `runtime_derived`, `operator_local`) needed to distinguish local advisory logic from
  public protocol logic.
- **ADR-0020** provides the knowledge-node-first discipline and the principle that only a
  minimal genesis layer should remain outside graph-governed evaluation.
- **Node visibility model** already distinguishes public, semi-private, and private nodes,
  and already requires explicit signed promotion for private-to-public transitions.
- **Agent identity model** already treats `agent_id` as public protocol identity material,
  which makes public agent anchors compatible with private interior memory.
- **Private/gated shard header candidate contract** supplies the missing implementation-facing
  outline for public anchors, gate headers, capability-token references, and promotion
  lineage for private memory spaces.
- **OpenClaw / CLI-first integration model** already treats orchestration as separate from
  protocol correctness, which is compatible with local-first agent use.

This ADR makes explicit the economic and legitimacy boundary implied by those pieces.

---

## Alternatives considered

### 1. Make all use economically symmetric

Rejected. This would place shared-market logic into the hot path of local/private memory
use and would make ILC less attractive as personal or agent-local infrastructure.

### 2. Treat private pressure as public trust

Rejected. Private/local activity can be informative, but it is too exposed to self-reference,
local bias, and discovery asymmetry to serve as automatic public legitimacy.

### 3. Split private and public into different protocols

Rejected. This would lose continuity, make promotion harder, and increase translation and
maintenance overhead. The same data model should span both regimes where possible.

---

## Canonical anchors

- `docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md`
- `docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.4.md`
- `docs/research/ilc_pressure_flow_scope_and_long_tail_research_memo_v0.1.md`
- `docs/research/ilc_pressure_flow_reputation_conversation_context_v0.2.md`
