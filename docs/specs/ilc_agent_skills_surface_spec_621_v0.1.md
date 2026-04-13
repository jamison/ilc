# ILC Agent Skills Surface Spec 621 v0.1

Status: locked
Date: 2026-04-13
Phase: 621
Owner lane: G8 architectural planning

## 1. Authorization basis and scope

This phase publishes the Tier 1 and Tier 2 Agent Skills surface spec only. It
does not implement skill files, does not create a `skills/` directory, does not
mutate `ilc_core/`, and does not open any CDL.

Authorization basis:
- ADR-0024 (Proposed) is the planning design basis for the Tier 1 and Tier 2
  skill structure; it does not become accepted ADR law in this phase.
- The runtime authorization basis is the Phase 619 handoff token
  `agent_skills_deferred_to_post_619_window` together with the Phase 620
  sequence lock that explicitly opened this bounded planning lane.
- This artifact is spec-form only; implementation is a separate later action
  after this window.

Canonical path rule:
- root `skills/` is the canonical source path for shared skill definitions;
  `skills_root_directory_canonical_source_path`
- harness-specific discovery configuration may still be required
- no automatic native discovery across all tools is claimed here

Governance tokens:
- `agent_skills_surface_spec_621_locked`
- `tier_1_skills_invocation_contract_locked`
- `tier_2_skills_invocation_contract_locked`
- `cdl_033_extension_requirements_surfaced`
- `tier_3_skill_node_deferred_per_adr_0024`
- `agent_skills_spec_form_only_no_implementation`
- `skills_root_directory_canonical_source_path`

General invocation rule for this spec:
- canonical skill identifier = the directory name under `skills/`
- canonical source artifact = `skills/<skill-name>/SKILL.md`
- harnesses may expose the invocation as a slash command, command palette
  action, prompt attachment, or tool selection, but the contract here is the
  skill name plus required inputs plus the declared machine-legible output

## 2. Tier 1 workflow skills invocation contract

`tier_1_skills_invocation_contract_locked`

### `phase-validate`

- Invocation form: invoke `phase-validate` against
  `skills/phase-validate/SKILL.md` with `prompt_path`
- Required inputs:
  - `prompt_path` pointing to a phase prompt markdown file
- Expected output (human-readable):
  - `VALID` summary or a validation-failure summary with line references
- Machine-legible output format:
  ```json
  {"status": "valid|error", "file": "docs/antigravity_tasks/...", "errors": [{"line": 1, "message": "..."}]}
  ```
- Failure modes:
  - `prompt_missing`
  - `prompt_not_phase_prompt`
  - `validation_failed`
  - `validator_invocation_failed`

### `phase-commit`

- Invocation form: invoke `phase-commit` against
  `skills/phase-commit/SKILL.md` with `phase_number`, `main_commit_subject`,
  and `backfill_commit_subject`
- Required inputs:
  - `phase_number`
  - `main_commit_subject`
  - `backfill_commit_subject`
- Expected output (human-readable):
  - two-commit execution checklist with verification status and clean-worktree
    result
- Machine-legible output format:
  ```json
  {"main_commit": "sha-or-null", "backfill_commit": "sha-or-null", "clean": true, "checks": [{"name": "post_main_pytest", "status": "pass|fail"}]}
  ```
- Failure modes:
  - `phase_number_missing`
  - `main_commit_failed`
  - `backfill_commit_failed`
  - `dirty_worktree`
  - `path_set_mismatch`

### `run-canary`

- Invocation form: invoke `run-canary` against
  `skills/run-canary/SKILL.md` with no arguments
- Required inputs:
  - none
- Expected output (human-readable):
  - mutation canary verdict with per-probe pass/fail notes
- Machine-legible output format:
  ```json
  {"result": "pass|fail", "probes": [{"name": "probe_name", "status": "pass|fail", "details": "..."}]}
  ```
- Failure modes:
  - `canary_invocation_failed`
  - `probe_failure`
  - `target_mutation_detected`

### `cdl-status`

- Invocation form: invoke `cdl-status` against `skills/cdl-status/SKILL.md`
  with optional `status_filter`
- Required inputs:
  - optional `status_filter` in `ratified|open|reserved`
