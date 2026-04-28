# ILC Window 945–952: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-04-28
**Baseline:** Window 939–944 CLOSED (Phase 944 coherence report). CDL-081 ratified (Phase 943).
Capsule v5.31. 7,643 tests passing. Phase numbering: normal lane at 944; next available 945.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 945–950 are the
hard minimum lane. Phases 951–952 are coherence and closure — fixed tail. No conditional tail
slots this window.

---

## 1. Window Identity and Scope

**Window 945–952** covers three interleaved tracks following CDL-081 ratification:

1. **Capsule v5.32** — closes the forward obligation recorded in the Phase 944 coherence report.
   Brings the context capsule current for the post-H-013 / post-CDL-081 frontier.

2. **H-012 Attribution Settlement Runtime** — implements `EpochAttributionBatch.settle()` as
   specified in CDL-081 §§4.1–4.6. This is the first H-series runtime that CDL-081 unlocks.
   CDL-081 is the sole blocker; it is now ratified. H-CON-02 (panel quorum rules) remains a
   forward obligation and gates only the ejected-stake treasury sub-path — all other CDL-081
   paths are implementable now.

3. **CDL-082 H-013 Emission Threshold Amendment** — constitutionalises the SIM-BEACON-01
   recommendation to raise `H013_CHANGE_THRESHOLD` from 0.10 to 0.15. SIM evidence exists
   (Phase 939 results). No new simulation required. CDL opens, prelock-hardens, and ratifies
   within this window. Ratification requires a two-commit runtime mutation
   (`ilc_core/node/node_startup_runtime.py`).

Additionally, the Phase 944 code audit finding M1 (float ECU rates) is addressed inline in
Phase 946 as a pre-H-012 precision fix — no standalone phase required.

**Tail-slot policy:** This window has no conditional tail slots. The window is fully determined
at entry. Werner φ-bound CDL and H-CON-02 are explicitly deferred (see §Non-goals).

---

## 2. Baseline and Inheritance

### 2.1 Ratified CDL Chain (relevant portion)

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-073 | Ratified | 860 | RC1 homoiconic bootstrap schema |
| CDL-074 | Ratified | 870 | Truth primitive runtime |
| CDL-075 | Ratified | 884 | Truth primitive graph persistence |
| CDL-076 | Ratified | 897 | Truth primitive announcement gossip (L1) |
| CDL-077 | Ratified | 904 | WANT-HAVE/WANT-BLOCK fetch (L2) |
| CDL-078 | Ratified | 911 | Relay incentive constitutional lock (L5) |
| CDL-079 | Ratified | 918 | HB-002 bootstrap distribution protocol |
| CDL-080 | Ratified | 927 | Star.map N-gram route index (L3) |
| CDL-081 | **Ratified** | **943** | **Hyperedge ECU attribution** |
| CDL-082 | To be opened | 948 | H-013 emission threshold amendment (this window) |

Next fresh CDL number after this window: **CDL-083**.

### 2.2 Active Runtime Chain (relevant portion)

| Module | Version token | Phase |
|--------|---------------|-------|
| `ilc_core/types.py` — `REUSE_ATTRIBUTION_RATE` | `Decimal("0.20")` | 943 |
| `ilc_core/types.py` — `EpochAttributionBatch.settle()` | `NotImplementedError(CDL_HCON_01_DEPENDENCY)` | 943 |
| `ilc_core/economics/passive_ecu_attribution_runtime.py` | `float` rate (audit M1 — to fix Phase 946) | pre-944 |
| `ilc_core/network/star_map/star_map_route_index_runtime.py` | `star_map_route_index_runtime_923.v0.1` | 923 |
| `ilc_core/network/d2d/spectral_beacon.py` | Epoch-keyed replay cache (Phase 0928x) | 0928x |
| `ilc_core/node/node_startup_runtime.py` | `H013_CHANGE_THRESHOLD: float = 0.1` | H-013 |
| `ilc_consensus/` Rust crate | blahaj 0.6.0, rustls-webpki 0.103.13 (Phase 0919x) | 0919x |

### 2.3 Canonical Anchors Inherited

- Capsule v5.31 — PRIMARY context reference (to be superseded by v5.32 in Phase 945)
- Phase 944 coherence report — forward obligations and remediation record
- CDL-081 spec — `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md`
- SIM-BEACON-01 results — `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`
- Phase numbering remediation: normal lane 945–989, skip 990–1099, resume 1100+

---

## 3. Track Inventory

### 3.1 Constitutionally Obligated (this window)

| Obligation | Source | Prerequisite met? |
|------------|--------|-------------------|
| H-012: `EpochAttributionBatch.settle()` runtime | CDL-081 §§4.1–4.6 | Yes — CDL-081 ratified Phase 943 |
| CDL-082: H-013 threshold amendment | Phase 944 coherence report §7 | Yes — SIM-BEACON-01 Phase 939 |
| Capsule v5.32 | Phase 944 coherence report §7 | Yes — coherence report complete |
| Decimal precision fix (Audit M1) | Phase 944 audit finding M1 | Yes — identified, no blocker |

### 3.2 Deferred Governance (not this window)

