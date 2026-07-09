# ILC Atlas Graph Node Classification and Edge Type Taxonomy v0.1

**Status:** Authoritative
**Established:** Phase 1573u / post-1573u ledger hardening
**Authority:** CDL-098 (provenance metadata); Fix38 annotation ledger (active candidate record store)
**Supersedes:** Informal per-phase guidance embedded in phase prompts

---

## §1 — Purpose

This document is the authoritative reference for agents (Codex, Claude Code, Genesis Agent)
classifying files as candidate graph nodes in the Fix38 annotation ledger
(`docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json` or its active successor).

Every new file created in `docs/specs/`, `docs/antigravity_tasks/`, `ilc_core/`, `tools/`,
or `tests/` requires a ledger entry in the same commit as the file. This taxonomy standardises
what goes into that entry so agents do not invent field names, edge types, or node kinds
ad hoc between sessions.

**Do not alter node kind strings or edge type strings.** They are used as identity tokens
in the Fix38 ledger and downstream graph materialisation tooling. Introducing synonyms
(e.g. `test_module` instead of `test_file`) creates coverage gaps that require manual repair.

---

## §2 — Ledger Entry Structure

Each new entry in `data['annotations']` is a JSON object with these exact field
names. Do not substitute alternative names for new records. The historical ledger
still contains a small number of legacy records with older keys; those are
permitted as legacy records only and must not be copied into new batches.

```json
{
  "annotation_batch": "manual_batch_NNN_phase_MMMM_<slug>",
  "chronology_note": "YYYY-MM-DD phase_MMMM <one-line description>",
  "manual_read_summary": "<one sentence describing the file's purpose — requires reading the file first>",
  "proposed_authority_trace_edges": [
    {
      "edge_type": "REFERENCES_AUTHORITY",
      "target": "cdl:CDL-NNN",
      "review_status": "candidate_cdl_NNN_trace"
    }
  ],
  "proposed_semantic_edges": [
    {
      "edge_type": "SOURCE_TREE_MEMBER",
      "target": "genesis:genesis_root_v0.4"
    }
  ],
  "proposed_trace_roles": ["REFERENCES_AUTHORITY", "SOURCE_TREE_MEMBER"],
  "recommended_graph_action": "load_bearing_artifact_added",
  "repo_path": "docs/specs/example_file_v0.1.md"
}
```

### Field descriptions

| Field | Required | Description |
|---|---|---|
| `annotation_batch` | Yes | Batch identifier string; see §8 for numbering convention |
| `chronology_note` | Yes | Date, phase, and brief description of the file's commit context |
| `manual_read_summary` | Yes | One sentence summary of the file's purpose; **must be based on reading the file** — do not invent |
| `proposed_authority_trace_edges` | Yes | Authority-connection edges (CDL, ADR, ratified spec); may be empty array `[]` if none exist |
| `proposed_semantic_edges` | Yes | Structural/content edges; must include at minimum `SOURCE_TREE_MEMBER → genesis:genesis_root_v0.4` |
| `proposed_trace_roles` | Yes | Flat array of all edge type strings used across both edge arrays |
| `recommended_graph_action` | Yes | Normalized graph action token: `support_only`, `load_bearing_artifact_added`, `load_bearing_artifact_changed`, `none`, or `deferred`; older records may contain free-text materialization notes |
| `repo_path` | Yes | Repo-relative file path (NOT `path`; NOT replaced by `candidate_id` or `node_type`) |

### What NOT to use

These field names appeared in earlier informal guidance and are **incorrect**:

| Wrong field | Correct field |
|---|---|
| `path` | `repo_path` |
| `node_type` | (not a top-level field; node kind is encoded in `recommended_graph_action` and `proposed_trace_roles`) |
| `candidate_id` | Do not add to new records; legacy records may retain it for historical repair traces |
| `proposed_edges` | `proposed_authority_trace_edges` + `proposed_semantic_edges` |
| `annotation_method` | Do not add to new records; provenance metadata belongs in the per-node Genesis signing block, not the candidate record |

---

## §3 — Node Kind Taxonomy

Node kind is inferred from file path and content type. Use the strings in the
`node_kind` column exactly when encoding node kind in downstream tooling.

