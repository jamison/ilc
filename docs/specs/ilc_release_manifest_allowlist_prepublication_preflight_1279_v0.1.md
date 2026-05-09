# ILC Release Manifest Allowlist Prepublication Preflight 1279 v0.1

**Date:** 2026-05-09
**Phase:** 1279
**Status:** prepublication inventory and validation only; no publication or release artifact authority
**Window lock:** `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md`

```text
release_manifest_allowlist_publication_preflight_phase_1279.v0.1
public_repository_publication_not_authorized_phase_1279
release_artifact_production_not_authorized_phase_1279
v0_2_signing_not_authorized_phase_1279
source_allowlist_export_not_executed_phase_1279
release_keys_not_generated_phase_1279
release_envelope_not_produced_phase_1279
genesis_atlas_mutation_not_authorized_phase_1279
public_rc_remains_blocked_after_phase_1279
```

## 1. Verdict

Phase 1279 records the release manifest and source allowlist prepublication
state after ATLAS-G-006 graph reachability passed and after CDL-087 ratification.
The verdict is inventory-only:

```text
release_manifest_prepublication_verdict_phase_1279=inventory_ready_publication_blocked
source_allowlist_prepublication_verdict_phase_1279=procedure_defined_execution_blocked
public_release_path_phase_1279=blocked_pending_counsel_publication_signing_and_final_claimability_authority
```

Phase 1279 does not publish source, produce release artifacts, generate release
keys, produce a release envelope, mutate or sign Genesis Atlas, sign v0.2, or
make a public-RC claim.

## 2. Direct-Read Canon Basis

| Source | Phase 1279 use |
|--------|----------------|
| `docs/PLANNING_INDEX.md` | Current frontier and next-phase routing after Phase 1278 Fix1. |
| `docs/phases/STATUS.md` | Actual phase history through Phase 1278 Fix1. |
| `docs/specs/ilc_antigravity_context_capsule_v5.50.md` | Latest published capsule; older CDL-087 status superseded by current register. |
| `docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md` | Authority boundary for Phase 1279 inventory-only preflight. |
| `docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md` | Phase 1279 scope and non-claims. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Current public-RC blocker classes and post-Fix1 status. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-086 and CDL-087 ratified governance state. |
| `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md` | Future release artifact manifest schema; no artifact produced here. |
| `docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md` | Future distribution checks; no distribution attempted here. |
| `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md` | Allowlist-export procedure; execution remains blocked. |
| `docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md` | Selected-profile graph reachability pass with release artifacts blocked. |
| `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md` | CDL-087 ratified; public fetch/sidecar/projection still blocked. |

## 3. Discovery Audit

Exact-token `rg` was used only as a schema/completion check. Phase 1279 also
searched and direct-read broader concepts around:

```text
release manifest
source allowlist
allowlist export
publication
public repository
public package
release artifact
release key
release envelope
Genesis Atlas
v0.2 signing
ATLAS-G-006
openclaw_skill_claimable
CDL-086
CDL-087
license
CLA
trademark
patent
counsel
```

Contradiction and non-claim discovery searched:

```text
not authorized
blocked
deferred
no public
not published
no release artifact
no release key
no signing
unsigned
counsel
license
CLA
trademark
allowlist
```

The discovery result is consistent: prior artifacts define schemas, procedures,
and graph evidence, but no current canon authorizes source publication, release
artifact production, release keys, release envelopes, Genesis Atlas mutation or
signing, v0.2 signing, or a public-RC claim.

## 4. Prepublication Inventory

