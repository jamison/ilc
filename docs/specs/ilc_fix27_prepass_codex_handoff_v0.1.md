# Fix27 Pre-Pass Handoff — Codex Execution Guidance

**Date:** 2026-06-15
**Phase:** 1545p-Fix27-G10
**Status:** Pre-pass COMPLETE — boundary corrected by Codex audit — DPO runner pending Codex execution
**Sensitivity:** NON-SENSITIVE

> **BOUNDARY CORRECTION (Codex audit 2026-06-15):** The pre-pass edges were
> originally written directly into `out/genesis_atlas_full_repo_candidate_1545p_fix22.json`,
> which contaminates the Fix22 signing baseline. This has been corrected:
> Fix22 has been restored to committed state (10,029 nodes / 27,668 edges) via
> `git checkout`. The enriched graph is preserved at
> `out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json`.
> Fix27 must consume Fix22 read-only and emit pre-pass edges as a separate
> candidate JSONL layer — not by mutating Fix22.

---

## 1. What Has Been Done (Claude Code session 2026-06-15)

### 1.1 Summary

Two bodies of work were completed in the current session before this handoff:

1. **Semantic pre-pass P1–P29** — a classifier (`tools/evaluators/sim_atlas_semantic_prepass_fix27.py`) was developed, calibrated over 73 manually-annotated files from batch reviews, and executed over the full 14,958-record Fix26 deferred queue. It discovered **24,879 candidate edges** across 17 extraction rounds.

2. **Manual bucket annotation B1–B12** — after the pre-pass reached diminishing returns, the remaining 486 dark files (deferred nodes with zero outgoing edges) were resolved through 12 manual batch rounds that identified **1,278 additional candidate edges**. This produced a coverage result of zero dark deferred nodes.

**Enriched graph artifact (NOT the Fix22 baseline):**
- Location: `out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json`
- Total edges in enriched artifact: **53,825** (Fix22 baseline 27,668 + 26,157 candidate edges)
- Dark deferred nodes in enriched artifact: **0** (was 486 at start of session)
- Manually annotated nodes: **801** | Pre-pass annotated nodes: **4,183**

**Fix22 baseline (committed, read-only):**
- Location: `out/genesis_atlas_full_repo_candidate_1545p_fix22.json`
- Nodes: 10,029 | Edges: 27,668 — **unchanged, restored to committed state**

All Fix26 tests pass (6/6) against the restored Fix22 baseline.

**Edge type correction (Codex audit):** The B10–B12 fallback edges from dark files to the
genesis root used `REFERENCES_AUTHORITY`. Codex correctly identified this as too strong for
files that have no internal content references to that authority. The Fix27 runner should
reclassify these as `SOURCE_TREE_MEMBER` or a provenance/containment edge type, not
authority trace closure. See §3.5 below.

---

### 1.2 Semantic Pre-Pass — Pattern Inventory

The pre-pass implements 29 discovered patterns. The script is at:

```
tools/evaluators/sim_atlas_semantic_prepass_fix27.py
```

Pattern registry (each is a Python function in the script):

