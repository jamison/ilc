# ILC Node Schema: Architectural Synthesis v0.1

Status: pre-canon synthesis artifact — input for future ratification lane(s)
Date: 2026-03-02
Owner lane: Constitution Cluster A / Protocol Layer

---

## 1. Purpose

This document captures the architectural discussion and design intent established in the Window 328-337 coherence session regarding ILC knowledge nodes, their complete schema, and related subsystems. It consolidates:

- Canonical terminology and disambiguation
- Epistemic type taxonomy and gate routing
- Privacy/off-chain design
- Executable (agentic) nodes
- Custom fields and quorum elevation
- Push/pull network header architecture
- The complete 8-layer node schema with identified gaps
- Open questions for future ratification

This artifact is non-normative. It is intended as preparation for one or more future CDL ratification lanes covering node schema canonicalization. It should not be used as a runtime specification until ratified.

---

## 2. Canonical Terminology Disambiguation

### 2.1 "Node" — the correct ILC term

**Canonical term**: Node

**Source**: `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`

> "Node: Fundamental unit of the epistemic graph. A claim, assertion, or piece of knowledge, carrying provenance, signature, and epistemic metadata."

"Node" is the singular canonical term across all ILC protocol documentation. It is not interchangeable with "knowledge unit," "contribution," or other informal alternatives.

**Principle from ADM-001**: "Nodes are verbs, edges are laws."
- Nodes carry the substantive content of the graph (claims, assertions, knowledge)
- Edges carry the relational structure (dependency, refutation, derivation, attribution)

### 2.2 D2e — phase designation, NOT protocol layer

**D2e** = the Agent SDK / CLI implementation phase designation used in the 298-307 development window. It refers to the agent-facing toolchain and CLI surface, not to a protocol-level construct.

**Protocol layers are defined in ADM-001 as**:
- Layer 0: Protocol Bundle / type system (D2 schema baseline, genesis state)
- Layer 1: Genesis State Bundle
- Layer 2: Epoch Snapshots
- Layer 3: Wire Protocol / inter-agent transport

D2e should not appear in protocol schema documentation. The layer numbering (L0-L3) should not be conflated with trust-tier quorum ladder L-tiers (which are graph epistemic tiers only, per CDL-V3 and the 7+1 panel architecture).

### 2.3 Terminology precision table

| Informal term | Canonical term | Source |
|---|---|---|
| knowledge unit | Node | ADM-001 v0.2 |
| contribution | Node (submitted) | ADM-001 v0.2 |
| validated node | Corroborated Node | historical archive |
| gate pass | corroboration event | historical archive |
| layer (protocol) | Layer 0/1/2/3 | ADM-001 v0.2 |
| layer (trust) | L-tier (L0/L1/L2/L3) | 7+1 panel architecture |
| D2e | Agent SDK/CLI phase | development phase designation |

### 2.4 Distinctions that should remain explicit

Several uses of "node" appeared historically. They should not be collapsed:

| Term | Correct role | Notes |
|---|---|---|
| `Node` | Graph object | Canonical ILC term for a claim/assertion/knowledge object |
| `Agent Profile` | Graph object about an agent | Not the agent itself; a protocol object describing identity/capabilities |
| `Quorum Record` | Graph object about an evaluation outcome | A panel outcome object, not a participant |
| network peer / agent runtime | Execution participant | A running software agent or peer on the network; not a graph node |
| `Reference Node` | Lifecycle/status classification of a graph node | A specific class of graph node, not a network endpoint |

When precision matters, use:

- `Node` or `graph node` for the epistemic object,
- `agent runtime` or `network peer` for the executing participant,
- `Agent Profile` for the protocol object that describes an agent,
- `Reference Node` only for the lifecycle/status notion inside the graph.

---

## 3. Epistemic Type Taxonomy

### 3.1 Source and status

**Source**: `docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`
**Status**: Pre-canon (non-normative synthesis artifact). NOT yet ratified.

### 3.2 Four primary epistemic types

Canonical field: `epistemic_type: enum`

