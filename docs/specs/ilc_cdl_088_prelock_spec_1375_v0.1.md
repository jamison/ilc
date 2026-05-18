# ILC CDL-088 Public Claimability Authority Prelock Spec 1375 v0.1

**CDL number:** CDL-088
**Title:** Public Claimability Authority
**Status after this phase:** OPEN / PRELOCKED
**Phase:** 1375
**Date:** 2026-05-18
**Prelock token:** `cdl_088_prelock_committed_phase_1375`
**Non-ratification token:** `cdl_088_not_ratified_phase_1375`
**Scope-lock token:** `cdl_088_scope_constants_locked_phase_1375`
**Basis:** `cdl_088_public_claimability_opened_phase_1374`

---

## 1. Prelock Statement

Phase 1375 prelocks CDL-088 by resolving the Phase 1374 public-claimability
opening questions and locking the scope constants for Phase 1376 ratification.
CDL-088 remains open and not ratified. This phase does not mutate the CDL
register, does not activate public claimability, does not open a claim endpoint,
does not enable a public verifier API, does not authorize wallet-facing actions,
does not mint ECU, does not settle ILC, and does not modify `ilc_core/`.

```text
cdl_088_prelock_committed_phase_1375
cdl_088_not_ratified_phase_1375
cdl_088_scope_constants_locked_phase_1375
```

---

## 2. Authority Inputs

| Authority | Binding for CDL-088 |
| --- | --- |
| CDL-088 opening, Phase 1374 | Opens public claimability authority only; leaves reciprocal scoring, ECU-escrow admission, bounded claimability, and verifier API prerequisites for this prelock. |
| CDL-090 ratification, Phase 1373 | Supplies identity-bootstrap governance. Identity artifacts and public identity activation remain separately gated. |
| Gap 13 public-claimability boundary, Phase 1252 | Public claimability is derived from settled runtime roots and epoch resolution, not agent-authored manual entitlement claims. |
| Phase 1291 verifier contract preflight | Defines a future verifier envelope and denial conditions while keeping public API and public claimability disabled. |
| Phase 1274 / 1275 / 1305 local claimability substrate | Supplies local conversion, proof-binding, and verifier-substrate evidence only; public serving remains blocked. |
| Phase 1377 replay/nullifier policy | Must define replay and duplicate-claim prevention before any public claim endpoint may activate. |
| Phase 1387a accepted ADR/CDL and public-economics firewall | Must prove public-only economics admission before public claimability or value-path activation. |
| Phase 1388 counsel/value-path clearance | Must close counsel and activation prerequisites before value-path or public verifier activation can pass. |
| Phase 1389 public claimability gate | Remains the first possible public activation gate and requires separate explicit human authorization. |

---

## 3. Terminology Lock

| Term | Meaning |
| --- | --- |
| `public_claimability` | A later public authority state allowing an eligible participant to present a public proof bundle for claimability evaluation. It is not wallet withdrawal, transfer, spend, ECU minting, or ILC settlement authority. |
| `bounded_claimability_condition` | A gate-bounded and epoch-scoped condition set that must be satisfied before any public claim endpoint or public verifier API may activate. It rejects always-open or indefinite claimability. |
| `claim_endpoint` | Any public or non-loopback route, listener, service, or API surface that accepts public claimability presentations. CDL-088 prelock does not create or activate one. |
| `public_verifier_api` | A future public service boundary that evaluates claimability proof bundles. CDL-088 locks minimum authority prerequisites but does not implement or serve the API. |
| `reciprocal scoring` | A minimum identity/proof interlock: claimability cannot be based only on contributor identity or only on claim payload. The historical reciprocal scoring formula remains a non-selected research candidate. |
| `ECU-escrow admission` | A conditional future economic-admission boundary for claim classes that require a bond, escrow, or stake. It is not universal claimability admission and is not activated by CDL-088. |
| `prelock` | A deliberation record resolving open questions and locking scope constants for ratification. It is not ratification. |

