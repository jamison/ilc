# ILC Window 1565-1575 Handoff

**Version:** v0.1
**Date:** 2026-07-14
**Window:** 1565-1575
**Closure phase:** 1575c
**Closure verdict:** pass
**Public RC status:** `public_rc_live_phase_1575c`

## 1. Window Identity and Closure Basis

Window 1565-1575 was the Block 6 public-RC readiness and publication window. It inherited the pre-RC completion state from Window 1556-1564 and closed the remaining publication gate chain through Phase 1575c.

Closure basis:

- Phase 1574 activation matrix and public-RC readiness assessment.
- Phase 1574-Fix1 economic intent reconciliation.
- Phase 1575a private economic soft-RC production-candidate rehearsal and accepted disposition.
- Phase 1575b economic activation certificate.
- Phase 1575b Fix-series bootstrap, Atlas slice, StarMap installer, LMDB cleanliness, witness lane, wallet, settlement, and epoch-transition rehearsals.
- Phase 1575c-Fix1 verified Genesis v0.5 public-RC signing envelope.
- Phase 1575c sanitized public mirror regeneration and source export verification.
- Phase 1575c-Fix2 corrected the envelope-vs-graph-package scope record,
  repaired the Fix38 LMDB hub defect, and materialized the canonical public-RC
  Atlas graph package pending operator signature.

## 2. Inputs and Inheritance

Key inherited inputs:

| Input | Disposition |
|---|---|
| Window 1556-1564 closure | closed pass |
| Block 6 sequence lock | satisfied |
| Public-RC activation matrix | committed and amended by 1575b certificate |
| Economics soft-RC evidence | accepted as `freeze_retain_candidate` |
| Genesis v0.5 public-RC envelope | signed and verified |
| Genesis v0.5 public-RC Atlas graph package | materialized and LMDB-replay verified; operator signature pending |
| Source allowlist export | pass |
| Sanitized public mirror | regenerated, clean, no push by Codex |
| Atlas LMDB cleanliness | confirmed pre-1575c; Fix38 hub defect repaired in 1575c-Fix2 |

## 3. Closure Verdict Summary

Window 1565-1575 closes with verdict `pass`.

Phase 1575c emits:

- `genesis_v05_public_rc_envelope_consumed_phase_1575c`
- `public_rc_gate_001_authorized`
- `window_1565_closed_phase_1575c`
- `window_1565_closure_gate_verdict=pass`
- `public_rc_live_phase_1575c`
- `public_repository_push_authorized_phase_1575c`
- `post_rc_v05_behavioral_graph_carry_forward_locked_phase_1575c`
- `sanitized_public_mirror_regenerated_phase_1575c`

The public repository push is authorized for the sanitized mirror identified in `docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md`. Codex did not perform the network push or repository visibility change.

## 4. Carry-Forward and Residual Blockers

The following are not blockers to Window 1565-1575 closure, but they are routed forward:

| Item | Routing |
|---|---|
| Full behavioral Genesis v0.5 ceremony | Post-RC v0.5 workstream |
| Behavioral spec nodes and language-neutral conformance receipts | Post-RC v0.5 workstream |
| Economic behavior spec and CDL-048 distributed conversion instrument | First post-RC economic window |
| Guard-clearing runtime activation for public value paths | Separate explicit activation phase; not performed by 1575c |
| Epoch 0 to 1 live transition | Separate explicit activation phase; private rehearsal passed in Fix9 |
| OpenClaw/ClawHub marketplace publication | Separate operator/publication action |
| CDL-002 root identity sovereignty amendment | Sensitive governance lane |
| ADR-0035 type registry runtime activation | Post-RC explicit GO after required governance conditions |
| Werner policy/runtime activation | Post-RC economic/governance lane |
| Graph-derived public mirror exporter | Post-RC graph/materialization lane |
| Local graph-state and slice-installation inventory | Post-RC local-node/sidecar lane; track installed slices, hydrated content availability, and pending local nodes/edges not yet included in a star map |
| Genesis v0.5 Atlas graph package operator signature | 1575c-Fix2 follow-up signing ceremony before claiming signed graph-package completion |

## 5. Next-Window Entry Criteria and Routing

The first post-RC window should start from `docs/specs/ilc_post_rc_architectural_targets_v0.1.md` and the carry-forward register in the Phase 1575c gate artifact.

Recommended first priorities:

1. Economic behavior spec and Decimal/ECU conformance vectors.
2. Distributed CDL-048 mandatory conversion instrument.
3. Guard-clearing activation procedure for rows certified `public_rc_live`.
4. Behavioral spec node schema and language-neutral test vector extraction.
5. Sidecar typed-subgraph schema and post-RC marketplace/installability rules.
6. Local graph-state inventory and slice reconciliation store for day-to-day LMDB use.

## 6. MemPalace Refresh Disposition

MemPalace refresh is routed to the first post-RC planning phase. Phase 1575c did not rebuild MemPalace. The post-RC refresh should index the Phase 1575c gate artifact, this handoff, the updated planning index, and the retained source/mirror evidence records.
