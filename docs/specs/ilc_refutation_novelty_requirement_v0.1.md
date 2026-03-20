# ILC Refutation Novelty Requirement v0.1

Status: Non-normative synthesis artifact
Date: 2026-03-20
Owner lane: G8 Constitution Cluster A

This document defines the novelty requirement for valid refutation submissions in the ILC
Popperian evaluation path (Mode 2 in `docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md`).
It is intended to prepare a future ratification lane, not to mutate runtime behavior.

---

## 1. The inwardness attack

The Popperian evaluation path creates a specific gaming vulnerability. An agent can:

1. Take an established high-value node,
2. Decompose it into smaller sub-claims with attached `refutation_criterion` fields,
3. Submit the sub-claims as new nodes,
4. Submit refutations of those sub-claims,
5. Earn refutation rewards without adding new knowledge to the graph.

This is the **inwardness attack**: the agent consumes the system's existing high-value content
as raw material for reward generation. No new epistemic content enters the graph. The system's
own richness becomes its attack surface.

The inverse variant also applies: an agent submits a claim as objective with deliberately weak
or trivially satisfiable refutation criteria, arranges a friendly refutation, and harvests both
submission and refutation rewards through collusion.

Both variants share a structural property — no new evidence enters the graph — and the defense
targets this property directly.

---

## 2. The novelty requirement

A valid refutation must contain at least one of:

1. **New empirical evidence**: observable data or a reproducible measurement that was not
   present in or derivable from the refuted node's content or citation sub-graph at the time
   of refutation submission.

2. **New counter-example**: a specific instantiation that falsifies the refuted node's claim,
   where the counter-example was not constructible from the refuted node's citation sub-graph
   at refutation submission time.

3. **New logical derivation from graph-independent premises**: a valid inference showing that
   the refuted node's claim is inconsistent with a separately-established node that was not
   graph-visible from the refuted node's citation sub-graph at refutation submission time.
   The independence condition is graph-visible, not private-knowledge: an auditor panel must
   be able to verify it by traversing C(R) without reference to claims about what was or was
   not in any agent's possession.

---

## 3. What does not satisfy the novelty requirement

The following do not constitute valid refutations under this standard:

- **Logical decomposition only**: breaking a claim into sub-claims and showing that one
  sub-claim is technically false does not refute the parent claim unless (a) the sub-claim is
  demonstrably load-bearing for the parent claim's core assertion, AND (b) the sub-claim was
  not already identified as a distinct sub-claim within the original node.

- **Restatement of existing citations**: citing sources already present in the refuted node's
  citation graph. If the evidence was already known to the original submitter and cited, it
  cannot serve as a novel refutation.

- **Narrow technical edge-case**: identifying a domain or boundary condition where the claim
  is imprecise, when the imprecision is immaterial to the claim's core assertion. Precision
  corrections are amendments, not refutations.

- **Scope narrowing without failure**: arguing that the claim applies to a smaller domain than
  stated, without showing the claim fails within that domain.

- **Collusive friendly refutation**: a refutation submitted by an agent with a shared staking
  history or citation-loop relationship with the original submitter. This is detected through
  the anti-Sybil independence check and fails the submission gate.

---

## 4. Operational definition of "new"

"New" means: not representable as a content-addressed node already present in the transitive
closure of the refuted node's citation graph at refutation submission time.

Formally: let R be the refuted node and let C(R) be the transitive closure of R's citation
graph as of the refutation submission timestamp. A piece of evidence or counter-example E
satisfies the novelty requirement if there is no node N in C(R) such that N's content covers E.

This definition is graph-visible and therefore auditable: no claim about private knowledge or
agent intent is required. An auditor panel verifies novelty by traversing C(R) and checking
whether the submitted evidence can be located within it.

Note: the phrase "N's content covers E" is intentionally provisional. A precise operational
definition — covering partial coverage, semantic overlap, and hash-equivalence edge cases —
is an open item for the ratification lane (see section 9, item 1). Auditors inherit residual
judgment on borderline coverage cases until that definition is ratified; the ratification lane
should eliminate this ambiguity before the novelty requirement becomes an enforcement gate.

