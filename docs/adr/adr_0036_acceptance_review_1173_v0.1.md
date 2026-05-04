# ADR-0036 Acceptance Review — Phase 1173

**ADR:** ADR-0036 Operational Release Key Genesis Binding
**Review phase:** 1173
**Review date:** 2026-05-04
**Reviewer:** Claude Sonnet 4.6 (local architectural reviewer)
**Prior status:** Proposed (Phase 1159)
**Verdict:** **ACCEPTED**

`adr_0036_accepted_phase_1173`

---

## Sequencing Note

ADR-0037 was reviewed first (see `adr_0037_acceptance_review_1173_v0.1.md`). ADR-0037
is now accepted, establishing the governing version equivalence (§3.3) and fork boundary
(§7) criteria. This review confirms ADR-0036's release-key binding semantics are
consistent with those criteria.

---

## Acceptance Criteria Checklist

### Criterion 1 — Operational release key scope correctly bounded

ADR-0036 §3 Scope section explicitly lists:
- What it covers: key registration, key scope, release-envelope hash binding, key rotation, verifier behavior ✓
- What it does NOT cover: full Genesis Canonical Lineage Contract, network_id derivation, Node 0 Merkle proofs, ECU legitimacy windows, gossip-domain continuity, contributor keys, legal licensing ✓

Token `genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036` is present in §3 ✓.
ADR-0037 now exists and is accepted, closing this deferred obligation. ✓

**Result: PASS.**

### Criterion 2 — Genesis binding semantics consistent with ADR-0037

The ADR-0036 delegation chain (§2):
```
Genesis root envelope
  → release key registration artifact
  → operational release public key
  → release envelope
  → package / star-map / runtime artifact hashes
```

Checked against ADR-0037:
- **Lineage (§1 ADR-0037):** registration artifact must be "signed or explicitly referenced
  by a Genesis root envelope or by a successor envelope whose own authority traces to Genesis"
  (ADR-0036 §4). This satisfies ADR-0037 §1 minimum lineage proof condition 1 and 5. ✓
- **Canonical base object (§2 ADR-0037):** "a release key...whose legitimacy traces to
  the signed Genesis root envelope or to an explicitly authorized successor envelope"
  (ADR-0036 §2). Genesis root envelope is the canonical base. ✓
- **Version equivalence (§3.3 ADR-0037):** ADR-0036 §5 binds release envelopes to artifact
  hashes and "prior release-envelope hash." Version equivalence governs whether a signed
  star-map candidate is a canonical refinement vs a new universe. ADR-0036 correctly
  delegates this question to ADR-0037 rather than redefining it. ADR-0037 §8 states:
  "A release key can sign canonical releases only if the target artifact remains
  version-equivalent and fork-equivalent under this contract." This guard is clear and
  active. ✓
- **Fork boundary (§7 ADR-0037):** same guard applies. If a signed artifact fails the
  fork boundary (loses convergence in any slice), it exits canonical identity and the
  release key does not confer canonical meaning on it. ADR-0036 is silent on this —
  correctly, since ADR-0037 §8 governs it. ✓

**Result: PASS.** ADR-0036 defers all lineage semantics to ADR-0037, which is the right
design. ADR-0037 §8 provides the explicit forward guard from the governing side.

### Criterion 3 — Key rotation policy specified

ADR-0036 §6 specifies:
- Routine rotation only through a forward-linked transition: old key → signed transition
  envelope → new key registration ✓
- Transition envelope must reference prior and new registrations ✓
- Must not retroactively invalidate already-signed releases ✓
- Compromise response: historical releases remain valid artifacts at their signing epoch ✓

**Result: PASS.**

### Criterion 4 — Relationship to v0.2 signing ceremony stated

ADR-0036 §1 lists "versioned star-map candidates" as a signed artifact class ✓.
ADR-0036 §7 notes "public RC envelope transition policy remains a separate obligation" ✓.

The explicit precondition that v0.2 signing requires ADR-0037 version equivalence policy
is stated in ADR-0037 §8 (the governing document). ADR-0036 does not repeat it — this
is appropriate, since repeating governance preconditions in a subordinate ADR would create
maintenance risk. The precondition is active and authoritative from ADR-0037 §8.

**Result: PASS** (governed by ADR-0037 §8 from the authoritative side).

---

## Additional Notes

ADR-0036 was designed explicitly to be a narrow mechanism. Its scope exclusions are
thorough, and the Phase 1159 draft correctly anticipated that the Lineage Contract ADR
would be required separately. With ADR-0037 now accepted:
- All lineage and equivalence semantics governing what the release key may bind to are
  specified in ADR-0037.
- The release key mechanism itself (registration, rotation, envelope binding) is fully
  specified in ADR-0036.
- The two ADRs are non-overlapping and consistent.

The v0.2 signing ceremony may now proceed in Window 1176+ given both ADRs are accepted.

---

## Acceptance Token

`adr_0036_accepted_phase_1173`
