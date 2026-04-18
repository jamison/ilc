# M-017 Execution Guidance: Workload E — Validator Operability

**Date:** 2026-04-18  
**Prepared by:** Claude Code  
**For:** Gemini (M-series lane executor)  
**Prerequisite:** M-016 COMPLETE `d5283dca` — `run_m016_workload_d_verdict=pass`  
**Authority:** `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` §M-017

---

## 0. Tool Usage Rules — Read Before Touching Any Tool

**grep_search, search_files, semantic_search, and any other search tool WILL
time out on this repository. Do not call them. Ever. Not once.**

Use only direct file reads. Every file path you need is listed explicitly in
this document. If a path is not listed here, ask Claude rather than searching.

### Mandatory tool pattern

| Task | Correct tool | Wrong tool |
|---|---|---|
| Read a source file | `view_file <absolute-path>` | grep_search, search_files |
| Read a config file | `view_file <absolute-path>` | any search |
| Check a log | `run_command tail -50 /tmp/ilc_m017_v1.log` | grep_search |
| Find a token in a log | `run_command grep "epoch_record_committed" /tmp/ilc_m017_v1.log` | grep_search tool |
| Count commits | `run_command grep -c "epoch_record_committed" /tmp/ilc_m017_v1.log` | search tools |
| Build the binary | `run_command ~/.cargo/bin/cargo build --release ...` | anything else |
| Run the runner | `run_command bash tools/testbed/ilc_loopback_m017_runner.sh` | anything else |

`run_command` (bash execution) is safe. The search/grep *tools* are what freeze.
Using `grep` as a shell command inside `run_command` is fine.

### All file paths you need — pre-resolved, no searching required

```
# Binaries (build target)
ilc_consensus/target/release/validator_harness
ilc_consensus/target/release/testnet_client
ilc_consensus/target/release/state_extractor

# Config and genesis
config/mysticeti_testnet_M009/genesis.json
config/mysticeti_testnet_M009/validator_1_config.json
config/mysticeti_testnet_M009/validator_2_config.json
config/mysticeti_testnet_M009/validator_3_config.json
config/mysticeti_testnet_M009/validator_4_config.json
config/mysticeti_testnet_M009/certs/client_cert.pem
config/mysticeti_testnet_M009/certs/client_key.pem
config/mysticeti_testnet_M009/certs/validator_1_cert.der
config/mysticeti_testnet_M009/certs/validator_2_cert.der
config/mysticeti_testnet_M009/certs/validator_3_cert.der
config/mysticeti_testnet_M009/certs/validator_4_cert.der

# Source files (read these directly; do not search)
ilc_consensus/src/node.rs          — NodeRunner, dispatch, sync task
ilc_consensus/src/network.rs       — GossipMessage enum, receive(), 10MB cap
ilc_consensus/src/epoch_settlement.rs — EpochStore, get_epochs_after
ilc_consensus/src/main.rs          — validator_harness entry point
ilc_consensus/Cargo.toml           — dependencies, [[bin]] entries
ilc_consensus/src/config.rs        — NodeConfig fields

# Reference runners (read these to understand the pattern; copy what you need)
tools/testbed/ilc_loopback_m016_runner.sh   — most recent runner; copy structure
tools/testbed/ilc_loopback_m015_runner_tier2.sh — sync recovery pattern

# M-017 output files (you will create these)
tools/testbed/ilc_loopback_m017_runner.sh
docs/research/ilc_mysticeti_workload_e_results_M017_v0.1.md
docs/research/ilc_m017_operability_report.json
docs/phases/phase_M017_workload_e_walkthrough.md
tests/test_phase_M017_workload_e_results.py

# Runtime logs (created by runner)
/tmp/ilc_m017_v1.log
/tmp/ilc_m017_v2.log
/tmp/ilc_m017_v3.log
/tmp/ilc_m017_v4.log
/tmp/ilc_m017_v1_sync.log
/tmp/ilc_m017_state_report.json
/tmp/ilc_m017_operability_report.json
```

