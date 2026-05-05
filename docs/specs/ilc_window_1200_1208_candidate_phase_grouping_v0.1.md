# ILC Window 1200-1208: Candidate Phase Grouping

**Author:** Claude Code (local planning synthesis)
**Date:** 2026-05-05
**Baseline:** Window 1191-1199 CLOSED at Phase 1199 (`window_1191_1199_closed_phase_1199`).
Capsule v5.45 is current. CDL-086 OPEN (packaging blocker, not ratified). Tier-3 and
persistent rate limiter both scoped but not implemented. Canon bundle repaired. RC2 gate 1
(CDL-085 ratified) is the only satisfied RC2 gate.
**Planning note:** This is a candidate grouping, not a locked sequence. Phase 1200 must
publish the sequence lock before execution. Sensitive phases require explicit human GO.

---

## 1. Window Objective

Window 1200-1208 is an **implementation window**. The prior window established scopes for
Tier-3 runtime linkage and the persistent rate limiter. This window builds them.

Primary goals:

- **Implement** Tier-3 runtime linkage — `ilc_core/node/tier3_runtime_linkage_runtime.py`;
  `schema:*` / `runtime:*` node-class validation; runtime version token; RC2 gate 3.
- **Implement** persistent rate limiter — `ilc_core/network/d2d/persistent_fetch_rate_limiter_runtime.py`;
  hashed requester IDs; atomic write; epoch-counter windowing; restart-survival tests; RC2 gate 5.
- **Advance** CDL-086 deliberation toward prelock — Q1-Q5 from the opening spec must be
  resolved or have explicit carry-forward dispositions.
- **Conditional** v0.2 signing ceremony slot — if `v0_2_signing_ceremony_authorized_phase_120x`
  is issued before execution.
- Coherence report + capsule v5.46, then close the window.

Non-goals:

- No public launch claim.
- No public repository publication.
- No counsel/legal conclusion — counsel engagement is a CDL-086 ratification condition,
  not an opening condition.
- No Genesis v0.1 mutation.
- No v0.2 signing without the explicit signing authorization token.
- No CDL-086 ratification this window unless Q1-Q5 resolve early and the human explicitly
  re-scopes.

---

## 2. Incoming State

Constitutional/runtime frontier:

- CDL-085 ratified; `EDGE_MINT_PHI_BOUND = Decimal("0.60")` active.
- CDL-086 OPEN — public-launch packaging blocker; Q1-Q5 unresolved.
- Runtime: `epoch_attribution_settle_runtime_1185.v0.6`.
- Capsule: v5.45.

RC2 gate status:

| # | Gate | Status |
|---|------|--------|
| 1 | CDL-085 ratified | **SATISFIED** |
| 2 | v0.2 signing | OPEN — authorization absent |
| 3 | Tier-3 runtime linkage | SCOPED — implement this window |
| 4 | Packaging blocker progressed | IN PROGRESS — CDL-086 open, prelock target this window |
| 5 | Persistent rate limiter | SCOPED — implement this window |
| 6 | Truth-primitive permanence governance | OPEN |

Carry-forward tokens into this window:

- `v0_2_signing_ceremony_deferred_pending_signing_authorization`
- `cdl_086_public_launch_packaging_blocker_opened_phase_1194`
- `tier3_runtime_linkage_scope_committed_phase_1195`
- `persistent_rate_limiter_scope_committed_phase_1196`

---

## 3. Phase Table

| Phase | Topic | Sensitivity | Character |
|-------|-------|-------------|-----------|
| 1200 | Window sequence lock | SENSITIVE | Firm; requires `GO Phase 1200` |
| 1201 | Tier-3 runtime linkage implementation | NON-SENSITIVE | Firm; mandated implementation |
| 1202 | Persistent rate limiter implementation | NON-SENSITIVE | Firm; mandated implementation |
| 1203 | CDL-086 deliberation — Q1-Q5 dispositions | NON-SENSITIVE | Firm; prelock target |
| 1204 | CDL-086 prelock | SENSITIVE (CDL prelock doc, no mutation) | Firm if Q1-Q5 resolve; skip+carry token if not |
| 1205 | v0.2 signing ceremony conditional slot | SENSITIVE if executed | Requires `v0_2_signing_ceremony_authorized_phase_1205` + `GO Phase 1205`; otherwise skip |
| 1206 | Truth-primitive permanence governance — first pass | NON-SENSITIVE | Firm; RC2 gate 6 |
| 1207 | Coherence report + capsule v5.46 | NON-SENSITIVE | Firm |
| 1208 | Window closure gate | SENSITIVE | Firm; requires `GO Phase 1208` |