| node_kind | Applies to | Description | graph_delta form |
|---|---|---|---|
| `test_file` | `tests/test_*.py` | Automated test files | `support_only` |
| `runtime_module` | `ilc_core/**/*.py` | Python runtime modules implementing protocol logic | `load_bearing_artifact_added` |
| `spec_doc` | `docs/specs/ilc_*_v*.md` (non-evidence) | Governance specs, taxonomy docs, schema references | `load_bearing_artifact_added` |
| `cdl_evidence` | `docs/specs/ilc_cdl_*_evidence_*.md` | CDL opening, ratification, or amendment evidence docs | `load_bearing_artifact_added` |
| `adr_spec` | `docs/adr/ADR_*.md` | Architecture Decision Records | `load_bearing_artifact_added` |
| `phase_prompt` | `docs/antigravity_tasks/antigravity_prompt__*.md` | Phase execution prompts | `support_only` |
| `phase_walkthrough` | `docs/phases/phase_*_walkthrough.md` | Retrospective phase records | `support_only` |
| `window_guidance` | `docs/specs/ilc_window_*_guidance_*.md`, `ilc_window_*_handoff_*.md` | Window guidance and closure handoff docs | `support_only` |
| `tool_script` | `tools/**/*.py`, `tools/**/*.sh` | Repository tooling and utility scripts | `support_only` |
| `sim_tool` | `tools/**/sim_*.py`, `out/sim_*/` (when tracked) | Simulation scripts and result files when tracked | `support_only` or `load_bearing_artifact_added` if simulation is authoritative evidence |
| `constraint_record` | `docs/specs/ilc_*_obligation_register_*.md`, repair receipts | Obligation registers, blocker records, repair receipts | `load_bearing_artifact_added` |

---

## §4 — Canonical ILC Edge Type Namespace

This section and §4a define one canonical ILC edge namespace. There are not two
competing taxonomies. The distinction is a **usage profile**:

- `usage_profile=phase_intake` — edge labels agents may use for ordinary new
  Fix38 phase-intake records.
- `usage_profile=atlas_native_reserved` — canonical ILC edge labels reserved for
  Atlas/LMDB materialization, package topology, source-code extraction,
  governance topology, or lifecycle normalization.
- `usage_profile=legacy_reserved_no_new_use` — labels preserved for historical
  graph fidelity but not available for new ordinary phase-intake records.

The labels described directly in §4 are canonical and have
`usage_profile=phase_intake` unless explicitly marked legacy. The additional
labels in §4a are also canonical; they are restricted by usage profile so agents
do not use high-authority or materialization-specific graph relations casually.

Do not invent new edge names in Fix38 records. If a phase needs a relationship
that cannot be expressed by a `phase_intake` edge below, either use a documented
substitution from §4a or route the new edge through the namespace governance
policy. New canonical edge names require governance; user-created extension
edges must follow the namespace extension policy and remain non-canonical unless
ratified.

### SOURCE_TREE_MEMBER

**Meaning:** Connects any tracked file to the genesis root — asserts it is part of the
ILC source tree.
**Source node types:** All node kinds.
**Target format:** `genesis:genesis_root_v0.4`
**Example:** `{"edge_type": "SOURCE_TREE_MEMBER", "target": "genesis:genesis_root_v0.4"}`

Every file in every ledger entry must include this edge in `proposed_semantic_edges`.
Do not omit it.

---

### REFERENCES_AUTHORITY

**Meaning:** The file cites, depends on, or is governed by a CDL, ADR, or ratified spec.
Requires an actual content reference — do not use for mere co-existence.
**Source node types:** `spec_doc`, `cdl_evidence`, `adr_spec`, `test_file`, `runtime_module`,
`phase_prompt`, `window_guidance`, `constraint_record`
**Target format:** `cdl:CDL-NNN`, `adr:ADR-NNNN`, or `docs/specs/<filename>`
**review_status in authority trace edges:** `"candidate_cdl_NNN_trace"`, `"candidate_adr_NNNN_trace"`, etc.
**Example:**
```json
{
  "edge_type": "REFERENCES_AUTHORITY",
  "target": "cdl:CDL-098",
  "review_status": "candidate_cdl_098_trace"
}
```

---

### REFERENCES

**Meaning:** Legacy generic reference edge found in older Fix38 annotation
records. Do not use for new records when a more specific edge applies. Prefer
`REFERENCES_AUTHORITY` for CDL/ADR/spec authority links, `DERIVED_FROM` for
derivation, `TESTS` for test coverage, and `EVIDENCES` for evidence links.

**Source node types:** Legacy records only.
**Target format:** Historical target string from the legacy record.
**Migration note:** Future cleanup may migrate legacy `REFERENCES` edges to more
specific edge types after source-read review.

---

### IMPLEMENTS

**Meaning:** Runtime module implements parameters, constraints, or behaviour specified by
a CDL or ADR.
**Source node types:** `runtime_module`
**Target format:** `cdl:CDL-NNN`, `adr:ADR-NNNN`
**Example:** `{"edge_type": "IMPLEMENTS", "target": "cdl:CDL-051"}`

