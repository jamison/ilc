# ILC Operator Guide

Status: local operator packaging guide
Phase: 1577e / GAP-DEPLOY-01

## 1. Overview

This guide explains how to run the local ILC operator packaging produced for
GAP-DEPLOY-01. It is scoped to local development and rehearsal. It does not
activate public RC, production minting, live settlement, validator admission, or
dynamic peer discovery.

The committed packaging includes:

- `Dockerfile` for a combined Python `ilc_core` plus Rust `ilc_consensus` image.
- `docker-compose.yml` for a local three-service observer/bootstrap topology.
- `monitoring/dashboards/ilc_node_dashboard.json` for Grafana import.

## 2. Key Provisioning Ceremony

IMPORTANT — M-019 Deferred TODO:
ILC Genesis Agent keys are NOT provisioned and NOT bundled with this image.
The operator must supply their own node key. Genesis Agent keys, meaning the
protocol founder identity, are managed separately and are never distributed via
Docker images or this guide.

For local observer mode, no production validator custody material is required.
For validator-harness operation, the operator must generate and mount their own
TLS certificate/key pair, consensus key, and validator config paths expected by
`validator_harness --config <path> --genesis <path>`.

Operator key rules:

- Never put private keys in the repository, Docker image, or compose file.
- Store local operator key material outside git, such as under `keys/<node-id>/`.
- Mount key directories read-only when running validator-harness containers.
- Never reuse a node private key across multiple operator identities.
- Back up operator keys using an offline custody process controlled by the
  operator, not by Genesis.

## 3. Peer Configuration

The local compose file uses static bootstrap configuration:

- `ILC_BOOTSTRAP_SEED_PEER=ilc-bootstrap-1`
- `ILC_BOOTSTRAP_BUNDLE_CID=local-testnet-bootstrap`

The current committed gossip registry is static-v1. Dynamic discovery requires the separate CDL-103 lane and GAP-DISCOV-03 activation. Until that happens,
operators should treat seed peers as explicit configuration, not automatic
network discovery.

## 4. First-Run Checklist

- Confirm Docker is installed on the operator machine.
- Run `docker compose config` and resolve any local compose errors.
- Confirm no private key paths are copied by `Dockerfile`.
- Confirm local disk has at least 10 GiB free for LMDB and logs.
- Start the local topology with `docker compose up --build`.
- Confirm the expected startup log line `node_daemon_starting` appears.
- Confirm the app endpoint line `node_daemon_api_endpoint url=http://127.0.0.1:8000` appears inside each container log.

## 5. Monitoring Setup

Import `monitoring/dashboards/ilc_node_dashboard.json` into Grafana when a
Prometheus scrape path is configured. The dashboard is schema metadata only; it
does not start Prometheus, Grafana, or a metrics exporter.

Initial metric names reserved for the operator surface:

- `ilc_peer_count_static`
- `ilc_peer_count_dynamic`
- `ilc_epoch_settlement_latency_ms`
- `ilc_ecu_attribution_events_total`
- `ilc_decay_application_events_total`

## 6. Expected Startup Lines

The root `run_node.py` entry point currently logs:

- `node_daemon_starting`
- `node_daemon_api_endpoint url=http://127.0.0.1:8000`
- `node_daemon_docs_endpoint url=http://127.0.0.1:8000/docs`

The Rust validator harness logs are separate and require an operator-supplied
config and genesis file:

```bash
validator_harness --config <path> --genesis <path>
```

## 7. Troubleshooting

If Docker is missing, install Docker Desktop or Docker Engine on the operator
machine and rerun `docker compose config`.

If startup fails with a missing Python module, rebuild the image with
`docker compose build --no-cache`.

If validator-harness startup fails with missing cert/key/config paths, confirm
that operator-supplied volumes are mounted read-only and that the config paths
match `ilc_consensus/src/config.rs`.

If peer discovery does not expand beyond the static seed, that is expected
before CDL-103/GAP-DISCOV-03. Do not treat this local compose topology as
dynamic discovery.

## 8. Non-Claims

This guide does not authorize live validator admission, production economics,
minting, settlement, public mirror push, package publication, or public-RC
activation.