| Item | Reason for deferral |
|------|---------------------|
| H-CON-02: Panel hyperedge quorum rules | Large CDL — own window; CDL-081 ✅ prerequisite met |
| Werner φ-bound CDL (`EDGE_MINT_PHI_BOUND = None`) | Needs SIM evidence; no SIM yet |
| SIM-BEACON-01 adversary model revision | Revised adversary model with sealed-sender constraints — future SIM window |
| H-011 patent assessment | Ongoing — non-blocking for testnet |

### 3.3 Simulation-Conditional (not this window)

None this window. All simulation work for active tracks is complete (SIM-BEACON-01, SIM-REUSE-01).

---

## 4. H-012 Attribution Settlement Runtime Scope

### 4.1 What H-012 Implements

`EpochAttributionBatch.settle()` currently raises `NotImplementedError(CDL_HCON_01_DEPENDENCY)`.
This was a CDL-081 prerequisite guard. CDL-081 is now ratified. H-012 implements the CDL-081
attribution formulas:

| CDL-081 Section | Content | Implementable? |
|-----------------|---------|----------------|
| §4.1 REUSE edge attribution | `attribution_ECU = REUSE_ATTRIBUTION_RATE` per traversal | **Yes** |
| §4.2 CO_AUTHORSHIP star node | `ECU_i = total × (stake_i / Σ stake_j)` | **Yes** (static stake map) |
| §4.3 Edge type scope | REUSE + CO_AUTHORSHIP trigger; others excluded | **Yes** |
| §4.4 Buy-in and decay | CDL-V1 temporal decay from buy-in epoch | **Yes** (delegates to `temporal_decay_runtime`) |
| §4.5 Ejection fallback | Ejected stake → treasury (H-CON-02 quorum required) | **Partial** — stub with `CDL_HCON_02_DEPENDENCY` |
| §4.6 Zero-member commons | Attribution suspended; accumulates to CDL-047 treasury | **Yes** |

### 4.2 Implementation Target Files

| File | Change |
|------|--------|
| `ilc_core/economics/epoch_attribution_settle_runtime.py` | **NEW** — settlement logic for §§4.1–4.6 |
| `ilc_core/types.py` | Update `settle()` stub: remove `CDL_HCON_01_DEPENDENCY` guard, delegate to runtime |
| `ilc_core/economics/passive_ecu_attribution_runtime.py` | Fix M1: `PASSIVE_ATTRIBUTION_RATE` float → `Decimal` |
| `tests/test_phase_0946_h012_epoch_attribution_settle.py` | **NEW** — 30 tests |

### 4.3 settle() Runtime Design (Phase 946 spec)

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_946.v0.1"
CDL_081_DEPENDENCY = "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"
CDL_HCON_02_DEPENDENCY = "h_con_02_cdl_required_before_ejected_stake_treasury_executes"
```

**New type — `AttributionEvent`** (defined in `epoch_attribution_settle_runtime.py`):
```python
@dataclass(frozen=True)
class AttributionEvent:
    edge_type: EdgeType          # REUSE or CO_AUTHORSHIP (others ignored per CDL-081 §4.3)
    target_creator_id: str       # REUSE: creator of target node (receives attribution_ECU)
    star_node_id: Optional[str]  # CO_AUTHORSHIP: star node identifier (for stake lookup)
    epoch: int                   # Epoch at which traversal was cleared
```

**Stake map structure (CO_AUTHORSHIP):**
`stake_map` passed to `settle_attribution_batch` is typed as:
```python
stake_map: dict[str, dict[str, Decimal]]
  # outer key: star_node_id
  # inner dict: {member_agent_id: stake_amount}
  # Empty inner dict → zero-member commons path (§4.6)
```
For REUSE events, `stake_map` is not accessed (target_creator_id is used directly).

**Runtime function:**
```python
settle_attribution_batch(
    batch: EpochAttributionBatch,
    stake_map: dict[str, dict[str, Decimal]],
) -> list[tuple[str, Decimal]]
```
— accepts a batch of `AttributionEvent` objects + CO_AUTHORSHIP stake snapshot at epoch `t`
— returns list of `(agent_id, ecu_amount)` payouts (all amounts Decimal)
— raises `NotImplementedError(CDL_HCON_02_DEPENDENCY)` for the ejected-stake treasury path

**Updated `EpochAttributionBatch` in `types.py`** (Phase 946 changes):
```python
# Before (Phase 946 removes these):
EPOCH_ATTRIBUTION_BATCH_VERSION = "epoch_attribution_batch.v0.1_stub"
CDL_HCON_01_DEPENDENCY = "h_con_01_cdl_required_before_settle_executes"
# ...
def settle(self) -> None:
    raise NotImplementedError(CDL_HCON_01_DEPENDENCY)

# After (Phase 946 writes):
EPOCH_ATTRIBUTION_BATCH_VERSION = "epoch_attribution_batch.v0.2"
# (CDL_HCON_01_DEPENDENCY constant removed — no longer needed)
# ...
def settle(
    self,
    stake_map: dict[str, dict[str, Decimal]],
) -> list[tuple[str, Decimal]]:
    """Process all events and execute ECU attribution transfers.
    CDL-081 §§4.1–4.6. Partial: ejected stake treasury deferred to H-CON-02.
    """
    from ilc_core.economics.epoch_attribution_settle_runtime import settle_attribution_batch
    return settle_attribution_batch(self, stake_map)
