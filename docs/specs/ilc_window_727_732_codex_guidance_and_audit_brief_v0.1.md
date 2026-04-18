# ILC Window 727-732: Codex Guidance Brief + Codebase Audit Report

**Prepared by:** Claude Code (2026-04-18)  
**For:** Codex (next window executor)  
**Status:** Pre-window guidance — Window 727-732 packet not yet created  
**Prerequisite reads:** capsule v4.9, closure gate 726, 701+ carry-forward program, M-series lane doc

---

## Part 1 — Audit Report: Known Issues and Pre-Window State

This section reports every substantive issue found in the current codebase
before Window 727-732 opens. Codex should read this before drafting the
sequence lock. Issues are categorized by severity and routing.

---

### A1 — STALE: PLANNING_INDEX.md Track B line

**Severity:** Administrative — correct before Phase 727 sequence lock  
**Location:** `docs/PLANNING_INDEX.md` line 4 and lines 29/44/57  
**Current text:**
```
authoritative Track B line in STATUS.md: M-015 complete, next planned phase M-016
```

**Correct state:** M-016 is now COMPLETE (commit `d5283dca`, 2026-04-18).
`docs/phases/STATUS.md` tail should read M-016 complete, next planned M-017.

**The closure gate 726 (line 43) also captured the stale Track B line** —
it recorded `M-015 complete; next planned phase M-016` because that was the
STATUS.md tail at 726 close. That is historically accurate. What is stale is
PLANNING_INDEX.md's forward-looking description, which has not yet been
updated to reflect M-016 completion.

**Action for Window 727-732 sequence lock author:** The sequence lock must
read and cite the STATUS.md tail at the time it is written. PLANNING_INDEX.md
should be patched to reflect the current Track B line in the same commit as
the sequence lock.

---

### A2 — STALE: M-series lane doc completion table

**Severity:** Administrative  
**Location:** `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
bottom of §6 (M-series completion status, line 1154)

**Current text (tail):**
```
- M-015 ✓ COMPLETE `7cfbe344` — Workload C: partition / heal / recovery loopback proof
- Next: M-016 (Workload D: replayability + state extraction); guidance pending publication
```

**Should be:**
```
- M-015 ✓ COMPLETE `d10bc470` — Workload C Tier 2: partition/heal/recovery with
  protocol-driven sync recovery confirmed
- M-016 ✓ COMPLETE `d5283dca` — Workload D: replayability + state extraction
  (state_extractor binary, READ_ONLY|NO_LOCK LMDB offline scan, JSON chain report,
  epochs 1-5 confirmed, chain_complete=true, sentinel_consistent=true,
  run_m016_workload_d_verdict=pass)
- Next: M-017 (Workload E: validator operability)
```

Note: M-015 final commit is `d10bc470` (Tier 2 fixes from this session), not
the earlier `7cfbe344`. Update both the commit hash and the description.

**Action:** Patch the completion table when drafting Window 727-732 sequence
lock, or as a standalone administrative commit.

---

### A3 — OPEN: `testnet_fault_sim` feature flag not defined in Cargo.toml

**Severity:** Pre-production concern — not a current blocker, but must be
resolved before M-019 (adversarial hardening) or any production build  
**Location:** `ilc_consensus/Cargo.toml` — no `[features]` table exists  
**References in code:** 5 occurrences of `TODO(pre-production): isolate under
#[cfg(feature = "testnet_fault_sim")]` in `ilc_consensus/src/node.rs`

**Specific locations (node.rs):**
1. `NodeRunner.partition_block_peers` field declaration (struct body)
2. `dispatch()` inbound drop block (~line 208)
3. `EpochSettlementTx` censor block in `dispatch()` (~line 235)
4. `broadcast_certificate()` partition filter (~line 525)
5. `send_to_peer()` partition filter (~line 555)

**Nature of the issue:** The fault-injection code (PARTITION_BLOCK_PEERS env
var, censor_validator) is compiled into production release builds. In
production, these are controlled by env vars that default to no-op (empty
string / None), so there is no runtime exposure. However, the code surface
exists unconditionally — an operator who sets PARTITION_BLOCK_PEERS on a
production validator would silently activate partition behavior.

