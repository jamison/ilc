#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CTL="${ROOT_DIR}/tools/watch_review_markers_ctl.sh"

STALE_SECONDS="${STALE_SECONDS:-120}"
CHECK_INTERVAL_SECONDS="${CHECK_INTERVAL_SECONDS:-60}"
AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW:-1}"
REVIEW_ON_FAILED="${REVIEW_ON_FAILED:-1}"
POLL_SECONDS="${POLL_SECONDS:-10}"

check_once() {
  local status_output
  status_output="$(
    STALE_SECONDS="${STALE_SECONDS}" \
    "${CTL}" status
  )"

  local running health age
  running="$(printf '%s\n' "${status_output}" | awk -F= '/^running=/{print $2}')"
  health="$(printf '%s\n' "${status_output}" | awk -F= '/^health=/{print $2}')"
  age="$(printf '%s\n' "${status_output}" | awk -F= '/^heartbeat_age_seconds=/{print $2}')"

  if [[ "${running}" == "yes" && "${health}" == "healthy" ]]; then
    echo "watchdog: watcher healthy (heartbeat_age_seconds=${age})"
    return 0
  fi

  echo "watchdog: watcher unhealthy (running=${running}, health=${health}, age=${age}) - restarting"
  AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW}" \
  REVIEW_ON_FAILED="${REVIEW_ON_FAILED}" \
  POLL_SECONDS="${POLL_SECONDS}" \
  "${CTL}" restart
}

MODE="${1:-check}"
case "${MODE}" in
  check)
    check_once
    ;;
  loop)
    while true; do
      check_once || true
      sleep "${CHECK_INTERVAL_SECONDS}"
    done
    ;;
  *)
    echo "Usage: $0 [check|loop]"
    exit 2
    ;;
esac
