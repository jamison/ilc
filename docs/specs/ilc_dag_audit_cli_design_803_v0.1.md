# ILC DAG Audit CLI Design — Phase 803

**Phase:** 803
**Window:** 801-804
**Date:** 2026-04-23
**Status:** complete — design artifact for Codex implementation window

`dag_audit_cli_design_complete`
`binary_name=ilc_dag_audit`
`tier1_implementable_without_schema_changes`
`tier2_dag_vertex_archive_design_included_as_appendix`

---

## 1. Purpose

This document is the complete design specification for the `ilc_dag_audit`
binary. It is the primary deliverable of Phase 803. A Codex implementation
window may implement `ilc_dag_audit` from this specification without
further design decisions.

The binary discharges the Tier-1 component of
`verification_tooling_delivery_before_public_deployment`.

---

## 2. Binary Contract

### 2.1 Name and location

Binary: `ilc_dag_audit`
Source file: `ilc_consensus/src/dag_audit_main.rs`
Cargo.toml entry:

```toml
[[bin]]
name = "ilc_dag_audit"
path = "src/dag_audit_main.rs"
```

### 2.2 Invocation

```
ilc_dag_audit verify-epoch-chain \
    --lmdb-path <dir> \
    --genesis <genesis.json> \
    [--verbose]
```

The `verify-epoch-chain` subcommand is the only subcommand required for
Tier-1 condition discharge. The `--verbose` flag causes per-epoch BLS
verification steps to be emitted to stderr (mirroring state_extractor's
`[m016]` prefix convention; dag_audit uses `[dag_audit]`).

### 2.3 Exit codes

| Exit code | Meaning |
|---:|---|
| 0 | All epochs verified: chain gap-free, all BLS sigs valid against genesis key set |
| 1 | Verification failure: chain gap, BLS sig invalid, or sentinel mismatch |
| 2 | Usage error: missing or unparseable arguments |
| 3 | I/O error: cannot open LMDB or genesis file |

---

## 3. Input Contract

### 3.1 LMDB path

Same format as `state_extractor`. The `epoch_records` named database must
exist and be readable. The tool opens in read-only mode with `NO_LOCK`
(same flags as state_extractor).

Safety boundary: this mode is safe for offline use against an exported LMDB.
Against a live validator, it is safe for LMDB MVCC snapshot reads on Linux with
a sufficiently large map size; do not rely on live-validator reads in scripts
without first confirming the validator's map utilization is below its
configured ceiling.

### 3.2 genesis.json

The genesis file must contain a `validators` array. Each entry must have
a `consensus_key_hex` field carrying the hex-encoded BLS12-381 G1
(min_pk) public key for that validator.

The number of validators declared in genesis determines the expected
aggregate verification set (all-N, per HIGH-002 known limitation —
see §5).

---

## 4. Output Schema

The tool emits a single JSON object to stdout. The schema is versioned
with `schema_version` for forward compatibility.

```json
{
  "schema_version": "ilc_dag_audit_v1",
  "genesis_anchor": {
    "network_id": "<string>",
    "genesis_epoch": 0,
    "validator_count": 4,
    "genesis_network_note": "<string>"
  },
  "epoch_results": [
    {
      "epoch": 1,
      "state_root_hex": "<72 hex chars>",
      "agg_sig_hex": "<192 hex chars>",
      "bls_verified": true,
      "bls_error": null
    }
  ],
  "chain_complete": true,
  "sentinel_consistent": true,
  "all_sigs_verified": true,
  "high_002_note": "BLS verification uses all-N aggregate (fast_aggregate_verify). Production fix: track 2F+1 signing subset.",
  "verdict": "dag_audit_tier1_pass"
}
```

### 4.1 Verdict tokens

| Verdict | Meaning |
|---|---|
| `dag_audit_tier1_pass` | Chain complete, sentinel consistent, all BLS sigs verify |
| `dag_audit_fail_chain_gap` | One or more epochs missing from 1..N |
| `dag_audit_fail_sentinel_mismatch` | Sentinel epoch ≠ max committed epoch |
| `dag_audit_fail_bls_invalid` | One or more epoch BLS sigs failed verification |
| `dag_audit_fail_no_epochs` | LMDB has no committed epochs |

---

## 5. Verification Algorithm

### Step 1: Parse genesis

Load `consensus_key_hex` for each validator → deserialize as `blst::min_pk::PublicKey`.
Reject genesis if any key fails to parse.

### Step 2: Open LMDB

Open `epoch_records` database read-only. Collect all records (same scan
as state_extractor), separating the sentinel key (`\xff`) from epoch records.

### Step 3: Check chain completeness and sentinel consistency

Same logic as state_extractor: expected `1..=max` equals actual key set;
sentinel epoch == max committed epoch.

### Step 4: Per-epoch BLS verification

For each `StoredCheckpoint` in epoch order:

```
msg    = bincode::serialize(&checkpoint.record)
           where record = EpochSettlementRecord { epoch: EpochSeq(n), state_root: CIDv1Root }
DST    = b"ILC_EPOCH_SIG_BLS12381G2_XMD:SHA-256_SSWU_RO_NUL_"
sig    = blst::min_pk::Signature::uncompress(&agg_sig_bytes[..96])
result = sig.fast_aggregate_verify(true, &msg, DST, &pk_refs)
```

Where `pk_refs` is a `Vec<&blst::min_pk::PublicKey>` over all N validators
from genesis (HIGH-002: all-N, not 2F+1 subset).

