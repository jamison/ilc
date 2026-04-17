# ILC CDL-039 Topology Shuffling Authorization Scope Note 711 v0.1

**Date:** 2026-04-17  
**Phase:** 711  
**Status:** Scope note only

Tokens:
- `cdl_039_scope_note_published`
- `topology_shuffling_requires_later_authorization`
- `cdl_039_privacy_boundary_preserved_during_shuffle_scope`
- `vrf_not_yet_production_ratified_here`

## 1. Current ratified boundary

`CDL-039` is already ratified for:

- brokerless peer-to-peer transport baseline,
- no-central-broker invariants,
- topology-privacy constraints at the transport and metadata layer.

That ratification does not automatically authorize validator-topology shuffling
as a production governance surface. The present note therefore starts from the
existing `CDL-039` privacy boundary rather than reopening it.

## 2. Narrow authorization path for topology shuffling

`topology_shuffling_requires_later_authorization`

The narrow authorization path is:

1. Phase `710` defines validator-agent admission and diversity assumptions,
2. Phase `711` commissions `SIM-TOPOLOGY-01`,
3. later simulation evidence shows whether shuffle cadence, graph degree, and
   seeding mode preserve both resilience and `CDL-039` privacy,
4. a later named authorization artifact or amendment then decides whether
   topology shuffling is constitutionally authorized beyond testnet framing.

This means topology shuffling is a candidate governed capability, not a
pre-authorized production feature.

## 3. Epoch-hash versus VRF framing

`vrf_not_yet_production_ratified_here`

The current option framing is:

- epoch-hash is acceptable for testnet framing because it is deterministic and
  auditable,
- VRF remains the stronger production candidate if later evidence shows it is
  needed for privacy or anti-manipulation reasons,
- neither option is finally selected for production by this note.

The required future question is not "which seed sounds better" but "which seed
preserves privacy, resilience, and auditability under the commissioned
simulation envelope."

## 4. Preserved exclusions and privacy constraints

`cdl_039_privacy_boundary_preserved_during_shuffle_scope`

This note does not authorize:

- production topology shuffling,
- final production VRF law,
- any relaxation of `CDL-039` topology-privacy constraints,
- runtime disclosure of global validator adjacency,
- validation pools or delegated stake semantics.

Any later shuffling authorization must preserve the existing `CDL-039` boundary:

- no central broker,
- no transport metadata that makes full cluster membership inferable,
- no heavy topology payload push that violates the hybrid push-pull posture.
