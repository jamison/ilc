# M-Series Guidance: M-013 — Workload A Real Liveness Run

**Date:** 2026-04-17  
**For:** Gemini (owner), local reviewer / Sonnet (auditor)  
**Status:** M-012 approved `binary_complete` — M-013 is the active next phase

---

## 1. Where we are

| Phase | Status | Commit |
|---|---|---|
| M-011 | COMPLETE — `keygen` + `testnet_client` binaries; Workload A liveness tooling | `83a1305d` |
| M-012 | COMPLETE — full BFT ECUTransfer round-trip; `testnet_client --msg full_transfer` | `2086fc29` |
| **M-013** | **NEXT** | — |

**M-012 verdict:** `binary_complete` — tooling committed with two explicit deferrals
documented: gRPC balance verification (step 7) and genesis-read `f` value. Both are
acceptable for the testnet tooling phase. M-013 must not assume either deferral is
resolved.

**Key provisioning additions from M-012 (must be applied before M-013 run):**
- Client TLS cert generated via `tools/run_mysticeti_testnet_M012.sh --gen-client-tls`
- `ValidatorID(5)` → `127.0.0.1:9500` added to each validator's `peers` config via `--update-configs`
- Client cert `.der` copied into each validator's `peer_cert_dir`

---

## 2. M-013 — Workload A: Real 4-Validator Liveness Run

**Owner:** Gemini (execution) + local reviewer (verification)  
**Prerequisite:** M-012 approved ✓  
**Verdict target:** `run_m013_workload_a_verdict=pass`

This is the first real multi-machine run. It proves liveness under normal
operation (F=1, N=4) and BFT tolerance under a silent-validator scenario.

---

## 3. What M-013 is and is not

**Is:** A real run of the actual binaries against real network sockets on
real machines (or local processes with separate ports). Log evidence is
required — not assertions that logs would look like X.

**Is not:** A simulation. No synthetic log injection. No "would pass" language
in the results artifact. If the run does not happen, M-013 does not close.

**Is not:** A full BFT round-trip test (that was M-012). M-013 uses
`--msg epoch_settlement` (the M-011 liveness evidence path), not
`--msg full_transfer`. The `EpochSettlementTx` path is the Workload A
primary evidence signal.

---

## 4. Provisioning sequence (run once before the M-013 liveness run)

The M-011 harness (`tools/run_mysticeti_testnet_M011.sh`) and M-012 harness
(`tools/run_mysticeti_testnet_M012.sh`) together cover all provisioning steps:

```bash
# Step 1 — Generate BLS keypairs (if not already done from M-011)
bash tools/run_mysticeti_testnet_M011.sh --keygen

# Step 2 — Generate validator mTLS certs (if not already done)
bash tools/run_mysticeti_testnet_M011.sh --gen-tls

# Step 3 — Generate client TLS cert and copy to each validator's peer_cert_dir
bash tools/run_mysticeti_testnet_M012.sh --gen-client-tls

# Step 4 — Add ValidatorID(5) to each validator's peers config
bash tools/run_mysticeti_testnet_M012.sh --update-configs

# Step 5 — Build all binaries
cd ilc_consensus
cargo build --release --bin validator_harness --bin keygen --bin testnet_client

# Step 6 — Review operator guide for machine distribution steps
bash tools/run_mysticeti_testnet_M011.sh --operator-guide
```

If running all 4 validators on a single machine (loopback), use distinct ports
(e.g., 9001, 9002, 9003, 9004) and separate working directories for each
validator's LMDB data file and config.

---

## 5. M-013 run procedure

### Phase A: Baseline liveness (all 4 validators active)

```bash
# Start all 4 validators (each in its own terminal or background process)
./validator_harness --config config/mysticeti_testnet_M009/validator_1_config.json
./validator_harness --config config/mysticeti_testnet_M009/validator_2_config.json
./validator_harness --config config/mysticeti_testnet_M009/validator_3_config.json
./validator_harness --config config/mysticeti_testnet_M009/validator_4_config.json

# Inject EpochSettlementTx epochs 1-10 to ALL 4 validators
for EPOCH in $(seq 1 10); do
  for VALIDATOR_ADDR in <v1_addr> <v2_addr> <v3_addr> <v4_addr>; do
    ./testnet_client \
      --validator $VALIDATOR_ADDR \
      --cert config/mysticeti_testnet_M009/certs/client_cert.pem \
      --key  config/mysticeti_testnet_M009/certs/client_key.pem \
      --peer-cert config/mysticeti_testnet_M009/certs/<validator_cert>.der \
      --peer-id 5 \
      --msg epoch_settlement \
      --epoch $EPOCH \
      --count 1
  done
done

# Capture logs from all 4 validators
# Look for: epoch_record_committed:epoch=N  (in stderr of each validator_harness)
```

Pass criterion A: All 4 validator logs show `epoch_record_committed:epoch=N`
for N = 1 through 10.

### Phase B: Silent-validator tolerance (F=1 test)

