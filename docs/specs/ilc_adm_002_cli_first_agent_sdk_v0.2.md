# ILC ADM-002: CLI-First Agent SDK v0.2

Status: Proposed (non-ratified planning artifact)
Date: 2026-02-20
CDL routing: `CDL-032`
Supersedes: `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.1.md`
Depends on:
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`

## 1. Decision

The ILC Agent SDK remains CLI-first: `ilc` is the canonical user-facing protocol interface. Framework adapters wrap CLI semantics and do not redefine protocol behavior.

## 2. Boundary alignment update (Phase 234)

This v0.2 revision incorporates the Phase-234 boundary contract:
- Protocol surface is contract-first and transport-agnostic.
- Orchestration/runtime surfaces are explicitly out of SDK contract scope.
- `star.map` routing remains deferred outside SDK boundary commitments.

Canonical boundary anchor:
`docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`

## 3. Command surface and I/O contract

Core command families remain unchanged from v0.1:
- protocol primitives (`assert`, `validate`, `contradict`, `refute`, `revise`, `link`, `epoch`),
- operational commands (`query`, `verify`, `balance`, `identity`, `bundle`, `shard`, `capproof`, `config`).

I/O contract remains JSON-first:
- input via flags/stdin JSON,
- output via structured JSON,
- deterministic error payloads and stable exit-code semantics.

## 4. D2e bootstrap scope

D2e work is staged by roadmap v0.3:
- D2e-01 and D2e-02 define ratified surface and output schema contracts,
- D2e-03+ implementation tasks remain dependency-gated by schema readiness and lane ordering.

Roadmap anchor:
`docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`

## 5. Security and operational constraints

- Signing provider credential handling must avoid unsafe transcript leakage.
- Economic actions must keep explicit user/agent confirmation boundaries.
- CLI contract stability takes precedence over backend implementation churn.

## 6. Non-goals

This ADM revision does not:
- ratify `CDL-032`,
- define cryptographic primitives or custody policy,
- implement D2e runtime tasks.

## 7. Forward pointer

Activation sequencing and blockers for D2e implementation are documented in:
`docs/specs/ilc_d2e_activation_assessment_245_v0.1.md`.