---

## 4. Phase Specifications

### Phase 1201 — Tier-3 Runtime Linkage Implementation

**Mandatory implementation.** Codex must produce working runtime code, not another planning
doc. If a genuine protocol ambiguity is discovered, stop and document the specific blocker;
do not produce a second scoping doc.

Implementation targets (per Phase 1195 plan):

1. Create `ilc_core/node/tier3_runtime_linkage_runtime.py` with:
   - `SchemaNodeRecord` — dataclass or validated dict with required fields:
     `schema_id`, `schema_version`, `schema_digest`, `schema_artifact_ref`,
     `authority_ref`, `lineage_ref`, `status`
   - `RuntimeNodeRecord` — required fields:
     `runtime_id`, `runtime_version`, `implementation_ref`, `schema_refs`,
     `cdl_dependency_refs`, `adr_dependency_refs`, `test_evidence_refs`,
     `lineage_ref`, `status`
   - `validate_schema_node(record: dict) -> dict` — raises `ValueError("token")` on
     missing/invalid fields; no `assert`
   - `validate_runtime_node(record: dict) -> dict` — same
   - Deterministic JSON serialization helper: `sort_keys=True, allow_nan=False,
     separators=(",", ":")`
   - `TIER3_RUNTIME_LINKAGE_VERSION = "tier3_runtime_linkage_runtime_1201.v0.1"`

2. No signed Genesis v0.1 mutation. No new CDL. No wall-clock protocol logic.
3. Use `Decimal` for any numeric fields that represent economic values; `float` banned.

Minimum tests (in `tests/test_phase_1201_tier3_runtime_linkage.py`):

- `test_schema_node_required_fields` — valid record passes; missing each required field
  raises `ValueError`
- `test_runtime_node_required_fields` — same pattern
- `test_runtime_node_schema_refs_linkage` — `schema_refs` must be a non-empty list
- `test_tier3_json_serialization_deterministic` — same input → same bytes across two calls
- `test_tier3_runtime_version_token` — `TIER3_RUNTIME_LINKAGE_VERSION` contains `"1201"`
- `test_no_signed_genesis_mutation` — confirm signed v0.1 hash unchanged
- At least 2 additional tests covering error tokens and status field validation

Minimum test count: **8**.

Runtime version token: `tier3_runtime_linkage_runtime_1201.v0.1`

Commit subject: `feat(tier3): phase 1201 tier-3 runtime linkage implementation`

---

### Phase 1202 — Persistent Rate Limiter Implementation

**Mandatory implementation.** Per Phase 1196 scope, Codex must produce the persistent
backend. Wiring into `HttpFetchTransportRuntime` is allowed only if the seam is small and
testable after inspection. If wiring is too broad, implement and test the backend in
isolation and record the specific wiring blocker — do not defer the backend itself.

Implementation targets (per Phase 1196 plan):

1. Create `ilc_core/network/d2d/persistent_fetch_rate_limiter_runtime.py` with:
   - `PersistentFetchRateLimiter` class:
     - Buckets keyed by `sha256(requester_id)` — never raw IDs
     - Window keyed by caller-supplied `window_id` (int, epoch counter), not wall clock
     - `limit_per_window: int = 10` (matches existing `WANT_BLOCK_RATE_LIMIT_PER_MINUTE`)
     - `max_buckets: int` — hard cap; prune LRU on overflow
     - `check_and_consume(requester_id: str, window_id: int) -> bool`
     - `save(path: Path) -> None` — atomic (temp file + `os.replace`)
     - `load(path: Path) -> "PersistentFetchRateLimiter"` — classmethod; returns fail-closed
       limiter (all buckets at limit) if file is corrupt or schema version mismatch
   - State schema version: `"ilc.fetch_rate_limiter_state@v1"`
   - `PERSISTENT_RATE_LIMITER_VERSION = "persistent_fetch_rate_limiter_runtime_1202.v0.1"`
   - Canonical JSON: `json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))`

2. `FetchRateLimiter` in `truth_primitive_fetch_runtime.py` remains unchanged and default.
   `PersistentFetchRateLimiter` is additive; no CDL-077 semantics change.
