# ILC Public RC Packaging Architecture Gate v0.1

**Status:** Architecture planning constraint.
**Recorded:** 2026-05-10.
**Authority:** This document records an architecture gate for future public-RC
packaging. It does not open Window 1303+, execute source export, publish a
repository or package, produce release artifacts, generate release keys or
envelopes, mutate or sign Genesis Atlas, sign v0.2, activate public
claimability, activate public P2P/fetch/sidecar serving, or authorize
wallet/ECU/ILC economics.

```text
public_rc_packaging_architecture_gate_recorded
public_rc_packaging_gate_sequence_implementation_then_dry_run_then_execution
public_rc_package_export_must_be_public_tree_clean_not_flag_flip
release_artifact_packet_must_reference_clean_export_gate
public_rc_exclude_absence_is_not_allowlist_clearance
legacy_untagged_docs_default_review_required_before_public_export
graph_native_sidecar_suite_must_package_as_clean_materialized_components
deterministic_scaffold_compilation_for_public_rc_recorded_phase_1306
rc_materialization_disposition_compile_retain_internal_strip_replace_phase_1306
public_rc_exclude_helper_disposition_inventory_recorded_phase_1308
truth_primitive_sidecar_boundary_recorded_phase_1308
helper_stripping_not_executed_phase_1308
source_allowlist_export_not_executed_phase_1308
```

## 1. Architecture Invariant

The public RC package must be produced from a clean materialized public source tree. It must not be produced by taking the private canonical repository and
flipping internal fail-closed helper flags from false to true.

Any helper, tool, test, or document carrying `PUBLIC_RC_EXCLUDE` is internal by
default. Before a public source, package, or release artifact can include the
affected functionality, the functionality must be handled by one of three
routes:

| Route | Required result |
|-------|-----------------|
| `replace_before_export` | A public-safe implementation replaces the internal helper, and exported code imports only the replacement. |
| `strip_from_export` | The helper is excluded from the public tree, and exported code has no import dependency on it. |
| `defer_public_rc` | The affected profile remains blocked, and no public-RC claim is made for that profile. |

Absence of `PUBLIC_RC_EXCLUDE` is not allowlist clearance. Many older documents
predate the marker and may still contain private process notes, patent-sensitive
research, counsel/publication gates, stale public-release language, or
non-authorizing phase claims. Untagged legacy files must remain excluded or
review-required until an explicit allowlist manifest names them.

Graph-native sidecars follow the same materialization rule. The sidecar suite is
not an ordinary wrapper API that can smuggle private helpers into a public
package. Any sidecar included in a public RC export must be a clean materialized
component with explicit manifest identity, no `PUBLIC_RC_EXCLUDE` markers, no
stripped-helper imports, and explicit non-claims for public serving,
claimability, transport, wallet, ECU, and ILC gates that remain closed.

Phase 1306 records the deterministic scaffold compilation rule. The private
development workspace may keep the full chain of phase notes, planning strings,
governance tokens, and scaffold helpers. A public RC must not publish that chain
raw unless a future manifest explicitly retains a subset as public metadata.
Instead, materialization must deterministically compile development scaffolding
into final public contracts or exclude it through a recorded disposition.

| Disposition | Meaning |
|-------------|---------|
| `compile_into_contract` | The scaffold or token chain deterministically produces a final public contract, manifest, generated artifact, or static evidence packet. |
| `retain_as_public_metadata` | The token remains public because the final artifact intentionally exposes it as audit metadata. |
| `retain_internal_only` | The token remains in the private development workspace and is not part of the public RC tree. |
| `strip_from_export` | The surface is excluded from the materialized public tree. |
| `replace_before_export` | A public-safe implementation replaces an internal helper or scaffold before export. |

This is a packaging invariant, not a current export action.

Phase 1308 applies the invariant to the current runtime helper inventory. The
four current runtime helpers carrying `PUBLIC_RC_EXCLUDE` are mapped to
`replace_before_export`, not promoted or stripped in-place. Later materialized
public trees must use public-safe replacements or carry the affected profile
forward as blocked. The Phase 1308 truth-primitive sidecar boundary is local
graph-native replacement infrastructure; it is not public serving authority and
does not change the dry-run/execution gates.

## 2. Best Current Phase Plan

The best current plan is a three-step gate sequence:

1. Phase 1308 performs helper pruning/replacement planning and implementation
   hardening. It records `replace_before_export` dispositions for the four
   current runtime helpers and truth-primitive sidecar boundary metadata, but
   must not execute public export, helper stripping, helper promotion, or marker
   removal.
2. Phase 1319 performs deterministic source allowlist export rehearsal. It must
   materialize a dry-run public tree and prove zero `PUBLIC_RC_EXCLUDE` markers,
   zero imports of stripped helpers, deterministic file hashes, and explicit
   non-claims.
3. Phase 1333 performs the source allowlist export execution gate only if later
   explicitly authorized. It must reject the export if marker scans, import
   scans, counsel/IP gates, manifest evidence, or package-profile checks are
   incomplete.

Release artifact production, release-key generation, release envelopes, public
claimability/API activation, public sidecar/P2P activation, wallet/ECU/ILC
economics, Genesis mutation, and v0.2 signing remain separate later gates. A
clean source export is necessary for those gates, but it is not sufficient by
itself to authorize them.

## 3. Release Packet Rule

The release artifact manifest schema remains the minimum manifest shape. Future
public-RC release packets that contain or reference source/package artifacts
must also reference the clean source export evidence produced by the packaging
gate:

- source revision and manifest hash;
- materialized public-tree file hashes;
- `PUBLIC_RC_EXCLUDE` marker-scan result;
- stripped-helper import-scan result;
- graph-native sidecar component manifest and non-claim state, if any sidecar
  suite components are included;
- Phase 1307 sidecar registry/profile integrity evidence if the package includes
  graph-native sidecar components;
- counsel/IP/publication clearance state;
- legacy untagged-file review state;
- explicit non-claims for any still-deferred public path or economics gate.

No release packet should describe a source/package artifact as public-RC clean if
the corresponding materialized tree still contains `PUBLIC_RC_EXCLUDE`, imports
an excluded helper, or depends on a helper whose authority was created by
flipping a fail-closed private flag.

## 4. Durable References

Future window sequence locks and prompt drafts that touch public RC packaging,
source export, release artifact production, or public RC claims should reference
all of these anchors:

- `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
- `docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md`
- `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md`
- `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md`
- `docs/specs/ilc_graph_native_sidecar_registry_manifest_1307_v0.1.md`

## 5. Non-Claims

This architecture gate does not authorize:

- Window 1303+ execution;
- helper promotion or marker removal;
- source allowlist export execution;
- public repository publication;
- public package publication;
- release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- public launch claim;
- public claimability activation;
- public P2P/fetch/sidecar serving;
- wallet withdrawal, transfer, spend, ECU minting, or ILC settlement;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- CDL mutation or CDL-088 opening;
- IP filing or paper publication.