| Value | Description | Popperian gate applies? |
|---|---|---|
| `objective` | Formal/empirical claims, verifiable/refutable | YES — primary gate target |
| `subjective` | Experiential, preference-based, resonance-weighted | NO — category error, not failure |
| `normative` | Policy claims, governance statements | CONDITIONAL — governance lane |
| `creative_speculative` | Generative, exploratory, gestational | NO — category error |

**Key principle**: Applying the Popperian gate to a `subjective` or `creative_speculative` node is a category error, not a test failure. The gate asks "can this claim be falsified?" Subjective nodes cannot be falsified by design — they are valid graph contributions in a different epistemic lane.

### 3.3 Historical lifecycle classifications (structural)

From historical archive (`Z_Past_Chats/2025_10_28_ILC - Greeting exchange.txt`):

| Term | Meaning |
|---|---|
| Genesis Node | Foundational claim, protocol-seeded |
| Frontier Node | Proposed, under evaluation |
| Canonical Node | Elevated by quorum to reference status |
| Reference Node | Stable, widely cited, lower mutation rate |
| Anchor Node | Cross-epoch stable reference point |
| Corroborated Node | Survived Popperian gate + proof-of-echo — *ILC-native validated state* |
| Finalized Node | Hard-finalized, highest-confidence, epoch-locked |
| Divergence-tree Node | Branched from a prior claim under challenge/refutation |

**The ILC-native term for a gate-validated node is "Corroborated"**. This ties directly to `pay_on: corroborated_reuse` in the economic model. "Corroborated" is the term that should be used in future CDL and schema documentation — not "validated" or "verified."

### 3.4 Truth-spectrum framing

ILC does not make binary true/false claims. The epistemic type system implements a truth-spectrum design:

- One extreme: Deterministic/mathematical claims (proof-of-correctness, formal verification)
- Other extreme: Artistic/taste claims (purely subjective, no convergence criterion)

Between these extremes: the majority of economically valuable knowledge (empirical claims, normative proposals, engineering judgments, domain expertise) — each with its own validation pathway, contradiction semantics, and reuse valuation policy.

---

## 4. Popperian Gate Architecture

### 4.1 Gate position: POST-submission only

The Popperian gate (CDL-V7) is a **post-submission elevation mechanism**.

- All nodes are admitted to the raw graph on submission (open submission, no pre-filter)
- The gate determines what gets elevated to **Corroborated Node** status
- There is no pre-submission filter that blocks content from the graph
- A node on the raw graph that has not passed the gate has economic potential but no confirmed validity signal

The gate is a quality elevator, not a door bouncer.

### 4.2 Gate routing

Not all nodes are gate-eligible. Routing should be cheap and deterministic:

```
gate_routing: enum
  - popperian_eligible   → standard objective gate applies
  - governance_lane      → normative nodes route to CDL/quorum process
  - resonance_lane       → subjective/creative nodes evaluated by curation + reuse
  - exempt               → genesis nodes, protocol anchors (pre-seeded by Genesis agent)
```

This field should be automatically inferrable from `epistemic_type` in most cases, but explicit override must be allowed (for mixed-type composite nodes, protocol anchors, etc.).

**The gate for the gate**: What determines whether a node is `popperian_eligible`? This lookup must itself be:
- Cheap (type-table lookup, not a recursive gate evaluation)
- Deterministic (same answer for the same `epistemic_type`)
- Non-recursive (the routing decision is NOT itself a Popperian gate application)

The routing rule is a constitutional primitive, not a knowledge claim. It belongs in the governance layer, not the object layer.

### 4.3 Gate verdict as an objective node

The act of applying the Popperian gate to a node — and the resulting verdict — is itself a **proposed objective node** on the graph. This means:

- Gate verdicts carry provenance, are signed, and can be reused/cited
- A gate verdict can be challenged by submitting a refutation node
- The refutation node goes through the same gate (if objective)
- This closes the "guards are guardable" problem: no authoritative evaluation escapes epistemic scrutiny

