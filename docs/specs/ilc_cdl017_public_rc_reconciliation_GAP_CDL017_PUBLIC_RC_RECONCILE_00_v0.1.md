# ILC CDL-017 Public-RC Reconciliation

**Phase:** GAP-CDL017-PUBLIC-RC-RECONCILE-00  
**Date:** 2026-08-21  
**Sensitivity:** NON-SENSITIVE  
**Disposition:** PASS WITH IMPLEMENTATION-DELTA REQUIRED

## Purpose

This phase reconciles the public-RC CDL-017 validator-agent launch claims against the actual repository state after GAP-CDL017-PRELOCK-VERIFY-00. It does not reopen or ratify CDL-017. CDL-017 is already ratified at Phase 765.

## Output Tokens

- `cdl017_public_rc_reconciliation_complete_GAP_CDL017_PUBLIC_RC_RECONCILE_00`
- `cdl017_no_duplicate_open_ratify_required_GAP_CDL017_PUBLIC_RC_RECONCILE_00`
- `cdl017_public_rc_impl_delta_required_GAP_CDL017_PUBLIC_RC_RECONCILE_00`

## Direct-Read Inputs

| Artifact | Finding |
|---|---|
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-017 is `ratified`; row records `ratified_phase: 765`. |
| `docs/specs/ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md` | Ratified validator-governance framework while preserving the first non-Genesis validator deployment human gate. |
| `ilc_consensus/src/validator.rs` | Rust `ValidatorSet::admit_validator` and `ValidatorSet::eject_validator` are implemented, not placeholders. |
| `ilc_core/validator/admission_ejection_runtime.py` | Python runtime exposes `ValidatorRoleRecord`, `build_validator_role_record()`, and guarded `admit_validator()` / `eject_validator()` decisions under CDL-017. |
| `ilc_core/validator/validator_eligibility_certificate.py` | `ValidatorEligibilityCertificate` and `GenesisBootstrapAuthorityCertificate` exist and are deterministic/frozen runtime artifacts. |
| `ilc_core/cli/main.py` | `identity init` is the current enrollment hook and has invite flags, but no `--no-validator` option. |
| `docs/research/ilc_validator_agent_identity_system_v0.1.md` | Design evidence calls for validators to be AgentID-linked and for `ValidatorKey` to be a derived sub-key with provable linkage. |
| `docs/specs/ilc_comprehensive_forward_plan_post_1575c_v0.1.md` | Current planning claims default-on candidate validator enrollment, `validator_participation_enabled = True`, and `ilc agent init --no-validator`; these are not implemented in `ilc_core/`. |

## Existing Runtime Coverage

| Surface | Status | Notes |
|---|---|---|
| CDL-017 constitutional authority | COMPLETE | Already ratified at Phase 765; no duplicate OPEN/RATIFY phase is authorized. |
| Rust validator-set hooks | COMPLETE | Phase 769 activated `admit_validator` / `eject_validator` membership transforms. |
| Python validator admission/ejection quote/runtime | COMPLETE, GUARDED | Phase 1353 runtime exists; Phase 1589 role-record surface exists; production activation remains token-gated. |
| Validator eligibility certificates | COMPLETE, GUARDED | Candidate/provisional/official verdict model and Genesis bootstrap certificate exist. |
| Validator endpoint identity binding | COMPLETE, SEPARATE LANE | CDL-105 endpoint assertions exist; launch freshness and provisioning remain operational concerns. |
| Topology shuffle constants | COMPLETE, GUARDED | CDL-068 runtime exists and records VRF threshold / k-degree / cluster constraints. |

## Public-RC Implementation Gaps

| Gap | Actual state | Public-RC consequence |
|---|---|---|
| Default-on candidate validator enrollment | No `validator_participation_enabled` runtime field found in `ilc_core/`. | New identity initialization will not automatically produce a candidate validator record. |
| Opt-out CLI | No `--no-validator` flag found in `ilc_core/cli/main.py`. | Planning claims an operator UX that does not exist. |
| First-class `ValidatorRegistration` model | Design doc names `ValidatorRegistration`; runtime currently uses `ValidatorRoleRecord`. | A public-RC implementation phase must either add `ValidatorRegistration` or explicitly bind `ValidatorRoleRecord` as the canonical registration artifact. |
| AgentID-linked validator sub-key derivation | Research/spec planning calls for a derived BLS sub-key with provable linkage; current runtime accepts a supplied `validator_key`. | Clean VPS provisioning cannot truthfully claim deterministic CDL-017 key derivation until a concrete derivation/proof path exists or the launch claim is downgraded to configured-key registration. |
| Enrollment-to-role-record write path | `identity init` does not write validator role/candidate records. | Candidate pool formation remains manual/off-path. |
| Rust `ValidatorID` structural migration | Rust still uses `ValidatorID(u32)` and `ValidatorKey`; Python can map u32 to AgentID, but Rust does not natively carry AgentID in the validator ID. | Acceptable for public RC only if the Python-layer mapping is explicitly the launch boundary; otherwise requires implementation before launch. |

## Re-Scoped Next Phase

The stale `GAP-CDL017-IMPL-00` row should be replaced or interpreted as:

**GAP-CDL017-IMPL-DELTA-00 — Validator-Agent Public-RC Implementation Delta**

Minimum scope:

1. Add a first-class public-RC validator registration artifact. Either implement `ValidatorRegistration` as a small wrapper over `ValidatorRoleRecord`, or explicitly ratify `ValidatorRoleRecord` as the canonical public-RC registration record in the implementation spec.
2. Add `validator_participation_enabled` to the concrete enrollment record path, defaulting to `True` for public-RC identity initialization.
3. Add an operator/user opt-out flag on the actual CLI surface that exists today. The current concrete surface is `ilc identity init`; if a new `ilc agent init` alias is introduced, both paths must be tested. The opt-out flag should map to the same internal field.
4. Make candidate validator registration zero-quorum-weight by construction.
5. Define the validator-key posture precisely:
   - If derived sub-key generation is implemented now, keep private-key handling out of Python unless an existing approved helper already handles it safely.
   - If derived sub-key generation is not implemented now, record a launch non-claim and use explicit configured validator keys with a provenance/proof placeholder that fails closed for Official promotion.
6. Preserve the first non-Genesis validator deployment human gate; candidate record creation must not activate BFT membership.

If this delta lands in `ilc_core/`, then `GAP-CDL017-PACKAGE-00a/00b` should produce and publish `ilc-core==0.3.1`. If the delta is deferred, the package rows should be skipped and the launch claims should be downgraded to the already-existing `0.3.0` runtime.

## Non-Claims

This phase does not open CDL-017, ratify CDL-017, amend any CDL, mutate `ilc_core/`, mutate `ilc_consensus/`, generate validator keys, provision VPS hosts, admit a non-Genesis validator, upload a package, regenerate the public mirror, push a public repository, transition epochs, or activate public RC.
