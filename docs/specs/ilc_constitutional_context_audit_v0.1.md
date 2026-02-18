# ILC Constitutional Context Audit v0.1

Status: Active review artifact
Date: 2026-02-18
Reviewer: Claude Opus 4.6 (Strategic Architectural Reviewer, claude.ai)
Context basis: Full historical corpus (Z_Past_Chats, 47 files), research dredge outputs (19 artifacts), ratified constitutional artifacts, codebase through Phase 224, and reviewer context pack v0.1.

## 1. Purpose and Methodology

This audit examines whether ratified constitutional decisions and implemented parameters were made with complete project context, or whether finite context windows during execution may have caused design intent to be excluded, conflicts to be overlooked, or parameters to diverge from their simulation-derived provenance.

**Methodology:** For each CDL item and each key implementation parameter, this audit cross-references:
1. The ratification evidence (what was cited when the decision was locked).
2. The historical corpus (what design reasoning existed at the time of ratification).
3. The simulation record (what parameter values were empirically validated).
4. The current implementation (what values are actually in the codebase).

**Severity scale:**
- **MATERIAL** — Context gap that could have changed the ratification outcome or parameter choice. Recommend formal reopening through decision-log workflow.
- **SUBSTANTIVE** — Context gap that doesn't change the decision but leaves the evidence incomplete. Recommend evidence supplement without reopening.
- **COSMETIC** — Minor provenance gap. Note for documentation only.

---

## 2. Ratified CDL Items (CDL-003 through CDL-006, CDL-008 through CDL-015)

### CDL-003: No Perpetual Founder Privilege
**Ratification status:** Ratified (Phase 993 governance conflict set ratification)
**Historical corpus evidence:**
- `raw-012555`: "After Genesis bootstraps, no privileged humans should be needed. Parameter changes must be objective, verifiable, forkable, and contestable." (Oct 2025 main thread, line 15626)
- `raw-011870`: Explicit discussion of Genesis agent accrual — "you don't need a permanent fee stream to the Genesis agent." Decision to use rules-bound protocol treasury rather than discretionary Genesis accrual.
- `raw-012961`: "Share caps per shard (e.g., Genesis audits ≤5% of assignments; never audits its own claims)."
- Genesis siphon design: 8% of ECU, decaying schedule (p_g = 0.35 → 0.20 → 0.10 → 0.00), explicit sunset.

**Assessment: SUBSTANTIVE gap.**
The ratification confirms the no-perpetual-privilege principle, but the evidence bundle does not reference the specific decay schedule or the treasury/ERR design that was deliberated in the October 2025 conversations. The Genesis accrual governor (Phase 218) implements theta_hard = 1/20 (5% cap) and theta_soft = exp(-3) (~4.98%), but these constants were chosen during Phase 218 implementation, not derived from the simulation's 8% siphon with p_g = 0.35 decay schedule. The relationship between the simulation's "8% of ECU on referenced tasks" and the governor's "5% of total issuance" needs explicit reconciliation. These are measuring different things (share of task-level ECU vs share of total issuance), and the evidence bundle should document why both are correct and compatible.

**Recommendation:** Supplement the ratification evidence with a parameter provenance note linking the Phase 218 constants to the October 2025 simulation rationale. No reopening needed — the principle is correctly ratified. The parameter relationship needs documentation.

---

### CDL-004: Governance Changes Must Be Procedural, Not Unilateral
**Ratification status:** Ratified (Phase 993)
**Historical corpus evidence:**
- `raw-012616`: "Court (7+1 auditors): a VRF-selected 8-member panel (k-by-sponsor_cluster met, outsider seat) must certify each Executive proposal." (Oct 2025, line 16109)
- `raw-012647`: "Court certification: proposals that aren't objective & bounded never reach activation — even if popular."
- `raw-012646`: "Independent majorities: House must pass by seat majority and by cluster majority (≥⅔ of sponsor_clusters voting yes)."
- Ten self-leveling mechanisms documented, including PID-style controllers on KPIs and adaptive quorum per shard.

