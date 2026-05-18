# ILC CDL-088 Public Claimability Authority Ratification Evidence 1376 v0.1

**CDL number:** CDL-088
**Title:** Public Claimability Authority
**Status after this phase:** RATIFIED
**Phase:** 1376
**Date:** 2026-05-18
**Human authorization:** `GO Phase 1376` plus `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1376`
**CDL-only register commit:** `3d8ce11e`
**Evidence token:** `cdl_088_public_claimability_ratification_evidence_committed`

```text
cdl_088_ratified_phase_1376
cdl_088_public_claimability_ratification_evidence_committed
cdl_088_historical_hardening_phase_1374_ref_asserted
```

---

## 1. Ratification Statement

Phase 1376 ratifies CDL-088 as the constitutional authority for future public
claimability. Ratification means the CDL register records CDL-088 as `ratified`
and binds the Phase 1375 locked scope constants as governance law for any later
public claimability activation gate.

Phase 1376 does not activate public claimability. It does not open a claim
endpoint, does not enable a public verifier API, does not authorize wallet-facing
actions, does not mint ECU, does not settle ILC, does not activate any value
path, and does not modify `ilc_core/`.

Register disposition:

```text
cdl_088_register_diff_disposition_phase_1376=cdl088_open_to_ratified
```

---

## 2. Pre-Execution Claim Verification

