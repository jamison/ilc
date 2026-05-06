# commit.epoch Audit — Call-Site Inventory, vote_weight Scope, Mutation Plan

**Phase:** 1234
**Window:** 1233-1240
**Date:** 2026-05-06
**Status:** complete
**Token:** `commit_epoch_audit_complete_phase_1234`

---

## §1 — commit.epoch Call-Site Inventory

### Active conflict confirmed

`make_commit_epoch_event` in `ilc_core/protocol/event_log.py:295` requires `created_at: str`
as a required positional parameter (line 299). `validate_commit_epoch_payload` at line 201
lists `"created_at"` in the `required_top` set (line 214), and the validator at lines 236-241
parses it with `datetime.fromisoformat(...)`, enforcing ISO 8601 UTC format.

Phase 1226 ratified `timestamp_policy = "epoch_sequence_only_no_wall_clock"` in the canonical
commit.epoch mapping spec. This is an active runtime conflict.

### Complete caller table

| File | Line | `created_at` supplied how | Runtime class |
|------|------|--------------------------|---------------|
| `ilc_core/rc/economic_cycle_runtime.py` | 458 | `created_at=_utc_now()` where `_utc_now()` is `datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")` (line 36-37) | **Production runtime** — RC economic settlement path |
| `ilc_core/sim/devnet_multi_epoch.py` | 107 | `created_at=datetime.now(timezone.utc).isoformat()` (line 111) | **Devnet/sim** — not production consensus; test fixture pattern |

**No other callers** of `make_commit_epoch_event` exist in `ilc_core/`. Grep across
`ilc_core/` confirms only these two call sites plus the definition.

### Additional wall-clock observations in devnet_multi_epoch.py

Lines 61-69 also construct `StakeSnapshot` with
`created_at=datetime.now(timezone.utc).isoformat()` and `total_stake=float(len(stakes))`.
Lines 75, 117 use Python `float` for `reward_total` and `stake_total` in the summary dict
passed to `make_commit_epoch_event`. These floats conflict with the Phase 1226 requirement
that reward/stake be canonical Decimal strings and will require fixing when the commit.epoch
constructor is migrated.

---

## §2 — vote_weight Float Scope Determination

### Site 1: `ilc_core/consensus/finality_evaluator.py`

**Location:** `_aggregate_weights` function, lines 195-200.

```python
def _aggregate_weights(normalized_records: list[dict[str, Any]]) -> dict[str, float]:
    aggregate_weights: dict[str, float] = {}
    for record in normalized_records:
        block_hash = record["block_hash"]
        aggregate_weights[block_hash] = aggregate_weights.get(block_hash, 0.0) + record["vote_weight"]
    return {key: aggregate_weights[key] for key in sorted(aggregate_weights)}
```

**Called by:** `evaluate_epoch_finality` (line 211) and `evaluate_epoch_finality_with_diversity`
(line 236). Both are exported from `ilc_core/consensus/__init__.py`.

**Production import audit:** Only `validator_bootstrap_runtime.py` imports from
`finality_evaluator`, and it imports only the `CDL_051_RATIFICATION_DEPENDENCY` constant,
not the finality evaluation functions. **No production runtime code calls
`evaluate_epoch_finality`.** Only test files do.

**Does float enter `epoch_state_cid` or production settlement?** No. The float
accumulation in `_aggregate_weights` produces comparison results (qualifying hashes) that
are not fed into any hash or settlement computation in the current codebase.

**Classification: Test-exercised consensus code; currently test-only usage. Float does
not enter any hash or settlement computation.**

**Recommended resolution for Phase 1235:** Migrate `_aggregate_weights` accumulator from
`float` to `Decimal` (or require integer weights at API boundary and use integer arithmetic).
This is core consensus finality infrastructure; the migration is a precaution before it is
wired to any production path. Add a comment documenting the Phase 1234 audit verdict.

---

### Site 2: `ilc_core/consensus/circuit_breaker_interface.py`

**Location:** `_normalize_votes`, line 64 acceptance check and line 78 cast.

```python
# line 64:
if isinstance(vote_weight, bool) or not isinstance(vote_weight, (int, float)) or vote_weight <= 0:
    raise CircuitBreakerInterfaceError(...)
# line 78:
'vote_weight': float(vote_weight),
```

