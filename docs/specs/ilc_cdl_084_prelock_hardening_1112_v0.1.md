# CDL-084 Prelock Hardening — Phase 1112

**CDL:** CDL-084 (PROVENANCE Chain Attribution)
**Phase:** 1112
**Date:** 2026-04-29
**Status:** complete
**Preceding commit:** 2066f75d (Phase 1111 CDL-084 opening)

`cdl_084_prelock_hardened_phase_1112`

---

## 1. CDL-084 OPEN State Assertion

Historical assertion command:

```bash
git show 2066f75d:docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md \
  | grep "^\*\*Status:\*\*"
```

Observed output:

```text
**Status:** OPEN
```

This is the Phase 1111 introducing-commit anchor for the Phase 1115 G11 historical assertion.

---

## 2. Pre-Ratification Invariants

All invariants were checked against the current repository state before this document was
committed.

| # | Invariant | Expected | Actual | Result |
|---|-----------|----------|--------|--------|
| I1 | `PROVENANCE_DECAY_ALPHA` type in `ilc_core/types.py` | `float` | `float` | PASS |
| I2 | `PROVENANCE_DECAY_ALPHA` value in `ilc_core/types.py` | `0.5` | `0.5` | PASS |
| I3 | `PROVENANCE_MAX_DEPTH` type in `ilc_core/types.py` | `int` | `int` | PASS |
| I4 | `PROVENANCE_MAX_DEPTH` value in `ilc_core/types.py` | `3` | `3` | PASS |
| I5 | `EdgeType.PROVENANCE` value in `ilc_core/types.py` | `"provenance"` | `"provenance"` | PASS |
| I6 | `AttributionEvent.provenance_chain` field absent | absent | absent | PASS |
| I7 | PROVENANCE silent-ignore stub present in `settle_attribution_batch()` | present | present | PASS |
| I8 | CDL log `CDL-084` row has `opened_phase: 1111` and status `open` | present | present | PASS |

`cdl_084_prelock_invariants_i1_i8_all_pass`

---

## 3. Phase 1113 Commit 1 Targets Locked

Phase 1113 Commit 1 must deliver only the pre-activation runtime shape changes:

- `ilc_core/types.py`: replace `PROVENANCE_DECAY_ALPHA: float = 0.5` with
  `PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.5")`.
- `ilc_core/types.py`: add
  `CDL_084_TYPES_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`.
- `ilc_core/economics/epoch_attribution_settle_runtime.py`: add
  `AttributionEvent.provenance_chain: Optional[tuple[tuple[str, str], ...]] = None`.
- `ilc_core/economics/epoch_attribution_settle_runtime.py`: add
  `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`.
- `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` remains
  `"epoch_attribution_settle_runtime_1106.v0.2"` until Phase 1114 activates the settlement
  path.

Phase 1113 Commit 1 must not implement the PROVENANCE settlement path. The silent-ignore stub
remains active until Phase 1114.

---

## 4. G11 Historical Assertion Commit Reference

Phase 1115 G11 must use:

```text
Phase 1111 introducing commit: 2066f75d
File at that commit: docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md
Expected content at OPEN: **Status:** OPEN
```

`cdl_084_g11_historical_open_assertion_commit_2066f75d`
