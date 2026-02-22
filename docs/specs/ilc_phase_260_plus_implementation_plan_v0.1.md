# ILC Phase 260+ Implementation Plan v0.1

Status: Proposed execution plan (Codex)
Date: 2026-02-22
Scope: Post-Phase-259 sequence opening

## 1. Purpose

Define a practical, dependency-correct implementation sequence for the Phase 260+ window that:
- preserves locked constraints from Phases 250-259,
- delivers D2e-03 CLI implementation without architectural drift,
- adds the ratification mutation-scope guardrail before any new ratification lane,
- stages issuance-governance ratifications using evidence-first ordering.

This plan supersedes ad hoc sequencing proposals that conflict with existing locks or currently available evidence.

## 2. Hard constraints inherited from existing canon

1. Command surface remains locked by `CDL-032` and `docs/specs/ilc_cli_command_surface_lock_253_v0.1.md`.
2. D2e-03 remains JSON-first with explicit DAG-CBOR deferral per `docs/specs/ilc_d2e_03_readiness_assessment_257_v0.1.md`.
3. Before any 260+ ratification phase, a reusable mutation-scope test guard must exist (Phase-259 handoff requirement).
4. Signing-provider interface specification is a pre-D2e-07 planning dependency, not a D2e-02 blocker.
5. Issuance CDLs (`CDL-025` through `CDL-031`) are not equally ready; ordering must follow Phase-256 readiness and dependency map.

## 3. Corrections to the Gemini draft plan

1. Do not start with a generic ilc_core bug-fix batch as the default Phase-260 opener. Most cited items are already resolved; the remaining behavioral item (`Agent.refute_node`) can be handled in a small, targeted quality lane later.
2. Do not introduce parallel CLI architecture (`ilc_cli/*`). Use existing `ilc_core/cli` and update `pyproject.toml` entry points in-place.
3. Do not run issuance ratifications before the mutation-scope guardrail fixture lands.
4. Do not use broad "run one test then mutate decision log" ratification flow. Use the Phase-250 ceremony protocol with per-CDL evidence artifacts, scoped field mutation checks, and sensitive GO gates.
5. Keep naming aligned with locked command surface (`assert`, not `assert_truth` or aliases).

## 4. Recommended sequence (260-269)

| Phase | Lane | Sensitivity | Objective | Primary outputs |
| --- | --- | --- | --- | --- |
| 260 | Sequence lock | non-sensitive | Lock 260-269 dependencies, gates, and sensitivity map | `ilc_phase_260_269_sequence_lock_v0.1.md`, tests |
| 261 | Test infrastructure | non-sensitive | Deliver reusable ratification mutation-scope guardrail | test utility + fixture + tests |
| 262 | Signing spec + doc amendments | non-sensitive | Publish signing-provider contract and wallet-agnostic amendments | signing spec, schema v0.2, SDK/ADM edits |
| 263 | D2e-03 contract lock | non-sensitive | Lock runtime boundary and acceptance contract for CLI prototype | D2e-03 contract doc + tests |
| 264 | D2e-03 implementation | non-sensitive | Implement JSON-first CLI prototype on locked command surface | CLI runtime code + schema conformance tests |
| 265 | D2e-03 composed gate | non-sensitive | Add preflight gate for D2e-03 closure and handoff | gate script + gate tests + handoff |
| 266 | Issuance evidence closure A | non-sensitive | Close missing evidence for CDL-025 and CDL-029 + reconciliation notes | simulation/evidence bundle docs + tests |
| 267 | CDL-025 ratification | sensitive | Ratify terminal issuance model using ceremony protocol | ratification evidence + decision-log mutation |
| 268 | CDL-019 ratification | sensitive | Ratify multiplier-governance closure after migration evidence | ratification evidence + decision-log mutation |
| 269 | Ratification verification gate + handoff | sensitive | Compose verification over 267-268 and publish next queue | ratification gate script + handoff artifact |

## 5. Phase-by-phase implementation detail

### Phase 260 (non-sensitive): sequence lock
- Lock exact ordering and preconditions for 261-269.
- Explicitly declare sensitive phases (267, 268, 269).
- Include hard stop rule on verification failure.
- Include first-use acronym expansions in prompts and artifacts.

### Phase 261 (non-sensitive): mutation-scope guardrail fixture
- Add reusable utility that snapshots a CDL row pre-mutation and compares post-mutation fields.
- Allowed diff keys only: `status`, `ratified_phase`, `ratified_date`, `evidence_document`.
- Add negative tests for unauthorized mutations (for example, `current_candidate` drift).
- Add command-level pre-mutation grep checks as executable test helpers.

