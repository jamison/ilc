# CDL-084: PROVENANCE Chain Attribution

**Status:** RATIFIED
**Opened:** Phase 1111 (2026-04-29)
**Ratified:** Phase 1113 (2026-04-29)
**Authority:** CDL-081 §4.3 (PROVENANCE deferred pending H-CON-02) /
             CDL-083 §5.4 (PROVENANCE silence CDL-licensed pending CDL-084) /
             CDL-081 Q1 (PROVENANCE=defer) / ilc_core/types.py
             (PROVENANCE_MAX_DEPTH=3)
**Blocks:** silent-ignore stub for PROVENANCE in `settle_attribution_batch()` in
           `ilc_core/economics/epoch_attribution_settle_runtime.py` (active since Phase 946)

`cdl_084_open_phase_1111`

**Amendment — Phase 1126 (2026-04-30):** Q2 alpha value locked at
`Decimal("0.45")` following SIM-PROVENANCE-01 (Phases 1120-1121). Token updated
to `q2_geometric_decay_alpha_decimal_0_45_locked`. All other Q decisions unchanged.

---

## 1. Problem Statement

PROVENANCE represents derivation credit: when an agent builds work on top of a prior node,
the creator of that ancestor node contributed value. CDL-081 §4.3 deferred PROVENANCE
attribution, leaving an active silent-ignore stub in the attribution settlement runtime.
Agents building on each other's work therefore receive no upstream derivation attribution.

CDL-084 resolves two gaps:

1. **Silent ignore:** `settle_attribution_batch()` silently drops PROVENANCE events.
2. **Unsafe provisional numeric type:** `PROVENANCE_DECAY_ALPHA: float = 0.5` in
   `ilc_core/types.py` is a float adjacent to an economic path and must become
   `Decimal("0.5")` before PROVENANCE settlement is activated.

---

## 2. Human-Gate Decisions

All Q1-Q10 decisions were human-authorized on 2026-04-29 and locked by the Phase 1110
guidance and sequence-lock artifacts.

### Q1 — PROVENANCE ECU trigger and caller-only contract

**PROVENANCE triggers ECU attribution, but only when the caller emits an explicit
PROVENANCE clearance event for the traversal. A single traversal emits either REUSE or
PROVENANCE, not both.**

Rationale: This preserves the no-double-payment intent without adding batch-level or
cross-event detection state to settlement. It follows the same caller-filter pattern as
CDL-083 REFUTATION: the caller is responsible for constructing only semantically valid
events before batch entry.

`q1_provenance_triggers_ecu_caller_only_contract`

### Q2 — Geometric decay

**PROVENANCE payouts use geometric decay with `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`.
Both the mechanism and the alpha value are now locked.**

SIM-PROVENANCE-01 evidence (CDL-084 Q8):
- Run 01 (Phase 1120): alpha `0.45` passes concentration and mint-surface metrics
  (seed 42). Alpha `0.50` fails mint-surface (drift `0.2065` > `0.20` threshold).
- Run 02 (Phase 1121): alpha `0.45` keep rate `3/3` (seeds 42, 1337, 2026).
  Alpha `0.50` keep rate `2/3` (seed-marginal). SIM recommendation: alpha `0.45`.
- Disposition: `docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md`

Rationale: Geometric decay gives immediate ancestors stronger credit while keeping deeper
lineage bounded. `Decimal("0.45")` is exact, avoids float leakage into economic runtime,
and follows the completed SIM-PROVENANCE-01 recommendation.

`q2_geometric_decay_alpha_decimal_0_45_locked`

*(Supersedes: `q2_geometric_decay_alpha_decimal_0_5_provisional`)*

### Q3 — Maximum depth and hop numbering

**`PROVENANCE_MAX_DEPTH = 3`. The immediate parent is hop 1; the maximum included hop is
hop 3.**

Rationale: A three-hop cap is a bounded and understandable derivation horizon. It is already
the provisional constant in `ilc_core/types.py` and does not require simulation to set.

`q3_max_depth_3_hop_1_is_immediate_parent`

### Q4 — Payout recipient

**The creator of each ancestor node receives the PROVENANCE ECU payout.**

Rationale: PROVENANCE is originator credit. It should flow to the agent who created the
ancestor work, not to current occupants or later maintainers. This is consistent with
CDL-081 Q5 for REUSE attribution.

`q4_ancestor_creator_receives_ecu`

### Q5 — Per-event isolation and nearest creator wins

**Settlement uses a fresh `visited_set` per event per CDL-081 §4.1. Within a PROVENANCE
event, `visited_creators` deduplicates creators and the nearest hop wins.**

Rationale: Cross-event state contamination is prohibited by CDL-081. Duplicate creators
within a single ordered chain are handled deterministically by processing nearest ancestors
first.

`q5_fresh_per_event_visited_creators_nearest_hop_wins`

### Q6 — Explicit chain payload and pure settlement

