# ILC Simplified Epistemic Model — Synthesis v0.1

Status: Non-normative synthesis artifact
Date: 2026-03-20
Owner lane: G8 Constitution Cluster A

This document supersedes the four-type epistemic enum proposed in
`docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`
section 3, and records the design decision to replace it with a simpler three-mode routing
model. It is intended to prepare a future ratification lane, not to mutate runtime behavior.

---

## 1. Design decision: drop the static epistemic type enum

The four-type enum (`objective`, `subjective`, `normative`, `creative_speculative`) proposed
in the prior pre-canon artifact treated epistemic classification as a static property declared
at node creation time. This approach has two problems:

1. **Classification burden**: requiring every submitter to classify every node before
   submission adds bureaucratic overhead that conflicts with the organic routing philosophy
   at the core of ILC's praxic epistemology.

2. **Static vs. dynamic**: a node's epistemic status is not fixed at creation. A subjective
   claim can accumulate corroborating reuse evidence over time; an objective claim can be
   refuted. Classification should emerge from behavior, not be asserted upfront.

The correct Popperian position is: you do not *declare* a claim objective. You demonstrate it
by attaching falsifiable criteria and surviving challenges.

Most nodes should exist on the graph and route through economic gravity. Organic reuse
pressure — not top-down classification — is the primary value-routing mechanism. This is
consistent with the praxic epistemological foundation established in
`docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`.

---

## 2. The three-mode routing model

Under this proposed model, all nodes would enter the graph without a mandatory type
classification. Routing to one of three evaluation modes would be determined by the presence
or absence of a single optional schema field and by runtime anomaly signals, not by a
pre-declared type enum. None of the following is ratified; this section describes the proposed
design for a future ratification lane.

### Mode 1: Default reuse-valuation (all nodes)

Every node on the graph receives reuse-weighted centrality valuation by default. "Valuable"
means "gets reused by agents who are themselves frequently reused" — a StarRank
eigenvalue measurement over the reuse graph. This is ILC's praxic epistemological core.

No explicit epistemic classification is required. Subjective content, creative work, cultural
artifacts, and normative claims coexist with empirical claims on the same graph, distinguished
by their reuse patterns rather than type tags. A widely reused song, a foundational scientific
claim, and a governance policy statement all exist on the same graph and are all valued by
organic reuse centrality.

Economic pressure routes agents toward high-value nodes organically. Top-down classification
is not required for this to function.

### Mode 2: Popperian elevation path (opt-in via `refutation_criterion`)

An agent who wants a node treated as an objective, falsifiable claim would attach a
`refutation_criterion` field at submission. Presence of this field would opt the node into
the Popperian evaluation path:

- The node would become eligible for corroboration: surviving challenge attempts would raise
  its credibility tier toward a `corroborated_reuse` designation (proposed future vocabulary,
  not yet ratified).
- Refutation of the node would follow the novelty-requirement protocol documented in
  `docs/specs/ilc_refutation_novelty_requirement_v0.1.md`.
- Refutation rewards would be proportional to the reuse centrality of the refuted node at
  the time of refutation submission, not at the time of the original node's creation.
- Nodes that survive challenge would receive the `corroborated_reuse` designation —
  this term is proposed here as future economic vocabulary and is not yet ratified.

This path is opt-in, not mandatory. Nodes without a `refutation_criterion` field are not
penalized — they are valued by reuse alone. Applying the Popperian gate to nodes that did
not opt in is a category error.

### Mode 3: Anomaly-triggered auditor review (contested nodes)

Auditor selection and diversity controls are not applied universally to every node. They
activate when specific anomaly signals are detected:

- Centrality spike in a short time window without organic citation history.
- Citation cluster with high internal density and low external reuse.
- New agents with no prior track record suddenly citing heavily.
- A participant files a formal challenge claiming adversarial reuse optimization.

On anomaly trigger, a randomized auditor panel is activated. Panel selection uses the
diversity mechanism from `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md` —
random selection from eligible auditors. This is diversity-by-random-selection, not de-facto
enforcement of agent type or model diversity. The panel reviews the flagged node and either
clears it (centrality stands) or applies a correction.

