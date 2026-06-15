# ILC Homoiconic Test Registry Implementation Guidance

Status: forward implementation guidance.

Date: 2026-06-15

This document turns the recovered homoiconic testing discussion into concrete
implementation routing. It is a planning artifact only. It does not mutate the
Atlas, execute tests, create canonical test evidence, sign nodes, publish nodes,
activate public RC, activate runtime, or mutate ADR/CDL state.

## 1. Design Position

ILC should not try to replace `pytest` before public RC. The correct near-term
architecture is:

- the graph becomes the registry of test identity, coverage, prerequisites,
  evidence, and frontier gaps;
- `pytest` remains one executor that can be invoked from graph-resolved node
  identities;
- test evidence becomes a deterministic artifact attached to test nodes rather
  than terminal-only output;
- graph-native test discovery is introduced in research/support phases before it
  becomes canonical protocol architecture.

The practical inversion is:

- current model: filesystem discovery -> pytest collection -> test execution;
- target model: graph query -> selected test nodes -> executor invocation ->
  canonical evidence envelope -> graph evidence node.

## 2. Required Pushback

The following constraints are mandatory for future prompts and implementations.

1. AST parsing alone is not sufficient. Python AST can find functions and some
   decorators, but pytest determines real node IDs, parametrization expansion,
   fixture resolution, skip semantics, and collection behavior. A collector must
   combine AST metadata with `pytest --collect-only` output.
2. Passing tests are evidence, not authority. A passing result can evidence a
   claim only under its declared scope. It does not grant governance authority,
   economic effect, validator eligibility, juror eligibility, claimability, or
   public activation.
3. Test nodes must survive pruning. Test file nodes and test function nodes need
   an explicit graph tier such as `tier_3_test_evidence` or equivalent, otherwise
   optimization passes can remove the very nodes needed to discover validation.
4. Private and environment-sensitive tests need gates. A graph-native runner
   must not blindly execute tests that require private fixtures, VPS state,
   operator secrets, live network access, expensive release artifacts, historical
   snapshot mode, or sensitive closure selftests.
5. Evidence envelopes must be canonical. Result records must use deterministic
   JSON with sorted keys, finite values only, stable command/profile fields, and
   content digests for source tree, input graph, stdout, and stderr.
6. Candidate Atlas nodes are not Genesis-signed until the signing gate. The
   current path-to-node mapping identifies test files as unsigned candidates.
   Future docs must not describe them as Genesis-signed until a signing phase
   actually signs them.

## 3. Node Model

Minimum `test_file` node:

```json
{
  "node_kind": "test_file",
  "repo_path": "tests/test_example.py",
  "content_sha256": "hex",
  "source_node_id": "repo:file:<path-hash>:<encoded-path>",
  "executor_family": "pytest",
  "collection_policy": "default | historical_phase_snapshot | expensive_release_artifact | sensitive_selftest | private_local | manual_only",
  "privacy_class": "public_candidate | private_local | public_rc_excluded",
  "signature_status": "unsigned_candidate | signed_source_tree_member | signed_atlas_node",
  "graph_trace_status": "candidate | trace_declared | trace_missing | rejected"
}
```

Minimum `test_function` node:

```json
{
  "node_kind": "test_function",
  "repo_path": "tests/test_example.py",
  "pytest_nodeid": "tests/test_example.py::test_case",
  "function_name": "test_case",
  "parametrization_id": null,
  "marks": [],
  "fixture_dependencies": [],
  "executor_profile_id": "pytest_default_local",
  "covered_symbols": [],
  "covered_nodes": [],
  "environment_gates": [],
  "sensitivity_class": "default | opt_in | private | live_network | expensive | historical",
  "non_claim_boundaries": []
}
```

Minimum `test_evidence_run` node:

```json
{
  "node_kind": "test_evidence_run",
  "test_node_id": "node id",
  "executor_family": "pytest",
  "executor_version": "string",
  "command": ["python", "-m", "pytest", "tests/test_example.py::test_case", "-q"],
  "executor_profile_id": "pytest_default_local",
  "source_tree_digest": "hex",
  "input_graph_digest": "hex",
  "environment_digest": "hex",
  "result_status": "passed | failed | skipped | error | xfailed | xpassed",
  "stdout_digest": "hex",
  "stderr_digest": "hex",
  "duration_class": "bounded_short | bounded_medium | expensive",
  "created_by_agent": "agent id or local operator",
  "signature_status": "unsigned_local | signed_local | signed_public"
}
```

