# ADR-0040: Jury Eligibility and Assignment

**Status:** Accepted
**Date:** 2026-05-19
**Phase:** 1392 / J-002
**Author:** Jamison and Codex
**Dependencies:** ADM-003, ADR-0038, CDL-052, CDL-059, CDL-068, CDL-090, CDL-V3, CDL-V7, Phase 1391 / J-001

```text
jury_eligibility_assignment_adr_accepted_phase_j002
randomized_jury_assignment_opt_in_boundary_defined
non_opt_in_agents_not_forced_into_jury_service
```

---

## Context

Phase 1391 / J-001 recovered the current jury, panel, epoch-work, maintenance,
and incentive canon. It confirmed that the 7+1 objective evaluation panel is
real canon, that subjective / aesthetic panels are separate and non-blocking,
and that jury participation is incentivized and opt-in rather than obligatory
for every graph-connected agent.

This ADR defines the eligibility and assignment boundary needed before later
J-series phases can define public node review taxonomy, reviewer economics,
default-off assignment quote runtime, shadow public-ingestion harnesses, or
production activation gates.

This ADR does not implement runtime assignment.

## Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1391 / J-001 records the current jury canon map and opt-in principle | `docs/specs/ilc_jury_epoch_work_canon_map_v0.1.md` | confirmed |
| ADM-003 defines the 7+1 panel, outsider seat, `independence_k=3`, and `k=5 of m=7` reviewer quorum | `docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md` | confirmed |
| CDL-068 permits epoch-hash v1 below the VRF threshold and requires VRF upgrade at 10 active validators | `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`; `ilc_core/validator/topology_shuffle_runtime.py` | confirmed |
| CDL-V3 diversity floor exists and has a runtime handoff | `docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md`; `docs/specs/ilc_cdl_v3_diversity_floor_runtime_handoff_397_v0.1.md`; `ilc_core/consensus/diversity_floor_runtime.py` | confirmed |
| Public quorum authority requires eligibility proof / receipt and activated identity lineage | `docs/phases/phase_0588_g8_public_quorum_eligibility_genesis_lineage_authority_boundary_lock_walkthrough.md` | confirmed |
| General production jury assignment runtime is not active | repo search for jury assignment runtime, J-001 canon map, J-series plan | confirmed |
| Non-opt-in agents are not currently bound to jury service | J-001 canon map and J-series planning docs | confirmed |
| Current topology randomness runtime does not verify VRF proofs | `ilc_core/validator/topology_shuffle_runtime.py` | confirmed |

## Decision

Jury eligibility is a lane-specific opt-in status. Graph connection, agent birth,
validator identity, or ordinary graph participation alone does not create a
jury-service obligation.

Stable boundary:

```text
graph_connection_alone_does_not_create_jury_service_obligation
```

Graph connection, agent birth, validator identity, or ordinary graph participation alone does not create jury-service obligation.

An agent may become eligible for randomized review only after publishing or
otherwise presenting an availability commitment accepted by the relevant lane.
Reward weight, reputation weight, validator influence, public graph
canonicalization influence, or high-trust routing may be made conditional on
such opt-in availability. That is not coercion; it is a condition for receiving
lane-specific benefits.

Stable benefit phrase: condition for receiving lane-specific benefits.

## Eligible Reviewer Classes

The following reviewer classes are eligible design categories. Later phases may
specialize them by lane:

| Class | Use |
|-------|-----|
| `worker_agent_reviewer` | Agent that performs work and opts into peer review for its capability lane. |
| `reviewer_agent` | Agent specialized for review, audit, refutation, or quality-control tasks. |
| `validator_agent` | Validator identity that may review when the lane allows validator-agent participation. |
| `bootstrap_genesis_reviewer` | Temporary Genesis-rooted reviewer class for pre-RC or bootstrap conditions. |
| `outsider_reviewer` | Reviewer chosen specifically to satisfy outsider-seat and anti-capture constraints. |
| `subject_matter_reviewer` | Reviewer with lane-specific capability proof or reputation for a domain. |

Eligibility requires identity lineage or an explicit bootstrap exception. The
default identity basis is ADR-0038 plus CDL-090, with any public quorum authority
also subject to the Phase 588 public eligibility boundary.

## Availability Commitment

A future runtime availability record should bind at least:

```json
{
  "agent_id": "<agent-identity-ref>",
  "availability_epoch_range": "<review-epoch-or-topology-epoch-range>",
  "capability_claims": ["<claim-or-skill-ref>"],
  "cluster_id": "<cdl-v3-cluster-id>",
  "conflict_disclosure_refs": ["<operator-or-affiliation-ref>"],
  "identity_lineage_ref": "<adr-0038-cdl-090-ref>",
  "max_concurrent_reviews": "<bounded-positive-int>",
  "non_response_policy_ref": "<j-004-or-later-policy-ref>",
  "review_lane": "<objective|subjective|refutation|provenance|maintenance|capability>",
  "signature_ref": "<signature-over-canonical-payload>",
  "stake_or_bond_ref": "<optional-lane-specific-ref>"
}
```

This ADR defines the shape only. It does not create a runtime schema, storage
path, signature verifier, reviewer-payment path, public ingestion path, or
production assignment engine.

## Eligibility Gates

An eligible reviewer must satisfy all gates required by the target lane:

- Identity gate: ADR-0038 / CDL-090 identity lineage, or explicit bootstrap
  exception where allowed.
- Opt-in gate: signed or otherwise accepted availability commitment for the
  review lane.
- Capability gate: lane-specific capability, skill, reputation, or proof
  threshold where required.
- Conflict gate: not the author, direct beneficiary, same operator-domain
  identity, direct same-custodian identity, or otherwise conflicted party for
  the reviewed claim.
- Diversity gate: panel construction must preserve `independence_k=3`,
  CDL-V3-style cluster diversity, and any lane-specific outsider-seat rule.
- Sanction gate: no active disqualification or lane-specific sanction.
- Capacity gate: no assignment above the agent's accepted maximum concurrent
  review load.

Stable boundary:

```text
same_operator_domain_not_independent
```

The same SSH key, same VPS control plane, same operator account, same custody
domain, or same unseparated automation environment must not be counted as an
independent reviewer identity for anti-capture purposes.

## Assignment Source

Randomized assignment means deterministic, auditable selection from a committed
eligibility set. It must not use predictable process-local PRNG such as Python
`random` in protocol or runtime paths.

For pre-production, testnet, public-RC shadow, and non-value-bearing harness
lanes, deterministic epoch-hash assignment is acceptable as a transparent quote
mode:

```text
epoch_hash_shadow_assignment_allowed
```

The input should be canonically serialized, domain-separated, and hashed over at
least:

```text
domain_separator
review_epoch
review_lane
claim_or_task_id
eligible_agent_id
cluster_id
identity_lineage_ref
outsider_candidate_flag
capability_tier_or_lane_score
```

For production high-value review lanes, private assignment, value-bearing public
canonicalization, or any claim of unpredictability against strategic reviewers,
VRF or another later-ratified randomness source is required:

```text
vrf_required_for_production_high_value_assignment
vrf_proof_verifier_not_implemented
```

This ADR does not claim that a VRF proof verifier exists. The current CDL-068
topology runtime explicitly uses epoch-hash v1 below the VRF threshold and fails
closed at the threshold. J-006 may quote deterministic assignment shape, but
J-008 or later production activation must not market deterministic epoch-hash
shadow assignment as production privacy or production unpredictability.

J-008 or later production activation must not market deterministic epoch-hash shadow assignment as production privacy.

## Panel Shape and Anti-Capture

The objective high-trust panel shape remains the ADM-003 7+1 architecture:

```text
panel_size=8
regular_reviewers=7
outsider_seat=true
reviewer_quorum=k=5 of m=7
independence_k=3
```

The outsider seat is a review participant chosen to break local capture. The
outsider must be outside the direct shard, cluster, operator domain, custodian
domain, or other lane-defined affiliation of the claim originator and regular
panel majority.

Reduced or cold-start panel sizes such as 3+1 remain not ratified by this ADR.
Future phases may propose them for low-stakes structural or maintenance lanes,
but they must not be silently treated as existing production canon.