---

### TESTS

**Meaning:** Test file exercises or validates a specific module, doc, or function. Distinct
from `REGRESSES` (which guards a named invariant) and `COVERS_SYMBOL` (which pinpoints a
Python symbol).
**Source node types:** `test_file`
**Target format:** `ilc_core/path/to/module.py`, `docs/specs/<filename>`, `docs/adr/<filename>`
**Example:** `{"edge_type": "TESTS", "target": "ilc_core/reputation/temporal_decay_runtime.py"}`

---

### COVERS_SYMBOL

**Meaning:** Test or spec covers a specific Python symbol (class, method, or function) by
dotted import path.
**Source node types:** `test_file`, `spec_doc`
**Target format:** `module.Class.method` (dotted Python import path)
**Example:** `{"edge_type": "COVERS_SYMBOL", "target": "ilc_core.types.Node.type"}`

---

### EVIDENCES

**Meaning:** Spec, walkthrough, or test provides evidence for a CDL ratification, phase
output token, or ADR acceptance.
**Source node types:** `cdl_evidence`, `phase_walkthrough`, `test_file`, `spec_doc`
**Target format:** `cdl:cdl_NNN_<slug>_ratified_MMMM`, `phase:<NNNN_token>`, `adr:<slug>`
**Example:** `{"edge_type": "EVIDENCES", "target": "cdl:cdl_098_provenance_metadata_ratified_1573pre"}`

---

### REGRESSES

**Meaning:** Test guards against regression of a specific named invariant. The invariant
token should be stable and not phase-specific.
**Source node types:** `test_file`
**Target format:** `invariant:<token_name>`
**Example:** `{"edge_type": "REGRESSES", "target": "invariant:no_decision_log_mutation_phase_354"}`

---

### CLASSIFIED_BY

**Meaning:** File is classified by a policy, guard, or sensitivity rule that restricts
its publication or distribution.
**Source node types:** All node kinds (when applicable).
**Target format:** `policy:<policy_token>` (e.g., `policy:public_rc_excluded`)
**Example:** `{"edge_type": "CLASSIFIED_BY", "target": "policy:public_rc_excluded"}`

Add this edge to any file with a `PUBLIC_RC_EXCLUDE` header, in addition to its other edges.

---

### SIM_EVIDENCE

**Meaning:** Simulation script or result file provides evidence for a claim, design
decision, or protocol parameter.
**Source node types:** `sim_tool`, `spec_doc`
**Target format:** `claim:<claim_slug>`, `cdl:CDL-NNN`
**Example:** `{"edge_type": "SIM_EVIDENCE", "target": "claim:spectral_route_efficiency_threshold"}`

---

### DERIVED_FROM

**Meaning:** File is derived from, generated by, or directly extends another file.
**Source node types:** `tool_script`, `sim_tool`, `spec_doc`
**Target format:** `docs/specs/<filename>`, `ilc_core/<module.py>`, `tools/<script>`
**Example:** `{"edge_type": "DERIVED_FROM", "target": "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json"}`

---

### PROVENANCE

**Meaning:** Records the provenance chain for an artifact — traces custody, authorship,
or transformation lineage.
**Source node types:** `cdl_evidence`, `spec_doc`, `constraint_record`
**Target format:** `phase:<NNNN_token>`, `cdl:CDL-NNN`, `commit:<hash>`
**Example:** `{"edge_type": "PROVENANCE", "target": "phase:1573e_ccss_spectral_authority"}`

---

### ATTESTATION

**Meaning:** Walkthrough or record attests to the completed execution of a phase or act.
Distinct from `EVIDENCES` (which provides substantive evidence, not just attestation of
completion).
**Source node types:** `phase_walkthrough`, `constraint_record`
**Target format:** `phase:<NNNN_output_token>`
**Example:** `{"edge_type": "ATTESTATION", "target": "phase:1573e_spectral_authority_ratified"}`

---

### COVERS_COMMAND_CONTRACT

**Meaning:** Test covers the CLI contract (flags, exit codes, output format) of a specific
command.
**Source node types:** `test_file`
**Target format:** `cli:<command> <subcommand>`
**Example:** `{"edge_type": "COVERS_COMMAND_CONTRACT", "target": "cli:ilc sidecar graph-viz"}`

---

### NEGATIVE_ASSERTS

