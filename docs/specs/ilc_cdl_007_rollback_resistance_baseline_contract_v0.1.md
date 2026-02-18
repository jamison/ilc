# ILC CDL-007 Rollback Resistance Baseline Contract v0.1

Status: Phase-227 remediation contract (decision remains open)
Date: 2026-02-18
Related decision: `CDL-007`
Related artifacts:
- `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 1. Blocker statement

Phase-226 rubric verdict for `CDL-007` is `genesis_blocker` because incomplete rollback supersession/clawback baseline leaves exploitable state-corruption risk.

## 2. Remediation boundary (locked in Phase 227)

`CDL-007` remediation is bounded to a deterministic rollback baseline contract with four required elements:

1. **Supersession event contract**
   - rollback must be represented as explicit superseding commit metadata
   - required token: `finalization_state=rolled_back`
2. **Clawback declaration contract**
   - rollback event must declare reward treatment via explicit policy token
   - required values: `clawback_required` or `clawback_not_required`
3. **Conflict rejection contract**
   - conflicting supersession chains for the same target window are invalid
   - replay/reapplication of supersession identifiers is invalid
4. **Channel-to-protocol alignment contract**
   - existing channel-level protections must remain aligned with the protocol-level baseline semantics

## 3. Deterministic acceptance checks

This remediation contract is accepted only if all checks are true:

1. This artifact includes all baseline elements and required tokens in Section 2.
2. The remediation package artifact (`docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md`) includes a `CDL-007` section with required boundary/check/defer/risk fields and bounded token.
3. Decision-log Phase-227 remediation notes explicitly reference this contract while keeping `CDL-007` status `open`.
4. Phase-227 gate/tests validate artifact presence and required tokens.

## 4. Deferred implementation list (explicit)

Deferred beyond this docs-contract phase:
- full protocol-level rollback orchestration runtime hooks,
- negative-path replay/supersession runtime enforcement beyond existing targeted channel checks,
- production clawback settlement runner integration.

## 5. Residual risk after bounded mitigation

Until full protocol-level rollback enforcement is runtime-wired, rollback integrity is governed by explicit baseline contracts and partial channel protections, not complete protocol automation.

## 6. Bounded status for Genesis packaging

bounded_for_genesis_packaging: yes