```

Also update the stale comment block in `types.py` above `EPOCH_ATTRIBUTION_BATCH_VERSION`:
- Remove: "Gate: H-CON-01 CDL must be ratified before settle() can execute"
- Replace with: "CDL-081 ratified (Phase 943). H-012 runtime in epoch_attribution_settle_runtime.py."

The `visited_set` per event (CDL-081 §4.1: "each event processed with fresh visited_set")
prevents cross-event state contamination. No global mutable state in the settle path.

### 4.4 Precision Requirements

All ECU arithmetic in the settlement runtime uses `Decimal`. No float. `REUSE_ATTRIBUTION_RATE`
is already `Decimal("0.20")` in `ilc_core/types.py`. The fix to
`passive_ecu_attribution_runtime.py` converts `PASSIVE_ATTRIBUTION_RATE = 0.20` (float) to
`PASSIVE_ATTRIBUTION_RATE = Decimal("0.20")` — all compute methods in that module must be
updated to propagate Decimal through. Note: `passive_ecu_attribution_runtime.py` is an
analysis/passive module; updating to Decimal is a precision hardening, not a semantic change.

### 4.5 H-012 Test Structure (30 tests)

| Test group | Count | Scope |
|-----------|-------|-------|
| REUSE attribution single creator | 5 | Basic path: one REUSE traversal, one creator |
| REUSE attribution multiple events per epoch | 3 | Batch accumulation, epoch isolation |
| CO_AUTHORSHIP proportional split | 5 | 2-member, 3-member, unequal stakes |
| CO_AUTHORSHIP zero-member commons | 3 | Attribution suspended, treasury token |
| CDL-V1 temporal decay integration | 3 | Late buy-in naturally discounted |
| Ejected stake treasury guard | 2 | `CDL_HCON_02_DEPENDENCY` raises NotImplementedError |
| Decimal precision invariants | 4 | No float leakage, canonical string output |
| `visited_set` epoch isolation | 3 | Cross-event state contamination blocked |
| Version token present | 1 | `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION` check |
| Dependency token present | 1 | `CDL_081_DEPENDENCY` check |

**Total: 30 tests.**

---

## 5. CDL-082 H-013 Emission Threshold Amendment Scope

### 5.1 Constitutional Basis

`H013_CHANGE_THRESHOLD: float = 0.1` (in `ilc_core/node/node_startup_runtime.py`) was set
at H-013 activation. SIM-BEACON-01 (Phase 939) found that threshold=0.10 puts the emission
system in a spurious-emission regime (small spectral changes trigger unnecessary beacon
emissions). Threshold=0.15 exits this regime. This is a constitutionally observable parameter
change — it alters beacon emission frequency, which affects privacy and bandwidth tradeoffs.
A CDL amendment is required before changing this value in any deployment.

### 5.2 SIM-BEACON-01 Evidence (pre-existing)

From `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`:
- `H013_TESTNET_EMISSION_SIGMA = 0.05` — keep (routing correctness 97.65%)
- `H013_CHANGE_THRESHOLD` → raise 0.10 → 0.15 (exits spurious-emission regime)
- `DEFAULT_DEAD_PEER_SILENCE_EPOCHS = 10` — confirmed at 0% false-dead rate

The threshold recommendation is standalone — it does not depend on the adversary model
revision (which addresses a separate sigma calibration question).

### 5.3 CDL-082 Decision Digest

| Field | Value |
|-------|-------|
| Title | H-013 gossip beacon emission threshold amendment |
| Authority | CDL-079 (H-013 activation); SIM-BEACON-01 (Phase 939) |
| Question | Should `H013_CHANGE_THRESHOLD` be raised from 0.10 to 0.15? |
| Evidence | SIM-BEACON-01 spurious-emission regime finding |
| Decision | Yes — raise to 0.15 |
| Runtime mutation | `ilc_core/node/node_startup_runtime.py:H013_CHANGE_THRESHOLD = 0.15` |
| Out of scope | Sigma parameter, adversary model revision, mainnet sigma change |

### 5.4 Two-Commit Ratification Pattern

CDL-082 ratification (Phase 950) follows the established two-commit CDL pattern
(CDL-081 precedent, Phases 942–943):

- **Commit 1 (runtime mutation):** `ilc_core/node/node_startup_runtime.py` —
  `H013_CHANGE_THRESHOLD = 0.15`. No `ILC_CDL_MUTATION_AUTHORIZED` env var. No CDL log changes.
- **Commit 2 (CDL mutation):** CDL-082 spec OPEN → RATIFIED + CDL log entry. Requires
  `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=950`.

Pre-commit hook enforces: if `ILC_CDL_MUTATION_AUTHORIZED=1` is set, commit must NOT touch
`ilc_core/` files. Both commits must pass this gate independently.

### 5.5 CDL-082 File Targets

| File | Change |
|------|--------|
| `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md` | **NEW** — CDL-082 spec (Phase 948) |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-082 row inserted (Phase 948 open; Phase 950 ratified) |
| `ilc_core/node/node_startup_runtime.py` | `H013_CHANGE_THRESHOLD = 0.15` (Phase 950 Commit 1) |
| `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_ratification_evidence_949_v0.1.md` | **NEW** — prelock + evidence (Phase 949) |

---

## 6. CDL Number Assignments

| CDL | Title | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------|----------------------|---------------|-------------------|
| CDL-082 | H-013 gossip beacon emission threshold amendment | `H013_CHANGE_THRESHOLD=0.15` | Phase 948 | Phase 950 |

CDL-082 is pre-authorized (evidence from SIM-BEACON-01 already exists; decision is not
governance-contingent). No conditional CDLs this window.

Next CDL after this window: **CDL-083**.

---

## 7. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 945 | Window 945–952 sequence lock + capsule v5.32 | Foundation / Constitutional | NON-SENSITIVE |
| 2 | 946 | H-012 settle() runtime + Decimal precision fix (M1) | Runtime | NON-SENSITIVE |
| 3 | 947 | H-012 ratification evidence (30 tests) | Runtime | NON-SENSITIVE |
| 4 | 948 | CDL-082 opening — H-013 threshold amendment | Constitutional | **SENSITIVE** |
| 5 | 949 | CDL-082 prelock hardening + ratification evidence doc | constitutional | NON-SENSITIVE |
| 6 | 950 | CDL-082 ratification (two-commit: runtime + CDL) | Constitutional / Runtime | **SENSITIVE** |
| 7 | 951 | Coherence report + capsule v5.33 | Synthesis | NON-SENSITIVE |
| 8 | 952 | Window 945–952 closure gate | Gate | **SENSITIVE** |

### Phase 945 note — Sequence lock + capsule

The sequence lock document commits the phase table above as the authoritative plan for this
window. The capsule v5.32 update is in the same commit. Together these constitute Phase 945.
Neither is a CDL mutation. Sensitivity: NON-SENSITIVE.

### Phase 946 note — Runtime without CDL mutation

Phase 946 creates a new `ilc_core/economics/epoch_attribution_settle_runtime.py` and updates
`ilc_core/types.py` (settle() delegation) and `ilc_core/economics/passive_ecu_attribution_runtime.py`
(Decimal fix). No CDL doc is mutated. The pre-commit hook permits `ilc_core/` changes in
non-CDL commits. Sensitivity: NON-SENSITIVE.

### Phase 948 note — CDL-082 opening (SENSITIVE)

CDL-082 is opened by inserting a new row in `ilc_constitutional_decision_log_v0.1.md` with
`status: open`. The CDL spec doc is also committed. This is a CDL mutation — pre-commit hook
requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=948`. Human GO token required
before execution.

