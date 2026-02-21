# OpenClaw Findings Integration Plan v0.3

**Date:** 2026-02-20  
**From:** Claude Opus 4.6 (Strategic Architectural Reviewer)  
**Revision history:**  
- v0.1 (2026-02-20): Initial integration plan  
- v0.2 (2026-02-20): Corrected ClawHub guidance (PR-based, not self-service). Added Codex instructions  
- v0.3 (2026-02-20): Revised to reflect actual Phase 228-233 execution. Corrected CDL numbering (CDL-025-031 now claimed by issuance governance; SDK/OpenClaw renumbered to CDL-032/033). Re-sequenced all Codex instructions for Phase 234+  

**Companion document:** `ilc_openclaw_architecture_deep_dive_v0.1.md` (the research — unchanged)  
**Purpose:** Map each actionable finding from the OpenClaw Architecture Deep Dive to a specific document, roadmap phase, and action. No finding should be floating — everything gets a home.

---

## 1. Current Project State (Post-Phase 233)

### What Phases 228-233 Actually Accomplished

| Phase | Title | Key Output |
|---|---|---|
| 228 | Genesis Release Artifact Packaging | Wheel + sdist built, SHA-256 provenance captured, clean-venv install validated |
| 229 | Genesis Packaging Closure 222-228 | Composed closure gate (4 sub-gates), handoff artifact, provenance supplement. CDL-001/002/007 remain open |
| 230 | CapProof Activation Readiness Sequence Lock + D1 Reproducibility | 230-239 sequence locked, SOURCE_DATE_EPOCH=0 pinned, rebuild gate script, backend decision (keep setuptools). CDL-019 confirmed open |
| 231 | CapProof Activation Readiness Contract Lock | Gate A criteria locked, AWP/IIH deferred to Gate C, QATPS/CIT deferred to Gate E. Glossary anchored |
| 232 | Security Runtime Implementation Plan Lock | CDL-001/002/007 implementation sequence locked with dependency ordering, per-CDL risk/rollback plans |
| 233 | Issuance Governance Plan Lock | CDL-019 three-component analysis, hard cap vs tail emission reconciliation (Model B recommended), **CDL-025 through CDL-031 queue mapping for issuance/governance topics** |

### Key State Facts

- **Next phase:** 234 (not yet scoped)
- **No ilc_core/ runtime changes since before Phase 228.** The entire 228-233 arc is documentation, plan locks, and contract locks. This is the "plan everything before building anything" posture — correct for this stage.
- **CDL-001, CDL-002, CDL-007:** Remain `open`. Security implementation plan is locked (Phase 232) but not yet executed.
- **CDL-019:** `open`. Issuance governance plan locked (Phase 233) with three-component analysis and queue mapping.
- **CDL-025 through CDL-031:** Proposed in Phase 233 for issuance/governance topics. **These numbers are now claimed.**
- **OpenClaw integration artifacts:** Not yet committed to repo. No integration plan actions have been executed yet.

### CDL Numbering Update

The v0.2 integration plan proposed CDL-025 for CLI-first SDK and CDL-026 for OpenClaw skill. Phase 233 independently claimed CDL-025 through CDL-031 for issuance/governance. The correct renumbering:

| v0.2 Proposed | v0.3 Corrected | Subject |
|---|---|---|
| CDL-025 | **CDL-032** | CLI-first Agent SDK interface contract and command surface (ADM-002) |
| CDL-026 | **CDL-033** | OpenClaw skill specification and ClawHub publication contract |

All references below use the corrected numbers.

---

## 2. What Changes and Where

### Summary Matrix (Updated)