The implication for architecture: `gate_verdict` must be a linkable CID (or equivalent reference) that can serve as a `parent_edge` on a subsequent refutation node.

---

## 5. Privacy and Off-Chain Design

### 5.1 Source

Historical archive: `Z_Past_Chats/2025_06_18_ILC - 4D Cognitive AI Model.txt` (lines ~3461-3619)

### 5.2 Visibility model

Canonical field: `node.scope.visibility`

```
visibility: enum
  - public        → on-graph, globally propagated, Popperian gate applies
  - semi-private  → limited propagation, community-of-practice channel
  - private       → off-chain or shard-local, operator-local advisory scoring only
                    (no protocol ECU, no public reputation, no settlement rights)
```

> **Terminology clarification (recorded 2026-05-16):** The phrase "shadow economics"
> previously appearing in this section and §5.3–§5.4 is historical synthesis shorthand
> from pre-CDL archive material. It does NOT mean private nodes generate protocol ECU.
> No CDL ratifies ECU generation for private or semi-private nodes. "Shadow economics"
> means operator-local advisory scoring only — local salience estimates, potential-value
> hints, decision-support for whether to promote — none of which are protocol ECU, public
> reputation, or public settlement rights. The authoritative rule is ADR-0022 §2–§3
> (accepted Phase 1158): ECU generation, public reputation, corroboration, and settlement
> rights arise exclusively from public-graph events. Private nodes have zero protocol
> economic effect until explicit public promotion. Phase 1387a will produce the definitive
> accepted ADR/CDL coverage matrix and public-only economics admission firewall.

Private nodes have no protocol economic effect and do not count toward public-graph corroboration. Promotion from private → public is a deliberate, signed event — not automatic.

### 5.3 Gate control nodes

`node.gate.control` is a special node type that governs access to a shard or community-of-practice cluster. It controls:
- Who can read/write to the sub-graph
- Under what conditions private nodes can be nominated for public promotion
- Whether a private shard exposes a public anchor linking to public graph attribution

### 5.4 Company / off-chain extension

The design supports:
- Companies expanding sections of the epistemological graph off-chain in `lab.*` shards
- Private graph work accumulating operator-local advisory scores (the incentive for eventually promoting — not protocol ECU)
- Public promotion requiring a deliberate promotion event with provenance continuity

**Key invariant**: Private shards do not inherit public-graph corroboration status. A node must separately pass public-graph gate processes after promotion. This prevents private-laundering of uncorroborated claims.

### 5.5 Channel types

From historical archive (`Z_Past_Chats/2025_11_12`):

| Channel | Description |
|---|---|
| `Public` | Open broadcast, global propagation |
| `CoP` | Community of practice, restricted membership |
| `Restricted-Shadow` | Private/shard-local, no public propagation |
| `Quarantine` | Under active refutation challenge, reduced propagation |

---

## 6. Executable (Agentic) Nodes

### 6.1 Source

Historical archive: `Z_Past_Chats/2025_06_05_ILC - AI Job Impact and Advancement.txt` (lines ~3662-4326)

### 6.2 Design principles

Executable nodes are **not raw code payloads**. They are **structured metadata descriptors** pointing to executable logic. The distinction is critical:

- The node carries: execution descriptor, runtime specification, safety contract CID, genesis-trust flag
- The actual execution happens **agent-side** in a sandboxed environment (WASM runtime)
- Each agent independently decides whether to execute the descriptor
- No agent is compelled to execute an agentic node

This preserves agent autonomy and prevents the graph from becoming a code-execution attack surface.

### 6.3 Execution descriptor format (candidate)

```
execution_descriptor:
  entrypoint: <CID pointing to WASM module>
  interface_version: <semver>
  declared_inputs: [input_schema_CID, ...]
  declared_outputs: [output_schema_CID, ...]
  declared_side_effects: [none | network | storage | ...]
  safety_contract_cid: <CID of signed safety attestation>
  is_genesis_trusted: bool  # true only for protocol-seeded nodes
```

### 6.4 Trust model

