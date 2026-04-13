# ILC Machine Migration & Environment Recovery Handoff
**Date:** 2026-04-08  
**Prepared by:** Claude Code (local reviewer)  
**For:** Codex  
**Working directory:** `/Users/jamison/Documents/ILC_Main/01_Current`

---

## 1. What Happened

### Primary incident
On 2026-04-07/08, the external SSD suffered simultaneous file-pointer corruption in both the active working partition (`ExternalSSD-System`, Sealed: Broken) and the TimeCapsule backup. The result was total loss of the bootable Sonoma environment and the working `jamstar` admin user account.

Full incident log and recovery steps: `/Users/jamison/Downloads/iMac_Recovery_and_Migration_Log.md`

### Resolution
A fresh macOS Sequoia install was created on a 4th APFS partition (`SonomaTemp`) on the same external SSD. OCLP root patches were applied for Nvidia GPU support. All relevant files were manually copied from the intact data volume (`/Volumes/ExternalSSD - Data/Users/jamstar/`).

### Username change
| Item | Old | New |
|---|---|---|
| Username | `jamstar` | `jamison` |
| Home directory | `/Users/jamstar/` | `/Users/jamison/` |
| Symlink (created) | `/Users/jamstar → /Users/jamison` | covers all hardcoded paths |

---

## 2. Environment Recovery — What Was Done

### Python venv (REBUILT)
The old `.venv` used Python 3.13 (from a framework install that no longer exists on this machine). It was deleted and rebuilt:

