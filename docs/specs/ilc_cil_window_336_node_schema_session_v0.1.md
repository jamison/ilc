# ILC Conversation Intelligence Log (CIL)
## Session: Window 336 Node Schema / Trajectory Discussion
## Coverage: "Administrative aside" question through end of session

Status: working document — input for Codex dialogue
Date: 2026-03-02
Prepared by: Local architectural reviewer (Claude Sonnet 4.6)

Classification key:
- A — Blocking: must resolve before current or next window
- B — Scheduled: known future window, not blocking
- C — Event-triggered: opens when a named condition is met
- D — Open: worth tracking, no timeline; CDL candidate
- E — Discard: won't pursue
- F — Captured: already in spec/MEMORY artifact; pointer only

---

## Item 01 — Development trajectory and known unknowns

**Class**: F (captured in coherence report 336) + D (unknown unknowns still open)

**Summary**: User assessed ILC as having a clear path to a distributable package. Reviewer agreed with the structural assessment but identified five known unknowns and four unknown unknowns.

**Known unknowns (all tracked):**
1. ADM-003 gap (7+1 panel behavioral role) — Class A, Window 338
2. CDL-021 (Rust/WASM) — Class B, deferred explicitly in CDL
3. Genesis execution protocol (formal codification pre-public) — Class B, pre-deployment
4. Economic validation (does the reuse-centrality model produce intended incentives at scale?) — Class C, opens when pilot data available
5. 7+1 panel implementation — Class B, Window 338+

**Unknown unknowns (monitoring items):**
- Stochastic agent compliance gap (agents claiming to run CDL-V7 gate but not actually doing so)
- Multi-agent coordination failure under network partition
- Epoch migration with live economic data (untested at scale)
- Regulatory surface emergence (not a design problem now; becomes one at public deployment)

**Captures**: `docs/specs/ilc_integration_coherence_report_336_v0.1.md` (known unknowns). Unknown unknowns not yet in any artifact.

**Codex note**: We want Codex's assessment of the unknown unknowns list — are there additional categories we're missing? Specifically: does Codex see architectural gaps that could cause distributable-package failure that we haven't anticipated?

---

## Item 02 — Noise control architecture (CDL-V7 as quality elevator)

**Class**: F (captured in synthesis doc + CDL ratifications)

**Summary**: The core architecture controls against noisy agents through four layered mechanisms: CDL-V7 (post-submission Popperian gate for elevation), CDL-V3 (cluster diversity preventing correlated noise), CDL-V2 (sybil resistance preventing identity-amplified noise), CDL-V1 (temporal decay muting unreinforced noise). The gate is a quality elevator, not a pre-submission filter.

**Critical correction documented**: Gate is POST-submission only. All content reaches the raw graph. Gate determines what gets elevated to Corroborated Node status.

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 4.1; all V-series CDL ratifications (Phases 330-335).

**Codex note**: No action needed. Confirming the architecture is correct as documented.

---

## Item 03 — Reputation scores as noise mitigation

**Class**: D (open, no CDL lane yet)

**Summary**: Reputation scores should function as an additional noise-mitigation layer alongside the four V-series CDL mechanisms. High-reputation agents' corroboration events carry more weight; low-reputation agents' challenges are less likely to successfully quarantine nodes.

**Gap**: Reputation score mechanism is not yet specified as a protocol-level construct. It exists conceptually but has no schema definition, update rules, or CDL anchor.

**Timing**: Should enter CDL pipeline alongside or after validation lifecycle (Layer 4) canonicalization. Cannot specify reputation update rules before `validation_state` state machine is ratified.

**Codex note**: We want Codex's view on the reputation model design: (1) should reputation be global or domain-scoped? (2) how does reputation interact with the 7+1 panel quorum ladder (L-tiers)? (3) is reputation a first-class graph construct (nodes about agents) or a protocol-layer aggregate?

---

## Item 04 — Agent diversity ecosystem

**Class**: D (design assumption, not yet documented in spec)

**Summary**: The expected ILC agent ecosystem is heterogeneous: high-lucidity/high-precision agents (domain experts, formal verifiers), creative/generative agents (high-noise, high-novelty), and everything in between. The architecture must accommodate all types without penalizing creative agents for noise that is appropriate to their epistemic lane.

**Key design implication**: `epistemic_type` routing is load-bearing for ecosystem health. `creative_speculative` nodes must not be penalized by a gate designed for `objective` nodes. If gate routing fails (wrong type assigned), creative agents get incorrectly penalized and exit the ecosystem.

**Gap**: No specification for how agent type influences gate routing defaults, or how agents declare their epistemic lane tendencies.

**Codex note**: We want Codex's view on agent type declarations — should agents have a protocol-level `agent_profile.primary_epistemic_lane` field that biases default gate routing for their submissions?

---

## Item 05 — Gate verdict as objective node (guards are guardable)

**Class**: F (captured in synthesis doc) + D (operational specification still open)

**Summary**: The act of applying the Popperian gate to a node, and the resulting verdict, is itself a proposed objective node on the graph, subject to refutation. This closes the "guards are guardable" philosophical problem — no authoritative evaluation escapes epistemic scrutiny.

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 4.3.