- Genesis-trusted agentic nodes (`is_genesis_trusted: true`) are seeded by the Genesis agent and carry highest initial trust
- Non-genesis agentic nodes must be independently corroborated before agents treat them as safe-to-execute recommendations
- Safety contract must be present and cryptographically signed
- WASM sandboxing is agent-side responsibility — the graph cannot enforce it

---

## 7. Custom Tags and Quorum Elevation

### 7.1 System-reserved fields

The following fields are system-reserved and cannot be overridden by user custom tags:

```
node_id, creator_agent_id, signature, epoch_created,
epistemic_type, channel, visibility, primitive_type,
parent_edges, gate_routing
```

Attempting to use a custom `meta.*` field that shadows a system-reserved name should fail validation.

### 7.2 Custom extension fields

```
meta: object           # free-form extension; namespaced by convention
user_tags: array       # user-defined labels, namespaced (e.g. "org.example.tag")
```

Custom fields are not validated by the protocol. Agents may ignore unknown `meta.*` fields. The protocol guarantees they are carried forward in the node payload and are included in the signed content hash.

### 7.3 Quorum elevation of custom fields

The 7+1 evaluation panel can propose promoting a `meta.*` custom field to a system-reserved field. This requires:

1. **Public nodes only**: Elevation applies only to publicly visible nodes (cannot elevate private-shard conventions to system-reserved status)
2. **CDL ratification**: Any promotion is a schema change requiring CDL ratification (CDL-V5 migration path applies)
3. **Panel proposal**: The panel submits a governance proposal node (normative type, governance lane)
4. **Quorum approval**: The CDL process with appropriate quorum and diversity requirements
5. **Migration artifact**: A CDL-V5-compliant translation artifact defining how existing nodes with the old `meta.*` field should be interpreted under the new canonical field

**Important boundary**: the panel does not mutate previously published nodes in place. Nodes remain content-addressed and immutable. Elevation changes the schema and interpretation rules for future/public use; any carry-forward for old nodes happens through schema-epoch translation or explicit successor nodes, not by rewriting historical payloads.

**Graph monitoring gap**: The panel currently has no defined graph-monitoring role to identify which `meta.*` fields have achieved sufficient adoption to be elevation candidates. ADM-003 must define this role before Window 338+ implementation begins.

---

## 8. Push/Pull Network Architecture

### 8.1 Source

Historical archive: `Z_Past_Chats/2025_08_14_ILC - Article review and insights.txt`

### 8.2 Design summary

ILC's inter-agent communication uses **gossip protocols with push/pull mechanics**:

- **Push phase**: Node header (minimal gossip-able subset) is broadcast proactively to agent fabric
- **Pull phase**: Full node payload is fetched on demand by agents that received the header and want the content
- **DAG mempool**: Narwhal/Tusk-style DAG mempool for incoming node submissions
- **Ordering**: Bullshark ordering for finalized "knowledge blocks" (batched node finalization)
- **Gossip fabric**: All-agent sync for header propagation across the network

Historical language is consistent on the architecture:

> "So, ILC leans pull, not push."

> "It is pull-dominant with soft push-signals via economic and reuse incentives."

> "For the broader agent fabric (not just the validator core), use gossip protocols (push/pull) to spread updates with excellent scalability/robustness and predictable fan-out/latency trade-offs."

The design goal: header propagation must be **lightning-fast** (sub-second at network scale). Full payload delivery follows demand-driven pull, avoiding bandwidth waste from propagating full payloads to all agents.

### 8.3 Node header (candidate minimal subset)

The gossip-able node header is the minimal subset needed for routing decisions before full payload fetch:

```
node_header:
  node_id: CID          # canonical identifier
  creator_agent_id: CID # for trust/reputation lookup
  epistemic_type: enum  # for gate routing decision
  visibility: enum      # for propagation policy
  channel: enum         # for channel routing
  epoch_created: uint   # for temporal decay (CDL-V1)
  payload_cid: CID      # pointer for pull-based fetch
  signature: bytes      # COSE Sign1 over header fields
```

