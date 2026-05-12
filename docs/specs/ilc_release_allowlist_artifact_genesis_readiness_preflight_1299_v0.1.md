# ILC Release Allowlist Artifact Genesis Readiness Preflight 1299 v0.1

Status: preflight only / no artifacts
Date: 2026-05-11
Phase: 1299
Owner lane: G8 public-RC release and signing boundary

Required tokens:

```text
release_allowlist_artifact_genesis_readiness_preflight_phase_1299.v0.1
release_readiness_verdict_phase_1299=preflight_only_no_artifacts
source_allowlist_export_not_executed_phase_1299
release_artifact_not_produced_phase_1299
release_keys_not_generated_phase_1299
release_envelope_not_produced_phase_1299
genesis_atlas_not_mutated_or_signed_phase_1299
v0_2_signing_not_authorized_phase_1299
public_rc_exclude_helper_stripping_deferred_to_package_materialization_after_phase_1299
public_rc_remains_blocked_after_phase_1299
phase_1300_counsel_ip_publication_clearance_inventory_next
```

Verdict:

```text
release_readiness_verdict_phase_1299=preflight_only_no_artifacts
```

Phase 1299 was executed after explicit human authorization:

```text
GO Phase 1299
```

The authorization grants only this release allowlist, artifact, and Genesis
readiness preflight. It does not execute source allowlist export, publish source
or packages, produce a release artifact or manifest instance, generate release
keys, produce a release envelope, mutate or sign Genesis Atlas, authorize v0.2
signing, activate public claimability, activate public P2P/fetch/sidecar
serving, mutate the CDL register, open CDL-088, file IP, publish papers, or
authorize wallet/ECU/ILC economics.

---

## 0. Discovery Discipline

Phase 1299 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval. Boundary
analysis used direct repo reads and broader concept discovery before this
packet was written.

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | Verified the Phase 1299 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1299_g8_release_allowlist_artifact_genesis_readiness_preflight.md` and carried them into this packet, tests, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.52, and Roadmap v1.1. |
| Section 0b Concept-discovery search | Searched release artifact, release manifest, source allowlist, allowlist export, public repository, public package, release key, release envelope, Genesis Atlas, v0.2 signing, public RC, `PUBLIC_RC_EXCLUDE`, and legacy untagged review terms. |
| Section 0c Contradiction and non-claim search | Searched not authorized, blocked, deferred, not executed, not generated, not produced, no release, no signing, no mutation, unsigned, publication blocked, public RC remains blocked, counsel required, and source export blocked terms. |
| Section 0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source grants source export, release artifact, release-key, release-envelope, Genesis Atlas mutation/signing, v0.2 signing, or public-RC authority. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1299_g8_release_allowlist_artifact_genesis_readiness_preflight.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
- `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md`
- `docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md`
- `docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md`
- `docs/specs/ilc_atlas_graph_integrated_phase_discipline_forward_planning_1241_v0.1.md`
- `docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md`
- `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md`
- `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Readiness Inventory

Phase 1299 records readiness classification only. It does not produce any
machine release surface.

| Surface | Current evidence | Phase 1299 disposition | Carry-forward |
|---------|------------------|------------------------|---------------|
| Source allowlist export | Phase 1255 defines the export procedure and deny/default review rules with `allowlist_export_procedure_defined_phase_1255`. | Not executed: `source_allowlist_export_not_executed_phase_1299`. | Future dry-run materialization in Phase 1319; possible execution gate in Phase 1333 only with explicit authority. |
| `PUBLIC_RC_EXCLUDE` helper stripping | Phase 1293 keeps current helpers internal; Phase 1294 records raw measured profile is not directly exportable; packaging gate forbids flag flips. | Deferred: `public_rc_exclude_helper_stripping_deferred_to_package_materialization_after_phase_1299`. | Phase 1308 replacement/strip/carry-forward inventory; Phase 1319 dry-run marker/import scan; Phase 1333 export execution gate if authorized. |
| Legacy untagged docs | Phase 1255 and packaging gate define absence of `PUBLIC_RC_EXCLUDE` as not allowlist clearance. | Not cleared. | Future manifest must exclude or explicitly review legacy untagged docs, phase walkthroughs, research notes, whitepaper drafts, roadmap fragments, and private context material. |
| Release artifact manifest schema | Phase 1213 schema exists with `release_artifact_manifest_schema_committed_phase_1213`; release packet must reference clean export evidence for source/package artifacts. | No artifact and no manifest instance produced: `release_artifact_not_produced_phase_1299`. | Phase 1320 rehearsal and Phase 1334 production gate if later authorized. |
| Release keys | ADR/release-key procedure remains separately gated by release authorization. | Not generated: `release_keys_not_generated_phase_1299`. | Phase 1321 rehearsal and Phase 1335 key/envelope gate if later authorized. |
| Release envelope | Phase 1213 allows release envelope artifact type, but no envelope authority is granted here. | Not produced: `release_envelope_not_produced_phase_1299`. | Phase 1321 rehearsal and Phase 1335 key/envelope gate if later authorized. |
| ATLAS-G-006 graph reachability | Phase 1271 passes selected-profile graph gate only and keeps release artifacts blocked. | Evidence accepted as preflight input only. | ATLAS-G-007 through ATLAS-G-010 remain future work before any v0.2 signing claim. |
| Genesis Atlas | Signed Genesis v0.1 remains canonical until explicit v0.2 signing authorization. | Not mutated, regenerated, or signed: `genesis_atlas_not_mutated_or_signed_phase_1299`. | Future unsigned candidate regeneration/non-excisability/signing-root/v0.2 gates only under later sequence locks and explicit authority. |
| v0.2 signing | ATLAS-G planning keeps ATLAS-G-010 sensitive and explicitly authorized only. | Not authorized: `v0_2_signing_not_authorized_phase_1299`. | Future signing gate only after clean export, release/signing readiness, Genesis/Atlas authority, and explicit human signing authorization. |
| Public RC claim | Public claimability, public serving, counsel/IP/publication, source export, release artifacts, keys/envelopes, Genesis/v0.2 signing, wallet/ECU/ILC all remain gated. | Still blocked: `public_rc_remains_blocked_after_phase_1299`. | Phase 1300 counsel/IP/publication inventory next; Phase 1301 no-activation audit; Phase 1302 closure classification. |

