# ILC Public Claimability Activation Gate Report 1389 Rerun v0.2

**Phase:** 1389 rerun
**Date:** 2026-05-19
**Status:** PASS - public claimability gate activated
**Supersedes for routing:** `docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md`

```text
public_claimability_gate_phase_1389_executed
result=public_claimability_activated
public_claimability_gate_rerun_passed_after_1389b
claimability_runtime_public_mode_blockers_cleared_phase_1389_rerun
phase_1389_v0_1_failed_closed_superseded_by_v0_2_pass
```

## 1. Verdict

Phase 1389 has been rerun after Phase 1389a and Phase 1389b closed the
remaining public-mode blockers discovered by the historical v0.1 gate report.

The gate now passes:

```text
result=public_claimability_activated
```

This records the public claimability gate verdict required by the Phase 1389
prompt. It does not start a public HTTP server, add a public claim endpoint,
publish public RC artifacts, perform a wallet action, mint ECU, settle ILC, or
launch mainnet.

## 2. Historical v0.1 Disposition

`docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md`
remains valid historical evidence. It failed closed because
`ilc_core/sidecars/claimability_receipt_verifier.py` still carried five
public-mode blocker constants at that time.

Phase 1389a and 1389b resolved those blockers. This v0.2 report is the
superseding routing artifact for the Phase 1389 gate verdict.

## 3. Phase 1336 Blocker Recheck

| Phase 1336 blocker | Required evidence | Evidence read | Result |
|--------------------|-------------------|---------------|--------|
| CDL-088 not ratified | `cdl_088_ratified_phase_1376` | `docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md`; CDL-088 register row | closed |
| Agent birth attestation spec missing | `agent_birth_attestation_adr_0038_committed_phase_1370` | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | closed |
| Identity bootstrap ADR/CDL not drafted or ratified | `cdl_090_ratified_phase_1373` | `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md`; CDL-090 register row | closed |
| Replay/nullifier policy unwritten | `replay_nullifier_policy_committed_phase_1377`; `claim_nullifier_registry_v1_active_phase_1389b` | `docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md`; `ilc_core/sidecars/claim_nullifier_registry_v1.py`; Phase 1389b tests | closed |
| Legacy `/v1/public/*` routes not cleaned | `legacy_public_labeled_fastapi_routes_cleaned_phase_1378` | `docs/phases/phase_1378_legacy_fastapi_route_cleanup_walkthrough.md`; `tests/test_fastapi_route_cleanup_1378.py`; `ilc_core/server.py` | closed |
| Counsel clearance not obtained | `counsel_clearance_public_verifier_api_phase_1388`; `cdl_048_activated_phase_1388` | `docs/specs/ilc_counsel_clearance_1388_v0.1.md`; Phase 1388 runtime evidence | closed |

## 4. Additional Window 1369-1390 Preconditions

| Precondition | Evidence read | Result |
|--------------|---------------|--------|
| Phase 1387 hardening gate pass | `docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md`; token `pre_activation_hardening_gate_pass_phase_1387` | closed |
| Accepted ADR/CDL public-RC coverage matrix | `docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md`; token `accepted_adr_cdl_runtime_coverage_matrix_phase_1387a` | closed |
| Public-only economics admission firewall | `docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md`; `ilc_core/ledger/public_economics_admission_firewall.py`; tokens `public_economics_requires_public_node_admission_verified_phase_1387a` and `private_visibility_excluded_from_public_economics_phase_1387a` | closed |
| No unrouted accepted ADR/CDL public-RC functionality | Phase 1387a matrix token `no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a` | closed |
| CDL-048 activation and Phase 1388 counsel clearance | `docs/specs/ilc_counsel_clearance_1388_v0.1.md`; `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | closed |
| Claimability verifier public-mode blockers absent | `ilc_core/sidecars/claimability_receipt_verifier.py`; `tests/test_phase_1389b_claimability_public_mode_runtime.py` | closed |

## 5. Public-Mode Blocker Closure

The historical Phase 1389 v0.1 report named five public-mode blockers. Their
current dispositions are:

| Blocker | Closing artifact | Result |
|---------|------------------|--------|
| `public_claimability_api_authority_missing_phase_1305` | Phase 1389a records `cdl_088_is_public_claimability_api_authority_phase_1389a` | closed |
| `public_safe_disclosure_schema_not_final_phase_1305` | Phase 1389a records `public_safe_disclosure_schema_final_cdl_088_scope_phase_1389a` | closed |
| `transport_principal_public_path_not_activated_phase_1305` | Phase 1389a records `transport_principal_resolved_at_d2d_layer_adr_0039_cdl_078_phase_1389a` | closed |
| `replay_nullifier_policy_not_activated_phase_1305` | Phase 1389b records `claim_nullifier_registry_v1_active_phase_1389b` | closed |
| `duplicate_claim_registry_not_activated_phase_1305` | Phase 1389b records `duplicate_claim_registry_active_phase_1389b` | closed |

Direct code inspection confirms:

```text
_PUBLIC_MODE_BLOCKERS: tuple[str, ...] = ()
```

The Phase 1389b runtime tests confirm produced verifier decisions carry:

```text
public_mode_blockers=[]
```

## 6. Claim Enumeration Results

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1389 prompt validates | `docs/antigravity_tasks/antigravity_prompt__phase_1389_g8_public_claimability_activation_gate.md`; `tools/validate_phase_prompt.py` | confirmed |
| CDL-088 is ratified and provides public claimability authority | CDL-088 row; Phase 1376 evidence; Phase 1389a governance disposition | confirmed |
| ADR-0038 is accepted | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed |
| CDL-090 is ratified | CDL-090 row; Phase 1373 evidence | confirmed |
| Replay/nullifier policy and runtime registry are active | Phase 1377 policy; `ilc_core/sidecars/claim_nullifier_registry_v1.py`; Phase 1389b tests | confirmed |
| Duplicate-claim registry is active | `ClaimNullifierRegistry.reserve_claim(...)`; Phase 1389b tests | confirmed |
| Legacy `/v1/public/*` routes are removed | `ilc_core/server.py`; Phase 1378 tests and walkthrough | confirmed |
| Phase 1388 counsel/value-path prerequisite is closed | `docs/specs/ilc_counsel_clearance_1388_v0.1.md` | confirmed |
| Public economics cannot be constructed from private visibility | Phase 1387a matrix/firewall docs and runtime guard | confirmed |
| Verifier public-mode blockers are empty | `_PUBLIC_MODE_BLOCKERS: tuple[str, ...] = ()` | confirmed |

## 7. Non-Authorizations

This rerun records the Phase 1389 gate verdict. It does not:

- add or start a public HTTP server;
- add or start a public verifier API route;
- add or start a public claim endpoint route;
- publish public RC artifacts;
- publish source code or packages;
- sign release artifacts;
- perform wallet withdrawal, wallet transfer, wallet spend, or wallet signing;
- mint ECU;
- settle ILC;
- launch mainnet;
- mutate the CDL register;
- claim external legal advice;
- claim counsel approval by external counsel;
- record a legal conclusion.

## 8. Next Phase

Phase 1390 window closure is now the next main-lane Window 1369-1390 action.

## 9. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md -> public-claimability/activation-gate
```