**Meaning:** Test or spec records a negative claim or non-claim — asserts that something
does NOT happen, does NOT apply, or is explicitly excluded.
**Source node types:** `test_file`, `spec_doc`, `cdl_evidence`
**Target format:** `claim:<claim_slug>` or `invariant:<invariant_token>`
**Example:** `{"edge_type": "NEGATIVE_ASSERTS", "target": "claim:standing_genesis_governance_bonus"}`

---

### REQUIRES_PROFILE

**Meaning:** File's correctness depends on a specific execution profile, environment flag,
or guard being active (e.g., git history availability, a specific env variable).
**Source node types:** `test_file`, `tool_script`
**Target format:** `executor_profile:<profile_token>`
**Example:** `{"edge_type": "REQUIRES_PROFILE", "target": "executor_profile:git_history_available"}`

---

### TESTS_STORAGE

**Meaning:** Test exercises LMDB, on-disk, or storage-layer behaviour specifically.
Use in addition to `TESTS` when storage fidelity (not just logic) is the test concern.
**Source node types:** `test_file`
**Target format:** `ilc_core/path/to/storage_module.py` or `lmdb:<store_name>`
**Example:** `{"edge_type": "TESTS_STORAGE", "target": "lmdb:atlas_graph_store"}`

---

## §4a — Additional Canonical Native Edge Definitions

The live Atlas LMDB at `out/genesis_base_graph_v0.4_unified.lmdb` contains
native graph edges that are valid canonical ILC graph semantics but are not
automatically available for new ordinary Fix38 phase-intake records. These
labels are reserved for ILC native use and are accepted by
`ilc_core/storage/genesis_atlas_lmdb_writer.py`.

The single canonical edge namespace is the union of §4 and §4a. New phase ledger
entries should still prefer `usage_profile=phase_intake` labels. Use the
additional native labels only when a phase explicitly operates on Atlas/LMDB
materialization or a ratified graph-governance spec authorizes that label in the
current context.

| Edge type | Reserved meaning | Usage profile | Substitution guidance for ordinary phase records |
|---|---|---|---|
| `CARRIES_FORWARD` | Carries an obligation, phase result, policy, or invariant forward across windows/phases. | `atlas_native_reserved` | Use `PROVENANCE` for lineage evidence, `ATTESTATION` for phase completion, or `REFERENCES_AUTHORITY` for governing authority. |
| `CONSTRAINS` | A policy or parameter constrains another policy, primitive, or rule. | `atlas_native_reserved` | Use `REFERENCES_AUTHORITY` when documenting the governing spec; do not collapse true constraint topology without review. |
| `CONTAINS_FILE` | Package/root artifact contains a concrete repo file node. | `atlas_native_reserved` | No Fix38 substitute; ordinary files use `SOURCE_TREE_MEMBER`. |
| `CONTAINS_GROUP` | Package/root artifact contains a repo group node. | `atlas_native_reserved` | No Fix38 substitute. |
| `CONTAINS_PARTITION` | Package/root artifact contains a graph or package partition. | `atlas_native_reserved` | No Fix38 substitute. |
| `EXPECTS_RESOLUTION` | Authority or artifact expects a gap node to be resolved later. | `atlas_native_reserved` | Use `REFERENCES_AUTHORITY` to cite a gap policy; do not encode lifecycle state unless authorized. |
| `GOVERNS` | Authority node governs a policy, invariant, CDL, ADR, or other governed object. | `atlas_native_reserved` | Use `REFERENCES_AUTHORITY` for ordinary docs that cite governing authority. Do not substitute when the actual claim is governance topology. |
| `IMPLEMENTS_MODULE` | Legacy/module-level implementation relation between files or tests and modules. | `legacy_reserved_no_new_use` | Prefer `IMPLEMENTS` for runtime-to-CDL/ADR implementation and `TESTS`/`COVERS_SYMBOL` for test coverage. |
| `IMPORTS_MODULE` | Source module imports another source module. | `atlas_native_reserved` | Usually omit from Fix38. Use `DERIVED_FROM` only if the relationship is substantive derivation, not a normal import. |
| `OPENED_FOR` | CDL/ADR/opening artifact opens a governance item for a target authority. | `atlas_native_reserved` | Use `EVIDENCES` or `REFERENCES_AUTHORITY` in ordinary phase evidence records. |
| `PRELOCK_FOR` | Prelock artifact or phase prelocks a governance item. | `atlas_native_reserved` | Use `EVIDENCES` or `ATTESTATION` if the file records the prelock event. |
| `PRIMITIVE_INVOCATION` | Truth primitive invokes, maps to, or is authorized against an axiom/primitive target. | `atlas_native_reserved` | No ordinary Fix38 substitute. |
| `PROPOSES_CHANGE_TO` | Proposal object targets an authority/spec for future modification. | `atlas_native_reserved` | Use `REFERENCES_AUTHORITY` for docs that merely discuss proposed changes. |
| `RATIFICATION_EVIDENCE_FOR` | Specific ratification evidence points to a CDL/ADR authority. | `legacy_reserved_no_new_use` | Prefer `EVIDENCES` plus `REFERENCES_AUTHORITY` for new records. |
| `RESOLVED_BY` | A superseded/alternate/gap node is resolved by a canonical node or decision. | `atlas_native_reserved` | Do not substitute unless source-read proves `EVIDENCES` or `ATTESTATION` is the actual relationship. |
| `SAME_AUTHORITY` | Two authority aliases or historical records refer to the same authority surface. | `atlas_native_reserved` | No ordinary Fix38 substitute; route alias repairs through governance/normalization phases. |
| `SAME_SOURCE` | A file reference node and repo file node identify the same source artifact. | `atlas_native_reserved` | No ordinary Fix38 substitute. |
| `SUPERSEDED_BY` | One authority or artifact is superseded by another. | `atlas_native_reserved` | Do not collapse to `REFERENCES_AUTHORITY`; lifecycle semantics would be lost. |
| `USES` | Tool/script/module uses another module or adapter. | `atlas_native_reserved` | Usually omit. Use `DERIVED_FROM` only for substantive derivation, not ordinary dependency. |

