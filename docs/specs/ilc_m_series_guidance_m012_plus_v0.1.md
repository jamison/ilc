# M-Series Guidance: M-012 and Beyond

**Date:** 2026-04-17  
**For:** Gemini (owner), local reviewer / Sonnet (auditor)  
**Status:** Post-M-011 handoff — M-012 is the active next phase

---

## 1. Where we are

| Phase | Status | Commit |
|---|---|---|
| M-009 | COMPLETE — multi-machine testnet scaffold; all 6 SEC gates satisfied | `acfcfd2d` |
| M-010 | COMPLETE — `validator_harness` binary; config/node loader; SEC-005 closed | `152b584b` |
| M-011 | COMPLETE — `keygen` + `testnet_client` binaries; Workload A liveness tooling | `83a1305d` (main), `ef244272` (backfill) |
| **M-012** | **NEXT** | — |

**M-011 verdict:** `binary_complete` — tooling committed and smoke-tested (30/30 Rust tests).
Real 4-validator run requires provisioning (see M-013 below).

**Security gate status:**
- SEC-001 ✓ Implementation CLOSED (`acfcfd2d`); CDL-066 Track A ratification open (Window 707+, does not block M-series)
- SEC-002 ✓ CLOSED (M-008)
- SEC-003 ✓ CLOSED (M-008)
- SEC-004 OPEN dormant — requires CDL-017 activation; M-019 handoff must name it
- SEC-005 ✓ CLOSED (M-010 `83a1305d`)
- SEC-006 ✓ CLOSED (M-008)

---

## 2. M-012 — Full BFT ECUTransfer Round-Trip

**Owner:** Gemini  
**Prerequisite:** M-011 approved ✓  
**Scope:** Full owned-object fast path end-to-end from a non-validator client.

In the Mysticeti fast path, the originator of a `BroadcastHonest` receives
`AckFor` messages from other validators. M-011's `testnet_client` does not
collect these acks because it has no listening QUIC port. M-012 fixes this.

**Implementation requirements:**

1. `testnet_client` binds a QUIC listening port at startup
2. Client sends `BroadcastHonest` to all 4 validators
3. Client collects `AckFor` messages from at least 2F+1 = 3 validators
4. Client forms `TransferCertificate { transfer: ECUTransfer, sigs: Vec<ValidatorSig> }`
5. Client broadcasts `TransferCertificate` to all 4 validators
6. Each validator calls `execute_certificate` and updates `BalanceStore`
7. Client verifies balance update on at least 3 validators via gRPC query

**CLI additions to `testnet_client`:**
- `--msg full_transfer` mode (new) — runs the complete round-trip above
- `--listen-addr <addr>` — QUIC address to bind for receiving `AckFor`
- The existing `--msg broadcast` (fire-and-forget) remains unchanged

**Deliverables:**
- Updated `ilc_consensus/src/testnet_client_main.rs`
- `docs/research/ilc_mysticeti_testnet_M012_full_bft_transfer_v0.1.md`
- `tests/test_phase_M012_full_bft_transfer.py`
- Updated `tools/run_mysticeti_testnet_M011.sh` or new `run_mysticeti_testnet_M012.sh`

**Verdict target:** `binary_complete` (tooling committed, real run on 4 validators follows in M-013)

**Claude audit checklist:**
- [ ] Client binds a real QUIC port (not simulated)
- [ ] AckFor collection uses actual network receives, not in-process
- [ ] `TransferCertificate` formed only after 2F+1 = 3 validator acks
- [ ] `execute_certificate` called on all 4 validators (not just quorum)
- [ ] Balance update verified via independent query (not self-reported)
- [ ] Existing `--msg epoch_settlement` and `--msg broadcast` still pass smoke test
- [ ] 30+ Rust unit tests still pass
- [ ] M-011 8/10 phase tests unaffected

---

## 3. M-013 — Workload A: Real 4-Validator Liveness Run

**Owner:** Gemini (execution) + local reviewer (verification)  
**Prerequisite:** M-012 approved  
**Scope:** First real multi-machine run. Proves liveness and BFT tolerance.

**Provisioning steps (run once, before M-013 phases):**

```bash
# 1. Generate BLS keypairs for all 4 validators
bash tools/run_mysticeti_testnet_M011.sh --keygen

# 2. Generate self-signed mTLS certs
bash tools/run_mysticeti_testnet_M011.sh --gen-tls

# 3. Build all binaries
cargo build --release --bin validator_harness --bin keygen --bin testnet_client

# 4. Distribute binary + configs to ilc-node-2 and ilc-node-3
# (follow --operator-guide output)

# 5. Start all 4 validators
# 6. Inject EpochSettlementTx epochs 1-10 to all validators
# 7. Verify epoch_record_committed:epoch=N in all 4 logs
# 8. Kill validator 1 (silent-validator test)
# 9. Inject epochs 11-12 to validators 2, 3, 4
# 10. Verify epochs 11-12 committed on 3 remaining validators
```

**Pass criteria:**
- All 4 validators commit epochs 1-10 with `epoch_record_committed:epoch=N` log line
- With validator 1 silent: validators 2, 3, 4 commit epochs 11-12 (liveness with F=1)
- No panics, no LMDB map errors, no mTLS rejections during the run

**Verdict target:** `run_m013_workload_a_verdict=pass`

**Deliverables:**
- `docs/research/ilc_mysticeti_workload_a_results_M013_v0.1.md` — run record with log evidence
- `tests/test_phase_M013_workload_a_results.py`
- STATUS.md backfill

---

## 4. M-014 and beyond

| Phase | Scope | Prerequisite |
|---|---|---|
| M-014 | Workload B: censorship resistance drill (f=1 censoring validator; note deviation from original f=2 spec) | M-013 |
| M-015 | Workload C: partition / heal / recovery | M-014 |
| M-016 | Workload D: replayability + state extraction | M-015 |
| M-017 | Performance baseline (100+ epochs, latency at 50/95/99th percentile) | M-016 |
| M-018 | gRPC query surface hardening | M-017 |
| M-019 | CDL-017 activation handoff and SEC-004 transition | M-018 |

Full M-phase table: `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` §7.

---

## 5. Docs to read at M-012 session start

1. `docs/PLANNING_INDEX.md` — verify M-series current state entry
2. `docs/phases/STATUS.md` (tail, M-series entries) — confirm M-011 is last M-phase
3. `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` — full lane spec
4. `docs/research/ilc_mysticeti_testnet_M011_workload_a_v0.1.md` — M-011 artifact (what exists to build on)
5. `docs/phases/phase_M011_workload_a_walkthrough.md` — design decisions, mTLS constraint, scope boundary

---

## 6. Local reviewer (Sonnet) responsibilities

At each M-phase:
- Read the deliverable artifact and test file before approving
- Run audit checklist items that can be verified by code inspection
- Verify two-commit structure: main commit (exact deliverables) + backfill (walkthrough + STATUS.md)
- Check that STATUS.md entry matches actual commit hash
- Confirm M-series lane doc phase table is updated to COMPLETE for the finished phase
- Flag any SEC gate that appears newly satisfied but not yet marked CLOSED

Do not approve a phase if:
- Verdict is missing or ambiguous
- Walkthrough doc is absent
- STATUS.md is not updated
- Any previously-passing Rust test is now failing
