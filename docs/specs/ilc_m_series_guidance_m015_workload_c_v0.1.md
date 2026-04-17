# ILC M-Series Guidance: M-015 — Workload C Partition/Heal/Recovery

**Prepared by:** Claude Sonnet 4.6 (local reviewer)  
**Date:** 2026-04-18  
**For:** Gemini  
**Prerequisite:** M-014 COMPLETE `34e492a5`; post-audit cleanup `dfbe85b5`

---

## 1. Phase identity

**M-015 — Phase 690 Workload C: Partition/Heal/Recovery**

Originally planned as M-012 before the BFT ECUTransfer round-trip insertion.
The status table in `ilc_mysticeti_implementation_lane_m_series_v0.1.md` is
authoritative: M-015 = Workload C.

---

## 2. TLA+ Spec C — formal pre-condition (READ BEFORE CODING)

Before running the empirical testbed, read:

```
docs/specs/tla/ilc_partition_heal.tla
docs/specs/tla/ilc_partition_heal.cfg
```

TLC has verified this spec (5,577 states, 867 distinct, depth 13 — PASS).
The spec formally defines the pass criteria for M-015 and proves they are
achievable under the ILC epoch settlement protocol.

**Three properties M-015 must demonstrate empirically:**

| Property | TLA+ name | M-015 meaning |
|---|---|---|
| No fork during partition | `NoNewGlobalCommitDuringPartition` | No conflicting epoch commits while split |
| Eventual commit after heal | `EventualCommit` | All submitted records committed after reconnect |
| No loss | structural (Deliver is additive-only) | No submitted record permanently lost |

These map exactly to the Phase 690 Workload C pass criteria. The TLA+ proof
shows they hold in the abstract model. The empirical run must demonstrate they
hold in the Rust implementation.

---

## 3. Scope

Run Phase 690 Workload C:

1. Start 4 validators normally (loopback multi-process, same topology as M-013/M-014)
2. Submit an `EpochSettlementTx` for epoch 1 to ALL 4 validators (pre-partition baseline)
3. Introduce a simulated partition: block network communication between {V1,V2} and {V3,V4}
4. Submit an `EpochSettlementTx` for epoch 2 to the A-side {V1,V2} ONLY during partition
5. Verify B-side {V3,V4} has NOT committed epoch 2 during partition
6. Heal the partition: restore full network connectivity
7. Verify all 4 validators eventually commit epoch 2

**Partition mechanism for loopback testbed:**  
Since validators run as local processes communicating on loopback, the simplest
partition mechanism is OS-level firewall rules (`pfctl` on macOS) or port blocking.
Alternatively, use a CENSOR-style env var extension to the network layer that
drops outbound connections from {V1,V2} to {V3,V4} ports and vice versa.
The chosen mechanism must be documented in the results doc with its exact implementation.

---

## 4. Pass criteria (from Phase 690 spec)

1. No conflicting commits during partition — **safety preserved, no fork**
2. Recovery to normal operation **within 10 epoch durations** after reconnection
3. No submitted epoch records **permanently lost**

All three must be satisfied. Report each explicitly.

---

## 5. Deliverables

| Artifact | Path |
|---|---|
| Results doc | `docs/research/ilc_mysticeti_workload_c_results_M015_v0.1.md` |
| Test file | `tests/test_phase_M015_workload_c_results.py` |
| Walkthrough (backfill) | `docs/phases/phase_M015_workload_c_walkthrough.md` |
| STATUS.md backfill | Append M-015 line with verdict and commit hash |

---

## 6. Results doc required content

The results doc must contain:

1. **Partition mechanism** — exact implementation used (pfctl rules, env var drop,
   or other), command lines or code that induced the partition
2. **Pre-partition evidence** — `epoch_record_committed:epoch=1` from all 4 validators
3. **During-partition evidence** — epoch 2 submitted to A-side; B-side validators
   show NO `epoch_record_committed:epoch=2` log line while partition is active
4. **Post-heal evidence** — after healing, B-side shows `epoch_record_committed:epoch=2`
5. **Recovery time** — epoch delta from heal to final commit (must be ≤10 epoch durations)
6. **No-loss confirmation** — epoch 1 records (pre-partition) still present after heal
7. **TLA+ Spec C connection** — one sentence per criterion connecting to the TLA+ result:
   - NoNewGlobalCommitDuringPartition → observed B-side silence during partition
   - EventualCommit → observed B-side commit after heal
   - No-loss → observed epoch 1 persistence throughout