## 4. Edge Model

Use role-specific edges. Do not overload `TESTS`.

- `SOURCE_TREE_MEMBER`: file node belongs to the signed or candidate source-tree
  manifest.
- `DERIVED_FROM`: test function node derives from a test file node.
- `TESTS`: test node validates a module, spec, ADR, CDL, graph node, or claim.
- `COVERS_SYMBOL`: function-level test covers a specific runtime symbol.
- `USES_FIXTURE`: test depends on a fixture, data file, or harness.
- `REQUIRES_PROFILE`: test requires an executor profile or environment gate.
- `SKIPPED_BY_DEFAULT_UNLESS`: test is opt-in by policy.
- `PRODUCES_EVIDENCE`: execution produces a result envelope.
- `EVIDENCES`: evidence node supports a claim, invariant, phase condition, or
  closure record.
- `CLOSES`: evidence closes a work item under a declared scope.
- `REGRESSES`: evidence reopens or blocks a claim.
- `SUPERSEDES`: newer test/evidence replaces a stale node.

## 5. Implementation Route

### Phase 1545p-Fix32: contract

Define the formal contract, schema, non-claims, smoke-check requirements, and
future phase routing. No collector, executor wrapper, canonical graph mutation,
or signing.

### Phase 1545p-Fix33: test-node Atlas smoke audit

Build a research-only audit runner that:

- enumerates all local `tests/**/*.py` files;
- resolves each file to its Fix22/Fix26/Fix27 candidate node;
- checks whether each test file has test semantics in the graph;
- checks whether outgoing `TESTS` edges exist and target valid nodes;
- classifies gaps as `missing_candidate_node`, `missing_tests_edge`,
  `dangling_tests_target`, `missing_executor_profile`, `private_or_opt_in_gate`,
  or `ready_for_function_collection`;
- emits deterministic JSON and a human report.

This phase measures file-level readiness. It does not create canonical graph
nodes or execute test functions.

### Phase 1545p-Fix34: pytest collection to function-node candidates

Build a research-only collector that combines:

- `pytest --collect-only` output for real pytest node IDs;
- AST metadata for function names, decorators, imports, docstrings, and obvious
  target references;
- `tests/conftest.py` and `pyproject.toml` marker/skip policy;
- Fix33 file-node audit results.

It emits candidate `test_function` nodes and candidate edges only. It must
record uncertain coverage as deferred, not invent `TESTS` or `COVERS_SYMBOL`
claims.

### Phase 1545p-Fix35: canonical evidence envelope rehearsal

Build a local-only wrapper that executes a bounded selected set of graph-resolved
test nodes and emits canonical result envelopes. This phase must preserve
deterministic serialization and must not run private, live-network, sensitive, or
expensive tests unless the executor profile explicitly allows them.

### Phase 1545p-Fix36: graph-derived test frontier report

Query the graph and evidence records for:

- runtime/source nodes without test coverage;
- tests whose targets are missing or superseded;
- tests skipped by default without a clear gate;
- stale historical tests that still look current;
- authority/spec nodes without evidence.

This report becomes the bridge from local pytest coverage to homoiconic
maintenance and gap discovery.

### Later ADR/CDL route

An ADR is required before the homoiconic test registry becomes protocol
architecture. A CDL is required only if test evidence grants governance effect,
public economic weight, eligibility, claimability, or constitutional authority.

## 6. Acceptance Standard

The registry lane is ready for public-RC support only when all of the following
are true:

- every publishable test file has a candidate test-file node or a documented
  exclusion;
- every default-regression test file has at least one valid outgoing `TESTS` or
  deferred-gap classification;
- function-level node IDs are derived from actual pytest collection output;
- opt-in/private tests have explicit graph gates;
- evidence envelopes are deterministic and replayable;
- no test result is overclaimed as authority or activation.

## 7. Non-Claims

This guidance does not claim:

- canonical Atlas mutation;
- Genesis signing;
- public graph publication;
- public RC activation;
- replacement of `pytest`;
- live distributed test execution;
- governance authority from test results;
- economic activation;
- ADR/CDL mutation.