Implementation note:
- Avoid weak row matching logic (for example, zip-based row comparison that can hide added/deleted columns).
- Parse by explicit CDL ID and normalized column names.

### Phase 262 (non-sensitive): signing-provider specification
- Publish `ilc_signing_provider_interface_262_v0.1.md`.
- Add required privacy invariant: COSE `kid` must be opaque protocol identifier; must not expose raw key material.
- Apply deferred documentation amendments from `ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`:
  - `ilc_sdk_boundary_contract_234_v0.1.md` wording update,
  - `ilc_adm_002_cli_first_agent_sdk_v0.2.md` wording update,
  - `ilc_lineage_lifecycle_event_schema_v0.2.md` as successor doc (do not mutate locked v0.1).

### Phase 263 (non-sensitive): D2e-03 contract lock
- Formalize implementation boundary before code changes:
  - command names from Phase-253 lock,
  - output shape from Phase-254 schemas,
  - JSON-first local state,
  - DAG-CBOR explicitly deferred.
- Define acceptance tests and non-goals (no D2e-04+ scope creep).

### Phase 264 (non-sensitive): D2e-03 implementation
- Implement under `ilc_core/cli` only.
- Add/adjust `pyproject.toml` scripts in-place; do not create parallel package roots.
- Ensure deterministic JSON output and locked exit-code contract.
- Add conformance tests against Phase-254 output schemas and D2 minimal schemas.

### Phase 265 (non-sensitive): composed closure gate
- Add gate script with required CLI contract (`--dry-run`, `--help`, unknown-arg exit 2).
- Compose checks for D2e-03 tests, prior gate regressions, and no-ellipsis walkthrough guardrail.
- Publish handoff artifact for issuance ratification opening.

### Phase 266 (non-sensitive): issuance evidence closure A
- Produce missing evidence required by Phase-256 for next ratifications:
  - CDL-025 model comparison package with explicit sustainability analysis,
  - CDL-029 allocation validation report tied to `theta_hard = 1/20`,
  - explicit reconciliation artifact for 8% simulation framing vs issuance-share governor framing.
- This phase does not mutate the decision log.

### Phase 267 (sensitive): CDL-025 ratification
- Ratify terminal issuance model only if Phase-266 evidence passes acceptance tests.
- Use mutation-scope fixture from Phase-261.
- Decision-log edits must be limited to allowed ratification fields.

### Phase 268 (sensitive): CDL-019 ratification
- Ratify multiplier-governance closure only after migration/invariant evidence is complete.
- Keep dynamic ranking policy (`CDL-031`) deferred unless explicit closure criteria are met.

### Phase 269 (sensitive): ratification verification gate + handoff
- Add composed gate verifying:
  - Phase-267 and Phase-268 ratification tests,
  - mutation-scope checks,
  - no unintended CDL row drift,
  - pre-existing runtime security gates still pass.
- Publish handoff with updated recommended order for remaining issuance CDLs.

## 6. Recommended order for remaining issuance CDLs after Phase 269

After CDL-025 and CDL-019 are closed, recommended sequence is:
1. `CDL-029` (allocation split lock)
2. `CDL-026` (`C_max` lock)
3. `CDL-027` (decay formulation and constants)
4. `CDL-028` (fee-burn split)
5. `CDL-030` (price clamp bounds)
6. `CDL-031` (dynamic ranking policy, only after CDL-019 and explicit guardrails)

This order is consistent with Phase-233 dependency rules and Phase-256 readiness.

## 7. Verification baseline for every phase in this window

Minimum command set per phase prompt:
1. `python3 tools/validate_phase_prompt.py <prompt>`
2. phase-local focused tests (`python3 -m pytest ... -q`)
3. composed regression gate appropriate to lane
4. `python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q`

Stop-on-failure policy is mandatory:
- if any verification command exits non-zero, stop;
- do not write walkthrough completion;
- do not update `STATUS.md`;
- do not commit.

## 8. Source anchors

- `docs/specs/ilc_cdl_ratification_window_250_258_handoff_v0.1.md`
- `docs/specs/ilc_cdl_ratification_and_d2e_activation_sequence_250_259_v0.1.md`
- `docs/specs/ilc_d2e_03_readiness_assessment_257_v0.1.md`
- `docs/specs/ilc_issuance_parameter_analysis_256_v0.1.md`
- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/phases/review_methodology_refinement_opus_feedback_2026_02_21.md`