### Substitution rules

Safe substitutions are contextual, not mechanical. Do not run a blind migration
that rewrites Atlas/LMDB edges into phase-intake edges. A substitution is allowed
only when the original source and target have been direct-read and the narrower
edge preserves the claim:

1. `RATIFICATION_EVIDENCE_FOR`, `OPENED_FOR`, and `PRELOCK_FOR` may become
   `EVIDENCES` or `ATTESTATION` in new phase records when the file attests to or
   evidences that governance act.
2. `IMPLEMENTS_MODULE` may become `IMPLEMENTS` only when the source is a runtime
   module and the target is a CDL/ADR authority. If the source is a test, use
   `TESTS` or `COVERS_SYMBOL`.
3. `IMPORTS_MODULE` and `USES` should usually be omitted from phase-intake
   records. Normal imports are not graph-governance claims.
4. `GOVERNS`, `SAME_AUTHORITY`, `SAME_SOURCE`, `SUPERSEDED_BY`,
   `RESOLVED_BY`, `CONTAINS_*`, `CONSTRAINS`, `PRIMITIVE_INVOCATION`, and
   `EXPECTS_RESOLUTION` should not be substituted automatically. They carry
   native graph semantics that should remain explicit when present.

The current difference between phase-intake and Atlas-native usage profiles is
therefore intentional after this section: the single canonical ILC edge namespace
contains more native semantics than ordinary phase-intake records should use.

## §4b — Simplification, Recipes, and Retirement Plan

The canonical namespace should converge toward fewer high-quality primitive
relations. Some historical labels remain reserved only to preserve current LMDB
fidelity, but should be retired from new graph production once their existing
rows are migrated with receipts.

Do not delete or rewrite LMDB edges in-place without a migration phase. A
retirement migration must:

1. count existing source edge rows before migration;
2. direct-read a representative sample for every source/target pattern;
3. generate replacement edges with deterministic `edge_id` values;
4. preserve or rebuild preimages and graph payload/index consistency;
5. emit a migration receipt with before/after edge counts; and
6. run Atlas LMDB validation after the rewrite.

