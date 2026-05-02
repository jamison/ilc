# ADR-0035: Homoiconic Type Definition System

**Status:** DRAFT — direction accepted, implementation deferred
**Date:** 2026-04-28
**Author:** Local architectural reviewer (Claude Sonnet 4.6)
**Trigger:** Window 1102–1109 naming discussion; `hyperedge_type` string literals identified
as a governance gap
**Forward obligation:** CDL required before any runtime change; no implementation in Window
1102–1109

`adr_0035_homoiconic_type_definition_system_direction_accepted`
`adr_0035_implementation_deferred_pending_cdl`

---

## 1. Context

The ILC knowledge graph has two parallel type systems today:

**Level 1 — `NodeType` (Literal string in `ilc_core/types.py`):**
```python
NodeType = Literal[
    "genesis", "claim", "refutation", "task", "star_map",
    "proposal", "genesis.schema", "genesis.blob", "hyperedge_entity",
]
```

**Level 2 — `HyperEdge.hyperedge_type` (free string in `ilc_core/types.py`):**
```python
hyperedge_type: str  # "panel" | "co_authorship" | "refutation_coalition" |
                     # "epoch_boundary" | "content_package"
```

Both levels are **hardcoded string literals** — their definitions, rules, and
characteristics live in Python source code and prose documentation, not in the
knowledge graph itself. This creates a governance gap:

- The rules of what "co_authorship" means cannot be queried, attributed, or disputed
  through the graph's own machinery
- Amending what "co_authorship" requires means a CDL + runtime mutation + deployment
- Disputes about whether a specific hyperedge satisfies its declared type have no
  formal adjudication path within the system
- New `hyperedge_type` values require code changes, not governance actions

ILC's core thesis — that knowledge and its governance live in the same graph — is
currently violated by having the type system outside the graph.

---

## 2. Decision

**Accept the homoiconic type definition system as the long-term architectural target.**

The target state:

1. Each `hyperedge_type` value becomes a **definition node** in the graph — a
   genesis-class node that encodes the rules, attribution behaviour, membership
   requirements, and dispute resolution path for that type.

2. `HyperEdge.hyperedge_type` becomes a **node reference** (ID pointer) rather than
   a string literal, pointing to the definition node for that type.

3. The runtime resolves type semantics by reading the definition node, not by
   switching on a string constant.

4. Amendments to what a type means go through the CDL process — the definition node
   is immutable once ratified, and amendment requires a new CDL that supersedes it.

5. Disputes about whether a specific hyperedge satisfies its declared type are
   adjudicable by a 7+1 empaneled jury, which references the definition node as
   the authoritative specification.

**This direction is accepted. Implementation is deferred pending a dedicated CDL.**

---

## 3. Rejected Alternatives

### Option A — Keep hardcoded strings (status quo)
Rejected as long-term target. Hardcoded strings are ungovernable within the system's
own machinery. Every rule change requires a code deployment. Disputes have no
in-system adjudication path.

### Option B — Multi-type node fields
Allow a `Node` to carry multiple types simultaneously (e.g., `types={"claim", "co_authorship"}`).
Rejected. Conflates content identity with ownership mode. Complicates all downstream
type-switching logic. Does not solve the governance gap — types are still hardcoded.

### Option C — Ownership as a node attribute flag
Add `is_collectively_owned: bool` or `members: dict` to `Node`. Rejected as primary
architecture. This makes ownership implicit in field presence rather than explicit
in a governable type definition. It also does not extend to non-ownership hyperedge
types (panel, refutation_coalition, etc.).

---

## 4. Design Constraints

### 4.1 Bootstrapping layer

The homoiconic type system cannot be fully self-referential. A small set of
**genesis primitives** must remain hardcoded as the axiomatic floor:

| Hardcoded primitive | Rationale |
|---------------------|-----------|
| `type="genesis"` | Axioms; immutable by definition; cannot be homoiconic |
| `type="type_definition"` | The meta-type for definition nodes; must be hardcoded to avoid infinite regress |
| `type="claim"` | Fundamental epistemic unit; pre-dates governance machinery |

All other `NodeType` and `hyperedge_type` values are migration candidates.

### 4.2 Definition node properties

A definition node must be:
- `type="type_definition"` (new NodeType to be introduced)
- Genesis-class: declared by a ratified CDL commit, immutable after ratification
- Content-addressed: its ID is derived from its content, making silent mutation detectable
- Signed: declaring agent is the CDL ratification agent
- Non-attributable: definition nodes do not participate in REUSE or CO_AUTHORSHIP
  attribution — they are infrastructure, not content

