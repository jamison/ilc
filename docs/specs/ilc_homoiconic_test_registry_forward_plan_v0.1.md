# ILC Homoiconic Test Registry Forward Plan

Status: planning-only forward spec.

Date: 2026-06-15

This document records the recovered June 2026 design thread about moving from
centralized filesystem-based `pytest` discovery toward graph-query-driven,
homoiconic test discovery and test evidence.

This document does not execute a phase, mutate the Atlas, authorize public RC,
authorize Genesis signing, upload nodes, activate runtime, activate economics,
or mutate ADR/CDL state.

## 1. Problem

During bootstrap, ILC can rely on conventional repo distribution and
conventional `pytest` execution:

- GitHub or package registry hosts the source tree.
- Local checkout contains `tests/`.
- `pytest` discovers tests by filesystem naming convention.
- CI or a local operator runs tests against the checked-out source tree.

That model is practical for public RC, but it is not the final homoiconic
model. If Genesis central hosting fades and the graph becomes the primary
artifact, tests must remain discoverable, executable, and useful without
depending on one central repository layout.

The target inversion is:

- filesystem model: `tests/` glob -> pytest collection -> test execution;
- homoiconic model: graph query -> validation set -> executor invocation ->
  signed/canonical evidence nodes.

`pytest` should remain an executor. It should not remain the only registry of
what tests exist, what they validate, or what evidence closes a work item.

## 2. Recovered Design Thread

The recovered Sonnet discussion proposed two levels:

1. File-level test nodes with `TESTS` edges.
   This is sufficient to answer questions like:
   "which test files validate `ilc_core/epoch/allocation_distributor_runtime.py`?"
   A runner can query those file nodes and invoke `pytest <file>`.

2. Function-level test nodes.
   For true homoiconic execution, each test function needs its own node carrying
   module path, function name, marks, executor profile, and typed coverage edges.
   A runner can resolve graph results into:
   `pytest <path>::<test_name>`.

That direction is correct, but incomplete. Function-level nodes need more than
AST identity. They need enough semantics to be safe and useful after the central
repo stops being the authoritative test index.

## 3. Required Test Node Semantics

Minimum file-level node fields:

- `node_id`
- `node_kind: "test_file"`
- `repo_path`
- `content_sha256`
- `public_rc_tier`
- `privacy_class`
- `executor_family: "pytest"`
- `default_collection_policy`
- `graph_trace_status`

Minimum function-level node fields:

- `node_id`
- `node_kind: "test_function"`
- `repo_path`
- `module_path`
- `function_name`
- `pytest_nodeid`
- `marks`
- `executor_family: "pytest"`
- `executor_profile`
- `expected_invariants`
- `covered_symbols`
- `covered_nodes`
- `fixture_dependencies`
- `environment_gates`
- `skip_policy`
- `sensitivity_class`
- `non_claim_boundaries`

Minimum evidence-result node fields:

- `node_id`
- `node_kind: "test_evidence_run"`
- `test_node_id`
- `executor_version`
- `command`
- `environment_digest`
- `input_graph_digest`
- `source_tree_digest`
- `result_status`
- `stdout_digest`
- `stderr_digest`
- `duration_class`
- `created_by_agent`
- `signature_status`

## 4. Edge Vocabulary

The graph should not use one overloaded edge type for all testing semantics.
Recommended edge roles:

- `TESTS`: test node validates a production module, symbol, ADR, CDL, spec, or
  graph node.
- `COVERS_SYMBOL`: test function covers a specific code symbol.
- `EVIDENCES`: test evidence node supports a claim, phase output, invariant, or
  closure record.
- `USES_FIXTURE`: test node depends on fixture or sample data.
- `REQUIRES_PROFILE`: test node requires an execution profile or environment
  gate.
- `SKIPPED_BY_DEFAULT_UNLESS`: test node is archival, expensive, sensitive, or
  otherwise opt-in.
- `PRODUCES_EVIDENCE`: test execution produces a canonical evidence node.
- `CLOSES`: passing evidence closes a specific obligation, phase condition, or
  work item.
- `REGRESSES`: failing evidence reopens or blocks a claim.
- `SUPERSEDES`: newer test node replaces an older snapshot or stale assertion.
- `DERIVED_FROM`: test node was extracted from a source file or generated from
  a prompt/phase artifact.

These roles are candidate roles until a later ADR or protocol contract accepts
them as canonical.

