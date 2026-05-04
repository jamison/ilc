# ADR-0037: Genesis Canonical Lineage Contract

**Status:** Proposed
**Date:** 2026-05-04
**Phase:** 1167

`adr_0037_lineage_contract_draft_committed_phase_1167`

---

## 1. Context

Window 1156-1165 closed with CDL-085 still SIM-gated and with the unsigned Genesis
v0.2 candidate at 41 nodes and 73 edges. The closure handoff routed the next work
through a Genesis Canonical Lineage Contract before either CDL-085 reconsideration or
v0.2 signing.

The contract is separate from ADR-0036. ADR-0036 covers a delegated operational release
key. This ADR covers the canonical lineage, equivalence, and merge-policy semantics
that determine what the release key may bind to.

This ADR is Proposed only. Acceptance review is Phase 1173.

---

## 2. Decision

Define the Genesis Canonical Lineage Contract as the governance contract that answers
three questions for ILC objects:

- **Lineage:** where did this object come from?
- **Equivalence:** can this object and another object be treated as the same canonical
  object for a stated purpose?
- **Merge policy:** if the objects are equivalent, what happens to attribution,
  authority, versioning, and economic flow?

Genesis signed v0.1 is the canonical base object for this contract. This is a governance
anchor, not a mathematical identity claim.

---

## 3. Lineage

An ILC object has canonical Genesis lineage only if it can produce a deterministic,
verifiable trace to the signed Genesis v0.1 root.

Minimum lineage proof:

1. The object references a signed Genesis v0.1 root envelope hash:
   `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`.
2. The referenced root envelope verifies against the Genesis Agent 01 signing material.
3. Node 0 is present in the signed manifest or in a Merkle-inclusion path anchored by
   that manifest.
4. Any ADR/CDL authority dependency is traceable through accepted ADR status or ratified
   CDL status.
5. Any release artifact that claims canonical ILC identity traces through the Genesis
   root envelope and any delegated operational release-key authority ratified later.

Failure of any minimum lineage proof condition means the object may still be a fork,
copy, or derivative work, but it does not carry canonical ILC lineage.

---

## 4. Canonical Base Object

Genesis signed v0.1 is the canonical base object against which equivalence and merge
claims are evaluated.

This contract deliberately uses the terms "canonical base object" and "governance
anchor." It does not make a category-theoretic identity claim. The practical claim is
narrower: canonical ILC identity is measured by convergence back to signed Genesis v0.1
under the observer slices declared in this ADR.

---

## 5. Equivalence Policy

Equivalence is domain-specific. Two objects can be equivalent in one domain and not
equivalent in another. Each equivalence claim must state its domain.

### 5.1 Claim Equivalence

Two claims are claim-equivalent when:

- they assert the same falsifiable content;
- they share the same valid refutation surface under the Popperian Equivalence Criterion
  in §6;
- their authority dependencies trace to the same Genesis canonical lineage root; and
- neither claim adds a material condition that would make a valid refutation apply to
  only one of them.

Boundary: paraphrase, formatting, translation, and non-semantic decomposition may be
claim-equivalent. Added premises, removed falsifiability conditions, or changed truth
primitive dependencies are not claim-equivalent.

Merge consequence: claim-equivalent objects may share canonical claim identity, but
their provenance paths remain separately auditable unless provenance equivalence also
holds.

### 5.2 Provenance Equivalence

This subsection is the named SIM-SPECTRAL-05 input criterion.

Two derivation paths are provenance-equivalent as independent canonical derivations if
and only if all of the following hold:

1. **Genesis convergence:** each path terminates at a Genesis primitive, signed Genesis
   artifact, accepted ADR, or ratified CDL that traces to the signed Genesis v0.1 root.
2. **Independent separator failure:** the system cannot construct a valid separator that
   distinguishes one path as non-independent without also defeating the other path's
   independence claim.
3. **Injection-point separation absence:** no shared non-Genesis intermediary controls
   the claimed independent paths in a way that refutes independence for one path while
   leaving genuine independent derivations intact.