| Edge type | Simplification class | Preferred representation | Migration posture |
|---|---|---|---|
| `REFERENCES` | `legacy_retire_candidate` | Replace with `REFERENCES_AUTHORITY`, `DERIVED_FROM`, `EVIDENCES`, `TESTS`, or `PROVENANCE` after source-read classification. | Plan migration; no new use. |
| `IMPLEMENTS_MODULE` | `legacy_retire_candidate` | Runtime-to-authority becomes `IMPLEMENTS`; test-to-module becomes `TESTS`; symbol-level coverage becomes `COVERS_SYMBOL`. | Plan migration; no new use. |
| `RATIFICATION_EVIDENCE_FOR` | `recipe_retire_candidate` | `EVIDENCES -> cdl:<ratification-token>` plus `REFERENCES_AUTHORITY -> cdl:CDL-NNN`. | Good candidate for scripted migration with source/target validation. |
| `USES` | `recipe_retire_candidate` | Ordinary imports become `IMPORTS_MODULE`; generation/lineage claims become `DERIVED_FROM`. | Good candidate for scripted migration after source-read target classification. |
| `OPENED_FOR` | `recipe_retire_candidate` | `EVIDENCES -> cdl:<opening-token>` plus `REFERENCES_AUTHORITY -> cdl:CDL-NNN`. | Candidate migration if opening targets can be identified deterministically. |
| `PRELOCK_FOR` | `recipe_retire_candidate` | `ATTESTATION -> phase:<prelock-token>` or `EVIDENCES -> cdl:<prelock-token>` plus `REFERENCES_AUTHORITY -> cdl:CDL-NNN`. | Candidate migration if prelock targets can be identified deterministically. |
| `EXPECTS_RESOLUTION` | `native_primitive_review` | Usually preserve as lifecycle topology; may be represented by a future gap-node recipe only after gap schema ratification. | Do not migrate automatically. |
| `CONTAINS_FILE` | `materialized_shortcut_keep` | Can be derived from package manifest membership plus `SOURCE_TREE_MEMBER`, but direct edge supports package queries. | Keep. |
| `CONTAINS_GROUP` | `materialized_shortcut_keep` | Can be derived from package/group manifest membership, but direct edge supports package queries. | Keep. |
| `CONTAINS_PARTITION` | `materialized_shortcut_keep` | Can be derived from partition manifest membership, but direct edge supports package queries. | Keep. |
| `SAME_SOURCE` | `materialized_shortcut_keep` | Can be inferred from source path/content-hash equality, but direct edge supports normalization queries. | Keep. |
| `IMPORTS_MODULE` | `native_extraction_keep` | Direct source-code import relation. | Keep for code-graph extraction; not for ordinary phase intake. |
| `CARRIES_FORWARD` | `native_primitive_keep` | Carries temporal obligation/phase continuity. | Keep unless a future temporal-edge CDL replaces it. |
| `CONSTRAINS` | `native_primitive_keep` | Captures policy/parameter constraint semantics. | Keep. |
| `GOVERNS` | `native_primitive_keep` | Captures authority topology. | Keep; governance-sensitive. |
| `PRIMITIVE_INVOCATION` | `native_primitive_keep` | Captures truth-primitive/axiom topology. | Keep. |
| `PROPOSES_CHANGE_TO` | `native_primitive_keep` | Captures proposal-target topology. | Keep, even if currently unused. |
| `RESOLVED_BY` | `native_primitive_keep` | Captures gap/alternate resolution lifecycle. | Keep. |
| `SAME_AUTHORITY` | `native_primitive_keep` | Captures authority alias equivalence. | Keep. |
| `SUPERSEDED_BY` | `native_primitive_keep` | Captures lifecycle replacement. | Keep. |

Near-term cleanup target: retire `REFERENCES`, `IMPLEMENTS_MODULE`,
`RATIFICATION_EVIDENCE_FOR`, `USES`, `OPENED_FOR`, and `PRELOCK_FOR` from the
live Atlas LMDB through a dedicated migration phase, unless source-read audit
finds rows whose semantics cannot be represented by the preferred recipes.

## §5 — Classification Decision Tree

Apply these steps in order for every new file. Stop at the first match.

**Step 1 — Is it in `out/`?**
→ `graph_delta=none:generated_output` — do not add a ledger entry.

**Step 2 — Is it a test file (`tests/test_*.py`)?**
→ `node_kind=test_file`
→ Required edges: `TESTS → module(s) it tests`, `SOURCE_TREE_MEMBER → genesis:genesis_root_v0.4`
→ Optional edges: `COVERS_SYMBOL` if specific symbols are covered; `REGRESSES` if named invariants are guarded; `REQUIRES_PROFILE` if env-gated
→ `graph_delta=support_only:<path>`

**Step 3 — Is it an `ilc_core/` runtime module?**
→ `node_kind=runtime_module`
→ Required edges: `IMPLEMENTS → cdl:CDL-NNN` (or `REFERENCES_AUTHORITY` if no specific CDL), `SOURCE_TREE_MEMBER`
→ `graph_delta=load_bearing_artifact_added:<path> -> cdl:CDL-NNN`

**Step 4 — Is it a CDL evidence or ratification doc (`docs/specs/ilc_cdl_*_evidence_*.md`)?**
→ `node_kind=cdl_evidence`
→ Required edges: `EVIDENCES → cdl:cdl_NNN_<slug>`, `REFERENCES_AUTHORITY → cdl:CDL-NNN`
→ Add `NEGATIVE_ASSERTS` for any non-claims documented
→ `graph_delta=load_bearing_artifact_added:<path> -> cdl:CDL-NNN`

