# ILC ADR-0019 Graph-Native Governance Boundary Disposition Note v0.1

**Date:** 2026-04-20  
**Phase:** 737  
**Status:** Complete

`adr_0019_disposition_complete_phase_737`
`adr_0019_verdict_accepted_with_scope_amendment`

## 1. Disposition verdict

Verdict: `Accepted with scope-limiting amendment`

ADR-0019 Status field updated to: `Accepted`

The accepted direction is that graph-native governance compilation remains a
real architectural boundary, but its admissible use must be stated more
narrowly than the still-proposed ADR text implied on its own.

## 2. Scope-limiting amendment

The scope-limiting amendment is:

- graph-native compilation of governance constants is the long-horizon
  architectural direction, not a currently authorized action,
- no production governance constant may be moved to graph-native form without a
  dedicated CDL ratification naming the specific constants and their
  graph-native source,
- the kernel boundary section of ADR-0019 is sound as written and is not
  amended,
- this amendment prevents ADR-0019's long-horizon direction from being cited as
  current authorization for graph-native constant compilation.

The practical effect is deliberate:

- ADR-0019 remains the right architectural boundary document,
- it does not silently authorize moving live production constants out of the
  audited code-resident kernel,
- any future move from `kernel_resident` to graph-native compilation requires a
  named constitutional vehicle rather than ADR drift.

## 3. Consistency with live CDLs and ADMs

ADR-0019 as accepted-with-amendment is consistent with the live constitutional
and architecture surface:

- CDL-017: validators are agents, which is compatible with future graph-native
  governance provenance, but no graph-native compilation of validator constants
  is authorized by ADR-0019 alone,
- CDL-066: agent sender authorization remains code-resident in the
  cryptographic kernel; ADR-0019 does not authorize moving that kernel logic
  into graph-native form,
- ADM-003 v0.2: the reference agent architecture keeps protocol interpretation
  separated from runtime adapters and preserves a small audited kernel, which is
  aligned with ADR-0019's accepted boundary.

This means ADR-0019 is consistent with the live repo posture precisely because
it is now read as a boundary document, not as an activation document.

## 4. Activation trigger for revisiting

Revisit ADR-0019 when a specific CDL proposes moving named governance constants
to graph-native form.

Acceptance of ADR-0019 means the boundary direction is sound. It does not
pre-authorize any specific move. The next legitimate activation trigger is a
named CDL that specifies:

- which constants or bounded declarative rule surfaces would move,
- what graph-native source becomes authoritative,
- what deterministic compile boundary is used,
- what audit and rollback path preserves the kernel boundary.