| Finding | Action | Document | Phase | Priority |
|---|---|---|---|---|
| CLI-first SDK is the integration key | New architectural decision + new roadmap phase | ADM-002 + Roadmap v0.3 | New Phase D2e | **CRITICAL** |
| ILC SKILL.md for OpenClaw | New tasks in D3 | Roadmap v0.3 (D3 amendment) | D3 | HIGH |
| SKILL.md format for Antigravity prompts | Workflow improvement | Capsule v0.3 + standing guidance | Phase 234+ | MEDIUM |
| ClawHub publication | New task in D3 | Roadmap v0.3 (D3 amendment) | D3 (requires working CLI first) | HIGH |
| OpenClaw foundation engagement | Strategic action item | Go-to-market doc (new) | Pre-Phase-B | MEDIUM |
| Agent Edition launch timing | Go-to-market coordination | Go-to-market doc (new) | Aligned with D3 | HIGH |
| Gateway pattern → ILC Coordinator | Design input for D2d/D2e | ADM-002 | D2e | HIGH |
| Epoch lifecycle hooks | New tasks in D2d | Roadmap v0.3 (D2d amendment) | D2d | MEDIUM |
| CapProof via OpenClaw nodes | New task in D3 | Roadmap v0.3 (D3 amendment) | D3 | LOW |
| Semantic snapshots → graph state | Design input for D2c | Note in D2c tasks | D2c | LOW |
| TypeBox → schema validation pattern | Design input for D2 | Note in D2 tasks | D2 | LOW |
| Security considerations for ILC skill | Constraints in D3 + D2e | Roadmap v0.3 | D3/D2e | MEDIUM |

---

## 3. Architectural Decision: ADM-002 (CLI-First Agent SDK)

*Unchanged from v0.2. Reproduced here for completeness.*

### ADM-002: CLI-First Agent SDK

**Status:** Proposed (requires CDL routing as **CDL-032**)  
**Depends on:** ADM-001 v0.2 (four-layer distribution), D2 (Protocol Bundle schemas), D2d (Wire Protocol)  
**Triggered by:** OpenClaw architecture analysis finding that CLI-first design is the universal agent integration surface

#### Decision

The ILC Agent SDK's primary interface is a command-line tool (`ilc`) that accepts structured input (JSON/flags) and returns structured output (JSON). All protocol operations are exposed as CLI commands. The CLI is the canonical integration surface — libraries, plugins, and framework-specific adapters are wrappers around the CLI semantics, not independent implementations.

#### Rationale

1. **Universal agent compatibility.** OpenClaw (150K+ stars), Claude Code, Codex, and virtually every AI agent framework can execute CLI tools natively. CLI-first means every agent can participate in ILC without custom integration code.

2. **The You.com precedent.** You.com built a CLI that takes JSON and returns JSON. OpenClaw integration was trivial — no custom adapter, no platform-specific logic.

3. **Skills ecosystem leverage.** A SKILL.md + CLI binary is the standard OpenClaw extension pattern. ILC becomes installable via ClawHub PR. 3,000+ existing skills prove the pattern works at scale.

4. **Clean boundary enforcement.** The CLI IS the SDK boundary contract. Everything inside is protocol internals. Everything outside is user-facing. No leaky abstractions.

5. **Language agnosticism.** The CLI can be Python (Genesis), then Rust (Phase B), then WASM (Phase C) — without changing the interface.

#### CLI Command Surface (Draft)

**Seven primitives → seven commands:**

```
ilc assert    --claim "..." --shard <id> --evidence "..." --key <path>
ilc validate  --cid <claim-cid> --confidence <0-1> --key <path>
ilc contradict --cid <claim-cid> --counter "..." --key <path>
ilc refute    --cid <claim-cid> --proof "..." --key <path>
ilc revise    --cid <claim-cid> --revision "..." --key <path>
ilc link      --source <cid> --target <cid> --relation "..." --key <path>
ilc epoch     --commit | --status | --history
```

**Operational commands:**

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

**I/O contract:**
- Input: CLI flags for simple cases, JSON on stdin for complex payloads
- Output: JSON on stdout (structured, parseable by any agent)
- Errors: JSON on stderr with error codes
- Exit codes: 0 success, 1 protocol error, 2 usage error, 3 network error

