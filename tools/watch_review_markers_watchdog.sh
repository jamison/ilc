#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CTL="${ROOT_DIR}/tools/watch_review_markers_ctl.sh"
STATE_DIR="${ROOT_DIR}/automation/state"
RESTART_TS_FILE="${STATE_DIR}/watch_review_markers_watchdog_last_restart_epoch.txt"

STALE_SECONDS="${STALE_SECONDS:-120}"
CHECK_INTERVAL_SECONDS="${CHECK_INTERVAL_SECONDS:-60}"
AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW:-1}"
REVIEW_ON_FAILED="${REVIEW_ON_FAILED:-1}"
POLL_SECONDS="${POLL_SECONDS:-10}"
MIN_RESTART_INTERVAL_SECONDS="${MIN_RESTART_INTERVAL_SECONDS:-45}"

mkdir -p "${STATE_DIR}"

now_epoch() {
  date +%s
}

read_last_restart_epoch() {
  if [[ ! -f "${RESTART_TS_FILE}" ]]; then
    echo 0
    return 0
  fi
  local value
  value="$(cat "${RESTART_TS_FILE}" 2>/dev/null || true)"
  if [[ "${value}" =~ ^[0-9]+$ ]]; then
    echo "${value}"
  else
    echo 0
  fi
}

write_last_restart_epoch() {
  local epoch="$1"
  printf '%s\n' "${epoch}" > "${RESTART_TS_FILE}"
}

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

  local now last elapsed
  now="$(now_epoch)"
  last="$(read_last_restart_epoch)"
  elapsed="$((now - last))"

  if [[ "${elapsed}" -lt "${MIN_RESTART_INTERVAL_SECONDS}" ]]; then
    local wait_left
    wait_left="$((MIN_RESTART_INTERVAL_SECONDS - elapsed))"
    echo "watchdog: restart cooldown active (${wait_left}s remaining), skip restart"
    return 0
  fi

  echo "watchdog: watcher unhealthy (running=${running}, health=${health}, age=${age}) - restarting watcher only"
  if AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW}" \
  REVIEW_ON_FAILED="${REVIEW_ON_FAILED}" \
  POLL_SECONDS="${POLL_SECONDS}" \
  START_WATCHDOG=0 \
  STOP_WATCHDOG=0 \
  "${CTL}" restart; then
    write_last_restart_epoch "${now}"
  else
    echo "watchdog: restart command failed"
    return 1
  fi
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