**`AttributionEvent` carries
`provenance_chain: Optional[tuple[tuple[str, str], ...]]`, ordered nearest-ancestor-first.
Each tuple is `(node_id, creator_id)`. The chain length must be no greater than
`PROVENANCE_MAX_DEPTH` for full payout eligibility. `settle_attribution_batch()` makes no
graph queries.**

Rationale: Explicit chain payload keeps settlement pure, deterministic, and testable.
Chain construction and graph traversal are caller responsibilities.

`q6_explicit_chain_payload_nearest_first_pure_settle`

### Q7 — Duplicate handling

**A repeated `node_id` in a provenance chain raises
`ValueError("provenance_chain_contains_duplicate_node_id")`. A repeated `creator_id` is
not an error; the nearest occurrence wins and later occurrences are skipped.**

Rationale: Repeated node IDs indicate malformed or cyclic lineage. Repeated creators can
occur legitimately if one creator authored multiple ancestors; nearest-hop-wins prevents
double payment within one event.

`q7_duplicate_node_id_raises_nearest_creator_wins`

### Q8 — Mint source and simulation obligation

**PROVENANCE attribution is sourced from the epoch mint, consistent with REUSE and
REFUTATION. SIM-PROVENANCE-01 must test the inflation and gaming surface before alpha is
locked.**

Rationale: PROVENANCE is an attribution reward, not a transfer from the downstream agent
or ancestor. The provisional alpha value requires simulation before it becomes final.

`q8_epoch_mint_source_sim_provenance_01_required`

### Q9 — Numeric type lock

**`PROVENANCE_DECAY_ALPHA: float = 0.5` in `ilc_core/types.py` must be replaced with
`Decimal("0.5")` before any economic runtime use. This fix executes in Phase 1113 Commit 1.**

Rationale: Economic runtime must not use Python float. CDL-084 explicitly converts the
provisional alpha into an exact Decimal constant before activating PROVENANCE settlement.

`q9_float_kill_decimal_literal_0_5`

### Q10 — Missing and empty chain validation

**A PROVENANCE event with `provenance_chain=None` raises
`ValueError("provenance_event_missing_chain")`. A PROVENANCE event with
`provenance_chain=()` raises `ValueError("provenance_event_empty_chain")`.**

Rationale: PROVENANCE triggers ECU. A PROVENANCE event with no ancestors is malformed, not
a silent no-op.

`q10_none_raises_missing_empty_raises_empty`

---

## 3. Implementation Targets

### 3.1 `ilc_core/types.py` changes (Phase 1113 Commit 1)

Replace:

```python
PROVENANCE_DECAY_ALPHA: float = 0.5
```

With:

```python
PROVENANCE_DECAY_ALPHA: Decimal = Decimal("0.5")
CDL_084_TYPES_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
```

`PROVENANCE_MAX_DEPTH: int = 3` is already the correct type and value.

### 3.2 `AttributionEvent` extension (Phase 1113 Commit 1)

Add this field to `AttributionEvent` in
`ilc_core/economics/epoch_attribution_settle_runtime.py`:

```python
provenance_chain: Optional[tuple[tuple[str, str], ...]] = None
```

The chain is `((node_id, creator_id), ...)`, ordered nearest-ancestor-first. `None` remains
valid for non-PROVENANCE events.

### 3.3 Dependency token and version posture (Phase 1113 Commit 1 / Phase 1114)

In `epoch_attribution_settle_runtime.py`:

```python
CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
```

`EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` remains
`"epoch_attribution_settle_runtime_1106.v0.2"` through Phase 1113 because Phase 1113 does
not activate the PROVENANCE settlement path. The version bump to
`"epoch_attribution_settle_runtime_1114.v0.3"` is Phase 1114 scope, when the active
PROVENANCE path replaces the silent-ignore stub.

### 3.4 PROVENANCE settlement path (Phase 1114)

Replace the PROVENANCE silent-ignore path with:

```python
elif attr_event.edge_type == EdgeType.PROVENANCE:
    chain = attr_event.provenance_chain
    if chain is None:
        raise ValueError("provenance_event_missing_chain")
    if len(chain) == 0:
        raise ValueError("provenance_event_empty_chain")

    seen_node_ids: set[str] = set()
    for node_id, _ in chain:
        if node_id in seen_node_ids:
            raise ValueError("provenance_chain_contains_duplicate_node_id")
        seen_node_ids.add(node_id)

    visited_creators: set[str] = set()
    for hop_index, (node_id, creator_id) in enumerate(chain):
        if hop_index >= PROVENANCE_MAX_DEPTH:
            break
        if creator_id in visited_creators:
            continue
        visited_creators.add(creator_id)
        decay = PROVENANCE_DECAY_ALPHA ** (hop_index + 1)
        payout = REUSE_ATTRIBUTION_RATE * decay
        payouts.append((creator_id, payout))
```

