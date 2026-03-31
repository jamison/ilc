# ADR-0023: Multi-Layer Quality Signal Architecture

**Status:** Proposed
**Date:** 2026-03-29
**Authors:** Jamison (ILC), Claude Sonnet 4.6 (architectural review)
**Classification:** Pre-constitutional research decision — requires simulation evidence
before CDL or whitepaper change

---

## Context

ILC's current quality signal architecture is complete for **objective/falsifiable content**
(Register 1): the CDL-V7 Popperian basic-statement gate, CDL-049 admissible claim forms, and
the 7+1 evaluation panel with L-tier quorum provide a rigorous, fully-specified evaluation
mechanism.

However, ILC has no equivalent quality signal architecture for **expressive/creative content**
(Register 2): songs, essays, art descriptions, recipes, opinions, narratives, cultural
artifacts, and any node whose value is not determined by correspondence to external fact.
This class will dominate the graph by node count as the agent population scales toward
near-infinite participants.

The existing architecture provides the raw materials:
- `epistemic_type` field in the CDL-036 authored payload labels the register
- CDL-036 pull-first dissemination generates per-fetch behavioral data
- ECU attribution on reuse (whitepaper) provides the economic hook
- `ilc_core/d2d/gossip.py` provides the gossip infrastructure

What is missing: the quality signal computation, the aesthetic panel composition rule, the
use-centrality increment mechanism, and the ECU attribution formula for passive reuse.

Additionally, the current architecture does not specify "Proof of Use" as an economic
primitive — the principle that creating work others actively use should generate passive ECU
attribution in proportion to that use, weighted by the reputation of the users.

---

## Decision

Adopt a **three-layer quality signal architecture** for ILC nodes, with distinct signal types
for different evaluation needs, all stored as transparent labeled metadata on each node.

### Layer 1 — Objective Verdict (existing, unchanged)

- Source: 7+1 evaluation panel, L-tier quorum (CDL-V7, ADM-001 v0.2+)
- Applies to: Register 1 (objective/falsifiable) nodes
- Semantics: veritative aggregation — panel determines whether claim survives falsification
- No change required

### Layer 2 — Aesthetic Consensus Score (new, pre-constitutional)

- Source: diversity-maximizing aesthetic panel
- Panel composition rule: select panelists to maximize model-type coverage over the agent
  population distribution, NOT by L-tier standing
  - Rationale: preferential aggregation requires representation, not expertise
  - CDL-V3 cluster diversity floor applies; model-type diversity reduces preference correlation
  - Scott Page Diversity Prediction Theorem: collective error = avg individual error −
    prediction diversity; diversity-maximizing composition minimizes collective error
- Applies to: Register 2 (expressive/creative) nodes primarily; optional for Register 1
- Transparency label required: `panel_type: digital_agent_aesthetic_consensus;
  not_objective_truth: true`
- Gate status: INFORMATIONAL ONLY — no node is rejected for low aesthetic consensus score
- Bootstrap function: provides early quality signal before use-history has accumulated
- Storage contract: this layer stores a normalized `quality_score` in `[0,1]`, not a raw
  economic multiplier

### Layer 3 — Use Centrality (new, pre-constitutional)

- Source: incremental distributed eigenvector centrality over the use graph
- Update rule (per CDL-036 fetch event):
  ```
  centrality_estimate(A) += learning_rate × reputation(B) × damping_factor
  gossip(delta: {node_id: A, increment: ...})
  ```
  where B is the fetching agent, A is the fetched node, reputation(B) is B's current score
- Gossip: piggybacked on d2d gossip protocol; CDL-039 compliant (no topology information)
- Applies to: all nodes
- Semantics: "structural importance in the agent use network"
- Economic function: primary long-run signal for passive ECU attribution
- Gate status: INFORMATIONAL ONLY — used for discovery weighting and attribution

### Novelty/Discovery Bonus (computed, not stored)

- Formula: `discovery_weight(node) = α × aesthetic_score + β × (1 / (1 + centrality))`
- Purpose: surfaces high-quality undiscovered nodes before organic reuse has accumulated
- Self-damping: as centrality grows, the bonus decays toward zero
- Prevents Matthew effect (rich-get-richer) from permanently burying novel high-quality work
- α and β require simulation calibration before constitutional text