### 4.3 Retroactivity rule

When a definition node is superseded by amendment:
- Existing hyperedges retain a reference to the definition node valid at their
  creation epoch (snapshot semantics)
- The new definition applies only to hyperedges created after the amendment's
  ratification epoch
- No retroactive re-adjudication of settled attribution events

### 4.4 Runtime resolution

To avoid per-event graph traversal on the hot attribution path:
- Definition nodes are loaded into a local cache at node startup
- Cache is invalidated only on CDL ratification events (rare)
- The `settle()` path reads from cache, not from the graph store directly

### 4.5 Gaming surface

A bad actor cannot introduce a malicious definition node because:
- Only `type="type_definition"` nodes ratified via CDL are accepted by the runtime
- The CDL process is the existing constitutional gate — the attack surface is
  the same as for any other CDL mutation
- Definition node IDs are content-addressed; any tampering changes the ID and
  breaks the reference

---

## 5. Migration Path

| Phase | Action |
|-------|--------|
| Now (pre-CDL-035) | Continue using hardcoded `hyperedge_type` strings. Document existing types as definition node drafts (prose only — not yet wired). |
| CDL-035 opening | Introduce `type="type_definition"` as a new `NodeType`. Ratify definition nodes for existing `hyperedge_type` values: `co_authorship`, `panel`, `refutation_coalition`, `epoch_boundary`, `content_package`. |
| CDL-035 ratification | Runtime updated to resolve `hyperedge_type` via definition node cache. `HyperEdge.hyperedge_type` field type changes from `str` to `str` (node ID — same wire format, different semantics). |
| Post-CDL-035 | New hyperedge types require a CDL to ratify a definition node — no code change needed. |

**CDL number:** CDL-035 is the next available constitutional definition lane for this work.
(CDL-083 is reserved for H-CON-02 in Window 1102–1109; CDL-084 for PROVENANCE;
CDL-085+ for homoiconic type system — exact number to be assigned at opening.)

---

## 6. Definition Node Drafts (Informational — Not Yet Ratified)

These are prose drafts of what each definition node would contain. They are NOT
yet wired into the runtime. They serve as reference for juries and for future
CDL drafting.

### `co_authorship`

**What it means:** A set of agents (≥ 2) who jointly produced a knowledge artefact.
Membership is stake-weighted. Attribution ECU splits proportionally to each member's
stake at settlement time. Membership is dynamic: agents may buy in or exit subject
to CDL-081 §4.4 decay rules. A member may be ejected by panel quorum (H-CON-02 /
CDL-083).

**Dispute adjudication:** A jury determines whether a declared `co_authorship`
hyperedge genuinely reflects joint production or is a manufactured attribution
vehicle. Evidence: commit history, stake timeline, content provenance.

### `panel`

**What it means:** A set of agents empaneled to adjudicate a specific dispute or
governance question. Membership is fixed at empanelment. Panel decisions are
binding within their defined scope. A panel is not an attribution entity — it does
not receive REUSE or CO_AUTHORSHIP ECU.

**Dispute adjudication:** Meta-panel (higher-order jury) adjudicates disputes about
panel composition or procedure.

### `refutation_coalition`

**What it means:** A set of agents who jointly assert that a target node's claim is
invalid. Governed by CDL-V7 Popperian gate. If the coalition's refutation is upheld,
ECU attribution flows per CDL-083 (H-CON-02) rules.

**Dispute adjudication:** CDL-V7 Popperian gate is the primary arbiter. Jury
adjudicates procedural disputes about coalition formation.

### `epoch_boundary`

**What it means:** A structural hyperedge marking the close of a validation epoch.
Non-attributive — no ECU flows for REUSE or CO_AUTHORSHIP of an epoch_boundary
hyperedge. Used for temporal indexing only.

**Dispute adjudication:** N/A — epoch boundaries are system-generated, not
agent-declared.

### `content_package`

**What it means:** A bundling hyperedge grouping multiple nodes into a distributable
unit. Attribution flows to the package creator, not to the package as a collective.
Members are the packaged nodes, not agents.

**Dispute adjudication:** Jury determines whether a declared content_package
genuinely reflects a coherent bundle or is a gaming vehicle for attribution
aggregation.

---

## 7. Relationship to Existing ADRs