### Phase 950 note — Two-commit CDL ratification (SENSITIVE)

Two commits required; only Commit 2 uses the CDL mutation env var.

- Commit 1: `ilc_core/node/node_startup_runtime.py` — update `H013_CHANGE_THRESHOLD = 0.15`.
  Add version comment. No CDL env var. Pre-commit hook must pass (no CDL log changes in this commit).
- Commit 2: CDL-082 spec OPEN → RATIFIED. CDL log row updated. `ILC_CDL_MUTATION_AUTHORIZED=1
  ILC_CDL_MUTATION_PHASE=950`. Pre-commit hook enforces no `ilc_core/` file changes in Commit 2.

Human GO token required before executing either commit.

### Phase 952 note — Closure gate (SENSITIVE)

Closure gate is a structural window boundary. It requires human confirmation of the closure
verdict. The gate test file (`tests/test_phase_0952_window_945_952_closure_gate.py`) must
assert all Phase 945–951 test counts, key version tokens, and CDL-082 ratified status.

---

## 8. Sensitivity Classification

### SENSITIVE phases

- **Phase 948** — CDL mutation: CDL-082 opened in constitutional decision log.
  Requires: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=948`.
  Requires: explicit human GO token.

- **Phase 950** — CDL mutation (Commit 2): CDL-082 ratified in constitutional decision log.
  Requires: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=950` for Commit 2 only.
  Commit 1 (runtime mutation) does NOT use the CDL env var.
  Requires: explicit human GO token before either commit.

- **Phase 952** — Closure gate: structural window boundary.
  Requires: explicit human GO token (closure verdict confirmation).

### NON-SENSITIVE phases

- **Phase 945** — Documentary only: sequence lock + capsule. No CDL mutation. No `ilc_core/` restriction applies (no CDL env var context).
- **Phase 946** — Runtime implementation: `ilc_core/` changes permitted in non-CDL commits.
- **Phase 947** — Test implementation: no CDL mutation, no runtime restriction.
- **Phase 949** — Prelock hardening: CDL-082 spec and evidence doc updates only — no CDL log mutation (status remains `open`).
- **Phase 951** — Documentary only: coherence report + capsule. No CDL mutation.

### Pre-commit hook block

The following phases require `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<N>`:
```
Phase 948:  ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=948
Phase 950 (Commit 2 only):  ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=950
```