### If you feel the urge to search — stop and do this instead

1. The information you need is in this document or in one of the files listed above.
2. Read that file directly with `view_file`.
3. If you genuinely cannot find it by reading, send a message to Claude asking
   for the specific path. Claude will answer. Do not search.

---

## 0. Critical Operating Rules — Read First

1. **No new code to the consensus protocol.** M-017 is a measurement phase.
   The binary is `validator_harness` as built from the current source. You
   measure what the existing system does; you do not add features.

2. **Build the existing binary before running.** The source changed since
   M-016 (SEC-008 cursor protocol). Rebuild release before running any
   measurement.

3. **Do not use PARTITION_BLOCK_PEERS or CENSOR_VALIDATOR.** This is a
   clean-run measurement. No fault injection.

4. **Do not activate gRPC.** The stub is intentionally skipped. Do not
   touch it. gRPC activation is M-018 scope.

5. **Document real machine specs.** Capture actual hardware. Do not
   estimate, guess, or omit the hardware section.

6. **Be honest about extrapolation.** You cannot run 10,000 epochs on this
   testbed. You must extrapolate sync time from a measured proxy. State the
   methodology explicitly. Do not present an extrapolated figure as a
   measured result.

7. **Carry forward M-016 runner patterns.** Use `set -euo pipefail`,
   `trap cleanup EXIT INT TERM`, `VALIDATOR_PIDS`, `export REPO_ROOT`,
   and the retry-only-missing submission loop. Do not regress these.

---

## 1. Scope and Pass Criteria

Phase 690 Workload E requires measuring the operational burden of running a
validator node. Three pass criteria from the benchmark spec:

| Criterion | Target | How to measure |
|---|---|---|
| 1. Commodity hardware | ≤8 cores, ≤32 GB RAM, ≤1 TB SSD | Capture sysctl/proc output; document test machine |
| 2. New node sync time | ≤24h at 10,000 epoch history | Measure recovery of a fresh-LMDB validator; extrapolate |
| 3. Storage growth | ≤100 KB/epoch on-chain state | Measure LMDB directory bytes before/after; divide by epoch count |

---

## 2. Deliverables

All five deliverables are required. Claude will audit each before commit.

| # | File | Description |
|---|---|---|
| 1 | `tools/testbed/ilc_loopback_m017_runner.sh` | Runner script |
| 2 | `docs/research/ilc_mysticeti_workload_e_results_M017_v0.1.md` | Results doc with evidence |
| 3 | `docs/research/ilc_m017_operability_report.json` | Machine-readable report |
| 4 | `docs/phases/phase_M017_workload_e_walkthrough.md` | Design decisions and methodology |
| 5 | `tests/test_phase_M017_workload_e_results.py` | 12+ Python tests anchored to artifacts |

---

## 3. Runner Specification

### 3.1 Phase sequence

```
Phase 0: Build release binary (cargo build --release)
Phase 1: Capture hardware snapshot
Phase 2: Start 4 validators with fresh temp LMDBs
Phase 3: Submit 20 epochs to all validators (retry-only-missing loop, 4 passes)
Phase 4: Confirm all 80 commits (20 epochs × 4 validators)
Phase 5: Measure storage (LMDB size after 20 epochs)
Phase 6: Stop V3 and V4. Keep V1 and V2 running.
Phase 7: Wipe V1's LMDB and restart V1 fresh (sync proxy measurement start)
Phase 8: Time how long until V1 has recovered all 20 epochs via sync protocol
Phase 9: Stop all validators
Phase 10: Run state_extractor against V1's LMDB (sanity check: chain complete)
Phase 11: Emit JSON report and verdict token
```

### 3.2 Hardware capture

At the start of the runner, before any validators are launched, capture the
test machine specs. On macOS:

