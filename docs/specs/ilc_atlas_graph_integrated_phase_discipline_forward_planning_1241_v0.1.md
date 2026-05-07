# ILC Atlas Graph Integrated Phase Discipline — Forward Planning 1241+ v0.1

**Status:** Planning-only forward plan.
**Recorded:** 2026-05-07.
**Authority:** Current canon remains `PLANNING_INDEX.md`, `STATUS.md`, active
window guidance/sequence lock, the CDL register, signed Genesis artifacts, and the
latest context capsule. This document does not mutate Genesis, regenerate the Atlas,
authorize v0.2 signing, authorize public RC, or change any CDL.

`atlas_graph_integrated_phase_discipline_forward_planning_recorded_phase_1238`

---

## 1. Purpose

The public-RC packaging strategy requires ILC Core to be modular but not
excisable: Genesis, ILC Coin, ECU, truth primitives, canonical JSON, Rust
consensus core, and the hypergraph substrate must remain load-bearing and
machine-verifiably reachable.

The organizing driver is:

```text
public_rc_load_bearing_artifacts_must_be_reachable_from_genesis_ilc_ecu_hypergraph_anchors
```

This is not a "more nodes" objective. It is a reachability and
non-excisability objective: every public-RC load-bearing artifact must have an
explainable typed path from Genesis / ILC / ECU / Hypergraph anchors.

---

## 2. Current Baseline

Current verified baseline, as of 2026-05-07:

- Signed Genesis star map v0.1 remains canonical: 32 nodes, 55 edges.
- Unsigned Genesis Atlas v0.2 candidate exists: 41 nodes, 73 edges.
- Observed repo/governance hypergraph artifact exists:
  `out/genesis_observed_repo_hypergraph_v0.1.json`.
- Current observed repo/governance hypergraph counts in the dirty worktree:
  2,014 vertices, 5,487 hyperedges, 11,580 incidence records.
- Current GENESIS-COMPILE verdict remains `PARTIAL_WITH_STRUCTURAL_GAPS`.
- Current compile coverage diagnostic records 640 / 1,944 observed source files
  with any core-star-map link, and 313 / 1,944 basis-explainable source files.

Boundary:

```text
signed_genesis_v0_1_remains_canonical_until_explicit_v0_2_signing_authorization
```

---

## 3. Integrated Phase Discipline

Every phase close should declare a graph delta. The valid declarations are:

```text
graph_delta=none:<reason>
graph_delta=support_only:<paths>
graph_delta=load_bearing_artifact_added:<path> -> <anchor>
graph_delta=load_bearing_artifact_changed:<path> -> <anchor>
graph_delta=deferred:<token>
```

Rules:

- If a phase adds or changes a public-RC load-bearing artifact, it must either
  update the graph manifest/projection or emit a graph carry-forward token.
- If a phase has no graph impact, it must say why.
- `graph_delta=none` is acceptable only when the phase creates no load-bearing
  protocol, economic, packaging, signing, public-RC, or release artifact.
- Graph deltas are phase-close metadata, not automatic Genesis mutation.

ATLAS-G-001 should implement the validator for this discipline.

Token:

```text
phase_close_graph_delta_field_required
```

---

## 4. Atlas-G Strike Force Series

The Graph/Atlas lane should run as a parallel strike-force lane after Window
1233-1240 closes. It owns the map; normal phases leave breadcrumbs.

### ATLAS-G-001 — Graph Reachability Policy and Phase Schema

Scope:

- Add formal graph-delta schema for phase walkthroughs and STATUS entries.
- Add validator tests requiring graph-delta fields.
- Add prompt-template language for graph impact declarations.
- Keep the first pass non-mutating.

Tokens:

```text
atlas_g_001_graph_delta_schema_required
phase_close_graph_delta_field_required
graph_delta_validator_required_before_public_rc
```

### ATLAS-G-002 — Deterministic Repo Hypergraph Compiler Hardening

Scope:

- Harden `tools/compare_genesis_star_map_to_repo_graph.py` and adjacent compiler
  tooling.
- Ensure deterministic canonical JSON output with stable counts.
- Classify generated artifacts, tests, runtime files, docs, ADRs, CDLs, Rust
  crates, and package profiles.
- Preserve no-network, no-wall-clock, no-float, bounded-output expectations.

Tokens:

```text
atlas_g_002_repo_hypergraph_compiler_hardening_required
observed_repo_hypergraph_canonical_export_required
```

### ATLAS-G-003 — Public-RC Package Profile Reachability Manifest

Scope:

- Generate reachability manifests for `openclaw_skill_local` and
  `openclaw_skill_claimable`.
- Map package profile components to files, modules, CLI entrypoints, Rust crate
  surfaces, and graph anchors.
- Confirm non-excisable components are present in each declared profile.

Tokens:

```text
atlas_g_003_package_profile_reachability_manifest_required
openclaw_skill_claimable_graph_manifest_required
```

### ATLAS-G-004 — High-Authority Gap Closure

Scope:

- Classify all high-authority ADR/CDL/runtime/economic/package files as
  core/support/archive.
- Close high-authority unlinked source samples or explicitly mark them support.
- Preserve support/history distinction so Genesis core does not become a raw
  file dump.

Tokens:

```text
atlas_g_004_high_authority_gap_closure_required
high_authority_sources_must_be_core_support_or_archive_classified
```

### ATLAS-G-005 — Import and Dependency Graph Bridge

Scope:

- Add Python import graph edges.
- Add Rust crate/module dependency edges.
- Add CLI entrypoint and package export edges.
- Connect package modularity Gap 14 to the Atlas graph.

Tokens:

```text
atlas_g_005_import_dependency_graph_bridge_required
package_modularity_edges_required_for_public_rc_graph
```

### ATLAS-G-006 — Public-RC Graph Reachability Gate

Scope:

- Fail closed if the selected public-RC profile has unreachable load-bearing
  artifacts.
- Check reachability from Genesis / ILC / ECU / Hypergraph anchors.
- Treat research/docs/history as support edges, not mandatory core.

Tokens:

```text
atlas_g_006_public_rc_graph_reachability_gate_required
selected_public_rc_profile_must_pass_graph_reachability_gate
```

### ATLAS-G-007 — Unsigned Genesis Atlas Candidate Regeneration

Scope:

- Regenerate the unsigned candidate from compiler output.
- Produce candidate manifest and diff against signed v0.1.
- Do not sign.

Token:

```text
atlas_g_007_unsigned_v0_2_plus_candidate_regeneration_required
```

### ATLAS-G-008 — Non-Excisability Review Packet

Scope:

- Human-review packet for Genesis / ILC / ECU / Hypergraph non-excisability.
- Explicitly separate packaging integrity from fork prevention.
- Link to Genesis lineage, CDL authority, and licensing/IP gates.

Token:

```text
atlas_g_008_non_excisability_review_packet_required
```

### ATLAS-G-009 — Signing Root Envelope Prep

Scope:

- Prepare signing root envelope, manifest, and verification checklist.
- Do not generate release keys or sign without explicit authorization.

Token:

```text
atlas_g_009_signing_root_envelope_prep_required_no_signing
```

### ATLAS-G-010 — v0.2 Signing Ceremony

Scope:

- Execute only if explicit signing authorization is issued.
- Remains SENSITIVE.

Token:

```text
atlas_g_010_v0_2_signing_only_if_explicitly_authorized
```

---

## 5. Window Placement

Recommended placement:

| Window band | Atlas-G scope |
|-------------|---------------|
| 1241-1248 | ATLAS-G-001 to ATLAS-G-003 |
| 1249-1256 | ATLAS-G-004 to ATLAS-G-005, parallel to TransportPrincipal |
| 1265-1272 | ATLAS-G-006 with package modularity/harness adapter gates |
| 1289-1296 | ATLAS-G-007 to ATLAS-G-010 if signing is authorized |

The active Window 1233-1240 should only carry this forward through Phase 1239
coherence/capsule and Phase 1240 closure. No Atlas mutation or v0.2 signing is
authorized in this document.

---

## 6. Homoiconic Self-Compilation Model

The final public-RC ILC package should compile itself into a machine-verifiable
graph artifact:

1. Select package profile (`openclaw_skill_local`, `openclaw_skill_claimable`,
   or later full-node profile).
2. Scan declared files, Python imports, Rust crates, CLI entrypoints, ADR/CDL
   references, tests, and release manifests.
3. Emit typed nodes: files, symbols, modules, crates, package profiles, CDLs,
   ADRs, truth primitives, Genesis/ILC/ECU anchors.
4. Emit typed edges/hyperedges: `DECLARES`, `IMPLEMENTS`, `TESTS`,
   `DEPENDS_ON`, `GOVERNED_BY`, `ANCHORS`, `EXPORTS`, `NON_EXCISABLE_WITH`.
5. Validate reachability from Genesis / ILC / ECU / Hypergraph anchors.
6. Export canonical JSON with deterministic ordering and no float values.
7. Compute Merkle/Laplacian commitment through the Rust consensus core when the
   binding profile is available.
8. Bundle the profile-specific graph into release artifacts.

This is the practical homoiconic contract: the package contains a canonical graph
of what it is, why each load-bearing piece belongs, and how each piece derives
from the non-excisable anchors.

Tokens:

```text
ilc_package_self_compilation_homoiconic_graph_required_before_public_rc
public_rc_release_artifact_must_include_profile_graph_manifest
```

---

## 7. Non-Claims

This planning artifact does not:

- mutate signed Genesis v0.1;
- sign Genesis Atlas v0.2 or later;
- authorize release-key generation;
- authorize public RC;
- authorize public repository publication;
- authorize public P2P exposure;
- mutate the CDL register;
- require every repo file to become Genesis-core.

It records the recurring discipline and the ATLAS-G strike-force lane required
to make public-RC non-excisability machine-verifiable.
