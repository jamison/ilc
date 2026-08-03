# ILC Value-Action Live RC Readback Binding

**Phase:** GAP-VALUE-ACTION-LIVE-RC-06
**Date:** 2026-08-03
**Status:** public-RC readback decision record

## Readback Question

For public RC, is Python LMDB authoritative for agent-id-to-agent-id settled ILC transfer balances and transfer records, or is Rust/gRPC readback required before claiming ILC transfer finality?

## Architecture Analysis

The live-RC ILC transfer lane implemented by GAP-VALUE-ACTION-LIVE-RC-01 through RC-05 is a Python LMDB settled-account path. `ILCTransferLedger.execute_transfer()` validates the value-action envelope, consumes the sender nonce, debits the sender, credits the recipient, and writes the transfer record inside one caller-provided LMDB write transaction.

This ILC settled-transfer path does not import Rust consensus code, does not call the production gRPC bridge, and does not mutate `EpochSettlementRecord`. `EpochSettlementRecord` remains a Rust consensus settlement record for epoch/checkpoint machinery and is not the source of truth for the Python settled-ILC transfer ledger.

The authoritative readback path for public RC is therefore:

```text
READBACK_PATH = "PYTHON_LMDB_AUTHORITATIVE"
```

## ECU Fast-Path Contrast

ECU fast-path transfer is a separate lane. It routes through Rust `ECUTransfer` surfaces and the Python-to-Rust adapter, and its readback requirements are handled by GAP-ECU-TRANSFER-RC phases. `PYTHON_LMDB_AUTHORITATIVE` applies only to the ILC settled-transfer ledger created by the GAP-VALUE-ACTION-LIVE-RC lane.

## Readback Surfaces

The public-RC ILC settled-transfer readback surfaces are:

- `ILCTransferLedger.get_balance(agent_id)` for balance readback.
- `ILCTransferLedger.get_transfer_record(transfer_id)` for transfer-record readback.
- `ILCTransferReadbackVerifier.verify_post_transfer_balance(...)` for exact expected-balance checks.
- `ILCTransferReadbackVerifier.verify_transfer_record_retrievable(...)` for record presence checks.

The LMDB named databases are:

- `ilc_transfer_balances`
- `ilc_transfer_records`

## Integrity Requirement

Transfer-record readback must recompute and validate the embedded `record_sha256`. A malformed or tampered stored record is not authoritative readback and must fail closed.

## Post-RC Note

A future Rust or gRPC balance-query surface may be added as a query adapter or mirror, but it is not required for public-RC ILC settled-transfer finality and does not supersede the Python LMDB source of truth unless separately ratified.

## Non-Claims

This decision record does not activate live transfer, does not add Rust readback, does not mutate `EpochSettlementRecord`, does not claim ECU fast-path Python-only readback, does not publish the public mirror, and does not activate mainnet.
