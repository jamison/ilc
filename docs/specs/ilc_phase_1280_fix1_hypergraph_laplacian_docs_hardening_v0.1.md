# ILC Phase 1280 Fix1 Hypergraph/Laplacian Docs Hardening v0.1

Status: docs-only hardening and forward-planning registry
Date: 2026-05-09
Phase: 1280 Fix1
Classification: sensitive docs-only planning, IP/publication boundary
Human authorization: `GO Phase 1280 Fix1`

This packet is a planning/control artifact. It does not publish source, produce
release artifacts, generate release keys, produce release envelopes, mutate
Genesis, sign v0.2, open or mutate any CDL row, activate public fetch serving,
activate public sidecar/projection serving, activate public claimability, mint
ECU, settle ILC, or make a public-RC claim.

```text
phase_1280_fix1_hypergraph_laplacian_docs_hardened
h_series_020_plus_registered_phase_1280_fix1
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
public_rc_candidate_standard_preserved_phase_1280_fix1
```

## 1. Purpose

Phase 1280 closed Window 1273-1280, but follow-up review found stale
hypergraph/Laplacian and Atlas-G planning text. Phase 1280 Fix1 corrects those
records without opening Window 1281-1288 and without widening runtime or release
authority.

The phase has three goals:

- Harden seven existing documents with current-status addenda and obvious stale
  claim fixes.
- Register H-020+ as the continuation lane for technical
  hypergraph/Laplacian work.
- Register IP-001+ as the separate patent/publication-prep lane so IP work is
  tracked without becoming an accidental public-RC blocker or disclosure.

## 2. Documents Hardened

| Document | Phase 1280 Fix1 disposition |
|----------|-----------------------------|
| `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md` | Added `PUBLIC_RC_EXCLUDE`, fixed malformed `Δ` emphasis, added current-status addendum, and marked SIM-awaiting text as historical. |
| `docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.7.md` | Added current-status addendum, corrected CDL-085 status to later ratified, and marked Window 1139-1147 snapshot as historical. |
| `docs/research/ilc_hypergraph_implementation_lane_h_series_v0.1.md` | Added H-020+ continuation addendum, corrected primary planning authority to v0.7, marked H-CON-01/H-CON-02 as resolved, and moved patent assessment to IP lane. |
| `docs/research/ilc_subgraph_laplacian_research_memo_791_v0.1.md` | Added H-027 routing addendum for named subgraph commitments and sparse eigensolver planning. |
| `docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md` | Added consumed/future ATLAS-G status addendum and marked original baseline as historical. |
| `docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md` | Added consumed/future ATLAS-G status addendum and marked ATLAS-G-001..006 as consumed. |
| `docs/specs/ilc_dynamic_epistemic_traversal_engine_forward_planning_1241_v0.1.md` | Added current-status addendum, corrected stale CDL-087 non-ratification language, and kept DTE unscheduled. |

## 3. H-Series Continuation Registry

The H-series remains the technical hypergraph/Laplacian lane. H-001 through
H-019 are historical lane items. H-020 through H-028 are the current
continuation registry after Phase 1280 Fix1.

| H phase | Name | Scope | Default gate |
|---------|------|-------|--------------|
| H-020 | Hypergraph/Laplacian current-state reconciliation and tracker refresh | Build the consolidated live tracker from v0.7, H-series, CDL register, STATUS, and paper status. | Docs-only; no runtime or CDL mutation. |
| H-021 | Dual hypergraph utility `compute_dual()` | Add analytics-only pure utility for vertex/hyperedge dual representation. | No CDL; exact deterministic tests required. |
| H-022 | Incremental structural proof-chain implementation plan | Specify `compute_laplacian_delta()`, `perturbation_norm`, and proof-chain artifacts. | No epoch-commitment mutation; no public claim. |
| H-023 | Spectral hash CDL preflight | Prepare successor to H-007 for spectral hash in epoch commitment. | Human authorization required before CDL opening. |
| H-024 | PoSK CDL preflight | Prepare successor to H-008 for λ₂/PoSK admission. | Blocked by IP/counsel posture and explicit human authorization. |
| H-025 | SIM-REUSE-01 commissioning | Calibrate `reuse_count` functional form, caps/floors, and gaming resistance. | Simulation authorization required. |
| H-026 | EdgeType coefficient / reuse cap CDL preflight | Prepare constitutional parameters for type coefficients and reuse caps. | Requires SIM-REUSE-01 evidence. |
| H-027 | Named subgraph Laplacian sparse-eigensolver plan | Plan bounded named subgraph roots, sparse construction, approximate eigensolvers, and batching. | Research/spec only before CDL or runtime commitment. |
| H-028 | Star expansion authorization preflight | Reconcile `expand_to_star_node()` gates and public/IP posture. | Blocked by IP/counsel posture and explicit human authorization. |

## 4. IP Lane Registry

The IP lane is separate from H-series and ATLAS-G. These phases produce internal
filing/publication-prep packets only. They are not public-RC package contents
unless later explicitly cleared.

