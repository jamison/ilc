# ADR-0004: Genesis Truth Primitives — commit.epoch and star.map demotion

**Status:** Accepted  
**Date:** 2026-01-29  
**Context:** Protocol Spec & Semantics Freeze (“New Seven”)

---

## Summary

Update the canonical Genesis Truth Primitives list to replace `star.map` with `commit.epoch`. Star maps remain an L2 Development/Experience tool and routing artifact, not a Genesis truth primitive.

---

## Context

The Master Development Plan defines the “New Seven” Genesis Truth Primitives and explicitly demotes `star.map` to a Development/Experience tool. The canonical principle list still listed `star.map` as a truth primitive, creating ambiguity across core docs.

To keep the protocol’s epistemic core clean and consistent with the planning track, we must align the canonical list with the “New Seven” definition.

---

## Decision

Adopt the following Genesis Truth Primitives as canonical:

1. `assert.truth`
2. `validate.claim`
3. `contradict.assert`
4. `refute.claim`
5. `revise.assert`
6. `link.claim`
7. `commit.epoch`

`star.map` is explicitly **not** a Genesis truth primitive. It is an L2 Development/Experience tool that provides routing and navigation artifacts (e.g., star.map route indexes).

---

## Consequences

- Canonical docs now list `commit.epoch` as the time/finalization primitive.
- `star.map` is treated as an L2 routing artifact, not a consensus‑level truth primitive.
- Any future schema or protocol surfaces that enumerate Genesis primitives must use the New Seven list above.

---

## Non‑Goals

- This ADR does not define the `commit.epoch` schema or economics.
- This ADR does not change star.map tooling or artifacts.

---

## References

- `docs/ILC_Master_Development_Plan_v0.4.md` (Protocol Spec & Semantics Freeze — The New Seven)
- `docs/ILC_Master_Principle_List_v5.1.md`
- `docs/specs/star.map.ngram.route_index.v1.md`