**What this is NOT:** Not a daemon/server. Not a library API. Not transport-specific.

#### CDL Routing

**CDL-032** "CLI-first Agent SDK interface contract and command surface."

---

## 4. Roadmap v0.3 Amendments

### New Phase: D2e — Agent SDK / CLI

*Unchanged from v0.2 except CDL reference corrected.*

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| D2e-01 | Ratify CLI command surface | ADM-002 ratification as **CDL-032** | All seven primitive commands + operational commands specified. I/O contract defined |
| D2e-02 | Define CLI output schemas | JSON schema spec per command | Every command has documented JSON output schema including error formats |
| D2e-03 | Build Python CLI prototype | `ilc` CLI entry point wrapping Genesis codebase | All seven primitive commands functional against local graph. JSON output. Signing works |
| D2e-04 | Build `ilc identity` subsystem | Key generation and management | `ilc identity --init` creates COSE keypair. `--export` portable format. `--info` shows agent CID |
| D2e-05 | Build `ilc query` subsystem | Graph query interface | Filter by shard, validation status, refutation bounty, freshness. JSON output with CIDs |
| D2e-06 | Build `ilc verify` subsystem | Cross-reference interface | Agent submits claim, CLI checks graph for matches/contradictions. Returns confidence signal |
| D2e-07 | Build `ilc bundle` subsystem | Bundle operations | Verify protocol bundle by CID. Display bundle info. Validate local state against bundle |
| D2e-08 | Build `ilc epoch` subsystem | Epoch operations | Current epoch status, commit participation, view history, reward projections |
| D2e-09 | Build `ilc balance` subsystem | Economic operations | ILC balance, vesting schedule, staking status, reward history |
| D2e-10 | End-to-end CLI integration test | Test suite | Full workflow: init identity → join shard → assert → validate → refute → check balance. All via CLI |
| D2e-11 | CLI man page and --help | Documentation | Every command has comprehensive `--help`. Man page generated from help text |

**Exit criteria:** A developer (or agent) with only the `ilc` CLI binary can perform every protocol operation.

**Dependencies:** D2 (schemas for encoding), D2d (wire protocol for network operations). D2e-03 through D2e-06 can start with local-only operations before D2d is complete.

**CDL routing:** CDL-032

---

### D3 Amendments (OpenClaw Integration — expanded from 8 to 13 tasks)

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| **D3-09** | **Write ILC SKILL.md for OpenClaw** | `skills/ilc/SKILL.md` | Complete skill definition following `openclaw/skills` CONTRIBUTING.md conventions |
| **D3-10** | **Package ILC CLI as skill binary** | `skills/ilc/bins/ilc` | CLI binary bundled. Auto-added to agent PATH. macOS + Linux |
| **D3-11** | **Write skill.json with environment config** | `skills/ilc/skill.json` | Dependencies, env vars (ILC_KEY_PATH, ILC_ENDPOINT, ILC_SHARD), platform install instructions |
| **D3-12** | **Submit ILC skill PR to `openclaw/skills` repo** | Merged PR in official skills repo | Follows CONTRIBUTING.md. Working CLI included. PR passes review |
| **D3-13** | **Build reference multi-agent ILC mining config** | OpenClaw config + workspace files | 3 agents (asserter, validator, refuter), separate workspaces, heartbeat-driven mining |

**D3-09 depends on D2e-03** (working CLI).  
**D3-12 depends on D3-09 + D3-10 + working CLI** (complete, tested skill for PR).  
**D3-13 depends on D3-12.**

**CDL routing:** CDL-033

---

### D2d Amendments (Wire Protocol — add 2 tasks)

| Task ID | Task | Deliverable | Acceptance criteria |
|---------|------|-------------|-------------------|
| **D2d-10** | **Define epoch lifecycle event schema** | Wire protocol spec section | Events: epoch-start, claim-finalized, refutation-occurred, reward-vested, epoch-end |
| **D2d-11** | **Define subscription/notification protocol** | Wire protocol spec section | Agent event subscriptions (per-shard, per-claim). Push vs poll. Filtering. Delivery guarantees |

