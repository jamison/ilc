#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  tools/run_phase_baseline_once.sh --key <cache-key> --cmd "<command>" [--cmd "<command>"] [--force]

Behavior:
  - Runs each command in order and fails on first non-zero exit.
  - Caches successful execution keyed by:
      * git HEAD
      * working-tree status hash (tracked + untracked, excluding baseline stamp files)
      * command-list hash
  - Reuses the cached success when all key parts match.

Notes:
  - This is for expensive entry/baseline checks only.
  - Any tracked file change invalidates cache automatically.
USAGE
}

KEY=""
FORCE=0
CMDS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --key)
      KEY="${2:-}"
      shift 2
      ;;
    --cmd)
      CMDS+=("${2:-}")
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$KEY" ]]; then
  echo "Missing --key" >&2
  usage >&2
  exit 2
fi

if [[ ${#CMDS[@]} -eq 0 ]]; then
  echo "At least one --cmd is required" >&2
  usage >&2
  exit 2
fi

mkdir -p out/monitoring
STAMP_PATH="out/monitoring/phase_baseline_cache_${KEY}.env"

HEAD_SHA="$(git rev-parse HEAD)"
TRACKED_STATUS="$(git status --porcelain --untracked-files=no)"
UNTRACKED_STATUS="$(git ls-files --others --exclude-standard || true)"
UNTRACKED_STATUS="$(printf '%s\n' "$UNTRACKED_STATUS" | grep -Ev '^out/monitoring/phase_baseline_cache_.*\.env$' || true)"
STATUS_HASH="$(printf '%s\n--\n%s\n' "$TRACKED_STATUS" "$UNTRACKED_STATUS" | shasum -a 256 | awk '{print $1}')"
CMD_HASH="$(printf '%s\n' "${CMDS[@]}" | shasum -a 256 | awk '{print $1}')"

if [[ "$FORCE" -eq 0 && -f "$STAMP_PATH" ]]; then
  # shellcheck disable=SC1090
  source "$STAMP_PATH"
  if [[ "${BASELINE_HEAD_SHA:-}" == "$HEAD_SHA" && \
        "${BASELINE_STATUS_HASH:-}" == "$STATUS_HASH" && \
        "${BASELINE_CMD_HASH:-}" == "$CMD_HASH" && \
        "${BASELINE_RESULT:-}" == "pass" ]]; then
    echo "baseline_cache_hit=$KEY"
    echo "baseline_head=$HEAD_SHA"
    exit 0
  fi
fi

echo "baseline_cache_miss=$KEY"
echo "baseline_head=$HEAD_SHA"

for cmd in "${CMDS[@]}"; do
  echo "[baseline:$KEY] running: $cmd"
  bash -lc "$cmd"
done

{
  echo "BASELINE_KEY=$KEY"
  echo "BASELINE_HEAD_SHA=$HEAD_SHA"
  echo "BASELINE_STATUS_HASH=$STATUS_HASH"
  echo "BASELINE_CMD_HASH=$CMD_HASH"
  echo "BASELINE_RESULT=pass"
  echo "BASELINE_UPDATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$STAMP_PATH"

echo "baseline_cache_written=$STAMP_PATH"