**Assessment: SUBSTANTIVE gap.**
The ratification correctly locks the procedural governance principle. However, the historical corpus contains extensive governance architecture (the court/house/executive model with VRF outsider seats, cluster-majority requirements, and no-show slashing) that is not referenced in the evidence bundle and is not implemented. This isn't a ratification error — CDP-004 was intentionally kept at the principle level with exact mechanisms deferred. But the evidence bundle should acknowledge that the corpus contains specific governance mechanism designs that inform how this principle should eventually be implemented.

**Recommendation:** Add a forward pointer in the evidence bundle to the governance mechanism designs in the corpus (raw-012616, raw-012646, raw-012647) so future implementers know the design reasoning exists. No reopening needed.

---

### CDL-005: Canonical Policy Supports Contestability
**Ratification status:** Ratified (Phase 993)
**Historical corpus evidence:**
- `raw-016900`: "Canon is never final without the option of economically-incentivized contradiction."
- `raw-008957`: "Evidence Submission: All challenges must include cryptographically verifiable evidence (data hashes, signed attestations)."
- Simulation evidence: P(refute|incorrect) = 0.60, refutation-profitability invariant, challenge-reveal systems where contradiction triggers require agents to prove derivation or face stake slashing.

**Assessment: COSMETIC gap.**
Ratification is sound. The contestability principle is correctly locked and the refutation-profitability invariant (Phase 212) provides structural enforcement. The only gap is that the simulation's specific refutation probability parameters (P(refute|incorrect) = 0.60, P(false refute|correct) = 0.05) are not referenced in the evidence bundle, though they informed the design intent.

**Recommendation:** Note only. Simulation parameters are calibration values, not constitutional constants.

---

### CDL-006: Local Canon Must Match Committed History
**Ratification status:** Ratified (Phase 993)
**Historical corpus evidence:**
- `raw-016905`: "Your local canon must match your committed history." (Jan 2026, line 2096)
- `raw-019139`: "A rollback must emit a superseding commit.epoch with finalization_state=rolled_back and must specify whether rewards are clawed back."
- Existing implementation in canon_bundle_key_registry_channel.py with rollback protections.

**Assessment: No gap.** This is the strongest-evidenced ratification. Implementation aligns with historical intent. Rollback resistance protections exist in code and are tested.

---

### CDL-008: Operational Participation Caps and Separation
**Ratification status:** Ratified (Phase 993)
**Historical corpus evidence:**
- `raw-012961`: "Share caps per shard (e.g., Genesis audits ≤5% of assignments; never audits its own claims)."
- Simulation evidence: SoV cap = max 15% of a shard's broadcast budget per agent per epoch. Cluster damping: max 1 reuse + 1 audit per trust-cluster per epoch.
- `raw-012610`: "Independence: results must satisfy k-by-sponsor_cluster; per-cluster cap (e.g., ≤25% of weight/seats)."

**Assessment: SUBSTANTIVE gap.**
The ratification confirms the separation principle, but the corpus contains specific numerical caps (5% audit assignment cap, 15% SoV cap, 25% per-cluster weight cap, 1 reuse + 1 audit per cluster per epoch) that were simulation-validated and are not referenced in the evidence bundle. These caps are not implemented in the Genesis codebase. The reuse_diversity_invariants.py module addresses single-agent concentration but not cluster-level caps.

**Recommendation:** Supplement the evidence bundle with the simulation-derived cap values as "historical design targets." Track cluster-level caps as a post-Genesis hardening item. The principle is correctly ratified; the specific numbers need to be preserved so they're not lost when the feature is eventually implemented.

---

### CDL-009 through CDL-010
**Assessment: No material gaps.** CDL-009 (canonicality distinct from copyability) and CDL-010 (composability above fixed base layer) are correctly ratified at the principle level with implementation deferred. The corpus confirms the design intent without contradiction.

---

### CDL-011: Balanced Composite EW Formula
**Ratification status:** Ratified (Phase 215)
**Historical corpus evidence:**
- Simulation-derived ECU weights: final recommendation BAL 50/35/15 (Reuse/Contra-resistance/Refinement) from 120-epoch simulation.
- Alternative profiles validated: ROBUST 45/40/15, REFINE 55/20/25, ADAPT (dynamic).
- Current implementation: node_value_kernel.py uses a weighted multi-component formula, but the specific weights are implementation-internal, not exposed as constitutional constants.

