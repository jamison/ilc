# ILC M-015 True Partition-Heal Recovery Remediation Note v0.1

**Author:** Codex  
**Date:** 2026-04-18  
**Purpose:** Convert the M-015 audit finding into an exact remediation spec for
future execution. This note does not amend the recorded M-015 result. It states
what must change before a future workload can honestly claim true partition-heal
recovery of the original submission rather than cold-restart re-ingestion.

---

## 1. Audit finding summary

Current M-015 proves:
- pre-partition ingest on all four validators for epoch 1,
- A-side ingest of epoch 2 while B-side is offline,
- B-side silence while offline,
- post-heal cold-start re-ingestion on B-side after explicit resubmission,
- A-side persistence of epoch 1.

Current M-015 does **not** prove:
- that the original epoch-2 submission eventually reaches B-side after heal,
- that heal alone is sufficient for eventual commit,
- that the epoch-settlement path is replayable or self-repairing after partition.

The decisive reason is architectural: the current `EpochSettlementTx` path
commits locally and does not propagate, queue, replay, or sync after reconnect.

Relevant code anchor:
- `ilc_consensus/src/node.rs`
  - `handle_epoch_settlement_tx()` commits locally only
  - no post-heal replay queue exists
  - no epoch-settlement sync message exists

---

## 2. Non-negotiable boundary for future claims

Before any future artifact claims true partition-heal recovery, all of the
following must be true in the empirical run:

1. The partition is a **live-process network partition**, not process death.
2. The B-side remains alive throughout the partition.
3. The original epoch-2 submission is made only during partition to the A-side.
4. No post-heal client resubmission of epoch 2 is sent to B-side.
5. After heal, B-side commits epoch 2 because the protocol recovers it, not
   because the client re-injected it.

If any one of those is false, the correct claim is a weaker one such as:
- cold-restart re-ingestion works, or
- post-heal manual replay works,
- but **not** true partition-heal recovery.

---

## 3. Required runtime changes

### 3.1 Replace process-kill partition with a live partition control

Required change:
- add a bilateral network-drop mechanism for validator-to-validator traffic.

Recommended implementation:
- extend `NodeRunner` in `ilc_consensus/src/node.rs` with:
  - `partition_block_peers: HashSet<u32>`
- parse env var:
  - `PARTITION_BLOCK_PEERS=3,4`
- apply the block on outbound validator-to-validator traffic in:
  - `send_to_peer()`
  - `broadcast_certificate()`

Required log token when a message is intentionally dropped:
- `[m015_partition_drop] validator_id=<self> target=<peer> kind=<message>`

Required code comment:
- `// TODO(pre-production): isolate under #[cfg(feature = "testnet_fault_sim")]`

Why this location:
- `dispatch()` is too narrow because it only sees inbound `EpochSettlementTx`.
- true partition simulation must block certificate / ack / sync traffic between
  the two validator sets.
- outbound send control is the cleanest bilateral fault-injection point in the
  current structure.

### 3.2 Add epoch-settlement replay or sync semantics

Required change:
- the epoch-settlement lane must gain a protocol-level recovery path after
  reconnect.

Current blocker:
- `handle_epoch_settlement_tx()` in `ilc_consensus/src/node.rs` only commits to
  local `epoch_store`.
- it does not:
  - broadcast the committed epoch record,
  - queue failed deliveries,
  - request missing epoch records on reconnect,
  - or answer missing-epoch queries from peers.

At least one of the following must be implemented before a true recovery claim
is honest:

Option A — explicit epoch sync messages:
- add `GossipMessage::MissingEpochSync`
- add `GossipMessage::MissingEpochResponse`
- on reconnect or on periodic timer, a validator that is behind requests missing
  epochs from peers
- responders send the missing epoch records
- receiver commits them and logs replay provenance

Option B — epoch settlement rebroadcast plus reconnect replay queue:
- on first successful commit of an epoch record, queue it for peer delivery
- if delivery to a peer fails during partition, keep it in a pending set
- when connection to that peer is re-established, replay pending epoch records
- log replay completion per peer

Recommendation:
- use **Option A**. It is cleaner, auditable, and aligns with the already
  established `MissingCertSync` / `MissingCertResponse` pattern.

Required proof token after implementation:
- `m015_epoch_recovery_path_protocol_driven`

### 3.3 Preserve validator state across heal

Required change:
- do **not** clear B-side LMDB during the heal step.

Current invalidating behavior:
- `rm -rf "$V3_LMDB"` / `rm -rf "$V4_LMDB"`

That turns the run into cold-start re-ingestion, not recovery.

Required post-heal shape:
- V1 / V2 / V3 / V4 all remain alive, or if restart is absolutely required,
  their state stores remain intact and are treated as reconnect, not reset.

Recommendation:
- prefer **no restart at all** during the partition-heal workload.
- if restart is unavoidable for runner reasons, retain all four LMDBs and prove
  that the missing epoch arrived from peer sync after reconnect.

---

## 4. Required runner changes

File to replace or supersede:
- `tools/testbed/ilc_loopback_m015_runner.sh`

### 4.1 Safety and isolation

