# ILC Release Publication Signing Authorization Preflight 1287 v0.1

Status: publication/signing preflight recorded / no publication or signing
Date: 2026-05-09
Phase: 1287
Owner lane: G8 public-RC release/publication/signing boundary

Required tokens:

```text
release_publication_signing_authorization_preflight_phase_1287.v0.1
public_repository_publication_not_authorized_phase_1287
release_artifact_production_not_authorized_phase_1287
source_allowlist_export_not_executed_phase_1287
release_keys_not_generated_phase_1287
release_envelope_not_produced_phase_1287
v0_2_signing_not_authorized_phase_1287
genesis_atlas_mutation_not_authorized_phase_1287
```

Additional carry-forward tokens:

```text
release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing
public_package_publication_not_authorized_phase_1287
public_rc_claim_not_authorized_phase_1287
genesis_atlas_signing_not_authorized_phase_1287
phase_1288_window_1281_1288_closure_gate_next
public_rc_remains_blocked_after_phase_1287
```

Verdict:

```text
release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing
```

Phase 1287 was executed after explicit human authorization:

```text
GO Phase 1285-1288
```

The authorization is interpreted according to the user's stated preflight
stance for Phases 1285-1288. It authorizes this sensitive preflight packet. It
does not authorize source allowlist export execution, public repository
publication, public package publication, public release artifact production,
release-key generation, release-envelope production, Genesis Atlas mutation,
Genesis Atlas regeneration, Genesis Atlas signing, v0.2 signing, public RC
claim, public launch claim, CDL mutation, CDL-088 opening, public P2P, public
fetch serving, public sidecar/projection serving, public claimability, wallet
withdrawal, wallet transfer, wallet spend, ECU minting, or ILC settlement.

---

## 0. Discovery Discipline

Phase 1287 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval. Boundary
analysis used direct repo reads and broader concept discovery before this
packet was written.

| Check | Result |
|-------|--------|
| §0a Known-token audit | Verified the Phase 1287 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1287_g8_release_publication_signing_authorization_preflight.md` and carried them into this packet, the walkthrough, STATUS, PLANNING_INDEX, Roadmap v1.1, and Capsule v5.51. |
| §0b Concept-discovery search | Searched publication, source allowlist, release manifest, release key, release envelope, artifact, Genesis Atlas, v0.2 signing, counsel, license, CLA, trademark, patent, public repository, public package, public RC claim, and public launch terms. |
| §0c Contradiction and non-claim search | Searched not authorized, blocked, deferred, not executed, not generated, not produced, no release, no signing, no mutation, public RC remains blocked, unsigned, counsel required, publication blocked, and source export blocked terms. |
| §0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source granted publication, release artifact, release-key, release-envelope, Genesis Atlas mutation/signing, v0.2 signing, or public-RC authority. Newly carried tokens are `release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing`, `public_package_publication_not_authorized_phase_1287`, `public_rc_claim_not_authorized_phase_1287`, `genesis_atlas_signing_not_authorized_phase_1287`, `phase_1288_window_1281_1288_closure_gate_next`, and `public_rc_remains_blocked_after_phase_1287`. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md`
- `docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
- `docs/specs/ilc_atlas_g_006_public_rc_graph_reachability_gate_1271_v0.1.md`
- `docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Boundary Decision

Phase 1287 records a release publication/signing authorization preflight only:

```text
public_repository_publication_not_authorized_phase_1287
release_artifact_production_not_authorized_phase_1287
source_allowlist_export_not_executed_phase_1287
release_keys_not_generated_phase_1287
release_envelope_not_produced_phase_1287
v0_2_signing_not_authorized_phase_1287
genesis_atlas_mutation_not_authorized_phase_1287
```

No publication or signing authority is activated. No source allowlist export is executed.
No release artifact manifest instance is produced.
No release keys or release envelopes are generated.
No Genesis Atlas mutation, regeneration, or signing is authorized.
No v0.2 signing is authorized. No public RC claim is authorized.

The Phase 1255 allowlist procedure remains procedure-only:

```text
allowlist_export_procedure_defined_phase_1255
public_repository_publication_not_authorized_phase_1255
```

