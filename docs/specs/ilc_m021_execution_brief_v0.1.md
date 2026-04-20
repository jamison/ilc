# ILC M-021 Execution Brief

**Phase:** M-021
**Date:** 2026-04-20
**For:** Gemini
**Prerequisite:** M-020 approved (`run_m020_audit_prep_verdict=pass`, commit `4e789c19`)
**Claude audit:** Required before operator approval

---

## What M-021 is

M-021 has two parallel obligations. Both must be complete for the phase to pass.

**Obligation 1 (primary): SIM-LEAKAGE-01 execution**

Run the dedicated contributor-linkage leakage measurement against the
M-009 testbed. The governing contract is
`docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md` — read it in
full before beginning. Everything in that spec applies. This brief adds
context and tightens the output gate; it does not relax anything in the spec.

**Obligation 2 (secondary): Security fix verification + audit brief update**

Three security fixes were applied to the Rust codebase by Claude in commit
`16147c2b` (2026-04-20) after an adversarial audit of M-019/M-020 work.
Verify that each fix is correctly implemented. Then add one explicit
documentation note to the existing audit brief.

---

## Obligation 1: SIM-LEAKAGE-01

### What to run

The M-009 four-validator testbed (`config/mysticeti_testnet_M009/`). Build
with `--features testnet_fault_sim` as before — CRIT-001 (see Obligation 2)
does not change the measurement surface since the testbed already requires
that feature flag.

Run repeated scripted contributors across multiple epochs. Capture:
- validator-host timing and message-size-bucket data
- query-trace data for any hosted-query surface, or an explicit
  surface-absence record if the testbed exposes no hosted-query surface
- public receipts and lineage traces for the same workload window
- a manifest tying all captures to the same run

### Three attacker variants — all required

**Variant A — operator-path attacker**
Vantage: validator-host timing and message-size buckets.
Produce: measured same-contributor linkage recall estimate.
Pass band: ≤ 0.60.

**Variant B — hosted-query attacker**
Vantage: query timing traces and aggregation view across epochs.
If no hosted-query surface exists on the testbed, produce an explicit
surface-absence record with a brief surface audit confirming why. Do not
skip this variant — a surface-absence record is a valid result.
Pass band: ≤ 0.45 (or surface-absence record accepted in place).

**Variant C — repeated-contributor attacker**
Vantage: public receipt and lineage corpus.
Produce: measured same-contributor linkage recall estimate from the
ordinary public legitimacy surface.
Pass band: ≤ 0.45.

### What the results artifact must contain

`docs/research/ilc_sim_leakage_01_results_M021_v0.1.md` must include:

1. **Methodology section** — how linkage recall was computed. What data was
   captured, what algorithm was used to estimate same-contributor linkage,
   what the unit of measurement is. This section must be substantive enough
   that a reviewer can judge whether the methodology is sound. A one-sentence
   "we measured linkage" is not sufficient.

2. **Raw numbers for each variant** — the actual computed linkage recall
   figures, not just "within band" or "pass." State the numbers. If a variant
   produces a range (e.g., due to script parameterization), state the range
   and the worst-case figure used for the verdict.

3. **Observability-floor check** — four explicit statements, each confirmed
   true or false:
   - receipts remained discoverable
   - lineage remained legible
   - challengeability was preserved
   - bounded human auditability was preserved
   If any statement is false, the verdict is fail regardless of linkage numbers.

4. **Capture manifest** — list of artifacts produced (traffic captures, query
   traces, receipt files) with the run they correspond to. The manifest does
   not need to include the raw binary captures in the results doc, but must
   name them and confirm they exist.

5. **Explicit verdict** — one of `sim_leakage_01_verdict=pass`,
   `sim_leakage_01_verdict=fail`, or `sim_leakage_01_verdict=incomplete`.
   State which band each variant hit or missed. Do not conflate the M-019
   pass verdict with this verdict — they are separate.

### Hard pass criteria (from commissioning spec §5)

All of the following must be true for `sim_leakage_01_verdict=pass`:
- All three attacker variants exercised
- Ordinary-observer / repeated-contributor linkage recall ≤ 0.45
- Hosted-query linkage recall ≤ 0.45, OR explicit surface-absence record
- Operator-path linkage recall ≤ 0.60
- No observability-floor violation
- Raw numbers and methodology present (not just assertion)

A missing methodology section or missing raw numbers makes the artifact
`sim_leakage_01_verdict=incomplete` regardless of the stated verdict.
Claude will not approve an incomplete artifact.

### What Claude will audit

Claude will verify:
- methodology is substantive (not assertion)
- raw numbers are present and are plausible against the gossip graph structure
- all three variants are present
- observability-floor check is explicit
- verdict is consistent with the numbers stated
- the M-019 pass verdict is not being cited as a substitute

---

## Obligation 2: Security fix verification + audit brief update

### Background

After M-020, Claude performed an independent adversarial audit of the Rust
codebase. Four findings were identified. Three were fixed immediately by Claude
in commit `16147c2b` (2026-04-20). One (HIGH-001) was confirmed safe but needs
explicit documentation.

Your job in this obligation is to:
1. Read commit `16147c2b` and verify each fix is correctly applied
2. Add one documentation note to the existing audit brief

Do not re-implement these fixes. Do not propose alternative implementations
unless you find a correctness problem with what was committed. The fixes are
already in the repo — this is a verification pass.

### Fix 1: CRIT-001 — EpochSettlementTx gated to testnet_fault_sim

