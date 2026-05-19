# ILC Public Claimability Activation Gate Report 1389 v0.1

**Phase:** 1389
**Date:** 2026-05-19
**Status:** FAILED CLOSED

```text
public_claimability_gate_phase_1389_executed
public_claimability_gate_failed_phase_1389
gate_failed_reason=claimability_runtime_public_mode_blockers_still_active
claimability_runtime_public_mode_blockers_still_active_phase_1389
```

## 1. Verdict

Phase 1389 re-executed the public claimability/API activation gate after
explicit human authorization:

```text
GO Phase 1389
```

The gate fails closed. The governance/documentation prerequisites are mostly
closed, including CDL-088 ratification, ADR-0038, CDL-090 ratification, Phase
1377 replay/nullifier policy, Phase 1378 legacy route cleanup, Phase 1387
hardening pass, Phase 1387a public-economics firewall, and Phase 1388 CDL-048
activation/counsel clearance.

The implementation surface is not activation-ready. Direct code inspection of
`ilc_core/sidecars/claimability_receipt_verifier.py` shows the claimability
verifier remains local-only and still carries active public-mode blockers:

```text
public_claimability_api_authority_missing_phase_1305
replay_nullifier_policy_not_activated_phase_1305
duplicate_claim_registry_not_activated_phase_1305
public_safe_disclosure_schema_not_final_phase_1305
transport_principal_public_path_not_activated_phase_1305
```

The Phase 1377 artifact committed policy, but explicitly did not implement or
activate the nullifier registry, public claim endpoint, public verifier API, or
public claimability runtime. Therefore this gate cannot honestly record a public
claimability activation verdict.

## 2. Phase 1336 Blocker Recheck

| Blocker | Required evidence | Evidence read | Result |
|---------|-------------------|---------------|--------|
| CDL-088 not ratified | `cdl_088_ratified_phase_1376` | `docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md`; CDL-088 register row | closed |
| Agent birth attestation spec missing | `agent_birth_attestation_adr_0038_committed_phase_1370` | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | closed |
| Identity bootstrap ADR/CDL not drafted or ratified | `cdl_090_ratified_phase_1373` | `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md`; CDL-090 register row | closed |
| Replay/nullifier policy unwritten | `replay_nullifier_policy_committed_phase_1377` | `docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md` | policy closed; runtime activation still open |
| Legacy `/v1/public/*` routes not cleaned | `legacy_public_labeled_fastapi_routes_cleaned_phase_1378` | `docs/phases/phase_1378_legacy_fastapi_route_cleanup_walkthrough.md`; `tests/test_fastapi_route_cleanup_1378.py`; `ilc_core/server.py` | closed |
| Counsel clearance not obtained | `counsel_clearance_public_verifier_api_phase_1388` | `docs/specs/ilc_counsel_clearance_1388_v0.1.md` | closed |

## 3. Additional Window 1369-1390 Preconditions

| Preconditions | Evidence read | Result |
|----------------|---------------|--------|
| Phase 1387 hardening gate pass | `docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md` | closed |
| Accepted ADR/CDL public-RC coverage matrix | `docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md` | closed |
| Public-only economics admission firewall | `docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md`; `ilc_core/ledger/public_economics_admission_firewall.py` | closed |
| CDL-048 activation and Phase 1388 counsel clearance | `docs/specs/ilc_counsel_clearance_1388_v0.1.md`; `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | closed for value-path prerequisite |
| Claimability verifier public-mode blockers absent | `ilc_core/sidecars/claimability_receipt_verifier.py` | open |

## 4. Claim Enumeration Results

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1389 prompt validates | `docs/antigravity_tasks/antigravity_prompt__phase_1389_g8_public_claimability_activation_gate.md`; `tools/validate_phase_prompt.py` | confirmed |
| CDL-088 is ratified | CDL-088 row in `docs/specs/ilc_constitutional_decision_log_v0.1.md`; Phase 1376 evidence | confirmed |
| ADR-0038 is accepted | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed |
| CDL-090 is ratified | CDL-090 row in `docs/specs/ilc_constitutional_decision_log_v0.1.md`; Phase 1373 evidence | confirmed |
| Replay/nullifier policy exists | `docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md` | confirmed |
| Replay/nullifier runtime registry is active | `ilc_core/sidecars/claimability_receipt_verifier.py`; repo search for `claim_nullifier_registry_v1` | not confirmed |
| Duplicate-claim registry is active | `ilc_core/sidecars/claimability_receipt_verifier.py`; repo search for duplicate-claim registry implementation | not confirmed |
| Legacy `/v1/public/*` routes are removed | `ilc_core/server.py`; `tests/test_fastapi_route_cleanup_1378.py` | confirmed |
| Phase 1388 counsel/value-path prerequisite is closed | `docs/specs/ilc_counsel_clearance_1388_v0.1.md` | confirmed |
| Public economics cannot be constructed from private visibility | Phase 1387a matrix/firewall docs and runtime guard | confirmed |

## 5. Disposition

Gate result:

```text
gate_failed_reason=claimability_runtime_public_mode_blockers_still_active
```

No public claimability activation is recorded. The next required work is an
implementation/hardening phase that removes the remaining public-mode blockers
only after it implements or proves:

1. public-safe disclosure schema finality;
2. public transport principal activation for claimability admission;
3. replay/nullifier registry implementation;
4. duplicate-claim rejection at API admission;
5. public claim endpoint or verifier API activation semantics;
6. tests proving public-mode blockers are no longer present.

## 6. Non-Authorization

Phase 1389 does not activate public claimability, public verifier API serving,
public claim endpoint serving, public RC publication, source publication,
release signing, wallet withdrawal, wallet transfer, wallet spend, ECU minting,
ILC settlement, mainnet launch, public token distribution, CDL mutation,
external legal advice, counsel approval by external counsel, or legal
conclusion.

## 7. Graph Delta

`graph_delta=load_bearing_artifact_added:docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md -> public-claimability/activation-gate`