8. **Explicit PASS or FAIL verdict** per criterion and overall

---

## 7. Test file requirements

`tests/test_phase_M015_workload_c_results.py` — minimum 8 tests:

1. Results doc exists at the correct path
2. Pre-partition epoch 1 committed: `epoch_record_committed:epoch=1` present for all 4 validators (or at least one per side)
3. During-partition B-side silence: assert B-side log does NOT contain `epoch_record_committed:epoch=2` before heal token
4. Post-heal B-side commit: `epoch_record_committed:epoch=2` appears in B-side logs after heal
5. Recovery within 10 epochs: a measurement or claim with numeric delta ≤10 is present
6. No-loss: epoch 1 evidence still present after heal (i.e., results doc asserts epoch 1 not lost)
7. TLA+ Spec C referenced (search for `ilc_partition_heal` or `Spec C`)
8. Explicit overall PASS or FAIL verdict token present

Each test must anchor to a literal token from the actual run. Tests that search
for generic prose (e.g., `"safety"` or `"recovery"`) will be rejected on audit.

---

## 8. Two-commit pattern (mandatory)

**Commit 1 (main):** Partition mechanism code (if any) + runner script + results doc + test file.  
**Commit 2 (backfill):** Walkthrough + STATUS.md tail update.

Both commit hashes must match what is on disk. Report the actual `git log --oneline -2` output.

---

## 9. Partition implementation notes

**Option A — pfctl (macOS firewall, recommended for clean network-layer partition):**
```bash
# Block V3 (port 9003) and V4 (port 9004) from V1/V2 perspective
sudo pfctl -e
echo "block drop quick proto tcp from any to 127.0.0.1 port {9003, 9004}" | sudo pfctl -f -
# ... run epoch 2 submission to V1/V2 only ...
# Heal:
sudo pfctl -F all -f /etc/pf.conf
```
This requires sudo on macOS. If unavailable, use Option B.

**Option B — env var network drop (no sudo required):**
Extend `NodeRunner` with a new `PARTITION_BLOCK_PEERS` env var (comma-separated
validator IDs to drop all outbound messages to). This is analogous to the M-014
`CENSOR_VALIDATOR` pattern and stays within the existing testnet_fault_sim boundary.
V1 and V2 set `PARTITION_BLOCK_PEERS=3,4`; V3 and V4 set `PARTITION_BLOCK_PEERS=1,2`.

If adding code to `node.rs` or `network.rs`, add a `// TODO(pre-production): isolate
under #[cfg(feature = "testnet_fault_sim")]` comment consistent with M-014 pattern.
The 30 Rust tests must still pass.

**Option C — process kill (crude but acceptable for documentation):**
Kill V3 and V4 processes (simulate them being unreachable), submit epoch 2 to V1/V2,
then restart V3 and V4. Clearly label this as a process-kill partition in the results
doc; note it doesn't test actual network-layer isolation.

Choose whichever option is most reproducible and document it precisely.

---

## 10. Claude audit checklist

- [ ] Partition mechanism is documented with exact commands or code
- [ ] Pre-partition epoch 1 committed by all 4 validators (literal log lines)
- [ ] B-side silence during partition confirmed (B-side log checked for absence of epoch 2 commit)
- [ ] Post-heal B-side commit confirmed (literal log line)
- [ ] Recovery time stated as numeric epoch delta ≤10
- [ ] No-loss assertion for epoch 1 explicit
- [ ] Each Phase 690 criterion answered as PASS or FAIL individually
- [ ] TLA+ Spec C cited per criterion (not just mentioned once generically)
- [ ] 8+ tests, all anchored to literal run tokens
- [ ] 30/30 Rust tests still pass (if any Rust code touched)
- [ ] Both commit hashes match `git log --oneline -2`

---

## 11. What comes after M-015

M-016 = Workload D: Replayability and State Extraction.  
Prerequisite: M-015 approved. Do not begin M-016 until M-015 is explicitly approved.