- Expected output (human-readable):
  - filtered table of CDL rows with status and phase
- Machine-legible output format:
  ```json
  [{"cdl": "CDL-033", "status": "ratified", "phase": "291"}]
  ```
- Failure modes:
  - `decision_log_missing`
  - `status_filter_invalid`
  - `decision_log_parse_failed`

### `selftest-audit`

- Invocation form: invoke `selftest-audit` against
  `skills/selftest-audit/SKILL.md` with `gate_test_path` or `all`
- Required inputs:
  - `gate_test_path` or literal `all`
- Expected output (human-readable):
  - per-gate selftest guard-chain audit summary
- Machine-legible output format:
  ```json
  {"gates": [{"path": "tests/test_phase_...", "selftest_guard_present": true, "env_var": "ILC_SELFTEST_GUARD"}]}
  ```
- Failure modes:
  - `target_test_missing`
  - `guard_missing`
  - `env_var_missing`
  - `audit_invocation_failed`

### `pre-flight-check`

- Invocation form: invoke `pre-flight-check` against
  `skills/pre-flight-check/SKILL.md` with no arguments
- Required inputs:
  - none
- Expected output (human-readable):
  - clean-state checklist covering `ilc_core/`, decision-log cleanliness, and
    CDL environment-variable state
- Machine-legible output format:
  ```json
  {"ilc_core_clean": true, "cdl_env_vars_unset": true, "decision_log_clean": true}
  ```
- Failure modes:
  - `ilc_core_dirty`
  - `decision_log_dirty`
  - `cdl_env_var_set`
  - `preflight_invocation_failed`

### `cdl-open`

- Invocation form: invoke `cdl-open` against `skills/cdl-open/SKILL.md` with
  `cdl_number` and `summary`
- Required inputs:
  - `cdl_number`
  - `summary`
- Expected output (human-readable):
  - one additive-only CDL opening stub row for human review before any commit
- Machine-legible output format:
  - one pipe-delimited CDL row string suitable for insertion into
    `docs/specs/ilc_constitutional_decision_log_v0.1.md` after human review
- Failure modes:
  - `cdl_number_invalid`
  - `summary_missing`
  - `row_collision`
  - `format_generation_failed`

## 3. Tier 2 scaffold skills invocation contract

`tier_2_skills_invocation_contract_locked`

### `phase-test-scaffold`

- Invocation form: invoke `phase-test-scaffold` against
  `skills/phase-test-scaffold/SKILL.md`
- Required inputs:
  - `phase_number`
  - `deliverable_paths`
  - `main_subject_tokens`
  - `backfill_subject_tokens`
- Output (human-readable draft content for review):
  - draft phase test file content using the 7-test 5+2 structure
- Reference example paths:
  - `tests/test_phase_620_window_620_622_sequence_lock.py`
  - `tests/test_phase_616_public_receipt_schema_and_query_contract_spec.py`

### `cdl-evidence-scaffold`

- Invocation form: invoke `cdl-evidence-scaffold` against
  `skills/cdl-evidence-scaffold/SKILL.md`
- Required inputs:
  - `cdl_number`
  - `ratification_phase`
  - `section_structure`
- Output (human-readable draft content for review):
  - draft CDL ratification evidence artifact content
- Reference example paths:
  - `docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md`
  - `tests/test_cdl_033_ratification_291.py`

### `sim-doc-scaffold`

- Invocation form: invoke `sim-doc-scaffold` against
  `skills/sim-doc-scaffold/SKILL.md`
- Required inputs:
  - `sim_number`
  - `phase`
  - `subject`
- Output (human-readable draft content for review):
  - draft six-section SIM document content
- Reference example paths:
  - `docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md`
  - `tests/test_phase_542_sim_passive_ecu_01_attribution_formula.py`

### `gate-scaffold`

- Invocation form: invoke `gate-scaffold` against
  `skills/gate-scaffold/SKILL.md`
- Required inputs:
  - `phase_number`
  - `category_commands`
- Output (human-readable draft content for review):
  - draft closure gate shell script with six categories and selftest guard chain
- Reference example paths:
  - `tools/run_window_613_619_closure_gate_phase_619.sh`
  - `tests/test_phase_619_window_613_619_closure_gate.py`

