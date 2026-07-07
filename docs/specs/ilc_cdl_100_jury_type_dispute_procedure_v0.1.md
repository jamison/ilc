# ILC CDL-100 Jury Type Dispute Procedure v0.1

**Phase:** 1573c
**Date:** 2026-07-07
**Status:** ratified
**Ratification token:** `cdl_100_ratified`
**Closure token:** `jury_type_dispute_procedure_s9_ratified`

## 1. Governing Authority Chain

CDL-100 ratifies the jury procedure required by ADR-0035 forward obligation S9.
The authority chain is:

| Layer | Role | Evidence |
| --- | --- | --- |
| ADR-0035 | Defines homoiconic type-definition architecture and the two-path claim form for type disputes | `docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md` |
| CDL-097 | Ratifies the type-definition node authority surface and default-off registry boundary | `cdl_097_ratified_phase_1528p` |
| CDL-099 | Ratifies the initial five hyperedge type-definition node records | `cdl_099_ratified` |
| CDL-100 | Ratifies the two-path jury procedure for type disputes | `cdl_100_ratified` |

CDL-100 is governance-only. It does not activate the ADR-0035 type registry,
does not change runtime hyperedge validation, and does not migrate
`HyperEdge.hyperedge_type` away from its current string-literal runtime surface.

## 2. Two-Path Overview

CDL-100 preserves the ADR-0035 distinction between type-level and
instance-level claims.

| Path | Claim target | Claim character | Resolution path |
| --- | --- | --- | --- |
| Path A | The definition node or the meaning/scope of a hyperedge type | Constitutional | CDL amendment process only |
| Path B | A specific hyperedge instance and whether it satisfies its declared type | Epistemic | Standard Popperian jury path |

Path A changes what a type means only through a later CDL amendment. Path B
evaluates whether a concrete hyperedge instance satisfies the already-ratified
definition node referenced by that instance.

## 3. Path A - Type-Level Constitutional Claims

### 3.1 Who May Assert

Any agent may assert a type-level challenge against a ratified type-definition
node.

Path A is a CDL amendment process only. It is not an instance-refutation path.

### 3.2 Filing

The filer submits a type-level petition with a bond. The bond basis is:

`CDL-095 high-stakes petition bond * dispute_scope_multiplier`

where:

- `CDL-095 high-stakes petition bond` is `3 * CDL-091 base review fee`.
- `dispute_scope_multiplier` is the number of existing hyperedges of the
  challenged type, subject to a later implementation phase defining the exact
  count source and cap rules.

The multiplier deters frivolous attacks on foundational or widely used types
without creating an unreachable bond for narrow or newly ratified types.

### 3.3 Jury

Type-level disputes use the CDL-096 global-tier architecture as a high-stakes
constitutional surface:

- panel size: 21 reviewers
- participation floor: 15 of 21 reviewers
- approval threshold: exact 2/3 integer arithmetic over participating
  non-abstain approvals where the ratified jury-verdict rules permit approval
  counting

This selection is locked by:

`cdl_100_type_level_jury_size_global_tier_high_stakes_auto`

CDL-100 does not activate global-tier runtime review. It ratifies the
constitutional procedure that a later runtime phase must follow.

### 3.4 Evidence Standard

The jury asks whether the proposed amendment correctly captures the intended
revision to the type definition while preserving:

- ADR-0035 compositional primitive-basis requirements
- the existing definition node's role schema and decomposition recipe as the
  baseline being challenged
- CDL-099 snapshot semantics for already-created hyperedges
- any governing CDL attribution, finality, and escalation constraints cited by
  the challenged type

### 3.5 Verdict Effect

A successful Path A verdict authorizes opening a new CDL lane to supersede the
definition node. The verdict does not itself ratify the new definition and does
not mutate the existing definition node.

This is locked by:

`cdl_100_type_level_verdict_authorizes_cdl_opening_not_automatic_ratification`

### 3.6 Snapshot Semantics

Existing and in-flight hyperedges retain the definition-node version current at
their creation epoch. A type-level challenge does not retroactively redefine
existing hyperedges and does not reverse settled attribution events.

This is locked by:

`cdl_100_in_flight_snapshot_semantics_no_retroactive_redefinition`

### 3.7 Escalation