```bash
NCPU=$(sysctl -n hw.logicalcpu)
MEM_BYTES=$(sysctl -n hw.memsize)
MEM_GB=$(python3 -c "print(round($MEM_BYTES / 1073741824, 1))")
OS_VERSION=$(sw_vers -productVersion 2>/dev/null || uname -r)
ARCH=$(uname -m)
```

Emit to stderr and include in the JSON report as `hardware` object:
```json
{
  "logical_cpu_count": <int>,
  "ram_gb": <float>,
  "arch": "<str>",
  "os": "<str>",
  "disk_type": "ssd|unknown"
}
```

Disk type: attempt `diskutil info /` on macOS; grep for "Solid State" in
output. If unavailable, emit `"unknown"` — do not fabricate.

### 3.3 Storage measurement

After Phase 4 (all 20 epochs committed on all validators), measure each
validator's LMDB directory:

```bash
V1_LMDB_BYTES=$(du -sk "$V1_LMDB" | awk '{print $1}')  # kilobytes
V1_LMDB_BYTES=$((V1_LMDB_BYTES * 1024))                # convert to bytes
BYTES_PER_EPOCH=$((V1_LMDB_BYTES / 20))
```

Capture all four validators' LMDB sizes. Report all four; compute average.

**Expected result:** LMDB allocates in pages (minimum 4 KB). With ~50 bytes
per epoch record, 20 epochs ≈ 1 KB of actual data in a much larger allocated
file. The measured `bytes_per_epoch` will be dominated by LMDB page overhead
at low epoch counts. Report the raw measurement honestly. The target of ≤100
KB/epoch will be satisfied by orders of magnitude on actual record data; the
page-overhead report is also correct to include as the true operational cost.

### 3.4 Sync time proxy measurement

This is the most important measurement for the 24h target.

**Setup:** After Phase 4, keep V2-V4 running (with their full epoch 1-20
LMDBs). V3 and V4 are stopped in Phase 6 — **restart only V2 and V4** in
Phase 7. (V3 can stay stopped; we need at least one peer to serve sync
responses.)

Actually: Stop V3 and V4, but restart V4 immediately so V1 has two peers
(V2 and V4) to sync from. Then:

1. Record timestamp T0.
2. Delete V1's LMDB directory (`rm -rf "$V1_LMDB" && mkdir -p "$V1_LMDB"`).
3. Restart V1 with fresh empty LMDB (`validator_harness --config ...`).
4. Poll V1's log every 2 seconds: `grep -c "epoch_record_committed" /tmp/ilc_m017_v1_sync.log`
5. When V1's committed count reaches 20, record timestamp T1.
6. Sync time = T1 - T0 seconds.

**Extrapolation to 10,000 epochs:**

The sync protocol sends records in batches of 64 per sync interval
(EPOCH_SYNC_INTERVAL_SECS, default 5s). With 2 responding peers, V1
may receive 64 records per interval (duplicates from the second peer
are silently dropped). Measured sync time for 20 epochs will be:
- If ≤20 epochs fit in one batch: approximately 1 sync interval (5s)
- Report actual measured time

Extrapolation formula (include this exact text in the results doc):
```
extrapolated_10k_sync_seconds = (10000 / min(epochs_per_interval, 20)) × measured_interval_seconds
extrapolated_10k_sync_hours = extrapolated_10k_sync_seconds / 3600
```

Where `epochs_per_interval` = 20 / (measured_sync_seconds / 5). Report
all intermediate values. Note explicitly that the extrapolation assumes
constant throughput and does not account for network latency at multi-machine
scale — real multi-machine sync may be slower.

### 3.5 Emit verdict token

The runner must emit one of:
```
run_m017_workload_e_verdict=pass
run_m017_workload_e_verdict=fail
```

Pass conditions (all three must hold):
1. Commodity hardware criterion: test machine is ≤8 cores OR the machine
   exceeds spec and the measured resource usage is well within commodity
   limits (document the distinction honestly)
