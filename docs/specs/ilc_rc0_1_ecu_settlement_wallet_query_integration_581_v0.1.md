# ILC RC0.1 ECU Settlement and Wallet Query Integration 581 v0.1

Status: locked
Date: 2026-04-03
Phase: 581
Owner lane: G8 implementation cluster

## 1. Bounded RC target

Phase 581 promotes the already-landed LMDB-backed economic runtime into the
explicitly verified authoritative settlement and wallet-query path for the
RC0.1 curated testnet.

Required governance tokens:
- `phase_581_live_settlement_path_authoritative`
- `phase_581_replay_idempotency_required`
- `phase_581_wallet_queries_must_read_settled_lmdb_state`
- `phase_581_runtime_roots_must_remain_identity_aligned`
- `phase_581_no_public_claimability_or_spend_semantics`
- `phase_581_keeps_576_577_578_meaning_unchanged`

This packet does not create public claimability, spend, transfer, withdrawal,
or founder/genesis payout semantics. It proves the live three-machine runtime
can settle one bounded epoch and expose read-only wallet and ledger state from
durable LMDB-backed roots without semantic drift.

## 2. Authoritative runtime surfaces

The authoritative Phase 581 runtime surfaces are:
- `ilc_core/rc/economic_cycle_runtime.py`
- `tools/query_rc0_1_economic_state.py`
- `tools/run_rc0_1_economic_proof.py`
- `tools/testbed/check_phase_581_settlement_wallet_query_integration.py`
- `tools/testbed/run_phase_581_settlement_wallet_query_integration.py`

The authoritative artifact set for the integration check is:
- one passing Phase 580 scenario root
- one `economic-state/manifest.json` durable runtime-state manifest
- one primary economic proof runner manifest
- one repeated economic proof runner manifest proving idempotent replay
- live wallet status, wallet history, wallet export, ledger summary, graph
  summary, quorum record, and store summary query payloads
- one machine-legible `phase_581_settlement_wallet_query_manifest.json`

## 3. Deterministic settlement and wallet query contract

`phase_581_live_settlement_path_authoritative`.

A passing Phase 581 integration requires all of the following:
- the Phase 580 integration proof remains valid for the same scenario root
- the live durable economic manifest exists and remains bound to the same
  scenario root as the Phase 579 and Phase 580 artifacts
- settlement status remains `applied` on the authoritative runtime root or
  `idempotent_replay` on deterministic replay only
- repeated proof execution preserves wallet export, wallet status, wallet
  history digests, ledger summary, and quorum-record identity without drift
- wallet status, wallet history, and wallet export queries read settled
  LMDB-backed state rather than projection-only helper files
- zero-balance and rewarded wallets are both queryable on the same settled
  runtime root
- the runtime-store roots, runtime identity, quorum record, and ledger summary
  remain aligned on `task_id`, `epoch_id`, and `claim_batch_sha256`

`phase_581_replay_idempotency_required`.

`phase_581_wallet_queries_must_read_settled_lmdb_state`.

`phase_581_runtime_roots_must_remain_identity_aligned`.

## 4. Claimability and read-only boundary

`phase_581_no_public_claimability_or_spend_semantics`.

The wallet surface in RC0.1 remains read-only visibility and accounting only.
A passing Phase 581 surface must not expose:
- spend, transfer, withdrawal, or signing authority
- claimable or withdrawable public balances
- private-key, mnemonic, or wallet-secret material
- any wallet query field that implies live public payout authority

Phase 581 proves settled balances and history are machine-auditable. It does
not widen the constitutional meaning fixed by Phase 576.

## 5. Carry-forward into Phase 582

Phase 581 is complete when the live economic runtime, replay-safe settlement,
and wallet-query surfaces are authoritative and machine-legible over the same
scenario root.

This packet does not authorize:
- public-release minting semantics
- spend, transfer, or withdrawal wallet semantics
- new persisted-graph roles beyond the Phase 577 minimum contract
- lineage widening beyond the Phase 578 curated boundary

Carry-forward obligation for Phase 582:
- `agreement_score` currently stands in as the RC0.1 testnet proxy for
  `centrality_score` when building passive ECU claims in `tools/agent_loop_v1.py`
- the bounded CDL-V7 reproducibility disposition must name that proxy as a
  testnet approximation and preserve the obligation to replace it with graph
  centrality before any public-release claim widens beyond RC0.1 testnet scope

`phase_581_keeps_576_577_578_meaning_unchanged`.