| IP phase | Name | Scope | Public-RC status |
|----------|------|-------|------------------|
| IP-001 | IP inventory and disclosure-control map | Identify invention areas, source docs, public-disclosure risk, and `PUBLIC_RC_EXCLUDE` boundaries. | Internal only. |
| IP-002 | Merkle-Laplacian dual commitment provisional draft package | Draft filing packet around content+structure dual commitment and incremental structural proof chain. | Internal only. |
| IP-003 | Proof of Structural Knowledge provisional draft package | Draft filing packet around validator/agent structural-knowledge admission and attestation. | Internal only. |
| IP-004 | Sealed spectral beacon and spectral routing provisional draft package | Draft filing packet around privacy-preserving spectral beaconing and routing. | Internal only. |
| IP-005 | Homoiconic star map / star expansion provisional draft package | Draft filing packet around hyperedge-as-entity, star maps, and graph-native entity promotion. | Internal only. |
| IP-006 | Publication clearance matrix | Decide what papers, preprints, docs, snippets, or source packages may become public after filing/counsel review. | Internal until cleared. |

IP lane files should carry this marker by default:

```text
PUBLIC_RC_EXCLUDE: internal_ip_publication_planning_not_public_rc_launch_surface
```

## 5. Public-RC Boundary

The public-RC candidate standard remains full-strength. Phase 1280 Fix1 does
not record or authorize any reduced public-RC posture. It records only that
publication/IP tasks are tracked separately and remain pending until explicit
filing/counsel/publication decisions.

The public-RC path remains blocked by the current Phase 1280 blocker set:

- public claimability verifier/API authority
- public sidecar/projection serving authorization
- TransportPrincipal public-path activation
- Rust M-5/public-P2P hostile-network hardening
- counsel/IP/publication authorization
- source publication/release artifact authorization
- v0.2 signing authorization

## 6. Non-Authorization Boundary

This packet does not:

- open Window 1281-1288;
- execute Phase 1281;
- mutate any CDL row;
- open CDL-088;
- authorize public RC;
- authorize public repository publication;
- authorize public package publication;
- authorize public P2P exposure;
- authorize public fetch serving;
- authorize public sidecar/projection serving;
- activate public claimability;
- enable wallet withdrawal, transfer, or spend;
- authorize ECU minting;
- authorize ILC settlement or withdrawal runtime;
- generate release keys;
- produce release envelopes;
- produce public release artifacts;
- mutate signed Genesis v0.1;
- regenerate or sign Genesis Atlas v0.2+;
- file any patent application;
- publish, submit, or preprint any paper;
- remove `PUBLIC_RC_EXCLUDE` from IP/publication-sensitive material;
- authorize v0.2 signing.

## 7. Carry-Forward Tokens

```text
phase_1280_fix1_hypergraph_laplacian_docs_hardened
h_series_020_plus_registered_phase_1280_fix1
ip_lane_001_plus_registered_phase_1280_fix1
publication_ip_boundary_tracked_without_public_rc_activation_phase_1280_fix1
public_rc_candidate_standard_preserved_phase_1280_fix1
h020_hypergraph_laplacian_tracker_refresh_registered
h021_dual_hypergraph_utility_registered
h022_incremental_structural_proof_chain_plan_registered
h023_spectral_hash_cdl_preflight_registered
h024_posk_cdl_preflight_ip_gated_registered
h025_sim_reuse_01_commissioning_registered
h026_edge_type_coefficient_reuse_cap_cdl_preflight_registered
h027_named_subgraph_laplacian_sparse_eigensolver_plan_registered
h028_star_expansion_authorization_preflight_registered
ip001_ip_inventory_disclosure_control_registered
ip002_merkle_laplacian_provisional_draft_registered
ip003_posk_provisional_draft_registered
ip004_sealed_spectral_beacon_routing_provisional_draft_registered
ip005_homoiconic_star_expansion_provisional_draft_registered
ip006_publication_clearance_matrix_registered
public_rc_remains_blocked_after_phase_1280_fix1
```

## 8. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md -> planning/frontier
graph_delta=support_only:docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md -> research/ip
graph_delta=support_only:docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.7.md -> research/hypergraph
graph_delta=support_only:docs/research/ilc_hypergraph_implementation_lane_h_series_v0.1.md -> research/hypergraph
graph_delta=support_only:docs/research/ilc_subgraph_laplacian_research_memo_791_v0.1.md -> research/hypergraph
graph_delta=support_only:docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md -> planning/atlas_g
graph_delta=support_only:docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md -> planning/atlas_g
graph_delta=support_only:docs/specs/ilc_dynamic_epistemic_traversal_engine_forward_planning_1241_v0.1.md -> planning/dte
graph_delta=support_only:docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1280_fix1_hypergraph_laplacian_docs_hardening_walkthrough.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1280_fix1_hypergraph_laplacian_docs_hardening.py -> validation
```
