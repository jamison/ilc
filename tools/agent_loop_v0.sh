#!/usr/bin/env bash
# Agent Loop v0 (pseudocode)
# NOTE: This script is a scaffold, not production‑ready. Review before use.

set -euo pipefail

PROMPT_DIR="docs/antigravity_tasks"
WALK_DIR="docs/phases"
PROMPT_DELAY_SECS=180
WALK_DELAY_SECS=120

last_prompt=""
last_walkthrough=""

while true; do
  prompt=$(ls -t "$PROMPT_DIR"/antigravity_prompt__phase_*.md 2>/dev/null | head -n 1 || true)
  if [[ -n "$prompt" && "$prompt" != "$last_prompt" ]]; then
    echo "[loop] New prompt detected: $prompt"
    echo "[loop] Sleeping $PROMPT_DELAY_SECS seconds before execution"
    sleep "$PROMPT_DELAY_SECS"
    # TODO: trigger Antigravity execution here
    last_prompt="$prompt"
  fi

  walk=$(ls -t "$WALK_DIR"/phase_*_walkthrough.md 2>/dev/null | head -n 1 || true)
  if [[ -n "$walk" && "$walk" != "$last_walkthrough" ]]; then
    echo "[loop] New walkthrough detected: $walk"
    echo "[loop] Sleeping $WALK_DELAY_SECS seconds before Codex review"
    sleep "$WALK_DELAY_SECS"
    # TODO: trigger Codex review gate here
    last_walkthrough="$walk"
  fi

  sleep 10
 done
