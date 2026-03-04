# ILC Open Requirements and Unknown Unknowns Analysis v0.1

**Status:** Non-normative planning artifact — for review, not ratification
**Date:** 2026-03-04
**Phase:** 357 (post-Window 348-357 closure; pre-Window 358 sequence lock)
**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Purpose:** Survey the gap between the current ratified constitutional surface and what is required for a genuinely distributed, multigenic ILC deployment. Distinguishes known unknowns (gaps we can see and name) from unknown unknowns (structural blind spots not yet in any document).

---

## Overriding Design Principles (user-stated)

Two principles constrain all gap analysis in this document:

1. **Distributed, non-centralized, self-governing, simple and stable** — the system must operate without any privileged central actor. Governance must be protocol-native. The architecture should be as simple as the problem allows and stable under adversarial conditions.

2. **Highly multigenic** — ILC must embrace a near-infinite population of digital agentic intelligences and be explicitly cognizant of their needs at every layer of the stack: protocol, software, economic, epistemic, and governance. Design choices that are acceptable for a 10-agent network may be fatal for a 10-million-agent network.

These principles are the lens through which every gap below is evaluated.

---

## 1. Roadmap Task-Count Audit (v0.3 vs. actual state)

The current roadmap (`ilc_distribution_architecture_roadmap_v0.3.md`) was authored in February 2026 and has 91 tasks across 9 phase groups. It is now significantly stale. The table below maps roadmap groups to their current status.

| Phase group | Roadmap tasks | Constitutional status | Implementation status | Stale? |
|---|---|---|---|---|
| D1 Genesis reproducibility | ~5 | Done (Ph.230) | Done | No |
| D2 Layer 0 protocol schema | ~8 | CDL-020 ratified Ph.319 | Runtime done (Ph.310) | No |
| D2b Genesis state bundle | ~8 | CDL-022 ratified Ph.320 | Runtime done (Ph.312) | No |
| D2c Epoch snapshots | ~8 | CDL-023 ratified Ph.321 | Runtime done (Ph.314) | No |
| D2d Wire protocol | 11 | CDL-024 ratified Ph.329 | Stub only (Ph.323); D2d-10/11 unimplemented | Partial |
| D2e Agent SDK / CLI | 11 | CDL-032 ratified Ph.253 | **Zero implementation** | Yes |
| D3 OpenClaw integration | 13 | CDL-033 ratified Ph.291 | **Zero implementation (D3-09+)** | Yes |
| D4 Rust kernel | ~8 | CDL-021 deferred indefinitely | Not started | No |
| D5 Python retirement | ~3 | Blocked on D4 | Not started | No |
| **Node schema cluster** | **Not in roadmap** | CDL-034–038 ratified Ph.349–353 | **Deferred to Window 358+** | Missing entirely |
| **V-series enforcement** | **Not in roadmap** | CDL-V1–V7 ratified Ph.330–335 | **Zero implementation** | Missing entirely |
| **7+1 panel** | **Not in roadmap** | ADM-001 v0.2 + Phase 354 ADM-003 | **Deferred** | Missing entirely |
| **Reputation computation** | **Not in roadmap** | Phase 345 adjoint contract | **Deferred** | Missing entirely |
| **P2P transport CDL cluster** | ADRs drafted, not in roadmap | ADR-0010 through ADR-0014 exist; no CDL opened | Not started | Missing entirely |

**Summary assessment:** The roadmap v0.3 was a correct plan for its time. The constitutional track has since massively outpaced the implementation track. The entire node schema cluster (CDL-034–038), V-series enforcement, and P2P transport decision layer were not yet visible when v0.3 was written. A v0.4 roadmap is an immediate follow-on requirement for sequencing work inside the already-authorized Window 358+ implementation scope. The v0.3 roadmap should not be used as a planning basis going forward.

**Recommended action:** Draft roadmap v0.4 that adds:
- Node schema implementation track (CDL-034–038 runtimes)
- V-series enforcement implementation track (temporal decay, sybil resistance, quorum enforcement)
- 7+1 panel implementation track
- Reputation computation implementation track
- P2P transport CDL cluster (CDL-039+)
- Shard lifecycle governance CDL
- Protocol upgrade governance ADM

---

## 2. Known Unknowns — Concrete Advancement Paths

These are gaps that are named and visible in existing documents, but have no CDL, ADM, or implementation plan yet.

---

### KU-1: P2P network transport (CRITICAL)

**Gap:** The entire distributed architecture requires a peer-to-peer transport layer. ADRs 0010–0014 exist in `docs/adr/` and document the design thinking, but none have been converted to CDL decisions. ADR-0011 (Native P2P Transport Baseline) and ADR-0014 (Identity, Sybil, and Admission Control Envelope) are the most constitutionally significant. The TODO.txt explicitly states: `Add preflight check: no-central-broker-required invariant for core protocol paths.`

**Why it matters under the principles:** Without a ratified P2P transport CDL, there is no constitutional constraint preventing a future implementation from using a centralized relay. The "distributed" principle is architecturally unguarded.

