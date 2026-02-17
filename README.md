# Intelligent Labor Coin (ILC) - MVP Node

The reference implementation for the ILC Protocol—a decentralized epistemological graph where value is derived from verified truth (Proof of Intelligent Labor).

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize the Network (Genesis)
Boot the network with the axiomatic core (Math, Physics, Logic).

```bash
python3 tools/genesis_boot.py
```
Output: Reads `config/genesis.json` and prints the Genesis hash and signer summary.

### 3. Run the Node
Start the P2P Daemon and API Server.

```bash
python3 run_node.py
```
The API will be available at: http://127.0.0.1:8000

Interactive Docs: http://127.0.0.1:8000/docs

### 4. Run the Demo (User Simulation)
In a separate terminal, run the walkthrough script to mine your first claim.

```bash
python3 tools/demo_walkthrough.py
```

## 📂 Project Structure
*   `ilc_core/`: Core implementation package.
    *   `server.py`, `agent.py`, `graph.py`, `types.py`: runtime protocol surfaces.
    *   `protocol/`: replay-proof, event-log, and schema-bound protocol utilities.
    *   `ledger/`: canon export, bundle, registry, and settlement helpers.
    *   `cli/`: command-line entry points for canon and replay-proof operations.
    *   `encoding/`, `crypto/`: canonical encoding, CID/CBOR/COSE primitives.
    *   `analysis/`, `sim/`: analysis kernels and simulation harnesses.
    *   `genesis/`, `economics/`, `consensus/`, `network/`: bootstrap and policy/runtime modules.
*   `tools/`: bootstrapping, guardrail gates, migration utilities, and maintenance scripts.
*   `tests/`: focused phase gates and regression suites.
*   `docs/`: specs, ADRs, walkthroughs, and planning artifacts.
*   `whitepaper/`: protocol narrative and constitution layer.

## 🔧 Code Health Checks

```bash
python3 -m pytest tests/test_code_health.py -v  # Size/nesting thresholds
python3 tools/scan_duplicates.py                 # Duplicate imports/lines
```

## 📦 Canon Consumer

```bash
ilc-canon-summary --path tests/fixtures/canon_state_v0.1.json
ilc-canon-summary --path tests/fixtures/canon_state_v0.1.json --report
```