**Resolution required before M-019:** A `[features]` table entry:
```toml
[features]
testnet_fault_sim = []
```
And all 5 blocks in node.rs gated with `#[cfg(feature = "testnet_fault_sim")]`.
The M-015/M-016 runners that use PARTITION_BLOCK_PEERS would need to build
with `cargo build --release --features testnet_fault_sim`. Runners that don't
use it build normally.

**For M-017:** This is NOT a blocker for M-017 (Workload E: validator
operability). M-017 is a measurement workload; it does not use fault injection.
Codex should log this as a pre-M-019 gate item, not a Window 727-732 blocker.

---

### A4 — OPEN: gRPC is a compile-time dependency but a runtime stub

**Severity:** Known architectural deferment — deferred to M-018  
**Location:** `ilc_consensus/src/main.rs` — gRPC server startup is skipped  
at runtime with log message `"gRPC start is a stub in M-010; skipping."`  
`ilc_consensus/Cargo.toml` — `tonic`, `prost`, `tonic-build` in deps/build-deps

**Assessment:** This is documented and intentional. M-018 (Workload F:
bounded public auditability + CLI) is the phase that activates gRPC. No
action needed from Codex in Window 727-732. **Do not attempt to activate
gRPC before M-018.**

---

### A5 — OPEN: No formal unit tests for `state_extractor` binary

**Severity:** Low — acceptable for testnet tooling phase  
**Location:** `ilc_consensus/src/state_extractor_main.rs`  
**Assessment:** The binary has no `#[cfg(test)]` block. Its correctness is
verified by:
1. The 12 Python tests in `tests/test_phase_M016_workload_d_results.py`
   (all 12 passing as of 2026-04-18)
2. The committed JSON run artifact
   `docs/research/ilc_m016_state_extraction_report.json`

This is acceptable for a testnet-phase binary. If the extractor is to be
productized, unit tests should be added before M-020 (security audit prep).
Not a current blocker.

---

### A6 — OPEN: SEC-007b (rand 0.8.6 Dependabot alert)

**Severity:** Low — documented in M-series lane doc §6.1  
**Assessment:** Not exploitable in ILC (no custom logger calling rand::rng()).
Blocked on tonic 0.11→0.13+ upgrade (tower dep chain). Designated clearance
path: tonic upgrade window (separate from current workload sequence).
**Not a Window 727-732 concern.** Do not bundle with M-017.

---

### A7 — OPEN: SEC-007a (protoc system dependency)

**Severity:** Low — documented in M-series lane doc §6  
**Assessment:** Two-phase resolution plan documented. Immediate fix
(protoc-bin-vendored) and long-term fix (protox after tonic 0.13+ upgrade)
are both scoped. **Not a Window 727-732 concern.**

---

### A8 — ASSESSMENT: TLA+ gap items

**Reference:** `docs/research/ilc_tla_plus_gap_analysis_v0.1.md`  
**Status of pre-RC items at M-016 close:**
- TLA-PRE-1 (MaxRound widening): TODO in gap analysis — not yet actioned
- TLA-PRE-2 (Spec C partition/heal): COMPLETE — 5,577 states, TLC PASS;
  integrated into M-015 gate script
- TLA-PRE-3 (Spec B refinement notes): noted in gap analysis

TLA-PRE-1 (MaxRound widening) is not yet actioned. This is a pre-RC item.
It does not block M-017 (measurement workload), but it should be completed
before M-019 (adversarial hardening). Codex should flag it in the
Window 727-732 carry-forward if the window does not include a TLA phase.

---

## Part 2 — Window 727-732 Guidance for Codex

### 2.1 What this window should accomplish

The Window 723-726 closure gate carries forward four prerequisites before any
financial-shard opening work can proceed in the main lane:

1. **Public launch must exist** before any financial-shard opening work
2. **At least one post-launch monitoring cycle must exist**
3. **A concrete demand signal must exist**
4. **Separate `B_hft` and L1/L2 firewall surfaces must be specified**

