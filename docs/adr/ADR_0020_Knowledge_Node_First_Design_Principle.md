# ADR-0020: Knowledge-Node-First Design Principle

**Status:** Accepted
**Date:** 2026-03-20
**Author:** Jamison and Sonnet 4.6
**Source:** Window 441-449 session discussion, 2026-03-20
**Dependencies:** ADR-0019, ADM-003 v0.2, CDL-V7
**Accepted:** Phase 1157, 2026-05-04
**Acceptance token:** `adr_0020_accepted_phase_1157`

**Scope of acceptance:** ADR-0020 is accepted as the durable
knowledge-node-first design principle and migration discipline for governable
information surfaces. Acceptance does not immediately migrate all constants,
working notes, or bootstrap artifacts into graph-native nodes; those migrations
remain staged by later Atlas/runtime work.

---

## Context

ILC's epistemic graph provides a general-purpose substrate for representing, evaluating, and
governing information: knowledge nodes with provenance, panel-evaluated claims with quorum
ratification, reputation-weighted agents, and ECU staking for skin-in-the-game incentives.

The question arises repeatedly during design work: when should a new system capability be
expressed as a new governance mechanism, and when should it be expressed as knowledge nodes
governed by existing mechanisms?

ADR-0019 establishes the architectural boundary for graph-native governance compilation (what
is kernel-resident vs. graph-compilable). ADR-0020 extends that into an actionable design
principle and checklist for all new system components.

The core insight is that the panel/quorum/reputation machinery is already a general-purpose
evaluation infrastructure. Every additional governance mechanism created alongside it rather
than on top of it increases complexity, reduces composability, and misses the compounding
returns of the underlying substrate.

This principle is sometimes called "homoiconic" or "reflective" system design: the system
represents and governs itself using the same data structures and mechanisms as everything
else. The ILC application of this principle at the network level is: governance rules,
network parameters, documentation, and history are all candidates for knowledge-node
representation, evaluated by the same panel/quorum/reputation machinery.

---

## Decision

### 1. Knowledge-Node-First design check (mandatory)

For any new system component that involves governed information, policy, a parameter, or a
rule surface, the first design question must be:

> **"Can this be a knowledge node governed by existing mechanisms?"**

If yes, that is the preferred path. A new governance mechanism is justified only when the
existing panel/quorum/reputation machinery genuinely cannot serve the use case.

This check applies to:
- new governance parameters (quorum thresholds, staking rules, penalty coefficients),
- new policy surfaces (activation flags, protocol rules, schema profiles),
- new documentation artifacts intended to persist and be queried by agents,
- new historical records intended to serve as orientation material in distribution packages.

### 2. Governance parameters as graph migration targets

Governance constants currently embedded in the runtime or in genesis-layer specifications
should be classified and tracked as migration targets for the graph:

- CDL constants (e.g. `quorum_threshold`, `max_cluster_share_ceiling`,
  `distinct_cluster_floor`) belong in this category.
- After genesis, these constants should have a defined graph-migration plan: from runtime
  constants to ratified knowledge nodes with version history and panel-approval history.
- In the interim, every such constant must be tagged with its provenance class per ADR-0019
  (`kernel_resident`, `graph_compiled`, `runtime_derived`, or `operator_local`).

### 3. Documentation as knowledge nodes (with scope constraints)

Stable, ratified project documentation is a natural candidate for knowledge-node
representation post-genesis:

**Appropriate candidates (post-genesis migration):**
- Master Principle List and ratified CDL evidence artifacts — have survived challenge,
  have clear version history, serve as orientation for new agents.
- Ratified design specifications (ratified ADR rows, ratified CDL rows).
- Release-package orientation guides — new agents querying the graph should be able to
  receive highest-reputation onboarding nodes rather than relying on operator-injected
  context.

**Excluded (knowledge-node cost exceeds benefit):**
- Working documentation: drafts, ephemeral phase notes, in-progress specs — content
  changes too frequently for panel evaluation overhead to pay off.
- Genesis bootstrap documentation: must exist in plain form before the graph can evaluate
  it (circularity guard — see Section 5).

**The capsule system is already a proof of this principle** at the distribution layer
(versioned, structured, provenance-bound context artifacts). Extend it; do not replace it
with ad hoc formats.

