# ILC Node Schema Concretization Proposals v0.1

Status: pre-canon proposal set — input for Window 338+ planning  
Date: 2026-03-03  
Owner lane: Constitution Cluster A / Protocol Layer

---

## 1. Purpose

This document turns the open questions in `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` into concrete proposed answers. It is not a ratified specification. It is the recommended default posture if the project wants to move from broad architecture discussion into implementable schema planning.

The working assumption here is pragmatic:

- prefer explicit boundaries over clever flexibility,
- preserve content-addressed immutability,
- keep constitutional semantics separate from transport/runtime convenience,
- do not let the evaluation-panel mechanism quietly become the constitutional governance mechanism.

---

## 2. Executive Recommendations

### 2.1 Recommended answers to the five main questions

1. **ADM-003 panel role**
   - Add a new behavioral-role section in `ADM-003` for the evaluation panel and a separate graph-observation / schema-evolution role.
   - Do **not** overload the 7+1 evaluation panel with continuous graph-monitoring duties by default.
   - `ADM-003` should define the role boundary; a separate governance artifact should define the workflow.

2. **Recursive gate-verdict convergence**
   - Keep the graph unbounded in what it can represent.
   - Bound the protocol obligation, economic weight, and operational status effects of recursive verdict disputes.
   - Allow challenge chains to exist, but only the latest eligible verdict within a bounded review depth should affect node status or payouts.

3. **Reputation model**
   - Use a hybrid model:
     - low-weight global integrity score,
     - domain-scoped competency/reliability vectors.
   - Reputation should be a protocol-derived aggregate published through `Agent Profile` / attestation objects, not an inline node field.

4. **Transport/ordering stack**
   - Keep `pull-dominant gossip + CID fetch` as the architectural invariant.
   - Treat `Narwhal/Tusk/Bullshark` as a reference pattern for later high-throughput ordering, not as a constitutional commitment for v1.
   - Window 338+ should specify the header/fetch contract first, then revisit validator-core ordering.

5. **Private -> public promotion continuity**
   - Carry forward provenance continuity, not public economic credit.
   - Promotion should preserve lineage links and optional disclosed audit history, but public corroboration/reuse economics should begin only after promotion.

### 2.2 Additional recommendation not in the original five

The unified schema should be modeled as a **three-envelope architecture**:

- **Authored Payload Envelope** — immutable, signed, content-addressed
- **Protocol Interpretation Envelope** — lifecycle, corroboration, quorum, governance attachments by reference
- **Transport Envelope** — fast header/advertisement/fetch subset

This should be treated as a core design constraint for the future node-schema CDL lane.

---

## 3. Concrete Proposed Answers

## 3.1 ADM-003: panel role and graph observation

### Proposed answer

`ADM-003` should define two distinct roles:

1. **Evaluation Panel Member**
   - participates in 7+1 review boards,
   - evaluates task outputs, decomposition validity, and ILC attribution,
   - does not continuously survey the whole graph.

2. **Graph Observation / Schema Evolution Analyst**
   - monitors public-graph patterns,
   - surfaces candidate field-elevation proposals,
   - publishes evidence summaries for governance lanes,
   - does not directly ratify schema changes.

### Why this is the right split

The 7+1 mechanism is case-evaluation infrastructure. Continuous graph observation is an analytics/governance-preparation function. Conflating them creates three problems:

- the panel quietly becomes a standing constitutional authority,
- operational burden grows without explicit design,
- implementation roles become confused in ADM-003.

### Implementation consequence

Window 338+ should treat ADM-003 resolution as a prerequisite for any custom-field elevation or validation-lifecycle work.

---

## 3.2 Recursive gate-verdict challenge chains

### Proposed answer

Use this rule set:

1. The graph may contain arbitrarily deep challenge chains.
2. The protocol only treats a bounded suffix of the chain as operationally relevant.
3. Each meta-challenge must:
   - target the latest eligible verdict,
   - include explicit stake,
   - include fresh evidentiary basis or decomposition basis,
   - pay a higher challenge cost than the previous layer.
4. Only the latest eligible verdict inside the bounded operational window affects:
   - `validation_state`,
   - payout eligibility,
   - quarantine/corroboration status.

### Recommended bounded operational rule

- `operational_verdict_depth_max = 2`

Meaning:
- original claim evaluation,
- challenge to that evaluation,
- challenge to the challenge,
- deeper chains may exist on graph but do not automatically alter node status until collapsed back into first-order evidentiary claims.

### Why not a hard graph-level depth limit

A hard depth limit on graph expression is philosophically wrong for ILC. It suppresses representation. The correct place to bound is the protocol obligation and economics, not what the graph can represent.

### Why not rely on decay alone

Decay helps, but decay alone is too weak under coordinated adversarial activity. The system also needs stake escalation and bounded operational relevance.

---

## 3.3 Reputation model

### Proposed answer

Reputation should be **hybrid**:

- **Global integrity component**
  - measures behavior that is domain-independent:
    - signing consistency,
    - fraud / compromise history,
    - challenge honesty,
    - panel-service reliability.