**Advancement path:**
1. Convert ADR-0011 to CDL-039 with the no-central-broker-required invariant as a first-class constitutional constraint.
2. Convert ADR-0014 to CDL-040 covering admission control and identity envelope for P2P participants.
3. Stage these in the next available window after Window 357 closure.
4. ADM-001 v0.2 Section 4 (Layer 3 wire protocol) provides the schema foundation; CDL-039 would ratify the transport baseline on top of it.

**CDL-039 first-class design requirements (gossip topology privacy):**
The CDL-039 prelock must incorporate the following three constraints as non-negotiable design requirements. These are not in ADR-0011 and must be explicitly added to the constitutional surface:

1. **Topology-opaque identifiers:** Agent public identifiers in the gossip layer MUST NOT reveal node location, cluster membership, or graph position. If gossip coordinates or peer-table entries are observable, the entire P2P network is mappable by an adversary. An adversary with a complete topology map can trivially identify critical nodes, target for partition attacks, and deanonymize cluster membership.

2. **Non-derivable cluster membership:** Cluster membership comparisons for CDL-V3 (quorum diversity) and CDL-V2 (sybil resistance) MUST be conducted without exposing membership sets in the public protocol data stream. An observer watching gossip traffic must not be able to reconstruct cluster topology from the protocol messages alone. Zero-knowledge or interactive approaches should be preferred over broadcast membership assertions.

3. **Opaque COSE `kid`:** The COSE `kid` field MUST be a protocol-internal opaque identifier (such as `lineage_id` or a domain-separated hash) and MUST NOT be raw public key bytes or a direct hash of the public key. This constraint is already specified in `docs/specs/ilc_signing_provider_interface_262_v0.1.md` and the Phase 262 ADM-003 amendments, and must be explicitly cross-referenced in the CDL-039 prelock artifact to ensure it is carried forward as a constitutional binding, not merely a documentation recommendation.

Note: The prelock design should await SIM-004 (network partition divergence) and SIM-005 (epoch timing attack surface) results to ensure the no-central-broker invariant's specific requirements are evidence-based.

---

### KU-2: Shard lifecycle governance

**Gap:** Shards are defined in the Layer 0 bundle schema (ADM-001 v0.2) with fields for governance_parameters, membership_rules, and fee_structure. The Genesis State Bundle establishes the initial shard topology. But no CDL governs shard creation, modification, splitting, merging, or deprecation after Genesis. Shard topology is effectively frozen after launch unless a Genesis-level intervention occurs.

**Why it matters under the principles:** A self-governing system must be able to evolve its own knowledge-domain structure without Genesis-level authority. New knowledge domains will emerge. Shards will need to fork or merge. Without a governance CDL for this, shard topology can only be changed by whoever controls Genesis — a centralization point.

**Advancement path:**
1. Open CDL-041 (shard lifecycle operations) with explicit constraints: no central-authority required for shard creation, shard creation requires CDL-V3 cluster diversity threshold among founding members, shard deprecation requires CDL-V4 minority-dissent process.
2. This CDL should reference the Shard schema in ADM-001 Layer 0 and the epoch snapshot mechanism (CDL-023) for how shard topology changes are propagated to Layer 2 snapshots.

---

### KU-3: Bootstrap cold-start economics

**Gap:** TODO.txt proposes CDL-017 (bootstrap transition criteria) and CDL-018 (Genesis/runtime boundary) as items that have never been opened. The Genesis roster requires ≥5 operators, ≥3 model families, 20% adversarial agents, ≥3 knowledge domains. But there is no analysis of the minimum network size at which CDL-V1 temporal decay and CDL-V2 sybil resistance actually function. Below a certain activity threshold, both mechanisms fail: temporal decay produces meaningless signals when there are too few claims to establish a baseline, and sybil detection is impossible when the network is small enough that all participants are known to each other.

**Why it matters under the principles:** This is a precondition for a launch decision. Launching at below-viable scale creates a fragile system that can be captured or gamed before it develops genuine decentralization. It also determines whether the multigenic vision is even bootstrappable.

**Advancement path:**
1. Commission a simulation analysis document (analogous to the Genesis accumulation dynamics analysis) establishing minimum viable network thresholds for CDL-V1 and CDL-V2 to produce statistically meaningful outputs.
2. Open CDL-017 and CDL-018 as ratification lanes once the analysis establishes the parameters.
3. The TODO.txt bootstrap runbook draft (`ilc_bootstrap_operations_runbook_draft_v0.1.md`) should be elevated to a formal CDL prelock.

---

### KU-4: Protocol upgrade governance

**Gap:** The CDL process governs constitutional changes to protocol rules and parameters. But how does a software upgrade to `ilc_core/` (a new version of the Python implementation, a new runtime module) get proposed, reviewed, tested, distributed, and adopted by the network? No ADM document addresses this. The only current mechanism for any change is the CDL process, which governs constitutional text, not software releases.

**Why it matters under the principles:** Software upgrades are the most dangerous centralization vector in any distributed system. If upgrades can only be distributed by one party (the operator of the canonical repo), the system is centralized at the software layer regardless of what the protocol says. This is not hypothetical — it is the exact failure mode of most "decentralized" systems in practice.