`PROVENANCE_DECAY_ALPHA` must be `Decimal` before this path is activated. `Decimal ** int`
is exact for this terminating alpha and bounded integer exponent.

---

## 4. Prelock Hardening Checklist

Phase 1112 must confirm:

1. `docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md` exists
   with `**Status:** OPEN`.
2. CDL log contains a CDL-084 row with `opened_phase: 1111`.
3. `PROVENANCE_DECAY_ALPHA: float` is still present in `ilc_core/types.py` as a forward
   obligation for Phase 1113 Commit 1.
4. `AttributionEvent` does not yet have a `provenance_chain` field.
5. `settle_attribution_batch()` still silently ignores PROVENANCE.
6. `PROVENANCE_MAX_DEPTH == 3` is present and typed as `int`.
7. `EdgeType.PROVENANCE == "provenance"` exists.
8. The Phase 1111 introducing commit shows this spec with `**Status:** OPEN`.

---

## 5. Ratification Gate

Ratification is eligible when:

1. Phase 1112 prelock hardening is committed and all §4 items are confirmed.
2. Phase 1113 Commit 1 changes runtime/types only: Decimal alpha, `provenance_chain`, and
   the CDL-084 dependency token. Runtime version remains
   `"epoch_attribution_settle_runtime_1106.v0.2"` until Phase 1114 activates PROVENANCE
   settlement. No `ILC_CDL_MUTATION_AUTHORIZED` env var is used.
3. Phase 1113 Commit 2 changes CDL docs only: this spec moves OPEN → RATIFIED and the CDL
   log row is updated. `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1113` is
   required.
4. Phase 1115 evidence tests pass: at least 30 tests across the evidence groups.

---

## 6. Scope Exclusions

- ATTESTATION and EPOCH_BOUNDARY remain silently ignored.
- Star expansion implementation is not authorized by this CDL.
- SIM-PROVENANCE-01 executes in a separate window; alpha remains provisional until then.
- Werner phi-bound CDL remains a future candidate.
- ADR-0035 implementation CDL remains post-CDL-084.
- CDL-081 and CDL-083 are not amended by this opening.

---

## 7. Prelock Hardening Record (Phase 1112)

**Prelock commit:** Phase 1112 commit (reported by executor)
**Prelock date:** 2026-04-29

All §4 checklist items confirmed:

- CDL-084 spec shows `**Status:** OPEN` at Phase 1111 introducing commit (`2066f75d`).
- CDL log CDL-084 row: `opened_phase: 1111`, status `open`.
- `PROVENANCE_DECAY_ALPHA: float = 0.5` confirmed present in `ilc_core/types.py`
  (float kill pending Phase 1113 Commit 1).
- `AttributionEvent.provenance_chain` field absent (addition pending Phase 1113 Commit 1).
- `settle_attribution_batch()` PROVENANCE silent-ignore stub confirmed present (replacement
  pending Phase 1114).
- `PROVENANCE_MAX_DEPTH: int = 3` confirmed present and correct type.
- `EdgeType.PROVENANCE == "provenance"` confirmed.
- Runtime version remains `epoch_attribution_settle_runtime_1106.v0.2` through Phase 1113;
  v0.3 is deferred to Phase 1114 when the active PROVENANCE path lands.

`cdl_084_prelock_hardened_phase_1112`

---

## 8. Ratification Record (Phase 1113)

**Ratification commit (Commit 2):** Phase 1113 Commit 2 (reported by executor)
**Runtime commit (Commit 1):** 3d943f32
**Ratification date:** 2026-04-29

Phase 1113 ratified CDL-084 in the required two-commit structure:

- **Commit 1** (`ilc_core/` plus stale evidence-test assertion only, no CDL env var):
  float kill (`PROVENANCE_DECAY_ALPHA: float -> Decimal("0.5")`),
  `CDL_084_TYPES_DEPENDENCY` in `ilc_core/types.py`; `AttributionEvent.provenance_chain`
  field, `CDL_084_DEPENDENCY` token, and PROVENANCE imports in
  `epoch_attribution_settle_runtime.py`. Version stays at
  `epoch_attribution_settle_runtime_1106.v0.2` (bump deferred to Phase 1114).
- **Commit 2** (CDL docs only, CDL env var): this spec OPEN -> RATIFIED; CDL log row updated.

Pre-commit hook audit: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1113` used.
No `ilc_core/` changes in Commit 2.

`cdl_084_ratified_phase_1113`

---

## 9. Audit Note

`cdl_mutation_audit`: Phase 1111 CDL log mutation must be committed with
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1111`; the repository hook records
the mutation in `.git/ilc_cdl_mutation_audit.log`.

---

`cdl_084_open_phase_1111`
`cdl_084_ratified_phase_1113`
`cdl_084_q1_q10_all_resolved_at_opening_human_authorized_2026_04_29`
`provenance_decimal_float_kill_forward_obligation_phase_1113_commit_1`
`provenance_explicit_chain_payload_pure_settle_no_graph_queries`
