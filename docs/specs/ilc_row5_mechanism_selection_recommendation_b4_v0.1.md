# ILC Row-5 Mechanism Selection Recommendation B-4 v0.1

**Phase:** B-4
**Window:** B-Scope
**Date:** 2026-04-23
**Status:** hold point recommendation

`row5_mechanism_selection_human_gate_pending`

## 1. Decision summary

Recommended mechanism family:

- **Mixing layer**

Recommended parameter range:

- `mix_pool_size = 16..24`
- `num_rounds = 2..5`
- `delay_epochs = 2..4`
- `forward_fraction = 0.85..1.0`
- `shuffle_strategy = uniform`

Recommended simulation-derived bar recommendation, pending B-Impl confirmation:

- Variant A: `<= 0.30`
- Variant B: `<= 0.45`
- Variant C: `<= 0.40`

This recommendation is not a runtime bar. It is a simulation-derived bar
recommendation pending:

1. human confirmation at B-4, and
2. B-Impl live confirmation through SIM-LEAKAGE-03.

## 2. Why mixing is the recommendation

Mixing is the only family that cleared the inherited Phase-740 bars across all
three variants in the B-3 model.

Evidence:

- total old-bar-clearing mixing points: `13`
- lowest-complexity old-bar-clearing point:
  - `pool=16`, `rounds=2`, `delay=4`, `forward=1.0`, `uniform`
  - Variant A `0.251631`
  - Variant B `0.440345`
  - Variant C `0.373525`
  - complexity `0.772500`
  - latency `1.700` epochs

By contrast:

- k-anonymity never drove Variant C below `0.45`
- sealed-sender never drove Variant C below `0.738719`
- sealed-sender without extra balance protection left Variant B near `1.0`

This makes the family comparison straightforward:

- sealed-sender is still a Variant-A tool, not a full Row-5 answer,
- k-anonymity is viable as a fallback or hybrid component, not as the lead
  family,
- mixing is the only family with a complete closure path in the current model.

## 3. Why this parameter range

The recommendation is intentionally a range rather than a single point.

The recommended range captures the portion of the mixing frontier that is
strong enough to matter without simply selecting the single most extreme point:

| Profile | Parameters | A | B | C | Complexity | Latency |
|---|---|---:|---:|---:|---:|---:|
| Balanced clear point | `16 / 2 / 4 / 1.0 / uniform` | `0.251631` | `0.440345` | `0.373525` | `0.772500` | `1.700` |
| Stronger privacy point | `24 / 5 / 2 / 1.0 / uniform` | `0.187076` | `0.370288` | `0.316914` | `0.871323` | `1.793` |
| Strongest explored point | `24 / 5 / 4 / 1.0 / uniform` | `0.071722` | `0.260722` | `0.186786` | `0.911323` | `2.193` |

The selected range keeps the implementation window focused on the real privacy
regime instead of drifting back toward the low-complexity frontier, where the
model no longer supports meaningful privacy claims.

## 4. Why the simulation-derived bar recommendation is set here

Recommended simulation-derived bar recommendation, pending B-Impl confirmation:

- Variant A `<= 0.30`
- Variant B `<= 0.45`
- Variant C `<= 0.40`

Rationale:

- Variant A:
  the recommended mixing band repeatedly reaches the mid-`0.20s`, so `0.30`
  preserves headroom while materially improving on the inherited `0.60`.
- Variant B:
  the recommended mixing band clears `0.45`, but not by a huge margin at the
  lower-cost end. Holding this at `0.45` is a disciplined recommendation rather
  than a cosmetic reset.
- Variant C:
  the recommended mixing band reaches the `0.37` range, so `0.40` is supported
  by the model while still being tighter than the inherited `0.45`.

## 5. Honest uncertainty

The recommendation is strongest on family ranking and weaker on exact decimal
thresholds.

Main uncertainties:

1. **Hosted-query modeling**:
   Variant B is simulated from balance-surface exposure assumptions, not from a
   live mechanism implementation against the real gRPC surface.
2. **Repeated-contributor realism**:
   Variant C is modeled from persistence and release smoothing rather than from
   a live epoch-lineage trace under a new privacy mechanism.
3. **Operational coupling**:
   the model does not simulate queue buildup, failed release windows, or user
   retry behavior, all of which could worsen or shift the live frontier.

This is exactly why the recommendation is framed as a simulation-derived bar
recommendation pending B-Impl confirmation, not as a final runtime bar.

## 6. Explicit answers requested at the hold point

### Does any mixing configuration clear the old `0.45 / 0.60` bands?

Yes. `13` explored mixing configurations did so in the model.

### If not, what were the best achievable floors?

Not applicable, because mixing did clear the old bands. The best-achievable
floors explored anywhere in the model were:

- Variant A `0.071722`
- Variant B `0.260722`
- Variant C `0.186786`

Those floors came from a high-complexity point and are not recommended as the
intended B-Impl target.

## 7. What B-Impl will need to deliver

If the human accepts this recommendation, B-Impl will need to deliver:

- a real mixing implementation rather than further relay indirection only,
- a release policy consistent with the recommended range,
- live instrumentation sufficient to run SIM-LEAKAGE-03,
- measured recall under the intended target,
- an honest closure verdict based on live evidence rather than on this model.

## 8. Human confirmation questions

Please confirm explicitly:

1. Is the recommended mechanism family accepted?
2. Is the recommended parameter range accepted, or do you want it narrowed or widened?
3. Is the recommended simulation-derived bar recommendation accepted as the
   intended B-Impl target pending live confirmation?
4. Any adjustments before the implementation-window scope is locked?