None of these prerequisites exist yet. **The financial-shard deferment posture
is therefore unchanged for Window 727-732.** No activation, no CDL ratification
targeting financial-shard infrastructure.

The window should focus on **adjacent foundational work** that can proceed
without the financial-shard prerequisites. Based on the 701+ carry-forward
program and current frontier state, appropriate candidates are:

---

### 2.2 Recommended phase grouping for Window 727-732

**Phase 727 — Sequence lock + administrative updates**

Mandatory first action:
- Read STATUS.md tail (Track B is now M-016 complete, next M-017)
- Update PLANNING_INDEX.md Track B line
- Update M-series lane doc completion table (see A2 above)
- Publish sequence lock with correct Track B citation
- Create Window 727-732 planning packet

Key tokens to include:
```
window_727_732_sequence_lock_active
run_m016_workload_d_verdict=pass  (carry-forward from M-016)
track_b_m016_complete_m017_next
```

**Phase 728 — 701+ program: identify the next open carry-forward item**

Read `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
in full to identify the highest-priority unresolved item that:
- Does not require financial-shard prerequisites
- Does not require Mysticeti convergence window completion
- Can be completed in a single 727-732 phase

The program lists items in `spec_or_contract_lock`, `doctrine_lock`, or
`constitutional_lock` completion modes. Prioritize `spec_or_contract_lock`
items that are blocking or adjacent to CDL-062 (sovereign substrate research
lane — the current open CDL).

**Phase 729-730 — Main lane constitutional/research work**

Candidate areas (confirm against 701+ program and capsule v4.9):
- CDL-017 constitutional text refinement (not ratification — ratification
  waits for M-022 convergence window, but the text can be drafted and reviewed)
- ADR-0022 / private-gated hardening review — if any scoped sub-item is
  actionable without financial-shard activation
- CDL-062 research lane: any bounded research question that can be completed
  within the window

**Phase 731 — Coherence report**

Standard format: window-level coherence report asserting boundary conditions.
Must confirm:
- no financial-shard activation,
- no CDL ratification (unless one is explicitly planned in the sequence lock),
- Track B advance to M-017 documented (M-016 complete),
- all A-series audit items from this guidance brief either addressed or
  explicitly carried forward with routing

**Phase 732 — Capsule update + closure gate**

- Capsule v5.0 (capsule v4.9 is current; v5.0 is the natural next increment)
- Closure gate 732 with explicit carry-forward to Window 733+

---

### 2.3 Track B status for Codex to cite

```
M-016 COMPLETE `d5283dca` (2026-04-18) — Workload D: Replayability and State Extraction
  state_extractor binary, READ_ONLY|NO_LOCK offline LMDB scan
  epochs 1-5 chain reconstructed without live validator
  run_m016_workload_d_verdict=pass
  row-7 replayability obligation satisfied for testnet scope

Next: M-017 — Workload E: Validator Operability
  Scope: commodity hardware measurement (≤8 core, ≤32 GB RAM, ≤1 TB SSD)
  Metric: new-validator sync time ≤24h at 10,000 epoch history
  Metric: storage growth ≤100 KB/epoch
  Owner: Gemini lane (Claude-audited before commit)
  Prerequisite: M-016 approved (satisfied)
