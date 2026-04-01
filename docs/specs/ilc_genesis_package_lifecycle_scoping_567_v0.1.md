# ILC Genesis, Package, and Lifecycle Scoping 567 v0.1

Status: locked
Date: 2026-04-01
Phase: 567
Owner lane: G8 implementation cluster

## 1. Scope target

Phase 567 locks the minimum startup, genesis, and packaging contract required
for the first three-machine testbed. The goal is to make transport
operationalization reproducible on real machines without absorbing a production
bootstrap ceremony or a full orchestration redesign.

## 2. Static peer-config JSON contract

The selected operator configuration format is JSON.

Required token:
- `json_peer_config_format_selected`

The JSON object must contain, at minimum:
- `node_id`
- `transport.kind`
- `transport.bind_host`
- `transport.bind_port`
- `transport.tls_cert_path`
- `transport.tls_key_path`
- `peers`

Duplicate peers are rejected at the config-loader boundary as
`duplicate_peers_rejected_at_config_loader_boundary`.

## 3. Test-grade genesis import contract

The selected genesis contract is a test-grade import reference, not a production
ceremony.

Required token:
- `test_grade_genesis_import_contract_selected`

The import reference must contain, at minimum:
- `network_id`
- `genesis_bundle_path`
- `genesis_bundle_sha256`

## 4. Lifecycle persistence rule

Persistence is locked to the minimum required startup surface.

Required token:
- `minimal_persistence_only_no_epoch_buffer_durability`

The following persist:
- startup configuration
- imported genesis reference
- existing event logs

The following remain out of scope:
- durable recovery of pending epoch buffers
- expanded consensus or ledger durability work

## 5. Packaging target

The selected packaging target is `venv + systemd`.

Required token:
- `venv_systemd_packaging_selected`

Containerization is deferred. This window only needs a reproducible operator path
for three-machine testing.

## 6. Required observability

Runtime and packaging failures must preserve deterministic operator signals.

Required token:
- `three_machine_logs_must_preserve_deterministic_error_tokens`

Logs and failure output must be sufficient to distinguish:
- configuration failure
- genesis import failure
- transport failure
- service/lifecycle failure
