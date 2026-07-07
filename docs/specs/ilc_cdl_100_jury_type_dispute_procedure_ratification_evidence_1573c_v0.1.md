# ILC CDL-100 Jury Type Dispute Procedure Ratification Evidence 1573c v0.1

**Phase:** 1573c
**Date:** 2026-07-07
**Status:** ratified
**Ratification token:** `cdl_100_ratified`
**Closure token:** `jury_type_dispute_procedure_s9_ratified`

## 1. CDL-100 Identity

CDL-100 ratifies the two-path jury procedure for type disputes required by
ADR-0035 section 7 forward obligation S9. It consumes the Phase 1573b CDL-099
definition-node ratification output as its immediate prerequisite.

The Phase 1573c prompt referenced `docs/adr/ADR_0021_Epistemic_Finality.md`,
but that path does not exist in the live repository. The live ADR-0021 source is
`docs/specs/ilc_adr_0021_epistemic_finality_claims_461_v0.1.md`; it defines the
boundary between CDL-051 protocol-finality truth and CDL-052 graph-side
epistemic evaluation of finality claims.

The prompt also suggested Decision 5 under CDL-044. Direct-read found that
CDL-044 ratifies `retention_epochs = 1 issuance_epoch`, while the live orphan timeout is ratified by CDL-046 and implemented as `ORPHAN_TIMEOUT_EPOCHS = 4`.
CDL-100 therefore locks Decision 5 to CDL-046.

## 2. Governing Authority Chain

| Authority | Status | Evidence |
| --- | --- | --- |
| ADR-0035 | Accepted; defines type-level versus instance-level claim forms and S9 | `docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md` |
| CDL-097 | Ratified; type-definition node authority | `cdl_097_ratified_phase_1528p` |
| CDL-099 | Ratified; five initial definition-node records | `cdl_099_ratified` and `definition_node_instances_s8_ratified` |
| CDL-095 | Ratified; local jury finality, petition, high-stakes, diversity-fail escalation | `cdl_095_ratified_phase_1448c` |
| CDL-096 | Ratified; global-tier finality architecture | `cdl_096_ratified_phase_1553p` |
| ADR-0021 | Completed boundary record; finality claims remain domain-separated | `docs/specs/ilc_adr_0021_epistemic_finality_claims_461_v0.1.md` |
| CDL-046 | Ratified; orphan timeout is 4 issuance epochs | `docs/specs/ilc_cdl_046_timed_out_amendment_ratification_evidence_409_v0.1.md` |

## 3. Five Decisions Locked

| Decision | Locked outcome | Token |
| --- | --- | --- |
| Type-level jury size | Global-tier high-stakes procedure under CDL-096 | `cdl_100_type_level_jury_size_global_tier_high_stakes_auto` |
| Type-level bond | CDL-095 high-stakes petition bond with dispute-scope multiplier | `cdl_100_type_level_bond_petition_cdl095_high_stakes_plus_scope_multiplier` |
| Type-level verdict effect | Authorizes CDL opening only; no automatic ratification | `cdl_100_type_level_verdict_authorizes_cdl_opening_not_automatic_ratification` |
| In-flight and existing hyperedges | Snapshot semantics; no retroactive redefinition | `cdl_100_in_flight_snapshot_semantics_no_retroactive_redefinition` |
| Instance-level statute/payout rule | CDL-046 four-issuance-epoch orphan timeout; settled payouts irreversible without later value-path authority | `cdl_100_instance_level_statute_cdl046_orphan_timeout_payout_irreversible` |

## 4. Two-Path Spec Document Committed

Procedure spec:

`docs/specs/ilc_cdl_100_jury_type_dispute_procedure_v0.1.md`

The spec defines:

- Path A: type-level constitutional claims resolved through the CDL amendment
  process only.
- Path B: instance-level epistemic claims resolved through the standard
  Popperian jury path.
- Snapshot semantics for superseded definition nodes.
- CDL-046 orphan-timeout treatment for unsettled instance-level claims.
- Irreversibility of settled payouts absent separate value-path authority.

## 5. ADR-0035 S9 Closed

ADR-0035 section 7 forward obligation S9 required a jury procedure for type
disputes. CDL-100 closes S9 for the initial pre-RC type-definition lane.

Closure token:

`jury_type_dispute_procedure_s9_ratified`

## 6. Ratification Verdict

CDL-100 is ratified in Phase 1573c under the explicit human authorization
`GO Phase 1573c`.

Verdict token:

`cdl_100_ratified`

## 7. Non-Claims

This phase does not:

- activate the ADR-0035 type registry
- clear `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED`
- migrate `HyperEdge.hyperedge_type`
- implement any jury runtime machinery
- activate shard-tier or global-tier review
- alter CDL-095 or CDL-096 finality constants
- ratify a value-path reversal process
- write wallet, treasury, settlement, minting, production-emission, or public
  path state
- authorize public RC, Genesis signing, public repository publication, or epoch
  transition