3. No wall-clock as protocol truth. No raw requester IDs persisted. No float for counts.

Minimum tests (in `tests/test_phase_1202_persistent_rate_limiter.py`):

- `test_basic_rate_limiting` — check_and_consume allows up to limit, rejects over
- `test_window_reset` — new window_id resets bucket
- `test_max_buckets_cap` — adding more than `max_buckets` unique IDs prunes correctly
- `test_save_and_load_roundtrip` — save then load restores state; same check_and_consume behavior
- `test_corrupt_state_fails_closed` — truncated/invalid JSON → limiter that rejects all requests
- `test_schema_version_mismatch_fails_closed` — wrong schema → fail-closed
- `test_atomic_write` — temp file used; no partial write visible on crash
- `test_requester_ids_hashed` — raw requester ID not present in serialized state
- `test_deterministic_serialization` — same state → same bytes
- `test_runtime_version_token` — `PERSISTENT_RATE_LIMITER_VERSION` contains `"1202"`

Minimum test count: **10**.

Runtime version token: `persistent_fetch_rate_limiter_runtime_1202.v0.1`

Commit subject: `feat(runtime): phase 1202 persistent fetch rate limiter`

---

### Phase 1203 — CDL-086 Deliberation (Q1-Q5 Dispositions)

Resolve or explicitly carry-forward each of the five open questions from the CDL-086
opening spec (`ilc_cdl_086_public_launch_packaging_blocker_opening_1194_v0.1.md`):

| Q | Question | Target disposition |
|---|----------|--------------------|
| Q1 | Release artifact scope — what surfaces constitute public release artifacts? | Select from candidate list or record binding principle |
| Q2 | Public launch trigger — what conditions constitute "public launch"? | Define trigger(s) with bypass-proof language |
| Q3 | RC milestone relationship — does the blocker gate RC2 or RC3/launch only? | Recommendation: not RC2; gates any public launch claim |
| Q4 | Packaging governance — ADR-0036 key chain, distribution channel integrity, version equivalence | Record governing ADRs and any gaps |
| Q5 | Counsel track dependency — sign-off before opening or before ratification? | Recommendation: ratification condition, not opening condition |

Deliverable: `docs/specs/ilc_cdl_086_deliberation_1203_v0.1.md` with disposition table.
Token: `cdl_086_deliberation_committed_phase_1203`

If any question cannot be resolved without human input, record the specific blocker and
required human decision. Do not produce a second open-questions doc — produce dispositions
or explicit blockers.

Commit subject: `docs(cdl): phase 1203 cdl-086 deliberation q1-q5 dispositions`

---

### Phase 1204 — CDL-086 Prelock

**SENSITIVE** — CDL prelock doc only. No CDL register mutation. No `ILC_CDL_MUTATION_AUTHORIZED` required.
Requires `GO Phase 1204`.

Contingent on Phase 1203 resolving Q1-Q5 without open blockers. If Phase 1203 records
unresolved blockers requiring human input, Phase 1204 is skipped and a carry-forward token
is issued: `cdl_086_prelock_deferred_pending_human_q1q5_resolution`.

Deliverables (if executed):

- `docs/specs/ilc_cdl_086_prelock_spec_1204_v0.1.md` — records Q1-Q5 resolutions,
  ratification conditions, counsel track disposition
- Tests: minimum 3 — prelock doc exists, prelock token present, Q1-Q5 each referenced
- Token: `cdl_086_prelock_committed_phase_1204`

Commit subject: `docs(cdl): phase 1204 cdl-086 prelock`

---

### Phase 1205 — v0.2 Signing Ceremony (Conditional)

Default: **skip**. Do not issue signing authorization upfront. v0.2 signing is not required
to implement Tier-3, the rate limiter, or prelock CDL-086. Signing before packaging/prelock
settles adds unnecessary ceremony risk.

The human may issue `v0_2_signing_ceremony_authorized_phase_1205` during the window only
after Phases 1201-1204 land cleanly and signing is still wanted inside this window. If
authorized mid-window, this phase becomes SENSITIVE and requires `GO Phase 1205`.

The signing sequence follows ADR-0036: release key registration → signing ceremony →
release envelope → PLANNING_INDEX + capsule update.

Skip token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

### Phase 1206 — Truth-Primitive Permanence Governance

