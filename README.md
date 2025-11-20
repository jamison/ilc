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
Output: Generates `config/genesis.json` and the Genesis Hash.

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
*   `ilc_core/`: The protocol kernel.
    *   `types.py`: Node/Edge definitions.
    *   `agent.py`: The EVE agent logic (Mining).
    *   `consensus/`: Staking, Slashing, and Evolution logic.
    *   `network/`: P2P Gossip protocol.
    *   `server.py`: FastAPI interface.
*   `whitepaper/`: The living constitution of the protocol.
*   `tools/`: Bootstrapping and demo scripts.
