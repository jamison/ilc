# ADR-0027: Canonical Self-Describing Bootstrap and Receipt Boundary

**Status:** Accepted
**Date:** 2026-04-03
**Authors:** Jamison (ILC), Codex
**Classification:** Architectural boundary for bootstrap, receipts, and public legitimacy lineage

---

## Context

ILC has an important recurring design intuition: the system should increasingly
explain and govern itself through canonical machine-legible artifacts rather
than through ad hoc operator convention, hidden configuration, or unrelated
secondary foundations.

That intuition is sometimes described informally as "homoiconic" or
"reflective." Those labels are too broad to serve as actionable canon on their
own. They risk implying claims ILC is not making, such as:
- everything in ILC must be one universal object type,
- the graph is code,
- all state must be self-evaluating,
- every object must embed every other object.

What the architecture actually needs is a narrower, enforceable boundary:
canonical bootstrap artifacts, manifests, receipts, and later governance
artifacts must form one signed, self-describing, machine-legible lineage.

This matters directly to the public-release lane. If canonical public identity,
consensus bootstrap, economic activation, and later governance all derive from
the same artifact lineage, then public ILC legitimacy becomes much harder to
decouple from its economic and consensus foundations.

## Decision

### 1. Canonical bootstrap artifacts must be self-describing

Canonical bootstrap artifacts must declare enough machine-legible information to
support deterministic interpretation and verification, including:
- schema or artifact kind,
- version,
- signer or attestor identity,
- authority scope,
- lineage or predecessor references where applicable,
- deterministic verification references or material.

Canonical network operation must not depend on undocumented operator knowledge to
interpret bootstrap authority.

### 2. Bootstrap and configuration authority must derive from signed canonical artifacts

When bootstrap or configuration values are authoritative for the canonical
network, they must derive from signed canonical Genesis/bootstrap artifacts,
manifests, or receipts.

Arbitrary graph state, arbitrary local configuration, and unverifiable prose are
not canonical substitutes for signed bootstrap authority.

### 3. Canonical manifests, receipts, and state surfaces must share a uniform representation discipline

ILC does not require one monolithic schema for every artifact. It does require a
common representation discipline across canonical manifests, receipts, and state
surfaces:
- explicit schema/versioning,
- canonical serialization rules,
- stable machine-legible field names,
- provenance and lineage references,
- deterministic verification rules.

This discipline applies to bootstrap artifacts, receipt artifacts, and later
public-legitimacy artifacts.

### 4. Genesis bootstrap artifacts are the recursive self-anchor of canonical lineage

Genesis-signed bootstrap artifacts are the recursive self-anchors that bind:
- early network identity,
- early economic activation,
- and consensus bootstrap

into one canonical artifact lineage.

Genesis is therefore not merely an initial operational convenience. It is the
first signed canonical boundary from which the network can explain who is
authoritative, how canonical identity begins, how canonical economic activation
begins, and how canonical consensus bootstrap begins.

### 5. Later governance must extend the same lineage

As Genesis authority recedes, later governance must extend the same canonical
artifact lineage rather than replacing it with an unrelated foundation.

That means later governance artifacts must remain:
- signed or otherwise cryptographically attested where required,
- self-describing,
- machine-legible,
- lineage-aware,
- and verification-friendly.

This lineage provides the bridge from Genesis bootstrap to later governance
without requiring a separate ontological foundation.

### 6. Public legitimacy must reference canonical artifact lineage

For the public-release lane, canonical public legitimacy should flow through this
artifact boundary.

That includes future work on:
- public identity activation receipts,
- public namespace authority,
- public quorum eligibility proofs,
- settlement-linked public legitimacy,
- public reputation continuity.

These public surfaces should anchor to signed canonical artifact lineage rather
than ad hoc local convention.

### 7. Explicit exclusions

This ADR does **not** require:
- a universal single object schema for all of ILC,
- embedding the moving ledger root into every graph object,
- treating arbitrary graph state as trusted auto-configuration,
- replacing key-derived identity with transaction-derived identity,
- Lisp-style self-evaluation as a protocol requirement,
- forcing local/private graph use into public economic coupling.

## Consequences

### Positive

- Bootstrap, receipts, and later governance share one coherent legitimacy model.
- Canonical public identity, consensus, and economics can be coupled through
  artifact lineage without poisoning every utility module.
- Machine agents and operators can rely on self-describing canonical artifacts
  instead of undocumented operator knowledge.
- Genesis-to-governance continuity becomes architecturally cleaner.

### Tradeoffs

- Canonical artifacts must carry more explicit metadata and verification fields.
- Bootstrap/config loading must remain strict about authority provenance.
- Later public-release work must preserve lineage discipline rather than adding
  ad hoc shortcuts.

### Immediate implications

- Phase 585+ public-release planning must treat this ADR as a dependency.
- Auto-configuration should load only from signed canonical bootstrap artifacts,
  manifests, or receipts with explicit authority scope.
- Receipt/manifests/state surfaces should converge on uniform representation
  discipline over time.

## Non-goals

This ADR does not:
- complete Phase 585+ implementation work,
- redefine wallet scope,
- widen local/private economics,
- or replace the protocol-vs-harness boundary in ADR-0026.

## Related references

- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`
- `docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/specs/eve_capsule_format_v0.1.md`
- `docs/specs/canon_bundle_key_registry_bundle_v0.1.md`
- `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