4. **Refutation-surface equality:** every valid provenance refutation that defeats one
   path's canonical independence also defeats the other path's canonical independence.
5. **Declared merge scope:** the equivalence claim states whether it is being used for
   attribution, authority, versioning, economic flow, or SIM classification.

Operational Sybil separator: a claimed set of independent paths fails provenance
equivalence if the paths converge first at a non-Genesis injection point, coordinated
issuer, synthetic cluster, or unratified authority object before they converge at a
Genesis primitive or signed Genesis artifact.

SIM-SPECTRAL-05 must treat this criterion as the provenance equivalence input:
legitimate S1 paths should converge at Genesis primitives or signed Genesis artifacts;
Sybil S3 paths should either fail to converge or converge first at a non-Genesis
intermediary.

### 5.3 Version Equivalence

Two versions are version-equivalent when the later version is a signed or explicitly
authorized refinement of the earlier canonical object and preserves the earlier object's
lineage, truth-primitive dependencies, and refutation surface.

Boundary: a version that removes Node 0, breaks the root-envelope trace, or changes
non-amendable truth primitives is not version-equivalent.

Merge consequence: version-equivalent objects may be treated as the same continuing
canonical object for release and documentation purposes, with the later version recorded
as a successor rather than a new universe.

### 5.4 Governance Equivalence

Two governance outcomes are governance-equivalent when they produce the same operative
constitutional state under the same ratification authority and refutation surface.

Boundary: supersession, amendment, and clarification can be governance-equivalent if
they preserve operative effect. A new authorization, new emergency authority, or new
scope of mutable objects is not governance-equivalent.

Merge consequence: governance-equivalent outcomes may be indexed as the same operative
governance state while preserving distinct historical records.

### 5.5 Fork Equivalence

A fork remains canonical-ILC-equivalent only if it converges to signed Genesis v0.1
through all six observer slices in §8.

Boundary: a fork that strips Node 0, changes the Genesis root envelope, breaks gossip
domain continuity, redirects economic attribution away from Genesis lineage, or fails
runtime-binding traceability exits canonical ILC identity.

Merge consequence: non-equivalent forks may copy or derive from the code according to
the applicable license, but they do not carry canonical ILC meaning, identity, ECU/ILC
lineage, or governance authority.

### 5.6 Economic Equivalence

Two contribution paths are economic-equivalent when they represent one canonical
attribution event under the same provenance equivalence, same claim equivalence, and
same ratified economic rule.

Boundary: separate independent derivations may receive separate attribution if they
fail economic equivalence while still remaining legitimate claims. Sybil-coordinated
derivations fail independent economic equivalence.

Merge consequence: economic-equivalent paths receive one attribution event or shared
allocation; non-equivalent independent paths may receive separate allocation; Sybil
paths are not independent allocation events.

---

## 6. Popperian Equivalence Criterion

The Popperian Equivalence Criterion (PEC) is the merge gate for equivalence claims:

> Two ILC objects are equivalent in a declared domain only if every valid refutation
> that defeats one defeats the other, and the system cannot construct a meaningful
> separator that defeats one object while leaving the other intact.

Equivalence is established by failure to find a separator, not by positive similarity.

CDL-V7 (`cdl_v7_popperian_gate_runtime_398.v0.1`) is the existing single-claim
Popperian gate. PEC is the relational merge extension: it asks whether two objects
share the same valid refutation surface.

For this ADR, a valid refutation is one that satisfies CDL-V7's Popperian gate for the
object/domain under review and is specific enough to defeat one side of the equivalence
claim. A separator is meaningful when it creates a domain-relevant difference in
lineage, falsifiability, authority, convergence, or economic consequence.

Sybil application: Sybil cluster independence claims are refutable by injection-point
identity. That separator defeats the cluster's independence claim without defeating
genuine independent derivations that converge separately to Genesis primitives.

---

## 7. Merge Policy

Merge consequences are domain-specific:

| Domain | Attribution consequence | Authority consequence | Versioning consequence | Economic-flow consequence |
|--------|-------------------------|-----------------------|------------------------|---------------------------|
| Claim | One canonical claim identity; separate provenance retained | Same claim authority surface | No version change unless version equivalence also holds | No payment merge unless economic equivalence also holds |
| Provenance | Paths can be treated as one derivation class for the declared scope | No extra governance authority from duplicated paths | No version effect | Sybil-equivalent paths collapse to one or zero independent events |
| Version | Historical attribution preserved across successor | Later version inherits only ratified authority | Successor/refinement, not new canonical universe | Economic flows continue only if economic rules preserve them |
| Governance | Historical entries remain separate; operative state can merge | Same operative constitutional effect | Supersession or clarification recorded | No economic effect unless specified by ratified policy |
| Fork | Canonical forks retain lineage only if all slices converge | Fork loses canonical authority if any slice fails | Separate universe if non-equivalent | No canonical ECU/ILC economic continuity if non-equivalent |
| Economic | One allocation event or declared split | No governance-weight multiplication | No version effect | Single payment, shared payment, or separate payment by ratified rule |

No merge may erase audit history. Merge policy affects canonical identity and downstream
treatment, not historical observability.

---

## 8. Multi-Slice Encrustation

Genesis is a cross-slice lineage invariant. A canonical ILC observer should be able to
trace the same object back to Genesis through each relevant slice.

| Slice | Convergence question | Failure mode |
|-------|----------------------|--------------|
| Authority | Does the authority chain trace to signed Genesis v0.1, accepted ADRs, or ratified CDLs? | Unratified authority or stripped root |
| Claim-composition | Do derivation paths converge at Genesis primitives or signed Genesis artifacts? | Non-Genesis claim hub or broken primitive dependency |
| Runtime-binding | Do runtime versions link to the ratified CDL/ADR chain that authorizes them? | Runtime semantics without lineage |
| Economic-flow | Do attribution flows trace to Genesis-anchored ECU/ILC rules and events? | Forked economic meaning or duplicated Sybil allocation |
| Gossip | Do peer/domain identifiers preserve Genesis network identity and lineage? | New gossip domain posing as canonical ILC |
| Provenance | Do provenance paths converge at Genesis-signed artifacts, accepted ADRs, or ratified CDLs? | Injection-point convergence before Genesis convergence |

A fork that cannot converge through all six slices has exited canonical ILC identity.

---

## 9. Fork Boundary

A fork remains within canonical ILC identity if and only if it can demonstrate all of:

1. signed Genesis v0.1 lineage;
2. Node 0 continuity;
3. root-envelope continuity;
4. ADR/CDL authority traceability;
5. runtime-binding traceability;
6. economic-flow continuity for canonical ECU/ILC meaning;
7. gossip/domain continuity; and
8. provenance convergence at Genesis-signed artifacts or ratified governance objects.

Failure in any slice exits canonical identity for the failed scope. The fork may still
exist as a derivative project, but it is not the same canonical ILC object.

---

## 10. Relationship to ADR-0036

ADR-0036 may define an operational release key only as delegated Genesis-bound authority.
ADR-0036 does not define what counts as Genesis-equivalent. This ADR does.

Before ADR-0036 can be accepted, its release-key binding semantics must be checked
against this ADR's version equivalence (§5.3) and fork boundary (§9). A release key can
sign canonical releases only if the target artifact remains version-equivalent and
fork-equivalent under this contract.

---

## 11. Consequences

If accepted, this ADR provides:

- the formal lineage/equivalence/merge-policy basis for public RC artifacts;
- the provenance equivalence criterion consumed by SIM-SPECTRAL-05;
- the version equivalence policy needed before v0.2 signing;
- the fork-boundary policy needed before public release-key acceptance; and
- the Genesis encrustation model that makes Genesis non-removable across observer slices.

Open risks before acceptance:

- Phase 1168 must confirm that §5.2 is operational enough for SIM-SPECTRAL-05.
- Phase 1173 must confirm consistency with ADR-0036.
- Later windows must implement deferred observer-slice tests for runtime-binding,
  economic-flow, and gossip.