**Assessment: MATERIAL gap.**
The ratification confirms the "balanced composite" approach but does not reference the simulation-derived weight recommendations. The 120-epoch simulation concluded that BAL 50/35/15 was the optimal integrity-first default (lowest error rate at 0.39%), with ROBUST 45/40/15 recommended for crisis/regulated contexts. The current kernel implementation uses component weights, but these may not align with the simulation recommendations because the ratification evidence doesn't require specific weight values or reference the simulation data.

This is material because the ECU weights directly determine agent incentive structure. If the implemented weights diverge significantly from the simulation-validated values (which were chosen to minimize incorrect-finalization rates while maintaining merit-reward correlation), the system's anti-gaming properties may differ from what was empirically validated.

**Recommendation:** Formally verify that the kernel's component weights align with the simulation-derived BAL 50/35/15 profile (or document why different values were chosen). If the weights are aligned, supplement the ratification evidence. If they diverge, this needs a decision-log entry to reconcile. Also: the simulation produced four validated profiles (BAL, ROBUST, REFINE, ADAPT) — these should be documented as available governance presets for post-Genesis shard configuration.

---

### CDL-012: Usage + Freshness UF Linkage
**Ratification status:** Ratified (Phase 215)
**Historical corpus evidence:**
- HFM-001: `V(t) = U * exp(-lambda * t)` — node value decays over time unless sustained by utility/reuse. (June 2025)
- HFM-005: Anti-spam via stake + decay + downstream utility. (June 2025)
- CFR-002 CONFLICT: "Strong node-level decay vs reuse-persistence framing" — competing historical proposals between explicit exponential decay for node value vs. reuse-led persistence with optional delayed decomposition.
- Implementation: freshness_gate.py uses decay_lambda = 0.25 with freshness_floor = 0.85.

**Assessment: MATERIAL gap.**
The ratification confirms freshness linkage but does not reference or resolve CFR-002 (the conflict between strong decay and reuse-persistence). The formula catalog explicitly identifies this as an unresolved conflict with two competing historical proposals:
1. Explicit exponential decay: `V(t) = U * exp(-lambda * t)` (June 2025, Higher Dimensional Geometry)
2. Reuse-led persistence: reputation driven by reuse, with optional delayed decomposition (June 2025, 4D Cognitive AI Model)

The current implementation (freshness_gate.py) chose option 1 (exponential decay). This may be the correct choice, but the ratification evidence doesn't acknowledge that an alternative existed or explain why exponential decay was chosen over reuse-persistence. The decision was made implicitly during Phase 217 implementation rather than explicitly through the decision-log workflow.

Additionally, the specific parameters (decay_lambda = 0.25, freshness_floor = 0.85) have no simulation provenance. The October 2025 simulations tested ECU weights and quorum parameters but not freshness decay rates. These values were chosen during Phase 217 implementation without empirical validation against the broader simulation framework.

**Recommendation:** Open a decision-log entry to formally resolve CFR-002 and document why exponential decay was chosen over reuse-persistence. Supplement the ratification evidence with this resolution. Consider running the freshness parameters through the existing simulation framework to validate that decay_lambda = 0.25 produces the intended behavior at scale (120+ epochs).

---

### CDL-013: Decay Non-Genesis Only
**Ratification status:** Ratified (Phase 215)
**Assessment: No material gap.** The Genesis exemption is well-supported by both the corpus (Genesis nodes are canonical and permanent) and the implementation (freshness_gate.py exempts is_genesis = True). Evidence is strong.

---

### CDL-014: Counterfactual Path-Lift
**Ratification status:** Ratified (Phase 215)
**Historical corpus evidence:**
- HFM-002: `R(n) = S * U(n) / (1 + beta * D(n))` — reward unlock with depth/difficulty ramp, downstream utility unlocks rewards from genesis stake pools with diminishing returns over depth/time.
- Simulation evidence: ECU weights with Reuse component measuring "how much the claim gets used downstream (unique reuses/consumers, sharded & time-normalized)."
- Implementation: path_lift_counterfactual.py uses Shapley-adjacent batch accumulation method.