Prior release-publication preflight token:

```text
release_manifest_allowlist_publication_preflight_phase_1279.v0.1
release_publication_signing_authorization_preflight_phase_1287.v0.1
atlas_g_006_public_rc_graph_reachability_gate_phase_1271.v0.1
atlas_g_007_unsigned_v0_2_plus_candidate_regeneration_required
public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution
```

Readiness summary:

```text
source_allowlist_export_not_executed_phase_1299
release_artifact_not_produced_phase_1299
release_keys_not_generated_phase_1299
release_envelope_not_produced_phase_1299
genesis_atlas_not_mutated_or_signed_phase_1299
v0_2_signing_not_authorized_phase_1299
```

---

## 2. Package Materialization Boundary

Phase 1299 confirms that public RC packaging must be a clean materialized public
tree, not a private tree with fail-closed helper flags flipped.

The later public source/package materialization must fail closed if:

- any exported file contains `PUBLIC_RC_EXCLUDE`;
- any exported file imports a stripped helper module;
- exported code depends on a helper whose authority was created by changing an
  internal false flag to true;
- marker-scan or import-scan evidence is missing;
- legacy untagged docs/research/planning files are included without explicit
  legacy review evidence;
- counsel/IP/publication status is missing for files that require it.

Phase 1299 does not remove `PUBLIC_RC_EXCLUDE`, promote helpers, strip helpers,
materialize a public tree, create a package manifest, or create release
artifacts.

Carry-forward token:

```text
public_rc_exclude_helper_stripping_deferred_to_package_materialization_after_phase_1299
```

---

## 3. Genesis And Signing Boundary

Phase 1299 treats ATLAS-G and Genesis evidence as readiness inputs only:

- ATLAS-G-006 passed selected-profile graph reachability in Phase 1271, but the
  verdict is explicitly `pass_graph_gate_only_release_artifacts_blocked`.
- ATLAS-G-007 unsigned v0.2+ candidate regeneration, ATLAS-G-008
  non-excisability review, ATLAS-G-009 signing-root envelope prep, and
  ATLAS-G-010 v0.2 signing remain future work.
- The signed Genesis v0.1 baseline remains canonical unless a later phase
  explicitly authorizes candidate regeneration, mutation, signing preparation,
  and signing.

Boundary tokens:

```text
genesis_atlas_not_mutated_or_signed_phase_1299
v0_2_signing_not_authorized_phase_1299
```

---

## 4. Next Phase

The next locked phase is:

```text
phase_1300_counsel_ip_publication_clearance_inventory_next
```

Phase 1300 is sensitive and requires explicit `GO Phase 1300`.

---

## 5. Non-Claims

Phase 1299 does not authorize or perform:

- source allowlist export execution
- materialized export manifest production
- public repository publication
- public package publication
- release artifact production
- release artifact manifest instance production
- release-key generation
- release envelope production
- release signing material generation
- Genesis Atlas mutation
- Genesis Atlas regeneration
- Genesis Atlas signing
- v0.2 signing
- public RC claim
- public launch claim
- public claimability activation
- public claimability API activation
- public verifier service
- public claim endpoint
- public P2P exposure
- public fetch serving
- public sidecar/projection serving
- public projection endpoint serving
- non-loopback bind
- public listener
- peer discovery
- TransportPrincipal public-path activation
- credential lifecycle policy activation
- public revocation registry activation
- public replay cache activation
- admission policy activation
- ban registry activation
- public rate-limit state activation
- privacy policy activation
- helper promotion
- marker removal
- helper stripping
- CDL mutation
- CDL-088 opening
- IP filing
- paper publication
- wallet withdrawal
- wallet transfer
- wallet spend
- wallet signing authority
- wallet ledger-write authority
- ECU minting
- ILC settlement
- withdrawal runtime activation
- immutable diagnostic mutation
- production `commit.epoch` emission

Public RC remains blocked after Phase 1299:

```text
public_rc_remains_blocked_after_phase_1299
```

Exact non-claim phrase guard:

```text
source allowlist export execution
materialized export manifest production
public repository publication
public package publication
release artifact production
release artifact manifest instance production
release-key generation
release envelope production
Genesis Atlas mutation
Genesis Atlas regeneration
Genesis Atlas signing
v0.2 signing
public RC claim
public launch claim
public claimability
public verifier service
public P2P
public fetch serving
public sidecar/projection serving
non-loopback bind
public listener
peer discovery
TransportPrincipal public-path activation
helper promotion
marker removal
helper stripping
CDL mutation
CDL-088 opening
IP filing
paper publication
wallet withdrawal
wallet transfer
wallet spend
ECU minting
ILC settlement
production `commit.epoch` emission
```

---

## 6. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_release_allowlist_artifact_genesis_readiness_preflight_1299_v0.1.md -> release/publication
graph_delta=support_tests_added:tests/test_phase_1299_release_allowlist_artifact_genesis_readiness_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1299_release_allowlist_artifact_genesis_readiness_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