**Step 5 — Is it an ADR spec (`docs/adr/ADR_*.md`)?**
→ `node_kind=adr_spec`
→ Required edges: `REFERENCES_AUTHORITY → governing CDL(s)` (if any), `SOURCE_TREE_MEMBER`
→ `graph_delta=load_bearing_artifact_added:<path> -> adr:ADR-NNNN`

**Step 6 — Is it a governance spec in `docs/specs/` (non-CDL-evidence)?**
→ `node_kind=spec_doc`
→ Required edges: `REFERENCES_AUTHORITY → CDL/ADR it cites`, `SOURCE_TREE_MEMBER`
→ `graph_delta=load_bearing_artifact_added:<path> -> <primary authority anchor>`

**Step 7 — Is it a phase prompt (`docs/antigravity_tasks/antigravity_prompt__*.md`)?**
→ `node_kind=phase_prompt`
→ Required edges: `SOURCE_TREE_MEMBER` only
→ `graph_delta=support_only:<path>`

**Step 8 — Is it a phase walkthrough (`docs/phases/phase_*_walkthrough.md`)?**
→ `node_kind=phase_walkthrough`
→ Required edges: `ATTESTATION → phase output token(s)`, `SOURCE_TREE_MEMBER`
→ `graph_delta=support_only:<path>`

**Step 9 — Is it a window guidance or handoff doc?**
→ `node_kind=window_guidance`
→ Required edges: `SOURCE_TREE_MEMBER`; `REFERENCES_AUTHORITY` if it cites a CDL or ADR
→ `graph_delta=support_only:<path>`

**Step 10 — Is it a tool or simulation script (`tools/`, `sim_*.py`)?**
→ `node_kind=tool_script` (general) or `sim_tool` (simulation)
→ Required edges: `SOURCE_TREE_MEMBER`; `DERIVED_FROM` if it processes another file;
`SIM_EVIDENCE` if it produces authoritative evidence
→ `graph_delta=support_only:<path>` (or `load_bearing_artifact_added` if simulation output is authoritative evidence cited in a CDL)

**Step 11 — Is it a constraint record (obligation register, repair receipt)?**
→ `node_kind=constraint_record`
→ Required edges: `REFERENCES_AUTHORITY`, `SOURCE_TREE_MEMBER`
→ `graph_delta=load_bearing_artifact_added:<path> -> <primary obligation anchor>`

**In all cases — does the file have a `PUBLIC_RC_EXCLUDE` header?**
→ Add `CLASSIFIED_BY → policy:public_rc_excluded` to `proposed_semantic_edges`
regardless of node kind.

---

## §6 — graph_delta Forms

These five forms are used in phase walkthroughs and STATUS backfills. Use exactly one
per file. They appear in `recommended_graph_action` in the ledger record.

### `graph_delta=load_bearing_artifact_added:<path> -> <anchor>`

New file that IS a protocol graph artifact. The file itself is a node in the Genesis/ILC
hypergraph, not merely support material.

Use for: CDL evidence, ADRs, ratified specs, `ilc_core/` runtime modules,
governance constraint records, taxonomy specs (including this file).

Example: `graph_delta=load_bearing_artifact_added: docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md -> genesis:genesis_root_v0.4`

---

### `graph_delta=load_bearing_artifact_changed:<path> -> <anchor>`

An existing protocol artifact was modified. The anchor records what authority governs
the change.

Use for: Amendments to CDL evidence docs, ADR updates, `ilc_core/` module changes.

---

### `graph_delta=support_only:<path>`

New file that supports the graph but is not itself a graph node.

Use for: Phase prompts, walkthroughs, test files, tool scripts, window guidance docs,
handoff docs.

---

### `graph_delta=none:<reason>`

File has no epistemic relationship to the protocol graph. Extremely rare. Must justify.

Use for: `out/` directory outputs, ephemeral scratch files.

---

### `graph_delta=deferred:<token>`

Graph registration is deferred to a named follow-up. Must specify the phase token that
will close it. Avoid this form — same-commit registration is strongly preferred.