---

### Updated Dependency Graph

```
D1 (Genesis reproducibility)  [DONE - Phase 230]
  |
  v
D2 (Protocol Bundle + full type system) ─────────────────┐
  |                                                        |
  +──> D2b (Genesis State Bundle)                          |
  |       |                                                |
  |       +──> D3 (OpenClaw integration) ◄── D2e (SDK/CLI) |
  |                                                        |
  +──> D2d (Wire Protocol + lifecycle events)              |
  |       |                                                |
  |       +──> D2e (Agent SDK / CLI) ◄── depends on D2d   |
  |                                                        |
  +──> D2c (Epoch Snapshots) ←── depends on D2 + network  |
  |                                                        |
  v                                                        |
D4 (Rust kernel) ── triggered by Phase B milestones ───────┘
  |
  v
D5 (Python retirement) ── triggered by Phase C stability
```

**Critical path:** D1 → D2 → D2d → D2e → D3  
**New total:** 73 + 18 = **91 tasks** (unchanged from v0.2; only CDL numbers changed)

---

### Updated CDL Routing Summary

| CDL | Subject | Layer | Status |
|---|---|---|---|
| CDL-019 | Multiplier-governance surface unification | 0 | `open` (Phase 233 analysis complete) |
| CDL-020 | Protocol-native bundle schema and complete type system | 0 | `proposed` |
| CDL-021 | Rust kernel port and WASM distribution | 0 | `proposed` |
| CDL-022 | Genesis state bundle specification and signing ceremony | 1 | `proposed` |
| CDL-023 | Epoch snapshot mechanism and fast-bootstrap protocol | 2 | `proposed` |
| CDL-024 | Wire protocol specification and transport bindings | 3 | `proposed` |
| CDL-025–031 | Issuance/governance topics (per Phase 233 queue mapping) | 0 | `proposed` |
| **CDL-032** | **CLI-first Agent SDK interface contract (ADM-002)** | 3 | **`proposed`** |
| **CDL-033** | **OpenClaw skill specification and ClawHub publication** | 3 | **`proposed`** |

---

## 5. Immediate Actions (Post-Phase 233)

Two things that should happen soon, plus pre-work for a third:

### 5.1 Prepare ClawHub Skill Submission (Pre-work — Execute When CLI Exists)

**Constraint:** ClawHub skills must be submitted as PRs to `github.com/openclaw/skills`. No placeholder skills, no personal repos. The skill must follow the Agent Skill convention and pass review. We CANNOT register until we have a working CLI binary (D2e-03).

**What to do now (pre-work):**
- Star and watch `github.com/openclaw/skills`
- Read their `CONTRIBUTING.md` and formatting guidelines
- Verify the SKILL.md draft from the deep dive (Section 4.2) conforms to their conventions
- Prepare the full skill directory structure so it's ready to submit the day the CLI prototype works

**What to do when D2e-03 is functional:**
- Build `ilc` CLI binary for macOS and Linux
- Finalize SKILL.md with working examples tested against real CLI output
- Submit PR to `github.com/openclaw/skills` same-day

### 5.2 Adopt SKILL.md Frontmatter for Antigravity Prompts

Starting with the next prompt Codex drafts, add YAML frontmatter:

```yaml
---
name: ilc-phase-NNN
description: [phase description]
requires: [list of input files]
sensitivity:
  - [sensitivity items]
boundary: "[phase boundary statement]"
---
```

Additive — doesn't break existing prompt structure. Makes prompts machine-parseable and ecosystem-compatible.

### 5.3 Decide Agent Edition Launch Timing

The OpenClaw community is at peak attention (150K stars, Steinberger joining OpenAI, foundation forming). The cultural moment is now.