| Pattern | Function | Edge type | What it detects |
|---|---|---|---|
| P1 | `_p1_py`, `_p1_rs` | `IMPORTS_MODULE` | Python `import`/`from...import` + Rust `use` statements resolved to repo file nodes |
| P2 | `_p2_py` | `REFERENCES_AUTHORITY` | `CDL_NNN_DEPENDENCY` and `CDL_VN_DEPENDENCY` AST assignments in Python files |
| P3 | `_p3_md` | `REFERENCES_AUTHORITY` | `Anchor: <path>` explicit declarations in markdown |
| P4 | `_p4_md` | `REFERENCES_AUTHORITY` | `## Inputs to read first` / `## Required inputs` bullet paths in phase prompts |
| P5 | `_p5_py` | `TESTS` / `REFERENCES_AUTHORITY` | Path constants (`ROOT / "..."`) in test file module scope |
| P6 | (phase→seqlock table in `main()`) | `REFERENCES_AUTHORITY` | Phase number → window sequence lock deterministic mapping |
| P7 | (inline in `classify_file`) | `EVIDENCES` | Sim notes referencing tool scripts |
| P8 | `_p8_walkthrough_md` | `REFERENCES_AUTHORITY` | Walkthrough "Files touched" / "Main implementation commit" paths |
| P9 | `_p9_graph_delta` | `REFERENCES_AUTHORITY` / `EVIDENCES` | `graph_delta=<rel>:<src> -> <category>` annotations |
| P10 | `_p10_claim_table` | `REFERENCES_AUTHORITY` | Walkthrough claim audit table rows with `confirmed` |
| P11 | `_p11_files_changed_plain` | `REFERENCES_AUTHORITY` | Walkthrough "Files Changed" table — markdown links and plain paths |
| P12 | `_p12_ingestion_order` | `REFERENCES_AUTHORITY` | Numbered "Claude Ingestion Order" / "Required reading order" lists |
| P13 | `_p13_related_artifacts` | `REFERENCES_AUTHORITY` | Spec front-matter `Related artifacts:` / `Primary roadmap anchor:` fields |
| P14 | `_p14_inputs_verified` | `REFERENCES_AUTHORITY` | "Inputs Verified" / "Read and consumed" bullet sections in walkthroughs |
| P15 | `_p15_json_source_refs` | `REFERENCES_AUTHORITY` / `EVIDENCES` | JSON keys: `source_ref`, `governing_adr`, `evidence_refs`, `source_anchors`, `first_pass_results` |
| P16 | `_p16_sh_commands` | `TESTS` / `REFERENCES_AUTHORITY` | Shell scripts: `pytest tests/...py`, `validate_phase_prompt`, path variable assignments |
| P17 | `_p17_ratification_evidence` | `EVIDENCES` | CDL ratification evidence docs → CDL register |
| P18 | `_p18_global_bullet_paths` | `REFERENCES_AUTHORITY` | Non-phase-doc bullet list backtick paths to `docs/` and `ilc_core/` |
| P19 | `_p19_global_table_paths` | `REFERENCES_AUTHORITY` | Table cell backtick `docs/` paths in any markdown |
| P20 | `_p20_git_diff_paths` | `REFERENCES_AUTHORITY` | `git diff -- path` commands in walkthroughs and specs |
| P21 | `_p21_deliverables_fenced_block` | `REFERENCES_AUTHORITY` | Phase prompt deliverables fenced code block paths |
| P22 | `_p22_scope_section` | `REFERENCES_AUTHORITY` | "In scope" / "Scope" section paths in phase prompts |
| P23 | `_p23_prose_cdl_refs` | `REFERENCES_AUTHORITY` | Prose CDL-NNN / ADR-NNNN mentions resolved to CDL/ADR nodes |
| P24 | (inside `_p16_sh_commands`) | `TESTS` | Multi-line bash array: `python3 -m pytest` on its own line, then indented test file paths |
| P25 | (inside `_p16_sh_commands`) | `REFERENCES_AUTHORITY` | Shell scripts calling `tools/*.py` runners |
| P26 | `_p26_md_code_block_pytest` | `TESTS` | Pytest invocations inside fenced code blocks + test paths in section headings |
| P27 | (phase→seqlock alias) | `REFERENCES_AUTHORITY` | Variant of P6 for differently formatted filenames |
| P28 | `_p28_md_inline_backtick_paths` | `REFERENCES_AUTHORITY` / `TESTS` | Backtick-wrapped relative file paths anywhere in MD prose |
| P29 | `_p29_md_absolute_path_links` | `REFERENCES_AUTHORITY` / `TESTS` | Absolute filesystem paths in MD markdown links (Atlas turn logs use `/Users/jamison/.../path`) |

**Pre-pass edge type breakdown (24,879 edges):**

| Edge type | Count |
|---|---:|
| `REFERENCES_AUTHORITY` | ~19,500 |
| `TESTS` | ~4,500 |
| `EVIDENCES` | ~800 |
| `IMPLEMENTS` | ~79 |

---

### 1.3 Manual Batch Annotations — Batch Inventory

After the pre-pass reached the crossover point where remaining dark files had idiosyncratic patterns (2–10 files each), the user directed reading individual files manually and applying Category A epistemological reasoning.