2. Extrapolated sync time ≤ 24h at 10,000 epochs
3. State extractor reports `chain_complete=true` after sync (V1 recovered
   correctly)

Storage criterion: always measure and report, but do NOT fail on storage
unless measured bytes_per_epoch > 102,400 (100 KB). At testnet epoch sizes
this will not trigger.

### 3.6 Config and runner patterns (mandatory)

- Use tempfile LMDB dirs (same pattern as M-016 runner)
- Write LMDB paths to sidecar `.txt` files (same as M-016)
- `export REPO_ROOT` after setting it (SEC-008 audit fix — do not regress)
- Retry-only-missing submission loop (4 passes max, same as M-016)
- VALIDATOR_PIDS array + cleanup trap (same as M-016)
- Log prefix: `[m017]` throughout
- Log files: `/tmp/ilc_m017_v{1..4}.log`, `/tmp/ilc_m017_v1_sync.log`

---

## 4. JSON Report Schema

`docs/research/ilc_m017_operability_report.json` must have this structure:

```json
{
  "phase": "M-017",
  "workload": "Workload E: Validator Operability",
  "date": "<ISO-8601>",
  "hardware": {
    "logical_cpu_count": <int>,
    "ram_gb": <float>,
    "arch": "<str>",
    "os": "<str>",
    "disk_type": "ssd|unknown"
  },
  "storage": {
    "epochs_committed": 20,
    "validator_lmdb_bytes": {
      "v1": <int>, "v2": <int>, "v3": <int>, "v4": <int>
    },
    "average_bytes_per_epoch": <float>,
    "target_bytes_per_epoch": 102400,
    "storage_criterion_pass": true
  },
  "sync": {
    "epochs_to_recover": 20,
    "measured_sync_seconds": <float>,
    "extrapolated_10k_sync_seconds": <float>,
    "extrapolated_10k_sync_hours": <float>,
    "target_sync_hours": 24,
    "sync_criterion_pass": true,
    "extrapolation_method": "linear from measured batch throughput"
  },
  "chain_sanity": {
    "chain_complete": true,
    "sentinel_current_epoch": 20,
    "verdict": "workload_d_replayability_pass"
  },
  "commodity_hardware_criterion_pass": true,
  "overall_verdict": "workload_e_operability_pass"
}
```

`overall_verdict` is `"workload_e_operability_pass"` or
`"workload_e_operability_fail"`. The Python tests will anchor to this field.

---

## 5. Results Doc Structure

`docs/research/ilc_mysticeti_workload_e_results_M017_v0.1.md` must contain:

```
# ILC M-017 Workload E: Validator Operability — Results

## 1. Scope
## 2. Test machine hardware
## 3. Run evidence
   ### 3.1 Storage measurement
   ### 3.2 Sync time measurement and extrapolation
   ### 3.3 State extractor sanity check
## 4. Pass criteria evaluation
   ### 4.1 Commodity hardware
   ### 4.2 New node sync time (≤24h at 10,000 epochs)
   ### 4.3 Storage growth (≤100 KB/epoch)
## 5. Known limitations (testnet scope)
## 6. Overall verdict
```

The verdict token `run_m017_workload_e_verdict=pass` must appear in §6.

---

## 6. Python Test File Specification

`tests/test_phase_M017_workload_e_results.py` — minimum 12 tests.

