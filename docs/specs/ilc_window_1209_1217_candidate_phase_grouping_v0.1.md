# ILC Window 1209-1217: Candidate Phase Grouping

**Author:** Claude Code (local planning synthesis)
**Date:** 2026-05-05
**Baseline:** Window 1200-1208 CLOSED at Phase 1208 (`window_1200_1208_closed_phase_1208`).
Capsule v5.46 is current. Tier-3 linkage and persistent rate limiter backend implemented.
CDL-086 prelocked. φ-bound enforcement gap confirmed (dead code). Truth-primitive permanence
routed. RC2 gate 1 satisfied; gates 2-6 partially satisfied or open.
**Planning note:** Candidate grouping only. Phase 1209 sequence lock publishes the locked
order. Sensitive phases require explicit human GO.

---

## 1. Window Objective

Window 1209-1217 closes the two largest remaining implementation gaps:

- **φ-bound enforcement** — `EDGE_MINT_PHI_BOUND` is dead code; ECU stripping must be
  implemented in `settle_attribution_batch()` with a new `epoch_node_mint_count` parameter.
- **Truth-primitive permanence ratification packet** — concrete packet defining primitive
  set, ratifier class, event mechanics, threshold, and sunset boundary.

Secondary goals:

- Wire `PersistentFetchRateLimiter` into `HttpFetchTransportRuntime`.
- Advance CDL-086 toward ratification (release artifact manifest schema, distribution
  channel integrity checklist).
- Conditional v0.2 signing ceremony slot.
- Coherence report + capsule v5.47, then close the window.

Non-goals:

- No public launch claim.
- No public repository publication.
- No CDL-086 ratification without counsel track closure.
- No Genesis v0.1 mutation.
- No v0.2 signing without explicit authorization token.

---

## 2. Incoming State

Carry-forward tokens:

- `edge_mint_phi_bound_enforcement_not_yet_implemented`
- `persistent_rate_limiter_wiring_deferred_phase_1202`
- `truth_primitive_permanence_ratification_packet_required_window_1209`
- `cdl_086_prelock_committed_phase_1204`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization`

RC2 gate status:

| # | Gate | Status entering this window |
|---|------|----------------------------|
| 1 | CDL-085 ratified | SATISFIED |
| 2 | v0.2 signing | OPEN |
| 3 | Tier-3 runtime linkage | SATISFIED (`tier3_runtime_linkage_runtime_1201.v0.1`) |
| 4 | Packaging blocker progressed | PRELOCKED — ratification needs 9 conditions from Phase 1204 §5 |
| 5 | Persistent rate limiter | BACKEND IMPLEMENTED — transport wiring deferred |
| 6 | Truth-primitive permanence | ROUTED — ratification packet required |

---

## 3. Phase Table

| Phase | Topic | Sensitivity | Character |
|-------|-------|-------------|-----------|
| 1209 | Window sequence lock | SENSITIVE | Firm; requires `GO Phase 1209` |
| 1210 | φ-bound enforcement spec + implementation | NON-SENSITIVE | Firm; mandated implementation |
| 1211 | Truth-primitive permanence ratification packet | NON-SENSITIVE | Firm; mandated artifact |
| 1212 | Rate limiter transport wiring | NON-SENSITIVE | Firm; mandated implementation |
| 1213 | CDL-086 ratification prep — release artifact manifest + distribution checklist | NON-SENSITIVE | Firm |
| 1214 | CDL-086 ratification evidence + ratification | SENSITIVE / constitutional | Requires `GO Phase 1214` + CDL mutation env; contingent on Phase 1213 + counsel disposition |
| 1215 | v0.2 signing ceremony (conditional) | SENSITIVE if executed | Requires `v0_2_signing_ceremony_authorized_phase_1215` + `GO Phase 1215`; otherwise skip |
| 1216 | Coherence report + capsule v5.47 | NON-SENSITIVE | Firm |
| 1217 | Window closure gate | SENSITIVE | Firm; requires `GO Phase 1217` |

---

## 4. Phase Specifications

### Phase 1210 — φ-bound Enforcement Spec + Implementation

**Mandatory implementation.** `EDGE_MINT_PHI_BOUND` is currently imported but never used
in any settlement logic. This phase must implement ECU stripping in `settle_attribution_batch()`.
If a genuine protocol ambiguity blocks implementation, stop and document the specific
blocker — do not produce a scoping doc.

**Contract change:**

`settle_attribution_batch()` requires a new parameter:

```python
def settle_attribution_batch(
    batch: "EpochAttributionBatch",
    stake_map: dict[str, dict[str, Decimal]],
    emitted_tokens: Optional[list[str]] = None,
    epoch_node_mint_count: int = 0,          # NEW — caller supplies epoch node-mint count
) -> list[tuple[str, Decimal]]:
```

**Enforcement logic (PROVENANCE path only):**

The φ-bound governs the ratio of provenance-equivalent edge-mint events to node-mint events
per epoch. Enforcement belongs at the Python attribution layer (ECU stripping), not at the
Rust graph layer (branchial convergence is a batch/epoch property, not per-edge).

Within `settle_attribution_batch()`, for the PROVENANCE path:
- Track `provenance_events_processed` (count of PROVENANCE events in this batch call).
- Before paying each PROVENANCE event: if `epoch_node_mint_count > 0` and
  `Decimal(provenance_events_processed) / Decimal(epoch_node_mint_count) >= EDGE_MINT_PHI_BOUND`,
  append token `edge_mint_phi_bound_exceeded` to `emitted_tokens` (if provided) and skip
  payout (yield `Decimal("0")` or continue — no ECU emitted).
- If `epoch_node_mint_count == 0`, skip enforcement (no node mints in epoch → ratio
  undefined → allow all PROVENANCE events; this is the safe default for genesis/bootstrap).
- Increment `provenance_events_processed` after each PROVENANCE event regardless of
  whether payout was suppressed.

**Runtime version bump:**

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1210.v0.7"
```

