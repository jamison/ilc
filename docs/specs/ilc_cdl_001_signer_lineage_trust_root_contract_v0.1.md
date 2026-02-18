# ILC CDL-001 Signer Lineage Trust-Root Contract v0.1

Status: Phase-227 remediation contract (decision remains open)
Date: 2026-02-18
Related decision: `CDL-001`
Related artifacts:
- `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 1. Blocker statement

Phase-226 rubric verdict for `CDL-001` is `genesis_blocker` because signer-lineage gaps create key/data loss and canonical authority ambiguity risk.

## 2. Remediation boundary (locked in Phase 227)

`CDL-001` remediation is bounded to a deterministic trust-root contract surface with four required elements:

1. **Signer hierarchy contract**
   - `canonical_root_key` (trust root)
   - `authority_recovery_key` (recovery control)
   - `operational_signer_key` (day-to-day signing)
2. **Lifecycle event contract**
   - required states: `active`, `rotated`, `revoked`, `recovered`
   - required transition events: `register`, `rotate`, `revoke`, `recover`
3. **Canonical authority linkage**
   - canonical signer acceptance must chain to an active trust root
   - revoked lineage must be rejected for canonical authority decisions
4. **Auditability contract**
   - every lineage transition must be represented as an append-only, replayable record

## 3. Deterministic acceptance checks

This remediation contract is accepted only if all checks are true:

1. This artifact includes all required hierarchy keys and lifecycle states listed in Section 2.
2. The remediation package artifact (`docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md`) includes a `CDL-001` section with:
   - remediation boundary,
   - deterministic checks,
   - deferred implementation list,
   - residual risk,
   - `bounded_for_genesis_packaging: yes|no` token.
3. Decision-log Phase-227 remediation notes explicitly reference this contract while keeping `CDL-001` status `open`.
4. Phase-227 gate/tests validate artifact presence and required tokens.

## 4. Deferred implementation list (explicit)

Deferred beyond this docs-contract phase:
- production key-registry schema migration and runtime validator enforcement,
- cryptographic key-material custody/rotation automation,
- distributed recovery quorum tooling and incident orchestration integration,
- hardware-backed signer controls.

## 5. Residual risk after bounded mitigation

Until runtime lineage enforcement ships, canonical signer misuse is mitigated by documented scope boundaries and explicit open-CDL status, not by full runtime prevention.

## 6. Bounded status for Genesis packaging

bounded_for_genesis_packaging: yes

