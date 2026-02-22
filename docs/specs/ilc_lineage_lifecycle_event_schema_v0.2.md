# ILC Lineage Lifecycle Event Schema v0.2

Status: Successor schema artifact (Phase-262)
Date: 2026-02-22
Supersedes: `docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md`

## 1. Purpose and scope

This v0.2 successor preserves the v0.1 lineage lifecycle schema and adds explicit coordination guidance for external signing providers.

No state-transition pairs, event names, or canonical field contracts from v0.1 are changed by this revision.

## 2. Schema continuity with v0.1

Inherited without modification from v0.1:
- lifecycle events: `register`, `rotate`, `revoke`, `recover`,
- lifecycle states and allowed/disallowed transition matrix,
- event identity and replay assumptions,
- Phase-240 lock intent and Phase-232 Section 6.1 dependency link.

## 3. Lifecycle coordination with external signing providers

The signer-lineage registry is protocol-layer state and does not observe external wallet key-management events automatically.

Normative coordination rules:
- external provider key rotation requires explicit ILC `rotate` lifecycle event emission,
- external provider key compromise requires explicit ILC `revoke` lifecycle event emission,
- authority restoration after incident handling requires explicit ILC `recover` lifecycle event emission.

The registry is not a proxy for wallet provider custody systems.

## 4. Non-goals

This successor does not:
- alter v0.1 event schema field contracts,
- ratify new transition types,
- implement provider SDK logic,
- modify runtime behavior in `ilc_core`.

## 5. Canonical anchors

- `docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md`
- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `docs/specs/ilc_signing_provider_interface_262_v0.1.md`
- `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