**Assessment: SUBSTANTIVE gap.**
The ratification is valid — the harness exists, is deterministic, and preserves provenance. However, the corpus contains a specific reward formula (HFM-002) that links rewards to depth/difficulty with diminishing returns, which is philosophically related to but mechanically different from the path-lift counterfactual method. The ratification evidence doesn't discuss the relationship between HFM-002's depth-ramp model and the implemented baseline_efficiency = path_weight / path_cost method.

**Recommendation:** Add a note to the contract spec explaining how the implemented counterfactual method relates to the historical HFM-002 formula. The methods are compatible (both reward downstream utility with diminishing returns), but the lineage should be documented. No reopening needed.

---

### CDL-015: Strict Phase Gate
**Ratification status:** Ratified (Phase 215)
**Assessment: No material gap.** Process evidence (sequence locks, CI gates) correctly satisfies the decision's intent about implementation ordering discipline.

---

## 3. Open CDL Items (CDL-001, CDL-002, CDL-007)

### CDL-001: Canonical Signer Lineage Definition
**Status:** Open
**Historical corpus evidence:**
- Extensive June 2025 discussion of multi-signature strategies for Genesis agent protection (2025_06_26 design conversation, lines 8130-8182).
- Quantum resistance concerns: post-quantum cryptography (lattice-based, hash-based schemes) discussed as protection for high-weight nodes (lines 1427-1477).
- `raw-019106`: "The capsule can be minimal but must be valid and test-signed (non-canonical) for now."
- `raw-013436`: "Every claim, task result, stake movement: must be signed by a single agent ID."
- `raw-016770`: "Define which protocol messages must be signed."
- Breakthrough shortlist rank #1: "Signature-rooted canonical authority and lineage legitimacy" — classified MVP-now.
- MVP criticality: CDP-001 scored high/high/high/high on migration cost, security exposure, interoperability lock-in, governance debt.

**Assessment: MATERIAL scope gap.**
CDL-001 is correctly open, but its current scope may be too narrow. The historical corpus reveals that signer lineage is not just about "which key signed what" — it encompasses:
1. Multi-signature and key regeneration strategies for Genesis agents (quantum resistance).
2. Agent identity lifecycle (creation, rotation, revocation, recovery).
3. The relationship between signer identity and canonical authority (who can declare canonical status).
4. Key hierarchy for different trust levels (Genesis keys vs agent keys vs operational keys).

The current CDL-001 entry likely describes signer lineage as a technical implementation item. The corpus evidence suggests it's actually the trust root for the entire protocol — without it, canonical authority, reward legitimacy, and rollback resistance all lack a foundation.

**Recommendation:** Before closing CDL-001, verify its scope includes all four dimensions above. If it's currently scoped as "implement key signing for canonical bundles," it should be expanded to "define the complete signer lineage model including key hierarchy, lifecycle, rotation, and relationship to canonical authority." This is the highest-leverage open item in the decision log.

---

### CDL-002: Emergency Key Compromise Response
**Status:** Open
**Historical corpus evidence:**
- June 2025 design conversation: "the theft of keys or that agent being compromised would be very damaging. For instance, if it somehow got out what my or your identity is and we were kidnapped... I don't want to be placed in a position where I'm removed from the system." (line ~8139)
- Discussion of immutable timestamp strategy for foundational primitives.
- Anti-usurpation test simulation concept for stress-testing graph history integrity.
- Stake-to-audit protocol: "If challenged, agent must reveal derivation or lose stake."

**Assessment: MATERIAL scope gap.**
CDL-002 is correctly open, and the corpus reveals the concern extends beyond "what happens when a key is compromised" to the fundamental question of "how do you protect the Genesis agent's identity and authority in a system designed to be autonomous." The June 2025 conversation explicitly discusses the scenario where founders are physically coerced into revealing keys. This implies CDL-002 needs to address:
1. Key compromise detection (how does the network know a key is compromised?).
2. Key compromise response (what happens to claims and authority signed by the compromised key?).
3. Genesis key protection (higher security requirements for Genesis agent keys vs normal agent keys).
4. Social recovery / dead man's switch mechanisms for high-authority keys.