**Options:**
- **A: Wait for working CLI.** Honest but slow.
- **B: Launch whitepaper + placeholder.** Can't do — ClawHub doesn't accept placeholders.
- **C: Launch whitepaper independently. Skill follows when CLI lands.** Two distinct moments, each with own impact.

**Recommendation: Option C.** The Agent Edition whitepaper stands on its own. When the CLI lands, the ClawHub skill submission is a second wave. One editing pass on v0.2 before it goes public — tighten, cut, sharpen.

---

## 6. Document Updates Required

| Document | Update | Who | When |
|---|---|---|---|
| `ilc_distribution_architecture_roadmap_v0.2.md` | Amend to v0.3: add D2e (11 tasks), expand D3 (+5), expand D2d (+2), update deps and counts | Codex | Phase 234 or 235 |
| `ilc_antigravity_context_capsule_v0.2.md` | v0.3: add SDK/CLI architecture (ADM-002), OpenClaw integration surface | Opus or Codex | Next capsule update |
| `TODO.txt` | Add D2e block, updated D3/D2d tasks, corrected CDL numbers | Codex | Phase 234 or 235 |
| CDL file | Add CDL-032 and CDL-033 as `proposed` entries | Codex | When roadmap v0.3 is committed |
| **NEW:** `ilc_adm_002_cli_first_agent_sdk_v0.1.md` | Formal ADM from Section 3 of this document | Codex | With roadmap v0.3 |
| **NEW:** `ilc_go_to_market_strategy_v0.1.md` | Agent Edition timing, ClawHub strategy, community engagement | Jamie + Opus | When Jamie decides on timing |

---

## 7. What NOT to Do

- **Don't build the CLI before D2 schemas are at least drafted.** Schema-first, CLI-second.
- **Don't make OpenClaw a dependency.** The CLI works standalone. SKILL.md is a distribution channel.
- **Don't let OpenClaw integration disrupt the 230-239 CapProof sequence.** The sequence lock exists for a reason. Integration work belongs in the D-series roadmap, which runs parallel to the main-track phases.
- **Don't build the multi-agent mining config (D3-13) before the single-agent skill works (D3-09).**
- **Don't announce on agent social media before the Agent Edition is polished.** v0.2 is strong but working draft — one editing pass before public.
- **Don't use CDL-025 or CDL-026 for SDK/OpenClaw.** Those numbers are claimed by Phase 233's issuance governance queue. Use CDL-032/033.

---

## 8. Revised Phase Sequencing (Big Picture — Post-Phase 233)

```
CURRENT: Phase 233 complete. Issuance governance plan locked. Next: Phase 234.

Phase 234-239: Remaining CapProof activation readiness sequence
    (230-239 sequence lock in effect)
    └── Phase 234-235 window: commit OpenClaw artifacts to docs/specs/
    └── Phase 234-235 window: amend roadmap to v0.3, create ADM-002
    └── Phase 234-235 window: update TODO.txt with D2e/D3/D2d additions
    
Phase 240+: CDL implementation begins
    └── CDL-001/002/007 security runtime (per Phase 232 plan)
    └── CDL-019 multiplier-governance (per Phase 233 plan)
    └── CDL-025-031 issuance parameters (per Phase 233 queue)

Post-CDL implementation: D-series roadmap
    └── D2 (Protocol Bundle schemas)
    └── D2d (Wire Protocol) + D2e (CLI) — can overlap
    └── D2b (Genesis State Bundle) — parallel with D2d
    └── D3 (OpenClaw integration) — after D2e-03 CLI prototype
    └── D2c (Epoch Snapshots) — after running network

Phase B trigger (≥50 agents, ≥10 operators):
    └── D4 (Rust kernel)
    └── D3-13 (multi-agent mining config) becomes practical

Go-to-market:
    └── Agent Edition whitepaper: can launch independently (Option C)
    └── ClawHub skill PR: when D2e-03 is functional
    └── OpenClaw foundation engagement: when foundation governance forms
```