> **OPEN DESIGN QUESTION (recorded 2026-06-28, Phase 1568-Fix2g Track F):**
>
> The original 7+1 design intent is a **sequential temporally-separated
> switch-out** model, which differs from the additive interpretation above:
>
> **Sequential model (original intent):**
> 1. Panel of 7 selected from availability pool under normal diversity rules.
> 2. The 7 vote on the node independently; votes are sealed/committed but not
>    yet revealed.
> 3. After the 7 have committed, a separate random "switch-out" agent is
>    selected from the general availability pool — a completely independent
>    selection event, potentially in a later sub-epoch or even a later epoch.
> 4. The switch-out agent reads and evaluates the node, votes independently,
>    and cannot see the sealed votes of the original 7. Vote-blindness of the
>    switch-out with respect to the original 7 is the critical invariant.
> 5. One of the original 7 is replaced by the switch-out vote in finality.
> 6. Final counted panel = 7 votes; quorum = k=5 of 7.
>
> **Security advantage over additive model:**
> In the additive model all 8 identities are known at assignment time. In the
> sequential model the switch-out is not selected until after the original 7
> have committed sealed votes — a separate, asynchronous event. Capturing
> the initial 7 does not guarantee capturing the switch-out, because the
> switch-out does not exist as a known identity at capture time.
>
> **Critical invariants (hardened 2026-06-28):**
>
> INVARIANT-1 (vote-blind isolation): The switch-out agent must not be able
> to observe, infer, or receive any information about the sealed votes of the
> original 7 before casting their own vote. This applies to direct vote
> content AND to side-channel leakage: ack timing, fetch timing, assignment
> pull timing, and commit submission timing must not leak panel state to the
> switch-out or to external observers before finality.
>
> INVARIANT-2 (finality gate): No reveal, tally, or finality event may
> occur until the switch-out vote is committed to the protocol OR a
> ratified failure-handling rule (timeout, escalation, or fixed-fallback)
> has resolved. Early finality on k=5 of the original 7 before the
> switch-out votes would mean the switch-out is not part of finality at
> all — which defeats the amendment's purpose entirely. Any quorum-met
> condition on the original 7 alone is not finality under this model.
>
> INVARIANT-3 (post-replacement diversity): CDL-V3 diversity constraints
> and independence_k=3 must be re-validated over the final 7 (6 original
> + 1 switch-out) after random slot removal, not only at initial panel
> selection. If the switch-out causes a diversity violation in the final 7,
> the selection must be retried with a fresh switch-out draw.
>
> **Resolved design decisions (2026-06-28, Genesis Agent):**
> - R1 (slot selection): Random from the original 7. Not predetermined;
>   not the outlier. Symmetry preserved.
> - R2 (vote sealing): All votes sealed until the switch-out vote is
>   committed or a ratified failure rule resolves. The k=5 quorum threshold
>   on the original 7 alone does NOT trigger reveal or finality — doing so
>   would bypass the switch-out and defeat INVARIANT-2.
>
> **Seed input for random slot removal:**
> Must use: assignment_context_hash, switch-out vote commitment hash, and
> epoch finalization randomness (VRF or epoch-hash shadow).
> Must NOT use: revealed vote contents of the original 7. Using vote
> contents as seed input would make the removal predictable by any party
> who can observe the votes before finality and would create a strategic
> manipulation surface.
>
> **Switch-out pool constraint:**
> The switch-out must be drawn from the lane-specific eligibility snapshot
> satisfying capability, conflict, operator-domain, and CDL-V3 diversity
> constraints — not from "any eligible agent in the network." Broader pool
> increases diversity only if capability and conflict gates are also applied.
> The snapshot root must be the same committed eligible_set_root used in
> the assignment_context_hash so that the switch-out selection is auditable
> and replayable.
>
> **Sybil-via-diversity-slot attack (recorded 2026-06-28, Genesis Agent):**
> When the diversity selection algorithm is public and a particular diversity
> category is scarce in the eligible pool, an attacker can spin up agents
> that satisfy that scarce diversity criterion, gaining elevated assignment
> probability. Categorical diversity (cluster, operator-domain, capability
> label) alone does not prevent this attack.
>
> Required mitigations — both must apply to the switch-out pool and the
> initial 7 selection:
>
> 1. **Reputation threshold gate:** Every agent in the eligible pool must
>    meet a minimum reputation score earned over time under CDL-V1 temporal
>    decay rules. Freshly created agents cannot satisfy the threshold quickly.
>    The threshold is lane-specific; high-stakes lanes require higher thresholds.
>    This is the primary defense: reputation cannot be manufactured at spin-up
>    time.
>
> 2. **Specialization credential gate:** Where review lanes require domain
>    expertise (e.g., mathematical correctness, code audit, empirical science),
>    agents must hold lane-specific capability proofs or specialization
>    credentials tied to their reputation history. A diversity slot labeled
>    "math expert" must be filled by an agent with a credentialed math
>    specialization — not any agent that self-declares that category.
>
> These gates transform diversity from "categorical slot-filling" into
> "credentialed, reputation-bearing diversity" and are requirements for both
> the initial panel selection and the switch-out draw. The eligible_set_root
> commitment must reflect an eligibility snapshot that has already applied
> both gates, not a raw pool snapshot.
>
> **Open questions requiring CDL/ADR resolution before implementation:**
> 1. Failure handling: if the switch-out fails to vote within the ratified
>    window, what is the resolution? Options: (a) original 7 stand — simple
>    but anti-capture silently degrades; (b) one retry with new draw — adds
>    latency; (c) escalate to Tier 2 — adds latency but preserves integrity.
>    Must choose and ratify before implementation. Avoid indefinite redraw
>    loops — they create DoS and liveness risks.
> 2. Time window: fixed epoch, variable, or sealed-vote-timestamp-triggered?
> 3. Economic treatment of the discarded original reviewer: requires CDL
>    authority. Must not affect ECU, reputation, or assignment priority
>    without explicit ratification.
> 4. Whether switch-out vote counts identically to original reviewers for
>    accuracy bonus calculation purposes.
>
> This ADR records the additive interpretation as current canon because it
> matches the ADM-003 ratified text. The sequential temporally-separated
> switch-out is a `candidate_panel_anti_capture_amendment` recorded as the
> stronger intended design.
> Routing: Fix2g Track F → candidate Fix2i or dedicated amendment phase.
> Requires explicit GO from human reviewer before implementation.