This design applies diversity controls where they are needed without imposing them as
universal overhead on every node.

---

## 3. Anti-gaming: staking and reputation

The primary anti-gaming mechanism is economic, not classificatory. Staking requirements for
node submission and refutation create skin-in-the-game that discourages spam and gaming
without requiring top-down enforcement:

- **Node submission staking**: proportional to the claim's scope or citation ambition.
  Frivolous submissions are economically discouraged.
- **Refutation staking**: required to submit a refutation. A refutation that fails the novelty
  requirement or is successfully challenged results in a stake loss and reputation record.
- **Reward proportionality**: refutation rewards are proportional to the reuse centrality of
  the refuted node at refutation submission time. Gaming newly-submitted low-centrality nodes
  is unprofitable by construction.
- **Reputation history**: track record of successful vs. failed submissions and refutations
  feeds into staking eligibility and auditor panel weighting.

Reputation and staking together create a self-regulating system: high-quality contributors
accumulate reputation that lowers their effective staking cost and increases their panel
authority; low-quality or gaming contributors accumulate reputation debts that raise their
costs and restrict their access.

This mechanism is consistent with organic routing philosophy. Agents self-regulate through
economic pressure without requiring classification-based bureaucracy.

---

## 4. Normative claims

Normative claims (policy positions, governance statements, constitutional design choices) do
not require a mandatory type tag. Agents submitting normative claims are encouraged to use an
optional `normative: true` metadata flag to signal that Popperian falsifiability criteria are
not applicable. This prevents normative nodes from being incorrectly challenged on empirical
grounds.

This is a lightweight signal, not an enum value with associated routing logic. It requires no
validation on submission and carries no economic consequence by itself.

---

## 5. The objective/subjective spectrum in practice

Nodes exist on a spectrum between fully objective (mathematical proofs, reproducible
measurements) and fully subjective (aesthetic preferences, cultural resonance). Neither end
requires special treatment under this model:

- Fully objective nodes are well-served by the Popperian elevation path: attach refutation
  criteria, survive challenges, accumulate corroboration.
- Fully subjective nodes are well-served by reuse-valuation alone: a widely reused song has
  high centrality; a niche cultural artifact has lower centrality but is not penalized.
- Most economically valuable nodes fall in between: their value is partially demonstrable and
  partially experiential. The three-mode model handles this naturally — the node can opt into
  partial Popperian evaluation for its demonstrable components while accumulating reuse
  centrality across its full content.

The gradient between objective and subjective is reflected in network behavior around a node
(reuse, challenge, corroboration patterns), not in a binary type declaration at creation time.

---

## 6. Open items for future ratification lane

1. Formal schema definition for `refutation_criterion` field: structure, required elements,
   validation rules.
2. Staking contract specification: amounts, penalty structure, reputation feed mechanism.
3. Anomaly detection algorithm specification: what patterns trigger Mode 3 activation and
   what thresholds govern panel size.
4. `corroborated_reuse` economic designation rules: what combination of survived challenges
   and reuse centrality qualifies a node.
5. Temporal decay interaction with Mode 1 centrality (CDL-V1 candidate): how reuse events age
   and lose weight, and whether decay rate is uniform or type-sensitive.
6. `normative: true` flag formalization: whether this becomes a ratified schema field or
   remains advisory.

---

## 7. Relationship to existing documents

- Supersedes: four-type enum in
  `docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`
  section 3.
- Retains and elevates: Sybil guardrail bundle in
  `docs/specs/ilc_subjective_objective_epistemic_type_and_sybil_guardrails_precanon_v0.1.md`
  section 5 (rearchitected as anomaly-triggered rather than universal).
- Epistemological foundation:
  `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`.
- Novelty requirement companion:
  `docs/specs/ilc_refutation_novelty_requirement_v0.1.md`.
- Anti-Sybil controls:
  `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md`.
- Node schema:
  `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`.