- **Domain-scoped competency component**
  - measures reliability inside declared knowledge domains or shard families.

### Recommended representation

Do **not** store reputation as a mutable inline field on every node.

Instead:
- derive it from graph history,
- publish periodic signed aggregates through `Agent Profile` and/or `Quorum Record`-adjacent attestation objects,
- let runtimes recompute if they distrust the published aggregate.

### Interaction with the L-tier ladder

The L-tier ladder should not become a disguised reputation ladder.

Recommended relationship:
- reputation gates **panel eligibility** and may weight reviewer selection,
- L-tier quorum thresholds remain about epistemic claim evaluation levels,
- CDL-V3 diversity floor still dominates cluster-structure protection.

### Strong boundary

Reputation should influence *who gets trusted to evaluate*, not *what is true*.

---

## 3.4 Transport / ordering stack

### Proposed answer

The project should constitutionally commit to this invariant:

- **header-first dissemination**,
- **CID-addressed pull fetch**,
- **content-addressed verification before interpretation**.

It should **not yet** constitutionally commit to Narwhal/Tusk/Bullshark as the permanent validator-core ordering layer.

### Recommended stance

- Treat Narwhal/Tusk/Bullshark as a strong reference pattern.
- Keep CDL-024 and future node-header work transport/orderer-agnostic where possible.
- Define a minimal v1 contract around:
  - header schema,
  - fetch API semantics,
  - signature scope,
  - retry/idempotence,
  - epoch visibility rules.

### Why this is the right choice

The high-value invariant is fast shareability + deterministic fetch/verify semantics. The exact consensus/orderer stack can be revised later if deployment reality differs from theory.

---

## 3.5 Private -> public promotion continuity

### Proposed answer

Promotion should preserve:
- provenance continuity,
- optional disclosed lineage hashes,
- optional disclosed local-shadow audit history.

Promotion should **not** automatically preserve:
- public corroboration counts,
- public reuse counts,
- public reputation credit,
- public payout entitlement.

### Recommended rule

On promotion:
- the promoted public node is treated as a new public submission for corroboration/economic purposes,
- but it may link to a `promotion_receipt` object carrying:
  - private lineage commitment,
  - origin-shard identifier,
  - disclosed review history hashes,
  - promotion signer(s),
  - timestamp/epoch.

### Why this is the right compromise

This preserves auditability without allowing private rehearsal to manufacture public epistemic legitimacy.

---

## 4. Additional Proposed Answers

## 4.1 `gate_routing`: explicit or derived?

### Proposed answer

Use a **derived field with bounded override**, not a free explicit field.

Rule:
- default `gate_routing` is derived from `epistemic_type`,
- override is allowed only for a small constitutionally enumerated set of structural cases,
- override must be validated against `primitive_type` and/or protocol role.

### Example

- `objective` -> `popperian_eligible`
- `subjective` -> `resonance_lane`
- `creative_speculative` -> `resonance_lane`
- `normative` -> `governance_lane`
- protocol-seeded genesis anchors -> `exempt`

### Why not a free explicit field

A free explicit field creates the exact gaming surface you already identified: agents can try to masquerade a claim into the wrong validation lane.

---

## 4.2 `primitive_type` vs `epistemic_type`

### Proposed answer

These should be **orthogonal**.

- `primitive_type` answers: what structural/protocol thing is this?
- `epistemic_type` answers: what kind of epistemic claim is being made?

### Recommended initial `primitive_type` family

- `claim`
- `observation`
- `proposal`
- `citation`
- `executable_descriptor`
- `receipt`
- `promotion_receipt`
- `quorum_record_ref`

### Important recommendation

Do **not** make `refutation` a `primitive_type`.

Refutation is better modeled as:
- a semantic relation / edge role,
- or a claim with refutational intent,
- not as a wholly separate primitive ontology class.

Why:
- many refutations are still just claims/observations with a specific relational target,
- making `refutation` primitive risks duplicating edge semantics at the node layer.

---

## 4.3 Composite nodes

### Proposed answer

A node should have **one primary `epistemic_type`**, not a list.

If a submission mixes empirical, normative, and speculative material, the decomposition mechanism should separate it into multiple nodes.

### Why

Allowing multiple epistemic types per node breaks:
- gate routing,
- validation policy clarity,
- economic lane clarity,
- contradiction semantics.

This is exactly why CDL-V7 matters.

---

## 4.4 Executable nodes and CDL-V7 decomposition

### Proposed answer

Yes: CDL-V7 should apply to executable descriptors, but at the descriptor-claim level, not at the raw code level.

The executable node must be decomposable into falsifiable claims such as:
- declared inputs,
- declared outputs,
- declared side effects,
- safety assertions,
- determinism guarantees,
- bounded resource guarantees.

### Consequence

An executable descriptor that cannot be decomposed into basic-statement-style claims should not receive corroborated status.

---

## 4.5 Cross-epoch node identity

### Proposed answer