```bash
rm -rf .venv
/usr/local/bin/python3.14 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

**New venv:** Python 3.14.3 (Homebrew `/usr/local/bin/python3.14`)  
**Editable install:** `ilc-core 0.1.0` — confirmed `import ilc_core` works.

**How to run tests:**
```bash
PATH=.venv/bin:$PATH .venv/bin/pytest tests/ --tb=short -q
```
Note: `PATH=.venv/bin:$PATH` is required so that subprocess calls within tests (which use bare `python3`) find the venv Python with all dependencies installed.

### pyproject.toml (MODIFIED)
Added `[tool.pytest.ini_options]` section so targeted single-file pytest invocations can import the `tools/` namespace package:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

This was missing — running `pytest tests/test_agent_loop_v1_runtime.py` alone would fail with `ModuleNotFoundError: No module named 'tools'`. Full suite run (`pytest tests/`) was unaffected. **This change is uncommitted** — it is in the working tree as a modified file and should be committed as part of the next phase or a standalone chore commit.

### Git config (REBUILT)
No `~/.gitconfig` existed on the new partition. Recreated:
```bash
git config --global user.name "Genesis Agent"
git config --global user.email "ilcops@proton.me"
git config --global color.ui auto
```

### SSH config (MODIFIED)
`~/.ssh/config` updated to add `UseKeychain yes` and `AddKeysToAgent yes` to all three hosts, so passphrase is stored in macOS Keychain after first entry:

```
Host github-ilc-core   # GitHub deploy key for ilc-core repo
Host ilc-node-2        # 100.109.27.59 (Tailscale)
Host ilc-node-3        # 100.108.3.57 (Tailscale)
```

SSH key for `github-ilc-core` has been added to Keychain — `ssh -T git@github-ilc-core` now authenticates without passphrase prompt.

### Claude Code permissions (REBUILT)
`~/.claude/settings.json` was rebuilt with broad permissions replacing the old granular allow-list:
```json
{
  "permissions": {
    "allow": ["Bash(*)", "Read(*)", "Edit(*)", "Write(*)", "WebFetch(domain:...)"],
    "additionalDirectories": ["/Users/jamison/Downloads", "/Users/jamstar/Downloads", "/tmp", "/Users/jamison/.ssh", "/Volumes/ExternalSSD - Data/Users/jamstar"]
  }
}
```

### Codex files
Codex state, session history, auth, config, skills, and shell snapshots were all copied from the old partition. Full session history (164MB SQLite) is present.

### Tailscale
Both ILC testbed nodes are reachable:
- `ilc-node-2`: 100.109.27.59 — ping OK (~195ms)
- `ilc-node-3`: 100.108.3.57 — ping OK (~78ms)

---

## 3. Critical Issue Found and Fixed — Mutation Canary Mid-Crash State

### What was found
When the disk crashed, the mutation canary (`tools/run_mutation_canary_phase_297.py`) was mid-execution. This tool works by:
1. Staging sentinel mutation values into source files (e.g. `v9.9` instead of `v0.1`)
2. Running a targeted test to confirm the dep-chain assertion fires
3. Restoring the file to its original content

The crash happened after step 1 but before step 3. Five sentinel mutations were frozen in the git staging area and working tree:

| File | Constant | Wrong value | Correct value |
|---|---|---|---|
| `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` | `CDL_060_GOSSIP_RUNTIME_VERSION` | `v9.9` | `v0.1` |
| `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` | `D2D_GOSSIP_DEPENDENCY` | `d2d_gossip_999.v0.1` | `d2d_gossip_382.v0.1` |
| `ilc_core/network/d2d/gossip_transport.py` | `GOSSIP_TRANSPORT_RUNTIME_VERSION` | `v9.9` | `v0.1` |
| `ilc_core/network/d2d/gossip_transport.py` | `CDL_061_DEPENDENCY` | `cdl_061_ratified_999.v0.1` | `cdl_061_ratified_561.v0.1` |
| `ilc_core/network/d2d/gossip_transport.py` | `FORBIDDEN_HEADER_KEYS` entry | `"REMOVED_FOR_MUTATION"` | `"creator_agent_id"` |

### Why it kept reverting
Antigravity (VS Code) had these files open in editor tabs with the old mutated buffer content. Every time a write was applied via tool, VS Code auto-saved its buffer back to disk within ~1 second, reverting the fix. The fix was applied by manually editing the correct values in Antigravity and saving — after which the values became stable.

### Resolution
All 5 values manually corrected in Antigravity and saved. Both files unstaged (`git reset HEAD`). All pycache cleared. Files now match HEAD exactly.

### Also fixed: context pack misplaced in `docs/context_packs/`
`docs/context_packs/ilc_rc_gap_context_pack_v0.1.md` was an untracked file copied from the old partition. It contains `...` ellipses (it's a research/dredge artifact, not a walkthrough). The `test_no_ellipses_in_walkthroughs` test scans `docs/context_packs/` and was failing because of this file. Fixed by moving it to `docs/research/` where it belongs.

---

## 4. Test Suite Status Post-Recovery

**Run command:**
```bash
PATH=.venv/bin:$PATH .venv/bin/pytest tests/ --tb=no -q
```

**Result (final full run, 2026-04-08):**

| Category | Count |
|---|---|
| Passed | 4,639 |
| Skipped | 5 (intentional selftest guards) |
| Failed — migration-introduced | 0 |
| Failed — pre-existing debt | 28 + 1 (see below) |

### Pre-existing failures (NOT introduced by migration)

**28 failures — missed historicalization in Windows 515-524, 535-544, 545-554:**

The closure gate tests for these three windows check CDL inventory state ("no CDL above 060", "CDL-059 not present") using live reads of the CDL. These checks were designed to be historicalized when later CDLs opened (CDL-059 in Window 525+, CDL-061 in Window 555+). The historicalization was never performed. Affected gate scripts:
- `tools/check_window_515_524_closure_gate_phase_524.sh` — asserts `CDL-059 not in rows`
- `tools/check_window_535_544_closure_gate_phase_544.sh` — inner test `test_live_cdl_inventory_preserves_cdl_060_and_no_new_rows` asserts no CDL above 060
- `tools/check_window_545_554_closure_gate_phase_554.sh` — same chain

The test file even documents it: *"The Phase-542 no-new-CDL-above-060 check will be historicalized when CDL-061 opens."* — it was never done.

**1 failure — code health guardrail (pre-existing):**
- `tests/test_code_health.py::test_function_size_thresholds` — `export_wallet_state()` in `ilc_core/rc/economic_cycle_runtime.py` is 163 lines (limit 150). Was failing before migration at commit `f7697f90`.

---

## 5. Uncommitted Working Tree Changes

These changes are in the working tree but **not staged or committed**. They are legitimate and should be committed at the appropriate phase:

| File | Change | Commit timing |
|---|---|---|
| `pyproject.toml` | Added `[tool.pytest.ini_options] pythonpath = ["."]` | Next chore commit or Phase 596 |
| `TODO.txt` | Staged additions: Agent Skills Infrastructure (Tier 1/2) research track | Whenever agent skills work begins |
| `docs/adr/ADR_0011_...md` | Status: Proposed → Accepted (post-Phase 547 review) | Next docs commit |
| `docs/specs/ilc_window_555_564_candidate_phase_grouping_v0.1.md` | Minor edits | Part of prior session work |
| `out/monitoring/d2e_risk_snapshot_phase_306.json` | Updated monitoring snapshot | Next monitoring update |
| `out/monitoring/infrastructure_risk_snapshot_phase_316.json` | Updated monitoring snapshot | Next monitoring update |

Untracked files (copied from old partition, not yet committed):
- `docs/adr/ADR_0024_Agent_Skills_Infrastructure.md`
- `docs/research/ilc_rc_gap_context_pack_v0.1.md` (moved here from context_packs/)
- `docs/research/ilc_rc_*.md` and `tools/ilc_rc_*.py` — RC gap dredge research artifacts
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.1.md`
- Various `tools/rc_*.py` — RC gap triage tools