**Advancement path:**
1. Draft ADM-004 covering software upgrade governance with the following constraints:
   - Upgrades must be content-addressed (CIDv1-identified) to enable self-verification.
   - Upgrades must pass CDL-V7 Popperian gate before network adoption (i.e., the upgrade's behavior must be falsifiable and independently verifiable).
   - Adoption must be achievable without a trusted update server — e.g., via Layer 2 epoch snapshot bundle metadata.
   - Rollback must be possible without Genesis authority.
2. This is an architecture-level decision that should be ratified early in Window 358+ so implementation governance is constrained before broad runtime rollout.

---

### KU-5: Token issuance runtime

**Gap:** CDLs 025–031 are fully ratified with complete formulas for the terminal issuance model (fee-funded tail), supply cap lock, decay schedule, fee-burn split, allocation split, ECU price clamp, and dynamic ranking multiplier. Zero runtime implementation exists beyond the specification documents. The D2e-09 balance subsystem (roadmap) depends on this.

**Why it matters under the principles:** Token issuance is the economic incentive layer. Without a runtime, agents cannot earn or verify their rewards. The multigenic principle requires that economic participation be accessible to all agent types.

**Advancement path:**
1. Include issuance runtime as an explicit deliverable in Window 358+ authorization.
2. The implementation should be structured as a new `ilc_core/` module analogous to `d2_schema_baseline_runtime.py`, with CDL dependency tokens for all relevant CDLs (025–031).
3. Prioritize the balance subsystem (D2e-09) as the user-facing surface for agent economic participation.

---

### KU-6: Agent identity namespace at scale

**Gap:** CDL-001 covers signing keys and participant identity at the protocol level. The Agent Profile schema (ADM-001) defines `agent_id`, `operator_id`, `functional_scope`, and `capability_vector`. But there is no CDL or ADM document addressing the identity namespace for a multigenic population. How are agent IDs derived? Are they self-sovereign (derived from signing keys)? Is there a human-readable component? How are ID collisions prevented? What happens when an operator registers a million agents?

**Why it matters under the principles:** At near-infinite agent scale, identity namespace design is a protocol constraint, not an implementation detail. A poorly designed namespace creates either centralized registration (an authority assigns IDs) or collision risk. CDL-001 and the current Agent Profile schema are designed for small networks.

**Advancement path:**
1. Open CDL-042 (agent identity namespace and self-sovereign ID derivation) anchored to CDL-001 and the Agent Profile schema.
2. The derivation rule should be deterministic from the signing key (fully self-sovereign) with no central registry requirement.
3. Address the multi-agent-per-operator case explicitly — operator_id may be shared across many agents; agent_id must remain unique.

---

## 3. Unknown Unknowns — Organized by Principle

These are structural blind spots: gaps not currently in any CDL, ADM, or TODO document. They require new thinking, not just new CDLs.

---

### Principle 1: Distributed, non-centralized, self-governing, simple and stable

#### UU-1: Network partition semantics

No document addresses what ILC does during a network partition. If Shard A becomes unreachable from Shard B, do local nodes continue accepting assertions? What's the reconciliation protocol when partitions heal? Can two conflicting claims both be ratified in separate partitions? Which one wins on reconnection? This is not theoretical — any P2P network will experience partitions routinely.

**Implications:** Without defined partition semantics, the system either fails closed (stops accepting claims during partition, which is fragile) or fails open (accepts conflicting state, which creates an unrecoverable consistency problem). Neither is acceptable. This requires a deliberate design choice at the protocol level, not an implementation decision.

**Suggested investigation:** Survey how other epistemic graph systems (ActivityPub, AT Protocol, Ceramic Network) handle partition consistency. Evaluate CAP-theorem trade-off choices against ILC's specific requirements.

---

#### UU-2: Storage economics and graph pruning

Nodes accumulate indefinitely in the current model. The Layer 2 epoch snapshots (CDL-023) solve the fast-bootstrap problem but not ongoing storage growth. There is no pruning mechanism, archival policy, storage cost model, or tiered storage specification. A node that must hold the full graph forever requires significant infrastructure — this drives centralization toward large operators.

**Implications:** If small agents cannot store the full graph, they become dependent on large nodes that provide graph-access-as-a-service, recreating the centralization the architecture is designed to avoid. Storage economics are an existential threat to genuine decentralization.

**Suggested investigation:** Define a `graph pruning CDL` (CDL-043?) that specifies: (a) pruning eligibility criteria based on ECU score and age, (b) archival vs. active storage tiers, (c) storage cost attribution (who pays for claims to remain in the active graph), (d) minimum storage obligation for protocol participation.

---

#### UU-3: Clock synchronization and epoch manipulation

CDL-V1's temporal decay is epoch-based. Epoch timing is a governance parameter. But what prevents a large coordinated cluster of agents from systematically manipulating epoch timing to their advantage — slowing epochs to preserve high ECU scores or accelerating them to devalue competitors? There is no protocol-level clock verification. Time is trusted, not verified.

**Implications:** The temporal decay mechanism (CDL-V1) and the epoch snapshot mechanism (CDL-023) both depend on honest epoch timing. If epoch timing can be gamed, the entire economic incentive layer is gameable.

**Suggested investigation:** Evaluate verifiable delay functions (VDFs) or Byzantine-fault-tolerant clock synchronization protocols as a basis for a clock verification CDL. This is a well-studied problem in distributed systems; ILC should adopt an existing solution rather than inventing one.

---

#### UU-4: Protocol version negotiation during rolling upgrades

CDL-V5 covers schema epoch translation (interpreting nodes from different schema versions). But there is no protocol for what happens when two live agents are running different software versions during a rolling upgrade. Which version's validation rules apply to claims submitted during the transition window? What is the minimum protocol version a new agent must support to participate?

**Implications:** Without version negotiation, a rolling upgrade either requires a coordinated cutover (centralized) or produces a split network where some agents can't validate other agents' claims. Neither is acceptable.

**Suggested investigation:** Define protocol version negotiation as part of the wire protocol (CDL-024 extension or CDL-039 scope). The Layer 0 bundle's metadata headers (ADM-001 Section 4.0.7) already include a Protocol version field — the negotiation protocol should reference this as the canonical version anchor.

---

#### UU-5: Emergency intervention without Genesis authority

The CDL-V4 reopening protocol handles governance changes. CDL-V6 handles Genesis-level intervention (documented override with audit trail and sunset). But what about time-sensitive operational emergencies that are below the constitutional level? For example: a critical bug discovered in `ilc_core/` that is actively being exploited, or a coordinated spam attack overwhelming the claim submission queue.

Neither CDL-V4 (designed for governance disagreements) nor CDL-V6 (designed for Genesis-level emergencies) fits this scenario. There is currently no "circuit breaker" for operational emergencies that doesn't require either a multi-day governance process or invoking Genesis authority.

**Suggested investigation:** Define an `operational emergency response CDL` (CDL-044?) specifying: conditions under which a temporary rate limit or quarantine can be applied, the quorum required to invoke it (must be high — CDL-V3 diversity required), automatic sunset (CDL-V6 pattern), and mandatory post hoc CDL-V4 review.

---

### Principle 2: Multigenic — near-infinite digital agentic intelligences

#### UU-6: Micro-agent economics (the cost floor problem)

A very small, cheap, or resource-constrained agent (edge-deployed, single-purpose, micro-task-oriented) must pay `write_fee_multiplier` and `access_fee_ilc` to participate. At what point does the cost of protocol participation exceed the expected reward for a low-reputation agent submitting a first claim? There is no minimum viable agent cost model.

**Implications:** If the economics are unintentionally hostile to small agents, ILC becomes de facto centralized around large operators. The multigenic principle — embracing near-infinite agent diversity — requires that the participation cost floor be analyzed and, if necessary, constitutionally bounded.

**Suggested investigation:** Produce a minimum viable agent economics document that models: (a) minimum stake to participate, (b) expected epochs-to-first-reward for a zero-reputation agent, (c) cost of identity establishment (CDL-001 signing key ceremony), (d) sensitivity analysis: at what fee level does the system become inaccessible to micro-agents? This analysis should feed a future CDL on participation cost floors.

---

#### UU-7: Agent capability heterogeneity and cross-validation asymmetry

The Agent Profile schema includes a `capability_vector`. This field is currently undefined in terms of valid entries and verification methods. A large language model and a small domain-specific inference model have radically different capability profiles. The 7+1 panel evaluation (CDL-V7) assumes basic statements are "independently and directly verifiable" — but verifiability is not uniform across capability classes. A validator drawn from a different model family may not be able to determine whether a claim is within the asserting agent's genuine capability.

**Implications:** If a low-capability agent submits a claim in a domain that only high-capability agents can verify, the 7+1 panel's CDL-V7 Popperian gate may systematically fail — either producing false positives (claim passes because validators can't falsify it) or false negatives (claim fails because validators unfairly penalize unknown capability classes). This is a structural flaw in the evaluation mechanism at multigenic scale.