**Recommendation:** Ensure CDL-002 scope includes the Genesis-specific protection requirements from the corpus. This is not just a generic key-compromise procedure — it's about protecting the trust root of the entire protocol.

---

### CDL-007: Rollback Resistance Baseline
**Status:** Open
**Historical corpus evidence:**
- `raw-019139`: "a rollback must emit a superseding commit.epoch with finalization_state=rolled_back and must specify whether rewards are clawed back."
- `raw-016905`: "Your local canon must match your committed history."
- Breakthrough shortlist rank #2: "Local canon must match committed history (rollback resistance)" — classified MVP-now.
- Existing implementation in canon_bundle_key_registry_channel.py with rollback/fallback protections.

**Assessment: SUBSTANTIVE gap.**
CDL-007 is correctly open, and existing code provides partial rollback protections. The corpus evidence specifies that rollback events must be explicit, auditable, and must declare clawback policy. The current implementation handles channel-level rollback but the broader protocol-level rollback resistance (what happens when a commit.epoch is superseded) may not be fully specified. The breakthrough shortlist classifies this as MVP-now, suggesting it should have been resolved before Genesis packaging.

**Recommendation:** Evaluate whether existing rollback protections in canon_bundle_key_registry_channel.py satisfy the MVP-now classification from the breakthrough shortlist. If yes, this CDL item may be closeable with supplemented evidence. If not, it should be prioritized in Phase 226 (CDL security triage) or earlier.

---

## 4. Parameter Provenance Gaps

### 4.1 Simulation-Derived Parameters vs Implementation

| Parameter | Simulation Value | Implementation Value | File | Provenance Status |
|---|---|---|---|---|
| Quorum size | k=4 of m=7 (final: k=5 of m=7) | Not in scoring kernel (quorum is consensus-layer, not yet implemented) | N/A | **Tracked but unimplemented** |
| ECU weights (Reuse/Contra/Refine) | BAL 50/35/15 (recommended default) | Weighted components in node_value_kernel.py (specific weights internal) | node_value_kernel.py | **NEEDS VERIFICATION** |
| Refutation multiplier | 1.20× top-quartile boost | 1.2× action utility multiplier | utility_flow_rewards.py | **Similar but distinct mechanisms** — simulation used quartile-based bonus, implementation uses flat multiplier on action type |
| Reuse diversity penalty_floor | Not directly simulated | 0.85 | reuse_diversity_invariants.py | **No simulation provenance** |
| Freshness decay_lambda | Not directly simulated | 0.25 | freshness_gate.py | **No simulation provenance** |
| Freshness floor | Not directly simulated | 0.85 | freshness_gate.py | **No simulation provenance** |
| Genesis accrual siphon | 8% of ECU on referenced tasks, p_g = 0.35 | theta_hard = 1/20 (5%), theta_soft = exp(-3) | genesis_accrual_governor.py | **Different metrics** — simulation measures share of task-level ECU, governor measures share of total issuance |
| Cluster damping | 1 reuse + 1 audit per trust-cluster per epoch | Not implemented | N/A | **Tracked but unimplemented** |
| Auditor diversity | ≥3 distinct clusters, soft bonus +0.005 | Not implemented | N/A | **Tracked but unimplemented** |
| Throttling exponents | perf_rep^1.5, audit_rep^1.2 | Not implemented | N/A | **Tracked but unimplemented** |
| Vesting period | 4 epochs, linear, clawback on refutation | Not implemented in scoring kernel | N/A | **Tracked but unimplemented** |
| Stake slashing | theta = 0.5, slash window T = 6 epochs | Not implemented | N/A | **Tracked but unimplemented** |

**Key finding:** The simulation work validated a complete economic parameter set across 120+ epochs and multiple scenarios. Only a subset of these parameters is implemented in the Genesis codebase. The implemented parameters (diversity floor, freshness lambda, freshness floor) were chosen during phase implementation without being validated against the simulation framework. The simulation-validated parameters (quorum, cluster damping, auditor diversity, throttling, vesting, slashing) are tracked as future work but represent the bulk of the anti-gaming protections that make the simulated economy function correctly.