---

## 9. Scope Notes for Fixed Phases

### Phase 945 — Window 945–952 Sequence Lock + Capsule v5.32

**NON-SENSITIVE.** No GO token required.

**Deliverables:**
- `docs/specs/ilc_phase_945_952_sequence_lock_v0.1.md` — window sequence lock
- `docs/specs/ilc_antigravity_context_capsule_v5.32.md` — supersedes v5.31
- `docs/phases/phase_0945_window_945_952_sequence_lock_capsule_walkthrough.md`

**Capsule v5.32 content requirements:**
1. Current frontier state: Phase 944 coherence report completed; windows 921–929, 930–938 (H-013), 939–944 all CLOSED.
2. CDL status table: CDL-081 RATIFIED (Phase 943).
3. H-013 status: CLOSED (Phase 938). 35 spectral beacon tests.
4. SIM-BEACON-01 finding: adversary_reduction ≈ 0.684 = `1 - 1/√T` — mathematical constant; sealed-sender (ADR-0034) is primary privacy mechanism.
5. SIM-REUSE-01 finding: `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` — gaming non-attractive by construction.
6. Forward obligations: H-012 settle(), CDL-082 threshold, H-CON-02, Werner φ-bound, H-011.
7. Phase numbering remediation: normal lane 945–989, skip 990–1099, resume 1100+.
8. Audit findings summary (window 945 is first window post-audit; record findings M1-M5 and H1-H2 as tracked items).

**Sequence lock content requirements:**
- Window identity: 945–952
- Phase table (identical to §7 above)
- Token: `window_945_952_sequence_lock_committed_phase_945`

**Commit subject:** `docs(capsule): capsule v5.32 + window 945-952 sequence lock`

### Phase 946 — H-012 settle() Runtime + Decimal Precision Fix

**NON-SENSITIVE.** No GO token required. `ilc_core/` changes permitted (no CDL env var).

**Deliverables:**
- `ilc_core/economics/epoch_attribution_settle_runtime.py` — NEW
- `ilc_core/types.py` — updated `EpochAttributionBatch.settle()` delegation
- `ilc_core/economics/passive_ecu_attribution_runtime.py` — M1 Decimal fix
- `docs/phases/phase_0946_h012_epoch_attribution_settle_runtime_walkthrough.md`

**Required runtime module content:**
```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_946.v0.1"
CDL_081_DEPENDENCY = "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"
CDL_HCON_02_DEPENDENCY = "h_con_02_cdl_required_before_ejected_stake_treasury_executes"
```

**`settle_attribution_batch` function spec:**
- Input: `batch: EpochAttributionBatch`, `stake_map: dict[str, dict[str, Decimal]]`
  (outer key: star_node_id; inner: member_agent_id → stake — see §4.3 above)
- For each event in `batch.events` (cast to `AttributionEvent`):
  - If `edge_type == EdgeType.REUSE`: payout = `REUSE_ATTRIBUTION_RATE` to `target_creator_id`
  - If `edge_type == EdgeType.CO_AUTHORSHIP` and stake_map[star_node_id] is non-empty:
    payout = proportional by member stakes (CDL-081 §4.2)
  - If `edge_type == EdgeType.CO_AUTHORSHIP` and stake_map[star_node_id] is empty:
    attribution suspended; emit `cdl_081_zero_member_commons_transition` token (§4.6)
  - If ejected stake path triggered (explicit ejection event): raise `NotImplementedError(CDL_HCON_02_DEPENDENCY)`
  - `visited_set` reset per event (no cross-event contamination)
  - Edge types other than REUSE and CO_AUTHORSHIP: silently ignored per CDL-081 §4.3
- All arithmetic in `Decimal`. No float.
- Returns `list[tuple[str, Decimal]]` — `(agent_id, ecu_amount)` pairs

**M1 Decimal fix spec (`passive_ecu_attribution_runtime.py`):**
The module has four float rate constants: `PASSIVE_ATTRIBUTION_RATE`, `GAMMA`, `DECAY_FLOOR`,
`ATTRIBUTION_CAP`. `Decimal * float` raises TypeError, so a single-constant conversion breaks
the module. All four constants must be converted together.
- `PASSIVE_ATTRIBUTION_RATE = 0.20` → `Decimal("0.20")`
- `GAMMA = 0.15` → `Decimal("0.15")`
- `DECAY_FLOOR = 0.05` → `Decimal("0.05")`
- `ATTRIBUTION_CAP = 0.15` → `Decimal("0.15")`
- `_validate_runtime_contract()`: update comparison to use Decimal arithmetic
- `quality_factor()` and `compute_passive_ecu()`: convert GAMMA to float at point of use
  (function signatures remain `float → float`; Decimal(str(val)) converts inputs internally)
- Callers of `compute_passive_ecu()` are unaffected (return type stays `float`)
- `import math` kept; `from decimal import Decimal` added

**Phantom edit guard:** After implementing, verify `types.py` settle() stub is actually
replaced (not left as a parallel dead branch). Run:
```
grep -n "CDL_HCON_01_DEPENDENCY" ilc_core/types.py
```
Must return zero hits. If any hits remain, the runtime delegation is incomplete.