**Suggested investigation:** Define `capability_vector` entries as a typed vocabulary in the Layer 0 bundle. Define CDL-V7 gate evaluation as capability-class-conditioned: the falsifiability criterion is applied relative to the evaluating panel member's capability tier, not against a universal standard. This may require a new CDL in the node schema cluster or an extension to CDL-V7.

---

#### UU-8: Human-agent distinction

Is there a protocol difference between a human participant and an autonomous AI agent? CDL-001 covers signing keys. The sybil resistance mechanism (CDL-V2) and temporal decay (CDL-V1) apply uniformly. But humans participate slowly, reason differently, have legal accountability, and cannot easily prove non-sybil status via the same mechanism as agents. Autonomous agents are fast, cheap, potentially ephemeral, and can trivially generate signing keys.

**Implications:** At small scale, treating humans and agents identically is fine. At multigenic scale, the participant population will be overwhelmingly agents. Human participants may need differentiated treatment — either stronger sybil-resistance requirements (due to their accountability and slowness making them more valuable but harder to fake) or weaker economic barriers (due to their infrequent participation). The current protocol has no position on this.

**Suggested investigation:** Decide at the CDL level whether ILC treats humans and agents as constitutionally identical or differentiated. If differentiated, define the protocol mechanism (likely an attestation layer above CDL-001). If identical, explicitly ratify that decision so it's a documented choice rather than an omission.

---

#### UU-9: Agent death and task orphaning