| Surface | Current evidence | Phase 1279 disposition |
|---------|------------------|------------------------|
| Release artifact manifest schema | `release_artifact_manifest_schema_committed_phase_1213` | Schema exists; no manifest instance or artifact is produced. |
| Distribution channel checklist | `distribution_channel_integrity_checklist_committed_phase_1213` | Checklist exists; no distribution attempt or pass/fail evidence record is produced. |
| CDL-086 release governance | `cdl_086_ratified_phase_1220` | Governance basis exists; counsel/IP/publication gates still block public release acts. |
| Source allowlist-export procedure | `allowlist_export_procedure_defined_phase_1255` | Procedure exists; export execution remains blocked. |
| ATLAS-G-006 graph reachability | `atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1` | Selected profile passes graph gate only; release artifacts remain blocked. |
| CDL-087 canonical fetch distribution | `cdl087_ratified_phase_1278_fix1` | Governance blocker cleared; public fetch/sidecar/projection serving remains separately blocked. |
| v0.2 signing | `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Signing remains unauthorized. |

## 5. Prepublication Gate Matrix

| Gate | Required before publication/release | Current state |
|------|-------------------------------------|---------------|
| Counsel license instruments | Counsel-approved final license instruments and per-zone markings. | Open. |
| CLA or no-external-contributor policy | Counsel-approved contributor agreement or explicit no-external-contributor policy. | Open. |
| Trademark and identity policy | Approved canonical identity and trademark/fork labeling policy. | Open. |
| Patent/publication review | Required filings or explicit no-file decision before disclosure. | Open. |
| Source allowlist manifest | Reviewed include/exclude manifest with deterministic dry-run evidence. | Procedure defined; manifest execution not authorized. |
| Release artifact manifest | Artifact-specific manifest conforming to Phase 1213 schema. | Schema exists; no artifact manifest produced. |
| Release keys and envelope | ADR-0036-bound key/envelope generation with explicit authority. | Not authorized. |
| Genesis Atlas / v0.2 signing | Explicit signing ceremony authorization after Atlas-G tail. | Deferred. |
| Final public claimability authority | Public claimability API/verifier and claimability runtime authority. | Still blocked. |
| Final public-RC claim | Explicit human/publication authorization naming exact commit and destination. | Absent. |

## 6. Candidate Dry-Run Manifest Shape

The future dry-run manifest should use canonical JSON if machine-verifiable:

```text
json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))
```

Required future fields:

| Field | Rule |
|-------|------|
| `schema_version` | `ilc_public_source_allowlist_manifest.v0.1` or successor. |
| `source_commit` | Full commit hash selected for a future dry run. |
| `capsule` | Current capsule at the future freeze point. |
| `mode` | `dry_run` by default; `authorized_publication` only with later explicit authority. |
| `include_rules` | Ordered repo-relative selectors. |
| `exclude_rules` | Ordered repo-relative deny selectors; deny wins over include. |
| `review_required` | Counsel, patent, trademark, Genesis, or publication-review routes. |
| `license_zone_map` | Counsel-approved license zone map, not inferred automatically. |
| `file_hashes` | SHA-256 for every materialized exported file after a future dry run. |
| `non_claims` | Explicit statement that dry-run evidence is not publication authority. |

Path selectors must be repo-relative, must not be absolute, must not escape the
repo root through `..`, and must reject symlink traversal during any future
materialization.

## 7. Default Exclusion Inventory

Future publication dry runs must continue to exclude, unless explicitly reviewed
and allowlisted later:

- files marked `PUBLIC_RC_EXCLUDE`;
- `docs/antigravity_tasks/`;
- `docs/phases/` unless a specific public transparency excerpt is authorized;
- `docs/research/patent_pending/`;
- unpublished paper drafts and patent-sensitive research;
- raw chats, memory corpora, local context packs, and private transcript derivatives;
- `out/`, local monitoring snapshots, generated diagnostics, caches, and scratch outputs;
- `.env*`, private keys, TLS keys, release keys, local certificates, `.venv/`, editor state, and OS metadata;
- unsigned release envelopes, draft release manifests, signing ceremony material, and claimability artifacts until their independent gates close;
- ambiguous roadmap, counsel, licensing, and research drafts pending human review.

## 8. Non-Claims

Phase 1279 records these boundary tokens:

```text
public_repository_publication_not_authorized_phase_1279
release_artifact_production_not_authorized_phase_1279
v0_2_signing_not_authorized_phase_1279
source_allowlist_export_not_executed_phase_1279
release_keys_not_generated_phase_1279
release_envelope_not_produced_phase_1279
genesis_atlas_mutation_not_authorized_phase_1279
public_rc_remains_blocked_after_phase_1279
```

Phase 1279 does not authorize:

- public repository publication;
- public package publication;
- public release artifact production;
- source allowlist export execution;
- public RC claim;
- public launch claim;
- release-key generation;
- release envelope production;
- release artifact manifest instance production;
- distribution channel evidence-record production;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- public claimability API activation;
- wallet withdrawal, transfer, or spend semantics;
- ECU minting;
- ILC settlement or withdrawal runtime activation;
- CDL mutation;
- CDL-088 opening.

## 9. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md -> release/publication
graph_delta=support_tests_added:tests/test_phase_1279_release_manifest_allowlist_prepublication_preflight.py -> validation
graph_delta=support_tests_changed:tests/test_window_1273_1280_prompt_drafts.py -> validation/frontier
graph_delta=support_only:docs/phases/phase_1279_release_manifest_allowlist_prepublication_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_phase_1273_1280_sequence_lock_v0.1.md -> planning/frontier
```

## 10. Next

Phase 1280 remains the next locked phase:

```text
window_1273_1280_closure_gate_phase_1280
```

Phase 1280 is sensitive and requires explicit `GO Phase 1280`. It must close
or carry forward public-RC blockers honestly without converting this inventory
preflight into publication authority.