```

Do NOT wait for M-017 completion before opening Window 727-732. The Gemini
M-series lane runs in parallel. Codex does not need to hold its phase clock
for M-017 execution.

---

### 2.4 CDL and constitutional posture for 727-732

| CDL | Status | Window 727-732 action |
|---|---|---|
| CDL-017 (validator governance) | OPEN | No ratification — Mysticeti convergence window only. Text review is permitted. |
| CDL-062 (sovereign substrate research) | OPEN | Research lane work permitted within scope. |
| CDL-066 (agent sender auth) | RATIFIED Phase 707 | No action needed. |
| CDL-067 | RATIFIED Phase 707 | No action needed. |
| Financial-shard CDLs | NOT OPEN | Blocked by 723-726 carry-forward prerequisites. |

---

### 2.5 What NOT to do in Window 727-732

1. **Do not activate any financial-shard CDL.** The four carry-forward
   prerequisites from Window 723-726 are not satisfied.

2. **Do not attempt CDL-017 ratification.** The Mysticeti convergence window
   (M-022 approval gate) has not been reached. CDL-017 ratification is reserved
   for that window.

3. **Do not mutate `ilc_core/` or `ilc_consensus/` in the Codex main lane.**
   Those files are owned by the Gemini M-series lane during active M-phases.
   The next main-lane code write authority opens at the Mysticeti convergence
   window.

4. **Do not attempt to activate gRPC in M-017.** gRPC is deferred to M-018.
   The M-017 runner should not touch the gRPC stub.

5. **Do not feature-gate `testnet_fault_sim` in this window** unless a
   dedicated phase is allocated for it. It is a pre-M-019 concern, not a
   Window 727-732 blocker.

---

### 2.6 M-017 guidance for Gemini (for Codex to relay or include in planning packet)

M-017 is Workload E: Validator Operability. Key points for Gemini:

- **Do NOT add any new code to the validator or consensus protocol.** This is
  a measurement phase only. The binary is `validator_harness` as built for M-016.

- **Measure on real hardware.** Document the actual test machine specs (cores,
  RAM, SSD size/type). Do not report estimated figures.

- **Sync time measurement:** Run a validator with an empty LMDB against a peer
  that has N epochs committed. Measure wall-clock time to reach epoch N.
  Target: ≤24h at 10,000 epochs. The testbed runs at 5 epochs, so extrapolate
  from measured storage and throughput figures — make the extrapolation method
  explicit, do not claim it as a measured result.

- **Storage growth:** Measure LMDB file size growth per epoch. The sentinel and
  each epoch record have a fixed byte footprint. Report per-epoch delta.
  Target: ≤100 KB/epoch.

- **Runner pattern:** Reuse the M-016 runner's retry-only-missing submission
  loop. Submit enough epochs (at least 20) to get stable per-epoch storage
  measurements. Do not use a fixed double-pass.

- **Do NOT activate PARTITION_BLOCK_PEERS or censor_validator.** This is a
  clean-run operability measurement, not a fault-injection test.

- **Verdict token:** `run_m017_workload_e_verdict=pass` or `=fail` with
  explicit pass/fail against all three Phase 690 criteria.

- **State extractor:** The offline state_extractor binary should be run once
  post-M-017 epochs to confirm LMDB health (optional but recommended as a
  sanity check, not a new pass criterion).

---

## Part 3 — Test Suite Health Summary (as of 2026-04-18)

**M-016 test suite:** 12/12 tests PASS  
`tests/test_phase_M016_workload_d_results.py`

**Rust unit tests:** 0 lib tests (all tests in network.rs require real TLS
infra; run with the integration test harness, not `cargo test --lib`).
The state_extractor binary has no unit tests (acceptable for testnet scope).

**Full Python test suite:** Verification in progress at guidance authoring time.
The M-016 tests above represent the current active test file.

---

## Part 4 — Carry-Forward Checklist for Window 727-732 Sequence Lock Author

Before the 727 sequence lock is published, confirm:

- [ ] STATUS.md tail read and cited (Track B: M-016 complete, M-017 next)
- [ ] PLANNING_INDEX.md Track B line patched
- [ ] M-series lane doc completion table patched (A2)
- [ ] `testnet_fault_sim` feature gate logged as pre-M-019 item in carry-forward
- [ ] TLA-PRE-1 (MaxRound widening) logged as pre-RC item in carry-forward
- [ ] Financial-shard deferment posture confirmed unchanged (four prerequisites unmet)
- [ ] CDL-017 ratification deferred to convergence window (not this window)
- [ ] Window 727-732 planning packet created

---

`window_727_732_guidance_brief_published`
`codex_pre_window_audit_complete_2026_04_18`
`track_b_m016_complete_m017_next_at_guidance_time`