### `coherence-scaffold`

- Invocation form: invoke `coherence-scaffold` against
  `skills/coherence-scaffold/SKILL.md`
- Required inputs:
  - `phase_number`
  - `window`
  - `verdict`
- Output (human-readable draft content for review):
  - draft coherence report and companion capsule section structure
- Reference example paths:
  - `docs/specs/ilc_window_613_619_coherence_report_618_v0.1.md`
  - `docs/specs/ilc_antigravity_context_capsule_v3.3.md`
  - `tests/test_phase_618_mvp_gate_synthesis_and_coherence_report.py`

## 4. CDL-033 extension requirements for ILC graph interaction

`cdl_033_extension_requirements_surfaced`

CDL-033, ratified in Phase 291, governs the OpenClaw skill publication contract
at the docs/policy boundary. Phase 468 later scoped the graph-operation
surfaces that exceed the CDL-033 baseline and therefore require extension work
before skills can directly submit to or query the ILC graph.

Surfaced verb classes from Phase 468:
- authored-envelope submission verbs
- refutation submission verbs
- novelty-check status query
- reuse-centrality query

Which Tier 1 and Tier 2 skills require these verbs at the Phase 621 spec level:
- none of the seven Tier 1 workflow skills require live graph-submission or
  graph-query verbs in their baseline contracts
- none of the five Tier 2 scaffold skills require live graph-submission or
  graph-query verbs in their baseline contracts
- the extension requirements are surfaced here because later graph-aware skills
  or later expanded skill contracts will need them

Surfaced extension requirements:
- authored-envelope submission requires typed request/response envelopes for
  skill-invoked graph contribution submission
- refutation submission requires typed request/response envelopes and malformed
  `refutation_criterion` error contracts
- novelty-check status query requires typed status-query request/response
  contracts
- reuse-centrality query requires typed query request/response contracts for
  reuse-centrality snapshots

No CDL is opened in this phase to address these requirements.
The forward pointer is explicit: the CDL-033 extension requirements from this
spec are input to a later CDL opening in a post-622 lane. This phase surfaces
requirements only; it does not ratify them, implement them, or claim them as
already opened law.

## 5. AG-gate assessment

| Gate | Assessment | Notes |
|---|---|---|
| AG-1 Co-flourishing mission | advance | Shared workflow skills reduce operational friction for both human reviewers and agent operators. |
| AG-2 W_e increase | advance | Tier 1 skills reduce re-discovery cost per session and make high-frequency repo workflows more repeatable. |
| AG-3 Epistemic integrity | neutral | This phase defines instruction contracts only and does not suppress refutation or mutate settled graph state. |
| AG-4 ECU-ILC separation | neutral | No payment surface, wallet write surface, or ECU/ILC conflation is introduced by this skills spec. |
| AG-5 Harness-agnostic | advance | root `skills/` is the canonical source path; harness-specific discovery configuration may still be required. |
| AG-6 Near-infinite scale | advance | Shared machine-legible skills reduce repeated onboarding cost across many agent sessions without introducing a central execution bottleneck. |
| AG-7 Machine-legible first | advance | Every Tier 1 contract declares a machine-legible output and keeps the surface CLI/file/JSON-first. |
| AG-8 Outbound economic loop | neutral | Phase 622 is the advancement phase for AG-8; this phase only prepares the skills layer that may later support it. |

No AG-gate row is a FAIL.

## 6. Deferred items and exclusions

- Tier 3 `skill_node` is deferred per ADR-0024 and requires Tier 1 operational
  use, CDL-053 evidence-track progress, and CDL-034 extension design before any
  later opening can be considered.
- Actual `skills/` directory creation and file writing is implementation and is
  not performed in this phase.
- CDL-033 extension CDL opening is surfaced here as a requirement only; any CDL
  opening occurs in a later lane.
- Benchmark protocol definition remains deferred as the Tier 3 prerequisite.
- External skill import from agentskills.io or community catalogs remains
  prohibited.
- No `ilc_core/` mutation, no ADR mutation, no CDL mutation, no wallet
  widening, and no Option-B selection claim occurs in this phase.