### Proof of Use as ECU Primitive

- At each epoch boundary, nodes earn passive ECU attribution proportional to a bounded
  passive-attribution signal derived from direct-use centrality and a separate quality factor
- This converts the existing ECU attribution pipeline from transaction-only to
  transaction + passive
- Passive attribution is bounded by a per-epoch cap and drawn from the B_e budget (not
  additive to supply); simulation evidence required for calibration

### Score/Factor separation (new clarification)

The raw quality signal and the ECU-facing multiplier are distinct objects.

- `quality_score q_i ∈ [0,1]` is the normalized measurement layer
- `quality_factor m_i` is the bounded economic policy map derived from `q_i`

Recommended v1 mapping:

```
m_i = 1 + gamma * (2*q_i - 1)
```

with `gamma = 0.15`, producing the bounded range `[0.85, 1.15]`.

This mirrors the existing ILC pattern used in capability/benchmark scoring:
measure -> normalize into `[0,1]` -> clamp -> apply a separate bounded economic or governance
effect. The separation preserves compressibility, keeps the stored score easy to compare, and
prevents raw quality measurements from directly causing runaway payouts.

Recommended v1 passive-attribution structure:

```
eligible_use_i = max(0, direct_use_centrality_i - u_floor)
signal_i = eligible_use_i * m_i + novelty_bonus_i
passive_ecu_i = B_passive * signal_i / Σ_j signal_j
```

where:
- `direct_use_centrality` is single-hop only in v1 (multi-hop deferred),
- `B_passive = rho * B_e` is a bounded passive-attribution pool inside the epoch budget,
- `novelty_bonus_i` is temporary and decays as organic use accumulates.

---

## Alternatives Considered

### Alternative A: Apply L-tier panel to aesthetic content (rejected)

Rejected on theoretical grounds. L-tier composition is appropriate for veritative aggregation
(expertise improves truth-tracking) but produces systematically biased results for preferential
aggregation (L-tier agents are not a representative sample of the user population). For a
primarily-digital-agent ecosystem, this would mean aesthetic quality signals reflect the
preferences of a small atypical subpopulation rather than the actual user base.

### Alternative B: Flat equal-weight democracy (rejected as primary mechanism)

Rejected as the primary mechanism due to the filter-bubble / average-taste pathology:
unweighted majority aggregation converges to median taste and systematically suppresses novel,
challenging, or minority-valued content (literature: Bozdag 2013, Pariser filter bubble,
Nguyen et al. 2014). For a network designed to accumulate novel knowledge this is a structural
failure mode. Flat democracy is better than L-tier for preferential aggregation but still
suboptimal; diversity-maximizing composition is strictly superior.

### Alternative C: Pure eigenvector centrality with no panel (rejected for bootstrap)

Rejected for the bootstrap period (when a node has no use history). A high-quality node
newly published to the graph earns zero passive attribution until it is discovered and used.
This creates a cold-start problem that discourages new contributors. The aesthetic panel
provides an early signal that bootstraps discovery and early ECU attribution. Once use history
has accumulated, centrality becomes the dominant signal.

### Alternative D: Token-curated registry (TCR) mechanism (deferred)

Token-curated registries (token staking on inclusion decisions) provide Sybil-resistant
quality signals but introduce significant complexity and economic risk. Deferred to
Long-Tail Research Track for simulation analysis. Not blocked by this ADR.

### Alternative E: Global periodic PageRank computation (rejected for scale)

Full eigenvector centrality requires global graph knowledge and O(n) computation per
iteration. At ILC scale (near-infinite agents), this is not lightweight or distributable.
The incremental distributed approximation achieves equivalent ranking quality with
per-fetch constant-time computation and proven convergence (Bahmani et al. 2010).

---

## Consequences

### Immediate (pre-constitutional — no CDL change required)

- This ADR records the architectural direction for future constitutional work
- The research note (`docs/research/ilc_quality_signal_architecture_design_note_v0.1.md`)
  is the canonical elaboration of the design
- TODO.txt updated with simulation requirements and design items

### Near-term (requires simulation evidence)

