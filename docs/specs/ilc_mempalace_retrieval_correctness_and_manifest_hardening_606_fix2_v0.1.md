# ILC MemPalace Retrieval Correctness and Manifest Hardening 606 Fix 2 v0.1

Status: bounded internal tooling hardening packet
Date: 2026-04-10
Classification: local retrieval-tool correctness and workflow hardening; not protocol law

## 1. Purpose and bounded scope

`distance_values_must_not_be_labeled_as_raw_similarity`.

This packet hardens the bounded Phase 606 MemPalace workflow by correcting
retrieval-score labeling, consolidating runtime pin control, making the tiered
manifest resilient to missing local-only historical files, and expanding the
planning-tier corpus used for post-605 planning support.

The Phase 606 boundary remains unchanged:
- MemPalace is retrieval-only and non-canonical.
- direct repo reads remain mandatory before drafting or strong claims.
- ordinary repo CI must not require MemPalace installation.
- no wallet, payment, escrow, release, decision-log, or `ilc_core/` boundary is
  widened by this packet.
- wrapper scripts remain the supported ILC workflow; a generic native plugin may
  be used ad hoc by operators but does not replace the bounded wrapper path.

## 2. Retrieval score correctness

`distance_values_must_not_be_labeled_as_raw_similarity`.

The tiered query helper must preserve the raw distance value reported by the
underlying Chroma collection and must not relabel `1 - dist` as similarity.
That prior presentation was incorrect because the collection metric is not
bounded to a fixed [0, 1] similarity surface.

The supported output model is now:
- preserve raw `distance`,
- surface collection metric metadata when available,
- emit a separate bounded monotonic ranking aid as `relevance_score`,
- keep JSON and plain-text output compatible with source-path filtering.

`relevance_score` is a local ranking convenience only. It is not the collection
metric, not a semantic-truth score, and not a substitute for direct source
inspection.

## 3. Runtime dependency single source of truth

`requirements_file_is_single_source_of_truth_for_mempalace_runtime_pins`.

The dedicated local MemPalace runtime must take its package pins from one place:
`docs/tools/mempalace/requirements-mempalace.txt`.

That file now explicitly pins:
- `mempalace==3.1.0`
- `chromadb==0.6.3`

The install script must:
1. choose a supported Python 3.9-3.12 interpreter,
2. create a dedicated local virtualenv,
3. install from the requirements file,
4. verify the `mempalace` CLI before reporting success.

This keeps runtime pinning reviewable, testable, and independent from ordinary
repo Python tooling.

## 4. Manifest resilience for local-only historical material

`optional_manifest_entries_allow_local_historical_absence_without_tier_failure`.

The corpus manifest may express include entries as either:
- a plain string path, or
- an object with `path` and optional `optional` fields.

Builder behavior is fixed as follows:
- missing required files fail hard with a clear error,
- missing optional files record a warning and do not fail the tier,
- malformed include entries fail with explicit human-readable messages,
- malformed tiers missing `include` fail with explicit human-readable messages.

This is required because Tier D contains local-only provenance material that may
not exist on a fresh clone or after generated-output cleanup.

## 5. Planning-tier expansion and retrieval-brief coverage

`tier_b_planning_manifest_expansion_is_required_for_window_606_plus_utility`.

The original three-file Tier B corpus was too thin for meaningful planning
retrieval. Tier B is expanded so that Window 606+ planning can search across:
- approved planning packs,
- current roadmap material,
- current and adjacent candidate groupings,
- current and adjacent sequence locks,
- the window-guidance schema.

`retrieval_brief_path_extraction_must_cover_simulations_and_other_repo_files`.

The retrieval-brief renderer must no longer rely on a narrow prefix whitelist.
It must recognize any repo-relative file path directly referenced in markdown,
including `simulations/...`, while still excluding URLs, absolute paths, and
non-file directories.

Planning support remains bounded:
- canonical anchors still lead,
- retrieval briefs stay advisory,
- wrapper-script staging/query flow remains the supported reproducible path.

## 6. Verification and maintenance

Verification for this packet requires:
- prompt validation,
- artifact and boundary checks,
- targeted tests for score semantics, manifest resilience, and path extraction,
- successful dedicated-runtime installation from the requirements file,
- successful Tier B mining,
- successful Tier D staging with optional missing files tolerated,
- a real tiered query using the hardened output fields,
- retrieval-brief rendering from a real prompt.

Maintenance triggers:
- update Tier B when the active planning frontier changes,
- update Tier A and Tier C after new handoffs, capsules, or walkthroughs land,
- review Tier D optional entries after migration or cleanup events,
- keep native plugin usage, if any, subordinate to the bounded wrapper workflow.