If `agg_sig_bytes` is empty, record `bls_verified: false` with
`bls_error: "empty_sig_testnet_fault_sim_path"` (this is the testnet
fault-sim path noted in epoch_settlement.rs:40-41 and must be explicitly
reported). Empty aggregate signatures are never accepted by `ilc_dag_audit`;
operators who need structural-only testbed inspection should use
`state_extractor`, not this verifier.

### Step 5: Emit JSON and exit

If chain complete AND sentinel consistent AND all sigs verified: exit 0 with
`verdict: dag_audit_tier1_pass`.

Otherwise: exit 1 with the appropriate failure verdict.

---

## 6. Dependencies

All required crates are already present in `ilc_consensus/Cargo.toml`:

| Crate | Use |
|---|---|
| `blst` | `min_pk::PublicKey::deserialize`, `Signature::uncompress`, `fast_aggregate_verify` |
| `bincode` | `serialize(&EpochSettlementRecord)` for signed message reconstruction |
| `lmdb-rkv` | LMDB read-only access (same as state_extractor) |
| `serde_json` | Genesis parsing and JSON output |
| `serde` | `#[derive(Serialize)]` on output structs |

No new dependencies are required.

`tier1_requires_no_new_crate_dependencies`

---

## 7. HIGH-002 Known Limitation Surface

The tool must include the `high_002_note` field in every output regardless
of the verification result. This ensures that any consumer of the tool's
JSON output understands that the all-N verification reflects a known
implementation gap, not the final intended quorum semantics. The note
should read:

> "BLS verification uses all-N aggregate (fast_aggregate_verify). A valid
> epoch chain requires signatures from all N validators as currently
> implemented. Production fix: track per-validator sigs, select 2F+1
> subset before aggregation. See HIGH-002 in ilc_m_series_vulnerabilities_and_fixes."

---

## 8. Testability

The implementation window must deliver the following tests in
`tests/test_dag_audit_cli.py` (Python, using subprocess):

1. **test_dag_audit_pass_on_valid_lmdb**: Run against a known-good testbed
   LMDB with valid BLS sigs → assert exit 0, `dag_audit_tier1_pass`.
2. **test_dag_audit_fail_on_chain_gap**: Manufacture an LMDB with epoch 2
   missing → assert exit 1, `dag_audit_fail_chain_gap`.
3. **test_dag_audit_fail_on_invalid_sig**: Modify one epoch's `agg_sig_bytes`
   to garbage → assert exit 1, `dag_audit_fail_bls_invalid`.
4. **test_dag_audit_empty_sig_reports_honestly**: Run against a testnet-fault-sim
   LMDB where some sigs are empty → assert the `bls_error` field is populated
   per affected epoch and exit code is 1 (not a silent pass).
5. **test_dag_audit_output_schema**: Assert `schema_version`,
   `genesis_anchor`, `epoch_results`, `verdict`, and `high_002_note` are
   all present in the JSON output.

---

## Appendix A: Tier-2 Archive Mode Design (deferred)

### A.1 Purpose

Tier-2 archiving enables deep censorship-resistance audit by expert third
parties. A Tier-2 archive node stores every DAG vertex (block) observed
during consensus, not only the epoch settlement checkpoints.

### A.2 New LMDB table: `dag_vertices`

Key: `(round: u64, validator_id: u32)` → big-endian 12-byte composite key.
Value: `bincode::serialize(&StoredVertex { round, validator_id, payload_cid, parent_refs, validator_sig })`.

`StoredVertex` definition (new type to be added to `epoch_settlement.rs`):

```rust
#[derive(Serialize, Deserialize)]
pub struct StoredVertex {
    pub round: u64,
    pub validator_id: u32,
    /// CIDv1Root of the vertex payload (ECU transfers + epoch settlement txs).
    pub payload_cid: CIDv1Root,
    /// (round-1, validator_id) pairs for parents this vertex acknowledges.
    pub parent_refs: Vec<(u64, u32)>,
    /// 96-byte BLS12-381 G2 individual validator signature over the vertex.
    pub validator_sig_bytes: Vec<u8>,
}
```

### A.3 New LMDB table: `commit_wave_membership`

Key: `epoch: u64` → big-endian 8-byte.
Value: `bincode::serialize(&Vec<(round: u64, validator_id: u32)>)` — the
ordered list of vertices included in the committed wave for that epoch.

### A.4 Archive node mode

A new `--archive` flag for the `validator_harness` binary (or a separate
`archive_node` binary) that:
1. Joins the gossip network as a non-voting observer.
2. Writes every received+certified vertex to `dag_vertices` before forwarding.
3. When an epoch commits, writes the wave membership to
   `commit_wave_membership`.

### A.5 `ilc_dag_audit verify-dag-archive` subcommand

A second subcommand for Tier-2:

```
ilc_dag_audit verify-dag-archive \
    --lmdb-path <archive-dir> \
    --genesis <genesis.json>
```

This subcommand traverses `dag_vertices` and `commit_wave_membership` to
emit a per-epoch report confirming that all committed wave vertices are
present, the parent chain is connected to genesis, and no honest-validator
vertex is absent from a committed wave without a BFT-quorum reason.

### A.6 Implementation trigger

Tier-2 archive mode is not required for the
`verification_tooling_delivery_before_public_deployment` condition. It
should be scoped as a prerequisite for an external security audit engagement.
`tier2_trigger=pre_external_security_audit_engagement`