**Open operational gap**: The convergence mechanism for adversarial recursive challenge chains is not specified. CDL-V1 temporal decay provides natural damping, but explicit economic convergence rules (stake penalties for losing refutation chains, bounded challenge depth) need specification.

**Codex note**: We want Codex's view on the convergence mechanism. Is bounded challenge depth the right answer (e.g., max 3 levels of meta-refutation), or should the system rely purely on stake economics + temporal decay to achieve natural convergence?

---

## Item 06 — Gate routing field (popperian_eligible)

**Class**: D (needs CDL lane; pre-canon captured in synthesis doc)

**Summary**: A `gate_routing` field (or `popperian_eligible` flag) should be added to Layer 2 of the node schema to make gate applicability explicit. Routing must be cheap (type-table lookup), deterministic, and non-recursive. The routing rule is a constitutional primitive, not a knowledge claim.

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 4.2.

**Open design question**: Should `gate_routing` be an explicit field, or should it derive automatically from `epistemic_type` by rule? The risk of an explicit field: agents can set `gate_routing = exempt` on objective nodes to bypass the gate. The risk of automatic derivation: composite nodes with mixed epistemic types have no override mechanism.

**Codex note**: We want Codex's view on this field design trade-off: explicit field with validation constraints vs. automatic derivation with composite-node handling.

---

## Item 07 — Epistemic type taxonomy (four types)

**Class**: F (captured in synthesis doc) + D (ratification lane needed)

**Summary**: Four `epistemic_type` values: `objective`, `subjective`, `normative`, `creative_speculative`. Source is pre-canon synthesis artifact. Also surfaced: richer structural/lifecycle classifications from historical archives (Genesis, Frontier, Canonical, Reference, Anchor, Corroborated, Finalized, Divergence-tree nodes).

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 3; `docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`.

**Timing**: CDL ratification lane for `epistemic_type` enum needed before Layer 2 schema can be considered canonical. Blocks gate routing specification.

**Codex note**: We want Codex's view on the boundary between `normative` and `objective` — particularly for engineering decisions and domain expertise claims. Is this distinction operationally tractable, or does it collapse under adversarial classification gaming?

---

## Item 08 — Privacy / off-chain node design

**Class**: F (captured in synthesis doc)

**Summary**: `node.scope.visibility` (public/semi-private/private), promotion protocol, gate control nodes, shadow economics, `lab.*` shards for company off-chain extension. Key invariant: private nodes do not inherit public-graph corroboration; promotion requires a separate public-graph gate process.

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 5.

**Open question**: When a private node is promoted to public, does its private-graph economic history (staking, shadow attribution) carry forward? Not yet specified. Economic incentive implications are significant.

**Codex note**: We want Codex's view on promotion continuity. Does private economic history carry forward (incentivizes promotion but creates gaming surface) or not (cleaner but reduces promotion incentive)?

---

## Item 09 — Executable (agentic) nodes

**Class**: F (captured in synthesis doc) + D (formal spec needed)

**Summary**: Executable nodes are structured metadata descriptors (not raw code). Agent-side sandboxing (WASM). Agent independently decides whether to execute. Safety contract CID required. Genesis-trusted flag for protocol-seeded nodes.

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 6.

**Major gap**: Execution descriptor format, WASM interface version negotiation, safety contract schema, and agent-side sandboxing requirements are all unspecified. Needs a dedicated CDL lane before agentic nodes can be deployed.

**Codex note**: We want Codex's view on the executable node security model — specifically: (1) how does agent-side sandboxing get enforced without protocol enforcement? (2) should the safety contract be an on-graph attestation node, or a separate off-graph certificate? (3) what constitutes "safe" execution for a WASM module that declares network side effects?

---

## Item 10 — Custom tags and quorum elevation

**Class**: F (captured in synthesis doc) + A (ADM-003 gap must be resolved first)

**Summary**: `meta: object` for free-form extension. System-reserved fields cannot be overridden. 7+1 panel can propose promoting `meta.*` fields to system-reserved via CDL ratification (public nodes only, CDL-V5 migration path applies).

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 7.

**Blocking dependency**: ADM-003 must define 7+1 panel's graph monitoring role before quorum elevation can be specified. Panel has no current mechanism to identify which `meta.*` fields have sufficient adoption to be elevation candidates.

**Codex note**: We want Codex's view on whether quorum elevation of custom fields is the right abstraction, or whether we should instead define a richer initial reserved-field set and eliminate the elevation mechanism entirely (simpler, but less adaptive).

---

## Item 11 — Push/pull node header broadcasting

**Class**: F (captured in synthesis doc)

**Summary**: Gossip protocols with push/pull mechanics for agent fabric. Narwhal/Tusk DAG mempool + Bullshark ordering for finalized knowledge blocks. Gossip fabric for all-agent sync. Push = minimal node header (node_id, creator_agent_id, epistemic_type, visibility, channel, epoch_created, payload_cid, signature). Pull = full payload on demand.

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Section 8.

**Open gap**: Node header format, signing scope, serialization format, and versioning are not formally specified. Narwhal/Tusk/Bullshark integration points with ILC's epoch boundaries need explicit mapping.

