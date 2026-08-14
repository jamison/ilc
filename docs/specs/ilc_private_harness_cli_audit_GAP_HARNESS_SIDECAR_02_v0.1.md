# ILC Private Harness CLI Audit GAP-HARNESS-SIDECAR-02 v0.1

**Phase:** GAP-HARNESS-SIDECAR-02
**Date:** 2026-08-14
**Status:** committed audit
**Sensitivity:** NON-SENSITIVE

```text
agent_onboarding_guide_committed_GAP_HARNESS_SIDECAR_02
```

## 1. Scope

This audit inventories `ilc_core/harness/` as it exists before public RC. It is
an audit table, not a promotion decision. No runtime code, activation flag, CDL,
public mirror, or graph state is changed by this phase.

## 2. Harness Boundary

The harness package is explicitly marked `PUBLIC_RC_EXCLUDE`. Existing
architecture docs define the harness as an operator wrapper over stable
`ilc_core/` surfaces. It may help an agent operate ILC, but it must not become a
protocol correctness dependency or redefine admission, graph, settlement, or
identity law.

## 3. File Inventory

| File | Purpose | Activation guard | PUBLIC_RC_EXCLUDE scope | Promotion route |
|---|---|---|---|---|
| `ilc_core/harness/__init__.py` | Marks the private harness package and exports the package-level exclusion constant. | `PUBLIC_RC_EXCLUDE_PRIVATE_AGENTIC_HARNESS = True` | Yes | SENSITIVE public-harness promotion phase plus public package review. |
| `ilc_core/harness/co_attestation_receipt.py` | Builds and verifies local co-attestation receipts for private artifacts. | No separate activation flag; file-level `PUBLIC_RC_EXCLUDE`. | Yes | Receipt schema promotion, signature verification hardening, and public artifact boundary gate. |
| `ilc_core/harness/consent_gate.py` | Enforces deterministic local consent decisions before private capture-to-artifact transitions. | No separate activation flag; file-level `PUBLIC_RC_EXCLUDE`. | Yes | Public consent-policy CDL or sidecar authorization gate before network claims. |
| `ilc_core/harness/idle_capacity_scheduler.py` | Routes private provider token budget to deterministic maintenance task candidates. | `IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED = True` | Yes | SENSITIVE scheduler activation lane with anti-gaming, admission, and non-economic-claim tests. |
| `ilc_core/harness/local_immutable_store.py` | Stores private consent-approved harness artifacts as local immutable JSON entries. | `LOCAL_IMMUTABLE_STORE_NOT_PRODUCTION = True` | Yes | Separate public artifact-store authority; must not be confused with LMDB graph or settlement ledgers. |
| `ilc_core/harness/local_node_capture.py` | Builds deterministic local snapshots for private graph-shaped artifacts after consent. | No separate activation flag; `production_graph_write = False`; file-level `PUBLIC_RC_EXCLUDE`. | Yes | SENSITIVE graph-capture promotion and admission/readback lane. |
| `ilc_core/harness/maintenance_task_executor.py` | Executes deterministic private maintenance fixtures into query-response artifacts. | `MAINTENANCE_TASK_EXECUTOR_NOT_ACTIVATED = True` | Yes | SENSITIVE task-executor promotion with sandboxing, receipt, and audit trails. |
| `ilc_core/harness/provider_usage_adapter.py` | Tracks bounded local provider usage and quota signals for private scheduling. | `PROVIDER_USAGE_ADAPTER_NOT_PROTOCOL_TRUTH = True` | Yes | May remain private; any public promotion must preserve that quota signals are operational only. |

## 4. Promotion Risks

| Risk | Reason |
|---|---|
| Treating quota headers as protocol truth | Provider usage data is operational scheduling context, not economic proof or Werner input. |
| Treating local immutable store as a production ledger | The store is JSON-file-backed private evidence, not LMDB graph or settlement state. |
| Treating co-attestation receipts as public admission | Receipts are local fixtures until promoted by a separate sidecar/public artifact lane. |
| Treating scheduled maintenance as claimable work | Scheduler output is private fixture scheduling and does not activate maintenance-lottery rewards. |
| Treating local capture as public graph mutation | `LocalNodeSnapshot.production_graph_write` is fixed false. |

## 5. Current Verdict

`ilc_core/harness/` is present and internally bounded, but remains private
`PUBLIC_RC_EXCLUDE` infrastructure. It can inform onboarding and future sidecar
design. It cannot be cited as public RC runtime capability until later
promotion gates remove the exclusion and prove the public behavior.

## 6. Non-Claims

This audit does not promote the harness package, activate public serving,
activate scheduler economics, write graph state, write settlement state, mutate
CDLs, push a public mirror, or launch public RC.