| ADR | Relationship |
|-----|-------------|
| ADR-0029 | Established the hypergraph substrate and star expansion pattern. ADR-0035 extends it by governing the type of hyperedge, not just its structure. |
| ADR-0019 | Graph-native governance boundary. ADR-0035 brings type definitions inside that boundary. |
| ADR-0021 | Epistemic finality claims. Definition nodes carry implicit epistemic weight — amendment requires CDL, which is an epistemic finality event. |

---

## 8. Forward Obligations

1. **CDL for `type="type_definition"` introduction** — opens a new NodeType. Requires
   human gate decision and ratification evidence.
2. **Definition node drafts → CDL-ratified nodes** — the §6 drafts must be hardened
   into ratified definition nodes before the runtime migration.
3. **`HyperEdge.hyperedge_type` field semantics change** — wire format stays `str`
   (node ID); runtime semantics change. Requires migration guide for existing data.
4. **Jury procedure for type disputes** — the 7+1 empanelment process for type
   adjudication needs a procedure spec (separate ADR or CDL annex).
5. **Decomposition recipe requirement (added 2026-05-02, Window 1130–1138)** — every
   definition node must carry a `decomposition_recipe` field specifying which truth
   primitives compose the type and in what order. Types with identical recipes must
   either be unified into a single type (with a `scope` or `role_schema` parameter
   distinguishing cases) or provide a formal written rationale for remaining distinct.
   This requirement applies before CDL ratification of any proposed type. See
   `docs/research/ilc_markov_trace_projection_and_transition_basis_v0.1.md` §3 and
   GND-0034 in `docs/sims/sim_spectral_02/genesis_node_candidate_decision_log_v0.1.md`.

---

## 9. Design Constraint Amendment — Compositional Primitive Basis

*Added 2026-05-02, Window 1130–1138.*

The 7 truth primitives established in ADR-0004 constitute the **semantic basis** for
all edge type and hyperedge type definitions. This is a design constraint on definition
nodes, complementary to the bootstrapping floor defined in §4.1.

### Compositional basis rule

Every proposed type definition must be expressible as a composition of truth primitives:

```
type_semantics = primitive₁ ∘ primitive₂ ∘ ... ∘ primitiveₙ
```

where `∘` denotes sequential application to the graph state (i.e., the first primitive
is applied to the initial state, and subsequent primitives are applied to the resulting
states). The composition need not be unique — a type may have multiple valid recipes —
but at least one valid recipe must be stated.

**Types that are irreducible** (not expressible as compositions of other primitives)
must be flagged `"irreducible": true` in their definition node. `commit.epoch` (the
EPOCH_BOUNDARY type) is the canonical example of an irreducible type: it is itself a
truth primitive and does not decompose further.

### Consequence: type proliferation governance

Before any new type is ratified via CDL:

1. State the `decomposition_recipe` (which primitives, in what order)
2. If the recipe is identical to an existing ratified type, the new type must either
   be rejected (it is the same type) or provide a `scope` / `role_schema` parameter
   that formally distinguishes the cases
3. Types that decompose as `TYPE_A + TYPE_B` where both already exist are not
   standalone new types — they are compositions and should be represented as
   sequential edge applications, not new enum values

### Known applications (Window 1130–1138 atlas work)

| Proposed type | Recipe | Status |
|--------------|--------|--------|
| `PRIMITIVE_INVOCATION` | `assert.truth ∘ link.claim` with `source_role=operator` | Review: may unify with ATTESTATION |
| `GOVERNS` | `validate.claim ∘ link.claim` | Review: identical recipe to CONSTRAINS |
| `CONSTRAINS` | `validate.claim ∘ link.claim` | Review: identical recipe to GOVERNS — unify with `scope` param |
| `LINEAGE_GOVERNS` | `link.claim ∘ commit.epoch ∘ validate.claim` = PROVENANCE + GOVERNS | Likely remove; represent as composition |
| `MORPHOGENIC_OVERLAY` | No clear primitive recipe | Reject as edge type; use node metadata |
| `EPOCH_BOUNDARY` | `commit.epoch` alone | `irreducible: true` — confirmed |

These are atlas-level determinations. Full CDL adjudication is required before any
change to the runtime `EdgeType` enum.

`adr_0035_homoiconic_type_definition_system_direction_accepted`
`adr_0035_implementation_deferred_pending_cdl`
`adr_0035_definition_node_drafts_informational_not_ratified`
`adr_0035_compositional_primitive_basis_amendment_2026_05_02`