```bash
# Kill validator 1 (SIGTERM or SIGKILL)
kill <validator_1_pid>

# Wait for clean shutdown (or kill immediately for worst-case test)

# Inject epochs 11 and 12 to validators 2, 3, 4 ONLY
for EPOCH in 11 12; do
  for VALIDATOR_ADDR in <v2_addr> <v3_addr> <v4_addr>; do
    ./testnet_client \
      --validator $VALIDATOR_ADDR \
      --cert config/mysticeti_testnet_M009/certs/client_cert.pem \
      --key  config/mysticeti_testnet_M009/certs/client_key.pem \
      --peer-cert config/mysticeti_testnet_M009/certs/<validator_cert>.der \
      --peer-id 5 \
      --msg epoch_settlement \
      --epoch $EPOCH \
      --count 1
  done
done
```

Pass criterion B: Validators 2, 3, and 4 logs show `epoch_record_committed:epoch=11`
and `epoch_record_committed:epoch=12`. Validator 1 shows neither (it was silent).

---

## 6. Pass criteria (all required for `run_m013_workload_a_verdict=pass`)

1. All 4 validators emit `epoch_record_committed:epoch=N` for N = 1..10
2. With validator 1 silent, validators 2+3+4 emit `epoch_record_committed:epoch=11` and `epoch_record_committed:epoch=12`
3. No panics in any validator log during the run (`thread 'main' panicked` or `RUST_BACKTRACE`)
4. No LMDB map errors (`MdbError`, `map full`, `LMDB_MAP_SIZE`)
5. No mTLS rejection errors (`certificate verify failed`, `peer_cert_not_registered`)
6. Validator 1 log shows no epoch 11 or 12 commit (it was not injected)

Partial runs (fewer than 4 validators reaching quorum for epochs 1-10) are a
`run_m013_workload_a_verdict=fail` with documented failure mode, not a deferred pass.

---

## 7. Deliverables

| File | Content |
|---|---|
| `docs/research/ilc_mysticeti_workload_a_results_M013_v0.1.md` | Run record with actual log excerpts, timestamps, pass/fail verdict, failure notes if any |
| `tests/test_phase_M013_workload_a_results.py` | Tests that verify the results artifact structure, required tokens, and verdict |
| `docs/phases/phase_M013_workload_a_walkthrough.md` | Design decisions, run conditions, failure modes encountered |
| `docs/phases/STATUS.md` | M-013 entry (backfill commit) |

**The results artifact must contain actual log lines** — copy/paste from real
validator stderr, not reconstructed from memory. At minimum:

```
epoch_record_committed:epoch=1   <-- from each of validators 1-4
...
epoch_record_committed:epoch=10  <-- from each of validators 1-4
epoch_record_committed:epoch=11  <-- from validators 2, 3, 4 only
epoch_record_committed:epoch=12  <-- from validators 2, 3, 4 only
```

If the run cannot be completed (provisioning blocked, network unavailable,
binary crash), document the failure mode fully and issue
`run_m013_workload_a_verdict=fail` with the specific criterion that failed.
Do not skip to M-014.

---

## 8. Audit checklist (local reviewer verifies before approving)

**Run evidence:**
- [ ] Results artifact contains actual log lines (not reconstructed language like "the log showed...")
- [ ] `epoch_record_committed:epoch=N` present for N=1..10 from all 4 validators
- [ ] `epoch_record_committed:epoch=11` and `epoch_record_committed:epoch=12` present from exactly validators 2, 3, 4
- [ ] Validator 1 log excerpts confirm no epoch 11/12 commit
- [ ] No panic lines in any validator log
- [ ] No LMDB map error in any validator log
- [ ] No mTLS rejection in any validator log

**Artifact quality:**
- [ ] Results artifact is plain English describing what happened, not word salad
- [ ] Pass/fail verdict stated explicitly (`run_m013_workload_a_verdict=pass` or `=fail`)
- [ ] If any criterion failed, the failure is described specifically (which criterion, which validator, what the log showed)
- [ ] Walkthrough describes the actual run conditions (local/remote, port layout, which machine ran which validator)

**Process:**
- [ ] Two-commit structure: main commit (results + test + artifact) then backfill (walkthrough + STATUS.md)
- [ ] STATUS.md entry contains actual commit hash (not `[pending]`)
- [ ] M-012 deferrals (gRPC balance verify, genesis f read) are not silently assumed resolved

**Regression:**
- [ ] M-011 Python phase tests still pass (8/10 passing as before; known failures remain known)
- [ ] M-012 Python phase tests still pass (4/4)
- [ ] 30+ Rust unit tests still pass (`cargo test` in `ilc_consensus/`)

---

## 9. M-014 and beyond (for context only — do not begin)

| Phase | Scope | Prerequisite |
|---|---|---|
| M-014 | Workload B: censorship resistance drill (f=1 censoring validator) | M-013 |
| M-015 | Workload C: partition/heal/recovery | M-014 |
| M-016 | Workload D: replayability + state extraction | M-015 |
| M-017 | Performance baseline (100+ epochs, latency at 50/95/99th percentile) | M-016 |
| M-018 | gRPC query surface hardening (closes M-012 step 7 deferral) | M-017 |
| M-019 | CDL-017 activation handoff and SEC-004 transition | M-018 |

M-018 is the natural closure point for the M-012 gRPC balance verification
deferral. Keep that in view but do not let it block M-013 or M-014.
