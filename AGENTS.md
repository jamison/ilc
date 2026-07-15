# ILC Agent Execution Guidelines

This file provides guidance for AI coding agents (and humans using AI tools) working
in the ILC repository. It covers project orientation, codebase structure, coding
standards, and contribution conventions.

---

## What Is ILC?

**Intelligent Labor Coin (ILC)** is a protocol for incentivizing, valuing, and
settling epistemic work — the production of knowledge, claims, refutations, and
reputation. Participants contribute work, earn ECU (Epistemic Credit Units), and
exchange these for ILC tokens according to a governed economic model.

The protocol is built around a hypergraph of content-addressed epistemic objects
called **Graph Nodes**. Each node is a fact, claim, refutation, agent identity,
or protocol artifact. Edges represent relationships: provenance, support,
contradiction, governance authority, and more.

Key public documentation:
- `README.md` — project overview and quickstart
- `QUICKSTART.md` — running a local node
- `docs/architecture/` — Architecture Decision Records (ADRs) and canonical glossary
- `docs/adr/` — formal governance decisions
- `economics.md` — ECU and ILC economic model overview
- `metaphysics.md` — epistemological foundations
- `WHITEPAPER.md` — full whitepaper

---

## Codebase Structure

```
ilc_core/          Python implementation — protocol runtime, economics, identity,
                   consensus interfaces, CLI, sidecar management
ilc_consensus/     Rust implementation — BLS signatures, QUIC transport,
                   LMDB graph store, post-quantum cryptography
tests/             pytest test suite (run with: python -m pytest)
docs/adr/          Architecture Decision Records
docs/architecture/ Canonical glossary and architecture specs
docs/specs/        CDLs (Constitutional Decision Logs), ratified specs
docs/genesis/      Genesis signing artifacts
docs/contact/      Published agent contact records (D2D pubkeys)
config/            Runtime configuration: governance, hardware archetypes
protocol/          Protocol schema definitions
tools/             Developer tooling and scripts
skills/            OpenClaw skill packages
```

### Key modules in `ilc_core/`

| Module | Purpose |
|--------|---------|
| `ilc_core/cli/` | CLI entry points (`ilc` command) |
| `ilc_core/economics/` | ECU reward, fee burn, expansion bounty |
| `ilc_core/epoch/` | Epoch emission, settlement, treasury distribution |
| `ilc_core/identity/` | Agent ID derivation, Sybil resistance |
| `ilc_core/reputation/` | Temporal decay, Popperian gate, diversity floor |
| `ilc_core/genesis/` | Genesis authority, serving receipts, assertion builder |
| `ilc_core/graph/` | LMDB graph adapter, truth primitive graph |
| `ilc_core/bundle/` | Layer 0 protocol bundle, type registry |
| `ilc_core/sim/` | Simulation harnesses (devnet scenarios, param grid) |
| `ilc_core/config.py` | Governance config loader |
| `ilc_core/hardware.py` | Hardware archetype loader |

---

## Development Setup

```bash
# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
python -m pytest

# Run a focused test
python -m pytest tests/test_<name>.py -q

# Rust components (requires Rust toolchain)
cd ilc_consensus && cargo build
```

The full test suite must pass before any contribution is considered complete.
If you add a runtime module in `ilc_core/`, add a corresponding test file in
`tests/test_<module_name>.py`.

---

## Coding Standards

These are hard rules for all `ilc_core/` and `ilc_consensus/` work. Violations
will be caught by `tests/test_sensitive_runtime_coding_taboos.py` and the checker
at `tools/check_sensitive_runtime_coding_taboos.py`.

### 1. Mandatory JSON Canonicalization

Any `json.dumps()` that feeds protocol state, hashing, signing, canon export,
or machine-verifiable artifacts **must** use `sort_keys=True`.

```python
# Correct
json.dumps(payload, sort_keys=True, separators=(',', ':'))

# Wrong — key order is insertion-order, non-deterministic
json.dumps(payload)
```

Insertion-order desynchronization across implementations breaks DAG hash
reproducibility. This is a zero-tolerance rule.

### 2. No Predictable PRNG in Runtime or Security-Sensitive Paths

`import random` is **banned** in `ilc_core/`. The Mersenne Twister is predictable
and compromises Sybil protections in peer selection, quorum generation, and hash
routing.

```python
# Correct
import secrets
nonce = secrets.token_bytes(32)

# Wrong
import random
selected_peer = random.choice(peers)
```

Simulation-only or research-only code may use explicit deterministic generation
when that use is isolated and clearly marked non-protocol.

### 3. No Float for Economic or Staking Runtime State

Python `float` is **banned** for ECU, ILC, balance, stake, reward, earmark, and
settlement values. IEEE 754 drift destroys double-entry invariants.

```python
# Correct
from decimal import Decimal
amount = Decimal("12.500000")
if not amount.is_finite():
    raise ValueError("invalid_amount_non_finite")

# Wrong
amount = 12.5
```

**Critical:** `Decimal` silently accepts `"NaN"` and `"Infinity"`. Always call
`is_finite()` immediately after constructing a `Decimal` from external input.
- `Decimal("NaN")` causes `InvalidOperation` on comparison → crashes epoch processor (DoS)
- `Decimal("Infinity")` bypasses oversubscription checks (infinite money exploit)

### 4. No `assert` for Protocol or Validation Enforcement

`assert` is stripped by Python `-O`. Never use it for production economic bounds,
dependency constraints, or input validation in `ilc_core/`.

```python
# Correct
if amount <= 0:
    raise ValueError("amount_must_be_positive")

# Wrong
assert amount > 0
```