**What was fixed:** `handle_epoch_settlement_tx()` and its dispatch branch in
`node.rs` are now `#[cfg(feature = "testnet_fault_sim")]` gated. Production
builds reject `EpochSettlementTx` with `InvalidSignature`. Added as SEC-010
in the audit brief.

**Verify:**
- The dispatch branch in `node.rs` for `GossipMessage::EpochSettlementTx`
  returns `Err(ILCConsensusError::InvalidSignature)` in non-testnet_fault_sim
  builds
- `handle_epoch_settlement_tx()` is annotated `#[cfg(feature = "testnet_fault_sim")]`
- `cargo build` (no features) succeeds with no errors
- `cargo build --features testnet_fault_sim` succeeds with no errors
- The `commit_epoch_record()` doc comment in `epoch_settlement.rs` notes its
  testnet-only scope

**Report:** Confirmed correct / found issue (describe).

### Fix 2: HIGH-002 — All-N quorum requirement documented

**What was fixed:** A comment was added to `process_epoch_checkpoint()` in
`epoch_settlement.rs` documenting that `fast_aggregate_verify` requires all N
validator keys (not 2F+1), making a single offline honest validator block epoch
finalization. The comment notes this as a known testnet liveness limitation that
does not affect safety.

**Verify:**
- The comment is present at the `fast_aggregate_verify` call site in
  `process_epoch_checkpoint()`
- The comment correctly describes the limitation (all-N vs 2F+1, liveness
  impact, safety unaffected)
- No code change was made — this is documentation only

**Report:** Confirmed correct / found issue (describe).

### Fix 3: TEST-002 — M-019 runner port correction

**What was fixed:** The equivocation, censoring, and silent/slow scenarios in
`tools/testbed/ilc_loopback_m019_runner.sh` were sending to ports 9001-9003.
Validators listen on 50151-50154 (configured via jq). All PORT calculations
corrected to `50150+vid` base. Equivocation `--peer-id` corrected from 5 to 1.

**Verify:**
- Equivocation scenario sends to `127.0.0.1:50151` (not 9001)
- Censoring scenario uses `PORT=$((50150 + vid))` (not `9000 + vid`)
- Silent/slow scenarios use `PORT=$((50150 + vid))` (not `9000 + vid`)
- `--peer-id` in the equivocation scenario is 1 (not 5)

**Report:** Confirmed correct / found issue (describe).

### HIGH-001: Add explicit note to audit brief §5

**Finding:** `in_flight` HashMap in `node.rs` tracks equivocation detections
in memory only. It is not persisted to LMDB. On validator restart, the
in-flight table is empty and a replayed equivocating transfer could pass the
in-flight check.

**Why this is safe (two-layer defence):** The durable barrier is
`balance_store.apply_transfer()` in `balance_store.rs`, which enforces LMDB
version locking. An object at version V cannot be transferred twice — the
second attempt fails at the LMDB write layer regardless of what the in-flight
table says. The in-flight table is an early-rejection optimization, not the
safety barrier. The safety barrier is LMDB-persistent.

**What to add:** Add a new item to §5 of
`docs/research/ilc_external_security_audit_brief_M020_v0.1.md`:

```
X. **HIGH-001 — In-memory equivocation detection (two-layer defence, no fix
   required).** The `in_flight` HashMap in `node.rs` is not persisted to LMDB
   and resets on restart. However, the durable safety barrier is
   `balance_store.apply_transfer()` in `balance_store.rs`, which enforces LMDB
   version locking: an object at version V cannot be transferred twice
   regardless of the in-flight table state. The in-flight table is an
   early-rejection optimization. The LMDB version lock is the real
   SafetyNoDualCert barrier and is restart-persistent. No fix required;
   documented here for auditor awareness.
```

Number it correctly in sequence after the existing items.

---

## Deliverables

| File | Status at M-021 close |
|---|---|
| `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md` | New — SIM-LEAKAGE-01 results with methodology, raw numbers, three variants, observability floor, explicit verdict |
| `docs/research/ilc_external_security_audit_brief_M020_v0.1.md` | Updated — HIGH-001 note added to §5 |
| `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` | Updated — M-021 audit checklist checked off, `run_m021_verdict=pass` recorded, Status: COMPLETE |
| `docs/phases/STATUS.md` | Updated — M-021 phase record added, Track B advanced to M-021 complete / M-022 next |

---

## What M-021 does NOT do

- Does not run M-022 (exitability drill) — that is a separate phase
- Does not open the convergence window — that requires M-022 approval
- Does not close row 5 — that happens in the convergence window using this
  artifact as input
- Does not fix or re-implement the three security fixes — verify only
- Does not re-run any M-019 workloads
- Does not touch `ilc_core/`, `ilc_consensus/` (except confirming the existing
  commits are correctly applied), or the CDL register

---

## Gate condition

M-021 is approved when:

1. `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md` exists with
   methodology, raw numbers, all three variants, observability-floor check,
   and an explicit `sim_leakage_01_verdict=pass` or `fail`
2. All three security fixes verified correct (or issues reported and resolved)
3. HIGH-001 note added to audit brief §5
4. Claude adversarial audit completed with no blocking findings
5. Operator approval

If `sim_leakage_01_verdict=fail`, M-021 still closes as complete — the honest
fail verdict is the deliverable. Row 5 remains `spec_closed_runtime_pending`
and the convergence window cannot close row 5. That is the correct outcome.
Do not adjust numbers to force a pass.
