# ILC Gap 14 Package Profile CI Audit 1251 v0.1

- Version: `gap14_package_ci_gate_phase_1251.v0.1`
- Status: `pass`
- Package size token: `public_package_size_audit_recorded_phase_1251`
- Profile contract version: `public_rc_package_profiles_1243.v0.1`

## Required Tokens

- `gap14_package_ci_gate_phase_1251.v0.1`
- `public_package_size_audit_recorded_phase_1251`
- `phase_1251_gap14_package_ci_profile_audit_complete`

## Selected Profiles

| Profile | Status | Files | Bytes | Lines | Public P2P | Public claimability | Public RC claimed |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `openclaw_skill_local` | `pass` | 93 | 667393 | 19066 | `False` | `False` | `False` |
| `openclaw_skill_claimable` | `pass` | 96 | 691589 | 19736 | `False` | `True` | `False` |

## Surface Measurements

| Profile | Surface | Boundary status | Files | Bytes | Lines |
| --- | --- | --- | ---: | ---: | ---: |
| `openclaw_skill_local` | `ilc_cli` | `pass` | 25 | 174260 | 5131 |
| `openclaw_skill_local` | `ilc_harness_adapters` | `pass` | 7 | 121830 | 3186 |
| `openclaw_skill_local` | `ilc_logic` | `pass` | 61 | 371303 | 10749 |
| `openclaw_skill_local` | `local_sidecar` | `measurement_only` | 2 | 36388 | 1069 |
| `openclaw_skill_claimable` | `ilc_cli` | `pass` | 25 | 174260 | 5131 |
| `openclaw_skill_claimable` | `ilc_harness_adapters` | `pass` | 7 | 121830 | 3186 |
| `openclaw_skill_claimable` | `ilc_logic` | `pass` | 61 | 371303 | 10749 |
| `openclaw_skill_claimable` | `local_sidecar` | `measurement_only` | 2 | 36388 | 1069 |
| `openclaw_skill_claimable` | `public_claimability` | `measurement_only` | 6 | 46139 | 1233 |

## Phase 1250 Fix1 Scope Preservation

Phase 1251 consumes only `RCGAP-1250-FIX1-001` as package-focus confirmation.
The non-package findings remain routed as follows:

- `phase_1252`: `RCGAP-1250-FIX1-003`, `RCGAP-1250-FIX1-006`; status `carried_forward`; token `phase_1252_digest_truncation_security_binding_classification_recorded`
- `phase_1253`: `RCGAP-1250-FIX1-004`, `RCGAP-1250-FIX1-005`; status `carried_forward`; token `phase_1253_transport_digest_and_rust_m5_disposition_recorded`
- `phase_1254`: `RCGAP-1250-FIX1-002`; status `carried_forward`; token `phase_1254_legacy_graph_delta_gap_disposition_recorded`

## Non-Claims

- No package publication was performed.
- No public repository publication was performed.
- No public RC claim was made.
- No public claimability runtime was activated.
- No public P2P exposure was introduced.