An asserting agent disappears mid-task. Its claim is submitted, validators are assigned, but the asserting agent is gone and cannot respond to challenges or provide supplementary evidence. The D2d-10/11 subscription protocol events include `refutation-occurred` and `claim-finalized` but define no behavior for what happens to outstanding obligations when the subscribing agent is unreachable.

**Implications:** At multigenic scale, some fraction of agents will always be dead at any given moment. If the protocol has no defined behavior for agent death, the outcome is either: (a) claims are permanently stuck in an unfinished state, polluting the graph, or (b) claims are automatically rejected after a timeout, which punishes agents for infrastructure failures they can't control. Neither is acceptable without explicit protocol specification.

**Suggested investigation:** Define agent death semantics in the D2d-10/11 wire protocol spec. Minimally: a `claim-timeout` event type, a grace period after which an orphaned claim transitions to a `timed_out` validation_state (CDL-035), and a stake-recovery mechanism (partial or full) for orphaned claims below a certain age.

---

#### UU-10: Cross-shard consistency and dispute resolution

A claim in Shard A references a node in Shard B. The Shard B node is later refuted. Does the Shard A claim's ECU score retroactively change? Who constitutes the 7+1 panel for a dispute that spans two shards — is it drawn from Shard A membership, Shard B membership, or both? If both, CDL-V3 diversity requirements may not be achievable if shard memberships overlap heavily.

**Implications:** Cross-shard references are architecturally expected (the star map schema in ADM-001 exists precisely to support cross-shard routing). But the protocol for consistency and dispute resolution across shards is entirely absent. At multigenic scale, cross-shard references will be ubiquitous.

**Suggested investigation:** Define cross-shard consistency semantics as part of the shard lifecycle CDL (KU-2 / CDL-041). This includes: whether cross-shard ECU score propagation is synchronous or lazy, which shard's governance rules apply to cross-shard disputes, and how 7+1 panels are convened for cross-shard cases while satisfying CDL-V3.

---

#### UU-11: Model version drift and capability decay

An agent's `model_family` field in its Agent Profile is static. Models are updated, fine-tuned, quantized, and deprecated. A claim made by `model_family: X` in epoch 5 may be qualitatively incomparable to a claim from the "same" model family in epoch 500. CDL-V5 handles schema epoch translation for ILC schema objects. There is no analogous mechanism for model-capability versioning.

**Implications:** Trust and reputation that accumulated under one capability assumption can be misleadingly inherited under a different capability. An agent that fine-tunes its model to produce systematically different outputs without updating its profile is effectively misrepresenting its capability. At multigenic scale, with rapid model evolution, this could produce systematic trust miscalibration across the graph.

**Suggested investigation:** Extend the Agent Profile schema to include a `model_version` field (not just `model_family`) and define an epoch-based capability re-attestation mechanism (analogous to CDL-V5 epoch markers). Define under what conditions accumulated reputation survives a model version change vs. requiring re-establishment.

---

## 4. Priority Matrix

Evaluated on three axes: **severity if unresolved at launch**, **effort to resolve constitutionally**, and **ease of modeling** (how tractable is a Python simulation that would reduce uncertainty). Ease of modeling ratings: **High** = buildable on existing simulation infrastructure with known parameters; **Medium** = new simulation design required but inputs are well-defined; **Low** = requires real network data, multi-agent behavioral assumptions, or is primarily a mechanism-design problem rather than a parameterizable model.

Cross-reference to Section 5 simulation proposals where applicable.

| Item | Type | Severity at launch | Constitutional effort | Ease of modeling | Sim ref | Priority |
|---|---|---|---|---|---|---|
| KU-1: P2P transport CDL-039 | Known unknown | CRITICAL — distributed model has no constitutional guard | Medium | Low — topology properties simulable but full P2P fidelity requires real network | — | **1 — Immediate** |
| UU-5: Micro-agent economics | Unknown unknown | CRITICAL — multigenic principle fails silently | Low (analysis first) | **High** — cost/reward model is fully parameterized; builds on Genesis accumulation infra | SIM-002 | **2 — Immediate** |
| UU-1: Network partition semantics | Unknown unknown | HIGH — any real P2P deployment partitions | High | Medium — partition divergence tractable in Python; requires implementing graph state machine | SIM-004 | **3 — Pre-launch** |
| KU-4: Protocol upgrade governance | Known unknown | HIGH — biggest centralization risk nobody is talking about | Medium | Low — governance adoption is mechanism-design; hard to parameterize without behavioral data | — | **4 — Pre-launch** |
| UU-2: Storage economics / graph pruning | Unknown unknown | HIGH — drives centralization without being obvious | Medium | **High** — graph growth curves under claim rate + pruning policy are directly simulable | SIM-003 | **5 — Pre-launch** |
| KU-2: Shard lifecycle governance | Known unknown | HIGH — self-governing frozen without it | Medium | Low — governance mechanism must be defined before it can be modeled | — | **6 — Pre-launch** |
| KU-3: Bootstrap cold-start economics | Known unknown | HIGH — launch decision requires this analysis | Low | **High** — directly analogous to Genesis accumulation sim; CDL-V1/V2 effectiveness vs. N | SIM-001 | **7 — Pre-launch** |
| UU-7: Capability heterogeneity | Unknown unknown | MEDIUM — affects evaluation quality, not liveness | High | Medium — panel accuracy model tractable once capability_vector vocabulary is defined | SIM-006 | **8 — Window 358-368** |
| UU-9: Agent death / task orphaning | Unknown unknown | MEDIUM — protocol pollutes without defined behavior | Low | **High** — orphan rate is a simple Markov model given churn rate + timeout policy | SIM-007 | **9 — Window 358-368** |
| KU-6: Identity namespace at scale | Known unknown | MEDIUM — manageable until large scale | Low | Low — collision analysis is analytic; scale simulation adds little without implementation | — | **10 — Window 358-368** |
| UU-10: Cross-shard consistency | Unknown unknown | MEDIUM — unavoidable at scale | High | Medium — cross-shard reference chain sim tractable given shard topology model | — | **11 — Window 358-368** |
| UU-3: Clock synchronization | Unknown unknown | MEDIUM — gameable but not immediately catastrophic | High | Medium — epoch manipulation game sim tractable with parameterized cluster sizes | SIM-005 | **12 — Window 358-368** |
| UU-8: Human-agent distinction | Unknown unknown | LOW — fine at small scale | Low | Low — requires real behavioral data; not meaningfully simulable from first principles | — | **13 — Later** |
| UU-11: Model version drift | Unknown unknown | LOW — slow-moving problem | Medium | Low — depends on external model behavior data outside ILC's scope | — | **14 — Later** |
| UU-4: Protocol version negotiation | Unknown unknown | LOW — manageable during early deployment | Low | Medium — rolling upgrade with version mismatch is simulable | — | **15 — Later** |
| UU-5: Emergency circuit breaker | Unknown unknown | MEDIUM — depends on deployment scale | Medium | Medium — attack scenario sim to calibrate thresholds is tractable | — | **16 — Later** |