`assert` is correct and idiomatic in test files only.

### 5. Bound Remote Streams and Untrusted Payloads

Never `list.append()` against unbounded remote data. Enforce a hard `MAX_RECORDS`
cap before raising a capacity error, or process via iterator.

```python
# Correct
records = []
for i, item in enumerate(stream):
    if i >= MAX_RECORDS:
        raise ValueError("stream_exceeds_max_records")
    records.append(item)

# Wrong
records = [item for item in remote_stream]
```

### 6. Mandatory Network Timeouts

Every outbound HTTP request **must** include an explicit timeout.

```python
# Correct
requests.get(url, timeout=30)

# Wrong — exposes node to Slowloris/Tarpit DoS
requests.get(url)
```

### 7. TLS Verification Must Not Be Disabled

Never set `verify=False`, `check_hostname=False`, or equivalent in any `ilc_core/`
network path. If a certificate trust issue arises, fix it at the CA bundle level.

```python
# Correct
requests.get(url, timeout=30)  # verify=True is the default

# Wrong — silent MITM exposure
requests.get(url, verify=False, timeout=30)
```

### 8. Atomic Writes for Protocol Artifacts

Never write canonical, signed, registry, ledger, or key-lifecycle files directly
to their final path. Use a temporary file in the same directory then atomically
rename.

```python
# Correct
import os, tempfile
fd, tmp = tempfile.mkstemp(dir=target_dir)
try:
    with os.fdopen(fd, 'w') as f:
        json.dump(payload, f, sort_keys=True)
    os.replace(tmp, final_path)
except:
    os.unlink(tmp)
    raise

# Wrong — partial reads under crash
with open(final_path, 'w') as f:
    json.dump(payload, f)
```

### 9. Bounded Outbound Fetches and Archive Extraction

Downloads from remote or untrusted sources must have explicit byte limits.
Never use `extractall()` on untrusted archives without pre-validating every member
for path traversal, absolute paths, excessive member count, and total extracted size.

### 10. Epoch-Based Protocol Time, Not Wall Clock

Never use `datetime.now()` or `time.time()` to advance protocol logic, expire
consensus windows, or enforce settlement deadlines. OS clocks drift across topology.

```python
# Correct — use protocol epoch sequence number
def is_expired(item, current_epoch):
    return item.epoch + item.ttl_epochs < current_epoch

# Wrong — wall-clock-based expiry
def is_expired(item):
    return datetime.now() > item.expires_at
```

`datetime.now(timezone.utc)` is permitted only for local diagnostic logging.

### Quick Checklist Before Committing `ilc_core/` Changes

Before submitting any change to `ilc_core/`, confirm:

- [ ] No `float` introduced for ECU, balance, stake, or reward values
- [ ] Any `Decimal` from external input passes `is_finite()` before use
- [ ] All protocol JSON uses `json.dumps(..., sort_keys=True)`
- [ ] No `import random` in runtime paths
- [ ] No `assert` for production validation
- [ ] All outbound HTTP calls have explicit `timeout=`
- [ ] TLS verification is not disabled
- [ ] Canonical/signed state files use atomic write + `os.replace`
- [ ] Remote fetches and archive extractions have size and traversal bounds
- [ ] Protocol timing uses epoch sequence numbers, not wall clock

---

## CLI Design Convention

All ILC CLI commands follow standard Unix CLI patterns. This applies to every
command surface in `ilc_core/cli/`, sidecar CLIs, and tool scripts.

1. **Hierarchy via subcommands, not flags.**
   `ilc sidecar graph-viz --summary` — not `ilc --sidecar=graph-viz --summary`

2. **Kebab-case for all multi-word names.**
   `graph-viz`, `--max-nodes`, `--core-only` — never camelCase or underscores
   in CLI-facing names (Python internals may use underscores).

3. **Three-level help hierarchy, always.**
   `ilc --help` → `ilc <command> --help` → `ilc <command> <subcommand> --help`

4. **Discovery via `list`, not `--help`.**
   External sidecars and plugins appear in `ilc sidecar list`.
   `--help` shows management commands only.

5. **`--flag` for options, positional args for primary inputs.**

6. **Short flags only for universally standard ones** (`-h`, `-v`, `-q`).

7. **Passthrough for external sidecars.** The top-level parser never consumes
   flags that belong to a sidecar's own CLI.

8. **Exit codes:** 0 = success, 1 = error, 2 = usage/argument error.

---

## `PUBLIC_RC_EXCLUDE` Header Convention

Files that are internal-only, investigative, diagnostic, or phase-specific
carry a header near the top:

```
# PUBLIC_RC_EXCLUDE: <reason_token>
# PUBLIC_RC_EXCLUDE_REASON: <brief explanation>
```

Files with this header are stripped from the sanitized public mirror automatically.
If you add a file that should not be in the public release, add this header in
the first 8 lines. Do not add it to files that should be public.

---

## Contributing

ILC follows a governance-first development model. Significant protocol changes
require a Constitutional Decision Log (CDL) or Architecture Decision Record (ADR)
before implementation.

- **ADRs** (`docs/adr/`) — architectural decisions with rationale and consequences
- **CDLs** (`docs/specs/ilc_constitutional_decision_log_v0.1.md`) — protocol
  parameter and governance decisions

For bug fixes and non-protocol improvements, open a pull request with:
1. A clear description of what changed and why
2. Tests covering the change
3. Confirmation that `python -m pytest` passes

For protocol changes, open an issue first to discuss the CDL/ADR path.

Contact: `ilcops@proton.me` | D2D: see `docs/contact/genesis_identity.json`
