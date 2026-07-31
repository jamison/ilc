# CDL-102 Inviter-Chaining Economics Ratification 1576m v0.1

**CDL:** CDL-102
**Title:** Inviter-Chaining Economics
**Status:** RATIFIED
**Phase:** 1576m
**Date:** 2026-07-31
**Sensitivity:** SENSITIVE CDL ratification
**Ratification token:** `cdl_102_ratified_phase_1576m`

## 1. CDL Identity

CDL-102 is the constitutional lane for economic credit attribution to inviters
when invited agents complete work on the graph. It consumes the opening at
`docs/specs/ilc_cdl_102_inviter_chaining_economics_opening_1573ad_v0.1.md`
and the prelock at
`docs/specs/ilc_cdl_102_inviter_chaining_economics_prelock_1573aq_v0.1.md`.

CDL-102 is ratified as a governance authority only. It does not activate invite
enforcement, invite nullifier gossip, invite provenance edge writing, backward
attribution production settlement, ECU minting, ILC settlement, wallet writes,
public mirror publication, or public RC.

## 2. Authority Chain And Evidence

Required input tokens were confirmed in `docs/phases/STATUS.md`:

| Token | Authority surface |
| --- | --- |
| `cdl_102_inviter_chaining_economics_opened_phase_1573ad` | CDL-102 opening |
| `inviter_chaining_cdl_prelocked_phase_1573aq` | CDL-102 prelock |
| `backward_attribution_cdl_ratified_GAP_ECU_03` | CDL-108 formula and invite-init authority |
| `backward_attribution_runtime_wired_GAP_ECU_04b` | Backward attribution runtime bridge and anti-gaming caps |
| `backward_attribution_soak_complete_GAP_ECU_06` | Focused graph-to-ECU backward attribution soak |

The Phase 1573aq prelock required "live network" evidence before ratification
because the then-open model still contemplated unresolved invite-specific
fractions, depth decay, and fraud/clawback parameters. The 2026-07-28 forward
plan superseded that fixed-fraction model: CDL-102 now binds inviter economics
to ratified CDL-108 graph-derived backward attribution. Therefore the evidence
threshold for this ratification is the completed CDL-108 ratification plus the
GAP-ECU-04b runtime bridge and GAP-ECU-06 focused soak. Post-public-RC live
invite-redemption evidence is not required to ratify this non-activation
governance rule.

Production invite credit remains gated by later phases: 1576n, 1576p-b, 1576q,
and 1576r.

## 3. Q1 Resolution - Inviter Credit Mechanism

**Opening question:** What fraction of an invited agent's initial ECU earnings
routes to the inviter?

**Resolution:** No hardcoded fraction is ratified. Inviter credit is organic
graph-derived backward attribution under CDL-108.

At invite redemption, later Phase 1576q is authorized to create a durable Atlas
`PROVENANCE` edge from the invited agent's INIT/work context to the inviter's
identity or eligible inviter artifact context. When the invited agent's accepted
frontier or accepted revision work triggers a CDL-108 backward attribution
event, the traversal engine may reach the inviter through that typed graph path.
The inviter receives only the credit produced by the ratified CDL-108 formula:

```text
raw_path_score = alpha^depth * age_weight * typed_path_weight *
                 artifact_weight * status_quality_weight * novelty_weight
```

with `alpha = Decimal("0.45")`, `max_depth = 3`, backward pool share
`Decimal("0.10")`, and the CDL-108 event-local caps. There is no referral fee,
no percentage of the invitee's future earnings, no direct transfer, no
top-down payment, and no CDL-084 explicit inviter chain.

## 4. Q2 Resolution - Invite-Depth Decay

**Opening question:** Does inviter credit decay with invite depth,
distinguishing direct invitees from second-generation or deeper invitees?

**Resolution:** No separate invite-depth decay parameter is ratified.
Invite-related credit decays through CDL-108 traversal depth and age weighting:

```text
alpha = Decimal("0.45")
max_depth = 3
age_weight = Decimal("0.5") ** floor(age_epochs / 16)
```

Invite chains are not an independent royalty ladder. If an invite-related path
is not reachable through eligible typed graph edges within CDL-108 bounds, it
earns zero invite-init backward credit.

## 5. Q3 Resolution - Genesis Inviter-Credit Treatment

**Opening question:** Does Genesis receive inviter credit for directly invited
agents, or is Genesis' invite-service contribution covered by the fixed Genesis
tranche?

**Resolution:** Genesis receives no special invite referral fee and no
governance, reputation, or validator floor from invite credit. If Genesis is a
qualifying upstream artifact/identity context in an eligible CDL-108 graph path,
it may receive formula-derived backward ECU exactly like any other qualifying
recipient and subject to the same self-dealing, identity-overlap, novelty, and
cap rules.

This does not amend CDL-029. CDL-029 remains the separate 80/15/5
performer/auditor/Genesis ILC allocation split, including the Genesis 5%
tranche and hard cap mechanics. CDL-102 creates no extra Genesis ILC tranche and
does not alter `G_max`, `theta_hard`, or post-theta-hard routing.

## 6. Q4 Resolution - Attribution Expiry

**Opening question:** How many epochs does inviter attribution persist before
expiry?

**Resolution:** No separate invite-only expiry period is ratified. The Atlas
provenance edge is durable and audit-visible unless a later authorized graph
revision, supersession, refutation, or governance path changes its status. Credit
magnitude decays through CDL-108's age-weight function; stale paths may therefore
contribute little or zero credit without deleting the historical graph record.

## 7. Q5 Resolution - Fraud, Duplicate Redemption, Clawback, And Withheld Reward

**Opening question:** What fraud, duplicate-redemption, clawback, or
withheld-reward review path applies when invitation provenance is valid but the
invited agent's work is later rejected?

**Resolution:** CDL-102 ratifies the following fraud boundary:

- Duplicate redemption is blocked locally by Phase 1576p and must be blocked
  cross-node by Phase 1576p-b before public RC.
- Invite-init is non-recursive; receiving inviter credit does not create another
  invite-init trigger.
- Inviter/invitee identity overlap, same root key, same operator cluster, and
  circular invite lineage receive zero invite-init backward credit under CDL-108.
- Semantically thin invite paths must pass CDL-108's
  `novelty_minimum_score = Decimal("0.20")` gate.
- Pre-settlement invalid or duplicate invite evidence withholds invite-derived
  backward credit.
- Post-epoch-close ECU is not silently clawed back by CDL-102. Later fraud
  findings must use explicit graph revision, refutation, invalidation, or
  governance paths; they do not create an implicit invite-credit reversal.

## 8. Q6 Resolution - Evidence Required Before Ratification

**Opening question:** Which evidence is required before ratification: local
rehearsal evidence, 3-VPS / 7-agent evidence, or post-public-RC live network
evidence?

**Resolution:** Completed CDL-108 plus GAP-ECU runtime/soak evidence is
sufficient for CDL-102 ratification because this ratification no longer
authorizes a standalone invite percentage or live payment path. The accepted
evidence is:

- CDL-108 ratification locks the graph-derived formula, caps, audit surface, and
  invite-init mechanics.
- GAP-ECU-04b wires the backward attribution runtime bridge and anti-gaming caps.
- GAP-ECU-06 verifies the focused graph-to-ECU backward attribution soak.
- Phase 1576o and Phase 1576p provide completed preflight support for nonce
  Merkle proof verification and local nullifier detection.

Live public-RC invite redemption evidence is required for later closure of the
full invite chain, but it is not required to ratify CDL-102's constitutional
economic rule.

## 9. Locked Runtime Parameters Carried Forward From Prelock

The following Phase 1573aq locked parameters remain binding:

| Parameter | Locked value |
| --- | --- |
| CDL number | `CDL-102` |
| Runtime version | `invite_batch_runtime_1573z.v0.1` |
| Nullifier domain | `b"ilc-invite-nullifier-v1:"` |
| Nullifier construction | `sha256(INVITE_NULLIFIER_DOMAIN + batch_id.encode("utf-8") + b":" + nonce_bytes).hexdigest()` |
| `InviteBatchRecord.inviter_cid` | non-empty `str` |
| `InviteBatchRecord.batch_id` | non-empty `str` |
| `InviteBatchRecord.count` | positive `int`; `bool` rejected |
| `InviteBatchRecord.nonce_merkle_root` | 64-char lowercase SHA-256 hex |
| `InviteBatchRecord.created_epoch` | non-negative protocol epoch `int`; `bool` rejected |
| `InviteBatchRecord.inviter_sig` | non-empty `str` |
| `InviteRedemptionRecord.batch_id` | non-empty `str` copied from batch |
| `InviteRedemptionRecord.redemption_nullifier` | 64-char lowercase SHA-256 hex |
| `InviteRedemptionRecord.nonce_membership_proof` | tuple of 64-char lowercase SHA-256 hex strings |
| `InviteRedemptionRecord.redeemer_pubkey_cid` | non-empty `str` |
| `InviteRedemptionRecord.redeemer_agent_id` | non-empty `str` derived from identity seed |
| `InviteRedemptionRecord.redemption_epoch` | non-negative protocol epoch `int`; `bool` rejected |
| `InviteRedemptionRecord.inviter_cid` | non-empty `str` copied from batch |
| Raw nonce storage policy | raw nonce returned to caller for private custody; never stored in permanent batch or redemption records |
| Redemption nullifier storage | stored permanently in `InviteRedemptionRecord.redemption_nullifier` |

The unresolved prelock fields are resolved by this ratification as:

| Former unresolved field | Ratified resolution |
| --- | --- |
| Maximum invite-chain depth | CDL-108 `max_depth = 3`; no separate invite chain depth |
| Inviter credit fraction | none; fixed percentage rejected |
| Invite-depth credit decay | CDL-108 depth/age decay |
| Genesis inviter-credit treatment | no special referral treatment; CDL-029 unchanged |
| Attribution expiry | no invite-only expiry; CDL-108 age decay plus graph status |
| Fraud, duplicate-redemption, clawback, withheld-reward review | nullifier gates, CDL-108 zero-credit self-dealing rules, novelty gate, and explicit later graph/governance remedies |

## 10. CDL-091 And CDL-029 Disambiguation

CDL-091 remains Jury Incentive Economics. CDL-102 does not reuse, amend,
reinterpret, or supersede CDL-091.

CDL-029 remains the 80/15/5 allocation split and Genesis tranche authority.
CDL-102 does not modify CDL-029, the Genesis 5% tranche, `theta_hard`, `G_max`,
or post-theta-hard routing.

## 11. Implementation Gates

This ratification authorizes the following successor phases to proceed:

- Phase 1576n: invite enforcement gate.
- Phase 1576p-b: cross-node invite nullifier D2D gossip.
- Phase 1576q: invite provenance edge wiring.
- Phase 1576r: end-to-end invite-chain integration tests after 1576n, 1576p-b,
  and 1576q.

This ratification does not by itself activate any runtime path.

## 12. Non-Claims

This ratification does not:

- activate inviter credit;
- implement invite provenance edge writing;
- implement invite enforcement;
- implement cross-node nullifier gossip;
- mint ECU;
- settle ILC;
- write wallet, treasury, validator, or production graph state;
- modify `InviteBatchRecord` or `InviteRedemptionRecord` schemas;
- amend CDL-029, CDL-084, CDL-091, or CDL-108;
- authorize public mirror publication;
- authorize public RC.

## 13. Ratification Token

```text
cdl_102_ratified_phase_1576m
```