---

## 4. Phase 1374 Questions Resolved

| Q | Phase 1374 question | Resolution | Scope constant locked |
| --- | --- | --- | --- |
| Q1 | Is reciprocal scoring in CDL-088 scope? | Yes, but only as a minimum claim-identity/proof interlock and anti-single-factor rule. CDL-088 does not select or ratify the historical reciprocal scoring formula. Full scoring math remains deferred unless a later explicit ADR/CDL selects it. | `reciprocal_claim_identity_score_interlock_v1` |
| Q2 | Is ECU-escrow admission in CDL-088 scope? | Yes, as a conditional boundary and denial rule for future claim classes that require economic admission. CDL-088 does not require universal escrow, does not accept deposits, does not create custody, and does not authorize escrow runtime. | `ecu_escrow_admission_boundary_v1` |
| Q3 | What exactly constitutes bounded public claimability? | Public claimability is bounded by ratified CDL-088 authority, explicit Phase 1389 gate authorization, epoch-scoped proof inputs, settled-root proof binding, replay/nullifier policy, public-only economics admission, counsel/value-path clearance if value movement is implicated, and release/API allowlist promotion. | `bounded_public_claimability_condition_v1` |
| Q4 | What proof bundle must exist before a public claim endpoint can activate? | The bundle must bind canonical agent identity, epoch id, settled runtime root, wallet-state root, latest balance receipt, history digest, claimability proof reference, conversion receipt and key hashes, conversion lot, issuance/deadline epochs, TransportPrincipal or successor public-transport authority, replay/nullifier evidence, public-safe disclosure review, and public-only economics admission evidence. | `public_claimability_proof_bundle_v1` |
| Q5 | Does CDL-088 impose a condition-bounded window, epoch-bounded window, operator quorum, counsel precondition, or all of these? | CDL-088 imposes all four as activation prerequisites: condition-bounded gate checks, epoch-bounded proof validity, operator or governance quorum as defined by the Phase 1389 gate, and counsel/value-path clearance where public economic action is implicated. Wall-clock-only expiry is rejected. | `claimability_activation_preconditions_v1` |
| Q6 | Which items are CDL-088 ratification requirements versus Phase 1389 activation-gate requirements? | Phase 1376 ratifies the scope constants and non-authorization boundary. Phase 1389 verifies live prerequisites, operational evidence, allowlist/counsel status, public-only economics admission, and records the final gate result. | `ratification_vs_activation_split_v1` |

No Phase 1374 question remains unresolved for Phase 1376, except the separate
ratification decision itself.

---

## 5. Locked Scope Constants

| Constant | Locked value |
| --- | --- |
| `bounded_public_claimability_condition_v1` | Public claimability may be considered only under a later explicit activation gate. It must be condition-bounded, epoch-scoped, proof-bound, replay-protected, public-only, and release/API-authorized. |
| `public_claimability_proof_bundle_v1` | Any future public claimability presentation must bind identity, epoch, settled runtime root, wallet-state root, latest balance receipt, history digest, claimability proof, conversion receipt hash, conversion key hash, conversion lot, issuance epoch, conversion deadline epoch, transport authority, replay/nullifier evidence, and public-only economics admission evidence. |
| `reciprocal_claim_identity_score_interlock_v1` | Claimability evaluation must bind canonical agent identity to the claimability proof and settlement evidence. It must not derive public claimability solely from reputation, solely from a claim payload, solely from private history, or from an unselected reciprocal scoring formula. |
| `reciprocal_scoring_formula_deferred_v1` | The historical reciprocal scoring formula remains a non-selected research candidate. CDL-088 ratification must not promote it into public-RC launch law without a later explicit ADR/CDL. |
| `ecu_escrow_admission_boundary_v1` | ECU escrow is not a universal prerequisite. If a future claim class uses escrow, the escrow proof must be public-graph, non-custodial by default, exact-numeric, finite, replay-protected, and bound to public ECU/ILC settlement evidence after explicit value-path authority. |
| `no_private_or_shadow_economics_claimability_v1` | Private, semi-private, shard-local, or operator-local advisory scores cannot create public claimability, public ECU, public reputation, public settlement, or public corroboration. |
| `public_verifier_api_minimum_preconditions_v1` | A public verifier API requires CDL-088 ratification, replay/nullifier policy, public-safe disclosure review, authenticated public transport, release allowlist promotion, public-only economics admission, counsel/value-path clearance where applicable, and explicit Phase 1389 authorization. |
| `ratification_vs_activation_split_v1` | Phase 1376 may ratify CDL-088 scope only. Public activation remains outside Phase 1376 and requires the later Phase 1389 gate. |
| `claim_endpoint_default_closed_v1` | Claim endpoints, public routes, non-loopback listeners, wallet actions, ECU minting, ILC settlement, and value-path behavior remain disabled unless a later explicit gate activates them. |

