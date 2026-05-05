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

**Contract change — two callsites:**

Both `settle_attribution_batch()` and `EpochAttributionBatch.settle()` (the public batch
API at `ilc_core/types.py:134`) must be updated together. `types.py` currently calls
`settle_attribution_batch(self, stake_map, emitted_tokens)` without passing
`epoch_node_mint_count`, leaving the public batch path silently unenforced even after
Phase 1210. Both must carry the new parameter.

`settle_attribution_batch()` in `epoch_attribution_settle_runtime.py`:

```python
def settle_attribution_batch(
    batch: "EpochAttributionBatch",
    stake_map: dict[str, dict[str, Decimal]],
    emitted_tokens: Optional[list[str]] = None,
    epoch_node_mint_count: int = 0,          # NEW — caller supplies epoch node-mint count
) -> list[tuple[str, Decimal]]:
```

`EpochAttributionBatch.settle()` in `ilc_core/types.py`:

```python
def settle(
    self,
    stake_map: dict[str, dict[str, "Decimal"]],
    emitted_tokens: Optional[list[str]] = None,
    epoch_node_mint_count: int = 0,          # NEW — forwarded to settle_attribution_batch
) -> list[tuple[str, "Decimal"]]:
    ...
    return settle_attribution_batch(self, stake_map, emitted_tokens, epoch_node_mint_count)
```

**Enforcement logic (PROVENANCE path only):**

The φ-bound governs the ratio of provenance-equivalent edge-mint events to node-mint events
per epoch. Enforcement belongs at the Python attribution layer (ECU stripping), not at the
Rust graph layer (branchial convergence is a batch/epoch property, not per-edge).

Within `settle_attribution_batch()`, for the PROVENANCE path:
- Track `provenance_events_processed: int = 0` before the batch loop.
- Before paying each PROVENANCE event: if `epoch_node_mint_count > 0` and
  `Decimal(provenance_events_processed) / Decimal(epoch_node_mint_count) >= EDGE_MINT_PHI_BOUND`,
  append token `"edge_mint_phi_bound_exceeded"` to `emitted_tokens` (if provided) and skip
  payout (ECU emitted is `Decimal("0")`).
- If `epoch_node_mint_count == 0`, skip enforcement AND append token
  `"edge_mint_phi_bound_enforcement_skipped_no_node_mints"` to `emitted_tokens` (if provided).
  This makes the skip observable at the call site; callers cannot bypass enforcement silently
  by omission.
- Increment `provenance_events_processed` after each PROVENANCE event regardless of
  whether payout was suppressed.

**Threshold example** (concrete for test authoring):
With `epoch_node_mint_count=5` and `EDGE_MINT_PHI_BOUND=0.60`:
- Event 1: ratio = 0/5 = 0.00 → allow (paid)
- Event 2: ratio = 1/5 = 0.20 → allow (paid)
- Event 3: ratio = 2/5 = 0.40 → allow (paid)
- Event 4: ratio = 3/5 = 0.60 → **STRIP** (≥ 0.60); `edge_mint_phi_bound_exceeded` emitted
- Event 5+: ratio ≥ 0.60 → strip

Exactly 3 PROVENANCE payouts are allowed; the 4th is stripped.

