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

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/adr/ADR_0040_Jury_Eligibility_Assignment.md -> jury_epoch_work_canon
```