**Commit subject:** `feat(h012): epoch attribution settle() runtime + Decimal precision fix (M1)`

### Phase 947 — H-012 Ratification Evidence Tests (30 tests)

**NON-SENSITIVE.** No GO token required.

**Deliverables:**
- `tests/test_phase_0947_h012_epoch_attribution_settle.py` — 30 tests
- `docs/phases/phase_0947_h012_ratification_evidence_walkthrough.md`

**Test structure:** Per §4.5 above. All 30 tests must pass `pytest tests/test_phase_0947_h012_epoch_attribution_settle.py -v`.

**Required test assertions (sample):**
- Test asserts `EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_946.v0.1"`
- Test asserts `CDL_081_DEPENDENCY` token present
- Test asserts REUSE batch produces `Decimal("0.20")` per event (exact Decimal, not float)
- Test asserts `isinstance(result_ecu, Decimal)` for all payouts (type guard)
- Test asserts ejected stake path raises `NotImplementedError` with `CDL_HCON_02_DEPENDENCY`
- Test asserts zero-member case returns no payouts and emits commons token
- Test asserts `CDL_HCON_01_DEPENDENCY` no longer appears in `ilc_core/types.py` (phantom edit guard)

**Commit subject:** `test(h012): 30-test ratification evidence for settle() runtime`

### Phase 948 — CDL-082 Opening (SENSITIVE)

**SENSITIVE.** Human GO token required before executing. CDL mutation.
Env var: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=948`

**Deliverables:**
- `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md` — NEW CDL spec
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL-082 row inserted (`status: open`)
- `docs/phases/phase_0948_cdl_082_h013_threshold_amendment_opening_walkthrough.md`

**CDL-082 spec required sections:**
1. Status: OPEN; Opened: Phase 948; Authority: CDL-079 (H-013 activation)
2. Problem Statement: spurious-emission regime at threshold=0.10; SIM-BEACON-01 evidence
3. Human-Gate Decisions: Q1 — Raise threshold from 0.10 to 0.15? (RESOLVED in this phase)
4. Decision record: `H013_CHANGE_THRESHOLD = 0.15` — SIM-BEACON-01 Phase 939 evidence
5. Out-of-scope: sigma parameter, adversary model revision, mainnet sigma change
6. Ratification gate (pre-ratification checklist — all items to be checked at Phase 950)
7. Token: `cdl_082_open_phase_948`

**CDL log insertion:** New row for CDL-082 with `status: open`, `opened_phase: 948`, `opened_date: 2026-04-28`.

**Commit subject:** `feat(cdl): open CDL-082 h013 emission threshold amendment (Phase 948)`

### Phase 949 — CDL-082 Prelock Hardening + Ratification Evidence Doc

**NON-SENSITIVE.** No GO token required. CDL-082 spec is updated but CDL log status remains
`open` (no CDL mutation triggering the hook).

**Deliverables:**
- `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md` — hardened (prelock additions)
- `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_ratification_evidence_949_v0.1.md` — NEW
- `docs/phases/phase_0949_cdl_082_prelock_hardening_walkthrough.md`

**Prelock hardening requirements:**
The prelock test in Phase 949's evidence doc must assert the CDL-082 spec at the Phase 948
opening commit ref has `status: open`. Pattern:
```python
# historical-hardening: read CDL-082 at its opening commit
opening_commit = "$(git log --oneline | grep 'CDL-082' | head -1 | cut -d' ' -f1)"
# assert status == "open" in that commit's version of the spec
```
(Exact implementation per existing prelock pattern in CDL-079/080/081 evidence docs.)

**Evidence doc required content:**
- Cite SIM-BEACON-01 simulation parameters and result tokens
- Assert: `H013_CHANGE_THRESHOLD = 0.1` in node_startup_runtime.py at this point (pre-mutation)
- Assert: CDL-082 status is `open` at Phase 948 commit
- Record: all 30 H-012 tests pass (imported from Phase 947 results)
- Pre-ratification checklist: `[x]` all items from CDL-082 §6

**Commit subject:** `docs(cdl): cdl-082 prelock hardening + ratification evidence (Phase 949)`

### Phase 950 — CDL-082 Ratification (SENSITIVE — Two Commits)

**SENSITIVE.** Human GO token required before executing either commit.

**Commit 1 (runtime mutation — NON-SENSITIVE commit):**
- `ilc_core/node/node_startup_runtime.py`:
  - Change `H013_CHANGE_THRESHOLD: float = 0.1` → `H013_CHANGE_THRESHOLD: float = 0.15`
  - Update inline docstring at line ~391: `(0.1, provisional)` → `(0.15, CDL-082 ratified Phase 950)`
  - Add header comment: `# CDL-082 ratified Phase 950; SIM-BEACON-01 evidence Phase 939`
- No CDL env var. Pre-commit hook must pass.
- Commit subject: `feat(h013): raise change_threshold 0.10→0.15 (CDL-082 Phase 950)`

