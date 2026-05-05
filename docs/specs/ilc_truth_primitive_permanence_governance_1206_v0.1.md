# Truth-Primitive Permanence Governance Routing 1206 v0.1

**Phase:** 1206
**Window:** 1200-1208
**Date:** 2026-05-05
**Status:** ROUTED — governance process path selected

`truth_primitive_permanence_governance_routed_phase_1206`

---

## 1. Incoming Carry-Forward

The open carry-forward token is:

```text
truth_primitive_permanence_requires_community_ratification_before_genesis_sunset
```

The token has been carried as a pre-public-RC / RC2 governance item. The concern is that
truth primitives should not become silently permanent only by implementation inertia before
Genesis governance sunset. Permanence needs an explicit ratification path.

---

## 2. Gap Classification

The current gap is a **community-ratification process gap**, not an immediate runtime or
CDL-register mutation.

Why:

- Existing truth primitives are operational and already participate in signed Genesis and
  runtime evidence surfaces.
- The unresolved question is not a numeric runtime constant, data schema, or release-key
  operation.
- The unresolved question is who ratifies permanence, what artifact they ratify, and what
  evidence proves that the ratification occurred before Genesis governance sunset.
- Opening a CDL in Phase 1206 would be premature without a ratification packet defining the
  exact primitive set, evidence bundle, eligible ratifiers, vote/event mechanics, and sunset
  boundary.

Therefore Phase 1206 uses the non-sensitive routing path and does not open a CDL.

---

## 3. Routing Decision

Selected route:

> Draft a governance process packet, then execute a later human-authorized community
> ratification event. A CDL may be opened only after that packet specifies whether the
> community event itself needs constitutionalization.

This is not an indefinite deferral. The next concrete artifact is:

```text
docs/specs/ilc_truth_primitive_permanence_ratification_packet_1209_v0.1.md
```

Recommended Window 1209+ phase token:

```text
truth_primitive_permanence_ratification_packet_required_window_1209
```

---

## 4. Required Ratification Packet Contents

The next packet must specify:

1. **Primitive set:** exact truth primitives covered by permanence.
2. **Evidence bundle:** signed Genesis references, ADR/CDL dependencies, runtime surfaces,
   and any known dissent/exception notes.
3. **Ratifier class:** who can ratify permanence before Genesis governance sunset.
4. **Event mechanics:** whether ratification is a signed ceremony, governance vote, CDL,
   ADR acceptance, or combined process.
5. **Threshold:** exact quorum/approval rule if a vote is used.
6. **Sunset boundary:** the latest phase/window by which ratification must occur before the
   Genesis governance sunset condition is considered unsafe.
7. **Non-bypass rule:** no public RC / public launch claim may imply truth-primitive
   permanence unless this ratification path completes or is superseded by later explicit
   human-authorized constitutional action.

---

## 5. Current RC2 Disposition

RC2 gate 6 moves from **OPEN — governance carry-forward** to:

```text
ROUTED — ratification packet required
```

This routing allows internal RC2 engineering work to continue, but it does not satisfy the
community-ratification requirement and does not authorize public-launch-facing permanence
claims.

---

## 6. Non-Claims

This routing document does not:

- ratify truth-primitive permanence;
- open a CDL;
- accept an ADR;
- define a ratifier class;
- select a quorum threshold;
- authorize Genesis governance sunset;
- authorize public RC or public launch claims;
- mutate signed Genesis v0.1;
- mutate v0.2 candidate artifacts;
- mutate runtime code.

---

## 7. Tokens

```text
truth_primitive_permanence_governance_routed_phase_1206
truth_primitive_permanence_ratification_packet_required_window_1209
```
