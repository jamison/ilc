# Window 1576-1584 Candidate Phase Grouping: Homoiconic Test Registry And Pytest Sidecar

Status: candidate window proposal.

Date: 2026-06-15

This window proposal defines when and how the homoiconic test registry and
pytest executor sidecar should be implemented after the current Block 6 route,
unless a later human-authorized plan explicitly pulls the work forward. It does
not open Window 1576-1584, does not execute any phase, does not activate public
RC, does not mutate Atlas canon, does not sign nodes, does not upload nodes,
does not activate runtime, does not activate economics, and does not mutate
ADR/CDL state.

This proposal does not open Window 1576-1584.

## 1. Window Objective

Move ILC testing from directory-first discovery toward graph-first discovery
without replacing `pytest` prematurely.

The target shape is:

1. the graph identifies test files and test functions;
2. the sidecar resolves graph test nodes into safe executor commands;
3. `pytest` executes those commands in a verified workspace;
4. the sidecar writes canonical evidence envelopes;
5. graph frontier reports use test evidence to identify validation gaps.

The initial implementation must support two practical modes:

- registry mode: query graph -> resolve existing local pytest node IDs -> run
  local pytest;
- graph-hydrated workspace mode: hydrate source/test nodes into a temporary
  verified workspace -> run pytest in that workspace -> emit evidence.

The native pytest collector/plugin mode is deferred until after these two modes
are stable.

## 2. Preconditions

Before this window opens, the project should have:

- Block 6 status resolved or explicitly paused by human decision;
- Phase 1545p-Fix32 contract complete;
- no unresolved contradiction between `docs/testing/test_inventory.md` and
  `tests/conftest.py` gating policy;
- current Atlas candidate artifacts available locally;
- explicit human authorization for this window if it is scheduled before the
  public-RC gate.

## 3. Phase Plan

### Phase 1576: Window sequence lock and contract reconciliation

Sensitivity: NON-SENSITIVE unless the active sequence-lock process requires
explicit human GO.

Scope:

- create the Window 1576-1584 sequence lock;
- direct-read Fix32 contract outputs and current Block 6 frontier docs;
- confirm this window is support/research until a later ADR/CDL route accepts
  any canonical protocol effect;
- define exact paths for registry artifacts, sidecar artifacts, evidence
  envelopes, and frontier reports.

Completion tokens:

- `window_1576_1584_homoiconic_test_registry_opened_phase_1576`
- `homoiconic_test_registry_contract_reconciled_phase_1576`
- `pytest_sidecar_mode_boundaries_recorded_phase_1576`
- `public_path_remains_blocked_phase_1576`

### Phase 1577: Test-file Atlas smoke audit

Sensitivity: NON-SENSITIVE.

Scope:

- implement `tools/check_test_graph_coverage.py` as a read-only diagnostic;
- use `out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json`
  as the preferred graph input when present;
- load Fix26/Fix27 queue artifacts as supplementary candidate-edge context;
- record `coverage_input_scope: lower_information_fallback` if the checker must
  fall back to a lower-information graph such as Fix22 alone;
- enumerate all `tests/**/*.py` files;
- map every test file to its Fix22/Fix26/Fix27 candidate node where possible;
- verify each test file node has test semantics or a classified gap;
- verify outgoing `TESTS` edges target existing nodes;
- verify expected authority traces only for test roles that require them
  instead of requiring `REFERENCES_AUTHORITY` for every test file;
- classify private, historical, expensive, live-network, and sensitive tests by
  executor gate;
- emit `out/test_graph_coverage_phase_1577.json` plus
  `docs/specs/ilc_test_graph_coverage_report_1577_v0.1.md`;
- add focused tests for deterministic output, gap classes, and report-first
  threshold behavior.

This phase does not execute tests and does not create canonical graph nodes.
The checker may expose `--enforce-threshold`, but the first Phase 1577 baseline
must be report-first unless a later prompt explicitly authorizes enforcement.

Completion tokens:

- `test_graph_coverage_checker_committed_phase_1577`
- `homoiconic_test_file_atlas_smoke_audit_committed_phase_1577`
- `test_graph_coverage_enriched_input_preferred_phase_1577`
- `test_file_candidate_node_mapping_recorded_phase_1577`
- `test_graph_gap_classes_recorded_phase_1577`
- `test_graph_coverage_threshold_report_only_phase_1577`
- `public_path_remains_blocked_phase_1577`

### Phase 1578: Pytest collection to function-node candidates

Sensitivity: NON-SENSITIVE.

Scope:

- run bounded `pytest --collect-only` under the default local profile;
- parse collection output into stable `pytest_nodeid` records;
- combine collection output with AST metadata;
- emit candidate `test_function` nodes and candidate edges;
- defer ambiguous coverage rather than inventing `TESTS` or `COVERS_SYMBOL`
  claims;
- preserve skip/marker/gate semantics from `tests/conftest.py` and
  `pyproject.toml`.

Completion tokens:

- `pytest_collection_function_node_candidates_committed_phase_1578`
- `pytest_nodeid_identity_grounded_phase_1578`
- `ast_only_identity_rejected_phase_1578`
- `public_path_remains_blocked_phase_1578`

### Phase 1579: Registry-mode pytest sidecar scaffold

Sensitivity: NON-SENSITIVE.

Scope:

- implement a local-only sidecar command that accepts graph node selectors;
- query the local Atlas/LMDB projection or JSON candidate artifacts;
- resolve selected test nodes to `pytest <path>::<nodeid>` commands;
- enforce executor profile gates before execution;
- support dry-run mode that prints commands without running tests;
- fail closed on missing source files, unknown profiles, private gates, or
  dangling test targets.