### 4. Test for genesis layer membership

Not all information can be placed on the graph. The genesis layer (CDL-001 signer lineage,
initial validator roster, minimum quorum diversity) must be pre-determined because there is
no graph yet to ratify it.

**Test for genesis layer membership:**

> *Can this information be wrong without catastrophic failure?*

- If **yes** → belongs on the graph. Panels can correct it after genesis.
- If **no** (cryptographic identity roots, signer lineage, genesis roster diversity
  minimums) → belongs in the genesis layer.

**Goal:** make the genesis layer as small and stable as possible, then migrate everything
else to the graph.

### 5. Circularity guard

The system cannot use its own evaluation machinery to bootstrap itself. Genesis-layer
documentation must exist in plain form (outside the graph) before the graph is operational.
The circularity guard is:

> *No knowledge node may be required to exist before the graph can accept knowledge nodes.*

---

## Consequences

**Positive:**
- Reduces proliferation of bespoke governance mechanisms.
- Maximizes composability: every new system component that becomes a knowledge node
  inherits panel evaluation, quorum ratification, confidence scoring, reputation effects,
  and ECU staking for free.
- The epistemic layer becomes progressively more self-describing and self-governing as
  governance parameters and documentation migrate to the graph post-genesis.
- New agents can bootstrap from graph-native orientation nodes rather than requiring
  operator-injected context packages.

**Tradeoffs:**
- Requires design discipline: the knowledge-node-first question must be asked proactively,
  not retroactively.
- Panel evaluation overhead is non-trivial. The check must distinguish "can be a knowledge
  node" from "should be one now." Working documentation and ephemeral artifacts should not
  be knowledge nodes.
- Genesis bootstrapping still requires a minimal pre-determined layer. The goal is to
  minimize this layer, not eliminate the bootstrapping constraint.

---

## Sooner-rather-than-later implications

1. **CDL constants migration plan:** `quorum_threshold`, `max_cluster_share_ceiling`,
   `distinct_cluster_floor`, and similar CDL constants should each have a documented
   migration-target classification before production genesis.

2. **Documentation migration inventory:** After Window 450+ CDL-050 resolution, a
   documentation migration inventory should identify which ratified specs are candidates
   for knowledge-node migration at genesis.

3. **Epistemic finality claims:** The proposed future `epoch_finality_attestation`
   knowledge-node type (agents filing claims about epoch state with ECU/reputation staking,
   evaluated by 7+1 panels hierarchically) is a direct application of this principle at
   the consensus layer — epoch finality expressed as knowledge nodes governed by existing
   mechanisms rather than as a new bespoke finality protocol. See planned ADR-0021.

4. **Capsule extension:** The context capsule system (v0.1 → v1.9) should be extended to
   track knowledge-node-first classification decisions alongside phase deliverables.

---

## Relation to ADR-0019

ADR-0019 establishes the boundary between kernel-resident and graph-compilable surfaces
(what can be graph-native). ADR-0020 adds the prior design-check step (should this be a
knowledge node) and the practical migration discipline for governance parameters and
documentation. These two ADRs are complementary and should be read together.

---

## Alternatives considered

### 1. Handle on a case-by-case basis without a formal principle

Rejected. Without a formal first-question design check, each design discussion will
default to creating bespoke mechanisms. The compounding returns of the substrate are lost
through uncoordinated decisions.

### 2. Require all new components to be knowledge nodes immediately

Rejected. The bootstrapping constraint is real: the genesis layer cannot be placed on the
graph before the graph exists. Working documentation and high-churn artifacts have panel
overhead that exceeds their benefit as knowledge nodes.

### 3. Defer until after genesis

Rejected. The migration-target classification for governance constants and documentation
must be decided before genesis to avoid lock-in of ad hoc designs that become expensive to
migrate later.

---

## Canonical anchors

- `docs/adr/ADR_0019_Graph_Native_Governance_Compilation_Boundary.md`
- `docs/specs/ilc_adm_003_panel_and_quorum_management_v0.2.md`
- `docs/specs/ilc_integration_coherence_report_336_v0.1.md` (L-tier ladder and 7+1 panel)
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (CDL-V7 Popperian gate)
- `Z_Past_Chats/20260320_ILC - Epistemic Finality Panel Architecture and Graph-Native Design.txt`