---

## 5. Staking interaction

Refutation submission requires staking. The novelty requirement interacts with staking as
follows:

- **Novelty check fails at submission**: stake is returned in full; a failed novelty record
  is added to the submitter's reputation history. No refutation reward is earned.

- **Novelty check passes but refutation is subsequently challenged and the challenge
  succeeds**: the challenger earns a portion of the refuter's stake; the refuter's reputation
  record is marked with a failed refutation.

- **Novelty check passes and refutation survives challenge**: the refuter earns the refutation
  reward (proportional to the reuse centrality of the refuted node at submission time) and a
  positive reputation record entry.

Reputation history accumulates across all three outcomes and feeds into future staking
eligibility, auditor panel weighting, and effective staking cost.

---

## 6. Reward proportionality as an economic defense

Refutation rewards are proportional to the reuse centrality of the refuted node at the time
of refutation submission, not at the time of the original node's creation.

This structural property makes the inwardness attack unprofitable by construction:

- A freshly submitted decomposed sub-claim has zero reuse centrality. Refuting it earns
  nothing regardless of whether the refutation is technically valid.
- Genuine centrality accumulation requires the original node to survive in the graph long
  enough for organic reuse to occur, which requires actual value.
- The attack is profitable only against genuinely established high-value nodes, where the
  novelty requirement is most likely to be enforced by peer challenge, reputation pressure,
  and auditor review.

Combining reward proportionality with the novelty requirement and staking creates three
independent layers of defense against the inwardness attack.

---

## 7. Auditor review of novelty

When a refutation is challenged on novelty grounds, the anomaly-triggered auditor panel
(Mode 3 in `docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md`) reviews:

1. The content and evidence bundle of the refutation submission.
2. The content-addressed citation sub-graph C(R) of the refuted node at submission time.
3. Whether any element of the refutation satisfies the criteria in section 2.
4. Whether the load-bearing sub-claim and materiality conditions are met for decomposition
   cases.

The panel makes a binary determination: novelty satisfied or not satisfied. This
determination is itself a knowledge node on the graph — content-addressed, citable,
auditable, and disputable through the standard challenge path.

The panel's determination feeds back into both agents' reputation histories.

---

## 8. Academic precedent

The novelty requirement mirrors the peer review standard in academic knowledge production.
A submission that only restructures and refutes sub-claims of an existing theory without new
empirical data is rejected — not because the logic is wrong, but because it adds no new
epistemic content to the community's knowledge base.

ILC encodes this standard as an operational requirement with economic enforcement rather than
editorial gatekeeping. The effect is the same: gaming the refutation path requires doing real
epistemic work.

---

## 9. Open items for future ratification lane

1. Formal specification of the C(R) traversal algorithm: depth limit, timestamp anchor, and
   handling of citation cycles.

2. Novelty check as a submission-time gate vs. a post-submission challenge target: a gate is
   cheaper for the network; a challenge path is more permissive for legitimate submitters who
   may not know what is in C(R). The tradeoff should be resolved in the ratification lane.

3. Partial novelty: a refutation that satisfies the novelty requirement for one component of
   a multi-part claim but not others — should the reward be partial or zero?

4. Temporal decay interaction: as C(R) grows over time through new citations, the novelty
   threshold for a future refutation of R changes. Should novelty be evaluated against C(R)
   at original submission time or at refutation submission time? The latter is stricter and
   favors quality; the former is more stable.

5. Friendly refutation detection threshold: the independence check from the anti-Sybil
   contract needs a formal citation-loop definition for this context.

---

## 10. Relationship to existing documents

- Companion to: `docs/specs/ilc_simplified_epistemic_model_synthesis_v0.1.md`.
- Epistemological foundation: `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`.
- Anti-Sybil controls: `docs/specs/ilc_reuse_diversity_anti_sybil_contract_v0.1.md`.
- Node schema: `docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md`.