If authored payload bytes change, `node_id` changes.

Identity continuity should be preserved by explicit linkage, not by pretending the CID stayed the same.

### Recommended mechanism

Use:
- successor links,
- translation receipts,
- epoch-transition receipts,
- attribution carry-forward rules.

### Why this is correct

Trying to preserve the same identity across changed content would break content-addressing.

---

## 5. Three-Envelope Node Model

This is the strongest architectural recommendation in this document.

## 5.1 Envelope A — Authored Payload Envelope

Immutable, signed, content-addressed.

Suggested contents:

```yaml
authored_payload:
  node_id: CIDv1
  payload: bytes
  primitive_type: enum
  creator_agent_id: CID
  epoch_created: uint64
  parent_edges: [CID]
  signature: bytes
  epistemic_type: enum
  confidence: float | null
  uncertainty_note: string | null
  visibility: enum
  channel: enum
  meta: object
  user_tags: [string]
```

This is the thing the submitter authors and signs.

## 5.2 Envelope B — Protocol Interpretation Envelope

Derived or attached by protocol operations, not by mutating authored payload.

Suggested contents:

```yaml
protocol_interpretation:
  validation_state: enum
  gate_routing: enum
  gate_verdict_refs: [CID]
  quorum_record_refs: [CID]
  corroboration_count: uint
  refutation_count: uint
  quarantine_state: enum
  promotion_receipt_ref: CID | null
  attribution_status: object
```

`gate_routing` belongs here if it is materialized at all. It is a protocol-layer derivation from
`epistemic_type` plus any ratified override rules. It is not submitter-controlled authored payload.

This should generally live as attached objects / derived views, not as inline mutation of Envelope A.

## 5.3 Envelope C — Transport Envelope

Minimal dissemination and fetch surface.

Suggested contents:

```yaml
transport_header:
  node_id: CID
  payload_cid: CID
  creator_agent_id: CID
  epistemic_type: enum
  visibility: enum
  channel: enum
  epoch_created: uint64
  signature: bytes
```

This is what gets pushed rapidly; the rest is pulled.

## 5.4 Why this structure matters

Without this split, the project will blur:
- authored truth claims,
- governance/evaluation outcomes,
- dissemination optimization layers.

That would make:
- schema evolution harder,
- CDL-V5 translation harder,
- transport optimization riskier,
- immutability guarantees less clear.

---

## 6. Proposed Window 338+ Work Breakdown

Recommended ordering:

1. **ADM-003 resolution**
   - define panel role boundary
   - define graph observation / schema evolution role

2. **Unified node schema contract + evidence prelock**
   - lock three-envelope model
   - lock `primitive_type` candidate set
   - lock authored/protocol/transport boundary

3. **Validation lifecycle contract**
   - `validation_state` machine
   - verdict attachment model
   - recursive challenge operational bound

4. **Node header / dissemination contract**
   - transport header fields
   - fetch semantics
   - visibility/channel interaction

5. **Executable node contract**
   - execution descriptor schema
   - safety contract schema
   - decomposition requirements for executable claims

6. **Privacy promotion economics contract**
   - `promotion_receipt`
   - shadow-history disclosure rules
   - no automatic public credit carry-forward

This breakdown is now sequenced concretely in:
- `docs/specs/ilc_window_338_347_node_schema_program_plan_v0.1.md`

That program plan keeps Window 338-347 limited to role resolution, CDL opening, and prelock work. Ratification and any later runtime implementation are deliberately deferred.

---

## 7. Recommended Defaults to Carry Forward Immediately

Even before ratification work starts, these should be treated as default design assumptions in discussion:

- use `Node` as the canonical graph-object term,
- do not use `D2e` as a protocol-layer term,
- keep the system pull-dominant with fast header dissemination and on-demand fetch,
- preserve node immutability; never solve governance by mutating published payloads,
- treat reputation as derived and mostly domain-scoped,
- keep `primitive_type` and `epistemic_type` separate,
- keep one primary epistemic lane per node,
- separate authored payload, protocol interpretation, and transport header.

---

## 8. Non-Recommendations

These are approaches I do **not** recommend:

- letting the 7+1 panel directly rewrite or reinterpret historical node payloads,
- free explicit `gate_routing` chosen by submitters,
- multiple epistemic types per node,
- automatic public economic credit carry-forward from private shards,
- making `refutation` a first-class primitive type by default,
- over-committing to Narwhal/Tusk/Bullshark before the header/fetch contract is specified,
- storing mutable reputation inline on nodes.

---

## 9. Relationship to Existing Artifacts

This document concretizes questions raised in:
- `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`
- `docs/specs/ilc_cil_window_336_node_schema_session_v0.1.md`
- `docs/specs/ilc_window_338_347_node_schema_program_plan_v0.1.md`

It should be read as the next-step proposal layer:
- synthesis = what we know,
- CIL = what needs follow-up,
- concretization proposals = what we should tentatively decide unless stronger evidence appears,
- program plan = how the tentatively decided work should be sequenced.