Because Path A claims affect the canonical type namespace, they are treated as
HIGH_STAKES governance claims. CDL-096 global-tier escalation applies when a
type-level dispute threatens namespace fragmentation, cross-shard consistency,
or a governing CDL interpretation.

## 4. Path B - Instance-Level Epistemic Claims

### 4.1 Who May Assert

Any agent may assert that a specific hyperedge instance does not satisfy its
declared type.

### 4.2 Filing

The filer submits a standard Popperian refutation node citing:

- the challenged hyperedge instance
- the type-definition node or CDL-099 record for the declared type
- the alleged mismatch against `role_schema`, `membership_requirements`, or
  `decomposition_recipe`

### 4.3 Jury

Instance-level claims use the CDL-095 local jury path:

- 7 regular reviewers plus 1 outsider/advisory reviewer in the J-series panel
  model
- exact 2/3 integer arithmetic for verdict threshold where CDL-095 permits
  approval counting
- CDL-095 petition, high-stakes, and diversity-fail escalation semantics

CDL-100 does not alter CDL-095 jury size or finality semantics for
instance-level claims.

### 4.4 Evidence Standard

The jury asks whether the challenged hyperedge satisfies the declared type's:

- `role_schema`
- `membership_requirements`
- `decomposition_recipe`
- governing CDL references
- snapshot-bound definition version at the hyperedge creation epoch

The jury must not use a later superseding definition to judge an earlier
hyperedge.

### 4.5 Verdict Effect

The verdict affects the challenged hyperedge instance and its claim status under
CDL-095 and CDL-096 finality paths. It does not amend the type definition and
does not create a new CDL.

### 4.6 Statute Of Limitations And Settled Payouts

The live orphan-timeout constant is CDL-046, not CDL-044. CDL-046 ratifies
`orphan_timeout_epochs = 4` issuance epochs and `recovery_policy =
stake_full_release`.

Instance-level type claims should be filed within the CDL-046 four-issuance-
epoch orphan-timeout horizon when the challenged claim remains orphaned or
unsettled. After an attribution event is economically finalized, an
instance-level claim may still produce a graph-side finding, but it cannot
reverse the settled payout without a separate value-path authority.

This is locked by:

`cdl_100_instance_level_statute_cdl046_orphan_timeout_payout_irreversible`

CDL-044 remains a separate retention-epochs authority and is not the source of
the orphan-timeout constant.

## 5. Five Required Decisions Locked

| Decision | Chosen value | Token |
| --- | --- | --- |
| 1. Jury size for type-level claims | CDL-096 global-tier high-stakes procedure | `cdl_100_type_level_jury_size_global_tier_high_stakes_auto` |
| 2. Bond requirements for type-level challenge petitions | CDL-095 high-stakes petition bond multiplied by dispute scope | `cdl_100_type_level_bond_petition_cdl095_high_stakes_plus_scope_multiplier` |
| 3. Automatic CDL after type-level verdict | Verdict authorizes CDL opening; it does not automatically ratify a new CDL | `cdl_100_type_level_verdict_authorizes_cdl_opening_not_automatic_ratification` |
| 4. In-flight hyperedges during type challenge | Snapshot semantics; no retroactive redefinition | `cdl_100_in_flight_snapshot_semantics_no_retroactive_redefinition` |
| 5. Statute of limitations for instance-level claims | CDL-046 four-issuance-epoch orphan timeout; settled payouts irreversible without later value-path authority | `cdl_100_instance_level_statute_cdl046_orphan_timeout_payout_irreversible` |

## 6. ADR-0035 S9 Closure Declaration

ADR-0035 section 7 forward obligation S9 required a jury procedure for type
disputes. CDL-100 closes that obligation for the initial ADR-0035/CDL-099
pre-RC type-definition lane.

Closure token:

`jury_type_dispute_procedure_s9_ratified`

## 7. Non-Claims

CDL-100 does not:

- activate the ADR-0035 type registry
- clear `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED`
- migrate `HyperEdge.hyperedge_type` from `str`
- implement jury runtime machinery
- activate shard-tier or global-tier runtime review
- alter CDL-095 or CDL-096 finality constants
- define the ECU formula for type-dispute resolution
- reverse settled value-path payouts
- write wallet, treasury, minting, settlement, or production-emission state
- authorize public P2P, public RC, public repository publication, Genesis
  signing, or epoch transition