| # | Test name | What it checks |
|---|---|---|
| 1 | `test_results_doc_exists` | Results doc file present |
| 2 | `test_results_doc_verdict_pass` | `run_m017_workload_e_verdict=pass` in doc |
| 3 | `test_operability_report_exists_and_parseable` | JSON report present and valid JSON |
| 4 | `test_report_has_required_fields` | All top-level keys present in JSON |
| 5 | `test_hardware_section_present` | `hardware` object with all 5 fields |
| 6 | `test_storage_criterion_pass` | `storage.storage_criterion_pass == true` |
| 7 | `test_storage_bytes_per_epoch_under_target` | `average_bytes_per_epoch <= 102400` |
| 8 | `test_sync_criterion_pass` | `sync.sync_criterion_pass == true` |
| 9 | `test_sync_extrapolated_under_24h` | `sync.extrapolated_10k_sync_hours <= 24` |
| 10 | `test_chain_sanity_complete` | `chain_sanity.chain_complete == true` |
| 11 | `test_runner_emits_verdict_token` | `run_m017_workload_e_verdict=pass` in runner |
| 12 | `test_runner_uses_retry_only_missing_pattern` | runner contains `retry-only-missing` or `ensure_all_committed` |
| 13 | `test_overall_verdict_field` | `overall_verdict == "workload_e_operability_pass"` |
| 14 | `test_commodity_hardware_criterion_pass` | `commodity_hardware_criterion_pass == true` |

Tests 1-14 anchor to the literal artifact content. Add 1-2 more if there are
additional structural details worth locking in.

---

## 7. Walkthrough Specification

`docs/phases/phase_M017_workload_e_walkthrough.md` must cover:

- What this phase proved (operability at testnet scale; extrapolated to production)
- Hardware documented
- Storage measurement methodology and why LMDB page alignment affects readings
- Sync proxy design and the extrapolation formula used
- Why the extrapolation is honest (constant throughput assumption, loopback caveat)
- Deferred items (real multi-machine sync measurement, gRPC state export, crash recovery drill)
- What comes next: M-018 (Workload F: bounded public auditability + gRPC + row-7 accessibility closure)

---

## 8. Verdict Conditions

| Condition | Required for pass |
|---|---|
| `run_m017_workload_e_verdict=pass` emitted by runner | Yes |
| `overall_verdict: "workload_e_operability_pass"` in JSON | Yes |
| All 14+ Python tests pass | Yes |
| Hardware section populated with real values | Yes |
| Extrapolation method explicitly stated in results doc | Yes |
| `run_m016_workload_d_verdict=pass` cited as prerequisite | Yes |
| No new consensus code introduced | Yes |

`run_m017_workload_e_verdict=pass` is the gate token for M-018.

---

## 9. Scope Boundaries (What NOT to Do)

- **Do not implement BLS verification.** That is SEC-009, M-018.
- **Do not activate gRPC.** That is M-018.
- **Do not add `[features]` to Cargo.toml.** That is SEC-007c, M-019.
- **Do not run with PARTITION_BLOCK_PEERS or CENSOR_VALIDATOR.** Clean run only.
- **Do not measure latency percentiles.** That is not Workload E. Workload E
  is operability (hardware, sync time, storage). If you see latency data in
  your logs, you may note it as an observation, but it is not a pass criterion.
- **Do not report sync time as "measured at 10,000 epochs."** You will run
  20 epochs. Extrapolate and say so.
- **Do not claim full row-7 closure.** M-016 closed the reconstruction step;
  M-018 closes the accessibility step. M-017 does not touch row-7.

---

## 10. Carry-Forward to M-018

After M-017 is approved, M-018 (Workload F: Bounded Public Auditability)
must address:

1. SEC-009: BLS epoch record verification (`process_epoch_checkpoint`)
2. AggSig storage in LMDB (`EpochCheckpoint` persistence)
3. gRPC public query surface activation
4. Row-7 accessibility component (public epoch retrieval without operator cooperation)
5. Python tests for gRPC: `test_grpc_get_epoch_record`, `test_grpc_no_write_methods`

These items are documented in:
- `docs/specs/ilc_m_series_test_coverage_and_hardening_plan_v0.1.md` §2
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` §SEC-009

`m017_approved_opens_m018`
`run_m017_workload_e_verdict=pass_required_before_m018`