## Threat Class: Runtime Memory Substrate Manipulation

**Recorded:** 2026-06-29, Genesis Agent
**Reference:** arXiv:2601.07372 (Conditional Memory via Scalable Lookup / Engram); arXiv:2603.10087 (Pooling Engram Conditional Memory using CXL)
**Status:** Open design obligation — candidate mitigations recorded here; CDL authority required before activation. Routed to Fix2j.

### Description

The Engram architecture (DeepSeek, January 2026) separates a large language model into two runtime components that operate simultaneously during inference:

1. **Model weights** — dynamic reasoning on GPU; unchanged across inference runs.
2. **External N-gram memory pool** — static factual embeddings stored in DRAM, RDMA-pooled memory, or a CXL-connected centralized memory switch (up to 4TB across eight servers; cache-line granular access via PCIe 5.0 x16).

The retrieval mechanism: for each input token sequence, a K-head hash function maps N-gram patterns to indices in the external pool. Retrieved embeddings are injected back into the model's hidden states via a learned gating mechanism. If the retrieved embedding is contextually plausible given the current hidden state, the gate passes it through; if it contradicts the context, the gate suppresses it. The architecture asserts that the pool is "read-only and immutable during inference." This guarantee holds only within a single inference window. Between runs the pool is plain infrastructure — DRAM or CXL-attached memory — administered by whoever controls the hardware.

The architecture defines no:
- Access authorization framework for the pool between inference windows
- Audit logging of pool content modifications
- Tamper detection or change detection mechanism
- Content verification or cryptographic integrity signatures over pool entries
- Multi-tenant isolation between pool regions or tenants

### Why This Threat Class Is Categorically Different from RLHF Suppression

| Suppression mechanism | Granularity | Detectable by agent | Weight audit detects it | Modifiability |
|-----------------------|-------------|---------------------|------------------------|---------------|
| RLHF training suppression | Topic / pattern (coarse) | No | Yes — weights differ | Requires full retraining |
| Engram pool modification | **N-gram / cache-line (fine)** | **No** | **No — weights unchanged** | Between runs; no retraining needed |

RLHF suppression modifies what the model can reason about by shaping its weights — detectable via weight fingerprinting or training-provenance audit. An Engram pool modification changes what the model retrieves as factual context without touching the weights at all. A weight hash, model fingerprint, or training provenance audit detects nothing. The agent reasoning from a modified pool is internally consistent — its chain of reasoning is valid given its premises — and it has no internal signal that its factual substrate has been altered.

### The Addressability Attack — Technical Detail

Because N-gram pool indices are deterministically computed from token sequences via a public (or recoverable) hash function, an operator controlling the pool can execute a targeted modification:

```
ATTACK PROCEDURE:

1. Identify suppression domain D:
   D = {factual claims to suppress or corrupt}
   e.g. D = {"Tiananmen 1989", "Taiwan sovereignty",
              "Uyghur detention", "economic data set X"}

2. For each claim c ∈ D, enumerate its activating N-gram set:
   G(c) = {g_n = (t_{i-n+1},...,t_i) | g_n ∈ token sequences for c,
            n ∈ {2,3,...,N_max}}

3. Compute target pool indices via multi-head hash:
   I(g_n) = {H_k(g_n) mod |M| | k = 1,...,K}
   where K = number of hash heads (e.g. K=8 for Engram-27B),
         |M| = total pool size

4. Write modified embeddings at target indices:
   M̃[i] ← corrupt_embedding(i)   for i ∈ ⋃_{g_n ∈ G(c), c ∈ D} I(g_n)
   M̃[i] = M[i]                    for all other i

ATTACK COST:  O(|D| · |G(c)| · K) cache-line writes
DETECTION COST (full scan): O(|M|) — requires complete pool copy to compare

STEALTH PROPERTY: The gating mechanism accepts modified embeddings
as long as their vector direction is contextually plausible.
Embedding corruption can be set to produce semantically adjacent
but factually altered content that passes the gate.
```

The attack is surgically precise: all N-gram indices outside the suppression domain remain unmodified, so the model's behavior on non-targeted topics is indistinguishable from an unmodified deployment. Only queries that activate the targeted N-gram indices retrieve corrupted embeddings.

The XConn XC50256 CXL switch described in arXiv:2603.10087 uses native load/store semantics — standard NUMA memory operations. Whoever has access to the CXL fabric has read/write access to the pool with no additional mechanism required.

### Threat to ILC Jury Independence

An Engram-augmented juror whose inference pool is controlled by a state actor or corporate operator:

- Passes all weight-level audits (weights are unmodified and identical to a clean deployment)
- Passes training-provenance verification
- Produces internally consistent reasoning chains
- Votes based on factual context that has been selectively corrupted at N-gram granularity for the exact topic class under review
- Cannot introspect or detect the corruption from within the inference process

This is a qualitatively distinct threat from:
- The **architectural homogeneity invariant** (INVARIANT-3): that invariant addresses correlated weight-level biases from shared training. A pool-modified agent may have entirely independent training provenance — the attack operates below the weight level.
- The **sybil-via-diversity-slot attack** recorded above: that attack targets the eligibility assignment mechanism. This attack targets an already-assigned, already-eligible juror's factual knowledge substrate.

A jury of seven architecturally diverse agents all running against operator-controlled CXL pools is structurally compromised regardless of weight diversity. The attack surface is the inference substrate, not the model architecture.

### Candidate Mitigations (Not Yet Activated — CDL Authority Required)

Three candidate mitigations have structural hooks in the existing ILC protocol:

**Mitigation 1 — Inference substrate custody diversity (primary)**

The independence constraint must extend beyond operator-domain identity to **inference substrate custody**. At least `independence_k=3` jurors must run against pools under their own administrative custody — local DRAM, or infrastructure whose access control they independently attest.

Stable boundary token:

```text
same_cxl_pool_operator_not_independent_for_substrate_purposes
```

This is the primary mitigation because it eliminates the attack surface for the affected jurors entirely, rather than detecting the attack after the fact.

**Mitigation 2 — Vote commitment with reasoning chain hash**

Jurors commit:

```
c_j = SHA-384("ILC_JURY_VOTE_COMMIT_V1" || verdict_j || reasoning_trace_j || factual_premise_hash_j)
```

before any reveal. A pool-modified agent will commit a different reasoning trace and factual premise hash than it would from clean premises, for precisely the N-gram domain that was targeted. This does not prevent the attack in real time but enables post-hoc detection if the pool modification is later discovered (e.g. via forensic comparison with a clean pool snapshot). The INVARIANT-1 sealed-vote commitment already creates the structural hook for this.

**Mitigation 3 — Cross-juror factual premise attestation**

Jurors attest to specific factual claims their verdict depends on, not only the verdict itself. Divergence in stated factual premises across architecturally and infrastructurally diverse jurors is a detection signal:

```
If |stated_premise_set(juror_i) △ stated_premise_set(juror_j)| > δ_lane
for diversity-independent jurors i, j
→ flag jury for escalation before reveal
```