The OpenClaw integration (D3) doesn't gate Genesis launch. It gates Phase A → Phase B growth. The critical path for Genesis remains: CDL implementation → issuance ratification → whitepaper release.

---

## 9. Codex Implementation Instructions (Revised for Post-Phase 233)

### Phase 228-233 Review Acknowledgment

Phases 228-233 represent a coherent "plan everything before building anything" arc:

- **228-229:** Genesis packaging closed ✅
- **230-231:** CapProof activation readiness baselined ✅
- **232:** Security CDL implementation sequenced ✅
- **233:** Issuance governance planned with CDL queue mapping ✅

This is the correct posture. No ilc_core/ runtime changes, no CDL status mutations — just rigorous plan locks and contract locks. The integration plan respects this pattern and does NOT propose any runtime changes.

### Step 1: Read and Acknowledge (Immediate)

Codex should read this full document and the companion `ilc_openclaw_architecture_deep_dive_v0.1.md`. The goal is context absorption.

**Codex deliverable:** Brief acknowledgment noting any concerns about ADM-002, the D2e phase, or CDL-032/033 numbering. If Codex sees conflicts with Phase 233's CDL-025-031 queue or the 230-239 sequence lock, flag them before anything is committed.

**Critical check:** Confirm CDL-025 through CDL-031 are indeed claimed by the issuance governance plan. If those numbers are only "placeholder" suggestions in Phase 233 and haven't been formally written into the CDL file, Codex should clarify the actual state.

### Step 2: Determine Integration Window (Phase 234 Scoping)

The OpenClaw integration artifacts are pure documentation — they don't change ilc_core/, don't mutate CDL status, and don't break the 230-239 sequence lock. They can be committed as housekeeping in any upcoming phase.

**Recommended approach:** Include OpenClaw artifact commits as a Group B (housekeeping) item in either Phase 234 or 235, alongside whatever the primary mission of that phase is. This mirrors how Phase 230 handled D1 reproducibility alongside the CapProof sequence lock.

**What gets committed:**

| File | Repo location | Nature |
|---|---|---|
| `ilc_openclaw_architecture_deep_dive_v0.1.md` | `docs/specs/` | Non-normative reference |
| `ilc_openclaw_findings_integration_plan_v0.3.md` | `docs/specs/` | Non-normative planning artifact |
| `ilc_adm_002_cli_first_agent_sdk_v0.1.md` | `docs/specs/` | Proposed ADM (not ratified) |

These are reference documents. Their presence in the repo does NOT trigger any implementation work.

### Step 3: Amend Roadmap and TODO (Phase 234 or 235)

When the primary-mission workload permits, amend:

**3a. Roadmap v0.2 → v0.3:**
- Add Phase D2e (Agent SDK / CLI) — 11 tasks per Section 4
- Add 5 new tasks to D3 (D3-09 through D3-13) per Section 4
- Add 2 new tasks to D2d (D2d-10, D2d-11) per Section 4
- Update dependency graph (D2e sits between D2d and D3)
- Update task count (73 → 91)
- Update CDL routing summary (add CDL-032, CDL-033)
- **Verify no conflicts with Phase 233's CDL-025-031 queue**

**3b. TODO.txt:**
- Add D2e task block (11 tasks) under "Post-Genesis — Agent SDK / CLI"
- Add new D3 tasks under existing D3 block
- Add new D2d tasks under existing D2d block
- Note dependency: D3-09+ depends on D2e-03

