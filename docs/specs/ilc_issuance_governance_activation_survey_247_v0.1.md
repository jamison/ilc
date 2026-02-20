# ILC Issuance Governance Activation Survey 247 v0.1

Status: Non-ratified planning survey
Date: 2026-02-20
Window: Phase 247
Primary planning anchor: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`
Related runtime-sequence anchor: `docs/specs/ilc_security_runtime_implementation_sequence_240_249_v0.1.md`

## 1. Scope and window anchor

This survey evaluates activation readiness for issuance-governance queue items `CDL-025` through `CDL-031` after completion of the Phase 241-244 security runtime cluster. The survey is documentation-only and does not ratify decisions or set policy constants.

## 2. Per-CDL assessment (CDL-025 through CDL-031)

Assessment baseline source: `docs/specs/ilc_issuance_governance_plan_233_v0.1.md`

| CDL | Topic | Readiness snapshot | Hard prerequisite gates |
| --- | --- | --- | --- |
| `CDL-025` | terminal issuance model reconciliation | planning-ready | model-comparison evidence package and decision-lane prompt |
| `CDL-026` | `C_max` lock | blocked-on-ordering | `CDL-025` closure candidate defined and accepted for ratification lane |
| `CDL-027` | decay formulation and schedule | blocked-on-ordering | `CDL-026` cap lock draft and schedule simulation evidence |
| `CDL-028` | fee-burn split ratio | blocked-on-ordering | `CDL-025` terminal model decision candidate and payout-trace evidence |
| `CDL-029` | allocation split validation and lock | blocked-on-evidence | invariant and governor-compatibility evidence for allocation lane |
| `CDL-030` | ECU price clamp bounds | blocked-on-ordering | issuance schedule evidence from `CDL-027` and pricing simulation package |
| `CDL-031` | dynamic ranking multiplier policy | deferred-lane | `CDL-019` closure path and invariant migration evidence |

Runtime-constraint drift statement:
- **No constraint drift detected from Phase 241-244 runtime work for CDL-025 through CDL-031.**
- Security runtime changes in Phases 241-244 addressed signer lineage, key compromise response, and rollback resistance lanes only, with no new issuance-policy constraints introduced.

## 3. Dependency graph narrative

Current activation dependency narrative remains consistent with Phase 233:

1. `CDL-025` remains the terminal-model gateway for issuance flow.
2. `CDL-026` and `CDL-028` remain downstream of `CDL-025`.
3. `CDL-027` remains downstream of `CDL-026`.
4. `CDL-030` remains downstream of issuance schedule closure in `CDL-027`.
5. `CDL-031` remains downstream of `CDL-019` closure criteria.

No dependency-edge additions were required by the Phase 241-244 security-runtime outputs.

## 4. Non-goal boundaries

This survey does not:
- ratify `CDL-025` through `CDL-031`,
- set or propose issuance policy constants,
- mutate any CDL status field from `open`,
- change `ilc_core/` runtime behavior.

## 5. Forward pointer

Next integration step is to carry this readiness map into the Phase 248 coherence lane, then preserve final ordering and dependency handoff in the Phase 249 closure artifact.