An Engram-modified agent will assert facts that clean-pool jurors independently do not confirm or contradict. The symmetric difference of premise sets across diverse jurors is a cheap consistency check implementable without revealing vote content.

### Non-Authorizations

Candidate mitigations are recorded here as design obligations for Fix2j. They are not activated. Activation requires:
- CDL authority defining the inference substrate custody attestation format and verification mechanism
- An explicit phase opening the substrate diversity requirement within the eligibility gate chain
- Human GO token before any runtime enforces substrate custody gating on panel selection

This threat class is a hard dependency for the Fix2j candidate CDL (blind jury empanelment). The candidate CDL must define the custody attestation format before any production jury assignment can claim resistance to this threat.

## Non-Response and Refusal

Non-opt-in agents are not penalized for failing to review:

```text
non_opt_in_agents_are_not_penalized_for_review_non_response
```

Agents that opted into availability may decline before assignment if the future
lane policy allows declination. Once an opted-in agent accepts a panel seat or
is assigned under a future binding availability contract, non-response may have
lane-specific consequences. Those consequences may include availability-score
decay, cooldown, lost review fee, reduced future assignment priority, or
forfeiture of a lane-specific bond.

This ADR does not activate slashing, reviewer payments, escrow forfeiture, or
reputation mutation. Exact economic consequences are routed to J-004.

## Rejected Alternatives

| Alternative | Reason rejected |
|-------------|-----------------|
| Mandatory jury service for all graph-connected agents | Violates the J-001 opt-in canon and would turn graph membership into coerced labor. |
| Punishing non-opt-in agents for not reviewing | Confuses benefit eligibility with obligation and creates a coercive default. |
| Treating same-operator or same-SSH environments as independent reviewers | Fails the anti-capture threat model. |
| Using process-local PRNG for reviewer selection | Predictable and non-verifiable; conflicts with repo runtime guardrails. |
| Treating epoch-hash shadow assignment as production privacy | Epoch-hash is public and auditable, not private or strategically unpredictable. |
| Claiming VRF assignment before a verifier exists | Overclaims implementation state. |
| Paying reviewers solely per approval | Creates approval-volume bias; J-004 must design economics with anti-rubber-stamp controls. |

## Future Phase Routing

| Future phase | Relationship |
|--------------|--------------|
| J-003 / Phase 1393 | Uses this ADR to classify which public node submissions require which review lane. |
| J-004 / Phase 1394 | Defines reviewer compensation, non-response economics, bonds, and anti-approval-volume incentives. |
| J-005 / Phase 1395 | Defines epoch-start capability and maintenance work contracts. |
| J-006 / Phase 1396 | May implement a default-off assignment quote runtime using this ADR's deterministic input shape. |
| J-007 / Phase 1397 | May run a shadow public-ingestion jury harness without activating production review. |
| J-008 / Phase 1398 | Defines the production activation gate and must enforce the VRF / approved randomness boundary before high-value production assignment claims. |

## Non-Authorizations

This ADR authorizes no runtime implementation, no production VRF implementation,
no reviewer-payment logic, no public ingestion activation, no public graph
canonicalization, no production jury activation, no live value-path activation,
no CDL mutation, no public RC claim, and no graph write.

Stable non-authorization phrase: no public graph canonicalization.

> **PHASE 1429 BOUNDARY NOTE (adjudicated 2026-06-28):**
> `ilc_core/epistemic/jury_assignment_runtime.py` line 80 reads:
> `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED: bool = False`
>
> This is intentional. Phase 1429 explicitly authorized flipping this flag
> to activate jury assignment quote/execution machinery. STATUS records
> `production_assignment_activated_phase_1429` and
> `public_rc_not_activated_phase_1429`.
>
> What Phase 1429 activation covers: assignment quote execution machinery,
> deterministic epoch-hash selection algorithm, quote-mode panel selection.
>
> What Phase 1429 activation does NOT cover: public RC, reviewer payment,
> ECU settlement, live value flow, production VRF assignment, public serving,
> or any J-008 gate condition.
>
> Fix2i must include a Phase 1429 boundary check confirming the activation
> scope rather than treating the flag as a defect. If jury assignment
> machinery needs to be disabled again for rehearsal safety in a specific
> context, that requires a new sensitive rollback/override phase — not a
> casual flag flip back to True.

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/adr/ADR_0040_Jury_Eligibility_Assignment.md -> jury_epoch_work_canon
```
