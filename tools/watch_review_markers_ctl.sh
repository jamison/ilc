#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCH_SCRIPT="${ROOT_DIR}/tools/watch_review_markers.sh"
STATE_DIR="${ROOT_DIR}/automation/state"
PID_FILE="${STATE_DIR}/watch_review_markers.pid"
LOG_FILE="${STATE_DIR}/watch_review_markers.log"
HEARTBEAT_FILE="${STATE_DIR}/watch_review_markers_heartbeat.json"

AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW:-1}"
REVIEW_ON_FAILED="${REVIEW_ON_FAILED:-1}"
POLL_SECONDS="${POLL_SECONDS:-10}"
STALE_SECONDS="${STALE_SECONDS:-90}"

usage() {
  cat <<'EOF'
Usage: tools/watch_review_markers_ctl.sh <start|stop|restart|status>

Environment:
  AUTO_CODEX_REVIEW   default 1
  REVIEW_ON_FAILED    default 1
  POLL_SECONDS        default 10
  STALE_SECONDS       default 90 (status freshness threshold)
EOF
}

is_running() {
  if [[ ! -f "${PID_FILE}" ]]; then
    return 1
  fi
  local pid
  pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
  [[ -n "${pid}" ]] || return 1
  ps -p "${pid}" > /dev/null 2>&1
}

heartbeat_age_seconds() {
  if [[ ! -f "${HEARTBEAT_FILE}" ]]; then
    echo -1
    return 0
  fi

  HEARTBEAT_FILE_ENV="${HEARTBEAT_FILE}" python3 - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

path = Path(os.environ["HEARTBEAT_FILE_ENV"])
try:
    data = json.loads(path.read_text(encoding="utf-8"))
    updated = data.get("updated_at")
    if not isinstance(updated, str):
        print(-1)
        raise SystemExit(0)
    dt = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    print(max(0, int((now - dt).total_seconds())))
except Exception:
    print(-1)
PY
}

start() {
  mkdir -p "${STATE_DIR}"

  if is_running; then
    local pid
    pid="$(cat "${PID_FILE}")"
    echo "watch_review_markers is already running (pid=${pid})"
    return 0
  fi

  # stale PID file
  rm -f "${PID_FILE}"

  nohup env \
    AUTO_CODEX_REVIEW="${AUTO_CODEX_REVIEW}" \
    REVIEW_ON_FAILED="${REVIEW_ON_FAILED}" \
    POLL_SECONDS="${POLL_SECONDS}" \
    "${WATCH_SCRIPT}" >> "${LOG_FILE}" 2>&1 &
  local pid="$!"
  echo "${pid}" > "${PID_FILE}"

  sleep 1
  if is_running; then
    echo "watch_review_markers started (pid=${pid})"
  else
    echo "Failed to start watch_review_markers"
    tail -n 40 "${LOG_FILE}" || true
    return 1
  fi
}

stop() {
  if ! is_running; then
    rm -f "${PID_FILE}"
    echo "watch_review_markers is not running"
    return 0
  fi

  local pid
  pid="$(cat "${PID_FILE}")"
  kill "${pid}" >/dev/null 2>&1 || true

  for _ in $(seq 1 20); do
    if ps -p "${pid}" > /dev/null 2>&1; then
      sleep 0.2
    else
      break
    fi
  done

  rm -f "${PID_FILE}"
  echo "watch_review_markers stopped"
}

status() {
  local running="no"
  local pid=""
  if is_running; then
    running="yes"
    pid="$(cat "${PID_FILE}")"
  fi

  local age
  age="$(heartbeat_age_seconds)"
  local health="stopped"
  if [[ "${running}" == "yes" ]]; then
    if [[ "${age}" -ge 0 && "${age}" -le "${STALE_SECONDS}" ]]; then
      health="healthy"
    else
      health="stale"
    fi
  fi

  echo "running=${running}"
  echo "pid=${pid}"
  echo "heartbeat_age_seconds=${age}"
  echo "health=${health}"
}

ACTION="${1:-status}"
case "${ACTION}" in
  start) start ;;
  stop) stop ;;
  restart)
    stop
    start
    ;;
  status) status ;;
  *)
    usage
    exit 2
    ;;
esac
