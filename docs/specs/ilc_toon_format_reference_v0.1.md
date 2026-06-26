# TOON Format Reference Pointer

**Version:** v0.1
**Date:** 2026-06-26
**Purpose:** Discovery pointer for the TOON format used in ILC agent hydration
capsules and internal documents. Not a spec — the upstream package is authoritative.

---

## What TOON Is

**Token-Oriented Object Notation (TOON)** is a compact, human-readable
serialization format optimized for LLM contexts. It achieves 30–60% token
reduction versus JSON while maintaining readability and structure. TOON is
used in ILC for agent hydration capsules, internal orientation documents, and
any structured document where token efficiency matters for LLM ingestion.

TOON is semantically equivalent to JSON — every TOON document can be decoded
to a JSON-compatible structure and vice versa.

## Where to Find It in This Repo

The TOON format Python package is installed in the project virtualenv:

| Location | Contents |
|---|---|
| `.venv/bin/toon` | CLI: convert between JSON and TOON formats |
| `.venv/lib/python3.14/site-packages/toon_format/` | Python package source |
| `.venv/lib/python3.14/site-packages/toon_format/__init__.py` | Package init, version, usage examples |
| `.venv/lib/python3.14/site-packages/toon_format-0.9.0b1.dist-info/` | Package metadata |

**Package version:** `toon_format==0.9.0b1` (implements TOON spec v1.3)
**License:** MIT

## Quick Usage

```bash
# Decode a TOON document to JSON
.venv/bin/toon -d < input.toon

# Encode JSON to TOON
.venv/bin/toon -e < input.json

# Validate a fenced TOON block in a markdown file
.venv/bin/toon -d <<'EOF'
name: Alice
age: 30
tags: [admin, reviewer]
EOF
```

```python
from toon_format import encode, decode

data = {"name": "Alice", "age": 30}
toon = encode(data)        # → "name: Alice\nage: 30"
decoded = decode(toon)     # → {"name": "Alice", "age": 30}
```

## Where TOON Is Used in This Repo

- `docs/research/ilc_technical_genesis_v0.1.md` — TOON-first agent hydration
  capsule; the primary example of TOON usage in ILC documents
- Any internal document with fenced ` ```toon ``` ` blocks

## Why Not JSON or YAML

TOON was chosen over JSON for agent hydration capsules because:

- **Token efficiency** — 30–60% fewer tokens than JSON for the same structured
  data; critical for large context hydration documents
- **Human readability** — no quotes around keys, no trailing commas, clean
  indentation; closer to YAML but with stricter semantics
- **LLM-native** — designed specifically for LLM ingestion contexts, not
  general-purpose serialization

YAML was not chosen because YAML's implicit type coercion and ambiguous
multi-document semantics introduce parsing hazards in automated pipelines.

## MemPalace / Search Discovery

Search terms that will find this document:
`TOON`, `Token-Oriented Object Notation`, `toon_format`, `agent hydration`,
`token reduction`, `.venv/bin/toon`