This is the first usable sidecar mode. It still runs against the local repo
checkout.

Completion tokens:

- `pytest_sidecar_registry_mode_scaffold_committed_phase_1579`
- `graph_resolved_pytest_commands_recorded_phase_1579`
- `pytest_sidecar_gate_enforcement_recorded_phase_1579`
- `public_path_remains_blocked_phase_1579`

### Phase 1580: Canonical test evidence envelope rehearsal

Sensitivity: NON-SENSITIVE unless an authorized live/VPS profile is selected.

Scope:

- run a bounded selected set of default-safe graph-resolved tests;
- emit deterministic `test_evidence_run` envelopes;
- include command, source-tree digest, input-graph digest, environment digest,
  stdout/stderr digests, result status, and non-claim fields;
- use canonical JSON with sorted keys and `allow_nan=False`;
- do not execute private, live-network, historical, expensive, or sensitive
  selftest profiles unless explicitly selected.

Completion tokens:

- `canonical_test_evidence_envelope_rehearsed_phase_1580`
- `graph_resolved_pytest_evidence_recorded_phase_1580`
- `test_evidence_no_authority_overclaim_phase_1580`
- `public_path_remains_blocked_phase_1580`

### Phase 1581: Graph-hydrated workspace mode

Sensitivity: NON-SENSITIVE for local candidate hydration only.

Scope:

- hydrate a bounded source/test dependency slice into a temporary workspace;
- verify every hydrated file against graph/source-tree digests;
- run pytest only inside that temporary workspace;
- emit the same evidence-envelope format from Phase 1580;
- clean up or archive the workspace according to explicit policy;
- record limitations for imports, package layout, fixtures, compiled
  dependencies, and private material.

This phase proves the graph can become the source of execution material while
`pytest` remains the executor.

Completion tokens:

- `pytest_sidecar_graph_hydrated_workspace_committed_phase_1581`
- `hydrated_workspace_digest_verification_recorded_phase_1581`
- `pytest_sidecar_hydration_limits_recorded_phase_1581`
- `public_path_remains_blocked_phase_1581`

### Phase 1582: Graph-derived test frontier report

Sensitivity: NON-SENSITIVE.

Scope:

- identify runtime/source nodes without test coverage;
- identify test nodes with missing, dangling, private, stale, or superseded
  targets;
- identify authority/spec nodes without validation evidence;
- compare graph-derived findings with `docs/testing/test_inventory.md`,
  `docs/phases/STATUS.md`, and `docs/PLANNING_INDEX.md`;
- produce prioritized gaps and route them to later prompts.

Completion tokens:

- `graph_derived_test_frontier_report_committed_phase_1582`
- `test_coverage_gap_classes_recorded_phase_1582`
- `stale_test_nodes_routed_phase_1582`
- `public_path_remains_blocked_phase_1582`

### Phase 1583: Multi-agent rehearsal profile planning

Sensitivity: SENSITIVE if it schedules live VPS, private key, wallet, or
networked execution.

Scope:

- define executor profiles for local-only, private-VPS, OpenClaw/harness,
  public-candidate, historical, and expensive suites;
- specify which profiles are allowed before public RC;
- define signature expectations for evidence produced by different agents;
- define how agent-produced evidence enters the graph without granting
  authority by default.

Completion tokens:

- `multi_agent_test_evidence_profile_plan_committed_phase_1583`
- `pytest_sidecar_agent_signature_boundary_recorded_phase_1583`
- `test_evidence_not_governance_authority_phase_1583`
- `public_path_remains_blocked_phase_1583`

### Phase 1584: Window coherence and handoff

Sensitivity: NON-SENSITIVE unless the handoff requests activation or public
execution.

Scope:

- verify all Window 1576-1584 outputs;
- confirm no public activation, signing, graph publication, economic effect, or
  governance mutation occurred;
- decide whether the registry remains support-only, requires an ADR, or requires
  a CDL before any protocol-level effect;
- produce handoff to the next public-RC or post-RC window.

Completion tokens:

- `window_1576_1584_homoiconic_test_registry_closed_phase_1584`
- `pytest_sidecar_registry_and_hydration_modes_rehearsed_phase_1584`
- `homoiconic_test_registry_governance_route_recorded_phase_1584`
- `public_path_remains_blocked_phase_1584`

## 4. Roadmap Waypoints

Waypoint A: file-level graph readiness.

- Done when every test file is mapped to a graph candidate node or documented
  exclusion, and `tools/check_test_graph_coverage.py` records a deterministic
  report-first baseline with gap classes.

Waypoint B: function-level graph readiness.

- Done when `pytest --collect-only` produces deterministic function-node
  candidates with profile/gate metadata.

Waypoint C: registry-mode sidecar.

- Done when a graph query can produce a safe local pytest command and evidence
  envelope.

Waypoint D: graph-hydrated sidecar.

- Done when a bounded graph slice can hydrate a temporary workspace and run
  pytest with digest verification.

Waypoint E: test frontier.

- Done when graph queries identify missing coverage, stale tests, and evidence
  gaps better than filesystem grep alone.

## 5. Governance Boundary

An ADR is required before this becomes canonical protocol architecture for test
discovery or evidence. A CDL is required only if test evidence gains governance
effect, public economic weight, eligibility, claimability, rewards, or
constitutional authority.

## 6. Non-Claims

This proposal does not claim:

- public RC activation;
- Genesis signing;
- graph node upload;
- canonical Atlas mutation;
- public graph publication;
- replacement of `pytest`;
- public distributed execution;
- governance authority from tests;
- economic activation;
- ADR/CDL mutation.