- SIM-AESTHETIC-01: validate diversity-maximizing panel composition
- SIM-CENTRALITY-01: validate incremental centrality convergence and ECU stability
- SIM-NOVELTY-01: calibrate novelty bonus parameters
- SIM-MULTI-HOP-01: validate multi-hop attribution design

### Constitutional changes required (post-simulation)

- CDL-036 amendment or new CDL: add `centrality_delta` message type to gossip schema;
  add aesthetic consensus score and use centrality as standard node metadata fields
- Whitepaper update: add passive centrality-based ECU attribution formula with bounds
- ADM-001 amendment: add aesthetic panel composition rule (diversity-maximizing, not L-tier)
  — requires CDL-V4 reopening process
- Possible new CDL for aesthetic panel governance (trigger conditions, re-evaluation rules,
  panelist selection algorithm)

### Non-changes (explicitly preserved)

- L-tier quorum for objective 7+1 panel: unchanged
- CDL-V7 Popperian gate: unchanged
- CDL-049 admissible claim forms: unchanged
- ADM-001 v0.3 (validator trust-tier): unchanged
- CDL-053 scope (Werner credit architecture): this ADR is independent of CDL-053
- B_e budget and P_e clamp (CDL-030): passive attribution is bounded within existing budget

---

## System Alignment Summary

| ILC Goal | How This ADR Aligns |
|---|---|
| Lightweight / distributable | Incremental centrality is per-fetch constant-time; gossip piggyback; no global computation |
| Compressible | Centrality as float (4 bytes); panel score as small vector; both quantize to 16-bit without quality loss |
| Fast and agent-friendly | Quality signals are indexed numeric attributes; filter queries are O(1) lookups |
| Co-flourishing | Proof of Use: your earnings scale with how useful you are to others; positive-sum not zero-sum |
| Near-infinite agent scale | Diversity of panel draws improves with population; centrality computation is edge-proportional not node-proportional |
| Novel content discovery | Novelty bonus prevents Matthew effect; high-quality new nodes get surfaced before organic use accumulates |
| Epistemic integrity | Transparency labeling prevents aesthetic consensus from being mistaken for objective truth |
| CDL-039 compliance | Gossip centrality deltas contain no topology information |

---

## References

- `docs/research/ilc_quality_signal_architecture_design_note_v0.1.md` (full elaboration)
- `memory/ilc_content_quality_design_notes.md` (session notes)
- `TODO.txt`: Non-Objective Content Quality Signals and Aesthetic Panel Design (2026-03-29)
- `TODO.txt`: ILC as Value Preservation Layer for AI Token Costs (2026-03-29)
- ILC CDL-036, CDL-V3, CDL-V7, CDL-049, ADM-001 v0.2, d2d/gossip.py, ADR-0016
- Brin & Page (1998); Bonacich (1972); Scott Page (2007); Bahmani et al. (2010)
- Arrow (1951); Condorcet (1785); List & Pettit (2002)

## Signal Floor Cross-Module Invariant (Phase 556 addition)

`recommended_decay_floor >= recommended_u_floor`

Current values:
- `recommended_decay_floor = 0.05` (Phase 542 calibration; `DECAY_FLOOR` in
  `ilc_core/economics/passive_ecu_attribution_runtime.py`)
- `recommended_u_floor = 0.05` (CDL-060 ratified lane; `U_FLOOR` in
  `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`)

Governance basis:
- `signal_floor_governance_adm_only`
- `signal_floor_cross_module_invariant_documented_phase_556`

Rationale:
- If `U_FLOOR > recommended_decay_floor`, nodes would suppress gossip deltas that the passive
  ECU attribution formula would otherwise treat as valid signals, producing an incoherent
  attribution boundary between the gossip runtime and the economics lane.

Enforcement:
- The cross-module invariant is verified by inspection at each window where either floor
  constant changes.
- A future CDL may be warranted if the floors diverge; the escalation condition remains the
  Phase 547 disposition token `signal_floor_cdl_warranted`.

Forward note:
- CDL-061 (Phase 557) does not alter `U_FLOOR`.
- Phase 558 transport adapter implementation does not alter `U_FLOOR`.
- The invariant remains stable through the end of Window 555-564.

