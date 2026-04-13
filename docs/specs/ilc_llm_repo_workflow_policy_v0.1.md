# ILC LLM Repo Workflow Policy v0.1

Status: workflow policy
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This policy keeps the repository authoritative while allowing multiple LLM audit
lanes to contribute safely.

## 2. Canonical authority

The canonical authority model is:
- one canonical local repo on the home machine
- one canonical private GitHub origin
- one implementation authority on any active phase

For the current workflow, Codex is the implementation authority unless the user
explicitly assigns a different model for a specific phase.

## 3. Audit lanes

Claude and Gemini may be used as audit lanes for:
- adversarial code review
- prompt audit
- document audit
- design criticism
- bug-hunting

Audit lanes do not become authoritative just by proposing a fix.

## 4. Branch and change policy

Recommended branch model:
- `main` as canonical branch
- one active implementation branch per window if needed
- short-lived audit branches only when isolation is necessary

Avoid:
- long-lived model-specific forks as sources of truth
- simultaneous authoritative edits to the same files from multiple models
- VPS-resident LLM agents mutating runtime state directly

## 5. VPS agent policy

No resident LLM agent is required on each VPS for the first release-candidate
path.

The preferred model is:
- all LLM reasoning remains on the home control machine
- VPS nodes remain script-driven execution targets
- remote observation is collected through logs and deterministic control scripts

## 6. GitHub policy

GitHub is used for:
- private canonical remote backup
- collaboration
- release packaging and distribution later
- issue and milestone tracking

GitHub is not used for:
- peer discovery
- live node control
- autonomous network coordination

## 7. Prompt split policy

When a workflow has both operator work and repository work, define paired task
tracks:
- operator tasks for machine provisioning and environment setup
- Codex tasks for repo mutation, test harnesses, and verification scripts

This keeps execution responsibility explicit and debuggable.

## 8. Quality bar

Repository progress is counted only when it produces one of the following:
- real runtime capability
- deterministic verification of that capability
- reproducible operator workflow

File count, scaffold count, or placeholder breadth do not count as progress.

## 9. Protected run lock

Long-running verification and operator commands should use the shared operator
lock wrapper:

`python3 tools/run_with_operator_lock.py --lock <name> --owner <owner> --label <label> -- <command ...>`

Use this for:
- full pytest runs
- window closure gates
- mutation canary runs
- release gates
- long three-machine or testbed runs
- any background task likely to overlap with another model or operator session

Recommended default lock names:
- `repo_verification` for full suites, gate stacks, and canary work
- `rc_operator` for long RC/testbed operations

Status check:

`python3 tools/run_with_operator_lock.py --lock repo_verification --status`

Expected behavior:
- if no protected run is active, the wrapper acquires the lock and runs the
  command
- if another protected run is active, the wrapper exits with code `73` and
  prints the current owner, label, pid, and command when metadata is available
- `--wait` is allowed when serialization is preferred over fail-fast behavior

This lock is an operator-safety guard only. It does not replace per-tool or
per-script locking where true in-process critical sections still require their
own protection.