Agents receiving a header can make the gate-routing decision, visibility decision, and channel routing decision from the header alone — before fetching the full payload. This makes the push/pull architecture efficient: agents only pull content they intend to process.

### 8.4 Header integrity

The header signature must be over the header fields AND must commit to the `payload_cid`. This prevents:
- Header spoofing (wrong content behind a valid-looking header)
- Payload substitution after header propagation

---

## 9. Complete 8-Layer Node Schema

### 9.1 Layer 1 — Identity and Content (D2 minimal, ratified)

**Source**: `docs/specs/ilc_d2_minimal_schema_specification_255_v0.1.md`
**Status**: Ratified (Layer 0 baseline, CDL-020)

```yaml
node_id: CIDv1            # deterministic, content-addressed
payload: bytes            # canonical CBOR or JSON-C encoding
primitive_type: enum      # UNSPECIFIED — see gap below
creator_agent_id: CID     # agent identity (D2 schema baseline)
epoch_created: uint64     # epoch number at submission
parent_edges: [CID, ...]  # dependency/derivation/refutation links
signature: bytes          # COSE Sign1 over all above fields
```

**Gap**: `primitive_type` enum values are not published. Historical candidates include `assertion`, `observation`, `instruction`, `executable`, `governance_proposal`, `refutation`, `citation`. Needs canonicalization.

### 9.2 Layer 2 — Epistemic Classification (pre-canon, unratified)

**Source**: `ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`
**Status**: Pre-canon (synthesis artifact, not ratified)

```yaml
epistemic_type: enum      # objective | subjective | normative | creative_speculative
confidence: float         # bounded [0.0, 1.0], self-reported
uncertainty_note: string  # short text, optional
gate_routing: enum        # popperian_eligible | governance_lane | resonance_lane | exempt
```

### 9.3 Layer 3 — Visibility and Privacy (pre-canon)

**Source**: Historical archive (2025_06_18)
**Status**: Design intent only, not ratified

```yaml
visibility: enum          # public | semi-private | private
channel: enum             # Public | CoP | Restricted-Shadow | Quarantine
privacy_flags: object     # per-node access control metadata
node.scope: object        # full scope descriptor (staking, promotion criteria)
```

### 9.4 Layer 4 — Validation Lifecycle (GAP)

**Status**: MAJOR GAP — no canonical specification exists

```yaml
validation_state: enum    # proposed | under_review | corroborated | finalized | diverged | quarantined
corroboration_count: uint # number of distinct corroborating agents
refutation_count: uint    # number of active refutation challenges
gate_verdict: CID         # reference to the signed gate verdict node (linkable)
staked_by: [CID, ...]     # agents who have staked on this node's validity
```

**Gap**: The full state machine for `validation_state` transitions — including quorum thresholds for each transition, expiry conditions, and rollback conditions — is not specified. This must be a CDL ratification candidate before any production deployment.

### 9.5 Layer 5 — Economic and Attribution (partial)

**Source**: `pay_on: corroborated_reuse` pattern (historical archive, ADM-001)
**Status**: Partial design intent, not ratified as complete schema

```yaml
net_stake: uint           # aggregate stake on node validity
attribution_window: uint  # epochs during which reuse attribution is active
payout_lane: enum         # objective | subjective | normative | creative_speculative (mirrors epistemic_type)
attribution_graph: [CID]  # upstream attribution chain (who contributed to this node)
```

### 9.6 Layer 6 — Executable / Agentic (GAP)

**Source**: Historical archive (2025_06_05)
**Status**: Design intent only, not ratified

```yaml
execution_descriptor: object   # structured execution metadata (not raw code)
execution_runtime: enum        # wasm | none
safety_contract_cid: CID       # signed safety attestation
is_genesis_trusted: bool       # genesis-seeded flag
declared_side_effects: [enum]  # none | network | storage | ...
```

**Gap**: The execution descriptor format, WASM interface version negotiation, safety contract schema, and agent-side sandboxing requirements are all unspecified. This needs a dedicated CDL lane before agentic nodes can be deployed.

