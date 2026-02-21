# ILC CDL-032 CLI-First SDK Ratification Evidence 253 v0.1

Status: Ratification evidence (Phase 253)
Date: 2026-02-21
Ratification lane: G8 Constitution Cluster A
CDL ratified: CDL-032
Ceremony protocol reference: `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md` §6
Phase 252 gate: PASS (prerequisite confirmed)

## 1. Scope

This document records the ratification evidence for `CDL-032` (CLI-first Agent SDK interface contract and command surface). CDL-032 is ratified in Phase 253 under the G8 Constitution Cluster A lane.

Boundary statement: No runtime implementation was introduced in this ratification phase. The sole outputs of Phase 253 are this evidence document, the D2e-01 CLI command surface lock, the CDL-032 decision-log row mutation, and associated tests.

---

## 2. CDL-032 evidence table

| Evidence field | Reference |
| --- | --- |
| Decision topic | CLI-first Agent SDK interface contract and command surface |
| Related ADM | ADM-002 |
| Chosen option | CLI-first (single CLI entry point) |
| ADM artifact | `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md` |
| Boundary contract | `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md` |
| D2e activation assessment | `docs/specs/ilc_d2e_activation_assessment_245_v0.1.md` |
| D2e pipeline scaffolding spec | `docs/specs/ilc_d2e_pipeline_scaffolding_spec_v0.1.md` |
| Phase 252 gate | `tools/run_phase_252_security_ratification_gate.py` — PASS |
| CLI command surface lock | `docs/specs/ilc_cli_command_surface_lock_253_v0.1.md` |
| Ratification tests | `tests/test_cdl_032_ratification_253.py` |
| Coherence check | `docs/specs/ilc_integration_coherence_report_248_v0.1.md` — CDL-032 referenced as open through Phase 248, confirmed no premature ratification |

### 2.1 Evidence chain details

**Source citation (promotion criterion 1):**
`CDL-032` was formalized in the decision log under the Phase-233 post-work queue-entry record and is grounded in ADM-002 (`docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md`). The decision is rooted in ADM-002, which establishes the CLI-first architecture decision for the ILC Agent SDK.

**Chosen option with rationale (promotion criterion 2):**
Option selected: CLI-first (single CLI entry point). Rationale: ADM-002 v0.2 establishes that `ilc` is the canonical user-facing protocol interface. Framework adapters wrap CLI semantics and do not redefine protocol behavior. The boundary contract (`ilc_sdk_boundary_contract_234_v0.1.md`) locks the protocol surface (primitives + operational commands) as SDK-owned and excludes orchestration, runtime, and `star.map` routing from the SDK contract.

**Concrete implementation impact (promotion criterion 3):**
- Seven protocol primitive commands are locked as the canonical SDK command surface.
- Eight operational commands are locked as the canonical SDK operational surface.
- JSON I/O contract (stdin/stdout JSON, stderr errors) and exit-code semantics (0/1/2/3) are normatively established.
- `star.map` routing is explicitly excluded from the SDK contract.
- CapProof Gate-A invariants (fail-closed, no user-supplied kernels) are normatively established.
- The D2e-01 CLI command surface lock (`ilc_cli_command_surface_lock_253_v0.1.md`) is the normative downstream artifact for D2e implementation phases.

**Verification artifact (promotion criterion 4):**
`tests/test_cdl_032_ratification_253.py` verifies: evidence document existence, CLI surface lock existence, CDL-032 ratified status, ratification metadata fields, all seven primitive commands present, `star.map` exclusion present, CDL-001/002/007 remain ratified, and CDL-019/025–031/033 remain open.

---

## 3. Formal ratification statement — CDL-032

`CDL-032` (CLI-first Agent SDK interface contract and command surface) is hereby ratified with the following evidence chain:

1. ADM-002 v0.2 (`ilc_adm_002_cli_first_agent_sdk_v0.2.md`) established the CLI-first architecture with the `ilc` CLI as the canonical user-facing protocol interface. It defines the seven protocol primitive commands and eight operational commands with a JSON-first I/O contract.

2. The SDK boundary contract (`ilc_sdk_boundary_contract_234_v0.1.md`, Phase 234) locked the boundary between SDK-owned protocol operations and external orchestration, including the CapProof Gate-A invariants and the explicit `star.map` exclusion.

3. The D2e activation assessment (`ilc_d2e_activation_assessment_245_v0.1.md`, Phase 245) confirmed D2e-01 (CLI surface ratification lane) is ready-for-spec and that CDL-032 queue handling was the blocking prerequisite for that lane.

4. The Phase-252 ratification gate (`run_phase_252_security_ratification_gate.py`) passed, confirming the security-CDL ratification chain is intact and the ratification environment is valid.

5. The D2e-01 CLI command surface lock (`ilc_cli_command_surface_lock_253_v0.1.md`) is published in this phase as the normative implementation reference for D2e CLI development.

6. All four CDL promotion criteria are satisfied: source citations present, chosen option with rationale recorded, concrete implementation impact documented, verification artifact created.

Chosen option: CLI-first (single CLI entry point)
Ratification basis: all four promotion criteria satisfied per decision-log §Promotion Rule.

---

## 4. Non-goal boundary statement

This ratification phase does not:
- ratify CDL-033 (OpenClaw skill specification and ClawHub publication contract),
- ratify any issuance CDL (CDL-025 through CDL-031),
- implement D2e runtime code in `ilc_core/`,
- modify ADM-002, the boundary contract, or any contract source artifact,
- change CDL-001/002/007 ratified status (remain ratified from Phase 251).