**Key epistemological principle (user-stated):**
> "By definition in epistemics, all files should connect back to the graph, at least to Genesis directly — we did make those files."

This is correct as a provenance/containment claim: every ILC repo file was created under Genesis authority and therefore belongs in the graph's reachability envelope. However, the edge type for files with no internal content references to Genesis is **not** `REFERENCES_AUTHORITY` — that type requires the source file to explicitly reference the target authority in its content. The correct edge type for "this file is a member of the Genesis-governed source tree" is `SOURCE_TREE_MEMBER`, `DERIVED_FROM_GENESIS_REPO`, or `ATTESTED_BY_GENESIS_OPERATOR`. B10–B12 used `REFERENCES_AUTHORITY` as a fallback; see §3.5 for the reclassification requirement.

Batch registry:

| Batch | Files | Edges | Method |
|---|---|---|---|
| B1–B8 | 283 files | ~1,018 | Prior session — pattern discovery and early manual reads |
| B9 | 73 Atlas turn logs | 219 | All atlas turn logs → EVIDENCES STATUS.md + ATLAS_INDEX.md + schema doc |
| B10 | 23 files | 29 | Dark ADR files → logical `adr:` nodes; root governance → genesis root; atlas authority docs and pilot files → econ research spec |
| B11 | 115 files | 115 | docs/specs clusters (canon_bundle_key_registry, cluster_a, whitepaper); antigravity atlas G-prompts; dark phase walkthroughs; sim docs |
| B12 | 352 files | 357 | Comprehensive sweep: all remaining python, json, shell, docs/research, config, testbed, misc |
| Batch 12 final | 1 | 1 | `sidecars.md` |

**Original targets used in enriched artifact (not all are accepted authority traces):**

| Target node | Edge type used | Status |
|---|---|---|
| `artifact:genesis_intent_attestation_init_authority_map` | `REFERENCES_AUTHORITY` | **Fallback for B10–B12 Category A files — NOT an accepted authority trace.** Reclassify to `SOURCE_TREE_MEMBER` / `DERIVED_FROM_GENESIS_REPO`. See §3.5. |
| `adr:0001_...`, `adr:0004_...`, `adr:0008_...`, `adr:0012_...` | `EVIDENCES` | ADR source files evidencing their logical ADR node — valid edge type |
| `artifact:full_repo_genesis_atlas_candidate_root_1545p_fix22` | `REFERENCES_AUTHORITY` | Atlas G-series prompts referencing atlas candidate root — valid |
| econ research window spec (`docs/specs/ilc_econ_research_window_01_...`) | `REFERENCES_AUTHORITY` | ATLAS_INDEX, STATUS, pilot docs — valid (content references) |

**Atlas cluster note (from user):**
The Atlas of Cliffs cluster is a live use case of ILC epistemological graphing, authored by Genesis Agent 01, studying macroeconomic transition cliffs from AI growth. The authority chain for all atlas files flows:
- Atlas turn logs → EVIDENCES `STATUS.md` + `ATLAS_INDEX.md`
- `ATLAS_INDEX.md` + `STATUS.md` → REFERENCES_AUTHORITY econ research window spec
- econ research window spec → REFERENCES_AUTHORITY CDL-052
- CDL-052 → genesis root

---

### 1.4 Git State After Boundary Correction

After boundary correction (Codex audit 2026-06-15), the working directory is:

```
Untracked (stage for Commit 1):
  tools/evaluators/sim_atlas_semantic_prepass_fix27.py       ← pre-pass classifier (P1–P29)
  out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json  ← enriched artifact
  docs/specs/ilc_homoiconic_graph_loading_tiers_v0.1.md
  docs/specs/ilc_fix27_prepass_codex_handoff_v0.1.md        ← this file

Modified (stage for Commit 1):
  docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix27_g10_rewrite_candidate_generation.md

DO NOT STAGE (unrelated to Fix27):
  out/genesis_compile_coverage_diagnostic_v0.1.json
  out/genesis_core_star_map_gap_analysis_v0.1.json
  out/monitoring/d2e_risk_snapshot_phase_306.json
  out/monitoring/infrastructure_risk_snapshot_phase_316.json
  docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.1.md
  docs/sims/sim_spectral_02/genesis_core_star_map_gap_analysis_v0.1.md
  tools/graph_viz_3d.py
  graphify-out/
  lib/

MUST REMAIN CLEAN (do not stage, must match committed baseline):
  out/genesis_atlas_full_repo_candidate_1545p_fix22.json    ← 10,029 nodes / 27,668 edges
```

