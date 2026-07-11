# ILC Public-RC Atlas Slice Readiness Gate 1575b-Fix3 v0.1

Status: committed readiness gate, unsigned fixture evidence

Phase: 1575b-Fix3

Date: 2026-07-11

Sensitivity: NON-SENSITIVE

## Purpose

This gate proves that public-RC launch planning can rely on bounded
AtlasSliceManifest fixtures instead of requiring full private Atlas graph
completion before publication.

The launch standard is slice readiness:

- Core Public-RC Slice readiness.
- Economic Soft-RC Slice readiness.
- Explicit exclusions and carry-forward boundaries.
- Deterministic manifest commitments.
- No private material in public fixtures.
- Recipe coverage or explicit exemption for every fixture entry.

Full Atlas graph completion remains valuable, but it is not a pre-1575c blocker
unless the signed public-RC package depends on a node outside the bounded slices.

## Sequence Correction

The original 1575b-Fix3 prompt listed these as hard preconditions:

- `public_rc_economic_intent_reconciled_phase_1574_fix1`
- `private_economic_soft_rc_gate_defined_phase_1574_fix1`
- `economic_activation_certificate_complete_phase_1575b`

Direct status read during execution found those tokens absent. That is expected
under the current corrected launch order because 1575b-Fix3 is being prepared
before the sensitive economic activation sequence is executed.

Therefore, this phase is a readiness-audit and fixture phase only. The fixtures
are valid inputs for later installer work, but they are not sufficient for
public-RC publication until the missing economic-intent and activation-certificate
tokens exist.

## Canonical Readiness Boundary

Current ILC Atlas graph is partially homoiconic at whole-repo scale.

The Genesis/core star-map and selected runtime surfaces are much closer to
homoiconic.

Public RC requires bounded slice readiness, not full graph completion.

## Direct Read Authority Set

| Path | Role in this gate |
| --- | --- |
| `docs/PLANNING_INDEX.md` | Corrected pre-public-RC phase order and slice-readiness routing. |
| `docs/specs/ilc_window_1576_plus_forward_plan_v0.1.md` | Window 1576+ carry-forward context. |
| `docs/specs/ilc_signed_atlas_slice_manifest_executable_map_forward_plan_v0.1.md` | Manifest-first architecture: identity, integrity, availability, authorization. |
| `docs/specs/ilc_atlas_slice_manifest_build_pipeline_v0.1.md` | AtlasSliceManifest build and verification contract. |
| `docs/specs/ilc_whole_graph_atlas_objective_contract_1545p_fix24_v0.1.md` | Typed trace and proof-class standard. |
| `docs/sims/sim_atlas_axiomatic_calibration_1545p_fix19_v0.1.md` | Seven truth primitive basis and recipe library. |
| `docs/sims/sim_atlas_axiomatic_extraction_replay_1545p_fix26_v0.1.md` | Whole-repo extraction replay and candidate limitations. |
| `docs/sims/sim_spectral_02/genesis_graphopt_01_synthesis_report_v0.1.md` | Governance decomposition recipe precedent. |
| `docs/sims/sim_spectral_02/genesis_node_candidate_inventory_v0.3_candidate.md` | Genesis node inventory and partial source-coverage boundary. |
| `docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md` | Ledger node kinds and edge namespace. |
| `ilc_core/bundle/atlas_slice_manifest.py` | Current manifest builder/parser/verifier runtime. |
| `tests/test_atlas_slice_manifest.py` | Existing manifest determinism and bool/int hardening tests. |

## Fixture Set

| Fixture | Slice role | Publication status | Consumption boundary |
| --- | --- | --- | --- |
| `tests/fixtures/starmap/core_public_rc_slice_fixture.json` | Core public protocol/bootstrap readiness fixture | Unsigned test fixture | May be consumed by 1575b-Fix4 installer tests; must be replaced or signed by 1575c before publication. |
| `tests/fixtures/starmap/economic_soft_rc_slice_fixture.json` | Economic soft-RC evidence/installability fixture | Unsigned test fixture | May be consumed by 1575b-Fix4 installer tests; must wait for 1575b activation certificate before publication. |

Both fixtures are generated through `build_atlas_slice_manifest()` and can be
parsed by `manifest_from_json_dict()`. They are not Genesis-signed artifacts.

## Core Public-RC Slice Entry Categories

