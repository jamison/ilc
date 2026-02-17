# ILC Genesis Readiness Remediation 996-1008 Handoff v0.1

## Status
Prepared in Phase 1009 as closure handoff for the remediation sequence defined in `docs/specs/ilc_genesis_readiness_audit_reconciliation_v0.1.md`.

## Scope covered

This handoff summarizes closure of remediation phases 996 through 1008:

- 996: Audit reconciliation and deterministic execution lock.
- 997: Root license closure.
- 998: Quickstart and README parity fixes.
- 999: CLI key-loader dedupe and narrowing.
- 1000: Silent exception diagnostic hardening.
- 1001: Server app-factory import side-effect reduction.
- 1002: NodeID dual-id contract foundation.
- 1003: NodeID runtime bridge acceptance.
- 1004: Canonical-default migration utility with compatibility fallback.
- 1005: Package hygiene root-orphan and archive surface lock.
- 1006: Config dependency policy lock (JSON default, YAML optional).
- 1007: Edge and link boundary contract clarification.
- 1008: Operator config documentation lock.

## Audit-claim closure map

| Audit claim ID | Phase(s) | Closure note |
|---|---|---|
| P0-2 (`LICENSE` missing) | 997 | Closed with root `LICENSE` and guard tests. |
| P1-5 (root orphan artifacts) | 1005 | Closed by moving legacy root artifacts and adding manifest guardrails. |
| P1-6 (`Z_Past_Chats` release-surface concern) | 1005 | Closed for distribution surface via `MANIFEST.in` prune and ignore policy; historical corpus retained in repository history path. |
| P1-7 (PyYAML optional divergence) | 1006 | Closed via JSON-default lock and explicit YAML fallback contracts. |
| P2-2 (governance config docs gap) | 1008 | Closed with `config/README.md` and documentation guard tests. |
| P2-5 (Edge/Link ambiguity) | 1007 | Closed via boundary contract spec and runtime/test enforcement. |

## Deterministic closure gate

Phase 1009 adds:

- `tools/check_genesis_readiness_remediation_closure_996_1008.sh`
- `tests/test_genesis_readiness_remediation_closure_gate_phase_1009.py`

The closure gate runs the consolidated remediation regression subset for phases 997-1008 and is intended to be rerun before release tags and major branch promotions.

## Residual notes

1. This handoff closes the mapped Genesis-readiness remediation claims only.
2. Broader main-track roadmap phases remain governed by `docs/ILC_Master_Development_Plan_v0.4.md`.
3. Historical corpus retention policy remains intentional for research traceability and is now separated from distributable packaging surface by manifest policy.