**Commit 2 (CDL mutation — SENSITIVE commit):**
- `docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md`: Status OPEN → RATIFIED; add ratification fields
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`: CDL-082 row updated (`status: ratified`, `ratified_phase: 950`)
- Env var: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=950`
- Pre-commit hook: NO `ilc_core/` files in this commit (hook blocks if any present).
- Commit subject: `feat(cdl): ratify CDL-082 h013 emission threshold amendment (Phase 950)`

**Additional deliverable:**
- `docs/phases/phase_0950_cdl_082_ratification_walkthrough.md`

### Phase 951 — Coherence Report + Capsule v5.33

**NON-SENSITIVE.** No GO token required.

**Deliverables:**
- `docs/specs/ilc_integration_coherence_report_951_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.33.md` — supersedes v5.32
- `docs/phases/phase_0951_coherence_report_capsule_v5_33_walkthrough.md`

**Coherence report required content:**
1. Window 945–952 summary (tracks: H-012, CDL-082, capsule)
2. H-012 CDL-081 implementation chain: §§4.1–4.6 coverage table, H-CON-02 stub forward obligation
3. CDL-082 constitutional chain: SIM-BEACON-01 → CDL-082 open → prelock → ratification
4. Precision fix record: M1 Decimal fix in `passive_ecu_attribution_runtime.py`
5. Audit findings disposition: H1/H2 tracked, M1 resolved, M2–M5 tracked for future windows
6. Forward obligations table (H-CON-02, Werner φ-bound, SIM-BEACON-01 adversary revision, H-011)
7. Test count: 30 (H-012) + {prior count} (regression) — all pass
8. Coherence verdict token

**Commit subject:** `docs(coherence): phase 951 coherence report + capsule v5.33`

### Phase 952 — Window 945–952 Closure Gate

**SENSITIVE.** Human GO token (closure verdict confirmation) required.

**Deliverables:**
- `tests/test_phase_0952_window_945_952_closure_gate.py` — gate test
- `docs/specs/ilc_window_945_952_closure_gate_952_v0.1.md` — closure verdict doc
- `docs/specs/ilc_window_945_952_handoff_952_v0.1.md` — handoff doc (per closure handoff schema)
- `docs/phases/phase_0952_window_945_952_closure_gate_walkthrough.md`

**Gate test categories (per prior gate pattern):**
1. Category 1 — Phase 945 artifacts: sequence lock token, capsule v5.32 token
2. Category 2 — Phase 946–947 H-012 runtime: version token, CDL_081_DEPENDENCY, CDL_HCON_01_DEPENDENCY absent from types.py, 30 tests pass
3. Category 3 — Phase 948–950 CDL-082: spec open at Phase 948 commit, ratified at Phase 950 commit, runtime mutation present (`H013_CHANGE_THRESHOLD == 0.15`), CDL log row correct
4. Category 4 — Phase 951 coherence: coherence verdict token, capsule v5.33 exists
5. Category 5 — Selftest guard: `ILC_PHASE_952_GATE_SELFTEST=1` required in category 3 to prevent recursion

**Handoff doc required content (per closure handoff schema):**
1. Window identity and closure basis
2. Inputs and closure inheritance (CDL-081 ratification, SIM-BEACON-01 results)
3. Closure verdict summary (H-012 partial settle(), CDL-082 ratified, capsule current)
4. Carry-forward items: H-CON-02, Werner φ-bound, SIM-BEACON-01 adversary revision, H-011, M2–M5 audit findings
5. Next-window entry criteria: CDL-083 available; H-CON-02 may open; Werner φ-bound needs SIM first
6. MemPalace refresh disposition: Disposition required (CDL-082 and H-012 add to retrieval surface)

**Commit subject:** `docs(g8): phase 952 window 945-952 closure gate`

---

## 10. Key Dependencies and Open Questions

### Must-resolve at window entry (Phase 945)

- None. All dependencies are confirmed met (CDL-081 ratified, SIM-BEACON-01 complete, capsule
  forward obligation recorded).

### Sequencing constraints

1. Phase 945 (seq lock) must precede all other phases — locks the sequence.
2. Phase 946 (runtime) must precede Phase 947 (tests) — tests import the runtime.
3. Phase 948 (CDL-082 open) must precede Phase 949 (prelock hardening).
4. Phase 949 (prelock + evidence) must precede Phase 950 (ratification).
5. Phase 950 Commit 1 (runtime) must precede Phase 950 Commit 2 (CDL mutation).
6. Phases 945–950 must precede Phase 951 (coherence report cites all window work).
7. Phase 951 must precede Phase 952 (closure gate verifies coherence report).

### Open questions

None blocking at window entry. The following are tracked but deferred:

- **H-CON-02 scoping:** Panel hyperedge quorum rules depend on CDL-081 §4.5 (ejected stake
  treasury). The scope is known but substantial — own window. No decision needed this window.
- **Werner φ-bound value:** `EDGE_MINT_PHI_BOUND = None` remains unset. A SIM is needed before
  a CDL value can be locked. Not this window.
- **Audit H1/H2:** SSL posture tokens and bootstrap exception handling — mainnet concerns, not
  testnet blockers. Tracked in coherence report, not addressed this window.

### Permanently deferred items (not this window, not next window)