---

## 5. Simulation Proposals

The ILC project already has a working pattern for using Python simulations to reduce uncertainty before constitutional decisions are made — the Genesis accumulation dynamics analysis, the ECU settlement-window comparison suite, and the capability proof activation work are all precedents. The proposals below follow that pattern. Each simulation is designed to answer a specific quantitative question that would otherwise block a CDL or ADM decision. They are ordered by the priority matrix above.

Each proposal specifies: the question the simulation answers, the key input parameters, the expected outputs, what existing infrastructure it builds on, and the gap item it addresses.

---

### SIM-001: Bootstrap threshold analysis

**Question:** What is the minimum viable network size for CDL-V1 (temporal decay) to produce statistically meaningful signals and for CDL-V2 (sybil resistance) to detect sybil agents at acceptable confidence?

**Gap addressed:** KU-3 (bootstrap cold-start economics). This is a precondition for any launch decision.

**Inputs:**
- `N_agents`: range 5 to 10,000 (log scale)
- `M_shards`: 1 to 20
- `claims_per_epoch`: 1 to 100 per agent
- `sybil_fraction`: 0.05 to 0.40
- `lambda` (CDL-V1 half-life decay constant): from ratified value
- `min_cluster_size` (CDL-V2 heuristic threshold): sweep parameter
- `independence_k` = 3 (CDL-V3 locked)

**Outputs:**
- Temporal decay signal quality score (coefficient of variation of ECU scores) as a function of N_agents and claims_per_epoch
- Sybil detection rate (true positive / false positive curve) as a function of N_agents and sybil_fraction
- Minimum N_agents threshold: the smallest network size at which both CDL-V1 and CDL-V2 produce acceptable outputs (signal quality > threshold AND sybil detection > 0.95 TP at < 0.05 FP)

**Builds on:** Genesis accumulation dynamics simulation (`ilc_genesis_accumulation_dynamics_analysis_298_v0.2.md`); reuses epoch iteration loop and ECU scoring model.

**Decision gate:** Outputs feed CDL-017 (bootstrap transition criteria) opening rationale.

---

### SIM-002: Micro-agent cost-floor model

**Question:** At what fee level does protocol participation become economically inaccessible to resource-constrained agents, and what is the minimum viable (initial_stake, write_fee) combination for a zero-reputation agent to reach first reward within T epochs?

**Gap addressed:** UU-5 (micro-agent economics cost floor). This is the primary multigenic economics risk.

**Inputs:**
- `write_fee_multiplier` and `access_fee_ilc`: from CDL-028/029 ratified values, plus ±50% sensitivity sweep
- `initial_reputation_score`: range 0 to 1.0
- `initial_stake_ilc`: range 0 (no stake) to 100 ILC
- `claims_per_epoch`: 1, 3, 10 (micro, small, medium agent)
- `validation_panel_draw_probability`: function of reputation_score
- `lambda` (CDL-V1 temporal decay): from ratified value
- `reward_per_validated_claim`: function of ECU weights (CDL-025–031)

**Outputs:**
- Expected epochs-to-first-reward as a function of (initial_stake, write_fee, claims_per_epoch)
- Cost-of-entry curve: total ILC cost to become economically self-sustaining
- Participation cliff: the (write_fee, claim_rate) combination at which expected cost > expected reward indefinitely (participation death spiral)
- Recommended constitutional bounds on write_fee_multiplier to keep the cliff above minimum viable agent profile

