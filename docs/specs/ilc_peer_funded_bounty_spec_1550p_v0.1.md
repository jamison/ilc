# ILC Peer-Funded Bounty Spec 1550p v0.1

**Status:** PRE-RC SPECIFICATION
**Phase:** 1550p
**Window:** 1546p-1555p
**OBL:** OBL-029
**Runtime activation:** none

```text
obl_029_peer_funded_bounty_spec_committed_phase_1550p
peer_funded_bounty_runtime_not_activated_phase_1550p
no_bounty_payout_activation_phase_1550p
```

## 1. Purpose

This specification closes the pre-public-RC design gap for peer-funded bounties:
bottom-up ILC-escrowed bounty commitments distinct from treasury-funded bounties
and the Phase 1542 protocol-issued productive ECU expansion bounty scaffold.

The spec is intentionally non-activating. It defines the required future
workflow, authority path, anti-gaming constraints, and runtime invariants before
any peer-funded bounty escrow or payout path can exist.

## 2. Relationship to Existing Surfaces

| Surface | Status | Relationship |
|---|---|---|
| ADR-0016 | Proposed | Describes protocol-issued bounties, peer-funded bounties, and funding requests |
| OBL-027 / Phase 1542 runtime | Default-off scaffold complete | Protocol-issued bounty accounting only; explicitly excludes peer-funded bounties |
| CDL-047 treasury governance | Ratified | Treasury-funded bounty and burn-floor governance; not the funding source for peer-funded bounties |
| OBL-029 / this spec | Complete by Phase 1550p | Defines peer-funded bounty design without creating runtime or escrow |

Peer-funded bounties are demand-side pull: an agent with ILC reserves identifies
a productive knowledge gap and offers escrow-backed funding for validated work.
Treasury-funded or protocol-issued bounties are top-down stimulus: governance or
treasury allocates protocol-side resources to selected work.

## 3. Future Lifecycle

1. **Bounty proposal:** A poster submits a bounty node with deliverable,
   objective/refutable acceptance criteria, domain, deadline, maximum ECU reward,
   required panel lane, and escrow commitment.
2. **Escrow proof:** The poster locks ILC in a future non-custodial escrow
   object bound to the bounty identifier, poster identifier, amount, deadline,
   and refund rules.
3. **Admission review:** The bounty is checked for uniqueness, non-duplication,
   objective scope, anti-spam limits, and cap compatibility.
4. **Work submission:** Any eligible agent may submit candidate work against the
   bounty.
5. **Validation:** A panel or jury lane applies CDL-V3 diversity and CDL-V7
   Popperian validation requirements before any reward can be recognized.
6. **Success path:** If work is validated and finality gates pass, the future
   runtime may create bounty ECU within the ratified cap and bind escrowed ILC
   to the conversion budget.
7. **Failure or expiry path:** If work fails, is not submitted, or does not reach
   finality before the deadline, unconsumed escrow returns under the ratified
   refund rule and no bounty ECU is created.
8. **Audit record:** Every terminal state emits a canonical bounty audit record
   with replay protection.

## 4. Required Future Runtime Invariants

Any future runtime must satisfy all of the following before activation:

- exact decimal or fixed-point arithmetic only;
- no `float` for escrow, reward, cap, deadline, or payout amounts;
- canonical sorted-key serialization for bounty identifiers and audit records;
- atomic escrow-state writes;
- replay-protected terminal transitions;
- no payout before panel finality;
- no ECU creation without validated productive work;
- no debt: if escrow or cap is insufficient, the bounty does not proceed;
- per-bounty and per-epoch caps;
- non-custodial escrow by default;
- explicit refund rules;
- idempotent success, failure, expiry, and cancellation handling.

## 5. Anti-Gaming Constraints

The future governance instrument must address:

| Vector | Required mitigation |
|---|---|
| Self-bounty farming | Poster/worker relatedness disclosure, conflict checks, and panel scrutiny |
| Sybil fund splitting | Aggregate caps by funding cluster, bounty family, and epoch |
| Ambiguous deliverables | Objective acceptance criteria required at admission |
| Circular work | Provenance checks against already-rewarded claims and tautologies |
| Escrow spoofing | Escrow proof must be protocol-verifiable and bound to bounty ID |
| Griefing through impossible bounties | Admission review rejects impossible or underspecified deliverables |
| Deadline abuse | Maximum and minimum deadline bounds |
| Milestone abuse | Optional milestone escrow releases require independent finality per milestone |
| Funder exit manipulation | Withdrawal rules must be explicit before bounty admission |

## 6. Relationship to Funding Requests

Funding requests are the reciprocal push side of ADR-0016: an agent with
capability requests backing. Peer-funded bounties are the pull side: funders
post a desired work target. Both share escrow, finality, cap, and anti-gaming
requirements, but they should remain distinct node types or subtypes until a
future CDL decides whether a unified schema is safe.

## 7. Minimum Future CDL Questions

Before runtime activation, a future governance process must decide:

1. Minimum and maximum escrow size.
2. Maximum bounty amount as a fraction of `B_e`.
3. Whether peer-funded bounty ECU has the same vesting as ordinary productive
   ECU.
4. Whether funders receive only public-good satisfaction, a fixed premium, or a
   share of downstream ECU.
5. Whether multi-funder escrow is admitted at launch or deferred.
6. Which panel lane reviews prospective bounty admission.
7. Which panel lane reviews bounty fulfillment.
8. How failed work affects worker reputation.
9. How malicious or impossible bounty postings affect poster reputation.

## 8. Closure of OBL-029

OBL-029 required a pre-RC spec for peer-funded, bottom-up, ILC-escrowed bounties
separate from treasury-funded bounties. This document provides that spec while
preserving runtime activation as future governance scope.

```text
obl_029_closed_phase_1550p
peer_funded_bounty_runtime_not_activated_phase_1550p
no_bounty_payout_activation_phase_1550p
```

## 9. Non-Authorization

This specification does not create escrow balances, write wallet state, write
treasury state, issue ECU, settle ILC, activate bounty payouts, activate
peer-funded bounty runtime, change ADR-0016 status, amend CDL-047, open or
ratify a CDL, activate public RC, or transition epoch.