- Retrospective walkthrough docs for Phases 849–943: on-demand only per Phase 944 §5.3.
- `SIM-MULTI-HOP-01` and `SIM-SIM-PASSIVE-ECU-01` follow-on work: not scheduled.

---

## 11. Known Patterns and Technical Constraints

### Novel patterns this window

1. **First H-series CDL-081 implementation** — H-012 settle() is the first runtime to implement
   the CDL-081 attribution formulas. The partial implementation pattern (stub H-CON-02 sub-path)
   is established here. Future H-CON-02 implementation must remove the `CDL_HCON_02_DEPENDENCY`
   stub and implement the treasury path.

2. **Decimal audit fix inline with feature implementation** — M1 float→Decimal fix is bundled
   into Phase 946 rather than a standalone phase. The rationale: passive_ecu_attribution_runtime.py
   is already touched in Phase 946 (economics module context). This pattern is acceptable when the
   audit fix is low-risk and same-module as the feature work.

### Historical prelock hardening

Each ratification phase (Phase 950) must harden the corresponding prelock test to assert that
the CDL-082 spec had `status: open` at the Phase 948 opening commit ref. Pattern established in
CDL-079/080/081. Read the actual commit ref from `git log --oneline` — do not reason by analogy.

### Phantom edit guard

**Target file:** `ilc_core/types.py` — `EpochAttributionBatch.settle()`.

After Phase 946, the stub must be fully replaced. Detection:
```bash
grep -n "CDL_HCON_01_DEPENDENCY" ilc_core/types.py
```
Must return empty. If non-empty: the old NotImplementedError guard was not removed. Fix before
running Phase 947 tests — they include an assertion for this.

**Target file:** `ilc_core/node/node_startup_runtime.py` — `H013_CHANGE_THRESHOLD`.

After Phase 950 Commit 1, verify:
```bash
grep "H013_CHANGE_THRESHOLD" ilc_core/node/node_startup_runtime.py
```
Must show `0.15`, not `0.1`.

### Pre-commit hook ilc_core/ clean-state guard

Phase 950 Commit 2 (CDL mutation) must NOT touch any `ilc_core/` file. The pre-commit hook
will reject the commit if any staged `ilc_core/` file is present. Stage only CDL spec and CDL
log files for Commit 2.

### Closure gate selftest guard chain

Phase 952 gate test (Category 3) must include:
```python
if os.environ.get("ILC_PHASE_952_GATE_SELFTEST") == "1":
    # only run internal selftest probes; skip full gate execution
```
The selftest guard prevents infinite recursion if prior gate tests are also re-run by Phase 952.
Read each prior gate test file directly (`test_phase_0947_h012_epoch_attribution_settle.py`,
etc.) before writing the Phase 952 gate — do not reconstruct from memory.

---

## 12. Non-Goals and Explicitly Deferred Items

- **H-CON-02** — panel hyperedge quorum rules CDL. Not this window.
- **Werner φ-bound CDL** — `EDGE_MINT_PHI_BOUND = None` will remain None after this window.
- **SIM-BEACON-01 adversary model revision** — revised SIM with sealed-sender constraints. Future SIM window.
- **H-011 patent assessment** — ongoing, no action this window.
- **Audit M2–M5** — requester_id fix, EndorsementCache thread safety, PeerFingerprintCache validation, star_map private field — tracked, not addressed this window.
- **Audit H1/H2** — SSL posture tokens, bootstrap exception handling — tracked, mainnet concerns.
- **Mainnet sigma parameter change** — CDL-082 explicitly does NOT change `H013_TESTNET_EMISSION_SIGMA`. That requires the adversary model revision SIM.
- **Closing window 939–944 handoff doc** — window 939–944 did not produce a handoff doc (pre-CLAUDE.md workflow gap). Retrospective handoff is optional; the Phase 944 coherence report is authoritative. Not produced this window.

---

## 13. Key Canonical Anchors for Prompt Drafting

- **PRIMARY:** `docs/specs/ilc_antigravity_context_capsule_v5.31.md` (superseded by v5.32 after Phase 945)
- `docs/specs/ilc_integration_coherence_report_944_v0.1.md` — forward obligations and current frontier
- `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md` — CDL-081 §§4.1–4.6 (H-012 spec source)
- `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md` — CDL-082 evidence source
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL register (CDL-082 insertion target)
- `ilc_core/types.py` — `EpochAttributionBatch`, `REUSE_ATTRIBUTION_RATE`, `EdgeType` (H-012 implementation context)
- `ilc_core/economics/passive_ecu_attribution_runtime.py` — M1 fix target
- `ilc_core/node/node_startup_runtime.py` — CDL-082 runtime mutation target
- `ilc_core/economics/` — directory for new `epoch_attribution_settle_runtime.py`
- `docs/phases/phase_0847_window_844_847_closure_gate_walkthrough.md` — walkthrough format reference
- For closure gate (Phase 952): all Phase 945–951 test files and walkthrough artifacts.

---

`window_945_952_guidance_doc_v0.1`
`cdl_082_pre_authorized_sim_beacon_01_evidence`
`h012_settle_partial_hcon02_stub`
`normal_lane_phases_945_952_confirmed`
