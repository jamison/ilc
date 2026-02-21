# ILC CLI Command Surface Lock 253 v0.1

Status: Normative lock (Phase 253 — D2e-01)
Date: 2026-02-21
Lane: D2e-01 CLI surface ratification
Sourced from: `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md`, `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`
CDL routing: `CDL-032` (ratified Phase 253)

## 1. Purpose and scope

This document is the normative D2e-01 CLI command surface lock for the ILC CLI. It defines:
- the seven protocol primitive commands and their roles,
- the eight operational commands and their roles,
- the JSON I/O contract,
- the exit-code semantics,
- the explicit `star.map` exclusion statement,
- the CapProof Gate-A invariants.

This lock is the implementation reference for D2e CLI development phases (D2e-02 through D2e-11). No command may be added, renamed, or removed from the locked surface without a new CDL superseding CDL-032.

---

## 2. Protocol primitive commands (seven — normative)

| Command | Role |
| --- | --- |
| `assert` | Create a protocol claim assertion. |
| `validate` | Submit protocol validation evidence for a claim. |
| `contradict` | Submit contradiction evidence against a prior claim. |
| `refute` | Submit a refutation proof for a disputed claim. |
| `revise` | Publish a revision to prior claim state. |
| `link` | Create typed claim-to-claim relationship edges. |
| `epoch` | Interact with epoch state and commitment lifecycle. |

All seven commands are SDK-owned and protocol-native. Implementations must preserve their semantics across D2e versions.

---

## 3. Operational commands (eight — normative)

| Command | Role |
| --- | --- |
| `query` | Retrieve protocol state, claim data, or node records. |
| `verify` | Verify claim validity, signatures, or bundle integrity. |
| `balance` | Query token balance and economic account state. |
| `identity` | Initialize, export, or inspect node identity credentials. |
| `bundle` | Produce, verify, or inspect protocol-native bundles. |
| `shard` | Interact with shard assignment and routing metadata. |
| `capproof` | Execute capability proof probes (Gate-A). |
| `config` | Manage SDK configuration and runtime settings. |

---

## 4. JSON I/O contract

The ILC CLI uses a JSON-first I/O contract:

- **Output**: Structured JSON on `stdout`. Every command produces a JSON object response.
- **Input**: Complex payloads accepted via `stdin` JSON or flag-specified JSON strings for simple payloads.
- **Errors**: Emitted on `stderr` as structured JSON error objects.
- **Determinism**: Error payloads have stable structure (error code, message, and context fields). Unstable or unstructured error output is prohibited.

---

## 5. Exit-code semantics

| Exit code | Meaning |
| --- | --- |
| `0` | Success. Command completed and output is valid. |
| `1` | Protocol or runtime error. The command failed due to a protocol violation or runtime condition. |
| `2` | Usage or argument error. The command was invoked with invalid arguments or missing required flags. |
| `3` | Network or transport error. The command failed due to connectivity or transport-layer failure. |

These exit codes are normative for all SDK commands across D2e phases.

---

## 6. Explicit star.map exclusion statement

`star.map` routing and cross-shard L2 behavior are explicitly excluded from the SDK contract and from this command surface lock.

No `star.map` command will be added to the SDK command surface in any D2e phase without a new CDL superseding CDL-032. `star.map` routing is deferred to Phase B/C and is not a Genesis SDK command.

---

## 7. CapProof Gate-A invariants

The `capproof` command is governed by two non-negotiable Gate-A invariants sourced from `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md` §3 and Phase-231 constraints:

1. **Fail-closed invariant**: A failed probe is a refusal, never a default pass. No capability proof probe may silently pass on failure.

2. **No-user-supplied-kernels invariant**: Probes measure actual host capability. User-supplied backend hints, overrides, or synthetic kernel injections are prohibited. Probes run against the actual execution environment.

The five CapProof probes (GEMM, Infer, Graph, Bandwidth, Determinism) are all governed by these invariants.

---

## 8. Deferred surfaces

The following are out of scope for this surface lock and for D2e-03+ implementation until explicitly unblocked by subsequent phases or CDLs:

- `star.map` routing (deferred per Section 6 above).
- Any additional commands beyond the fifteen locked in Sections 2 and 3.
- Orchestration, session continuity, multi-agent fleet coordination, and channel adapters (not SDK responsibilities per boundary contract).
- D2e-03+ runtime implementation (blocked on D2 schema baseline: D2-01, D2-02, D2-08 required per Phase 255 and Phase 257).

---

## 9. Implementation anchor chain

This command surface lock is derived from and must remain consistent with:

1. `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md` — ADM-002 CLI-first architecture decision.
2. `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md` — SDK boundary contract (Phase 234).
3. `docs/specs/ilc_d2e_activation_assessment_245_v0.1.md` — D2e activation readiness (Phase 245).
4. `docs/specs/ilc_d2e_pipeline_scaffolding_spec_v0.1.md` — D2e pipeline scaffolding (Phase 246).
5. `docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md` — CDL-032 ratification evidence (Phase 253).

Any change to the command surface or I/O contract requires a new CDL superseding CDL-032 with a corresponding evidence document.