| Category | Included entry example | Origin mode | Readiness status |
| --- | --- | --- | --- |
| Truth primitive definition | `truth_primitive:assert.truth` | `cdl_ratified_definition` | Included with irreducible recipe edge metadata. |
| Consensus-layer primitive exemption | `truth_primitive:commit.epoch` | `cdl_ratified_definition` | Included with explicit `consensus_layer_only_not_agent_issuable` exemption. |
| ADR authority | `adr:0004_genesis_truth_primitives` | `adr_authority` | Included as authority basis. |
| Atlas manual intake invariant | `invariant:fix86_content_layer_edge_type_irreducible_asserted_by` | `atlas_manual_intake` | Included as content-layer recipe coverage evidence. |
| Repo file materialization | `repo:file_ref:ilc_core_bundle_atlas_slice_manifest_py` | `repo_file_materialization` | Included as manifest runtime fixture reference. |

## Economic Soft-RC Slice Entry Categories

| Category | Included entry example | Origin mode | Readiness status |
| --- | --- | --- | --- |
| CDL authority | `cdl:020` | `cdl_ratified_definition` | Included as economic authority trace. |
| ADR authority | `adr:0028_settlement_substrate_graduation_governance_route` | `adr_authority` | Included as settlement-governance route. |
| Runtime materialization | `repo:file:3a03f06a69e1e34e:ilc_core_epoch_epoch_emission_production_path_py` | `repo_file_materialization` | Included as emission runtime evidence, not activation. |
| Runtime materialization | `repo:file:07a2ed17e87de754:ilc_core_epoch_canonical_economic_event_py` | `repo_file_materialization` | Included as canonical economic event evidence, not activation. |
| Future certificate placeholder | `phase:public_rc_economic_activation_certificate_placeholder_1575b` | `generated_evidence` | Explicitly waits for the sensitive 1575b activation certificate. |

## Excluded Categories

| Category | Reason |
| --- | --- |
| `excluded_private_material` projection | Public-RC fixtures must not require private or custody-adjacent nodes. |
| `genesis_private_material_node` | Private material cannot be required for public build or public-RC claim verification. |
| Files marked with `PUBLIC_RC_EXCLUDE` text | Public slice fixtures must not contain excluded-file markers or excluded contents. |
| `Z_Past_Chats`, `.gemini`, `.codex/attachments` | Private/local memory and attachment material. |
| Genesis signing ceremony secrets or recovery tooling | Not needed for readiness fixtures and not public-RC distributable. |
| Full private Atlas graph backlog | Valuable for future graph completeness, not required for bounded launch slices. |

## Recipe Coverage Standard

Every fixture content entry must include exactly one of:

- `recipe_status = irreducible_primitive`
- `recipe_status = composed_governance_recipe`
- `recipe_status = explicit_exemption` with a non-empty `recipe_exemption`

The Core Public-RC Slice records `commit.epoch` as an explicit exemption because
it is consensus-layer only and is rejected for agent truth-primitive submission.

Runtime modules and repo-file materializations are explicit exemptions because
source-file materialization is not itself a truth-primitive output edge.

## Determinism And Hashing

Each fixture is canonical JSON with sorted keys and compact separators. Each
content entry carries a deterministic `record_sha256` over its metadata excluding
the `record_sha256` field itself. The manifest runtime computes:

- canonical manifest JSON;
- DAG-CBOR bytes;
- CIDv1;
- manifest SHA-256;
- included-node Merkle root.

Both fixtures use LMDB graph payload hash:

`34f1806b8e6a0ba5c2c622583daaf69cfb7c346c00dd6a0dd12f051eda906789`

## Tests

The readiness gate is pinned by:

`tests/test_phase_1575b_fix3_public_rc_atlas_slice_readiness.py`

The tests check:

- fixture parseability through `manifest_from_json_dict()`;
- unsigned, non-publication status;
- canonical JSON;
- no private material markers;
- required origin, authority, export, hash, and recipe metadata;
- Core Public-RC Slice origin-mode coverage;
- `commit.epoch` consensus-layer exemption;
- Economic Soft-RC Slice waits for the 1575b activation certificate;
- bool rejection for `cross_section_ref_count`.

## Non-Claims

This phase does not complete the full Atlas graph.

This phase does not create a signed public-RC AtlasSliceManifest.

This phase does not execute Phase 1574-Fix1, Phase 1575a, Phase 1575b, or
Phase 1575c.

This phase does not publish a public mirror, change repository visibility,
publish OpenClaw or ClawHub, activate public serving, activate economics, mint
ECU, settle ILC, activate validator admission, write treasury records, activate
mainnet, or transition epochs.