---

## 6. Pending Manual Actions (User-Interactive)

These require Jamison's direct action in a terminal:

```bash
# 1. GitHub CLI authentication (not yet done)
gh auth login

# 2. ILC node SSH key — add to Keychain if id_ed25519 has a passphrase
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

---

## 7. Project State — Where We Were Before the Crash

**Window 575-584: IN PROGRESS** (was the active window at time of crash)
- Phase 575: COMPLETE (seq lock)
- Phase 576: COMPLETE (RC0.1 settlement + wallet boundary lock)
- Phase 577: COMPLETE (RC0.1 persisted graph contract lock)
- Phase 578: COMPLETE (RC0.1 curated genesis bootstrap lineage lock)
- Phase 579: COMPLETE (agent behavioral loop runtime cutover, `tools/agent_loop_v1.py`)
- Phase 580: COMPLETE (7+1 panel and live submission integration)
- Phase 581: prompt drafted (`9101153b`) — **NOT YET EXECUTED**
- Phases 582-584: not started

**Window 596-605: PLANNED** (prompts drafted but not executed)
- All 10 phase prompts exist in `docs/antigravity_tasks/`
- The entire window is the Genesis carry-forward closure lane
- Phase 596 (sequence lock) is next to execute, all entry criteria verified clean

**Pre-execution audit of phases 596-605 completed this session.** See session transcript for full audit findings (two LOW findings on Phase 598 and Phase 605 for Codex to address before execution).

---

## 8. Window 596-605 Audit Summary (Completed This Session)

This session completed an external audit of all 10 prompts for Window 596-605 before any execution. Key findings:

**Phase 596 (sequence lock) — READY TO EXECUTE**
All entry criteria verified. Two LOW findings were fixed by Codex in the prior session:
- EC3 token corrected to `freshness_and_accrual_supporting_context_not_closed_public_law` (verified present in Phase 590 doc)
- EC9 updated to include all 15 CDLs
- Phase 601 description updated to name CDL-023 provenance dependency

**Phases 597-605 — GO with two LOW findings for Codex's attention before execution:**

1. **LOW — Phase 598:** `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md` appears in "Inputs to read first" but is NOT in the Section 2 required dependency bundle. Decision needed: add to Section 2 with `supporting_context` tier label, or accept as silent read-only background.

2. **LOW — Phase 605:** Handoff Section requirements do not explicitly mandate writing the `ILC_PHASE_605_GATE_SELFTEST=1` forward obligation into Section 6 for Window 606+ gates (unlike Phase 594's handoff which did). Decision needed: add this requirement explicitly, or accept that the selftest guard is enforced by gate test 7.

**Token chain (verified clean):** 597 → 598 → 599 → 600 → 601 → 602 → 603 → 604 → 605 — all 8 forward/consume links grounded.

**Pre-597 strategic decisions Codex must get from Jamison before executing:**
- Whether any Genesis brake semantics survive (Phase 597 disposition)
- Whether freshness gate closes as ratified, evidence-supplemented, or deferred (Phase 598)
- Whether denominator mode closes in Phase 599 or hands to Phase 600 (Phase 599)
- How hard to retire historical 8% language vs theta_hard (Phase 599)
- Whether capability-proof lane is deferred or positively dispositioned (Phase 601)
- Exact public tokenomics wording for Phase 602

---

## 9. System Configuration Notes for Codex

**Python:** `/usr/local/bin/python3.14` (Homebrew, Python 3.14.3)  
**Venv:** `.venv/` at project root — activate before any Python work  
**Always run pytest as:** `PATH=.venv/bin:$PATH .venv/bin/pytest tests/ ...`  
**Git remote:** `git@github-ilc-core:jamison/ilc-core.git` (SSH via `~/.ssh/id_ed25519_ilc_core`)  
**Tailscale nodes:** Both reachable at 100.109.27.59 and 100.108.3.57  
**GitHub CLI:** Installed (`gh` v2.89.0) but not yet authenticated  

**Important:** The mutation canary (`tools/run_mutation_canary_phase_297.py`) modifies source files in-place and restores them. If a process is interrupted mid-canary, the files will be left in a mutated state. Always check `git status` and `git diff HEAD` before running tests if there's any reason to suspect an interrupted canary run.

---

*Handoff prepared 2026-04-08 by Claude Code after machine migration recovery.*
