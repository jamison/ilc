# ILC Phase 1388 CDL-048 Activation and Counsel Clearance Record v0.1

**Phase:** 1388
**Date:** 2026-05-19
**Status:** COMPLETE
**Runtime commit:** `e96a629d`

```text
cdl_048_activated_phase_1388
counsel_clearance_public_verifier_api_phase_1388
first_live_value_path_activation_phase_1388
```

## 1. Purpose

This record closes the Phase 1388 rerun after Phase 1388a supplied the
Genesis-authority self-counsel clearance artifact for the narrow CDL-048
pre-production/testnet activation scope.

Phase 1388 activates the CDL-048 ECU-to-ILC conversion-path runtime gate. It
does not activate public claimability, public API serving, mainnet, public RC
publication, source publication, public distribution, or any external-party
conversion surface.

## 2. Prerequisites Confirmed

| Prerequisite | Evidence | Result |
|--------------|----------|--------|
| Phase 1387 hardening gate passed | `docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md` | confirmed |
| Phase 1387a accepted ADR/CDL coverage passed | `docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md` | confirmed |
| Phase 1387a public-only economics firewall passed | `docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md` | confirmed |
| Phase 1388a self-counsel clearance exists | `docs/specs/ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md` | confirmed |
| CDL-048 dry-run wire proof exists | `docs/phases/phase_1380_cdl_048_dry_run_wiring_walkthrough.md` | confirmed |

## 3. Runtime Gate Change

The runtime unlock is committed separately in `e96a629d`.

| Runtime path | Before Phase 1388 | After Phase 1388 |
|--------------|-------------------|------------------|
| `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py::build_cdl048_dry_run_wire_quote(..., activation_requested=True)` | raised `cdl_048_not_activated_phase_1380` | returns an activation-authorized quote |
| `gate_closed` | `true` | `false` |
| `quote_only` | `true` | `false` |
| `conversion_activation_authorized` | `false` | `true` |
| `ledger_write_authorized` | `false` | `true` |
| `wallet_write_authorized` | `false` | `true` |
| `public_claimability_activated` | `false` | `false` |

The default call path, `activation_requested=False`, remains the Phase 1380
gate-closed dry-run mode.

## 4. Counsel Clearance

Phase 1388 relies on:

```text
counsel_clearance_cdl_048_activation_phase_1388a
self_counsel_decision_not_external_legal_opinion_phase_1388a
```

This is Genesis-authority self-counsel clearance for the CDL-048
pre-production/testnet activation surface. It is not external legal advice, not
attorney sign-off, not a licensed-practitioner opinion, and not a public launch
clearance.

For Phase 1388 routing purposes, this satisfies the counsel-clearance
prerequisite represented by:

```text
counsel_clearance_public_verifier_api_phase_1388
```

That token records clearance of the Phase 1388 activation prerequisite only. It
does not activate a public verifier API or create a public claimability result.

## 5. Phase 1389 Boundary

Phase 1389 remains separate and SENSITIVE. It still requires explicit
`GO Phase 1389`.

This record does not produce:

```text
result=public_claimability_activated
```

## 6. Non-Authorization

Phase 1388 does not mutate the CDL register, activate public claimability,
publish public RC artifacts, publish source, sign a release, invite external
users, activate mainnet, activate public API serving, authorize a public token
offering, record external legal advice, or record an attorney opinion.

## 7. Graph Delta

`graph_delta=load_bearing_artifact_changed:ilc_core/ledger/cdl048_conversion_sweeper_runtime.py -> value-path/activation-gate`