---

## 2. What Codex Must Do

### 2.1 Commit 1 — Pre-Pass Script + Enriched Artifact Digest + Corrected Prompt

Commit the semantic pre-pass script, a digest record for the enriched candidate artifact
(under its Fix27 name, NOT overwriting Fix22), and the updated Fix27 prompt. Fix22 is NOT
staged.

**IMPORTANT — enriched artifact is gitignored:**
`out/` is in `.gitignore` (line 69). `out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json`
(35 MB) cannot be staged with plain `git add`. Two options — choose one:

**Option A (recommended): commit a digest record, not the blob.**
The scripted pre-pass portion is reproducible from the pre-pass script + Fix22 + Fix26
queue. The manual B1-B12 annotation portion is preserved in the local enriched artifact
and summarized in this handoff; full deterministic replay of those manual batches requires
a future committed manual annotation JSONL/script or explicit force-add of the 35 MB
artifact. Commit a small digest record instead:
```bash
python3 -c "
import hashlib, json
data = open('out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json','rb').read()
digest = hashlib.sha256(data).hexdigest()
record = {
  'artifact': 'genesis_atlas_enriched_candidate_1545p_fix27_prepass.json',
  'sha256': digest,
  'nodes': 10035,
  'edges': 53825,
  'phase': '1545p-Fix27',
  'note': 'Not committed (35MB, gitignored). Pre-pass is script-reproducible; manual B1-B12 requires replayable annotation data or force-added artifact.'
}
open('docs/specs/ilc_fix27_prepass_artifact_digest_v0.1.json','w').write(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n')
print('Digest written')
"
git add docs/specs/ilc_fix27_prepass_artifact_digest_v0.1.json
```

**Option B: force-add the blob (deliberate repo-bloat decision).**
Only if the team has decided to track large research artifacts in git:
```bash
git add -f out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json
```
This adds 35MB to git history permanently. Requires explicit team sign-off.

**Files to stage (Option A):**
```bash
git add tools/evaluators/sim_atlas_semantic_prepass_fix27.py
git add docs/specs/ilc_fix27_prepass_artifact_digest_v0.1.json
git add docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix27_g10_rewrite_candidate_generation.md
git add docs/specs/ilc_homoiconic_graph_loading_tiers_v0.1.md
git add docs/specs/ilc_fix27_prepass_codex_handoff_v0.1.md
```

Do NOT stage `out/genesis_atlas_full_repo_candidate_1545p_fix22.json` — it must remain at
its committed baseline.

Do NOT stage `tools/graph_viz_3d.py`, `graphify-out/`, or `lib/` unless separately scoped.

**Suggested commit message:**
```
feat(fix27-prepass): semantic pre-pass P1-P29 + manual annotations B1-B12

- P1-P29 classifier: tools/evaluators/sim_atlas_semantic_prepass_fix27.py
- Enriched artifact (gitignored, 35MB): digest at docs/specs/ilc_fix27_prepass_artifact_digest_v0.1.json
- 24,879 edges from P1-P29; 1,278 from manual B1-B12; 0 dark deferred nodes
- Fix22 baseline unchanged (10,029 nodes / 27,668 edges)
- B10-B12 fallback edges flagged for reclassification: REFERENCES_AUTHORITY → SOURCE_TREE_MEMBER
- Script now supports --annotation-graph for reproducible skip behaviour over the local enriched artifact
```

**Verify before committing:**
```bash
.venv/bin/python -m pytest tests/test_phase_1545p_fix26_axiomatic_extraction_replay.py -q
git diff --check
python3 -c "import json; g=json.load(open('out/genesis_atlas_full_repo_candidate_1545p_fix22.json')); print(f'Fix22: {len(g[\"nodes\"])} nodes / {len(g[\"edges\"])} edges')"
# Must print: Fix22: 10029 nodes / 27668 edges
git check-ignore out/genesis_atlas_full_repo_candidate_1545p_fix22.json || echo "Fix22 is not gitignored — good"
```

