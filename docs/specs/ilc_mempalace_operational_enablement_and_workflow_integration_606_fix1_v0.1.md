# ILC MemPalace Operational Enablement and Workflow Integration 606 Fix 1 v0.1

Status: bounded internal tooling enablement packet
Date: 2026-04-10
Classification: local operator workflow enablement; not protocol law

## 1. Purpose and boundary

`mempalace_local_runtime_requires_supported_python`.

This packet enables a working local MemPalace runtime for internal ILC use and
binds it to a deterministic staging-and-query workflow.

The boundary from Phase 606 remains intact:
- MemPalace is retrieval tooling only.
- Repo canon remains authoritative.
- Direct repo reads remain mandatory for final drafting and final answers.
- Wallet, payment, escrow, release, and protocol boundaries remain unchanged.

## 2. Supported local runtime

MemPalace currently supports Python 3.9-3.12. The current repo default Python
is newer, so MemPalace must run in a dedicated local virtualenv rather than the
main repo test environment.

The supported operational path is:
1. select a supported Python runtime,
2. create a dedicated MemPalace virtualenv under generated local state,
3. install `mempalace==3.1.0`,
4. verify the CLI is callable before any corpus build or query.

This separation is intentional. `main_repo_ci_must_not_require_mempalace_installation`.

## 3. Tiered corpus build workflow

`staged_tiered_corpus_build_is_required_for_authority_control`.

The supported ILC workflow is not to mine the entire repo directly into one
unlabeled palace. Instead:
- read the committed four-tier manifest,
- stage only the listed files into per-tier directories,
- write a minimal `mempalace.yaml` into each staged tier,
- mine each tier into one shared palace while preserving the tier name as the
  MemPalace wing.

This gives deterministic authority control:
- `tier_a_canonical` becomes the default direct-answer wing,
- `tier_b_planning` remains available for planning-only questions,
- `tier_c_evidence` supports walkthrough and execution provenance,
- `tier_d_historical` remains explicitly advisory.

## 4. Tiered query workflow

`mempalace_queries_must_not_override_direct_repo_reads`.

Supported query flow:
1. choose the smallest relevant tier,
2. run a tier-filtered query against the staged palace,
3. add source-path filters when a tier mixes broad planning packs with narrow
   target specs,
4. inspect the returned full source paths,
5. read the retrieved repo files directly,
6. only then turn the result into planning or drafting language.

Tier queries may emit JSON for tooling or plain text for operators. In both
modes, returned results remain retrieval hints until the source files are read
from the repo.

## 5. Prompt and window-guidance integration

`prompt_and_window_guidance_workflow_may_use_rendered_retrieval_briefs`.

Before drafting a new phase prompt or window-guidance document, operators may
run a retrieval-brief renderer against the source markdown. The rendered brief
must:
- extract direct repo file references,
- classify them by tier when possible,
- present direct reads first,
- present MemPalace query suggestions second,
- label retrieval output as advisory only.

This is an aid for forming prompts and guidance documents. It does not replace
canonical anchors, explicit repo reads, or the final human/agent drafting step.

## 6. Verification and maintenance

Operational verification for this lane requires:
- install-script success on a supported Python,
- staged-corpus build success from the committed manifest,
- at least one real tiered query against the built palace,
- successful retrieval-brief rendering from a real prompt or guidance file.

Maintenance triggers:
- update staged corpus after a new capsule, handoff, or closure window,
- update the manifest when authoritative or planning source sets change,
- keep the dedicated MemPalace runtime isolated from ordinary repo CI and
  normal Python test workflows.