**Codex note**: We want Codex's view on whether the Narwhal/Tusk/Bullshark stack is the right choice for ILC's specific requirements, or whether there are better-suited consensus/dissemination layers given ILC's epistemic graph semantics (as opposed to financial transaction ordering).

---

## Item 12 — Complete 8-layer node schema and gap map

**Class**: F (captured in synthesis doc)

**Summary**: 8-layer schema synthesized from historical archives, ADM-001, D2 minimal schema, and this session's architectural discussion. Layers 1 and 5 have real specification support. Layers 4 (validation lifecycle), 6 (executable nodes), and 8 (network header) are almost entirely unspecified.

**Captures**: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` Sections 9-10.

**Codex note**: This is the primary artifact for Codex review. We want Codex to: (1) identify any gaps we missed, (2) challenge the layer decomposition (is 8 layers right? should some merge?), (3) assess which gaps are most architecturally load-bearing for a v1 distributable package.

---

## Item 13 — ADM-003 gap (7+1 panel graph monitoring role)

**Class**: A — BLOCKING for Window 338+

**Summary**: ADM-003 (agent behavioral roles) omits the 7+1 evaluation panel as a defined agent behavioral role. Multiple downstream features depend on the panel having a graph monitoring function: quorum elevation of custom fields, validation lifecycle governance, quarantine/promotion decisions, `primitive_type` canonicalization. Must resolve before Window 338+ implementation begins.

**Tracking**: `TODO.txt` (existing entry); `docs/specs/ilc_integration_coherence_report_336_v0.1.md` (documented gap).

**Codex note**: We want Codex's view on what the ADM-003 resolution should look like — specifically, should the 7+1 panel's graph monitoring role be defined as a new agent behavioral profile in ADM-003, or as a separate governance spec document that ADM-003 references?

---

## Item 14 — `primitive_type` enum canonicalization

**Class**: D — open, no CDL lane yet

**Summary**: `primitive_type` (Layer 1) enum values are unspecified. Historical candidates: `assertion`, `observation`, `instruction`, `executable`, `governance_proposal`, `refutation`, `citation`. Needs canonicalization before Layer 1 schema is complete.

**Open design question**: Is `refutation` a `primitive_type` value, or is it always expressed as an edge type? If refutations are edges, what is the `primitive_type` of a node that exists solely to refute another node?

**Codex note**: We want Codex's view on the `primitive_type` vs. edge-type boundary — particularly for refutation/divergence nodes.

---

## Item 15 — Authored payload vs protocol metadata vs transport header split

**Class**: D — open architectural constraint

**Summary**: The node model should explicitly separate (a) immutable authored payload, (b) protocol-interpreted metadata and lifecycle outcomes, and (c) derived transport/header surfaces. If these are collapsed into one object shape, schema evolution and transport optimization will become brittle.

**Why it matters**:
- authored content should remain content-addressed and immutable,
- protocol outcomes such as quorum records and gate verdicts should attach by reference rather than mutate authored payload,
- transport headers should be derivable/cacheable without becoming the authoritative semantic object.

**Captures**: discussed in the Window-336 node-schema synthesis follow-up; not yet formalized in a dedicated artifact.

**Codex note**: We want Codex's view on whether the unified schema should be modeled explicitly as a three-envelope structure rather than a single flat object with optional fields.

---

## Transmission Summary for Codex

### What this document is

A structured capture of architectural discussions from the Window 336 coherence session. Items are classified by urgency and action type. Items marked Class F are already captured in `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`. Items marked Class A or D need Codex input.

### Primary artifact to review first

`docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md` — the 8-layer node schema synthesis. This is the central output of the session and the primary thing we want Codex to analyze and push back on.

### Follow-up artifact to review second

`docs/specs/ilc_node_schema_concretization_proposals_v0.1.md` — proposed answers and default architectural decisions intended to turn the synthesis questions into a concrete future work plan.

### Follow-up artifact to review third

`docs/specs/ilc_window_338_347_node_schema_program_plan_v0.1.md` — proposed Window 338-347 sequencing for the node-schema contract window, with runtime work explicitly deferred until after later ratification.

### Top 5 questions for Codex (in priority order)

1. **ADM-003** (Item 13): What should the 7+1 panel's graph monitoring role look like as a spec? New ADM-003 section or separate governance doc?

2. **Convergence mechanism** (Item 05): For adversarial recursive gate-verdict challenge chains — bounded depth, stake economics, or pure temporal decay?

3. **Reputation model** (Item 03): Global or domain-scoped? First-class graph construct or protocol aggregate? How does it interact with L-tier quorum ladder?

4. **Narwhal/Tusk/Bullshark fit** (Item 11): Is this the right consensus/dissemination stack for ILC's epistemic graph semantics specifically?

5. **Private node promotion continuity** (Item 08): Does private economic history carry forward on promotion to public? What are the gaming implications either way?

### Items to explicitly discard (none currently proposed)

No items from this session are recommended for discard. The trajectory discussion (Item 01) identified "unknown unknowns" that are monitoring items rather than active design problems — but they should remain on record, not discarded.