**Runtime version bump:**

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1210.v0.7"
```

**Minimum tests (in `tests/test_phase_1210_phi_bound_enforcement.py`, minimum 10):**

1. `test_phi_bound_skips_enforcement_when_node_mint_count_zero_emits_token` —
   `epoch_node_mint_count=0`, all PROVENANCE events pay out normally AND token
   `edge_mint_phi_bound_enforcement_skipped_no_node_mints` is appended to `emitted_tokens`
2. `test_phi_bound_allows_events_below_threshold` — ratio < 0.60, all events pay
3. `test_phi_bound_strips_ecu_at_threshold` — `epoch_node_mint_count=5`; events 1-3 pay
   (ratios 0/5, 1/5, 2/5 < 0.60); event 4 is stripped (ratio 3/5 = 0.60 ≥ bound);
   token `edge_mint_phi_bound_exceeded` emitted
4. `test_phi_bound_strips_ecu_above_threshold` — ratio > 0.60, subsequent events stripped;
   ECU payout is `Decimal("0")` for stripped events
5. `test_phi_bound_does_not_affect_reuse_events` — REUSE events unaffected regardless of ratio
6. `test_phi_bound_does_not_affect_co_authorship_events` — CO_AUTHORSHIP events unaffected
7. `test_phi_bound_uses_decimal_not_float` — `EDGE_MINT_PHI_BOUND` is `Decimal`; ratio
   computation uses no `float`; verify `isinstance(EDGE_MINT_PHI_BOUND, Decimal)`
8. `test_runtime_version_contains_1210` — version string contains `"1210"` and `"v0.7"`
9. `test_batch_settle_method_forwards_epoch_node_mint_count` — `EpochAttributionBatch.settle()`
   in `ilc_core/types.py` accepts `epoch_node_mint_count` and φ-bound is enforced through
   that path (not just via the direct `settle_attribution_batch()` call)
10. `test_negative_epoch_node_mint_count_raises` — negative `epoch_node_mint_count` raises
    `ValueError("epoch_node_mint_count_must_be_non_negative")`

Also add a regression test to `tests/test_phase_1185_cdl_085_ratification.py` asserting
that submitting PROVENANCE events exceeding the φ-bound suppresses ECU output.

Hard pass condition: all 10 tests pass; `epoch_node_mint_count=0` is backward-compatible
with all existing tests (callers that don't supply it get the genesis-safe default and
emit the skip token). The skip token must be emitted — the zero-count path is not silent.

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

**Design boundary.** This phase is a transport abuse circuit breaker, not the final ILC
scaling model for agent communication. Static caps are acceptable as node-local DoS
protection for early/public nodes, but they must not become the long-term economic policy
for a network intended to serve many fast digital agents. The long-term direction is
reciprocal fetch admission: useful, reciprocal, reputable, staked, or otherwise
work-contributing peers should earn more pull capacity; extractive peers should face
rising cost, proof burden, or lower priority. Phase 1212 must therefore carry forward:

`reciprocal_fetch_admission_model_required`

Future model sketch:
- baseline free `WANT-BLOCK` capacity
- additional capacity from CDL-078 routing reputation / successful serves
- additional capacity from ECU/stake escrow or paid priority fetch
- optional symbolic Hashcash-style puzzle for unknown peers with no reputation
- abuse debt / low-reciprocity penalty for peers whose inbound pull pressure greatly
  exceeds useful outbound contribution
- static limiter remains only an emergency brake while this model is not implemented

Implementation target:

- Add `persistent_limiter_path: Optional[Path] = None` to `FetchTransportConfig` or
  equivalent config struct in `ilc_core/network/d2d/http_fetch_transport_runtime.py`
- When `persistent_limiter_path` is set, call `PersistentFetchRateLimiter.load(path)`.
  The backend's `load()` is fail-closed: on corrupt/missing/version-mismatch state, it
  returns a fresh fail-closed limiter internally. The wiring layer must preserve this
  behavior AND make it observable: detect whether a reset occurred (e.g. by comparing
  state before and after, or by inspecting load return metadata) and append token
  `"persistent_rate_limiter_state_reset_on_load_failure"` to the transport's emitted
  tokens list. Do not silently discard the reset.
- Save limiter state on each successful WANT-BLOCK response (or on a configurable
  save-interval if per-request save is too expensive)
- In-memory `FetchRateLimiter` remains the default when `persistent_limiter_path` is None
- No CDL-077 semantic changes — limit value, 429 token, WANT-HAVE behavior all unchanged
- Documentation/status output for Phase 1212 must describe the limiter as
  `transport_abuse_circuit_breaker_not_final_scaling_policy`.

Minimum tests (in `tests/test_phase_1212_rate_limiter_wiring.py`, minimum 6):

1. `test_default_config_uses_in_memory_limiter` — no path set → in-memory limiter active
2. `test_persistent_config_loads_limiter` — path set → `PersistentFetchRateLimiter` used
3. `test_persistent_limiter_survives_reload` — save + reload + rate limit respected
4. `test_want_have_unaffected` — WANT-HAVE never rate-limited regardless of config
5. `test_429_token_unchanged` — `fetch_rate_limit_exceeded` token still emitted on over-limit
6. `test_persistent_limiter_load_failure_emits_degradation_token` — corrupt/missing state
   → limiter starts fresh AND `persistent_rate_limiter_state_reset_on_load_failure` emitted

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
- Phase 1212 circuit-breaker boundary:
  `transport_abuse_circuit_breaker_not_final_scaling_policy`
- Carry-forward token:
  `reciprocal_fetch_admission_model_required`
- Signed Genesis v0.1 immutability + diagnostic SHA confirmed

Token: `capsule_v5_47_supersedes_v5_46`

---

## 5. Human Decisions (RESOLVED 2026-05-05)

1. **v0.2 signing authorization** — DEFERRED. Do not sign before Phase 1210 φ-bound
   enforcement and Phase 1212 transport wiring are implemented and closed. Target is the
   next window after 1217, assuming no closure-gate findings. Phase 1215 is skip-default
   this window; carry forward `v0_2_signing_ceremony_deferred_pending_signing_authorization`.

2. **CDL-086 counsel disposition** — CONDITIONAL SKIP. Do not execute Phase 1214 unless
   all five counsel items (license, contributor agreement, trademark, documentation license,
   commit-history treatment) have explicit dispositions. If counsel is not ready, Phase 1214
   records `cdl_086_ratification_deferred_pending_counsel_disposition` and skips.

3. **Truth-primitive permanence sunset boundary** — RESOLVED. Target ratification window:
   **Window 1218-1224**. Hard unsafe-after boundary: **Window 1225-1232 closure**. No
   public RC claim or public launch claim may imply truth-primitive permanence after that
   boundary unless ratification completes or is explicitly superseded by a ratified CDL.
   Phase 1211 must record these bounds in the packet.

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
- `transport_abuse_circuit_breaker_not_final_scaling_policy`
- `reciprocal_fetch_admission_model_required`
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
- Do not frame static rate limiting as ILC's long-term communication policy. It is an
  abuse circuit breaker until reciprocal fetch admission is designed and implemented.
