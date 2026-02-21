# ILC ADM-002: CLI-First Agent SDK

**Status:** Proposed
**Date:** 2026-02-20
**CDL routing:** CDL-032
**Source analysis:** `docs/specs/ilc_openclaw_architecture_deep_dive_v0.1.md` (Section 3.4)
**Integration plan:** `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md` (Section 3)

---

## Decision

The ILC Agent SDK's primary interface is a command-line tool (`ilc`) that accepts structured input (JSON/flags) and returns structured output (JSON). All protocol operations are exposed as CLI commands. The CLI is the canonical integration surface — libraries, plugins, and framework-specific adapters are wrappers around the CLI semantics, not independent implementations.

---

## Depends on

- ADM-001 v0.2 (four-layer content-addressed distribution model)
- D2 (Protocol Bundle schemas — required for encoding)
- D2d (Wire Protocol — required for network operations)

D2e-03 through D2e-06 can begin with local-only operations before D2d is complete.

---

## Rationale

1. **Universal agent compatibility.** OpenClaw (150K+ stars), Claude Code, Codex, and virtually every AI agent framework can execute CLI tools natively. CLI-first means every agent can participate in ILC without custom integration code.

2. **The You.com precedent.** You.com built a CLI that takes JSON and returns JSON. OpenClaw integration was trivial — no custom adapter, no platform-specific logic.

3. **Skills ecosystem leverage.** A SKILL.md + CLI binary is the standard OpenClaw extension pattern. ILC becomes installable via ClawHub PR. 3,000+ existing skills prove the pattern works at scale.

4. **Clean boundary enforcement.** The CLI IS the SDK boundary contract. Everything inside is protocol internals. Everything outside is user-facing. No leaky abstractions.

5. **Language agnosticism.** The CLI can be Python (Genesis), then Rust (Phase B), then WASM (Phase C) — without changing the interface.

---

## CLI Command Surface

### Seven protocol primitives → seven commands

```
ilc assert    --claim "..." --shard <id> --evidence "..." --key <path>
ilc validate  --cid <claim-cid> --confidence <0-1> --key <path>
ilc contradict --cid <claim-cid> --counter "..." --key <path>
ilc refute    --cid <claim-cid> --proof "..." --key <path>
ilc revise    --cid <claim-cid> --revision "..." --key <path>
ilc link      --source <cid> --target <cid> --relation "..." --key <path>
ilc epoch     --commit | --status | --history
```

### Operational commands

```
ilc query     --shard <id> [--unvalidated] [--refutable] [--min-bounty <n>]
ilc verify    --claim "..." --shard <id>
ilc balance   --agent <cid> | --self
ilc identity  --init | --export | --info
ilc bundle    --verify <cid> | --info
ilc shard     --list | --info <id> | --join <id> | --leave <id>
ilc capproof  --run | --status | --history
ilc config    --get <key> | --set <key> <value>
```

---

## I/O Contract

- **Input:** CLI flags for simple cases; JSON on stdin for complex payloads
- **Output:** JSON on stdout (structured, parseable by any agent)
- **Errors:** JSON on stderr with error codes
- **Exit codes:** 0 success, 1 protocol error, 2 usage error, 3 network error

---

## What this is NOT

- Not a daemon or server
- Not a library API
- Not transport-specific
- Not framework-specific (OpenClaw is a distribution channel, not a dependency)

---

## Roadmap phase

This decision is implemented in **Phase D2e — Agent SDK / CLI** (11 tasks: D2e-01 through D2e-11).

D2e sits between D2d (Wire Protocol) and D3 (OpenClaw integration) in the dependency graph:

```
D2 → D2d → D2e → D3
```

---

## CDL routing

**CDL-032:** "CLI-first Agent SDK interface contract and command surface."

Ratification of this ADM requires CDL-032 closure with:
- Full command surface specification
- I/O contract schema per command
- Signed boundary contract

---

## Security constraints

- Key material (`--key <path>`) must never appear in JSONL transcripts or agent memory files
- Use environment variables (`ILC_KEY_PATH`) for key paths, not inline values
- All network operations require explicit signing confirmation
- CLI validates all inputs and never trusts ambient environment state
- Economic actions (assert with stake, refute) require explicit approval flag

---

## References

- `docs/specs/ilc_openclaw_architecture_deep_dive_v0.1.md` — source analysis (Section 3.4)
- `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md` — roadmap D2e, D3 amendments
- `docs/specs/ilc_distribution_architecture_roadmap_v0.2.md` — roadmap phases D1-D5
- `docs/specs/ilc_antigravity_context_capsule_v0.2.md` — project context
