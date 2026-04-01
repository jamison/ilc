# ILC Remote Control Surface v0.1

Status: planning spec
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This document defines the deterministic control surface for the three-machine
testbed. The intent is to let the home control machine drive remote execution
without relying on ad hoc shell work on each VPS.

## 2. Control-surface principle

The authoritative control surface is script-first.

Primary interfaces:
- repo-local scripts
- JSON and NDJSON control files
- SSH execution from the home machine
- systemd on the remote nodes

Optional IDE plugins are secondary interfaces only.

## 3. Canonical control files

### 3.1 Host inventory

Recommended path:
- `testbed/hosts.json`

Minimum schema:
- `name`
- `ssh_host`
- `ssh_user`
- `repo_path`
- `venv_path`
- `config_path`
- `systemd_unit`

### 3.2 Curated bootstrap peers

Recommended path:
- `testbed/bootstrap_peers.json`

Used for curated bootstrap distribution and verification.

### 3.3 Candidate discovery cache

Recommended path:
- `testbed/peer_candidates.ndjson`

Append-only observations only.

### 3.4 Local overrides

Recommended path:
- `testbed/peer_overrides.json`

Used for manual allow, deny, and pin rules.

## 4. Canonical remote scripts

The current implementation lane uses these script names:
- `tools/testbed/render_testbed_configs.py`
- `tools/testbed/generate_testbed_tls.sh`
- `tools/testbed/render_bootstrap_peers.py`
- `tools/testbed/render_peer_candidates.py`
- `tools/testbed/apply_peer_promotion.py`
- `tools/testbed/verify_bootstrap_peers.py`
- `tools/testbed/prepare_remote_app.sh`
- `tools/testbed/sync_repo.sh`
- `tools/testbed/install_service.sh`
- `tools/testbed/push_configs.sh`
- `tools/testbed/start_nodes.sh`
- `tools/testbed/stop_nodes.sh`
- `tools/testbed/restart_nodes.sh`
- `tools/testbed/start_home_node.sh`
- `tools/testbed/stop_home_node.sh`
- `tools/testbed/restart_home_node.sh`
- `tools/testbed/tail_home_node.sh`
- `tools/testbed/tail_logs.sh`
- `tools/testbed/run_remote_smoke.sh`
- `tools/testbed/check_three_node_exchange.sh`
- `tools/testbed/collect_diagnostics.sh`
- `tools/testbed/run_three_node_exchange.sh`
- `tools/testbed/run_recovery_drills.sh`
- `tools/testbed/run_negative_path_drills.sh`

## 5. Script output contract

Every remote script must emit deterministic machine-readable results.

Accepted output shapes:
- single-line status markers
- newline-delimited JSON
- final JSON summary file

Required operator-visible outcome classes:
- success
- config failure
- bootstrap/genesis failure
- transport failure
- lifecycle failure
- remote connectivity failure

## 6. Logging contract

The first testbed does not need a full observability stack.
It does need deterministic retrievable logs.

Required sources:
- `journalctl` output for `ilc-node-v1.service`
- captured home-node log output under `out/testbed/home-node.log`
- captured stdout/stderr from testbed scripts
- `testbed/bootstrap_peers.json` snapshot in diagnostics bundles
- `testbed/peer_candidates.ndjson` and `testbed/peer_overrides.json` snapshots
  in diagnostics bundles
- per-run `manifest.json` under each diagnostics bundle root
- optional NDJSON run bundles collected on the home machine

## 7. Security posture for the control surface

Required posture:
- SSH keys only
- dedicated testbed user per VPS
- minimal sudo where needed
- no blanket root login requirement
- no direct autonomous promotion of candidates into active peers

## 8. Non-goals

This control surface does not require:
- Kubernetes
- Ansible
- Terraform
- a message bus
- remote autonomous agents on the VPSs

These may be useful later, but they are not required to achieve the first
release-candidate infrastructure proof.