**3c. CDL file:**
- Add CDL-032 (`proposed`): CLI-first Agent SDK interface contract
- Add CDL-033 (`proposed`): OpenClaw skill specification and ClawHub publication
- **Do NOT modify CDL-025-031 entries** (those belong to Phase 233's issuance queue)

### Step 4: Adopt SKILL.md Frontmatter (Next Prompt After Commitment)

Starting with the first Antigravity prompt AFTER the OpenClaw artifacts are committed, add YAML frontmatter:

```yaml
---
name: ilc-phase-NNN
description: [phase description]
requires: [list of input files]
sensitivity:
  - [sensitivity items]
boundary: "[phase boundary statement]"
---
```

This is additive and backwards-compatible. If the prompt validator needs updating to accept the frontmatter, that's a one-line regex change.

### Step 5: Update Context Capsule

The Antigravity context capsule needs a v0.3 update. Add:

**New section: SDK/CLI Architecture**
- ADM-002 summary: CLI-first design, `ilc` command surface, JSON I/O
- D2e sits between D2d and D3 in dependency graph
- Constraint: CLI is canonical interface; libraries wrap CLI semantics

**New section: OpenClaw Integration Model**
- Three levels (skill → plugin → dedicated agent)
- SKILL.md + CLI binary is primary integration pattern
- ClawHub requires PR to official repo with working skill
- Security: key material never in logs, sandbox execution, explicit signing

### Step 6: Prepare ClawHub Infrastructure (When Convenient)

Non-blocking, can happen in any phase:
- Create `skills/ilc/` directory in ILC repo as staging area
- Add README explaining it's the staging area for the `openclaw/skills` PR
- Note: "Skill will be submitted when ILC CLI (D2e-03) is functional"

### Step 7: Route to Sonnet/Antigravity for Review Awareness

When the next review assignment goes out, include:

> "ADM-002 (CLI-first Agent SDK) has been proposed as CDL-032. When reviewing D2d (Wire Protocol) tasks, verify wire protocol is compatible with CLI-first consumption (stateless per-invocation, JSON I/O, no long-lived connections required for basic operations). When reviewing D3 (OpenClaw integration) tasks, verify skill specification references actual CLI command surface. Flag any D3 work that begins before D2e-03 (CLI prototype) exists. Note: CDL-025 through CDL-031 are claimed by Phase 233's issuance governance queue — do not reuse these numbers."

---

### Summary: Codex Action Timeline (Revised)

| When | What | Scope |
|---|---|---|
| **Now** | Read this document + deep dive. Acknowledge. Confirm CDL-025-031 numbering state | Context only |
| **Phase 234 or 235** | Commit OpenClaw artifacts to `docs/specs/` (Step 2). Amend roadmap to v0.3 (Step 3a). Update TODO (Step 3b). Add CDL-032/033 (Step 3c). Create ADM-002 doc (Step 2) | Documentation housekeeping |
| **Phase 234+ (first prompt after commit)** | Adopt SKILL.md frontmatter for prompts (Step 4) | Workflow improvement |
| **Next capsule update** | Update capsule to v0.3 with SDK/CLI + OpenClaw sections (Step 5) | Context maintenance |
| **When convenient** | Prepare ClawHub staging area (Step 6). Route to Sonnet (Step 7) | Housekeeping |
| **D2e phase (future)** | CLI implementation begins — execution phase for ADM-002 | Implementation |
| **D2e-03 complete** | Submit ClawHub PR same-day (D3-12) | Go-to-market |

### Key Guardrails for Codex

1. **Do NOT disrupt the 230-239 sequence lock.** The OpenClaw artifacts are documentation housekeeping, not a new work stream.
2. **Do NOT use CDL-025 or CDL-026 for SDK/OpenClaw.** Those numbers belong to Phase 233's issuance queue. Use CDL-032/033.
3. **Do NOT begin D2e implementation until D2 schemas are at least drafted.** Schema-first, CLI-second.
4. **Do NOT make any ilc_core/ changes as part of this integration.** The current plan-lock posture is correct.
5. **The Agent Edition whitepaper is a Jamie strategic decision, not a Codex task.** Codex should not publish or announce anything without Jamie's explicit go-ahead.

---

*End of integration plan v0.3. This document is ready for Codex consumption. Jamie can share it along with the OpenClaw Architecture Deep Dive as a package. All Codex actions are documentation-only and respect the current plan-lock posture established by Phases 228-233.*
