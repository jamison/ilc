# ILC Getting Started

> **PRE-PUBLIC-RC PLACEHOLDER.** This guide covers the internal development setup and pre-RC operator surfaces. It will be replaced at Phase ~1449 with the full operator bootstrap guide covering: genesis key ceremony, activation certificate verification, epoch 0→1 transition, external peer connection, and ECU-to-ILC conversion. Do not use this file as the authoritative onboarding guide for post-public-RC operators.

This guide bridges the root [`README.md`](../README.md) quickstart and the
[`docs/specs/`](specs/) protocol/spec docs. It is intentionally practical and
focuses on what you can run today from a fresh clone.

## 1) What ILC is

ILC is a content-addressed, evidence-first knowledge network. Agents submit
[claims](../metaphysics.md#6-trustless-truth-precisely-stated),
counter-claims, and task outcomes as signed protocol events. The node maintains
an [epistemic graph](../metaphysics.md#2-ilc-as-epistemological-instrument) and
deterministic protocol artifacts so replay and verification can be audited end
to end.

In this repository, there are two main operator surfaces:

- Runtime node/API surface ([`run_node.py`](../run_node.py) +
  [`ilc_core/server.py`](../ilc_core/server.py))
- Canon/replay-proof CLI surface (`ilc-canon-*` commands from
  [`pyproject.toml`](../pyproject.toml))

## 2) Prerequisites

- Python 3.10+
- Local checkout of this repository

Install dependencies:

```bash
pip install -r requirements.txt
```

## 3) First local run (quick path)

### Step A: Boot genesis

```bash
python3 tools/genesis_boot.py
```

Expected behavior:

- Reads `config/genesis.json`
- Prints genesis hash/signer summary
- Finishes with success status output

### Step B: Run node API

```bash
python3 run_node.py
```

Default local endpoints:

- API root: `http://127.0.0.1:8000/`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

### Step C: Run demo walkthrough

In a second terminal:

```bash
python3 tools/demo_walkthrough.py
```

## 4) Core concepts (runtime view)

- Node: a typed, signed payload in the
  [epistemic graph](../docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md#21-the-two-nodes).
- Claim: a positive assertion (`/v1/protocol/claim`).
- Refutation: a targeted contradiction (`/v1/protocol/refute`).
- Task outcome: work/task execution output (`/v1/protocol/task_outcome`).
- NodeID: canonical CIDv1 identity for protocol compatibility, with
  transitional legacy bridge support in selected boundaries; see the
  [Node ID term contract](architecture/ilc_canonical_glossary_and_concepts_v0.2.md#26-protocol-and-runtime-contracts-phase-990).
- Replay-proof package: deterministic evidence set used to verify
  contract-level behavior and drift; see the
  [methodology replay section](../methodology.md#10-progress-tracking-and-frontier-documents).

## 5) API surface you will use first

Basic node/runtime routes:

- `GET /` health and node summary
- `POST /mine` local claim mining helper
- `GET /node/{node_id}` node fetch by id
- `POST /gossip/receive` gossip ingestion boundary

Protocol routes:

- `GET /v1/protocol/schema`
- `POST /v1/protocol/claim`
- `POST /v1/protocol/refute`
- `POST /v1/protocol/task_outcome`
- `GET /v1/protocol/ep_task_schema`
- `POST /v1/protocol/ep_task`

## 6) CLI surfaces (canon and replay proof)

Installed scripts from `pyproject.toml` include:

- `ilc-canon-verify`
- `ilc-canon-summary`
- `ilc-canon-export`
- `ilc-canon-bundle-validate`
- `ilc-canon-bundle-sign`
- `ilc-canon-bundle-pipeline`
- `ilc-canon-bundle-replay`
- `ilc-canon-cluster-a-replay-proof`

Example replay-proof CI gate run:

```bash
ilc-canon-cluster-a-replay-proof ci-gate --profile release-v0.1 --pretty
```

## 7) Recommended operator checks

After local setup, run the deterministic closure/regression gates already used in this repo:

```bash
bash tools/check_cluster_a_replay_proof_release_gate.sh
bash tools/check_genesis_readiness_remediation_closure_996_1008.sh
```

## 8) Where to go next

- Runtime config policy: [`config/README.md`](../config/README.md)
- Architecture/canon terms: [`docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`](architecture/ilc_canonical_glossary_and_concepts_v0.2.md)
- Development methodology: [`methodology.md`](../methodology.md)
- Sidecar namespace and public-RC sidecar orientation: [`sidecars.md`](../sidecars.md)
- Current phase status: [`docs/phases/STATUS.md`](phases/STATUS.md)
