#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_DIR="${HOME}/Library/LaunchAgents"

MAIN_LABEL="com.ilc.watch_review_markers"
WATCHDOG_LABEL="com.ilc.watch_review_markers_watchdog"

MAIN_TEMPLATE="${ROOT_DIR}/automation/launchd/${MAIN_LABEL}.plist.template"
WATCHDOG_TEMPLATE="${ROOT_DIR}/automation/launchd/${WATCHDOG_LABEL}.plist.template"
MAIN_PLIST="${PLIST_DIR}/${MAIN_LABEL}.plist"
WATCHDOG_PLIST="${PLIST_DIR}/${WATCHDOG_LABEL}.plist"

render_template() {
  local src="$1"
  local dst="$2"
  sed "s|__ROOT_DIR__|${ROOT_DIR}|g" "${src}" > "${dst}"
}

load_agent() {
  local plist="$1"
  launchctl unload -w "${plist}" >/dev/null 2>&1 || true
  launchctl load -w "${plist}"
}

unload_agent() {
  local plist="$1"
  launchctl unload -w "${plist}" >/dev/null 2>&1 || true
}

status() {
  echo "Main plist: ${MAIN_PLIST}"
  [[ -f "${MAIN_PLIST}" ]] && echo "  present" || echo "  missing"
  echo "Watchdog plist: ${WATCHDOG_PLIST}"
  [[ -f "${WATCHDOG_PLIST}" ]] && echo "  present" || echo "  missing"
  echo
  echo "launchctl list (filtered):"
  launchctl list | grep -E "${MAIN_LABEL}|${WATCHDOG_LABEL}" || true
}

install() {
  mkdir -p "${PLIST_DIR}" "${ROOT_DIR}/automation/state"
  render_template "${MAIN_TEMPLATE}" "${MAIN_PLIST}"
  render_template "${WATCHDOG_TEMPLATE}" "${WATCHDOG_PLIST}"
  load_agent "${MAIN_PLIST}"
  load_agent "${WATCHDOG_PLIST}"
  echo "Installed and loaded:"
  echo "  ${MAIN_PLIST}"
  echo "  ${WATCHDOG_PLIST}"
}

uninstall() {
  unload_agent "${MAIN_PLIST}"
  unload_agent "${WATCHDOG_PLIST}"
  rm -f "${MAIN_PLIST}" "${WATCHDOG_PLIST}"
  echo "Uninstalled launchd agents."
}

ACTION="${1:-status}"
case "${ACTION}" in
  install) install ;;
  uninstall) uninstall ;;
  reload)
    install
    ;;
  status) status ;;
  *)
    echo "Usage: $0 [install|reload|uninstall|status]"
    exit 2
    ;;
esac