Replace:
- in-place rewrite of tracked config files
- `pkill -f validator_harness`

With:
- temporary copied config directory under `mktemp -d`
- explicit PID file management for only the validators launched by this run
- `trap cleanup EXIT INT TERM`

Required runner guarantees:
- no tracked repo files are mutated in place,
- no unrelated validator processes are killed,
- all temporary files are namespaced to the run.

### 4.2 Partition lifecycle

Required runner phases for a true claim:

1. start all four validators and wait for readiness
2. submit epoch 1 to all four validators
3. verify epoch 1 committed on all four validators
4. activate bilateral partition:
   - V1/V2 block peers 3,4
   - V3/V4 block peers 1,2
5. submit epoch 2 to A-side only
6. verify B-side did not commit epoch 2 during partition
7. heal partition:
   - remove `PARTITION_BLOCK_PEERS`
   - keep all validators running
8. wait for protocol-driven recovery
9. verify B-side commits epoch 2 without any post-heal client replay
10. verify epoch 1 still present on all four validators

Required runner tokens:
- `m015_partition_active`
- `m015_partition_healed`
- `m015_no_post_heal_client_resubmission`
- `m015_bside_epoch2_commit_after_heal`
- `m015_epoch1_persisted_all_four`
- `run_m015_workload_c_tier2_verdict=pass`

### 4.3 Failure discipline

The runner must exit nonzero on any failed checkpoint.

Replace:
- warning-only behavior after failed submissions or missing commit tokens

With:
- explicit `exit 1` on:
  - failed readiness
  - missing epoch 1 pre-partition commit
  - unexpected B-side epoch 2 commit during partition
  - missing post-heal B-side epoch 2 commit
  - any post-heal client resubmission to B-side
  - failed no-loss check

Required helper behavior:
- `submit_epoch()` must return failure if all retries fail
- checkpoint functions must hard-fail, not print-and-continue

---

## 5. Required evidence changes

### 5.1 Results artifact

A future results doc may only claim true recovery if it contains all of:

1. exact partition mechanism and activation commands
2. literal pre-partition epoch 1 commit lines for all four validators
3. literal A-side epoch 2 ingest lines during partition
4. literal B-side non-commit evidence during partition
5. heal token
6. literal B-side post-heal epoch 2 commit lines
7. explicit statement that no post-heal client resubmission to B-side occurred
8. explicit identification of the protocol mechanism that delivered epoch 2
   after heal:
   - replay queue, or
   - missing-epoch sync response

Forbidden wording unless proven:
- `EventualCommit` from the original submission
- `no submitted epoch records permanently lost`
- `recovery was immediate upon message delivery`

Allowed wording if the stronger fix is not implemented:
- post-heal re-ingestion succeeded after explicit replay
- cold-start B-side recovery path succeeded

### 5.2 Preserve raw run evidence

Required committed or generated artifacts:
- runner transcript log
- per-validator logs
- optionally a compact extracted evidence file checked into `docs/research/`

Tests must not rely on prose alone.

---

## 6. Required test changes

File to replace or supersede:
- `tests/test_phase_M015_workload_c_results.py`

### 6.1 Add runner-shape tests

Add tests that inspect the runner source and forbid the old invalidating
behaviors:

1. no `pkill -f validator_harness`
2. no `rm -rf "$V3_LMDB"` / `rm -rf "$V4_LMDB"`
3. no post-heal `submit_epoch` to B-side validators for epoch 2
4. presence of `PARTITION_BLOCK_PEERS` control or an equivalent bilateral
   partition mechanism
5. runner exits nonzero on failed checkpoints

### 6.2 Add raw-evidence tests

Add tests against preserved raw logs or extracted evidence files:

1. B-side logs contain no epoch-2 commit before heal token
2. B-side logs contain epoch-2 commit after heal token
3. no post-heal client submission to B-side for epoch 2 appears in runner
   transcript
4. recovery token names the delivery mechanism
5. epoch 1 persistence is shown for all four validators, not A-side only

### 6.3 Keep document tests, but demote them

The current prose-token tests are still useful, but they must be secondary.
Primary assurance has to come from:
- runner-shape tests, and
- raw log / evidence-file tests.

---

## 7. Exact claim tiers going forward

### Tier 1 — weaker claim (already demonstrated)

Allowed claim text:
- process-kill partition with post-heal manual replay / re-ingestion succeeded

### Tier 2 — stronger claim (not yet demonstrated)

Required before allowed claim text:
- live partition with bilateral validator isolation
- no B-side reset
- no post-heal client replay
- protocol-driven eventual B-side commit after heal

Only Tier 2 justifies:
- true partition-heal recovery
- eventual commit of the original submission
- no-loss of the submitted epoch record across the partition event

---

## 8. Recommended next execution path

1. keep the current M-015 artifact as a documented weaker scenario unless it is
   deliberately amended downward,
2. implement `PARTITION_BLOCK_PEERS` and epoch-settlement recovery semantics,
3. rerun Workload C under the stronger runner,
4. update tests to inspect runner shape and raw evidence,
5. only then approve a true partition-heal recovery claim,
6. after that, open M-016 replayability/state-extraction work on top of the
   stronger recovery path.