**Called by:** `summarize_circuit_breaker_quorum_state` (line 92) and
`verify_circuit_breaker_request` (line 152). Both exported from `ilc_core/consensus/__init__.py`.

**Production import audit:** Grep of `ilc_core/` shows no production runtime imports
`circuit_breaker_interface` directly. The `ilc_core/consensus/__init__.py` re-exports it,
but no production runtime imports from `ilc_core.consensus` other than `finality_evaluator`
(constant only) and `popperian_gate_runtime` (via `epistemic/node_submission_runtime.py`).
**No production runtime code calls `summarize_circuit_breaker_quorum_state`.**

**Does `float(vote_weight)` enter any hash or settlement?** No. The float normalization is
internal to the circuit breaker summarization logic; it does not feed any hash computation
or settlement amount.

**Classification: Test-exercised consensus code; currently test-only usage. Float cast in
internal normalization, does not enter hash or settlement.**

**Recommended resolution for Phase 1235:** Change `_normalize_votes` to reject float inputs
(consistent with Genesis bootstrap int enforcement; aligns with protocol intent). Change
acceptance to `isinstance(vote_weight, int)` only (or `int` plus `Decimal`); remove
`float(vote_weight)` cast at line 78; add rejection test. Document the Phase 1234 audit
verdict in a `# NOTE` comment.

---

### Site 3: `ilc_core/consensus/epoch_state_runtime.py` canonical vectors

**Location:** `_CANONICAL_VECTOR_SPECS` at lines 16-74. Float values: `0.40`, `0.35`, `0.34`,
`0.33` in `vote_weight` fields of test quorum records.

**Module import audit:** `epoch_state_runtime.py` is not imported by any production runtime
code in `ilc_core/`. Grep confirms no `ilc_core` file imports `epoch_state_runtime`. The
module is standalone; its canonical vector specs are consumed by test files.

**Do float values seed production runtime state?** No. The constants are test fixture data
only.

**`_normalize_quorum_record` type pass-through:** The normalizer at line 195-221 calls
`_require_positive_number` on `vote_weight`, which validates positiveness but does not
reject float. Float inputs therefore pass through unchanged. But since no production code
calls this normalizer with these constants, float does not enter production runtime.

**Classification: Test fixture data only. Float values do not seed production runtime state.**

**Recommended resolution for Phase 1235:** Add `# TEST-ONLY` comments to each float
`vote_weight` entry in `_CANONICAL_VECTOR_SPECS`. No code change required for these
constants, but `_require_positive_number` should be updated to enforce `int` (or
`int | Decimal`) so future production callers cannot accidentally pass float.

---

## §3 — Proposed Patch Plan for Phase 1235

### commit.epoch wall-clock: select Option A

**Recommendation: Option A — new canonical constructor.**

Rationale: `economic_cycle_runtime.py` (production) and `devnet_multi_epoch.py` (devnet) both
call the legacy constructor. Option A preserves backward compatibility with existing test
fixtures that supply `created_at`; the legacy constructor can remain callable. Option B
would break all existing test fixtures that supply `created_at` as a required field.

**Files to change in Phase 1235:**

**`ilc_core/protocol/event_log.py`:**
- Add version token: `COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION = "commit_epoch_canonical_constructor_phase_1235.v0.1"`
- Add `make_canonical_commit_epoch_event(epoch_index, epoch_id, namespace_id, finalization_state, summary, checksums, source)` — no `created_at` parameter; payload does not include `created_at` as required top-level field
- Add `validate_canonical_commit_epoch_payload` — `required_top` must NOT contain `"created_at"`; `created_at` may appear only as optional observability annotation not in required fields
- Add `LEGACY_RC_ONLY` marker comment above `make_commit_epoch_event`: "This constructor requires wall-clock `created_at`, which conflicts with Phase 1226 `epoch_sequence_only_no_wall_clock` policy. Use `make_canonical_commit_epoch_event` for all new code. Retained for backward compatibility with existing RC/devnet test fixtures only."

**`ilc_core/rc/economic_cycle_runtime.py`:**
- Migrate call at line 454 from `make_commit_epoch_event(..., created_at=_utc_now(), ...)` to `make_canonical_commit_epoch_event(...)` (no `created_at`)
- Update import: add `make_canonical_commit_epoch_event`, retain `make_commit_epoch_event` if used elsewhere (or remove if not)