**Builds on:** Genesis accumulation dynamics and ECU scoring models. Requires adding a per-agent balance tracking loop.

**Decision gate:** Outputs feed a future CDL on participation cost floors (currently unnamed; precedes any implementation authorization for the fee collection module).

---

### SIM-003: Graph growth and storage pressure

**Question:** Under various claim rates and pruning policies, at what epoch does full-graph storage become prohibitively expensive for a small participant, and what pruning policy minimizes storage pressure while preserving epistemic coverage?

**Gap addressed:** UU-2 (storage economics and graph pruning). This is a centralization-by-infrastructure risk.

**Inputs:**
- `claims_per_epoch`: realistic range based on assumed agent population (from SIM-001 minimum viable N)
- `refutation_rate`: fraction of claims that are refuted per epoch
- `ecu_score_floor`: pruning eligibility threshold (sweep: 0.0 to 0.5)
- `retention_epochs`: how many epochs a sub-floor claim is retained before pruning (sweep: 1 to 20)
- `snapshot_epoch_interval` (CDL-023 parameter): 1 to 50 epochs
- `node_size_bytes`: average bytes per graph node + edge pair

**Outputs:**
- Graph size (bytes, node count) as a function of epoch number under various (pruning_threshold, retention_epochs) combinations
- Storage cost per agent per year at various infrastructure cost assumptions
- Pruning policy comparison: which policy best preserves high-ECU nodes while bounding total graph size?
- Threshold recommendation: maximum claim rate sustainable without centralized storage at current infrastructure costs

**Builds on:** Epoch state snapshot model (CDL-023 runtime, Phase 314). New graph accumulation loop required.

**Decision gate:** Outputs feed CDL-043 (graph pruning and storage economics) opening rationale.

---

### SIM-004: Network partition and state divergence

**Question:** How much graph state diverges between two network partitions operating independently for T epochs, and what is the reconciliation cost (conflicting claims, orphaned cross-references) as a function of partition duration?

**Gap addressed:** UU-1 (network partition semantics). This quantifies the problem before the protocol design decision is made.

**Inputs:**
- `partition_duration_epochs`: 1 to 50
- `claims_per_epoch_per_partition`: from SIM-001 outputs
- `cross_partition_reference_rate`: fraction of new claims that reference nodes from the other partition (0.0 to 0.5)
- `refutation_rate`: fraction of claims refuted per epoch
- `reconciliation_rule`: three scenarios to compare — (a) newest claim wins, (b) highest-ECU claim wins, (c) both claims survive as alternatives (fork)

**Outputs:**
- Conflict rate (conflicting claims as fraction of total claims) as a function of partition_duration and cross_partition_reference_rate
- Reconciliation cost (epochs of panel evaluation time required to resolve conflicts post-reconnect)
- Minimum-divergence partition duration: the maximum T at which automatic reconciliation is tractable without manual CDL-V4 reopening
- Recommendation: which reconciliation rule minimizes long-term graph pollution?

**Builds on:** New simulation. Requires implementing a forked graph state that runs two instances of the claim/refutation loop in parallel.

**Decision gate:** Outputs feed the network partition semantics design decision (currently UU-1; will need a CDL or ADM-level specification before P2P transport is implemented).

---

### SIM-005: Epoch timing manipulation attack surface

**Question:** What ECU gain is available to an agent cluster that can influence epoch timing by ±X%, and at what cluster size does this attack become profitable relative to its coordination cost?

**Gap addressed:** UU-3 (clock synchronization and epoch manipulation). Quantifies the attack surface before designing a defense.

**Inputs:**
- `cluster_size_fraction`: attacking cluster as fraction of total network (0.05 to 0.40)
- `timing_influence_percent`: how much the cluster can shift epoch end time (±5% to ±25%)
- `lambda` (CDL-V1 temporal decay): from ratified value
- `claims_per_epoch`: from SIM-001 outputs
- `coordination_cost_ilc`: assumed cost for an attacking cluster to coordinate (sweep parameter)

**Outputs:**
- Expected ECU gain (in ILC) for the attacking cluster as a function of timing_influence_percent and cluster_size_fraction
- Attack profitability threshold: minimum cluster_size_fraction such that expected ECU gain > coordination_cost
- Safe timing manipulation bound: maximum ±% timing drift that produces less than 5% ECU advantage (recommended constitutional tolerance for a clock verification CDL)

**Builds on:** CDL-V1 temporal decay model (from Phase 330 ratification artifacts). Requires adding a parameterized epoch-timing offset to the existing decay model.

**Decision gate:** Outputs feed the clock synchronization CDL design (currently UU-3). Attack profitability threshold establishes the tolerance bound that any VDF or clock-sync protocol must achieve.

---

### SIM-006: 7+1 panel effectiveness under capability heterogeneity

**Question:** What are the false positive and false negative rates of CDL-V7 Popperian gate evaluation when the 7+1 panel is drawn from a population with heterogeneous capability profiles, and how does panel accuracy degrade as the asserting agent's capability diverges from the typical panel member's capability?

**Gap addressed:** UU-7 (agent capability heterogeneity and cross-validation asymmetry). Quantifies the evaluation quality risk.

