# ILC ATLAS-G-004/005 High-Authority Dependency Bridge 1254 v0.1

- Version: `atlas_g_004_005_dependency_bridge_1254.v0.1`
- Status: `pass`
- Scope: unsigned ATLAS-G planning/validation artifact; no Genesis Atlas v0.2 regeneration or signing.

## Required Tokens

- `atlas_g_004_high_authority_gap_closure_committed_phase_1254`
- `atlas_g_005_import_dependency_graph_bridge_committed_phase_1254`
- `phase_1254_legacy_graph_delta_gap_disposition_recorded`
- `phase_1254_atlas_g_004_005_complete`

## High-Authority Source Classification

- Policy token: `high_authority_sources_must_be_core_support_or_archive_classified`
- Source count: `39`
- Core sources: `23`
- Support sources: `12`
- Archive sources: `4`
- Classification classes are `core/support/archive` to separate current controlling canon, support evidence, and superseded/closed-window context.

| Class | Example source | Role |
| --- | --- | --- |
| `core` | `AGENTS.md` | current controlling canon, runtime contract, package profile, or active ATLAS-G compiler surface |
| `support` | `docs/antigravity_tasks/antigravity_prompt__atlas_g_004_high_authority_gap_closure.md` | phase evidence, prompt contract, validation, or status surface supporting current canon |
| `archive` | `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md` | superseded or closed-window context retained for history but not controlling current execution |

## Import And Dependency Bridge

- Policy token: `package_modularity_edges_required_for_public_rc_graph`
- Edge count: `343`
- Edge types: `high_authority_source_classified_as, package_component_reachable_from_anchor, package_profile_exports_surface, package_profile_requires_component, python_cli_entrypoint, python_surface_imports_root, rust_binary_entrypoint, rust_crate_dependency`
- Python import roots are derived from the existing bounded import-boundary inventory.
- Python CLI entrypoint edges are derived from `pyproject.toml` `[project.scripts]`.
- Rust crate dependency and binary entrypoint edges are derived from `ilc_consensus/Cargo.toml`.
- Package export and non-excisable component edges are derived from `ilc_core/rc/package_profiles.py` and reachability manifests.

## Legacy graph_delta Disposition

- Finding: `RCGAP-1250-FIX1-002`
- Token: `phase_1254_legacy_graph_delta_gap_disposition_recorded`
- Missing legacy closure/handoff files: `129`
- Bulk legacy backfill authorized: `False`
- Disposition: preserve archive classification and avoid bulk history rewrites; enforce graph_delta on current/future phase close and backfill legacy docs only when they become current authority or are touched by scoped work.
- Concept label: legacy graph_delta hygiene.

## Non-Authorization Boundary

- `no_signed_genesis_v0_1_mutation`
- `no_genesis_atlas_v0_2_regeneration`
- `no_v0_2_signing`
- `no_immutable_diagnostic_mutation`
- `no_public_rc_claim`
- `no_public_repository_publication`
- `no_public_p2p_exposure`
- `no_public_sidecar_projection_serving`
- `no_public_claimability_activation`
- `no_cdl_mutation`

## Artifact Paths

- Canonical JSON: `docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.json`
- Summary: `docs/specs/ilc_atlas_g_004_005_high_authority_dependency_bridge_1254_v0.1.md`
