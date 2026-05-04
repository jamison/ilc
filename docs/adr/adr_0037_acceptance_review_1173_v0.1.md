# ADR-0037 Acceptance Review — Phase 1173

**ADR:** ADR-0037 Genesis Canonical Lineage Contract
**Review phase:** 1173
**Review date:** 2026-05-04
**Reviewer:** Claude Sonnet 4.6 (local architectural reviewer)
**Prior status:** Proposed (Phase 1167)
**Verdict:** **ACCEPTED**

`adr_0037_accepted_phase_1173`

---

## Acceptance Criteria Checklist

### Criterion 1 — Six equivalence domains specified with criterion, boundary, and merge consequence

| Domain | Criterion | Boundary | Merge consequence |
|--------|-----------|----------|-------------------|
| Claim (§3.1) | Same falsifiable content; same refutation surface; same lineage; no new separator | Paraphrase OK; added premises, removed falsifiability, changed truth primitives NOT equivalent | Shared canonical claim identity; provenance paths remain separately auditable |
| Provenance (§3.2) | Five conditions: Genesis convergence, independent separator failure, injection-point absence, refutation-surface equality, declared merge scope | Sybil paths fail because injection-point identity IS a valid separator | Paths treated as one derivation class for declared scope; Sybil paths collapse to zero |
| Version (§3.3) | Signed/authorized refinement preserving lineage, truth primitives, refutation surface | Removes Node 0, breaks root-envelope trace, changes non-amendable truth primitives = NOT equivalent | Successor/refinement; not new canonical universe; historical attribution preserved |
| Governance (§3.4) | Same operative constitutional state under same ratification authority | New authorization, emergency authority, or new scope of mutable objects = NOT equivalent | Same operative state indexed; historical entries remain separate |
| Fork (§3.5) | Converges to signed Genesis v0.1 through all six observer slices | Strips Node 0, changes root, breaks gossip domain, redirects economics, fails runtime binding = exits canonical identity | Non-equivalent forks lose ILC canonical meaning, ECU lineage, governance authority |
| Economic (§3.6) | Same provenance + claim equivalence + same ratified economic rule | Separate independent derivations may receive separate attribution | Single or shared allocation event; Sybil paths = zero independent allocation events |

**Result: PASS.** All six domains fully specified.

### Criterion 2 — PEC formally stated as operational test

- Negative test formulation present: "Equivalence is established by failure to find a separator, not by positive similarity." ✓
- CDL-V7 (`cdl_v7_popperian_gate_runtime_398.v0.1`) cited as existing single-claim Popperian gate ✓
- PEC stated as relational merge extension of CDL-V7 ✓
- "Valid refutation" operationalized: one that satisfies CDL-V7's Popperian gate for the object/domain under review and is specific enough to defeat one side of the equivalence claim ✓
- Sybil separator test: injection-point identity refutes Sybil independence without refuting genuine independent derivations converging separately at Genesis primitives ✓

**Result: PASS.**

### Criterion 3 — Multi-slice encrustation and fork boundary specified

§6 six-slice table:
- Authority: chain traces to signed Genesis v0.1, accepted ADRs, or ratified CDLs ✓
- Claim-composition: derivation paths converge at Genesis primitives or signed artifacts ✓
- Runtime-binding: runtime versions link to ratified CDL/ADR chain ✓
- Economic-flow: attribution flows trace to Genesis-anchored ECU/ILC rules ✓
- Gossip: peer/domain identifiers preserve Genesis network identity ✓
- Provenance: paths converge at Genesis-signed artifacts, accepted ADRs, or ratified CDLs ✓
- "A fork that cannot converge through all six slices has exited canonical ILC identity." ✓

§7 fork boundary: 8 conditions stated; "Failure in any slice exits canonical identity for the failed scope." ✓

**Result: PASS.**

### Criterion 4 — Consistency with SIM-SPECTRAL-05 results

The §3.2 provenance equivalence criterion was consumed verbatim by the SIM-SPECTRAL-05
program spec (Phase 1168) as the named input. SIM-SPECTRAL-05 emitted `sim_spectral_05_gate_pass`:

- Track A: λ_max, spectral_gap, degree_gini all discriminate against `synthetic_sybil_cluster`.
  Structural separation is detectable — consistent with §3.2 condition 3 (injection-point
  separation absence: Sybil injection points create structurally distinguishable clusters).
- Track B: S1 branchial convergence 0.85 vs S3 Sybil convergence 0.25 (separation 0.60).
  Legitimate paths converge at Genesis primitives; Sybil paths converge first at non-Genesis
  intermediaries — directly validates §3.2 conditions 1 and 3.

**Result: PASS.** ADR-0037 §3.2 was operationalizable and the SIM produced consistent results.

### Criterion 5 — Provenance equivalence criterion operationalizable

Phase 1168 consumed §3.2 as a named SIM input and confirmed operationalizability before
Track A and Track B executed. SIM-SPECTRAL-05 pass confirms the criterion was testable
as specified.

**Result: PASS.**

---

## Additional Notes

ADR-0037 §8 correctly guards ADR-0036: "Before ADR-0036 can be accepted, its release-key
binding semantics must be checked against this ADR's version equivalence (§3.3) and fork
boundary (§7)." This guard ensures ADR-0037 governs the lineage semantics for the release
key rather than ADR-0036 re-specifying them.

No changes to ADR-0037 text are required for acceptance. Status advances to Accepted.

---

## Acceptance Token

`adr_0037_accepted_phase_1173`