---

## 6. Bounded Public Claimability Condition

The bounded claimability condition is:

1. CDL-088 is ratified in Phase 1376 or a later explicitly authorized ratification phase.
2. The claimant identity is bound to ratified identity-bootstrap authority and to the proof bundle.
3. The claimability presentation is tied to a specific ratified `epoch_id`, not wall-clock time.
4. The settled runtime root, wallet-state root, latest balance receipt, history digest, conversion receipt, conversion key, conversion lot, issuance epoch, and conversion deadline epoch all match.
5. Replay/nullifier and duplicate-claim rules are specified and satisfied.
6. Public-safe disclosure has been reviewed so the public endpoint does not leak private payloads, private lineage, wallet internals, secret material, or unauthorized identifiers.
7. Public-only economics admission is proven: private or semi-private nodes, private promotion history, local advisory scores, and opaque commitments cannot construct public claimability.
8. Any value-path implication has Phase 1388 counsel and activation clearance.
9. A later explicit public claimability gate authorizes activation.

This condition rejects unbounded claimability, perpetual claim windows without
epoch scoping, manual entitlement assertions, private-history credit claims,
and public endpoint activation before all gate prerequisites close.

---

## 7. Reciprocal Scoring Disposition

CDL-088 includes reciprocal scoring only as a launch-safety interlock:

- claimability must bind a canonical agent identity to a claimability proof;
- claimability must bind that proof to settled runtime and wallet-state roots;
- identity reputation alone cannot create claimability;
- claim text or claim payload alone cannot create claimability;
- private history, private lineage, shard-local pressure, or local advisory
  scores cannot create public claimability; and
- later public scoring math, if any, requires separate explicit authority.

The Phase 1222 reciprocal scoring formula remains a non-selected research candidate. CDL-088 does not select it and does not make it launch-critical.

---

## 8. ECU-Escrow Admission Disposition

CDL-088 includes ECU-escrow admission as a conditional boundary, not as a
universal gate.

If a later public claim class requires a bond, stake, fee, or escrow:

1. the escrow proof must bind to public-graph ECU or ILC state only;
2. private or shard-local work cannot supply escrow value;
3. exact numeric representation is required and Python `float` is forbidden;
4. non-finite numeric values are rejected before arithmetic or comparison;
5. no provider, verifier service, or wallet provider may hold custody by default;
6. release and counsel gates must authorize the public value-path surface; and
7. replay/nullifier checks must prevent reusing escrow evidence across claims.

CDL-088 does not accept escrow deposits, open a custody path, create wallet
provider authority, or activate any value transfer.

---

## 9. Public Verifier API Boundary

CDL-088 governs minimum public verifier API acceptance prerequisites, not API
implementation.

Before any public verifier API can activate, a later gate must prove:

1. CDL-088 is ratified.
2. The verifier contract version is authorized by Phase 1291 or a later ratified successor.
3. The local verifier substrate or successor helper no longer carries unresolved public-RC exclusion status.
4. The negative-path corpus and public-safe disclosure schema are complete.
5. The public transport identity and non-loopback serving authority are explicit.
6. The replay/nullifier policy and duplicate-claim registry are specified and tested.
7. The public-only economics admission firewall rejects private and semi-private economics.
8. Counsel, release allowlist, source/export, and packaging gates are closed where public release is implicated.
9. The public activation gate receives explicit human authorization.

Phase 1375 creates no HTTP route, FastAPI route, socket listener, non-loopback
bind, wildcard bind, public host bind, peer discovery surface, public verifier
service, claim endpoint, withdrawal endpoint, transfer endpoint, spend endpoint,
ECU mint endpoint, or ILC settlement endpoint.

---

## 10. Phase 1376 Ratification Requirements Versus Phase 1389 Activation Gate

Phase 1376 ratification, if authorized, should ratify only:

1. the bounded public claimability condition;
2. the public claimability proof bundle;
3. the reciprocal claim-identity/proof interlock;
4. the ECU-escrow admission boundary;
5. the public verifier API minimum preconditions;
6. the non-authorization boundary; and
7. the ratification versus activation split.

Phase 1389 or a later explicit activation gate must verify operational facts:

1. every required predecessor phase completed successfully;
2. replay/nullifier policy is implemented or explicitly carried with authority;
3. legacy public routes are clean;
4. public verifier and sidecar query paths are complete;
5. value-path dry-run and counsel clearance are complete if value movement is implicated;
6. the external audit/hardening gates pass or record authorized bounded deferrals;
7. accepted ADR/CDL coverage and public-only economics admission pass; and
8. the final public activation result is recorded only by the activation gate.

---

## 11. Rejected Candidates

The following candidates are rejected by this prelock:

1. Unbounded public claimability.
2. Always-open claim endpoints.
3. Public claimability before the later explicit activation gate.
4. Claimability derived from agent-authored manual entitlement statements.
5. Claimability derived from private or semi-private node history.
6. Claimability derived from operator-local advisory scoring.
7. Public priority or reward claims based on private opaque commitments alone.
8. Automatic public reputation, reward, corroboration, or settlement carry-forward from private material.
9. Universal ECU escrow as a prerequisite for every public claim class.
10. Provider custody, verifier-service custody, or wallet-provider custody as default escrow.
11. Treating a visible settled balance as withdrawal, transfer, spend, or public claimability authority.
12. Treating CDL-088 prelock or ratification as endpoint activation.
13. Treating the Phase 1222 reciprocal scoring formula as selected public-RC launch law.

---

## 12. Non-Goals And Non-Claims

This prelock does not:

1. Ratify CDL-088.
2. Mutate the CDL register.
3. Activate public claimability.
4. Activate a public verifier API.
5. Activate a claim endpoint.
6. Activate a public HTTP route.
7. Activate a public socket listener or non-loopback bind.
8. Enable wallet withdrawal, transfer, or spend.
9. Enable wallet-provider signing.
10. Enable wallet-provider ledger writes.
11. Accept ECU escrow.
12. Open an escrow custody path.
13. Mint ECU.
14. Settle ILC.
15. Activate value-path behavior.
16. Publish a public RC.
17. Publish source.
18. Produce or sign release artifacts.
19. Deploy production validators.
20. Execute production governance.
21. Modify `ilc_core/`.

CDL-088 remains open and not ratified:

```text
cdl_088_not_ratified_phase_1375
```

---

## 13. Phase 1376 Handoff

Phase 1376 must decide whether to ratify CDL-088 using the constants locked
above. If Phase 1376 mutates the CDL register, it must do so in a CDL-only
commit under explicit mutation authority and must not activate public
claimability or any public endpoint.

Carry-forward:

```text
phase_1376_cdl_088_ratification_next
```