---

### 2.2 Commit 2 — Fix27 DPO Rewrite Candidate Generation (main execution)

After Commit 1, execute the Fix27 runner per the phase prompt at:

```
docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix27_g10_rewrite_candidate_generation.md
```

**Required deliverables:**

| File | Description |
|---|---|
| `tools/evaluators/sim_atlas_rewrite_candidate_generation_1545p_fix27.py` | DPO rewrite candidate runner |
| `out/atlas_research/genesis_atlas_rewrite_candidates_1545p_fix27.jsonl` | Candidate JSONL |
| `out/sim_atlas_rewrite_candidate_generation_1545p_fix27.json` | SIM summary JSON |
| `docs/sims/sim_atlas_rewrite_candidate_generation_1545p_fix27_v0.1.md` | SIM report |
| `docs/specs/ilc_atlas_rewrite_candidate_generation_review_1545p_fix27_v0.1.md` | Review spec |
| `tests/test_phase_1545p_fix27_rewrite_candidate_generation.py` | Gate tests |
| `docs/phases/phase_1545p_fix27_rewrite_candidate_generation_walkthrough.md` | Walkthrough |
| `docs/phases/STATUS.md` | Phase entry update |
| `docs/PLANNING_INDEX.md` | Research addendum |

**Verification commands (from prompt):**
```bash
.venv/bin/python tools/evaluators/sim_atlas_rewrite_candidate_generation_1545p_fix27.py
.venv/bin/python -m pytest tests/test_phase_1545p_fix27_rewrite_candidate_generation.py -q
.venv/bin/python tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix27_g10_rewrite_candidate_generation.md
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff --check
```

**Required output tokens (must appear in SIM JSON and all surface docs):**
```
atlas_rewrite_candidate_generation_committed_phase_1545p_fix27
atlas_dpo_invariant_checks_recorded_phase_1545p_fix27
atlas_hyperedge_replacement_candidates_recorded_phase_1545p_fix27
atlas_node_merge_split_candidates_recorded_phase_1545p_fix27
atlas_rewrite_candidates_not_promoted_phase_1545p_fix27
public_path_remains_blocked_phase_1545p_fix27
```

**Suggested commit message:**
```
Generate Atlas rewrite candidates
```

---

## 3. Key Context Codex Must Carry

### 3.1 Fix22 Is Read-Only; Fix27 Prepass Artifact Is the Enriched Input

**Fix22 baseline (read-only, committed):**
`out/genesis_atlas_full_repo_candidate_1545p_fix22.json` — 10,029 nodes / 27,668 edges.
Do NOT write to this file. Fix22 is the signing preimage baseline.

**Fix27 enriched artifact (research-only, not committed under Fix22 name):**
`out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json` — 53,825 edges.
This is the result of all pre-pass and manual annotation work. The Fix27 DPO runner
should read this as its graph context for terminal resolution and reachability checks.

The enriched artifact contains edges with provenances:
- `semantic_prepass_fix27` / `semantic_prepass_fix27_rN` — P1–P29 extraction rounds
- `manual_bucket_analysis_fix27_bN` — B1–B12 manual annotation batches

All edges in the enriched artifact are `"signature_status": "unsigned_support_only"` and
are candidate signal only. None are canon. None are signing-batch-ready.

### 3.2 Fix26 Queue Is the Candidate Input; Enriched Artifact Is the Graph Context

The DPO runner reads the Fix26 accepted queue for candidate atoms:
```
out/atlas_research/genesis_atlas_atom_candidates_1545p_fix26.jsonl
```
(5,482 accepted candidates).

For terminal resolution, reachability checks, and passage-proximity calculations, the runner
should load the **enriched Fix27 pre-pass artifact**, not Fix22:
```
out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json
```