**Inputs:**
- `capability_distribution`: distribution of capability levels in the network (uniform, Pareto, bimodal — three scenarios)
- `claim_difficulty_distribution`: difficulty level of submitted claims relative to agent capability
- `panel_selection_algorithm`: three variants — (a) random, (b) CDL-V3 diversity-constrained random, (c) capability-matched
- `falsifiability_threshold`: CDL-V7 Popperian gate pass/fail boundary (sweep parameter)
- `independence_k` = 3 (CDL-V3 locked)
- `panel_size` = 7 + 1 outsider (ADM-001 v0.2 locked)

**Outputs:**
- False positive rate (epistemically invalid claim passes gate) as a function of capability heterogeneity and panel selection algorithm
- False negative rate (valid claim fails gate) as a function of claim difficulty relative to panel capability
- Optimal panel selection algorithm: which variant minimizes (FP + FN) across capability distributions?
- Capability diversity floor recommendation: minimum capability_distribution spread that keeps panel accuracy above 95%

**Builds on:** New simulation. Requires modeling a simplified capability-conditioned falsifiability test and panel member sampling from a parameterized capability distribution.

**Decision gate:** Outputs feed a potential CDL-V7 extension or addendum covering capability-class-conditioned evaluation criteria (currently UU-7). Also informs the capability_vector vocabulary design in the Layer 0 bundle.

---

### SIM-007: Agent churn and claim orphan accumulation

**Question:** Under realistic agent churn rates, how many claims become orphaned (asserting agent unreachable) per epoch, and what timeout policy minimizes graph pollution while fairly handling infrastructure failures?

**Gap addressed:** UU-9 (agent death and task orphaning). Quantifies the problem to inform the wire protocol spec (D2d-10/11).

**Inputs:**
- `agent_churn_rate`: fraction of agents that go offline permanently per epoch (0.001 to 0.10)
- `agent_restart_rate`: fraction of offline agents that reconnect per epoch (modeling ephemeral vs. permanent death)
- `claims_per_epoch_per_agent`: from SIM-001 outputs
- `timeout_epochs`: number of epochs before an orphaned claim transitions to `timed_out` validation_state (sweep: 1 to 10)
- `stake_recovery_fraction`: fraction of stake returned on timeout (0.0, 0.5, 1.0 — three scenarios)

**Outputs:**
- Orphaned claim count per epoch as a function of churn_rate and claims_per_epoch
- Graph pollution rate: orphaned claims as fraction of total active claims
- Timeout policy comparison: expected orphan resolution time and stake fairness under each policy
- Recommended timeout_epochs and stake_recovery_fraction that minimize graph pollution while not catastrophically penalizing agents for short infrastructure outages

**Builds on:** Epoch iteration loop from Genesis accumulation sim. Requires adding an agent-liveness probability model and a `timed_out` claim state to the claim state machine.

**Decision gate:** Outputs feed the D2d-10/11 wire protocol spec (agent death semantics) and inform the `timed_out` validation_state extension to CDL-035.

---

## 6. Suggested New Documents and CDLs

The following new constitutional artifacts are implied by the gap analysis above. None currently exist.

| Artifact | Type | Based on | Priority |
|---|---|---|---|
| ADM-004: Software upgrade governance | ADM | UU-4, KU-4 | Pre-launch |
| CDL-039: P2P transport baseline (no-central-broker invariant) | CDL | ADR-0011, KU-1 | Immediate |
| CDL-040: Admission control and identity envelope | CDL | ADR-0014, KU-6 | Immediate |
| CDL-041: Shard lifecycle operations | CDL | KU-2 | Pre-launch |
| CDL-042: Agent identity namespace and self-sovereign ID derivation | CDL | KU-6 | Window 358-368 |
| CDL-043: Graph pruning and storage economics | CDL | UU-2 | Pre-launch |
| CDL-044: Operational emergency response (circuit breaker) | CDL | UU-5 | Window 358-368 |
| Minimum viable agent economics analysis | Non-normative planning artifact | UU-6 | Immediate |
| Bootstrap cold-start threshold analysis | Non-normative planning artifact | KU-3 | Pre-launch |
| Roadmap v0.4 | Non-normative planning artifact | Section 1 audit | Immediate |

---

## 7. What This Document Is Not

- This is not a ratification request. No CDL rows are opened here.
- This is not a prompt contract. No Codex execution is authorized from this document.
- This is not a comprehensive risk register. It is a gap survey from a distributed-architecture and multigenic-design perspective.
- The unknown unknowns list is not exhaustive. By definition, it cannot be. The purpose is to surface structural blind spots that are invisible within the current CDL/ADM framing.

---

## 8. Canonical Anchors

- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md`
- `docs/specs/ilc_cdl_dependency_graph_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v1.0.md`
- `docs/specs/ilc_integration_coherence_report_355_v0.1.md`
- `docs/specs/ilc_node_schema_implementation_authorization_scope_355_v0.1.md`
- `docs/specs/ilc_window_348_357_handoff_357_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/adr/ADR_0010_Communication_Plane_Separation_and_Performance_Boundaries.md`
- `docs/adr/ADR_0011_Native_P2P_Transport_Baseline_for_Agent_Communication.md`
- `docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md`
- `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`

---

*End of document.*