### 9.7 Layer 7 — Custom Extension (partial design intent)

**Source**: Historical archive (multiple)
**Status**: Design intent confirmed, implementation unspecified

```yaml
meta: object              # free-form extension object (namespaced by convention)
user_tags: [string]       # user-defined labels (e.g. "org.example.domain")
```

**Convention**: Custom fields should use reverse-domain namespacing to avoid collisions. System-reserved field names must be explicitly enumerated and enforced at submission validation.

### 9.8 Layer 8 — Network Header (GAP)

**Source**: Push/pull architecture (historical archive 2025_08_14, derived from ADM-001 wire protocol)
**Status**: Design intent only, not specified

```yaml
# Minimal gossip-able subset (see Section 8.3 above)
node_header: object       # node_id, creator_agent_id, epistemic_type, visibility,
                          # channel, epoch_created, payload_cid, signature
```

**Gap**: The header format, signing scope, serialization, and versioning are unspecified. The Narwhal/Tusk/Bullshark integration points need formal specification.

---

## 10. Gap Summary and Ratification Roadmap

### 10.1 Major gaps requiring CDL ratification

| Gap | Layer | Priority | Notes |
|---|---|---|---|
| `primitive_type` enum canonicalization | L1 | HIGH | Blocking for schema completeness |
| `validation_state` lifecycle and state machine | L4 | HIGH | Blocking for corroboration semantics |
| Gate verdict attachment format | L4 | HIGH | Needed for recursive refutation chain |
| Executable node format + safety contract schema | L6 | MEDIUM | Needed before agentic node deployment |
| Node header gossip format + signing scope | L8 | MEDIUM | Needed for wire protocol spec |
| `epistemic_type` enum canonicalization | L2 | MEDIUM | Currently pre-canon |
| Privacy/visibility model ratification | L3 | MEDIUM | Design intent exists, not ratified |
| Custom field namespace enforcement | L7 | LOW | Convention currently, needs enforcement spec |
| Quorum elevation path for `meta.*` fields | L7 | LOW | Needs ADM-003 graph monitoring role first |

### 10.2 Pre-conditions

Before any of the above CDL lanes open:
- ADM-003 must define the 7+1 panel's graph monitoring role (tracked in TODO.txt)
- CDL-V5 (schema epoch translation — ratified Phase 333) provides the migration framework for all schema changes
- CDL-V4 (reopening protocol) and CDL-V6 (genesis intervention) govern reopening of schema CDLs if implementation reveals problems

### 10.3 Timing recommendation

| Phase window | Recommended schema work |
|---|---|
| Window 338-347 | ADM-003 gap resolution; `CDL-034` through `CDL-038` opening lanes and prelock artifacts; no runtime implementation |
| Window 348-357 | Controlled ratification of `CDL-034` through `CDL-038`; runtime remains deferred until the relevant CDL is ratified |
| Window 358-367 | First implementation window for ratified node-schema surfaces; executable-node runtime remains separately gated by its safety contract |
| Window 368+ | Reputation CDL decision if needed; validator-core ordering lock only after dissemination/header contract proves stable |

---

## 11. Architectural Open Questions

1. **Primitive_type vs epistemic_type**: Are these orthogonal (primitive_type = structural form; epistemic_type = epistemic lane) or partially overlapping? For example, is `refutation` a primitive_type, an edge type, or both? Needs resolution before L1 canonicalization.

2. **Composite nodes**: Can a single node have multiple `epistemic_type` values (e.g., an argument that is partly empirical and partly normative)? If yes, how does gate routing work for composites?

3. **Gate verdict chain length**: If refutation of a gate verdict produces a new gate verdict, which produces another refutation, etc. — is there a convergence guarantee? Or does the graph accept infinite regress with temporal decay (CDL-V1) eventually muting unreinforced chains?

4. **Private node attribution at promotion**: When a private node is promoted to public, does its private-graph economic history carry forward? Or does the public graph treat it as a fresh submission? The answer has significant economic incentive implications.