**Minimum tests (in `tests/test_phase_1210_phi_bound_enforcement.py`, minimum 8):**

1. `test_phi_bound_not_enforced_when_node_mint_count_zero` — `epoch_node_mint_count=0`,
   all PROVENANCE events pay out normally
2. `test_phi_bound_allows_events_below_threshold` — ratio < 0.60, all events pay
3. `test_phi_bound_strips_ecu_at_threshold` — ratio reaches exactly 0.60, event at
   threshold is stripped; token `edge_mint_phi_bound_exceeded` emitted
4. `test_phi_bound_strips_ecu_above_threshold` — ratio > 0.60, excess events stripped
5. `test_phi_bound_does_not_affect_reuse_events` — REUSE events unaffected by bound
6. `test_phi_bound_does_not_affect_co_authorship_events` — CO_AUTHORSHIP unaffected
7. `test_phi_bound_uses_decimal_not_float` — confirm `EDGE_MINT_PHI_BOUND` is `Decimal`
   and arithmetic uses no float
8. `test_runtime_version_contains_1210` — version string contains `"1210"` and `"v0.7"`

Also add a regression test to `tests/test_phase_1185_cdl_085_ratification.py` asserting
that submitting PROVENANCE events exceeding the φ-bound suppresses ECU output.

Hard pass condition: all tests pass; `epoch_node_mint_count=0` is backward-compatible
with all existing tests (callers that don't supply it get the genesis-safe default).

Commit subject: `feat(runtime): phase 1210 phi-bound enforcement in settle_attribution_batch`

---

### Phase 1211 — Truth-Primitive Permanence Ratification Packet

**Mandatory artifact.** Per Phase 1206 routing, the next concrete artifact is the
ratification packet. This phase must produce it — not another routing doc.

The packet must specify all seven items from Phase 1206 §4:

1. **Primitive set** — exact list of truth primitives covered by permanence; cite runtime
   modules and CDL/ADR references for each
2. **Evidence bundle** — signed Genesis references, ADR/CDL dependencies, runtime version
   tokens, and any known dissent/exception notes
3. **Ratifier class** — who can ratify; must not be a single agent; should include Genesis
   founding members and at minimum one external witness class
4. **Event mechanics** — signed ceremony, governance vote, CDL, ADR acceptance, or
   combined; specify which
5. **Threshold** — exact quorum/approval rule if a vote is used; no vague language
6. **Sunset boundary** — latest phase/window by which ratification must complete before
   Genesis governance sunset condition is considered unsafe; must be a concrete phase
   number or window bound, not "TBD"
7. **Non-bypass rule** — no public RC / public launch claim may imply truth-primitive
   permanence unless this path completes or is explicitly superseded

If any item cannot be specified without a human decision, record the exact question (one
sentence) — do not leave items as "to be determined."

Deliverable: `docs/specs/ilc_truth_primitive_permanence_ratification_packet_1211_v0.1.md`
Token: `truth_primitive_permanence_ratification_packet_committed_phase_1211`

Minimum tests (3):
1. Packet doc exists
2. Token present in doc
3. All 7 required sections present (parametrize or check individually)

Commit subject: `docs(governance): phase 1211 truth-primitive permanence ratification packet`

---

### Phase 1212 — Rate Limiter Transport Wiring

**Mandatory implementation.** The backend (`PersistentFetchRateLimiter`) is complete and
tested. This phase wires it into `HttpFetchTransportRuntime` behind an opt-in config flag.

Implementation target:

- Add `persistent_limiter_path: Optional[Path] = None` to `FetchTransportConfig` or
  equivalent config struct in `ilc_core/network/d2d/http_fetch_transport_runtime.py`
- When `persistent_limiter_path` is set, instantiate `PersistentFetchRateLimiter` and
  use it for WANT-BLOCK handling instead of the in-memory `FetchRateLimiter`
- Save limiter state on each successful WANT-BLOCK response (or on a configurable
  save-interval if per-request save is too expensive)
- In-memory `FetchRateLimiter` remains the default when `persistent_limiter_path` is None
- No CDL-077 semantic changes — limit value, 429 token, WANT-HAVE behavior all unchanged

Minimum tests (in `tests/test_phase_1212_rate_limiter_wiring.py`, minimum 5):

1. `test_default_config_uses_in_memory_limiter` — no path set → in-memory limiter active
2. `test_persistent_config_loads_limiter` — path set → `PersistentFetchRateLimiter` used
3. `test_persistent_limiter_survives_reload` — save + reload + rate limit respected
4. `test_want_have_unaffected` — WANT-HAVE never rate-limited regardless of config
5. `test_429_token_unchanged` — `fetch_rate_limit_exceeded` token still emitted on over-limit

Token: `persistent_rate_limiter_transport_wiring_committed_phase_1212`

Commit subject: `feat(runtime): phase 1212 persistent rate limiter transport wiring`

---

### Phase 1213 — CDL-086 Ratification Prep

**Mandatory artifacts.** Two of the nine CDL-086 ratification conditions from the prelock
§5 require new documents that don't yet exist:

1. **Release artifact manifest schema** — a machine-verifiable JSON schema for what
   constitutes a public release artifact record; must define required fields, allowed
   artifact types, canonical hash format, and lineage reference format.
2. **Distribution channel integrity checklist** — operational checklist an operator must
   complete before distributing any public release artifact; must cover signing verification,
   lineage chain verification, ADR-0036/0037 compliance, and CDL-086 ratification prerequisite check.

These must be committed as spec documents. They do not ratify CDL-086 — they are
ratification-condition artifacts that Phase 1214 depends on.

Deliverables:
- `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
- `docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md`
- Tests: minimum 3 — both docs exist, both contain version tokens

Tokens:
- `release_artifact_manifest_schema_committed_phase_1213`
- `distribution_channel_integrity_checklist_committed_phase_1213`

Commit subject: `docs(cdl): phase 1213 cdl-086 ratification prep artifacts`

---

### Phase 1214 — CDL-086 Ratification

**SENSITIVE / constitutional.** Requires `GO Phase 1214` and:
```
ILC_CDL_MUTATION_AUTHORIZED=1
ILC_CDL_MUTATION_PHASE=1214
```

**Contingent on:**
- Phase 1213 artifacts committed
- Counsel disposition: either counsel-approved OR explicit human-authorized constitutional
  deferral for each of the 5 counsel items (license, contributor agreement, trademark,
  documentation license, commit-history treatment)
- Human decision on counsel track before `GO Phase 1214`

If counsel disposition is not provided before execution, Phase 1214 is skipped:
`cdl_086_ratification_deferred_pending_counsel_disposition`

**If executed** (two-commit pattern per standard CDL ratification):

Commit 1 — CDL register mutation only:
- CDL register: CDL-086 status PRELOCKED → RATIFIED
- Evidence doc: `docs/specs/ilc_cdl_086_ratification_evidence_1214_v0.1.md`
- CDL-only tests (no runtime imports)
- Token: `cdl_086_ratified_phase_1214`

Commit 2 — none needed (CDL-086 has no runtime constant to activate)

Commit subject: `feat(cdl): CDL-086 public-launch packaging blocker ratified`

---

### Phase 1215 — v0.2 Signing Ceremony (Conditional)

Default: **skip**. Authorize mid-window only after Phases 1210-1214 land cleanly.

Requires `v0_2_signing_ceremony_authorized_phase_1215` + `GO Phase 1215` if executed.
Follows ADR-0036 signing sequence.

Skip token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

### Phase 1216 — Coherence Report + Capsule v5.47

Standard synthesis phase. Record actual verdicts for Phases 1209-1215. Capsule delta:
- `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1210.v0.7"`
- φ-bound enforcement status
- CDL-086 status (ratified or deferred)
- Truth-primitive permanence ratification packet status
- v0.2 signing status
- Signed Genesis v0.1 immutability + diagnostic SHA confirmed

Token: `capsule_v5_47_supersedes_v5_46`

---

## 5. Open Human Decisions

Before or at Phase 1209 sequence lock:

1. **v0.2 signing authorization** — issue `v0_2_signing_ceremony_authorized_phase_1215`
   or confirm carry-forward. Handoff recommends scheduling as an early sensitive phase if
   no blocker found — but only after 1210-1213 land.

2. **CDL-086 counsel disposition** — before `GO Phase 1214`:
   - Either initiate counsel engagement and record partial or full approval, or
   - Issue an explicit human-authorized constitutional deferral for each counsel item.
   Phase 1214 cannot execute without one of these two paths recorded.

3. **Truth-primitive permanence sunset boundary** — Phase 1211 must name a concrete
   phase/window bound. Human input needed: what is the latest acceptable window before
   Genesis governance sunset is considered unsafe? Record before Phase 1211 executes.

---

## 6. Sensitivity Classification

**SENSITIVE** (require explicit GO):
- Phase 1209 (sequence lock)
- Phase 1214 (CDL-086 ratification, if counsel disposition satisfied)
- Phase 1215 (v0.2 signing, if authorized)
- Phase 1217 (closure gate)

**NON-SENSITIVE** (Codex may proceed after prompt approval):
- Phase 1210 (φ-bound enforcement)
- Phase 1211 (permanence ratification packet)
- Phase 1212 (rate limiter wiring)
- Phase 1213 (CDL-086 ratification prep)
- Phase 1216 (coherence + capsule)

**CDL mutation environment** required for Phase 1214 only:
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1214`

---

## 7. Carry-Forward Tokens

Consuming:
- `edge_mint_phi_bound_enforcement_not_yet_implemented`
- `persistent_rate_limiter_wiring_deferred_phase_1202`
- `truth_primitive_permanence_ratification_packet_required_window_1209`
- `cdl_086_prelock_committed_phase_1204`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization`

Expected new tokens:
- `window_1209_1217_sequence_lock_committed`
- `edge_mint_phi_bound_enforcement_implemented_phase_1210`
- `truth_primitive_permanence_ratification_packet_committed_phase_1211`
- `persistent_rate_limiter_transport_wiring_committed_phase_1212`
- `release_artifact_manifest_schema_committed_phase_1213`
- `distribution_channel_integrity_checklist_committed_phase_1213`
- `cdl_086_ratified_phase_1214` OR `cdl_086_ratification_deferred_pending_counsel_disposition`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization` OR signed-v0.2 token
- `truth_primitive_permanence_ratification_packet_committed_phase_1211`
- `capsule_v5_47_supersedes_v5_46`
- `window_1209_1217_closed_phase_1217`

---

## 8. Guardrails

- Do not mutate signed Genesis v0.1.
- Verify immutable diagnostic SHA before Phase 1217:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`
- No `float` for any economic or attribution value — `Decimal` throughout.
- No `assert` for production constraints — `if not: raise ValueError("token")`.
- No wall-clock as protocol source of truth.
- Phase 1210 `epoch_node_mint_count=0` default must preserve backward compatibility
  with all existing tests — verify before commit.
- Phase 1214 requires two-phase check: CDL mutation commit must not include runtime
  changes; runtime bump (if any) is a separate commit. CDL-086 has no runtime constant,
  so Commit 2 may be empty or skipped.
- No CDL-086 public-launch claim from ratification alone — counsel items are ratification
  conditions, not post-ratification conditions.