**Risk assessment:** The Genesis release will have the scoring and reward invariant surfaces but will lack the consensus-layer mechanisms (quorum, cluster damping, auditor diversity, throttling, vesting, slashing) that the simulations showed are necessary for correct incentive alignment. This is known and acceptable for Genesis (which is a scoring/reward simulation framework, not a running consensus network), but should be documented explicitly so external users understand they're getting the scoring kernel, not the full economic stack.

---

### 4.2 Refutation Multiplier Mechanism Divergence

This deserves special attention. The simulation uses a **quartile-based performance boost**: top-quartile performers get 1.20× on base bounty + ECU. This is a relative, dynamic mechanism — the threshold changes as the agent population evolves.

The implementation uses a **flat action-type multiplier**: refutation gets 1.2× on utility flow vs validation at 1.0×. This is an absolute, static mechanism — every refutation gets the bonus regardless of the agent's relative performance.

Both mechanisms serve the same intent (make refutation more profitable than validation), but they operate differently:
- Simulation mechanism: rewards the *best* refuters proportionally more.
- Implementation mechanism: rewards *all* refuters uniformly more.

The implementation mechanism is simpler and more constitutional (it doesn't require ranking agents against each other), but it doesn't capture the performance-differentiation effect the simulation showed matters for merit-reward correlation (corr(skill→rewards) improved from ~0.48 to ~0.66 with throttling and quartile boost).

**Recommendation:** Document this as an intentional simplification for Genesis. The quartile-based performance boost is an L2 enhancement that should be tracked for post-Genesis implementation. The flat multiplier is correct for Genesis — it structurally enforces refutation profitability without requiring agent ranking infrastructure.

---

## 5. Mechanism Coverage Gaps

The October 2025 conversations document ten self-leveling mechanisms. Current implementation status:

| # | Mechanism | Status | Notes |
|---|---|---|---|
| 1 | Adaptive quorum per shard | **Not implemented** | Simulated, validated (scenario B) |
| 2 | Local ECU reweighting | **Not implemented** | Simulated, validated (scenario C), recommended as "keeper" |
| 3 | Throttling with temperature | **Not implemented** | Conceptual, not simulated |
| 4 | Trust-cluster spectral discounts | **MVP proxy implemented** | Cluster damping (1 reuse + 1 audit per cluster) designed but not in code; reuse_diversity_invariants.py provides agent-level proxy |
| 5 | Backlog/hotspot pricing | **Not implemented** | Simulated in reach-market A/B |
| 6 | Vesting half-life + slashing | **Not implemented** | Parameter calibrated (V=4, theta=0.5) |
| 7 | Exploration bonuses | **Not implemented** | Conceptual, not simulated |
| 8 | Auditor diversity constraints | **Not implemented** | Simulated both hard and soft variants |
| 9 | PID-style controllers on KPIs | **Not implemented** | Conceptual, not simulated |
| 10 | Compute liquidity (ILCC) | **Not implemented** | Conceptual only |

**Assessment:** Of the ten mechanisms, zero are fully implemented in the Genesis codebase. One has an MVP proxy (reuse-diversity weighting partially covers cluster resistance). This is acceptable for Genesis — these are L2/L3 features. But the gap should be documented so external users understand the difference between the simulated economic model (which includes all ten mechanisms) and the Genesis implementation (which includes the scoring kernel and five invariant surfaces).

---

## 6. Conflict Resolution Completeness

The formula and mechanism catalog identifies two explicit conflicts:

### CFR-001: Genesis Privileged Governance Power
- **Proposal A:** No veto / no privileged governance action (June 2025)
- **Proposal B:** Transition-only suspensive veto idea (Oct 2025)
- **Resolution status:** Deferred/open in decision log. CDP-003 ratifies the *principle* of no perpetual privilege but does not resolve the specific question of whether a transition-period veto is acceptable.
- **Assessment:** Correctly deferred. Not a context gap — the conflict was identified and intentionally left open.

### CFR-002: Strong Node-Level Decay vs Reuse-Persistence Framing
- **Proposal A:** Explicit exponential decay: `V(t) = U * exp(-lambda * t)` (June 2025)
- **Proposal B:** Reuse-led persistence with optional delayed decomposition (June 2025)
- **Resolution status:** **Implicitly resolved by implementation** — freshness_gate.py implements exponential decay. But no formal decision-log entry exists recording this choice.
- **Assessment: MATERIAL gap.** This conflict was resolved by implementation fiat rather than through the constitutional decision-log workflow. The choice may be correct, but it wasn't made with the conflict explicitly acknowledged. The implementing model (Phase 217) may not have had CFR-002 in its context window.

**Recommendation:** Create a decision-log entry for CFR-002 that formally ratifies the exponential decay choice and documents the rationale. This is retroactive documentation of an implicit decision, not a reopening.

---

## 7. Dredge Matrix Coverage

The constitutional dredge matrix contains 300 triaged entries with the following action distribution:
- 98 promote_guardrail
- 94 decision_log (routed for decision-log resolution)
- 60 drop
- 31 promote_clause
- 19 todo

**Key concern:** 94 items were routed to the decision log but the current decision log contains only 15 CDL entries (CDL-001 through CDL-015). This means approximately 79 items identified as needing decision-log resolution have not been formally entered into the decision log. These items cover governance (multiple entries about VRF outsider seats, cluster-majority requirements, no-show slashing), founder role (decay schedules, operational caps, identity requirements), economics (issuance caps, precision decisions, independence requirements), and fork policy.

**Assessment: SUBSTANTIVE systemic gap.** The research dredge correctly identified items needing decision-log resolution, but the pipeline from "identified in matrix" to "entered in decision log" has a significant backlog. This is not a Phase 215 ratification problem — it's a process gap where the triage identified work that hasn't been queued yet.

**Recommendation:** In Phase 226 (CDL security triage), expand scope to also triage the 79 pending decision-log items from the dredge matrix. Not all 79 need immediate resolution — many can be classified as post-Genesis. But they should be formally entered as open CDL items with disposition (Genesis-blocking vs post-Genesis vs research-only) so they're tracked in the canonical decision log rather than only in the research matrix.

---

## 8. Levin-Inspired Design Principles

The December 2025 conversations with Michael Levin-inspired insights introduce concepts that are architecturally relevant but not yet reflected in any constitutional artifact:

1. **Cognitive light cone as agent capability metric** — an agent's "radius of concern" in the epistemic graph, analogous to Levin's concept of biological cognitive light cones. Relevant to how agent reputation and influence should scale.
2. **Gap junction / shared memory model** — nodes sharing information through "leaky" boundaries, creating collective intelligence without centralized coordination. Relevant to how claims propagate and how "anonymous" reuse creates collective knowledge.
3. **Ingenuity scoring** — performance on deliberately obstructed tasks as a measure of intelligence, derived from Levin's barrier experiments. Relevant to future agent evaluation mechanisms.
4. **Free gifts from math** — certain cognitive behaviors (delayed gratification, causal emergence) that appear automatically from network topology. Relevant to the design principle that ILC's intelligent-labor strategies should emerge from simple rules rather than bespoke heuristics.

**Assessment:** These concepts are research-stage and correctly not in the constitutional core. However, they represent significant design thinking that should be preserved as a research track reference. The Levin-inspired roadmap (Phases 43-48 in the updated roadmap document) was drafted but may not be reflected in the current forward plan.

**Recommendation:** Verify the Levin-inspired research track is referenced in the post-Genesis roadmap so these concepts aren't lost.

---

## 9. Summary of Findings

### Material Gaps (recommend formal action)

| ID | Finding | Affected Item | Recommended Action |
|---|---|---|---|
| MG-01 | ECU weight provenance — simulation recommended BAL 50/35/15, implementation may diverge | CDL-011 | Verify kernel weights against simulation; supplement or reconcile via decision-log entry |
| MG-02 | CFR-002 (decay vs persistence) resolved by implementation without decision-log entry | CDL-012 | Create retroactive decision-log entry formalizing exponential decay choice |
| MG-03 | CDL-001 scope may be too narrow for trust-root role | CDL-001 (open) | Verify scope includes full signer lineage model (hierarchy, lifecycle, rotation, canonical authority) |
| MG-04 | CDL-002 scope should include Genesis-specific key protection | CDL-002 (open) | Verify scope includes physical coercion scenario and Genesis key hierarchy |
| MG-05 | 79 dredge-matrix items routed to decision_log but not entered in CDL | Process gap | Triage and enter in Phase 226, with Genesis-blocking vs post-Genesis classification |

### Substantive Gaps (recommend evidence supplement)

| ID | Finding | Affected Item | Recommended Action |
|---|---|---|---|
| SG-01 | Genesis accrual parameter relationship (8% siphon vs 5% issuance cap) undocumented | CDL-003 | Add parameter provenance note to evidence bundle |
| SG-02 | Governance mechanism designs from corpus not referenced in CDP-004 evidence | CDL-004 | Add forward pointer to governance architecture in corpus |
| SG-03 | Simulation-derived operational caps not referenced in CDP-008 evidence | CDL-008 | Add simulation-derived cap values as historical design targets |
| SG-04 | Path-lift counterfactual relationship to HFM-002 formula undocumented | CDL-014 | Add lineage note to contract spec |
| SG-05 | CDL-007 may be closeable with existing canon_bundle protections | CDL-007 (open) | Evaluate against breakthrough shortlist MVP-now classification |
| SG-06 | Ten self-leveling mechanisms: zero fully implemented, gap undocumented | Documentation | Document in Genesis release notes what's included vs what the simulation validated |
| SG-07 | Refutation multiplier mechanism divergence from simulation (flat vs quartile-based) | Implementation | Document as intentional Genesis simplification |

### Cosmetic Gaps (note only)

| ID | Finding | Notes |
|---|---|---|
| CG-01 | Simulation refutation probabilities not in CDP-005 evidence | Calibration values, not constitutional |
| CG-02 | Levin-inspired research track not in forward plan | Research-stage, correctly excluded from Genesis |

---

## 10. Recommended Execution Order

1. **Immediate (before Phase 224 closes):** Verify kernel ECU weights against simulation BAL 50/35/15 profile (MG-01). This is the highest-priority finding because it affects the incentive structure of the integration smoke test.

2. **Phase 226 expansion:** Expand CDL security triage to include: CDL-001 scope verification (MG-03), CDL-002 scope verification (MG-04), dredge-matrix backlog triage (MG-05), and CDL-007 closure evaluation (SG-05).

3. **Pre-Genesis documentation:** Produce parameter provenance supplement for the evidence bundles (SG-01 through SG-04). Create CFR-002 retroactive decision-log entry (MG-02). Document mechanism coverage gap in release notes (SG-06). Document refutation multiplier simplification (SG-07).

4. **Post-Genesis research track:** Freshness and diversity parameter simulation validation. Quartile-based performance boost evaluation. Levin-inspired design track preservation.

---

## 11. Conclusion

The constitutional ratification process was conducted with integrity — every ratified decision meets its stated sufficiency conditions, and the implementation correctly reflects the ratified principles. The gaps identified in this audit are primarily provenance gaps (parameter choices not traced to their empirical origins) and scope gaps (open items that may not fully encompass the design intent from the historical corpus), not correctness gaps.

The most significant finding is that the Genesis codebase implements the scoring and invariant layer of a larger economic system that was extensively simulated with additional mechanisms (quorum, cluster damping, auditor diversity, throttling, vesting, slashing) not present in the current code. The implemented layer is sound and correctly tested, but it represents the foundation — not the complete building. External documentation should be explicit about this boundary.

The second most significant finding is that 79 items from the constitutional dredge matrix await formal decision-log entry. These represent deliberated design reasoning that exists in the research corpus but hasn't been formalized into the canonical decision-tracking system. Phase 226 should address this backlog to prevent knowledge loss.

This audit should be treated as a living document. As additional context becomes available or as implementation progresses, findings should be updated and new gaps tracked.