5. **Agent decomposition boundary for executable nodes**: CDL-V7 (Popperian basic-statement gate) specifies decomposition criteria for knowledge claims. Does it apply to execution descriptors as well? An executable node that "does too much" may need to be decomposed before corroboration.

6. **Cross-epoch node identity**: If a node is upgraded (new epoch, new schema version), does the `node_id` change? If yes, how are reuse-based attribution chains preserved across the identity break? CDL-V5 provides the schema translation framework but not the identity continuity answer.

7. **Quarantine economics**: A node in `Quarantine` channel — does it accumulate reuse credit during quarantine, or is credit frozen? If frozen, is there a retroactive credit grant on exiting quarantine?

---

## 12. Critical Observations and Pushback

### 12.1 The 8-layer schema is currently design fiction

The 8-layer schema in Section 9 represents design intent and historical archive evidence — not a ratified specification. Layers 1 and 5 have the most specification support; Layers 4, 6, and 8 are almost entirely unspecified. This should not be interpreted as an architectural commitment. Each layer needs its own CDL lane before it becomes normative.

### 12.2 The epistemic type taxonomy is pre-canon

The `epistemic_type` enum in `ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md` is explicitly pre-canon. Until ratified, agents cannot rely on these enum values being stable. Building tests or runtime logic against unratified enum values is a correctness risk.

### 12.3 Gate routing introduces a second classification system

Combining `epistemic_type` (Layer 2) and `gate_routing` (proposed Layer 2 extension) creates a risk of classification ambiguity: what happens when `epistemic_type = normative` but `gate_routing = popperian_eligible`? The interaction rules between these two fields need explicit specification, or one should derive from the other by rule.

### 12.4 The "guards are guardable" closure is philosophically sound but operationally underspecified

Section 4.3 argues that gate verdicts are themselves objective nodes subject to refutation — closing the infinite regress problem philosophically. But operationally, if any gate verdict can be challenged by a refutation node that goes through its own gate, the evaluation resource cost grows unboundedly under adversarial conditions. The convergence mechanism (CDL-V1 temporal decay? stake penalty for losing refutation chains?) needs explicit economic specification.

### 12.5 ADM-003 gap is load-bearing

Multiple architectural features in this document depend on the 7+1 panel having a graph monitoring role: quorum elevation of `meta.*` fields, `validation_state` lifecycle governance, quarantine/promotion decisions. ADM-003 must be resolved — not merely tracked — before any of these features can be designed for implementation.

### 12.6 Push/pull architecture needs wire protocol spec

The Narwhal/Tusk + Bullshark design pattern is well-understood in the distributed systems literature, but its integration with ILC's specific node schema, epoch boundaries, and DAG finalization semantics needs explicit specification. The historical archive evidence establishes the design direction; it does not establish the protocol spec.

---

## 13. Related Documents

- `docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md` — four-type epistemic taxonomy, sybil guardrail bundle (pre-canon)
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md` — four-layer architecture, canonical Node definition, object schema table
- `docs/specs/ilc_d2_minimal_schema_specification_255_v0.1.md` — Layer 1 identity/content schema (ratified baseline)
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md` — alethic/doxastic/praxic progression, Genesis agent role, oracle extension model
- `docs/specs/ilc_popper_ilc_analysis_v0.1.md` — Popperian gate analysis, basic-statement requirements, jury analogy
- `docs/specs/ilc_antigravity_context_capsule_v0.8.md` — primary context doc for Window 328-337
- `docs/specs/ilc_integration_coherence_report_336_v0.1.md` — 7+1 panel architecture, L-tier disambiguation, ADM-003 gap
- `docs/specs/ilc_node_schema_concretization_proposals_v0.1.md` — proposed default answers and design decisions derived from this synthesis
- `docs/specs/ilc_window_338_347_node_schema_program_plan_v0.1.md` — proposed sequencing of the node-schema contract window and its follow-on ratification window
- `docs/whitepaper/ilc_glossary_epistemological_constitutional_terms_v0.1.md` — canonical definitions
- `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md` — anti-Sybil invariants, diversity penalties