The Phase 1213 release artifact manifest schema remains schema-only and does
not produce artifacts. The Phase 1279 prepublication inventory remains
inventory-only and did not authorize publication. The Phase 1271 graph gate
passes graph reachability only and explicitly keeps release artifacts blocked.

## 2. Counsel, Publication, And Signing Gate Table

| Gate | Current Phase 1287 disposition |
|------|--------------------------------|
| Counsel-approved license instruments | Still required before public RC. |
| CLA or explicit no-external-contributor policy | Still required before external contributor intake. |
| Trademark and fork-labeling policy | Still required before public launch. |
| Patent/publication review | Still required before disclosure-sensitive publication. |
| Source allowlist export | Procedure defined; export not executed. |
| Public repository publication | Not authorized. |
| Public package publication | Not authorized. |
| Release artifact manifest instance | Not produced. |
| Release artifact production | Not authorized. |
| Release-key generation | Not authorized. |
| Release-envelope production | Not produced. |
| Genesis Atlas mutation/regeneration/signing | Not authorized. |
| v0.2 signing | Not authorized. |
| Public RC claim | Not authorized. |

## 3. Current Permitted Surface

The current permitted surface is documentation-only preflight and blocker
classification. The repo may cite existing procedures, schemas, graph evidence,
and prior prepublication inventory, but Phase 1287 does not execute any release
act.

Permitted evidence surfaces:

- Phase 1213 release artifact manifest schema.
- Phase 1255 public source allowlist export procedure.
- Phase 1271 ATLAS-G-006 graph reachability pass with release artifacts blocked.
- Phase 1279 release manifest/source allowlist prepublication inventory.
- Phase 1280 window handoff carrying publication/signing blockers forward.
- Current CDL register showing CDL-087 ratified and CDL-088 unopened.

## 4. Activation Preconditions Carried Forward

Future publication or signing still requires:

- explicit public repository publication authority naming source commit,
  manifest hash, and destination;
- reviewed source allowlist manifest and deterministic dry-run evidence;
- counsel-approved license, CLA/no-external-contributor, trademark, and
  publication posture;
- patent/publication review disposition before disclosure-sensitive material is
  exposed;
- explicit release artifact production authority and manifest instance;
- explicit release-key and release-envelope generation authority;
- explicit Genesis Atlas mutation/regeneration/signing authority if the signed
  Atlas changes;
- explicit v0.2 signing ceremony authority after the Atlas-G tail;
- final public claimability API/verifier authority and release allowlist
  promotion;
- public RC claim authority naming exact commit, package, and distribution
  destination.

The next locked phase is:

```text
phase_1288_window_1281_1288_closure_gate_next
```

Phase 1288 is sensitive and should close the window honestly: either blockers
remain carried forward, or a later explicit activation/release phase is planned.

## 5. Non-Claims

Phase 1287 does not authorize or perform:

- source allowlist export execution
- public repository publication
- public package publication
- public release artifact production
- release artifact manifest instance production
- release-key generation
- release envelope production
- Genesis Atlas mutation, regeneration, or signing
- v0.2 signing
- public RC claim
- public launch claim
- CDL mutation
- CDL-088 opening
- public P2P exposure
- public fetch serving
- public sidecar/projection serving
- public claimability activation
- public claimability API activation
- public verifier service
- wallet withdrawal, transfer, or spend
- wallet signing authority or wallet ledger-write authority
- ECU minting
- ILC settlement or withdrawal runtime activation
- IP filing
- paper publication
- immutable diagnostic mutation
- production `commit.epoch` emission

Public RC remains blocked after Phase 1287:

```text
public_rc_remains_blocked_after_phase_1287
```

Remaining blocker classes include final public claimability API/verifier
authority, actual TransportPrincipal public-path activation authority, actual
sidecar public projection serving authority, privacy filtering/public-safe
projection schema, counsel/IP/publication authorization, source allowlist export
execution, release artifact production, release keys, release envelopes, Genesis
Atlas mutation/regeneration/signing if needed, v0.2 signing authorization,
wallet withdrawal/transfer/spend semantics, ECU minting, and ILC settlement.

---

## 6. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md -> release/publication
graph_delta=support_tests_added:tests/test_phase_1287_release_publication_signing_authorization_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1287_release_publication_signing_authorization_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier
```