Fix22 is used only as a reference for which edges are original canon (provenance: committed
Fix22 edges have no `provenance` field or have `provenance: null`). The enriched artifact
is a superset — it contains all Fix22 edges plus all candidate pre-pass and manual annotation
edges. The runner does not re-run the pre-pass; it reads the pre-pass results from the
enriched artifact.

### 3.3 Manual Annotations Skip Rule

Files with `manually_annotated: True` on their node record in the enriched artifact were
annotated by human reading. Files with `prepass_annotated: True` were processed by P1–P29.
The DPO runner should not generate redundant candidate edges for these nodes — check the
node flag before emitting. When the enriched artifact already has an edge for a (source,
target, edge_type) triple, the runner should record it as `already_covered` rather than
emitting a duplicate.

### 3.4 Dark-File Baseline Is Zero

The DPO runner should record in its SIM JSON that the pre-pass resolved all 486 dark files.
The baseline for its own coverage metric is: 5,482 accepted candidates as input, zero
starting dark in the enriched artifact.

### 3.5 B10–B12 Edge Type Correction

Codex audit finding: the B10–B12 manual batch edges that connect dark files to the genesis
root (`artifact:genesis_intent_attestation_init_authority_map`) used edge type
`REFERENCES_AUTHORITY`. This is too strong for files that contain no internal content
references to that authority — it conflates "this file is in the ILC repo" with
"this file makes an authority claim about Genesis."

**Correct edge type for these:** `SOURCE_TREE_MEMBER`, `DERIVED_FROM_GENESIS_REPO`, or
`ATTESTED_BY_GENESIS_OPERATOR` — a containment/provenance edge, not an authority trace.

The Fix27 DPO runner should filter and reclassify B10–B12 edges when consuming the
enriched artifact. Edges in the enriched graph with provenance `manual_bucket_analysis_fix27_b10`,
`manual_bucket_analysis_fix27_b11`, `manual_bucket_analysis_fix27_b12` and edge type
`REFERENCES_AUTHORITY` targeting `artifact:genesis_intent_attestation_init_authority_map`
should be treated as provenance candidates, not authority trace candidates.

Similarly, several P-pattern extractions (P18 global bullet paths, P19 table paths, P11
files-changed tables, P20 git diff paths) may overuse `REFERENCES_AUTHORITY` where
`EVIDENCES`, `TOUCHES_SOURCE`, or `DERIVED_FROM` would be more precise. The Fix27
precision filter (CF-A) should account for this.

### 3.6 CF-A through CF-D From the Prompt Still Apply

The carry-forward notes in the Fix27 prompt (CF-A through CF-D) are about the DPO rewrite candidate generation, not the pre-pass. They are the precision filter requirements Codex must implement in the runner:

- **CF-A**: Fix27 must implement the first real precision filter — passage-level evidence locality check
- **CF-B**: Fix26 candidates are file-level hypotheses; Fix27 must add passage-level validation records
- **CF-C**: Fix26 terminal assignment is deterministic first-hit; Fix27 must mark multi-terminal ambiguity
- **CF-D**: Deferred reason breakdown is required — do not treat all 14,958 deferred as a homogeneous bucket

### 3.7 Atlas of Cliffs Cluster — Governance Context

The Atlas of Cliffs research cluster (`docs/research/atlas_of_cliffs/`) is a distinct ILC research initiative where Genesis Agent 01 is using the ILC epistemological graph to study macroeconomic transition cliffs and corners arising from AI growth — a demonstration use case of the protocol. It is not a protocol phase; it has no ILC phase number. Its governing chain is:
```
atlas_files → econ research window spec → CDL-052 → genesis root
```
The cluster connects back to Genesis Agent 01 as its author and to `artifact:genesis_intent_attestation_init_authority_map` as the ultimate authority root. This is correct and intentional.

---

## 4. Non-Claims

This pre-pass handoff does not authorize:
- No canonical Genesis graph mutation (pre-pass edges are `unsigned_support_only`)
- No promotion of any Fix26 atom candidate
- No Genesis signing
- No public RC activation
- No CDL or ADR mutation
- No runtime activation
- No production economics activation

The graph modifications in this session are research-only semantic annotations. They carry `"signature_status": "unsigned_support_only"` on every new edge.