## 5. Current Pytest Policy Remains Valid

The current local execution policy remains:

- `pytest` is the practical executor.
- `tests/conftest.py` is the current machine policy for default collection.
- `docs/testing/test_inventory.md` is the human inventory for suite families.
- historical phase snapshots and expensive release-artifact proofs remain
  opt-in under explicit environment gates.

The homoiconic registry should build on this policy. It should not delete
`pytest`, flatten historical tests into default regressions, or pretend archival
tests are current runtime evidence.

## 6. Candidate Execution Plan

### Fix32 candidate: homoiconic test registry contract

Produce a planning/spec phase that defines:

- test node kinds;
- test evidence envelopes;
- edge roles;
- executor profile names;
- skip/opt-in semantics;
- public/private test tiering;
- graph query examples.

Output should be a spec and schema only. No runtime activation.

### Fix33 candidate: pytest-to-graph collector

Build a research-only collector that reads local `pytest --collect-only` output
and Python AST metadata, then emits candidate nodes:

- one node per test file;
- one node per collected test function;
- candidate `TESTS` / `COVERS_SYMBOL` edges where evidence is strong;
- deferred records where coverage cannot be inferred.

The collector must not promote edges to canonical Atlas authority. It emits a
candidate queue for review.

### Fix34 candidate: canonical test evidence envelope

Build a local runner wrapper that executes selected test nodes and emits
canonical JSON evidence records:

- deterministic key ordering;
- explicit command and source digest;
- result status;
- environment profile digest;
- no wall-clock protocol semantics;
- no public serving;
- no graph mutation.

### Fix35 candidate: graph-derived test frontier report

Query the Atlas/LMDB projection for:

- runtime nodes with no current test evidence;
- authority/spec nodes with no validation evidence;
- tests that point to missing or superseded targets;
- tests skipped by default without clear opt-in gate;
- stale tests asserting superseded phase state.

Compare this graph-derived frontier against `docs/testing/test_inventory.md`,
`docs/phases/STATUS.md`, and `docs/PLANNING_INDEX.md`.

### Candidate Window 1576-1584: pytest sidecar implementation

After the Fix32-Fix36 support lane or equivalent preparation, the proposed
implementation window is:

`docs/specs/ilc_window_1576_1584_homoiconic_test_registry_candidate_phase_grouping_v0.1.md`

This window separates the sidecar into registry mode and graph-hydrated
workspace mode:

- registry mode: graph query resolves existing local pytest node IDs and runs
  local pytest under explicit executor gates;
- graph-hydrated mode: graph/source-tree nodes hydrate a temporary verified
  workspace, then pytest executes inside that workspace;
- native pytest plugin mode is deferred until both modes are stable.

The window is a candidate proposal only. It does not supersede Block 6 and does
not authorize public RC, signing, graph upload, runtime activation, or
governance mutation.

## 7. Governance Boundary

ADR is needed if the homoiconic test registry becomes the canonical protocol
architecture for test discovery or test evidence.

CDL is needed only if test evidence grants any of the following:

- constitutional authority;
- governance effect;
- public economic weight;
- juror or validator eligibility;
- claimability;
- reward or credit.

Until then, this remains a planning and research lane.

## 8. Non-Claims

This plan does not claim:

- public RC activation;
- Genesis v0.4 or v0.5 signing;
- public graph publication;
- node upload;
- canonical Atlas mutation;
- test evidence authority;
- runtime activation;
- economic activation;
- ADR/CDL mutation;
- replacement of `pytest` as an executor.

## 9. Recommended Immediate Routing

Record this plan as a forward-planning artifact now.

Do not patch completed Fix27 execution records retroactively. Fix27 can remain a
rewrite-candidate phase. The homoiconic test registry should enter as a
successor planning lane after Fix31, or as a Block 6 support lane if public RC
testing requires it.

The next concrete prompt should be:

`Phase 1545p-Fix32: Homoiconic Test Registry Contract`

It should be NON-SENSITIVE, planning/spec-only, and should not mutate runtime,
Atlas canon, public path, signing state, or governance logs.

Implementation guidance:
`docs/specs/ilc_homoiconic_test_registry_implementation_guidance_v0.1.md`

Draft executable prompt:
`docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix32_g10_homoiconic_test_registry_contract.md`

Candidate phase window:
`docs/specs/ilc_window_1576_1584_homoiconic_test_registry_candidate_phase_grouping_v0.1.md`