RC2 gate 6. Firm, non-sensitive.

The carry-forward token `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`
has been open since at least Window 1176. This phase must:

1. Inspect the current truth-primitive permanence surface — what is the specific
   constitutional gap: is it a CDL, an ADR, a community ratification event, or a process doc?
2. Produce either:
   a. A CDL opening if the gap requires constitutional amendment, or
   b. A governance process doc with an explicit ratification pathway, or
   c. A human-decision doc naming the specific question that requires human input before
      any action can be taken
3. Do not produce another indefinite carry-forward without a specific routing decision.

Deliverable: `docs/specs/ilc_truth_primitive_permanence_governance_1206_v0.1.md`
Token: `truth_primitive_permanence_governance_routed_phase_1206`

Commit subject: `docs(governance): phase 1206 truth-primitive permanence routing`

---

## 5. Open Human Decisions

Before or at Phase 1200 sequence lock:

1. **v0.2 signing authorization** — issue `v0_2_signing_ceremony_authorized_phase_1205`
   or confirm carry-forward. Independent of all other phases.

2. **CDL-086 prelock authorization** — confirm Phase 1204 may execute if Q1-Q5 resolve.
   Recommendation: yes; prelock does not ratify.

3. **Truth-primitive permanence governance mode** — Phase 1206 will produce a routing
   decision. Does the human want to pre-authorize a CDL opening in Phase 1206 if
   the gap turns out to require one? Recommendation: allow CDL opening in Phase 1206 if
   the analysis supports it; treat as NON-SENSITIVE since it follows the standard CDL
   opening sensitivity rules (opening = NON-SENSITIVE unless the guidance doc marks it
   otherwise).

---

## 6. Sensitivity Classification

**SENSITIVE** (require explicit GO):
- Phase 1200 (sequence lock)
- Phase 1204 (CDL-086 prelock, if executed)
- Phase 1205 (v0.2 signing, if executed)
- Phase 1208 (closure gate)

**NON-SENSITIVE** (Codex may proceed after prompt approval):
- Phase 1201 (Tier-3 implementation)
- Phase 1202 (rate limiter implementation)
- Phase 1203 (CDL-086 deliberation)
- Phase 1206 (truth-primitive permanence governance)
- Phase 1207 (coherence + capsule)

**Phase 1206 sensitivity is conditional:**
- If Phase 1206 produces only a routing/governance doc → **NON-SENSITIVE**, no GO required.
- If Phase 1206 opens a CDL → **SENSITIVE**, requires `GO Phase 1206` and
  `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1206`.
  Codex must declare which scenario applies before committing.

---

## 7. Carry-Forward Tokens

Window 1200-1208 should consume or preserve:

- `v0_2_signing_ceremony_deferred_pending_signing_authorization`
- `cdl_086_public_launch_packaging_blocker_opened_phase_1194`
- `tier3_runtime_linkage_scope_committed_phase_1195`
- `persistent_rate_limiter_scope_committed_phase_1196`

Expected new tokens:

- `window_1200_1208_sequence_lock_committed`
- `tier3_runtime_linkage_runtime_1201.v0.1`
- `persistent_fetch_rate_limiter_runtime_1202.v0.1`
- `cdl_086_deliberation_committed_phase_1203`
- `cdl_086_prelock_committed_phase_1204` OR `cdl_086_prelock_deferred_pending_human_q1q5_resolution`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization` OR signed-v0.2 token
- `truth_primitive_permanence_governance_routed_phase_1206`
- `capsule_v5_46_supersedes_v5_45`
- `window_1200_1208_closed_phase_1208`

---

## 8. Guardrails

- Do not mutate signed Genesis v0.1.
- Verify immutable diagnostic SHA before Phase 1208 closure gate:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`
  Fix: `git restore out/genesis_compile_coverage_diagnostic_v0.1.json`
- No `float` for economic, attribution, or staking values — use `Decimal`.
- No `assert` for production constraints in `ilc_core/` — use `if not: raise ValueError("token")`.
- No wall-clock as protocol source of truth in the rate limiter.
- No raw requester IDs in persisted rate limiter state.
- No CDL-086 ratification claim from this window.
- No public launch claim.
- Runtime implementation phases (1201, 1202) must produce code that passes tests on commit.
  A second scoping doc is not an acceptable substitute unless a specific protocol blocker
  is documented.