| Claim | File/symbol checked | Result |
| --- | --- | --- |
| CDL-088 is open before Phase 1376 register mutation | `docs/specs/ilc_constitutional_decision_log_v0.1.md` before CDL-only commit | confirmed |
| Phase 1375 prelock complete | `docs/phases/STATUS.md`; `docs/specs/ilc_cdl_088_prelock_spec_1375_v0.1.md` | confirmed |
| Phase 1375 locked all six opening questions | `docs/specs/ilc_cdl_088_prelock_spec_1375_v0.1.md` §4 | confirmed |
| Phase 1374 historical opening commit exists | `git log`; `git show 43bcddc0:docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |
| Phase 1374 historical CDL-088 row was open | `git show 43bcddc0:docs/specs/ilc_constitutional_decision_log_v0.1.md` CDL-088 row | confirmed |
| `cdl_088_ratified_phase_1376` was not a current register token before mutation | repo token search before CDL-only commit | confirmed |
| No active claim-endpoint token is current | repo contradiction search | confirmed |

---

## 3. Authority Inputs

| Authority | Binding for CDL-088 ratification |
| --- | --- |
| CDL-088 opening, Phase 1374 | Opened the public claimability authority lane only; did not ratify or activate public claimability. |
| CDL-088 prelock, Phase 1375 | Resolved the Phase 1374 questions and locked the scope constants ratified here. |
| CDL-090 ratification, Phase 1373 | Supplies identity-bootstrap governance, while public identity activation remains separately gated. |
| Gap 13 public-claimability boundary, Phase 1252 | Public claimability must be derived from settled runtime roots and epoch resolution, not manual entitlement claims. |
| Phase 1291 verifier contract preflight | Supplies the future verifier contract boundary while keeping public API serving disabled. |
| Phase 1377 replay/nullifier policy | Remains required before any live claim endpoint can activate. |
| Phase 1387a accepted ADR/CDL and public-economics firewall | Must prove public-only economics admission before public RC or public economics activation. |
| Phase 1388 counsel/value-path clearance | Must close counsel and value-path prerequisites where public economic action is implicated. |
| Phase 1389 public claimability gate | Remains the first possible public activation gate and requires separate explicit human authorization. |

---

## 4. Ratified Scope Constants

| Constant | Ratified value |
| --- | --- |
| `bounded_public_claimability_condition_v1` | Public claimability may be considered only under a later explicit activation gate. It must be condition-bounded, epoch-scoped, proof-bound, replay-protected, public-only, and release/API-authorized. |
| `public_claimability_proof_bundle_v1` | Any future public claimability presentation must bind identity, epoch, settled runtime root, wallet-state root, latest balance receipt, history digest, claimability proof, conversion receipt hash, conversion key hash, conversion lot, issuance epoch, conversion deadline epoch, transport authority, replay/nullifier evidence, and public-only economics admission evidence. |
| `reciprocal_claim_identity_score_interlock_v1` | Claimability evaluation must bind canonical agent identity to the claimability proof and settlement evidence. It must not derive public claimability solely from reputation, solely from a claim payload, solely from private history, or from an unselected reciprocal scoring formula. |
| `reciprocal_scoring_formula_deferred_v1` | The historical reciprocal scoring formula remains a non-selected research candidate. CDL-088 does not promote it into public-RC launch law. |
| `ecu_escrow_admission_boundary_v1` | ECU escrow is not a universal prerequisite. If a future claim class uses escrow, the escrow proof must be public-graph, non-custodial by default, exact-numeric, finite, replay-protected, and bound to public ECU/ILC settlement evidence after explicit value-path authority. |
| `no_private_or_shadow_economics_claimability_v1` | Private, semi-private, shard-local, or operator-local advisory scores cannot create public claimability, public ECU, public reputation, public settlement, or public corroboration. |
| `public_verifier_api_minimum_preconditions_v1` | A public verifier API requires CDL-088 ratification, replay/nullifier policy, public-safe disclosure review, authenticated public transport, release allowlist promotion, public-only economics admission, counsel/value-path clearance where applicable, and explicit Phase 1389 authorization. |
| `ratification_vs_activation_split_v1` | Phase 1376 ratifies CDL-088 scope only. Public activation remains outside Phase 1376 and requires the later Phase 1389 gate. |
| `claim_endpoint_default_closed_v1` | Claim endpoints, public routes, non-loopback listeners, wallet actions, ECU minting, ILC settlement, and value-path behavior remain disabled unless a later explicit gate activates them. |

---

## 5. Ratification Decision

CDL-088 ratifies the following launch-safety boundaries:

1. Public claimability must be bounded by conditions, epoch scope, proof binding,
   replay/nullifier policy, public-only economics admission, release/API
   authority, and an explicit later activation gate.
2. Future public claimability presentations must use a proof bundle that binds
   identity, epoch, settled runtime root, wallet-state root, balance receipt,
   history digest, conversion evidence, transport authority, replay/nullifier
   evidence, and public-only economics admission evidence.
3. Reciprocal scoring is ratified only as an identity/proof interlock. The
   historical reciprocal scoring formula remains deferred.
4. ECU escrow is ratified only as a conditional admission boundary for claim
   classes that later explicitly require escrow. Universal escrow is rejected.
5. Public verifier API authority is ratified only as a minimum prerequisite set.
   No public verifier API implementation or serving surface is authorized here.
6. Ratification and activation are separate. Phase 1376 ratifies scope; Phase
   1389 or a later explicit gate must activate any public claimability surface.

---

## 6. Rejected Candidates

The ratification rejects these candidates:

1. Unbounded public claimability.
2. Always-open claim endpoints.
3. Public claimability before the later explicit activation gate.
4. Claimability from agent-authored manual entitlement statements.
5. Claimability from private or semi-private node history.
6. Claimability from operator-local advisory scoring.
7. Public priority or reward claims based on private opaque commitments alone.
8. Automatic public reputation, reward, corroboration, or settlement
   carry-forward from private material.
9. Universal ECU escrow as a prerequisite for every public claim class.
10. Provider custody, verifier-service custody, or wallet-provider custody as
    default escrow.
11. Treating visible settled balance as withdrawal, transfer, spend, or public
    claimability authority.
12. Treating CDL-088 ratification as endpoint activation.
13. Treating the Phase 1222 reciprocal scoring formula as selected public-RC
    launch law.

---

## 7. Non-Authorization Boundary

Phase 1376 does not authorize or perform:

1. Public claimability activation.
2. Public verifier API activation.
3. Claim endpoint activation.
4. Public HTTP route activation.
5. Public socket listener or non-loopback bind.
6. Wallet-facing withdrawal, transfer, or spend.
7. Wallet-provider signing.
8. Wallet-provider ledger writes.
9. ECU escrow acceptance.
10. Escrow custody.
11. ECU minting.
12. ILC settlement.
13. Value-path behavior.
14. Public RC publication.
15. Public launch.
16. Source publication.
17. Release artifact production.
18. Release signing.
19. Production validator deployment.
20. Production governance execution.
21. Runtime mutation in `ilc_core/`.

Current register non-activation tokens remain:

```text
public_claimability_activation_status: not_enabled
claim_endpoint_status: not_enabled
public_verifier_api_status: not_enabled
runtime_activation_status: not_authorized
phase_1389_gate_status: still_required
```

---

## 8. Historical Hardening Evidence

The Phase 1376 test suite reads the historical Phase 1374 opening commit:

```text
43bcddc0
```

The historical register row at that commit shows CDL-088 as `open`, not
`ratified`, and does not contain `cdl_088_ratified_phase_1376`.

The current register row after CDL-only commit `3d8ce11e` shows CDL-088 as
`ratified` and records:

```text
cdl_088_ratified_phase_1376
```

This records:

```text
cdl_088_historical_hardening_phase_1374_ref_asserted
```

---

## 9. Seven-Test Structure

The focused regression test file is:

```text
tests/test_cdl_088_ratification.py
```

It contains seven tests:

1. Phase 1376 prompt remains schema-valid.
2. Ratification evidence records required tokens and locked constants.
3. Current CDL-088 register row is ratified with evidence references.
4. CDL-088 ratification preserves the no-activation boundary.
5. Frontier docs record Phase 1376 completion and downstream dependencies.
6. Historical Phase 1374 register row was open.
7. Historical opening row lacks the Phase 1376 ratification token while the
   current row contains it.

---

## 10. Handoff

Phase 1377 may proceed as the replay/nullifier and duplicate-claim policy phase.
Phase 1380 may rely on CDL-090 and CDL-088 ratification as prerequisites, but
must remain dry-run and gate-closed. Phase 1389 remains the first possible public
claimability activation gate and still requires explicit human authorization.

Carry-forward:

```text
phase_1377_replay_nullifier_policy_next
phase_1380_requires_cdl_090_and_cdl_088_ratified
phase_1389_public_claimability_gate_still_required
```

Graph delta:

```text
graph_delta=load_bearing_register_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> governance/cdl088
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md -> governance/cdl088
```