**`ilc_core/sim/devnet_multi_epoch.py`:**
- Migrate call at line 107 from `make_commit_epoch_event(..., created_at=datetime.now(...).isoformat(), ...)` to `make_canonical_commit_epoch_event(...)` (no `created_at`)
- Fix `reward_total = float(sum(...))` at line 75 and `stake_total = float(len(stakes))` at line 117 — convert to `Decimal` or `str` before passing to summary dict (see Open questions §4 Q1)
- Update import

**`ilc_core/consensus/finality_evaluator.py`:**
- Migrate `_aggregate_weights` accumulator from float to `Decimal` (initialize to `Decimal("0")`, accumulate with Decimal addition)
- Accept only `int` or `Decimal` vote weights at API boundary; reject float
- Add `# NOTE` comment documenting Phase 1234 audit verdict and Phase 1235 resolution

**`ilc_core/consensus/circuit_breaker_interface.py`:**
- Change `_normalize_votes` line 64 to reject float: `isinstance(vote_weight, bool) or not isinstance(vote_weight, int) or vote_weight <= 0`
- Remove `float(vote_weight)` cast at line 78; store as `int`
- Add rejection test: confirm `vote_weight=0.5` raises `CircuitBreakerInterfaceError`
- Add `# NOTE` comment documenting Phase 1234 audit verdict

**`ilc_core/consensus/epoch_state_runtime.py`:**
- Add `# TEST-ONLY` comment to each float `vote_weight` in `_CANONICAL_VECTOR_SPECS`
- No code change required for the constants; update `_require_positive_number` if it needs to enforce int (see §4 Q3)

### Tests to add or update in Phase 1235

Phase 1235 test contract (11 tests per prompt) covers:
1. `make_canonical_commit_epoch_event` produces valid ProtocolEvent without `created_at`
2. Canonical payload does NOT contain `created_at` as required top-level field
3. Canonical payload passes `validate_canonical_commit_epoch_payload`
4. `make_canonical_commit_epoch_event` does not accept `created_at` as a positional arg
5. `reward_total` and `stake_total` serialized as canonical Decimal strings (not float)
6. Canonical JSON is deterministic across two identical calls
7. Legacy `make_commit_epoch_event` still callable (backward compat for existing tests)
8. `economic_cycle_runtime` now uses canonical constructor (no wall-clock in production path)
9. vote_weight finding: for each production site — confirm float removed or isolated per Phase 1234 §2 resolution
10. vote_weight finding: genesis bootstrap int enforcement still holds
11. Sensitive-runtime guardrail passes: `check_sensitive_runtime_coding_taboos.py`

---

## §4 — Open Questions for Human Review Before Phase 1235 GO

**Q1 — devnet_multi_epoch.py reward/stake float:** Lines 75 and 117 compute
`reward_total = float(sum(...))` and `stake_total = float(len(stakes))` before passing to
the summary dict. If Phase 1235 uses the canonical constructor with Decimal enforcement,
these lines must be converted. **Confirm: Phase 1235 should also convert devnet reward/stake
float to `Decimal` or canonical string.** (Recommended: yes — devnet should be
canonical-compliant to prevent test fixture drift that could mask production bugs.)

**Q2 — finality_evaluator Decimal migration scope:** The `_aggregate_weights` accumulator
currently uses float. Since `evaluate_epoch_finality` is not wired to any production path
today, a `# NOTE` comment alone could suffice. **Confirm: migrate to `Decimal` accumulator
in Phase 1235 (recommended) or defer with comment?** (Recommended: migrate — this is
consensus finality code; better to fix before it goes live.)

**Q3 — circuit_breaker int-only enforcement:** Genesis bootstrap (`validator_bootstrap_runtime.py:70`)
enforces `vote_weight: int`. The circuit breaker currently accepts `int | float`. **Confirm:
Phase 1235 should tighten circuit breaker to reject float inputs, aligning with genesis
bootstrap canonical intent.** (Recommended: yes — reject float, add rejection test.)

**Q4 — `_require_positive_number` type update:** The normalizer in `epoch_state_runtime.py`
does not enforce int for `vote_weight`. If float rejection is added to the circuit breaker
and finality evaluator, it may be consistent to update `_require_positive_number` too.
**Confirm: update or leave as-is for test fixture compatibility?** (Recommended: update to
reject float, since test vectors should use int weights to match genesis bootstrap intent.)

---

`commit_epoch_audit_complete_phase_1234`
