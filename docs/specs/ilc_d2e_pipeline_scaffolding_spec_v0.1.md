# ILC D2e Pipeline Scaffolding Specification v0.1

Status: Non-ratified planning specification
Date: 2026-02-20
Primary anchor: `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
Related anchors:
- `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`

## 1. Purpose and scope

This specification defines the scaffolding for D2e (Agent SDK and CLI lane) so downstream implementation phases can proceed with a stable documentation contract. It constrains D2e pipeline structure and ordering without introducing runtime code.

## 2. Layer mapping

D2e maps to Layer 3 protocol operations and developer-facing interfaces established by ADM-001 and ADM-002.

| Pipeline surface | Layer alignment | Source anchor |
| --- | --- | --- |
| CLI protocol commands | Layer 3 (wire operations via CLI contract) | `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md` |
| Output schema contracts | Layer 0/3 boundary contract surface | `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md` |
| Identity and signing entry points | Layer 3 operation boundary | `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md` |

## 3. Pipeline stage definitions

D2e scaffolding stages:

1. **Stage S1 - Surface lock**
   - Fix CLI command families and JSON I/O contract.
   - Produce command-surface and output-schema references.
2. **Stage S2 - Runtime skeleton planning**
   - Define subsystem scaffolds for identity, query, verify, bundle, epoch, and balance flows.
   - Bind subsystem interfaces to documented JSON schemas.
3. **Stage S3 - Integration harness planning**
   - Define end-to-end command sequence coverage and failure-path expectations.
   - Define documentation/help output packaging expectations.

## 4. Pre-conditions and ordering constraints

- D2e work must remain aligned with `D2d -> D2e -> D3` ordering from roadmap v0.3.
- D2 schema prerequisites from Phase 245 remain blocking for D2e-03 and later runtime tasks.
- D2e scaffolding must preserve CLI-first contract stability before any adapter-specific work.
- No D2e stage may assume D3 skill publication artifacts are complete.

## 5. Explicit deferred boundaries

The following scopes are explicitly deferred outside D2e scaffolding:

- **D3 deferred scope:** OpenClaw skill packaging/publication, multi-agent orchestration configuration, and operational skill delivery.
- **D4 deferred scope:** Rust kernel and WASM interfaces.
- **D5 deferred scope:** Python retirement and alternate runtime migration.

This document does not collapse D2e responsibilities into D3, D4, or D5 lanes.

## 6. Carry-forward and non-goal statement

Carry-forward:
- Use this spec as the D2e scaffolding reference for later implementation prompts.
- Keep references synchronized with ADM-001 v0.2 and roadmap v0.3.

Non-goals:
- No `ilc_core/` runtime implementation.
- No CDL ratification or status mutation.
- No policy constant selection.
