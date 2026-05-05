# ILC Antigravity Context Capsule v5.47

**Date:** 2026-05-05
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.46.md`
**Produced:** Phase 1216, Window 1209-1217
**Frontier:** Window 1209-1217 in progress; Phase 1216 complete; Phase 1217 closure gate pending

`capsule_v5_47_supersedes_v5_46`
`coherence_report_1216_verdict=pass`
`edge_mint_phi_bound_enforcement_implemented_phase_1210`
`truth_primitive_permanence_ratification_packet_committed_phase_1211`
`persistent_rate_limiter_transport_wiring_committed_phase_1212`
`transport_abuse_circuit_breaker_not_final_scaling_policy`
`reciprocal_fetch_admission_model_required`
`release_artifact_manifest_schema_committed_phase_1213`
`distribution_channel_integrity_checklist_committed_phase_1213`
`cdl_086_ratification_deferred_pending_counsel_disposition`
`v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

## 1. Current State

Window 1209-1217 is complete through Phase 1216. Phase 1217 remains pending and is
SENSITIVE.

Current coherence report:

- `docs/specs/ilc_integration_coherence_report_1216_v0.1.md`

Current active window lock and guidance:

- `docs/specs/ilc_phase_1209_1217_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1209_1217_candidate_phase_grouping_v0.1.md`

---

## 2. Runtime Frontier

Attribution runtime:

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1210.v0.7"
EDGE_MINT_PHI_BOUND = Decimal("0.60")
PROVENANCE_DECAY_ALPHA = Decimal("0.45")
CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"
```

Phase 1210 implemented φ-bound enforcement:

```text
edge_mint_phi_bound_enforcement_implemented_phase_1210
```

HTTP fetch transport:

```python
HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_1212.v0.2"
PERSISTENT_RATE_LIMITER_VERSION = "persistent_fetch_rate_limiter_runtime_1202.v0.1"
```

Phase 1212 wired persistent limiter support behind opt-in config. It is an abuse circuit
breaker, not the final ILC-scale communication policy:

```text
transport_abuse_circuit_breaker_not_final_scaling_policy
reciprocal_fetch_admission_model_required
```

---

## 3. Governance Frontier

Truth-primitive permanence:

- Packet committed: `truth_primitive_permanence_ratification_packet_committed_phase_1211`
- Target ratification window: Window 1218-1224
- Hard unsafe-after boundary: Window 1225-1232 closure
- Not ratified in this window

CDL-086:

- Opened Phase 1194
- Prelocked Phase 1204
- Ratification prep artifacts committed Phase 1213:
  - `release_artifact_manifest_schema_committed_phase_1213`
  - `distribution_channel_integrity_checklist_committed_phase_1213`
- Ratification deferred Phase 1214:
  `cdl_086_ratification_deferred_pending_counsel_disposition`

CDL-086 still blocks public launch claims, public repository publication, public release
artifact distribution, public RC announcements, external operator bootstrap, and equivalent
external-reliance acts relabeled as preview/alpha/community/internal.

---

## 4. Genesis Atlas Frontier

Signed Genesis v0.1 remains canonical and unchanged:

- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

Strictly immutable diagnostic:

- `out/genesis_compile_coverage_diagnostic_v0.1.json`
- Expected and confirmed SHA-256:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Unsigned v0.2 candidate:

- Nodes: 41
- Edges: 73
- Status: unsigned candidate
- Signing status: deferred pending signing authorization
- Token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

## 5. RC2 Gate Status

| Gate | Status |
|------|--------|
| CDL-085 ratified and active | **SATISFIED** |
| v0.2 signing ceremony executed | **OPEN** - authorization absent |
| Tier-3 runtime linkage | **SATISFIED** |
| Public-launch packaging blocker evaluated/progressed | **PREP-COMPLETE / DEFERRED** - CDL-086 not ratified |
| Persistent rate limiter | **SATISFIED** - backend implemented and transport wiring committed |
| Truth-primitive permanence community ratification | **PACKET-COMMITTED** - event still required |
| Canon bundle signing/report/audit fixture debt | **SATISFIED** |

---

## 6. Active Carry-Forward Obligations

- Phase 1217 closure gate - requires `GO Phase 1217`
- CDL-086 ratification - pending counsel disposition
- v0.2 signing ceremony - deferred pending explicit signing authorization
- truth-primitive permanence ratification event - target Window 1218-1224
- reciprocal fetch admission model - `reciprocal_fetch_admission_model_required`
- counsel track for CDL-086 - license, contributor agreement, trademark / identity policy,
  public documentation license, existing commit-history treatment

---

## 7. Verification

Window 1209-1217 is verified through Phase 1216:

- Phase 1209 sequence-lock tests passed
- Phase 1210 φ-bound enforcement tests passed
- Phase 1211 truth-primitive permanence packet tests passed
- Phase 1212 persistent rate limiter transport wiring tests passed
- Phase 1213 CDL-086 ratification prep tests passed
- Phase 1214 deferral tests passed
- Phase 1215 signing skip tests passed
- Phase 1216 coherence/capsule tests passed
- Sensitive runtime coding taboo tests passed during runtime phases
- Immutable diagnostic SHA remains:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Phase 1217 closure gate remains pending.

`capsule_v5_47_supersedes_v5_46`