Use only when registration genuinely cannot occur in the same commit (e.g., the ledger
file itself is what's being created for the first time).

---

## §7 — What NOT to Do

1. **Do not invent summaries.** `manual_read_summary` must come from reading the file.
   An invented summary that contradicts the file content propagates incorrect provenance.

2. **Do not use `"path"`.** Always `"repo_path"`. The wrong field name causes coverage
   audit gaps (the audit script looks for `repo_path`).

3. **Do not omit `SOURCE_TREE_MEMBER`.** Every tracked file must assert membership in the
   source tree. Omitting it leaves the file disconnected from the genesis root in the
   graph projection.

4. **Do not defer ledger registration.** Same-commit rule: the ledger entry must be in
   the same commit as the new file. A later-phase backfill is only acceptable when
   registering existing pre-protocol files (the historical backlog).

5. **Do not run parallel LMDB writes.** Never run more than one LMDB-mutating command
   against the same LMDB root concurrently. Sequential writes only; validate after
   each write group.

6. **Do not reference a CDL that is not ratified or opened.** If a CDL is in draft or
   informal planning, use `"review_status": "candidate_unconfirmed"` and note it is
   not yet a canonical reference. Only ratified or formally opened CDLs may appear
   without qualification in `proposed_authority_trace_edges`.

7. **Do not add `annotation_method`, `node_type`, or `candidate_id` as top-level fields**
   in new candidate ledger records. Some historical records retain these keys as
   legacy repair traces, but new records use the §2 schema only. Provenance metadata
   belongs to the per-node Genesis signing block, not the candidate ledger record.

---

## §8 — Batch Numbering Convention

Batch identifier format: `manual_batch_NNN_phase_MMMM_<slug>`

- `NNN` — zero-padded 3-digit sequential integer, starting from the last batch in the
  ledger and incrementing by 1 per new batch
- `MMMM` — the current phase number (e.g., `1575`)
- `<slug>` — short lowercase underscore-separated description of what the batch covers

**Current last batch (as of Phase 1573ai/1573aj edge retirement prompt drafting):** `manual_batch_092_phase_1573ai_1573aj_edge_retirement_prompt_drafts`
**Next batch:** `manual_batch_093_<slug>`

For retroactive backfills covering a range of phases, use:
`manual_batch_NNN_phase_RANGE_retroactive`

Example: `manual_batch_079_phase_1400_1450_retroactive`

Do not reuse batch numbers. Do not use non-sequential numbers. If two separate
work streams produce batches in the same session, assign them sequential numbers
(079, 080, …) — do not assign both 079.

---

## §9 — Coverage Audit Script

Run this before committing to confirm that all files created in the current phase are
registered. A large total gap is expected (the historical pre-protocol backlog) and is
not the pass condition. The pass condition is: every file created IN THIS PHASE is
registered.

```python
import json, subprocess

with open('docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json') as f:
    data = json.load(f)

registered = set(a['repo_path'] for a in data['annotations'] if 'repo_path' in a)

result = subprocess.run(
    ['git', 'ls-files', '--', 'docs/specs/', 'docs/antigravity_tasks/',
     'ilc_core/', 'tools/', 'tests/'],
    capture_output=True, text=True
)
all_files = set(l.strip() for l in result.stdout.splitlines() if l.strip())

gap = sorted(all_files - registered)
print(f"Registered: {len(registered)}, In-scope: {len(all_files)}, Gap: {len(gap)}")
for p in gap:
    print(" UNREGISTERED:", p)
```

To check only files added in the current commit (tighter phase-close check):

```python
import json, subprocess

with open('docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json') as f:
    data = json.load(f)

registered = set(a['repo_path'] for a in data['annotations'] if 'repo_path' in a)

new_files = set(subprocess.run(
    ['git', 'diff', '--name-only', '--cached', '--diff-filter=A'],
    capture_output=True, text=True
).stdout.splitlines())

in_scope = {f for f in new_files if any(
    f.startswith(p) for p in ('docs/specs/', 'docs/antigravity_tasks/',
                               'ilc_core/', 'tools/', 'tests/')
)}

missing = sorted(in_scope - registered)
if missing:
    print("UNREGISTERED new files in this commit:")
    for p in missing:
        print(" ", p)
    raise SystemExit(1)
print(f"All {len(in_scope)} new in-scope file(s) in this commit are registered.")
```

---

## §10 — Provenance Metadata Block (CDL-098)

When a file is Genesis-signed (batch materialisation under CDL-098 authority), the
per-node provenance metadata block is added to the LMDB node payload. This is separate
from the candidate ledger record:

```json
{
  "annotation_method": "manual_reviewed",
  "annotation_phase": "<current phase>",
  "annotation_reviewer": "genesis_agent:01 | codex | sonnet",
  "genesis_signature_version": "v0.4",
  "update_authority": "genesis_until_sunset",
  "update_authority_cdl": "cdl_098",
  "graph_trace_status": "candidate"
}
```

This block does NOT replace any field in the candidate ledger record. The candidate
record (`repo_path`, `proposed_*_edges`, etc.) is the pre-signing annotation. The
provenance metadata block is added when the Genesis signing cycle materialises the
candidate into a signed node.
